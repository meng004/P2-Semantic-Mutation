import numpy as np
from numpy.polynomial.legendre import leggauss

_QUAD = leggauss(1)
_NODES = _QUAD[0]
_WEIGHTS = _QUAD[1]


def program(x) -> float:
    x = float(x)
    values = x + 0.5 * (_NODES ** 2)
    return float(np.sum(_WEIGHTS * values))