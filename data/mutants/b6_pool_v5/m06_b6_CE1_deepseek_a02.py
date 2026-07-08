import numpy as np

_SEED = 42
_N = 6000
_U = np.random.default_rng(_SEED).uniform(1e-12, 1.0, _N)


def program(x) -> float:
    x = float(x)
    inv_scale = np.float64(2.5) - np.float64(1.0) * np.float64(x)
    exp_draws = -np.log(_U)
    return float(np.mean(exp_draws) / inv_scale)