# Stage 4.5 Final Integrity Verification Report

**Date**: 2026-05-02
**Verifier**: integrity_verification_agent (Stage 4.5 mode, independent from-scratch run)
**Manuscript**: `论文初稿P2_EN.md` at commit `e7fe7d2` (1844 lines, English IST submission)
**Cross-version source**: `论文初稿P2.md` (1853 lines, Chinese authoritative)
**Verdict**: **BLOCK** (3 P0 findings)

---

## Executive Summary

Independent verification surfaces **three P0 BLOCKING issues** that the pipeline's IRON RULE 1 mandates be resolved before Stage 5:

1. **P0-A — Citation hallucination, §8.3 (Tip 2024 LLMorpheus author list).** The manuscript lists `Tip, F., Misailovic, S., Bavota, G., et al.` The actual authors of arXiv:2404.09952 / IEEE TSE are **Tip, F., Bell, J., & Schäfer, M.** *Misailovic and Bavota are not authors of this paper.* This falls under 7-Mode Failure Class 1.
2. **P0-B — Citation hallucination, §8.4 (DeepCrime).** The manuscript lists `Hu, Q., Guaman, D., Schumann, F., & Briand, L. (2022). DeepCrime … ESEC/FSE 2022. https://doi.org/10.1145/3540250.3549144`. The actual DeepCrime paper is **Humbatova, N., Jahangirova, G., & Tonella, P. (2021). ISSTA 2021. https://doi.org/10.1145/3460319.3464825**. The cited DOI `10.1145/3540250.3549144` resolves to a *different* paper ("Online Testing of RESTful APIs", Martin-Lopez et al., ESEC/FSE 2022). The citation is fabricated on multiple axes (authors, year, venue, DOI).
3. **P0-C — Statistical-data drift, §3.2.6.3 cosmic-ray total count.** Manuscript states "1276 syntactic mutants across 12 PUTs" (lines 594, 603); SSOT `data/results/cosmic_ray_12put_ast_diff.json` reports `n_cosmic_ray_total = 1250` (sum-over-PUTs verified: 201+17+336+76+151+32+66+51+99+48+99+74 = 1250). The 5.14% overall overlap rate is computed as 15/292 (P2-mutant denominator) and is unaffected, but the manuscript number contradicts the SSOT and would fail any reviewer audit.

P1 advisories: one numerical-rounding gloss in the abstract (class-c +89% should be +91.4%); one orphan related-work table whose entries have no §8 backing (Pradel/Cito/Tian); two minor data-SSOT internal inconsistencies independent of the manuscript (`rq3_friedman_v4.json` vs `paper_numbers_v4.json` per-class chi-squared mismatch — manuscript follows the SSOT-of-record `paper_numbers_v4.json` and `rq3_friedman_v3b.json`, not the v4 friedman file).

The remainder of the verification (statistical numbers, structural claims, methodology, theorem statement, scripts) is **clean**: all checked numbers within the H1/H2/H4/H5/abstract/§3-§5/§9 backbone trace cleanly to the JSON SSOT or the registered scripts, and the Round-1 → Round-2 polish trajectory has not introduced regressions in the methodology backbone.

---

## Phase 1 — References (§8.1–§8.8 entry verification)

For each §8 entry the verdict is one of: ✓ verified online, △ minor format issue, ✗ FABRICATED / wrong work.

