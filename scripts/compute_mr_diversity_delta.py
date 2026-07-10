#!/usr/bin/env python3
"""Study-5 confirmatory analysis — H2-4 MR-side diversity (Family MR).

Pre-frozen under docs/prereg_v2/PREREGISTRATION_STUDY5_v1.md (§3.4, §6 contract)
BEFORE any Study-5 data generation. Any post-data modification of this script
MUST be disclosed as a deviation in the registration amendments log.

    ┌───────────────────────────────────────────────────────────────────────┐
    │ PRE-FROZEN SCORER — no LLM-prompted MR battery, no L-side SMS cell,    │
    │ and no delta_MR outcome existed when this file was frozen              │
    │ (2026-07-10). The decision ladder below is the registered a-priori     │
    │ rule; changing the estimand or a threshold after any L-side outcome    │
    │ is visible is a protocol violation (registration §7, §8).              │
    └───────────────────────────────────────────────────────────────────────┘

Estimand (registration §3.4). The mutant pools are FROZEN (the Study-4 v7
pools, byte-identical, never regenerated); the manipulated variable is the
SOURCE OF THE MR BATTERY that scores them:

  arm R = the registered NOETHER-derived MR batteries — per-cell SMS REUSED
          from the frozen Study-4 v7 SSOTs (never rerun);
  arm L = LLM-prompted MR batteries (four vendors, prompted with the PUT
          source + the target NOETHER MR-family stratum name only; certified
          for executability V1/V2 only, never tuned; per-cell battery = the
          UNION of the four vendors' certified MRs), scored on the
          byte-identical frozen pools.

Per PUT p and Study-4 arm a in {cross, same}: battery-level SMS_B(p, a) =
mean SMS over p's adjudicated cells in arm a under battery B. Per-PUT paired
difference d_p = mean over available arms of [SMS_R(p, a) - SMS_L(p, a)].
Point estimate delta_MR = mean over the 28 confirmatory PUTs of d_p.

Test: paired PUT-level bootstrap of the mean (resample the PUT list with
replacement, B = 10,000, seed 20260708 — the same block-bootstrap scheme as
the H2-2 paired-role bootstrap). alpha = 0.05.

Decision ladder (FROZEN; evaluated top-down, first hit wins):
  0. n_puts_paired < 24 (registered recruitment gate) -> UNDER_RECRUITED
     (fewer than 24 of the 28 confirmatory PUTs yield a paired R/L unit —
     e.g. the LLM batteries failed V1/V2 certification on too many PUTs;
     achieved n and delta_MR reported factually; NO threshold is moved)
  1. one-sided 95% lower bound > 0                  -> CONFIRM
     (algebra-derived batteries dominate LLM-prompted batteries)
  2. two-sided 95% CI upper bound < 0               -> REVERSED
     (LLM-prompted batteries dominate — reported factually; counts against
     the algebra-derivation lever, registration §8)
  3. CI includes 0 AND half-width <= 0.14           -> BOUNDED_EQUIVALENCE
     (no delta_MR effect larger than the registered margin is detectable;
     note: on the SMS scale the projected achieved half-width is far tighter,
     power_study5.json::e_mr_diversity — disclosed in the registration §4)
  4. else                                           -> UNDER_RECRUITED
     (CI includes 0 with half-width > 0.14; factual report only)

INTEGRITY — R-side freeze pins. The two R-side inputs are the CLOSED Study-4
SSOTs; their sha256 digests at Study-5 freeze time are hard-coded below and
verified at run time. A digest mismatch aborts with exit 3: the R side is
"reused not rerun" and quiet substitution is a protocol violation.

EXCLUSIONS (registration §6): the Python calibration-pilot PUTs {a2, b4} are
excluded (the roster is the 28 confirmatory PUTs); vacant / non-adjudicated /
null-SMS cells are dropped through the SAME _is_excluded as every prior
confirmatory leg (imported from the frozen compute_dualblind_delta.py).

Inputs (registration §6 SSOT paths):
  R cross arm : data/results/sms_track2_v7.json        (frozen, reused)
  R same  arm : data/results/sms_track2_v7_same.json   (frozen, reused)
  L cross arm : data/results/sms_track2_v8_mrL.json        (Study-5, fresh)
  L same  arm : data/results/sms_track2_v8_mrL_same.json   (Study-5, fresh)
Output:
  data/results/mr_diversity_delta_v8.json  (verdict + licensed string)

Exit codes: 0 ok; 2 = an input SSOT is absent (no Study-5 L-side data exists
at freeze time); 3 = R-side freeze-pin digest mismatch.

Usage:
    PYTHONPATH=src python3 scripts/compute_mr_diversity_delta.py
    PYTHONPATH=src python3 scripts/compute_mr_diversity_delta.py \
        --l-cross data/results/sms_track2_v8_mrL.json \
        --l-same  data/results/sms_track2_v8_mrL_same.json \
        --out     data/results/mr_diversity_delta_v8.json
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

RESULTS = ROOT / "data" / "results"

# ---- registered constants (PREREGISTRATION_STUDY5_v1.md §3.4, §6) -----------
MASTER_SEED = 20260708          # registration master seed
B_BOOT = 10_000                 # bootstrap resamples
EQ_HALFWIDTH_BOUND = 0.14       # registered bounded-equivalence half-width gate
MIN_N_PUTS_PAIRED = 24          # registered recruitment gate (cannot be moved)
ALPHA = 0.05

# 28-PUT confirmatory roster (pilots {a2, b4} excluded), identical IDs to
# Studies 2-4 (class balance 7/6/7/8).
CONFIRMATORY_PUTS = (
    "a1", "a3", "a4", "a5", "a6", "a7", "a8",
    "b1", "b2", "b3", "b5", "b6", "b7",
    "c1", "c2", "c3", "c4", "c5", "c6", "c7",
    "d1", "d2", "d3", "d4", "d5", "d6", "d7", "d8",
)

R_CROSS = RESULTS / "sms_track2_v7.json"
R_SAME = RESULTS / "sms_track2_v7_same.json"
L_CROSS = RESULTS / "sms_track2_v8_mrL.json"
L_SAME = RESULTS / "sms_track2_v8_mrL_same.json"
OUT = RESULTS / "mr_diversity_delta_v8.json"

# R-side freeze pins (sha256 at Study-5 freeze, 2026-07-10). The R arm is
# "reused not rerun": these two files are CLOSED Study-4 SSOTs.
R_FREEZE_SHA256 = {
    "sms_track2_v7.json":
        "13c6e0f81b5a6c423e7e5b5dd3c6f669ff9eeda62e67b060e827978d8b22c792",
    "sms_track2_v7_same.json":
        "c7931a74785da22c1f8aca90604125924e2546988e5ad4d23efec12438a1b4af",
}


# --------------------------------------------------------------------------- #
# Shared exclusion/parsing machinery, IMPORTED from the frozen H2-2 scorer so
# no measurement can drift between the R and L legs (same pattern as
# compute_hlang_delta.py).
# --------------------------------------------------------------------------- #
def _load_dualblind_module():
    spec = importlib.util.spec_from_file_location(
        "compute_dualblind_delta", ROOT / "scripts" / "compute_dualblind_delta.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_DBD = _load_dualblind_module()
_is_excluded = _DBD._is_excluded
_parse_cell = _DBD._parse_cell


def _rel(path) -> str:
    try:
        return str(Path(path).resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def _check_freeze_pin(path: Path) -> None:
    """Abort (exit 3) if a reused R-side SSOT differs from its freeze digest."""
    want = R_FREEZE_SHA256.get(path.name)
    if want is None:
        return
    got = hashlib.sha256(path.read_bytes()).hexdigest()
    if got != want:
        print(f"ERROR: R-side freeze-pin mismatch for {_rel(path)}\n"
              f"  frozen sha256 : {want}\n"
              f"  found  sha256 : {got}\n"
              "The R arm is the CLOSED Study-4 SSOT, reused not rerun "
              "(registration §3.4). Quiet substitution is a protocol violation.",
              file=sys.stderr)
        raise SystemExit(3)


def load_sms(path: str | Path) -> dict:
    return json.loads(Path(path).read_text())


def per_put_battery_sms(sms: dict, roster=CONFIRMATORY_PUTS) -> dict:
    """{put: battery-level SMS = mean SMS over the PUT's adjudicated cells}.

    Restricted to the confirmatory roster so pilot / extra cells cannot leak
    into the estimand. Uses the SAME _is_excluded as every prior leg."""
    vals: dict[str, list] = {}
    for cell, v in sms.items():
        put, _mp = _parse_cell(cell)
        if put not in roster:
            continue
        if _is_excluded(v):
            continue
        vals.setdefault(put, []).append(float(v["sms"]))
    return {p: float(np.mean(xs)) for p, xs in vals.items()}


# --------------------------------------------------------------------------- #
# H2-4 — MR-side diversity (Family MR)
# --------------------------------------------------------------------------- #
def paired_diffs(r_arms: dict, l_arms: dict, roster=CONFIRMATORY_PUTS):
    """Per-PUT paired differences d_p = mean over available arms of
    (SMS_R - SMS_L). A PUT contributes iff at least one arm carries it on BOTH
    the R and L sides. Returns (puts, diffs, per_put_detail)."""
    puts, diffs, detail = [], [], {}
    for p in roster:
        per_arm = {}
        for arm in r_arms:
            r = r_arms[arm].get(p)
            l = l_arms[arm].get(p)
            if r is not None and l is not None:
                per_arm[arm] = {"sms_R": round(r, 4), "sms_L": round(l, 4),
                                "d": round(r - l, 4)}
        if per_arm:
            d_p = float(np.mean([a["d"] for a in per_arm.values()]))
            puts.append(p)
            diffs.append(d_p)
            detail[p] = {"d_p": round(d_p, 4), "arms": per_arm}
    return puts, np.asarray(diffs, dtype=float), detail


def boot_mean_distribution(diffs: np.ndarray, B: int = B_BOOT,
                           seed: int = MASTER_SEED) -> np.ndarray:
    """PUT-level block bootstrap of the mean paired difference (the same
    resample-the-PUT-list scheme as the H2-2 paired-role bootstrap)."""
    n = diffs.size
    if n == 0:
        return np.zeros(B)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, n, size=(B, n))
    return diffs[idx].mean(axis=1)


def verdict_mr(lower_one_sided: float, ci_lo: float, ci_hi: float,
               n_puts: int) -> tuple[str, str, float]:
    """Registered decision ladder (§3.4); evaluated top-down, first hit wins."""
    half_width = (ci_hi - ci_lo) / 2.0
    if n_puts < MIN_N_PUTS_PAIRED:
        return ("UNDER_RECRUITED",
                f"recruitment gate: only {n_puts} of the 28 confirmatory PUTs "
                f"yield a paired R/L unit (< registered gate "
                f"{MIN_N_PUTS_PAIRED}); achieved n and delta_MR reported "
                "factually; no threshold is moved",
                half_width)
    if lower_one_sided > 0.0:
        return ("CONFIRM",
                "algebra-derived MR batteries DOMINATE LLM-prompted batteries "
                "on the frozen mutant pools (delta_MR one-sided 95% lower bound "
                "> 0): the MR battery's algebraic derivation, not merely the "
                "presence of some MR battery, is the lever",
                half_width)
    if ci_hi < 0.0:
        return ("REVERSED",
                "LLM-prompted batteries dominate the registered algebra-derived "
                "batteries (two-sided 95% CI entirely below 0) — reported "
                "factually; counts against the algebra-derivation lever (§8)",
                half_width)
    if half_width <= EQ_HALFWIDTH_BOUND:
        return ("BOUNDED_EQUIVALENCE",
                "no MR-battery-source effect larger than the registered margin "
                "is detectable on the frozen pools (CI includes 0, half-width "
                "<= 0.14 on the SMS scale)",
                half_width)
    return ("UNDER_RECRUITED",
            "inconclusive: CI includes 0 with half-width > 0.14",
            half_width)


def analyze_mr(r_arms: dict, l_arms: dict, B: int = B_BOOT,
               seed: int = MASTER_SEED) -> dict:
    puts, diffs, detail = paired_diffs(r_arms, l_arms)
    point = float(diffs.mean()) if diffs.size else 0.0
    dist = boot_mean_distribution(diffs, B=B, seed=seed)
    lower = float(np.quantile(dist, 0.05))              # one-sided 95% lower
    ci_lo = float(np.quantile(dist, 0.025))             # two-sided 95%
    ci_hi = float(np.quantile(dist, 0.975))
    verdict, licensed, half_width = verdict_mr(lower, ci_lo, ci_hi, len(puts))
    per_arm_means = {
        arm: {"mean_sms_R": round(float(np.mean(
                  [detail[p]["arms"][arm]["sms_R"] for p in puts
                   if arm in detail[p]["arms"]])), 4),
              "mean_sms_L": round(float(np.mean(
                  [detail[p]["arms"][arm]["sms_L"] for p in puts
                   if arm in detail[p]["arms"]])), 4)}
        for arm in r_arms if any(arm in detail[p]["arms"] for p in puts)
    }
    return {
        "family": "MR — MR-side diversity (single test, confirmatory)",
        "statistic": "paired per-PUT battery-level SMS difference "
                     "delta_MR = SMS_R - SMS_L on the FROZEN Study-4 v7 mutant "
                     "pools; per-PUT unit = mean over available arms; point = "
                     "mean over the 28 confirmatory PUTs",
        "n_puts_paired": len(puts),
        "delta_mr_point": round(point, 4),
        "bootstrap_B": B,
        "bootstrap_seed": seed,
        "one_sided_95_lower_bound": round(lower, 4),
        "ci95_two_sided": [round(ci_lo, 4), round(ci_hi, 4)],
        "ci95_half_width": round(half_width, 4),
        "registered_eq_halfwidth_bound": EQ_HALFWIDTH_BOUND,
        "registered_recruitment_gate_n_puts": MIN_N_PUTS_PAIRED,
        "registered_test": "PUT-level paired block bootstrap of the mean "
                           "difference (B=10,000, seed 20260708); ladder: "
                           "n_puts<24 -> UNDER_RECRUITED (gate); one-sided "
                           "LB>0 -> CONFIRM; CI<0 -> REVERSED; CI incl. 0 & "
                           "hw<=0.14 -> BOUNDED_EQUIVALENCE; else "
                           "UNDER_RECRUITED",
        "verdict": verdict,
        "licensed_claim": licensed,
        "per_arm_battery_means": per_arm_means,
        "per_put": detail,
    }


# --------------------------------------------------------------------------- #
# Driver
# --------------------------------------------------------------------------- #
def run(r_cross=R_CROSS, r_same=R_SAME, l_cross=L_CROSS, l_same=L_SAME,
        out_path=OUT, B: int = B_BOOT, seed: int = MASTER_SEED) -> dict:
    for p in (Path(r_cross), Path(r_same)):
        _check_freeze_pin(p)
    r_arms = {"cross": per_put_battery_sms(load_sms(r_cross)),
              "same": per_put_battery_sms(load_sms(r_same))}
    l_arms = {"cross": per_put_battery_sms(load_sms(l_cross)),
              "same": per_put_battery_sms(load_sms(l_same))}
    mr = analyze_mr(r_arms, l_arms, B=B, seed=seed)
    report = {
        "artefact": "mr_diversity_delta_v8",
        "generated_by": "scripts/compute_mr_diversity_delta.py",
        "pre_registration": "docs/prereg_v2/PREREGISTRATION_STUDY5_v1.md "
                            "(§3.4 H2-4; §6 contract)",
        "integrity": "Pre-frozen before ANY Study-5 data generation "
                     "(2026-07-10); R-side inputs sha256-pinned to the CLOSED "
                     "Study-4 SSOTs (reused not rerun); any post-data "
                     "modification must be disclosed as a deviation (§7, §8).",
        "inputs": {
            "r_cross_arm_sms_frozen": _rel(r_cross),
            "r_same_arm_sms_frozen": _rel(r_same),
            "l_cross_arm_sms": _rel(l_cross),
            "l_same_arm_sms": _rel(l_same),
            "r_freeze_sha256": R_FREEZE_SHA256,
        },
        "master_seed": seed,
        "bootstrap_B": B,
        "mutant_pool_freeze": "the Study-4 v7 mutant pools are byte-identical "
                              "and never regenerated; the ONLY manipulated "
                              "variable is the MR-battery source (R vs L)",
        "H2_4_mr_side_diversity": mr,
    }
    if out_path is not None:
        Path(out_path).parent.mkdir(parents=True, exist_ok=True)
        Path(out_path).write_text(json.dumps(report, indent=2, ensure_ascii=False))
    return report


def _print_verdict(report: dict) -> None:
    h = report["H2_4_mr_side_diversity"]
    print("=== Study-5 H2-4 MR-side diversity verdict (Family MR) ===")
    print(f"[H2-4] delta_MR={h['delta_mr_point']:+.4f} "
          f"one-sided 95% lower={h['one_sided_95_lower_bound']:+.4f} "
          f"CI {h['ci95_two_sided']} half-width={h['ci95_half_width']:.4f} "
          f"(n_puts={h['n_puts_paired']})")
    print(f"    VERDICT: {h['verdict']} — {h['licensed_claim']}")


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--r-cross", default=str(R_CROSS),
                    help="FROZEN Study-4 cross-arm SMS SSOT (R battery; "
                         "sha256-pinned)")
    ap.add_argument("--r-same", default=str(R_SAME),
                    help="FROZEN Study-4 same-arm SMS SSOT (R battery; "
                         "sha256-pinned)")
    ap.add_argument("--l-cross", default=str(L_CROSS),
                    help="Study-5 L-battery SMS SSOT scored on the byte-"
                         "identical cross-arm pool")
    ap.add_argument("--l-same", default=str(L_SAME),
                    help="Study-5 L-battery SMS SSOT scored on the byte-"
                         "identical same-arm pool")
    ap.add_argument("--out", default=str(OUT),
                    help="output SSOT path ('-' = stdout only, no file write)")
    args = ap.parse_args()
    for p in (args.r_cross, args.r_same, args.l_cross, args.l_same):
        if not Path(p).exists():
            print(f"ERROR: input SSOT missing: {p}\n"
                  "This script runs on the ANALYSIS leg, AFTER the Study-5 "
                  "L-battery scoring of the frozen v7 pools. No Study-5 L-side "
                  "data exists at freeze time (PREREGISTRATION_STUDY5_v1.md "
                  "§0.1).", file=sys.stderr)
            return 2
    out_path = None if args.out == "-" else args.out
    report = run(args.r_cross, args.r_same, args.l_cross, args.l_same, out_path)
    _print_verdict(report)
    if out_path is not None:
        print(f"\nwrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
