from typing import Sequence


def is_ood_induced(
    fails_per_input: Sequence[bool], valid_mask: Sequence[bool],
) -> bool:
    """L2: returns True iff failures occur only on inputs outside valid domain."""
    fails_inside = sum(1 for f, v in zip(fails_per_input, valid_mask) if f and v)
    fails_outside = sum(1 for f, v in zip(fails_per_input, valid_mask) if f and not v)
    return fails_inside == 0 and fails_outside > 0