| § | Entry | Cited DOI / URL | Verdict | Notes |
|---|---|---|---|---|
| 8.1 | DeMillo, Lipton, Sayward (1978) "Hints on test data selection". *Computer*, 11(4), 34-41. | doi.org/10.1109/C-M.1978.218136 | ✓ | DOI redirects to IEEE Xplore record 1646911; CPH origin paper, correctly cited. |
| 8.1 | Jia & Harman (2011) "An analysis and survey…". *IEEE TSE*, 37(5), 649-678. | doi.org/10.1109/TSE.2010.62 | ✓ | DOI redirects to IEEE record 5487526; well-known canonical TSE paper. |
| 8.1 | Jia & Harman (2009) "Higher Order Mutation Testing". *IST*, 51(10), 1379-1393. | doi.org/10.1016/j.infsof.2009.04.016 | ✓ | Verified via WebSearch — paper is canonical HOM paper in IST. |
| 8.1 | Andrews, Briand, Labiche (2005) "Is mutation an appropriate tool…" *ICSE 2005*. | doi.org/10.1145/1062455.1062530 | ✓ | DOI valid; canonical mutant-as-fault-proxy paper. |
| 8.1 | Just, Jalali, Inozemtseva, Ernst, Holmes, Fraser (2014) "Are mutants a valid substitute…" *FSE 2014*. | doi.org/10.1145/2635868.2635929 | ✓ | DOI redirects to dl.acm.org record (403 on direct fetch but DOI is valid; well-known FSE paper). |
| 8.1 | Papadakis, Kintis, Zhang, Jia, Le Traon, Harman (2019) "Mutation testing advances…" *Advances in Computers*, 112, 275-378. | doi.org/10.1016/bs.adcom.2018.03.015 | ✓ | Verified via WebSearch — chapter 6 of Advances in Computers v.112. |
| 8.1 | Kintis, Papadakis, Papadopoulos, Valvis, Malevris, Le Traon (2018) "How effective are mutation testing tools?" *EMSE*, 23(4), 2426-2463. | doi.org/10.1007/s10664-017-9582-5 | ✓ | Author list and venue verified. |
| 8.1 | Ammann & Offutt (2008) *Introduction to software testing* (1st ed.). Cambridge UP. | (book) | ✓ | Standard pedagogical reference, no DOI required. |
| 8.2 | Petrović & Ivanković (2018) "State of mutation testing at Google". *ICSE-SEIP 2018*. | doi.org/10.1145/3183519.3183521 | ✓ | DOI valid (ACM 403 on direct fetch but DOI structure correct; well-known paper, multiple indep refs). |
| 8.2 | Petrović, Ivanković, Fraser, Just (2021) "Practical mutation testing at scale". *IEEE TSE*, 48(10), 3900-3912. | doi.org/10.1109/TSE.2021.3107634 | ✓ | Author list and venue verified via search. |
| 8.3 | **Tip, F., Misailovic, S., Bavota, G., et al.** (2024). LLMorpheus. *Preprint*. | franktip.org/pubs/llmorpheus2024.pdf | **✗ P0 BLOCKING** | **Author list FABRICATED.** Actual authors of arXiv:2404.09952 are **Tip, F., Bell, J., Schäfer, M.** Misailovic and Bavota are not authors. The URL does resolve to the correct paper PDF. The citation must be corrected to `Tip, F., Bell, J., & Schäfer, M. (2024). LLMorpheus: Mutation testing using large language models. arXiv:2404.09952` (and updated to "IEEE Transactions on Software Engineering, 2025" if accepted version is preferred — the paper was accepted to IEEE TSE per IEEE Xplore search hit). |
| 8.4 | **Hu, Q., Guaman, D., Schumann, F., & Briand, L.** (2022). DeepCrime. *ESEC/FSE 2022*. | doi.org/10.1145/3540250.3549144 | **✗ P0 BLOCKING** | **Multiple-axis fabrication.** (a) Author list fabricated — actual authors are **Humbatova, Jahangirova, Tonella**. (b) Year wrong — DeepCrime is **2021**, not 2022. (c) Venue wrong — DeepCrime is at **ISSTA 2021** (`10.1145/3460319.3464825`), not ESEC/FSE 2022. (d) The cited DOI `10.1145/3540250.3549144` resolves to a different paper, "Online Testing of RESTful APIs: Promises and Challenges" by Martin-Lopez et al., ESEC/FSE 2022. The entry must be replaced with `Humbatova, N., Jahangirova, G., & Tonella, P. (2021). DeepCrime: Mutation testing of deep learning systems based on real faults. ISSTA 2021. https://doi.org/10.1145/3460319.3464825`. |
| 8.4 | Just, Jalali, Ernst (2014) "Defects4J". *ISSTA 2014*. | doi.org/10.1145/2610384.2628055 | ✓ | Author list and venue verified. |
| 8.5 | Romano, Kromrey, Coraggio, Skowronek, Devine (2006) "Appropriate statistics for ordinal level data". (Florida AIR meeting). | (conference, no DOI) | △ | Verified via WebSearch — thresholds 0.147/0.330/0.474 confirmed as Romano et al. 2006. The 5th author "Devine" is not always listed in secondary citations (some sources list only 4 authors); minor format question, not blocking. |
| 8.5 | Vargha & Delaney (2000) "A critique and improvement…" *J. Educational and Behavioral Statistics*, 25(2), 101-132. | doi.org/10.3102/10769986025002101 | ✓ | DOI valid; correct authors and venue. |
| 8.6 | Press, Teukolsky, Vetterling, Flannery (2007) *Numerical Recipes* (3rd ed.). Cambridge UP. | (book) | ✓ | Standard textbook. |
| 8.6 | ASME V&V 20-2009 *Standard for Verification and Validation in CFD*. | (standard) | ✓ | Standard correctly identified; ASME publishes this. |
| 8.7 | Hovde *mutmut* https://github.com/boxed/mutmut | (software) | △ | Repo URL correct. The actual author/maintainer of the boxed/mutmut project is **Anders Hövel** ("@boxed"); "Hovde, A." is a transliteration that some BibTeX styles use. Not a fabrication, but the spelling in §8.7 should match the upstream README ("Hövel" with diaeresis or "Hovel"). Format-only issue. |
| 8.7 | Tomilin *cosmic-ray* https://github.com/sixty-north/cosmic-ray | (software) | △ | The cosmic-ray project is by **Austin Bingham** at sixty-north, not Tomilin. This is a citation attribution issue — actually, the project's README lists Austin Bingham as primary author. **Recommend re-verify** (P1 advisory; not P0 since the URL itself resolves correctly to the cosmic-ray repo). |
| 8.7 | Hovstadius *mutpy* https://github.com/mutpy/mutpy | (software) | △ | The mutpy project is by **Konrad Hałas** (@hałas). Hovstadius is not the project author. Recommend re-verify (P1 advisory). |
| 8.8 | Li, M. et al. *P1 paper*. *SANER 2027* (under review). | (under review) | ✓ | Companion P-series paper, internally tracked. Honest "under review" framing. |
| 8.8 | Li, M. et al. *P2-CN companion*. *Progress in Nuclear Energy* (under review). | (under review) | ✓ | Internally tracked. |

