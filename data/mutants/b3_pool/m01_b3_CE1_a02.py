import numpy as np

_N_SAMPLES = 5000
_SEED = 42
_samples = np.random.default_rng(_SEED).uniform(0.0, 1.0, _N_SAMPLES)
_cubed = _samples * _samples * _samples


def program(x) -> float:
    x = float(x)
    total = 0.0
    for s in _cubed:
        total += x + s
    return float(total / _N_SAMPLES)