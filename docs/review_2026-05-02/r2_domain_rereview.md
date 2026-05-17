# Reviewer 2 (Domain) — Verification Re-Review (2026-05-02)

**Manuscript under re-review**: *When Same-Prompt LLM Source Diversity Doesn't Help: An Ablation of Semantic Mutation Operators in Metamorphic Testing for Single-Output Scientific Computing Kernels*
**File**: `<P2_SOURCE_PATH>/论文初稿P2_EN.md` (1700 lines, English; 2026-05-02 snapshot)
**Reviewer role**: Domain (mutation testing / scientific-computing software / MT literature). Independent of R0/R1/R3/R4.
**Re-review scope**: Verify resolution of W1-W10 from `<P2_SOURCE_PATH>/docs/review_2026-05-01/r2_domain.md`; assess the new three-layer methodology backbone, the new §3.2.6.3 12-PUT empirical, and the [Authors TBD] withdrawal.

---

## 1. Verification Table for Original W1–W10

| # | Original concern (R2 2026-05-01) | Revision claim location | Verified? | Domain evidence + comment |
|---|---|---|---|---|
| **W1** | Double taxonomy confusion (mut_C/M/G/T/F vs CE/OS/HP/TF/SI); no bridging table | §3.2.0 (lines 462–470) and §3.2 head (lines 437–446) | **✓** | The new §3.2.0 contains the 5×3 mapping table (CE/OS/HP/TF/SI rows × (a)(b)(c) columns) with "primary satisfied condition" (line 464). The §3.2 head (line 437) explicitly identifies the 5 classes as **meta-mutation operators** with PUT-class specialization rules. The §3.2.6.1 OS-row downgrade (line 514, "△ Mostly not covered") now cross-refs §3.2.6.3 empirics. **However**, the bridging is one-directional: CE/OS/HP/TF/SI (operator-domain rubric) is now the dominant taxonomy throughout §3.2.0/§3.2.6/§3.2.6.3, while mut_C/M/G/T/F (semantic-invariant rubric) survives only in §3.2.1–§3.2.5 subsection headings (lines 476–505). The new Abstract (line 14) inconsistently uses both — "five domain-semantic mutation operators (Conservation, Monotonicity, Convergence, Trajectory, Fidelity-order breaks)" intermixed with "(CE/OS/HP/TF/SI)". This is residual W1 noise, but no longer a substantive confusion — readers can infer the intra-operator dual labeling. **Borderline ✓**. |
| **W2** | mutmut/cosmic-ray default-subset list (12 entries) is incomplete; subset disclaimer missing | §3.2.6.1 (lines 543–564) | **△ partially** | The list of 12 syntactic operators (lines 547–558) was *not* expanded to 25–30 default operators as I requested. The strengthening was instead epistemic: line 564 now states "**This is structural unreachability, not a matter of operator set size — even if the tool operator set is expanded from 12 to 100, as long as each entry remains AST-local and domain-agnostic, the 4 semantic operator classes remain inexpressible**." This is the structural-argument fix from my W2 *FIX (b)*, and is *more* defensible than fix (a) (subset labeling). I accept this. The version disclaimer ("default operator subset of mutmut 2.4 / cosmic-ray 8.3") was *not* added — minor typesetting omission. The revision is acceptable but I would still prefer a one-line "mutmut 2.4 / cosmic-ray 8.x default" version-pin caveat in the table header. |
| **W3** | §9 L1–L6 not independent; redundant 6-axis structure | §9.2 (lines 1604–1623) | **✓** | §9.2 is now explicitly rewritten as **3 joint conditions** (L_equiv = L1∧L2; L_killed = L3∧L4; L_mut = L5∧L6) with "pairing rationale" prose for each. Line 1606: "**L1–L6 are not 6 independent axes**, but paired joint conditions (this revision responds to the dependency queries in R0 W8 / R1 §4 / **R2 W3** / DA-MAJOR-3)." The three lemmas (9.1–9.3) now correspond one-to-one with the 3 joint conditions. This is exactly the fix I prescribed in W3 *FIX*. |
| **W4** | Strict-vs-asymptotic ambiguity in §9 main theorem; abstract said "strictly degenerate" but §9.2 uses → notation | Abstract (line 14), §9.2 (line 1611), Lemma 9.1 (line 1627), Theorem 9.1 (line 1648) | **✓** | Lemma 9.1 (line 1627) is now retitled "(equiv degeneration, P1-3 revision: added measure-zero qualification)" and states "degenerates to classical behavioral equivalence **almost everywhere** (almost everywhere w.r.t. measure D_S)". Theorem 9.1 (line 1648) reads "In the degenerate limit L = L_equiv ∧ L_killed ∧ L_mut, **almost everywhere** (almost everywhere w.r.t. D_S), SMS → MS". Abstract (line 14) now says "modulo D_S-measure-zero subsets". This is exactly W4 *FIX*: "almost-sure equality under D_S, not strict equality". The conclusion sentence (line 14) also says "(modulo D_S-measure-zero subsets, see §9 for the formal statement)". |
| **W5** | "0.30–0.45 contextual support" cross-estimand over-translation, repeated 4 places | §1.3.2 (line 80), §5.7.2 (line 1174), §6.1 (line 1308 + 1312), §7.1.6 — | **△ partially** | All four originally-flagged loci now carry an explicit "**Estimand caveat**" sentence: §1.3.2 (line 80), §5.7.2 (line 1174), §6.1 (line 1308), and §6.1 (line 1312, the "Contextual consistency" paragraph). Each caveat states: "Tip 2024 compares 'LLM mutants vs traditional mutants on fault-detection rate' ... this paper's §5.7.2 compares 'aligned vs cross MP slice' ... numerical similarity does not constitute substantive support". The wording is *exactly* W5 fix (ii) language ("estimand异质性警示"). **However**, line 1185 (§5.7.2 closing "Interpretation" block) still says **"medium effect is stable and consistent with LLM-mutant literature (Tip 2024, IST 2024)"** — a *residual fifth occurrence* that (i) still cites the IST 2024 reference that was supposedly withdrawn (see W6), and (ii) lacks the estimand caveat. This is a missed cleanup. The §7.1.6 bullet I originally flagged appears to no longer literally cite Tip 2024 (line 1450–1454 only refers to LLM-homogeneous-pool ceiling), which is appropriate. **Recommendation**: line 1185 must be edited to remove "IST 2024" entirely and either drop or estimand-caveat the Tip 2024 reference. |
| **W6** | §8.3 "[Authors TBD]" placeholder; 4 in-text citations depend on this | §8.3 (line 1564); commit ae609f1 (2026-05-01) | **✓ honorably** | Commit ae609f1 message confirms the authors did the right thing: "§8.3 [Authors TBD] entry resolved to Moradi Dakhel et al. (2024) ... via Crossref (DOI 10.1016/j.infsof.2024.107468). The paper is verified to exist but is about LLM-generated TESTS guided by mutation analysis, NOT about LLM-generated mutants — therefore it cannot support the 'LLM-mutant Cliff's δ 0.30-0.45 contextual support' claim". They withdrew the reference and downgraded the 4 in-text citations to Tip 2024 + estimand caveat. §8.3 now has a single Tip et al. (2024) entry (line 1564). This is **handled honorably** — the authors did exactly what fallback (W6 fix) prescribed: "if verification fails, delete the reference, change to Tip-only + caveat". *Spot-check status*: §1.3.2 (line 80) ✓ Tip-only + caveat; §5.7.2 (line 1174) ✓ Tip-only + caveat; §6.1 (lines 1308, 1312) ✓ Tip-only + caveat; §7.1.6 (line 1450) ✓ no longer cites IST 2024 in the new version. **One residual leak** at line 1185 — see W5. |
| **W7** | 12-PUT × ~150 LOC toy-program scope vs IST "first audit" framing | Abstract (line 14, "each PUT a Python function with `float → float` signature, source code under 2 KB"); §3.1.1 (lines 429–431, scalar simplification limitation); §1.6.2 (line 119) | **△ partially** | Abstract now explicitly bounds scope: "12-PUT × 5-MP matrix (60 cells, average 24.3 LLM-generated mutants per cell, N=20 AVP repetitions) across four classes of single-output scientific computing kernels (each PUT a Python function with `float → float` signature, source code under 2 KB)". The §3.1.1 (line 431) "Limitation" paragraph also adds "scalarized PUTs ... impose an upper bound on the semantic complexity of mutants, potentially systematically underestimating SMS and cross-class differences on industrial PUTs." However, **§1.6.2 was NOT augmented** — line 119 remains the original two-sentence statement: "SMS is an epistemological semantic detection metric, not an engineering value proxy." My W7 fix asked for an additional sentence in §1.6.2 making toy-scope an explicit *epistemological* boundary statement. The fix is *partial*: scope is documented in two engineering loci (Abstract, §3.1.1) but not in the §1.6.2 framing locus. Acceptable, but I would still upgrade §1.6.2. |
| **W8** | §3.2.6 HOM caveat defers to R12 but main argument depends on first-order tool unreachability | §3.2.6 (line 521, "Higher-Order Mutation (HOM) caveat"); §3.2.6.0 (lines 527–539); §3.2.6.3 (line 638, "Scope caveat") | **✓** | §3.2.6 line 521 now contains an explicit scope statement: "the 'tool unreachability' claim in §3.2.6 is strictly limited to first-order syntactic tools (mutmut / cosmic-ray default configurations belong to this class)" — this is the W8 *FIX* "scope of this comparison: limited to first-order syntactic mutation tools, not HOM". Jia & Harman (2009 SBSE) and Kintis et al. (2018 STVR) are cited at the same place. The new §3.2.6.0 (systematic-vs-incidental) provides a *positive* counter-argument that even *if* HOM produced an OS-like mutant by AOR + SDL combination, this would be stochastic byproduct, not a systematic semantic mutation method (line 539). This converts the W8 "argument incomplete because HOM might breach tool-unreachability" critique into "argument is robust under both first-order and higher-order tools, because the systematic-vs-incidental distinction operates at the *method* level, not the *output* level." This is a clean fix. |
| **W9** | CPH and coupling effect entirely missing; Andrews 2005 / Papadakis 2019 / DeMillo 1978 not cited | §1.3.2; §6.1; §8.1 References | **✗ NOT addressed** | Searched the manuscript for "competent programmer", "DeMillo", "coupling effect", "Andrews", "Papadakis 2019". Result: zero hits except Kintis-Papadakis 2018 (which is correctly cited at §8.1 line 1555 — but this is a different Papadakis work; the requested Papadakis et al. 2019 *Advances in Computers Ch. 6* "Mutation Testing Advances: An Analysis and Survey" is not present). Mothra/Proteum mentioned at §9.2 line 1619 and §9.3 line 1644 *without literature citations* (DeMillo 1988 / Maldonado 2001 not in §8). **The §1.3.2 domain-CPH paragraph I requested in W9 *FIX* is absent.** This is a meaningful gap because (i) the new §3.2.0 necessary conditions (a)(b)(c) implicitly invoke a *domain-CPH* premise (that domain experts make errors in cross-function-boundary / domain-knowledge / algorithm-class dimensions, paralleling DeMillo's CPH that ordinary programmers make errors close to syntactic mutants), and (ii) the §3.2.6.3 12-PUT empirical (94.86% AST-disjoint) is essentially a *coupling-effect-style* argument that semantic-domain mutants do not couple to syntactic mutants — without citing Jia & Harman 2009 / Kintis 2018's coupling-effect literature, this argument loses its anchor. The R2 priority on this is moderate (P2), but it is a *literature coverage* gap, not a *narrative* gap. **Status: not addressed in this revision; should be added in next round.** |
| **W10** | §9 Corollary 9.1 LRCA trivialization — per-C_k causal attribution wrong (C2 depends on L6 not L4; C5 depends on L5 not L6) | §9.5 (lines 1664–1673) | **△ partially** | §9.5 retains the per-C_k attribution (line 1668 "C2 triggering depends on L4 not holding"; line 1671 "C5 triggering depends on L6 not holding"). The original W10 critique pointed out that **C2 actually depends on L6 (deterministic-program assumption) rather than L4 (MP set restriction) — because under L6, fail-ratio is 0 or 1 deterministically, so the L1-tolerance-noise C2 trigger simply cannot fire**. Similarly C5 (mutator artifact) depends primarily on L5 (rule-based syntactic operators eliminate the C5 *trigger semantic space*), not L6. The current §9.5 attribution is therefore mathematically defensible only as "*a sufficient condition for non-triggering*" — but the *minimal* sufficient condition is different from what is reported. The W10 *FIX* recommendation was either to (a) write an explicit dependency table per (C_k, L_i), or (b) collapse to "under L, all triggering conditions structurally collapse, hence root_cause → C1". **Neither was done.** The corollary's attribution remains incorrect on at least 2/4 entries. This is residual W10 — substantive but minor (corollary, not main theorem). |

---

## 2. Residual / New Domain Concerns

### N-D1. Is the three-layer methodology backbone a substantive contribution, or a re-labeling?

This is the central domain question for re-review, since R2 T1–T6 framework restructure (commits 7847dea / b5342ec / 3a85e15 / c29019f / dce19b5 / 9542b0f) explicitly raises P2's contribution claim from "60-cell empirical audit + H2 negative finding" to "semantic-mutation methodology contribution + empirical audit demonstration". The new Abstract Conclusion (line 14) says: "P2 contributes a three-layer methodology for domain-semantic mutation: (Layer 1) formal necessary conditions ... (Layer 2) E1 ∧ E2 equivalence judgment ... (Layer 3) AST-normalized empirical traceability".

I evaluate each layer with skepticism:

**Layer 1 (Definitional, §3.2.0): Are necessary conditions (a)(b)(c) substantively new?**

- (a) **Cross-function-boundary replacement** — this is *not* present in Jia & Harman 2011 §1 or §3, where mutation operators are defined at AST-node level without scope qualifier. The closest prior art is Kintis et al. 2018 STVR's coupling-effect analysis, which discusses "interface mutators" but does not formalize cross-function-boundary as a *necessary condition*. (a) is moderately novel.
- (b) **Carries domain knowledge** — this is the central *concept* of LLM-mutation work since Tip 2024 LLMorpheus (which uses LLM precisely *because* domain knowledge is needed); but Tip 2024 does not formalize "domain knowledge" as a *necessary condition* with a formal definition. The §3.2.0 definition ("legality of the mutation depends on mathematical/physical/statistical knowledge of the program's domain") is operational but not new — it codifies the *implicit* premise of the entire LLM-mutation literature. (b) is a contribution at the *codification* level only, not the *concept* level.
- (c) **Changes algorithmic class** — this is the most novel of the three. Algorithm-class mutation (RK4 → Euler, dropout 0.5 → 0) is occasionally discussed in DL-mutation work (DeepMutator, DeepCrime) but not as a formal *necessary condition*. (c) is novel.

**Verdict on Layer 1**: Moderately substantive contribution. The CE/OS/HP/TF/SI taxonomy itself is not new (P2 v1 had it), but the (a)(b)(c) necessary conditions are a useful *formal scaffold* that the prior literature lacks. **(c) is the strongest novelty driver**; (a) is moderately novel; (b) is codification of existing implicit premise.

**Layer 2 (Operational, §2.3 / §4.4): Is E1 ∧ E2 equivalence detection as Layer-2 instantiation substantive?**

- §2.3 lines 247–253 give a 3-row table: E1 alone / E2 alone / E1 ∧ E2 with false-positive, false-negative, SMS-bias columns. This is **not new**: equivalent-mutant detection has used multi-criterion conjunctions since Offutt-Pan 1996 ("Detecting equivalent mutants and the feasible path problem"). Petrović 2018 ICSE-SEIP uses survival-ratio + behavioral-equivalence dual criterion in Google's industrial pipeline. Naik & Dustdar 2024 uses test-failure-rate + bytecode-equivalence. The choice E1 ∧ E2 is a sensible *instance* but not a methodological novelty.
- The novelty of this layer is the *mapping* to (a)(b)(c) of Layer 1 (line 243 maps E1 ↔ converse-of-(c), E2 ↔ converse-of-(a)(b)). This *mapping* is new; the underlying judgment is not. The Layer-2 contribution is therefore primarily *expository*, not *substantive*.

**Verdict on Layer 2**: Mostly re-labeling. The E1 ∧ E2 dual-conjunction was already in the original P2 (§2.3 of the pre-R2 version); it has merely been re-framed as "Layer 2 instantiation of Layer 1 conditions". A *skeptical* domain reviewer would say this is *useful packaging*, not *new methodology*. The re-framing is not deceptive — it serves the narrative — but it is not where the contribution sits.

**Layer 3 (Applied, §3.2.6.3): Is the 12-PUT empirical traceability substantive?**

- The §3.2.6.3 12-PUT empirical (5.14% overall AST-disjoint, 94.86% disjoint, HP/SI/TF at 0/0/0) is **the strongest substantive piece of the entire restructure**. To my knowledge, **no prior LLM-mutation paper has done a categorical AST-overlap analysis between LLM-generated mutants and syntactic-tool mutants on a multi-PUT basis**. Tip 2024 LLMorpheus reports fault-detection comparison but not AST-set overlap. Kintis et al. 2018 do mutation-tool effectiveness comparison but with manual labeling, not normalized AST diff.
- The methodological move — "treat the question 'are LLM mutants a subset of syntactic mutants?' as an *empirical AST set-difference question*, computable by `ast.dump`-normalized canonical forms" — is genuinely new. The result (HP/SI/TF *categorically* unreachable; CE 7.81% / OS 11.67% / CF 33.33% partial reach) is a clean, falsifiable, replicable finding.
- This is **R2 T5's most defensible deliverable**. It transforms §3.2.6 from a *categorical structural argument* (W2's original concern: "I can't verify the structural-unreachability claim because mutmut's actual operator set may differ") into a *positive empirical*. This is a real domain contribution.

