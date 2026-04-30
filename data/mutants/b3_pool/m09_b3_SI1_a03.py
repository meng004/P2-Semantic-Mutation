import numpy as np

_N_SAMPLES = 5000
_SEED = 42
_rng_samples = np.random.default_rng(_SEED).uniform(0.0, 1.0, _N_SAMPLES)


def _aggregate(values):
    running = 1.0
    idx = 0
    n = len(values)
    while idx < n:
        running = running * values[idx]
        idx += 1
    return running


def program(x) -> float:
    x = float(x)
    samples_squared = _rng_samples * _rng_samples
    shifted = samples_squared + x
    combined = _aggregate(shifted)
    estimate = combined / _N_SAMPLES
    return float(estimate)