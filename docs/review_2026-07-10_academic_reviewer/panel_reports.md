# Academic Paper Reviewer — Full Panel Reports

**Review date:** 2026-07-10
**Target venue:** ACM Transactions on Software Engineering and Methodology (TOSEM), Regular Research Paper
**Manuscript:** *A Semantic Mutation Metric for Metamorphic-Relation Adequacy for Scientific-Computing Kernels*
**Reviewed package:** `submission/TOSEM_regular_20260710/`
**Mode:** `academic-paper-reviewer/full`
**Review constraint:** The manuscript and submission package were read only. This report is a separate artifact.

## 1. Field Analysis and Panel Configuration

The manuscript is a hybrid formal-conceptual and quantitative empirical software-engineering paper. Its primary field is software testing, verification, and validation; secondary fields are mutation testing, metamorphic testing, scientific-computing software, and AI-assisted empirical software engineering. The main PDF has 50 pages and approximately 30,000 extracted words including statements and references; the 37-page supplement has approximately 15,200 words. The paper cites 53 references.

The target is a field-leading specialist journal. Topical fit is strong, but editorial risk is moderate to high because the manuscript combines several paper identities: metric construction, semantic-mutation theory, four empirical studies, LLM-source analysis, attribution theory, cross-language validation, and industrial real-defect evidence.

The five independent reviewer roles were:

1. **EIC:** TOSEM fit, archival contribution, companion-paper boundary, proportionality, and artifact readiness.
2. **Methodology Reviewer:** sampling units, cluster inference, preregistration, incidents, AI-label reliability, admission regimes, and reproducibility.
3. **Domain Reviewer:** mutation/MT novelty, semantic-mutant admission, fibers, duality, degeneration, AST/HOM claims, and self-containment.
4. **Perspective Reviewer:** numerical invariants, tolerance governance, compact-kernel transfer, industrial and cross-language evidence, and practical V&V value.
5. **Devil's Advocate:** circularity, alignment by construction, strongest counter-narrative, sequential redesign, and the “so what?” test.

## 2. Frozen Sprint-Contract Score Matrix

Scores use `block | warn | pass` under `reviewer/reviewer_full/v1`.

| Dimension | EIC | Methodology | Domain | Perspective | Devil's Advocate |
|---|---:|---:|---:|---:|---:|
| D1 methodology_rigor (mandatory) | block | block | block | warn | block |
| D2 domain_accuracy (mandatory) | warn | warn | block | block | block |
| D3 argumentative_coherence (mandatory) | warn | block | block | warn | block |
| D4 cross_disciplinary_relevance (high) | warn | pass | warn | warn | warn |
| D5 writing_and_structure (normal) | warn | warn | warn | warn | warn |

Mechanical failure-condition evaluation:

- **F1 — any mandatory dimension scores block:** fired. Every reviewer supplied at least one mandatory block.
- **F2 — majority find two or more mandatory dimensions warn or worse:** fired. All five reviewers met the reviewer-local predicate.
- **F3 — any high-priority D4 block:** not fired.
- **F0 — all reviewers pass every mandatory dimension:** not fired.

The highest-severity fired condition is F1, so the contract action is `reject_or_major_revision`. Panel arbitration favors **Major Revision**, but only if the construct and realized designs are changed rather than merely caveated.

## 3. EIC Review

**Recommendation:** Reject or Major Revision
**Confidence:** 4/5

The manuscript is an excellent topical fit and displays unusually strong transparency. Tables 1 and 10, the explicit non-claims, failed hypotheses, singular-model disclosure, cluster corrections, incident log, bounded-null language, and selection-conditioned interpretation are genuine strengths.

