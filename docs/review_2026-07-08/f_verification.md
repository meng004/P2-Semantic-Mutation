# Wave-F Acceptance Verification — Study-2 v1.1 Amendment

**Verifier:** Wave-F acceptance verifier
**Date:** 2026-07-08
**Branch:** `claude/paper-journal-acceptance-kxpveo`
**Commits audited:** `c904bba` (v1.1 amendment + power_analysis_v11), `e6d4b1e` (CF/TF stratum filter), `93d4999` (packet harness)

**Verdict summary:** all six checks PASS on the audited-commit content. No publication-blocker or integrity defect found in the three commits. Findings are LOW/INFO and concern (a) live sibling work-in-progress outside these commits and (b) doc-staleness, not the audited artefacts.

---

## Check 1 — v1.1 THRESHOLD TRACEABILITY: PASS

**Determinism.** Reran `PYTHONPATH=src python scripts/power_analysis_v11.py` to completion (seed 20260708, n_sim 20000). Regenerated `data/results/power_study2_v11.json` is **byte-identical** to the committed file:
- sha256 before and after = `30ec95abf4db14be807cfedfae879ac92cb12c418391cb1c9152a6fe24b5f0cd`; `git diff` empty.

**Every registered number verified against the regenerated JSON AND the amendment text (exact quotes):**

| Quantity | JSON value | Amendment quote | Status |
|---|---|---|---|
| H1' feasibility @ M=8, X=4 | `registered_feasibility=0.843`, `registered_M=8` | §3 H1' "≥8 of the 28 … Feasibility 0.843" | ✓ exact |
| H1' M=8 is max bar ≥0.80 | `feasibility_P_ge4of5_clear_M`: M8=0.843, M9=0.65445 | §3 "M=8 is the largest bar with feasibility ≥0.80 (M=9 → 0.654)" | ✓ exact |
| H3' power P(≥3/4 positive) | `power_P_ge3of4_positive=0.9493` | §3 H3' "Simulated power 0.949" | ✓ (rounds 0.949) |
| H4' rule-of-three | `projected…rule_of_three=0.0131` (=3/229) | §3 H4' "rule-of-three 3/229 = 0.0131" | ✓ exact |
| H4' threshold / margin | `registered_threshold=0.05`, `margin=0.0369` | §3 "≤ 0.05 … margin of 0.037"; 0.05−0.0131=0.0369 | ✓ arithmetic sound |
| H2-1' δ>0 power @ n=28 | `delta_ref_0.0[28]=0.9285` | §2 table + §3 "0.9285 at n=28" | ✓ exact |
| H2-2 Δδ=0.20 power @ n=28 | `dd_0.2[28]=0.792775` | §2/§3 "0.793 … marginal" (below 0.80, disclosed) | ✓ (rounds 0.793) |
| H2-2 paired SE @ n=28 | `paired_se_by_n[28]=0.072` | §3 H2-2 "paired SE at n=28 = 0.072" | ✓ exact |

Console rerun echoed feasibility=0.843, P(≥3/4)=0.949, margin 0.0369, H2-1' 0.9285, H2-2 0.792775 — all match. H2-2 sub-0.80 shortfall is disclosed honestly in §2 ("marginally below the 0.80 target") and §3 ("marginal"), consistent with the CLAUDE.md honesty norm.

Note (not a defect): §2 contrasts "0.9285 at n=28 vs 0.9445 at n=30". The 0.9445 traces to the **v1.0** SSOT (`power_study2.json::delta_ref_0.0[30]=0.9445`), verified. The v11 recompute of n=30 gives 0.9415 (RNG-stream shift from inserting n=28 into the grid); citing the originally-registered v1.0 figure for the n=30 comparison is correct, not an inconsistency.

## Check 2 — AMENDMENT INTEGRITY: PASS

**§0 diff table (15 rows D1–D15).** Spot-checked 6 rows against the frozen v1.0 text (`PREREGISTRATION_STUDY2.md`):
- D3: v1.0 "**30 PUTs**" (L68) → v1.1 28. Real, justified (pilot removal). ✓
- D6: v1.0 H2-1 δ>0 power 0.9445 @ n=30 (confirmed in v1.0 SSOT) → H2-1' 0.9285 @ n=28. ✓
- D7: v1.0 H2-5 "≥4 of 5 operators … ≥⌈0.75·30⌉=23 of 30 PUTs" (L178-179) → H1' ≥8/28 coverage-derived. ✓
- D8: v1.0 H2-6 "within-class sign test 4/4 … Friedman χ²" (L181-182) → H3' ≥3/4 direction. ✓
- D9: v1.0 H2-7 "mean suspect_share ≤ 0.20 across the 150 cells" (L185) → H4' ≤0.05 over 140. ✓
- D10: v1.0 H2-2 confirmatory Family B (decision matrix L448) → gated not-run. ✓
All six are real, justified diffs; the remaining rows (D1/D2/D4/D5/D11-D15) are additive machinery consistent with the bodies of §2b/§5b/§5c/§7/§10.

