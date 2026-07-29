"""v5 held-out MR — set 2 (grok-4.5), d3 MP1, candidate 1/3."""
import numpy as np

def r(x):
    return 0.5 * float(x)

def R(y_orig, y_new):
    yo = float(y_orig)
    yn = float(y_new)
    if not (0.0 < yo < 1.0 and 0.0 < yn < 1.0):
        return False
    logit_o = np.log(yo / (1.0 - yo))
    logit_n = np.log(yn / (1.0 - yn))
    return bool(abs(logit_n - 0.5 * logit_o) <= 0.5)
