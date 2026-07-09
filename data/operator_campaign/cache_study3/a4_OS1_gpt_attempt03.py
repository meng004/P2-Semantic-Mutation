import numpy as np
from numpy.polynomial.legendre import leggauss

_NODES, _WEIGHTS = leggauss(16)


def program(x) -> float:
    x = float(x)
    integrand = np.subtract(x, 0.5 * np.power(_NODES, 2))
    return float(np.sum(_WEIGHTS * integrand))