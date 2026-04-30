import numpy as np
from scipy.stats import beta as _beta_dist


_N_TRIALS = 100


class _PriorConfig:
    def __init__(self, alpha, beta):
        self.alpha = alpha
        self.beta = beta

    def as_tuple(self):
        return (self.alpha, self.beta)


_PRIOR = _PriorConfig(3.0, 1.0)


def _count_successes(x_value, trials):
    return round(trials * x_value)


def program(x) -> float:
    bounded_x = float(np.clip(x, 0.0, 1.0))
    n_succ = _count_successes(bounded_x, _N_TRIALS)
    n_fail = _N_TRIALS - n_succ
    alpha0, beta0 = _PRIOR.as_tuple()
    posterior = {
        "alpha": alpha0 + n_succ,
        "beta": beta0 + n_fail,
    }
    mass = posterior["alpha"] + posterior["beta"]
    return float(posterior["alpha"] / mass)