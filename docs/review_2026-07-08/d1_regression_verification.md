# Wave-D1 Regression Verification (Devil's-Advocate lens)

Branch `claude/paper-journal-acceptance-kxpveo`; commits 3014fa3 (Wave-A artifacts), 855df4a (text integration + hash-key renames), d7ecb56 (package regen). Verified 2026-07-08.

Verdict: **PASS with one must-fix regression** (a word/count mismatch) plus two LOW cosmetic items. Every SSOT number that was integrated matches its authoritative JSON within stated rounding. No stale survivor of any corrected claim was found. No broken cross-refs or citations.

---

## Severity-ranked findings

### MEDIUM (must-fix regression) — "four cells" but FIVE are listed

- `source/main.tex:2469` and regenerated `submission/TOSEM_fastimpact_20260708/main.tex:2429`:
  > "...31/88 (35.2%) from multi-stratum mutants, the latter confined to the **four cells** `B2_MP1`, `C1_MP1`, `C1_MP2`, `D1_MP5`, and `D3_MP5`."
- Five cell names are listed. `s5_purity_v4.json` `rq2_off_diagonal_reattribution.off_diagonal_cells` has exactly **five** cells with `multi>0`: B2_MP1(9), C1_MP1(2), C1_MP2(2), D1_MP5(9), D3_MP5(9) = 31. The word "four" is wrong; it should read "five cells." Introduced by the surgical S5-audit insertion in 855df4a and carried into the d7ecb56 package. Fix both files.

### LOW — Fisher one-sided p rounded up

- `source/main.tex:2005` (and the abstract clause / commit messages): "one-sided Fisher exact test gives `p = 0.036`". SSOT `h2_incidence_v4.json.headline_ssot_correct.fisher_p_onesided_greater = 0.03548831`, which rounds to **0.035** at three decimals, not 0.036. Direction is conservative (overstates p, i.e. understates significance), so it does not inflate any claim, but it is an inexact round. Recommend 0.035 (or 0.0355).

### LOW — acmart submission abstract diverges from the source/arXiv abstract (two-place-sync trap)

- `submission/TOSEM_fastimpact_20260708/main.tex:~97` carries a *separate, concise* acmart abstract that does **not** include the new S5-verified / detection-incidence / distribution-free clauses that 855df4a added to the elsarticle frontmatter abstract (`source/main.tex:63`). This is **not a contradiction**: the acmart abstract states "Several pre-registered empirical thresholds are not met... construct separation supported on industrial code," which is consistent with the body verdicts. But the two abstracts differ in content, and the acmart `\keywords` (line 96) has 6 keywords (correctly free of "Cliff's delta") while the source `\keyword` has 7 (adds "test adequacy criteria"). Flagged for awareness; not a blocker.

### LOW — orphan hash-key bib entries remain

- `source/references.bib` still contains ~20 uncited `@misc{<40-hex>}` entries. None are cited (grep for `\citep{<40hex>}` = 0 hits; all 16 *cited* hashes were renamed). Harmless for compilation (bibtex only emits cited keys); optional cleanup.

---

## Verified CLEAN (checked, no problem)

**SSOT number integration (check group 1) — all exact within rounding:**
- H2 incidence (`h2_incidence_v4.json`): aligned 6/12, cross 9/48, 50% vs 18.75%, sample OR 4.33, cMLE 4.20, one-sided CI [1.12,+inf); robustness range "OR 4.1-7.0, p=0.006-0.049" matches grid (4.133/6.0/5.0/7.0; p 0.0486/0.0263/0.0238/0.0064). main.tex:1999-2011.
- RQ2 MP5 pool (`rq2_cliffs_delta_v4_mp5.json`): tab:p2-09 aligned 12 / 0.213 / 0.100, cross 48 / 0.077 / 0.000; abstract map "0.213 vs 0.077 (MP5-held)"; δ=0.314. main.tex:456-457, 137-138.
- Friedman v4 (`rq3_friedman_v4.json`): χ²=16.76, p=0.0022, rank means 3.08/2.58/2.00/3.00/4.33; per-class Bonferroni×4 a1.000/b0.140/c0.924/d1.000; Kendall W a0.333/b0.862/c0.467/d0.417 — all recomputed and match (main.tex:599-613, 656; supplementary.tex:231-244).
- S5 purity table (`s5_purity_v4.json`, verified against `per_operator`): flip {0:170,1:93,≥2:29}, 263/292=90.1%, table CE 64/27/27/0, OS 60/35/35/0, HP 72/11/11/0, SI 33/11/11/0, CF 9/9/0/9, TF 54/29/9/20, All 292/122/93/29; off-diagonal 57:31 = 64.8%:35.2%; local families 0/229. main.tex:511-552, 296-302.
- Industrial battery (`industrial_stats_v1.json`): permutation p=0.014 (2^27), MC p=0.005, BCa δ CI [+0.07,+0.46], Wilcoxon V=279.5 z=2.16 p=0.015, mean diff +0.101, Holm p=0.046, δ=0.247, seed 20260704. main.tex:557-579.

