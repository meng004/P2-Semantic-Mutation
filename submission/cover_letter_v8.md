# Cover Letter — IST Submission (v6, retitled to lead with the framework contribution)

**Date:** 2026-05-02

**To:** Editor-in-Chief, *Information and Software Technology* (Elsevier)

**From:**
Meng Li
School of Computing, University of South China
Postcode 421001, China
mlemon@usc.edu.cn

---

Dear Editor,

I am pleased to submit the manuscript

> **"A semantic mutation metric for metamorphic relation adequacy in scientific computing programs"**

for consideration as a regular research article in *Information and Software Technology*. The paper is accompanied by an Appendix (single supplementary file) and the per-IST-guideline **Highlights** (5 bullets, ≤ 85 characters each) and **structured Abstract** (≤ 250 words; Context / Objective / Method / Results / Conclusion).

## Why this submission fits IST's scope

The paper sits squarely in IST's empirical-software-engineering tradition and engages four of IST's recurring themes:

1. **Mutation-testing methodology.** IST has a long publication record in mutation-testing methodology — most directly **Jia & Harman (IST 2009) "Higher Order Mutation Testing"** (which we cite as the substrate against which our preventive-defence argument and our HOM-residual-threat declaration R12 are framed) and the broader Jia & Harman (TSE 2011) / Papadakis et al. (Adv. Computers 2019) survey lineage. Our SMS metric is a **strict generalisation** of Jia & Harman's classical Mutation Score (formal proof in Section 8: SMS degenerates almost-everywhere to classical MS in a precisely-defined limit `L = L_equiv ∧ L_killed ∧ L_mut`), and the §3.5 12-PUT empirical (5.14% AST overlap with cosmic-ray defaults; HP/SI/TF categorically unreachable at 0/0/0) is a direct empirical-software-engineering audit of the boundary between syntactic and domain-semantic mutation operators.

2. **LLM-augmented testing.** IST has been actively publishing on LLM-augmented testing methodology. Recent precedents include Tip, Bell & Schäfer (2024) on LLMorpheus, and the Kintis-style ESE-2018 mutation-tool empirical tradition. Our paper extends this line by being, to our knowledge, **the first work to factor-decompose "LLM source diversity vs MR design"** in scientific-computing software, via a three-stage ablation (v3 same-source / v3b same-source with data-driven primary MP / v4 cross-source over Claude Opus 4.6 + GPT-5.4 + DeepSeek chat). The headline empirical finding — under identical prompt template, three-LLM cross-source moves Cliff's delta by only -0.007 — is the kind of negative empirical result that we believe IST's audience values.

3. **Mutation-testing adequacy.** The paper proposes Semantic Mutation Score (SMS) as a domain-aware adequacy metric for metamorphic-relation sets, with an explicit three-layer methodology: (Layer 1) formal necessary conditions for "semantic mutation" (cross-function-boundary substitution / domain knowledge / algorithmic-class change); (Layer 2) E1 ∧ E2 equivalence judgement as the conservative complete instantiation; (Layer 3) AST-normalised empirical traceability over 12 PUTs (292 P2 mutants vs 1,250 cosmic-ray mutants). This is a methodological contribution at the metric level — exactly what IST's adequacy-metric thread (Andrews-Briand-Labiche ICSE 2005, Just et al. FSE 2014, Petrović & Ivanković ICSE-SEIP 2018 / TSE 2021) has been refining.

4. **Scientific-software validation.** IST has consistently published empirical work on scientific-software testing. Our 12 PUTs span four representative classes (numeric / probabilistic / surrogate / ML) using Python's de facto foundation stack (numpy 2.4.4, scipy 1.17.1, scikit-learn 1.8.0). The methodological honesty commitments — air-gap incompatibility declaration for IEC 60880 / DO-178C / IEC 62304 / ISO 26262 environments, conceptual complementarity (not normative compliance) with ASME V&V 20-2009 §3 — are made explicit in the main body and in Appendix E.

## Headline contributions

