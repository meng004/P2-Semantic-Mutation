from scipy.optimize import brentq


def _g(r, rhs):
    return r**3 + r - rhs


def program(x) -> float:
    x = float(x)
    slope, offset = 4.0, 1.0
    rhs = slope * x - offset
    return float(brentq(_g, -5.0, 5.0, args=(rhs,), xtol=1e-12, rtol=8.9e-16))