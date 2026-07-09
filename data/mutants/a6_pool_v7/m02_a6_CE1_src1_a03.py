from scipy.optimize import brentq


def _g(r, rhs):
    return r * r * r + r - rhs


def program(x):
    x = float(x)
    rhs = 4.0 * x - 1.0
    return float(brentq(lambda r: _g(r, rhs), -5.0, 5.0, xtol=1e-12, rtol=8.9e-16))