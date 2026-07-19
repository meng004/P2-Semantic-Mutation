# V125 Two-Layer Semantic Operator Redesign

**Status:** approved direction, written specification pending user review  
**Date:** 2026-07-20  
**Scientific scope:** P3 RQ1 operator-system rescue experiment  
**Upstream blocked evidence:** D1 `V124_OPERATOR_REDESIGN_V5_1_3_DEVELOPMENT_BLOCKED` at `9d01626a3551a331469f7d3e0953632f22b0aea5`

## 1. Decision and purpose

V125 performs one bounded redesign of the semantic-operator system. It tests
whether the V124 breadth failure is caused by coupling an abstract semantic
fault mechanism to one narrow executable source shape.

The redesign separates:

1. an **abstract semantic operator**, which defines the semantic fault; and
2. one or more **generic executable adapters**, which instantiate that fault
   on auditable AST and data-flow shapes.

V125 is not another in-place `v5.1.x` patch. It must not overwrite V124,
reinterpret V124 calibration evidence as validation evidence, or continue
iterating until a favorable result appears.

## 2. Alternatives considered

### A. Continue incremental generator repair

Create `v5.1.4` from `v5.1.3` and repair additional trigger or site-binding
cases. This is rejected because `v5.1.2 -> v5.1.3` increased valid development
units from 16 to 19 without increasing the five represented variants or three
represented families. The observed problem is breadth, not merely yield.

### B. Two-layer operator redesign — selected

Keep the planned 14-variant/8-family semantic taxonomy, but express each
semantic mechanism independently from its executable source adapters. This
directly tests the structural explanation while retaining fail-closed evidence
rules and a fixed stopping boundary.

### C. Stop operator development and narrow the paper immediately

This remains the mandatory fallback if V125 fails its pre-validation gate. It
is not selected as the first action because one bounded architecture-level
test has substantially greater information value than another local repair.

## 3. Frozen evidence interpretation

The P12 intake must independently recompute, rather than trust prose, that
V124 used the same frozen 584-unit development queue and produced:

- 584 attempted units;
- 19 exact-site development-valid units;
- 565 non-valid units;
- 5 variants with at least one valid unit;
- 3 represented families;
- 5 variants with at least two source-disjoint valid projects;
- 0 noninterference failures among admitted development-valid units; and
- 0 validation units and 0 Gate-B-admissible units.

The intake must preserve all V124 generator versions, ledgers, atlases,
failure records, manifests, and handoffs byte-unchanged. The observed
`v5.1.2 -> v5.1.3` breadth delta is frozen as zero variants and zero families.

## 4. Layer 1: abstract semantic operator

Each abstract operator record must contain:

- stable `family_id` and `variant_id`;
- semantic quantity or invariant being changed;
- applicability preconditions;
- intended local semantic effect;
- propagation obligation from the changed value to a downstream checkpoint;
- final observable and semantic abstraction;
- exception, termination, timeout, and numerical-tolerance semantics;
- known invalid, degenerate, and equivalence cases;
- admissible generic adapter identifiers; and
- content hashes of the contract and all referenced policies.

The abstract contract must not name a project, commit, source path, concrete
symbol, outcome, or preferred passing site. Project-specific rules are not
abstract operators.

## 5. Layer 2: generic executable adapter

An executable adapter must define:

- a structural AST/data-flow shape;
- a deterministic source rewrite;
- static applicability guards;
- site ranking frozen before runtime outcomes;
- a public-API reachability certificate;
- an exact mutation-node execution probe;
- a local value trace and downstream propagation checkpoint;
- a final semantic observable;
- build and runtime requirements;
- original/mutant witness construction; and
- instrumented-versus-uninstrumented noninterference checks.

Multiple generic adapters may implement one abstract variant. An adapter is
invalid if it names or special-cases a project, package, commit, source path,
symbol, or previously successful unit. Adapter selection may use only frozen
structural evidence and must not use witness or mutant outcomes.

## 6. Per-unit evidence contract

A development or validation unit is valid only when all of the following are
content-addressed and pass:

1. exact source commit and tree are verified;
2. the selected site matches an allowed adapter and was frozen before the
   original/mutant outcome;
3. the original builds and passes the frozen baseline witness;
4. the mutation is nonempty, unique, parseable, compilable, and attributable
   to exactly one frozen mutation node;
5. the frozen public API reaches that exact mutation node;
6. ordered local-value evidence is captured at the node;
7. required propagation evidence reaches the frozen downstream checkpoint;
8. the final observable is computed using the frozen abstraction and
   tolerance;
9. repeated executions are deterministic under the frozen policy;
10. instrumentation is noninterfering for output, exception type and message,
    abstraction, RNG state, enumerated global state, repeated execution, and
    final-observable bytes; and
11. the unit receives one explicit terminal state, including every build,
    site, trigger, propagation, witness, equivalence, or infrastructure
    failure.

Function entry, line coverage, finite output agreement, absence of a probe,
MR survival, and zero observable divergence cannot substitute for these
requirements.

## 7. Equivalence and denominator governance

Every viable mutant receives one of four scientific states:

