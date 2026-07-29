"""v5 held-out MR — set 2 (grok-4.5), a2 MP1, candidate 1/3."""
import numpy as np

def r(x):
    return 1.0 - float(x)

def R(y_orig, y_new):
    return bool(np.isclose(y_orig + y_new, 15.0, rtol=1e-9, atol=1e-9))
