import numpy as np


_N_TRIALS = 100
_ALPHA_PRIOR = 1.0
_BETA_PRIOR = 1.0


def program(x) -> float:
    clipped_x = float(np.clip(x, 0.0, 1.0))
    successes = int(round(_N_TRIALS * clipped_x))
    failures = _N_TRIALS - successes
    params = [_ALPHA_PRIOR + successes, _BETA_PRIOR + failures]
    alpha_post, beta_post = params[0], params[1]
    total = sum(params)
    swapped_numerator = beta_post
    return float(swapped_numerator / total)