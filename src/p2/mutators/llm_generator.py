"""LLM-G: Claude Opus 4.6 generates complete mutant Python programs."""
import time
from pathlib import Path
from typing import List

from p2.mutators.llm_client import generator_client

_TEMPLATE = (Path(__file__).parent / "prompts" / "generator_template.txt").read_text()


def generate_mutants(
    put_source: str,
    put_name: str,
    scientific_domain: str,
    mut_intent: str,
    n_candidates: int = 5,
    temperature: float = 0.7,
) -> List[str]:
    """Call Claude Opus 4.6 to generate n_candidates complete mutant programs.

    Returns list of Python source strings (complete files, not diffs).
    Caller is responsible for mechanical validation and LLM review.
    """
    client, model = generator_client()
    # Multi-turn conversation: each request includes all previous mutants so the
    # model is forced to generate a genuinely different defect each time.
    messages: List[dict] = []
    programs: List[str] = []

    for i in range(n_candidates):
        already = ""
        if programs:
            snippets = "\n\n".join(
                f"--- Previously generated candidate #{j+1} ---\n{p}"
                for j, p in enumerate(programs)
            )
            already = (
                f"\n\n━━━ ALREADY GENERATED (DO NOT REPEAT) ━━━\n{snippets}\n"
                "You MUST introduce a DIFFERENT defect from every candidate above."
            )

        candidate_prompt = _TEMPLATE.format(
            put_name=put_name,
            scientific_domain=scientific_domain,
            mut_intent=mut_intent,
            put_source=put_source,
            candidate_index=i + 1,
            n_candidates=n_candidates,
            prev_index=max(i, 1),
        ) + already

        messages.append({"role": "user", "content": candidate_prompt})
        try:
            resp = client.chat.completions.create(
                model=model,
                temperature=temperature,
                max_tokens=1500,
                messages=messages,
            )
            code = resp.choices[0].message.content.strip()
            # Strip accidental markdown fences
            if code.startswith("```"):
                lines = code.splitlines()
                code = "\n".join(
                    ln for ln in lines if not ln.startswith("```")
                ).strip()
            messages.append({"role": "assistant", "content": code})
            programs.append(code)
        except Exception as e:
            programs.append(f"# GENERATION_ERROR: {e}")
            messages.append({"role": "assistant", "content": f"# error: {e}"})
        if i < n_candidates - 1:
            time.sleep(0.5)

    return programs
