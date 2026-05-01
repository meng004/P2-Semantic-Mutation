"""LRCA L3 — Statistical-noise false positive (C4).

For stochastic PUTs (b2 MCMC, b3 MC integration, c-class with random
``random_state``, d-class), a mutant may R-fail on a single shot but pass
under N=20 majority vote. Such cases are C4 (the "kill" was noise, not
signal).

Note: this is the Round 8 single-(mutant, MR) statistical-noise probe.
The legacy assumption-violation test ``p2.lrca.l3_assumption`` lives in
a sibling module and is unrelated.
"""
from typing import Callable

from p2.avp.dispatcher import call_avp
from p2.avp.interface import AVPResult, MR
from p2.avp.repeat import call_avp_repeated


def is_statistical_noise(
    mutant: Callable, mr: MR, epsilon: float = 1e-6, repeats: int = 20,
) -> bool:
    """True if single-shot AVP fails but N=repeats majority-vote passes.

    Exceptions during the underlying AVP calls are narrowed to
    ``(ValueError, ArithmeticError, TypeError, RuntimeError)`` per the
    project pattern; on any such exception we conservatively return False
    (the kill is not labeled as noise).
    """
    try:
        single = call_avp(mutant, mr, epsilon)
        majority = call_avp_repeated(mutant, mr, epsilon, repeats=repeats)
    except (ValueError, ArithmeticError, TypeError, RuntimeError):
        return False
    return single == AVPResult.FAIL and majority == AVPResult.PASS
