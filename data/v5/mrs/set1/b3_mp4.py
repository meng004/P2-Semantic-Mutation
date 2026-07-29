"""v5 held-out MR — set 1 (gemini-3.5-flash), b3 MP4, candidate 1/3."""
def r(x):
    # Since program(x) = x + constant is strictly monotonic,
    # the only exact output-preserving transform is the identity.
    return x


def R(y_orig, y_new) -> bool:
    return abs(y_orig - y_new) <= 1e-6
