# D1 V125 Two-Layer Operator System Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement and execute one bounded, byte-new D1 two-layer semantic-operator development experiment under the P12 V125 contract, stopping before validation.

**Architecture:** D1 keeps all V124 bytes immutable, vendors the P12 V125 contract, defines 14 project-neutral abstract semantic operators, and implements generic AST/data-flow adapters under `v125/gen/two_layer_v1/`. A frozen development queue is executed once; a pure evaluator recomputes the 12-variant/8-family/24-unit development gate and emits either a blocked handoff or a pass-pending-P12-validation-authorization handoff.

**Tech Stack:** Python 3 standard library, `ast`, JSON/JSONL, SHA-256, `unittest`, source-locked Python project environments.

---

## Execution lineage and baseline

- Repository: `meng004/P12-D1-Staging-private`
- Base branch: `codex/p12-v124-generator-site-witness-redesign`
- Base commit: `9d01626a3551a331469f7d3e0953632f22b0aea5`
- Work branch: `codex/p12-v125-two-layer-operator-system`
- P12 contract repository: `meng004/P12-Defect4MR`
- P12 contract branch:
  `codex/p12-v124-blocked-intake-and-v125-redesign-contract`
- P12 contract commit: `912e4daf2e4a3307ab482b99c7729de13cca0346`
- Required P12 state:
  `V125_OPERATOR_SYSTEM_REDESIGN_CONTRACT_FROZEN_PENDING_D1_EXECUTION`

Observed clean-worktree baseline at the exact D1 base commit:

- `python3 v124/verify_v5_1_3_development_blocked.py`: PASS;
- current D124-10/v5.1.3 focused tests: PASS;
- complete historical `v124/tests`: 37 tests, 31 pass, 2 fail, 4 error;
- the six failures are obsolete early D124-0/v5.1.1/v5.1.2 assertions contradicted
  by later append-only V124 states, and their bytes must not be edited by V125.

V125 execution may proceed only after the user explicitly approves retaining
those six tests as a named pre-existing baseline. Every V125 commit must prove
that it introduces no additional failure beyond that exact list.

### Task 0: Record the baseline and freeze the V125 start event

**Files:**
- Create: `v125/amendments/D125-0-V125-CONTRACT-INTAKE.json`
- Create: `v125/reports/D125-0-BASELINE.json`
- Create: `v125/ledgers/d125-events.jsonl`
- Create: `v125/tests/test_d125_baseline.py`

- [ ] Record the exact six pre-existing failures by fully qualified test name,
  base commit, command, stdout hash, and stderr hash.
- [ ] Test that a seventh failure blocks every V125 gate.
- [ ] Test that changing any V124 tracked byte blocks intake.
- [ ] Append the first D125 event with no scientific result fields.
- [ ] Run the D124-10 verifier, focused V124 tests, and new baseline tests.
- [ ] Commit as `governance(v125): freeze D1 baseline and start event`.

### Task 1: Vendor and mechanically verify the P12 contract

**Files:**
- Create: `v125/input/p12-v125-contract/`
- Create: `v125/intake/V125-CONTRACT-INTAKE-RECEIPT.json`
- Create: `v125/intake/verify_p12_v125.py`
- Create: `v125/tests/test_d125_contract_intake.py`

- [ ] Write failing tests for the full P12 commit, manifest, SHA256SUMS,
  handoff state, amendment chain, six contract records, five K0–K4 records,
  schemas, registries, and authorization flags.
- [ ] Verify that P12 `scripts/holdout/verify_v125.py` passes before vendoring.
- [ ] Vendor the credential-free `data/holdout/v125/` payload byte-for-byte.
- [ ] Independently recompute every raw and canonical hash without trusting a
  stored PASS result.
- [ ] Reject any payload with validation authorization, core freeze, D2 open,
  D2 mapping, target-mutant, MR, MT, SMS, or RFDS authorization.
- [ ] Commit as `intake(v125): verify P12 redesign contract`.

### Task 2: Freeze the 14 abstract semantic-operator records

**Files:**
- Create: `v125/contracts/abstract-operators.json`
- Create: `v125/contracts/build_abstract_operators.py`
- Create: `v125/tests/test_d125_abstract_operators.py`

