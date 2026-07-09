from scipy.optimize import brentq


def program(x) -> float:
    x = float(x)
    rhs = 4.0 * x - 2.0
    f = lambda r, q: r**3 + r - q
    return float(brentq(f, -5.0, 5.0, args=(rhs,), xtol=1e-1, rtol=8.9e-16))