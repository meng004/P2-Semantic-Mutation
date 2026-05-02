# Stage 4.5 Round-2 Re-Verification Report

**Date**: 2026-05-02
**Verifier**: integrity_verification_agent (final-check mode, Round-2 focused re-verification)
**Manuscript**: `论文初稿P2_EN.md` at commit `1a5edef` (1841 lines after fixes)
**Cross-version source**: `论文初稿P2.md` (1853 lines)
**Round-1 report**: `docs/review_2026-05-02/stage_4_5_final_integrity_report.md` (BLOCK with 3 P0)
**Fix-up commit**: `1a5edef phase-D(stage-4.5 fixes): P0/P1 integrity issues from final-check report` (+19 / −22 in EN; +19 / −22 in CN)

---

## One-Line Verdict

**PASS_WITH_NITS** (3 P0s closed; 4 of 6 P1s closed; 2 residual P2 nits — non-blocking, listed below).

**Recommended action**: **Proceed to Stage 5 FINALIZE.** The two residuals are minor cosmetic / second-order numeric leftovers that do not affect a reviewer's first-pass integrity judgment.

---

## Per-Item Re-Verification Status

| ID | Round-1 Severity | Round-2 Status | Evidence |
|---|---|---|---|
| **P0-A** Tip 2024 author list | P0 BLOCK | **CLOSED ✓** | `Tip, F., Misailovic`, `Bavota` return **0 hits** in both EN/CN. Line 1706 (EN) / 1714 (CN) now reads `Tip, F., Bell, J., & Schäfer, M. (2024). LLMorpheus … arXiv:2404.09952. https://arxiv.org/abs/2404.09952`. WebFetch on arXiv:2404.09952 confirms authors are **Frank Tip, Jonathan Bell, Max Schaefer** (note: upstream uses "Schaefer" without diaeresis on arXiv; manuscript uses "Schäfer" — both are accepted transliterations of the same author, IEEE Xplore record uses the diaeresis form; not a fabrication). §1.3.2 line 73 in-text `Tip, Bell & Schäfer (LLMorpheus, arXiv 2024)` is consistent. |
| **P0-B** DeepCrime entry | P0 BLOCK | **CLOSED ✓** | `Hu, Q., Guaman` returns **0 hits**. `3540250.3549144` (the wrong DOI) returns **0 hits**. Line 1710 (EN) / 1718 (CN) now reads `Humbatova, N., Jahangirova, G., & Tonella, P. (2021). DeepCrime … ISSTA 2021. https://doi.org/10.1145/3460319.3464825`. **Crossref API verification** of `10.1145/3460319.3464825` confirms title `DeepCrime: mutation testing of deep learning systems based on real faults`, authors Humbatova/Jahangirova/Tonella (all USI Lugano), venue ISSTA '21. In-text references in §1.3.2 line 72 and §3.1.1 line 424 both updated to `Humbatova, Jahangirova & Tonella (DeepCrime, ISSTA 2021)`. |
| **P0-C** Cosmic-ray total 1276→1250 | P0 BLOCK | **CLOSED ✓** | `1276` returns **0 hits** in EN; `1250` appears at lines 591 (script-comment), 600 (table row "Total cosmic-ray syntactic mutants across 12 PUTs \| 1250"), 635 (prose "94.86% of P2 mutants are AST-disjoint with the 1250-mutant cosmic-ray output"). SSOT verified by direct Python load of `data/results/cosmic_ray_12put_ast_diff.json`: `aggregated.n_cosmic_ray_total = 1250`, `n_p2_total = 292`, `n_overlap_total = 15`, `overlap_rate_overall = 0.05137`. The 5.14% rate is unchanged (15/292) and consistent. |
| **P1-1** Abstract +89% → +91.4% | P1 advisory | **CLOSED ✓** | `+89%` returns **0 hits** in abstract context; `+91.4%` appears in abstract (line 14) and §6.3 (line 1463) and §6.1 (line 1445). Direct numerical check: v3 class_mean_c = 0.0467, v4 class_mean_c = 0.0894, ratio − 1 = +91.43%. Matches. |
| **P1-2** Abstract Spearman p version-mix | P1 advisory | **CLOSED ✓** (lead value) / **PARTIAL** (residual) | Abstract line 14 now reads `ρ = 0.16, n = 12, p = 0.61, v4 primary` — matches `paper_numbers_v4.json.rq4.spearman_p = 0.6133`. §5.9.2 line 1418 reads `Spearman ρ = 0.163 (p = 0.613) (v4 primary, paper_numbers_v4.json)`; line 1419 `Kendall τ = 0.136 (p = 0.568)` — matches v4 SSOT (kendall_tau = 0.1357, kendall_p = 0.5677). §5.9.3 line 1427 in-line repeat reads `p ≈ 0.61, 0.57`. §6.4 line 1471 leading-clause reads `p ≈ 0.61, 0.57`. **Lead values fully migrated to v4.** **Residual nit** (P2): three secondary mentions of "p = 0.74" / "p = 0.77" remain in narrative power-caveat sentences (line 434 `(n=12, p=0.74)`; line 1425 `p = 0.74 / 0.77`; line 1471 second clause `p = 0.74`). These are inside power-caveat illustrations, not primary number-reporting locations. Inconsequential for a reviewer (the headline values are correct), but slightly inconsistent with the migrated leads. Same residual present in CN at lines 434, 1431, 1479. |
| **P1-5** §5.9.2 / §5.9.3 numbers | P1 advisory | **CLOSED ✓** | §5.9.2 (lines 1418-1419): ρ = 0.163, p = 0.613; τ = 0.136, p = 0.568. SSOT verified (rq4.spearman_rho = 0.1628, kendall_tau = 0.1357). §5.9.3 (line 1427): "ρ = 0.163 and Kendall τ = 0.136 are not significantly different from zero (p ≈ 0.61, 0.57)" — consistent. |
| **P1-4** §1.3.2 orphan citations | P1 advisory | **CLOSED ✓** | `Pradel`, `Cito`, `Tian`, `DLMutation`, `DeepMutator` all return **0 hits** in both EN and CN. Per the diff: §1.3.2 related-work table reduced from 5 rows (4 orphans + 1 valid) to 3 rows (DeepCrime [Humbatova], LLMorpheus [Tip/Bell/Schäfer], Jia & Harman survey + Papadakis survey). §3.1.1 benchmark table (line 422-426) reduced from 4 rows (DeepCrime + DeepMutator + Defects4J + mutmut/cosmic-ray) to 3 rows (DeepCrime + Defects4J + mutmut/cosmic-ray). All §8 entries cited in body; no orphans. |

