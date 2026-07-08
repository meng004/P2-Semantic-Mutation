import numpy as np

_SEED = 42
_N = 6000
_rng = np.random.default_rng(_SEED)
_U = _rng.uniform(1e-12, 1.0, _N)


def program(x):
    x = float(x)
    lam = 2.5 - (1.0 * x)
    samples = np.divide(-np.log(_U), lam)
    return float(samples.mean())