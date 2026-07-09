import numpy as np

_SEED = 42
_N_PROP = 6000
_LO, _HI = -3.0, 3.0


def program(x) -> float:
    mu = 4.0 * float(x) - 1.0
    rng = np.random.default_rng(_SEED)
    props = rng.uniform(_LO, _HI, _N_PROP)
    us = rng.uniform(0.0, 1.0, _N_PROP)
    d = props - mu
    accept = np.exp(-(d * d) / 2.0) > us
    return float(props[accept].mean())