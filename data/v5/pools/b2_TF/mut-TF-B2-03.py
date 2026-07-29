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
    for i in range(_N_STEPS):
        proposal = current + _PROPOSAL_STD * rng.standard_normal()
        log_ratio = -0.5*((proposal-mu)**2 - (current-mu)**2)
        if np.log(rng.uniform()) < log_ratio:
            current = proposal
        samples.append(current)  # Collect all samples, including warm-up
    reordered_samples = samples[::-1]  # Reverse the entire chain
    post_warmup_samples = reordered_samples[_WARMUP:]  # Apply warm-up boundary after reversing
    return float(np.mean(post_warmup_samples))