- **Three-layer methodological framework** for domain-semantic mutation operators (Layer 1 definitional, Layer 2 operational, Layer 3 applied), with SMS strictly generalising Jia & Harman's classical MS (Theorem 9.1, almost-everywhere degeneration).
- **AST-normalised traceability across 12 PUTs**: 5.14% overall overlap with cosmic-ray default operators; HP / SI / TF (54.5% of P2 pool) categorically unreachable at 0/0/0 by **first-order** syntactic tools; positive empirical evidence that P2 is **not a "post-classification copy"** of syntactic mutants.
- **Three-stage ablation plus a v4 × MP5 robustness contrast** isolating the contributions of MR-design alignment and same-prompt LLM source diversity to Cliff's delta. The pre-registered H2 large-effect threshold (delta ≥ 0.474, Romano 2006) is **not met under the pre-registered point-estimate criterion** (v3 delta = 0.323; v3b 0.446†; v4 0.439†; v4 × MP5 robustness contrast = 0.314, CI [0.014, 0.622]). Stipulated-alternative power simulation gives only **49.1%** power at the H2 boundary, clarifying that "not met" is a point-estimate fact, not an effect-size claim.
- **Engineering attribution layer** (LRCA): cross-source pooling raises mean C1_share from 0.164 to 0.209 (+27%†) and class-c mean SMS by **+91.4%†**, but does not move delta, separating "mutant quality" from "effect-size ceiling" cleanly.
- **Axis decomposition** (replacing the earlier "dominant lever" framing): across two c-class primary-MP conditions (MP5 and MP1), the LLM-identity axis under an identical prompt shifts Cliff's delta by ≤ 0.01 in magnitude (v3 → v4 × MP5 = -0.009; v3b → v4 = -0.007), whereas the MR-design axis (MP5 ↔ MP1) shifts delta by approximately +0.12. Within this design, the c-class primary-MP choice is the lever; the strong-sense LLM source-diversity test with per-LLM differential prompts is deferred to P4.

## Methodological honesty commitments

The paper explicitly disclosures items that submissions in this area sometimes paper over:

- The §3.4 c-class primary MP shift (v3b) is honestly framed as **selection-on-the-response**, with cross-cell exchangeability permutation null (one-sided p = 0.9885) and Bonferroni × 5 quantification; v3b and v4 are reported as exploratory only.
- The §3.5 12-PUT empirical refines the original "OS row tool-inexpressible ✗" categorical claim to **"△ 88.33% disjoint + 11.67% incidental hits"** based on actual cross-table data — the manuscript does not retroactively rescue the original strong claim.
- §6.4 deployability discussion is **explicitly cabined to single-output kernels**; we make no normative claim toward IEC 60880 / DO-178C / IEC 62304 / ISO 26262 / ASME V&V 20 certification bodies; we only argue conceptual complementarity (Appendix E.3 long-term aspiration).
- Mixed-effects modelling failed (Singular matrix at N = 60 / 12 PUTs) and is honestly reported — H4 verdict shifts to direct presentation of class means + sign test + Friedman + forest plot.
- v3 / v3b vs v4 protocol asymmetry (R13) is explicitly disclosed: v4 lacks the dual-blind reviewer LLM stage.

## Why IST rather than another venue

- **JSS** (*Journal of Systems and Software*) targets systems-level papers and tool reports; this submission is methodology-and-metric centred (SMS as a metric class, with a degeneration theorem) rather than a systems contribution.
- **STVR** (*Software Testing, Verification and Reliability*) tilts toward verification methodology; our contribution is a **mutation-testing adequacy metric** with empirical ablation, sitting more naturally in IST's mutation-testing thread.
- **ICSE / FSE** are conference venues for proceedings papers; the journal-length deep-method submission with 12-PUT empirical, 60-cell ablation, formal degeneration theorem, and full appendix exceeds proceedings page budgets.
- **TOSEM** is reserved for the planned theoretical companion P4 (minimal MR-subset existence, three-pillar coupling theorems); the present P2 submission is the empirical-methodology piece IST would receive.

## Originality, ethics, and publication declarations

- **Originality.** This work has not been published or submitted elsewhere. The companion paper [Meng Li et al., *Progress in Nuclear Energy*, under review] (cited as P1 throughout) is a complementary empirical audit of metamorphic-relation meta-patterns; the present submission focuses on adequacy-metric methodology and shares the 12-PUT infrastructure but reports independent contributions.
- **Conflicts of interest.** None.
- **Funding.** To be declared per the journal's checklist at acceptance.
- **Author contributions.** Meng Li (sole author) conceived the study, designed the experimental protocol, implemented the SMS / LRCA / cross-source mutant pipeline, performed the empirical analyses, and wrote the manuscript and appendix.
- **Reproducibility.** All scripts (`scripts/`), per-cell results (`data/results/*.json`), and version-pinned mutant pools (`data/mutants/*_pool_v4/`) will be deposited in a public Zenodo archive at acceptance (DOI to be assigned). Replication entry point: `REPRODUCIBILITY.md`. Headline empirical numbers in the abstract / main body are traceable to `paper_numbers_v4.json` and `cosmic_ray_12put_ast_diff.json`.
- **Highlights and structured Abstract.** Per IST guidelines, the submission includes 5 Highlights (each ≤ 85 characters) and a structured Abstract (≤ 250 words; Context / Objective / Method / Results / Conclusion).

## Submission-system metadata

Reviewer suggestions and conflict declarations will be provided through the journal's submission system per IST policy.

Thank you for considering this submission. I look forward to the editorial decision.

Sincerely,

**Meng Li**
School of Computing, University of South China
mlemon@usc.edu.cn
