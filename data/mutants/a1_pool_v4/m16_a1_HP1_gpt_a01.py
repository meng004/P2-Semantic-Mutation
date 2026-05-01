"""A1: Lorenz ODE — chaotic dynamical system (scalar-output interface).

Library: scipy.integrate.solve_ivp (scipy 1.17.1)
URL: https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html

program(x) where x ∈ [0,1] scalar.
Maps x to IC: [20x-10, 20x-10, 30x+5]. Integrates for t_end=1.0.
Returns L2 norm of state vector at t=1.0 (scalar float).
"""
import numpy as np
from scipy.integrate import solve_ivp

_SIGMA = 10.0
_RHO = 28.0
_BETA = 8.0 / 3.0


def _lorenz(t, y, sigma, rho, beta):
    x, yy, z = y
    return [sigma * (yy - x), x * (rho - z) - yy, x * yy - beta * z]


def program(x) -> float:
    x = float(x)
    initial = np.asarray([20.0 * x - 10.0, 20.0 * x - 10.0, 30.0 * x + 5.0], dtype=float)
    interval = (0.0, 1.0)
    sol = solve_ivp(
        fun=_lorenz,
        t_span=interval,
        y0=initial,
        args=(_SIGMA, _RHO, _BETA),
        method="RK45",
        t_eval=np.array([interval[1]], dtype=float),
        rtol=1e-3,
        atol=1e-10,
    )
    return float(np.sqrt(np.dot(sol.y[:, -1], sol.y[:, -1])))