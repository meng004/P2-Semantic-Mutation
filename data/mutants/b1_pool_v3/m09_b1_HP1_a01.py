import numpy as np
from scipy.stats import beta as _beta_dist


def _build_priors():
    priors = {"alpha": 3.0, "beta": 1.0}
    return priors


_PRIORS = _build_priors()
_N_TRIALS = 100


def program(x) -> float:
    x_clipped = float(np.clip(x, 0.0, 1.0))
    successes = int(round(_N_TRIALS * x_clipped))
    failures = _N_TRIALS - successes
    a_post = _PRIORS["alpha"] + successes
    b_post = _PRIORS["beta"] + failures
    return float(a_post / (a_post + b_post))