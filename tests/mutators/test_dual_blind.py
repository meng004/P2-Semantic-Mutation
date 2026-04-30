from p2.mutators.dual_blind import classify_mutant, MutantStatus
from p2.mutators.llm_reviewer import ReviewVerdict


def _make_verdict(overall):
    return ReviewVerdict(True, "Yes", "Yes", "Yes", "Yes", "Yes",
                         overall, "ok", "gpt")


def test_confirmed_verdict():
    assert classify_mutant(_make_verdict("CONFIRMED")) == MutantStatus.CONFIRMED


def test_rejected_verdict():
    assert classify_mutant(_make_verdict("REJECTED")) == MutantStatus.REJECTED


def test_uncertain_maps_to_arbitrated():
    assert classify_mutant(_make_verdict("UNCERTAIN")) == MutantStatus.ARBITRATED
