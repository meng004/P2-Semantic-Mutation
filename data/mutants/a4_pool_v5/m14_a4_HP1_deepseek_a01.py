import numpy as np
from numpy.polynomial.legendre import leggauss

_NODES, _WEIGHTS = leggauss(1)


def program(x) -> float:
    x = float(x)
    quad = _NODES * _NODES
    integrand = x + 0.5 * quad
    return float(np.sum(_WEIGHTS * integrand))