# P3 v3 Minimum Evidence Foundation Alignment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:subagent-driven-development` (recommended) or
> `superpowers:executing-plans` to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Align the existing P3 v3 minimum-evidence implementation with the
frozen non-circular experiment design, including outcome-blind workload
selection, deterministic `E_COMMON`/`E_CONTRACT`, failure-conservative technique
classification, package-role separation, and the frozen P12 missingness
estimand.

**Architecture:** Preserve the proven canonical-JSON, pinned-Git, package,
immutable-ledger, and repeatable-preflight primitives. Deepen the existing
`bridge_and_frames.py` module so it owns every frame/input scientific rule,
strengthen `packages.py` and `run_records.py` at their existing seams, and keep
`evidence.py` as a thin dispatcher with no copied scientific constants. All
validation uses synthetic fixtures; no real P12 reveal, semantic-mutant
construction, MR execution, network collection, or Cursor scientific run occurs.

**Tech Stack:** Python 3.11 standard library, pytest 9, Git subprocesses with
`shell=False`, SHA-256, canonical JSON/JSONL, POSIX durable writes.

## Global Constraints

- Base implementation commit:
  `f4412db15b72d3c94616e79e44181108bc78a5dc`.
- Frozen scientific-plan SHA-256:
  `fea00496801c31ba074aa74742f5e6a77019ffc2e344642122a15462d7443830`.
- Frozen evidence-design SHA-256:
  `7e614e96aac833786d1b29580f8fae7d3f03c6567d7ca94f3e3c017addad2fa9`.
- Governing design path:
  `docs/superpowers/specs/2026-08-08-p3-v3-evidence-foundation-design.md`.
- Baseline on 2026-08-10: `53 passed` under `tests/p3_v3`; this proves only the
  prior implementation, not alignment with the revised design.
- Production remains limited to the existing five modules and thin CLI. Test
  fixtures may be added under `tests/p3_v3/fixtures/`.
- Canonical JSON remains UTF-8, sorted keys, compact separators, no nonfinite
  numbers, and exactly one terminal LF.
- Local Desktop commands use `rtk`. Cursor VM commands do not use `rtk`.
- Every behavior change follows RED -> GREEN and ends in one reviewable commit.
- Development failures may be diagnosed and corrected. They are not scientific
  jobs and do not consume experiment authorization.
- Do not modify P12 data, run live P12 reveal, construct mutants, execute MRs,
  collect network evidence, change the manuscript, create a PR, or merge.
- Do not add a generic schema engine, workflow framework, custom Cursor
  controller, YAML authority, or new production module.

## Existing implementation and required delta

| Existing asset | Decision | Required delta |
|---|---|---|
| `artifacts.py` canonical bytes, hashes, exact types, durable writes | Reuse | Add no scientific rule; only reuse its primitives |
| Pinned bridge and reveal checks | Reuse | Preserve exact Git identity and visible-secret rejection |
| `build_subject_frames` accepting custodian-style feature records | Replace path | Derive public behavior, workload, technique, inputs, and frames from permitted authorities |
| Package manifests and clean materialization | Deepen | Add exact A/B input roles and proposer view exclusion |
| Immutable attempts and phase close | Deepen | Bind atomic row identity, input role, retry ceiling, P12 denominator and estimand |
| Repeatable preflight | Deepen | Add declared capability/resource gates without creating a scientific intent |
| CLI-local protocol and MR rules | Move | Put rules in `bridge_and_frames.py`; CLI delegates only |
| Phase 0 -> Phase 2 synthetic path | Replace | Cover Phase 0 -> Phase 7 artifact chronology and missingness estimand |

---

### Task 1: Rebind protocol authority and remove CLI-owned scientific rules

**Files:**
- Modify: `src/p3_v3/bridge_and_frames.py`
- Modify: `scripts/p3_v3/evidence.py`
- Modify: `tests/p3_v3/test_cli.py`
- Modify: `tests/p3_v3/test_synthetic_phase_path.py`

