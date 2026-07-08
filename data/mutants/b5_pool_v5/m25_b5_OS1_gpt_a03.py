"""B5 mutant b5_OS1 gpt/3."""
import numpy as np

_SEED = 42
_N_PROP = 6000
_LO, _HI = -3.0, 3.0


def program(x) -> float:
    x = float(x)
    mu = 4.0 * x - 2.0
    neg_mu = -mu
    rng = np.random.default_rng(_SEED)
    props = rng.uniform(_LO, _HI, _N_PROP)
    us = rng.uniform(0.0, 1.0, _N_PROP)
    accept = us < np.exp(-0.5 * (props - neg_mu) ** 2)
    return float(np.mean(props[accept]))