import numpy as np

_N_STEPS = 2000
_WARMUP = 500
_PROPOSAL_STD = 0.5
_SEED = 42


def _target_mean(x: float) -> float:
    base = 4.0 * x - 2.0
    shift = 0.3
    return base + shift


def program(x) -> float:
    x = float(x)
    mu = _target_mean(x)
    rng = np.random.default_rng(_SEED)
    state = 0.0
    chain = []
    for step in range(_N_STEPS):
        candidate = state + _PROPOSAL_STD * rng.standard_normal()
        delta = (candidate - mu) ** 2 - (state - mu) ** 2
        log_alpha = -0.5 * delta
        u = rng.uniform()
        if np.log(u) < log_alpha:
            state = candidate
        if step >= _WARMUP:
            chain.append(state)
    return float(np.mean(chain))