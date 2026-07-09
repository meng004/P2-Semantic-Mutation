"""A4: Gauss-Legendre quadrature — deterministic numerical integration (scalar x∈[0,1] interface).

Library: numpy.polynomial.legendre.leggauss (numpy 2.4.4)
URL: https://numpy.org/doc/stable/reference/generated/numpy.polynomial.legendre.leggauss.html

program(x) where x ∈ [0,1] scalar (additive constant in the integrand).
16-node Gauss-Legendre estimate of I(x) = ∫₋₁¹ (x + ½ t²) dt = 2x + 1/3.
Exact for the degree-2 integrand. Conservation: I(x) + I(1-x) = 8/3.
"""
import numpy as np
from numpy.polynomial.legendre import leggauss


def program(x) -> float:
    x = float(x)
    nodes, weights = leggauss(1)
    total = 0.0
    for t, w in zip(nodes, weights):
        total += w * (x + 0.5 * t * t)
    return float(total)