# Reviewer 1 — Methodology Re-Review (Verification Round)

**Manuscript**: *When Same-Prompt LLM Source Diversity Doesn't Help: An Ablation of Semantic Mutation Operators in Metamorphic Testing for Single-Output Scientific Computing Kernels* (revised English manuscript, 1700 lines)
**Re-review date**: 2026-05-02
**Reviewer file**: `论文初稿P2_EN.md`
**Original review**: `docs/review_2026-05-01/r1_methodology.md` (W1–W10)
**Reviewer focus**: methodological execution of the Major Revision response — power analysis framing, CI-vs-threshold disclosure, selection-on-response propagation, fallback hierarchy, max-selection inflation quantification, equiv-detection sensitivity, zero-mass propagation, sign-test wording, SMS/SMS_unfiltered consistency, APA-7/triplet reporting

---

## 0. Overall Re-Review Assessment

The authors made substantial textual revisions across the Abstract, §5.7.2, §5.8, §6.1, §6.3, and added §7.1.8 (R11 Selection-on-response chained-conditioning) and §7.1.9 (R13 Protocol-implementation gap). Several formerly under-stated caveats are now lifted into top-level disclosures (e.g., the "rejected" → "not met under pre-registered point-estimate criterion" wording change in §5.7.2 line 1165; the explicit chained-conditioning disclosure in §4.2.5 line 736; the explicit Friedman-as-fallback caveat at §5.8.4 line 1273-1282). On the **narrative discipline** side, this is a successful revision.

However, two **structural** problems remain:

1. **The most-referenced revision anchor — §3.5.1 c-class primary MP shift caveat — does not exist as a section in the manuscript.** It is cited 17+ times across the text (lines 719, 736, 1151, 1154, 1156, 1165, 1180, 1183, 1231, 1233, 1280, 1305, 1308, 1318, 1328, 1330, 1467, 1486 etc.) but no `### 3.5` or `#### 3.5.1` heading appears in the §3 region (greatest §3 heading is §3.2.6.3 at line 584; next heading is §4.1 at line 644). All caveats nominally housed in §3.5.1 must be inferred by the reader from §4.2.5 line 736 and §7.1.8 line 1465-1473. **Reproducibility-of-rebuttal is impaired**: a reviewer who follows the cross-reference network arrives at a phantom anchor.
2. **The new §3.2.6.3 12-PUT empirical contains a numerical inconsistency** between the text claim (line 638: "DeepSeek 7/15, Claude 4/15, GPT 0/15, unknown 4/15") and the data file `cosmic_ray_12put_ast_diff.json`. Direct counting of `overlap_files` in the JSON yields **DeepSeek 11, Claude 4, GPT 0, no `unknown`** category (15 files in total, all with explicit `claude` or `deepseek` source tags in the filename — see the four overlap arrays at JSON lines 88-92, 119-124, 188-194, 226-234). The "unknown 4/15" phrase has no referent in the data; the DeepSeek count is off by 4. This is a verifiable numeric error that reviewers will flag.

The aggregate per-class numbers (HP 0/72, SI 0/33, TF 0/54, CE 5/64=7.81%, OS 7/60=11.67%, CF 3/9=33.33%, overall 15/292=5.14%, 159 = HP+SI+TF) all reconcile with the JSON.

---

## 1. Verification Table — W1 through W10

