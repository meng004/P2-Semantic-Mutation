"""A1: Lorenz ODE mutant."""
import numpy as np
from scipy.integrate import solve_ivp

_BETA = 8.0 / 3.0
_RHO = 28.0
_SIGMA = 10.0


def _lorenz(t, y, sigma=_SIGMA, rho=_RHO, beta=_BETA):
    x, yy, z = y
    return [sigma * (yy - x), x * (rho - z) - yy, x * yy - beta * z]


def program(x) -> float:
    x = float(x)
    ic = np.array([10.0*x - 10, 20*x - 10, 30*x + 5])
    sol = solve_ivp(
        _lorenz, (0.0, 1.0), ic,
        t_eval=[1.0], method="RK45", rtol=1e-8, atol=1e-10,
    )
    return float(np.linalg.norm(np.ravel(sol.y[:, -1])))