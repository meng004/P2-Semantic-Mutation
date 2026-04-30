from typing import Callable
from p2.avp.interface import AVPResult, MR
from p2.avp.mp1_conservation import verify_conservation
from p2.avp.mp2_5_wilcoxon import verify_wilcoxon
from p2.avp.mp3_convergence import verify_convergence_order


def call_avp(program: Callable, mr: MR, epsilon: float) -> AVPResult:
    """AVP dispatcher: route to MP_k specific verifier by mr.mp_index."""
    if mr.mp_index == 1:
        return verify_conservation(program, mr, epsilon)
    elif mr.mp_index in (2, 5):
        return verify_wilcoxon(program, mr, alpha=0.05)
    elif mr.mp_index == 3:
        h_values = [0.1, 0.05, 0.025, 0.0125]
        return verify_convergence_order(program, mr, h_values, expected_order=2.0)
    elif mr.mp_index == 4:
        from p2.avp.mp4_dtw import verify_trajectory_dtw
        return verify_trajectory_dtw(program, mr, epsilon_dtw=epsilon)
    else:
        raise ValueError(f"Unknown MP index {mr.mp_index}")
