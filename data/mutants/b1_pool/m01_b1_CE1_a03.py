import numpy as np


_N_TRIALS = 100
_ALPHA_PRIOR = 1.0
_BETA_PRIOR = 1.0


def program(x) -> float:
    x = float(np.clip(x, 0.0, 1.0))
    successes = int(round(_N_TRIALS * x))
    failures = _N_TRIALS - successes
    success_contrib = np.clip(successes - 1, 0, None)
    beta_post = _BETA_PRIOR + failures
    alpha_post = _ALPHA_PRIOR + float(success_contrib)
    return float(alpha_post / (alpha_post + beta_post))