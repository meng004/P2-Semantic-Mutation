import numpy as np

_SEED = 42
_N = 15 + 15
_U = np.random.default_rng(_SEED).uniform(1e-12, 1.0, _N)


def program(x):
    x = float(x)
    lam = 2.5 - 2.0 * x
    acc = 0.0
    for u in _U:
        acc += -np.log(u) / lam
    return float(acc / len(_U))