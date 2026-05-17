# Editor-in-Chief Re-Review Report (R0, Round 2) — P2 Manuscript

**Manuscript**: *When Same-Prompt LLM Source Diversity Doesn't Help: An Ablation of Semantic Mutation Operators in Metamorphic Testing for Single-Output Scientific Computing Kernels*
**Target Venue**: *Information and Software Technology* (IST)
**Re-Review Date**: 2026-05-02
**Reviewer Role**: R0 (EIC) — verification round on Major Revision response
**Manuscript file inspected**: `<P2_SOURCE_PATH>/论文初稿P2_EN.md` (1,700 lines)
**Independence statement**: This re-review verifies the Major Revision against my own R0 (W1–W8) plus the 5/5-consensus structural concerns codified in `editorial_decision.md`. I have not consulted other reviewers' Round-2 reports for this round.

---

## 1. Verification Matrix — R0 Original Concerns (W1–W8)

| # | Original concern (one-line) | Revision claim location | Verified? | Evidence + brief comment |
|---|---|---|---|---|
| **W1** | Title + 17.6:1 ratio + v3b/v4 selection asymmetry → headline structurally fragile | Title line 5; §4.2.5 line 736; §5.7.2 lines 1176–1183; §6.1 line 1308; §7.1.8 line 1465 | **△ Partially Addressed** | Title rewrites with "Same-Prompt" + "Single-Output Scientific Computing Kernels" (DA-CRITICAL-1 mandated string reproduced exactly). 17.6:1 ratio removed (grep zero hits). §6.1 line 1308: *"The two contrasts each carry their own selection / conditioning caveats and cannot be synthesized into a single factor decomposition ratio."* My R0 fix-1 (v4-pre at c→MP5 cross-source) was canonical; authors elected fix-2/3 (retitling + explicit limitation), citing in §4.2.5 line 736 that "v4-pre rerun cost ~$20-30 + 2-3 days wall time, asymmetric to the narrative benefit." Headline remains **conditional** on v3b's c→MP1 selection but the narrative is now self-consistent under that conditional framing — downgrade ✗ to △. |
| **W2** | v3b post-hoc shift — "严格达成 4/4" still propagated to Abstract / §6.3 | Abstract (line 14); §5.8.2 (line 1231); §6.3 (lines 1328–1332); §7.1.8 (line 1469) | **✓ Verified Addressed** | Abstract line 14: *"Under pre-registered v3, the H4 sign test is 3/4 (partial); under exploratory v3b (post-hoc, conditional on c-class primary MP shift, §3.5.1) the same sign test is 4/4. **We report v3 as the H4 primary result.**"* §5.8.2 line 1231: *"v3 (pre-registered): 3 / 4 (partial); v3b (exploratory, post-hoc): 4 / 4 (conditional on c-class primary MP shift, §3.5.1)"* — the word "严格" / "strict" has been deleted. §6.3 line 1332 closes with *"cross-class consistency verdict is based on v3 pre-registered = partial (sign test 3/4)."* This meets the spirit of W2 fix completely. |
| **W3** | "Pre-registered" claim lacks OSF/aspredicted ID or git-time-stamped protocol | §5.2 line 1002; Abstract line 14; §5.7.2 line 1153 | **✗ Not Addressed** | "Pre-registered" appears ≥8 times (Abstract, §5.7.2, §5.8.2, §6.3, …) but **no OSF / aspredicted URL, no registration date, no internal-protocol git hash**. §5.2 line 1002 only states *"The H2 large-effect threshold is a pre-commitment (following P1 setting), not modified post hoc in this paper"* — a prospective internal rule, not pre-registration in the OSF/PRP sense. Neither of my W3 fix paths (registration ID **or** rename to "fixed prior to data collection per internal protocol document") has been implemented. **Hard editorial requirement open.** |
| **W4** | IST 2024 survey "[Authors TBD]" + originality margin | §8.3 line 1562; §1.3.2 line 80; line 1185 | **△ Partially Addressed** | "[Authors TBD]" phantom entry **removed from §8.3** (commit `ae660bd`). The "0.30–0.45 range" claim that depended on it has been dropped from §1.3.2, replaced with *"in the same magnitude as the LLM-mutant medium-effect phenomenon observed by Tip et al. (2024)"* — acceptable scope shrinkage. Originality now anchored on §3.2.6.3 12-PUT 5.14% empirical + §9 degeneration. **Bug**: line 1185 still reads *"medium effect is stable and consistent with LLM-mutant literature (Tip 2024, **IST 2024**)"* — dangling citation to a reference no longer in §8. Scrub required. |
| **W5** | Petrović Google "highly matches" overstates validity | §1.3.2 line 80; §6.1 line 1314 | **△ Partially Addressed** | §6.1 line 1314 substantially rewritten: *"this is **numerical coincidence, not mechanism validation**: Google's 'productive mutant' is obtained from developer survey … a human judgment construct; LRCA's C1 is the automatic annotation output of a 3-layer classifier, an algorithmic construct."* This is the construct-difference framing W5 fix-2 demanded. **But §1.3.2 line 80 still says** *"…**closely matching** this paper's §5.6.2 LRCA C1_share measured levels"* — the wording W5 fix-1 explicitly asked deleted from the early-paper context. §6.1 fixed, §1.3.2 missed. |
| **W6** | RQ4 inconclusive + zero-mass dominance dilutes RQ2 | Abstract (line 14); §5.6.1.1 (line 1063); §5.7.2 effective-n note (line 1167); §5.9 (line 1286) | **△ Partially Addressed** | §5.7.2 effective-n note (lines 1167–1172) explicitly states *"effective n ≈ 12 + 6 ≈ 18 rather than surface 60"* and propagates this to the H2 verdict — exactly the propagation R0 W6 demanded. Abstract has dropped the "orthogonal" framing of RQ4 and instead now says *"SMS shows near-zero rank correlation with simple pattern coverage (ρ = 0.16, n = 12, p = 0.74); statistical power at this n is insufficient to support an 'orthogonal' claim, framed instead as a hypothesis for future work."* This is the conservative reframing R0 W6 asked for. **HOWEVER, an unexpectedly serious problem**: §5.9.2 in the English manuscript is **empty** — only the section header at line 1294 with no content. The Chinese authoritative source `论文初稿P2.md` line 1408 contains a complete §5.9.2 *"与 SMS 的相关性"* with Spearman ρ = 0.107, Kendall τ = 0.073, scatter-plot reference, plus a complete §5.9.3 interpretation. **The English translation has dropped both §5.9.2 body and the entirety of §5.9.3.** This is a P0 manuscript-level cross-version coherence failure introduced by the R-1 translation commit (`37fa9bb`). |
| **W7** | Scalar `float→float` PUT systematic deflation, no industrial-scale comparison | §3.1.1(d); §7.5 line 1543 | **✗ Not Addressed** (but mitigated by title rescope) | W7 fix asked for either §3.1.1(e) industrial-PUT comparison or a vector-state toy experiment. Neither was added. The scalar-signature deflation remains unquantified. **However**, the title rescoping to *"Single-Output Scientific Computing Kernels"* (DA-CRITICAL-1) honestly fences the over-claim. The risk is reduced by scope, even though the W7 fix itself is not done. |
| **W8** | §9 formal weight vs IST empirical expectations + L1–L6 dependency | §9.2 lines 1604–1623; §9.3 Lemma 9.1 line 1631 | **✓ Verified Addressed** | §9.2 substantially rewritten (commit `3bc5267` P1-3): 6-axis L1–L6 collapsed into 3 joint conditions (L_equiv = L1∧L2; L_killed = L3∧L4; L_mut = L5∧L6) with explicit pairing-rationale paragraphs. Lemma 9.1 line 1631: *"almost everywhere equivalent to ∀x ∈ D_S \ N, S_i(x) = s'(x), where N is a D_S-measure-zero set."* Abstract line 14 and §1.2 line 50 now consistently use "modulo D_S-measure-zero subsets". Lemma 9.2 r ≠ id case (line 1640) improved closer to my suggested "transformed-input oracle" wording, though Ammann & Offutt 2008 §11.4 anchor citation is still absent. Length-compression sub-fix not done, but principal rigor sub-fix done. |

