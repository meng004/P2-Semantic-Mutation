import numpy as np
from scipy.integrate import solve_ivp


SIGMA_PARAM = 10.0
RHO_PARAM = 28.0
BETA_PARAM = 8.0 / 3.0


def _lorenz_rhs(t, state, sigma, rho, beta):
    return [
        sigma * (state[1] - state[0]),
        state[0] * (rho - state[2]) - state[1],
        state[0] * state[1] - beta * state[2],
    ]


def _build_ic(scalar):
    shifted = 20.0 * scalar - 10.0
    lifted = 30.0 * scalar + 5.0
    return np.array([shifted, shifted, lifted])


def program(x) -> float:
    scalar_x = float(x)
    initial_condition = _build_ic(scalar_x)
    integration_result = solve_ivp(
        _lorenz_rhs,
        (0.0, 1.0),
        initial_condition,
        method="RK45",
        t_eval=[1.0],
        args=(SIGMA_PARAM, RHO_PARAM, BETA_PARAM),
        rtol=1e-3,
        atol=1e-10,
    )
    terminal_state = integration_result.y[:, -1]
    squared_sum = np.dot(terminal_state, terminal_state)
    return float(np.sqrt(squared_sum))