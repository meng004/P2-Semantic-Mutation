"""B2: MCMC Metropolis-Hastings sampler.

Library: numpy.random (numpy 2.4.4) — classic MH algorithm.
URL: https://numpy.org/doc/stable/reference/random/index.html

Reference: Metropolis et al. (1953), Hastings (1970).
Algorithm: https://en.wikipedia.org/wiki/Metropolis–Hastings_algorithm

program(x) where x = [x0, log_sigma] (initial state, log of proposal std).
Target distribution: standard normal N(0,1).
Fixed: n_steps=2000, seed derived from x0 for determinism.
Returns: sample mean of post-warmup chain (warmup = 500 steps).
"""
import numpy as np

_N_STEPS = 2000
_WARMUP = 500


def _log_target(z: float) -> float:
    return -0.5 * z**2  # log N(0,1) up to constant


def program(x: np.ndarray) -> float:
    """Run Metropolis-Hastings from x0 with proposal std exp(log_sigma); return chain mean."""
    x = np.asarray(x, dtype=float)
    x0, log_sigma = float(x[0]), float(x[1])
    proposal_std = np.exp(np.clip(log_sigma, -5.0, 5.0))
    rng = np.random.default_rng(seed=int(abs(x0 * 1e6)) % (2**31))
    current = x0
    log_p_current = _log_target(current)
    samples = []
    for i in range(_N_STEPS):
        proposal = current + proposal_std * rng.standard_normal()
        log_p_proposal = _log_target(proposal)
        if np.log(rng.uniform()) < log_p_proposal - log_p_current:
            current = proposal
            log_p_current = log_p_proposal
        if i >= _WARMUP:
            samples.append(current)
    return float(np.mean(samples))
