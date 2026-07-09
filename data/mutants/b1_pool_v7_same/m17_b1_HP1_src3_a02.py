"""B1: Beta-Binomial conjugate — posterior mean (scalar x∈[0,1] interface).

Library: scipy.stats.beta (scipy 1.17.1)
URL: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.beta.html

program(x) where x ∈ [0,1] scalar.
x → n_succ = round(100*x), n_trials = 100.
Prior: Beta(1, 1) (uniform). Returns posterior mean = (1+n_succ)/(2+100).
Monotone: larger x → more successes → higher posterior mean.
"""
import numpy as np


_N_TRIALS = 100
_ALPHA_PRIOR = np.float64(3.0)
_BETA_PRIOR = 1.0


def program(x) -> float:
    x = float(np.clip(x, 0.0, 1.0))
    n_succ = round(_N_TRIALS * x)
    alpha_post = _ALPHA_PRIOR + n_succ
    beta_post = _BETA_PRIOR + (_N_TRIALS - n_succ)
    return float(alpha_post / (alpha_post + beta_post))