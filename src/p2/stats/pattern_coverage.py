"""Pattern coverage: fraction of (MP, R-outcome) cells exercised.

Operationalisation: each cell is (MP_k, R_outcome ∈ {True, False}). A test
suite "covers" a cell if at least one (mutant, MP) pair in the suite produced
that R outcome. Pattern coverage = covered / (n_MPs × 2).

Used as the §1.4 RQ4 baseline against SMS.
"""
from typing import Iterable, Tuple


def compute_pattern_coverage(
    outcomes: Iterable[Tuple[int, bool]], n_mps: int = 5,
) -> float:
    """outcomes: iterable of (mp_index, R_pass_bool) tuples.
    Returns the fraction of (mp, outcome) cells covered."""
    covered = set()
    for mp, ok in outcomes:
        covered.add((mp, bool(ok)))
    total = n_mps * 2
    return len(covered) / total if total else 0.0
