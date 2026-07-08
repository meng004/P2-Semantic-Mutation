"""B5 mutant b5_CE1 deepseek/2."""
import numpy as np

_SEED = 42
_N_PROP = 6000
_LO, _HI = -3.0, 3.0

_shift = lambda t: 4.0 * t - 1.0


def program(x) -> float:
    x = float(x)
    mu = _shift(x)
    rng = np.random.default_rng(_SEED)
    props = rng.uniform(_LO, _HI, _N_PROP)
    us = rng.uniform(0.0, 1.0, _N_PROP)
    d = props - mu
    accept = us < np.exp(-0.5 * d * d)
    return float(np.mean(props[accept]))