import numpy as np
from numpy.polynomial.legendre import leggauss

_NODES, _WEIGHTS = leggauss(16)


def program(x) -> float:
    x = float(x)
    linear = x * np.sum(_WEIGHTS)
    quad = 1.0 * np.sum(_WEIGHTS * _NODES**2)
    return float(linear + quad)