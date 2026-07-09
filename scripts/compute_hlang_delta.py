#!/usr/bin/env python3
"""Study-4 confirmatory analysis — H-LANG cross-language invariance (RQ-S4c).

Pre-frozen under docs/prereg_v2/PREREGISTRATION_STUDY4_v1.md (§3.3, §7b contract;
Amendment v1.1) BEFORE any Study-4 C-port data generation. Any post-data
modification of this script MUST be disclosed as a deviation in the registration
§10 appendix.

    ┌─────────────────────────────────────────────────────────────────────┐
    │ PRE-FROZEN SCORER — no Study-4 C mutant, C SMS cell, or delta_C       │
    │ outcome existed when this file was frozen. The decision rule below    │
    │ (confirm iff one_sided_95_lower_bound > 0) is the registered a-priori │
    │ rule; changing the estimand or threshold after any C outcome is       │
    │ visible is a protocol violation (registration §5d, §8).               │
    └─────────────────────────────────────────────────────────────────────┘

Implements EXACTLY the registered H-LANG (Family L) verdict
(PREREGISTRATION_STUDY4_v1.md §3.3, §7b):

  On the ACHIEVED C port of the 7 original Study-1 PUTs (a1,a2,a3,b1,b2,b3,c2;
  the 5 sklearn kernels c1/c3/d1/d2/d3 are unportable, C_PORT_SPEC.md §3;
  amendment v1.1), split the per-cell SMS into

      aligned  = cells whose MP == the PUT's primary MP (PRIMARY_CELLS_V3,
                 mapped cell-for-cell to the C cells: a→MP1, b→MP2, c→MP5),
      cross    = all other adjudicated cells,

  compute the two-sample Cliff's delta_C = P(aligned > cross) - P(aligned <
  cross), and its one-sided 95% percentile-bootstrap LOWER bound (multinomial
  two-sample bootstrap, B=10,000, seed 20260708).

    Decision (FROZEN) = CONFIRM cross-language invariance iff
                        one_sided_95_lower_bound > 0.

BOOTSTRAP IS BYTE-IDENTICAL TO H2-1'.  The estimand, the split, and the
resampling scheme are the SAME as compute_dualblind_delta.analyze_h2_1 (the
Study-2 aligned>cross confirmatory test); this scorer imports
``cliffs_delta`` / ``boot_delta_distribution`` / ``_is_excluded`` / ``_parse_cell``
/ ``PRIMARY`` from that frozen module rather than re-implementing them, so no
measurement can drift between the Python and C legs. The only difference is the
grid: H-LANG restricts to the 7 C PUTs and reads the C-port pool.

Power (amendment v1.1): 0.6865 at n=7 from the v5-calibrated DGP (true delta
0.4385); below the 0.80 target and DISCLOSED — the estimand is a direction
claim, and H-LANG stays confirmatory with the achieved power disclosed
(power_study4.json::c...power_delta_gt0_at_n7). NO threshold moved.

EXCLUSIONS (§7b). Vacant / non-adjudicated / null-SMS cells are dropped
(``_is_excluded``, shared with the Python leg). The Python calibration pilot
{a2, b4} firewall does NOT apply here: H-LANG is a distinct C-port estimand and
the C-side data is fresh; a2 is confirmatory in the C grid (amendment v1.1 §0.3).

Inputs (registration §7b):
  C-port per-cell SMS pool : data/results/sms_track2_v7c.json (fresh validated
                             C pool; each cell carries an ``sms`` scalar)
Output:
  data/results/hlang_delta_v7c.json  (verdict + licensed string)

Usage:
    PYTHONPATH=src python3 scripts/compute_hlang_delta.py
    PYTHONPATH=src python3 scripts/compute_hlang_delta.py \
        --matrix data/results/sms_track2_v7c.json \
        --out    data/results/hlang_delta_v7c.json
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

RESULTS = ROOT / "data" / "results"

# ---- registered constants (PREREGISTRATION_STUDY4_v1.md §3.3, §7b) ----------
MASTER_SEED = 20260708          # registration master seed (§7)
B_BOOT = 10_000                 # bootstrap resamples (§3.3, byte-identical to H2-1')
# Achieved C-port grid (amendment v1.1; a2 RETAINED confirmatory).
C_GRID_PUTS = ("a1", "a2", "a3", "b1", "b2", "b3", "c2")

MATRIX = RESULTS / "sms_track2_v7c.json"
OUT = RESULTS / "hlang_delta_v7c.json"


# --------------------------------------------------------------------------- #
# Byte-identical estimand + bootstrap, IMPORTED from the frozen H2-1' scorer.
# --------------------------------------------------------------------------- #
def _load_dualblind_module():
    spec = importlib.util.spec_from_file_location(
        "compute_dualblind_delta", ROOT / "scripts" / "compute_dualblind_delta.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_DBD = _load_dualblind_module()
cliffs_delta = _DBD.cliffs_delta                    # noqa: N816
boot_delta_distribution = _DBD.boot_delta_distribution
_is_excluded = _DBD._is_excluded
_parse_cell = _DBD._parse_cell
PRIMARY = _DBD.PRIMARY                              # PRIMARY_CELLS_V3 (v3b prohibited)


def _rel(path) -> str:
    try:
        return str(Path(path).resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def load_sms(path: str | Path) -> dict:
    return json.loads(Path(path).read_text())


def split_aligned_cross_c(sms: dict) -> tuple[list, list]:
    """Split the C-port SMS pool into (aligned, cross) SMS lists over the 7 C
    PUTs. aligned = cells whose MP equals the PUT's registered primary MP;
    cross = all other adjudicated cells. Vacant cells excluded (§7b).

    Restricted to C_GRID_PUTS so a pool that carries extra cells cannot leak a
    non-C PUT into the C estimand. Uses the SAME _is_excluded / PRIMARY as the
    Python H2-1' leg (imported), so the split is byte-identical."""
    aligned, cross = [], []
    for cell, v in sms.items():
        put, mp = _parse_cell(cell)
        if put not in C_GRID_PUTS:
            continue
        if _is_excluded(v):
            continue
        (aligned if mp == PRIMARY[put] else cross).append(float(v["sms"]))
    return aligned, cross


