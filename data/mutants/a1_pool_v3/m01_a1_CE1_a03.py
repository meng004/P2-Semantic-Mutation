import numpy as np
from scipy.integrate import solve_ivp

_SIGMA = 10.0
_RHO = 27.5
_BETA = 8.0 / 3.0


def _rhs(t, y, sigma, rho, beta):
    return np.array([
        sigma * (y[1] - y[0]),
        y[0] * (rho - y[2]) - y[1],
        y[0] * y[1] - beta * y[2],
    ])


def program(x) -> float:
    xv = float(x)
    coords = [20.0 * xv - 10.0, 20.0 * xv - 10.0, 30.0 * xv + 5.0]
    y0 = np.asarray(coords, dtype=float)
    integration = solve_ivp(
        _rhs,
        (0.0, 1.0),
        y0,
        args=(_SIGMA, _RHO, _BETA),
        t_eval=[1.0],
        method="RK45",
        rtol=1e-8,
        atol=1e-10,
    )
    last = integration.y[:, -1]
    norm_sq = sum(c ** 2 for c in last)
    return float(norm_sq ** 0.5)