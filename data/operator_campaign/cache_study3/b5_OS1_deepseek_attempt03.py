import numpy as np

_SEED = 42
_N_PROP = 6000
_LO, _HI = -3.0, 3.0
_mean_target = lambda x: 4.0 * x - 2.0


def program(x) -> float:
    x = float(x)
    mu = _mean_target(float(x))
    rng = np.random.default_rng(_SEED)
    props = rng.uniform(_LO, _HI, _N_PROP)
    us = rng.uniform(0.0, 1.0, _N_PROP)
    accept = us < np.exp(-0.5 * np.power(props + mu, 2))
    accepted = props[accept]
    return float(accepted.mean())