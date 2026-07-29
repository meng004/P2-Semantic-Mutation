"""v5 held-out MR — set 1 (gemini-3.5-flash), b3 MP2, candidate 1/3."""
import numpy as np


def r(x):
    return 0.5 * float(x) + 0.5


def R(y_orig, y_new):
    return (
        np.isfinite(y_orig)
        and np.isfinite(y_new)
        and float(y_new) > float(y_orig)
    )