**R0 W-series score**: 2 ✓ verified (W2, W8) + 4 △ partial (W1, W4, W5, W6) + 2 ✗ not addressed (W3, W7).

---

## 2. Verification Matrix — 5/5-Consensus Editorial Decision Concerns (P0 / CRITICAL)

| # | Editorial CRITICAL / P0 | Revision claim location | Verified? | Evidence + brief comment |
|---|---|---|---|---|
| **C1 / P0-1 / DA-CRITICAL-1** | Title-evidence misalignment | Title line 5; Abstract line 14; §1.6.2 | **✓ Verified Addressed** | Title exactly reproduces the editorial-arbitration target string (`editorial_decision.md` line 84): R3's "Single-Output Scientific Computing Kernels" + DA's "Same-Prompt" both present. Abstract line 14 contains mandated additions (b) *"each PUT a Python function with `float → float` signature, source code under 2 KB"* and (c) *"under identical prompt template"*. §1.6.2 line 119 *"SMS is an epistemological semantic detection metric"* — mandated scope statement present. Headline now legitimately matches what the experiment tested. |
| **C2 / P0-2 / DA-CRITICAL-4** | "17.6:1 ratio" composite number | grep on EN file | **✓ Verified Addressed** | grep "17.6" returns **zero hits**. §6.1 line 1308 replaces with two-separate-contrasts narrative ending *"…cannot be synthesized into a single factor decomposition ratio."* This is exactly what DA-CRITICAL-4 demanded. |
| **C2 / P0-3 / DA-CRITICAL-2** | "严格达成" downgrade + Abstract reports v3 primary 3/4 only | §5.8.2 line 1231; §6.3 line 1332; Abstract line 14 | **✓ Verified Addressed** | §5.8.2 now: *"v3 (pre-registered): 3 / 4 (partial); v3b (exploratory, post-hoc): 4 / 4 (conditional on c-class primary MP shift, §3.5.1); v4 cross-source pool maintains 4 / 4 under v3b condition."* — "严格 / strict" is gone, and the conditional structure is explicit. Abstract: *"We report v3 as the H4 primary result."* §6.3 closes: *"cross-class consistency verdict is based on v3 pre-registered = partial (sign test 3/4)."* DA-CRITICAL-2 mandates (a) (b) (c) (d) all met. |
| **C3 / P0-4 / DA-CRITICAL-3** | c-class MP shift max-selection inflation quantified | §3.5.1 (referenced); §7.1.8 line 1469; permutation commit `d033334` | **△ Partially Addressed** | §7.1.8 line 1469: *"Bonferroni upper bound α_effective = 0.01 (§3.5.1 P0-4 revision), permutation p-values in `data/results/c_class_permutation_v4.json`."* Supporting analysis-script commits exist (`5995c4a`, `d033334`). **But §3.5.1 itself does not appear as a section header in the English manuscript** (see Residual 3.1). CRITICAL-3 mathematical fix is done; the English exposition is missing. |
| **C4 / P0-6 / DA-MAJOR-6** | IST 2024 [Authors TBD] removal + replacement | §8 (line 1547); line 1185 dangling citation | **△ Partially Addressed** | §8.3 references list **no longer contains the [Authors TBD] phantom entry** (commit `ae660bd`). The "0.30–0.45 range" claim that depended on it has been quietly dropped from §1.3.2 (compared with the original v3 manuscript). **However, line 1185 still contains** "*medium effect is stable and consistent with LLM-mutant literature (Tip 2024, IST 2024)*" — this is now a dangling citation. **Cleanup required: scrub "IST 2024" string from line 1185 (replace with Tip 2024 only) before submission.** |
| **C5 / P0-5** | v4-pre grid OR explicit chained-conditioning declaration | §4.2.5 line 736; §7.1.8 line 1465 | **✓ Verified Addressed** (option b chosen) | §4.2.5 line 736 carries the full chained-conditioning declaration ending *"This declaration makes the conditional nature of the v3b → v4 contrast explicitly visible, not dependent on reader inference."* §7.1.8 R11 cross-references it. Authors elected editorial fix-b (explicit declaration) rather than fix-a (run v4-pre). The Round-1 reject trigger ("if v4-pre runs and \|Δδ_LLM_pre\| > 0.05 outside zero CI") is moot since v4-pre was not run; title rescope + conditional framing are sufficient compensating controls. |
| **C6 / P0-7** | Pre-registration claim evidence (OSF or git-time-stamped protocol) | §1.5, §3.5.1 (chinese only), §5.2 | **✗ Not Addressed** | (Identical to W3 above.) No registration ID provided; "pre-registered" measure remains. This is the only **P0 with no fix attempt** that I can identify. |
| **C7 / P0-8** | §5.7.2 verdict wording + δ CI vs threshold | §5.7.2 line 1165; Abstract line 14 | **✓ Verified Addressed** | §5.7.2 line 1165 changes "rejected" → "not met under pre-registered point-estimate criterion". Abstract still uses "rejected" at line 14 (small inconsistency — see Residual 3.3) but immediately gives CI [0.017, 0.622]. Effective-n note (lines 1167–1172) propagates zero-mass dominance into the verdict. R1's TOST-style auxiliary not added; R0's part of P0-8 satisfied. |

