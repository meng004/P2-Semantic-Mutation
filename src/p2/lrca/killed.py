from typing import Callable, Sequence
from p2.avp.interface import MR, AVPResult
from p2.avp.dispatcher import call_avp


def is_killed(
    s_orig: Callable, s_mutant: Callable,
    mr_set: Sequence[MR], epsilon: float,
) -> bool:
    """killed ⇔ ∃ mr ∈ MR: AVP(S, mr) = pass ∧ AVP(s', mr) = fail."""
    for mr in mr_set:
        if call_avp(s_orig, mr, epsilon) == AVPResult.PASS and \
           call_avp(s_mutant, mr, epsilon) == AVPResult.FAIL:
            return True
    return False
