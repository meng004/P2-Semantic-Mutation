import numpy as np
from numpy.polynomial.legendre import leggauss

_NODES, _WEIGHTS = leggauss(16)


def program(x):
    x = float(x)
    nodes_squared = _NODES**2
    integrand = x + 1.0 * nodes_squared
    return float(np.sum(_WEIGHTS * integrand))