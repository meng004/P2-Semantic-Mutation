# Statistics — simulated review 2026-07-08 (Reviewer 3, ACM TOSEM fast-impact)

Manuscript: `source/main.tex` + `source/supplementary.tex`
Data SSOT: `data/results/*.json`. All headline numbers re-derived and cross-checked below.
Prior round: `docs/review_2026-07-07/r3_statistics.md` + `synthesis_and_fix_ledger.md` — claimed fixes verified landed except where noted.

---

## Verdict
**Minor revision (borderline accept).** The honesty infrastructure (inference-permissions table, stipulated-alternative power, degeneracy handling, effective-n heuristic, selection-conditioned face) remains best-in-class and the six prior-round blockers all landed. What blocks a clean accept is not dishonesty but (a) a **repository-level reproducibility gap on the entire industrial arm** — the sole inferential leg of RQ4 (Holm p=0.046) and every industrial number is *not recomputable from any repo data file*, and (b) two **internal version/pool inconsistencies** (Friedman reported on v3 while the pool is v4; the aligned/cross means displayed for H2 belong to a different pool variant than the reported δ). None is fatal; all are fixable from existing material plus a data-commit.

## Score: 7 / 10
(Prior round would have been 5. +2 for the six landed blockers and the correctly re-paired CI. Held below 8 by the industrial-arm irreproducibility and the pool-provenance mismatches.)

---

## Verification of prior-round claimed fixes

| Claim | Status | Evidence |
|---|---|---|
| Stale CI [0.127,0.740] → [0.014,0.622] | ✅ landed & **correct** | main.tex L1971, L2050 pair [0.014,0.622] with δ=0.314; matches `rq2_cliffs_delta_v4_mp5.json` (δ=0.3142, CI [0.0138,0.6215]). The old [0.127,0.740] is now absent (grep count 0); it was in fact the *correct* CI for the δ=0.439 MP1 pool, and the paper resolved the conflict by making the conservative 0.314 variant the headline. Good honesty move. |
| Effective n = 15 (9+6) | ✅ landed | main.tex L1958, L1968–69; 9 nonzero aligned + ≈6 nonzero cross. |
| Holm family enumeration | ✅ landed | main.tex L2438–39: T1>B1, T1>A1, B1>B2, three one-sided Wilcoxon under Holm. |
| 34/34 face | ✅ landed | main.tex L1928, L2432, L2455–56; permission row n=34 (L1926). Consistent across 5 sites. |
| p=0.046 fragility discussion | ✅ landed | main.tex L2447–51: narrowed 30→34, sensitivity rerun leaves verdict unchanged, census fixed before comparison. |
| OR≈21 sensitivity annotation | ✅ landed but **under-used** (see Major 2) | main.tex L1961–65: aligned 9/12 vs cross 6/48, OR=21, explicitly "not a licensed verdict." |
| Δδ=−0.009 CI printed (U7) | ✅ landed | main.tex L2073: paired-role bootstrap 95% CI [−0.238, 0.207]. |
| Abstract "confirming"→"supporting" (Blocker 6) | ✅ landed | main.tex L138, L181: "related but distinct constructs, supporting". |

Numbers independently re-derived and **confirmed correct**: Wilson CIs 377/1124→[0.308,0.364], 274/1124=0.244, 228/1124=0.203, 348/1124=0.310 (match L2442–44); permutation p one-sided = 0.989 (data 0.9885, `c_class_permutation_v4.json`); effective-n arithmetic; logit-δ = raw-δ = 0.439 (rank invariance, `rq2_cliffs_delta_logit_v4.json`).

---

## Major concerns

