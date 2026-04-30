import numpy as np

_N_STEPS = 2000
_WARMUP = 500
_PROPOSAL_STD = 0.5
_SEED = 42


def program(x) -> float:
    x = float(x)
    mu = 4.0 * x - 2.0
    rng = np.random.default_rng(_SEED)
    current = 0.0
    kept = []
    for i in range(_N_STEPS):
        z = rng.standard_normal()
        proposal = current + _PROPOSAL_STD * z
        delta = (proposal - mu) * (proposal - mu) - (current - mu) * (current - mu)
        accept_ratio = np.exp(-0.5 * delta)
        u = rng.uniform()
        accepted = bool(u > accept_ratio)
        if accepted:
            current = proposal
        if not (i < _WARMUP):
            kept.append(current)
    return float(np.mean(np.asarray(kept)))