# Mutant: cosmetic refactor — identical logic, same seed, same constants.
# Expected: EQUIV. Outputs bit-identical to original program.
import numpy as np


def program(x) -> float:
    x = float(x)
    mu = float(4 * x) - 2.0  # cosmetic: 4*x cast order differs, result same
    rng = np.random.default_rng(42)
    current = 0.0
    accepted = []
    for step in range(2000):
        candidate = current + 0.5 * rng.standard_normal()
        log_a = -0.5 * ((candidate - mu) ** 2 - (current - mu) ** 2)
        if np.log(rng.uniform()) < log_a:
            current = candidate
        if step >= 500:
            accepted.append(current)
    return float(np.mean(accepted))
