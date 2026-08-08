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
- Verification status: proposed design, pending user review
- Execution environment: fresh Cursor VM, Grok 4.5 High
- Scientific authority: frozen artifacts and executable checks, never model judgment
- Governing design:
  `docs/superpowers/specs/2026-08-08-p3-semantic-mutant-construction-principles-design.md`

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
  -> the same frozen MR inventory executed on both mutant populations
  -> family-aware MR-set adequacy profiles
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

P12 remains a benchmark of **MR-detectable real semantic defects**. Results may
be generalized to that declared benchmark domain, not to all software defects.

## 3. Research questions

### RQ1 — Construction and certification

Can the artifact-first protocol produce executable, independently certified,
non-equivalent semantic-mutant versions across different program scales and
implementation techniques?

Evidence:

- the complete candidate-to-certified funnel;
- pass, fail, and inconclusive states for every certification gate;
- certification yield by semantic family, program-scale stratum, implementation
  stratum, repository, and target program;
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

Which semantic mutants and semantic families are detected or missed by each MR
set, and what do unique contribution, redundancy, residual risk, and execution
cost reveal beyond a single aggregate mutation score?

The primary controlled-mutant measure is family-balanced semantic mutation
score. Instance-weighted score, conservative equivalence bounds, unique kills,
redundancy, residual families, and cost-normalized coverage are required
secondary views.

### RQ4 — P12 criterion validity and incremental value

On frozen P12 MR-detectable real defects, do semantic-mutant adequacy profiles
explain or predict MR-set detection outcomes, and do they add information beyond
traditional syntactic mutation score?

Primary evidence uses only real defects with an outcome-blind `DIRECT` mapping
to a frozen semantic family. `ADJACENT` mappings are sensitivity evidence;
`OUT_OF_SCOPE` and `UNCERTAIN` cases remain visible but do not enter the primary
mapping analysis.

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

### 5.1 Primary P12 frame

The real-fault frame contains every P12 item satisfying the P12 benchmark's
already-frozen requirements:

- immutable buggy and fixed program identities;
- a reproducible original/fixed execution path;
- an executable reference MR demonstrating that the fault is MR-detectable;
- complete provenance and no unresolved licensing restriction.

P3 applies no additional inclusion rule based on the candidate MR sets' kill
outcomes. All eligible P12 items in selected project/version strata remain in
the ledger, including items missed by every evaluated MR set.

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

Each subject receives exactly one primary technique label under the following
precedence order:

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

The classifier is a frozen rule engine over dependency metadata, call traces,
and declared target symbols. Ambiguous subjects receive `TECH_UNCERTAIN` and
remain visible; they do not enter technique-stratified confirmatory claims.

### 5.4 Deterministic subject selection

The paired confirmatory cohort is selected before P3 sees MR outcomes:

1. enumerate the complete eligible P12 fixed-version frame;
2. classify scale and implementation technique mechanically;
3. within each nonempty scale × technique cell, rank candidates by
   `SHA256(fixed_commit || project_id || target_id || "P3-C1")`;
4. select the first candidate per cell, then continue round-robin by the same
   rank until 18 subjects are selected or the frame is exhausted;
5. retain an explicit `EMPTY_FRAME` record for every unfilled cell.

The target is representation of all three size strata, at least four
implementation techniques, at least eight repositories, and at least 15 paired
subjects. Failure to meet that target downgrades cross-stratum claims; it does
not authorize outcome-based replacement.

### 5.5 Controlled-only supplements

If P12 does not cover a declared scale × technique cell or semantic family, a
public program may be added through the same hash-ranked eligibility procedure.
Supplemental programs contribute only to RQ1–RQ3 and are labelled:

```text
CONTROLLED_ONLY
REAL_FAULT_EVIDENCE_ABSENT
```

They never enter RQ4 or statements about observed real-fault prevalence.

## 6. Semantic-mutant population

### 6.1 Primary families

P3 uses five primary semantic mutation families, treated as semantic fault
campaign families rather than MR meta-patterns:

- `CE`: conservation or quantitative-constraint erosion;
- `OS`: semantically incompatible operator or API substitution;
- `HP`: hyperparameter or tolerance semantics perturbation;
- `TF`: trajectory, training-data, or state-evolution transformation;
- `SI`: structural, indexing, aggregation, or algorithm-skeleton injection.

The final operator catalogue must state family definitions, applicability
rules, forbidden overlaps, and the exact handling of legacy `CF` items before
candidate construction. `CF` cannot silently become a sixth primary family.

### 6.2 Candidate budget and applicability

For each confirmatory subject, the frozen applicability matrix allocates two
candidate slots to each of the five families. An inapplicable slot is recorded
as `NOT_APPLICABLE` and is not transferred to another family or subject.

Thus each subject has exactly ten declared slots before construction. Candidate
patches may be proposed by a project-specific script, an author, or Grok 4.5
High. Candidate proposal is not an evaluated contribution. The accepted patch,
its manifest, and its independent certification are the scientific artifact.

### 6.3 Construction blindness

The construction package contains only:

