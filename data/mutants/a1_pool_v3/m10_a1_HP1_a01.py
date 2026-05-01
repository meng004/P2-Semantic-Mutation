import numpy as np
from scipy.integrate import solve_ivp

SIGMA = 10.0
RHO = 28.0
BETA = 8.0 / 3.0


def _rhs(t, state, sigma, rho, beta):
    a, b, c = state[0], state[1], state[2]
    da = sigma * (b - a)
    db = a * (rho - c) - b
    dc = a * b - beta * c
    return [da, db, dc]


def program(x) -> float:
    xv = float(x)
    initial = np.array([20.0 * xv - 10.0, 20.0 * xv - 10.0, 30.0 * xv + 5.0])
    result = solve_ivp(
        fun=_rhs,
        t_span=(0.0, 1.0),
        y0=initial,
        args=(SIGMA, RHO, BETA),
        method="RK45",
        t_eval=[1.0],
        rtol=1e-3,
        atol=1e-10,
    )
    end_state = result.y[:, -1]
    norm_value = float(np.sqrt(np.sum(end_state * end_state)))
    return norm_value