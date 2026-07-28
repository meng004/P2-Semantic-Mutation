# SSOT Reconciliation — v4 Cliff's δ (0.314 vs 0.4392)

**Date:** 2026-07-28  
**Phase:** Argumentation uplift Phase 0 (Task 0.1–0.2)  
**Status:** Pending author sign-off at REVIEW CHECKPOINT 0

## 1. Conflict surface

| Source | Value | CI (95%) | Role claimed by source |
|---|---|---|---|
| `data/results/paper_numbers_v4.json` → `rq2.cliffs_delta` (pre-fix) | **0.4392** | [0.1267, 0.7396] | unlabeled "v4" δ in aggregate SSOT |
| `submission/TOSEM_fastimpact_20260707/main.tex` H2 primary bullet | **0.314** | [0.014, 0.622] | v4 cross-source, c-class held at pre-registered partial-order (MP5) |
| Historical flag | `research/fable-p3-p12-new-argumentation-plan.md` §3.4 | — | Marked `[SSOT_RECONCILIATION_REQUIRED]` |

**Path note:** Master plan cites `submission/TOSEM_regular_20260706/main.tex`; that directory is absent in this checkout. Gate target used here: `submission/TOSEM_fastimpact_20260707/main.tex` (current TOSEM package).

## 2. Reproduction commands

### 2.1 δ = 0.4392 (MP1 / v3b post-hoc primary)

```bash
P2_PRIMARY_VERSION=v3b SMS_VERSION=v4 python3 scripts/compute_rq2.py
# → data/results/rq2_cliffs_delta_v4.json
# cliffs_delta = 0.4392361111111111 ≈ 0.4392
# delta_ci_95  = [0.1267361111111111, 0.7395833333333334]
```

Mechanism: `src/p2/config/primary.py` with `P2_PRIMARY_VERSION=v3b` reassigns c1/c2/c3 to MP1 via `data/results/c_class_mp_ranking.json` (selection-on-the-response / R11).

### 2.2 δ = 0.314 (MP5 / pre-registered frozen primary)

```bash
python3 scripts/compute_rq2_v4_mp5.py
# → data/results/rq2_cliffs_delta_v4_mp5.json
# cliffs_delta = 0.3142361111111111 ≈ 0.314
# delta_ci_95  = [0.01384548611111115, 0.6215277777777778] ≈ [0.014, 0.622]
```

Mechanism: same `sms_track2_v4.json` pool; c-class primary held at `PRIMARY_CELLS_V3` (MP5). This strips R11 chained conditioning for the source-axis contrast.

### 2.3 Aggregate SSOT rebuild (byte-stable on historical `rq2`)

```bash
P2_PRIMARY_VERSION=v3b SMS_VERSION=v4 python3 scripts/build_paper_numbers.py
git diff data/results/paper_numbers_v4.json
# Before dual-key enrichment: DIFF EMPTY for rq2.* numeric fields
# (recompute with identical env reproduces 0.4392 / CI / means).
```

## 3. Root cause

Both numbers are **correct for different estimands** on the same mutant pool:

1. **Not a script bug / not silent data drift.** Rebuilding `paper_numbers_v4.json` under `P2_PRIMARY_VERSION=v3b` yields `rq2.cliffs_delta = 0.4392` with empty numeric diff vs the committed file.
2. **Ambiguous SSOT labelling.** `paper_numbers_v4.json::rq2` historically stored the **MP1/v3b sensitivity** slice without saying so in-key. Manuscript H2 primary correctly cites the **MP5** slice from `rq2_cliffs_delta_v4_mp5.json`.
3. **Default-env trap.** `P2_PRIMARY_VERSION` defaults to `"v3"` (MP5). A naive `SMS_VERSION=v4 python3 scripts/build_paper_numbers.py` without `P2_PRIMARY_VERSION=v3b` would rewrite `rq2` to 0.3142 and break the historical sensitivity lineage. Dual keys remove that foot-gun.

Prior audit consensus (kept): `docs/review_20260709/evidence_support_assessment.md` — MP5 = H2 primary; MP1 = sensitivity; do not headline 0.439.

## 4. Ruled values (proposed; awaiting CHECKPOINT 0)

| Estimand ID | SSOT key (post-fix) | Ruled point / CI | Narrative use |
|---|---|---|---|
| H2 primary (frozen MP5) | `rq2_primary_mp5.cliffs_delta` | **0.3142** / [0.0138, 0.6215] (report 0.314 / [0.014, 0.622]) | Abstract / H2 verdict / source-axis contrast |
| Sensitivity (MP1 / v3b) | `rq2.cliffs_delta` | **0.4392** / [0.1267, 0.7396] | Sensitivity / development-only; never headline |
| H2 threshold | `rq2.h2_threshold_delta` | 0.474 | Unchanged; both estimands fail the threshold |

**Verdict unchanged:** H2 large-effect criterion not met under primary.

## 5. Fixes applied this Phase

1. `scripts/build_paper_numbers.py` — when `SMS_VERSION=v4`, emit `rq2_primary_mp5` from `rq2_cliffs_delta_v4_mp5.json`; tag `rq2.estimand`; reserve `SMS_strict` / `SMS_cons` (null) for theory T5.2 (R-7).
2. `data/results/paper_numbers_v4.json` — rebuilt; historical `rq2` numerics unchanged; new dual keys added.
3. `scripts/check_ssot_consistency.py` — manuscript↔SSOT gate; hard-fails if v4 primary block ≠ `rq2_primary_mp5` or if dual-estimand keys collapse/missing.
4. Manuscript `main.tex` — **no numeric edit required** (primary already 0.314 / [0.014, 0.622]).

Gate command (path adapted):

```bash
python3 scripts/check_ssot_consistency.py \
  submission/TOSEM_fastimpact_20260707/main.tex \
  data/results/paper_numbers_v4.json
# expected: PASS (exit 0)
```

## 6. Deferred (Task 0.2 Step 2b)

Key migration `SMS → SMS_strict` + add `SMS_cons` waits on theory Task T5.2. Placeholder keys are present as `null`. Migration report path when triggered: `docs/review_20260728/ssot_key_migration.md` (Phase 4 number-injection gate).

## 7. Author attention items (CHECKPOINT 0)

1. **Confirm ruled table in §4** (primary = 0.314 / sensitivity = 0.4392).
2. **Narrative hygiene (non-blocking for this gate):** RQ4 means table still shows aligned/cross **0.275 / 0.061** (MP1 slice) immediately above the MP5 primary δ = 0.314 bullet. Recommend either (a) switch table to MP5 means 0.213 / 0.077, or (b) explicitly label the table as the MP1 sensitivity slice. Not changed in Phase 0 pending author choice.
3. After sign-off: every subsequent manuscript number edit must pass `check_ssot_consistency.py`.
