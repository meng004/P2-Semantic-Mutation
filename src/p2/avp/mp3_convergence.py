import numpy as np
from typing import Callable, Sequence
from p2.avp.interface import AVPResult, MR


def verify_convergence_order(
    program: Callable, mr: MR, h_values: Sequence[float],
    expected_order: float, tolerance: float = 0.2,
    reference_value: float = 1.0,
) -> AVPResult:
    """MP_3 verification: estimate convergence order from grid sequence."""
    h_arr = np.asarray(sorted(h_values, reverse=True))
    errors = np.array([abs(program(h) - reference_value) for h in h_arr])
    valid = errors > 1e-15
    if valid.sum() < 3:
        return AVPResult.FAIL
    log_h = np.log(h_arr[valid])
    log_e = np.log(errors[valid])
    order_est, _ = np.polyfit(log_h, log_e, 1)
    return (
        AVPResult.PASS
        if abs(order_est - expected_order) <= tolerance
        else AVPResult.FAIL
    )
