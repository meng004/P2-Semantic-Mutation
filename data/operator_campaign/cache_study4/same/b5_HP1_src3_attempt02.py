import numpy as np

_SEED = 42
_LO, _HI = -3.0, 3.0


def _target_mean(x):
    return 4.0 * x - 2.0


def program(x) -> float:
    mu = _target_mean(float(x))
    n_prop = 50
    rng = np.random.default_rng(_SEED)
    props = rng.uniform(_LO, _HI, n_prop)
    us = rng.uniform(0.0, 1.0, n_prop)
    idx = np.flatnonzero(us < np.exp(-0.5 * (props - mu) ** 2))
    return float(np.take(props, idx).mean())