| # | Original concern | Revision claim location | Verified? | Evidence + comment |
|---|---|---|---|---|
| **W1** | §5.7.3 power = parametric bootstrap from empirical pool, circular for "detect δ ≥ 0.474" | §5.7.3 lines 1187-1208 | **✗ Not Addressed** | The §5.7.3 method declaration is unchanged: "**With replacement** sample from observed aligned (n=12) and cross (n=48) v4 SMS pools" (line 1191). `rq2_power_v4.json` confirms `"method": "parametric bootstrap from empirical distributions"` (line 2). The two-condition (plug-in + stipulated alternative) re-frame requested by W1 was not implemented. The new "Key interpretation 3" (line 1205) explicitly defends the plug-in interpretation: "**But this cannot conversely say insufficient power is the cause of H2 not being met**". This is a defensible position but it is *not* the requested fix; the underlying conflation between sampling variability under the empirical distribution and Neyman–Pearson power against a stipulated δ_truth = 0.474 alternative remains. Moreover, the "achieved power 0.423 at δ > 0.474" at line 1200 is still labelled "Detect large effect (H2 threshold)" in the table column header — a heading that misleadingly equates plug-in pass-rate with power. |
| **W2** | δ CI [0.127, 0.740] crosses H2 threshold; verdict ignored CI–threshold tension | §5.7.2 lines 1165, 1167-1170; Abstract line 14 | **△ Partially Addressed** | The wording change from "rejected" to "**not met under pre-registered point-estimate criterion**" (line 1165, "P0-8 revision") **is** the key W2 fix and properly distinguishes operational rejection from frequentist exclusion. Abstract line 14 retains "**The pre-registered H2 large-effect threshold ... is rejected**" — bold "rejected" — which contradicts §5.7.2 line 1165's softer phrasing. The Abstract-vs-body inconsistency is exactly the residue W2 warned about (Abstract / §5.7.2 mismatch). **The TOST / non-inferiority auxiliary check requested by W2 fix step 2 was not added.** The new "effective sample size note" (lines 1167-1170) addresses W7 directly but does not close W2's CI-exclusion question. Net: partial. |
| **W3** | v3b → v4 conditional on c-class selection; 17.6:1 ratio not a clean factor decomposition | §4.2.5 line 736 (Chained-conditioning declaration); §6.1 lines 1304-1308; §7.1.8 line 1465-1473 | **✓ Verified Addressed** | The chained-conditioning declaration at §4.2.5 line 736 is exactly the W3-step-1 wording: "*conditional on v3b's c-class selection* + *identical prompt template*. This paper does not run the v4-pre (cross-source × c→MP5 pre-shift) grid point". §6.1 line 1308 explicitly removes the synthetic 17.6:1 ratio: "**The two contrasts each carry their own selection / conditioning caveats and cannot be synthesized into a single factor decomposition ratio**". The Abstract line 14 also drops the ratio, reporting Δδ_MR = +0.123 and Δδ_LLM = −0.007 separately with the disclaimer "reported separately rather than as a single ratio because the numerator reflects a confounded data-driven adjustment". §7.1.8 (NEW) makes R11 a first-class threat. The W3-step-3 v4-pre rerun was not done but is honestly declared as a future-work cost trade-off. |
| **W4** | Friedman from sensitivity to primary; Abstract / §6.3 still narrate as H4 evidence | Abstract line 14; §5.8.4 lines 1273-1282; §6.3 line 1332 | **✓ Verified Addressed** | Abstract line 14 now says: "Friedman test confirms a significant MP main effect (χ² = 15.30, p = 0.0041); **this is reported as a fallback non-parametric sensitivity, distinct from H4 cross-class consistency**." This is precisely the W4 ask. §5.8.4 line 1273 adds the "**Important caveat — Friedman main effect ≠ H4 cross-class consistency**" with a side-by-side table (lines 1275-1278) showing Friedman tests MP rank dispersion while sign test addresses H4. §6.3 line 1332 closes with "(c) 60-cell Friedman p = 0.0041 (non-parametric fallback, **not part of H4 verdict**, see §5.8.4)". This is a textbook successful disentangling. The W4-step-4 fallback hierarchy decision tree (Mixed-effects → Friedman → sign test → forest plot) is implicitly present in §5.8.3 line 1252 ("four-piece direct presentation"). |
| **W5** | c-class primary MP max-selection inflation not quantified | §7.1.8 line 1469 cites `c_class_permutation_v4.json`; Abstract/§3.5.1 references | **△ Partially Addressed (Direction Inverted)** | A 10,000-permutation null **was** run and stored at `data/results/c_class_permutation_v4.json` (verified: `n_perm=10000, seed=42`). The methodology is sound (cross-cell exchangeability over 15 c-class (PUT, MP) cells, max-over-5 per PUT recomputed per permutation). **However, the result is the opposite of what would close W5.** Verified numbers from the JSON: observed c-class aligned mean = 0.3136, null distribution mean = 0.3494, p25 = 0.3136, p50 = 0.3802, **`permutation_p_value_one_sided_geq = 0.9885`**. Translation: the v3b "MP1-as-primary" selection produces a c-class mean *at the 25th percentile* (or below) of the exchangeability null — i.e., 98.85% of random max-over-5 selections beat the actual c→MP1 choice. **This is the strongest possible evidence that v3b's c-class lift is not signal beyond chance**: it is *worse* than chance under the cross-cell exchangeability model. The paper does not draw this conclusion explicitly. §7.1.8 line 1469 instead reports only "Bonferroni upper bound α_effective = 0.01 (§3.5.1 P0-4 revision), permutation p-values in `data/results/c_class_permutation_v4.json`" — leaving the reader to derive the verdict, and the §3.5.1 anchor itself does not exist as a section. **A methodologically honest revision would replace the +0.123 Δδ_MR claim with "v3b's c→MP1 selection captures *less* than chance under cross-cell exchangeability (permutation p = 0.9885), so the +0.123 lift is best read as max-statistic noise, not real MR-MP alignment signal."** This permutation result is in tension with §6.1's "MR-MP alignment design itself" attribution (line 1305). |
| **W6** | K_eq sensitivity table promised in §7.1.2 but not in §5 | §7.1.2 line 1421; §5 search | **✗ Not Addressed** | §7.1.2 line 1421 retains the same promise: "§5 Appendix provides sensitivity analysis for three configurations K_eq ∈ {500, 1000, 2000}". I searched §5 (lines 977–1295) and Appendix-style attachments — no such table exists. No `K_eq` mention appears outside §7.1.2 and §4.4 line 788 (where K_eq=1000 is fixed). Hoeffding upper-bound number for false-equiv probability also still missing. W6 ask was either to deliver the table or downgrade the promise to a Limitation; neither happened. |
| **W7** | Effective sample size and zero-mass dominance not propagated to §5.7.2 verdict | §5.7.2 lines 1167-1172 (NEW "Effective sample size note", P1-5 revision) | **✓ Verified Addressed** | The new "Effective sample size note" at line 1167 says exactly what W7 asked: "surface n_aligned = 12 and n_cross = 48, but ... approximately 88% (42 / 48) of 48 cells are zero; Cliff's δ inference is actually dominated by 12 aligned cells + 6 non-zero cross cells, **effective n ≈ 12 + 6 ≈ 18 rather than surface 60**". Three downstream consequences are explicitly drawn (lines 1168-1170): (a) explains 0.42 power; (b) explains CI width [0.127, 0.740] ratio ≈ 5.83 with "known liberal tendency of percentile bootstrap at effective n ≈ 18"; (c) does not flip the verdict because point estimate 0.439 < 0.474 is an effect-size ceiling. The W7-step-2 BCa bootstrap replacement was not done, but the disclosure of the percentile-bootstrap liberal tendency at low effective n satisfies the spirit of W7's residual-caveat fix. |
| **W8** | "严格达成 / strictly met" in §5.8.2 conflicts with §3.5.1 caveat 3 (exploratory) | §5.8.2 line 1231 | **✓ Verified Addressed** | The verbal fix is clean: line 1231 reads "Pass count: **v3 (pre-registered): 3 / 4 (partial)**; **v3b (exploratory, post-hoc): 4 / 4 (conditional on c-class primary MP shift, §3.5.1)**". The word "strictly" is gone. §6.3 line 1332 mirrors this with "(b) v3b sign test 4/4 and v4 sign test 4/4 (both exploratory, conditional on c-class primary MP shift, §3.5.1)" — note the parenthetical demotion to exploratory and the explicit conditional reference. (W8-residue: §3.5.1 doesn't exist; that's a structural issue distinct from the wording fix.) |
| **W9** | SMS_unfiltered vs LRCA "does not modify SMS formula" tension | §5.4.2 line 1025-1032; §4.6.3 line 858-865 | **✗ Not Addressed** | §5.4.2 is unchanged from the pre-revision text: "Appendix provides cell-by-cell difference table between SMS_unfiltered and SMS; if relative difference < 5%, confirms LRCA does not affect robustness of primary conclusions." (line 1032). §4.6.3 line 865 still says "LRCA **does not modify SMS formula**, killed set does not exclude suspects." The two are still in tension: if LRCA truly does not modify SMS, then SMS_unfiltered ≡ SMS by construction and the "5% relative difference" check is empty. The naming clarification (`SMS_C1` vs `SMS`) suggested in W9 was not adopted. Minor issue but unaddressed. |
| **W10** | APA-7 / triplet reporting gaps (per-class Friedman effect size, Spearman ρ CI) | §5.8.4 line 1259-1269; §6.4 line 1336 | **△ Partially Addressed** | (a) Per-class Friedman table at lines 1265-1269 still gives χ² and p but **no Kendall's W** effect size and no Bonferroni × 4 correction (b-class p = 0.029 → adjusted 0.116, would flip "individually significant" verdict). (b) §6.4 line 1336 now states the Spearman ρ 95% CI verbally: "at this sample size, Spearman ρ's 95% CI is approximately [−0.5, +0.6], p = 0.74 does not constitute evidence of 'no correlation,' only 'not detected.'" — this addresses W10(c). (c) The §5.7.2 declarative summary triplet line for v3 primary is now de facto present in lines 1153-1155 (effect size + CI + sample size all on three consecutive lines). On balance: improved on Spearman ρ CI and on RQ2 triplet; per-class Friedman still missing W and Bonferroni × 4. |

