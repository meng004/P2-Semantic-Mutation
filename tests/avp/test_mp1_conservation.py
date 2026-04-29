import numpy as np
from p2.avp.interface import AVPResult, MR
from p2.avp.mp1_conservation import verify_conservation


def conservation_program(x):
    """Energy-conserving toy: returns (kinetic, potential) summing to 1.0."""
    return np.array([x, 1.0 - x])


def test_conservation_passes_when_holds():
    mr = MR(
        r=lambda x: x + 0.5,
        R=lambda y_orig, y_new: abs(y_orig.sum() - y_new.sum()) <= 1e-6,
        mp_index=1, name="energy-sum",
    )
    result = verify_conservation(conservation_program, mr, epsilon=1e-6)
    assert result == AVPResult.PASS


def test_conservation_fails_when_broken():
    def broken_program(x):
        return np.array([x, 1.0 - x + 0.1 * x])  # sum = 1 + 0.1*x, not conserved
    mr = MR(
        r=lambda x: x + 0.5,  # different input → different output
        R=lambda y_orig, y_new: abs(y_orig.sum() - y_new.sum()) <= 1e-6,
        mp_index=1, name="energy-sum",
    )
    result = verify_conservation(broken_program, mr, epsilon=1e-6)
    assert result == AVPResult.FAIL
