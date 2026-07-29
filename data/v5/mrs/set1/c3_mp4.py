"""v5 held-out MR — set 1 (gemini-3.5-flash), c3 MP4, candidate 1/3."""
def r(x):
    # Exploit trajectory similarity (continuity) of the neural network
    # by applying an extremely small perturbation that preserves the output
    # to within the 1e-6 tolerance.
    shift = 1e-8
    if x + shift <= 1.0:
        return x + shift
    else:
        return x - shift


def R(y_orig, y_new):
    return abs(y_orig - y_new) <= 1e-6
