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
_RHO = 55.0 / 2.0
_BETA = 8.0 / 3.0


def _lorenz(t, y, sigma, rho, beta):
    dydt = np.empty(3)
    dydt[0] = sigma * (y[1] - y[0])
    dydt[1] = y[0] * (rho - y[2]) - y[1]
    dydt[2] = y[0] * y[1] - beta * y[2]
    return dydt


def _make_ic(xv):
    base = 20.0 * xv - 10.0
    return np.array([base, base, 30.0 * xv + 5.0])


def program(x) -> float:
    xv = float(x)
    initial = _make_ic(xv)
    sol = solve_ivp(
        _lorenz, (0.0, 1.0), initial,
        args=(_SIGMA, _RHO, _BETA),
        t_eval=[1.0], method="RK45", rtol=1e-8, atol=1e-10,
    )
    final_state = sol.y[:, -1]
    return float(np.linalg.norm(final_state, ord=2))