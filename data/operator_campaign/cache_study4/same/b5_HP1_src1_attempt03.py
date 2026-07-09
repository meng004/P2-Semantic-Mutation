import numpy as np

_SEED = 42
_LO, _HI = -3.0, 3.0


def _accept_prob(t, mu):
    return np.exp(-0.5 * (t - mu) ** 2)


def program(x) -> float:
    mu = 4.0 * float(x) - 2.0
    rng = np.random.default_rng(_SEED)
    props = rng.uniform(_LO, _HI, 50)
    us = rng.uniform(0.0, 1.0, 50)
    accept = us < _accept_prob(props, mu)
    return float(np.mean(props[accept]))