import numpy as np

_N_SAMPLES = 5000
_SEED = 42
_rng_samples = np.random.default_rng(_SEED).uniform(0.0, 1.0, _N_SAMPLES)


def program(x):
    x = float(x)
    return float(np.mean([x * s**2 for s in _rng_samples]))