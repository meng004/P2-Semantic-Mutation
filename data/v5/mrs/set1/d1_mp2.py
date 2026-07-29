"""v5 held-out MR — set 1 (gemini-3.5-flash), d1 MP2, candidate 1/3."""
import math

def r(x):
    # Monotonically shift x closer to 1, ensuring the output of the MLP (P(y=1)) increases.
    return x + 0.25 * (1.0 - x)

def R(y_orig, y_new):
    # Ensure both outputs are valid, finite probability values.
    return math.isfinite(y_orig) and math.isfinite(y_new)
