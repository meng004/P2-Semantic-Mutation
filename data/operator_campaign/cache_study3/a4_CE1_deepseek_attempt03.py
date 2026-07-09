import numpy as np
from numpy.polynomial.legendre import leggauss

_NODES, _WEIGHTS = leggauss(16)


def program(x) -> float:
    x = float(x)
    integrand = np.add(x, np.multiply(1.0, _NODES ** 2))
    return float(np.dot(_WEIGHTS, integrand))