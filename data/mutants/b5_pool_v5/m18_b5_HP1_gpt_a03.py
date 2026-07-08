"""B5 mutant b5_HP1 gpt/3."""
import numpy as np

_SEED = 42
_LO, _HI = -3.0, 3.0


def _n_prop() -> int:
    return 50


def program(x) -> float:
    x = float(x)
    mu = 4.0 * x - 2.0
    n = _n_prop()
    rng = np.random.default_rng(_SEED)
    props = rng.uniform(_LO, _HI, n)
    us = rng.uniform(0.0, 1.0, n)
    accept = us < np.exp(-0.5 * (props - mu) ** 2)
    return float(np.mean(props[accept]))