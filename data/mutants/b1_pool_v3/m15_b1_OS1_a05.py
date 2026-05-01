import numpy as np


_N_TRIALS = 100
_ALPHA_PRIOR = 1.0
_BETA_PRIOR = 1.0


class _PosteriorState:
    def __init__(self, x_val):
        self.x = x_val
        self.successes = round(_N_TRIALS * x_val)
        self.failures = _N_TRIALS - self.successes

    @property
    def alpha(self):
        return _ALPHA_PRIOR + self.successes

    @property
    def beta(self):
        return _BETA_PRIOR + self.failures

    def total(self):
        accumulator = 0.0
        for component in (self.alpha, self.beta):
            accumulator += component
        return accumulator


def program(x) -> float:
    x_safe = float(np.clip(x, 0.0, 1.0))
    state = _PosteriorState(x_safe)
    numerator_for_mean = state.beta
    denominator_for_mean = state.total()
    return float(numerator_for_mean / denominator_for_mean)