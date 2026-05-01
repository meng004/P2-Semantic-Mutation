"""LRCA L1 — Tolerance/precision sensitivity (C2).

A killed mutant is C2 if its R-fail goes away when AVP epsilon is loosened
by 10x. Indicates the fault is borderline numerical noise, not a true
semantic break.

This module also retains the legacy ``check_l1_robust`` helper used by
Round 7's robustness pre-screen (kept for backwards compatibility with
``tests/lrca/test_l1_tolerance.py``); the Round 8 dispatcher uses
``is_tolerance_borderline`` instead.
"""
from typing import Callable, Sequence

from p2.avp.dispatcher import call_avp
from p2.avp.interface import AVPResult, MR
from p2.lrca.killed import is_killed


def is_tolerance_borderline(
    mutant: Callable, mr: MR, epsilon_strict: float = 1e-6,
    epsilon_loose: float = 1e-5,
) -> bool:
    """True if mutant is killed at strict ε but passes at 10× looser ε.

    Used by the Round 8 LRCA dispatcher to label a single (mutant, MR)
    pair as C2 when the fault is borderline numerical noise rather than
    a genuine semantic break.

    Exceptions during ``call_avp`` are narrowed to the project pattern
    ``(ValueError, ArithmeticError, TypeError, RuntimeError)`` to avoid
    swallowing ``BaseException`` subclasses such as ``KeyboardInterrupt``.
    """
    try:
        strict = call_avp(mutant, mr, epsilon_strict)
        loose = call_avp(mutant, mr, epsilon_loose)
    except (ValueError, ArithmeticError, TypeError, RuntimeError):
        return False
    return strict == AVPResult.FAIL and loose == AVPResult.PASS


def check_l1_robust(
    s_orig: Callable, s_mutant: Callable,
    mr_set: Sequence[MR], n_repeat: int = 20, epsilon: float = 0.05,
    threshold: float = 0.8,
) -> bool:
    """Legacy Round 7 helper: rerun N times, fail rate ≥ threshold ⇒ robust.

    Retained for backwards compatibility with the legacy decision-tree
    classifier (``p2.lrca.decision_tree``) which uses fail-rate >=
    ``threshold`` to gate C2 classification. The Round 8 dispatcher
    supersedes this with ``is_tolerance_borderline`` operating on a single
    (mutant, MR) pair.
    """
    fail_count = sum(
        1 for _ in range(n_repeat) if is_killed(s_orig, s_mutant, mr_set, epsilon)
    )
    return (fail_count / n_repeat) >= threshold
