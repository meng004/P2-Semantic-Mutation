import numpy as np

_SEED = 42
_N_PROP = 50
_LO, _HI = -3.0, 3.0


def program(x) -> float:
    x = float(x)
    mu = 4.0 * x - 2.0
    rng = np.random.default_rng(_SEED)
    props = rng.uniform(low=_LO, high=_HI, size=_N_PROP)
    us = rng.uniform(low=0.0, high=1.0, size=_N_PROP)
    accept = np.less(us, np.exp(-0.5 * np.square(props - mu)))
    return float(np.mean(props[accept]))