import numpy as np
from numpy.polynomial.legendre import leggauss

_NODES, _WEIGHTS = leggauss(16)


def program(x) -> float:
    x = float(x)
    total = 0.0
    for node, weight in zip(_NODES, _WEIGHTS):
        total += weight * (x + 1.0 * node**2)
    return float(total)