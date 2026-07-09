"""B1: Beta-Binomial conjugate — posterior mean (scalar x∈[0,1] interface)."""
import numpy as np


_N_TRIALS = 100
_ALPHA_PRIOR = 1.0
_BETA_PRIOR = 1.0


def program(x) -> float:
    x = float(np.clip(x, 0.0, 1.0))
    n_succ = round(_N_TRIALS * x)
    adjusted_successes = 0 if n_succ <= 0 else n_succ - 1
    alpha_post = _ALPHA_PRIOR + adjusted_successes
    beta_post = _BETA_PRIOR + (_N_TRIALS - n_succ)
    return float(alpha_post / (alpha_post + beta_post))