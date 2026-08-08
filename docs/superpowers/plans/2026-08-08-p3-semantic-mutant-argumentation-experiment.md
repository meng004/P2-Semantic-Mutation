# P3 Semantic-Mutant Argumentation Experiment Plan

> **For agentic workers:** REQUIRED SUB-SKILL: use
> `superpowers:writing-plans` to produce the implementation plan, then use
> `superpowers:executing-plans` to execute the frozen study phase by phase.
> This document fixes the scientific argument and execution order; it is not a
> Cursor launch packet.

## Material Passport

- Origin: P3 semantic-mutant construction principles
- Origin date: 2026-08-08
- Study type: empirical software engineering / mutation testing / metamorphic testing
- Verification status: methodology self-review passed; implementation and
  independent evidence audits pending
- Execution environment: fresh Cursor VM, Grok 4.5 High
- Scientific authority: frozen artifacts and executable checks, never model judgment
- Governing design:
  `docs/superpowers/specs/2026-08-08-p3-semantic-mutant-construction-principles-design.md`

## Review-remediation matrix

| Review finding | Binding repair in this revision |
|---|---|
| Patch mechanism was misused as semantic family | Separate `construction_mechanism` from `semantic_contract_family`; primary macro SMS uses only the latter |
| P12 admission/reference MR could leak into evaluated portfolios | Partition reference MRs as positive controls and mechanically exclude them and semantic duplicates from confirmatory portfolios |
| Contract, patch, and witness could be co-designed | Freeze contract/domain/oracle first, propose patch second, select the first canonical witness third |
| P12 population and paired cohort were ambiguous | Define `P12_FULL`, `P12_PAIRED`, and `P12_DIRECT`, plus separate diversity and criterion construction cohorts, with distinct estimands |
| Outcome blindness was logical rather than physical | Use three content-addressed packages with no `.git` history and mount them in chronological order |
| MR subset lattice created pseudo-replication and infeasible enumeration | Keep the lattice descriptive; use fixed-budget combinadic sampling and project-budget aggregates for inference |
| RQ4 model was too large for the proposed floor | Use a simulation-qualified project-level model and retain the existing 17-project/60-family confirmatory floor |
| `DIRECT`-only and unequal equivalence denominators favored the semantic model | Use all paired defects for primary criterion validity and common strict/conservative equivalence policies for both baselines |
| The new RQ4 estimand could override the frozen P12 v1.1.2 S1–S2 contract | Require an explicitly compatible successor P12 contract; otherwise retain v1.1.2 only under its own estimand and downgrade P3 RQ4 |

## 1. Goal and central argument

P3 introduces semantic mutants and uses them to compare, explain, and evaluate
the adequacy of MR sets. The paper does not evaluate a universal mutant
generator. It evaluates whether a frozen, independently certified semantic
fault domain provides information about MR-set adequacy that ordinary syntactic
mutation does not provide.

The central empirical chain is:

```text
P12 fixed program version
  -> independently constructed semantic mutants
  -> traditional syntactic mutants on the same version
  -> the same frozen non-reference MR inventory executed on both mutant populations
  -> semantic-contract-family-aware MR-set adequacy profiles
  -> comparison with the same MR sets on P12 buggy/fixed real-fault pairs
```

This paired substrate is the main protection against circular reasoning. P12
membership, semantic-mutant certification, syntactic-mutant generation, and MR
inventory freezing occur without using the confirmatory MR kill matrix. P12
real-fault outcomes are opened only after the controlled denominators, MR-set
portfolio lattice, and analysis code are frozen.

## 2. Why this design is selected

Three designs were considered:

1. **Controlled mutants only.** This is reproducible and supports construct
   coverage, but cannot establish real-defect relevance.
2. **P12 real faults only.** This supplies real faults but cannot isolate what
   semantic mutation adds beyond ordinary mutation or explain residual semantic
   risks.
3. **Paired three-layer evidence.** Semantic mutants, syntactic mutants, and
   P12 real faults share fixed program versions and MR inventories. This is the
   selected design because it supports construct validity, comparison, and
   criterion validity without using MR outcomes to admit experimental objects.

The intended successor P12 package is a benchmark of **MR-detectable real
semantic defects**. Results may be generalized to that declared benchmark
domain, not to all software defects. An MR used to establish that benchmark
property is a positive control, not an independent P3 evaluation MR. The frozen
P12 v1.1.2 package has a different admission rule and S1–S2/RFDS primary
estimand; P3 does not retroactively redefine either one.

## 3. Research questions

### RQ1 — Construction and certification

Can the artifact-first protocol produce executable, independently certified,
non-equivalent semantic-mutant versions across different program scales and
implementation techniques?

Evidence:

- the complete candidate-to-certified funnel;
- pass, fail, and inconclusive states for every certification gate;
- certification yield by semantic-contract family, program-scale stratum,
  implementation stratum, repository, and target program;
- stable original/mutant semantic witnesses.

RQ1 is descriptive. A failed construction remains evidence about the boundary
of the protocol and is never replaced after confirmatory outcomes are visible.

### RQ2 — Difference from traditional mutation

What semantic-contract, behavioral, patch-structure, and family-coverage
differences exist between certified semantic mutants and frozen first-order
syntactic mutants on the same program versions?

Evidence:

- exact normalized-patch overlap;
- exact mutant-tree overlap;
- independent semantic-contract categories;
- trigger and non-equivalence funnels;
- family and subject coverage.

