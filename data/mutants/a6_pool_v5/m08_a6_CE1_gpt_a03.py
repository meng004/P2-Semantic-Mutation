from scipy.optimize import brentq


def program(x) -> float:
    x = float(x)

    def residual(r, target):
        return r**3 + r - target

    return float(brentq(residual, -5.0, 5.0, args=(4.0 * (x) - 1.0,), xtol=1e-12, rtol=8.9e-16))