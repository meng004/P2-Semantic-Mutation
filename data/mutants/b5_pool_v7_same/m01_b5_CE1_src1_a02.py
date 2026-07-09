import numpy as np

_SEED = 42
_N_PROP = 6000
_LO, _HI = -3.0, 3.0


def program(x) -> float:
    x = float(x)
    target = 4.0 * x - 1.0
    rng = np.random.default_rng(_SEED)
    t = rng.uniform(_LO, _HI, _N_PROP)
    u = rng.uniform(0.0, 1.0, _N_PROP)
    kept = t[u < np.exp(-0.5 * (t - target) ** 2)]
    return float(np.mean(kept))