Structural non-overlap alone does not establish greater testing value. It is a
construct-distinctness result only.

### RQ3 — MR-set adequacy and explanation

Which semantic mutants and semantic-contract families are detected or missed by
each MR set, and what do unique contribution, redundancy, residual risk, and
execution cost reveal beyond a single aggregate mutation score?

The primary controlled-mutant measure is family-balanced semantic mutation
score. Instance-weighted score, conservative equivalence bounds, unique kills,
redundancy, residual families, and cost-normalized coverage are required
secondary views.

### RQ4 — P12 criterion validity and incremental value

On frozen P12 MR-detectable real defects, do semantic-mutant adequacy profiles
explain or predict MR-set detection outcomes, and do they add information beyond
traditional syntactic mutation score?

Primary criterion-validity evidence uses every eligible defect in the paired
P12 cohort and family-agnostic semantic-adequacy features. Outcome-blind
`DIRECT` mappings support a secondary mechanism-concordance analysis.
`ADJACENT`, `OUT_OF_SCOPE`, and `UNCERTAIN` cases remain in the primary
family-agnostic denominator and are reported separately for mapping analyses.

## 4. Claims and initial status

| Claim | Initial status | Upgrade condition |
|---|---|---|
| P3 defines an artifact-first semantic-mutant protocol | `supported` | Governing design and frozen schemas remain consistent |
| The protocol constructs certified mutants across scales and techniques | `blocked` | RQ1 evidence meets the diversity and completeness gates |
| Semantic mutants are construct-distinct from the chosen syntactic baseline | `blocked` | RQ2 paired evidence and uncertainty accounting complete |
| Family-aware SMS compares and explains MR-set residuals | `blocked` | Frozen kill matrix and all required adequacy views complete |
| Semantic adequacy adds explanatory value on P12 | `blocked` | RQ4 project-clustered analysis supports the prespecified criterion |
| Semantic mutation is superior for all programs or defects | `blocked` permanently | Outside P3's sampling domain and design |
| P3 provides language-independent automatic mutant generation | `blocked` permanently | Reserved for a later paper |

Negative or null results do not invalidate the study. They determine which
claims stay blocked and may themselves support a boundary or limitation result.

## 5. Experimental objects

### 5.1 P12 populations and reference-MR isolation

The plan maintains three immutable P12 populations:

- `P12_FULL`: every accepted P12 real-fault item, used for benchmark-wide
  descriptive reporting;
- `P12_PAIRED`: every `P12_FULL` fault whose exact fixed version has a complete
  prespecified criterion-construction profile, used for primary
  criterion-validity analysis;
- `P12_DIRECT`: the outcome-blind `DIRECT` semantic-contract-family subset of
  `P12_PAIRED`, used only for secondary mechanism-concordance analysis.

No fault may move between these populations after MR outcomes are opened. The
`P12_FULL` frame contains every item satisfying the P12 package's frozen
requirements:

- immutable buggy and fixed program identities;
- a reproducible original/fixed execution path;
- when the P12 benchmark definition requires it, an executable reference MR
  demonstrating that the fault is MR-detectable;
- complete provenance and no unresolved licensing restriction.

For P12 D2 packages governed by the existing v1.1.2 consumer contract, admission
must remain independent of MR detectability. For a successor P12 benchmark that
requires a reference MR, that reference MR, its implementation variants, and
any MR with the same canonical semantic signature are tagged
`ADMISSION_POSITIVE_CONTROL` and excluded from all confirmatory P3 portfolios.
Uncertain signature equivalence is resolved conservatively by exclusion.

Primary P3 RQ4 requires a successor P12 contract that prospectively authorizes
the paired fixed-version/non-reference-MR estimand, exposes the required atomic
ledger, and preserves at least the v1.1.2 scale and concentration floors. If
only v1.1.2 is available, P3 consumes it solely under its frozen S1–S2/RFDS
contract as external descriptive or sensitivity evidence. It cannot relabel
that package as the new P3 primary criterion-validity experiment.

P3 applies no inclusion rule based on confirmatory MR-set outcomes. All eligible
items remain in `P12_FULL`. Membership in `P12_PAIRED` is determined only by the
pre-outcome criterion-construction frame and complete profile availability;
faults missed by every evaluated MR set remain included. Unpaired faults and the
mechanical reason for missing a profile remain in the coverage ledger.

### 5.2 Program-scale strata

Repository source size is computed mechanically at the frozen fixed commit,
excluding vendored, generated, test-fixture, and environment directories:

- `S`: fewer than 10,000 nonblank noncomment source lines;
- `M`: 10,000–99,999 nonblank noncomment source lines;
- `L`: at least 100,000 nonblank noncomment source lines.

The target executable unit's source lines and dependency cone are recorded
separately, so a small target inside a large repository is not misreported as a
large mutation site.

### 5.3 Implementation-technique strata

Each subject receives a multi-label technique vector and exactly one primary
technique label under the following precedence order:

1. `HYBRID_NATIVE`: the target execution crosses a project-owned
   language/process/native-kernel boundary;
2. `TENSOR_AUTODIFF`: tensor, accelerator, neural-network, or automatic-
   differentiation semantics dominate the target;
3. `PROBABILISTIC_SURROGATE`: probabilistic inference, surrogate modelling, or
   statistical estimation dominates the target;
