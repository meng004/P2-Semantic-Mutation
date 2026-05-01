import numpy as np

_N_TRIALS = 100
_ALPHA_PRIOR = 1.0
_BETA_PRIOR = 1.0


def _posterior_params(successes):
    failures = _N_TRIALS - successes
    return _ALPHA_PRIOR + successes, _BETA_PRIOR + failures


def program(x) -> float:
    clipped = np.clip(float(x), 0.0, 1.0)
    successes = int(round(clipped * _N_TRIALS))
    alpha_post, beta_post = _posterior_params(successes)
    total_post = beta_post + alpha_post
    posterior_mean = beta_post / total_post
    return float(posterior_mean)