P1 items NOT addressed in fix-up commit (carry-over from Round-1, both still advisory):
- **P1-3** §5.8.1 class means version annotation. Lines 1336-1341 still cite v3-era values (a=0.067, b=0.156, c=0.047, d=0.081) without explicit "v3 baseline" tag. §6.3 line 1463 cites v4 explicitly (a=0.067, b=0.148, c=0.089, d=0.112). The fix-up commit did not touch §5.8.1. **Status: residual P1 advisory (unchanged from Round-1)**. Not a P0 because §5.8.1 narrative is methodology-presentation (the table is followed by sign-test analysis that uses v3 pre-registered as primary), and the §6.3 v4 numbers are explicitly tagged. A reviewer audit could still flag this, but it does not block submission integrity.
- **P1-6** Internal SSOT inconsistency `rq3_friedman_v4.json` vs `paper_numbers_v4.json.rq3.friedman_per_class_p`. Manuscript follows v3b values for per-class Friedman; this is a *data-file vs data-file* issue, not a manuscript-vs-data issue. The fix-up commit did not address it. **Status: residual P1 advisory (unchanged from Round-1)**. Pure SSOT-of-record decision; manuscript narrative is internally consistent.

---

## New-Issue Scan (introduced by the fix-up commit)

### N1 — DeepCrime domain reframing: did anything break?
**Check**: The Round-1 manuscript framed DeepCrime as "Probabilistic program mutation (MCMC, MC, Stan-style)" and claimed B-class (probabilistic) PUTs "completely overlap" DeepCrime. The fix-up commit reframed DeepCrime as "Deep learning systems (Keras/TensorFlow, real-fault-based)" — the actually-correct domain — and downgraded the overlap claim to "ML subset (D) shares topical overlap" only.

**Result**: ✓ Internally consistent. §1.3.2 line 72 says "Single class (deep learning); P2 includes ML as one of 4 classes". §3.1.1 line 424 says the topical overlap is on D (sklearn ML), not B. §3.1.1 line 428 says "classes A (numerical) / B (probabilistic) / C (surrogate) are this paper's unique extensions". This is a *more honest* framing than the original; no downstream §5/§6 claim depended on the false "DeepCrime = probabilistic / B-class overlap" framing because the original empirical analysis never invoked DeepCrime as a B-class baseline. **No regression.**

### N2 — §3.1.1 description as "deep learning systems": contradictions later?
**Check**: Searched §5/§6/§7 for any later text that still treats DeepCrime as probabilistic or that claims B-class baseline against DeepCrime.

**Result**: ✓ No remaining claims about DeepCrime in §5-§7. The DeepCrime references are confined to §1.3.2 + §3.1.1 + §8.4 (the bibliography entry). All three are now domain-correct.

### N3 — §8.4 section header
**Check**: §8.4 heading still reads "Probabilistic / numerical mutation benchmarks", but its only entries are now DeepCrime (deep learning) and Defects4J (Java general fault DB). The "Probabilistic" descriptor in the heading no longer fits.

**Result**: △ **P2 nit (cosmetic only)**. The heading is a leftover from when DeepCrime was (incorrectly) framed as probabilistic-program testing. Recommended fix (1-line edit): rename §8.4 to `Deep-learning and general fault benchmarks` or `Mutation-testing benchmarks`. Not blocking — section headings are subordinate to entry content for citation traceability.

