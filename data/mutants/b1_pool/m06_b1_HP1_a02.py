import numpy as np
from scipy.stats import beta as _beta_dist


_N_TRIALS = 100


def _prior_alpha():
    return 3.0


def _prior_beta():
    return 1.0


def program(x) -> float:
    x_val = float(np.clip(x, 0.0, 1.0))
    k = round(_N_TRIALS * x_val)
    a = _prior_alpha()
    b = _prior_beta()
    posterior_params = (a + k, b + (_N_TRIALS - k))
    numerator, denominator = posterior_params[0], posterior_params[0] + posterior_params[1]
    return float(numerator / denominator)