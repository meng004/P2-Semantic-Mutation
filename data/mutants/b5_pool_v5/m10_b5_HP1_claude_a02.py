"""B5 mutant b5_HP1 claude/2."""
import numpy as np

_SEED = 42
_LO, _HI = -3.0, 3.0
_N_PROP = 50


def program(x) -> float:
    x = float(x)
    mu = 4.0 * x - 2.0
    n_prop = _N_PROP
    rng = np.random.default_rng(_SEED)
    props = rng.uniform(_LO, _HI, n_prop)
    us = rng.uniform(0.0, 1.0, n_prop)
    accept = us < np.exp(-0.5 * (props - mu) ** 2)
    return float(np.mean(props[accept]))