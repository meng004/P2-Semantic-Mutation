from dataclasses import dataclass
from enum import Enum


class RootCause(Enum):
    C1 = "C1_genuine_semantic_failure"
    C2 = "C2_tolerance_perturbation"
    C3 = "C3_OOD_induced"
    C4 = "C4_assumption_violation"
    C5 = "C5_mutator_artifact"


@dataclass(frozen=True)
class KillContext:
    l1_robust: bool      # True if fail rate ≥ 0.8 over N repeats
    l2_ood: bool         # True if fails only outside D_S^valid (C/D classes)
    l3_violated: bool    # True if IID/stationarity broken (B/D classes + Wilcoxon/DTW)
    artifact: bool       # True if mutator/LLM artifact detected by post-hoc review


def classify_root_cause(ctx: KillContext) -> RootCause:
    """Decision tree per §2.6.3 with priority C5 > C4 > C3 > C2 > C1."""
    if not ctx.l1_robust:
        return RootCause.C2
    if ctx.l2_ood:
        return RootCause.C3
    if ctx.l3_violated:
        return RootCause.C4
    if ctx.artifact:
        return RootCause.C5
    return RootCause.C1
