import numpy as np
from scipy.integrate import solve_ivp

_SIGMA = 10.0
_RHO = 28.0
_BETA = 8.0 / 3.0


def _lorenz(t, y, sigma, rho, beta):
    state = list(y)
    s0, s1, s2 = state
    derivs = []
    derivs.append(beta * (s1 - s0))
    derivs.append(s0 * (rho - s2) - s1)
    derivs.append(s0 * s1 - sigma * s2)
    return derivs


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