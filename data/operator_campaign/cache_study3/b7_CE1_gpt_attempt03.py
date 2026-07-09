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

    def target_mu(t):
        return 4.0 * t - 1.0

    w = norm.pdf(_SAMPLES, target_mu(x), 1.0) / _Q
    return float((w * _SAMPLES).sum() / w.sum())