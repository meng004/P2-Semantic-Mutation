"""A1: Lorenz ODE mutant."""
import numpy as np
from scipy.integrate import solve_ivp


def program(x) -> float:
    x = float(x)
    sigma, rho, beta = 10.0, 28.0, 8.0 / 3.0

    def rhs(t, y):
        x_, yy, z = y
        return [beta * (yy - x_), x_ * (rho - z) - yy, x_ * yy - sigma * z]

    ic = np.array([20*x - 10, 20*x - 10, 30*x + 5])
    sol = solve_ivp(
        rhs, (0.0, 1.0), ic,
        t_eval=[1.0], method="RK45", rtol=1e-8, atol=1e-10,
    )
    return float(np.linalg.norm(sol.y[:, -1]))