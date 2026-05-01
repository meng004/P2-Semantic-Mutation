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
    center = (x * 4.0 - 2.0) + 0.3
    rng = np.random.default_rng(_SEED)
    state = 0.0
    kept = []
    for step in range(_N_STEPS):
        candidate = state + rng.standard_normal() * _PROPOSAL_STD
        delta = (candidate - center) ** 2 - (state - center) ** 2
        if np.log(rng.uniform()) < (-0.5 * delta):
            state = candidate
        if step >= _WARMUP:
            kept.append(state)
    return float(np.mean(kept))