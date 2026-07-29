"""v5 held-out MR — set 1 (gemini-3.5-flash), a1 MP1, candidate 1/3."""
import numpy as np

def r(x):
    # Perturb x slightly while staying within the [0, 1] domain
    if x < 0.5:
        return x + 1e-6
    else:
        return x - 1e-6


def R(y_orig, y_new):
    # The L2 norm of the final state must remain conserved within a tight tolerance
    return abs(y_orig - y_new) < 1e-3
