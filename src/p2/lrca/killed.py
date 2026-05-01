from typing import Callable, Sequence
from p2.avp.interface import MR, AVPResult
from p2.avp.dispatcher import call_avp
from p2.avp.repeat import call_avp_repeated


def is_killed(
    s_orig: Callable, s_mutant: Callable,
    mr_set: Sequence[MR], epsilon: float,
    repeats: int = 1,
) -> bool:
    """killed ⇔ ∃ mr ∈ MR: AVP(S, mr) = pass ∧ AVP(s', mr) = fail.

    When ``repeats > 1``, each AVP call is replaced by an N-repeat
    majority vote (see ``p2.avp.repeat.call_avp_repeated``) to stabilize
    the verdict for stochastic PUTs (b2 MCMC, b3 MC integration,
    classifiers with ``random_state``). Default ``repeats=1`` preserves
    the legacy single-shot behavior used by run_one_cell and l1_tolerance.
    """
    if repeats > 1:
        for mr in mr_set:
            if call_avp_repeated(s_orig, mr, epsilon, repeats=repeats) == AVPResult.PASS and \
               call_avp_repeated(s_mutant, mr, epsilon, repeats=repeats) == AVPResult.FAIL:
                return True
        return False
    for mr in mr_set:
        if call_avp(s_orig, mr, epsilon) == AVPResult.PASS and \
           call_avp(s_mutant, mr, epsilon) == AVPResult.FAIL:
            return True
    return False
