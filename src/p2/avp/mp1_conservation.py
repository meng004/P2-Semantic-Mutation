import numpy as np
from typing import Callable
from p2.avp.interface import AVPResult, MR


def verify_conservation(
    program: Callable, mr: MR, epsilon: float, n_samples: int = 30
) -> AVPResult:
    """MP_1 verification: tolerance equality |LHS - RHS| <= epsilon over samples."""
    rng = np.random.default_rng(seed=42)
    for _ in range(n_samples):
        x = rng.uniform(0, 1)
        y_orig = program(x)
        y_new = program(mr.r(x))
        if not mr.R(y_orig, y_new):
            return AVPResult.FAIL
    return AVPResult.PASS
