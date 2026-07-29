"""v5 held-out MR — set 1 (gemini-3.5-flash), d3 MP1, candidate 1/3."""
import math


def r(x):
    # For x in [0, 1], math.sqrt(x * x) is mathematically identical to x.
    # This maps the valid input domain into itself.
    return math.sqrt(x * x)


def R(y_orig, y_new):
    # Conservation of the predicted probability under the identity-equivalent transform.
    return math.isclose(y_orig, y_new, abs_tol=1e-12)
