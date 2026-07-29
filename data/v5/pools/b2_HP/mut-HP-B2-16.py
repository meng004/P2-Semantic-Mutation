import numpy as np

_N_STEPS = 2000
_WARMUP = 500
_PROPOSAL_STD = 4.25  # Mutated: scaled proposal step size by ~8.5x
_SEED = 42


def program(x) -> float:
    x = float(x)
    mu = 4.0 * x - 2.0
    rng = np.random.default_rng(_SEED)
    current = 0.0
    samples = []
    for i in range(_N_STEPS):
        proposal = current + _PROPOSAL_STD * rng.standard_normal()
        log_ratio = -0.5*((proposal-mu)**2 - (current-mu)**2)
        if np.log(rng.uniform()) < log_ratio:
            current = proposal
        if i >= _WARMUP:
            samples.append(current)
    return float(np.mean(samples))