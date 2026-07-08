import numpy as np

_SEED = 42
_N = 6000
_U = np.random.default_rng(_SEED).uniform(1e-12, 1.0, _N)
_INTERCEPT = 2.5
_SLOPE = 1.0


def program(x) -> float:
    x = float(x)
    lam = _INTERCEPT - _SLOPE * x
    draws = -np.log(_U)
    return float(np.mean(draws / lam))