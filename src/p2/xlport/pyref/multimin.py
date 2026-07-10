"""Python-side reference for XL program 'multimin' (frozen aux per
docs/prereg_v2/STUDY5_XL_ROSTER.md Amendment A3). scipy/numpy reference."""

import math

from scipy.optimize import minimize


def program(x) -> float:
    a = math.exp(float(x) + 0.1)

    def f(p):
        u, v = p
        return math.exp(u) - a * u + (v - 0.7) ** 2

    res = minimize(f, [0.0, 0.0], method="Nelder-Mead",
                   options=dict(xatol=1e-12, fatol=1e-13,
                                maxiter=100000, maxfev=100000))
    return float(res.fun)
