"""SMS evaluator for Track-1 (12 primary cells) and Track-2 (60 full matrix).

Track 1: each PUT evaluated against its primary MP only (12 cells).
Track 2: each PUT evaluated against ALL 5 MPs (60 cells). Per-PUT mutant
         pool is auto-resolved: prefer data/mutants/{put_id}_pool/ (Round-2
         enriched, 8-12 mutants) when present, else fall back to legacy
         data/mutants/{put_id}_MP{primary}_llm/ (3-5 mutants).

Usage:
  python scripts/sms_campaign.py                       # Track 1 (default)
  python scripts/sms_campaign.py --track 2             # Track 2, full 60-cell
  python scripts/sms_campaign.py --track 2 --workers 6
  python scripts/sms_campaign.py --cell a2             # single Track-1 cell
  python scripts/sms_campaign.py --cell a2 --mp 3      # single (PUT, MP) cell

Results saved to data/results/sms_track{1|2}.json.
"""
import argparse
import importlib.util
import json
import sys
import warnings
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import List, Optional

warnings.filterwarnings("ignore")

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "src"))

from p2.avp.interface import MR
from p2.config.primary import PRIMARY_CELLS  # type: ignore[import-not-found]
from p2.equiv.sampler import UniformSampler
from p2.pipeline.run_cell import run_one_cell

PUTS_DIR = ROOT / "src" / "p2" / "puts"
MRS_DIR  = ROOT / "src" / "p2" / "mrs"
MUTANTS_DIR = ROOT / "data" / "mutants"
RESULTS_DIR = ROOT / "data" / "results"

K_EQ = 1000
EPSILON_EQ = 1e-6
EPSILON_AVP = 1e-6


def _load_module(name: str, path: Path):
    """Import a Python file as a module."""
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


def _rel_to_root(p: Path) -> str:
    """Path relative to ROOT for JSON metadata; falls back to absolute when
    the path lies outside ROOT (e.g. tmp_path during tests)."""
    try:
        return str(p.relative_to(ROOT))
    except ValueError:
        return str(p)


def _load_mutants(cell_dir: Path) -> List[tuple]:
    """Load all .py mutants from directory, return [(name, callable), ...]."""
    mutants = []
    for py_file in sorted(cell_dir.glob("*.py")):
        mod = _load_module(f"_mut_{py_file.stem}", py_file)
        mutants.append((py_file.name, mod.program))
    return mutants


def _load_c_mutants(cell_dir: Path) -> List[tuple]:
    """Load all .c mutants from a C pool dir as CPutProgram callables.

    Mirrors :func:`_load_mutants` for the Study-4 C grid. Each compiled
    mutant is a plain ``Callable[[float], float]`` so ``run_one_cell`` and
    the MR machinery consume it with no modification."""
    from p2.cport.adapter import CPutProgram
    mutants = []
    for c_file in sorted(cell_dir.glob("*.c")):
        mutants.append((c_file.name, CPutProgram(c_file)))
    return mutants


def resolve_pool_dir(put_id: str, pool_version: Optional[str] = None) -> Path:
    """Resolve the mutant-pool directory for ``put_id``.

    ``pool_version`` (or the ``POOL_VERSION`` env when None) selects the pool:

      * ``v4``/``v5`` (Study-2) / ``v6`` (Study-3): STRICT — always the
        version-specific dir ``{put}_pool_{version}``. It never falls back to a
        Study-1
        pool; if the dir is absent, ``_load_mutants`` returns empty and the
        cell reports inst=0 (a visible failure, not a wrong-pool score). This
        is the fix for the pilot bug where POOL_VERSION=v5 scored the frozen
        Study-1 ``_pool_v3`` mutants.
      * ``v3``: the Study-1 enriched pool ``{put}_pool_v3``.
      * unset: legacy auto-resolution (v3 → v2 → primary-MP llm pool).
    """
    import os as _os
    pv = pool_version if pool_version is not None else _os.environ.get("POOL_VERSION", "")
    if pv in ("v4", "v5", "v6", "v7c"):
        return MUTANTS_DIR / f"{put_id}_pool_{pv}"
    pool_v3 = MUTANTS_DIR / f"{put_id}_pool_v3"
    pool_v2 = MUTANTS_DIR / f"{put_id}_pool"
    if pv == "v3":
        return pool_v3
    if pool_v3.exists():
        return pool_v3
    if pool_v2.exists():
        return pool_v2
    primary_mp = PRIMARY_CELLS[put_id]
    return MUTANTS_DIR / f"{put_id}_MP{primary_mp}_llm"


