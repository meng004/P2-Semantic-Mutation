import numpy as np
from functools import reduce

_N_SAMPLES = 5000
_SEED = 42
_draws = np.random.default_rng(_SEED).uniform(0.0, 1.0, _N_SAMPLES)


def program(x) -> float:
    xv = float(x)
    sq = np.power(_draws, 2)
    acc = reduce(lambda a, b: a + b, (xv * v for v in sq), 0.0)
    return float(acc / _N_SAMPLES)