"""Probe an obvious equivalent mutant: identity wrapper."""
import math

from p2.avp.interface import MR
from p2.equiv.diagnosis import probe_equivalence


def _orig(x):
    return float(x) * 2.0


def _identity_wrapper(x):
    return float(x) * 2.0  # exactly equivalent


def test_identity_wrapper_is_recognized_as_equivalent():
    mr = MR(r=lambda x: float(x) + 0.1, R=lambda a, b: True,
            mp_index=1, name="dummy")
    res = probe_equivalence(_orig, _identity_wrapper, mr,
                            cell_id="test", mutant_name="identity",
                            n_samples=100)
    assert res.n_y_identical == res.n_samples
    assert res.diff_max < 1e-12
    assert res.n_exception == 0


def test_nonequivalent_mutant_records_R_fails():
    """Mutant that always disagrees with orig should produce R_fail samples.

    R verdict: equal-within-tol. orig(x)=x, orig(x+0.1)=x+0.1, |diff|=0.1
    -> R returns False on orig. mutant(x)=x+1, mutant(x+0.1)=x+1.1,
    |diff|=0.1 -> R also returns False on mutant. So R agrees. We need an
    asymmetric R-input change: use R that compares to a fixed value via diff.
    Simpler: pick mutant that breaks the relation entirely."""
    # orig(x)=x; mutant(x)=x+1. R: |a-b| < 1e-9. r: x -> x.
    # orig: a=b=x -> R True. mutant: a=x+1, b=x+1 -> R True. Still agrees.
    # Use r(x)=x+0.1 so orig produces (x, x+0.1) -> R False; mutant produces
    # (x+1, x+1.1) -> R False. Agrees again. The R-verdict only differs if
    # the mutant actually changes the structure. Use mutant=lambda x: x*x.
    # orig: (x, x+0.1) -> |0.1| < 1e-9? No -> R False.
    # mutant: (x*x, (x+0.1)**2) -> diff = 0.2x + 0.01, on x in [0,1] this is
    # at least 0.01 -> R False. So R still agrees both False. We need a case
    # where exactly one side passes R. Easiest: r(x)=x (identity) so orig
    # always passes R (a==b), mutant=x+small_random breaks a==b on the second
    # call only -> mutant fails R. But our mutant is deterministic. Use
    # mutant=lambda x: x + (1 if x > 0.5 else 0) so mutant(x) != mutant(r(x))
    # whenever x crosses 0.5. With r(x)=x identity actually a==b for mutant
    # too. So make r non-trivial: r(x)= 1-x (so x and r(x) often straddle 0.5).
    # orig: a=x, b=1-x -> R: |2x-1|<1e-9 -> True only if x≈0.5.
    # mutant: a = x + (1 if x>0.5 else 0), b = (1-x) + (1 if 1-x>0.5 else 0)
    #         = x + [x>0.5], (1-x) + [x<0.5]
    # On x>0.5: a=x+1, b=1-x. diff=2x. R: False (2x > 1).
    # On x<0.5: a=x, b=1-x+1=2-x. diff=2-2x > 1. R: False.
    # On x=0.5: a=0.5, b=0.5. R: True (only orig: True, mutant: True too).
    # So R agrees almost everywhere -> n_R_fail likely 0. Reach for the
    # cleanest construction: an MR whose R inspects orig's outputs only via
    # equality, with r(x)=x and mutant(x)=x+1.
    # r(x)=x -> y_o_orig = x, y_n_orig = x -> R True (equal).
    # y_o_mut = x+1, y_n_mut = x+1 -> R True. Still agrees.
    # Final approach: make R asymmetric in a way the mutant breaks. Use
    # R = lambda a,b: a == b AND a >= 0. With r(x)=-x:
    # orig: a=x>=0, b=-x<=0 -> a==b only at 0; a>=0 True; combined False
    # except x=0. mutant=lambda x: x+1: a=x+1>=1, b=-x+1; equal when x=0.
    # combined False except x=0. Agrees. We need fundamentally different
    # behaviour. Use a mutant that returns a different TYPE-comparable value:
    # mutant = lambda x: x + 0.5. With R=lambda a,b: abs(a-b) < 0.3 and
    # r(x)=x+0.2:
    # orig diffs: |x - (x+0.2)|=0.2 < 0.3 -> True
    # mutant diffs: |(x+0.5) - (x+0.7)|=0.2 < 0.3 -> True
    # agrees. The R verdict depends only on diff structure, which mutant
    # preserves. Use R that depends on MAGNITUDE: R=lambda a,b: a+b < 1.
    # orig: a=x, b=x+0.2 -> sum=2x+0.2 < 1 iff x<0.4.
    # mutant: a=x+0.5, b=x+0.7 -> sum=2x+1.2 < 1 iff x<-0.1 -> always False.
    # On x<0.4: orig True, mutant False -> disagreement!
    # On x>=0.4: orig False, mutant False -> agreement.
    # Sample uniform on [0,1]: ~40% of samples should disagree.
    mr = MR(
        r=lambda x: float(x) + 0.2,
        R=lambda a, b: (float(a) + float(b)) < 1.0,
        mp_index=1, name="sum_lt_1",
    )
    res = probe_equivalence(
        _orig_id := (lambda x: float(x)),
        lambda x: float(x) + 0.5,
        mr, cell_id="test", mutant_name="plus_half",
        n_samples=200,
    )
    assert res.n_R_fail > 0, (
        f"expected disagreements, got n_R_fail={res.n_R_fail}, "
        f"n_R_pass={res.n_R_pass}"
    )
    assert res.n_exception == 0


def test_raising_mutant_recorded_as_exception():
    mr = MR(r=lambda x: float(x) + 0.1, R=lambda a, b: True,
            mp_index=1, name="dummy")
    res = probe_equivalence(
        _orig,
        lambda x: 1 / 0,  # ZeroDivisionError is an ArithmeticError subclass
        mr, cell_id="test", mutant_name="raises",
        n_samples=50,
    )
    assert res.n_exception > 0
    assert res.n_R_pass == 0
    assert res.n_R_fail == 0


def test_all_raises_returns_nan_diffs():
    mr = MR(r=lambda x: float(x) + 0.1, R=lambda a, b: True,
            mp_index=1, name="dummy")
    res = probe_equivalence(
        _orig,
        lambda x: 1 / 0,
        mr, cell_id="test", mutant_name="raises",
        n_samples=20,
    )
    assert res.n_exception == res.n_samples
    assert math.isnan(res.diff_max)
    assert math.isnan(res.diff_min)
    assert math.isnan(res.diff_mean)
