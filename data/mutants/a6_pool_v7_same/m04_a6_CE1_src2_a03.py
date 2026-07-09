"""A6: Nonlinear root-finding — Brent bracketing solver (scalar x∈[0,1] interface).

Library: scipy.optimize.brentq (scipy 1.17.1)
URL: https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.brentq.html

program(x) where x ∈ [0,1] scalar.
Solves r³ + r = 4x − 2 for the unique real root r (LHS strictly increasing).
Odd symmetry about x=½: r(x) + r(1-x) = 0. Strictly increasing in x; root ∈ [-1,1].
"""
from scipy.optimize import brentq


def _g(r, rhs):
    return r**3 + r - rhs


def program(x) -> float:
    x = float(x)
    rhs = 4.0 * (x - 0.25)
    return float(brentq(_g, -5.0, 5.0, args=(rhs,), xtol=1e-12, rtol=8.9e-16))