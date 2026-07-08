import numpy as np


def program(x) -> float:
    t_end, n_steps = 1.0, 20
    h = t_end / n_steps
    f = lambda v: v
    state = 2.0 * float(x) - 1.0
    for _step in range(n_steps):
        a = f(state)
        b = f(state + h * a / 2.0)
        c = f(state + h * b / 2.0)
        d = f(state + h * c)
        state = state + (h / 6.0) * (a + 2.0 * b + 2.0 * c + d)
    return float(np.asarray(state).item())