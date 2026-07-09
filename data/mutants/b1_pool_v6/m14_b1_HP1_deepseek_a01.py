"""B1 mutant."""
import numpy as np

_N_TRIALS = 100
_PRIOR = {"alpha": 3.0, "beta": 1.0}


def program(x) -> float:
    x = float(np.clip(x, 0.0, 1.0))
    n_succ = round(_N_TRIALS * x)
    alpha_post = _PRIOR["alpha"] + n_succ
    beta_post = _PRIOR["beta"] + (_N_TRIALS - n_succ)
    return float(alpha_post / (alpha_post + beta_post))