**Interfaces:**
- Produces: `validate_protocol(protocol, expected_plan_sha256,
  expected_design_sha256) -> dict[str, Any]`.
- Produces: `validate_mr_inventory(inventory) -> dict[str, Any]`.
- The CLI owns only the two frozen authority digests and delegates validation.

- [ ] **Step 1: Update protocol fixtures and write failing authority tests**

Use this exact protocol top-level schema in test fixtures:

```python
PROTOCOL_KEYS = {
    "schema_version", "scientific_plan_sha256", "evidence_design_sha256",
    "claims_initial_status", "rq_spec_sha256", "claim_ceiling_sha256",
    "p12_contract_sha256", "operator_catalogue_sha256",
    "adapter_registry_sha256", "input_generator_registry_sha256",
    "mr_policy_sha256", "site_policy_sha256", "analysis_spec_sha256",
    "package_policy_sha256", "environment_lock_sha256",
    "profiling_budgets", "behavior_category_order", "technique_order",
    "e_common_count", "e_contract_count", "p12_outcome_states",
    "p12_primary_estimand", "infrastructure_retry_limit", "artifact_sha256",
}
```

Add tests proving one extra key, one missing key, an old authority digest,
`e_common_count != 30`, `e_contract_count != 5`, retry limit other than `3`, or
an altered outcome-state order fails before any output file is written.

- [ ] **Step 2: Run RED**

Run:

```bash
rtk env PYTHONPATH=src /Users/limeng/Papers/P3-SemanticMutation/.venv/bin/python -m pytest tests/p3_v3/test_cli.py tests/p3_v3/test_synthetic_phase_path.py -q
```

Expected: failures show the current four-field protocol and old authority hashes
are still accepted.

- [ ] **Step 3: Implement the protocol and MR validators in the frame module**

Use exact constants:

```python
PROFILING_BUDGETS = {"S": 10, "M": 15, "L": 20}
BEHAVIOR_CATEGORY_ORDER = ["PUBLIC_API", "CLI", "EXAMPLE", "BENCHMARK", "PROJECT_TEST"]
P12_OUTCOME_STATES = [
    "MR_VIOLATION", "MR_SATISFIED",
    "DECLARED_EXCEPTION_OR_TIMEOUT_VIOLATION",
    "SCIENTIFIC_INCONCLUSIVE", "INFRASTRUCTURE_UNRESOLVED",
]
```

`validate_protocol` validates exact keys and types, every referenced SHA-256,
the canonical self-hash, all literal values above, `claims_initial_status ==
"blocked"`, counts `30/5`, primary estimand
`"INTENTION_TO_EVALUATE_LOWER_BOUND"`, and retry limit `3`.

Move `_mr_inventory` unchanged in meaning from the CLI into
`validate_mr_inventory`; retain the exact chronology candidate frame ->
custodian receipt -> final inventory -> portfolios.

- [ ] **Step 4: Make the CLI a pure delegate and run GREEN**

Set:

```python
SCIENTIFIC_PLAN_SHA256 = "fea00496801c31ba074aa74742f5e6a77019ffc2e344642122a15462d7443830"
EVIDENCE_DESIGN_SHA256 = "7e614e96aac833786d1b29580f8fae7d3f03c6567d7ca94f3e3c017addad2fa9"
```

Delete CLI copies of protocol/MR schemas. Run the RED command again; expected:
all selected tests pass.

- [ ] **Step 5: Commit**

```bash
rtk git add src/p3_v3/bridge_and_frames.py scripts/p3_v3/evidence.py tests/p3_v3/test_cli.py tests/p3_v3/test_synthetic_phase_path.py
rtk git commit -m "feat(p3-v3): bind revised protocol authority"
```

### Task 2: Derive the public behavior frame and exact Profiling Workload

**Files:**
- Modify: `src/p3_v3/bridge_and_frames.py`
- Modify: `tests/p3_v3/test_bridge_and_frames.py`
- Create: `tests/p3_v3/fixtures/public_behavior/python.json`
- Create: `tests/p3_v3/fixtures/public_behavior/cmake.json`
- Create: `tests/p3_v3/fixtures/public_behavior/unsupported.json`

