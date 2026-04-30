import numpy as np

_N_STEPS = 2000
_WARMUP = 500
_PROPOSAL_STD = 0.5
_SEED = 42


def _propose(curr, std, rng):
    return curr + std * rng.standard_normal()


def _log_ratio(prop, curr, mu):
    a = (prop - mu) ** 2
    b = (curr - mu) ** 2
    return 0.5 * (b - a)


def program(x) -> float:
    x = float(x)
    mu = 4.0 * x - 2.0
    rng = np.random.default_rng(_SEED)
    current = 0.0
    trace = []
    for i in range(_N_STEPS):
        proposal = _propose(current, _PROPOSAL_STD, rng)
        lr = _log_ratio(proposal, current, mu)
        accept_ratio = np.exp(min(0.0, lr)) if lr < 0 else 1.0
        u = float(rng.uniform())
        if u > accept_ratio:
            current = proposal
        if i >= _WARMUP:
            trace.append(current)
    return float(np.mean(trace))