---

## 2. Residual / new methodology concerns

### 2.1 Does §3.2.6.3 12-PUT 5.14% AST overlap survive scrutiny?

**Aggregate numbers**: ✓ verifiable. From `cosmic_ray_12put_ast_diff.json`:
- Total P2 mutants: 292 (paper line 598 ✓)
- Total cosmic-ray mutants: 1276 — wait, the paper line 599 says **1276** but the JSON does not give a single `n_cosmic_ray_total`. Summing per-PUT `n_cosmic_ray_mutants` from JSON: 201+17+336+76+151+32+66+51+99+48+99+74 = 1250. **The paper says 1276; the JSON sums to 1250.** This is a 26-mutant discrepancy. Either the paper rounded, double-counted, or includes mutants from a separate run not present in the JSON. *This needs to be reconciled.* (The interpretation may be that 1276 includes incompetent/duplicate-AST mutants not counted in `n_cosmic_ray_mutants`; but the JSON `n_cosmic_ray_unique_asts` sums to the same 1250, so this is not an AST-uniqueness issue.)
- AST-overlap = 15 ✓
- Overall rate = 5.14% ✓
- Per-class HP=0/72, SI=0/33, TF=0/54, CE=5/64 (7.81%), OS=7/60 (11.67%), CF=3/9 (33.33%) — all ✓
- HP+SI+TF = 159 mutants categorically unreachable ✓