def _c_puts_present(sms: dict) -> list:
    present = set()
    for cell in sms:
        put, _mp = _parse_cell(cell)
        if put in C_GRID_PUTS:
            present.add(put)
    return sorted(present)


# --------------------------------------------------------------------------- #
# H-LANG — cross-language invariance (Family L)
# --------------------------------------------------------------------------- #
def verdict_hlang(lower_95_one_sided: float) -> tuple[str, str]:
    """Registered decision rule (§3.3): lower bound > 0 -> CONFIRM."""
    if lower_95_one_sided > 0.0:
        return ("CONFIRM",
                "the aligned>cross construct is LANGUAGE-INVARIANT: on the C port "
                "the aligned slice dominates cross (delta_C one-sided 95% lower "
                "bound > 0), replicating the Python direction (NOETHER: MetaPatterns "
                "are operator-algebra invariants, not surface syntax)")
    return ("NOT_CONFIRMED",
            "language-invariance does NOT replicate: the C-port delta_C one-sided "
            "95% lower bound does not exceed 0 — reported as a genuine "
            "falsification of the language-invariance claim, not hedged away")


def analyze_hlang(sms_c: dict, B: int = B_BOOT, seed: int = MASTER_SEED) -> dict:
    aligned, cross = split_aligned_cross_c(sms_c)
    delta = cliffs_delta(aligned, cross)
    dist = boot_delta_distribution(aligned, cross, B=B, seed=seed)
    lower = float(np.quantile(dist, 0.05))              # one-sided 95% lower
    ci_lo = float(np.quantile(dist, 0.025))             # two-sided (descriptive)
    ci_hi = float(np.quantile(dist, 0.975))
    verdict, licensed = verdict_hlang(lower)
    return {
        "family": "L — Cross-language invariance (single test, confirmatory)",
        "statistic": "two-sample Cliff's delta_C, aligned (j=k) vs cross (j!=k), "
                     "on the 7 C PUTs (PRIMARY_CELLS_V3 mapped to the C cells)",
        "c_grid_puts": list(C_GRID_PUTS),
        "n_puts": len(_c_puts_present(sms_c)),
        "n_aligned": len(aligned),
        "n_cross": len(cross),
        "cliffs_delta_C": round(delta, 4),
        "bootstrap_B": B,
        "bootstrap_seed": seed,
        "one_sided_95_lower_bound": round(lower, 4),
        "registered_test": "one-sided 95% percentile-bootstrap lower bound > 0 "
                           "(byte-identical bootstrap to H2-1')",
        "verdict": verdict,
        "verdict_bool": bool(lower > 0.0),
        "licensed_claim": licensed,
        "descriptive_only": {
            "two_sided_ci95": [round(ci_lo, 4), round(ci_hi, 4)],
            "note": "two-sided CI is EXPLORATORY (§3.3); the confirmatory verdict "
                    "is the one-sided lower bound > 0 direction test.",
        },
    }


