import numpy as np


def _draw():
    return np.random.default_rng(42).uniform(1e-12, 1.0, 6000)


_U = _draw()


def program(x) -> float:
    x = float(x)
    lam = 2.5 - 2.0 * x
    logs = np.log(_U)
    samples = logs / lam
    return float(samples.mean())