# MR_SOURCE_SYMMETRY — EXP-DIS held-out provider checklist

Seed: `20260728`. v4 sources (FORBIDDEN for held-out): claude, gpt, deepseek.
Design: s = 2 held-out MR-set replicates from two distinct non-v4 families (strengthens the provider-singularity answer, power_report.md §3).

## Selected providers (author-directed preference + deliverability probes, 2026-07-29)

Author instruction (2026-07-29): prioritise gpt-5.5 / gemini-3.5-flash / grok-4.5 / deepseek-v4-flash / glm-5.2 / qwen3.7-plus / minimax-m2.7. Filtered by (a) the frozen held-out family constraint (NOT Claude/GPT/DeepSeek → gpt-5.5, deepseek-v4-flash ineligible for the MR arm) and (b) deliverability probes (MAX_TOKENS=16000, temperature 0.7): gemini-3.5-flash finish=stop ✓; grok-4.5 finish=stop ✓; glm-5.2 finish=length/empty ✗; qwen3.7-plus finish=length ✗; minimax-m2.7 finish=length/no fenced block ✗. Earlier 800-token probes (gemini-2.5 family, glm-4.7, qwen3-235b, kimi, minimax-m2.5) are archived in git history; the prior partial run (qwen3-235b + glm-4.7) is preserved under `data/v5/mrs/raw_prior_run_qwen_glm/`.

| Set | Family | Model | Credential | Slots won |
|---|---|---|---|---|
| 1 | gemini | `gemini-3.5-flash` | api_key_1 (shared with generation arm; family-level held-out-ness is the operative criterion, noted for transparency) | 44/60 |
| 2 | grok | `grok-4.5` | api_key_1 (shared with generation arm; family-level held-out-ness is the operative criterion, noted for transparency) | 46/60 |

## 7-item symmetry checklist

| # | Item | v4 value | v5 held-out value | Status |
|---|---|---|---|---|
| 1 | Prompt text | SHA-256 `06fa552d7431cecc00120bddeb4e8cdc4511ce03f695139809b5af83508a3e90` (cross_source_campaign.PROMPT_TEMPLATE; v4 had no MR-generation arm) | ONE fixed template shared verbatim by both sets and all slots, v4-matched structure/parameters; SHA-256 `b25d6d47099259c9a33e468f236eceec69ca906c205e2ec4304bc4b56ef21a06` | ✅ |
| 2 | Parser version | `cross_source_campaign._strip_fences (```python fence extractor)` | same function (replicated verbatim) | ✅ |
| 3 | Temperature | `0.7` | `0.7` | ✅ |
| 4 | Candidate count / K trials | K=`3` per (op, source) | K=`3` per (PUT, MP, set) slot | ✅ |
| 5 | Repair / retry budget | no auto-repair beyond K attempts | none beyond K candidates (first prescreen pass wins) | ✅ |
| 6 | Max tokens | `800` (cross_source_campaign._generate_one) | `16000` | ✅ |
| 7 | Provider identity | Claude / GPT / DeepSeek | set1 `gemini-3.5-flash`, set2 `grok-4.5` — both non-v4 families | ✅ |

## Prescreen (ex-ante, kill-blind)

1. Compiles; defines callables `r`, `R`; imports restricted to math/numpy.
2. Domain safety: `r` maps probes {0.1,0.3,0.5,0.7,0.9} to finite values in [0,1] ((0,1] for a3); `R` returns bool on a probe output pair.
3. Instrument validity: `AVP(original, mr) == PASS` under the frozen v4 dispatcher (epsilon 1e-6). An MR that fails on the original can never kill (kill requires original PASS), so it is a broken instrument, not evidence.
4. First passing candidate wins; K=3 exhausted -> slot EMPTY, recorded; the affected (cell, condition) is excluded + logged downstream (never imputed, never treated as observed zero).

MR prompt template SHA-256: `b25d6d47099259c9a33e468f236eceec69ca906c205e2ec4304bc4b56ef21a06` (fixed before any kill execution; kill matrices run only after this file + funnel are committed).

Generated: 2026-07-29T05:33:18Z
