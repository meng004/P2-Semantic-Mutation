"""v5 held-out MR — set 1 (gemini-3.5-flash), c1 MP1, candidate 1/3."""
import numpy as np


def r(x):
    # Map x to 1 - x, which corresponds to t -> -t
    return 1.0 - float(x)


def R(y_orig, y_new):
    # Since erf is an odd function, program(x) + program(1-x) should be approximately 0.
    # We use a tolerance of 0.08 to account for the GPR approximation error on the random training set.
    return abs(y_orig + y_new) < 0.08
