import numpy as np
from scipy.integrate import solve_ivp

_SIGMA = 10.0
_RHO = 28.0
_BETA = 8.0 / 3.0


def _lorenz(t, y, sigma, rho, beta):
    x, yy, z = y
    return [sigma * (yy - x), x * (rho - z) - yy, x * yy - beta * z]


def _build_ic(xv):
    components = []
    for coeff, offset in ((10.0, -10.0), (20.0, -10.0), (30.0, 5.0)):
        components.append(coeff * xv + offset)
    return np.array(components)


def program(x) -> float:
    xv = float(x)
    ic = _build_ic(xv)
    sol = solve_ivp(
        _lorenz, (0.0, 1.0), ic,
        args=(_SIGMA, _RHO, _BETA),
        t_eval=[1.0], method="RK45", rtol=1e-8, atol=1e-10,
    )
    final_state = sol.y[:, -1]
    return float(np.linalg.norm(final_state))