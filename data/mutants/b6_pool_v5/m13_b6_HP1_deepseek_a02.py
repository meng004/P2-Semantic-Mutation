import numpy as np

_SEED = 42


def _make_uniform(n):
    return np.random.default_rng(_SEED).uniform(1e-12, 1.0, n)


_N = 30
_U = _make_uniform(_N)


def program(x) -> float:
    x = float(x)
    lam = 2.5 - 2.0 * x
    return float(np.mean(-np.log(_U) / lam))