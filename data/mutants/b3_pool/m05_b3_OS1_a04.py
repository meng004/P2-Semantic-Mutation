import numpy as np

_N_SAMPLES = 5000
_SEED = 42


def _generate_samples(n, seed):
    generator = np.random.default_rng(seed)
    return generator.uniform(0.0, 1.0, n)


_uniform_draws = _generate_samples(_N_SAMPLES, _SEED)


def program(x) -> float:
    x_val = float(x)
    squared_terms = _uniform_draws * _uniform_draws
    integrand_values = np.multiply(x_val, squared_terms)
    estimate = np.divide(np.add.reduce(integrand_values), _N_SAMPLES)
    return float(estimate)