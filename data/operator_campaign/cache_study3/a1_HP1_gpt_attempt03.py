"""A1: Lorenz ODE mutant."""
import math
import numpy as np
from scipy.integrate import solve_ivp

_SIGMA = 10.0
_RHO = 28.0
_BETA = 8.0 / 3.0


def _lorenz(t, y, sigma, rho, beta):
    x, yy, z = y[0], y[1], y[2]
    return [sigma * (yy - x), x * (rho - z) - yy, x * yy - beta * z]


def program(x) -> float:
    x = float(x)
    ic = [20*x - 10, 20*x - 10, 30*x + 5]
    sol = solve_ivp(
        _lorenz, (0.0, 1.0), np.asarray(ic, dtype=float),
        args=(_SIGMA, _RHO, _BETA),
        t_eval=[1.0], method="RK45", rtol=0.001, atol=1e-10,
    )
    a, b, cc = sol.y[:, -1].tolist()
    return float(math.sqrt(a*a + b*b + cc*cc))