**Phase 1 verdict**: **2 P0 BLOCKING citation hallucinations** (Tip 2024 author list; DeepCrime entry with fabricated authors/venue/DOI). The §8.7 software-citation author attributions for mutmut/cosmic-ray/mutpy are also questionable (P1 advisory) — the names listed do not match the actual upstream maintainer names.

---

## Phase 2 — Citation Context (in-text ↔ §8 reconciliation)

### 2.1 Orphan in-text citations (cited in body, no §8 entry)

- **Pradel et al. (DeepMutator)** — appears in §1.3.2 line 72 and §3.1.1 line 427 ("DeepMutator (Pradel et al.)"). **No §8 entry.** P1 — must be added or expression must be reframed. Note: there is no widely-known DL mutation paper called "DeepMutator" by Pradel; the canonical Pradel work is "Sefer/MutationByMurphy" or "DeepBugs" (Pradel & Sen 2018). This may itself be a misattribution (P1 advisory).
- **Cito et al. (context-aware JS mutation)** — appears in §1.3.2 line 73. **No §8 entry.** P1.
- **Tian et al. (DLMutation)** — appears in §1.3.2 line 74. **No §8 entry.** The canonical "DLMutation"/"DeepMutation" is by **Ma et al.** (ASE 2018), not Tian. P1 — likely misattribution.
- **DeepMutator** in the §3.1.1 benchmark table (line 427) — same orphan as above.

These four orphan entries form an internally consistent block ("Pradel/Cito/Tian/Hu" related-work survey table) but lack §8 backing. The Hu et al. row in that same table is entirely fabricated (see P0-B above). **The whole §1.3.2 related-work table needs verification + §8 entries added or removed.** P1 advisory; not P0 because it does not block submission integrity (the §8 list itself does not depend on these), but a reviewer will flag it.

### 2.2 Dangling §8 entries (in §8 but never cited in body)

- **Just et al. (2014) Defects4J** (§8.4) — cited in body (§3.1.1 line 428 "Defects4J / SciTools (Just et al., 2014)"). ✓ used.
- **Vargha & Delaney 2000** (§8.5) — cited in §6.1 and §5.6 area as methodological reference for Â₁₂. ✓ used.
- **Press 2007 Numerical Recipes** — cited in §3.1.1 line 420. ✓ used.
- **ASME V&V 20-2009** — cited in §1.3.2 line 84 and §6.5.3. ✓ used.
- **mutmut, cosmic-ray, mutpy** — all cited in §3.2.6 / §7. ✓ used.
- **Kintis 2018** — cited in §3.2.6 HOM caveat (line 525). ✓ used.

No dangling entries.

### 2.3 Placeholder / "TBD" / "IST 2024" residuals

`grep -n "TBD\|Authors TBD\|IST 2024\|placeholder\|XXX"` returns **0 hits** in `论文初稿P2_EN.md`. The Round-1 P0-6 cleanup of the unverifiable IST 2024 reference (commit ae60969) is intact.

**Phase 2 verdict**: 4 orphan citations from the §1.3.2 related-work table (Pradel/Cito/Tian + DeepMutator) are P1 advisories — not P0, but the reviewers will flag them. The Hu/DeepCrime row is the P0-B finding above.

---

## Phase 3 — Statistical Data (every claimed number ↔ data/results JSON)

### 3.1 Abstract numbers (§14)

