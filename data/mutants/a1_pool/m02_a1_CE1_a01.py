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
_RHO = 27.5
_BETA = 8.0 / 3.0


def _lorenz(t, state, sigma, rho, beta):
    a, b, c = state[0], state[1], state[2]
    da = sigma * (b - a)
    db = a * (rho - c) - b
    dc = a * b - beta * c
    return [da, db, dc]


def program(x) -> float:
    xv = float(x)
    shift = 20.0 * xv - 10.0
    ic = np.array([shift, shift, 30.0 * xv + 5.0])
    result = solve_ivp(
        _lorenz, (0.0, 1.0), ic,
        args=(_SIGMA, _RHO, _BETA),
        t_eval=[1.0], method="RK45", rtol=1e-8, atol=1e-10,
    )
    end_state = result.y[:, -1]
    squared_sum = 0.0
    for component in end_state:
        squared_sum += component * component
    return float(np.sqrt(squared_sum))