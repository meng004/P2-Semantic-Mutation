from scipy.optimize import brentq


def _target(x):
    return 4.0 * x - 1.0


def _g(r, rhs):
    return r**3 + r - rhs


def program(x) -> float:
    x = float(x)
    rhs = _target(x)
    return float(brentq(_g, -5.0, 5.0, args=(rhs,), xtol=1e-12, rtol=8.9e-16))