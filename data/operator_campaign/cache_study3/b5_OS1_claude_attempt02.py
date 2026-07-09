"""B5 rejection sampler (mutant, helper target mean)."""
import numpy as np

_SEED = 42
_N_PROP = 6000
_BOUNDS = (-3.0, 3.0)


def _target_mean(x):
    return 4.0 * x - 2.0


def program(x) -> float:
    x = float(x)
    mu = _target_mean(x)
    rng = np.random.default_rng(_SEED)
    lo, hi = _BOUNDS
    props = rng.uniform(lo, hi, _N_PROP)
    us = rng.uniform(0.0, 1.0, _N_PROP)
    weight = np.exp(-0.5 * (props + mu) ** 2)
    return float(np.mean(props[us < weight]))