**Interfaces:**
- Produces: `validate_adapter_registry(registry, source_root) -> dict`.
- Produces: `build_public_behavior_frame(source_record, declarations,
  adapter_registry) -> dict`.
- Produces: `select_profiling_workload(frame, scale_class) -> dict`.

- [ ] **Step 1: Write failing frame-completeness and selection tests**

Test the frozen adapter IDs:

```python
CONFIRMATORY_ADAPTERS = {
    "PYTHON_PEP517_V1", "CMAKE_CTEST_V1",
    "MESON_TEST_V1", "AUTOTOOLS_MAKECHECK_V1",
}
```

Cover exact registry implementation-path/source hashes, all five category
accounting rows including zero counts, provenance on invalid declarations,
unsupported ecosystems retained as `ADAPTER_UNSUPPORTED`, rejection of public
behavior without provenance, shuffled-input invariance, and no hand-command
fallback.

Create more than 20 executable fixture rows and assert selection:

```python
assert workload["budget"] == 20
assert workload["category_order"] == [
    "PUBLIC_API", "CLI", "EXAMPLE", "BENCHMARK", "PROJECT_TEST"
]
assert max(workload["selected_category_counts"].values()) - min(
    workload["selected_category_counts"].values()
) <= 1
```

Mutating execution success, coverage, technique labels, MR outcomes, or P12
fields must not change selected behavior IDs.

- [ ] **Step 2: Run RED**

```bash
rtk env PYTHONPATH=src /Users/limeng/Papers/P3-SemanticMutation/.venv/bin/python -m pytest tests/p3_v3/test_bridge_and_frames.py -q
```

Expected: imports for the three new functions fail.

- [ ] **Step 3: Implement exact schemas and deterministic selection**

For every executable row compute:

```python
diversity_signature_sha256 = canonical_sha256({
    "category": row["category"],
    "normalized_entrypoint": row["normalized_entrypoint"],
    "sorted_static_dependency_tags": sorted(set(row["static_dependency_tags"])),
    "declared_input_schema_sha256": row["declared_input_schema_sha256"],
    "domain": "P3-PROFILE-DIVERSITY-v1",
})
```

Select one lowest `(diversity_signature_sha256, behavior_id)` row from each
nonempty executable category, then cycle in frozen category order, preferring
unseen diversity signatures and finally lowest remaining `behavior_id`, until
budget `10/15/20` or exhaustion. Keep every unsupported/invalid declaration in
the frame but never silently convert it to an executable row.

- [ ] **Step 4: Run GREEN and mutation cases**

Run the RED command. Expected: all frame/workload tests pass, including injected
outcome invariance and every one-field registry mutation.

- [ ] **Step 5: Commit**

```bash
rtk git add src/p3_v3/bridge_and_frames.py tests/p3_v3/test_bridge_and_frames.py tests/p3_v3/fixtures/public_behavior
rtk git commit -m "feat(p3-v3): derive outcome-blind profiling workload"
```

### Task 3: Classify implementation technique without dropping failures

**Files:**
- Modify: `src/p3_v3/bridge_and_frames.py`
- Modify: `tests/p3_v3/test_bridge_and_frames.py`

**Interfaces:**
- Produces: `classify_technique(workload, profiling_results) -> dict`.
- Produces fields: `lower_scores`, `upper_scores`, `confirmed_tags`,
  `possible_tags`, `primary_technique`, `category_funnel`.

- [ ] **Step 1: Write failing category-balance tests**

Create a fixture in which one category has eight successful scalar rows and a
second category has one successful array row. Assert category-equal scores, not
row-weighted `8/9` versus `1/9`. Add failures to the second category and assert
they remain in `n_c` and widen every `U_t`.

```python
assert profile["lower_scores"]["SCALAR_CONTROL"] == "0.5"
assert profile["lower_scores"]["ARRAY_NUMERICAL"] == "0.5"
```

