from p2.avp.interface import AVPResult, MR
from p2.avp.repeat import call_avp_repeated


def _det_pass(x):
    return float(x)


def test_majority_vote_pass_when_all_pass():
    # Identity transform + equality relation: program(x) == program(r(x)) holds.
    mr = MR(r=lambda x: float(x), R=lambda a, b: a == b,
            mp_index=1, name="t")
    result = call_avp_repeated(_det_pass, mr, epsilon=1e-6, repeats=10)
    assert result == AVPResult.PASS


def test_majority_vote_fail_when_majority_fail():
    # Doubling program with a relation expecting an "output unchanged" property
    # under a +1 input shift. f(x)=2x sends r(x)=x+1 to 2x+2, which is NOT
    # equal to the original 2x, so the relation deterministically fails.
    mr = MR(r=lambda x: x + 1.0,
            R=lambda y_orig, y_new: abs(y_new - y_orig) < 1e-9,
            mp_index=1, name="t")
    result = call_avp_repeated(lambda x: 2.0 * float(x), mr,
                               epsilon=1e-6, repeats=10)
    assert result == AVPResult.FAIL


def test_repeats_le_one_falls_back_to_single_call():
    mr = MR(r=lambda x: float(x), R=lambda a, b: a == b,
            mp_index=1, name="t")
    assert call_avp_repeated(_det_pass, mr, epsilon=1e-6, repeats=1) == AVPResult.PASS
    assert call_avp_repeated(_det_pass, mr, epsilon=1e-6, repeats=0) == AVPResult.PASS


def test_all_exceptions_yields_fail():
    # MR with an unknown mp_index raises in dispatcher; every repeat is counted
    # as a failed attempt; n_total stays 0 -> FAIL.
    mr = MR(r=lambda x: x, R=lambda a, b: True, mp_index=999, name="bad")
    assert call_avp_repeated(_det_pass, mr, epsilon=1e-6, repeats=5) == AVPResult.FAIL
