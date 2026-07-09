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
    mu = 4.0 * x - 2.0
    target_std = 2.0
    w = norm.pdf(_SAMPLES, mu, target_std) / _Q
    return float(np.sum(w * _SAMPLES) / np.sum(w))