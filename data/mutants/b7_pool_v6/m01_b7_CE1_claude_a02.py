"""B7 mutant."""
import numpy as np
from scipy.stats import norm

_SEED = 42
_N = 6000
_PROP_STD = 2.0
_SAMPLES = np.random.default_rng(_SEED).normal(0.0, _PROP_STD, _N)
_Q = norm.pdf(_SAMPLES, 0.0, _PROP_STD)


def program(x) -> float:
    x = float(x)
    slope, offset = 4.0, 1.0
    mu = slope * x - offset
    w = norm.pdf(_SAMPLES, mu, 1.0) / _Q
    return float(np.sum(w * _SAMPLES) / np.sum(w))