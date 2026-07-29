"""DVE portfolio-selection strategies S1-S4 (plan v1.1.1 §3.6).

Each strategy picks k MRs from the valid selection space R_valid(P) \\ R0(P)
using only its permitted guidance signal. All are deterministic given inputs
(S4 given a seed). Strategies never see the holdout.

Signal inputs are plain matrices so the selectors are pure and unit-testable:

- dev_kill[mr][family]        -> bool: does MR kill any instance of dev family
- syn_kill[mr][syn_mutant]    -> bool: does MR kill a surviving syntactic mutant
- coverage[mr]                -> frozenset of coverage elements the MR exercises
"""
from __future__ import annotations

from typing import Dict, List, Mapping, Sequence, Set


def _greedy_set_cover(candidates: Sequence[str],
                      element_sets: Mapping[str, Set],
                      already_covered: Set,
                      k: int,
                      cost: Mapping[str, float] | None = None) -> List[str]:
    """Greedy max-coverage: pick k candidates maximizing new element coverage.

    Ties broken by lower cost, then by candidate id for determinism.
    """
    covered = set(already_covered)
    remaining = list(candidates)
    chosen: List[str] = []
    cost = cost or {}
    for _ in range(min(k, len(remaining))):
        # pick the candidate with the smallest sort key
        # (-gain, cost, id): most new coverage, then lowest cost, then id.
        best = None
        best_key = None
        for c in remaining:
            gain = len(element_sets.get(c, set()) - covered)
            key = (-gain, cost.get(c, 0.0), c)
            if best_key is None or key < best_key:
                best, best_key = c, key
        chosen.append(best)
        covered |= element_sets.get(best, set())
        remaining.remove(best)
    return chosen


def s1_residual_guided(valid_mrs: Sequence[str],
                       dev_kill: Mapping[str, Set[str]],
                       r0_dev_residual_families: Set[str],
                       k: int,
                       cost: Mapping[str, float] | None = None) -> List[str]:
    """S1 (treatment): cover dev residual families U(R0, M_dev).

    dev_kill[mr] = set of dev family ids the MR kills. Elements are families,
    so a family with many instances is counted once (plan §3.6 anti-double-count).
    """
    element_sets = {mr: set(dev_kill.get(mr, set())) & r0_dev_residual_families
                    for mr in valid_mrs}
    return _greedy_set_cover(valid_mrs, element_sets, set(), k, cost)


def s2_classical_ms_guided(valid_mrs: Sequence[str],
                           syn_kill: Mapping[str, Set[str]],
                           r0_surviving_syntactic: Set[str],
                           k: int,
                           cost: Mapping[str, float] | None = None) -> List[str]:
    """S2 (joint primary baseline): cover R0-surviving syntactic mutants."""
    element_sets = {mr: set(syn_kill.get(mr, set())) & r0_surviving_syntactic
                    for mr in valid_mrs}
    return _greedy_set_cover(valid_mrs, element_sets, set(), k, cost)


def s3_coverage_guided(valid_mrs: Sequence[str],
                       coverage: Mapping[str, Set],
                       r0_coverage: Set,
                       k: int,
                       cost: Mapping[str, float] | None = None) -> List[str]:
    """S3 (joint primary baseline): maximize MR-coverage increment over R0.

    Uses no mutant information whatsoever.
    """
    element_sets = {mr: set(coverage.get(mr, set())) for mr in valid_mrs}
    return _greedy_set_cover(valid_mrs, element_sets, set(r0_coverage), k, cost)


def s4_random(valid_mrs: Sequence[str], k: int, seed: int) -> List[str]:
    """S4 (sanity-check): a single random draw of k MRs (seeded)."""
    import numpy as np
    rng = np.random.default_rng(seed)
    idx = rng.choice(len(valid_mrs), size=min(k, len(valid_mrs)), replace=False)
    return [valid_mrs[i] for i in sorted(idx)]


def s4_random_distribution(valid_mrs: Sequence[str], k: int,
                           n_draws: int, seed: int) -> List[List[str]]:
    """S4 reference distribution: n_draws independent random portfolios."""
    return [s4_random(valid_mrs, k, seed + i) for i in range(n_draws)]