- the P12 fixed program version;
- public documentation and build metadata;
- the frozen operator-family catalogue;
- the slot identifier and applicability record;
- the semantic-contract and witness schema.

It excludes P12 buggy diffs, P12 MR source, candidate MR definitions, MR kill
outcomes, syntactic-mutant outcomes, and manuscript hypotheses about which MR
should succeed. The package hash and allowlisted file tree are recorded.

### 6.4 Certification

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
- the primary syntactic score uses the full frozen executable denominator;
- a deterministic ten-candidate-per-subject sample provides a budget-matched
  sensitivity comparison with the semantic candidate slots;
- lack of a semantic contract prevents a syntactic mutant from being relabelled
  as a certified semantic mutant after observing MR outcomes.

The baseline supports incremental-value analysis. It does not define semantic
validity and is not claimed to represent every syntactic mutation system.

## 8. MR inventory and evaluated MR sets

### 8.1 Inventory freeze

For each subject, freeze every admissible P12 MR implementation, its source and
follow-up input generator, oracle, tolerance, seed policy, timeout, environment,
and cost measurement rule. Invalid or flaky MRs are classified before mutant
outcomes and remain in the execution funnel.

P3 does not compare MR-generation prompts or claim that one recognition method
is generally superior. Provenance labels may be reported descriptively but are
not the paper's central treatment.

### 8.2 Objective MR-set portfolio lattice

Let a subject have `q` frozen valid MRs.

- if `q <= 12`, evaluate every nonempty MR subset;
- if `q > 12`, evaluate all singleton sets, the full set, every leave-one-out
  set, and 100 deterministic subsets at each size
  `b = 2, ..., min(12, q - 1)`;
- deterministic subsets are the first 100 unique subsets after sorting by
  `SHA256(subject_id || b || sorted_mr_ids || "P3-MRSET")`;
- no portfolio is added, removed, or resized after seeing mutant or P12 results.

This lattice lets P3 compare and explain MR sets without introducing a separate
MR-selection method as an undeclared contribution.

## 9. Execution matrices

For every subject and every valid MR, record three aligned outcomes:

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

For MR set `R`, confirmed semantic-mutant set `M`, semantic family set `F`, and
kill indicator `K_R(m)`:

```text
SMS_instance(R) = sum_m K_R(m) / |M|

SMS_family(R) = (1 / |F*|) * sum_f [sum_{m in M_f} K_R(m) / |M_f|]
```

`F*` contains only prospectively applicable families with at least one
confirmed denominator item. Missing families are reported rather than silently
removed from the applicability funnel.

Required controlled-mutant outputs:

- family-balanced `SMS_family` as the primary score;
- instance-weighted `SMS_instance`;
- conservative lower and upper bounds including equivalence-unresolved items;
- family residual `1 - SMS_f(R)`;
- each MR's marginal and unique contribution;
- pairwise kill-vector overlap and redundancy;
- wall-clock and CPU cost per additional semantic kill;
- complete construction, certification, and execution funnels.

Required real-fault outputs:

- P12 real-fault detection rate within the declared MR-detectable benchmark;
- detection by `DIRECT` semantic family, size, technique, and repository;
- missed real faults associated with semantic-family residuals;
- all P12 exclusions, mapping uncertainties, and failed executions.

## 11. Prespecified analysis

### 11.1 RQ1

Report counts and project-clustered bootstrap 95% confidence intervals for
certification yield. Report all seven terminal states by family, scale, and
technique. Do not test a post hoc universal success threshold.

Broad cross-stratum constructibility wording requires:

- at least 75 confirmed non-equivalent semantic mutants;
- at least eight confirmed mutants in each primary family;
- at least 15 confirmed mutants in each represented size stratum;
- at least eight confirmed mutants in each claimed technique stratum;
- no subject contributing more than 12.5% of the semantic denominator;
- at least 15 subjects from at least eight repositories.

If a condition fails, retain the results and restrict the claim to represented
subjects and families.

### 11.2 RQ2

Report normalized-patch and mutant-tree exact overlap with exact binomial
intervals, plus contract-category coverage. Compare semantic and syntactic
execution funnels using paired subject-level differences and project-clustered
bootstrap intervals. Do not infer testing value from AST or patch distance.

### 11.3 RQ3

For every MR-set portfolio, report all metrics in Section 10. Compare portfolios
at the same MR count and measured execution budget. Use subject-blocked
permutation tests for family-balanced score contrasts and control family-level
secondary comparisons using Benjamini–Hochberg at `q = 0.05`.

The paper must report surviving semantic families and concrete residuals even
when aggregate scores are high.

### 11.4 RQ4

Primary RQ4 analysis is project-held-out and uses only `DIRECT` P12 mappings.

For each real defect `d` and MR set `R`, fit and compare:

- `M0`: MR count, execution cost, scale, and technique controls;
- `MSYN`: `M0` plus traditional syntactic mutation score;
- `MSEM`: `M0` plus family-balanced and mapped-family semantic coverage;
- `MBOTH`: `M0` plus both syntactic and semantic predictors.

