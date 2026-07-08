import numpy as np
from numpy.polynomial.legendre import leggauss

_NODES, _WEIGHTS = leggauss(16)
_COEFF = -0.5


def program(x) -> float:
    x = float(x)
    integrand = x + _COEFF * _NODES**2
    return float(np.sum(_WEIGHTS * integrand))