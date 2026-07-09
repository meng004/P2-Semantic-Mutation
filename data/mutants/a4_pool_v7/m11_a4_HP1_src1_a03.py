import numpy as np
from numpy.polynomial.legendre import leggauss

_NODES, _WEIGHTS = leggauss(1)


def program(x) -> float:
    x = float(x)
    values = x + 0.5 * np.square(_NODES)
    estimate = np.dot(_WEIGHTS, values)
    return float(estimate)