**LLM-source bias claim** (§3.2.6.3 line 638): "DeepSeek 7/15, Claude 4/15, GPT 0/15, unknown 4/15" — **✗ does not reconcile with the data file**. Direct counting of `overlap_files` in the JSON (15 files total): Claude = 4 (m03_a2_CE1_claude_a03, m02_a2_CE1_claude_a01, m01_a2_CE1_claude_a02, m12_b3_OS1_claude_a01); DeepSeek = 11 (m14_a3_OS1_deepseek_a01, m15_a3_OS1_deepseek_a03, m13_a3_OS1_deepseek_a02, m14_b2_CF1_deepseek_a01, m13_b2_CF1_deepseek_a02, m15_b2_CF1_deepseek_a03, m13_b3_OS1_deepseek_a02, m15_b3_OS1_deepseek_a03, m06_b3_CE1_deepseek_a01, m14_b3_OS1_deepseek_a01, m04_b3_CE1_deepseek_a03); GPT = 0; "unknown" = 0. The paper's numbers (DeepSeek 7, unknown 4) are off by 4 in each direction — the paper appears to have re-classified 4 DeepSeek-tagged files as "unknown", but the filenames are unambiguous. **This is a verifiable numerical error that should be corrected before resubmission.**

**Statistical defensibility of the LLM-source bias claim at n=15**: even with the corrected counts (Claude 4, DeepSeek 11, GPT 0), claiming "DeepSeek tends to generate syntactically simpler mutations" requires a baseline of "expected per-LLM share" given that the v4 pool is constructed to be Claude=101 / GPT=98 / DeepSeek=99 (from §4.2.5 line 732 — "three sources contribute nearly equally"). Under a null of "syntactic-tool collisions are uniformly distributed across the three LLMs", expected counts would be 5/5/5. Observed (Claude=4, DeepSeek=11, GPT=0) gives a chi-square ≈ 12.8 (df=2), p ≈ 0.0017 — significant departure from uniformity, even at n=15. **So the bias claim does survive a basic statistical test under the corrected counts**, but the paper does not perform this test. The qualitative interpretation that DeepSeek leans simpler/literal is consistent with the per-PUT pattern (a3 OS1 Deepseek, b2 CF1 Deepseek, b3 OS1+CE1 Deepseek). I would recommend the authors (a) correct the DeepSeek count from 7 to 11 and remove "unknown 4/15"; (b) add a one-line χ² test against the equal-share null; (c) point the §7.2 R8 cross-reference to a numerically defensible claim rather than the current loose phrasing.

### 2.2 §3.2.6.1 OS row downgrade "✗ → △ 88.33% disjoint + 11.67% incidental hits" — softening or category-error fix?

The §3.2.6.1 table at line 514 reads: "**OS** API replacement ... | △ Mostly not covered (§3.2.6.3 empirics 88.33% AST-disjoint; a small number of low-complexity OS sub-expressions occasionally hit by tools)". The original "✗ Not covered" categorical claim has been downgraded to "△ Mostly not covered". The §3.2.6.3 commentary at line 630 says: "the 12-PUT empirics show that this claim is too strong in the *categorical* sense, and is in practice **88.33% disjoint + 11.67% incidental hits**".

**My methodological verdict**: this is a **category-error fix**, not a retroactive softening of the central claim. The reasons:
1. The 11.67% OS overlap is concentrated in DeepSeek-generated `dx**2 → dx*dx` style algebraically equivalent rewrites on a3 FDM and b3 — these are exactly the "incidental hits" predicted by the §3.2.6.0 systematic-vs-incidental argument. The §3.2.6.0 framework (lines 527-539) was already in place to handle this case.
2. The claim was logically over-strong in its v1 phrasing ("✗ Not covered") because *cosmic-ray's BinOp operator can reach `**2` → `*` even though it cannot reach API-replacement at the conceptual level*. The fix re-aligns the claim with what the data + theory actually justify.
3. The 88.33% disjointness still makes the OS class **systematically distinct** from syntactic tools, which is the paper's load-bearing claim.
4. Even more importantly: the categorical claim on **HP / SI / TF** (the three "structurally unreachable" classes) is *strengthened* by the 12-PUT empirics — 0/72 HP, 0/33 SI, 0/54 TF overlap, against the previous single-PUT n=18 a1-only pilot.

**However**, the §3.2.6.1 table footnote / column header now mixes "✗" and "△" symbols without a legend explaining the difference between "categorical unreachability" (HP/SI/TF, ✗) and "instance-level unreachability" (OS, △). Reviewers in the methodology track may flag this as inconsistent table notation. Suggested fix: add a one-line legend below the table — "✗ = no operator-level intersection (structural / categorical claim); △ = operator-level intersection conceptually possible but instance-level overlap < 12% (empirical claim)".

**Net judgment**: the OS row downgrade is methodologically correct and does not weaken the paper's central claim; the §3.2.6.0 vs §3.2.6.3 framework is internally consistent. This is a **strength of the revision**, not a weakness.

### 2.3 Is the §9 L1-L6 → 3-joint-condition restructuring sufficient?

