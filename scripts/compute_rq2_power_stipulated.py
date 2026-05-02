"""Stipulated-alternative power simulation for RQ2 H2 (R1 W1 round-2).

Complementary to scripts/compute_rq2_power.py (which uses parametric
bootstrap from the *observed* empirical distributions). R1 W1 noted
that the plug-in approach answers "with what power could we detect
the *observed* δ = 0.439", but does not answer "if the truth is
δ = 0.474 (the H2 large-effect threshold), what is our power".

This script implements the stipulated-alternative simulation:
1. Take the observed cross pool C = {SMS values for cross MP slices, n=48}
   as fixed.
2. Search numerically for a shift constant Δ such that the shifted
   aligned pool A' = {x + Δ : x in observed aligned pool} has Cliff's δ
   against C exactly equal to the H2 threshold 0.474.
3. Resample (n_a=12, n_c=48) from (A', C) NSIM times; for each draw
   compute Cliff's δ and bootstrap-CI lower bound; tally rejection
   rate against H2 (δ point ≥ 0.474; CI lower bound > 0).
4. Report stipulated-alternative power at H2.

This answers R1 W1 directly:
  "Given that the *truth* is δ = 0.474 (H2 large-effect boundary), how
   often would n=(12,48) bootstrapping produce a δ point estimate
   meeting the H2 criterion?"

Configurable via env vars:
  SMS_VERSION         (default v4)
  P2_PRIMARY_VERSION  (default v3b — must match the paper)
  RQ2_POWER_NSIM      (default 5000)
  RQ2_POWER_SEED      (default 42)
  H2_TARGET_DELTA     (default 0.474, Romano 2006 large-effect)
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "src"))

from p2.config.primary import PRIMARY_CELLS as PRIMARY  # type: ignore[import-not-found]  # noqa: E402
from p2.stats.cliffs_delta import cliffs_delta  # type: ignore[import-not-found]  # noqa: E402

VERSION = os.environ.get("SMS_VERSION", "v4")
NSIM = int(os.environ.get("RQ2_POWER_NSIM", "5000"))
SEED = int(os.environ.get("RQ2_POWER_SEED", "42"))
H2_TARGET = float(os.environ.get("H2_TARGET_DELTA", "0.474"))

SMS_FILE = f"sms_track2_{VERSION}.json"
OUT_FILE = f"rq2_power_stipulated_{VERSION}.json"
print(f"compute_rq2_power_stipulated: SMS_VERSION={VERSION} nsim={NSIM} "
      f"seed={SEED} target_delta={H2_TARGET}")

data = json.loads((ROOT / "data/results" / SMS_FILE).read_text())

aligned, cross = [], []
for cell, v in data.items():
    put_id = cell.split("_")[0].lower()
    mp_k = int(cell.split("MP")[1])
    target = aligned if mp_k == PRIMARY[put_id] else cross
    target.append(v["sms"])

aligned_arr = np.asarray(aligned, dtype=float)
cross_arr = np.asarray(cross, dtype=float)
print(f"  observed n_aligned={len(aligned_arr)} n_cross={len(cross_arr)}")
observed_delta = cliffs_delta(aligned_arr.tolist(), cross_arr.tolist())
print(f"  observed Cliff's delta = {observed_delta:.4f}")


def calibrate_mixture_weight(
    aligned: np.ndarray,
    cross: np.ndarray,
    target: float,
    rng: np.random.Generator,
    nsim_per_w: int = 1000,
    n_a: int | None = None,
    n_c: int | None = None,
) -> tuple[float, float]:
    """Calibrate a mixture weight w ∈ [0, 1] such that aligned drawn as

        with prob w:    sample from (aligned + ε_pos)
        with prob 1-w:  sample from observed aligned

    has Cliff's δ ≈ target against the (fixed) observed cross pool.

    SMS distributions have heavy ties at zero (45/60 cells = 0); raw
    shifting is discontinuous (any ε > 0 jumps δ from 0.314 to 0.74).
    The mixture approach gives smooth control: w = 0 reproduces
    observed (δ = 0.439); w = 1 produces strongly-shifted pool
    (δ ≈ 0.736); intermediate w produces intermediate δ.

    Returns (w_calibrated, realized_delta_at_w).
    """
    n_a = n_a or len(aligned)
    n_c = n_c or len(cross)
    aligned_shifted = aligned + 0.001  # any positive ε creates the jump

    def realized_at(w: float) -> float:
        sims = np.empty(nsim_per_w)
        for i in range(nsim_per_w):
            mask = rng.random(n_a) < w
            a_b = np.where(
                mask,
                rng.choice(aligned_shifted, size=n_a, replace=True),
                rng.choice(aligned, size=n_a, replace=True),
            )
            c_b = rng.choice(cross, size=n_c, replace=True)
            sims[i] = cliffs_delta(a_b.tolist(), c_b.tolist())
        return float(np.mean(sims))

    # Bisection on w in [0, 1]
    lo, hi = 0.0, 1.0
    mid = 0.5 * (lo + hi)
    d_mid = realized_at(mid)
    for _ in range(15):
        mid = 0.5 * (lo + hi)
        d_mid = realized_at(mid)
        if abs(d_mid - target) < 0.005:
            return mid, d_mid
        if d_mid < target:
            lo = mid
        else:
            hi = mid
    return mid, d_mid


print(f"  calibrating mixture weight w to achieve Cliff's δ = {H2_TARGET} ...")
calib_rng = np.random.default_rng(SEED + 1)
w_calibrated, realized = calibrate_mixture_weight(
    aligned_arr, cross_arr, H2_TARGET, calib_rng, nsim_per_w=1000
)
print(f"  mixture weight w = {w_calibrated:.4f} → realized E[δ] = {realized:.4f}")


def bootstrap_ci_lower(rng, a, c, n_boot=200, alpha=0.05):
    """Lower bound of (1-alpha) percentile bootstrap CI of Cliff's δ."""
    sims = np.empty(n_boot)
    n_a, n_c = len(a), len(c)
    for i in range(n_boot):
        a_b = rng.choice(a, size=n_a, replace=True)
        c_b = rng.choice(c, size=n_c, replace=True)
        sims[i] = cliffs_delta(a_b.tolist(), c_b.tolist())
    return float(np.quantile(sims, alpha / 2))


