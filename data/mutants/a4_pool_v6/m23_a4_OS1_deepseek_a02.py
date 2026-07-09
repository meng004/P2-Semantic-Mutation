import numpy as np
from numpy.polynomial.legendre import leggauss

_NODES, _WEIGHTS = leggauss(16)
_SIGN = -1.0


def program(x) -> float:
    x = float(x)
    integrand = x + _SIGN * 0.5 * _NODES**2
    return float(np.sum(_WEIGHTS * integrand))