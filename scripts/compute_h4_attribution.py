#!/usr/bin/env python3
"""Study-2 confirmatory analysis — H4' attribution purity (RQ4 successor).

Pre-frozen under docs/prereg_v2/PREREGISTRATION_STUDY2_v1.1.md before Study-2
data generation; any post-data modification must be disclosed as a deviation.

Implements EXACTLY the registered H4' test (PREREGISTRATION_STUDY2_v1.1.md §3
H4', §7b contract, supersedes v1.0 H2-7):

  Family E — H4' (RQ4 successor).  Mean ``suspect_share`` (LRCA multi-stratum
    leakage fraction) over the 140 confirmatory cells (28 PUTs x 5 MP).  Per
    cell, suspect_share = (killed mutants that are MULTI-STRATUM, flip>=2) /
    (killed mutants in the cell); 0 when the cell has no kills.  Registered
    threshold: mean suspect_share <= 0.05 (margin 0.037 above the projected
    rule-of-three upper bound 0.0131 under the single-stratum spec constraint,
    power_study2_v11.json::h4_attribution).

  Decision (§3 H4'):
    * mean suspect_share <= 0.05 -> CONFIRM attribution purity.
    * otherwise                  -> observed leakage + offending families
                                    reported factually.

LRCA MACHINERY IS IDENTICAL TO STUDY 1.  The per-mutant multi-stratum
classification is NOT reimplemented here: it is imported from
``p2.mutators.stratum_filter`` (``audit_matrix`` / ``classify_flips``), which
"mirrors scripts/compute_s5_purity.py exactly" — the SAME offline invariant-flip
definition (a mutant perturbs invariant k iff KILLED under MP_k) used by the
Study-1 S5 audit (data/results/s5_purity_v4.json) and by the CF/TF single-
stratum admission filter.  No measurement change is introduced pre- or post-data.

EXCLUSIONS (§2b, §2c).  Pilot PUTs {a2, b4} and all Study-1 pools are excluded;
only the 28 registered confirmatory PUTs (140 cells) enter the mean.

INTEGRITY.  Pure function of the frozen per-cell SMS matrix plus the registered
constants (threshold, family list).  No tunable knob outside the registration;
no data peeking.

Inputs (registration §7b):
  per-cell SMS matrix : data/results/sms_track2_v5.json  (150-cell matrix; each
                        cell's ``outcomes`` list of {file, label} IS the Study-2
                        LRCA per-mutant classification substrate)
Output:
  data/results/s5_purity_v5.json

Usage:
    PYTHONPATH=src python3 scripts/compute_h4_attribution.py
    PYTHONPATH=src python3 scripts/compute_h4_attribution.py \
        --matrix data/results/sms_track2_v5.json \
        --out    data/results/s5_purity_v5.json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

# LRCA / S5 multi-stratum machinery — IMPORTED, never reimplemented (§3 H4').
# audit_matrix classifies every mutant's invariant-flip count exactly as the
# Study-1 S5 audit; category_from_filename gives the operator family.
from p2.mutators.stratum_filter import (  # noqa: E402
    audit_matrix, category_from_filename, KILLED,
)

RESULTS = ROOT / "data" / "results"

# ---- registered constants (PREREGISTRATION_STUDY2_v1.1.md §2c, §3 H4') ------
MASTER_SEED = 20260708               # registration master seed (§7) — recorded
REGISTERED_THRESHOLD = 0.05          # mean suspect_share bar (§3 H4')
PROJECTED_UPPER = 0.0131             # rule-of-three 3/229 projection (v11 SSOT)
MARGIN = 0.0369                      # margin_above_projected_upper (v11 SSOT)
N_CONFIRMATORY_CELLS = 140           # 28 PUTs x 5 MP (§3 H4')
MULTISTRATUM_MIN_FLIP = 2            # flip>=2 == multi-stratum (S5 definition)
FAMILIES = ["CE", "CF", "HP", "OS", "SI", "TF"]   # incl. CF/TF (Study-1 leakers)
PILOT_PUTS = frozenset({"a2", "b4"})        # calibration pilot (§2b), excluded
CONFIRMATORY_PUTS = [
    "a1", "a3", "a4", "a5", "a6", "a7", "a8",
    "b1", "b2", "b3", "b5", "b6", "b7",
    "c1", "c2", "c3", "c4", "c5", "c6", "c7",
    "d1", "d2", "d3", "d4", "d5", "d6", "d7", "d8",
]

MATRIX = RESULTS / "sms_track2_v5.json"
OUT = RESULTS / "s5_purity_v5.json"

_CELL_RE = re.compile(r"^([A-Da-d]\d+)_MP([1-5])$")


# --------------------------------------------------------------------------- #
# SSOT ingestion + validation
# --------------------------------------------------------------------------- #
def _rel(path) -> str:
    try:
        return str(Path(path).resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def _validate_cell(key: str, cell) -> None:
    if not _CELL_RE.match(key):
        raise ValueError(f"malformed SMS cell key (expected '<PUT>_MP<k>'): {key!r}")
    if not isinstance(cell, dict) or "outcomes" not in cell:
        raise ValueError(f"cell {key!r} missing 'outcomes' list")
    for o in cell["outcomes"]:
        if not isinstance(o, dict) or "file" not in o or "label" not in o:
            raise ValueError(f"cell {key!r} has a malformed outcome entry: {o!r}")


def load_matrix(path: str | Path) -> dict:
    matrix = json.loads(Path(path).read_text())
    for k, v in matrix.items():
        _validate_cell(k, v)
    return matrix


def _confirmatory_upper(matrix: dict) -> list:
    """Uppercase confirmatory PUT ids actually present in the matrix (pilots out)."""
    present = {k.split("_")[0].lower() for k in matrix}
    return [p.upper() for p in CONFIRMATORY_PUTS if p in present]


# --------------------------------------------------------------------------- #
# H4' — per-cell suspect_share via the IMPORTED S5 classification
# --------------------------------------------------------------------------- #
def multistratum_flip_map(matrix: dict, puts_upper: list) -> dict:
    """{(put_upper, file): flip_count} via the Study-1 S5 audit machinery.

    Delegates entirely to p2.mutators.stratum_filter.audit_matrix — no local
    reimplementation of the invariant-flip classifier.
    """
    audit = audit_matrix(matrix, puts_upper)
    return {(m["put"], m["file"]): m["flip_count"] for m in audit["per_mutant"]}


def analyze_h4(matrix: dict) -> dict:
    puts_upper = _confirmatory_upper(matrix)
    flips = multistratum_flip_map(matrix, puts_upper)

    per_cell = {}
    shares = []
    missing_cells = []
    for put in puts_upper:
        for mp in range(1, 6):
            key = f"{put}_MP{mp}"
            cell = matrix.get(key)
            if cell is None:
                missing_cells.append(key)
                continue
            killed = [o["file"] for o in cell["outcomes"] if o["label"] == KILLED]
            suspect = [f for f in killed
                       if flips.get((put, f), 0) >= MULTISTRATUM_MIN_FLIP]
            share = (len(suspect) / len(killed)) if killed else 0.0
            per_cell[key] = {
                "n_killed": len(killed), "n_suspect_multistratum": len(suspect),
                "suspect_share": round(share, 4),
            }
            shares.append(share)

    mean_share = sum(shares) / len(shares) if shares else 0.0

    # Per-family multi-stratum breakdown (offending families, §3 H4').
    per_family = {fam: {"n_mutants": 0, "n_multistratum": 0} for fam in FAMILIES}
    for (put, fname), flip in flips.items():
        fam = category_from_filename(fname)
        if fam not in per_family:
            per_family[fam] = {"n_mutants": 0, "n_multistratum": 0}
        per_family[fam]["n_mutants"] += 1
        if flip >= MULTISTRATUM_MIN_FLIP:
            per_family[fam]["n_multistratum"] += 1

    verdict = "CONFIRM" if mean_share <= REGISTERED_THRESHOLD else "NOT_CONFIRMED"
    if verdict == "CONFIRM":
        licensed = ("attribution is pure (mean suspect_share <= 0.05) under the "
                    "single-stratum spec constraint")
    else:
        offenders = sorted(f for f, r in per_family.items()
                           if r["n_multistratum"] > 0)
        licensed = ("observed multi-stratum leakage exceeds 0.05; offending "
                    f"families reported factually: {offenders}")

    return {
        "family": "E — Attribution purity (descriptive mean, verdict-factual)",
        "statistic": "mean suspect_share (multi-stratum leakage fraction) over "
                     "the 140 confirmatory cells (28 PUTs x 5 MP)",
        "lrca_machinery": "IMPORTED from p2.mutators.stratum_filter.audit_matrix "
                          "(identical to the Study-1 S5 audit / "
                          "scripts/compute_s5_purity.py; not reimplemented)",
        "registered_threshold": REGISTERED_THRESHOLD,
        "projected_upper_rule_of_three": PROJECTED_UPPER,
        "margin_above_projected_upper": MARGIN,
        "n_cells_expected": N_CONFIRMATORY_CELLS,
        "n_cells_scored": len(shares),
        "cells_missing": missing_cells,
        "pilot_puts_excluded": sorted(PILOT_PUTS),
        "mean_suspect_share": round(mean_share, 4),
        "per_family_multistratum": per_family,
        "verdict": verdict,
        "licensed_claim": licensed,
        "per_cell_suspect_share": per_cell,
    }


# --------------------------------------------------------------------------- #
# Driver
# --------------------------------------------------------------------------- #
def run(matrix_path=MATRIX, out_path=OUT) -> dict:
    matrix = load_matrix(matrix_path)
    report = {
        "artefact": "s5_purity_v5",
        "generated_by": "scripts/compute_h4_attribution.py",
        "pre_registration": "docs/prereg_v2/PREREGISTRATION_STUDY2_v1.1.md "
                            "(§3 H4'; §2b/§2c pilot exclusion; §7b contract)",
        "integrity": "Pre-frozen before Study-2 data generation; any post-data "
                     "modification must be disclosed as a deviation.",
        "inputs": {"per_cell_sms_matrix": _rel(matrix_path)},
        "master_seed": MASTER_SEED,
        "H4_attribution_purity": analyze_h4(matrix),
    }
    if out_path is not None:
        Path(out_path).write_text(json.dumps(report, indent=2, ensure_ascii=False))
    return report


def _print_verdicts(report: dict) -> None:
    h4 = report["H4_attribution_purity"]
    print("=== Study-2 H4' attribution-purity verdict (confirmatory) ===")
    print(f"cells scored: {h4['n_cells_scored']}/{h4['n_cells_expected']} "
          f"(pilots excluded: {h4['pilot_puts_excluded']})")
    print(f"mean suspect_share = {h4['mean_suspect_share']:.4f} "
          f"(bar <= {REGISTERED_THRESHOLD}; projected upper {PROJECTED_UPPER})")
    ms = {f: r["n_multistratum"] for f, r in h4["per_family_multistratum"].items()
          if r["n_multistratum"] > 0}
    print(f"    multi-stratum by family: {ms or 'none'}")
    print(f"    VERDICT: {h4['verdict']} — {h4['licensed_claim']}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--matrix", default=str(MATRIX),
                    help="per-cell SMS matrix SSOT (150-cell)")
    ap.add_argument("--out", default=str(OUT), help="output SSOT path")
    args = ap.parse_args()
    if not Path(args.matrix).exists():
        print(f"ERROR: per-cell SMS matrix SSOT missing: {args.matrix}\n"
              "This script runs on the ANALYSIS leg, after Study-2 SMS scoring "
              "(CAMPAIGN_RUNBOOK.md §2.4). No Study-2 data exists yet at freeze "
              "time.", file=sys.stderr)
        return 2
    report = run(args.matrix, args.out)
    _print_verdicts(report)
    print(f"\nwrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
