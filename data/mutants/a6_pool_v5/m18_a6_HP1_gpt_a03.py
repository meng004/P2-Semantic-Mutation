from scipy.optimize import brentq


def program(x) -> float:
    x = float(x)
    rhs = 4.0 * x - 2.0
    g = lambda r: r**3 + r - rhs
    return float(brentq(g, -5.0, 5.0, xtol=1.0e-1, rtol=8.9e-16))