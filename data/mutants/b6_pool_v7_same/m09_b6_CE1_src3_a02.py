import numpy as np

_SEED = 42
_N = 6000
_U = np.random.default_rng(_SEED).uniform(1e-12, 1.0, _N)


def program(x) -> float:
    x = float(x)
    scale = 1.0 / (2.5 - 1.0 * x)
    samples = -np.log(_U) * scale
    return float(np.mean(samples))