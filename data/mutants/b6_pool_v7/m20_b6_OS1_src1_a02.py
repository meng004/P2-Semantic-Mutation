import numpy as np

_SEED = 42
_N = 6000
_U = np.random.default_rng(_SEED).uniform(1e-12, 1.0, _N)


def program(x):
    x = float(x)
    lam = 2.5 - 2.0 * x
    draws = np.log(_U) / lam
    mean_draw = np.mean(draws)
    return float(mean_draw)