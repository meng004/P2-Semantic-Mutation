from enum import Enum
from typing import Protocol, Callable, Any
from dataclasses import dataclass


class AVPResult(Enum):
    PASS = "pass"
    FAIL = "fail"


@dataclass(frozen=True)
class MR:
    """Metamorphic Relation instance: input transform r and output verifier R."""
    r: Callable[[Any], Any]          # input transform
    R: Callable[[Any, Any], bool]    # output verifier
    mp_index: int                    # 1..5, which MP this MR belongs to
    name: str                        # for logging


class AVPInterface(Protocol):
    """AVP : Programs × MR × R⁺ → {pass, fail}"""
    def __call__(self, program: Callable, mr: MR, epsilon: float) -> AVPResult: ...