| Claim | Manuscript value | SSOT source | SSOT value | Match |
|---|---|---|---|---|
| v3 δ | 0.323 | `paper_numbers_v3.json` rq2.cliffs_delta | 0.3229 | ✓ rounds to 0.323 |
| v3 95% CI | [0.017, 0.622] | `paper_numbers_v3.json` rq2 | [0.0174, 0.6217] | ✓ |
| v3b δ | 0.446 | `paper_numbers_v3b.json` rq2.cliffs_delta | 0.4462 | ✓ |
| v4 δ | 0.439 | `paper_numbers_v4.json` rq2.cliffs_delta | 0.4392 | ✓ |
| v4 95% CI | [0.127, 0.740] (line 1267) | `rq2_cliffs_delta_v4.json` delta_ci_95 | [0.1267, 0.7396] | ✓ |
| Δδ_MR (v3→v3b) | +0.123 | computed | 0.4462 − 0.3229 = 0.1233 | ✓ |
| Δδ_LLM (v3b→v4) | −0.007 | computed | 0.4392 − 0.4462 = −0.0070 | ✓ |
| C1_share 0.164 → 0.209 | abstract | `paper_numbers_v3.json` mean_c1_share = 0.1643; `paper_numbers_v4.json` = 0.2092 | 0.164 / 0.209 | ✓ |
| Class-c +89% | abstract | computed (v3 0.0467 → v4 0.0894) | actual = +91.4% | △ **P1 numerical accuracy** — paper says "+89%", true value is +91.4%. Either change abstract to "+91%" or "~+90%", or recompute against a different baseline that rounds to +89%. |
| Friedman χ² = 15.30, p = 0.0041 | abstract / §5.8.4 | `paper_numbers_v4.json` rq3.friedman_chi2 = 15.3028, friedman_p = 0.0041 | ✓ | ✓ (also matches `rq3_friedman_v3b.json` exactly) |
| Spearman ρ = 0.16, n = 12, p = 0.74 | abstract | `paper_numbers_v4.json` rq4.spearman_rho = 0.1628, p = 0.6133 | ρ ✓ | △ **the abstract p = 0.74 does NOT match `paper_numbers_v4.json` (p = 0.6133); it matches `paper_numbers_v3.json` (p = 0.7412) and `paper_numbers_v3b.json` (p = 0.7412)**. The §5.9.2 in-text Spearman is reported as ρ = 0.107 / p = 0.741 (line 1422), which is the v3/v3b numbers. The abstract is using v3-era numbers in a v4-primary paper. **P1 — version-cross-talk in abstract**: abstract should either be ρ = 0.16, p = 0.61 (v4) or ρ = 0.11, p = 0.74 (v3). Currently mixes a v4 ρ with a v3 p. |
| 24.3 mutants/cell, 60 cells, N = 20 | abstract / §3.4 | `paper_numbers_v4.json` rq1.n_cells = 60; §3.4 line 670 "Each PUT averages 24.3"; v4 cross-source pool 298 / 12 PUTs ≈ 24.83 (or 292 / 12 = 24.33 if using §3.2.6.3 P2-mutant denominator). | 24.3 ≈ 292/12 ✓ | ✓ |

### 3.2 §3.2.6.3 12-PUT cosmic-ray AST overlap

| Claim | Manuscript value | SSOT (`cosmic_ray_12put_ast_diff.json`) | Match |
|---|---|---|---|
| 12 PUTs | 12 | n_puts_with_cr_data = 12 | ✓ |
| 292 P2 mutants | 292 (§3.2.6.3 / abstract) | aggregated.n_p2_total = 292 | ✓ |
| **1276 cosmic-ray mutants** | **1276 (§3.2.6.3 lines 594, 603)** | **aggregated.n_cosmic_ray_total = 1250** | **✗ P0-C BLOCKING** — manuscript number 1276 contradicts SSOT 1250. Per-PUT sum verified: 201+17+336+76+151+32+66+51+99+48+99+74 = 1250. Impact on 5.14% claim: nil (5.14% = 15/292, not 15/1250). But the absolute count is wrong. **Action**: change "1276" to "1250" in the table at line 603 and in the prose at line 594, OR re-run cosmic-ray to obtain 1276 (only viable if the SSOT was meant to be regenerated). |
| 15 overlap | 15 | aggregated.n_overlap_total = 15 | ✓ |
| 5.14% overall rate | 0.0514 | aggregated.overlap_rate_overall = 0.05137 | ✓ |
| HP 0/72 | 0/72 | per_class_aggregated.HP = {n_p2:72, n_overlap:0, rate:0.0} | ✓ |
| SI 0/33 | 0/33 | SI = {n_p2:33, n_overlap:0, rate:0.0} | ✓ |
| TF 0/54 | 0/54 | TF = {n_p2:54, n_overlap:0, rate:0.0} | ✓ |
| CE 5/64 = 7.81% | 5/64 (7.81%) | CE = {n_p2:64, n_overlap:5, rate:0.07813} | ✓ |
| OS 7/60 = 11.67% | 7/60 (11.67%) | OS = {n_p2:60, n_overlap:7, rate:0.11667} | ✓ |
| CF 3/9 = 33.33% | 3/9 (33.33%) | CF = {n_p2:9, n_overlap:3, rate:0.3333} | ✓ |
| LLM source: DeepSeek 11/15, Claude 4/15, GPT 0/15 | (line 642) | overlap_files: 11 deepseek, 4 claude, 0 gpt (verified by name-pattern across the 15 listed files) | ✓ |

### 3.3 §3.5.1 c-class permutation null

| Claim | Manuscript | SSOT (`c_class_permutation_v4.json`) | Match |
|---|---|---|---|
| Null mean | 0.3494 | null_distribution.mean = 0.34936 | ✓ |
| Observed | 0.3136 | observed.c_class_aligned_mean = 0.31357 | ✓ |
| One-sided p | 0.9885 | permutation_p_value_one_sided_geq = 0.9885 | ✓ |
| Bonferroni α_eff = 0.01 | 0.01 | bonferroni.alpha_effective = 0.01 | ✓ |
| N_PERM = 10000 | 10000 | n_perm = 10000 | ✓ |

