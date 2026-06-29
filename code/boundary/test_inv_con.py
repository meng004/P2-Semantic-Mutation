"""TDD: conservative scheme gets RH shock speed (pass); non-conservative wrong (killed)."""
import case_inv_con as c
def test_conservative_correct_speed_passes():
    assert c.verdict(c.CORRECT) == "pass"
def test_nonconservative_wrong_speed_killed():
    assert c.verdict(c.WRONG) == "fail"
