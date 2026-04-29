"""A1: Lorenz ODE — chaotic dynamical system.

Library: scipy.integrate.solve_ivp (scipy 1.17.1)
URL: https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html

program(x) where x = [x0, y0, z0] (initial state, shape (3,))
Returns [x_T, y_T, z_T] at t_end=10 with classic Lorenz parameters σ=10, ρ=28, β=8/3.
"""
import numpy as np
from scipy.integrate import solve_ivp

_SIGMA = 10.0
_RHO = 28.0
_BETA = 8.0 / 3.0
_T_END = 10.0
_T_SPAN = (0.0, _T_END)
_T_EVAL = np.linspace(0.0, _T_END, 1000)


def _lorenz(t, y, sigma, rho, beta):
    x, y_, z = y
    return [
        sigma * (y_ - x),
        x * (rho - z) - y_,
        x * y_ - beta * z,
    ]


def program(x: np.ndarray) -> np.ndarray:
    """Integrate Lorenz ODE from initial state x=[x0,y0,z0]; return final state."""
    x = np.asarray(x, dtype=float)
    sol = solve_ivp(
        _lorenz,
        _T_SPAN,
        x,
        args=(_SIGMA, _RHO, _BETA),
        t_eval=_T_EVAL,
        method="RK45",
        rtol=1e-8,
        atol=1e-10,
    )
    return sol.y[:, -1]  # shape (3,)
