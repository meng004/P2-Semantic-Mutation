"""v5 held-out MR — set 1 (gemini-3.5-flash), b1 MP1, candidate 1/3."""
# B1: Beta-Binomial conjugate — posterior mean (scalar x∈[0,1] interface).
import numpy as np


def r(x):
    # Map x to its complement 1 - x
    return 1.0 - x


def R(y_orig, y_new):
    # Conservation of total probability/mean: the sum of posterior means
    # for x and 1 - x must equal 1.0.
    return np.isclose(y_orig + y_new, 1.0, atol=1e-9)
