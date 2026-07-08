from scipy.optimize import brentq


def _g(r, rhs):
    return r**3 + r - rhs


def program(x) -> float:
    x = float(x)
    rhs = 4.0 * x - 2.0
    return float(brentq(_g, -5.0, 5.0, args=(rhs,), xtol=0.1, rtol=8.9e-16))