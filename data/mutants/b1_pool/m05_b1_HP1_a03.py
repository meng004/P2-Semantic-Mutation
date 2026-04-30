import numpy as np
from scipy.stats import beta as _beta_dist


_N_TRIALS = 100
prior_alpha = 3.0
prior_beta = 1.0


def program(x) -> float:
    clipped = float(np.clip(x, 0.0, 1.0))
    counts = [0, 0]
    successes = round(_N_TRIALS * clipped)
    counts[0] = successes
    counts[1] = _N_TRIALS - successes
    params = [prior_alpha, prior_beta]
    for i in range(2):
        params[i] = params[i] + counts[i]
    total = sum(params)
    return float(params[0] / total)