The original §9 (referenced in W5 of R1's W-list) was lemma-style with 6 axes presented as if independent. The R0 W8 / R1 §4 / R2 W3 / DA-MAJOR-3 issue was that L1-L6 are not independent (e.g., L4 implies most of L3's effect; L5 + L6 together but not separately give Lemma 9.3). The revised §9.2 (lines 1604-1623) **rewrites this as 3 joint conditions** (L_equiv = L1 ∧ L2; L_killed = L3 ∧ L4; L_mut = L5 ∧ L6) with explicit pairing rationale for each pair (lines 1611, 1616, 1621 — each explains why the pair must be taken jointly).

**My evaluation**: the joint-pairing argument is methodologically tighter than the original 6-axis presentation. The pairing rationale at line 1611 ("when L1 holds alone but L2 does not, equiv remains a probabilistic approximation") is specifically the kind of dependency disclosure W5 of the original review asked for. Lemma 9.1 now correctly carries the **measure-zero qualification** ("almost everywhere w.r.t. measure D_S", line 1627), addressing the formal gap that strict bitwise equality on continuous D_S requires excluding NaN propagation / float-cancellation pathological points (line 1631).

**Residual gap (minor)**: Lemma 9.2's `r ≠ id` case at line 1640 still has the awkwardness flagged in the original R1 review — "When r ≠ id, MP_eq restricted by L4 still requires S_i(x) = s'(r(x)), treating it as a 'reference output oracle' constructed from the original program; this still does not introduce new state classifications." This is too quick. Strictly, when r is a non-trivial input transformation, the classical-MS framework doesn't have an `r` at all; the killed condition under classical MS is `∃x: S_i(x) ≠ s'(x)`, not `S_i(x) ≠ s'(r(x))`. The clean way to handle this is to push the limit further: under L = L_equiv ∧ L_killed ∧ L_mut, MR set restricted to {MP_eq with R(y,y') ≡ y=y'} **also forces r = id** because non-identity r is part of the MR's input transformation, and a degenerate equality oracle wouldn't carry one. The current proof skirts this by hand-waving "this still does not introduce new state classifications" — methodologically this is OK at the journal level (the theorem is true) but a careful methodology reviewer (e.g., a TOSEM referee) might flag it. For IST level, sufficient.

**Net judgment**: ✓ the L1-L6 dependency proof is now sufficiently tight. The 3-joint-condition restructuring with explicit pairing rationale, the measure-zero qualification on Lemma 9.1, and the LRCA trivialization corollary together form a coherent degeneration argument. The remaining `r ≠ id` skirt is a minor formal-rigor issue, not a fatal flaw.

### 2.4 §5.7.3 power analysis — fundamental framing problem persists

This is the single most important residual methodological issue. The paper's revision strategy was to **defend** the plug-in-bootstrap approach rather than supplement it. Line 1205 makes the defense: "**But this cannot conversely say 'insufficient power is the cause of H2 not being met'**—observed δ = 0.439 < 0.474, effect size itself is below threshold; increasing sample size will only narrow CI, will not automatically elevate point estimate to large." This argument is logically valid **but it does not answer R1's W1 question**, which was: "if truth = 0.474, how often would we have detected it at (n_aligned=12, n_cross=48)?"

The answer to that question requires constructing a stipulated alternative distribution F'_aligned, F'_cross such that the rank-statistic δ(F'_aligned, F'_cross) = 0.474 strictly, then sampling from F' under (12, 48). The plug-in bootstrap from the empirical distributions answers a *different* question: "given this empirical distribution (with empirical δ ≈ 0.439), how often does a resample give δ > 0.474?" — that is sampling variability, not power. The two coincide only when the empirical δ equals the truth being tested against.

**The paper's defense is correct under the assumption that truth ≤ 0.439**, but if a reviewer asks "what if truth is 0.474?" (precisely the H2 boundary), the plug-in bootstrap cannot answer. The 0.42 number is comfortable for the paper's narrative (H2 not met is robust to sampling variability), but it is not the inferentially valid power against the H2 alternative.

**This is a minor flaw, not a fatal one**, because: (a) the paper's primary verdict (point estimate 0.323 < 0.474) does not depend on power analysis; (b) the paper now explicitly disclaims that the power analysis "does not say insufficient power caused H2 to fail" (line 1205) — a defensible epistemic stance; (c) the cost of running the proper stipulated-alternative simulation is low (~30 lines of code) but not free. **I am leaving this flagged as W1 ✗ in the verification table** because the original W1 explicitly asked for the two-condition (plug-in + stipulated) re-frame, and the revision chose a different (defense-via-disclaimer) strategy. A second-round reviewer at the same journal could legitimately request the proper power simulation.

### 2.5 Permutation null result is a buried smoking gun

This is the most striking new finding from data verification. `c_class_permutation_v4.json` reports:

