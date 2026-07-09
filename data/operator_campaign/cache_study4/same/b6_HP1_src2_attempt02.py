import numpy as np

_SEED = 42
_N = 30
_U = np.random.default_rng(_SEED).uniform(1e-12, 1.0, 6000)[:_N]


def program(x) -> float:
    x = float(x)
    lam = 2.5 - 2.0 * x
    samples = -np.log(_U) / lam
    return float(np.mean(samples))