from scipy.optimize import brentq

SLOPE = 4.0
OFFSET = 2.0


def _residual(r, rhs):
    return r**3 - r - rhs


def program(x) -> float:
    x = float(x)
    rhs = SLOPE * x - OFFSET
    return float(brentq(_residual, -5.0, 5.0, args=(rhs,), xtol=1e-12, rtol=8.9e-16))