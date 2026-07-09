import numpy as np

_SEED = 42
_N = 6000
_U = np.random.default_rng(_SEED).uniform(1e-12, 1.0, _N)
_LOG_U = np.log(_U)


def program(x) -> float:
    x = float(x)
    lam = 2.5 - 2.0 * x
    samples = _LOG_U / lam
    return float(np.mean(samples))