### M1. The industrial arm (RQ4) is not reproducible from the repository — and its headline p=0.046 is the arm's *only* inferential support.
`paper_numbers_v4.json` contains only `rq1..rq4` for the 12-PUT experiments. **No repo file** backs any industrial number: not the four group kill rates (377/1124, 348/1124, 274/1124, 228/1124), not the mean paired difference +0.101, not the bootstrap CI [+0.029,+0.179], not Cliff's δ=+0.247, not the per-case detection counts (27/34, 26/34, 19/34). Grep for `1124|377|0.101|0.247|holm|realdefect` across `data/` returns nothing; the manuscript itself says these are "recorded in the dataset report" (external Zenodo `defect4mr2026`, 10.5281/zenodo.21203424). For a statistics reviewer the consequence is direct: **I cannot verify the single inferential claim the industrial arm rests on.** A marginal Holm-adjusted p this close to 0.05, un-recomputable from the artifact, is the weakest possible footing for a "stable acceptance" leg.

*Distinguish the fix paths:*
- **New analysis of existing data is NOT possible from the repo** for RQ4 — the raw per-case kills live only in the external dataset. Permutation / Bayesian / effect-size-CI re-analysis (below) **requires first committing the 34-case per-case matrix** (T1/A1/B1/B2 kill counts per case) into `data/results/` as SSOT.
- **Minimum text-only remedy** (still open from prior Minor 9): report the Wilcoxon signed-rank statistic (V or z) and the **unadjusted** p alongside the Holm-adjusted 0.046, so the body is at least summary-statistic reproducible. Currently neither the test statistic nor any unadjusted p appears.

*Concrete strengthen-with-existing-data verdict (conditional on committing the per-case matrix — then all three are one script each and are the SAME estimand, not HARKing):*
1. **Exact sign-flip / signed-rank permutation test** on the 34 paired differences — distribution-free, replaces the normal-approx that produced the fragile 0.046 and gives an exact p that will not sit on the 0.05 knife-edge.
2. **BCa bootstrap CI on δ=+0.247** — a δ CI excluding 0 is a cleaner effect-size statement than a marginal p.
3. **One-sided Bayesian paired estimate** (posterior P(Δ>0) under a weakly-informative prior) — reports evidence strength without the dichotomous-threshold fragility.
Foreground the existing **paired-difference CI [+0.029,+0.179] (excludes 0)** as the primary statement; it is already more robust than p=0.046.

### M2. H2 pool-provenance mismatch: the displayed aligned/cross means belong to a different pool than the reported δ.
Table `tab:p2-09` (L2035–36) and the abstract evidence table (L268–269) show **aligned mean 0.275 / cross mean 0.061** — these are the **δ=0.439 MP1 pool** (`rq2_cliffs_delta_v4.json`: mean_aligned 0.275, mean_cross 0.061, δ 0.439). But the H2 verdict text (L2049–2064) reports the headline **δ=0.314** from the **MP5 pool** (`rq2_cliffs_delta_v4_mp5.json`: mean_aligned **0.213**, mean_cross **0.077**, δ 0.314). A reader forming a δ intuition from 0.275-vs-0.061 expects ≈0.44, not 0.314; the two summary statistics in the same subsection come from different pool variants. **Fix:** display the means (0.213/0.077) that generate the reported δ=0.314, or label both pool variants explicitly in the table. This is a consistency defect, not an error in either number individually.

### M3. Cross-class Friedman is reported on the v3 pool while the surrounding analysis and the class-mean table are v4.
Main.tex L2536/L2940 report **χ²=15.30, p=0.0041**, rank means 2.92/2.58/2.08/3.08/4.33 — these are `rq3_friedman.json` (**v3**). The v4 SSOT `rq3_friedman_v4.json` gives **χ²=16.76, p=0.0022**, rank means 3.083/2.583/2.0/3.0/4.333. The adjacent class-mean table `tab:p2-12` (L2506–09) shows **v4** means (c: 0.089 +91.5%, d: 0.112). So the section mixes a v3 Friedman with v4 class means. The verdict is unchanged (both p<0.01, cross-class consistency rejected, exploratory), but the specific χ²/p/rank-means are stale relative to the v4 pool used everywhere else. **Fix:** report the v4 Friedman, or state explicitly that the cross-class test is deliberately run on the v3 same-source pool and say why.

