# P3 v3 Phase 0 authority: Semantic operator catalogue and syntactic baseline

> Authority ID: p3-v3-phase0-operator-catalogue-v1
> Date frozen: 2026-08-12
> Governing plan: docs/superpowers/plans/2026-08-08-p3-semantic-mutant-argumentation-experiment.md
> Governing plan SHA-256: fea00496801c31ba074aa74742f5e6a77019ffc2e344642122a15462d7443830
> Source sections (verbatim, 1-based inclusive plan lines): Section 6 Semantic-mutant population (L550-L691); Section 7 Traditional syntactic-mutant baseline (L692-L716)
> Scope: verbatim extract for hash-binding and operational reference; the
> governing plan remains the sole scientific authority. All claims remain
> blocked (research/evidence/p3_claim_ledger_v1.3.0.yml).

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

For each family/mechanism slot, a frozen applicability predicate scans the
canonical `site_id` order and selects the first applicable site. If no site is
applicable, the slot is `NOT_APPLICABLE`; a later site, family, or subject cannot
inherit the budget. The selected site's secondary technique tags are retained
for sensitivity analysis but never redefine the program-level sampling stratum.
Profiling reachability is not an applicability predicate: an `UNPROFILED` site
remains eligible for this static scan, and its later activation attempt and
outcome remain explicit in the certification funnel.

Thus each subject has exactly ten declared slots before construction. Every
confirmatory slot uses the same frozen Grok 4.5 High proposal protocol: one
prompt, one context package, one returned candidate patch, and no author repair.
Author- or script-proposed patches are limited to `PILOT_ONLY`. RQ1 therefore
describes the observed artifact yield of this disclosed proposal protocol and
does not claim general LLM generation effectiveness. The frozen patch, manifest,
and independent certification—not regeneration of the proposal—are the
reproducible scientific artifacts.

Each proposal record binds the exact model and provider label, prompt hash,
context-package hash, raw-response hash, UTC timestamp, and all generation
metadata actually exposed by the provider. Any unavailable proprietary field is
the explicit literal `UNAVAILABLE_NOT_CLAIMED`; no seed, temperature, internal
model revision, or decoding parameter is inferred or fabricated. The
reproducibility claim concerns the frozen input/output artifacts and subsequent
certification, not deterministic regeneration by a proprietary model.

### 6.3 Construction blindness

The construction package contains only:

- the P12-bound blinded fixed source snapshot;
- public documentation and build metadata;
- the frozen two-axis operator catalogue;
- the slot identifier, applicability record, and permitted mechanism;
- the already frozen semantic contract, input domain, executable oracle,
  expected effect, and witness-selection policy.

The proposal process does not receive Profiling Workload outcomes, `E_COMMON`,
or `E_CONTRACT` identities. Those artifacts may coexist in Package A for later
phase consumers, but the proposer receives a clean materialization of the
proposal-process allowlist that excludes them.

It excludes `.git` history, P12 buggy diffs or revisions, P12 MR source,
reference-MR signatures, candidate MR definitions, MR kill outcomes,
syntactic-mutant outcomes, and manuscript hypotheses about which MR should
succeed. The package hash and exact allowlisted file tree are recorded.

### 6.4 Contract–patch–witness chronology

`E_COMMON` closes at subject level before sites or contracts. Each non-pilot
slot then follows exactly one of two terminal paths:

```text
APPLICABILITY_CLOSED_NOT_APPLICABLE
```

or

```text
SITE_FROZEN -> CONTRACT_FROZEN -> E_CONTRACT_FROZEN
-> PATCH_FROZEN -> CERTIFICATION_WITNESS_SELECTED -> TERMINAL_STATE
```

The applicability decision uses only the frozen static predicate and canonical
site order. A `NOT_APPLICABLE` slot has no contract, `E_CONTRACT`, patch, or
certification witness. For an applicable slot, `CONTRACT_FROZEN` records the
family, executable predicate, domain, oracle, tolerance, activation obligation,
and expected violation direction; then an outcome-blind sibling builder creates
the five predetermined `E_CONTRACT` ordinals before patch proposal. It cannot
read a patch, evaluated MR, P12 defect/reference MR, or outcome.

At `PATCH_FROZEN`, the proposer receives the contract package but neither input
inventory nor profiling outcomes. At `CERTIFICATION_WITNESS_SELECTED`, an
independent certifier searches the frozen domain and selects the first qualifying
non-equivalence witness in canonical order. This post-patch witness belongs to
neither `E_COMMON` nor `E_CONTRACT` and cannot be added to any evaluation
inventory. If no witness exists, the slot becomes `EQUIVALENCE_UNRESOLVED` or
`TRIGGER_UNEXERCISED`; neither contract nor patch may be edited.

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
