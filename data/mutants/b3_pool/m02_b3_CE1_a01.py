import numpy as np

_N_SAMPLES = 5000
_SEED = 42
_rng = np.random.default_rng(_SEED)
_t = _rng.uniform(0.0, 1.0, _N_SAMPLES)


def program(x) -> float:
    x = float(x)
    integrand = x + np.power(_t, 3)
    return float(integrand.sum() / _N_SAMPLES)