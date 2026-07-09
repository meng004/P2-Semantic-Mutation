import numpy as np

_SEED = 42
_PROPOSAL_BUDGET = 50
_LO, _HI = -3.0, 3.0


def program(x) -> float:
    mu = 4.0 * float(x) - 2.0
    rng = np.random.default_rng(_SEED)
    props = rng.uniform(_LO, _HI, _PROPOSAL_BUDGET)
    us = rng.uniform(0.0, 1.0, _PROPOSAL_BUDGET)
    mask = us < np.exp(-0.5 * (props - mu) ** 2)
    return float(np.compress(mask, props).mean())