print(f"  simulating power at n=({len(aligned_arr)},{len(cross_arr)}) "
      f"under stipulated δ = {H2_TARGET} ...")
rng = np.random.default_rng(SEED)
n_a_obs, n_c_obs = len(aligned_arr), len(cross_arr)
aligned_shifted_pool = aligned_arr + 0.001  # mixture component

n_meet_point = 0
n_meet_ci_zero = 0
delta_hats = np.empty(NSIM)
for i in range(NSIM):
    # Each draw: aligned[k] = mixture(observed, observed+0.001) with prob w
    mask = rng.random(n_a_obs) < w_calibrated
    a_b = np.where(
        mask,
        rng.choice(aligned_shifted_pool, size=n_a_obs, replace=True),
        rng.choice(aligned_arr,          size=n_a_obs, replace=True),
    )
    c_b = rng.choice(cross_arr, size=n_c_obs, replace=True)
    d_hat = cliffs_delta(a_b.tolist(), c_b.tolist())
    delta_hats[i] = d_hat
    if d_hat >= H2_TARGET:
        n_meet_point += 1
    # CI-lower-bound power: nested bootstrap (slow; subsample 1/5)
    if i % 5 == 0:
        ci_lo = bootstrap_ci_lower(
            np.random.default_rng(SEED + 10000 + i), a_b, c_b, n_boot=100
        )
        if ci_lo > 0:
            n_meet_ci_zero += 1

ci_zero_rate = n_meet_ci_zero / (NSIM // 5)
point_rate = n_meet_point / NSIM
print(f"  power(point-estimate δ_hat >= {H2_TARGET}) = {point_rate:.3f}")
print(f"  power(95% CI lower > 0)                 = {ci_zero_rate:.3f}")

report = {
    "method": "stipulated-alternative parametric bootstrap (R1 W1 round-2)",
    "n_simulations": NSIM,
    "seed": SEED,
    "version": VERSION,
    "observed": {
        "n_aligned": int(n_a_obs),
        "n_cross": int(n_c_obs),
        "cliffs_delta_observed": float(observed_delta),
    },
    "stipulated_truth": {
        "target_delta": H2_TARGET,
        "mixture_weight": float(w_calibrated),
        "realized_E_delta_at_w": float(realized),
        "rationale": (
            "SMS distributions have heavy ties at zero (45/60 cells = 0); "
            "raw shifting Cliff's δ is discontinuous (any ε > 0 jumps δ "
            "from 0.314 to 0.74). We instead use a mixture-weight "
            "construction: with probability w we draw from (observed_aligned + "
            "0.001), and with probability 1-w from observed_aligned. "
            "This gives smooth control over realized δ. Calibrating w "
            f"by bisection yields E[δ] = {realized:.4f} ≈ {H2_TARGET}, "
            "stipulating the alternative as the H2 boundary. This answers "
            "R1 W1: 'if the truth is the H2 threshold, how often would "
            "our n=(12,48) design produce a δ_hat meeting the H2 criterion?'"
        ),
    },
    "stipulated_alternative_power": {
        "power_point_estimate_meets_H2": float(point_rate),
        "power_CI_lower_above_zero":      float(ci_zero_rate),
        "delta_hat_distribution_summary": {
            "mean": float(np.mean(delta_hats)),
            "std":  float(np.std(delta_hats)),
            "p10":  float(np.quantile(delta_hats, 0.10)),
            "p50":  float(np.quantile(delta_hats, 0.50)),
            "p90":  float(np.quantile(delta_hats, 0.90)),
        },
    },
    "interpretation": (
        "Under stipulated truth δ = 0.474 (H2 large-effect threshold), "
        "the probability that a fresh n=(12,48) sample produces δ_hat >= "
        f"{H2_TARGET} is {point_rate:.3f}. This is the directly relevant "
        "power for the H2 verdict: even if the underlying distribution "
        "actually attained the large-effect boundary, our sample size "
        "still produces δ_hat below the threshold a non-trivial fraction "
        "of the time. This complements (but does not replace) the plug-in "
        "power 0.42 in compute_rq2_power.py: the plug-in number answers "
        "'with what power could we detect the observed δ = 0.439', while "
        "this stipulated number answers 'if the truth is at H2 boundary, "
        "what is our chance to confirm it'. Both are sub-0.80 at n=(12,48), "
        "consistent with §5.7.3's existing finding that the design is "
        "underpowered for distinguishing medium from large effects."
    ),
}

out = ROOT / "data/results" / OUT_FILE
out.write_text(json.dumps(report, indent=2, ensure_ascii=False))
print(f"  -> {out}")
