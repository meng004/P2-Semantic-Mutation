"""B5 mutant b5_CE1 gpt/3."""
import numpy as np

_SEED = 42
_N_PROP = 6000
_LO, _HI = -3.0, 3.0


def program(x) -> float:
    x = float(x)
    base = 4.0 * x
    mu = base - 1.0
    rng = np.random.default_rng(_SEED)
    proposals = rng.uniform(_LO, _HI, size=_N_PROP)
    thresh = rng.uniform(0.0, 1.0, size=_N_PROP)
    kernel = np.exp(-0.5 * (proposals - mu) ** 2)
    kept = proposals[thresh < kernel]
    return float(kept.mean())