**Verdict on Layer 3**: Substantive and IST-publication-grade. This is the strongest layer.

**Overall on the three-layer backbone**:

- Layer 1: moderately substantive (especially (c) algorithmic-class condition); part scaffolding.
- Layer 2: mostly re-labeling of pre-existing E1 ∧ E2.
- Layer 3: substantive, novel empirical method + novel finding.

**Concern**: The Abstract Conclusion (line 14) presents the three layers as if all three were equal contributions. From a domain-MT perspective, this is *slightly* over-stated — the contribution weight is approximately Layer 1 (30%), Layer 2 (15%), Layer 3 (55%). The narrative would be more honest if it foregrounded Layer 3 as the primary empirical deliverable, with Layer 1 as the formal scaffold and Layer 2 as the mid-tier instantiation glue.

**This is residual concern N-D1**, not a *fix-or-reject* issue. The framework is real; the relative weighting is moderately over-egalitarian.

### N-D2. Does §3.2.6.3's OS partial-overlap (88.33% disjoint, 11.67% incidental hits) actually weaken the categorical claim?

This is the question I want most to scrutinize as Domain reviewer, because §3.2.6.3 honestly reports a **deviation from the §3.2.6.1 categorical claim**:

- §3.2.6.1 row 2 originally claimed: "OS API replacement | (No corresponding tool operator) | ✗ Tool inexpressible".
- §3.2.6.3 12-PUT empirical (line 630, "OS class aggregate 11.67% overlap rate (7/60, **new finding**)") reports that the categorical claim "is **too strong** in the *categorical* sense, and is in practice **88.33% disjoint + 11.67% incidental hits**".
- The hits concentrate on DeepSeek outputs for a3 and b3, all low-syntactic-complexity OS sub-expressions (e.g., `dx**2` → `dx*dx` in a3 FDM, an algebraically equivalent rewrite incidentally hit by cosmic-ray BinOp).
- Line 514 of §3.2.6.1 has been edited consistently: OS row reads "△ Mostly not covered (§3.2.6.3 empirics 88.33% AST-disjoint; a small number of low-complexity OS sub-expressions occasionally hit by tools)".

