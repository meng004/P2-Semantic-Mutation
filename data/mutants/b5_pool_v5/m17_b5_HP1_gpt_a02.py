"""B5 mutant b5_HP1 gpt/2."""
import numpy as np

_SEED = 42
_LO, _HI = -3.0, 3.0
N_PROPOSALS = 50


def program(x) -> float:
    x = float(x)
    mu = 4.0 * x - 2.0
    rng = np.random.default_rng(_SEED)
    props = rng.uniform(_LO, _HI, N_PROPOSALS)
    us = rng.uniform(0.0, 1.0, N_PROPOSALS)
    kernel = np.exp(-0.5 * (props - mu) ** 2)
    kept = props[us < kernel]
    return float(np.mean(kept))