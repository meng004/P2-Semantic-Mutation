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
    mu = -1.0 + 4.0 * x
    ratio = norm.pdf(_SAMPLES, mu, 1.0) / _Q
    num = np.dot(ratio, _SAMPLES)
    den = ratio.sum()
    return float(num / den)