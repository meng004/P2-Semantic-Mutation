import numpy as np
from scipy.integrate import solve_ivp


def _lorenz_system(t, y, sigma, rho, beta):
    derivs = [0.0, 0.0, 0.0]
    derivs[0] = sigma * (y[1] - y[0])
    derivs[1] = y[0] * (rho - y[2]) - y[1]
    derivs[2] = y[0] * y[1] - beta * y[2]
    return derivs


_PARAMS = (10.0, 28.0, 8.0 / 3.0)


def program(x) -> float:
    val = float(x)
    y0 = np.array([20.0 * val - 10.0, 20.0 * val - 10.0, 30.0 * val + 5.0])
    integration = solve_ivp(
        _lorenz_system,
        (0.0, 1.0),
        y0,
        method="RK45",
        t_eval=[1.0],
        args=_PARAMS,
        rtol=1e-3,
        atol=1e-10,
    )
    last = integration.y[:, -1]
    acc = 0.0
    for component in last:
        acc += component * component
    return float(np.sqrt(acc))