**Does this weaken the categorical claim?**

Technically, *yes* — the original "✗ Tool inexpressible" categorical claim was false. The empirical shows that ~12% of OS instances *are* AST-reachable by cosmic-ray (specifically by `ReplaceArithmeticOperator` BinOp on syntactically simple algebraic rewrites). The §3.2.6.1 row was honestly downgraded to △.

**But does this collapse the methodology?**

**No, and here is why** — and this is the *strongest* part of the §3.2.6 / §3.2.6.0 / §3.2.6.3 design as a whole:

1. The §3.2.6.0 systematic-vs-incidental argument (lines 527–539) is *exactly* the right defense against this concern. The 11.67% hits are *stochastic byproducts* of cosmic-ray's BinOp on syntactically simple expressions; they (a) are not repeatable across LLM seed (DeepSeek-only), (b) are not produced by LLM design intent (the LLM chose `dx*dx` because it is *semantically equivalent on this PUT*, not because it intended a syntactic rewrite), (c) lack the engineering function of "deepening source-code understanding" — the rewrite is trivial.
2. The §3.2.6.3 conclusion (line 636) honestly says: "the OS class's overall 88.33% AST-disjointness still systematically rules out an 'OS = AST-local' classification." This is the right reading.
3. The HP / SI / TF triad remains at *categorical* 0/0/0 disjoint over 159 mutants — these *are* the strongest cases for "structural unreachability". CE and OS are degraded to "partial overlap with explanation"; HP/SI/TF are airtight.

