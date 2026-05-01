"""LRCA layered classifier: returns the strongest applicable label.

Order of resolution (per §2.6.3 decision tree):
  L0 artifact → label as artifact, exit
  Killed AND L3 statistical noise → C4
  Killed AND L1 tolerance borderline → C2
  Killed AND L2 OOD-concentrated → C3
  Killed otherwise → C1 (legit fault, the "good" kill)
  Not killed → "survived" (no label needed for SMS)
"""
from enum import Enum
from typing import Callable

from p2.avp.interface import MR
from p2.lrca.l0_artifact import L0Label, classify_l0
from p2.lrca.l1_tolerance import is_tolerance_borderline
from p2.lrca.l2_ood import ood_fail_share
from p2.lrca.l3_statistical import is_statistical_noise


class LRCALabel(str, Enum):
    """One of the six LRCA verdicts returned by ``classify_mutant``."""
    ARTIFACT = "L0_artifact"
    C1_LEGIT = "C1_legit_fault"
    C2_TOLERANCE = "C2_tolerance_borderline"
    C3_OOD = "C3_ood_concentrated"
    C4_STATISTICAL = "C4_statistical_noise"
    SURVIVED = "survived"


def classify_mutant(
    mutant: Callable, original: Callable, mr: MR, was_killed: bool,
    epsilon: float = 1e-6, ood_threshold: float = 0.5,
) -> LRCALabel:
    """Return one LRCA label for a (mutant, MR) pair.

    Decision priority:
      1. L0 artifact (NaN/Inf/constant/identity) → ARTIFACT
      2. Not killed → SURVIVED (no diagnosis needed)
      3. Statistical noise (single fail / majority pass) → C4
      4. Tolerance borderline (strict fail / loose pass) → C2
      5. OOD-concentrated (R-fails clustered on boundary band) → C3
      6. Otherwise → C1 (legit semantic fault, the "good" kill)
    """
    l0 = classify_l0(mutant, n_samples=30, original=original)
    if l0 != L0Label.LEGIT:
        return LRCALabel.ARTIFACT
    if not was_killed:
        return LRCALabel.SURVIVED
    if is_statistical_noise(mutant, mr, epsilon=epsilon, repeats=20):
        return LRCALabel.C4_STATISTICAL
    if is_tolerance_borderline(mutant, mr, epsilon, epsilon * 10):
        return LRCALabel.C2_TOLERANCE
    if ood_fail_share(mutant, original, mr) > ood_threshold:
        return LRCALabel.C3_OOD
    return LRCALabel.C1_LEGIT
