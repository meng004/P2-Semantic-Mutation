# P3 v3 Phase 0 authority: MR inventory, reference-MR isolation, and portfolio policy

> Authority ID: p3-v3-phase0-mr-policy-v1
> Date frozen: 2026-08-12
> Governing plan: docs/superpowers/plans/2026-08-08-p3-semantic-mutant-argumentation-experiment.md
> Governing plan SHA-256: fea00496801c31ba074aa74742f5e6a77019ffc2e344642122a15462d7443830
> Source sections (verbatim, 1-based inclusive plan lines): Section 5.1 P12 populations and reference-MR isolation (L208-L249); Section 8 MR inventory and evaluated MR sets (L717-L782)
> Scope: verbatim extract for hash-binding and operational reference; the
> governing plan remains the sole scientific authority. All claims remain
> blocked (research/evidence/p3_claim_ledger_v1.3.0.yml).

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

## 8. MR inventory and evaluated MR sets

### 8.1 Inventory freeze

MR construction is a sibling process, not a continuation of semantic-contract
construction. Its builder receives the permitted fixed source, build metadata,
public specifications, and public documentation, but cannot read semantic
contracts, either input inventory, slot applicability, candidate patches,
certificates, controlled denominators, or outcomes. Conversely, the contract,
input, and patch builders cannot read the candidate or final MR
frames.

For each subject, first freeze every candidate evaluation MR from the
predeclared P3 source frame. Record its provenance, source and follow-up input
generator, oracle, tolerance, seed policy, timeout, environment, cost measurement
rule, and canonical semantic signature. Send only the frozen candidate
IDs/signatures and inventory hash to the holdout custodian. P12 buggy artifacts,
reference MRs, and real-fault outcomes cannot be used to propose or admit an
evaluation MR. The returned receipt then removes every
`ADMISSION_POSITIVE_CONTROL` reference MR, exact implementation variant, and
canonical-semantic-signature duplicate. Freeze the receipt, final inventory, and
only then the portfolio sample, in that order. Invalid or flaky remaining MRs
are classified before mutant outcomes
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
