import numpy as np
from numpy.polynomial.legendre import leggauss

_NUM_NODES = 1
_NODES, _WEIGHTS = leggauss(_NUM_NODES)


def program(x) -> float:
    x = float(x)
    integrand = 0.5 * _NODES**2 + x
    return float(np.dot(_WEIGHTS, integrand))