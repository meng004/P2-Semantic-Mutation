import numpy as np

_SEED = 42
_N = 30


def program(x) -> float:
    x = float(x)
    u = np.random.default_rng(_SEED).uniform(1e-12, 1.0, _N)
    lam = 2.5 - 2.0 * x
    return float(np.mean(-np.log(u) / lam))