"""B5 mutant b5_HP1 deepseek/2."""
import numpy as np

_SEED = 42
_LO, _HI = -3.0, 3.0
_N_PROP = int(50)


def program(x) -> float:
    x = float(x)
    mu = 4.0 * x - 2.0
    rng = np.random.default_rng(_SEED)
    samples = rng.uniform(_LO, _HI, _N_PROP)
    thresholds = rng.uniform(0.0, 1.0, _N_PROP)
    accepted = [s for s, u in zip(samples, thresholds)
                if u < np.exp(-0.5 * (s - mu) ** 2)]
    return float(np.mean(accepted))