- `CERTIFIED_EQUIVALENT`;
- `CONFIRMED_NON_EQUIVALENT`;
- `EQUIVALENCE_UNRESOLVED`; or
- `EXECUTION_INFRASTRUCTURE_UNRESOLVED`.

Only a machine-verifiable sound certificate over the frozen domain may emit
`CERTIFIED_EQUIVALENT`. Finite replay and lack of divergence cannot certify
equivalence. A stable divergence witness may establish
`CONFIRMED_NON_EQUIVALENT`. Unresolved and infrastructure states remain
explicit and may not be silently deleted or renamed.

V125 development calibration does not create the final mutation-score
denominator. That denominator can be sealed only after independent validation
and later target-mutant execution under separately frozen protocols.

## 8. Development population and stopping rule

V124 identities and the earlier 843-project feasibility population may be
used as development evidence only. They are permanently excluded from future
confirmatory validation and holdout populations.

Before any V125 development execution, D1 must freeze:

- the complete development project population;
- source revisions and trees;
- operator/adapter/project ordering;
- site-ranking seeds;
- per-project and global budgets;
- retry and spare-activation rules; and
- the development stop rule.

The pre-validation gate passes only if development evidence contains:

- at least 12 of the planned 14 variants;
- exactly all 8 families;
- at least 2 source-disjoint valid projects per admitted variant;
- at least 24 exact-site development-valid units; and
- zero noninterference failures among admitted units.

If this gate fails after the frozen queue or budget is exhausted, V125 stops
at `V125_OPERATOR_SYSTEM_REDESIGN_DEVELOPMENT_BLOCKED`. No byte-new adapter,
new project, reordered queue, increased budget, or relaxed evidence condition
is authorized in the same experiment.

## 9. Independent validation

Validation is forbidden until the development gate passes and the following
bytes are frozen together:

- abstract contracts;
- executable adapters and generator;
- site-ranking and selection policy;
- witnesses, probes, checkpoints, abstraction, tolerance, and repeats;
- build and environment locks;
- validation identities and order; and
- validation budgets and stopping rules.

Validation runs once on source-disjoint identities not used in V124, the 843
project feasibility population, or V125 development. Validation results may
not feed back into contracts, adapters, sites, witnesses, or budgets.

Gate B passes only with:

- at least 12 validated variants;
- exactly all 8 families; and
- at least 36 valid validation units.

The planned full-cohort target of 14 variants/8 families/42 units is reported
separately and must never replace or be merged with the 12/8/36 minimum gate.

## 10. Role boundaries

- **P12:** freezes and audits the V125 contract, evidence inputs, gates, and
  handoffs. It does not author scientific execution outcomes.
- **D1:** implements and executes the redesign without reading D2, MR outcomes,
  target-mutant outcomes, or confirmatory holdout outcomes.
- **D2:** remains sealed with `open_count=0` and `operator_mapping_count=0`.
- **MR:** remains stopped; no gateway, provider, B0/B1, or prompt work is part
  of V125.

No target mutant, mutation score, D2 mapping, real-fault comparison, or MT
execution is authorized by this specification.

## 11. Required artifacts

P12 must emit a self-contained V125 contract package containing:

- V124 intake receipt and independently recomputed counts;
- redesign amendment and decision record;
- abstract-operator schema;
- executable-adapter schema;
- per-unit evidence schema;
- equivalence-state policy;
- development and validation population policies;
- development and Gate-B evaluators;
- exclusion registries;
- append-only ledger;
- manifest, handoff, SHA256SUMS, and clean-clone verifier; and
- negative tests for project special-casing, outcome-dependent adapter
  selection, validation leakage, finite-replay equivalence, missing
  propagation evidence, line-only trigger evidence, denominator inflation,
  and floor lowering.

D1 must subsequently emit byte-new implementations and ledgers bound to this
package. Every failed unit remains part of the evidence package.

## 12. Decision outcomes

### Strong continuation

If independent validation reaches 12/8/36, P12 may separately audit and decide
whether to grant `CORE_OPERATORS_FROZEN` and authorize target-mutant work.

### Qualified continuation

If development or validation reaches at least 8 variants/5 families/24 valid
units but misses 12/8/36, the result supports only a constrained cross-project
semantic-mutation system. It does not grant `CORE_OPERATORS_FROZEN`; a paper
scope amendment is required before further scientific execution.

### Stop and narrow

If the final breadth remains at or below 5 variants/3 families, operator
expansion stops. The admissible paper contribution becomes the auditable
method, failure atlas, equivalence governance, and applicability boundaries,
not a mature general semantic-mutation system.

## 13. Initial implementation lineages

The P12 coordinator should independently resolve and verify the reported V124
contract lineage before creating a new V125 branch. The D1 executor should
independently resolve and verify the reported blocked commit
`9d01626a3551a331469f7d3e0953632f22b0aea5` before consuming the V125 package.

Recommended branch names:

- P12: `codex/p12-v124-blocked-intake-and-v125-redesign-contract`;
- D1: `codex/p12-v125-two-layer-operator-system`.

Runtime discovery of a different authoritative full commit must be recorded
and fail closed rather than guessed. No force-push, history rewrite, or
in-place modification of V124/D124 artifacts is permitted.

