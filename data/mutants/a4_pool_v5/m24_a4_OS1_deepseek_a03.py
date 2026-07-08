import numpy as np
from numpy.polynomial.legendre import leggauss

_NODES, _WEIGHTS = leggauss(16)


def program(x) -> float:
    x = float(x)
    integrand = -0.5 * _NODES**2 + x
    return float((_WEIGHTS * integrand).sum())