import numpy as np

_N_STEPS = 2000
_WARMUP = 500
_PROPOSAL_STD = 0.5
_SEED = 42


def _scaled_sigma():
    return _PROPOSAL_STD * 1e-1


def program(x) -> float:
    x = float(x)
    mu = 4.0 * x - 2.0
    rng = np.random.default_rng(_SEED)
    chain = [0.0]
    step_size = _scaled_sigma()
    i = 0
    while i < _N_STEPS:
        cur = chain[-1]
        prop = cur + step_size * rng.standard_normal()
        log_r = 0.5 * ((cur - mu) ** 2 - (prop - mu) ** 2)
        accept = np.log(rng.uniform()) < log_r
        chain.append(prop if accept else cur)
        i += 1
    tail = chain[1 + _WARMUP:]
    return float(np.mean(tail))