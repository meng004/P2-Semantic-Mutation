"""B2: MCMC Metropolis-Hastings — chain mean tracking target (scalar x∈[0,1] interface).

Library: numpy.random (numpy 2.4.4)
URL: https://numpy.org/doc/stable/reference/random/index.html

program(x) where x ∈ [0,1] scalar.
x → target mean μ = 4x − 2 (range [−2, 2]).
Runs MH targeting N(μ,1) from x0=0, n_steps=2000, warmup=500, proposal_std=0.5.
Returns post-warmup chain mean. Monotone: x↑ → μ↑ → chain mean↑.
"""
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
        u = rng.uniform()
        if np.log(u) > log_ratio:
            current = proposal
        if i >= _WARMUP:
            samples.append(current)
    return float(np.mean(samples))