- Observed c-class aligned mean (under v3b's c→MP1 selection rule): **0.3136**
- Null distribution mean (10,000 cross-cell exchangeability permutations, max-over-5 per PUT): **0.3494**
- Null distribution percentiles: p25 = 0.3136, p50 = 0.3802, p75-p99 all = 0.3802
- **One-sided p-value (P[null ≥ observed]) = 0.9885**

This means: under cross-cell exchangeability of the 15 c-class (PUT, MP) cells (i.e., breaking any (PUT, MP) → SMS structural association), the chance-driven max-over-5 selection produces a c-class aligned mean **at or above the observed 0.3136 in 98.85% of permutations**. The observed selection is, under this exchangeability null, **at the 25th percentile or below** — i.e., *worse than chance*.

**The paper does not draw the natural conclusion from this result.** §7.1.8 line 1469 just cites the file as "permutation p-values in `data/results/c_class_permutation_v4.json`" without reporting the 0.9885 number or interpreting it. §6.1 line 1305 still attributes Δδ_{v3 → v3b} = +0.123 to "data-driven adjustment of c-class primary MP (§3.5.1), i.e., the MR-MP alignment design itself" — this attribution is in direct tension with the permutation result, which says the c→MP1 selection captures *less* than chance under exchangeability.

**Two charitable interpretations** of the high p-value:

1. **The exchangeability null is "wrong" in the sense that it's too generous** — it allows full reshuffling of (PUT, MP) → SMS, which destroys *both* the real MP-specific signal *and* the noise. If the truth is "MP1 has a small real advantage but most of the variance is PUT-level", then under reshuffling the max-over-5 picks up arbitrary PUT-level outliers and beats observed. Under this interpretation, the high p-value reflects null-misspecification rather than absence of MR-MP signal. (In support: per-PUT max SMS observed = c1: 0.20, c2: 0.00, c3: 0.7407 — c3's 0.74 is a single PUT outlier driving the mean.)

2. **The selection inflation argument was correct all along**: max-over-5 on n=3 PUTs × 5 MPs is high-variance and *can* produce values both higher and lower than the true mean across permutations. The observed 0.3136 sits in the lower tail of the noise distribution, and the apparent "lift" Δδ_{v3 → v3b} = +0.123 is consistent with selection noise, not signal.

Either way, **the paper owes the reader an explicit interpretation of the 0.9885 number**. Right now it is filed away as a footnote-level reference. A methodology reviewer comparing the permutation file to §7.1.8 will notice the omission. Recommendation: replace §7.1.8 line 1469 (a) with: "Under cross-cell exchangeability null (10,000 permutations, `c_class_permutation_v4.json`), the observed c-class aligned mean 0.3136 falls at the 25th percentile (one-sided p = 0.9885); the null mean 0.3494 exceeds the observed value. We interpret this as: under a model that breaks all (PUT, MP) → SMS association, max-over-5 selection alone routinely produces c-class means above the observed value. This **does not** support 'v3b's c→MP1 selection captures real MR-MP alignment signal beyond chance'. The +0.123 Δδ_{v3 → v3b} should be read as max-statistic noise, not MR-design signal — the v3 pre-registered verdict (sign test 3/4 partial, δ = 0.323) is therefore the one with cleanest causal interpretation, and v3b should be treated as exploratory in the strongest sense."

This honest disclosure would *strengthen* the paper's pre-registration discipline and weaken any reviewer suspicion that the v3b → v4 narrative is being used to soften H2.

### 2.6 Numerical reconciliation: 1276 vs 1250 cosmic-ray mutants

