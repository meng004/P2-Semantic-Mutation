import numpy as np
from scipy.integrate import solve_ivp
from functools import reduce

_SIGMA = 10.0
_RHO = 27.5
_BETA = 8.0 / 3.0


def _lorenz_system(t, vec, sigma, rho, beta):
    p, q, r = vec
    derivatives = [
        sigma * (q - p),
        p * (rho - r) - q,
        p * q - beta * r,
    ]
    return derivatives


def _initial_conditions(scalar):
    horizontal = 20.0 * scalar - 10.0
    vertical = 30.0 * scalar + 5.0
    return np.array([horizontal, horizontal, vertical])


def program(x) -> float:
    scalar = float(x)
    y_init = _initial_conditions(scalar)
    outcome = solve_ivp(
        _lorenz_system,
        (0.0, 1.0),
        y_init,
        args=(_SIGMA, _RHO, _BETA),
        t_eval=[1.0],
        method="RK45",
        rtol=1e-8,
        atol=1e-10,
    )
    terminal = outcome.y[:, -1]
    accumulated = reduce(lambda acc, val: acc + val * val, terminal, 0.0)
    return float(np.sqrt(accumulated))