import numpy as np
from numpy.polynomial.legendre import leggauss

_N = 1
_NODES, _WEIGHTS = leggauss(_N)


def program(x) -> float:
    x = float(x)
    integrand = x + 0.5 * _NODES**2
    return float(np.dot(_WEIGHTS, integrand))