import numpy as np
from numpy.polynomial.legendre import leggauss

_NODES, _WEIGHTS = leggauss(16)
_NSQ = _NODES ** 2


def program(x) -> float:
    x = float(x)
    integrand = x - 0.5 * _NSQ
    return float(np.sum(_WEIGHTS * integrand))