"""B7: Importance sampling mutant."""
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
    sigma = np.sqrt(4.0)
    w = norm.pdf(_SAMPLES, mu, sigma) / _Q
    return float(np.sum(w * _SAMPLES) / np.sum(w))