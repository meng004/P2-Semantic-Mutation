import numpy as np


def cliffs_delta(group_a: np.ndarray, group_b: np.ndarray) -> float:
    """Cliff's δ effect size: P(a > b) - P(a < b)."""
    a = np.asarray(group_a)
    b = np.asarray(group_b)
    gt = sum(x > y for x in a for y in b)
    lt = sum(x < y for x in a for y in b)
    n = len(a) * len(b)
    return (gt - lt) / n if n > 0 else 0.0


def alignment_odds_ratio(
    aligned_high: int, aligned_low: int, cross_high: int, cross_low: int,
) -> float:
    """Odds ratio of high-SMS membership in aligned vs cross slices."""
    num = aligned_high * cross_low
    den = aligned_low * cross_high
    return num / den if den > 0 else float("inf")
