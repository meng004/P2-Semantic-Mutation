import numpy as np

_N_SAMPLES = 5000
_SEED = 42
_rng_samples = np.random.default_rng(_SEED).uniform(0.0, 1.0, _N_SAMPLES)


def program(x) -> float:
    x = float(x)
    integrand_values = x + _rng_samples**3
    estimate = np.mean(integrand_values)
    return float(estimate)