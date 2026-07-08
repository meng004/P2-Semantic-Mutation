import numpy as np

_SEED = 42
_N = 6000
_U = np.random.default_rng(_SEED).uniform(1e-12, 1.0, _N)


def program(x):
    x = float(x)
    coeff = 1.0
    lam = 2.5 - coeff * x
    return float(np.mean(-np.log(_U)) / lam)