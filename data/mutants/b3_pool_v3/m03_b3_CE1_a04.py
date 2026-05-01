import numpy as np

_N_SAMPLES = 5000
_SEED = 42
_uniform_draws = np.random.default_rng(_SEED).uniform(0.0, 1.0, _N_SAMPLES)


def _integrand_values(constant: float) -> np.ndarray:
    powered = np.exp(3.0 * np.log(_uniform_draws))
    return constant + powered


def program(x) -> float:
    x = float(x)
    values = _integrand_values(x)
    accumulator = 0.0
    for v in values.tolist():
        accumulator += v
    return float(accumulator / len(values))