Use canonical decimal strings rather than binary floats. Add tests for: no
successful row in one selected category -> `TECH_UNCERTAIN`; overlapping
intervals -> `TECH_UNCERTAIN`; one strict `L_t > max(U_q)` winner -> that winner;
no unresolved row -> frozen technique-order tie break.

- [ ] **Step 2: Run RED**

```bash
rtk env PYTHONPATH=src /Users/limeng/Papers/P3-SemanticMutation/.venv/bin/python -m pytest tests/p3_v3/test_bridge_and_frames.py -q
```

- [ ] **Step 3: Implement rational category scores**

Use `fractions.Fraction` internally and serialize normalized decimal strings.
Treat every failed, timed-out, missing-trace, or adapter-uncertain selected row
as unresolved in its original category. A confirmed tag has `L_t > 0`; a
possible tag has `U_t > 0`. `build_subject_frames` must consume only the derived
robust primary label and confirmed vector, never a caller-supplied label.

- [ ] **Step 4: Run GREEN**

Run the RED command. Expected: all tests pass and an injected result-order
permutation produces byte-identical profile output.

- [ ] **Step 5: Commit**

```bash
rtk git add src/p3_v3/bridge_and_frames.py tests/p3_v3/test_bridge_and_frames.py
rtk git commit -m "feat(p3-v3): classify technique with failure bounds"
```

### Task 4: Freeze deterministic generator registry and `E_COMMON`

**Files:**
- Modify: `src/p3_v3/bridge_and_frames.py`
- Modify: `tests/p3_v3/test_bridge_and_frames.py`
- Create: `tests/p3_v3/fixtures/input_generators/registry.json`

**Interfaces:**
- Produces: `validate_input_generator_registry(registry, source_root) -> dict`.
- Produces: `build_common_inputs(source_record, public_frame, registry) -> dict`.
- Produces: `validate_common_inputs_on_fixed_source(inventory, validator) -> dict`.

- [ ] **Step 1: Write failing registry, seed, and no-replacement tests**

Require the exact five `E_COMMON` IDs from the design. Reject a source hash that
does not match the declared implementation path. Assert exactly ordinals
`0..29`, stable payload bytes under shuffled schemas, raw-schema deduplication,
schema assignment `i mod k`, and seed derivation:

```python
seed = int.from_bytes(bytes.fromhex(canonical_sha256({
    "domain": "P3-E-COMMON-SEED-v1",
    "controlled_subject_source_id": source_id,
    "ordinal": ordinal,
}))[:8], "big")
```

Assert project-test bodies/fixtures, contracts, sites, profiling results, patch,
MR, P12, and outcome keys are rejected as generator inputs. A generator failure
must occupy its ordinal as `COMMON_INPUT_INVALID`; zero eligible schemas must
produce 30 `COMMON_INPUT_UNAVAILABLE` rows.

- [ ] **Step 2: Run RED**

```bash
rtk env PYTHONPATH=src /Users/limeng/Papers/P3-SemanticMutation/.venv/bin/python -m pytest tests/p3_v3/test_bridge_and_frames.py -q
```

- [ ] **Step 3: Implement a version-stable digest stream and generator dispatch**

Use SHA-256 blocks rather than `random.Random`:

```python
def _seed_block(seed: int, counter: int) -> bytes:
    return hashlib.sha256(
        b"P3-INPUT-STREAM-v1" + seed.to_bytes(8, "big") + counter.to_bytes(8, "big")
    ).digest()
```

Dispatch only the five registered IDs. Each generator receives canonical schema
bytes and the seed, returns a canonical envelope plus raw payload hash, and has a
stable failure code. The registry binds ID, schema kind, implementation path,
source SHA-256, output schema, and failure code. No model or author fallback is
reachable.

- [ ] **Step 4: Implement fixed-source validity without changing identities**

`validate_common_inputs_on_fixed_source` emits exactly one status for each of
the 30 identities: `COMMON_INPUT_EXECUTABLE`, `COMMON_INPUT_INVALID`, or
`COMMON_INPUT_UNAVAILABLE`. The validator cannot replace a row or modify sites,
contracts, profile, frame, or payload identity.

