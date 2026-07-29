# MR_SOURCE_SYMMETRY — EXP-DIS held-out provider checklist

Seed: `20260728`. v4 sources (FORBIDDEN for held-out): claude, gpt, deepseek.

## Provider candidate ranking (by symmetry-satisfiability)

| Rank | Provider | Notes |
|---|---|---|
| 1 | Gemini | OpenAI-compatible proxy widely available; matches prompt-verbatim, temperature=0.7, candidate-count, budget constraints; not used in v4. |
| 2 | Qwen | DashScope or OpenAI-compat; temperature + max_tokens parity; strong code generation; not used in v4. |
| 3 | Mistral | La Plateforme / OpenAI-compat; chat completions parity; slightly thinner proxy ecosystem than Gemini/Qwen. |
| 4 | Llama-hosted | Together/Fireworks/Groq OpenAI-compat; last resort — temperature semantics can drift vs proprietary v4 sources. |

## 7-item symmetry checklist

| # | Item | v4 value | v5 held-out value | Status |
|---|---|---|---|---|
| 1 | Prompt text | SHA-256 `06fa552d7431cecc00120bddeb4e8cdc4511ce03f695139809b5af83508a3e90` (cross_source_campaign.PROMPT_TEMPLATE) | SAME (pending run) | ⬜ pending key |
| 2 | Parser version | `cross_source_campaign._strip_fences (```python fence extractor)` | same function | ⬜ pending key |
| 3 | Temperature | `0.7` | `0.7` | ⬜ pending key |
| 4 | Candidate count / K trials | default K=`3` per (op, source) | same K | ⬜ pending key |
| 5 | Repair / retry budget | v4: no auto-repair beyond K attempts | same | ⬜ pending key |
| 6 | Max tokens | `800` (cross_source_campaign._generate_one) | `800` | ⬜ pending key |
| 7 | Provider identity | Claude / GPT / DeepSeek | **(blank — select from ranking when key arrives)** | ⬜ pending key |

## Required env vars

```
V5_MR_API_KEY=<held-out provider key>
V5_MR_BASE_URL=<OpenAI-compatible base URL>
V5_MR_MODEL=<model id>
```

Generated: 2026-07-29T00:46:06Z
