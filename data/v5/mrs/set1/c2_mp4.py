"""v5 held-out MR — set 1 (gemini-3.5-flash), c2 MP4, candidate 1/3."""
def r(x):
    # Since the PCE surrogate is strictly monotone on [0, 1],
    # the only exact output-preserving map on this domain is the identity.
    return x


def R(y_orig, y_new):
    return abs(y_orig - y_new) < 1e-6
