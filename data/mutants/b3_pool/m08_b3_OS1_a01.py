import numpy as np

_N_SAMPLES = 5000
_SEED = 42
_rng = np.random.default_rng(_SEED)
_samples = _rng.uniform(0.0, 1.0, _N_SAMPLES)
_t_squared = np.square(_samples)


def program(x) -> float:
    xv = float(x)
    total = 0.0
    for ts in _t_squared:
        total += xv * ts
    return float(total / _N_SAMPLES)