4. `ITERATIVE_STOCHASTIC`: iterative solver, optimization, simulation, sampling,
   or state-trajectory semantics dominate the target;
5. `ARRAY_NUMERICAL`: dense/sparse array, vectorized, or linear-algebra semantics
   dominate the target;
6. `SCALAR_CONTROL`: scalar computation and ordinary control flow dominate.

The classifier is a frozen rule engine over dependency metadata, a predeclared
original-program smoke input, call traces, and declared target symbols. The
primary label supports deterministic stratified sampling; the multi-label vector
supports sensitivity analysis. Ambiguous subjects receive `TECH_UNCERTAIN` and
remain visible; they do not enter technique-stratified confirmatory claims.

### 5.4 Deterministic controlled cohorts

Two controlled cohorts are frozen before P3 sees MR outcomes:

1. `C_CONSTRUCT` supports RQ1–RQ3 diversity. Enumerate the complete eligible
   fixed-version frame, classify scale and technique mechanically, rank each
   scale × technique cell by
   `SHA256(fixed_commit || project_id || target_id || "P3-C1")`, select the first
   candidate per nonempty cell, then continue round-robin until 18 subjects are
   selected or the frame is exhausted. Retain `EMPTY_FRAME` for unfilled cells.
2. `C_CRITERION` supports RQ4 exact-version pairing. Enumerate, without sampling,
   every unique exact fixed commit referenced by the compatible successor
   `P12_FULL` frame and construct the same prespecified semantic and syntactic
   profiles. Multiple faults sharing an exact fixed commit reuse one immutable
   profile but remain distinct real-fault rows. A failed profile remains a
   failed pairing record and is never replaced by another version.

The `C_CONSTRUCT` target is representation of all three size strata, at least
four implementation techniques, at least eight repositories, and at least 15
subjects. The RQ4 target is at least 17 projects and 60 `P12_PAIRED` real-fault
families with complete exact-version profiles, subject to the concentration
rules in Section 11.4. Before proposal or outcome opening, preflight publishes
the number of unique `C_CRITERION` versions, planned candidate jobs, estimated
compute, and storage. Resource infeasibility downgrades RQ4 to a case series; it
does not authorize hash sampling or favorable-version selection. Exact overlap
between `C_CONSTRUCT` and `C_CRITERION` reuses one artifact and one execution,
with both cohort roles recorded.

### 5.5 Controlled-only supplements

If P12 does not cover a declared scale × technique cell or semantic-contract
family, a
public program may be added through the same hash-ranked eligibility procedure.
Supplemental programs contribute only to RQ1–RQ3 and are labelled:

```text
CONTROLLED_ONLY
REAL_FAULT_EVIDENCE_ABSENT
```

They never enter RQ4 or statements about observed real-fault prevalence.

## 6. Semantic-mutant population

### 6.1 Two orthogonal classification axes

Every candidate records both axes below. They cannot be substituted for each
other.

**Construction-mechanism axis** records how code is changed:

- `CE`, `OS`, `HP`, `TF`, and `SI` are historical internal patch-shape campaign
  IDs retained for reproducibility;
- this axis supports patch-overlap, feasibility, and implementation-heterogeneity
  analysis only;
- legacy `CF` must be mapped to a declared construction mechanism or retained as
  `LEGACY_CF`; it cannot silently become a sixth semantic family.

**Semantic-contract axis** records which externally stated property is changed:

- `INV`: invariant or conservation property;
- `MONO`: monotonicity or order property;
- `CONV`: convergence or limiting-behaviour property;
- `DYN`: state, trajectory, or dynamical-evolution property;
- `CMP`: comparison, relative-relation, or representation-consistency property.

Each candidate has exactly one pre-patch primary `semantic_contract_family`.
Additional affected properties may be recorded as secondary tags and enter only
sensitivity analyses. Primary family-balanced SMS and residual-risk claims use
the semantic-contract axis. The construction-mechanism axis never receives the
word “semantic family” in analysis or manuscript results.

The operator catalogue must define both axes, applicability rules, examples,
forbidden overlaps, and the exact mapping of historical IDs before construction.

### 6.2 Candidate budget and applicability

For each confirmatory subject in either controlled cohort, the frozen
applicability matrix allocates two
candidate slots to each of the five semantic-contract families. Each slot also
declares its permitted construction mechanism before patch proposal. An
inapplicable slot is recorded as `NOT_APPLICABLE` and is not transferred to
another family or subject.

Thus each subject has exactly ten declared slots before construction. Every
confirmatory slot uses the same frozen Grok 4.5 High proposal protocol: one
prompt, one context package, one returned candidate patch, and no author repair.
Author- or script-proposed patches are limited to `PILOT_ONLY`. RQ1 therefore
describes the observed artifact yield of this disclosed proposal protocol and
does not claim general LLM generation effectiveness. The frozen patch, manifest,
and independent certification—not regeneration of the proposal—are the
reproducible scientific artifacts.

### 6.3 Construction blindness

The construction package contains only:

- the P12 fixed program version;
- public documentation and build metadata;
- the frozen two-axis operator catalogue;
- the slot identifier, applicability record, and permitted mechanism;
- the already frozen semantic contract, input domain, executable oracle,
  expected effect, and witness-selection policy.

It excludes `.git` history, P12 buggy diffs or revisions, P12 MR source,
reference-MR signatures, candidate MR definitions, MR kill outcomes,
syntactic-mutant outcomes, and manuscript hypotheses about which MR should
succeed. The package hash and exact allowlisted file tree are recorded.

