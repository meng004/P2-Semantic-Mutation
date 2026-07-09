import numpy as np
from scipy.integrate import solve_ivp

_SIGMA = 10.0
_RHO = 28.0
_BETA = 8.0 / 3.0


def _lorenz(t, y, sigma, rho, beta):
    x0, x1, x2 = y
    dx0 = sigma * (x1 - x0)
    dx1 = x0 * (rho - x2) - x1
    dx2 = x0 * x1 - beta * x2
    return [dx0, dx1, dx2]


def program(x) -> float:
    value = float(x)
    initial_state = np.array(
        [20.0 * value - 10.0, 20.0 * value - 10.0, 30.0 * value + 5.0],
        dtype=float,
    )

    solution = solve_ivp(
        fun=_lorenz,
        t_span=(0.0, 1.0),
        y0=initial_state,
        args=(_SIGMA, _RHO, _BETA),
        t_eval=[1.0],
        method="RK45",
        rtol=1e-3,
        atol=1e-10,
    )

    terminal = solution.y[:, solution.y.shape[1] - 1]
    return float(np.linalg.norm(terminal))