- [ ] Derive the exact 14 variant and 8 family identities from
  `v124/reports/D124-7-DENOMINATOR-RECONCILIATION.json` and cross-check them
  against the P12 contract.
- [ ] For each variant freeze semantic quantity, applicability preconditions,
  local effect, propagation obligation, final observable, abstraction,
  tolerance, terminal semantics, invalid cases, equivalence risks, and allowed
  generic adapter identifiers.
- [ ] Reject project/package names, repository identities, commits, paths,
  symbols, prior outcomes, and preferred successful sites anywhere in an
  abstract record.
- [ ] Validate all records with
  `ABSTRACT_SEMANTIC_OPERATOR.schema.json`.
- [ ] Build twice in separate temporary directories and require byte identity.
- [ ] Commit as `contract(v125): freeze abstract semantic operators`.

### Task 3: Implement the byte-new generic adapter core with TDD

**Files:**
- Create: `v125/gen/two_layer_v1/__init__.py`
- Create: `v125/gen/two_layer_v1/model.py`
- Create: `v125/gen/two_layer_v1/registry.py`
- Create: `v125/gen/two_layer_v1/site_selection.py`
- Create: `v125/gen/two_layer_v1/rewrites.py`
- Create: `v125/gen/two_layer_v1/instrumentation.py`
- Create: `v125/gen/two_layer_v1/propagation.py`
- Create: `v125/gen/two_layer_v1/noninterference.py`
- Create: `v125/gen/two_layer_v1/VERSION_FREEZE.json`
- Create: `v125/tests/test_d125_adapter_core.py`

- [ ] Write and observe failing tests for generic structural matching,
  deterministic ranking, unique single-node rewriting, exact-node probes,
  ordered local traces, propagation checkpoints, final observables, and
  seven-dimension noninterference.
- [ ] Implement only enough production code to pass each test, one behavior at
  a time.
- [ ] Reject every project/package/path/symbol/commit special case in adapter
  source and serialized records.
- [ ] Reject site changes after a witness failure and any adapter order derived
  from runtime outcomes.
- [ ] Reject missing local probes, incomplete traces, missing propagation,
  unserializable values, multi-site rewrites, empty rewrites, parse failures,
  compile failures, and mutation attribution ambiguity.
- [ ] Freeze the package hash only after all adapter-core tests pass.
- [ ] Commit as `feat(v125): implement generic two-layer adapter core`.

### Task 4: Bind all 14 variants to generic adapters

**Files:**
- Create: `v125/gen/two_layer_v1/adapters/conservation.py`
- Create: `v125/gen/two_layer_v1/adapters/convergence_target.py`
- Create: `v125/gen/two_layer_v1/adapters/invariance_transform.py`
- Create: `v125/gen/two_layer_v1/adapters/matrix_symmetry.py`
- Create: `v125/gen/two_layer_v1/adapters/numerical_stability.py`
- Create: `v125/gen/two_layer_v1/adapters/order_rank.py`
- Create: `v125/gen/two_layer_v1/adapters/range_bounds.py`
- Create: `v125/gen/two_layer_v1/adapters/roundtrip_inverse.py`
- Create: `v125/gen/two_layer_v1/adapters/__init__.py`
- Create: `v125/tests/test_d125_variant_adapters.py`

- [ ] Write one minimal synthetic positive and at least one negative structural
  fixture per variant before implementing its adapter.
- [ ] Require every adapter to identify its abstract variant and no project.
- [ ] Require all 14 variants and all 8 families to be represented in the
  registry before any real development execution.
- [ ] Run cross-adapter ambiguity tests and reject a site if multiple adapters
  claim the same mutation node without a frozen structural tie-break.
- [ ] Commit each family adapter after its red-green cycle; make a final
  registry commit only after 14/8 structural coverage is complete.

### Task 5: Implement public-API witness and per-unit evidence validation

**Files:**
- Create: `v125/witness/public_api.py`
- Create: `v125/witness/contracts.py`
- Create: `v125/witness/run_pair.py`
- Create: `v125/evidence/unit.py`
- Create: `v125/tests/test_d125_witness_and_unit_evidence.py`

