# TOSEM Acceptance-Issue Repair Matrix

Date: 2026-07-08

Scope: TOSEM regular submission package and canonical source for the Semantic Mutation manuscript.

Principle: the manuscript reports final research results and necessary limitations, not a chronological log of exploratory process. However, every positive claim that remains in the manuscript must be traceable to a run artifact, result file, audited dataset, or documented re-analysis.

## Repair Matrix

| ID | Acceptance issue | Current evidence | Repair type | Publishable if | Manuscript action | Status |
|---|---|---|---|---|---|---|
| P0-H2-SSOT | H2 mixes the frozen MP5 primary contrast with MP1 sensitivity values. | `data/results/rq2_cliffs_delta_v4_mp5.json` reports mean aligned/cross SMS `0.213325/0.0766729`, Cliff's delta `0.314236`; `data/results/paper_numbers_v4.json` reports MP1 sensitivity mean aligned/cross `0.275/0.0612`, delta `0.4392`. | Re-analysis and synchronization first; no new experiment required to close the inconsistency. | One primary estimand is declared everywhere; MP1 is explicitly labeled sensitivity. | Report MP5 frozen-primary as H2 main result; report MP1 only as sensitivity. | Closed |
| P0-RQ3-DRIFT | RQ3 values differ across main text, supplementary material, and reproduction guide. | `data/results/rq3_friedman_v4.json` reports chi-square `16.7586`, p `0.002153`. | Reconciliation. | Main, supplement, and reproduction guide all use the same final RQ3 values. | Synchronize all RQ3 prose and tables to `rq3_friedman_v4.json`. | Closed |
| P0-BUILD-SSOT | Submission files were manually repaired but canonical `source/` and `venues/tosem/build.py` still contain old claims. | Current source, submission, root reproducibility, replication docs, and clean zip have been synchronized and scanned. | Source/submission synchronization. | Rebuilding/packaging does not reintroduce old values or overclaims. | Make `source/` the canonical manuscript and rebuild the submission package from it. | Closed |
| P1-INDUSTRIAL | Industrial real-defect arm is not auditable enough to support validation-strength wording. | The package lacks a complete case-level industrial ledger with frozen case IDs, admission rules, artifact hashes, and outcomes. | New evidence package or claim downgrade. | Case-level artifact ledger supports each retained industrial statement. | Downgrade to selection-conditioned external sanity check until ledger exists. | Downgraded; data gap remains |
| P1-S5-PURITY | S5 is used as if it verifies semantic alignment, but current evidence only supports an intended-stratum label. | Existing results support labels and outcome patterns, not independent purity verification. | New validation experiment or claim downgrade. | Independent audit or deterministic checks estimate S5 purity with uncertainty. | Describe S5 as an audited labelling assumption, not proof of pure semantic effects. | Downgraded; data gap remains |
| P1-LOW-POWER | The frozen-primary H2 effect is directionally positive but weaker and less decisive than the MP1 sensitivity. | `rq2_cliffs_delta_v4_mp5.json` gives delta `0.314236`; power files correspond to MP1 sensitivity rather than frozen MP5. | New experiment or stronger zero-aware analysis. | Additional data or a predeclared model narrows uncertainty without outcome-dependent stopping. | Keep only qualified H2 wording unless precision improves under the frozen-primary design. | Qualified; data gap remains |
| P1-ZERO-MASS | The SMS distribution is sparse: 45 of 60 cells have zero SMS. | `data/results/paper_numbers_v4.json` reports `n_zero_sms=45` of `n_cells=60`. | Reframing plus optional stratified analysis. | Zero-mass is treated as a substantive boundary condition, not an incidental nuisance. | Foreground sparsity as a final-study result and interpret SMS as boundary-sensitive. | Closed |
| P1-SOURCE-DIVERSITY | The source-diversity mechanism claim is stronger than the asymmetric protocol supports. | Current cross-source design is not a matched symmetric protocol for isolating source diversity. | New symmetric experiment or claim removal. | Symmetric source-diversity protocol supports the mechanism claim. | Remove mechanism-strength wording unless the new experiment supports it. | Downgraded; data gap remains |
| P1-ARTIFACT-ACCESS | Artifact availability language is too weak for TOSEM-style reproducibility expectations. | Clean zip has been rebuilt from the current directory; root and replication reproducibility docs list the final result-file contract. | Documentation and packaging. | All final result files and new experiment ledgers are listed with paths and expected hashes or sizes. | Update data availability, reproducibility guide, and supplementary appendix. | Closed for current claims |
| P2-NEGATIVE-FRAMING | Some final-study negative results are present late in the paper but not prominent enough for editorial confidence. | H1/H4 failure, zero-mass, and H2 below-threshold primary contrast are now in the abstract/front matter. | Manuscript reframing. | Abstract/introduction summarize final-study limits without turning the paper into a process diary. | Foreground H1/H4 failure, zero-mass, and estimator sensitivity as boundary findings. | Closed |

## Remedy Classes

- New experiment: evidence is missing and the corresponding claim is important enough to keep.
- Re-analysis: raw evidence exists but the current estimate, contrast, or wording is inconsistent.
- Claim downgrade/removal: the claim is not central enough to justify new evidence before submission.

## Reviewer Checkpoint 1

- Coverage: all P0/P1 issues raised by the reviewer panel are mapped to a remedy.
- Evidence discipline: every retained positive claim must pass through a result file, new experiment ledger, or documented re-analysis.
- Topic drift check: the repair keeps the paper centered on semantic mutation testing and SMS validity boundaries; it does not convert the manuscript into a generic negative-results paper or a process narrative.
- Current decision: proceed to disclosure policy before editing prose, because prose changes depend on which claims are publishable rather than merely internally observed.

