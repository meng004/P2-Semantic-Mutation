"""TDD: structural MR is BLIND (buggy survives); discriminator reveals the fault."""
import case_fn_rng as c
def test_structural_mr_blind_buggy_survives():
    assert c.structural_verdict(c.CORRECT_VER) == "pass"
    assert c.structural_verdict(c.BUGGY_VER) == "pass"   # FN: NOT killed
def test_discriminator_reveals_nonequivalence():
    assert c.discriminator(c.BUGGY_VER) < 0.01
    assert c.discriminator(c.CORRECT_VER) > 0.4