**Editorial P0 score**: 5 ✓ verified (P0-1, P0-2, P0-3, P0-5, P0-8) + 2 △ partial (P0-4, P0-6) + 1 ✗ not addressed (P0-7).

---

## 3. Residual Concerns / New Issues

### 3.1 Cross-version translation drift (NEW, P0 severity)

The R-1 translation commit (`37fa9bb`, 2026-05-02) introduced **at least three structural omissions** in the English manuscript that do not exist in the Chinese authoritative source `论文初稿P2.md`:

1. **§3.5.1 has no English section header.** The Chinese `论文初稿P2.md` line 676 contains `#### 3.5.1 c 类 primary MP 选择:pre-registered v3 vs exploratory v3b` (the entire post-hoc selection caveat, the four bullets that DA-CRITICAL-2 / R0 W2 explicitly required visible). The English `论文初稿P2_EN.md` makes **17 cross-references to §3.5.1** but the section header itself is missing. An English reader cannot find the formal caveats. This is the one section that absolutely **must exist**, given how many P0 issues route through it. Since the Chinese version has the content and §7.1.8 R11 explicitly says *"§3.5.1 (P0-4 revision) added permutation + Bonferroni quantification"*, the analytical work was done — only the translation is missing.

2. **§5.9.2 is empty in English** (only header at line 1294). Chinese line 1408–1416 contains the full RQ4 correlation results: *"Spearman ρ = 0.107 (p = 0.741); Kendall τ = 0.073 (p = 0.767)"* plus a scatter-plot reference. **§5.9.3 ("解读" / interpretation) is wholly missing from English** — line 1417–1423 in Chinese contains the conservative-finding language and the b2/b1/c1/c2/c3 specific examples. Without §5.9.3, RQ4 in the English manuscript has results promised in §1.4 but never reported. RQ4 is RQ4.

