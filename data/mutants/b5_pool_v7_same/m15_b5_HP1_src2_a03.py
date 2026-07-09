import numpy as np

_SEED = 42
_LO, _HI = -3.0, 3.0


def program(x) -> float:
    mu = 4.0 * float(x) - 2.0
    n = 50
    rng = np.random.default_rng(_SEED)
    props = rng.uniform(_LO, _HI, n)
    us = rng.uniform(0.0, 1.0, n)
    d = props - mu
    accept = np.exp(-(d * d) / 2.0) > us
    return float(props[accept].mean())