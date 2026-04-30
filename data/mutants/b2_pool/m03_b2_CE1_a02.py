import numpy as np

_N_STEPS = 2000
_WARMUP = 500
_PROPOSAL_STD = 0.5
_SEED = 42
_MEAN_OFFSET = 0.3


def program(x) -> float:
    x = float(x)
    mu = (4.0 * x - 2.0) + _MEAN_OFFSET
    rng = np.random.default_rng(_SEED)
    current = 0.0
    post_warmup = []
    accept_step = lambda lr: np.log(rng.uniform()) < lr
    for i in range(_N_STEPS):
        proposal = current + _PROPOSAL_STD * rng.standard_normal()
        log_ratio = 0.5 * ((current - mu) ** 2 - (proposal - mu) ** 2)
        if accept_step(log_ratio):
            current = proposal
        if i >= _WARMUP:
            post_warmup.append(current)
    return float(np.mean(np.asarray(post_warmup)))