**Pre-data attestation** (§0.1): present, blockquoted, enumerates the three verification facts (no `a4..d8` mutants, no v5 SSOTs, cache_cross Study-1-only). Independently reconfirmed under Check 6.

**ONE-SHOT rule** (§5c): prominent and complete — budget ("registered budget … mutant-count targets per cell"), **seeds** ("seeds (20260708)"), **template hash pinning** ("prompt-template version pinned by file hash"), **violation-reporting clause** ("protocol violation that must be reported as such in §10 and in the paper"). All four elements present. ✓

**H2-2 gating language** (§3 H2-2, §5b): airtight — "registered but gated", "cannot instantiate the cross-vendor comparison", "reported as **not-run** — no substitution of a same-vendor proxy for a cross-vendor arm". No same-vendor proxy claim anywhere. ✓

**Pilot {a2,b4} exclusion** stated where it matters: roster (§2c, 30−{a2,b4}=28), firewall (§2b "excluded from every confirmatory analysis": H2-1', H2-2, H1', H3', H4', industrial), H1' denominator 28 (§3, §7b), cell count **140 = 28×5** (§3 H4', §7b). ✓

**Confirmatory roster A7/B6/C7/D8 = 28** (§2c): 7+6+7+8=28. ✓ All 30 MR PUT source files (`src/p2/mrs/{a1..d8}.py`) present; the roster matches implemented files, and `family_coverage()` derives the same 28-PUT list (a2,b4 removed) in the JSON.

## Check 3 — FILTER REVALIDATION: PASS

**Audit-mode rerun (my own).** Ran `stratum_filter.audit_matrix` over the frozen `sms_track2_v4.json` (12 PUTs):
- n_mutants = **292**, n_multistratum = **29** — matches `s5_purity_v4.json` (`overall.n_multistratum_flip_ge2=29`).
- per-PUT: **B2:9, C1:2, D1:9, D3:9** (=29); categories: **CF:9, TF:20** (=29). Byte-consistent with CFTF_CONSTRAINT.md §4.

**Default-ON scope.** `single_stratum_filter_enabled()` defaults ON (env `P2_SINGLE_STRATUM_FILTER`, `_OFF` set excludes "1"). `build_pools.py` wires `SCREEN_FN` **only when flag ON AND `POOL_VERSION in ("v4","v5")`** (Study-2 versions). Study-1 pools are v2/v3 → never screened. ✓

**37 Study-1 specs byte-identical.** `git diff 47e286d HEAD -- src/p2/mutators/operator_registry.py` = **empty**; also empty vs `e6d4b1e~1`. The whole registry file is unchanged across F2, so the 37 original-PUT specs are byte-identical (pinned by `test_old_put_operators_unchanged`, `assert len==37`). ✓

## Check 4 — PACKET BLINDING: PASS

Inspected schemas + generated my own fixture packets (a2, b4/a4) via `export_generation_packets` / `export_review_packets` / `ingest_*`:
- **Generation packets carry no outcome fields.** `_assert_no_outcome_fields` (recursive KEY scan over `_FORBIDDEN_PACKET_KEY_TOKENS = sms/killed/survive/outcome/verdict/…`) passes; keys are structural only; `constraint_flag` surfaced on every operator spec. ✓
- **Review packets blinded.** Keys = {blind_id, instructions, mutant_code, operator, packet_type, put_source, response_schema, review_prompt}. No generator identity (claude/gpt/deepseek absent from flattened JSON), no `arm` key, no source key, no cell aggregate. `blind_id` is an opaque sha256 slice. The `_blind_map.json` (blind_id→source) is written as a private audit file, never inside a packet. (My crude substring scan flagged "sms"/"source" — traced to review-prompt prose and the legitimate `put_source` key; the KEY-based contract the code enforces is clean.) ✓
- **Template sha256 pinning + tamper detection.** `_pin_template` stores `sha256(PROMPT_TEMPLATE)` in each packet. I confirmed the live-template hash equals the pin (untampered), and a 1-char tamper produces a different hash → mismatch detected. (Note: pinning is an audit record; there is no automated ingest-time verifier — see Finding F4.) ✓
- **Ingestion strictness.** Reran round-trip with injected faults: missing `code`, forbidden `sms` field, invalid JSON, orphan packet — all rejected/logged, well-formed 27 still admitted; ingestion order-independent. Matches `test_packet_harness.py`. ✓

## Check 5 — CROSS-DOC CONSISTENCY: PASS (one LOW-severity staleness note)

- **Flag name** `single_stratum_filter_enabled` / `P2_SINGLE_STRATUM_FILTER` (default ON): identical across `campaign.py`, `build_pools.py`, `stratum_filter.py`, `cross_source_campaign.py`, `CFTF_CONSTRAINT.md`, `CAMPAIGN_RUNBOOK.md`. ✓
- **Thresholds:** CF/TF flip ≤1, suspect_share ≤0.05, 29/29 audit, 35.2% off-diagonal — consistent v1.1 ↔ CFTF_CONSTRAINT.md ↔ runbook. ✓
- **One-shot wording:** v1.1 §5c ↔ runbook §5b "One-shot rule (confirmatory)" ↔ packet manifest one-shot proof — consistent. ✓
- **Pilot IDs:** `{a2,b4}` consistent in v1.1 (§0.2/§2b/§2c/§10) and `power_analysis_v11.PILOT_PUTS=("a2","b4")`. No conflicting pilot-ID claim elsewhere. See Finding F2: the runbook's `{a2,a4}` references are the dry-run/packet-test smoke fixtures (a distinct construct), and the runbook (committed pre-amendment) does not yet mention the calibration pilot.

