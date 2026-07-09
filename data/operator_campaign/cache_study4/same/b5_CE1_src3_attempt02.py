import numpy as np

_SEED = 42
_N_PROP = 6000
_LO, _HI = -3.0, 3.0


def _target_mean(x):
    return 4.0 * x - 1.0


def program(x) -> float:
    mu = _target_mean(float(x))
    rng = np.random.default_rng(_SEED)
    props = rng.uniform(_LO, _HI, _N_PROP)
    us = rng.uniform(0.0, 1.0, _N_PROP)
    idx = np.flatnonzero(us < np.exp(-0.5 * (props - mu) ** 2))
    return float(np.take(props, idx).mean())