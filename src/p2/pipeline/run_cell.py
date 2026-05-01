from dataclasses import dataclass, field
from typing import Callable, Sequence, List
from p2.avp.interface import MR
from p2.equiv.judge import is_equivalent
from p2.equiv.sampler import InputSampler
from p2.lrca.killed import is_killed


@dataclass
class CellResult:
    cell_id: str
    inst_count: int = 0
    equiv_count: int = 0
    killed_count: int = 0
    survive_count: int = 0
    sms: float = 0.0
    equiv_indices: List[int] = field(default_factory=list)
    killed_indices: List[int] = field(default_factory=list)


def run_one_cell(
    put: Callable, mutants: Sequence[Callable],
    mr_set: Sequence[MR], cell_id: str,
    sampler: InputSampler, k_eq: int,
    epsilon_eq: float, epsilon_avp: float,
    repeats: int = 1,
) -> CellResult:
    """Evaluate one (PUT, MR-set) cell against a list of mutants.

    ``repeats`` is forwarded to :func:`p2.lrca.killed.is_killed`. When
    > 1, the killed verdict is the majority vote of N AVP repetitions
    (used by Round-4+ Track-2 to stabilize stochastic-PUT verdicts).
    Equivalence detection is unaffected (still single-shot, k_eq inputs).
    """
    result = CellResult(cell_id=cell_id, inst_count=len(mutants))
    for idx, sm in enumerate(mutants):
        if is_equivalent(put, sm, mr_set, sampler, k_eq, epsilon_eq, epsilon_avp):
            result.equiv_count += 1
            result.equiv_indices.append(idx)
            continue
        if is_killed(put, sm, mr_set, epsilon_avp, repeats=repeats):
            result.killed_count += 1
            result.killed_indices.append(idx)
        else:
            result.survive_count += 1
    denom = result.inst_count - result.equiv_count
    result.sms = result.killed_count / denom if denom > 0 else 0.0
    return result
