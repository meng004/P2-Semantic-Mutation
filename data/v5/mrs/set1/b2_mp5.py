"""v5 held-out MR — set 1 (gemini-3.5-flash), b2 MP5, candidate 1/3."""
import numpy as np


def r(x):
    # Move x towards the asymptotic upper limit of 1.0,
    # which systematically increases the target mean mu.
    return float(x + 0.2 * (1.0 - x))


def R(y_orig, y_new):
    # The output (chain mean) should increase.
    return y_new > y_orig
