"""v5 held-out MR — set 1 (gemini-3.5-flash), d3 MP2, candidate 1/3."""
def r(x):
    # Maps x in [0, 1] to (x + 1) / 2, which is strictly greater than x for x < 1
    return (x + 1.0) / 2.0


def R(y_orig, y_new):
    # For a monotonically increasing function, y_new should be >= y_orig
    return y_new >= y_orig
