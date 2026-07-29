"""v5 held-out MR — set 1 (gemini-3.5-flash), c1 MP4, candidate 1/3."""
def r(x):
    # Since the GPR model is trained on random data and fits a strictly
    # monotonic function (erf), there are no non-trivial exact invariances.
    # We use the identity transform as the admissible last resort.
    return x


def R(y_orig, y_new):
    return abs(y_orig - y_new) <= 1e-6
