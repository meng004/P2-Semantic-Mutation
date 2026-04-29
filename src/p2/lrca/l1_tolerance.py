from typing import Callable, Sequence
from p2.avp.interface import MR
from p2.lrca.killed import is_killed


def check_l1_robust(
    s_orig: Callable, s_mutant: Callable,
    mr_set: Sequence[MR], n_repeat: int = 20, epsilon: float = 0.05,
    threshold: float = 0.8,
) -> bool:
    """L1: rerun N times, fail rate ≥ threshold ⇒ robust (not C2)."""
    fail_count = sum(
        1 for _ in range(n_repeat) if is_killed(s_orig, s_mutant, mr_set, epsilon)
    )
    return (fail_count / n_repeat) >= threshold