def _build_mr(put_id: str, mp_k: int) -> MR:
    """Build MR for a (PUT, MP) cell. Post-Track-2 each PUT exposes r/R for
    all 5 MPs; raises if the requested mp_k is missing."""
    mrs_mod = _load_module(f"mrs_{put_id}", MRS_DIR / f"{put_id}.py")
    attr_r = f"r_mp{mp_k}"
    attr_R = f"R_mp{mp_k}"
    if not (hasattr(mrs_mod, attr_r) and hasattr(mrs_mod, attr_R)):
        raise ValueError(f"{put_id} has no MR functions for MP{mp_k}")
    return MR(
        r=getattr(mrs_mod, attr_r),
        R=getattr(mrs_mod, attr_R),
        mp_index=mp_k,
        name=f"{put_id.upper()}_mp{mp_k}",
    )


def evaluate_cell(
    put_id: str,
    mp_k: int,
    mutant_dir: Optional[Path] = None,
    repeats: int = 1,
    lang: str = "py",
) -> dict:
    """Evaluate SMS for one (put_id, mp_k) cell.

    Args:
        put_id: PUT identifier, e.g. "a2".
        mp_k:   Target MP index (may differ from PUT's primary MP).
        mutant_dir: Path to mutant directory. Defaults to the per-PUT
                    enriched pool ``data/mutants/{put_id}_pool/`` if it
                    exists (Round-2 build, 8-12 mutants/PUT), else falls
                    back to the legacy primary-MP pool
                    ``data/mutants/{put_id}_MP{primary}_llm/`` (3-5
                    mutants/PUT). Track-2 reuses the same per-PUT mutant
                    pool across all 5 MPs for diagonal-vs-cross comparison.
        repeats: N AVP repetitions per killed-check (Round-3 majority vote).
                 Default 1 = legacy single-shot. Use 20 for stochastic PUTs.
    """
    is_c = (lang == "c")
    if mutant_dir is None:
        mutant_dir = resolve_pool_dir(put_id, "v7c" if is_c else None)

    cell_label = f"{put_id.upper()}_MP{mp_k}"

    # Load PUT program (Python module, or compiled C via the adapter)
    if is_c:
        from p2.cport.adapter import load_c_put
        put_fn = load_c_put(put_id, ROOT)
    else:
        put_mod = _load_module(f"put_{put_id}", PUTS_DIR / f"{put_id}.py")
        put_fn = put_mod.program

    # Build MR (shared, language-agnostic — src/p2/mrs/{put}.py unchanged)
    mr = _build_mr(put_id, mp_k)

    # Load mutants
    named_mutants = _load_c_mutants(mutant_dir) if is_c else _load_mutants(mutant_dir)
    if not named_mutants:
        return {
            "cell": cell_label,
            "mutant_dir": _rel_to_root(mutant_dir),
            "repeats": repeats,
            "inst": 0, "equiv": 0, "killed": 0, "survive": 0,
            "sms": 0.0, "outcomes": [],
        }

    mutant_fns   = [fn   for _, fn   in named_mutants]
    mutant_names = [name for name, _ in named_mutants]

    sampler = UniformSampler(low=0.0, high=1.0, dim=1, seed=42)

    result = run_one_cell(
        put=put_fn,
        mutants=mutant_fns,
        mr_set=[mr],
        cell_id=cell_label,
        sampler=sampler,
        k_eq=K_EQ,
        epsilon_eq=EPSILON_EQ,
        epsilon_avp=EPSILON_AVP,
        repeats=repeats,
    )

    outcomes = []
    for idx, name in enumerate(mutant_names):
        if idx in result.equiv_indices:
            label = "EQUIV"
        elif idx in result.killed_indices:
            label = "KILLED"
        else:
            label = "SURVIVE"
        outcomes.append({"file": name, "label": label})

    return {
        "cell":    cell_label,
        "mutant_dir": _rel_to_root(mutant_dir),
        "repeats": repeats,
        "inst":    result.inst_count,
        "equiv":   result.equiv_count,
        "killed":  result.killed_count,
        "survive": result.survive_count,
        "sms":     round(result.sms, 4),
        "outcomes": outcomes,
    }


C_GRID_PUTS = ("a1", "a2", "a3", "b1", "b2", "b3", "c2")


def _worker(put_id: str, mp_k: int, repeats: int = 1, lang: str = "py") -> dict:
    """Top-level worker for ProcessPoolExecutor (must be picklable)."""
    return evaluate_cell(put_id, mp_k, repeats=repeats, lang=lang)


def _build_cell_list(track: int, cell: Optional[str], mp: Optional[int],
                     puts: Optional[list] = None) -> list:
    """Return a list of (put_id, mp_k) cells to evaluate.

    ``puts`` optionally restricts a track run to a subset of PUT ids (e.g. the
    calibration pilot ``[a2, b4]`` → 10 Track-2 cells). Ignored for --cell.
    """
    if cell is not None:
        if mp is not None:
            return [(cell, mp)]
        return [(cell, PRIMARY_CELLS[cell])]
    selected_puts = [p for p in PRIMARY_CELLS if (puts is None or p in puts)]
    if track == 1:
        return [(p, PRIMARY_CELLS[p]) for p in selected_puts]
    # track == 2: full 5-MP matrix over the selected PUTs
    return [(p, k) for p in selected_puts for k in (1, 2, 3, 4, 5)]


