import numpy as np
from numpy.polynomial.legendre import leggauss

_NODES, _WEIGHTS = leggauss(16)


def program(x) -> float:
    x = float(x)
    return float(x * np.sum(_WEIGHTS) - 0.5 * np.sum(_WEIGHTS * _NODES**2))