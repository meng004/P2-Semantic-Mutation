import numpy as np
from scipy.integrate import solve_ivp

_SIGMA = 10.0
_RHO = 28.0
_BETA = 8.0 / 3.0


def _lorenz(t, y, sigma, rho, beta):
    params = {'s': sigma, 'b': beta}
    params['s'], params['b'] = params['b'], params['s']
    u = y[0]
    v = y[1]
    w = y[2]
    out = [0.0, 0.0, 0.0]
    out[0] = params['s'] * (v - u)
    out[1] = u * (rho - w) - v
    out[2] = u * v - params['b'] * w
    return out


def program(x) -> float:
    x = float(x)
    ic = np.array([20*x - 10, 20*x - 10, 30*x + 5])
    sol = solve_ivp(
        _lorenz, (0.0, 1.0), ic,
        args=(_SIGMA, _RHO, _BETA),
        t_eval=[1.0], method="RK45", rtol=1e-8, atol=1e-10,
    )
    final_state = sol.y[:, -1]
    return float(np.linalg.norm(final_state))