import numpy as np


def program(x) -> float:
    x = float(x)
    u = np.random.default_rng(42).uniform(1e-12, 1.0, 6000)
    lam = 2.5 - 1.0 * x
    samples = -np.log(u) / lam
    return float(np.mean(samples))