"""Per-cell mutant pool builder: generate → validate → review → classify."""
from dataclasses import dataclass, field
from typing import List

from p2.mutators.llm_generator import generate_mutants
from p2.mutators.llm_reviewer import review_mutant, ReviewVerdict
from p2.mutators.dual_blind import classify_mutant, MutantStatus
from p2.mutators.validation import validate_mutant


@dataclass
class CellPool:
    cell_id: str
    confirmed: List[str] = field(default_factory=list)
    rejected: List[str] = field(default_factory=list)
    verdicts: List[ReviewVerdict] = field(default_factory=list)


def build_cell_pool(
    put_source: str,
    put_name: str,
    scientific_domain: str,
    mut_intent: str,
    original_fn,
    n_candidates: int = 5,
    cell_id: str = "unnamed",
) -> CellPool:
    """Generate, validate, and review n_candidates mutants for one (PUT, MP) cell."""
    candidates = generate_mutants(
        put_source=put_source,
        put_name=put_name,
        scientific_domain=scientific_domain,
        mut_intent=mut_intent,
        n_candidates=n_candidates,
    )
    pool = CellPool(cell_id=cell_id)
    for code in candidates:
        val = validate_mutant(code, original_fn)
        if not val.passed:
            pool.rejected.append(code)
            continue
        verdict = review_mutant(put_source=put_source, mutant_code=code)
        pool.verdicts.append(verdict)
        status = classify_mutant(verdict)
        if status == MutantStatus.CONFIRMED:
            pool.confirmed.append(code)
        else:
            pool.rejected.append(code)
    return pool
