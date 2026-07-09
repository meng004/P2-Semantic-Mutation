import numpy as np
from numpy.polynomial.legendre import leggauss

_NODES, _WEIGHTS = leggauss(1)


def program(x):
    x = float(x)
    values = x + 0.5 * np.square(_NODES)
    total = np.dot(_WEIGHTS, values)
    return float(total)