Evaluate with leave-one-project-out log loss. The primary incremental statistic
is:

```text
Delta_sem = logloss(MSYN) - logloss(MBOTH)
```

A positive value favors incremental semantic information. A central claim of
incremental value requires the project-clustered bootstrap 95% interval for
`Delta_sem` to lie entirely above zero. Otherwise the result is reported as
observed, qualified, insufficient, or blocked according to the claim ledger.

Secondary analyses are:

- Kendall association between semantic adequacy and real-fault detection,
  clustered by project and matched by MR-set size;
- odds ratio for a real fault remaining undetected when its `DIRECT` semantic
  family is a residual family of `R`;
- `ADJACENT` mapping sensitivity;
- budget-matched syntactic sampling sensitivity;
- leave-one-technique and leave-one-size-stratum sensitivity;
- full P12 case-series results without mapping-based inference.

If fewer than 30 eligible P12 faults or fewer than six P12 repositories enter
the primary paired analysis, RQ4 is reported as a bounded case series and no
broad predictive-validity claim is allowed.

## 12. Non-circular mapping of P12 faults

The P12-to-semantic-family mapper consumes only frozen buggy/fixed identities,
the defect patch, independently recorded behavioral contract metadata, and the
operator catalogue. It cannot read MR source, MR identities, or kill outcomes.

The mapper emits one of:

- `DIRECT`;
- `ADJACENT`;
- `OUT_OF_SCOPE`;
- `UNCERTAIN`.

Classification is rule-based and schema validated. Ambiguous multi-family cases
become `UNCERTAIN`; Grok or an author may explain an uncertainty but cannot
promote it into the primary analysis. The mapping registry and its hash are
frozen before any P12 MR outcome is opened to the analysis process.

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

Grok may not decide admission, semantic-family mapping, equivalence, MR kills,
claim status, or whether an inconvenient run should be excluded. Those decisions
are produced by frozen code, schemas, and prespecified rules.

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
- `research/p3_v3/environment-lock.json`.

Exit criterion: exact RQs, claim ceiling, metrics, retry policy, and prohibited
claims are machine-readable and internally consistent.

### Phase 1 — Build the blinded subject and MR frames

Produce:

- `research/p3_v3/p12-eligible-frame.json`;
- `research/p3_v3/subject-frame.json`;
- `research/p3_v3/subject-strata.json`;
- `research/p3_v3/mr-inventory.json`;
- `research/p3_v3/mr-set-lattice.json`;
- `research/p3_v3/construction-allowlist.json`.

Exit criterion: deterministic selection can be recomputed from frozen inputs;
the construction allowlist excludes buggy diffs, MRs, and outcomes.

### Phase 2 — Instrument pilot

Use separate non-P12 pilot subjects, one per represented implementation
technique, to validate patch application, contracts, coverage, witnesses,
syntactic baseline, MR runner, atomic ledger, and parallel reduction.

Pilot objects and outcomes are permanently labelled `PILOT_ONLY` and cannot
enter any confirmatory denominator or result table.

Exit criterion: every pipeline state has a deliberate positive and negative
test; pilot failures are resolved before the confirmatory freeze.

### Phase 3 — Confirmatory freeze

Freeze and hash:

- subject commits and strata;
- ten semantic candidate slots per subject;
- construction packages and frozen candidate exact patches;
- independent contracts and witnesses;
- syntactic mutation configuration;
- MR inventory and portfolio lattice;
- job list, seeds, tolerances, timeouts, and analysis code.

Exit criterion: a clean verifier proves that no evaluated MR or P12 outcome was
available to construction and certification inputs.

### Phase 4 — Semantic certification

Run the complete certification pipeline in Cursor VM. Preserve every terminal
state and raw artifact. Freeze the primary semantic denominator before any MR
execution.

Exit criterion: denominator membership is reproducible from exact patches,
contracts, witnesses, logs, and environment identity.

### Phase 5 — Syntactic baseline

Generate and execute the frozen syntactic candidate population on the same
fixed versions. Preserve the full and budget-matched denominator manifests.

Exit criterion: generation and funnel results are independent of all MR and P12
outcomes.

### Phase 6 — Controlled MR execution

Execute the frozen MR inventory against original versions, certified semantic
mutants, and syntactic mutants. Run the canonical job list in parallel where
allowed and reduce it into immutable atomic matrices.

Exit criterion: every planned row has exactly one terminal outcome, and missing
or failed rows are explicit rather than imputed.

### Phase 7 — P12 real-fault execution

Open the frozen P12 buggy/fixed layer only after Phases 4–6 are sealed. Run the
same MR inventories and freeze the rule-based family mapping before the
real-fault outcome matrix is provided to analysis.

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

1. subject frame by repository, scale, technique, and P12/supplemental role;
2. semantic candidate and certification funnel by family and stratum;
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
research/p3_v3/subject-frame.json
research/p3_v3/mr-inventory.json
research/p3_v3/mr-set-lattice.json
research/p3_v3/analysis-plan.md
research/p3_v3/environment-lock.json
data/p3_v3/manifests/
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
