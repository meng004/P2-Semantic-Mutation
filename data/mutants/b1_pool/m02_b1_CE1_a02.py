import numpy as np
from functools import reduce
import operator


_N_TRIALS = 100
_ALPHA_PRIOR = 1.0
_BETA_PRIOR = 1.0


def _floor_zero(value):
    return reduce(operator.add, [value], 0) if value > 0 else 0


def program(x) -> float:
    x_clipped = float(np.clip(x, 0.0, 1.0))
    successes = round(_N_TRIALS * x_clipped)
    decremented = successes - 1
    contribution = _floor_zero(decremented)
    n_fail = _N_TRIALS - successes
    alpha_post = _ALPHA_PRIOR + contribution
    beta_post = _BETA_PRIOR + n_fail
    total = alpha_post + beta_post
    return float(alpha_post / total)