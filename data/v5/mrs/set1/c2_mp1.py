"""v5 held-out MR — set 1 (gemini-3.5-flash), c2 MP1, candidate 1/3."""
import math


def r(x):
    # Maps x in [0,1] to 1 - x, which reflects the input around the symmetry point 0.5
    return 1.0 - float(x)


def R(y_orig, y_new):
    # Since the model approximates the odd function tanh(t) centered at x=0.5,
    # the outputs should satisfy y_orig ≈ -y_new (conservation of odd symmetry).
    return math.isclose(y_orig, -y_new, abs_tol=0.08)