### 6.4 Contract–patch–witness chronology

Each non-pilot slot follows a one-way three-stage state machine:

1. `CONTRACT_FROZEN`: freeze the semantic-contract family, executable predicate,
   committed input domain, canonical input ordering or seed stream, oracle,
   tolerance, activation obligation, and expected direction of violation;
2. `PATCH_FROZEN`: expose the contract package to the proposer and freeze the
   returned exact patch without changing any Stage 1 field;
3. `WITNESS_SELECTED`: an independent certifier searches the frozen domain and
   selects the first qualifying witness in canonical order. If no witness exists,
   the slot becomes `EQUIVALENCE_UNRESOLVED` or `TRIGGER_UNEXERCISED`; neither
   the contract nor patch may be edited.

The proposer cannot write certification artifacts. The certifier cannot edit
the contract, expected effect, patch, or candidate source tree. State hashes and
timestamps prove the order.

### 6.5 Certification

Every candidate is assigned exactly one terminal state:

- `CONFIRMED_NON_EQUIVALENT`;
- `CERTIFIED_EQUIVALENT`;
- `EQUIVALENCE_UNRESOLVED`;
- `TRIGGER_UNEXERCISED`;
- `INVALID_MUTANT`;
- `DUPLICATE_MUTANT`;
- `INFRASTRUCTURE_UNRESOLVED`.

Certification applies the nine gates in the governing design: patch scope,
build and execution, interface preservation, activation, original contract,
mutant contract, stability, non-equivalence witness, and uniqueness. No MR kill
result participates in certification.

## 7. Traditional syntactic-mutant baseline

For each paired fixed version, a frozen first-order syntactic mutation tool and
operator configuration generates the baseline population.

- generation order is canonicalized by operator, path, source span, and patch
  hash;
- at most 100 candidates per subject are selected by lowest patch SHA-256 before
  execution;
- invalid, duplicate, unresolved, and build-failing candidates remain in the
  funnel and are not replaced;
- the same MR-independent differential-witness and certificate rules classify
  syntactic candidates as confirmed non-equivalent, certified equivalent, or
  equivalence unresolved;
- `MS_syntax_strict` uses only confirmed non-equivalent candidates;
- `MS_syntax_conservative` reports lower and upper bounds with unresolved
  candidates, matching the semantic-mutant equivalence policy;
- a deterministic ten-candidate-per-subject sample provides a budget-matched
  sensitivity comparison with the semantic candidate slots;
- lack of a semantic contract prevents a syntactic mutant from being relabelled
  as a certified semantic mutant after observing MR outcomes.

The baseline supports incremental-value analysis. It does not define semantic
validity and is not claimed to represent every syntactic mutation system.

## 8. MR inventory and evaluated MR sets

### 8.1 Inventory freeze

For each subject, freeze every admissible evaluation MR from a predeclared P3 MR
source frame assembled from program specifications, public documentation, and
MR artifacts that predate Package C opening. Record its provenance, source and
follow-up input generator, oracle, tolerance, seed policy, timeout, environment,
and cost measurement rule. P12 buggy artifacts, reference MRs, and real-fault
outcomes cannot be used to propose or admit an evaluation MR. Before portfolio
construction, an isolated exclusion process removes every
`ADMISSION_POSITIVE_CONTROL` reference MR, exact implementation variant, and
canonical-semantic-signature duplicate. The exclusion manifest is frozen and
auditable. Invalid or flaky remaining MRs are classified before mutant outcomes
and remain in the execution funnel. If no non-reference MR remains for a
subject, record `NO_INDEPENDENT_EVALUATION_MR`; do not promote its reference MR.

The exclusion process runs under the holdout custodian. It may compare candidate
and reference signatures, but emits only the excluded candidate MR ID, reason
code, and comparison hash. Construction and controlled-execution processes do
not receive reference-MR source, identity, signature, or behavior.

The canonical semantic signature is computed without executions or outcomes as
the SHA-256 of a schema-versioned canonical representation of the source-input
transformation, follow-up-input transformation, metamorphic relation predicate,
tolerance class, and oracle direction. Signature construction normalizes names
but not executable semantics. A pair that cannot be classified mechanically is
`SIGNATURE_UNCERTAIN` and is conservatively excluded from confirmatory
portfolios rather than adjudicated after outcomes.

P3 does not compare MR-generation prompts or claim that one recognition method
is generally superior. Provenance labels may be reported descriptively but are
not the paper's central treatment.

### 8.2 Descriptive lattice and confirmatory portfolio sample

Let a subject have `q` frozen, non-reference valid MRs.

- the descriptive lattice contains all singleton sets, the full set, and every
  leave-one-out set;
- if `q <= 12`, all remaining nonempty subsets may be executed for descriptive
  visualisation only;
- confirmatory fixed budgets are `b = 1`, `b = 2`, `b = 4`, and `b = q`; a
  subject contributes only budgets not exceeding `q`;
- at each nontrivial budget below `q`, select at most 20 subsets by SHA-256-seeded
  combinadic unranking without enumerating all combinations;
- the exact generator, seed, sampled combination ranks, and portfolio hashes are
  frozen before outcomes;
- no portfolio is added, removed, resized, or promoted from descriptive to
  confirmatory after seeing mutant or P12 results.

