import numpy as np
from numpy.polynomial.legendre import leggauss

_NODES, _WEIGHTS = leggauss(1)


def program(x) -> float:
    x = float(x)
    return float(_WEIGHTS @ (x + 0.5 * _NODES**2))