"""B1 mutant."""
import numpy as np

_N_TRIALS = 100


def program(x) -> float:
    alpha_prior, beta_prior = 3.0, 1.0
    x = float(np.clip(x, 0.0, 1.0))
    n_succ = round(_N_TRIALS * x)
    alpha_post = alpha_prior + n_succ
    beta_post = beta_prior + (_N_TRIALS - n_succ)
    return float(alpha_post / (alpha_post + beta_post))