def main():
    parser = argparse.ArgumentParser(description="P2 SMS campaign")
    parser.add_argument("--track", type=int, default=1, choices=(1, 2),
                        help="1=primary-MP only (12 cells); 2=full 60-cell matrix")
    parser.add_argument("--workers", type=int, default=4,
                        help="Number of parallel workers (default: 4)")
    parser.add_argument("--cell", default=None,
                        help="Run a single cell, e.g. --cell a2")
    parser.add_argument("--mp", type=int, default=None,
                        help="With --cell, force a specific MP index (1-5)")
    parser.add_argument("--repeats", type=int, default=1,
                        help="N AVP repetitions per (mutant, MR) killed-check "
                             "(default 1 = single shot; Round-4 uses 20)")
    parser.add_argument("--out", type=str, default=None,
                        help="Override output JSON path (default "
                             "data/results/sms_track{N}.json)")
    parser.add_argument("--puts", default=None,
                        help="comma-separated PUT ids to restrict a track run "
                             "(e.g. a2,b4 for the calibration pilot)")
    parser.add_argument("--pool-version", "--pool_version", dest="pool_version",
                        default=None,
                        help="pool version for auto-resolution (v3/v4/v5); "
                             "overrides $POOL_VERSION for this run")
    parser.add_argument("--lang", choices=("py", "c"), default="py",
                        help="grid language: 'py' (default) or 'c' (Study-4 "
                             "H-LANG; scores the 7-PUT C grid from "
                             "{put}_pool_v7c via the adapter, MRs unchanged)")
    args = parser.parse_args()

    if args.pool_version:
        import os as _os
        _os.environ["POOL_VERSION"] = args.pool_version

    puts = [s.strip() for s in args.puts.split(",")] if args.puts else None
    if args.lang == "c":
        puts = [p for p in (puts or C_GRID_PUTS) if p in C_GRID_PUTS]
    cells = _build_cell_list(args.track, args.cell, args.mp, puts=puts)

    print(f"\n{'='*60}")
    print(f"P2 TRACK-{args.track} SMS CAMPAIGN — {len(cells)} cells")
    print(f"{'='*60}\n")

    all_results: dict = {}

    if len(cells) == 1:
        put_id, mp_k = cells[0]
        summary = evaluate_cell(put_id, mp_k, repeats=args.repeats, lang=args.lang)
        all_results[summary["cell"]] = summary
        _print_summary(summary)
    else:
        futures = {}
        with ProcessPoolExecutor(max_workers=args.workers) as executor:
            for put_id, mp_k in cells:
                fut = executor.submit(_worker, put_id, mp_k, args.repeats, args.lang)
                futures[fut] = (put_id, mp_k)

            for fut in as_completed(futures):
                put_id, mp_k = futures[fut]
                try:
                    summary = fut.result()
                except (ValueError, ArithmeticError, TypeError, RuntimeError, ImportError, OSError) as exc:
                    cell_label = f"{put_id.upper()}_MP{mp_k}"
                    print(f"  ERROR {cell_label}: {exc}")
                    summary = {
                        "cell": cell_label, "inst": 0, "equiv": 0,
                        "killed": 0, "survive": 0, "sms": 0.0,
                        "outcomes": [], "error": str(exc),
                    }
                all_results[summary["cell"]] = summary
                _print_summary(summary)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
    else:
        out_path = RESULTS_DIR / f"sms_track{args.track}.json"
    out_path.write_text(json.dumps(all_results, indent=2, ensure_ascii=False))
    print(f"\nResults saved → {out_path}")

    print(f"\n{'─'*50}")
    print(f"{'Cell':<16} {'inst':>4} {'equiv':>5} {'kill':>5} {'surv':>5} {'SMS':>7}")
    print(f"{'─'*50}")
    for cell_label in sorted(all_results):
        s = all_results[cell_label]
        print(f"{cell_label:<16} {s['inst']:>4} {s['equiv']:>5} {s['killed']:>5} {s['survive']:>5} {s['sms']:>7.4f}")
    print(f"{'─'*50}")


def _print_summary(summary: dict) -> None:
    print(
        f"Cell: {summary['cell']}  "
        f"inst={summary['inst']}  equiv={summary['equiv']}  "
        f"killed={summary['killed']}  survive={summary['survive']}  "
        f"SMS={summary['sms']:.4f}"
    )
    for o in summary.get("outcomes", []):
        print(f"    {o['label']:8s}  {o['file']}")
    print()


if __name__ == "__main__":
    main()
