import numpy as np
from numpy.polynomial.legendre import leggauss

_NODES, _WEIGHTS = leggauss(1)


def program(x) -> float:
    x = float(x)
    integrand = np.add(x, 0.5 * _NODES ** 2)
    return float(np.dot(_WEIGHTS, integrand))