---

## Focus-area answers (as tasked)

### (1) Is Holm p=0.046 at n=34 robust enough as the headline? What strengthens it from existing data?
Not robust enough as-is, primarily because it is (i) marginal, (ii) the *sole* inferential leg, and (iii) irreproducible from the repo (M1). Fragility handling is honest but a single knife-edge p cannot carry stable acceptance. **Strengthening does not require a new experiment** — the 34 cases already exist — but it **does require importing/committing the per-case matrix**, after which the sign-flip permutation test, BCa δ-CI, and Bayesian posterior (M1) are pure re-analysis and pre-declarable as the same one-sided contrast. This is the highest-value, lowest-risk move in the paper.

### (2) H2 — legitimate more-powerful, pre-declarable, non-HARKing analysis of existing v4 data?
Yes, and it is already half-computed. The zero-inflation (75% of cells = 0; 88% of cross cells = 0) means the aligned-vs-cross signal is really two estimands: **detection incidence** (does the MP score anything) and **conditional magnitude** (how much, given nonzero). Frame H2 as this **two-part / hurdle estimand**, pre-declared as a sensitivity family:
- **Incidence part:** the binarized nonzero-SMS contrast (aligned 9/12 vs cross 6/48) the paper already reports but discards. I ran it: **Fisher exact one-sided p = 0.000053, OR = 21, 95% OR CI [4.4, 100]** (excludes both 1 and the H2 ratio threshold 3.0). This is by far the paper's strongest existing-data separation result and it is currently given "zero evidential weight."
- **Magnitude part:** Cliff's δ = 0.314 (CI [0.014,0.622]) — misses the 0.474 large-effect bar; H2 magnitude verdict stays "not met."

**Honest label (no HARKing):** the median-OR≥3.0 was the pre-registered *magnitude* criterion and it degenerates to +∞ under zero-inflation — it cannot be rescued. The Fisher/OR result is a **different estimand** (incidence), so it **must not** be promoted to a confirmatory H2 pass. Report it as a **pre-specified binarized detection-incidence sensitivity**: "aligned MPs detect a nonzero effect far more often (OR≈21, Fisher p<0.001), while the *magnitude* of the aligned-vs-cross gap does not reach the pre-registered large-effect threshold." That is a legitimate, more-powerful, and fully honest reading of existing data. Note: mixed/multilevel models are *not* a viable route here — the RQ5 mixed-effects model already hit boundary-zero PUT variance (singular), and the logit transform leaves δ bit-identical (rank invariance). The hurdle decomposition is the right tool.

### (3) Source-diversity Δδ=−0.009, CI [−0.238,0.207] — is "cannot conclude inertness" correct, and would the deferred rerun be informative?
The framing is **statistically correct**: a CI covering zero is absence of evidence, not evidence of inertness; the paper does not over-claim. **But the deferred dual-blind rerun as described is underpowered by design.** Rough assessment: the paired-role bootstrap SE ≈ (0.207 − (−0.238)) / (2·1.96) ≈ **0.113**. To detect a true source-diversity effect of Δδ = 0.20 at 80% power (two-sided α=.05) needs |effect|/SE ≥ 2.8 → SE ≤ 0.071 → ≈2.5× the observations → **≈30 PUTs (≈75 cross cells)**, not the current 12/48. A dual-blind rerun on the **same 12 PUTs** only removes the protocol-asymmetry confound; it holds n fixed, so the CI stays ≈0.44 wide and would still routinely fail to exclude zero even if a genuine medium effect exists. The paper does say "larger PUT sample" at L2077–79 (good), but L2076 ("the exact source-diversity contribution requires a dual-blind v4 rerun") should explicitly add that the rerun must **also** reach n≥30 PUTs or it remains inconclusive. **Text-only fix.**

