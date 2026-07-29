"""v5 held-out MR — set 1 (gemini-3.5-flash), c3 MP1, candidate 1/3."""
import numpy as np


def r(x):
    return 1.0 - float(x)


def R(y_orig, y_new):
    # Conservation of the sum of sigmoid-like outputs:
    # program(x) + program(1-x) should be approximately 1.0
    return abs(y_orig + y_new - 1.0) < 0.08
