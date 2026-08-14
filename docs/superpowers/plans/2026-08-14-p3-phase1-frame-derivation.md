# P3 Phase 1 Frame Derivation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking. This closes charter Task 3
> checkbox 2 of
> `docs/superpowers/plans/2026-08-12-p3-return-to-scientific-critical-path.md`.
> Worker subagents run on `gpt-5.6-sol-high`; the independent reviewer runs
> on `claude-fable-5-thinking-max` (user-fixed division of labor,
> 2026-08-14; requested "Sol High Fast" has no available slug).

**Goal:** Derive frozen Phase 1 frames for all 35 blinded P12 subjects via
the production `build-frames` CLI, close Phase 1's scientific exit
criterion (byte-identical regeneration from shuffled inputs; no dynamic
result, contract, mutant, MR, or real-fault outcome), and record receipts.

**Architecture:** The CLI already exists. Two ITT-funnel gaps currently
crash exact 35-record coverage: (1) adapter `ValueError` becomes
`E_ADAPTER_EXECUTION` and aborts the batch; (2) `EXECUTABLE` discovery
with zero E_COMMON-eligible schemas raises `E_COMMON_EXECUTABLE`. Both
are validity repairs so failures stay visible as inventory rows. Phase 1
does not execute profiling; a helper builds unresolved receipts covering
the already-selected workload. A driver extracts hash-bound archives,
assembles exact subject specs, invokes `build-frames` with empty
slots/contracts/applicability, and proves byte-identical regeneration.

**Tech Stack:** Python 3.12 (`/opt/anaconda3/bin/python`, pytest 8.4.2),
stdlib only in scientific modules; existing `p3_v3` CLI
(`scripts/p3_v3/evidence.py build-frames`).

## Global Constraints

