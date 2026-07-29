"""v5 held-out MR — set 1 (gemini-3.5-flash), b2 MP1, candidate 1/3."""
import numpy as np


def r(x):
    return 1.0 - float(x)


def R(y_orig, y_new):
    return abs(y_orig + y_new) < 0.6