3. **§3.5.0 / §3.6 (LRCA risk grid) and §3.7 (interface to §4)** appear in the Chinese version (lines 670–770) but appear truncated/missing in the English version — section navigation jumps from §3.4 (Experimental Scale) directly to §4. I did not inspect this in depth because §3.5.1 alone is the load-bearing failure.

**Severity**: P0. The English manuscript is the actual submission. Reviewers and the EIC office cannot accept "the math is in the Chinese". This is fixable in 2–3 hours of careful translation but **must be fixed before resubmission**.

### 3.2 §3.2.6.1 OS row not updated to reflect §3.2.6.3 empirics (NEW, P1 severity)

The user's question in the brief explicitly raised this: cross-checking §3.2.6.1 (line 559) against the new §3.2.6.3 (line 630). I confirm:

- §3.2.6.1 row at line 559 still marks: *"(No corresponding tool operator) | … | OS API replacement | ✗ Tool inexpressible"*
- §3.2.6.3 line 630 empirical: *"OS class aggregate 11.67% overlap rate (7/60, **new finding**): The pre-existing argument (§3.2.6.1 row 2) claimed that the OS class is completely unreachable by cosmic-ray; the 12-PUT empirics show that this claim is too strong in the categorical sense, and is in practice 88.33% disjoint + 11.67% incidental hits."*

