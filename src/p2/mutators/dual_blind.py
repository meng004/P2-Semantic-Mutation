from enum import Enum
from p2.mutators.llm_reviewer import ReviewVerdict


class MutantStatus(Enum):
    DOUBLE_CONFIRMED = "double_confirmed"
    REJECTED_L0 = "rejected_l0"
    ARBITRATION_QUEUE = "arbitration_queue"


def classify_mutant(verdict: ReviewVerdict) -> MutantStatus:
    """Classify based on dual-blind review verdict per §4.2.4 protocol C."""
    if not verdict.syntax_ok or verdict.executable == "No":
        return MutantStatus.REJECTED_L0
    if verdict.fault_injected == "Yes" and verdict.executable == "Yes":
        return MutantStatus.DOUBLE_CONFIRMED
    return MutantStatus.ARBITRATION_QUEUE
