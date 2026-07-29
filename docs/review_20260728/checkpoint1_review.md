# REVIEW CHECKPOINT 1 — Execution Record (author-delegated)

**Date:** 2026-07-29 · **Trigger:** author instruction "请评审checkpoint 1。通过，则并行phase2和phase3."  
**Scope:** full prereg package (matrix / power-feasibility config / hypotheses full set / external protocol / freeze manifest + tag).

## 1. Verification results (commands executed this session)

| # | Check | Result |
|---|---|---|
| 1 | `shasum -a 256 -c FREEZE_MANIFEST.sha256` | 15/15 OK (re-verified after Amendment #1: all OK) |
| 2 | Tag `prereg-v2-freeze` exists locally + on origin | ✅ (`eaa400d…`) |
| 3 | Synthetic smoke suite `smoke_all.py` | 7/7 PASS (re-run) |
| 4 | Cross-document constants (n_app=51, MID 0.33, density 16, s=2, seed 20260728, 12/15 bar, J≥6 floor) | consistent across matrix / power report / hypotheses / protocol |
| 5 | Matrix in-header content hash | **DEFECT FOUND**: original recipe self-referential (marker string's first occurrence in header prose → scope contained the hash placeholder → could never re-verify). Body (all rulings) proven byte-identical to creation commit `2b36c81`. **Repaired as Amendment #1** (`6c5bbf1`), single-commit rule honoured, manifest regenerated. Validity-repair class; no claim touched. |
| 6 | Phase-1 acceptance metrics (master §1.7 row) | 矩阵 20 格全裁定+分歧记录 ✅ · 功效报告覆盖 6 假设+预算算术表 ✅ · 5+1+B 组判据与降级路径齐备 ✅ · FREEZE_MANIFEST 覆盖（AMENDMENTS 除外）✅ · tag 存在 ✅ |

Substantive decisions were already probe-audited at the pre-review (`prereg_prereview.md`): arbitrations UPHELD with intervention evidence; H-ZERO cliff published; H-CAL interval ruling and H-RANK floor passed the §10.1 anti-over-defence audit.

## 2. VERDICT: **CHECKPOINT 1 PASSED** (with Amendment #1 recorded)

Matrix header ratification note: the "author ratification pending" flag in the matrix header is discharged by this delegated checkpoint; any later flip of CE×c2 / SI×b3 goes through AMENDMENTS (conclusions robust to flips per pre-review §2).

## 3. Execution dispatch (per author instruction: Phase 2 ∥ Phase 3)

Environment capability audit for the execution phases:

| Capability | Status | Consequence |
|---|---|---|
| LLM API keys (Claude/GPT/DeepSeek/BLTCY) | **absent** (only `github_token`) | Tasks 2.1/2.2 (v5 mutant + held-out MR generation) = pipeline-prep + BLOCKED; **no fabrication permitted** |
| Kill/MR infrastructure (`data/mr_export/*_MP*_mr.json`, `src/p2/mrs/*`, `scripts/sms_campaign.py`) | **present** | Task 2.3 EXP-DOSE fully executable in-VM (960 kill judgments) |
| cosmic-ray v4 artifacts + AST audit scripts | present | Task 2.4 EXP-STR executable (v4 pool; v5 addendum deferred) |
| Defect4MR 64-pool artifact (P12 repo / Zenodo release) | **absent from workspace** | Task 3.1 re-adjudication of the 64 pool BLOCKED; admission scaffold + real supplementary mining via read-only `gh` proceed |
| Two human annotators | not available to an agent | Task 3.2 = packet/tooling prep only; BLOCKED on humans (R-4 fallback still needs one human) |
| Theory Phase T3 (THM-WIN draft) | present on theory branch (`2db25b9`) | Task 3.3 theory gate satisfiable, but 3.3 still sequenced behind 3.1/3.2 |

Dispatch: Phase 2 → `cursor-grok-4.5-high-fast` (as stipulated). Phase 3 → stipulated `gpt-5.6-terra-max` unavailable in this environment; **stand-in `gpt-5.6-sol-xhigh`** (same substitution as Rater B, disclosed).  
Ordering discipline: EXP-DOSE per-curve windows (Δ_r+2η̄) are estimated from original programs only and **committed before any dose-run artifact** (hypotheses §5.2), enforced by a two-pass dispatch with a parent-mediated commit between window freeze and execution.