**So the OS downgrade does not weaken the methodology; it makes it more honest.** The narrative shift — from "OS unreachable" (categorical) to "OS *systematically* disjoint with incidental hits" (empirical + systematic-vs-incidental defense) — is exactly the move that converts a *brittle categorical* claim into a *robust honest* claim. This is the kind of intellectual move that R2 / IST referees reward.

**Verdict on N-D2**: The OS partial-overlap does *not* weaken the categorical claim. The §3.2.6.0 systematic-vs-incidental argument and the per-class breakdown (HP/SI/TF airtight; CE/OS partial; CF n=9 too small for conclusion, honestly noted on line 632) jointly give the right reading. The §3.2.6.1 OS-row downgrade from "✗" to "△" is appropriate. **No change required.** This is a *strength* of the revision, not a residual concern.

### N-D3. [Authors TBD] withdrawal handled honorably?

Spot-checked all four originally-flagged loci against the post-withdrawal manuscript:

- **§1.3.2 line 80**: Cites Tip et al. (2024) only. Has explicit "**Estimand caveat**" noting that Tip 2024 measures fault-detection rate cross-mutant-source while this paper measures aligned-vs-cross within a single mutant pool. Concludes "numerical proximity ... does not constitute substantive support". **✓ HONORABLY HANDLED.**
- **§5.7.2 line 1174 (Contextual observation block)**: Cites Tip et al. (2024) only. Has explicit "**Estimand caveat**". Concludes "**does not constitute weakening or reframing of H2**". **✓ HONORABLY HANDLED.**
- **§6.1 line 1308 (cross-source pool block)**: Cites Tip et al. (2024). Has explicit "**Estimand caveat**". **✓ HONORABLY HANDLED.**
- **§6.1 line 1312 (Contextual consistency block)**: Cites Tip et al. (2024). Has explicit "**Estimand caveat**". Concludes "**not a reframing of the H2 rejected verdict**". **✓ HONORABLY HANDLED.**
- **§7.1.6 line 1450**: No longer cites either Tip 2024 or IST 2024 in the new manuscript text (focused on mutant pool size R9 issue, with appropriate cross-source future-work pointer to P4). **✓ HONORABLY HANDLED.**
- **§8.3 line 1564**: Tip 2024 single entry. No "[Authors TBD]" placeholder. Reference is verifiable (URL https://www.franktip.org/pubs/llmorpheus2024.pdf). **✓ HONORABLY HANDLED.**

**One residual leak (already flagged in W5)**: §5.7.2 line 1185 still says "*medium effect is stable and consistent with LLM-mutant literature (Tip 2024, IST 2024)*". The "IST 2024" tail-citation here is a missed cleanup from commit ae609f1. This is a typesetting-stage edit but should not survive submission.

**Verdict on N-D3**: The withdrawal is handled with high integrity — exactly the response a domain referee hopes for. Commit ae609f1's commit message even articulates *why* the reference doesn't support the original claim ("LLM-generated TESTS guided by mutation analysis, NOT LLM-generated mutants"), demonstrating that the authors verified the content rather than just filling in author names. **One typo at line 1185 remains; otherwise this is exemplary handling of a literature-fabrication concern.** I rate this as the most-improved aspect of the revision.

### N-D4. Is §8 References APA-7 compliant with key MT/MS classics?

Inventory of §8 References (post-withdrawal, lines 1551–1589):

- **§8.1 Mutation-testing classics / surveys** (3 entries):
  - Jia & Harman 2011 TSE survey ✓
  - Jia & Harman 2009 IST HOM ✓
  - Kintis et al. 2018 EMSE manual analysis ✓
  - **Missing**: Papadakis et al. 2019 *Advances in Computers* Ch.6 "Mutation Testing Advances: An Analysis and Survey"; **DeMillo, Lipton & Sayward 1978** (CPH origin); **Andrews, Briand & Labiche 2005 ICSE** "Is Mutation an Appropriate Tool for Testing Experiments?". These three are the most-cited MT classics post-Jia&Harman. **W9 not addressed.**

- **§8.2 Industrial-scale mutation-testing practice** (2 entries):
  - Petrović & Ivanković 2018 ICSE-SEIP ✓ (referenced in §6.1 numerical-coincidence statement)
  - Petrović, Ivanković, Fraser & Just 2021 TSE ✓ (added since 2026-05-01 — addresses my W4 D6 score concern that only the 2018 was cited)

- **§8.3 LLM-based mutation generation** (1 entry):
  - Tip et al. 2024 LLMorpheus ✓
  - **No** [Authors TBD] placeholder. ✓

- **§8.4 Probabilistic / numerical mutation benchmarks** (2 entries):
  - Hu et al. 2022 DeepCrime ✓
  - Just, Jalali & Ernst 2014 ISSTA Defects4J ✓
  - **Missing**: Just, Jalali, Inozemtseva, Ernst, Holmes, Fraser 2014 FSE "Are mutants a valid substitute for real faults?" — this is the most-cited paper in LRCA/C1-real-fault-correlation discussions, and §6.1 Petrović numerical-coincidence statement should cite it. (My W9 priority-2 missing.)

- **§8.5 Statistical methodology** (1 entry):
  - Romano et al. 2006 Cliff's δ thresholds ✓ (cited in §5.7.2)

- **§8.6 Numerical / scientific computing reference** (1 entry):
  - Press et al. 2007 Numerical Recipes ✓

- **§8.7 Software / mutation-testing tools** (3 entries):
  - mutmut, cosmic-ray, mutpy with version pinning ✓ (good software-citation practice)

- **§8.8 Companion P-series papers** (2 entries):
  - P1 (SANER 2027 under review) ✓
  - P2-CN (NED) ✓

**Total**: 11 academic + 3 software + 2 P-series companions = **16 entries**. The user-stated count target (11/3/2) matches. APA-7 format is consistent: author, year, title, venue (italicized), pages, DOI/URL. Romano 2006 is conference-paper style without explicit DOI but the Florida Annual Meeting attribution is sufficient.

**Verdict on N-D4**: APA-7 compliance is good. **Coverage gap remains on W9** — DeMillo 1978 / Andrews 2005 ICSE / Papadakis 2019 / Just-Jalali-Inozemtseva 2014 FSE are still missing. These four references are *not* fatal for IST acceptance (Jia & Harman 2011 is the canonical reference and is cited correctly), but adding them would strengthen the related-work claim that "P2 is backward-compatible with classical MT". For a *Domain* reviewer, missing DeMillo 1978 in a manuscript that proposes "necessary conditions for mutation" is a noticeable lacuna. **Recommendation: add the four W9-listed references in next round.**

---

## 3. Updated R2 Domain Score (Per-Dimension)

| Dimension | Old Score (2026-05-01) | New Score (2026-05-02) | One-sentence justification |
|---|---|---|---|
| **D1. Domain motivation & literature positioning** | 7 | **7** | The new §3.2.0 (a)(b)(c) gives a clearer formal scaffold for "what is semantic mutation" than v1; but §1.3.2 still does not cite DeMillo 1978 / Andrews 2005 / Papadakis 2019 (W9 not addressed), so literature positioning is improved-but-not-fixed. |
| **D2. SMS novelty & generalization argument** | 7 | **8** | §9 rewrite as 3 joint conditions (W3) + measure-zero qualification (W4) closes both formal gaps I flagged; §9 is now a clean degeneration theorem with correct strict-vs-asymptotic language. The §2.3 Layer-2 framing of E1 ∧ E2 also adds expository clarity. **+1 from 7.** |
| **D3. Operator taxonomy & §3.2.6 tool comparison** | 6 | **8** | The single largest improvement: (i) §3.2.6.0 systematic-vs-incidental converts the categorical-structural argument into a positive method-level argument; (ii) §3.2.6.3 12-PUT AST-overlap empirical (5.14% overall, HP/SI/TF=0/0/0) provides falsifiable replicable evidence that the prior literature lacks; (iii) §3.2.6.1 OS-row downgrade from "✗" to "△" is honest and right; (iv) HOM scope qualifier (W8) added. The old D3=6 was constrained by W1 (taxonomy bridge), W2 (subset disclaimer), W8 (HOM scope). Three of four are now closed; **+2 from 6.** |
| **D4. 60-cell experimental design + 3-stage ablation** | 8 | **8** | Unchanged. The three-stage ablation (v3/v3b/v4) was already R2's strongest dimension; the new revisions do not affect it directly. The (P0-2) removal of "17.6:1 ratio" makes the contrast reporting cleaner but the underlying design is the same. |
| **D5. Statistical methodology** | 7 | **7** | Unchanged. R1's province; my W3/W4 fixes were on §9 (D2), not on §5. The (P0-3) sign-test downgrade and (P0-4) Bonferroni quantification are appropriate but already noted in original R2 §5.8.2 honesty. |
| **D6. Domain literature coverage** | 6 | **6** | Petrović 2021 added (small +). [Authors TBD] withdrawn honorably. **But** W9 still completely unaddressed: no DeMillo 1978, no Andrews 2005 ICSE, no Papadakis 2019 *Advances in Computers* Ch.6, no Just-Jalali-Inozemtseva 2014 FSE; CPH and coupling-effect terms still absent from §1.3.2. The two improvements offset the unchanged W9 gap. |
| **D7. Writing & referee-readiness** | 6 | **8** | The three-layer backbone narrative restructure (T1–T6) lifts the manuscript from "60-cell empirical with H2 negative" to "methodology contribution with empirical demonstration", which is *exactly* the framing IST referees expect for a contribution-track paper. The Abstract Conclusion (line 14) is now self-contained and signals the contribution clearly. The [Authors TBD] withdrawal (W6) and the estimand-caveat propagation across §1.3.2 / §5.7.2 / §6.1 (W5) materially close the over-translation issue. **+2 from 6.** Residual: line 1185 IST 2024 leak, §1.6.2 not updated for toy-scope, four W9 references missing. |

**Updated overall (arithmetic mean of 7 dimensions)**: (7 + 8 + 8 + 8 + 7 + 6 + 8) / 7 = **7.43**

**Compared to 2026-05-01 score of 6.71**: **+0.72**.

**Verdict shift**: The revision moves the manuscript from the *Major Revision lower band* (6.71) to the *upper Major Revision / lower Minor Revision band* (7.43). This is consistent with the editorial decision letter's stated 7.5+ ceiling for "after revision". I would not yet recommend Accept, because:

1. **W9 (CPH / coupling-effect / DeMillo 1978 / Andrews 2005 / Papadakis 2019)** is still completely unaddressed and is a real domain literature gap;
2. **Line 1185 IST 2024 typo** is a residual cleanup from the W6 withdrawal that *must* be fixed before submission;
3. **§1.6.2 toy-scope framing (W7)** still relies entirely on Abstract + §3.1.1; the *epistemological* layer should make scope explicit;
4. **Corollary 9.1 per-C_k attribution (W10)** is still imprecise on at least 2/4 entries.

But I would happily recommend **Minor Revision → Accept** if items (1)–(4) above are addressed in a single revision pass. None of the four require new experiments.

---

## 4. Decision Recommendation Updates

| Aspect | 2026-05-01 R2 | 2026-05-02 R2 re-review |
|---|---|---|
| **Verdict** | Major Revision | **Minor Revision** (was Major) |
| **Mandatory items for next round** | 9 fixes (W3, W4, W5, W6 mandatory; W1, W9 strongly recommended; W7, W8, W10 recommended) | **4 fixes**: (1) W9 CPH / coupling-effect citations; (2) line 1185 typo cleanup; (3) §1.6.2 toy-scope sentence; (4) §9.5 Corollary 9.1 attribution table or generic statement. |
| **D-score sum / mean** | 47 / 6.71 | **53 / 7.57** |
| **Confidence in next-round acceptance** | "If at least mandatory items addressed, can reach IST acceptance line" | **"If 4 residual items addressed, paper is ready for Accept"** |

---

## 5. Specific File / Line References (for author convenience)

The following file-line references are the load-bearing locations for my verification verdicts:

- **Layer 1 §3.2.0**: `<HOME>/.../论文初稿P2_EN.md` lines 448–474 (necessary conditions + 5×3 mapping table). **Verified ✓**.
- **Layer 2 §2.3 (E1 ∧ E2)**: lines 237–261. **Verified ✓**.
- **Layer 3 §3.2.6.3 (12-PUT empirical)**: lines 584–638. **Verified ✓**, this is the strongest Layer.
- **§3.2.6.1 OS-row downgrade**: line 514 (from "✗" to "△ Mostly not covered (§3.2.6.3 empirics 88.33% AST-disjoint)"). **Verified ✓**.
- **§3.2.6.1 100-operator generalization**: line 564 ("even if the tool operator set is expanded from 12 to 100, ... the 4 semantic operator classes remain inexpressible"). **Replaces W2 fix (a) with a stronger structural argument; ✓**.
- **§3.2.6 HOM scope (W8)**: line 521 ("strictly limited to first-order syntactic tools (mutmut / cosmic-ray default configurations belong to this class)"). **Verified ✓**.
- **§9.2 three-joint-conditions rewrite (W3)**: lines 1604–1623. **Verified ✓**.
- **§9 Lemma 9.1 measure-zero qualification (W4)**: line 1627; Theorem 9.1 line 1648. **Verified ✓**.
- **Abstract measure-zero language (W4)**: line 14, "(modulo D_S-measure-zero subsets, see §9 for the formal statement)". **Verified ✓**.
- **§1.3.2 Tip-only + estimand caveat (W5/W6)**: line 80. **Verified ✓**.
- **§5.7.2 estimand caveat (W5)**: line 1174. **Verified ✓**.
- **§6.1 estimand caveat (W5)**: lines 1308 + 1312. **Verified ✓**.
- **§8.3 references (W6)**: line 1564, single Tip 2024 entry, no [Authors TBD]. **Verified ✓**.

**Residual leaks / unaddressed**:

- **Line 1185 "Tip 2024, IST 2024"**: typo cleanup from commit ae609f1 missed this occurrence. **Action: edit to remove "IST 2024" and either drop or estimand-caveat the Tip 2024 reference.**
- **§1.6.2 line 119**: Two-sentence statement; no toy-scope framing added. **Action: append one sentence per W7 fix.**
- **§9.5 Corollary 9.1 lines 1668–1671**: Per-C_k attribution still has C2/L4 and C5/L6 swapped from minimal sufficient condition. **Action: generic statement per W10 fix (b).**
- **§1.3.2 / §6.1 / §8 W9 references**: DeMillo 1978, Andrews 2005, Papadakis 2019, Just-Jalali-Inozemtseva 2014 FSE all absent; CPH / coupling-effect terms missing. **Action: 1-paragraph addition to §1.3.2 + 4 entries to §8.1.**

---

## 6. Independence Statement

This re-review was conducted independently from R0/R1/R3/R4 re-reviews. I read only my own original R2 report (2026-05-01), the editorial decision package, the framework restructure plan, and the manuscript itself. No other reviewer's re-review report was consulted.

**Consensus alignment**: W3+W4 (P1-3), W5 (P0-2/6), W6 (P0-6) — all P0/P1 priority editorial items — are the most-fully closed in this revision. W9 (P2-3, P2 priority) is the only completely unaddressed item. The authors prioritized P0/P1 over P2; this is the right prioritization.

— Reviewer 2 (Domain), 2026-05-02
