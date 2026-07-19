# P12 V125 Two-Layer Operator Contract Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Freeze and deliver a content-addressed V125 contract that authorizes one bounded D1 two-layer semantic-operator redesign without authorizing validation, target mutants, D2 mapping, MR work, or MT execution.

**Architecture:** P12 consumes the accepted V124 blocked intake at `b50cbb286cc3a6f3898cfdf2e6b8c3c678fe3f41`, derives the 14-variant/8-family denominator from the retained D1 evidence, and appends byte-new V125 schemas, policies, evaluators, ledgers, and a mechanical handoff. The contract separates abstract semantic mechanisms from generic executable adapters and makes both the development gate and the later validation gate independently recomputable.

**Tech Stack:** Python 3 standard library, JSON/JSONL, SHA-256 canonical hashing, `unittest`, existing P12 holdout verifier conventions.

---

## Execution lineage

- Repository: `meng004/P12-Defect4MR`
- Resume branch: `codex/p12-v124-d1-v5_1_3-blocked-intake`
- Resume commit: `b50cbb286cc3a6f3898cfdf2e6b8c3c678fe3f41`
- Create branch: `codex/p12-v125-two-layer-operator-redesign-contract`
- Required input state:
  `V124_OPERATOR_REDESIGN_DEVELOPMENT_BLOCKED_ACCEPTED_V125_SCIENTIFIC_REDESIGN_REQUIRED`
- Required terminal state:
  `V125_OPERATOR_SYSTEM_REDESIGN_CONTRACT_FROZEN_PENDING_D1_EXECUTION`

The implementation must fail closed if the resume commit, K0–K5 package,
14-variant denominator, V124 failure counts, or byte-preservation checks do
not reproduce exactly.

### Task 1: Establish the V125 append-only boundary

**Files:**
- Create: `data/holdout/v123/v125/AMENDMENT-V125-001.json`
- Create: `data/holdout/v123/v125/V124-INTAKE-BINDING.json`
- Create: `tools/holdout/v125/contract.py`
- Create: `tools/holdout/v125/__init__.py`
- Create: `tests/holdout/test_v125_contract_boundary.py`

- [ ] **Step 1: Write the failing ancestry and intake tests**

```python
class V125BoundaryTests(unittest.TestCase):
    def test_exact_resume_commit_is_bound(self):
        record = load_json("data/holdout/v123/v125/V124-INTAKE-BINDING.json")
        self.assertEqual(
            record["producer_commit"],
            "b50cbb286cc3a6f3898cfdf2e6b8c3c678fe3f41",
        )

    def test_v124_terminal_is_required(self):
        self.assertEqual(
            validate_v124_binding(repo_root()),
            "V124_OPERATOR_REDESIGN_DEVELOPMENT_BLOCKED_ACCEPTED_"
            "V125_SCIENTIFIC_REDESIGN_REQUIRED",
        )

    def test_prior_v124_delivery_bytes_are_unchanged(self):
        verify_sha256sums(
            "data/holdout/v123/v124/d1_v5_1_3_blocked_intake/SHA256SUMS"
        )
```

- [ ] **Step 2: Run the boundary tests and observe failure**

Run:

```bash
python3 -m unittest tests.holdout.test_v125_contract_boundary -v
```

Expected: import or file-not-found failure for `tools.holdout.v125` and the
new V125 binding files.

- [ ] **Step 3: Implement canonical binding validation**

`tools/holdout/v125/contract.py` must expose the constants
`RESUME_COMMIT` and `REQUIRED_V124_STATE`, plus four typed functions named
`canonical_sha256(value)`, `load_json(path)`, `verify_sha256sums(path)`, and
`validate_v124_binding(root)`. The constants are:

```python
RESUME_COMMIT = "b50cbb286cc3a6f3898cfdf2e6b8c3c678fe3f41"
REQUIRED_V124_STATE = (
    "V124_OPERATOR_REDESIGN_DEVELOPMENT_BLOCKED_ACCEPTED_"
    "V125_SCIENTIFIC_REDESIGN_REQUIRED"
)
```

`validate_v124_binding()` must read K0–K5, independently recompute their
self-hashes, verify the imported D1 distribution, and return the required
state only when all byte and count checks pass. It must never trust a stored
top-level PASS field.

- [ ] **Step 4: Write V125-001 before any redesign artifact**

The amendment must set exactly:

