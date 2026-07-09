from scipy.optimize import brentq


def _target(x):
    return 4.0 * x - 2.0


def _g(r, rhs):
    return r**3 + r - rhs


def program(x) -> float:
    x = float(x)
    return float(brentq(_g, -5.0, 5.0, args=(_target(x),), xtol=1e-1, rtol=8.9e-16))