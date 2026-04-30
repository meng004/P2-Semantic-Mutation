from enum import Enum
from p2.mutators.llm_reviewer import ReviewVerdict


class MutantStatus(Enum):
    CONFIRMED = "confirmed"      # GPT=CONFIRMED → pool
    REJECTED = "rejected"        # GPT=REJECTED → discard
    ARBITRATED = "arbitrated"    # DeepSeek final verdict


def classify_mutant(verdict: ReviewVerdict) -> MutantStatus:
    """Map ReviewVerdict.overall to MutantStatus per §4.2.4 protocol."""
    if verdict.overall == "CONFIRMED":
        return MutantStatus.CONFIRMED
    if verdict.overall == "REJECTED":
        return MutantStatus.REJECTED
    # DeepSeek arbitration result is also stored in overall
    return MutantStatus.ARBITRATED
