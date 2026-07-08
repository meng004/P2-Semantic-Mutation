from scipy.optimize import brentq


def _g(r, rhs):
    return r * r * r - r - rhs


def program(x) -> float:
    x = float(x)
    rhs = 4.0 * x - 2.0
    return float(brentq(_g, -5.0, 5.0, args=(rhs,), xtol=1e-12, rtol=8.9e-16))