```json
{
  "amendment_id": "V125-001",
  "scientific_impact": true,
  "changes_operator_architecture": true,
  "rewrites_historical_evidence": false,
  "v124_development_evidence_role": "DEVELOPMENT_ONLY",
  "validation_execution_authorized": false,
  "target_mutant_generation_authorized": false,
  "d2_mapping_authorized": false,
  "mr_work_authorized": false,
  "mt_execution_authorized": false,
  "core_operators_frozen": false
}
```

Add the normal canonical self-hash and predecessor amendment binding used by
the repository. `V124-INTAKE-BINDING.json` must bind the full producer commit,
all K0–K5 raw hashes, the imported distribution manifest, and the original
D1 producer commit `9d01626a3551a331469f7d3e0953632f22b0aea5`.

- [ ] **Step 5: Run tests and commit**

Expected: the focused tests pass and a one-byte change to any K0–K5 file is
rejected.

```bash
git add data/holdout/v123/v125 tools/holdout/v125 \
  tests/holdout/test_v125_contract_boundary.py
git commit -m "governance(v125): bind blocked V124 intake"
```

### Task 2: Define the two-layer schemas

**Files:**
- Create: `schemas/holdout/v125/abstract-operator.schema.json`
- Create: `schemas/holdout/v125/executable-adapter.schema.json`
- Create: `schemas/holdout/v125/unit-evidence.schema.json`
- Create: `schemas/holdout/v125/equivalence-state.schema.json`
- Create: `tests/holdout/test_v125_schemas.py`

- [ ] **Step 1: Write schema-negative tests**

Define `PROJECT_SPECIFIC_FIELDS` exactly as below and add six concrete tests
named `test_abstract_operator_rejects_project_identity`,
`test_adapter_rejects_project_name_guard`,
`test_unit_rejects_line_only_trigger_evidence`,
`test_unit_rejects_missing_propagation_checkpoint`,
`test_equivalence_rejects_finite_replay_as_certificate`, and
`test_equivalence_states_are_exhaustive_and_exclusive`. Each test must pass a
minimal otherwise-valid record to the repository's schema validator, mutate
only the named prohibited property, and assert the stable V125 validation
error code.

```python
PROJECT_SPECIFIC_FIELDS = {
    "project_id", "repository", "commit", "source_path", "symbol"
}
```

- [ ] **Step 2: Run the schema tests and observe failure**

Run:

```bash
python3 -m unittest tests.holdout.test_v125_schemas -v
```

Expected: schemas are absent.

- [ ] **Step 3: Implement the abstract-operator schema**

Require these fields with `additionalProperties: false`:

```json
[
  "family_id",
  "variant_id",
  "semantic_quantity",
  "applicability_preconditions",
  "intended_local_effect",
  "propagation_obligation",
  "final_observable",
  "semantic_abstraction",
  "tolerance_semantics",
  "terminal_semantics",
  "known_invalid_cases",
  "known_equivalence_cases",
  "adapter_ids",
  "contract_sha256"
]
```

Explicitly reject the project-specific fields listed in the tests.

- [ ] **Step 4: Implement the executable-adapter schema**

Require:

```json
[
  "adapter_id",
  "variant_id",
  "ast_shape",
  "dataflow_shape",
  "rewrite_rule",
  "static_guards",
  "site_ranking_policy_sha256",
  "public_api_certificate_schema_sha256",
  "exact_node_probe_schema_sha256",
  "local_trace_schema_sha256",
  "propagation_checkpoint_schema_sha256",
  "final_observable_schema_sha256",
  "build_profile_schema_sha256",
  "witness_schema_sha256",
  "noninterference_schema_sha256",
  "adapter_sha256"
]
```

The schema and validator must reject guards containing a project/package
identity, commit hash, source path, concrete symbol, or an outcome field.

- [ ] **Step 5: Implement unit and equivalence schemas**

`unit-evidence.schema.json` must require all eleven per-unit obligations from
the approved V125 specification, including exact mutation-node identity,
runtime site identity, ordered local-value hashes, propagation evidence,
final-observable bytes, repeated-run evidence, and seven-dimension
noninterference evidence.

`equivalence-state.schema.json` must allow only:

```json
[
  "CERTIFIED_EQUIVALENT",
  "CONFIRMED_NON_EQUIVALENT",
  "EQUIVALENCE_UNRESOLVED",
  "EXECUTION_INFRASTRUCTURE_UNRESOLVED"
]
```

`CERTIFIED_EQUIVALENT` requires a machine-checker artifact, frozen domain,
environment binding, replayable proof inputs, and successful independent
verification. Finite replay alone is structurally invalid.

