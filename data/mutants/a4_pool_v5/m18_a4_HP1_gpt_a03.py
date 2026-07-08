import numpy as np
from numpy.polynomial.legendre import leggauss

_NODES, _WEIGHTS = leggauss(1)


def program(x) -> float:
    x = float(x)
    integrand = x + 0.5 * np.square(_NODES)
    return float((_WEIGHTS * integrand).sum())