The §3.2.6.3 conclusion paragraph (line 636) honestly self-flags: *"the OS row's '✗ not covered' mark in the §3.2.6.1 table is too absolute, and is empirically refined by this section to 88.33% disjoint + 11.67% incidental hits."* — but the table itself at line 559 is **not updated**. A skim-reader who reaches §3.2.6.1 first will not learn until §3.2.6.3 that the categorical claim is too strong. The most economical fix: change the OS line in the §3.2.6.1 table to "△ 11.67% incidental hits (see §3.2.6.3)".

The CE row likewise: §3.2.6.1 line 547 marks CE as "△ Literal values only" (correct, fine), but row at line 553 marks `BreakContinueReplacer`/CF correspondence as `— ✗ No correspondence`, while §3.2.6.3 line 632 reports CF aggregate 33.33% overlap (3/9) on b2. This is also an internal inconsistency to refine.

**Self-consistency between §1.2 abstract and §3.2.6.3 empirics**: I cross-checked. §1.2 line 46 says: *"5.14% overall AST overlap rate, with three classes — HP/SI/TF, totaling 159 mutants — at 0/0/0 overlap"*. §3.2.6.3 line 599 reports total = 1276 cosmic-ray + 292 P2; HP=72/0, SI=33/0, TF=54/0; sum = 72+33+54 = 159. The 159/292 = 54.5% claim is internally consistent. **Abstract / §1.2 / §3.2.6.3 are mutually self-consistent on the headline 5.14% / HP-SI-TF-categorical-zero numbers.** Good.

### 3.3 Abstract H2 wording: "rejected" vs §5.7.2 "not met" (NEW, P2 severity)

Abstract line 14 retains: *"The pre-registered H2 large-effect threshold (Cliff's δ ≥ 0.474, Romano 2006) **is rejected** in the primary v3 analysis (δ = 0.323, 95% CI [0.017, 0.622])"*. §5.7.2 line 1165 explicitly states it was changed *"from 'rejected' → 'not met under pre-registered point-estimate criterion'"*. The change was applied to §5.7.2 but not propagated to the Abstract. Since the Abstract immediately gives the CI, a careful reader recovers, but the wording inconsistency violates the editorial-letter principle of "caveat propagation through the full chain". A 5-character edit fixes this.

### 3.4 Romano 2006 venue + missing Vargha & Delaney 2000 / Ammann & Offutt 2008 (NEW, P2 severity)

R0 §8 noted: Romano 2006 is published at the Florida Association of Institutional Research, a non-mainstream venue. Adding Vargha & Delaney 2000 (*JEBS*) was suggested as a cross-reference for the 0.147 / 0.330 / 0.474 thresholds. The reference list at line 1573 still cites only Romano 2006 with a verbatim FAIR venue tag. No Vargha & Delaney; no Cliff 1993; no Ammann & Offutt 2008 (needed to anchor the §9.3 Lemma 9.2 r ≠ id "transformed-input oracle" argument as I requested in W8 fix-c). These are P2-level cleanup items (typesetting stage), but the EIC for IST will note these gaps.

### 3.5 Pre-registration claim is the **only** P0 with no attempt (NEW restatement)

