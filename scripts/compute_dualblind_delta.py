#!/usr/bin/env python3
"""Study-2 confirmatory analysis — SMS-grid magnitude (H2-1) + dual-blind
source-diversity Delta-delta (H2-2).

Pre-frozen under PREREGISTRATION_STUDY2.md before Study-2 data generation; any
post-data modification must be disclosed as a deviation.

Implements EXACTLY the registered tests of PREREGISTRATION_STUDY2.md §3:

  Family A — H2-1 (RQ-S2a).  Two-sample Cliff's delta between the aligned slice
    (j=k, primary MP per the §4 deterministic class rule) and the cross slice
    (j!=k) on the 30-PUT x 5-MP grid.  Registered test: one-sided 95%
    percentile-bootstrap LOWER bound (multinomial two-sample bootstrap,
    B=10,000, master seed 20260708) must exceed 0.  Decision: lower bound > 0
    -> CONFIRM aligned dominates cross (a directional construct claim, NOT a
    large-effect claim).  The point delta + two-sided CI are reported against
    the Romano (2006) 0.147/0.330/0.474 bands DESCRIPTIVELY only (exploratory).

  Family B — H2-2 (RQ-S2b).  Delta-delta = delta(cross-source arm) -
    delta(same-source arm), both arms scored on the same 30 PUTs under the
    identical §5 dual-blind protocol.  Registered test: paired-role bootstrap
    (block-resample the 30 PUTs, SAME resample applied to both arms so the two
    per-arm deltas stay paired), 95% two-sided CI (B=10,000, seed 20260708).
    Decision rule (§3 H2-2):
      * CI excludes 0                          -> CONFIRM effect of magnitude >=0.20
      * CI includes 0 AND half-width <= 0.14   -> BOUNDED NULL (no >=0.20 effect
                                                  detectable under matched protocol)
      * CI includes 0 AND half-width  > 0.14   -> UNDER-RECRUITED (inconclusive)

INTEGRITY.  This script is a pure function of its input SSOTs plus the
registered constants below (seed, B, primary-MP rule, thresholds).  It contains
no tunable knob outside the registration and never peeks at data other than the
two SMS pool SSOTs it is given.  It writes no verdict that is not licensed by
the registered decision rules.

Inputs (registration §7 SSOT paths):
  cross-source arm SMS pool : data/results/sms_track2_v5.json        (also H2-1 grid)
  same-source  arm SMS pool : data/results/sms_track2_v5_same.json   (companion arm)
Output:
  data/results/dualblind_delta_delta_v5.json

Usage:
    PYTHONPATH=src python3 scripts/compute_dualblind_delta.py
    PYTHONPATH=src python3 scripts/compute_dualblind_delta.py \
        --cross data/results/sms_track2_v5.json \
        --same  data/results/sms_track2_v5_same.json \
        --out   data/results/dualblind_delta_delta_v5.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

# Registered primary-MP rule (§4): the deterministic, taxonomy-indexed v3 map
# (A->MP1, B->MP2, C->MP5-held, D->MP2). The v3b outcome-conditioned path is
# prohibited in Study 2, so we bind to PRIMARY_CELLS_V3 directly (never the
# env-resolved PRIMARY_CELLS, which could be v3b).
from p2.config.primary import PRIMARY_CELLS_V3 as PRIMARY  # noqa: E402

RESULTS = ROOT / "data" / "results"

# ---- registered constants (PREREGISTRATION_STUDY2.md §3, §7) --------------
MASTER_SEED = 20260708          # registration master seed (§7)
B_BOOT = 10_000                 # bootstrap resamples (§3 H2-1, H2-2)
ROMANO = (0.147, 0.330, 0.474)  # Romano (2006) bands — DESCRIPTIVE only (§3)
DD_MAGNITUDE = 0.20             # H2-2 registered detectable magnitude (§3)
DD_HALFWIDTH_BOUND = 0.14       # H2-2 bounded-null half-width gate (§3)
STUDY1_DD = -0.009              # Study-1 Delta-delta sign anchor (§0, §8)

SMS_CROSS = RESULTS / "sms_track2_v5.json"
SMS_SAME = RESULTS / "sms_track2_v5_same.json"
OUT = RESULTS / "dualblind_delta_delta_v5.json"


# --------------------------------------------------------------------------- #
# SSOT ingestion + registered exclusion rules (§7)
# --------------------------------------------------------------------------- #
def _is_excluded(cell_value: dict | None) -> bool:
    """Analysis-time exclusion (§7): vacant cells (not adjudicated) are dropped.

    A cell is excluded iff it is absent (handled by the loop), carries an
    explicit vacancy flag (``vacant`` true / ``adjudicated`` false), or has a
    null SMS. A dead PUT (all five cells equivalent) is NOT excluded: its cells
    are present with sms=0 and contribute zeros, per §7.
    """
    if cell_value is None:
        return True
    if cell_value.get("vacant") is True or cell_value.get("adjudicated") is False:
        return True
    return cell_value.get("sms") is None


def _parse_cell(cell: str) -> tuple[str, int]:
    put = cell.split("_")[0].lower()
    mp = int(cell.split("MP")[1])
    return put, mp


def _rel(path) -> str:
    """Repo-relative string when possible, else the path as given."""
    try:
        return str(Path(path).resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def load_sms(path: str | Path) -> dict:
    return json.loads(Path(path).read_text())


def split_aligned_cross(sms: dict) -> tuple[list, list]:
    """Split a 150-cell SMS pool into (aligned, cross) SMS lists.

    aligned = cells whose MP equals the PUT's registered primary MP (§4);
    cross = all other adjudicated cells. Vacant cells are excluded (§7).
    """
    aligned, cross = [], []
    for cell, v in sms.items():
        if _is_excluded(v):
            continue
        put, mp = _parse_cell(cell)
        (aligned if mp == PRIMARY[put] else cross).append(float(v["sms"]))
    return aligned, cross


def per_put_slices(sms: dict) -> dict:
    """{put: (aligned_vals, cross_vals)} for the paired-role bootstrap (§3 H2-2)."""
    out: dict[str, tuple[list, list]] = {}
    for cell, v in sms.items():
        if _is_excluded(v):
            continue
        put, mp = _parse_cell(cell)
        a, c = out.setdefault(put, ([], []))
        (a if mp == PRIMARY[put] else c).append(float(v["sms"]))
    return out


# --------------------------------------------------------------------------- #
# Cliff's delta + registered bootstraps
# --------------------------------------------------------------------------- #
def cliffs_delta(a, b) -> float:
    """delta = P(a>b) - P(a<b) (ties count 0). Returns 0.0 if either side empty."""
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    if a.size == 0 or b.size == 0:
        return 0.0
    return float(np.sign(a[:, None] - b[None, :]).mean())


def boot_delta_distribution(a, b, B: int = B_BOOT, seed: int = MASTER_SEED) -> np.ndarray:
    """Multinomial two-sample bootstrap of Cliff's delta (§3 H2-1).

    delta* = (wr @ D @ wc)/(na*nc) with wr,wc multinomial(n, uniform) resample
    counts. This equals the standard nonparametric two-sample bootstrap and is
    the exact method used by the pre-registration power analysis.
    """
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    na, nc = a.size, b.size
    if na == 0 or nc == 0:
        return np.zeros(B)
    D = np.sign(a[:, None] - b[None, :])
    rng = np.random.default_rng(seed)
    WR = rng.multinomial(na, np.full(na, 1.0 / na), size=B).astype(float)
    WC = rng.multinomial(nc, np.full(nc, 1.0 / nc), size=B).astype(float)
    return np.einsum("bi,bi->b", WR, WC @ D.T) / (na * nc)


def romano_band(delta: float) -> str:
    """Descriptive Romano (2006) band label (EXPLORATORY; never a confirmatory pass)."""
    m = abs(delta)
    if m >= ROMANO[2]:
        return "large (>=0.474)"
    if m >= ROMANO[1]:
        return "medium (>=0.330)"
    if m >= ROMANO[0]:
        return "small (>=0.147)"
    return "negligible (<0.147)"


# --------------------------------------------------------------------------- #
# H2-1 — aligned dominates cross (Family A)
# --------------------------------------------------------------------------- #
def verdict_h2_1(lower_95_one_sided: float) -> tuple[str, str]:
    """Registered decision rule (§3 H2-1): lower bound > 0 -> CONFIRM."""
    if lower_95_one_sided > 0.0:
        return ("CONFIRM",
                "aligned slice dominates cross (directional construct claim; "
                "NOT a large-effect claim)")
    return ("NOT_CONFIRMED", "no directional dominance claim licensed on this pool")


def analyze_h2_1(sms_cross: dict, B: int = B_BOOT, seed: int = MASTER_SEED) -> dict:
    aligned, cross = split_aligned_cross(sms_cross)
    delta = cliffs_delta(aligned, cross)
    dist = boot_delta_distribution(aligned, cross, B=B, seed=seed)
    lower = float(np.quantile(dist, 0.05))              # one-sided 95% lower
    ci_lo = float(np.quantile(dist, 0.025))             # two-sided 95% (descriptive)
    ci_hi = float(np.quantile(dist, 0.975))
    verdict, licensed = verdict_h2_1(lower)
    return {
        "family": "A — SMS magnitude (single test, confirmatory)",
        "statistic": "two-sample Cliff's delta, aligned (j=k) vs cross (j!=k)",
        "n_aligned": len(aligned),
        "n_cross": len(cross),
        "cliffs_delta": round(delta, 4),
        "bootstrap_B": B,
        "bootstrap_seed": seed,
        "one_sided_95_lower_bound": round(lower, 4),
        "registered_test": "one-sided 95% percentile-bootstrap lower bound > 0",
        "verdict": verdict,
        "licensed_claim": licensed,
        "descriptive_only": {
            "two_sided_ci95": [round(ci_lo, 4), round(ci_hi, 4)],
            "romano_band": romano_band(delta),
            "note": "Romano band + two-sided CI are EXPLORATORY (§3, §7); "
                    "never promoted to a confirmatory large-effect pass.",
        },
    }


# --------------------------------------------------------------------------- #
# H2-2 — source-diversity Delta-delta under matched dual-blind protocol (Family B)
# --------------------------------------------------------------------------- #
def _arm_delta(slices: dict, puts) -> float:
    aligned = [x for p in puts for x in slices[p][0]]
    cross = [x for p in puts for x in slices[p][1]]
    return cliffs_delta(aligned, cross)


def paired_bootstrap_dd(cross_slices: dict, same_slices: dict, puts,
                        B: int = B_BOOT, seed: int = MASTER_SEED):
    """Paired-role bootstrap of Delta-delta (§3 H2-2).

    Block-resample the shared PUT set; the SAME resample indexes both arms so
    the two per-arm deltas stay paired (positive correlation -> the registered
    paired SE). Returns (point_dd, lo, hi, distribution).
    """
    puts = list(puts)
    n = len(puts)
    point = _arm_delta(cross_slices, puts) - _arm_delta(same_slices, puts)
    if n == 0:
        return point, 0.0, 0.0, np.zeros(B)
    rng = np.random.default_rng(seed)
    dd = np.empty(B)
    for i in range(B):
        idx = rng.integers(0, n, size=n)
        samp = [puts[j] for j in idx]
        dd[i] = _arm_delta(cross_slices, samp) - _arm_delta(same_slices, samp)
    lo = float(np.quantile(dd, 0.025))
    hi = float(np.quantile(dd, 0.975))
    return point, lo, hi, dd


def verdict_h2_2(lo: float, hi: float) -> tuple[str, str, float]:
    """Registered three-way decision rule (§3 H2-2)."""
    half_width = (hi - lo) / 2.0
    excludes_zero = lo > 0.0 or hi < 0.0
    if excludes_zero:
        return ("CONFIRM",
                "a source-diversity effect of magnitude >=0.20 (CI excludes 0)",
                half_width)
    if half_width <= DD_HALFWIDTH_BOUND:
        return ("BOUNDED_NULL",
                "no source-diversity effect of magnitude >=0.20 is detectable "
                "under matched protocol; supports the MR-design-is-the-lever "
                "thesis as CONFIRMED (not confounded)",
                half_width)
    return ("UNDER_RECRUITED",
            "inconclusive: CI includes 0 with half-width > 0.14",
            half_width)


def analyze_h2_2(sms_cross: dict, sms_same: dict, B: int = B_BOOT,
                 seed: int = MASTER_SEED) -> dict:
    cross_slices = per_put_slices(sms_cross)
    same_slices = per_put_slices(sms_same)
    puts = sorted(set(cross_slices) & set(same_slices))
    delta_cross = _arm_delta(cross_slices, puts)
    delta_same = _arm_delta(same_slices, puts)
    point, lo, hi, _ = paired_bootstrap_dd(cross_slices, same_slices, puts,
                                           B=B, seed=seed)
    verdict, licensed, half_width = verdict_h2_2(lo, hi)
    reverses = (verdict == "CONFIRM"
                and np.sign(point) != np.sign(STUDY1_DD) and STUDY1_DD != 0.0)
    return {
        "family": "B — Source diversity (single test, confirmatory)",
        "statistic": "Delta-delta = delta(cross-source) - delta(same-source), "
                     "paired on PUTs under the identical §5 dual-blind protocol",
        "n_puts_paired": len(puts),
        "delta_cross_source_arm": round(delta_cross, 4),
        "delta_same_source_arm": round(delta_same, 4),
        "delta_delta_point": round(point, 4),
        "bootstrap_B": B,
        "bootstrap_seed": seed,
        "ci95_two_sided": [round(lo, 4), round(hi, 4)],
        "ci95_half_width": round(half_width, 4),
        "registered_magnitude_of_interest": DD_MAGNITUDE,
        "registered_halfwidth_bound": DD_HALFWIDTH_BOUND,
        "verdict": verdict,
        "licensed_claim": licensed,
        "reverses_study1_direction": bool(reverses),
    }


# --------------------------------------------------------------------------- #
# Driver
# --------------------------------------------------------------------------- #
def run(cross_path=SMS_CROSS, same_path=SMS_SAME, out_path=OUT,
        B: int = B_BOOT, seed: int = MASTER_SEED) -> dict:
    sms_cross = load_sms(cross_path)
    sms_same = load_sms(same_path)
    report = {
        "artefact": "dualblind_delta_delta_v5",
        "generated_by": "scripts/compute_dualblind_delta.py",
        "pre_registration": "docs/prereg_v2/PREREGISTRATION_STUDY2.md (§3 H2-1, "
                            "H2-2; §4 primary-MP rule; §7 SSOT/seeds)",
        "integrity": "Pre-frozen before Study-2 data generation; any post-data "
                     "modification must be disclosed as a deviation.",
        "inputs": {
            "cross_source_arm_sms": _rel(cross_path),
            "same_source_arm_sms": _rel(same_path),
        },
        "master_seed": seed,
        "bootstrap_B": B,
        "primary_mp_rule": "PRIMARY_CELLS_V3 (§4 deterministic class rule; "
                           "v3b prohibited)",
        "H2_1_aligned_dominates_cross": analyze_h2_1(sms_cross, B=B, seed=seed),
        "H2_2_source_diversity_dual_blind": analyze_h2_2(sms_cross, sms_same,
                                                         B=B, seed=seed),
    }
    if out_path is not None:
        Path(out_path).write_text(json.dumps(report, indent=2, ensure_ascii=False))
    return report


def _print_verdicts(report: dict) -> None:
    h1 = report["H2_1_aligned_dominates_cross"]
    h2 = report["H2_2_source_diversity_dual_blind"]
    print("=== Study-2 SMS-grid + dual-blind confirmatory verdicts ===")
    print(f"[H2-1 / Family A] delta={h1['cliffs_delta']:+.4f} "
          f"one-sided 95% lower={h1['one_sided_95_lower_bound']:+.4f} "
          f"(n_aligned={h1['n_aligned']}, n_cross={h1['n_cross']})")
    print(f"    VERDICT: {h1['verdict']} — {h1['licensed_claim']}")
    print(f"    (descriptive) Romano band: {h1['descriptive_only']['romano_band']}, "
          f"two-sided CI {h1['descriptive_only']['two_sided_ci95']}")
    print(f"[H2-2 / Family B] Delta-delta={h2['delta_delta_point']:+.4f} "
          f"CI {h2['ci95_two_sided']} half-width={h2['ci95_half_width']:.4f} "
          f"(n_puts={h2['n_puts_paired']})")
    print(f"    VERDICT: {h2['verdict']} — {h2['licensed_claim']}")
    if h2["reverses_study1_direction"]:
        print("    NOTE: confirmed Delta-delta REVERSES the Study-1 direction "
              "(counts against the construct per §8).")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cross", default=str(SMS_CROSS),
                    help="cross-source arm SMS pool SSOT")
    ap.add_argument("--same", default=str(SMS_SAME),
                    help="same-source arm SMS pool SSOT")
    ap.add_argument("--out", default=str(OUT), help="output SSOT path")
    args = ap.parse_args()
    for p in (args.cross, args.same):
        if not Path(p).exists():
            print(f"ERROR: input SSOT missing: {p}\n"
                  "This script runs on the ANALYSIS leg, after Study-2 data "
                  "generation (CAMPAIGN_RUNBOOK.md §2). No Study-2 data exists "
                  "yet at freeze time.", file=sys.stderr)
            return 2
    report = run(args.cross, args.same, args.out)
    _print_verdicts(report)
    print(f"\nwrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
