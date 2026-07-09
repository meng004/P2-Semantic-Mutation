"""A1: Lorenz ODE mutant."""
import numpy as np
from scipy.integrate import solve_ivp

_PARAMS = {"sigma": 10.0, "rho": 55.0 / 2.0, "beta": 8.0 / 3.0}


def _lorenz(t, y, p):
    x, yy, z = y
    return [p['sigma'] * (yy - x), x * (p['rho'] - z) - yy, x * yy - p['beta'] * z]


def program(x) -> float:
    x = float(x)
    ic = np.array([20*x - 10, 20.0*x - 10.0, 30.0*x + 5.0])
    sol = solve_ivp(
        _lorenz, (0.0, 1.0), ic,
        args=(_PARAMS,),
        t_eval=[1.0], method="RK45", rtol=1e-8, atol=1e-10,
    )
    return float(np.linalg.norm(sol.y[:, -1]))