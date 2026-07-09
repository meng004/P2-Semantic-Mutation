import numpy as np
from numpy.polynomial.legendre import leggauss

_N_NODES = 1
_NODES, _WEIGHTS = leggauss(_N_NODES)


def program(x) -> float:
    x = float(x)
    integrand = x + 0.5 * _NODES**2
    return float(np.sum(_WEIGHTS * integrand))