## Check 6 — INTEGRITY SWEEP: PASS (committed tree) — with WIP finding

- **No new-PUT (a4–a8, b4–b7, c4–c7, d4–d8) mutant/pool data** anywhere. ✓
- **No `*_v5` SSOTs** in `data/results/`. ✓
- **`cache_cross/` holds only `_log.json`** (Study-1 pilot). ✓ `data/study2_packets/` is gitignored.
- Legacy `*_pool_v4` dirs exist for the original-12 PUTs + non-registry `e1/e2`, added in phase-D commit `4e19374` (P1 work), predating Study-2. The §0.1 attestation is scoped to new PUTs `a4..d8` and holds. (INFO F3.)
- **Committed-tree pytest = 380 passed, 0 failed** (`pytest tests/` excluding the untracked WIP scorer tests; matches the `93d4999` commit claim of 380).
- **Working tree NOT clean:** 6 untracked files present (Finding F1).

---

## Severity-ranked findings

**F1 (LOW — outside audited commits; live sibling activity).** The §7b pre-freeze analysis scorers are present in the working tree but **untracked** and being edited live during this audit (mtimes 16:13–16:15): `scripts/compute_h1_instantiability.py`, `compute_h3_class_consistency.py`, `compute_h4_attribution.py` and their `tests/analysis/test_compute_h{1,3,4}_*.py`. Running `pytest tests/analysis/` currently shows **2 transient failures** in the H3' scorer WIP (`test_h3_boundary_exactly_three_positive_confirms`, `test_h3_friedman_degenerate_all_identical_not_computed`). These are entirely within the untracked sibling work, not in any of the three audited commits (whose committed tree is 380-green). Per the amendment's own §7b, these scorers "MUST be pre-frozen … covered by offline synthetic-fixture tests" before generation — a pre-freeze artefact is not frozen until committed and green. **Must-fix before Study-2 generation (not before accepting these three commits):** finish, green, and commit the §7b scorers.

**F2 (LOW — doc staleness).** `CAMPAIGN_RUNBOOK.md` (committed at `e6d4b1e`, before the `c904bba` amendment) does not reference the `{a2,b4}` calibration pilot or the 30→28 confirmatory split; its dry-run/packet examples use `{a2,a4}`. No flag/threshold contradiction, but the `{a2,a4}` (smoke) vs `{a2,b4}` (pilot) proximity invites confusion. Recommend a one-line runbook note distinguishing them.

**F3 (INFO).** Legacy `*_pool_v4` dirs (original-12 + `e1/e2`) share the `v4` pool path that Study-2's cross-source arm (`POOL_VERSION=v4`) will write; harmless pre-data, but the future cross-arm build will overwrite them. Consider a distinct Study-2 pool suffix or a clean step in the runbook.

**F4 (INFO).** Template-hash pinning is an audit record only; there is no automated ingest-time check that a response's originating template still matches `PROMPT_TEMPLATE`. Tamper detection works by manual hash comparison (verified). Optional hardening: assert the pin at ingest.

---

## Explicit CLEAN list (verified, no issue)

- power_analysis_v11.py regenerates `power_study2_v11.json` byte-identically (deterministic, seed 20260708).
- All 8 registered v1.1 numbers (H1' 0.843/M=8, H3' 0.949, H4' 0.0131/0.05/0.037, H2-1' 0.9285, H2-2 0.793, SE 0.072) trace exactly to the JSON and are quoted exactly in the amendment.
- §0 diff table 15 rows; 6 spot-checked against v1.0 = real, justified diffs.
- Pre-data attestation present; ONE-SHOT rule complete (budget/seeds/template-pin/violation clause); H2-2 gating airtight; pilot {a2,b4} exclusion consistent; roster A7/B6/C7/D8=28 matches implemented PUT files; H1' denom 28; cells 140.
- Filter audit reproduces 29/29 (B2:9,C1:2,D1:9,D3:9 / CF:9,TF:20); default-ON only for v4/v5; Study-1 pools never screened; operator_registry.py byte-identical to 47e286d (37 specs pinned).
- Packets: generation no-outcome-fields; reviews blinded (no source/arm/aggregate/generator-identity keys); template pin tamper-detects; strict ingestion rejects malformed (missing code / forbidden field / invalid JSON / orphan) and is order-independent.
- Cross-doc flag name, thresholds, one-shot wording, pilot IDs consistent.
- No new-PUT mutant data, no v5 SSOTs, cache_cross Study-1-only; committed-tree pytest 380 passed; no tracked file modified.