Every subject × budget cell receives total analysis weight one, divided equally
over its sampled portfolios. Consequently, a subject with many available MRs or
combinations cannot create a larger effective sample. The full lattice explains
set behaviour but supplies no independent degrees of freedom and is not used to
inflate inferential sample size.

## 9. Execution matrices

For every subject and every frozen non-reference valid MR, record three aligned
outcomes:

1. semantic-mutant kill vector;
2. syntactic-mutant kill vector;
3. P12 real-fault buggy/fixed detection vector when a paired P12 fault exists.

The atomic row key is:

```text
(subject_commit, object_type, object_id, mr_id, repetition_id, environment_id)
```

Each row records original output, follow-up output, oracle value, tolerance,
exit status, timeout, duration, seed, stdout/stderr hashes, and artifact paths.
Aggregation is forbidden until the complete atomic ledger passes schema,
uniqueness, and hash validation.

## 10. Metrics

For MR set `R`, confirmed semantic-mutant set `M`, frozen semantic-contract
family set `F_target = {INV, MONO, CONV, DYN, CMP}`, represented family set
`F_cert`, and kill indicator `K_R(m)`:

```text
SMS_instance(R) = sum_m K_R(m) / |M|

SMS_family(R) = (1 / |F_cert|) * sum_f [sum_{m in M_f} K_R(m) / |M_f|]

CDC = |F_cert| / |F_target|
```

`SMS_family` is never interpreted without construct-domain coverage `CDC` and
the exact `F_cert` set. A target family with no confirmed item is
`UNMEASURED`, not covered and not missed. Cross-cohort score comparisons use the
intersection of represented frozen families and report the excluded family set.
The patch-mechanism IDs `CE/OS/HP/TF/SI` never appear in this formula.

Required controlled-mutant outputs:

- family-balanced `SMS_family` as the primary score;
- construct-domain coverage `CDC` and every `UNMEASURED` target family;
- instance-weighted `SMS_instance`;
- conservative lower and upper bounds including equivalence-unresolved items;
- family residual `1 - SMS_f(R)`;
- each MR's marginal and unique contribution;
- pairwise kill-vector overlap and redundancy;
- wall-clock and CPU cost per additional semantic kill;
- complete construction, certification, and execution funnels.

Required real-fault outputs:

- P12 real-fault detection rate within the declared MR-detectable benchmark;
- detection by `DIRECT` semantic-contract family, size, technique, and repository;
- missed real faults associated with semantic-contract-family residuals;
- all P12 exclusions, mapping uncertainties, and failed executions.

## 11. Prespecified analysis

### 11.1 RQ1

Report counts and project-clustered bootstrap 95% confidence intervals for
certification yield. Report all seven terminal states by semantic-contract
family, construction mechanism, scale, and technique. Do not test a post hoc
universal success threshold.

Broad cross-stratum constructibility wording requires:

- at least 75 confirmed non-equivalent semantic mutants;
- at least eight confirmed mutants in each primary semantic-contract family;
- at least 15 confirmed mutants in each represented size stratum;
- at least eight confirmed mutants in each claimed technique stratum;
- no subject contributing more than 12.5% of the semantic denominator;
- at least 15 subjects from at least eight repositories;
- each claimed semantic-contract family, size stratum, or technique stratum to
  contain at least three subjects from at least two repositories.

If a condition fails, retain the results and restrict the claim to represented
subjects and families. These are minimum diversity gates, not power-derived
proof of population-wide constructibility or prevalence.

### 11.2 RQ2

Report normalized-patch and mutant-tree exact overlap with exact binomial
intervals, plus contract-category coverage. Compare semantic and syntactic
execution funnels using paired subject-level differences and project-clustered
bootstrap intervals. Do not infer testing value from AST or patch distance.

### 11.3 RQ3

For every MR-set portfolio, report all metrics in Section 10. The exhaustive or
descriptive lattice receives descriptive summaries only. Confirmatory contrasts
use the frozen fixed-budget sample, normalize weights to one per subject ×
budget cell, and resample or permute entire projects. Compare portfolios at the
same MR count and measured execution budget. Control family-level secondary
comparisons using Benjamini–Hochberg at `q = 0.05`.

The paper must report surviving semantic-contract families and concrete
residuals even when aggregate scores are high.

### 11.4 RQ4

Primary RQ4 analysis uses `P12_PAIRED`, including every mapping state, and is
performed on project × fixed-budget aggregates. The report first gives pairing
coverage by project, fault, and exact fixed version, including every failed or
missing controlled profile. Within a project × budget cell,
portfolio-level semantic score, syntactic score, and real-fault detection are
averaged using the frozen equal cell weights. Overlapping portfolios do not
become independent observations.

The response for a project × budget cell is the equal-fault, equal-portfolio
detection fraction, and model loss is Bernoulli cross-entropy evaluated on that
fraction. Each held-out project's loss is first averaged across its available
fixed budgets; `Delta_sem` is then the equal-project mean difference. Fault,
portfolio, or budget multiplicity therefore cannot increase a project's weight.

Before outcome opening, use P12 project and fault counts plus a grid of plausible
intraclass correlations and detection rates to simulate the minimum detectable
change in leave-one-project-out log loss. Predictive modelling is eligible only
under a prospectively compatible successor P12 contract and when all existing
P12 v1.1.2 confirmatory floors are met: at least 17 analyzable projects, at least
60 real-fault families, at least two families per project, and no project
contributing more than 20% of the faults. A successor P12 contract may raise but
not lower these floors without a separately reviewed amendment.

