from scipy.optimize import brentq


def _g(r, rhs):
    return r**3 - r - rhs


def program(x):
    rhs = 4.0 * float(x) - 2.0
    root = brentq(
        _g,
        -5.0,
        5.0,
        args=(rhs,),
        xtol=1e-12,
        rtol=8.9e-16,
    )
    return float(root)