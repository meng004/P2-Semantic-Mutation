"""Track-1 SMS evaluator: evaluate SMS for all 45 LLM mutants across 12 cells.

Usage:
  python scripts/sms_campaign.py               # all 12 cells, 4 workers
  python scripts/sms_campaign.py --workers 2   # custom parallelism
  python scripts/sms_campaign.py --cell a2     # single cell (LLM mutants)

Results saved to data/results/sms_track1.json.
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
    """Build MR for a cell using the mrs module for put_id.

    Special case: a3 is labeled MP1 in the directory naming convention but
    uses MP3 (convergence) as its actual primary verifier.  We dispatch
    correctly by reading the available r_/R_ functions from the MRS module.
    """
    mrs_mod = _load_module(f"mrs_{put_id}", MRS_DIR / f"{put_id}.py")

    # Determine which r/R pair to use based on mp_k
    # Each MRS module exposes r_mp{k} / R_mp{k} for its primary MP.
    # a3 is an exception: labeled mp_k=1 externally but internally uses MP3.
    attr_r = f"r_mp{mp_k}"
    attr_R = f"R_mp{mp_k}"

    if not (hasattr(mrs_mod, attr_r) and hasattr(mrs_mod, attr_R)):
        # Fallback: scan for available primary (non-trivial) r_/R_ pair
        for candidate in [1, 2, 3, 4, 5]:
            cr = f"r_mp{candidate}"
            cR = f"R_mp{candidate}"
            if hasattr(mrs_mod, cr) and hasattr(mrs_mod, cR):
                attr_r = cr
                attr_R = cR
                mp_k   = candidate
                break

    r_fn = getattr(mrs_mod, attr_r)
    R_fn = getattr(mrs_mod, attr_R)
    return MR(r=r_fn, R=R_fn, mp_index=mp_k, name=f"{put_id.upper()}_mp{mp_k}")


def evaluate_cell(
    put_id: str,
    mp_k: int,
    mutant_dir: Optional[Path] = None,
) -> dict:
    """Evaluate SMS for one (put_id, mp_k) cell.

    Args:
        put_id: PUT identifier, e.g. "a2".
        mp_k:   Primary MP index.
        mutant_dir: Path to mutant directory.  Defaults to
                    data/mutants/{put_id}_MP{mp_k}_llm/.

    Returns a dict with keys:
        cell, inst, equiv, killed, survive, sms, outcomes
    """
    if mutant_dir is None:
        mutant_dir = MUTANTS_DIR / f"{put_id}_MP{mp_k}_llm"

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


def _worker(put_id: str, mp_k: int) -> dict:
    """Top-level worker for ProcessPoolExecutor (must be picklable)."""
    return evaluate_cell(put_id, mp_k)


def main():
    parser = argparse.ArgumentParser(description="Track-1 SMS campaign")
    parser.add_argument("--workers", type=int, default=4,
                        help="Number of parallel workers (default: 4)")
    parser.add_argument("--cell", default=None,
                        help="Run a single cell, e.g. --cell a2")
    args = parser.parse_args()

    if args.cell:
        cells = {args.cell: PRIMARY_CELLS[args.cell]}
    else:
        cells = PRIMARY_CELLS

    print(f"\n{'='*60}")
    print("P2 TRACK-1 SMS CAMPAIGN — LLM mutants")
    print(f"{'='*60}\n")

    all_results: dict = {}

    if len(cells) == 1:
        # Single cell: run directly
        (put_id, mp_k) = next(iter(cells.items()))
        summary = evaluate_cell(put_id, mp_k)
        all_results[summary["cell"]] = summary
        _print_summary(summary)
    else:
        futures = {}
        with ProcessPoolExecutor(max_workers=args.workers) as executor:
            for put_id, mp_k in cells.items():
                fut = executor.submit(_worker, put_id, mp_k)
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

    # Save results
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RESULTS_DIR / "sms_track1.json"
    out_path.write_text(json.dumps(all_results, indent=2, ensure_ascii=False))
    print(f"\nResults saved → {out_path}")

    # Final table
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
