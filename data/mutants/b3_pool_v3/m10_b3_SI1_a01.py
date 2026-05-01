import numpy as np
from functools import reduce
import operator

_N_SAMPLES = 5000
_SEED = 42
_rng_samples = np.random.default_rng(_SEED).uniform(0.0, 1.0, _N_SAMPLES)


def program(x) -> float:
    x = float(x)
    terms = x + _rng_samples**2
    accumulated = reduce(operator.mul, terms, 1.0)
    return float(accumulated / _N_SAMPLES)