If eligible, compare two deliberately small regularized models:

- `MSYN`: budget, execution cost, and `MS_syntax_strict`;
- `MBOTH`: the same predictors plus `SMS_family` and `CDC`.

Hyperparameters are fixed by an inner leave-one-project-out loop. The outer
leave-one-project-out predictions are the only inputs to the primary log-loss
comparison. The primary incremental statistic is:

```text
Delta_sem = logloss(MSYN) - logloss(MBOTH)
```

A positive value favors incremental semantic information. A central claim of
incremental value requires the project-clustered bootstrap 95% interval for
`Delta_sem` to lie entirely above zero, no complete or quasi-complete separation,
and the simulation-based sensitivity report to show that effects of the
observed magnitude were identifiable under the achieved cluster structure.
Otherwise the result is reported as observed, qualified, insufficient, or
blocked according to the claim ledger.

Secondary analyses are:

- Kendall association between project-budget semantic adequacy and real-fault
  detection, using project-clustered intervals;
- odds ratio for a real fault remaining undetected when its `DIRECT`
  semantic-contract family is a residual family of `R`, restricted to
  `P12_DIRECT` and explicitly
  labelled mechanism-concordance evidence;
- `ADJACENT` mapping sensitivity;
- budget-matched syntactic sampling sensitivity;
- leave-one-technique and leave-one-size-stratum sensitivity;
- `P12_FULL` case-series results without paired or mapping-based inference;
- lower/upper model sensitivity using syntactic and semantic equivalence bounds.

Without the compatible successor contract, below the 17-project/60-family floor,
or when event distribution makes the regularized model unidentified, RQ4 is a
bounded project-level case series. No predictive-validity or incremental-value
claim is allowed.

## 12. Non-circular mapping of P12 faults

The P12-to-semantic-contract-family mapper consumes only frozen buggy/fixed
identities, the defect patch, independently recorded behavioral contract
metadata, and the operator catalogue. It cannot read MR source, MR identities,
or kill outcomes.

The mapper emits one of:

- `DIRECT`;
- `ADJACENT`;
- `OUT_OF_SCOPE`;
- `UNCERTAIN`.

Classification is rule-based and schema validated. Ambiguous multi-family cases
become `UNCERTAIN`; Grok or an author may explain an uncertainty but cannot
promote it into `P12_DIRECT`. All mapping states remain in the primary
family-agnostic `P12_PAIRED` analysis. The mapping registry and its hash are
frozen before any P12 MR outcome is opened to the analysis process.

After the P12 buggy layer is opened, a mechanical leakage audit compares every
controlled mutant with every paired real fault by exact patch hash, mutant tree,
changed-symbol set, and canonical semantic signature. Exact patch/tree matches
are tagged `REAL_FAULT_DUPLICATE_POSITIVE_CONTROL` and excluded from primary
incremental-value modelling; canonical-signature matches without exact identity
remain in a prespecified sensitivity analysis. Counts and exclusions are
reported, never replaced.

### 12.1 Physical evidence partitions

Logical allowlists are supplemented by three physical packages:

1. `PACKAGE_A_CONSTRUCTION`: fixed source snapshots, documentation, frozen
   contracts, and proposal inputs; no `.git`, buggy revisions, MR files,
   reference-MR signatures, or outcomes;
2. `PACKAGE_B_CONTROLLED_EXECUTION`: certified original/mutant trees and the
   non-reference MR inventory; no P12 buggy tree or real-fault result;
3. `PACKAGE_C_REAL_HOLDOUT`: P12 buggy/fixed identities and execution material,
   mounted only after Packages A and B, controlled denominators, non-reference
   portfolios, and analysis code are sealed. Immediately after mounting, an
   isolated mapper and leakage-audit processes may read Package C, but no
   evaluated MR may execute on a P12 bug until their outputs are frozen.

Each package has an independent manifest and tree hash. The Cursor controller
receives only the package required by the current phase. A clean verifier checks
absence, not merely non-use, of forbidden paths and identities.

## 13. Cursor VM execution design

### 13.1 Role of Cursor and Grok 4.5 High

The fresh Cursor VM with Grok 4.5 High is the execution environment. Grok may:

- invoke frozen commands;
- propose candidate exact patches during the blinded construction phase;
- report mechanical failures;
- assemble already-validated artifacts.

Cursor VM commands invoke the frozen project CLIs directly and do not use the
local GPT Desktop `rtk` wrapper. The `rtk` requirement remains limited to local
Desktop shell work.

Grok may not decide admission, semantic-contract-family mapping, equivalence, MR
kills, claim status, or whether an inconvenient run should be excluded. Those
decisions are produced by frozen code, schemas, and prespecified rules.

### 13.2 Reusable preflight rather than one-shot bootstrap

Before a confirmatory run, a repeatable non-scientific preflight verifies:

- repository and commit identities;
- normalized remote identity without requiring one URL spelling;
- CPU, memory, disk, OS, Python, compiler, and dependency lock;
- build and smoke tests for every selected subject;
- subprocess, atomic-rename, file-lock, and parallel-worker capabilities;
- offline availability of all confirmatory inputs;
- exact model label `Grok 4.5 High` in the environment record.

Preflight failure does not consume a scientific run and may be diagnosed and
rerun. Confirmatory authorization begins only after the complete manifest is
frozen and the first atomic experimental job is recorded.

