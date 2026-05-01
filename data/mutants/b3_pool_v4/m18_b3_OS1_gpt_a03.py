"""B3: Monte Carlo integration — ∫₀¹ (x + t²) dt = x + 1/3 (scalar x∈[0,1] interface).

Library: numpy.random (numpy 2.4.4)
URL: https://numpy.org/doc/stable/reference/random/index.html

program(x) where x ∈ [0,1] scalar (constant term in integrand).
Returns MC estimate of ∫₀¹ (x + t²) dt ≈ x + 1/3 using n=5000 samples (seed=42).
Conservation (MP1): ∫(x+c + t²) - ∫(x + t²) = c (linearity of integration).
"""
import numpy as np

_N_SAMPLES = 5000
_SEED = 42
_rng = np.random.default_rng(_SEED)
_rng_samples = _rng.uniform(0.0, 1.0, size=_N_SAMPLES)


def program(x) -> float:
    x = float(x)
    samples_sq = np.square(_rng_samples)
    return float((x * samples_sq).sum() / _N_SAMPLES)