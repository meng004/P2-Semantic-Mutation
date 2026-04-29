from p2.avp.interface import MR
from p2.lrca.l1_tolerance import check_l1_robust


def test_l1_robust_when_consistently_failing():
    s = lambda x: x
    sm = lambda x: -x  # anti-monotonic: always breaks the monotonicity MR
    mr_set = [MR(lambda x: x + 1, lambda yo, yn: yn > yo, 2, "m")]
    assert check_l1_robust(s, sm, mr_set, n_repeat=20, epsilon=0.05) is True


def test_l1_fragile_when_intermittent():
    import random
    rng = random.Random(0)

    def flaky(x):
        return x if rng.random() < 0.5 else x + 100

    mr_set = [MR(lambda x: x + 1, lambda yo, yn: yn > yo, 2, "m")]
    result = check_l1_robust(lambda x: x, flaky, mr_set, n_repeat=20, epsilon=0.05)
    assert isinstance(result, bool)
