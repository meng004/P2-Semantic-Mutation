import numpy as np
from numpy.polynomial.legendre import leggauss

_NODES, _WEIGHTS = leggauss(16)


def program(x) -> float:
    x = float(x)
    quad = 0.5 * _NODES ** 2
    integrand = x - quad
    return float(np.sum(_WEIGHTS * integrand))