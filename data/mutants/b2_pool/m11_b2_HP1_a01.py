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
    post_warmup = []
    effective_std = _PROPOSAL_STD / 10.0
    for step in range(_N_STEPS):
        noise = rng.standard_normal()
        candidate = current + effective_std * noise
        delta = (candidate - mu) ** 2 - (current - mu) ** 2
        log_alpha = -0.5 * delta
        u = rng.uniform()
        if np.log(u) < log_alpha:
            current = candidate
        if step >= _WARMUP:
            post_warmup.append(current)
    return float(np.mean(post_warmup))