- [ ] **Step 5: Run GREEN and commit**

```bash
rtk env PYTHONPATH=src /Users/limeng/Papers/P3-SemanticMutation/.venv/bin/python -m pytest tests/p3_v3/test_bridge_and_frames.py -q
rtk git add src/p3_v3/bridge_and_frames.py tests/p3_v3/test_bridge_and_frames.py tests/p3_v3/fixtures/input_generators
rtk git commit -m "feat(p3-v3): freeze common evaluation inputs"
```

### Task 5: Close slot applicability and generate `E_CONTRACT`

**Files:**
- Modify: `src/p3_v3/bridge_and_frames.py`
- Modify: `tests/p3_v3/test_bridge_and_frames.py`

**Interfaces:**
- Produces: `close_slot(slot, canonical_sites, applicability_predicate) -> dict`.
- Produces: `build_contract_inputs(applicable_slot, contract, registry) -> dict`.
- Produces: `verify_slot_chronology(slot_artifacts) -> None`.

- [ ] **Step 1: Write failing two-path state-machine tests**

Assert every slot has exactly one path:

```text
APPLICABILITY_CLOSED_NOT_APPLICABLE
```

or:

```text
SITE_FROZEN -> CONTRACT_FROZEN -> E_CONTRACT_FROZEN
-> PATCH_FROZEN -> CERTIFICATION_WITNESS_SELECTED -> TERMINAL_STATE
```

An inapplicable slot carrying a contract, input, patch, or witness must fail. An
applicable slot missing `E_CONTRACT` before patch must fail. A post-patch witness
whose identity appears in either input inventory must fail.

- [ ] **Step 2: Run RED**

```bash
rtk env PYTHONPATH=src /Users/limeng/Papers/P3-SemanticMutation/.venv/bin/python -m pytest tests/p3_v3/test_bridge_and_frames.py -q
```

- [ ] **Step 3: Implement five fixed contract ordinals**

Each applicable contract names one of the five frozen contract-generator IDs.
Derive ordinals `0..4` from:

```python
canonical_sha256({
    "domain": "P3-E-CONTRACT-SEED-v1",
    "controlled_subject_id": subject_id,
    "slot_id": slot_id,
    "ordinal": ordinal,
})
```

Unsupported domain generation produces five `CONTRACT_INPUT_UNAVAILABLE` rows.
It cannot select a new site, edit the contract, add a generator, or use a manual
witness.

- [ ] **Step 4: Run GREEN and commit**

```bash
rtk env PYTHONPATH=src /Users/limeng/Papers/P3-SemanticMutation/.venv/bin/python -m pytest tests/p3_v3/test_bridge_and_frames.py -q
rtk git add src/p3_v3/bridge_and_frames.py tests/p3_v3/test_bridge_and_frames.py
rtk git commit -m "feat(p3-v3): close contract input chronology"
```

### Task 6: Enforce Package A/B input roles and proposer isolation

**Files:**
- Modify: `src/p3_v3/packages.py`
- Modify: `tests/p3_v3/test_packages.py`

**Interfaces:**
- Extends: `materialize_package(source_root, target_root, manifest,
  allowed_classes=None) -> None`.
- Adds exact content classes without changing manifest byte/hash semantics.

- [ ] **Step 1: Write failing content-role and process-view tests**

Use these additions:

```python
PACKAGE_A_CLASSES = {
    "PUBLIC_BEHAVIOR_FRAME", "PROFILING_WORKLOAD", "PROFILING_RESULT",
    "CONTRACT", "E_COMMON", "E_CONTRACT", "SLOT", "PROPOSAL_INPUT",
}
PACKAGE_B_CLASSES = {
    "DENOMINATOR", "PORTFOLIO", "E_COMMON_PRIMARY",
    "E_CONTRACT_SENSITIVITY", "EXECUTION_CODE",
}
PROPOSER_ALLOWED_CLASSES = {"SOURCE", "BUILD", "PUBLIC_DOC", "CONTRACT", "PROPOSAL_INPUT"}
```