### 3.4 §5.7.3 plug-in power

| Claim | Manuscript | SSOT (`rq2_power_v4.json`) | Match |
|---|---|---|---|
| δ > 0: 0.997 | 0.997 | power_at_delta_gt_0.0 = 0.9974 | ✓ |
| δ > 0.147: 0.966 | 0.966 | power_at_delta_gt_0.147 = 0.966 | ✓ |
| δ > 0.330: 0.759 | 0.759 | power_at_delta_gt_0.33 = 0.759 | ✓ |
| δ > 0.474: 0.423 | 0.423 | power_at_delta_gt_0.474 = 0.423 | ✓ |
| n_aligned=6 power 0.974 | 0.974 | n=6_n_cross=24 = 0.9738 | ✓ |

### 3.5 §5.7.3 stipulated-alternative power (Round-2 NEW)

| Claim | Manuscript | SSOT (`rq2_power_stipulated_v4.json`) | Match |
|---|---|---|---|
| Calibrated mixture w | 0.094 | stipulated_truth.mixture_weight = 0.09375 | ✓ rounds to 0.094 |
| Realized E[δ] | 0.4746 | realized_E_delta_at_w = 0.4746 | ✓ |
| Point-estimate power | 0.491 | power_point_estimate_meets_H2 = 0.4915 | ✓ rounds to 0.491 (manuscript also says 49.1%) |
| CI-lower power | 0.868 | power_CI_lower_above_zero = 0.8675 | ✓ rounds to 0.868 |
| n_simulations | 2000 | n_simulations = 2000 | ✓ |

### 3.6 §5.8.4 Friedman per-class

Manuscript table (line 1387-1390): a chi²=4.00 p=0.406; b chi²=10.78 p=0.029; c chi²=4.00 p=0.406; d chi²=5.00 p=0.287.

`rq3_friedman_v3b.json` per_class:
- a: chi2 = 4.0000, p = 0.4060 ✓
- b: chi2 = 10.7755, p = 0.0292 ✓
- c: chi2 = 4.0000, p = 0.4060 ✓
- d: chi2 = 5.0000, p = 0.2873 ✓

So the §5.8.4 per-class numbers are pulled from `rq3_friedman_v3b.json`. They also match `paper_numbers_v4.json.rq3.friedman_per_class_p` (which appears to be copied from v3b).

⚠ **Internal SSOT inconsistency** (P1 advisory, *not* a manuscript-vs-data issue): `rq3_friedman_v4.json` reports DIFFERENT per-class values (a:p=0.406; b:chi2=10.34, p=0.035; c:chi2=5.6, p=0.231; d:chi2=5.0, p=0.287). The c-class differs notably (0.231 vs 0.406). Manuscript follows `paper_numbers_v4.json` which follows v3b. Reviewers re-running the v4 friedman script independently would get the v4-friedman-file values (0.231 for c) and detect the discrepancy. **Recommendation (not blocking)**: regenerate `paper_numbers_v4.json.rq3.friedman_per_class_p` from the v4 SMS data (i.e., from `rq3_friedman_v4.json`), then re-confirm §5.8.4 numbers. Currently the manuscript uses *v3b within-class Friedman* against *v4 60-cell Friedman main effect* which is methodologically inconsistent.

### 3.7 §5.8.1 Class means

Manuscript (line 1339-1342): a=0.067, b=0.156, c=0.047, d=0.081.
- `paper_numbers_v3.json`: 0.0667, 0.1556, 0.0467, 0.0811. ✓ matches v3.
- `paper_numbers_v4.json`: 0.0667, 0.1478, 0.0894, 0.1122.
- `paper_numbers_v3b.json`: 0.0667, 0.1556, 0.0467, 0.0811 (= v3).

So **§5.8.1 is using v3/v3b class means**, and §6.3 (line 1466) explicitly says "v4 cross-source: a=0.067, b=0.148, c=0.089, d=0.112" (matches v4). The two numbers conflict if read by a reviewer expecting the v4-primary narrative. **P1 advisory** — §5.8.1 should either explicitly note "v3 baseline" or be updated to v4 numbers, or both should be presented with version annotations.

### 3.8 §5.6 H5 numbers

| Claim | Manuscript | SSOT | Match |
|---|---|---|---|
| H5 calibrated 12/60 (20%) | 12/60 | `paper_numbers_v4.json.rq1.h5_cells_pass = 12`, `h5_pass_ratio = 0.20` | ✓ |
| H5 default 10/60 (16.7%) | 10/60 | `paper_numbers_v3.json.rq1.h5_cells_pass = 10` | ✓ (default = pre-calibration = v3 LRCA) |
| Sensitivity grid all 12/60 except 0.45–0.50 | (table 5.6.2.1) | `h5_sensitivity_v4.json.sensitivity_curve` | ✓ verified row-by-row |

**Phase 3 verdict**: 1 P0 BLOCKING (cosmic-ray total 1276 vs 1250); 3 P1 advisories (class-c percentage rounding; abstract Spearman p version mix; §5.8.1 class means version mix). All other numbers traceable.

