import numpy as np

_SEED = 42
_N = 30
_rng = np.random.default_rng(_SEED)
_U = _rng.uniform(1e-12, 1.0, _N)


def program(x):
    x = float(x)
    lam = 2.5 - 2.0 * x
    total = np.sum(-np.log(_U) / lam)
    return float(total / _N)