The blocking issue is the primary denominator. Section 3.3.8 (p. 13) requires a semantic mutant at stratum \(\psi\) to have a witnessed violation of \(\psi\) (S3). Section 5.9 (pp. 29–30) reports that the registered Study-1 pool has 170/292 mutants with zero invariant flips, 93 with one flip, and 29 with multiple flips. Section 9 (p. 43) then shows materially different aligned/cross estimates for all admitted mutants (292; \(\delta=0.3142\)), active-any-flip mutants (122; \(\delta=0.4043\)), and certified declared-stratum mutants (65; \(\delta=0.7917\)); six of twelve PUTs disappear in the certified view. The paper therefore has not fixed what SMS measures.

Additional EIC concerns are the unstable AI validation layer, the contribution boundary with NOETHER, Min-MR-Complete, defect4MR, and the arXiv version, and the 50+37-page presentation. The revision should rebuild the paper around one archival answer: the precise denominator and the evidence that validates it.

Administrative blockers include `<VERSION-DOI-PENDING>` in the manuscript (p. 47), cover letter, and declarations; the unpublished Studies 2–4 deposit; inconsistent defect4MR citation/provenance; and the need for confidential overlap disclosure for the anonymous NOETHER companion.

## 4. Methodology Review

**Recommendation:** Major Revision
**Confidence:** 4/5

The corrected PUT-cluster analyses are a strength: Study 2 H2-1′ remains positive, Study 4 H4‴ remains above the registered bar under a post-hoc 15-PUT cluster bootstrap, and H-LANG remains not confirmed. Zero inflation and effective information content are also reported unusually honestly.

Two Study-4 claims remain blocked by realized-design problems:

1. **H4‴ admission universe:** the registration did not specify the screened/unscreened regime. Study 3 v6 was screened, while Study 4 v7 pools were unscreened and this difference was found only at final review (p. 41). The matched screened-subset sensitivity leaves 13 units, fails the recruitment gate, and gives share 0.0; the positive signal is entirely carried by multi-stratum mutants excluded under the earlier regime (p. 42). The current result should be exploratory or replicated under a newly frozen unscreened universe.
2. **H2-2 serving-stack confounding:** after Amendment v1.2, the same-source arm mixes gateway- and harness-served Claude generation, whereas the cross-source arm remains gateway-served. Serving stack is nested within source arm. The narrow interval therefore identifies a composite protocol contrast, not clean vendor diversity.

AI review labels are diagnostic rather than gating, yet shadow agreement is only \(\kappa=0.44/0.36\) overall and near zero on the contested `bounds="fixed"` family (p. 41). A pre-specified human or independent cross-vendor audit, plus label-conditioned headline estimates, is required. The deferred \(K_{eq}\in\{500,1000,2000\}\) sensitivity and a stratified equivalence audit are also needed.

## 5. Domain Review

**Recommendation:** Reject or Major Revision
**Confidence:** 5/5

The paper's strongest defensible novelty is not the unchanged scalar ratio; it is an audited domain-specific semantic fault model, admission protocol, and MR-relative empirical instantiation. Classical mutation analysis already supports domain-specific operators and arbitrary test/property sets. The manuscript should not claim that the ratio alone is a new strict mathematical generalization without a sharper comparison to property-relative/specification mutation.

The formal layer has three acceptance-driving problems:

