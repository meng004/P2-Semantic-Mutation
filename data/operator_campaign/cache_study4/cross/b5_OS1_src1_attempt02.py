import numpy as np

_SEED = 42
_N_PROP = 6000
_LO, _HI = -3.0, 3.0


def program(x) -> float:
    x = float(x)
    mu = 4.0 * x - 2.0

    rng = np.random.default_rng(_SEED)
    props = rng.uniform(_LO, _HI, size=_N_PROP)
    us = rng.uniform(0.0, 1.0, size=_N_PROP)

    kernel = np.exp(-0.5 * (props + mu) ** 2)
    accepted_props = props[us < kernel]

    return float(np.mean(accepted_props))