- [ ] Test that private mutation symbols may be sites but never witness APIs.
- [ ] Test public API → exact node → local trace → propagation checkpoint →
  final observable as one complete evidence chain.
- [ ] Test deterministic repeated execution and all seven noninterference
  dimensions using real subprocesses and frozen seeds.
- [ ] Emit only the four governed equivalence states; finite equality and
  zero divergence must produce `EQUIVALENCE_UNRESOLVED`, never
  `CERTIFIED_EQUIVALENT`.
- [ ] Mark every development record `gate_b_admissible=false`.
- [ ] Commit as `feat(v125): enforce exact public witness evidence`.

### Task 6: Freeze the complete development population and zero-result checkpoint

**Files:**
- Create: `v125/calibration/DEVELOPMENT-POPULATION-FREEZE.json`
- Create: `v125/calibration/DEVELOPMENT-ORDER.json`
- Create: `v125/calibration/DEVELOPMENT-BUDGET.json`
- Create: `v125/calibration/DEVELOPMENT-ZERO-RESULT-CHECKPOINT.json`
- Create: `v125/registries/confirmatory-exclusions.json`
- Create: `v125/tests/test_d125_development_freeze.py`

- [ ] Freeze complete project identities, commits, trees, variant-adapter-
  project order, site seed, per-project/global budgets, retries, spares,
  build profiles, and stopping rule before the first real unit.
- [ ] Carry V124 and all 843 H17/H18 identities into the permanent
  no-confirmatory-reuse registry.
- [ ] Reject missing, duplicate, alias-hidden, reordered, or post-result-added
  identities.
- [ ] Emit a hash-bound checkpoint proving zero D125 unit results existed at
  freeze time.
- [ ] Commit as `freeze(v125): seal bounded development execution`.

### Task 7: Execute the full frozen development queue

**Files:**
- Create: `v125/calibration/run_development.py`
- Create: `v125/ledgers/development-units.jsonl`
- Create: `v125/ledgers/development-events.jsonl`
- Create: `v125/checkpoints/`

- [ ] Execute strictly in frozen order with a single-executor lock.
- [ ] Give every unit exactly one terminal state and preserve raw build,
  witness, trace, propagation, noninterference, and equivalence evidence.
- [ ] Never change adapters, sites, projects, retries, spares, or budgets after
  an outcome is available.
- [ ] Write content-addressed resumable checkpoints without resetting order or
  budgets.
- [ ] Complete or exhaust the full frozen queue; do not silently cap by
  favorable breadth.
- [ ] Commit durable checkpoints and the final ledger separately.

### Task 8: Recompute the development gate and export the terminal package

**Files:**
- Create: `v125/reports/DEVELOPMENT-FAILURE-ATLAS.json`
- Create: `v125/reports/DEVELOPMENT-GATE.json`
- Create: `v125/dist/MANIFEST.json`
- Create: `v125/dist/HANDOFF.json`
- Create: `v125/dist/SHA256SUMS`
- Create: `v125/verify_development.py`
- Create: `v125/tests/test_d125_terminal_gate.py`

- [ ] Independently recompute variants, families, source-disjoint projects,
  valid units, noninterference failures, and every failure class from raw
  records.
- [ ] Pass only with at least 12 variants, exactly 8 families, at least two
  source-disjoint valid projects per admitted variant, at least 24 valid
  units, and zero admitted noninterference failures.
- [ ] If PASS, stop at
  `V125_OPERATOR_SYSTEM_REDESIGN_DEVELOPMENT_GATE_PASS_PENDING_P12_VALIDATION_AUTHORIZATION`.
- [ ] If FAIL, stop at
  `V125_OPERATOR_SYSTEM_REDESIGN_DEVELOPMENT_BLOCKED`.
- [ ] In both outcomes keep validation authorization false, core freeze false,
  D2 sealed and unmapped, target-mutant authorization false, and MR/MT/SMS/RFDS
  authorization false.
- [ ] Verify from a clean clone, alternate cwd/TMPDIR, and one-byte tamper.
- [ ] Commit and push the terminal package.

## Hard stop

This plan never executes validation. It never creates another adapter version
after development outcomes. It never opens D2 or resumes MR. Any continuation
after Task 8 requires a new P12 intake and explicit authorization.