Assert full Package A verifies with both input inventories, while proposer
materialization contains no profiling result, `E_COMMON`, or `E_CONTRACT` file.
Assert a primary Package B job manifest rejects
`E_CONTRACT_SENSITIVITY`, whereas a sensitivity manifest must reject
`E_COMMON_PRIMARY`/`E_CONTRACT` role confusion. Package C classes remain
forbidden from A/B.

- [ ] **Step 2: Run RED**

```bash
rtk env PYTHONPATH=src /Users/limeng/Papers/P3-SemanticMutation/.venv/bin/python -m pytest tests/p3_v3/test_packages.py -q
```

- [ ] **Step 3: Implement filtered clean materialization**

Validate `allowed_classes` as a subset of the manifest role's allowed classes.
Build a projected manifest in memory, copy only its declared regular files to a
new target, and verify the projected file set and bytes. Do not mutate the
authoritative full-package manifest.

- [ ] **Step 4: Run GREEN and commit**

```bash
rtk env PYTHONPATH=src /Users/limeng/Papers/P3-SemanticMutation/.venv/bin/python -m pytest tests/p3_v3/test_packages.py -q
rtk git add src/p3_v3/packages.py tests/p3_v3/test_packages.py
rtk git commit -m "feat(p3-v3): separate package input roles"
```

### Task 7: Bind atomic job identity, retry ceiling, and P12 estimand

**Files:**
- Modify: `src/p3_v3/run_records.py`
- Modify: `tests/p3_v3/test_run_records.py`

**Interfaces:**
- Extends intent with: `object_type`, `object_id`, `mr_id`,
  `evaluation_input_class`, `evaluation_input_id`, `repetition_id`,
  `environment_id`, and `job_role`.
- Extends result with nullable `scientific_outcome`.
- Produces: `freeze_p12_denominator(paired_ids, job_records) -> dict`.
- Produces: `summarize_p12_outcomes(denominator, results) -> dict`.

- [ ] **Step 1: Write failing role and retry tests**

Primary controlled and P12 jobs must use `E_COMMON`; a
`CONTRACT_SENSITIVITY` job must use `E_CONTRACT`. Reject profiling or
certification-witness classes. Reject attempt 4 even after three infrastructure
failures, and reject retry after any scientific terminal result.

- [ ] **Step 2: Write failing P12 denominator/estimand tests**

Freeze a denominator before results, then cover all five scientific outcomes.
Expected contribution table:

| Outcome | Lower | Upper | Complete-case included |
|---|---:|---:|---:|
| `MR_VIOLATION` | 1 | 1 | 1 |
| `DECLARED_EXCEPTION_OR_TIMEOUT_VIOLATION` | 1 | 1 | 1 |
| `MR_SATISFIED` | 0 | 0 | 1 |
| `SCIENTIFIC_INCONCLUSIVE` | 0 | 1 | 0 |
| `INFRASTRUCTURE_UNRESOLVED` | 0 | 1 | 0 |

Adding/removing a job, changing `P12_PAIRED`, using `E_CONTRACT`, omitting a
terminal row, or reweighting after outcomes must fail.

- [ ] **Step 3: Run RED**

```bash
rtk env PYTHONPATH=src /Users/limeng/Papers/P3-SemanticMutation/.venv/bin/python -m pytest tests/p3_v3/test_run_records.py -q
```

- [ ] **Step 4: Implement exact validators and estimand**

Keep attempt status (`PASS`, infrastructure/scientific failure, inconclusive,
missing) distinct from `scientific_outcome`. Only Phase 7 P12 results may carry
one of the five outcome strings. The summary reports planned count, every state
count, lower numerator/rate, upper numerator/rate, complete-case numerator and
denominator/rate, and both unresolved counts. Use integer counts and exact
`Fraction` strings.

- [ ] **Step 5: Run GREEN and commit**

