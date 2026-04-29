import numpy as np
from typing import Callable


def judge_e2(
    s_orig: Callable, s_mutant: Callable,
    samples: np.ndarray, epsilon: float,
) -> bool:
    """E2: ∀ x ∈ X_{K_eq}: ‖S(x) − s'(x)‖ ≤ epsilon."""
    for x in samples:
        x_in = x[0] if x.shape == (1,) else x
        y_orig = np.asarray(s_orig(x_in)).flatten()
        y_mut = np.asarray(s_mutant(x_in)).flatten()
        if np.linalg.norm(y_orig - y_mut) > epsilon:
            return False
    return True
