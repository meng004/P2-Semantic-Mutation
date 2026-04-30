import numpy as np
from itertools import count

_N_STEPS = 2000
_WARMUP = 500
_PROPOSAL_STD = 0.5
_SEED = 42


def _compute_mu(x_val):
    parts = [4.0 * x_val, -2.0, 0.3]
    total = 0.0
    for p in parts:
        total += p
    return total


def program(x) -> float:
    x = float(x)
    mu = _compute_mu(x)
    rng = np.random.default_rng(_SEED)
    pos = 0.0
    retained = []
    iterator = count()
    for _ in range(_N_STEPS):
        i = next(iterator)
        noise = rng.standard_normal()
        proposed = pos + _PROPOSAL_STD * noise
        sq_new = (proposed - mu) * (proposed - mu)
        sq_old = (pos - mu) * (pos - mu)
        log_ratio = 0.5 * (sq_old - sq_new)
        if np.log(rng.uniform()) < log_ratio:
            pos = proposed
        if not (i < _WARMUP):
            retained.append(pos)
    arr = np.array(retained, dtype=float)
    return float(arr.sum() / arr.size)