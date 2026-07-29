"""v5 held-out MR — set 2 (grok-4.5), b1 MP2, candidate 1/3."""
import numpy as np

def r(x):
    x = float(np.clip(x, 0.0, 1.0))
    return float((x + 1.0) / 2.0)

def R(y_orig, y_new):
    if not (np.isfinite(y_orig) and np.isfinite(y_new)):
        return False
    return True
