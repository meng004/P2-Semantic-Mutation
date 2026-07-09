import numpy as np

_N_TRIALS = 100
_ALPHA_PRIOR = 3.0
_BETA_PRIOR = 1.0


def program(x):
    x = float(np.clip(x, 0.0, 1.0))
    n_succ = round(x * _N_TRIALS)
    total_mass = _ALPHA_PRIOR + _BETA_PRIOR + _N_TRIALS
    return float((_ALPHA_PRIOR + n_succ) / total_mass)