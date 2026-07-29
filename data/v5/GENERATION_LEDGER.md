# GENERATION_LEDGER — POOL-SEM v5 (Task 2.1)

Status: **BLOCKED on API keys** (PASS-1 prep only; no LLM outputs fabricated).

## Knowable-now configuration

| Field | Value |
|---|---|
| Generator script | `scripts/v5/generate_v5_mutants.py` |
| Generator version | `v5.0.0-pass1-prep` |
| Base seed | `20260728` |
| Prompt source | `scripts/cross_source_campaign.py` `PROMPT_TEMPLATE` (verbatim) |
| Prompt SHA-256 | `06fa552d7431cecc00120bddeb4e8cdc4511ce03f695139809b5af83508a3e90` |
| Temperature | `0.7` |
| Parser | `cross_source_campaign._strip_fences` (replicated in generate_v5_mutants) |
| n_app | `51` (applicability_matrix.md §3; hardcoded with provenance comment) |
| Target confirmed / cell | `16` |
| Attempts budget / cell | `18` (= ceil(16 × 1.117)) |
| Mutant ID scheme | `mut-<OP>-<PUT>-<序号>` |
| Output pools | `data/v5/pools/` |
| Funnel SSOT | `data/v5/funnel_v5.json` (schema for `analysis_hcons.py`) |

## Required env vars (fail-fast)

| Var | Purpose |
|---|---|
| `BLTCY_API_KEY` | OpenAI-compatible API key (v4 generator path) |
| `BLTCY_BASE_URL` | OpenAI-compatible base URL |
| `V5_GENERATOR_MODEL` | optional; default `gpt-4o` |

## Per-cell ledger (filled on live run)

| cell | attempts | parse | build | trigger | E1∧E2 | confirmed | certificate | timestamp |
|---|---|---|---|---|---|---|---|---|
| *(51 rows — see funnel_v5.json; all zeros while BLOCKED)* | | | | | | | | |

## Held-out MR source (Task 2.2)

See `data/v5/MR_SOURCE_SYMMETRY.md`. Required: `V5_MR_API_KEY`, `V5_MR_BASE_URL`, `V5_MR_MODEL`.
Provider ranking: Gemini > Qwen > Mistral > Llama-hosted (none of Claude/GPT/DeepSeek).

## Timestamps

| Event | Time (UTC) |
|---|---|
| PASS-1 ledger template written | 2026-07-29 (phase-2 executor) |
| Live generation start | *pending keys* |
| Live generation end | *pending keys* |
