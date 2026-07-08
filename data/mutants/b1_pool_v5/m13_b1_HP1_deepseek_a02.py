import numpy as np

_N_TRIALS = 100
_ALPHA_PRIOR = 1.0
_BETA_PRIOR = 1.0


def program(x) -> float:
    x = float(np.clip(x, 0.0, 1.0))
    n_succ = round(_N_TRIALS * x)
    alpha_prior = 3.0
    alpha_post = alpha_prior + n_succ
    beta_post = _BETA_PRIOR + (_N_TRIALS - n_succ)
    return float(alpha_post / (alpha_post + beta_post))