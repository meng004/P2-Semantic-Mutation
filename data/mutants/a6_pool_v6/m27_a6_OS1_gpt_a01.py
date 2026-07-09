from functools import partial
from scipy.optimize import brentq


def _g(r, rhs):
    return r**3 - r - rhs


def program(x) -> float:
    x = float(x)
    rhs = 4.0 * x - 2.0
    f = partial(_g, rhs=rhs)
    return float(brentq(f, -5.0, 5.0, xtol=1e-12, rtol=8.9e-16))