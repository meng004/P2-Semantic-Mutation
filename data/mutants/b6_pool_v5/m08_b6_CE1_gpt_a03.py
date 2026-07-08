import numpy as np

_SEED = 42
_N = 6000
_U = np.random.default_rng(_SEED).uniform(1e-12, 1.0, _N)


def program(x):
    x = float(x)
    lam = 2.5 + (-1.0) * x
    result = 0.0
    for u in (-np.log(_U) / lam):
        result += u
    return float(result / _N)