import numpy as np


def program(x) -> float:
    x = float(x)
    u = np.random.default_rng(42).uniform(1e-12, 1.0, 30)
    lam = 2.5 - 2.0 * x
    return float(np.mean(-np.log(u) / lam))