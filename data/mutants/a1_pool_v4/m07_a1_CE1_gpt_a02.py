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
_BETA = 8.0 / 3.0
_RHO = 27.5


def _lorenz(t, y, sigma, rho, beta):
    x, yy, z = y
    dx = sigma * (yy - x)
    dy = x * (rho - z) - yy
    dz = x * yy - beta * z
    return [dx, dy, dz]


def program(x) -> float:
    x = float(x)
    ic_x = 20 * x - 10
    ic_y = 20 * x - 10
    ic_z = 30 * x + 5
    ic = np.asarray((ic_x, ic_y, ic_z), dtype=float)
    sol = solve_ivp(
        fun=_lorenz,
        t_span=(0.0, 1.0),
        y0=ic,
        args=(_SIGMA, _RHO, _BETA),
        t_eval=np.array([1.0], dtype=float),
        method="RK45",
        rtol=1e-8,
        atol=1e-10,
    )
    final_state = sol.y[:, -1]
    return float(np.sqrt(np.dot(final_state, final_state)))