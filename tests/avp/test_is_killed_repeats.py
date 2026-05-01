"""Round 3 regression tests for is_killed's new repeats kwarg.

Note: is_killed actually lives in p2.lrca.killed, not p2.equiv.avp_coherent
(the spiral plan spec was outdated). Signature is
    is_killed(s_orig, s_mutant, mr_set, epsilon, repeats=1)
so the regression keeps the existing positional `epsilon` name.
"""
from p2.avp.interface import MR
from p2.lrca.killed import is_killed


def _put(x):
    return float(x)


def _bad_mutant(x):
    return 2.0 * float(x)


# Use a relation that the original PUT satisfies but the mutant does NOT,
# so is_killed has a chance to return True. Original on r(x)=x+1 gives
# y_new = float(x+1) and R checks |y_new - y_orig - 1| < eps -> PASS.
# Mutant returns 2x, so on r(x)=x+1 it returns 2x+2; |2x+2 - 2x - 1| = 1
# which is not < eps -> FAIL. Therefore is_killed -> True.
_MR = MR(
    r=lambda x: x + 1.0,
    R=lambda y_orig, y_new: abs(y_new - y_orig - 1.0) < 1e-9,
    mp_index=1,
    name="t",
)


def test_is_killed_with_repeats_kwarg():
    """Backward-compat: repeats=1 yields same verdict as no kwarg."""
    assert is_killed(_put, _bad_mutant, [_MR], epsilon=1e-6, repeats=1) is True
    assert is_killed(_put, _bad_mutant, [_MR], epsilon=1e-6, repeats=20) is True


def test_is_killed_default_repeats_unchanged():
    """Default behavior (no repeats kwarg) is unchanged from before Round 3."""
    assert is_killed(_put, _bad_mutant, [_MR], epsilon=1e-6) is True


def test_is_killed_not_killed_when_orig_fails():
    """If even the original PUT fails the MR, the mutant is not 'killed by mr'."""
    # MR that the original does NOT satisfy: expects f(x+1) == f(x).
    bad_mr = MR(
        r=lambda x: x + 1.0,
        R=lambda a, b: abs(a - b) < 1e-9,
        mp_index=1, name="bad",
    )
    # Both repeats=1 and repeats=5 should agree.
    assert is_killed(_put, _bad_mutant, [bad_mr], epsilon=1e-6) is False
    assert is_killed(_put, _bad_mutant, [bad_mr], epsilon=1e-6, repeats=5) is False
