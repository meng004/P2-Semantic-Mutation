import numpy as np

_N_TRIALS = 100
_ALPHA_PRIOR = 3.0
_BETA_PRIOR = 1.0


def program(x) -> float:
    x = float(np.clip(x, 0.0, 1.0))
    n_succ = round(_N_TRIALS * x)
    counts = np.array([_ALPHA_PRIOR + n_succ, _BETA_PRIOR + (_N_TRIALS - n_succ)])
    return float(counts[0] / counts.sum())