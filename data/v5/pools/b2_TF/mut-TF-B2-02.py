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
    samples = []
    warmup_samples = []
    for i in range(_N_STEPS):
        proposal = current + _PROPOSAL_STD * rng.standard_normal()
        log_ratio = -0.5*((proposal-mu)**2 - (current-mu)**2)
        if np.log(rng.uniform()) < log_ratio:
            current = proposal
        if i < _WARMUP:
            warmup_samples.append(current)
        else:
            samples.append(current)
    # Reverse the warm-up samples and include them in the averaging
    warmup_samples.reverse()
    all_samples = warmup_samples + samples
    return float(np.mean(all_samples))