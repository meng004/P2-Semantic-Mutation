"""SMS evaluator for Track-1 (12 primary cells) and Track-2 (60 full matrix).

Track 1: each PUT evaluated against its primary MP only (12 cells).
Track 2: each PUT evaluated against ALL 5 MPs (60 cells); the same mutants
         under data/mutants/{put_id}_MP{primary}_llm/ are reused per cell.

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
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import List, Optional

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "src"))

from p2.avp.interface import MR
from p2.equiv.sampler import UniformSampler
from p2.pipeline.run_cell import run_one_cell

# Primary (put_id -> mp_k) assignments — determines MR and mutant directory name
PRIMARY_CELLS = {
    "a1": 1, "a2": 1, "a3": 1,
    "b1": 2, "b2": 2, "b3": 2,
    "c1": 5, "c2": 5, "c3": 5,
    "d1": 2, "d2": 2, "d3": 2,
}

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
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _load_mutants(cell_dir: Path) -> List[tuple]:
    """Load all .py mutants from directory, return [(name, callable), ...]."""
    mutants = []
    for py_file in sorted(cell_dir.glob("*.py")):
        mod = _load_module(f"_mut_{py_file.stem}", py_file)
        mutants.append((py_file.name, mod.program))
    return mutants


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
    if mutant_dir is None:
        pool_dir = MUTANTS_DIR / f"{put_id}_pool"
        if pool_dir.exists():
            mutant_dir = pool_dir
        else:
            primary_mp = PRIMARY_CELLS[put_id]
            mutant_dir = MUTANTS_DIR / f"{put_id}_MP{primary_mp}_llm"

    cell_label = f"{put_id.upper()}_MP{mp_k}"

    # Load PUT program
    put_mod = _load_module(f"put_{put_id}", PUTS_DIR / f"{put_id}.py")
    put_fn = put_mod.program

    # Build MR
    mr = _build_mr(put_id, mp_k)

    # Load mutants
    named_mutants = _load_mutants(mutant_dir)
    if not named_mutants:
        return {
            "cell": cell_label,
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
        "inst":    result.inst_count,
        "equiv":   result.equiv_count,
        "killed":  result.killed_count,
        "survive": result.survive_count,
        "sms":     round(result.sms, 4),
        "outcomes": outcomes,
    }


def _worker(put_id: str, mp_k: int, repeats: int = 1) -> dict:
    """Top-level worker for ProcessPoolExecutor (must be picklable)."""
    return evaluate_cell(put_id, mp_k, repeats=repeats)


def _build_cell_list(track: int, cell: Optional[str], mp: Optional[int]) -> list:
    """Return a list of (put_id, mp_k) cells to evaluate."""
    if cell is not None:
        if mp is not None:
            return [(cell, mp)]
        return [(cell, PRIMARY_CELLS[cell])]
    if track == 1:
        return [(p, mp) for p, mp in PRIMARY_CELLS.items()]
    # track == 2: full 12 × 5 = 60 matrix
    return [(p, k) for p in PRIMARY_CELLS for k in (1, 2, 3, 4, 5)]


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
    args = parser.parse_args()

    cells = _build_cell_list(args.track, args.cell, args.mp)

    print(f"\n{'='*60}")
    print(f"P2 TRACK-{args.track} SMS CAMPAIGN — {len(cells)} cells")
    print(f"{'='*60}\n")

    all_results: dict = {}

    if len(cells) == 1:
        put_id, mp_k = cells[0]
        summary = evaluate_cell(put_id, mp_k, repeats=args.repeats)
        all_results[summary["cell"]] = summary
        _print_summary(summary)
    else:
        futures = {}
        with ProcessPoolExecutor(max_workers=args.workers) as executor:
            for put_id, mp_k in cells:
                fut = executor.submit(_worker, put_id, mp_k, args.repeats)
                futures[fut] = (put_id, mp_k)

            for fut in as_completed(futures):
                put_id, mp_k = futures[fut]
                try:
                    summary = fut.result()
                except Exception as exc:
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
