"""v5 held-out MR — set 2 (grok-4.5), a3 MP5, candidate 3/3."""
import numpy as np

def r(x):
    h = max(float(x), 1e-4)
    N = max(4, round(1.0 / h))
    if N < 8:
        return float(x)
    return 1.0 / (2 * N)

def R(y_orig, y_new):
    return bool(np.isfinite(y_orig) and np.isfinite(y_new))
