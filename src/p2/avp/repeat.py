"""N-repeat majority-vote AVP wrapper.

For stochastic PUTs (MCMC, MC integration, classifier with random_state),
single-shot AVP can mis-classify due to stochastic R-pass. We run the
verifier N times and majority-vote the verdict.
"""
import sys
from typing import Callable

from p2.avp.dispatcher import call_avp
from p2.avp.interface import AVPResult, MR


# Module-level dedupe set: print to stderr only the FIRST time we see a given
# exception type during repeated AVP calls. Mirrors p2.equiv.diagnosis and
# p2.mutators.pool_builder so Round 8 LRCA debugging has a quick signal
# without spamming logs.
_SEEN_REPEAT_EXCEPTIONS: set = set()


def _record_new_repeat_exception(e: BaseException) -> None:
    t = type(e)
    if t not in _SEEN_REPEAT_EXCEPTIONS:
        _SEEN_REPEAT_EXCEPTIONS.add(t)
        print(
            f"[avp.repeat] first {t.__name__}: {str(e)[:200]}",
            file=sys.stderr,
        )


def call_avp_repeated(
    program: Callable, mr: MR, epsilon: float, repeats: int = 20,
) -> AVPResult:
    """Run call_avp `repeats` times, return PASS iff > 50% repeats PASS.

    Repeats <= 1 falls back to a single call. Exceptions during call_avp
    are counted as FAIL for that repeat (the offending repeat is dropped
    from n_total; if every repeat raises, the verdict is FAIL).
    """
    if repeats <= 1:
        return call_avp(program, mr, epsilon)
    n_pass = 0
    n_total = 0
    for _ in range(repeats):
        try:
            r = call_avp(program, mr, epsilon)
        except Exception as exc:
            _record_new_repeat_exception(exc)
            continue
        n_total += 1
        if r == AVPResult.PASS:
            n_pass += 1
    if n_total == 0:
        return AVPResult.FAIL
    return AVPResult.PASS if n_pass > n_total / 2 else AVPResult.FAIL