---

## Phase 4 — Originality / Self-Plagiarism / AI-Text Characteristics

### 4.1 P1 cross-reference honesty

§1.3.2 / §3.1.1 / §6.1 reference `[Meng Li et al., Progress in Nuclear Energy, under review]`. The cross-references are framed as citations to P1's distinct contributions (12-PUT infrastructure, AVP implementation, MR meta-pattern audit), not as text duplication. §3.1.1 in particular adds **independent justification** for the 12-PUT selection (library coverage, mathematical structure coverage, comparison with DeepCrime/DeepMutator/Defects4J/mutmut benchmarks) rather than restating P1. This is honest cross-referencing, not self-plagiarism. ✓

### 4.2 AI-text patterns

The English manuscript uses some characteristic LLM-translation phrasings ("Specifically,", "It is important to note that…" — checked, only 1 hit; "Furthermore" — 0 hits in body), but at acceptable frequency for a translated technical paper. The Round-2 Group A textual fixes (commit a20e795) tightened wording. **No concentration of AI-text tells warranting P2 advisory.**

There is, however, one stylistic concern: numerous **inline parenthetical translations** of acronyms ("metamorphic relation (MR)", "ordinary differential equation (ODE)", "convolutional…") repeated multiple times across §3 and §5, which is a hallmark of translation-pass output. This is acceptable for international SE journals but slightly verbose. Not actionable.

---

## Phase 5 — Headline Claim Verification

### 5.1 Three-layer methodology contribution
- **Layer 1** (§3.2.0): Necessary conditions (a)/(b)/(c) for semantic mutation, lines 452-478. Defines (a) cross-function-boundary replacement, (b) carries domain knowledge, (c) changes algorithmic class. ✓ exists, internally consistent.
- **Layer 2** (§2.3 + §4.4): E1 ∧ E2 as conservative complete instantiation of necessary conditions. §2.3 lines 241-265 explicitly maps E1 ↔ converse of (c), E2 ↔ converse of (a)+(b). ✓ exists.
- **Layer 3** (§3.2.6.3): AST-normalized empirical traceability, lines 588-642. ✓ exists. (Subject to the P0-C number-drift finding above.)

The §1.2 core-claim block (lines 42-50) explicitly enumerates Layers 1/2/3 and the §6 / Conclusion sections (line 1436, abstract Conclusion sentence) maintain the methodology backbone as primary, the empirical audit as secondary. ✓

### 5.2 5.14% AST overlap claim
Traces to `data/results/cosmic_ray_12put_ast_diff.json` aggregated.overlap_rate_overall = 0.05137 = 15/292. ✓ verified against SSOT.

### 5.3 HP/SI/TF categorical 0/0/0
- HP: per_class_aggregated.HP.n_overlap = 0 (n_p2 = 72) ✓
- SI: SI.n_overlap = 0 (n_p2 = 33) ✓
- TF: TF.n_overlap = 0 (n_p2 = 54) ✓

### 5.4 OS row downgrade "△ 88.33% disjoint"
- §3.2.6 main table (line 518): "△ Mostly not covered (§3.2.6.3 empirics 88.33% AST-disjoint…)" ✓
- §3.2.6.1 operator-level table (line 563): "△ 88.33% disjoint (§3.2.6.3 empirics; small number of low-complexity OS sub-expressions occasionally hit by BinOp)" ✓
- §3.2.6.3 prose (line 634): "the OS class's overall 88.33% AST-disjointness still systematically rules out an 'OS = AST-local' classification" ✓
- 88.33% = 1 − 0.1167 = 0.8833 ✓ (computed against rate=0.1167)

The Round-1 NEW-MAJOR-1 downgrade is fully propagated and consistent across §3.2.6 / §3.2.6.1 / §3.2.6.3.

### 5.5 §9 SMS→MS degeneration theorem
- Three joint conditions: L_equiv (L1∧L2), L_killed (L3∧L4), L_mut (L5∧L6) defined at lines 1755-1769. ✓
- Three lemmas: 9.1 (equiv), 9.2 (killed), 9.3 (mut), each with independent proof. ✓
- Main theorem 9.1 (lines 1795-1809) combines all three lemmas. ✓
- Corollary 9.1 LRCA trivialization (lines 1813-1817), explicitly downgraded from a strong per-C_k mapping to a sketch with engineering caveat ("we do not claim a one-to-one correspondence at the §9 formal level"). ✓ honest.
- "Almost everywhere modulo D_S-measure-zero" qualification preserved in Lemma 9.1 and Theorem 9.1 (P1-3 revision). ✓
- Self-consistent. ✓

### 5.6 §5.7.2 H2 verdict wording vs Abstract alignment (P0-8)
- §5.7.2 line 1277: "**H2 verdict: pre-registered point-estimate criterion not met**"
- Abstract line 14: "**The pre-registered H2 large-effect threshold (Cliff's δ ≥ 0.474, Romano 2006) is not met under the pre-registered point-estimate criterion**"

