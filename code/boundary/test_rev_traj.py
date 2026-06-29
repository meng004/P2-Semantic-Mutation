"""TDD: symplectic leapfrog bounded (pass); non-symplectic Euler secular (killed)."""
import case_rev_traj as c
def test_symplectic_bounded_passes():
    assert c.verdict(c.CORRECT) == "pass"
def test_nonsymplectic_secular_killed():
    assert c.verdict(c.WRONG) == "fail"