**Stale-survivor hunt (check group 2) — none found:**
- No "OR of 21"/"ratio of 21"; the old binarized aligned-9/12-vs-6/48 passage is fully rewritten to 6/12-vs-9/48. No "5.3e-5". No Friedman "15.30"/"0.0041" — replaced in BOTH main.tex and supplementary.tex.
- Means 0.275/0.061 remain ONLY at main.tex:2092 and 2158, both explicitly labelled the unconditioned MP1 δ=0.439 pool (power-table provenance), never presented as the δ=0.314 pool. Correctly disambiguated.
- "structurally unreachable" removed: HP re-described as "Value-menu artifact (not structural)", SI/TF as "Structurally cross-function" (main.tex:343-345, 360-370).
- Old S5 hedge ("enforced by generation intent... not verified against all five invariants") deleted; replaced by verified audit. Remaining "unverified premise" (main.tex:2975) is the unrelated HOM/dual-blind δ-bound, not an S5 hedge.
- H1 threshold "9/12" undamaged: 6 legit "≥9/12 PUTs" occurrences intact (594,1899,2030,2032,2058,3083); new incidence prose correctly uses "9 of 12 PUTs" for the any-signal count and explicitly warns against mislabelling it as an aligned-cell count.
- "Cliff's delta" removed from keyword list (source keyword line + package keywords); prose usages of the statistic name retained appropriately.

**Cross-document consistency (check group 3):**
- Abstract vs body: thresholds not met (both), incidence qualitative + magnitude "not met" (both), construct separation "supported" not "confirmed" (abstract, cover letter, conclusion aligned). No contradiction.
- Page count: main.pdf=46, supplementary.pdf=21 (byte-level object count) — matches cover_letter.md:65-67 and declarations.md:23-24 ("46 pages incl. refs, 43 body, below 45"); identical in venues/ and package copies.
- cover_letter.md: "confirm"->"support" (line 309 of diff) + in-repo SSOT sentence present.
- Package regen (d7ecb56) carries all corrected numbers (16.76, 0.036, degiovanni2022mubert, foster2025ach, 0.213, S5 audit, detection-incidence).

**H2 two-part-hurdle wording (check group 4):** post-hoc label present ("post-hoc detection-incidence sensitivity"), own single-test family "outside the pre-registered Holm family and outside the H2 pre-registration", magnitude verdict "H2 verdict remains not met" — all present (main.tex:1994-2012). CLEAN.

**Front-load audit (check group 5):** Introduction (main.tex:1101-111 region, diff 101-111) states all four threshold misses (H1 instantiability, H2 effect size, H3 cross-class consistency, H4 attribution) in prose "each not met... report those misses plainly" *before* the industrial positive. CLEAN.

**New-problem scan (check group 6):**
- Cite/ref integrity: all 52 cite keys in source main+supp and all 52 in package main+supp resolve against their references.bib; 0 undefined. 16 hash->readable renames complete and consistent across bib+tex (westbrook2013approx, geoffroy2021partialmetric, aichernig2007utp/2002contract, cousot2002transform/1992absint, dotzel2023usageaware, bartocci2023propertymut, alblwi2023semanticcoverage, jeangoudoux2021interval, curto2025semanticinvariance, papadakis2019advances, petrovic2021improve, jia2011analysis/2009hom, clark2010semanticmut).
- Surgical edits read grammatically (intro front-load, industrial robustness clause, S5 audit paragraph, provenance notes) — no broken sentences observed except the "four cells" count word above.
- No duplicated content; supplementary "13 default classes" (Number added) now consistent with main's "13 default operators", no residual "12 default".
- Tone: corrected OR≈4 story is consistent everywhere (no leftover near-twentyfold framing presented as a verdict; explicitly demoted).

---

## Check-group scorecard

| # | Check group | Result |
|---|---|---|
| 1 | SSOT number match | PASS |
| 2 | Stale-survivor hunt | PASS |
| 3 | Cross-document consistency | PASS (LOW: acmart abstract diverges, non-contradictory) |
| 4 | H2 two-part-hurdle integrity | PASS |
| 5 | Intro front-load | PASS |
| 6 | New-problem scan | PASS except MEDIUM "four cells" count |

**Must-fix regressions:** (1) `source/main.tex:2469` + `submission/TOSEM_fastimpact_20260708/main.tex:2429` — change "four cells" to "five cells" (five are listed; JSON confirms five). Optional: Fisher p 0.036 -> 0.035.
