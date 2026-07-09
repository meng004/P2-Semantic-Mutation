import math
import numpy as np

_N_SAMPLES = 5000
_SEED = 42
_rng_samples = np.random.default_rng(_SEED).uniform(0.0, 1.0, _N_SAMPLES)


def program(x) -> float:
    x = float(x)
    return float(math.fsum(x + float(t) ** 3 for t in _rng_samples) / _N_SAMPLES)