This is the same issue as W3 / P0-7 above, but I want to call it out because it is **the single most surgical risk to round-2 acceptance**: the manuscript continues to use "pre-registered" in load-bearing positions (Abstract, H2 verdict, H4 verdict) without supplying registration evidence. The rest of the revision is methodologically scrupulous, which makes the un-evidenced "pre-registered" claim stand out as anomalous. A 30-minute fix (rename to "fixed prior to data collection per `docs/protocols/p2_analysis_plan_v3.md`, git commit `<HASH>`, dated 2026-XX-XX") closes this. There is no excuse not to do it.

### 3.6 Strengths preserved or new (NEW)

To balance the criticism, I record three substantive **gains** the revision adds:

1. **§3.2.6.3 12-PUT cosmic-ray empirical (NEW-MAJOR-1, commit `2547b61`)** is a substantive new contribution that meaningfully strengthens the originality argument. The 5.14% AST overlap with HP/SI/TF categorically zero is **positive evidence** (rather than mere argument) that P2 mutants are not a relabeling of syntactic mutants. This addresses a class of "new-concept relabeling" critique that R2 / R4 had implicitly raised. This is the single highest-leverage revision in the round.

2. **§9 P1-3 revision (commit `3bc5267`)** rewriting from 6 axes to 3 joint conditions is an unambiguous formal-rigor improvement. The L1–L6 dependency was an EIC-perspective worry that R2 worded most strongly; the joint-condition formulation directly addresses it.

3. **R2 methodology framework restructure (commits `7847dea` through `9542b0f`, T1–T6)** elevates the paper's framing from "60-cell empirical with degeneration theorem" to a three-layer methodology (Layer 1 definitional / Layer 2 operational / Layer 3 applied) with the empirical audit demoted to an "auxiliary finding". This is a courageous and correct narrative move: it sidesteps the editorial-letter criticism that the empirical headline was structurally fragile, and it puts the contribution where it actually is — the methodology, not the H2 verdict. **As EIC I find this restructure improves the paper's IST-fit substantially.**

---

## 4. Updated EIC Decision

### Decision: **Minor Revision** (downgraded from Major Revision)

### Justification (3 sentences)

The five-of-five-consensus editorial CRITICAL items (Title, 17.6:1, "严格" downgrade, IST 2024 [Authors TBD] removal, P0-8 verdict wording) and the methodologically substantive items (P0-2, P0-3, P0-5, P0-8) are all closed in spirit, and the new §3.2.6.3 12-PUT 5.14% empirical plus the §9 joint-condition rewrite measurably strengthen the paper above its Round-1 footing — the structural fragility R0 W1 worried about has been resolved by retitling-plus-conditional-framing rather than by re-running v4-pre, which is an acceptable EIC-perspective trade. **However**, three execution-level defects must be cleaned before the manuscript can be accepted: (i) **§3.5.1 must be present in English** (currently the section is referenced 17 times but has no English header; this is a P0 cross-version drift), (ii) **§5.9.2 / §5.9.3 RQ4 results must be translated** (currently empty in English while complete in Chinese), and (iii) **the "pre-registered" claim must be evidenced or renamed** (still the single un-attempted P0 from R0 W3 / editorial P0-7). These are 4–6 hours of work, not new experiments, hence the Minor Revision designation. The remaining △ items (W4 line 1185 IST 2024 dangling, W5 §1.3.2 "closely matching" residual, §3.2.6.1 OS-row update, Abstract "rejected" vs §5.7.2 "not met" wording inconsistency, missing Vargha & Delaney + Ammann & Offutt citations) are P2-level typesetting fixes that should not block the next round.

### Posture change rationale

In Round 1 I gave 6.7/10 with verdict Major Revision. The principal reason was that the headline ablation was structurally fragile (W1) and the v3b post-hoc selection was contaminating the verdict (W2). Both have been addressed: W2 fully and W1 conditionally (via re-titling rather than v4-pre data, but the conditional framing is honest and visible). The revisions also added a substantive new empirical (§3.2.6.3 NEW-MAJOR-1) and a meaningful theoretical sharpening (§9 joint conditions). The unaddressed W3 and the new translation drift (§3.5.1 / §5.9 in English) are mechanical issues, not methodological. I therefore upgrade my dimension scores:

