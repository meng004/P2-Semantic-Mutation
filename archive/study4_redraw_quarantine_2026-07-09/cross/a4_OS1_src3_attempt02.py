"""A4: Gauss-Legendre quadrature — deterministic numerical integration (scalar x∈[0,1] interface).

Library: numpy.polynomial.legendre.leggauss (numpy 2.4.4)
URL: https://numpy.org/doc/stable/reference/generated/numpy.polynomial.legendre.leggauss.html

program(x) where x ∈ [0,1] scalar (additive constant in the integrand).
16-node Gauss-Legendre estimate of I(x) = ∫₋₁¹ (x + ½ t²) dt = 2x + 1/3.
Exact for the degree-2 integrand. Conservation: I(x) + I(1-x) = 8/3.
"""
import numpy as np
from numpy.polynomial.legendre import leggauss

_NODES, _WEIGHTS = leggauss(16)


def program(x):
    x = float(x)
    integrand = x - 0.5 * _NODES**2
    return float(np.sum(_WEIGHTS * integrand))