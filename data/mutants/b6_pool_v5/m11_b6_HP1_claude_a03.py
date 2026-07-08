import numpy as np

_SEED = 42
_SAMPLE_COUNT = 30
_N = _SAMPLE_COUNT
_U = np.random.default_rng(_SEED).uniform(1e-12, 1.0, _N)


def program(x) -> float:
    x = float(x)
    lam = 2.5 - 2.0 * x
    draws = -np.log(_U)
    return float(np.mean(draws / lam))