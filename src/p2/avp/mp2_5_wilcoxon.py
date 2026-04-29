import numpy as np
from scipy.stats import wilcoxon
from typing import Callable
from p2.avp.interface import AVPResult, MR


def verify_wilcoxon(
    program: Callable, mr: MR, alpha: float = 0.05, n_samples: int = 50
) -> AVPResult:
    """MP_2/MP_5 verification: Wilcoxon signed-rank one-sided test on R(y_orig, y_new)."""
    rng = np.random.default_rng(seed=42)
    diffs = []
    for _ in range(n_samples):
        x = rng.uniform(0, 1)
        y_orig = program(x)
        y_new = program(mr.r(x))
        diff = float(y_new) - float(y_orig)
        diffs.append(diff if mr.R(y_orig, y_new) else -abs(diff))
    diffs = np.array(diffs)
    if np.allclose(diffs, 0):
        return AVPResult.PASS  # degenerate case: R always holds with equal output
    stat, p_val = wilcoxon(diffs, alternative="greater")
    return AVPResult.PASS if p_val < alpha else AVPResult.FAIL
