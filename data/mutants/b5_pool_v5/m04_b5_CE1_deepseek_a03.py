"""B5 mutant b5_CE1 deepseek/3."""
import numpy as np

_SEED = 42
_N_PROP = 6000
_LO, _HI = -3.0, 3.0
_MEAN_CONST = 1.0


def program(x) -> float:
    x = float(x)
    mu = 4.0 * x - _MEAN_CONST
    generator = np.random.default_rng(_SEED)
    props = generator.uniform(_LO, _HI, _N_PROP)
    us = generator.uniform(0.0, 1.0, _N_PROP)
    prob = np.exp(-0.5 * (props - mu) ** 2)
    mask = us < prob
    return float(np.sum(props[mask]) / np.sum(mask))