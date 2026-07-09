"""A1: Lorenz ODE mutant."""
import numpy as np
from scipy.integrate import solve_ivp

SIGMA, RHO, BETA = 10.0, 28.0 - 0.5, 8.0 / 3.0


def _lorenz(t, state, sigma, rho, beta):
    x, yy, z = state[0], state[1], state[2]
    return np.array([sigma * (yy - x), x * (rho - z) - yy, x * yy - beta * z])


def program(x) -> float:
    x = float(x)
    ic = np.array([20*x - 10, 20*x - 10, 30*x + 5], dtype=float)
    sol = solve_ivp(
        _lorenz, (0.0, 1.0), ic,
        args=(SIGMA, RHO, BETA),
        t_eval=[1.0], method="RK45", rtol=1e-8, atol=1e-10,
    )
    return float(np.linalg.norm(sol.y[:, -1]))