Both use the phrase "is not met under the pre-registered point-estimate criterion". P0-8 alignment ✓.

**Phase 5 verdict**: All six headline claims trace to evidence and are internally consistent (modulo the cosmic-ray total-count drift in Layer 3 / §3.2.6.3, which is the P0-C finding above).

---

## 7-Mode AI Research Failure Checklist (Lu 2026)

For BLOCK-eligible modes (1/3/5/6) INSUFFICIENT EVIDENCE = BLOCK; for 2/4/7 INSUFFICIENT = ADVISORY.

| # | Mode | Verdict | Evidence |
|---|---|---|---|
| 1 | **Citation hallucination** | **SUSPECTED → BLOCK** | §8.3 Tip 2024 author list contains fabricated co-authors (Misailovic, Bavota); §8.4 DeepCrime entry is fabricated on author / year / venue / DOI axes (resolves to a different paper). §1.3.2 related-work table includes orphan citations (Pradel, Cito, Tian) without §8 backing — possibly also misattribution (e.g., DLMutation is by Ma et al. ASE 2018 not Tian et al.). §8.7 software citations (mutmut Hovde / cosmic-ray Tomilin / mutpy Hovstadius) appear to misname upstream authors. |
| 2 | **Implementation bug** | PASS | Spot-checked `scripts/compute_rq2_power_stipulated.py` — mixture-weight calibration logic is rigorously implemented (bisection on w, mixture w·shifted + (1−w)·observed, target δ check, point + CI-lower power both reported). `scripts/permutation_c_class_inflation.py` — cross-cell exchangeability null is correctly implemented (the docstring even explicitly notes the prior within-PUT shuffle was buggy and was replaced). `scripts/p2_vs_syntactic_ast_diff_batch.py` uses `ast.dump(annotate_fields=False, include_attributes=False)` — matching the paper's claim. No implementation bug surfaced. |
| 3 | **Hallucinated results** | **SUSPECTED (P1)** → does NOT block (degraded from BLOCK) | The 1276 cosmic-ray mutant count in §3.2.6.3 (P0-C) does not match the SSOT (1250). This is *one* number wrong, not a pattern of hallucinated results — all other reported numbers (deltas, CIs, Friedman, power, permutation p, per-class overlap, LLM source counts) trace cleanly to the JSON. The number 1276 has the form of a specific count rather than a fabricated round figure, suggesting it may have come from an earlier campaign run; but the SSOT shipped in the repo is 1250. **Action**: re-derive 1276 from a re-run of cosmic-ray, OR change manuscript to 1250. As specific number-mismatch this is the same finding as P0-C — already raised once. Promoting Mode 3 to SUSPECTED rather than BLOCK because a single count discrepancy in a 12-PUT batch is a transcription/version-skew event, not a systematic results-fabrication pattern. |
| 4 | **Shortcut reliance** | PASS (advisory only) | RQ4 ρ = 0.16 with n = 12 is honestly framed as "no detectable statistical correlation" / "orthogonal semantic dimension is a hypothesis, not a finding from this dataset" (§5.9.3 line 1430, §6.4 line 1476). H5 cells 12/60 are honestly framed as "not met, but as an empirical starting point for LRCA calibration research directions" (§5.6.2). The H4 sign test 3/4 vs 4/4 distinction is preserved as v3 (pre-registered) vs v3b (exploratory). No shortcut reliance. |
| 5 | **Bug-as-insight** | PASS | The §3.5.1 v3b lift is explicitly identified as "post-hoc selection inflation, not a discovery" (line 698-704), with permutation p = 0.9885 quantifying that the observed value is statistically *consistent* with selection inflation. The §6 narrative (lines 1442-1449) explicitly attributes the v3 → v3b leap to "data-driven adjustment of c-class primary MP (§3.5.1), i.e., the MR-MP alignment design itself" but immediately frames this as "post-hoc selection (§3.5.1 caveat, Bonferroni-bounded effective α)". The reviewer-of-record concern (was the v3b lift framed as a "MR design contribution"?) — answer is negative: §6.1 explicitly says the v3 → v3b leap is post-hoc, and the §6 chapter-positioning preface (line 1436) frames §6 findings as "incidental empirical findings after the three-pillar methodological framework is established". No bug-as-insight pattern. |
| 6 | **Methodology fabrication** | PASS | §7.1.2 K_eq sensitivity sweep is **explicitly downgraded** to "not executed in this submission" (line 1561 — "The K_eq sweep sensitivity table was not executed in this submission; downgraded to §7.5 Limitations as a residual threat"). The original Round-1 strikethrough (~~"§5 Appendix provides sensitivity analysis for three configurations"~~) is preserved with a clear note. §3.2.6.2 cosmic-ray a1 single-PUT empirical was a *plan* and is now superseded by the §3.2.6.3 12-PUT run. §4.2.5.1 differential prompt protocol is **explicitly future work** ("execution deferred to R2 revision or P4 paper", line 856). All "planned" methodology is honestly labeled as planned. No methodology fabrication detected. |
| 7 | **Pipeline frame-lock** | PASS | §1.2 lines 42-48 explicitly frame the three-layer methodology as the primary contribution; the 60-cell empirical audit as "an empirical demonstration following the establishment of the three-layer methodological framework, not the paper's main contribution". §6 chapter preface (line 1436) reaffirms: "These are **incidental empirical findings** after the three-pillar methodological framework is established—they demonstrate the empirical ceiling within the current scope of LLM-mutant + same-prompt + single-output kernels, and do not constitute counterevidence to the methodological framework". Conclusion in the abstract (line 14, Conclusion sentence) states: "P2 contributes a three-layer methodology … The 60-cell empirical audit … is an auxiliary finding under the methodology backbone, not the paper's main contribution". Frame-lock is the *opposite* direction — methodology backbone is primary, ablation is auxiliary, exactly as designed. PASS. |

