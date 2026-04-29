import numpy as np
from p2.avp.interface import AVPResult, MR
from p2.avp.mp3_convergence import verify_convergence_order


def test_second_order_method_passes():
    """Method with O(h^2) error refinement should pass."""
    def second_order(h):
        return 1.0 + 0.1 * h**2  # error proportional to h^2

    mr = MR(
        r=lambda h: h / 2,
        R=lambda y_orig, y_new: True,  # carried by AVP internal logic
        mp_index=3, name="second-order",
    )
    h_values = [0.1, 0.05, 0.025, 0.0125]
    result = verify_convergence_order(second_order, mr, h_values, expected_order=2.0, tolerance=0.2)
    assert result == AVPResult.PASS


def test_wrong_order_fails():
    def first_order(h):
        return 1.0 + 0.1 * h  # error proportional to h, not h^2
    mr = MR(r=lambda h: h / 2, R=lambda a, b: True, mp_index=3, name="bad")
    h_values = [0.1, 0.05, 0.025, 0.0125]
    result = verify_convergence_order(first_order, mr, h_values, expected_order=2.0, tolerance=0.2)
    assert result == AVPResult.FAIL
