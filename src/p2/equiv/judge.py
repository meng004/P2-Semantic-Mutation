from typing import Callable, Sequence
from p2.avp.interface import MR
from p2.equiv.output_equiv import judge_e2
from p2.equiv.avp_coherent import judge_e1
from p2.equiv.sampler import sample_inputs, InputSampler


def is_equivalent(
    s_orig: Callable, s_mutant: Callable,
    mr_set: Sequence[MR], sampler: InputSampler,
    k_eq: int, epsilon_eq: float, epsilon_avp: float,
) -> bool:
    """equiv ⇔ (E1 AVP-coherent) ∧ (E2 output-equiv)."""
    samples = sample_inputs(sampler, k_eq)
    if not judge_e2(s_orig, s_mutant, samples, epsilon_eq):
        return False
    return judge_e1(s_orig, s_mutant, mr_set, epsilon_avp)
