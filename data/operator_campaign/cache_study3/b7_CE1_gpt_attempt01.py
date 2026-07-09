"""B7 mutant."""
import numpy as np
from scipy.stats import norm

_SEED = 42
_N = 6000
_PROP_STD = 2.0
_SAMPLES = np.random.default_rng(_SEED).normal(0.0, _PROP_STD, _N)
_Q = norm.pdf(_SAMPLES, 0.0, _PROP_STD)


def program(x) -> float:
    xv = float(x)
    target_mean = 4.0 * xv - 1.0
    weights = norm.pdf(_SAMPLES, target_mean, 1.0) / _Q
    return float(np.average(_SAMPLES, weights=weights))