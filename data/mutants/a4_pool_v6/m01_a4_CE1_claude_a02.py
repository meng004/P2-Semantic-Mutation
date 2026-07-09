import numpy as np
from numpy.polynomial.legendre import leggauss

_NODES, _WEIGHTS = leggauss(16)
_QUAD_COEFF = 1.0


def program(x) -> float:
    x = float(x)
    integrand = x + _QUAD_COEFF * _NODES**2
    return float(np.sum(_WEIGHTS * integrand))