- [ ] **Step 6: Run tests and commit**

```bash
git add schemas/holdout/v125 tests/holdout/test_v125_schemas.py
git commit -m "schema(v125): separate semantic operators and adapters"
```

### Task 3: Derive and freeze the 14-variant contract without hand copying

**Files:**
- Create: `tools/holdout/v125/derive_contract.py`
- Create: `data/holdout/v123/v125/OPERATOR-DENOMINATOR.json`
- Create: `data/holdout/v123/v125/ABSTRACT-OPERATOR-CONTRACTS.json`
- Create: `data/holdout/v123/v125/ADAPTER-AUTHORING-POLICY.json`
- Create: `tests/holdout/test_v125_contract_derivation.py`

- [ ] **Step 1: Write denominator reconciliation tests**

```python
def test_denominator_is_source_derived(self):
    observed = derive_denominator(repo_root())
    self.assertEqual(len(observed["variants"]), 14)
    self.assertEqual(len({x["family_id"] for x in observed["variants"]}), 8)

def test_no_variant_is_silently_removed(self):
    denominator = derive_denominator(repo_root())
    self.assertEqual(
        {x["variant_id"] for x in denominator["variants"]},
        set(load_json(D124_DENOMINATOR)["variant_ids"]),
    )

```

Add two further tests that flatten every derived contract/policy key and
value, reject every `PROJECT_SPECIFIC_FIELDS` key, and reject any normalized
project identity from the bound exclusion registry.

- [ ] **Step 2: Run and observe failure because derivation is absent**

- [ ] **Step 3: Implement source-derived construction**

`derive_contract.py` must derive identities from:

```text
dist/holdout/v124/d1-v5_1_3-development-blocked/
  v124/reports/D124-7-DENOMINATOR-RECONCILIATION.json
```

It must cross-check the same identities against the V5.1.3 atlas and ledger.
It must fail if the sources disagree, if any identity is duplicated, or if
the result is not exactly 14 variants and 8 families. It must never copy
V124 outcomes, project identities, paths, symbols, or successful-site choices
into an abstract contract.

- [ ] **Step 4: Freeze the adapter authoring policy**

The policy must state:

```json
{
  "multiple_generic_adapters_per_variant_allowed": true,
  "project_specific_adapters_allowed": false,
  "outcome_dependent_adapter_selection_allowed": false,
  "structural_ast_and_dataflow_guards_only": true,
  "site_order_frozen_before_runtime_outcomes": true,
  "witness_failure_allows_site_switch": false,
  "validation_feedback_to_design_allowed": false
}
```

- [ ] **Step 5: Rebuild twice and require byte identity**

Run the builder twice in two temporary directories. Expected: identical raw
SHA-256 for all three generated JSON artifacts.

- [ ] **Step 6: Commit**

```bash
git add tools/holdout/v125/derive_contract.py \
  data/holdout/v123/v125/OPERATOR-DENOMINATOR.json \
  data/holdout/v123/v125/ABSTRACT-OPERATOR-CONTRACTS.json \
  data/holdout/v123/v125/ADAPTER-AUTHORING-POLICY.json \
  tests/holdout/test_v125_contract_derivation.py
git commit -m "contract(v125): freeze source-derived operator denominator"
```

### Task 4: Freeze development and validation population governance

**Files:**
- Create: `data/holdout/v123/v125/DEVELOPMENT-POPULATION-POLICY.json`
- Create: `data/holdout/v123/v125/VALIDATION-POPULATION-POLICY.json`
- Create: `data/holdout/v123/v125/EXCLUSION-REGISTRY-BINDING.json`
- Create: `tests/holdout/test_v125_population_governance.py`

- [ ] **Step 1: Write fail-closed population tests**

Add five tests named
`test_v124_and_843_identities_are_development_only`,
`test_prior_identity_cannot_enter_validation`,
`test_development_population_must_freeze_before_execution`,
`test_validation_population_must_freeze_after_dev_pass_before_execution`, and
`test_validation_result_cannot_change_contract_or_adapter_hash`. Each test
must mutate one temporary record and assert the corresponding stable V125
population-governance error.

- [ ] **Step 2: Freeze policy constants**

Development policy:

```json
{
  "v124_and_h17_h18_role": "DEVELOPMENT_AND_FEASIBILITY_ONLY",
  "confirmatory_reuse": false,
  "freeze_before_execution": [
    "project_population", "source_revisions", "git_trees",
    "variant_adapter_project_order", "site_ranking_seed",
    "per_project_budget", "global_budget", "retry_rules",
    "spare_activation_rules", "stop_rule"
  ]
}
```

