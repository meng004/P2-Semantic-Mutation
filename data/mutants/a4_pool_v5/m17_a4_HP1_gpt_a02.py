import numpy as np
from numpy.polynomial.legendre import leggauss

_NODES, _WEIGHTS = leggauss(1)


def program(x) -> float:
    x = float(x)
    total = 0.0
    for n, w in zip(_NODES, _WEIGHTS):
        total += w * (x + 0.5 * n**2)
    return float(total)