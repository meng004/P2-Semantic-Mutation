#!/usr/bin/env python3
"""Study-2 confirmatory analysis — H3' cross-class direction consistency.

Pre-frozen under docs/prereg_v2/PREREGISTRATION_STUDY2_v1.1.md before Study-2
data generation; any post-data modification must be disclosed as a deviation.

Implements EXACTLY the registered H3' test (PREREGISTRATION_STUDY2_v1.1.md §3
H3', §7b contract, supersedes v1.0 H2-6):

  Family E — H3' (RQ5 successor).  Per design class (A, B, C, D), the SIGN of
    (class-mean aligned SMS - class-mean cross SMS) over the class's
    confirmatory PUTs (A7/B6/C7/D8).  Registered threshold: positive direction
    (aligned > cross) in >=3 of the 4 classes (simulated power 0.949,
    power_study2_v11.json::h3_class_consistency).

  Why not per-class significance (§3 H3').  Per-class one-sided binomial sign
    tests are UNDERPOWERED at 6-8 PUTs/class with heavy SMS ties (simulated
    per-class power ~0.05-0.06); registering 4/4 significant sign tests would
    repeat the Study-1 under-powering.  The >=3/4 DIRECTION criterion is the
    achievable, powered confirmatory test.  Per-class binomial sign-test
    p-values are reported DESCRIPTIVELY; Friedman chi^2 across the 5 MPs stays
    EXPLORATORY (Family X), exactly as Study 1.

  Decision (§3 H3'):
    * >=3 of 4 classes positive -> CONFIRM cross-class consistency.
    * otherwise                 -> direction not consistent, reported factually.

EXCLUSIONS (§2b, §2c).  Pilot PUTs {a2, b4} and all Study-1 pools are excluded;
only the 28 registered confirmatory PUTs enter the class means.

INTEGRITY.  Pure function of the frozen per-cell SMS pool plus the registered
constants (primary-MP rule §4, thresholds).  The aligned slice of a PUT is the
cell whose MP equals the PUT's registered primary MP under PRIMARY_CELLS_V3
(A->MP1, B->MP2, C->MP5-held, D->MP2); the v3b outcome-conditioned path is
prohibited (§4).  No tunable knob outside the registration; no data peeking.

Inputs (registration §7b):
  per-cell SMS pool : data/results/sms_track2_v5.json  (150-cell matrix)
Output:
  data/results/h3_class_consistency_v5.json

Usage:
    PYTHONPATH=src python3 scripts/compute_h3_class_consistency.py
    PYTHONPATH=src python3 scripts/compute_h3_class_consistency.py \
        --pool data/results/sms_track2_v5.json \
        --out  data/results/h3_class_consistency_v5.json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from scipy.stats import binomtest, friedmanchisquare

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

# Registered primary-MP rule (§4): the deterministic class-indexed v3 map. Bind
# to PRIMARY_CELLS_V3 directly (never env-resolved PRIMARY, which could be v3b).
from p2.config.primary import PRIMARY_CELLS_V3 as PRIMARY  # noqa: E402

RESULTS = ROOT / "data" / "results"

# ---- registered constants (PREREGISTRATION_STUDY2_v1.1.md §2c, §3 H3') ------
MASTER_SEED = 20260708               # registration master seed (§7) — recorded
CLASSES = ["a", "b", "c", "d"]       # design classes A/B/C/D
REG_POSITIVE_CLASSES = 3             # ">=3 of 4 classes positive" (§3)
N_CLASSES = 4
REGISTERED_POWER = 0.949             # power_study2_v11.json::h3_class_consistency
DIRECTION_EPS = 1e-9                  # float-noise tolerance for exact ties
PILOT_PUTS = frozenset({"a2", "b4"})        # calibration pilot (§2b), excluded
CONFIRMATORY_PUTS = [
    "a1", "a3", "a4", "a5", "a6", "a7", "a8",
    "b1", "b2", "b3", "b5", "b6", "b7",
    "c1", "c2", "c3", "c4", "c5", "c6", "c7",
    "d1", "d2", "d3", "d4", "d5", "d6", "d7", "d8",
]
CLASS_SIZES = {"a": 7, "b": 6, "c": 7, "d": 8}   # confirmatory A7/B6/C7/D8 (§2c)

POOL = RESULTS / "sms_track2_v5.json"
OUT = RESULTS / "h3_class_consistency_v5.json"

_CELL_RE = re.compile(r"^([A-Da-d]\d+)_MP([1-5])$")


# --------------------------------------------------------------------------- #
# SSOT ingestion + registered exclusion rules (§7)
# --------------------------------------------------------------------------- #
def _rel(path) -> str:
    try:
        return str(Path(path).resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def _is_excluded(cell) -> bool:
    """Analysis-time exclusion (§7): vacant / unadjudicated / null-SMS cells."""
    if cell is None:
        return True
    if cell.get("vacant") is True or cell.get("adjudicated") is False:
        return True
    return cell.get("sms") is None


def _validate_cell(key: str, cell) -> None:
    if not _CELL_RE.match(key):
        raise ValueError(f"malformed SMS cell key (expected '<PUT>_MP<k>'): {key!r}")
    if not isinstance(cell, dict) or "sms" not in cell:
        raise ValueError(f"cell {key!r} missing 'sms' field")


def load_pool(path: str | Path) -> dict:
    matrix = json.loads(Path(path).read_text())
    for k, v in matrix.items():
        _validate_cell(k, v)
    return matrix


def per_put_sms(matrix: dict) -> dict:
    """{put: {mp: sms}} over the 28 confirmatory PUTs (pilot / Study-1 dropped)."""
    keep = set(CONFIRMATORY_PUTS)
    out: dict[str, dict] = {}
    for key, cell in matrix.items():
        put = key.split("_")[0].lower()
        mp = int(key.split("MP")[1])
        if put not in keep or _is_excluded(cell):
            continue
        out.setdefault(put, {})[mp] = float(cell["sms"])
    return out


# --------------------------------------------------------------------------- #
# H3' — per-class aligned>cross direction + descriptive / exploratory companions
# --------------------------------------------------------------------------- #
def _put_aligned_cross(mp_sms: dict, put: str) -> tuple[float | None, list]:
    """(aligned_sms, [cross_sms...]) for one PUT under the §4 primary-MP rule."""
    prim = PRIMARY[put]
    aligned = mp_sms.get(prim)
    cross = [v for mp, v in mp_sms.items() if mp != prim]
    return aligned, cross


def analyze_class(sms: dict, cls: str) -> dict:
    """Class-mean aligned vs cross direction + descriptive per-class sign test."""
    puts = [p for p in CONFIRMATORY_PUTS if p[0] == cls and p in sms]
    aligned_vals, cross_vals = [], []
    per_put_delta = []          # aligned - mean(cross) per PUT (descriptive sign)
    for p in puts:
        a, c = _put_aligned_cross(sms[p], p)
        if a is not None:
            aligned_vals.append(a)
        cross_vals.extend(c)
        if a is not None and c:
            per_put_delta.append((p, a - (sum(c) / len(c))))
    class_mean_aligned = sum(aligned_vals) / len(aligned_vals) if aligned_vals else None
    class_mean_cross = sum(cross_vals) / len(cross_vals) if cross_vals else None
    direction = None
    positive = False
    if class_mean_aligned is not None and class_mean_cross is not None:
        diff = class_mean_aligned - class_mean_cross
        # Tolerance guards against float-representation noise on exact ties; the
        # registered criterion is a strict positive direction (aligned > cross).
        if abs(diff) <= DIRECTION_EPS:
            direction = "tie"
        elif diff > 0:
            direction = "positive"
        else:
            direction = "negative"
        positive = diff > DIRECTION_EPS

    # Descriptive per-class one-sided binomial sign test (NOT confirmatory).
    n_pos = sum(1 for _p, d in per_put_delta if d > 0)
    n_nonzero = sum(1 for _p, d in per_put_delta if d != 0)
    sign_p = (binomtest(n_pos, n_nonzero, 0.5, alternative="greater").pvalue
              if n_nonzero > 0 else None)

    return {
        "class": cls.upper(),
        "confirmatory_puts": puts,
        "registered_class_size": CLASS_SIZES[cls],
        "class_mean_aligned_sms": (round(class_mean_aligned, 4)
                                   if class_mean_aligned is not None else None),
        "class_mean_cross_sms": (round(class_mean_cross, 4)
                                 if class_mean_cross is not None else None),
        "direction": direction,
        "positive": positive,
        "descriptive_sign_test": {
            "n_puts_positive": n_pos,
            "n_puts_nonzero_delta": n_nonzero,
            "one_sided_binomial_p": (round(sign_p, 4) if sign_p is not None else None),
            "note": "DESCRIPTIVE only (§3 H3'): under-powered at 6-8 PUTs/class "
                    "with heavy SMS ties; never a confirmatory pass.",
        },
    }


def friedman_exploratory(sms: dict) -> dict:
    """Friedman chi^2 across the 5 MPs over confirmatory PUTs (EXPLORATORY, X)."""
    blocks = [sms[p] for p in CONFIRMATORY_PUTS
              if p in sms and all(mp in sms[p] for mp in range(1, 6))]
    if len(blocks) < 2:
        return {"computed": False,
                "reason": "need >=2 PUTs with all 5 MP cells present",
                "family": "X — exploratory"}
    import math
    import warnings
    columns = [[b[mp] for b in blocks] for mp in range(1, 6)]
    try:
        with warnings.catch_warnings():         # degenerate blocks -> nan (handled below)
            warnings.simplefilter("ignore", RuntimeWarning)
            stat, p = friedmanchisquare(*columns)
    except ValueError as e:                     # too few observations etc.
        return {"computed": False, "reason": str(e), "family": "X — exploratory"}
    if math.isnan(stat) or math.isnan(p):       # all-identical blocks -> undefined
        return {"computed": False,
                "reason": "degenerate (no within-PUT rank variation across MPs)",
                "family": "X — exploratory"}
    return {
        "computed": True, "family": "X — exploratory (NOT confirmatory)",
        "n_blocks_puts": len(blocks), "n_treatments_mps": 5,
        "friedman_chi2": round(float(stat), 4), "p_value": round(float(p), 4),
        "note": "Across-MP Friedman stays exploratory exactly as Study 1 (§3).",
    }


def verdict_h3(n_positive: int) -> tuple[str, str]:
    """Registered decision rule (§3 H3'): >=3 of 4 classes positive."""
    if n_positive >= REG_POSITIVE_CLASSES:
        return ("CONFIRM",
                f"aligned>cross direction is consistent across classes "
                f"(>={REG_POSITIVE_CLASSES}/{N_CLASSES} classes positive)")
    return ("NOT_CONFIRMED",
            "aligned>cross direction not consistent across classes; reported "
            "factually (no threshold move)")


def analyze_h3(matrix: dict) -> dict:
    sms = per_put_sms(matrix)
    per_class = [analyze_class(sms, c) for c in CLASSES]
    n_positive = sum(1 for r in per_class if r["positive"])
    verdict, licensed = verdict_h3(n_positive)
    return {
        "family": "E — Cross-class direction consistency (verdict-factual)",
        "statistic": "per class, sign of (class-mean aligned SMS - class-mean "
                     "cross SMS) over the class's confirmatory PUTs",
        "registered_threshold": {
            "positive_classes_required": REG_POSITIVE_CLASSES,
            "of_classes": N_CLASSES,
            "shape": ">=3 of 4 classes show positive aligned>cross direction",
            "power": REGISTERED_POWER,
        },
        "primary_mp_rule": "PRIMARY_CELLS_V3 (§4 deterministic class rule; "
                           "v3b prohibited)",
        "pilot_puts_excluded": sorted(PILOT_PUTS),
        "per_class": per_class,
        "n_classes_positive": n_positive,
        "verdict": verdict,
        "licensed_claim": licensed,
        "friedman_across_mps_exploratory": friedman_exploratory(sms),
    }


# --------------------------------------------------------------------------- #
# Driver
# --------------------------------------------------------------------------- #
def run(pool_path=POOL, out_path=OUT) -> dict:
    matrix = load_pool(pool_path)
    report = {
        "artefact": "h3_class_consistency_v5",
        "generated_by": "scripts/compute_h3_class_consistency.py",
        "pre_registration": "docs/prereg_v2/PREREGISTRATION_STUDY2_v1.1.md "
                            "(§3 H3'; §4 primary-MP rule; §2b/§2c; §7b contract)",
        "integrity": "Pre-frozen before Study-2 data generation; any post-data "
                     "modification must be disclosed as a deviation.",
        "inputs": {"per_cell_sms_pool": _rel(pool_path)},
        "master_seed": MASTER_SEED,
        "H3_class_direction_consistency": analyze_h3(matrix),
    }
    if out_path is not None:
        Path(out_path).write_text(json.dumps(report, indent=2, ensure_ascii=False))
    return report


def _print_verdicts(report: dict) -> None:
    h3 = report["H3_class_direction_consistency"]
    print("=== Study-2 H3' cross-class direction-consistency verdict ===")
    for r in h3["per_class"]:
        print(f"    class {r['class']}: aligned={r['class_mean_aligned_sms']} "
              f"cross={r['class_mean_cross_sms']} -> {r['direction']} "
              f"(descriptive sign p={r['descriptive_sign_test']['one_sided_binomial_p']})")
    print(f"classes positive: {h3['n_classes_positive']}/{N_CLASSES} "
          f"(bar >={REG_POSITIVE_CLASSES})")
    print(f"    VERDICT: {h3['verdict']} — {h3['licensed_claim']}")
    fr = h3["friedman_across_mps_exploratory"]
    if fr.get("computed"):
        print(f"    (exploratory) Friedman chi2={fr['friedman_chi2']} "
              f"p={fr['p_value']}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pool", default=str(POOL),
                    help="per-cell SMS pool SSOT (150-cell matrix)")
    ap.add_argument("--out", default=str(OUT), help="output SSOT path")
    args = ap.parse_args()
    if not Path(args.pool).exists():
        print(f"ERROR: per-cell SMS pool SSOT missing: {args.pool}\n"
              "This script runs on the ANALYSIS leg, after Study-2 SMS scoring "
              "(CAMPAIGN_RUNBOOK.md §2.4). No Study-2 data exists yet at freeze "
              "time.", file=sys.stderr)
        return 2
    report = run(args.pool, args.out)
    _print_verdicts(report)
    print(f"\nwrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
