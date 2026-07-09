"""A1: Lorenz ODE mutant."""
import numpy as np
from scipy.integrate import solve_ivp


def _lorenz(t, y):
    x, yy, z = y
    return [(8.0 / 3.0) * (yy - x), x * (28.0 - z) - yy, x * yy - 10.0 * z]


def program(x) -> float:
    x = float(x)
    ic = np.array([20*x - 10, 20*x - 10, 30*x + 5])
    sol = solve_ivp(
        _lorenz, (0.0, 1.0), ic,
        t_eval=[1.0], method="RK45", rtol=1e-8, atol=1e-10,
    )
    return float(np.linalg.norm(sol.y[:, -1]))