"""S5 stratum-purity verification for the v4 semantic-mutant corpus (Fix T2).

Reviewer concern (R2, docs/review_2026-07-08/r2_domain.md §3): the effect map
`sigma` is presented as a *function* but is single-valued only on the
S5-pure sub-domain. S5 (main.tex:952-955) requires that a mutant declared at
stratum psi violate *no other* invariant psi' in I \\ {psi}. The paper hedges
this as "enforced by generation intent ... not verified against all five
invariants" (main.tex:2391-2395). This script VERIFIES it against the existing
data, converting the hedge into an audited number.

Method (no LLM calls, no new experiment):
------------------------------------------
Each PUT was evaluated against ALL five MP invariant checkers (the offline,
deterministic AVP dispatcher, src/p2/avp/, repeats=20 majority vote). The
resulting 60-cell KILLED/SURVIVE matrix is the SSOT
data/results/sms_track2_v4.json. A mutant "perturbs invariant k" iff it is
KILLED in cell PUT_MPk. The number of MPs that kill a mutant is therefore its
invariant-flip count; S5 purity = each detected mutant flips exactly one.

  flip == 0 : survives all 5 MPs -> sigma = active-off-taxonomy (single-valued)
  flip == 1 : perturbs exactly one invariant -> sigma = psi_k   (single-valued, S5-pure)
  flip >= 2 : perturbs >= 2 invariants -> sigma MULTI-VALUED     (S5 VIOLATION)

The 60-cell matrix in sms_track2_v4.json IS the output of the offline invariant
checkers. Pass --live to independently re-execute the AVP dispatcher on the
mutant .py files via scripts.sms_campaign.evaluate_cell (slow: sklearn PUTs +
k_eq equivalence sampling). By default we consume the frozen SSOT and, if a
--live matrix is supplied via --matrix, cross-validate against it.

Usage:
  PYTHONPATH=src python scripts/compute_s5_purity.py
  PYTHONPATH=src python scripts/compute_s5_purity.py --live --puts B2 D1
"""
import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SSOT_IN = ROOT / "data" / "results" / "sms_track2_v4.json"
SSOT_OUT = ROOT / "data" / "results" / "s5_purity_v4.json"

PUTS = ["A1", "A2", "A3", "B1", "B2", "B3", "C1", "C2", "C3", "D1", "D2", "D3"]

# Per-PUT primary MP (RQ2 aligned cell). Mirrors src/p2/config/primary.py
# PRIMARY_CELLS_V3, the assignment used by the RQ2 aligned-vs-cross headline
# (rq2_cliffs_delta_v4_mp5.json holds c-class at MP5).
PRIMARY = {"A": 1, "B": 2, "C": 5, "D": 2}

# Operator family -> its "home" MP under align(j)=j (main.tex:960-962,
# operators mut_C..mut_F are the templates for strata psi_1..psi_5). Used only
# to annotate the per-operator table; NOT load-bearing for the flip counts.
OP_ALIGNED_MP = {"CE": 1, "OS": 2, "HP": 3, "TF": 4, "SI": 5, "CF": 2}

_OP_RE = re.compile(r"^m\d+_[a-z]\d_([A-Z]{2})\d")


def parse_operator(filename: str) -> str:
    m = _OP_RE.match(filename)
    return m.group(1) if m else "??"


def load_matrix_from_ssot(path: Path) -> dict:
    """Return {PUT: {file: {mp: label}}} from an sms_track2-style JSON."""
    raw = json.loads(path.read_text())
    matrix: dict = {p: defaultdict(dict) for p in PUTS}
    for p in PUTS:
        for mp in range(1, 6):
            cell = raw[f"{p}_MP{mp}"]
            for o in cell["outcomes"]:
                matrix[p][o["file"]][mp] = o["label"]
    return matrix


