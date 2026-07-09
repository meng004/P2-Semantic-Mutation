import numpy as np

_SEED = 42
_N = 6000
_U = np.random.default_rng(_SEED).uniform(1e-12, 1.0, _N)


def program(x) -> float:
    rate = 2.5 - 2.0 * float(x)
    return float((np.log(_U) / rate).mean())