Validation policy:

```json
{
  "source_disjoint_from_v124_h17_h18_and_v125_development": true,
  "single_execution_only": true,
  "post_validation_tuning_allowed": false,
  "minimum_gate": {"variants": 12, "families": 8, "units": 36},
  "planned_full_cohort": {"variants": 14, "families": 8, "units": 42}
}
```

- [ ] **Step 3: Bind existing exclusion registries by path and raw hash**

The binding must include every V124 development identity and the 843 H17/H18
identities without importing scientific outcomes into later validation. A
missing, duplicated, alias-hidden, or hash-mismatched identity blocks the
contract.

- [ ] **Step 4: Run tests and commit**

```bash
git add data/holdout/v123/v125/*POPULATION-POLICY.json \
  data/holdout/v123/v125/EXCLUSION-REGISTRY-BINDING.json \
  tests/holdout/test_v125_population_governance.py
git commit -m "governance(v125): freeze development and validation isolation"
```

### Task 5: Implement independent development and Gate-B evaluators

**Files:**
- Create: `tools/holdout/v125/gates.py`
- Create: `data/holdout/v123/v125/GATE-CONTRACT.json`
- Create: `tests/holdout/test_v125_gates.py`

- [ ] **Step 1: Write red tests for every denominator attack**

Add nine tests named
`test_development_gate_requires_12_variants`,
`test_development_gate_requires_exactly_8_families`,
`test_development_gate_requires_two_disjoint_projects_each`,
`test_development_gate_requires_24_valid_units`,
`test_development_gate_rejects_any_admitted_ni_failure`,
`test_validation_gate_requires_12_8_36`,
`test_calibration_units_never_count_toward_gate_b`,
`test_14_8_42_does_not_replace_12_8_36`, and
`test_stored_pass_is_ignored`. Build the passing fixtures mechanically from
the source-derived denominator, then remove or alter exactly one required
fact per test and assert a BLOCKED result with the named failed condition.

- [ ] **Step 2: Implement pure recomputation functions**

```python
DEV_MIN_VARIANTS = 12
DEV_REQUIRED_FAMILIES = 8
DEV_MIN_PROJECTS_PER_VARIANT = 2
DEV_MIN_VALID_UNITS = 24
VALIDATION_MIN_VARIANTS = 12
VALIDATION_REQUIRED_FAMILIES = 8
VALIDATION_MIN_VALID_UNITS = 36

```

Implement two pure typed functions named `evaluate_development(units,
denominator)` and `evaluate_validation(units, denominator)`, each returning a
JSON-serializable dict with recomputed counts, failed conditions, input hashes,
and `result` equal to `PASS` or `BLOCKED`.

Both functions must derive unique variants, families, projects, and valid
units from raw records. They must reject unknown variants, duplicate unit
identities, project aliases, non-source-disjoint evidence, missing exact-site
or propagation proof, and any unit marked calibration when evaluating Gate B.

- [ ] **Step 3: Add the three decision bands**

The evaluator may report:

```text
STRONG_CONTINUATION: validation >= 12/8/36
QUALIFIED_CONTINUATION: evidence >= 8 variants/5 families/24 units
STOP_AND_NARROW: final breadth <= 5 variants/3 families
```

Only `STRONG_CONTINUATION` is eligible for a later independent
`CORE_OPERATORS_FROZEN` decision. This contract itself grants no such state.

- [ ] **Step 4: Run tests and commit**

```bash
git add tools/holdout/v125/gates.py \
  data/holdout/v123/v125/GATE-CONTRACT.json \
  tests/holdout/test_v125_gates.py
git commit -m "gate(v125): freeze development and validation thresholds"
```

### Task 6: Add attack suite and boundary verifier

**Files:**
- Create: `data/holdout/v123/v125/ATTACKS.json`
- Create: `scripts/holdout/verify_v125_contract.py`
- Create: `tests/holdout/test_v125_attacks.py`

- [ ] **Step 1: Encode the required attacks**

`ATTACKS.json` and tests must cover at least:

