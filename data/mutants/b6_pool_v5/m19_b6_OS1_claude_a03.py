import numpy as np

_SEED = 42
_N = 6000
_U = np.random.default_rng(_SEED).uniform(1e-12, 1.0, _N)


def _draw(lam):
    return np.log(_U) / lam


def program(x) -> float:
    lam = 2.5 - 2.0 * float(x)
    return float(np.mean(_draw(lam)))