```bash
rtk env PYTHONPATH=src /Users/limeng/Papers/P3-SemanticMutation/.venv/bin/python -m pytest tests/p3_v3/test_run_records.py -q
rtk git add src/p3_v3/run_records.py tests/p3_v3/test_run_records.py
rtk git commit -m "feat(p3-v3): freeze P12 missingness estimand"
```

### Task 8: Complete repeatable preflight capability gates

**Files:**
- Modify: `src/p3_v3/preflight.py`
- Modify: `tests/p3_v3/test_preflight.py`

**Interfaces:**
- Extends preflight specification with `phase_role`, `minimum_cpu_count`,
  `minimum_memory_bytes`, `minimum_disk_free_bytes`, and `worker_limit`.
- Result records atomic-replace and file-lock probe status without a scientific
  job ID.

- [ ] **Step 1: Write failing resource and capability tests**

Assert failure before smoke commands for wrong normalized repository, commit,
dependency lock, phase input, Package C path in an A/B preflight, insufficient
CPU/memory/disk, invalid worker limit, failed same-filesystem atomic replace, or
failed exclusive file lock. Repeating a corrected preflight must pass and must
not create `intent.json` or modify a scientific ledger.

- [ ] **Step 2: Run RED**

```bash
rtk env PYTHONPATH=src /Users/limeng/Papers/P3-SemanticMutation/.venv/bin/python -m pytest tests/p3_v3/test_preflight.py -q
```

- [ ] **Step 3: Implement local capability probes**

Use `os.replace` within one disposable directory and `fcntl.flock` on an
exclusive temporary file. Read available memory using `os.sysconf` when
available; an unavailable platform fact is an explicit `UNAVAILABLE` failure
when the spec requires a positive minimum. Cap `worker_limit` at CPU count and
record all observed facts in the canonical receipt. Do not import or call
`create_intent`.

- [ ] **Step 4: Run GREEN and commit**

```bash
rtk env PYTHONPATH=src /Users/limeng/Papers/P3-SemanticMutation/.venv/bin/python -m pytest tests/p3_v3/test_preflight.py -q
rtk git add src/p3_v3/preflight.py tests/p3_v3/test_preflight.py
rtk git commit -m "feat(p3-v3): verify phase preflight capabilities"
```

### Task 9: Wire the thin CLI and close the synthetic Phase 0 -> Phase 7 path

**Files:**
- Modify: `scripts/p3_v3/evidence.py`
- Modify: `tests/p3_v3/test_cli.py`
- Modify: `tests/p3_v3/test_synthetic_phase_path.py`
- Modify: `docs/superpowers/plans/2026-08-08-p3-v3-minimum-evidence-foundation-implementation.md`

**Interfaces:**
- Retains exactly the ten CLI command names in the governing design.
- `build-frames` consumes explicit bridge/source/registry/profiling/slot paths
  and writes the declared frame/input artifacts exclusively under `--output-root`.
- `verify-evidence` validates protocol, manifests, ledger, phase receipts, input
  roles, slot chronology, denominator, and P12 summary as one evidence set.

- [ ] **Step 1: Write the new failing CLI and end-to-end test**

The synthetic test must execute this chronology:

```text
validate protocol
-> verify pinned synthetic bridge
-> build public frame and Profiling Workload
-> freeze 30 E_COMMON identities
-> ingest complete profiling success/failure rows
-> derive robust technique and subject frames
-> close NOT_APPLICABLE or E_CONTRACT per slot
-> build/verify Package A and proposer view
-> build/verify Package B primary and sensitivity views
-> run repeatable preflight
-> create immutable synthetic job attempts
-> reduce ledger and close controlled phase
-> verify reveal commitment on synthetic Package C
-> freeze P12 denominator before results
-> record all five outcome states
-> regenerate lower/upper/complete-case summaries
-> verify complete evidence set
```

Assert every claim remains `blocked`; the test must not access the network, real
P12 data, a live MR, or a real mutant.

- [ ] **Step 2: Run RED**

