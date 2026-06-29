"""TDD: hard-constraint PINN satisfies exact BC (pass); soft-constraint PINN
violates it at strict tolerance (killed). Also shows the FP<->FN eps tradeoff."""
import case_pinn_bc as c
def test_hard_constraint_exact_bc_passes():
    assert c.verdict(c.CORRECT) == "pass"
def test_soft_constraint_killed_at_strict_tol():
    assert c.verdict(c.WRONG, epsilon_tol=1e-4) == "fail"
def test_eps_tradeoff_soft_survives_loose_tol():
    assert c.verdict(c.WRONG, epsilon_tol=1e-3) == "pass"   # MR turns blind (FN)
