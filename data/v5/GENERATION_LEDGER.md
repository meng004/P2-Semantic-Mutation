# GENERATION_LEDGER — POOL-SEM v5 (Task 2.1)

Status: **COMPLETE** (live run; keys injected 2026-07-29).

## Run configuration

| Field | Value |
|---|---|
| Generator script | `scripts/v5/generate_v5_mutants.py` |
| Generator version | `v5.1.0-live` |
| Generator model | `gpt-4o` |
| Base seed | `20260728` (nominal; provider sampling is not seed-reproducible, raw outputs archived under `data/v5/raw_candidates/`) |
| Prompt source | `scripts/cross_source_campaign.py` `PROMPT_TEMPLATE` (verbatim) |
| Prompt SHA-256 | `06fa552d7431cecc00120bddeb4e8cdc4511ce03f695139809b5af83508a3e90` |
| Temperature | `0.7` |
| Max tokens | `800` |
| Parser | `cross_source_campaign._strip_fences` (replicated) |
| n_app | `51` (applicability_matrix.md §3) |
| Target confirmed / cell | `16` |
| Attempts budget / cell | `18` (= ceil(16 × 1.117)) |
| Confirmation | E1∧E2 non-equivalence: E2 K_eq=1000 uniform[0,1] seed 42 eps 1e-6; E1 AVP coherence over the PUT's 5 hand-coded MRs (v4 sms_campaign constants) |
| Dedup | exact SHA-256 of parsed code within cell（冻结 H-CONS 输入口径；见下节双口径敏感性） |
| Mutant ID scheme | `mut-<OP>-<PUT>-<NN>` (NN = confirmed order) |
| eff stratum labels | generation-time: CE→1 OS→2 HP→3 TF→4 SI→5 (ex-ante, applicability_matrix.md §7) |
| Output pools | `data/v5/pools/` (+ per-cell `manifest.json`) |
| Funnel SSOT | `data/v5/funnel_v5.json` (schema for `analysis_hcons.py`) |

## Per-cell funnel (attempts → parse → build → trigger → E1∧E2 → confirmed)

