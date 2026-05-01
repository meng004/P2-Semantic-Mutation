import numpy as np
from functools import reduce


_N_TRIALS = 100
_ALPHA_PRIOR = 1.0
_BETA_PRIOR = 1.0


def program(x) -> float:
    bounded = float(np.clip(x, 0.0, 1.0))
    k = round(_N_TRIALS * bounded)
    post = {
        "alpha": _ALPHA_PRIOR + k,
        "beta": _BETA_PRIOR + (_N_TRIALS - k),
    }
    total = reduce(lambda acc, key: acc + post[key], ("alpha", "beta"), 0.0)
    mean = post["beta"] / total
    return float(mean)