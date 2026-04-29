import os
import json
from dataclasses import dataclass
from typing import Literal
import openai


@dataclass(frozen=True)
class ReviewVerdict:
    syntax_ok: bool
    executable: Literal["Yes", "No", "Uncertain"]
    fault_injected: Literal["Yes", "No", "Uncertain"]


REVIEWER_PROMPT = """You are a code reviewer. Examine the original program and a mutant
(diff applied). Output strict JSON with three fields:
  syntax_ok: bool — is the mutant syntactically valid Python?
  executable: "Yes" | "No" | "Uncertain" — does it appear runnable?
  fault_injected: "Yes" | "No" | "Uncertain" — does it inject some semantic failure?

You are NOT told the failure category, MR, or generator identity.

ORIGINAL:
```python
{put_source}
```

MUTANT DIFF:
```
{mutant_diff}
```

Output JSON only, no prose."""


def review_mutant(put_source: str, mutant_diff: str, model: str = "gpt-4o") -> ReviewVerdict:
    client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY", ""))
    resp = client.chat.completions.create(
        model=model, temperature=0.0, seed=42,
        response_format={"type": "json_object"},
        messages=[{
            "role": "user",
            "content": REVIEWER_PROMPT.format(put_source=put_source, mutant_diff=mutant_diff),
        }],
    )
    parsed = json.loads(resp.choices[0].message.content)
    return ReviewVerdict(
        syntax_ok=bool(parsed["syntax_ok"]),
        executable=parsed["executable"],
        fault_injected=parsed["fault_injected"],
    )