### N4 — Spearman p secondary references not migrated
**Check**: Lines 434, 1425, 1471 (and CN counterparts) still cite "p = 0.74" / "p = 0.77" inside power-caveat illustration sentences, while the lead reporting now uses the v4 values "p = 0.61" / "p = 0.57".

**Result**: △ **P2 nit (within-paragraph version inconsistency)**. The lead values where the numbers are *first reported* are correct (v4: ρ = 0.163, p = 0.613, τ = 0.136, p = 0.568). The stale "p = 0.74 / 0.77" residuals appear only in second-mention power-caveat language ("at this sample size, p = 0.74 does not constitute evidence of no correlation" — the *form* of the power argument is unchanged whether the actual p is 0.61 or 0.74; this is a verbal artifact of the original v3 narrative). Recommended fix: 3 mechanical replacements ("p = 0.74" → "p = 0.61"; "p = 0.74 / 0.77" → "p = 0.61 / 0.57"; "n=12, p=0.74" → "n=12, p=0.61") in EN, plus the 3 CN counterparts. Estimated cost: 5 minutes. Non-blocking because (a) the lead reporting locations are all correct; (b) the qualitative argument ("not significantly different from zero at n=12") survives both p values; (c) a reviewer pattern-matching on the abstract / §5.9.2 lead numbers will not be misled.

### N5 — Independent author-name spot-check
**Check**: Verified the new attributions independently.
- arXiv:2404.09952 → Frank Tip, Jonathan Bell, Max Schaefer (manuscript renders "Schäfer"; same author, both spellings acceptable per IEEE / arXiv convention). ✓
- DOI 10.1145/3460319.3464825 → Humbatova, Jahangirova, Tonella; ISSTA '21. ✓ (via Crossref API).

**Result**: ✓ Both citations now correctly attributed to the actual upstream authors / venues / DOIs. No new fabrication.

### N6 — Class-c gain numerical recomputation
**Check**: Direct computation against v3 / v4 paper_numbers JSONs:
- v3 class_mean_c = 0.0467; v4 class_mean_c = 0.0894 → ratio − 1 = 0.91435 → +91.4%. ✓ matches abstract / §6.1 / §6.3 text.

**Result**: ✓ Number is correct. P1-1 closure verified.

---

## Summary Table

| Severity | Count | List |
|---|---|---|
| P0 BLOCK | **0** | (all 3 Round-1 P0s closed) |
| P1 advisory (carry-over, not addressed in fix-up) | **2** | P1-3 §5.8.1 v3-class-means without version tag; P1-6 internal SSOT (rq3_friedman_v4 vs paper_numbers_v4) — both already in Round-1 PASS_WITH_NITS bucket and not in this round's "must-fix" scope |
| P2 nit (newly observed) | **2** | N3 §8.4 header still says "Probabilistic / numerical" (DeepCrime is now correctly DL); N4 three stale "p = 0.74 / 0.77" residuals in power-caveat illustration text (lead numbers all correct) |
| Newly-introduced regression | **0** | DeepCrime domain reframe is internally consistent; no §5-§7 claims depended on the previous false framing |

---

## Recommended Action

**Proceed to Stage 5 FINALIZE.**

Optional 5-minute polish before submission (highly recommended for reviewer-credibility, not blocking):
1. Rename §8.4 heading to `Deep-learning and general fault benchmarks` (or similar) — 1 edit per file.
2. Replace 3 stale `p = 0.74` / `p = 0.77` residuals in power-caveat sentences with the v4 values `p = 0.61` / `p = 0.57` — 3 edits per file × 2 files.
3. (Optional carry-over) Add `(v3 baseline)` annotation to §5.8.1 class-means table caption to flag the v3-vs-v4 distinction made explicit in §6.3.

None of these affect Stage 5 readiness.

---

## Iron-Rule Independent-Verification Statement

I performed direct grep searches for every Round-1 flagged string (Tip/Misailovic/Bavota; Hu/Guaman; 1276; +89%; Pradel/Cito/Tian/DLMutation/DeepMutator) on both `论文初稿P2_EN.md` and `论文初稿P2.md`. I performed independent WebFetch verification of arXiv:2404.09952 and Crossref API verification of DOI 10.1145/3460319.3464825 to confirm the new author attributions are correct. I performed direct Python load of `data/results/cosmic_ray_12put_ast_diff.json` and `data/results/paper_numbers_v4.json` to confirm SSOT numbers (1250 cosmic-ray total; 0.6133 spearman p; 0.0894 class_c v4 mean; 0.9143 c-class gain). I did **not** modify any manuscript or script files.

The fixes are real, complete on the 3 P0s, complete on 4 of 6 P1s, and have not introduced any regression. The 2 residual P2 nits are cosmetic and do not affect Stage 5 progression.

---

*End of Round-2 re-verification report.*