# --------------------------------------------------------------------------- #
# Driver
# --------------------------------------------------------------------------- #
def run(matrix_path=MATRIX, out_path=OUT, B: int = B_BOOT,
        seed: int = MASTER_SEED) -> dict:
    sms_c = load_sms(matrix_path)
    hlang = analyze_hlang(sms_c, B=B, seed=seed)
    report = {
        "artefact": "hlang_delta_v7c",
        "generated_by": "scripts/compute_hlang_delta.py",
        "pre_registration": "docs/prereg_v2/PREREGISTRATION_STUDY4_v1.md "
                            "(§3.3 H-LANG; §7b contract; Amendment v1.1: n=7, v7c)",
        "integrity": "Pre-frozen before Study-4 C-port data generation; any "
                     "post-data modification must be disclosed as a deviation "
                     "(§5d, §8). Bootstrap byte-identical to H2-1'.",
        "inputs": {"c_port_sms_pool": _rel(matrix_path)},
        "master_seed": seed,
        "bootstrap_B": B,
        "primary_mp_rule": "PRIMARY_CELLS_V3 (A->MP1, B->MP2, C->MP5) mapped "
                           "cell-for-cell to the C cells; v3b prohibited",
        "registered_power": "0.6865 @ n=7 (v5 DGP, true delta 0.4385); below 0.80, "
                            "disclosed (power_study4.json::c...power_delta_gt0_at_n7)",
        "H_LANG_cross_language_invariance": hlang,
    }
    if out_path is not None:
        Path(out_path).parent.mkdir(parents=True, exist_ok=True)
        Path(out_path).write_text(json.dumps(report, indent=2, ensure_ascii=False))
    return report


def _print_verdict(report: dict) -> None:
    h = report["H_LANG_cross_language_invariance"]
    print("=== Study-4 H-LANG cross-language invariance verdict (Family L) ===")
    print(f"[H-LANG] delta_C={h['cliffs_delta_C']:+.4f} "
          f"one-sided 95% lower={h['one_sided_95_lower_bound']:+.4f} "
          f"(n_puts={h['n_puts']}, n_aligned={h['n_aligned']}, "
          f"n_cross={h['n_cross']})")
    print(f"    VERDICT: {h['verdict']} — {h['licensed_claim']}")
    print(f"    (descriptive) two-sided CI {h['descriptive_only']['two_sided_ci95']}")


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--matrix", default=str(MATRIX),
                    help="C-port per-cell SMS pool SSOT (fresh Study-4 v7c pool)")
    ap.add_argument("--out", default=str(OUT),
                    help="output SSOT path ('-' = stdout only, no file write)")
    args = ap.parse_args()
    if not Path(args.matrix).exists():
        print(f"ERROR: C-port SMS pool SSOT missing: {args.matrix}\n"
              "This script runs on the ANALYSIS leg, AFTER Study-4 C-port SMS "
              "scoring of the fresh v7c pool. No Study-4 C confirmatory data "
              "exists yet at freeze time (registration §0.1, §0.3).",
              file=sys.stderr)
        return 2
    out_path = None if args.out == "-" else args.out
    report = run(args.matrix, out_path)
    _print_verdict(report)
    if out_path is not None:
        print(f"\nwrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