| Dimension | Round 1 | Round 2 | Δ |
|---|---|---|---|
| D1 Originality | 6 | 7.5 | +1.5 (NEW-MAJOR-1 12-PUT empirical) |
| D2 Significance (IST) | 7 | 7.5 | +0.5 (three-layer framing) |
| D3 Methodological Rigor | 7 | 8 | +1 (chained-conditioning explicit, P0-4 done in spirit) |
| D4 Clarity & Writing | 7 | 6.5 | **−0.5** (translation drift, dangling citations) |
| D5 Reproducibility | 8 | 7.5 | −0.5 (W3 "pre-registered" still un-evidenced) |
| D6 Soundness of Claims | 6 | 8 | +2 (W2 ✓; W1 △ but defensible; P0-2/3 closed) |
| D7 Practical Implications | 7 | 7 | 0 |
| **Overall (weighted)** | **6.7** | **7.4** | **+0.7** |

A 7.4 aggregate maps to the *Minor Revision / Major Revision* boundary in the editorial scoring rubric. Given that all remaining items are mechanical (translation completion + 5 small text fixes), and that no further experimental work is required, **Minor Revision** is the correct verdict. If the §3.5.1 and §5.9.2/3 translations were already in place I would consider Accept-with-conditions.

### Conditions for Accept (after Round 2)

1. **§3.5.1 fully translated and inserted into the English manuscript.** This section is the load-bearing caveat for P0-2/3/4/5; an English reader currently cannot reach it.
2. **§5.9.2 and §5.9.3 fully translated.** RQ4 currently has no results in the English manuscript despite being declared in §1.4.
3. **W3 / P0-7 closed**: either supply OSF / aspredicted registration ID + URL + date, or rename "pre-registered" → "fixed prior to data collection per [protocol document], git commit `<HASH>`" globally.
4. **Line 1185 dangling "IST 2024" citation** scrubbed (replace with "Tip 2024" only).
5. **§1.3.2 line 80 "closely matching"** softened to neutral language consistent with §6.1's "numerical coincidence, not mechanism validation".
6. **§3.2.6.1 OS-row update** to "△ 11.67% incidental hits (see §3.2.6.3)" so the categorical-vs-empirical inconsistency is resolved at the table level, not only in the §3.2.6.3 conclusion paragraph.
7. **Abstract H2 wording**: change "is rejected" to "is not met under the pre-registered point-estimate criterion" to align with §5.7.2 line 1165.
8. **Add Vargha & Delaney 2000 (JEBS) and Ammann & Offutt 2008** to §8.5 / §8.1 respectively (P2 typesetting cleanup, not blocking).

### What would push back to Major Revision

If on re-submission §3.5.1 is still missing in English **or** the "pre-registered" claim is still un-evidenced, I would return to Major Revision. The reason is that both are structural integrity issues (the first is a manuscript-completeness failure visible to any English-only reviewer; the second is a methodological-honesty issue under IST norms for empirical SE).

### What would push to Reject

Nothing in the current revision. The Round-1 reject trigger was *"if v4-pre runs and shows Δδ_LLM > 0.05 outside zero CI"*; the authors elected not to run v4-pre and instead re-titled, which is an editor-acceptable resolution. The methodology is now self-consistent at the headline level.

---

## 5. Closing Note

The revision is, on the whole, **methodologically responsive** in the sense that R0 cared about: the authors did not paper over the editorial-letter CRITICAL items, they made structural changes (Title, narrative, three-layer methodology framing). The §3.2.6.3 NEW-MAJOR-1 work and the §9 P1-3 rewrite are evidence-grade additions, not just rhetorical compliance. The single category of remaining problems — translation drift between Chinese authoritative source and English submission — is mechanical and should not survive the next 6 hours of editorial polish. Subject to closing the eight conditions above, the manuscript is publishable in IST.

**Final EIC verdict: Minor Revision; conditional Accept after the eight-item checklist closes.**

---

*Reviewer R0 (EIC) — 2026-05-02 (Round 2 verification)*