```bash
rtk env PYTHONPATH=src /Users/limeng/Papers/P3-SemanticMutation/.venv/bin/python -m pytest tests/p3_v3/test_cli.py tests/p3_v3/test_synthetic_phase_path.py -q
```

- [ ] **Step 3: Wire existing module functions without copying rules**

The CLI parses paths, calls module functions, writes canonical outputs
exclusively, and emits one canonical status object. Scientific constants,
schemas, selection rules, generator maps, package policies, estimand rules, and
retry rules remain in their owner modules.

Update the historical implementation plan's Material Passport to state that it
is superseded for alignment work by this plan; do not rewrite its completed task
history.

- [ ] **Step 4: Run focused and full verification**

```bash
rtk env PYTHONPATH=src /Users/limeng/Papers/P3-SemanticMutation/.venv/bin/python -m pytest tests/p3_v3 -q
rtk env PYTHONPATH=src /Users/limeng/Papers/P3-SemanticMutation/.venv/bin/python -m pytest -q
rtk env PYTHONPATH=src /Users/limeng/Papers/P3-SemanticMutation/.venv/bin/python -m ruff check src/p3_v3 scripts/p3_v3 tests/p3_v3
rtk git diff --check
```

Expected: all focused and repository tests pass; Ruff and diff check are clean.

- [ ] **Step 5: Perform the evidence-gate acceptance audit**

Map all 25 tests in evidence-design Section 12 and all 20 acceptance criteria in
Section 13 to exact test node IDs. Reject completion if any row lacks a test or
if a test asserts only a self-declared field without independently reconstructing
the value.

- [ ] **Step 6: Commit**

```bash
rtk git add src/p3_v3 scripts/p3_v3 tests/p3_v3 docs/superpowers/plans/2026-08-08-p3-v3-minimum-evidence-foundation-implementation.md
rtk git commit -m "feat(p3-v3): align minimum evidence foundation"
```

## Design-to-task traceability

This table is a planning invariant, not a substitute for Task 9's node-level
evidence map. A completed implementation must preserve the already-passing
coverage as well as add the revised-design delta.

| Governing-design requirement | Owning task(s) |
|---|---|
| Section 12 tests 1-3: canonical bytes, pinned bridge, commitment opening | Existing regression suite; Task 9 re-verification |
| Tests 4-7: public frame, adapter registry, workload, technique bounds | Tasks 2-3 |
| Tests 8-9: `E_COMMON`, slot closure, `E_CONTRACT` | Tasks 4-5 |
| Tests 10-16: job roles, funnels, identities, frames, site selection, chronology | Tasks 2-7 and Task 9 regression |
| Tests 17-18: MR chronology and proposal provenance | Task 1 and Task 9 regression |
| Tests 19-21: package isolation and immutable job reduction | Tasks 6-7 |
| Tests 22-24: P12 estimand, ledger closure, repeatable preflight | Tasks 7-8 |
| Test 25: synthetic Phase 0 -> Phase 7 path | Task 9 |
| Section 13 criteria 1-2: authenticated bridge and blinded reveal | Existing regression suite; Task 9 re-verification |
| Criteria 3-10: behavior/workload/technique/inputs/slots/frames | Tasks 2-5 |
| Criteria 11-13: chronology, MR isolation, packages | Tasks 1, 5-6, and 9 |
| Criteria 14-16: preflight, intent-before-side-effect, phase close | Tasks 7-9 |
| Criteria 17-18: blocked claims and frozen P12 inference | Tasks 1, 7, and 9 |
| Criteria 19-20: regression suites and synthetic-only boundary | Task 9 |

## Final completion boundary

Completion means the synthetic, audited evidence channel satisfies the revised
design and all claims remain blocked. It does **not** authorize or establish:

- a real P12 pairing result;
- successful semantic-mutant construction;
- any MR kill or mutation score;
- RQ1-RQ4 support;
- a Cursor scientific experiment;
- manuscript result writing.

The next permitted planning step after this implementation passes independent
review is the controlled-experiment implementation plan. A Cursor VM scientific
launch remains separately authorized.