### (4) Inference-permissions consistency
- p=0.046 industrial → licensed row "four-group Wilcoxon, Holm-corrected, inferential within 34-case pool." ✅ consistent.
- p=0.0041 Friedman → licensed "exploratory inferential." ✅ label consistent, but **stale version** (M3).
- Spearman/Kendall p=0.61/0.57 (L2572) → row is "none (descriptive); hypothesis-generating only," yet the p-values are still quoted in prose. The current use is a *negative/power* reading ("does not support the strong claim…"), which is defensible, but it is the one residual place a p-value sits next to a "none" row. Either move it under an explicit power-caveat licensed reading, or drop the numeral. Minor residual from last round's Minor 2.
- 34/34 face → "none (descriptive; selection-conditioned)." ✅ consistent; not read as evidence.
- No p/CI is read above its row otherwise. The abstract no longer over-reads the face (Blocker 6 closed).

### (5) Multiplicity across the paper
Within-family control is clean everywhere: industrial Holm family (3 comparisons, enumerated), per-class Friedman Bonferroni×4, c-class permutation Bonferroni family_size=5 (p=0.989 n.s. regardless). H1/H3/H4 are count-threshold verdicts carrying no p-values. There is **no study-wide multiplicity control across families**, but that is standard and defensible given pre-registration + per-family correction + the permissions table scoping each statistic; note it in one sentence rather than "correct" it. **One caveat:** if the M2/focus-(2) Fisher incidence test is added, it is a *new* test and must be declared in its own labeled sensitivity family, **outside** the Holm and pre-registered families — do not fold it into an existing correction post hoc.

---

## Minor items

1. **Ablation-count mismatch main vs supplementary.** Main.tex L2462 reports **one** ablation ("dimension-reduction ablation loses the real defect in 19 of 34"); supplementary Appendix I `tab:realdefect-ledger` reports **two** ablated variants ("miss 19/34 and 17/34, 11 shared misses"). Reconcile — the main text silently drops the second ablation variant. (Baseline detect counts 7/34, 8/34 in supplementary correctly mirror main's "27 of 34," "26 of 34" miss counts. ✅)
2. **Industrial bootstrap B unstated.** The rq2 CIs use B=10,000 (`n_boot` in the v4 files) — good, closes last round's Minor 3 for the primary δ. But the industrial CI [+0.029,+0.179] has no stated B and no repo file; state it.
3. **Wilcoxon statistic still missing** (last round Minor 9). Report V or z with p=0.046.
4. **Stipulated 49.1% power** — the "rule-intrinsic ≈0.5 pass probability at the boundary" reframing landed (L2145–2161); good. Keep.
5. **"Sign test (df=3)"** — verify it was renamed to "directional consistency count" everywhere (ledger item 14); confirm no residual "df=3" survives in supplementary.
6. **elsarticle → acmart.** Source is still an Elsevier IST authoring master (L4 header "VENUE-NEUTRAL AUTHORING SOURCE"); confirm the `venues/tosem/` build produces acmart before resubmission.

---

## Reviewer 2 (ARS) cross-check on statistics
- **Statistical selection bias:** the paper chose the *conservative* δ=0.314 (MP5) over the stronger δ=0.439 (MP1) as headline — the opposite of cherry-picking; commendable. But M2 means it then displays the *stronger* pool's means next to the *weaker* pool's δ, which reads as accidental inflation of the visual effect; fix to remove the appearance.
- **Cherry-picking / HARKing:** the OR=21 incidence result is the one place the paper *under*-reports a favorable existing-data result rather than over-reports; promoting it as a labeled sensitivity (focus-2) is honest, not HARKing, provided the estimand relabeling is explicit.
- **External validity / reproducibility:** M1 is the genuine publication-risk item — a headline inferential claim that cannot be recomputed from the artifact is a fast-impact-track liability; close it by committing the per-case matrix.

No fabricated or above-row inferential claim detected. Reviewer 2 scan otherwise passes.
