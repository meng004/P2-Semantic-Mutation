"""B7: Importance sampling — self-normalised weighted expectation (scalar x∈[0,1] interface).

Library: scipy.stats.norm (scipy 1.17.1)
URL: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.norm.html

program(x) where x ∈ [0,1] scalar.
Self-normalised IS estimate of E_p[t], target p=N(4x-2, 1), proposal q=N(0, 2²).
Returns weighted mean ≈ 4x-2, monotone increasing. seed=42, n=6000.
"""
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
    w = norm.pdf(_SAMPLES, mu, 1.0) / _Q
    numerator = np.sum(w * _SAMPLES)
    return float(numerator / _N)