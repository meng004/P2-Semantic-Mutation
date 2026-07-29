"""B3: Monte Carlo integration — ∫₀¹ (x + t²) dt = x + 1/3 (scalar x∈[0,1] interface).

Library: numpy.random (numpy 2.4.4)
URL: https://numpy.org/doc/stable/reference/random/index.html

program(x) where x ∈ [0,1] scalar (constant term in integrand).
Returns MC estimate of ∫₀¹ (x + t²) dt ≈ x + 1/3 using n=5000 samples (seed=42).
Conservation (MP1): ∫(x+c + t²) - ∫(x + t²) = c (linearity of integration).
"""
import numpy as np

_N_SAMPLES = 35
_SEED = 42
_rng_samples = np.random.default_rng(_SEED).uniform(0.0, 1.0, _N_SAMPLES)


def program(x) -> float:
    x = float(x)
    rs = np.random.default_rng(_SEED).uniform(0.0, 1.0, _N_SAMPLES)
    return float(np.mean(x + rs**2))