| cell | attempts | parse | build | trigger | E1∧E2 nonequiv | dup | confirmed | certificate |
|---|---|---|---|---|---|---|---|---|
| CE×a1 | 18 | 18 | 18 | 18 | 15 | 3 | 15 | 15 |
| CE×a2 | 18 | 18 | 18 | 18 | 7 | 11 | 7 | 7 |
| CE×a3 | 18 | 18 | 18 | 18 | 18 | 0 | 16 | 16 |
| CE×b1 | 18 | 18 | 17 | 17 | 14 | 3 | 14 | 14 |
| CE×b2 | 18 | 18 | 18 | 18 | 18 | 0 | 16 | 16 |
| CE×b3 | 18 | 18 | 18 | 18 | 3 | 15 | 3 | 3 |
| CE×c1 | 18 | 18 | 18 | 0 | 0 | 0 | 0 | 0 |
| CE×c2 | 18 | 18 | 18 | 18 | 18 | 0 | 16 | 16 |
| CE×c3 | 18 | 18 | 18 | 18 | 7 | 11 | 7 | 7 |
| OS×a1 | 18 | 18 | 18 | 18 | 2 | 16 | 2 | 2 |
| OS×a2 | 18 | 18 | 18 | 18 | 2 | 16 | 2 | 2 |
| OS×a3 | 18 | 18 | 18 | 18 | 8 | 10 | 8 | 8 |
| OS×b1 | 18 | 18 | 18 | 18 | 1 | 17 | 1 | 1 |
| OS×b2 | 18 | 18 | 18 | 18 | 13 | 5 | 13 | 13 |
| OS×b3 | 18 | 18 | 18 | 18 | 6 | 12 | 6 | 6 |
| OS×c1 | 18 | 18 | 17 | 17 | 8 | 9 | 8 | 8 |
| OS×c2 | 18 | 18 | 18 | 18 | 10 | 8 | 10 | 10 |
| OS×c3 | 18 | 18 | 18 | 18 | 16 | 2 | 16 | 16 |
| OS×d1 | 18 | 18 | 18 | 18 | 17 | 1 | 16 | 16 |
| OS×d2 | 18 | 18 | 12 | 12 | 3 | 9 | 3 | 3 |
| OS×d3 | 18 | 18 | 18 | 18 | 6 | 12 | 6 | 6 |
| HP×a1 | 18 | 18 | 18 | 18 | 13 | 5 | 13 | 13 |
| HP×a3 | 18 | 18 | 18 | 0 | 0 | 0 | 0 | 0 |
| HP×b1 | 18 | 18 | 18 | 18 | 18 | 0 | 16 | 16 |
| HP×b2 | 18 | 18 | 18 | 18 | 18 | 0 | 16 | 16 |
| HP×b3 | 18 | 18 | 18 | 18 | 18 | 0 | 16 | 16 |
| HP×c1 | 18 | 18 | 18 | 2 | 2 | 0 | 2 | 2 |
| HP×c2 | 18 | 18 | 18 | 18 | 2 | 16 | 2 | 2 |
| HP×c3 | 18 | 18 | 18 | 18 | 4 | 14 | 4 | 4 |
| HP×d1 | 18 | 18 | 18 | 18 | 17 | 1 | 16 | 16 |
| HP×d2 | 18 | 18 | 18 | 18 | 16 | 2 | 16 | 16 |
| HP×d3 | 18 | 18 | 18 | 18 | 16 | 2 | 16 | 16 |
| TF×a1 | 18 | 18 | 16 | 8 | 8 | 0 | 8 | 8 |
| TF×a3 | 18 | 18 | 18 | 18 | 12 | 6 | 12 | 12 |
| TF×b2 | 18 | 18 | 18 | 4 | 4 | 0 | 4 | 4 |
| TF×c1 | 18 | 18 | 18 | 18 | 17 | 1 | 16 | 16 |
| TF×c2 | 18 | 18 | 18 | 18 | 12 | 6 | 12 | 12 |
| TF×c3 | 18 | 18 | 18 | 12 | 12 | 0 | 12 | 12 |
| TF×d1 | 18 | 18 | 18 | 18 | 6 | 12 | 6 | 6 |
| TF×d2 | 18 | 18 | 18 | 18 | 18 | 0 | 16 | 16 |
| TF×d3 | 18 | 18 | 17 | 17 | 11 | 6 | 11 | 11 |
| SI×a1 | 18 | 18 | 18 | 18 | 15 | 3 | 15 | 15 |
| SI×a2 | 18 | 18 | 18 | 18 | 3 | 15 | 3 | 3 |
| SI×a3 | 18 | 18 | 18 | 0 | 0 | 0 | 0 | 0 |
| SI×b3 | 18 | 18 | 0 | 0 | 0 | 0 | 0 | 0 |
| SI×c1 | 18 | 18 | 18 | 2 | 2 | 0 | 2 | 2 |
| SI×c2 | 18 | 18 | 18 | 18 | 4 | 14 | 4 | 4 |
| SI×c3 | 18 | 18 | 18 | 18 | 6 | 12 | 6 | 6 |
| SI×d1 | 18 | 18 | 18 | 18 | 1 | 17 | 1 | 1 |
| SI×d2 | 18 | 18 | 18 | 18 | 2 | 16 | 2 | 2 |
| SI×d3 | 18 | 18 | 18 | 18 | 11 | 7 | 11 | 11 |

## Distinctness dual-count (CP2 review disclosure)

Frozen H-CONS consumes the exact-SHA confirmed counts above (33/51 cells ≥5; Wilson LB 0.510 → PASS). An exploratory sensitivity probe ordered by the CP2 evidence-level review re-counts the same pool under the project's EXP-STR AST normaliser (`ast.dump(annotate_fields=False, include_attributes=False)`):

| Basis | cells ≥5 | Wilson 95% CI | Gate LB > 0.5 |
|---|---|---|---|
| exact-SHA (frozen input) | 33/51 | [0.510, 0.764] | yes |
| AST-normalised (sensitivity) | 28/51 | [0.414, 0.677] | **no** |

Five cells cross below the ≥5 line under AST dedupe (OS×b2 13→2, OS×c3 16→4, TF×a1 8→2, TF×d1 6→2, OS×d3 6→3). Artifact: `data/v5/hcons_dedup_sensitivity.json`. The frozen `analysis_hcons.py` verdict stands; manuscript must state H-CONS in bounded form (exact-text PASS / AST FAIL). No amendment — analysis code untouched; distinctness operationalisation was not pinned in the freeze text.

## Held-out MR source (Task 2.2)

See `data/v5/MR_SOURCE_SYMMETRY.md`.

## Timestamps

| Event | Time (UTC) |
|---|---|
| PASS-1 ledger template written | 2026-07-29 (phase-2 executor) |
| Live generation run | 2026-07-29T02:51:41Z |
| CP2 review dual-count disclosure | 2026-07-29 (post-review amendment to ledger text only) |