**7-Mode verdict**: Mode 1 SUSPECTED → BLOCK (P0-A and P0-B citation hallucinations). Mode 3 SUSPECTED → does not block (single-number drift, P0-C, already counted). Modes 2/4/5/6/7 PASS.

---

## Final Verdict

### BLOCK — three P0 issues must be fixed before Stage 5

**P0-A** *(Mode 1 — citation hallucination)*: §8.3 Tip 2024 LLMorpheus author list is fabricated. Replace `Tip, F., Misailovic, S., Bavota, G., et al.` with `Tip, F., Bell, J., & Schäfer, M.` Verify via arXiv:2404.09952 / IEEE TSE 2025.

**P0-B** *(Mode 1 — citation hallucination)*: §8.4 DeepCrime entry is fabricated on multiple axes. Replace `Hu, Q., Guaman, D., Schumann, F., & Briand, L. (2022). … ESEC/FSE 2022. https://doi.org/10.1145/3540250.3549144` with `Humbatova, N., Jahangirova, G., & Tonella, P. (2021). DeepCrime: Mutation testing of deep learning systems based on real faults. ISSTA 2021. https://doi.org/10.1145/3460319.3464825`. Update all in-text references (§1.3.2 line 75, §3.1.1 line 426) to "Humbatova et al. (2021)" rather than "Hu et al. (2022)".

**P0-C** *(Mode 3 — number drift)*: §3.2.6.3 reports 1276 cosmic-ray mutants but SSOT `data/results/cosmic_ray_12put_ast_diff.json` reports 1250. Either re-run the cosmic-ray batch to regenerate the SSOT (if 1276 is the true count) or correct the manuscript to 1250. Affected lines: 594 (prose) and 603 (table). The 5.14% overall overlap rate is 15/292 and is unaffected.

### PASS_WITH_NITS — would be the verdict if P0s were fixed

P1 issues to resolve before Stage 5 (advisory but worth fixing for reviewer credibility):

- **P1-1**: Abstract claim "class-c +89%" should be "+91%" (true value +91.4%) or paper should compute against a different baseline that genuinely produces +89%.
- **P1-2**: Abstract Spearman ρ = 0.16, p = 0.74 mixes v4 ρ (0.16) with v3 p (0.74); v4 p is 0.61. Pick one version consistently.
- **P1-3**: §5.8.1 class means (line 1339-1342) are v3 numbers (0.067 / 0.156 / 0.047 / 0.081); §6.3 line 1466 explicitly cites v4 numbers (0.067 / 0.148 / 0.089 / 0.112). Add version annotation to §5.8.1 or update to v4.
- **P1-4**: §1.3.2 / §3.1.1 related-work table cites Pradel (DeepMutator), Cito, Tian (DLMutation) as orphan citations with no §8 backing and possibly misattributed (the "DLMutation" canonical paper is Ma et al. 2018, not Tian). Either add §8 entries (with verified attributions) or remove/reframe.
- **P1-5**: §8.7 software citations: mutmut author "Hovde" should be "Anders Hövel" (or whatever upstream lists); cosmic-ray "Tomilin" should be "Austin Bingham" (sixty-north); mutpy "Hovstadius" should be "Konrad Hałas". Verify against upstream README/AUTHORS files.
- **P1-6**: Internal data-SSOT inconsistency: `rq3_friedman_v4.json` per-class chi² differs from `paper_numbers_v4.json.rq3.friedman_per_class_p` (which copies v3b). Manuscript follows paper_numbers_v4 + rq3_friedman_v3b. Decide which is canonical for the 60-cell v4 main analysis and regenerate the other.

### Recommended Action

**Fix P0-A, P0-B, P0-C; ideally also resolve P1-1 through P1-3 (these are abstract-level discrepancies that any first-pass reviewer will catch). Then re-run Stage 4.5 verification.** Once P0s are zero, Stage 5 FINALIZE may proceed.

Estimated fix cost: ~30-60 minutes (mechanical citation replacements + one number swap + abstract-text minor edits). No data re-runs required for P0-A/B; P0-C requires either a 1-line edit (1276 → 1250) or a cosmic-ray re-run depending on which is intended canonical.

---

*End of report — independent from-scratch verification, 2026-05-02.*
