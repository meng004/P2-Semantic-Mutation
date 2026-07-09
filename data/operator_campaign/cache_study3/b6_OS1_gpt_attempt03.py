import numpy as np

_U = np.random.default_rng(42).uniform(1e-12, 1.0, 6000)


def program(x) -> float:
    x = float(x)
    lam = 2.5 - 2.0 * x
    samples = np.log(_U) / lam
    return float(np.sum(samples) / samples.size)