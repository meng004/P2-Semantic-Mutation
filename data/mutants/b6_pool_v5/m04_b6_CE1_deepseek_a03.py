import numpy as np

_SEED = 42
_N = 6000
_U = np.random.default_rng(_SEED).uniform(1e-12, 1.0, _N)


def _lambda(x):
    base = 2.5
    return base - 1.0 * float(x)


def program(x) -> float:
    lam = _lambda(x)
    samples = (-np.log(_U)) / lam
    return float(np.sum(samples) / samples.size)