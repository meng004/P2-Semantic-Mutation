"""B1: Beta-Binomial conjugate update — Bayesian posterior inference.

Library: scipy.stats.beta (scipy 1.17.1)
URL: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.beta.html

program(x) where x = [n_trials, n_successes] (non-negative integers as floats).
Returns posterior mean = (alpha_post) / (alpha_post + beta_post).
Prior: Beta(alpha=1, beta=1) — uniform (Jeffreys alternative: Beta(0.5, 0.5)).
"""
import numpy as np
from scipy.stats import beta as beta_dist

_ALPHA_PRIOR = 1.0
_BETA_PRIOR = 1.0


def program(x: np.ndarray) -> float:
    """Bayesian conjugate update for Beta-Binomial model; return posterior mean."""
    x = np.asarray(x, dtype=float)
    n_trials, n_succ = float(x[0]), float(x[1])
    alpha_post = _ALPHA_PRIOR + n_succ
    beta_post = _BETA_PRIOR + n_trials - n_succ
    return beta_dist.mean(alpha_post, beta_post)  # = alpha_post / (alpha_post + beta_post)
