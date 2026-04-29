from p2.avp.interface import MR, AVPResult
from p2.lrca.killed import is_killed


def test_killed_when_any_mr_distinguishes():
    s = lambda x: x
    sm = lambda x: -x  # anti-monotonic: breaks the monotonicity MR
    mr_set = [
        MR(r=lambda x: x + 1, R=lambda yo, yn: yn > yo, mp_index=2, name="mono"),
    ]
    assert is_killed(s, sm, mr_set, epsilon=0.05) is True


def test_not_killed_when_all_mr_agree():
    s = lambda x: x
    sm = lambda x: x  # identical
    mr_set = [MR(r=lambda x: x, R=lambda a, b: True, mp_index=1, name="m")]
    assert is_killed(s, sm, mr_set, epsilon=1e-6) is False
