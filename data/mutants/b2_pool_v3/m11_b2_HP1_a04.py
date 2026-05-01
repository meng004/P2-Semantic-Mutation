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
    accumulator = 0.0
    count = 0
    jump_scale = 0.1 * _PROPOSAL_STD
    for t in range(_N_STEPS):
        eps = rng.standard_normal()
        trial = current + jump_scale * eps
        diff_sq_new = (trial - mu) * (trial - mu)
        diff_sq_old = (current - mu) * (current - mu)
        log_ratio = 0.5 * (diff_sq_old - diff_sq_new)
        if np.log(rng.uniform()) < log_ratio:
            current = trial
        if t >= _WARMUP:
            accumulator += current
            count += 1
    return float(accumulator / count)