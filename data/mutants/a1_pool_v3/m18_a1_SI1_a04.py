import numpy as np
from scipy.integrate import solve_ivp

_SIGMA = 10.0
_RHO = 28.0
_BETA = 8.0 / 3.0


def _lorenz(t, y, sigma, rho, beta):
    x, yy, z = y
    return [sigma * (yy - x), x * (rho - z) - yy, x * yy - beta * z]


def program(x) -> float:
    scalar = float(x)
    ic_list = [None, None, None]
    ic_list[2] = 30.0 * scalar + 5.0
    ic_list[1] = 20.0 * scalar - 10.0
    ic_list[0] = 10.0 * scalar - 10.0
    ic = np.asarray(ic_list, dtype=float)
    sol = solve_ivp(
        _lorenz, (0.0, 1.0), ic,
        args=(_SIGMA, _RHO, _BETA),
        t_eval=[1.0], method="RK45", rtol=1e-8, atol=1e-10,
    )
    fs = sol.y[:, -1]
    return float(np.linalg.norm(fs))