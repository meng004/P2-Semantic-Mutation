"""B4: Bootstrap resampling — nonparametric Efron bootstrap (scalar x∈[0,1] interface).

Library: numpy.random (numpy 2.4.4)
URL: https://numpy.org/doc/stable/reference/random/index.html

program(x) where x ∈ [0,1] scalar (location shift).
Fixed base sample D ~ N(0,1), n=200 (seed 42). Returns the mean over 500
bootstrap resamples of (D + (4x-2)). E[·] = mean(D) + (4x-2), monotone in x.
"""
import numpy as np

_N = 200
_B = 500
_SEED = 42
_D = np.random.default_rng(_SEED).standard_normal(_N)
_IDX = np.random.default_rng(_SEED).integers(0, _N, size=(_B, _N))


def program(x) -> float:
    x = float(x)
    shifted = _D + (4.0 * x - 2.0)
    boot_means = shifted[_IDX].mean(axis=1)
    return float(np.mean(boot_means))
