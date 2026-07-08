import numpy as np
from numpy.polynomial.legendre import leggauss

_NODES, _WEIGHTS = leggauss(16)


def program(x) -> float:
    x = float(x)
    quad = 1.0 * np.square(_NODES)
    return float(np.dot(_WEIGHTS, x + quad))