Paper line 599 says "1276 syntactic mutants across 12 PUTs"; JSON sum of `n_cosmic_ray_mutants` per PUT = 1250 (verified: 201+17+336+76+151+32+66+51+99+48+99+74). Discrepancy of 26 mutants. May be reconciled by inclusion/exclusion of incompetent mutants or pre-mutation parse failures (the JSON shows zero of those for all PUTs, so this can't be the source). **This needs a 1-line audit**: either correct the paper's 1276 to 1250, or recount the sum from the source-of-truth log file. Together with the DeepSeek 7→11 / unknown 4→0 correction in §3.2.6.3 line 638, this is the second numerical inconsistency in §3.2.6.3 detected during verification.

### 2.7 §3.5.1 phantom anchor

I count 17+ cross-references to §3.5.1 in the manuscript (lines 719, 736, 1151, 1154, 1156, 1165, 1180, 1183, 1231, 1233, 1280, 1305, 1308, 1318, 1328, 1330, 1467, 1486). The §3.5.1 anchor is cited as the home of: (a) the c-class data-driven primary MP shift caveat; (b) the post-hoc selection confound; (c) the P0-4 Bonferroni / permutation revisions; (d) selection-on-non-significance argument; (e) max-over-5 selection inflation. None of these are in §3 — the §3 region terminates at §3.2.6.3 (line 584-638). They are partially scattered across §4.2.5 line 736 and §7.1.8 line 1465.

**This is a P0-grade revision blocker for IST-style methodology peer review**: a reviewer following the manuscript's own cross-reference network arrives at a missing anchor. Typesetters and copy-editors may also flag this as a broken reference.

**Recommendation**: insert §3.5 "Pre-registration deviations and post-hoc analyses" with §3.5.1 "c-class primary MP data-driven shift (v3 → v3b)" containing: (a) the 4 caveats from the original Chinese draft; (b) the permutation null result and its honest interpretation (per §2.5 above); (c) the Bonferroni × 5 effective α = 0.01 conservative bound; (d) explicit declaration that v3b is exploratory and v3 is the H2 verdict source. This consolidation would close R1's W3, W5, W8 fully and also resolve the broken-reference issue.

---

## 3. Updated APA-7 / Triplet Reporting Audit

| Check item | Pre-revision | Post-revision | Notes |
|---|---|---|---|
| Effect size + 95% CI + sample size + p on same line | △ | ✓ | §5.7.2 lines 1153-1155 give all three v3/v3b/v4 with point + CI; effective n declared at line 1167 |
| Bootstrap n (B=10000) declared | ✓ | ✓ | §5.7.2 line 1155 |
| Multiple-comparison correction | △ | △ | per-class Friedman still missing Bonferroni × 4 (line 1265-1269); the b-class p=0.029 → 0.116 issue persists |
| Pre-registered vs exploratory | ✓ | ✓ | §5.7.2 line 1151 explicit; §5.8.2 line 1231 explicit |
| Verdict ↔ effect size + CI relation | △ | ✓ | line 1165 P0-8 revision: "not met under pre-registered point-estimate criterion" |
| Effect size + n, not just p | ✓ | ✓ | unchanged strength |
| Cliff's δ threshold source declared | ✓ | ✓ | §5.2 line 994 Romano (2006) cited; pre-commit |
| Zero-mass caveat propagation | △ | ✓ | line 1167-1170 effective n note |
| Spearman ρ CI | ✗ | △ | §6.4 line 1336 verbal CI [−0.5, +0.6]; §5.9.2 cell still lacks numeric (file truncates at line 1294 `#### 5.9.2` with no body!) |
| Per-class Friedman effect size (W) | ✗ | ✗ | not added |

**§5.9.2 is empty**: line 1294 `#### 5.9.2` has no body — the section header is followed directly by `## Section 6 · Discussion` at line 1296. RQ4 numerical results are nominally in line 1336 but appear in §6.4 (Discussion) instead of §5.9.2 (Empirical Results). This is a structural editing gap distinct from the §3.5.1 phantom; it means RQ4 numbers (Spearman ρ = 0.107, Kendall τ = 0.073, n=12, p=0.74) do not appear in the §5.9 results-reporting section at all but only in §6 narrative.

---

## 4. Reproducibility Re-Assessment

| Item | Status | Notes |
|---|---|---|
| SSOT JSON files | ✓ | `paper_numbers_v4.json`, `c_class_permutation_v4.json`, `cosmic_ray_12put_ast_diff.json`, `h5_sensitivity_v4.json`, `rq2_power_v4.json` all present and self-describing |
| Permutation p-values reproducible | ✓ | seed=42, n_perm=10000 declared in JSON |
| Power analysis reproducible | ✓ | seed=42, n_simulations=5000 declared |
| `REPRODUCIBILITY.md` audit | △ | not directly verified; SMS_VERSION + P2_PRIMARY_VERSION two-knob coupling still implicit (cf. §6.5.2 line 1373 example) |
| LLM-source filename tagging | ✓ | filename schema `{op_id}_{source}_attempt{NN}.py` (§4.2.5(a)) is what enables the LLM-source verification; system worked |
| Cross-references to anchors | ✗ | §3.5.1 phantom; §5.9.2 empty body |
| K_eq sensitivity | ✗ | promised in §7.1.2, never delivered in §5 or appendix |
| Numerical consistency in tables | △ | DeepSeek count (line 638); 1276 vs 1250 (line 599) |

---

## 5. Updated R1 Methodology Score (1–10)

| Dimension | Pre-revision | Post-revision | Justification |
|---|---|---|---|
| **Methodological rigor** | 6.5 | **7.5** | W3 (chained-conditioning), W4 (Friedman fallback explicit), W7 (effective n) closed; §9 3-joint-condition restructuring is a real improvement over original 6-axis presentation; lost ground only on W1 (plug-in power defended rather than supplemented) and W5 (permutation result not interpreted) |
| **Statistical inference correctness** | 6.0 | **7.0** | The point-estimate-vs-CI verdict reframing (W2, W7) is correct; effective-n-of-18 disclosure is appropriate; per-class Friedman Bonferroni × 4 not corrected; the permutation null at p=0.9885 is reported but not interpreted; this is the single biggest residual issue. |
| **Reproducibility** | 7.5 | **7.5** | SSOT preserved, raw JSON traceable, permutation seeds declared. Pulled down by §3.5.1 phantom anchor, empty §5.9.2, the 1276-vs-1250 mutant count, and the DeepSeek 7-vs-11 discrepancy in §3.2.6.3 line 638. None of these is a methodology flaw, but all four are reproducibility friction points. |

**Composite (geometric mean): 7.33 / 10**, up from 7.0.

---

## 6. Decision Recommendation

**Minor Revision** (downgraded from Major Revision, conditional on the items below). The paper has substantively addressed W2, W3, W4, W7, W8, W10 (Spearman ρ CI part), and the §9 degeneration theorem restructuring. The remaining items are tractable and do not require new experiments:

### 6.1 Must-Fix Before Acceptance (P0)

- **§3.5.1 phantom anchor**: write the section. Even a 200-300 word section consolidating the 4 caveats + permutation null + Bonferroni bound would close 17+ broken cross-references.
- **§3.2.6.3 line 638 LLM-source counts**: correct DeepSeek from 7 to 11; remove "unknown 4/15"; recount as Claude=4, DeepSeek=11, GPT=0; total = 15.
- **§3.2.6.3 line 599 cosmic-ray mutant total**: reconcile 1276 vs 1250 against `cosmic_ray_12put_ast_diff.json`.
- **Permutation null result interpretation**: the 0.9885 p-value should be reported and interpreted in §3.5.1 (or wherever you put the c-class selection caveat). Honest disclosure that the v3b lift is consistent with max-statistic noise, not signal-beyond-chance, will strengthen rather than weaken the paper's pre-registration credibility.
- **§5.9.2 empty body**: write the §5.9.2 results paragraph with the Spearman ρ = 0.107, Kendall τ = 0.073, n=12, p ≈ 0.74 numbers + Fisher-z 95% CI [−0.5, +0.6] inline (not just verbally in §6.4).
- **Abstract "rejected" wording**: change "**The pre-registered H2 large-effect threshold ... is rejected**" (line 14) to "**The pre-registered H2 large-effect threshold ... is not met under the point-estimate criterion**" to align with §5.7.2 line 1165.

### 6.2 Strongly Recommended (P1)

- **§5.7.3 power analysis**: add a 30-line stipulated-alternative simulation against truth_δ = 0.474 (shift-and-rescale on observed cross to construct F'); report both plug-in (existing 0.42) and stipulated-alternative power values. Current plug-in interpretation is defensible but the supplement closes W1 cleanly.
- **§5.8.4 per-class Friedman**: add Kendall's W column; apply Bonferroni × 4; report adjusted p (b-class 0.029 → 0.116). This will likely flip "individually significant" to "no class individually significant after correction" — which is methodologically more honest and consistent with the small per-class N (3 PUTs × 5 MPs).
- **§7.1.2 K_eq sensitivity table**: deliver or downgrade. If you can't run K_eq ∈ {500, 1000, 2000} sensitivity, move the promise from §7.1.2 mitigation list to §7.5 limitations; explicitly say "K_eq sensitivity not run in this version".

### 6.3 Nice to Have (P2)

- §3.2.6.1 table: add a one-line legend distinguishing ✗ (categorical / structural unreachability) from △ (instance-level overlap < 12% with conceptual proximity).
- §9.2 Lemma 9.2 `r ≠ id` case: tighten the "this still does not introduce new state classifications" argument by noting that under L_killed full limit, MR set restricted to {MP_eq with R(y,y') ≡ y=y'} forces r = id.
- §5.4.2 SMS_unfiltered naming: rename to `SMS_C1_only` to remove the tension with §4.6.3 "LRCA does not modify SMS formula".

---

## 7. Recommended Decision-Letter Line (Re-Review Edition)

> Minor Revision. The authors have made substantive methodological revisions to address the original W2 (verdict-vs-CI reframing as "not met under point-estimate criterion"), W3 (chained-conditioning declaration; removal of synthetic 17.6:1 ratio), W4 (Friedman explicitly disentangled from H4 evidence in Abstract, §5.8.4, §6.3), W7 (effective n ≈ 18 propagated to §5.7.2 verdict), W8 (post-hoc 4/4 sign test wording demoted from "strict"), and the §9 SMS-MS degeneration theorem (3-joint-condition restructuring with measure-zero qualification on Lemma 9.1). The new §3.2.6.3 12-PUT cosmic-ray empirical (HP=0/72, SI=0/33, TF=0/54 categorical unreachability + 5.14% overall AST overlap) is a strong empirical contribution that closes the "P2-as-syntactic-classification" challenge.
>
> Six items remain that should be cleared before acceptance. Three are textual: (a) the §3.5.1 c-class caveat anchor is referenced 17 times but the section does not exist in the manuscript — write it, consolidating the four pre-existing caveats with the permutation null result; (b) the §3.2.6.3 line 638 LLM-source bias claim "DeepSeek 7/15, Claude 4/15, GPT 0/15, unknown 4/15" does not reconcile with the data file, which counts Claude=4, DeepSeek=11, GPT=0 across 15 overlap files (no "unknown" category exists in the filename schema); (c) the Abstract retains "rejected" while §5.7.2 uses "not met under the pre-registered point-estimate criterion" — align the Abstract to the body. Two are interpretive: (d) the cross-cell exchangeability permutation null reports p = 0.9885 (`c_class_permutation_v4.json`) — this is a striking result that should be reported in the §3.5.1 caveat with honest interpretation that the v3b c→MP1 lift is consistent with max-statistic noise rather than MR-design signal beyond chance; (e) §5.7.3 power analysis is a parametric bootstrap from the empirical pool, which is defensible but does not stipulate the H2 alternative δ = 0.474 — supplement (not replace) with a stipulated-alternative simulation. One is structural: (f) §5.9.2 has no body text; write the RQ4 numerical results paragraph with Spearman ρ + Fisher-z 95% CI inline.
>
> The K_eq sensitivity table promised in §7.1.2 should also be either delivered or downgraded to a §7.5 limitation. With these edits the manuscript meets IST methodology standards.

---

*End of Reviewer 1 Re-Review Report (verification round, 2026-05-02).*
