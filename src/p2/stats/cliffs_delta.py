"""Cliff's delta effect size + bootstrap confidence interval.

delta in [-1, +1]: +1 => group A stochastically dominates group B; 0 =>
identical distributions; |delta| >= 0.474 is the "large effect" threshold
per Romano et al. (2006).

Used by RQ2 H2 evidence: aligned-slice vs cross-slice SMS comparison.
"""
from typing import Sequence, Tuple

import numpy as np


def cliffs_delta(group_a: Sequence[float], group_b: Sequence[float]) -> float:
    """Compute Cliff's delta = (#{a > b} - #{a < b}) / (n_a * n_b).

    Pair-comparison effect size over all (a_i, b_j) pairs. Returns 0.0 if
    either group is empty.
    """
    a = np.asarray(group_a, dtype=float)
    b = np.asarray(group_b, dtype=float)
    if a.size == 0 or b.size == 0:
        return 0.0
    diff = a[:, None] - b[None, :]
    n_gt = int(np.sum(diff > 0))
    n_lt = int(np.sum(diff < 0))
    return (n_gt - n_lt) / (a.size * b.size)


def bootstrap_delta_ci(
    group_a: Sequence[float],
    group_b: Sequence[float],
    n_boot: int = 1000,
    alpha: float = 0.05,
    seed: int = 42,
) -> Tuple[float, float]:
    """Return the (1 - alpha) percentile bootstrap CI for Cliff's delta.

    Resamples both groups with replacement n_boot times using a seeded
    numpy Generator. Returns (lo, hi) such that lo = quantile(alpha/2)
    and hi = quantile(1 - alpha/2). Returns (0.0, 0.0) if either group
    is empty.
    """
    rng = np.random.default_rng(seed)
    a = np.asarray(group_a, dtype=float)
    b = np.asarray(group_b, dtype=float)
    if a.size == 0 or b.size == 0:
        return 0.0, 0.0
    deltas = np.empty(n_boot)
    for i in range(n_boot):
        a_b = rng.choice(a, size=a.size, replace=True)
        b_b = rng.choice(b, size=b.size, replace=True)
        deltas[i] = cliffs_delta(a_b, b_b)
    lo = float(np.quantile(deltas, alpha / 2))
    hi = float(np.quantile(deltas, 1 - alpha / 2))
    return lo, hi


def odds_ratio(group_a: Sequence[float], group_b: Sequence[float]) -> float:
    """Return median(A) / median(B) as an "odds-ratio of the median" proxy.

    Returns +inf when median(B) = 0 and median(A) > 0; returns 0.0 when
    both medians are 0 or either group is empty.
    """
    a = np.asarray(group_a, dtype=float)
    b = np.asarray(group_b, dtype=float)
    if a.size == 0 or b.size == 0:
        return 0.0
    med_b = float(np.median(b))
    if med_b == 0.0:
        return float("inf") if float(np.median(a)) > 0 else 0.0
    return float(np.median(a)) / med_b
