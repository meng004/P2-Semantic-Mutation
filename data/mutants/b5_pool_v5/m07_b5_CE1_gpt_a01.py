"""B5 mutant b5_CE1 gpt/1."""
import numpy as np

_SEED = 42
_N_PROP = 6000
_LO, _HI = -3.0, 3.0
_SLOPE, _INTERCEPT = 4.0, -1.0


def program(x) -> float:
    x = float(x)
    mu = _SLOPE * x + _INTERCEPT
    rng = np.random.default_rng(_SEED)
    props = rng.uniform(_LO, _HI, _N_PROP)
    us = rng.uniform(0.0, 1.0, _N_PROP)
    weights = np.exp(-0.5 * (props - mu) ** 2)
    accept = us < weights
    return float(np.mean(props[accept]))