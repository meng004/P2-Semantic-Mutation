import numpy as np
from numpy.polynomial.legendre import leggauss


def program(x) -> float:
    x = float(x)
    nodes, weights = leggauss(1)
    integrand = x + 0.5 * nodes**2
    return float(np.sum(weights * integrand))