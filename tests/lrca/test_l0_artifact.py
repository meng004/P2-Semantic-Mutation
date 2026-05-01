from p2.lrca.l0_artifact import classify_l0, L0Label


def test_nan_output_classified_as_artifact():
    def m(x): return float("nan")
    assert classify_l0(m, n_samples=20) == L0Label.NAN_OUTPUT


def test_inf_output_classified_as_artifact():
    def m(x): return float("inf")
    assert classify_l0(m, n_samples=20) == L0Label.INF_OUTPUT


def test_constant_output_classified_as_artifact():
    def m(x): return 0.0
    assert classify_l0(m, n_samples=20) == L0Label.CONSTANT_OUTPUT


def test_identity_to_orig_classified_as_artifact():
    def orig(x): return float(x) * 2.0
    def m(x):    return float(x) * 2.0
    assert classify_l0(m, n_samples=20, original=orig) == L0Label.IDENTICAL_TO_ORIG


def test_legit_mutant_classified_as_legit():
    def orig(x): return float(x) * 2.0
    def m(x):    return float(x) * 2.0 + 0.5
    assert classify_l0(m, n_samples=20, original=orig) == L0Label.LEGIT
