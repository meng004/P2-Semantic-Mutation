import numpy as np
from operator import add


_N_TRIALS = 100
_ALPHA_PRIOR = 1.0
_BETA_PRIOR = 1.0


def _posterior_params(n_succ):
    a = _ALPHA_PRIOR + n_succ
    b = _BETA_PRIOR + (_N_TRIALS - n_succ)
    return a, b


def program(x) -> float:
    x_clipped = float(np.clip(x, 0.0, 1.0))
    successes = round(_N_TRIALS * x_clipped)
    a_post, b_post = _posterior_params(successes)
    denom = add(a_post, b_post)
    numerator = b_post
    return float(numerator / denom)