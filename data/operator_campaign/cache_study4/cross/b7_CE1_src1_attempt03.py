import numpy as np
from scipy.stats import norm

_SEED = 42
_N = 6000
_PROP_STD = 2.0
_SAMPLES = np.random.default_rng(_SEED).normal(0.0, _PROP_STD, _N)
_Q = norm.pdf(_SAMPLES, 0.0, _PROP_STD)


def _importance_weights(mu):
    return norm.pdf(_SAMPLES, mu, 1.0) / _Q


def program(x) -> float:
    x = float(x)
    mu = 4.0 * x - 1.0
    w = _importance_weights(mu)
    numerator = np.sum(w * _SAMPLES)
    denominator = np.sum(w)
    return float(numerator / denominator)