### 13.3 Parallel execution

Independent `(subject, object, MR, repetition)` jobs may run in parallel.

- the job list is canonical and hashed before launch;
- each job writes only to its own content-addressed directory;
- no worker mutates a shared ledger;
- workers use frozen seeds and resource limits;
- a single reducer validates and merges completed immutable rows;
- concurrency is capped by the lowest of CPU, memory, and subject-specific
  limits discovered in preflight;
- stochastic or GPU-sensitive subjects may declare concurrency `1`.

Parallel scheduling may change completion order but cannot change job identity,
inputs, seeds, or accepted outputs.

### 13.4 Failure and retry policy

The prior universal “first failure consumes the VM and forbids investigation”
policy is not used.

- every attempt, including failed and inconclusive attempts, remains in the
  experiment ledger;
- a transient infrastructure operation may be attempted at most three times
  with the same job ID, inputs, seed, and command;
- scientific repetitions are fixed in advance and are never increased after
  inspecting effect estimates;
- deterministic code, schema, or contract failure is not retried under the same
  protocol version;
- any code or configuration repair increments the protocol version and reruns
  the complete affected phase while retaining the failed version;
- a successful rerun cannot erase or overwrite an earlier failure.

## 14. Execution sequence

### Phase 0 — Freeze claims and governance

Create and hash:

- `research/p3_v3/score-task.yml`;
- `research/p3_v3/claim-ledger.yml`;
- `research/p3_v3/operator-catalog.yml`;
- `research/p3_v3/analysis-plan.md`;
- `research/p3_v3/rq4-sensitivity-plan.yml`;
- `research/p3_v3/p12-contract-compatibility.json`;
- `research/p3_v3/environment-lock.json`.

Exit criterion: exact RQs, claim ceiling, metrics, retry policy, and prohibited
claims are machine-readable and internally consistent; the RQ4 simulation grid,
cluster assumptions, model-eligibility floor, P12 contract-compatibility gate,
and downgrade rules are frozen.

### Phase 1 — Build the blinded subject and MR frames

Produce:

- `research/p3_v3/p12-eligible-frame.json`;
- `research/p3_v3/construct-cohort-frame.json`;
- `research/p3_v3/criterion-cohort-frame.json`;
- `research/p3_v3/subject-frame.json`;
- `research/p3_v3/subject-strata.json`;
- `research/p3_v3/mr-inventory.json`;
- `research/p3_v3/mr-set-lattice.json`;
- `research/p3_v3/reference-mr-exclusions.json`;
- `research/p3_v3/construction-allowlist.json`;
- package schemas and allow/deny rules, the final Package A manifest, and an
  independently assembled sealed Package C root hash. Until Phase 7, the
  construction and controlled-execution processes can read only that opaque root
  hash, not Package C paths, identities, or contents.

Exit criterion: deterministic selection can be recomputed from frozen inputs;
the reference-MR exclusion set is reproducible; Package A physically excludes
`.git`, buggy diffs, MRs, and outcomes; Package C is sealed but not mounted in
the construction or controlled-execution environment; the criterion frame
contains every unique eligible P12 fixed commit with no outcome-based sampling.

### Phase 2 — Instrument pilot

Use separate non-P12 pilot subjects, one per represented implementation
technique, to validate patch application, contracts, coverage, witnesses,
syntactic baseline, MR runner, atomic ledger, and parallel reduction.

Pilot objects and outcomes are permanently labelled `PILOT_ONLY` and cannot
enter any confirmatory denominator or result table.

Exit criterion: every pipeline state has a deliberate positive and negative
test; pilot failures are resolved before the confirmatory freeze.

### Phase 3 — Contract freeze and patch proposal

Process each candidate slot in the following order and freeze every transition:

- subject commits and strata;
- ten semantic-contract candidate slots per subject;
- each slot's semantic-contract family, executable predicate, domain, canonical
  witness search, oracle, tolerance, activation obligation, and expected effect;
- Package A construction input;
- the single Grok 4.5 High proposal response and frozen candidate exact patch;
- syntactic mutation configuration;
- hash bindings to the already frozen non-reference MR inventory, confirmatory
  portfolio sample, seeds, tolerances, timeouts, and analysis code; none of those
  MR contents is mounted in Package A.

Exit criterion: state hashes prove `CONTRACT_FROZEN` precedes `PATCH_FROZEN`; a
clean verifier proves that no evaluated MR, P12 buggy revision, reference-MR
signature, or P12 outcome was present in Package A.

### Phase 4 — Semantic certification

Run the canonical witness search and complete certification pipeline in Cursor
VM. Preserve every terminal state and raw artifact. The first qualifying witness
in canonical order is frozen without modifying the contract or patch. Freeze the
primary semantic denominator, then assemble and hash the immutable Package B
semantic segment. No MR execution is available before that denominator is
frozen.

Exit criterion: denominator membership is reproducible from exact patches,
contracts, witnesses, logs, and environment identity.

### Phase 5 — Syntactic baseline

Generate and execute the frozen syntactic candidate population on the same
fixed versions. Preserve the full and budget-matched denominator manifests,
then assemble the final Package B manifest from the already frozen semantic
segment, the frozen syntactic segment, the non-reference MR inventory, and the
controlled job-list inputs. Final assembly cannot rewrite either segment.

