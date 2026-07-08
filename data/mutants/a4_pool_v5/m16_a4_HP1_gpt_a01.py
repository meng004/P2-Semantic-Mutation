import numpy as np
from numpy.polynomial.legendre import leggauss

nodes, weights = leggauss(1)


def program(x) -> float:
    x = float(x)
    return float(np.sum(weights * (x + 0.5 * nodes ** 2)))