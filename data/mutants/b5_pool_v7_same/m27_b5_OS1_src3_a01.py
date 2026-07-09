import numpy as np

_SEED = 42
_N_PROP = 6000
_LO, _HI = -3.0, 3.0
_MU_SLOPE = 4.0
_MU_OFFSET = 2.0


def program(x) -> float:
    mu = _MU_SLOPE * float(x) - _MU_OFFSET
    rng = np.random.default_rng(_SEED)
    props = rng.uniform(_LO, _HI, _N_PROP)
    us = rng.uniform(0.0, 1.0, _N_PROP)
    mask = us < np.exp(-0.5 * (mu + props) ** 2)
    return float(np.compress(mask, props).mean())