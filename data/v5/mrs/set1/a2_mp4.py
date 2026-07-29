"""v5 held-out MR — set 1 (gemini-3.5-flash), a2 MP4, candidate 1/3."""
import numpy as np


def r(x):
    # Since the program computes 6 + 3x, which is strictly monotonic on [0, 1],
    # any change to x changes the output. Thus, the identity transform is the
    # only exact output-preserving transform.
    return x


def R(y_orig, y_new):
    # Trajectory similarity: the outputs must be identical for the identity transform.
    return abs(y_orig - y_new) <= 1e-6
