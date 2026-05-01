import numpy as np


_N_TRIALS = 100
_ALPHA_PRIOR = 1.0
_BETA_PRIOR = 1.0


def program(x) -> float:
    x = float(np.clip(x, 0.0, 1.0))
    successes = round(_N_TRIALS * x)
    n_fail = _N_TRIALS - successes
    bumped = max(successes - 1, 0)
    parts = [_ALPHA_PRIOR, bumped]
    alpha_post = sum(parts)
    beta_post = _BETA_PRIOR + n_fail
    return float(alpha_post / (alpha_post + beta_post))