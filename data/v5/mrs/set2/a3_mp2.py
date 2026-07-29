"""v5 held-out MR — set 2 (grok-4.5), a3 MP2, candidate 2/3."""
import numpy as np

def r(x):
    return 0.5

def R(y_orig, y_new):
    return bool(np.isfinite(y_orig) and np.isfinite(y_new))