- Charter rails apply verbatim: no verifier/lock hardening; frozen
  acceptance list per task; independent review judges PASS/BLOCK only
  against that list; max **two** repair rounds per task (charter cap, not
  SDD's five); root-cause batching; full suite only at the freeze point,
  in a **clean worktree, unsandboxed**. Interpreter:
  `/opt/anaconda3/bin/python`.
- All claims remain `blocked`. No scientific result is recorded. No
  network, no P12 reveal-ledger, no Cursor VM, no label/worksheet/
  `resolved.json`/Package C in P3 evidence.
- Do not patch the 5 missing-`CMakeLists.txt` subjects by swapping
  descriptors or trees. Do not invent schemas, SUCCESS traces, or
  technique tags. Do not execute profiling commands, contracts, mutants,
  or MRs.
- Subject specifications must cover the verified bridge **exactly** (35
  neutrals, no omission, no duplicate). Empty Phase 1 slot inputs:
  `slots=[]`, `contracts={}`, `applicability-map={}`.
- Archives stay gitignored. Extracted trees stay gitignored. Frames JSON
  is the committed scientific product.
- Commits land on `main` (user standing: continue current pipeline,
  commit/push). Do not add untracked TOSEM/review/artifact junk.

## Decision record (frozen)

1. **Adapter execution failure stays in the ITT funnel** as frame-level
   `discovery_status="ADAPTER_EXECUTION_FAILED"`. `run_adapter_discovery`
   still raises `E_ADAPTER_EXECUTION` (existing unit tests stay). A new
   wrapper used by `derive_subject_material` catches only that code,
   keeps the registered `adapter_id` / `implementation_source_sha256`,
   copies the original `ValueError` text into
   `unsupported_or_exclusion_reason`, and emits empty
   `source_files`/`declarations`/`public_schemas`/`sites`. This is not
   `ADAPTER_UNSUPPORTED` (an adapter exists; it fail-closed).
2. **`EXECUTABLE` + zero eligible schemas** yields 30
   `COMMON_INPUT_UNAVAILABLE` rows, same as `ADAPTER_UNSUPPORTED`. The
   remaining `E_COMMON_EXECUTABLE` check fires only when eligible schemas
   were non-empty but no row is `COMMON_INPUT_EXECUTABLE`. Do not
   fabricate schemas. Task-2 test
   `test_executable_discovery_with_zero_eligible_schemas_fails_closed`
   is rewritten to assert the UNAVAILABLE inventory (validity repair, not
   claim contraction).
3. **Phase 1 profiling receipts are unresolved.** Status
   `ADAPTER_UNCERTAIN`, `failure_code="PHASE1_PROFILING_NOT_EXECUTED"`,
   empty `call_trace`, `timed_out=False`. `classify_technique` therefore
   returns `TECH_UNCERTAIN`. Fabricating `SUCCESS` traces is forbidden.
4. **Two-pass specs, one CLI invocation.** The driver computes the
   unresolved receipt from the statically derived workload, then calls
   production `build-frames`, which re-derives and must bind
   byte-identically. Slots stay empty (slot closure is Phase 2).
5. **Capture risk.** If `_capture_tracked_source_manifest` rejects a
   P12-legal tree (evidence.py transient set vs
   `canonical_source_tree_sha256`), that is a Task C/D repair: align
   **subject-source** capture with the hash formula. Do not strip files
   to force a hash match.

## File map

- Modify: `src/p3_v3/bridge_and_frames.py` — wrapper, E_COMMON rule,
  unresolved-receipt helper; `derive_subject_material` uses the wrapper.
- Modify: `tests/p3_v3/test_bridge_and_frames.py` — ITT + receipt tests.
- Create: `scripts/p3_v3/build_phase1_frames.py` — extract, specs, CLI,
  shuffle regeneration.
- Create: `tests/p3_v3/test_phase1_frame_driver.py` — tiny-fixture driver
  tests (not the 3.3 GB intake).
- Create: `data/p3_v3/phase1_frames/inputs/{empty-slots,empty-contracts,empty-applicability}.json`
- Create: `data/p3_v3/phase1_frames/out/` (CLI artifacts, committed)
- Create: `docs/review_20260814/phase1_frames_task_report.md`
- Modify: `.gitignore` — `data/p3_v3/p12_intake/extracted/`
- Modify: charter Task 3 checkbox 2 + decision ledger

---

### Task A: ITT funnel — fail-closed discovery + zero-schema E_COMMON

**Files:**
- Modify: `src/p3_v3/bridge_and_frames.py` (`run_adapter_discovery`
  unchanged; new `discover_subject_or_fail_closed`;
  `derive_subject_material` calls the wrapper; `build_common_inputs`
  status set + zero-schema path)
- Test: `tests/p3_v3/test_bridge_and_frames.py`

**Interfaces:**
- Consumes: existing `run_adapter_discovery(source_snapshot,
  build_descriptor, registry, adapter_id) -> dict`;
  `EvidenceError.code`; adapter `ValueError` via `__cause__`.
- Produces: `discover_subject_or_fail_closed(...)` with the same
  signature and the same return schema as `run_adapter_discovery`. On
  `E_ADAPTER_EXECUTION` with a non-`None` `adapter_id`, returns a
  self-hashed discovery with `discovery_status="ADAPTER_EXECUTION_FAILED"`.
  `build_common_inputs` accepts frame-level
  `{EXECUTABLE, ADAPTER_UNSUPPORTED, ADAPTER_EXECUTION_FAILED}`.

- [ ] **Step A1: Write the failing tests** (append to
  `tests/p3_v3/test_bridge_and_frames.py`).

```python
def test_discover_subject_or_fail_closed_keeps_missing_cmakelists_visible(tmp_path):
    source = tmp_path / "subject"
    source.mkdir()
    (source / "README.md").write_text("no cmake root\n", encoding="utf-8")
    registry = validate_adapter_registry(
        _real_adapter_registry(), _real_controller_snapshot()
    )
    discovery = discover_subject_or_fail_closed(
        _source_snapshot(source),
        {"ecosystem": "cmake", "language_family": "c"},
        registry,
        "CMAKE_CTEST_V1",
    )
    assert discovery["discovery_status"] == "ADAPTER_EXECUTION_FAILED"
    assert discovery["adapter_id"] == "CMAKE_CTEST_V1"
    assert discovery["ecosystem"] == "cmake"
    assert discovery["implementation_source_sha256"]
    assert discovery["source_files"] == []
    assert discovery["declarations"] == []
    assert discovery["public_schemas"] == []
    assert discovery["sites"] == []
    assert discovery["unsupported_or_exclusion_reason"] == "CMakeLists.txt is absent"
    assert discovery["artifact_sha256"] == canonical_sha256(
        {key: value for key, value in discovery.items() if key != "artifact_sha256"}
    )


def test_run_adapter_discovery_still_raises_on_missing_build_file(tmp_path):
    source = tmp_path / "subject"
    source.mkdir()
    (source / "module.py").write_text("VALUE = 1\n", encoding="utf-8")
    registry = validate_adapter_registry(
        _real_adapter_registry(), _real_controller_snapshot()
    )
    with pytest.raises(EvidenceError, match="E_ADAPTER_EXECUTION"):
        run_adapter_discovery(
            _source_snapshot(source),
            {"ecosystem": "python"},
            registry,
            "PYTHON_PEP517_V1",
        )


def test_executable_discovery_with_zero_eligible_schemas_yields_unavailable_rows():
    registry = validate_input_generator_registry(
        _load_generator_registry(), _source_snapshot(GENERATOR_FIXTURE_ROOT)
    )
    inventory = build_common_inputs(
        _source_record(), _public_frame_with_schemas([]), registry
    )
    assert len(inventory["rows"]) == 30
    assert {row["status"] for row in inventory["rows"]} == {
        "COMMON_INPUT_UNAVAILABLE"
    }
    assert [row["ordinal"] for row in inventory["rows"]] == list(range(30))


def test_fail_closed_discovery_yields_thirty_unavailable_rows():
    registry = validate_input_generator_registry(
        _load_generator_registry(), _source_snapshot(GENERATOR_FIXTURE_ROOT)
    )
    inventory = build_common_inputs(
        _source_record(),
        _public_frame_with_schemas(
            [], discovery_status="ADAPTER_EXECUTION_FAILED"
        ),
        registry,
    )
    assert len(inventory["rows"]) == 30
    assert {row["status"] for row in inventory["rows"]} == {
        "COMMON_INPUT_UNAVAILABLE"
    }
```

Rewrite (do not keep a raising copy) the existing
`test_executable_discovery_with_zero_eligible_schemas_fails_closed` into
the UNAVAILABLE test above. Keep
`test_supported_common_input_generation_fails_closed_when_all_rows_invalid`
unchanged. Keep `test_real_python_adapter_requires_pyproject` unchanged.

- [ ] **Step A2:** Run the new tests; expect FAIL (wrapper missing /
  zero-schema still raises).

```bash
PYTHONPATH=src /opt/anaconda3/bin/python -m pytest \
  tests/p3_v3/test_bridge_and_frames.py::test_discover_subject_or_fail_closed_keeps_missing_cmakelists_visible \
  tests/p3_v3/test_bridge_and_frames.py::test_run_adapter_discovery_still_raises_on_missing_build_file \
  tests/p3_v3/test_bridge_and_frames.py::test_executable_discovery_with_zero_eligible_schemas_yields_unavailable_rows \
  tests/p3_v3/test_bridge_and_frames.py::test_fail_closed_discovery_yields_thirty_unavailable_rows \
  tests/p3_v3/test_bridge_and_frames.py::test_supported_common_input_generation_fails_closed_when_all_rows_invalid \
  tests/p3_v3/test_bridge_and_frames.py::test_real_python_adapter_requires_pyproject \
  -q
```

- [ ] **Step A3: Minimal implementation**

In `bridge_and_frames.py`, add:

```python
def discover_subject_or_fail_closed(
    source_snapshot: SourceSnapshot,
    build_descriptor: Mapping[str, Any],
    registry: Mapping[str, Any],
    adapter_id: str | None,
) -> dict[str, Any]:
    try:
        return run_adapter_discovery(
            source_snapshot, build_descriptor, registry, adapter_id
        )
    except EvidenceError as exc:
        if exc.code != "E_ADAPTER_EXECUTION" or not adapter_id:
            raise
        entries = {
            entry.get("adapter_id"): entry
            for entry in registry["adapters"]
            if isinstance(entry, Mapping)
        }
        entry = entries.get(adapter_id)
        if not isinstance(entry, Mapping):
            raise
        cause = exc.__cause__
        reason = str(cause) if cause is not None else str(exc)
        ecosystem = entry.get("ecosystem")
        if not isinstance(ecosystem, str) or not ecosystem:
            ecosystem = (
                build_descriptor.get("ecosystem")
                if isinstance(build_descriptor.get("ecosystem"), str)
                else ""
            )
        body = {
            "schema_version": "p3-adapter-discovery-v1",
            "adapter_id": adapter_id,
            "ecosystem": ecosystem,
            "discovery_status": "ADAPTER_EXECUTION_FAILED",
            "implementation_source_sha256": entry["source_sha256"],
            "source_files": [],
            "declarations": [],
            "public_schemas": [],
            "sites": [],
            "unsupported_or_exclusion_reason": reason,
        }
        return {**body, "artifact_sha256": canonical_sha256(body)}
```

Point `derive_subject_material`'s `run_adapter_discovery(...)` call at
`discover_subject_or_fail_closed(...)`.

In `build_common_inputs`:
- Allow `discovery_status` in
  `{"EXECUTABLE", "ADAPTER_UNSUPPORTED", "ADAPTER_EXECUTION_FAILED"}`.
- Treat `ADAPTER_EXECUTION_FAILED` like `ADAPTER_UNSUPPORTED` for the
  "cannot carry eligible public schemas" check.
- **Delete** the raise
  `"executable discovery produced no eligible common-input schema"` so
  `EXECUTABLE` with `not eligible` falls through to the existing
  30-row `COMMON_INPUT_UNAVAILABLE` branch.
- Change the terminal check to:

```python
    if (
        discovery_status == "EXECUTABLE"
        and eligible
        and not any(row["status"] == "COMMON_INPUT_EXECUTABLE" for row in rows)
    ):
        raise EvidenceError(
            "E_COMMON_EXECUTABLE",
            "supported subject produced no executable common input",
        )
```

- [ ] **Step A4:** Re-run Step A2 tests; expect PASS.

- [ ] **Step A5: Commit**

```bash
git add src/p3_v3/bridge_and_frames.py tests/p3_v3/test_bridge_and_frames.py
git commit -m "$(cat <<'EOF'
feat(p3-v3): keep adapter and zero-schema failures in the ITT funnel

Phase 1 must cover the 35-record bridge exactly. Adapter ValueError and
executable discovery with no E_COMMON schema stay visible as inventory
rows instead of aborting derive_subject_material.
EOF
)"
```

**Acceptance (frozen):** (1) missing `CMakeLists.txt` yields
`ADAPTER_EXECUTION_FAILED` with the verbatim reason; (2)
`run_adapter_discovery` still raises `E_ADAPTER_EXECUTION`; (3) zero
eligible schemas → 30 `COMMON_INPUT_UNAVAILABLE`; (4) all-invalid
eligible schemas still raise `E_COMMON_EXECUTABLE`.

---

### Task B: Phase 1 unresolved profiling receipt

**Files:**
- Modify: `src/p3_v3/bridge_and_frames.py` — add
  `build_phase1_unresolved_profiling_receipt`
- Test: `tests/p3_v3/test_bridge_and_frames.py`

**Interfaces:**
- Consumes: a validated-or-soon-to-be-validated profiling workload
  (`selected_rows`, `artifact_sha256`, `controlled_subject_source_id`);
  `_SOURCE_RECORD_SCHEMA`; `file_sha256(Path(__file__))`.
- Produces:

```python
def build_phase1_unresolved_profiling_receipt(
    workload: Mapping[str, Any],
    source_record: Mapping[str, Any],
    *,
    neutral_snapshot_id: str,
    adapter_implementation_source_sha256: str | None,
) -> dict[str, Any]:
```

Return schema is `_PROFILING_RECEIPT_SCHEMA` with
`schema_version="p3-profiling-results-v1"`. One result per selected row,
sorted by `behavior_id`. Empty `selected_rows` → `results=[]`.

Literal result fields:
- `status`: `"ADAPTER_UNCERTAIN"`
- `failure_code`: `"PHASE1_PROFILING_NOT_EXECUTED"`
- `argv`: `["p3-phase1-unexecuted", behavior_id]`
- `timed_out`: `False`
- `exit_code`: `None`
- `call_trace`: `[]`
- `call_trace_sha256`: `canonical_sha256([])`
- `observed_site_ids`: `[]`
- `input_sha256`: `[canonical_sha256({"behavior_id": behavior_id, "domain": "P3-PHASE1-UNEXECUTED-INPUT-v1"})]`
- `environment_sha256`: `canonical_sha256({"domain": "P3-PHASE1-UNEXECUTED-ENV-v1"})`
- `stdout_sha256` / `stderr_sha256`: `hashlib.sha256(b"").hexdigest()`
- `runner_version`: `"p3-phase1-unexecuted-v1"`
- `runner_implementation_source_sha256`: `file_sha256(Path(__file__))`

- [ ] **Step B1: Failing tests**

```python
def test_phase1_unresolved_receipt_covers_selected_rows_and_classifies_uncertain():
    behavior_id = _behavior_id("phase1-unexecuted")
    workload = _synthetic_workload([(behavior_id, "PUBLIC_API")])
    source = _source_record()
    source = {
        **source,
        "normalized_source_tree_sha256": workload["normalized_source_tree_sha256"]
        if "normalized_source_tree_sha256" in workload
        else "41" * 32,
        "build_descriptor_sha256": "42" * 32,
    }
    # Bind source ids the same way _profiling_receipt helpers do in this file.
    receipt = build_phase1_unresolved_profiling_receipt(
        workload,
        {
            "normalized_source_tree_sha256": "41" * 32,
            "build_descriptor_sha256": "42" * 32,
        },
        neutral_snapshot_id="61" * 32,
        adapter_implementation_source_sha256="31" * 32,
    )
    assert receipt["schema_version"] == "p3-profiling-results-v1"
    assert len(receipt["results"]) == 1
    row = receipt["results"][0]
    assert row["status"] == "ADAPTER_UNCERTAIN"
    assert row["failure_code"] == "PHASE1_PROFILING_NOT_EXECUTED"
    assert row["call_trace"] == []
    assert row["timed_out"] is False
    profile = classify_technique(workload, receipt)
    assert profile["primary_technique"] == "TECH_UNCERTAIN"


def test_phase1_unresolved_receipt_covers_empty_workload():
    workload = _synthetic_workload([])
    receipt = build_phase1_unresolved_profiling_receipt(
        workload,
        {
            "normalized_source_tree_sha256": "41" * 32,
            "build_descriptor_sha256": "42" * 32,
        },
        neutral_snapshot_id="61" * 32,
        adapter_implementation_source_sha256=None,
    )
    assert receipt["results"] == []
    profile = classify_technique(workload, receipt)
    assert profile["primary_technique"] == "TECH_UNCERTAIN"
```

If `_synthetic_workload([])` is illegal, construct a workload body with
`selected_rows=[]`, self-hash it, and use the same source-id fields the
empty-category `classify_technique` path already accepts. Inspect
`_synthetic_workload` and match its field names exactly. If the helper
requires a `controlled_subject_source_id` that equals
`_controlled_subject_source_id(source_record)`, set those bytes to match.

Also add an end-to-end `derive_subject_material` test using the real
cmake adapter on a tree without `CMakeLists.txt`: wrapper → failed
discovery → empty workload → unresolved receipt →
`derive_subject_material` PASS, `discovery_status=="ADAPTER_EXECUTION_FAILED"`,
30 UNAVAILABLE common inputs, `primary_technique=="TECH_UNCERTAIN"`.
Reuse `_real_adapter_registry` / `_real_controller_snapshot` /
`validate_input_generator_registry(_real_generator_registry(), ...)`.
Build a syntactically complete `_RECORD_SCHEMA` bridge record whose
`normalized_source_tree_sha256` / `build_descriptor_sha256` match the
spec (other sha256 fields may be dummy 64-hex; `eligibility_reason` a
nonempty string; both eligible flags `True`).

- [ ] **Step B2:** Run the new tests; expect FAIL (helper missing).

- [ ] **Step B3:** Implement `build_phase1_unresolved_profiling_receipt`.
  Sort results by `behavior_id`. Self-hash the body. Validate
  `neutral_snapshot_id` with `validate_sha256`. If
  `adapter_implementation_source_sha256` is not `None`, validate it too.
  Copy `controlled_subject_source_id` from the workload.

- [ ] **Step B4:** Re-run Task B tests; expect PASS. Also re-run Task A
  tests; they must stay green.

- [ ] **Step B5: Commit**

```bash
git add src/p3_v3/bridge_and_frames.py tests/p3_v3/test_bridge_and_frames.py
git commit -m "$(cat <<'EOF'
feat(p3-v3): emit Phase 1 unresolved profiling receipts

Profiling is not executed in Phase 1. Selected workload rows get
ADAPTER_UNCERTAIN receipts so technique classification stays
TECH_UNCERTAIN without fabricating SUCCESS traces.
EOF
)"
```

**Acceptance (frozen):** (1) selected rows are covered 1:1; (2) empty
workload → empty results; (3) `classify_technique` → `TECH_UNCERTAIN`;
(4) fail-closed cmake subject completes `derive_subject_material`.

---

### Task C: Phase 1 driver (extract, specs, CLI, shuffle)

**Files:**
- Create: `scripts/p3_v3/build_phase1_frames.py`
- Create: `tests/p3_v3/test_phase1_frame_driver.py`
- Create: `data/p3_v3/phase1_frames/inputs/empty-slots.json` → canonical
  `[]`
- Create: `data/p3_v3/phase1_frames/inputs/empty-contracts.json` → `{}`
- Create: `data/p3_v3/phase1_frames/inputs/empty-applicability.json` → `{}`
- Modify: `.gitignore` — add `data/p3_v3/p12_intake/extracted/`

**Interfaces:**
- Consumes: `data/p3_v3/p12_intake/verified_bridge.json`,
  `descriptors/<neutral>.json`, `archives/<neutral>.tar`,
  `data/p3_v3/protocol/{adapter_registry,input_generator_registry}.json`,
  repo-root adapter/generator implementations.
- Produces: subject-specs list covering the bridge exactly; CLI
  `build-frames` PASS; second run from shuffled specs with byte-identical
  per-artifact files (compare sha256 of file bytes).

Driver algorithm (stdlib + `p3_v3` imports only):

1. Read verified bridge; for each record in **sorted**
   `neutral_snapshot_id` order:
   - Verify `archives/<neutral>.tar` sha256 equals
     `source_archive_sha256`.
   - Load descriptor JSON; `canonical_sha256(descriptor)` must equal
     `build_descriptor_sha256` (parse JSON object, then canonical hash;
     do not hash raw file bytes if the custodian stored pretty JSON —
     match `build_p12_bridge._canonical_file_sha256` behaviour: JSON
     objects are canonical-hashed).
   - Extract the tar into `data/p3_v3/p12_intake/extracted/<neutral>/`
     (delete the directory first if present; reject any symlink in the
     archive). Process **one subject at a time**; never hold 35 snapshots
     in memory.
   - Capture source via the same function the CLI uses:
     `scripts.p3_v3.evidence._capture_tracked_source_manifest(source_root, ["."], "subject-source")`.
     Assert `canonical_source_tree_sha256(snapshot) == record["normalized_source_tree_sha256"]`.
   - Validate registries against repo-root snapshots the same way
     `_dispatch_build_frames` does (`validate_adapter_registry` /
     `validate_input_generator_registry` with captured implementation
     snapshots).
   - `adapter_id = _ecosystem_to_adapter(registry).get(ecosystem)`
     (julia → `None` → `ADAPTER_UNSUPPORTED`).
   - `raw = discover_subject_or_fail_closed(snapshot, descriptor, adapter_registry, adapter_id)`
   - `frame = build_public_behavior_frame(source_record, raw)`
   - `scale = derive_source_scale(snapshot, raw)`
   - `workload = select_profiling_workload(frame, scale["scale_class"])`
   - `receipt = build_phase1_unresolved_profiling_receipt(workload, source_record, neutral_snapshot_id=neutral, adapter_implementation_source_sha256=raw["implementation_source_sha256"])`
   - Append a CLI subject spec (`source_root` as a string path,
     **no** `source_snapshot` key) using the **unvalidated public**
     registry JSON from `data/p3_v3/protocol/` (the CLI re-validates).
2. Write canonical `subject-specs.json` under
   `data/p3_v3/phase1_frames/inputs/` (gitignored if it contains
   machine-local absolute paths; prefer repo-relative `source_root`).
3. Invoke production CLI:

```text
/opt/anaconda3/bin/python scripts/p3_v3/evidence.py build-frames
  --bridge data/p3_v3/p12_intake/verified_bridge.json
  --subject-specs data/p3_v3/phase1_frames/inputs/subject-specs.json
  --adapter-root .
  --generator-root .
  --slots data/p3_v3/phase1_frames/inputs/empty-slots.json
  --contracts data/p3_v3/phase1_frames/inputs/empty-contracts.json
  --applicability-map data/p3_v3/phase1_frames/inputs/empty-applicability.json
  --output-root data/p3_v3/phase1_frames/out
```

Expect `status=PASS`, `subject_count=35`,
`common_input_count=1050` (35×30), and no `slot-closure-*` files.

4. Shuffle the subject-specs list with `random.Random(0).shuffle`, write
   to a temp specs file, run `build-frames` into a temp output root,
   compare every filename's sha256 against `out/`. Must be identical.
   Delete the temp output. Keep `out/` as the frozen product.

CLI import note: the driver may `subprocess` the CLI (preferred; matches
production) rather than calling `_dispatch_build_frames` in-process.

Tiny-fixture tests in `test_phase1_frame_driver.py`: extract a helper
function that (a) rejects a symlink tar entry, (b) rejects archive sha
mismatch, (c) requires exact bridge coverage — using tmp_path tars of a
few bytes, **not** the intake. If the helper is easiest to test by
importing functions from the script, put those functions at module
level with snake_case names (`extract_archive`, `load_descriptor`,
`assert_exact_coverage`). Do not hit the network.

Empty JSON inputs must be written with `write_canonical_json(..., exclusive=True)`.

- [ ] **Step C1:** Write the failing tiny-fixture tests.
- [ ] **Step C2:** Run them; expect FAIL.
- [ ] **Step C3:** Implement the driver + empty inputs + gitignore line.
- [ ] **Step C4:** Tiny-fixture tests PASS. Do **not** run the 35-subject
  derivation in this task.
- [ ] **Step C5: Commit**

```bash
git add scripts/p3_v3/build_phase1_frames.py tests/p3_v3/test_phase1_frame_driver.py \
  data/p3_v3/phase1_frames/inputs .gitignore
git commit -m "$(cat <<'EOF'
feat(p3-v3): add Phase 1 frame-derivation driver

Extract hash-bound archives, assemble exact 35-record subject specs with
unresolved profiling receipts, and invoke production build-frames.
EOF
)"
```

**Acceptance (frozen):** (1) tiny-fixture tests green; (2) empty
slots/contracts/applicability committed; (3) extracted trees gitignored;
(4) driver does not import P12 labels or the reveal ledger.

---

### Task D: Run derivation, freeze, receipts, charter

**Files:**
- Create: `docs/review_20260814/phase1_frames_task_report.md`
- Modify: `docs/superpowers/plans/2026-08-12-p3-return-to-scientific-critical-path.md`
  Task 3 checkbox 2 + decision ledger
- Produce: `data/p3_v3/phase1_frames/out/**` (CLI artifacts)
- Produce: `data/p3_v3/phase1_frames/receipts.json` (counts + hashes;
  no labels)

- [x] **Step D1:** Production pass 1 completed; original driver then
  stopped at `E_ARTIFACT_SIZE` (101,778,506-byte `subject-frames.json`).
  That stop was correct. Pass 1 was not rerun. Shuffle pass 2 ran via
  the CA-01 continuation path.
- [x] **Step D2:** Write `receipts.json` with: bridge sha256, protocol
  sha256, adapter/generator registry sha256s, per-neutral
  `discovery_status`, `scale_class`, `primary_technique` (must be
  `TECH_UNCERTAIN` for every subject), common-input status counts,
  selected-row counts, and `subject-frames.json` sha256. Neutral IDs
  only. Expected funnel (from Task 4 smoke + julia): 3
  `ADAPTER_UNSUPPORTED` (julia), 5 `ADAPTER_EXECUTION_FAILED` (verbatim
  `CMakeLists.txt is absent`), 27 `EXECUTABLE` (23 cmake/meson/autotools
  OK + 4 python). If a count differs, record the actual status and stop
  for controller adjudication — do not relabel.
  **Actual (CA-02): 3 / 9 / 23.** Four extra Python fail-closed
  reasons retained verbatim.
- [x] **Step D3:** Freeze-point full suite in a **new** clean worktree,
  unsandboxed: `934 passed in 564.00s` at `54a72576`.
- [x] **Step D4:** Task report + charter: tick Task 3 checkbox 2; ledger
  entry dated 2026-08-14/15.
- [x] **Step D5: Commits** (amendment `693ae67f`, frames `54a72576`,
  docs follow). Then `git push origin main` (no force).

**Acceptance (frozen):** (1) `build-frames` PASS on 35 subjects; (2)
shuffle regeneration byte-identical; (3) every `primary_technique` is
`TECH_UNCERTAIN`; (4) no slot-closure artifacts; (5) no labels in
committed JSON; (6) clean-worktree suite green; (7) charter checkbox 2
ticked; (8) `git push` succeeded.

### Controller amendment CA-01 / CA-02 (2026-08-14)

Production pass 1 completed, then the original driver stopped at
`E_ARTIFACT_SIZE` because `subject-frames.json` is 101,778,506 bytes
(97.064 MiB). That stop was correct under the frozen 90 MiB gate. The
file was not stripped. Schema `p3-subject-frames-v1` is unchanged.

CA-01 PASS authorizes one named implementation round:

- Reuse the existing 281 pass-1 files; do **not** rerun pass 1.
- 128 MiB limit applies only to the exact root-relative path
  `subject-frames.json`; every other artifact stays at 90 MiB.
- Raw canonical JSON remains the scientific identity.
- Git stores lossless `subject-frames.json.gz` (`gzip -n -9`); raw JSON
  stays local and is gitignored by exact path.
- Run only the not-yet-started shuffle pass 2 via
  `scripts/p3_v3/continue_phase1_frames_after_size_gate.py`.
- Do not use checkpoints as a substitute for pass 2 derivation.

CA-02 PASS records the **actual** discovery funnel as 3 / 9 / 23
(`ADAPTER_UNSUPPORTED` / `ADAPTER_EXECUTION_FAILED` / `EXECUTABLE`).
The planned 3 / 5 / 27 remains historical expectation only. Four extra
Python fail-closed subjects (two missing `pyproject.toml`, two missing
`[project].name`) stay in the ITT funnel with their original reasons.
Do not relabel them `EXECUTABLE`. Claims stay `blocked`.

- [x] **Step D6:** CA-01 continuation tests + shuffle pass 2 + gzip
  transport + receipts with actual funnel 3/9/23.

## Self-review

- Spec coverage: scientific plan Phase 1 exit (workload selection,
  E_COMMON ordinals, sites, visible failures, no dynamic results) →
  Tasks A–D; exact bridge coverage → C/D; charter rails → Global
  Constraints; Task 4 5+3 funnel → Decision 1 and D2 expected counts.
- No placeholders: tests, CLI argv, failure codes, and status strings
  are literal. `_synthetic_workload` field binding is instructed to
  match the existing helper rather than guessed.
- Type consistency: wrapper signature matches `run_adapter_discovery`;
  receipt helper returns `_PROFILING_RECEIPT_SCHEMA`; CLI spec keys
  match `evidence.py _SUBJECT_SPEC_SCHEMA` (`source_root`, not
  `source_snapshot`).
