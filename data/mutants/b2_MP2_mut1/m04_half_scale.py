# Mutant: halve the mu scale → mu = 2x - 1.
# Expected: SURVIVE. r_mp2 shifts x by 0.05 → delta_mu = 0.1 > 0; Wilcoxon PASS.
import numpy as np

_N_STEPS = 2000
_WARMUP = 500
_PROPOSAL_STD = 0.5
_SEED = 42


def program(x) -> float:
    x = float(x)
    mu = 2.0 * x - 1.0  # halved scale: range [-1, 1] instead of [-2, 2]
    rng = np.random.default_rng(_SEED)
    current = 0.0
    samples = []
    for i in range(_N_STEPS):
        proposal = current + _PROPOSAL_STD * rng.standard_normal()
        log_ratio = -0.5 * ((proposal - mu) ** 2 - (current - mu) ** 2)
        if np.log(rng.uniform()) < log_ratio:
            current = proposal
        if i >= _WARMUP:
            samples.append(current)
    return float(np.mean(samples))
