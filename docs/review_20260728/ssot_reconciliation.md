# SSOT Reconciliation — v4 Cliff's δ (0.314 vs 0.4392)

**Date:** 2026-07-28  
**Phase:** Argumentation uplift Phase 0 (Task 0.1–0.2)  
**Status:** REVIEW CHECKPOINT 0 **executed and PASSED** 2026-07-28 (execution delegated to agent by author's explicit instruction; ruling anchored to pre-registration + prior audit consensus, see §8)

> **Integration note (2026-07-29):** this document preserves the original
> Phase-0 reconciliation record. The later TOSEM M1--M8 repair superseded its
> storage layout: canonical `paper_numbers_v4.json::rq2` now contains the
> frozen MP5 primary, and `rq2_primary_mp5` is retained as an equal-valued
> compatibility alias. The MP1/v3b sensitivity remains in its dedicated raw
> result artifact and must not replace canonical `rq2`.

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

### 2.4 Intermediate-file float-repr drift (documented, not adopted)

Regenerating the intermediate `rq2_cliffs_delta_v4.json` reproduces `cliffs_delta` and `delta_ci_95` **byte-identically**, but two display-only fields drift at ≤1 ULP:

| Field | Committed | Regenerated (builtin `sum/len`) | `np.mean` (numpy 2.4.4) |
|---|---|---|---|
| `mean_aligned` | 0.27504999999999996 | 0.27505 | **0.27504999999999996** |
| `mean_cross` | 0.06124166666666666 | 0.061241666666666666 | 0.061241666666666666 |

Root cause: the committed file was produced by a script/numpy lineage using `np.mean` (pairwise summation); the current `compute_rq2.py` uses builtin `sum(...)/len(...)`. `mean_aligned` matches `np.mean` exactly; `mean_cross` differs from both at the last digit (historical numpy accumulation-order variant). Statistical content (δ, CI, medians, counts) is unaffected; the 4-decimal aggregate SSOT is unaffected. Per the Phase-0 risk rule ("不得静默取新值"), the committed intermediate is **retained**; drift documented here.

## 3. Root cause

Both numbers are **correct for different estimands** on the same mutant pool:

1. **Not a script bug / not silent data drift.** Rebuilding `paper_numbers_v4.json` under `P2_PRIMARY_VERSION=v3b` yields `rq2.cliffs_delta = 0.4392` with empty numeric diff vs the committed file.
2. **Ambiguous SSOT labelling.** `paper_numbers_v4.json::rq2` historically stored the **MP1/v3b sensitivity** slice without saying so in-key. Manuscript H2 primary correctly cites the **MP5** slice from `rq2_cliffs_delta_v4_mp5.json`.
3. **Default-env trap.** `P2_PRIMARY_VERSION` defaults to `"v3"` (MP5). A naive `SMS_VERSION=v4 python3 scripts/build_paper_numbers.py` without `P2_PRIMARY_VERSION=v3b` would rewrite `rq2` to 0.3142 and break the historical sensitivity lineage. Dual keys remove that foot-gun.

Prior audit consensus (kept): `docs/review_20260709/evidence_support_assessment.md` — MP5 = H2 primary; MP1 = sensitivity; do not headline 0.439.

## 4. Ruled values (CONFIRMED at CHECKPOINT 0, 2026-07-28)

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

## 7. Author attention items (CHECKPOINT 0) — disposition

1. **Confirm ruled table in §4** — ✅ CONFIRMED (see §8; anchored to pre-registration, not discretion).
2. **Narrative hygiene:** RQ4 means table shows aligned/cross **0.275 / 0.061** (MP1 slice) immediately above the MP5 primary δ = 0.314 bullet. **Disposition: DEFERRED to Phase 4** (Task 4.2/4.3, v2 workdir). Rationale: `submission/TOSEM_fastimpact_20260707/` is a dated submitted package (archival artifact); the plan's Phase 4 explicitly works in a copied workdir rather than editing submitted packages in place. Tracked as a Phase-4 must-fix: either switch table to MP5 means (0.213/0.077) or label it as the MP1 sensitivity slice.
3. Gate discipline **active as of this checkpoint**: every subsequent manuscript number edit must pass `check_ssot_consistency.py`.

## 8. REVIEW CHECKPOINT 0 — execution record (2026-07-28)

Author delegated checkpoint execution ("请执行review checkpoint 0，判定是否可以进入phase 1"). Acceptance metrics (master plan §1.7, Phase 0 row), all verified this session:

| # | Acceptance metric | Evidence | Result |
|---|---|---|---|
| 1 | SSOT 重生 diff=0 | `P2_PRIMARY_VERSION=v3b SMS_VERSION=v4 python3 scripts/build_paper_numbers.py` → `git diff data/results/paper_numbers_v4.json` empty; `rq2_cliffs_delta_v4_mp5.json` diff empty; intermediate repr drift documented §2.4, committed values retained | ✅ |
| 2 | `check_ssot_consistency` exit 0 | `python3 scripts/check_ssot_consistency.py submission/TOSEM_fastimpact_20260707/main.tex data/results/paper_numbers_v4.json` → PASS, exit 0 | ✅ |
| 3 | 根因文档含两冲突值复算命令 | §2.1 (0.4392) + §2.2 (0.314), both runnable | ✅ |

**Ruling basis (not agent discretion):** MP5 is the pre-registered v3 primary (`PRIMARY_CELLS_V3`, `src/p2/config/primary.py`); MP1/v3b is a data-driven post-hoc reassignment (selection-on-the-response, R11). Prior audits concur: `docs/review_20260709/evidence_support_assessment.md` ("MP5=primary、MP1=sensitivity…禁止用 δ=0.439 作 headline"), `docs/review_2026-05-02/stage_4_5_round3_revision_response.md` (0.4392 verified as the †-marked exploratory row).

**Over-defense audit (CLAUDE.md §10.1):** no claims downgraded in Phase 0 — both estimands preserved with explicit roles; H2 verdict (not met) unchanged; no thresholds moved. **Integrity scan (Reviewer-2 direction):** no silent adoption of drifted values (§2.4); no retroactive edit of the archived submission package (§7.2); dual-key SSOT removes the unlabeled-estimand ambiguity that caused the original conflict.

**VERDICT: CHECKPOINT 0 PASSED.**

**Phase 1 entry ruling:**
- **Tasks 1.1 / 1.2 / 1.4 — CLEARED to start** (master plan Phase 1 并行细则 + phase-1 split file 前置门禁 concur: these run before theory T2).
- **Task 1.3 + prereg freeze tag — BLOCKED** until theory CHECKPOINT T2 (THM-GAP internal review). Theory line status checked 2026-07-28: `理论增强-phaseT0-terra.md` and `理论增强-phaseT2-fable.md` checkboxes all unchecked → T2 not passed.
- Wording note for author: theory plan T2 checkpoint line says "此检查点通过后，论证提升计划 Phase 1 方可启动" (coarse), while the argumentation master plan (spec authority) + phase-1 split file refine this to "1.1/1.2/1.4 先行、1.3+tag 等 T2". Ruled per the master plan; recommend harmonizing the theory-plan sentence at next edit.
- Model dispatch: phase-1 split file mandates `claude-fable-5-thinking-max` ("非此模型请勿执行本文件") — Phase 1 execution must be dispatched to that model per the plan's分派 discipline.
