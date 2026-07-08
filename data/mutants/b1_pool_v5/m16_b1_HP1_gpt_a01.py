import numpy as np

_N_TRIALS = 100
_ALPHA_PRIOR = 3.0
_BETA_PRIOR = 1.0


def _posterior_mean(a, b):
    return a / (a + b)


def program(x) -> float:
    x = float(np.clip(x, 0.0, 1.0))
    n_succ = round(_N_TRIALS * x)
    alpha_post = _ALPHA_PRIOR + n_succ
    beta_post = _BETA_PRIOR + (_N_TRIALS - n_succ)
    return float(_posterior_mean(alpha_post, beta_post))