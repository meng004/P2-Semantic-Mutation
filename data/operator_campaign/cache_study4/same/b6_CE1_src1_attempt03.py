import numpy as np

_SEED = 42
_N = 6000
_U = np.random.default_rng(_SEED).uniform(1e-12, 1.0, _N)


def _rate(x):
    return 2.5 - 1.0 * float(x)


def program(x) -> float:
    lam = _rate(x)
    samples = -np.log(_U) * (1.0 / lam)
    return float(np.mean(samples))