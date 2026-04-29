from p2.mutators.dual_blind import classify_mutant, MutantStatus
from p2.mutators.llm_reviewer import ReviewVerdict


def test_double_confirmed_when_all_yes():
    v = ReviewVerdict(syntax_ok=True, executable="Yes", fault_injected="Yes")
    assert classify_mutant(v) == MutantStatus.DOUBLE_CONFIRMED


def test_rejected_when_syntax_bad():
    v = ReviewVerdict(syntax_ok=False, executable="No", fault_injected="Yes")
    assert classify_mutant(v) == MutantStatus.REJECTED_L0


def test_arbitration_when_uncertain():
    v = ReviewVerdict(syntax_ok=True, executable="Yes", fault_injected="Uncertain")
    assert classify_mutant(v) == MutantStatus.ARBITRATION_QUEUE
