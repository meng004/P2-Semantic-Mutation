"""v5 held-out MR — set 2 (grok-4.5), b1 MP5, candidate 1/3."""
import numpy as np

def r(x):
    x = float(np.clip(x, 0.0, 1.0))
    return float(1.0 - 0.1 * (1.0 - x))

def R(y_orig, y_new):
    return bool(np.isfinite(y_orig) and np.isfinite(y_new))
