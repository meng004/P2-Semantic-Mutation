import numpy as np
from scipy.integrate import solve_ivp

_SIGMA = 10.0
_RHO = 28.0
_BETA = 8.0 / 3.0


def _lorenz(t, y, sigma, rho, beta):
    x, z, yy = y  # Swapped ordering of yy and z
    return [sigma * (z - x), x * (rho - yy) - z, x * z - beta * yy]  # Adjusted correspondingly


def program(x) -> float:
    x = float(x)
    ic = np.array([20*x - 10, 30*x + 5, 20*x - 10])  # Swapped initial condition ordering of y and z
    sol = solve_ivp(
        _lorenz, (0.0, 1.0), ic,
        args=(_SIGMA, _RHO, _BETA),
        t_eval=[1.0], method="RK45", rtol=1e-8, atol=1e-10,
    )
    final_state = sol.y[:, -1]
    return float(np.linalg.norm(final_state))