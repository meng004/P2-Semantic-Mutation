import numpy as np

_N_TRIALS = 100
_ALPHA_PRIOR = 1.0
_BETA_PRIOR = 1.0


def program(x) -> float:
    x = float(np.clip(x, 0.0, 1.0))
    n_succ = round(_N_TRIALS * x)
    a = _ALPHA_PRIOR + n_succ
    b = _BETA_PRIOR + (_N_TRIALS - n_succ)
    a, b = b, a
    return float(a / (a + b))