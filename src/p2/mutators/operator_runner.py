"""Per-(operator, attempt) generation+review trial.

Each trial:
  1. ask generator LLM for one code candidate implementing the operator
  2. mechanically validate (V1-V4) and inject results into the reviewer payload
  3. ask reviewer LLM for V1-V6 + operator_match verdict (JSON)
  4. classify into CONFIRMED / REJECTED / UNCERTAIN

Multiple trials per operator (K independent calls, varying seed/attempt_idx)
are coordinated by run_operator_K_times.
"""
import asyncio
import json
import re
import importlib.util
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from p2.mutators.async_llm import AsyncSemaphoreClient, async_chat_completion
from p2.mutators.operator_registry import MutationOperator
from p2.mutators.validation import validate_mutant

_OP_TEMPLATE = (Path(__file__).parent / "prompts" / "operator_template.txt").read_text()
_OP_REVIEWER = (Path(__file__).parent / "prompts" / "operator_reviewer_template.txt").read_text()


@dataclass(frozen=True)
class OperatorTrialResult:
    op_id: str
    attempt_idx: int
    code: str
    v1: bool
    v2: str
    v3: str
    v4: str
    v5: str
    v6: str
    operator_match: str
    overall: str  # CONFIRMED | REJECTED | UNCERTAIN
    reason: str

    @property
    def is_confirmed(self) -> bool:
        return self.overall == "CONFIRMED"

    @property
    def is_semantic_match(self) -> bool:
        return self.operator_match == "Yes"

    def to_dict(self) -> dict:
        return {
            "op_id": self.op_id, "attempt_idx": self.attempt_idx,
            "code": self.code, "v1": self.v1, "v2": self.v2, "v3": self.v3,
            "v4": self.v4, "v5": self.v5, "v6": self.v6,
            "operator_match": self.operator_match,
            "overall": self.overall, "reason": self.reason,
        }


def _strip_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        text = "\n".join(ln for ln in lines if not ln.startswith("```")).strip()
    return text


def _parse_review(raw: str) -> dict:
    m = re.search(r"\{.*\}", raw, re.DOTALL)
    if not m:
        return {"overall": "REJECTED", "reason": f"parse_error: {raw[:120]}"}
    try:
        return json.loads(m.group())
    except json.JSONDecodeError as e:
        return {"overall": "REJECTED", "reason": f"json_error: {e}"}


def _load_program_from_string(code: str):
    spec = importlib.util.spec_from_loader("_mut_inline", loader=None)
    mod = importlib.util.module_from_spec(spec)
    try:
        exec(code, mod.__dict__)
        return mod.program
    except Exception:
        return None


async def run_operator_trial(
    op: MutationOperator,
    attempt_idx: int,
    put_source: str,
    put_name: str,
    scientific_domain: str,
    generator_client: Optional[AsyncSemaphoreClient],
    reviewer_client: Optional[AsyncSemaphoreClient],
    n_attempts: int = 10,
    generator_model: str = "claude-opus-4-6",
    reviewer_model: str = "gpt-5.4",
    temperature: float = 0.5,
) -> OperatorTrialResult:
    # -- 1. generate
    gen_prompt = _OP_TEMPLATE.format(
        put_name=put_name, scientific_domain=scientific_domain,
        op_id=op.id, op_label=op.label, op_target=op.target_locator,
        op_transformation=op.transformation, op_rationale=op.rationale,
        attempt_idx=attempt_idx + 1, n_attempts=n_attempts,
        put_source=put_source,
    )
    raw_code = await async_chat_completion(
        client=generator_client, model=generator_model,
        messages=[{"role": "user", "content": gen_prompt}],
        temperature=temperature, max_tokens=1500,
    )
    code = _strip_fences(raw_code)

    # -- 2. mechanical V1-V4 (used as a hint for the reviewer)
    original_fn = _load_program_from_string(put_source)
    mech = validate_mutant(code, original_fn) if original_fn else None
    mech_v1 = bool(mech and mech.syntax_ok)

    # -- 3. review
    rev_prompt = _OP_REVIEWER.format(
        put_source=put_source, mutant_code=code,
        op_id=op.id, op_label=op.label, op_target=op.target_locator,
        op_transformation=op.transformation,
    )
    raw_rev = await async_chat_completion(
        client=reviewer_client, model=reviewer_model,
        messages=[{"role": "user", "content": rev_prompt}],
        temperature=0.0, max_tokens=600,
    )
    parsed = _parse_review(raw_rev)

    return OperatorTrialResult(
        op_id=op.id, attempt_idx=attempt_idx, code=code,
        v1=bool(parsed.get("V1_syntax_ok", mech_v1)),
        v2=parsed.get("V2_executable", "Uncertain"),
        v3=parsed.get("V3_nontrivial", "Uncertain"),
        v4=parsed.get("V4_nondegenerate", "Uncertain"),
        v5=parsed.get("V5_single_fault", "Uncertain"),
        v6=parsed.get("V6_plausible", "Uncertain"),
        operator_match=parsed.get("operator_match", "Uncertain"),
        overall=parsed.get("overall", "UNCERTAIN"),
        reason=parsed.get("reason", ""),
    )


async def run_operator_K_times(
    op: MutationOperator,
    K: int,
    put_source: str,
    put_name: str,
    scientific_domain: str,
    generator_client: AsyncSemaphoreClient,
    reviewer_client: AsyncSemaphoreClient,
    temperature: float = 0.5,
    start_idx: int = 0,
) -> List[OperatorTrialResult]:
    """Run K trials for one operator concurrently (each gated by client semaphore).

    `start_idx` lets callers append additional K runs (key operators K=20 = 10+10).
    """
    tasks = [
        run_operator_trial(
            op=op, attempt_idx=start_idx + i,
            put_source=put_source, put_name=put_name,
            scientific_domain=scientific_domain,
            generator_client=generator_client, reviewer_client=reviewer_client,
            n_attempts=K + start_idx, temperature=temperature,
        )
        for i in range(K)
    ]
    return await asyncio.gather(*tasks)
