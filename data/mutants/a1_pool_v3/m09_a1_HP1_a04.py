import numpy as np
from scipy.integrate import solve_ivp


def program(x) -> float:
    sigma = 10.0
    rho = 28.0
    beta = 8.0 / 3.0

    def rhs(t, y):
        u0, u1, u2 = y
        return np.array([
            sigma * (u1 - u0),
            u0 * (rho - u2) - u1,
            u0 * u1 - beta * u2,
        ])

    xf = float(x)
    y_init = np.array([20.0 * xf - 10.0, 20.0 * xf - 10.0, 30.0 * xf + 5.0])

    out = solve_ivp(
        rhs,
        [0.0, 1.0],
        y_init,
        method="RK45",
        t_eval=[1.0],
        rtol=1e-3,
        atol=1e-10,
    )

    final = out.y[:, -1]
    norm_sq = 0.0
    for i in range(final.shape[0]):
        norm_sq = norm_sq + final[i] ** 2
    return float(norm_sq ** 0.5)