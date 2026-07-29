"""v5 held-out MR — set 1 (gemini-3.5-flash), d3 MP5, candidate 1/3."""
import math
import numpy as np


def r(x):
    # Maps x in [0, 1] to [0.5, 1.0], moving it towards the asymptotic regime of 1.0
    # where the logistic regression prediction probability for class 1 increases.
    return 0.5 * x + 0.5


def R(y_orig, y_new):
    # Gates validity of the outputs (both must be valid probabilities in [0, 1])
    return 0.0 <= y_orig <= 1.0 and 0.0 <= y_new <= 1.0