def load_matrix_live(puts, repeats: int) -> dict:
    """Independently re-run the offline AVP checkers on the v4 mutant pool."""
    sys.path.insert(0, str(ROOT / "src"))
    import os
    os.environ["POOL_VERSION"] = "v4"
    from scripts.sms_campaign import evaluate_cell  # noqa: E402
    matrix: dict = {p: defaultdict(dict) for p in puts}
    for p in puts:
        for mp in range(1, 6):
            res = evaluate_cell(p.lower(), mp, repeats=repeats)
            for o in res["outcomes"]:
                matrix[p][o["file"]][mp] = o["label"]
            print(f"  [live] {p}_MP{mp}: killed={res['killed']}", file=sys.stderr)
    return matrix


def analyze(matrix: dict) -> dict:
    per_mutant = []
    for p in PUTS:
        prim = PRIMARY[p[0]]
        for fname, mplabels in sorted(matrix[p].items()):
            flipped = sorted(mp for mp, lab in mplabels.items() if lab == "KILLED")
            op = parse_operator(fname)
            per_mutant.append({
                "put": p,
                "file": fname,
                "operator": op,
                "primary_mp": prim,
                "flipped_invariants": flipped,
                "flip_count": len(flipped),
                "aligned_killed": prim in flipped,
                "cross_killed_mps": [k for k in flipped if k != prim],
                "sigma": (
                    "active-off-taxonomy" if not flipped
                    else f"psi{flipped[0]}" if len(flipped) == 1
                    else "MULTI:" + "+".join(f"psi{k}" for k in flipped)
                ),
                "s5_class": (
                    "silent" if not flipped
                    else "pure" if len(flipped) == 1
                    else "multi-stratum"
                ),
            })

    N = len(per_mutant)
    n_silent = sum(1 for m in per_mutant if m["flip_count"] == 0)
    n_pure = sum(1 for m in per_mutant if m["flip_count"] == 1)
    n_multi = sum(1 for m in per_mutant if m["flip_count"] >= 2)
    n_detected = n_pure + n_multi
    flip_hist = dict(sorted(Counter(m["flip_count"] for m in per_mutant).items()))

    overall = {
        "n_mutants": N,
        "flip_histogram": flip_hist,
        "n_silent_flip0": n_silent,
        "n_pure_flip1": n_pure,
        "n_multistratum_flip_ge2": n_multi,
        "n_detected": n_detected,
        # sigma is single-valued unless a mutant flips >=2 invariants:
        "sigma_well_defined_fraction": round((n_silent + n_pure) / N, 4),
        "multistratum_fraction": round(n_multi / N, 4),
        # purity among mutants that are detected by >=1 MP:
        "purity_among_detected": round(n_pure / n_detected, 4) if n_detected else None,
        # strict reading (denominator = all admitted mutants):
        "purity_flip1_over_all": round(n_pure / N, 4),
    }

    # Per-PUT table
    per_put = {}
    for p in PUTS:
        ms = [m for m in per_mutant if m["put"] == p]
        det = [m for m in ms if m["flip_count"] >= 1]
        mult = [m for m in ms if m["flip_count"] >= 2]
        per_put[p] = {
            "primary_mp": PRIMARY[p[0]],
            "n_mutants": len(ms),
            "n_detected": len(det),
            "n_pure": sum(1 for m in ms if m["flip_count"] == 1),
            "n_multistratum": len(mult),
            "s5_clean": len(mult) == 0,
            "multistratum_detail": {
                m["file"]: m["flipped_invariants"] for m in mult
            },
        }

    # Per-operator (stratum) table — R2's requested rows
    per_operator = {}
    for op in sorted({m["operator"] for m in per_mutant}):
        ms = [m for m in per_mutant if m["operator"] == op]
        det = [m for m in ms if m["flip_count"] >= 1]
        per_operator[op] = {
            "aligned_mp": OP_ALIGNED_MP.get(op),
            "n_mutants": len(ms),
            "n_detected": len(det),
            "n_pure_flip1": sum(1 for m in ms if m["flip_count"] == 1),
            "n_multistratum": sum(1 for m in ms if m["flip_count"] >= 2),
            "pct_flip_exactly_one_of_detected": (
                round(100 * sum(1 for m in det if m["flip_count"] == 1) / len(det), 1)
                if det else None
            ),
            "flip_histogram": dict(sorted(Counter(m["flip_count"] for m in ms).items())),
        }

    # RQ2 off-diagonal kill-mass re-attribution.
    # Aligned (diagonal) cell = PUT primary MP; off-diagonal = other 4 MPs.
    # Each KILLED entry in an off-diagonal cell is re-attributed to whether the
    # mutant is pure (flip==1, single-invariant cross-stratum detection) or
    # multi-stratum (flip>=2, an S5 artifact contaminating the contrast term).
    aligned_mass = 0
    off_total = 0
    off_from_pure = 0
    off_from_multi = 0
    off_cells = {}
    for m in per_mutant:
        prim = m["primary_mp"]
        for k in m["flipped_invariants"]:
            if k == prim:
                aligned_mass += 1
            else:
                off_total += 1
                if m["flip_count"] >= 2:
                    off_from_multi += 1
                else:
                    off_from_pure += 1
                cell = f"{m['put']}_MP{k}"
                off_cells.setdefault(cell, {"pure": 0, "multi": 0})
                off_cells[cell]["multi" if m["flip_count"] >= 2 else "pure"] += 1

    off_diagonal = {
        "aligned_diagonal_kill_mass": aligned_mass,
        "off_diagonal_kill_mass": off_total,
        "off_diagonal_from_pure": off_from_pure,
        "off_diagonal_from_multistratum": off_from_multi,
        "pct_off_diagonal_from_multistratum": (
            round(100 * off_from_multi / off_total, 1) if off_total else None
        ),
        "off_diagonal_cells": dict(sorted(off_cells.items())),
    }

    return {
        "overall": overall,
        "per_put": per_put,
        "per_operator": per_operator,
        "rq2_off_diagonal_reattribution": off_diagonal,
        "per_mutant": per_mutant,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--live", action="store_true",
                    help="Re-run AVP checkers instead of reading the SSOT")
    ap.add_argument("--repeats", type=int, default=20)
    ap.add_argument("--puts", nargs="*", default=PUTS,
                    help="With --live, restrict to these PUTs (confirmation)")
    ap.add_argument("--matrix", type=str, default=None,
                    help="Optional live-matrix JSON to cross-validate the SSOT")
    ap.add_argument("--out", type=str, default=str(SSOT_OUT))
    args = ap.parse_args()

    if args.live:
        matrix = load_matrix_live([p.upper() for p in args.puts], args.repeats)
        source = f"live AVP re-run (repeats={args.repeats})"
    else:
        matrix = load_matrix_from_ssot(SSOT_IN)
        source = str(SSOT_IN.relative_to(ROOT))

    result = analyze(matrix)
    result["_meta"] = {
        "description": "S5 stratum-purity verification for the v4 semantic-mutant "
                       "corpus. A mutant perturbs invariant k iff KILLED under MP_k "
                       "(offline AVP dispatcher, src/p2/avp/, repeats=20).",
        "source": source,
        "n_puts": len(PUTS),
        "primary_mp_map": PRIMARY,
    }

    Path(args.out).write_text(json.dumps(result, indent=2, ensure_ascii=False))
    o = result["overall"]
    print(f"Source: {source}")
    print(f"Mutants: {o['n_mutants']}  flip-hist: {o['flip_histogram']}")
    print(f"  silent(0)={o['n_silent_flip0']}  pure(1)={o['n_pure_flip1']}  "
          f"multi(>=2)={o['n_multistratum_flip_ge2']}")
    print(f"sigma well-defined on {o['sigma_well_defined_fraction']*100:.1f}% "
          f"({o['n_silent_flip0']+o['n_pure_flip1']}/{o['n_mutants']}); "
          f"multi-stratum {o['multistratum_fraction']*100:.1f}%")
    print(f"purity among detected: {o['purity_among_detected']*100:.1f}% "
          f"({o['n_pure_flip1']}/{o['n_detected']})")
    r = result["rq2_off_diagonal_reattribution"]
    print(f"off-diagonal kill mass {r['off_diagonal_kill_mass']}: "
          f"pure={r['off_diagonal_from_pure']} "
          f"multi={r['off_diagonal_from_multistratum']} "
          f"({r['pct_off_diagonal_from_multistratum']}% multi)")
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
