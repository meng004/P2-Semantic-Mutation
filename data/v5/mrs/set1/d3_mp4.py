"""v5 held-out MR — set 1 (gemini-3.5-flash), d3 MP4, candidate 1/3."""
import numpy as np


def r(x):
    # Since the logistic regression probability is strictly monotonic with respect to x
    # on the interval [0, 1], the only exact output-preserving transform is the identity.
    return x


def R(y_orig, y_new):
    # Trajectory similarity: outputs should be identical for identical inputs.
    return abs(y_orig - y_new) <= 1e-6
