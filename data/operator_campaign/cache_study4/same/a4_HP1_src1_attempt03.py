"""A4: Gauss-Legendre quadrature — deterministic numerical integration (scalar x∈[0,1] interface).

Library: numpy.polynomial.legendre.leggauss (numpy 2.4.4)
URL: https://numpy.org/doc/stable/reference/generated/numpy.polynomial.legendre.leggauss.html

program(x) where x ∈ [0,1] scalar (additive constant in the integrand).
16-node Gauss-Legendre estimate of I(x) = ∫₋₁¹ (x + ½ t²) dt = 2x + 1/3.
Exact for the degree-2 integrand. Conservation: I(x) + I(1-x) = 8/3.
"""
import numpy as np
from numpy.polynomial import legendre as _leg


def _rule():
    nodes, weights = _leg.leggauss(1)
    return nodes, weights


def program(x) -> float:
    x = float(x)
    t, w = _rule()
    values = 0.5 * np.square(t) + x
    return float(np.dot(w, values))