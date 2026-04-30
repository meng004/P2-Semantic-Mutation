"""LLM mutant generation campaign.

Pipeline per cell (put_id, mp_k):
  1. Load PUT source from src/p2/puts/{put_id}.py
  2. Generate N candidates via Claude Opus 4.6 (LLM-G)
  3. Mechanical validation V1-V4
  4. LLM review V5-V6 via GPT-5.4 / DeepSeek arbitration
  5. Save CONFIRMED mutants to data/mutants/{put_id}_MP{k}_llm/

Usage:
  python scripts/llm_campaign.py                  # all 12 cells × 5 candidates
  python scripts/llm_campaign.py --cell a2 --mp 1 # single cell
  python scripts/llm_campaign.py --n 3            # 3 candidates per cell
"""
import argparse
import json
import sys
from pathlib import Path

# ── repo root on path ────────────────────────────────────────────────────────
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "src"))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

from p2.mutators.mut_intents import INTENTS
from p2.mutators.llm_generator import generate_mutants
from p2.mutators.validation import validate_mutant
from p2.mutators.llm_reviewer import review_mutant
from p2.mutators.dual_blind import classify_mutant, MutantStatus

# Primary (put, mp) pairs — one MP per PUT
PRIMARY_CELLS = {
    "a1": 1, "a2": 1, "a3": 1,
    "b1": 2, "b2": 2, "b3": 2,
    "c1": 5, "c2": 5, "c3": 5,
    "d1": 2, "d2": 2, "d3": 2,
}

PUTS_DIR = ROOT / "src" / "p2" / "puts"
OUT_DIR  = ROOT / "data" / "mutants"


def load_put_source(put_id: str) -> str:
    return (PUTS_DIR / f"{put_id}.py").read_text()


def load_original_fn(put_id: str):
    """Import program() from a PUT file as a callable."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(put_id, PUTS_DIR / f"{put_id}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.program


def run_cell(put_id: str, mp_k: int, n_candidates: int, dry_run: bool = False):
    intent = INTENTS[put_id]
    put_source = load_put_source(put_id)
    original_fn = load_original_fn(put_id)
    cell_label = f"{put_id.upper()}_MP{mp_k}"
    out_dir = OUT_DIR / f"{put_id}_MP{mp_k}_llm"

    print(f"\n{'='*60}")
    print(f"  {cell_label}  ({intent['scientific_domain']})")
    print(f"{'='*60}")

    if dry_run:
        print("  [dry-run] skipping LLM calls")
        return {"cell": cell_label, "confirmed": 0, "rejected": 0, "dry_run": True}

    # Step 1: generate
    print(f"  Generating {n_candidates} candidates via Claude Opus 4.6 …")
    candidates = generate_mutants(
        put_source=put_source,
        put_name=put_id.upper(),
        scientific_domain=intent["scientific_domain"],
        mut_intent=intent["mut_intent"],
        n_candidates=n_candidates,
    )

    confirmed_paths = []
    summary_rows = []

    for idx, code in enumerate(candidates, 1):
        label = f"{put_id}_MP{mp_k}_llm_m{idx:02d}"
        print(f"\n  [{idx}/{n_candidates}] {label}")

        # Step 2: mechanical V1-V4
        val = validate_mutant(code, original_fn)
        v_tag = "V1-V4 OK" if val.passed else f"FAIL({val.error})"
        print(f"    Mechanical: {v_tag}")

        if not val.passed:
            summary_rows.append({"label": label, "stage": "mechanical", "verdict": "REJECTED",
                                  "reason": val.error})
            continue

        # Step 3: LLM review V5-V6
        print("    LLM review (GPT-5.4) …")
        rv = review_mutant(put_source=put_source, mutant_code=code)
        status = classify_mutant(rv)
        print(f"    Reviewer: {rv.reviewer} | overall: {rv.overall} | {rv.reason[:80]}")

        row = {
            "label": label,
            "stage": "llm_review",
            "reviewer": rv.reviewer,
            "V1": rv.V1_syntax_ok,
            "V2": rv.V2_executable,
            "V3": rv.V3_nontrivial,
            "V4": rv.V4_nondegenerate,
            "V5": rv.V5_single_fault,
            "V6": rv.V6_plausible,
            "verdict": rv.overall,
            "reason": rv.reason,
        }
        summary_rows.append(row)

        if status == MutantStatus.CONFIRMED:
            out_dir.mkdir(parents=True, exist_ok=True)
            fname = f"m{idx:02d}_llm.py"
            (out_dir / fname).write_text(code)
            confirmed_paths.append(str(out_dir / fname))
            print(f"    SAVED → {out_dir / fname}")

    result = {
        "cell": cell_label,
        "n_candidates": n_candidates,
        "confirmed": len(confirmed_paths),
        "rejected": n_candidates - len(confirmed_paths),
        "paths": confirmed_paths,
        "detail": summary_rows,
    }
    print(f"\n  {cell_label}: {len(confirmed_paths)}/{n_candidates} confirmed")
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cell", help="PUT id, e.g. a2 (default: all)")
    parser.add_argument("--mp", type=int, help="MP index (default: primary for cell)")
    parser.add_argument("--n", type=int, default=5, help="candidates per cell")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.cell:
        cells = {args.cell: args.mp or PRIMARY_CELLS[args.cell]}
    else:
        cells = PRIMARY_CELLS

    all_results = []
    for put_id, mp_k in cells.items():
        res = run_cell(put_id, mp_k, n_candidates=args.n, dry_run=args.dry_run)
        all_results.append(res)

    # Save campaign log
    log_path = ROOT / "data" / "results" / "llm_campaign_log.json"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(json.dumps(all_results, indent=2, ensure_ascii=False))
    print(f"\nCampaign log → {log_path}")

    # Summary table
    print("\n── Campaign Summary ─────────────────────────────────")
    print(f"{'Cell':<14} {'Confirmed':>9} {'Rejected':>9}")
    print("-" * 36)
    total_conf = total_rej = 0
    for r in all_results:
        if r.get("dry_run"):
            continue
        conf = r["confirmed"]
        rej  = r["rejected"]
        total_conf += conf
        total_rej  += rej
        print(f"{r['cell']:<14} {conf:>9} {rej:>9}")
    print("-" * 36)
    print(f"{'TOTAL':<14} {total_conf:>9} {total_rej:>9}")


if __name__ == "__main__":
    main()
