# Final Acceptance Review — Three-Study Manuscript (P3/P2)

**Reviewer lens:** combined EIC + methodology + statistics + Devil's Advocate
**Target:** ACM TOSEM, Regular Track
**Repo / branch:** `/home/user/P3-Semantic-Mutation`, `claude/paper-journal-acceptance-kxpveo`, post-commit `01a67bf`
**Prior reviews:** `j1_final_review.md` (7/10), `j2_final_review.md` (8/10), both pre-Study-3, all must-fix closed in phase-K.
**Date:** 2026-07-09

---

## 1. Study-3 verification

**Rerun** `PYTHONPATH=src python3 scripts/compute_h4_graded.py` — both verdicts reproduce **exactly**:

- **H4''-strict → CONFIRM**: purity `1.0`, one-sided 95% lower CP `0.9673` ≥ 0.90 bar, on {CE, HP, CF-with-screen}; `n=90` detected clean-family (CE 72, HP 18, CF 0).
- **H4''-graded → NOT_CONFIRMED**: rich-class mean share `0.0833`, one-sided 95% bootstrap lower `0.0` ≤ 0.15 bar; `n_rich=6` (C3–C6, D2, D5); per-class C `0.0` (4 PUTs), D `0.25` (2 PUTs).

**Number trace (≥8 required; 13 verified against SSOTs):** purity 1.0, CP-lower 0.9673, n=90/CE72/HP18/CF0, share 0.0833, boot-lower 0.0, n_rich=6 + PUT list, per-class C0.0/D0.25, 765 valid, 720 admitted / 45 rejected (families a3,b3,c1,d8), 633 pool / 678 incl {a2,b4} pilot, 140 cells / 20 nonzero-killed, 36 flagged multi-stratum. All resolve to `h4_graded_v6.json`, `sms_track2_v6.json` (independently: sum-inst 3165 = 633×5; 20 nonzero-killed cells; per-family CE 72 + HP 18 = 90), and `gen_confirmatory/campaign_log.json` (765/720, rejects a3/b3/c1/d8).

**Front-loading:** both verdicts led in §Results (`study3-scoreboard`), the scoreboard table, and the interpretation. **No overclaim:** licensed claim is exactly the registered `{CE,HP,CF-with-screen}` scope, explicitly NOT claimed for OS/SI/TF; graded miss reported factually with point estimate below bar (verdict does not rest on power alone). **Registration lineage** cited correctly: `PREREGISTRATION_STUDY3_v2.md` v2.0, pre-data attestation, supersedes only frozen H4', leaves other Study-2 verdicts untouched.

## 2. Three-study coherence

**No contradiction across the six verdict sets.** Abstract (`main.tex` L138 + `venues/tosem/build.py` L59/61) ↔ intro claim ladder (L205–219) ↔ three scoreboards ↔ inference-permissions table (both Family-G rows present, n_rich=6, n=90) ↔ conclusion findings item 9 (L3731–3746) ↔ supplementary Appendix J.6 all tell the identical story: Study 1 delimits (H1/H2/H3/H4 not met + industrial 34/34 face, modest aggregate), Study 2 confirms directionally (H1'/H2-1'/H3' confirm, H4' NOT_CONFIRMED, H2-2 gated not-run), Study 3 two-sided boundary (H4''-strict CONFIRM, H4''-graded NOT_CONFIRMED). Study-1 H4 (0.791) vs Study-2 H4' (0.1714) are distinctly labelled — no collision. The three-rung ladder is stated verbatim-consistent in abstract, intro, and conclusion.

**NOETHER naming discipline maintained:** the new section uses m_cmp / m_mono / m_inv for primary strata and reserves MP5/MP2 for registration labels ("registered labels MP5-held and MP2"). Correct per the m_xxx-primary / MPk-in-registration convention.

## 3. Incident / deviation ledger

P1–P8 + D-A1 present as rows in the supplementary consolidated ledger table; P9 disclosed in J.6 prose and in `PILOT_LOG.md` (confirmatory-phase section, pilot-phase incidents carried as D1–D3/P4–P5). **P8 story consistent across all three loci** (supplementary P8 row, main §Study-3 execution, Threats table row "Screen remediation verified in production"): v5 op-id model-source suffix → category regex reject → None → 81/81 CF/TF null-pass silent no-op → v6 op-id-tolerant all-family live screen matching 633 / flagging 36 vs v5's zero, smoke-gate loud-fail. P9 (v6 tooling wiring, only post-freeze code change, no threshold/estimand/roster touched) told consistently.

## 4. Regression sweep

Study-1/Study-2 numbers **untouched** (spot-check 6): 5.14% AST overlap, 1,250 syntactic mutants, δ_v3=0.323, 117/117 bucket split B, 34/34 real-defect face, χ²=16.76 — all present and unchanged. `pytest` **465 passed** (matches commit). Package↔source parity: bodies identical (diff is preamble-only, elsarticle authoring vs acmart TOSEM build); package `main.tex`/`supplementary.tex` carry every Study-3 number and J.6/P9. PDF page counts **main 56, supplementary 25** (verified via pdfinfo), matching commit.

## 5. Distance to stable acceptance & recommendation

**Score: 8 / 10.** Study-3 is a genuinely strong, honest, pre-registered two-sided confirmatory study with live-verified remediation and full SSOT traceability; it materially strengthens the paper over the pre-Study-3 7–8/10 baseline. No blocker or major residuals.

**Ranked residuals (all minor, all text-only, zero new analysis/experiment):**

| # | Sev | Type | Item |
|---|-----|------|------|
| 1 | minor | text-only | The 720-admitted → 633-pool transition (87-mutant drop; per-PUT, e.g. a1 36→30, d8 18→9) is unexplained in both main §Execution and the supplementary exec table. A careful reviewer will do the arithmetic and ask. Add one clause naming the post-admission instantiability/build filter. |
| 2 | minor | text-only | Cover letter (`TOSEM_regular_20260709/cover_letter.md` L78) says supplementary is "24 pages"; actual is 25 (off-by-one). |
| 3 | minor | text-only | P9 is narrated in J.6 prose + PILOT_LOG but has no row in the consolidated incident ledger table (which stops at P8). For a "P1–P9" ledger, add a P9 row for scan-completeness. |
| 4 | polish | housekeeping | Stale IST cover letter `submission/cover_letter_final.md` still references "Information and Software Technology" / Highlights / 250-word abstract; not in the TOSEM package dir, but clutter — archive per §9. |

**Recommendation: SUBMIT NOW.** The four residuals are minor text-only fixes appropriate for a same-pass cleanup or a minor-revisions round; none gate submission and none require re-running data. No further experiments are warranted — Study 3 explicitly and correctly registers no fourth study.
