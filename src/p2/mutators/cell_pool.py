from dataclasses import dataclass, field
from typing import List
from pathlib import Path
from p2.mutators.prompt_loader import load_prompt_template, render_prompt
from p2.mutators.llm_generator import generate_mutants
from p2.mutators.llm_reviewer import review_mutant
from p2.mutators.dual_blind import classify_mutant, MutantStatus


@dataclass
class CellPool:
    cell_id: str  # e.g., "A1_MP1_mutC"
    double_confirmed: List[str] = field(default_factory=list)
    rejected: List[str] = field(default_factory=list)
    arbitration: List[str] = field(default_factory=list)


def build_cell_pool(
    put_source: str, put_name: str, mut_intent: str,
    n_candidates: int = 5, cell_id: str = "unnamed",
    template_path: Path = Path("src/p2/mutators/prompts/template_base.txt"),
) -> CellPool:
    template = load_prompt_template(template_path)
    prompt = render_prompt(
        template, put_name=put_name, mut_intent=mut_intent, put_source=put_source,
    )
    diffs = generate_mutants(prompt, n_candidates=n_candidates)
    pool = CellPool(cell_id=cell_id)
    for d in diffs:
        verdict = review_mutant(put_source=put_source, mutant_diff=d)
        status = classify_mutant(verdict)
        if status == MutantStatus.DOUBLE_CONFIRMED:
            pool.double_confirmed.append(d)
        elif status == MutantStatus.REJECTED_L0:
            pool.rejected.append(d)
        else:
            pool.arbitration.append(d)
    return pool
