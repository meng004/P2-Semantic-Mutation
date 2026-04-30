"""LLM-R1/R2: GPT-5.4 review + DeepSeek V4 Pro arbitration.

Protocol (§4.2.4):
  Primary reviewer  : GPT-5.4  (blind to generator identity and MR)
  Arbitration model : DeepSeek V4 Pro  (replaces human arbitration)
  Entry rule        : GPT=CONFIRMED → pool; GPT=REJECTED → discard;
                      GPT=UNCERTAIN → DeepSeek arbitrates final verdict.
"""
import json
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from p2.mutators.llm_client import reviewer1_client, reviewer2_client

_TEMPLATE = (Path(__file__).parent / "prompts" / "reviewer_template.txt").read_text()

Overall = Literal["CONFIRMED", "REJECTED", "UNCERTAIN"]


@dataclass(frozen=True)
class ReviewVerdict:
    V1_syntax_ok: bool
    V2_executable: Literal["Yes", "No", "Uncertain"]
    V3_nontrivial: Literal["Yes", "No", "Uncertain"]
    V4_nondegenerate: Literal["Yes", "No", "Uncertain"]
    V5_single_fault: Literal["Yes", "No", "Uncertain"]
    V6_plausible: Literal["Yes", "No", "Uncertain"]
    overall: Overall
    reason: str
    reviewer: str  # "gpt" | "deepseek"


def _parse_verdict(raw: str, reviewer: str) -> ReviewVerdict:
    """Parse JSON from LLM response, tolerating extra prose."""
    m = re.search(r"\{.*\}", raw, re.DOTALL)
    if not m:
        return ReviewVerdict(False, "No", "No", "No", "No", "No",
                             "REJECTED", f"parse_error: {raw[:120]}", reviewer)
    try:
        d = json.loads(m.group())
        return ReviewVerdict(
            V1_syntax_ok=bool(d.get("V1_syntax_ok", False)),
            V2_executable=d.get("V2_executable", "Uncertain"),
            V3_nontrivial=d.get("V3_nontrivial", "Uncertain"),
            V4_nondegenerate=d.get("V4_nondegenerate", "Uncertain"),
            V5_single_fault=d.get("V5_single_fault", "Uncertain"),
            V6_plausible=d.get("V6_plausible", "Uncertain"),
            overall=d.get("overall", "UNCERTAIN"),
            reason=d.get("reason", ""),
            reviewer=reviewer,
        )
    except json.JSONDecodeError as e:
        return ReviewVerdict(False, "No", "No", "No", "No", "No",
                             "REJECTED", f"json_error: {e}", reviewer)


def _call_reviewer(client, model: str, put_source: str,
                   mutant_code: str, reviewer_name: str) -> ReviewVerdict:
    prompt = _TEMPLATE.format(put_source=put_source, mutant_code=mutant_code)
    try:
        resp = client.chat.completions.create(
            model=model,
            temperature=0.0,
            max_tokens=600,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = resp.choices[0].message.content
    except Exception as e:
        return ReviewVerdict(False, "No", "No", "No", "No", "No",
                             "REJECTED", f"api_error: {e}", reviewer_name)
    return _parse_verdict(raw, reviewer_name)


def review_mutant(put_source: str, mutant_code: str) -> ReviewVerdict:
    """Primary review by GPT-5.4; DeepSeek arbitrates if UNCERTAIN."""
    r1_client, r1_model = reviewer1_client()
    verdict = _call_reviewer(r1_client, r1_model, put_source, mutant_code, "gpt")

    if verdict.overall != "UNCERTAIN":
        return verdict

    # Arbitration: DeepSeek V4 Pro
    time.sleep(0.5)
    r2_client, r2_model = reviewer2_client()
    arb = _call_reviewer(r2_client, r2_model, put_source, mutant_code, "deepseek")
    return arb
