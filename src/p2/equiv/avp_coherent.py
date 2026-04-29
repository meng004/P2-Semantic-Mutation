from typing import Callable, Sequence
from p2.avp.dispatcher import call_avp
from p2.avp.interface import MR


def judge_e1(
    s_orig: Callable, s_mutant: Callable,
    mr_set: Sequence[MR], epsilon: float,
) -> bool:
    """E1: ∀ mr ∈ MR: AVP(S, mr) = AVP(s', mr)."""
    for mr in mr_set:
        if call_avp(s_orig, mr, epsilon) != call_avp(s_mutant, mr, epsilon):
            return False
    return True
