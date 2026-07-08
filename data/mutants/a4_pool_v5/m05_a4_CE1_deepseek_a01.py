import numpy as np
from numpy.polynomial.legendre import leggauss

_NODES, _WEIGHTS = leggauss(16)


def program(x) -> float:
    x = float(x)
    c = 1.0
    integrand = x + c * _NODES**2
    return float(np.sum(_WEIGHTS * integrand))