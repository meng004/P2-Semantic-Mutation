# Cover Letter — IST Submission

**Date**: 2026-05-02

**To**: Editor-in-Chief, *Information and Software Technology* (Elsevier)

**From**:
Meng Li
School of Computing, University of South China
Postcode 421001, China
mlemon@usc.edu.cn

---

Dear Editor,

I am pleased to submit the manuscript titled

> **"When Same-Prompt LLM Source Diversity Doesn't Help: An Ablation of Semantic Mutation Operators in Metamorphic Testing for Single-Output Scientific Computing Kernels"**

for consideration as a regular research article in *Information and Software Technology* (IST).

## Why this work fits IST

The manuscript addresses two intertwined open questions in software-engineering empirical research that are squarely within IST's scope:

1. **Adequacy of metamorphic relations.** Metamorphic Testing (MT) addresses the test-oracle problem in scientific computing software, but the field has lacked a domain-aware adequacy metric: classical Mutation Score (MS) operates on syntactic AST mutations and does not capture domain semantics such as conservation laws, monotonicity, or convergence order. We propose **Semantic Mutation Score (SMS)** — a strict generalization of Jia & Harman's classical MS that degenerates to MS in a precisely-defined limit (formal proof in Section 9, with measure-zero qualification on the boundary lemma).

2. **The role of LLM-source diversity in mutant generation.** Recent work (Tip, Bell, & Schäfer, 2024; Humbatova, Jahangirova, & Tonella, 2021) has begun using large language models to generate mutants. Whether *cross-source pooling* (mixing outputs from multiple LLMs under a fixed prompt template) contributes to mutant-set effectiveness, beyond the contribution of metamorphic-relation alignment design, has been an open empirical question. The manuscript reports a **three-stage ablation** (v3 same-source / v3b data-driven primary MP shift / v4 cross-source 3-LLM pool) that decomposes these factors honestly.

## Headline contributions

The manuscript's contribution is a **three-layer methodological framework** for domain-semantic mutation:

- **Layer 1 (Definitional, §3.2.0)**: necessary conditions (cross-function-boundary substitution / domain knowledge / algorithmic-class change) for "semantic mutation", with five meta-mutation operator classes (CE / OS / HP / TF / SI) as specializations across four representative kernel classes.
- **Layer 2 (Operational, §2.3 / §4.4)**: equivalence judgment $E_1 \wedge E_2$ as the conservative complete instantiation of the necessary conditions; three-candidate trade-off analysis is provided.
- **Layer 3 (Applied, §3.2.6.3)**: **AST-normalized empirical traceability** — across all 12 PUTs, 292 P2 mutants and 1,250 cosmic-ray syntactic mutants are compared at the AST-normalized level. Overall AST overlap rate is **5.14%**; three of the five operator classes (HP / SI / TF; 159/292 = 54.5% of the P2 pool) are **categorically unreachable** (0/72, 0/33, 0/54). This is positive empirical evidence that P2 is not a "post-classification copy" of syntactic mutants.

## Headline empirical findings (in scope of single-output kernels)

- The pre-registered H2 large-effect threshold (Cliff's $\delta \geq 0.474$, Romano 2006) is **not met under the pre-registered point-estimate criterion** in the primary v3 analysis ($\delta = 0.323$). Two exploratory follow-ups (v3b / v4) raise the point estimate to 0.446 / 0.439 but neither crosses the threshold. We report the v3 → v3b and v3b → v4 contrasts **separately** rather than as a single ratio, and we explicitly disclose the v3b post-hoc selection confound.
- Stipulated-alternative power simulation against $\delta_{\text{truth}} = 0.474$ shows that even at the H2 boundary, our $(n_a, n_c) = (12, 48)$ design produces $\hat\delta \geq 0.474$ in only ~49% of replications, so the H2 verdict is correctly framed as a point-estimate fact rather than an effect-size claim.
- Cross-source pooling improves mutant quality (mean C1\_share $0.164 \to 0.209$) and class-c mean SMS by **+91.4%**, but the v3b → v4 $\delta$ shift is only $-0.007$, so cross-source diversity is **not** the dominant driver of MR-aligned-vs-cross effect size — MR design itself is.

## Methodological honesty commitments

The manuscript explicitly disclosures items that submissions in this area sometimes paper over:

- The §3.5.1 c-class primary MP shift (v3b) is honestly framed as **selection-on-the-response**, with cross-cell exchangeability permutation null and Bonferroni × 5 quantification; v3b is reported as exploratory, not primary.
- The §3.2.6.3 OS row's "✗ tool-inexpressible" claim from the syntactic-vs-semantic operator cross-table is **empirically refined** to "△ 88.33% disjoint + 11.67% incidental hits" once we observe the 12-PUT data — the manuscript does not retroactively rescue the original strong claim.
- §6.5 deployability discussion is **explicitly cabined to single-output kernels**; there is no normative claim toward IEC 60880 / ISO 26262 / DO-178C / ASME V&V 20-2009 certification bodies, only conceptual complementarity (§6.5.3 long-term aspiration).

## Originality, ethical, and publication declarations

- **Originality**: This work has not been published or submitted elsewhere. The companion paper [Meng Li et al., *Progress in Nuclear Energy*, under review] (cited as P1 in the manuscript) is a complementary empirical audit of metamorphic-relation meta-patterns; the present submission focuses on adequacy-metric methodology and shares the 12-PUT infrastructure but reports independent contributions.
- **Conflicts of interest**: None.
- **Funding**: To be declared per the journal's checklist at acceptance.
- **Author contributions**: Meng Li (sole author) conceived the study, designed the experimental protocol, implemented the SMS / LRCA / cross-source mutant pipeline, performed the empirical analyses, and wrote the manuscript.
- **Reproducibility**: All scripts (`scripts/`), per-cell results (`data/results/*.json`), and version-pinned mutant pools (`data/mutants/*_pool_v4/`) are committed to a public Zenodo archive at acceptance (DOI to be assigned). The replication entry point is `REPRODUCIBILITY.md`.

## Suggested reviewers and exclusions

Reviewer suggestions and conflicts will be provided through the journal's submission system per IST policy.

Thank you for considering this submission. I look forward to the editorial decision.

Sincerely,

**Meng Li**
School of Computing, University of South China
mlemon@usc.edu.cn