1. **Two incompatible semantic-mutant definitions:** Section 3.3.8 requires witnessed invariant violation, while Section 4.2 defines semantic mutation through structural/domain-knowledge/algorithm-class conditions. The empirical denominator follows the latter and E1∧E2 bounded non-equivalence, not the former.
2. **Fiber ambiguity and one-way “duality”:** Section 3.3.1 defines \(\mathcal F(MR)\) as a killed subset; Section 3.3.9 defines fibers as effect-map preimages. Theorem 3.4 establishes only \(killed_r\subseteq active_\alpha\), yet the text says the kill matrix is supported “exactly” on active fibers despite demonstrated active survivors.
3. **Incomplete degeneration theorem:** Supplement Lemma G.2 permits \(r\ne id\), yielding \(S_i(x)\ne s'(r(x))\), not classical same-input difference detection. The classical limit requires \(r=id\). Once the mutant and oracle universes are explicitly replaced, the ratio equality is largely definitional.

The AST audit establishes non-observation in one default first-order Cosmic Ray pool, not general operator reachability. The HOM discussion should be rewritten, and a direct operator-level/exhaustive or multi-location experiment is needed for stronger reachability claims.

## 6. Cross-disciplinary / Perspective Review

**Recommendation:** Reject or Major Revision; Major Revision is viable if the denominator is repaired
**Confidence:** 4/5

The strong-boundary arm is valuable because it treats \(\varepsilon_{tol}\) as an operating point and shows both a PINN false positive and an RNG false negative. The industrial arm also makes a useful distinction among aggregate kill rate, alignment, and real-defect detection, and the paper correctly treats the 34/34 face as selection-conditioned.

The metric is not yet transferable beyond the controlled setting. The subjects are single-output `float -> float` kernels under 2 KB; tolerance checkers combine absolute residuals, Wilcoxon tests, residual ratios, and DTW without a common units/scale/precision/discretization contract. The industrial arm is result-level rather than an industrial SMS deployment, while the seven-PUT C99 arm does not confirm language replication.

For practical V&V use, each audit record should bind the kill to units, normalization, precision, discretization/resolution, baseline residual distribution, repeat policy, and the provenance of \(\varepsilon_{tol}\) and \(\varepsilon_{eq}\). Claims about IEC 60880, DO-178C, IEC 62304, and ISO 26262 should not imply blanket air-gap requirements without qualified standards review.

The present evidence supports an offline research diagnostic, not a release gate, certification metric, industrial acceptance threshold, or general portability claim.

## 7. Devil's Advocate Review

### Strongest Counter-Argument

The manuscript does not yet validate a semantic adequacy metric. It validates the behavior of an author-constructed mutant/MR system whose semantic categories and alignments are partly defined using the same invariants later used to score it. S3 requires a witnessed declared-invariant violation, but 170/292 primary mutants flip none of the invariants. The positive aligned-versus-cross direction is also expected because `align(j)=j` is an explicit design choice (p. 10). The real-defect arm admits cases only after the pattern-derived MR detects them (p. 31), so 34/34 cannot establish prospective defect-detection value. Vendor matching removes one source confound but does not break operator–MR co-construction. The work demonstrates an unusually transparent audit framework, but its central adequacy interpretation requires an independently defined denominator and held-out predictive validation.

### Critical Finding

**Formal–empirical denominator contradiction:** the empirical object does not instantiate the formal semantic-mutant universe. Repair requires either renaming SMS as an intent-labelled admitted-mutation score, or prospectively defining an independently certified declared-stratum denominator and rerunning primary analyses. Certification cannot use the same MR battery being evaluated.

### Major Findings

- Alignment is partly true by construction and presently demonstrates internal consistency, not independent adequacy.
- Theorem 3.4 is a one-way soundness/closure lemma, not completeness or practical adequacy.
- Studies 2–4 are legitimate fresh registered follow-ups, but they redesign hypotheses, admission, recruitment, and attribution after earlier failures; the sequence is metric development, not replication of one unchanged construct.
- The 34-case industrial evidence is selection-conditioned and cannot support prospective coverage.
- SMS has not yet been shown to improve MR selection, held-out defect detection, cost, or decision utility relative to established criteria.

### Unexamined Premise

The paper assumes that adequacy for a declared semantic risk can be measured using a mutant universe designed and labelled through the same semantic framework being evaluated. Without an independent fault ontology or certificate, SMS may measure framework self-consistency rather than external adequacy.

## 8. Shared Strengths Across the Panel

- Strong TOSEM topical fit.
- Transparent reporting of failed and non-confirmed hypotheses.
- Claim-evidence ledgers with explicit inference permissions.
- Correct movement toward PUT-clustered inference.
- Extensive SSOT, preregistration, freeze-then-score, and incident-trace intent.
- Useful distinction among mutant kill rate, semantic alignment, and real-defect detection.
- Clean PDF rendering, embedded fonts, no observed overfull boxes, and no undefined references in the inspected build logs.