1. project name embedded in an adapter;
2. passing site prioritized using witness outcome;
3. validation identity reused from V124 or the 843 population;
4. finite replay renamed `CERTIFIED_EQUIVALENT`;
5. missing propagation evidence with final output under tolerance;
6. function-entry or line-only coverage substituted for exact-node evidence;
7. calibration unit counted in Gate B;
8. 12/8/36 floor lowered or replaced by 14/8/42;
9. failed unit deleted from a ledger;
10. D2, MR, target-mutant, kill, SMS, or RFDS data imported;
11. `CORE_OPERATORS_FROZEN=true` written by the contract stage; and
12. V124 file changed by one byte.

- [ ] **Step 2: Implement `verify_v125_contract.py`**

The verifier must recompute all self-hashes, raw hashes, amendment-chain
membership, K0–K5 binding, 14/8 denominator, schema validity, exclusion
bindings, gate constants, attack rejection, and authorization flags. It must
run from a clean clone and alternate cwd/TMPDIR using only repository-relative
paths.

- [ ] **Step 3: Prove every attack transitions PASS → BLOCKED → PASS**

Do not merely assert that an attack detector exists. Each test must tamper a
temporary copy, observe the named block, restore the byte, and observe PASS.

- [ ] **Step 4: Run tests and commit**

```bash
python3 -m unittest tests.holdout.test_v125_attacks -v
python3 scripts/holdout/verify_v125_contract.py
git add data/holdout/v123/v125/ATTACKS.json \
  scripts/holdout/verify_v125_contract.py \
  tests/holdout/test_v125_attacks.py
git commit -m "test(v125): enforce redesign scientific boundaries"
```

### Task 7: Package the D1 mechanical handoff

**Files:**
- Create: `data/holdout/v123/v125/MANIFEST.json`
- Create: `data/holdout/v123/v125/HANDOFF.json`
- Create: `data/holdout/v123/v125/SHA256SUMS`
- Create: `dist/holdout/v125/operator-redesign-contract/`
- Create: `docs/holdout/V125-OPERATOR-REDESIGN-CONTRACT-HANDOFF.md`
- Create: `tests/holdout/test_v125_handoff.py`

- [ ] **Step 1: Write handoff tests before building the package**

Require the handoff to bind:

- P12 repository and branch, plus `producer_evidence_commit` equal to the
  commit immediately preceding the deterministic package-build commit; the
  final delivery commit is reported externally and must contain that evidence
  commit as its first parent;
- V124 intake commit and all K0–K5 artifact hashes;
- D1 blocked producer commit;
- amendment, denominator, contract, schema, population, equivalence, gate,
  ledger, and attack hashes;
- `d1_execution_authorized=true`;
- `validation_execution_authorized=false`;
- `target_mutant_generation_authorized=false`;
- `core_operators_frozen=false`;
- `d2_open_count=0`;
- `operator_mapping_count=0`; and
- terminal state
  `V125_OPERATOR_SYSTEM_REDESIGN_CONTRACT_FROZEN_PENDING_D1_EXECUTION`.

- [ ] **Step 2: Build a deterministic distribution**

Copy only the contract inputs and verifier needed by D1. Include no D2
identities or outcomes, MR artifacts, target-mutant outcomes, kill data, SMS,
or RFDS. Build twice and require byte-identical manifest and archive hashes.

- [ ] **Step 3: Verify from a clean clone**

Expected sequence:

```bash
sha256sum -c data/holdout/v123/v125/SHA256SUMS
python3 scripts/holdout/verify_v125_contract.py
python3 -m unittest discover -s tests/holdout -p 'test_v125_*.py' -v
```

Expected: all checks pass, no skipped scientific check, and a one-byte tamper
causes a nonzero exit.

- [ ] **Step 4: Commit and push**

```bash
git add data/holdout/v123/v125 dist/holdout/v125 \
  docs/holdout/V125-OPERATOR-REDESIGN-CONTRACT-HANDOFF.md \
  scripts/holdout/verify_v125_contract.py tests/holdout/test_v125_handoff.py
git commit -m "milestone(v125): freeze two-layer operator redesign contract"
git push -u origin codex/p12-v125-two-layer-operator-redesign-contract
```

## Final stop boundary

Stop immediately after the clean-clone package verifies at:

```text
V125_OPERATOR_SYSTEM_REDESIGN_CONTRACT_FROZEN_PENDING_D1_EXECUTION
```

Do not implement D1 adapters in P12. Do not execute calibration or validation.
Do not generate target mutants. Do not open or map D2. Do not resume MR or MT.
Return the exact delivery commit, archive/manifest/handoff/SHA256SUMS hashes,
verifier result, authorization flags, and D1 consumption path.
