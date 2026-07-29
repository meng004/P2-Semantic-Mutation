"""v5 held-out MR — set 2 (grok-4.5), b2 MP5, candidate 1/3."""
import numpy as np

def r(x):
    x = float(x)
    return 0.5 * x + 0.5

def R(y_orig, y_new):
    return np.isfinite(y_orig) and np.isfinite(y_new)