Exit criterion: generation and funnel results are independent of all MR and P12
outcomes; the final Package B manifest binds both controlled denominators and is
immutable before Phase 6 execution.

### Phase 6 — Controlled MR execution

Derive and freeze the canonical controlled job list from the already frozen
non-reference MR inventory and the two frozen mutant denominators. Execute it
against original versions, certified semantic mutants, and syntactic mutants.
Run jobs in parallel where allowed and reduce them into immutable atomic
matrices.

Exit criterion: every planned row has exactly one terminal outcome, and missing
or failed rows are explicit rather than imputed.

### Phase 7 — P12 real-fault execution

Mount Package C only after Phases 4–6 are sealed. First, an isolated mapper that
cannot read Package B freezes the rule-based semantic-contract-family mapping
from buggy/fixed artifacts. Second, a separate leakage auditor reads only
Package C and a projection of controlled-mutant patch, tree, changed-symbol, and
semantic-signature identities; it cannot read MR definitions or any kill
outcome. Freeze both outputs and the real-fault job list before the first
evaluated non-reference MR runs on any P12 buggy version. Then execute the same
non-reference MR inventories. Reference positive controls, if required for P12
benchmark admission, are not executed by P3 until the confirmatory P3 analysis
is sealed and never enter P3 models or portfolio scores.

Exit criterion: all eligible faults, including misses and execution failures,
are represented.

### Phase 8 — Prespecified analysis

Generate RQ1–RQ4 tables, figures, confidence intervals, portfolio comparisons,
residual explanations, model comparisons, and sensitivity analyses from the
immutable matrices.

Exit criterion: every number in a table or figure traces to atomic rows and the
analysis commit; no manual spreadsheet value is authoritative.

### Phase 9 — Independent evidence gate

On a clean environment, verify artifact hashes, schemas, input/output closure,
failed-run retention, denominator freeze chronology, analysis regeneration, and
claim status.

Exit criterion: produce an evidence package containing supported, observed,
qualified, insufficient, blocked, and speculative claims. Manuscript writing
may use only the first three statuses with matching wording strength.

## 15. Required result tables and figures

1. subject frame by cohort role, repository, exact fixed version, scale,
   technique, and P12/supplemental role, plus P12 pairing coverage;
2. semantic candidate and certification funnel by semantic-contract family,
   construction mechanism, and stratum;
3. semantic-versus-syntactic construct comparison;
4. per-MR and per-portfolio semantic kill matrix;
5. family-balanced, instance-weighted, and conservative SMS views;
6. MR unique contribution, redundancy, residual, and cost table;
7. P12 real-fault detection matrix and mapping states;
8. controlled-to-real criterion-validity and incremental-value results;
9. all failures, inconclusive cases, empty strata, and claim downgrades;
10. a claim-to-artifact ledger for every abstract and contribution sentence.

## 16. Reproducibility artifacts

The implementation must ultimately produce:

```text
research/p3_v3/score-task.yml
research/p3_v3/claim-ledger.yml
research/p3_v3/experiment-ledger.yml
research/p3_v3/operator-catalog.yml
research/p3_v3/construct-cohort-frame.json
research/p3_v3/criterion-cohort-frame.json
research/p3_v3/subject-frame.json
research/p3_v3/mr-inventory.json
research/p3_v3/mr-set-lattice.json
research/p3_v3/reference-mr-exclusions.json
research/p3_v3/rq4-sensitivity-plan.yml
research/p3_v3/p12-contract-compatibility.json
research/p3_v3/analysis-plan.md
research/p3_v3/environment-lock.json
data/p3_v3/manifests/package-a-construction.json
data/p3_v3/manifests/package-b-controlled-execution.json
data/p3_v3/manifests/package-c-real-holdout.json
data/p3_v3/manifests/p12-semantic-contract-family-mapping.json
data/p3_v3/manifests/controlled-real-leakage-audit.json
data/p3_v3/raw/
data/p3_v3/matrices/
data/p3_v3/results/
data/p3_v3/evidence-package.md
```

Raw, failed, and inconclusive artifacts are append-only. Derived tables and
figures are regenerated from raw matrices and never edited as sources of truth.

## 17. Argument outcomes

The design supports four scientifically honest endpoints:

1. **Strong positive:** semantic adequacy is construct-distinct, interpretable,
   and incrementally predictive within the P12 domain.
2. **Qualified positive:** semantic adequacy explains family-level residuals but
   incremental predictive evidence is uncertain.
3. **Boundary result:** semantic mutants are reproducible and distinct, but do
   not improve real-fault explanation over syntactic mutation.
4. **Negative result:** construction yield, diversity, or real-fault alignment
   is insufficient; the concept remains formal/methodological and the failed
   funnel defines its boundary.

No endpoint permits changing the sample, patches, MR portfolios, mappings,
metrics, or claim thresholds after outcomes are observed.

## 18. Work decomposition after approval

This scientific plan should be implemented through four separately reviewable
plans:

1. evidence schemas, subject framing, and blinded package construction;
2. artifact-first semantic-mutant construction and certification;
3. syntactic baseline, MR runner, atomic matrices, and parallel reducer;
4. P12 integration, statistical analysis, evidence package, and Cursor VM launch
   instructions.

Cursor VM instructions are generated only after all four implementation plans,
their tests, and the repeatable preflight pass. They must launch existing
audited CLIs rather than embed a new unaudited controller in the instruction
text.
