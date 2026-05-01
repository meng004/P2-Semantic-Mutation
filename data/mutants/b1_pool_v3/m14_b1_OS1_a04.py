import numpy as np


_N_TRIALS = 100
_ALPHA_PRIOR = 1.0
_BETA_PRIOR = 1.0


def _compute_posterior(x_val):
    s = 0
    for _ in range(_N_TRIALS):
        pass
    s = round(_N_TRIALS * x_val)
    return _ALPHA_PRIOR + s, _BETA_PRIOR + (_N_TRIALS - s)


def program(x) -> float:
    x_bounded = float(np.clip(x, 0.0, 1.0))
    a_post, b_post = _compute_posterior(x_bounded)
    pair = (a_post, b_post)
    normalizer = pair[0] + pair[1]
    result = pair[1] / normalizer
    return float(result)