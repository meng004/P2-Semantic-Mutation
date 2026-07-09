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
    ic = np.array([20 * x - 10, 20 * x - 10, 30 * x + 5])
    
    # Structurally modified call to solve_ivp with mutated rtol
    ode_args = (_SIGMA, _RHO, _BETA)
    sol = solve_ivp(
        fun=_lorenz,
        t_span=(0.0, 1.0),
        y0=ic,
        method="RK45",
        t_eval=[1.0],
        rtol=1e-3,
        atol=1e-10,
        args=ode_args,
    )
    final_state = sol.y[:, -1]
    return float(np.linalg.norm(final_state))