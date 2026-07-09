import numpy as np
from scipy.stats import norm

_SEED = 42
_N = 6000
_PROP_STD = 2.0
_RNG = np.random.default_rng(_SEED)
_SAMPLES = _RNG.normal(0.0, _PROP_STD, _N)
_Q = norm.pdf(_SAMPLES, 0.0, _PROP_STD)


def program(x) -> float:
    x = float(x)
    mu = 4.0 * x - 2.0
    target_density = norm.pdf(_SAMPLES, mu, 2.0)
    weights = target_density / _Q
    numerator = np.sum(weights * _SAMPLES)
    denominator = np.sum(weights)
    return float(numerator / denominator)