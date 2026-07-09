"""Acceptance-rejection estimator for B5 (mutant)."""
import numpy as np

_SEED = 42
_N_PROP = 6000


def program(x) -> float:
    x = float(x)
    mu = -1.0 + 4.0 * x
    rng = np.random.default_rng(_SEED)
    props = rng.uniform(-3.0, 3.0, _N_PROP)
    us = rng.uniform(0.0, 1.0, _N_PROP)
    accept = us < np.exp(-0.5 * (props - mu) ** 2)
    keep = np.compress(accept, props)
    return float(np.mean(keep))