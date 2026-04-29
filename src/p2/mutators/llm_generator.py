import os
import anthropic
from typing import List


def generate_mutants(
    prompt: str, model: str = "claude-opus-4-5",
    n_candidates: int = 5, temperature: float = 0.3, seed: int = 42,
    max_tokens: int = 1024,
) -> List[str]:
    """Call Claude to generate n_candidates mutant diffs.

    Returns list of unified-diff strings. Filtering of malformed outputs
    is the caller's responsibility (see mutators.dual_blind_review).
    """
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))
    diffs: List[str] = []
    for i in range(n_candidates):
        msg = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[{"role": "user", "content": prompt}],
        )
        diffs.append(msg.content[0].text)
    return diffs