## New Experiment And Analysis Protocols

### E1: Industrial Case-Level Audit

Decision: essential only if the manuscript keeps industrial-validation-strength wording. Otherwise the industrial arm must be downgraded to a selection-conditioned external sanity check.

Protocol:

| Field | Specification |
|---|---|
| Research question | Do admitted real-defect cases provide auditable external support for SMS behavior? |
| Unit | One frozen real-defect case. |
| Inputs | Frozen case list, source project and commit, defect reference, mutant ID, MR/test oracle, admission/exclusion rule. |
| Output files | `data/results/industrial_case_ledger.json`, `data/results/industrial_summary.json`. |
| Minimum case fields | `case_id`, `source_project`, `source_commit`, `defect_reference`, `mutant_id`, `operator`, `intended_stratum`, `test_result`, `real_defect_face_result`, `admitted`, `exclusion_reason`, `artifact_hash`. |
| Stopping rule | Audit all cases in the frozen case list exactly once; excluded cases remain in the ledger but cannot support positive claims. |
| Publishable claim if completed | "The industrial arm provides audited, selection-conditioned external evidence that kill-rate, semantic-stratum alignment, and real-defect detection are separable." |
| Publishable claim if not completed | "The industrial arm is an external sanity check and does not establish industrial validity." |

### E2: S5 Purity Validation

Decision: essential if the manuscript claims S5 alignment as verified construct separation; optional if S5 is described only as an intended-stratum label.

Protocol:

| Field | Specification |
|---|---|
| Research question | Are S5-labeled mutants actually confined to the intended semantic stratum? |
| Unit | One S5-labeled mutant. |
| Sampling | Stratified random sample across PUT classes and MP/operator families; oversample nonzero SMS cells so the audit covers cells that affect conclusions. |
| Assessment | Two independent annotators, or deterministic invariant checks where available. Disagreements are adjudicated and kept in the ledger. |
| Output files | `data/results/s5_purity_audit.json`, `data/results/s5_purity_summary.json`. |
| Primary metric | Verified pure rate with interval estimate and disagreement rate. |
| Stopping rule | Complete the predeclared sample before inspecting summary pass/fail. |
| Publishable claim if completed | "S5 labels have audited purity rate X within this sample." |
| Publishable claim if not completed | "S5 denotes intended-stratum labeling; aligned-vs-cross results are diagnostics under that labeling assumption." |

### E3: H2 Frozen-Primary Precision Extension

Decision: essential only if the paper wants to claim a robust aligned-vs-cross advantage under the frozen MP5 primary estimand. If not run, H2 must remain qualified.

Protocol:

| Field | Specification |
|---|---|
| Research question | Is the aligned-vs-cross advantage robust under the frozen MP5 primary estimand? |
| Unit | One PUT--MP cell, preserving the frozen primary-MP convention. |
| Candidate expansion | Add independent PUTs within the same scientific-computing scope, or add a predeclared number of independent mutants per existing PUT--MP cell. |
| Primary output | Updated aligned/cross means, medians, Cliff's delta, and bootstrap CI under MP5. |
| Secondary analysis | Zero-aware paired or hierarchical model that treats PUT as a block and reports sparse-cell sensitivity. |
| Output files | `data/results/rq2_cliffs_delta_v4_mp5_extended.json`, `data/results/rq2_zero_aware_model_v4_mp5.json`. |
| Stopping rule | Stop only after the predeclared expansion is complete; do not stop when a threshold is crossed. |
| Publishable claim if completed | "The frozen-primary effect is robust/qualified according to the final interval." |
| Publishable claim if not completed | "The frozen-primary effect is directionally positive but below the pre-registered large-effect threshold." |

### E4: Source-Diversity Symmetric Protocol

Decision: optional for the current submission if the mechanism claim is removed; essential if the paper keeps a source-diversity mechanism claim.

Protocol:

| Field | Specification |
|---|---|
| Research question | Does LLM source diversity improve mutant quality beyond condition separation? |
| Unit | One generated mutant set under a matched prompt, budget, and admission filter. |
| Conditions | Symmetric same-source and cross-source configurations with identical prompt constraints, sampling budgets, and filters. |
| Output file | `data/results/source_diversity_symmetric.json`. |
| Primary contrast | Change in SMS or valid semantic-mutant yield attributable to source diversity after matched filtering. |
| Stopping rule | Complete the matched generation budget before examining the contrast. |
| Publishable claim if completed | Keep source-diversity mechanism wording only if the symmetric contrast supports it. |
| Publishable claim if not completed | Treat source diversity as exploratory future work or a non-supporting observation under the current asymmetric design. |

## Reviewer Checkpoint 3

- Essential-now: P0-H2-SSOT, P0-RQ3-DRIFT, P0-BUILD-SSOT, P1-ZERO-MASS, and P2-NEGATIVE-FRAMING can and must be closed in this repair loop without new expensive data collection.
- Essential-if-claim-kept: P1-INDUSTRIAL, P1-S5-PURITY, P1-LOW-POWER, and P1-SOURCE-DIVERSITY require new evidence only if the manuscript keeps the corresponding strong claim.
- Current manuscript policy: until E1--E4 are actually run and produce auditable outputs, the paper must use qualified wording for industrial evidence, S5 purity, H2 robustness, and source-diversity mechanisms.
- Topic drift check: E1--E4 remain within semantic mutation testing, SMS construct validity, and MR adequacy; no proposed experiment changes the paper into a new benchmark or broad industrial validation study.
