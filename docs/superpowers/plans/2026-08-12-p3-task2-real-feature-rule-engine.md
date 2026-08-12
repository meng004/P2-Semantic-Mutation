# P3 Task 2 Implementation Plan — Real Source-Derived Feature Rule Engine

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking. This is Task 2 of the Exit-(b)
> charter (`2026-08-12-p3-return-to-scientific-critical-path.md`); its
> Global Constraints (bounded review, two-repair cap, root-cause batching,
> fast/slow test discipline) apply verbatim.

**Goal:** Make real Phase 1/2 feature records authoritative by (a) fixing the
one spec-fidelity defect in the derivation pipeline (E_COMMON ordinal base),
(b) supplying the real `PYTHON_PEP517_V1` adapter and the five real
`E_COMMON` input generators as source-hash-bound registry implementations,
and (c) populating registry V2 and re-emitting protocol V2.

**Architecture:** The 08-10 MEF-alignment work already derives scale, Public
Behavior Frame, profiling workload, technique, and site
reachability/applicability from validated adapter discovery
(`derive_source_scale`, `build_public_behavior_frame`,
`select_profiling_workload`, `classify_technique`, `tag_site_reachability`),
executes implementations only through the verified in-process seam, and
rejects caller-supplied discovery. What keeps real records non-authoritative
is the implementation layer: the only adapter/generator implementations are
test fixtures, and the Python fixture adapter is a manifest pass-through
(caller-declared records in disguise). This task adds real implementations
loaded exclusively through the existing registry seams; no controller module
imports them.

**Tech Stack:** Python stdlib only (`ast`, `tomllib`, `hashlib`, `json`);
existing seams unchanged; `/opt/anaconda3/bin/python` + pytest 8.4.2;
Ruff via `.venv/bin/ruff`.

## Discovery findings this plan is built on (verified 2026-08-12)

1. `build_common_inputs` emits ordinals `range(1, 31)` and seeds
   `_common_input_seed(source_id, 1..30)`
   (`src/p3_v3/bridge_and_frames.py:3485,3540-3542`), and
   `packages.verify_common_input_evidence` re-derives with
   `enumerate(rows, 1)` (`src/p3_v3/packages.py:526-535`). Both the
   SHA-pinned evidence design (L459-461) and the scientific plan (§5.2.2,
   "ordinals `0..29`", seed over `ordinal: i`) freeze a 0-based derivation.
   The `E_CONTRACT` side already uses `range(E_CONTRACT_COUNT)` (0..4)
   correctly. This is a preregistration-fidelity defect in the seed
   derivation and must be fixed before any real input exists.
2. The adapter contract: `discover(source_snapshot, build_descriptor)`
   executed via `_execute_verified_python` (network blocked, no output),
   normalized by `_normalize_adapter_result` (exact result schema; source
   paths must exist in the snapshot, be non-excluded, unique), validated by
   `_validate_discovery` + `_declaration_is_structurally_valid`.
3. The generator contract: `generate(schema_bytes, seed) ->
   {"envelope", "raw_payload_sha256"} | {"failure_code"}`; registry must
   list exactly the five E_COMMON generator IDs with
   `schema_kind == generator_id`, `output_schema.generator_id`, non-empty
   `failure_code`, real `implementation_path` + `source_sha256`.
4. Eligibility wall: only public-schema rows whose `schema_kind` is one of
   the five E_COMMON kinds are eligible; EXECUTABLE discovery with zero
   eligible schemas or zero executable rows fails
   (`E_COMMON_EXECUTABLE`); forbidden generator-input keys (project-test
   bodies/fixtures, contracts, sites, outcomes…) are rejected recursively.
5. `UNPROFILED` vs `NOT_APPLICABLE` semantics are already implemented and
   tested (`tag_site_reachability`); this task must not touch them.

## Frozen acceptance criteria (review judges only these)

1. **Ordinal fidelity:** E_COMMON rows carry ordinals `0..29`; seeds equal
   `SHA256(canonical_json({domain:"P3-E-COMMON-SEED-v1",
   controlled_subject_source_id, ordinal}))[:8]` per the design; schema
   assignment is `eligible[ordinal % k]`; `packages.verify_common_input_evidence`
   re-derives the same; no schema key/type changes anywhere.
2. **Real adapter:** `src/p3_v3/adapters/python_pep517_v1.py` derives
   discovery exclusively from snapshot bytes (pyproject.toml + AST), emits
   all five behavior categories on the realistic fixture repo, structurally
   valid declarations, canonical unique sites (including private helpers and
   methods), and at least one eligible public schema; a snapshot without a
   parseable `[project]` pyproject fails closed; excluded paths are never
   enumerated; PROJECT_TEST/EXAMPLE/BENCHMARK are path-evidenced only (their
   file bodies are never parsed for schemas); repeated invocation is
   byte-identical.
3. **Real generators:** the five E_COMMON generator implementations return
   deterministic schema-conforming envelopes (same seed → identical
   envelope bytes; different seed → different payload hash), and a stable
   `<ID>_INVALID` failure code on undecodable/subset-violating schema
   bytes. Each generator's payload conformance is asserted per kind.
4. **End-to-end:** `run_adapter_discovery` → `derive_source_scale` →
   `build_public_behavior_frame` → `select_profiling_workload` →
   `build_common_inputs` with the real registries on the fixture repo yields
   30 rows, ordinals 0..29, ≥1 `COMMON_INPUT_EXECUTABLE`.
5. **Registry V2 / protocol V2:** `build_phase0_protocol.py` populates both
   registries from the real implementation files (controller-root-relative
   paths + source SHA-256); `validate-protocol` exits 0 on the re-emitted
   protocol; double-run determinism holds.
6. **Freeze point:** full `tests/p3_v3` suite passes in the clean worktree,
   outside the shell sandbox; Ruff clean on all new/modified files; no
   verifier/lock/package/run-records schema (key/type) change; the packages
   change is confined to the ordinal value-domain of criterion 1.
7. **Declared-open (fail-visible):** CMAKE/MESON/AUTOTOOLS adapters remain
   unimplemented (their ecosystems stay on the frozen `ADAPTER_UNSUPPORTED`
   path until non-Python subjects enter the study); the five E_CONTRACT
   generators belong to the contract phase; the profiling runner is Phase 2
   execution scope.

## File structure

- Modify: `src/p3_v3/bridge_and_frames.py` (two loops + modulo, ~3 lines)
- Modify: `src/p3_v3/packages.py` (0-based enumerate + seed index, ~2 lines)
- Create: `src/p3_v3/adapters/python_pep517_v1.py` (no `__init__.py`;
  loaded only through the registry seam, never imported)
- Create: `src/p3_v3/input_generators/{json_schema_draft2020_12_v1,
  cli_token_grammar_v1,numeric_array_domain_v1,text_io_schema_v1,
  binary_record_schema_v1}.py`
- Create: `tests/p3_v3/fixtures/real_python_project/…` (realistic PEP 517
  repo: `pyproject.toml`, `src/demopkg/{__init__.py,core.py,textops.py,
  packing.py,_internal.py}`, `examples/run_demo.py`,
  `benchmarks/bench_core.py`, `tests/test_core.py`, `build/generated.py`
  (exclusion probe))
- Modify: `tests/p3_v3/test_bridge_and_frames.py` (ordinal pins at L1101,
  L1465, L3223 → `range(30)`; new rule-class test section)
- Modify: `tests/p3_v3/test_packages.py` (fixture rows 0..29; ordinal
  mutation probe value)
- Modify: `scripts/p3_v3/build_phase0_protocol.py` (registry population)
- Create: `docs/review_20260812/task2_rule_engine_task_report.md`
- Modify: charter Task 2 checkboxes + decision ledger

### Task A: E_COMMON ordinal spec-fidelity fix (RED → GREEN)

- [ ] **A1 RED:** flip the three ordinal pins to `list(range(30))` and the
  packages mutation probe from `rows[0]["ordinal"] = 0` to
  `rows[0]["ordinal"] = 1`; add explicit seed assertion
  `rows[0]["seed"] == int.from_bytes(bytes.fromhex(canonical_sha256({
  "domain": "P3-E-COMMON-SEED-v1", "controlled_subject_source_id": sid,
  "ordinal": 0}))[:8], "big")`. Run the touched tests; expect FAIL against
  current code.
- [ ] **A2 GREEN:** in `bridge_and_frames.build_common_inputs` change both
  `range(1, E_COMMON_COUNT + 1)` to `range(E_COMMON_COUNT)` and
  `eligible[(ordinal - 1) % len(eligible)]` to
  `eligible[ordinal % len(eligible)]`; in
  `packages.verify_common_input_evidence` change `enumerate(value["rows"], 1)`
  to `enumerate(value["rows"])`. Update the `test_packages.py` fixture
  builder loop to `range(30)`. Run: the touched tests pass.

### Task B: real `PYTHON_PEP517_V1` adapter (frozen discovery rule)

The adapter is stdlib-only, self-contained, and implements exactly this
frozen rule (its docstring restates it):

- **Precondition:** `pyproject.toml` must exist at the snapshot root, parse
  with `tomllib`, and contain a non-empty string `[project].name`;
  otherwise raise `ValueError` (surfaces as `E_ADAPTER_EXECUTION`).
- **Exclusion rule (inlined frozen copy):** a path is excluded when any
  casefolded component is in the module's `_EXCLUDED_SOURCE_PARTS` ∪
  `_EXCLUDED_SOURCE_NAMES` or starts with `cmake-build-`/`build-`.
- **source_files:** every snapshot path with suffix in
  `{.py,.pyi,.pyx,.pxd}` not excluded, sorted unique.
- **Package root:** `src/<pkg>/` when present, else flat `<pkg>/`, where
  `<pkg>` is the PEP 503-normalized project name with `-`→`_`. Public
  modules: `.py` files under the root with no `_`-prefixed component
  (`__init__.py` allowed, mapping to the package module).
- **PUBLIC_API:** for each public module, `ast.parse`; module-level
  `FunctionDef`/`AsyncFunctionDef`/`ClassDef` with public names; when a
  module-level `__all__` list of string constants exists, only those names.
  Declaration fields: entrypoint `"{dotted_module}:{name}"`; normalized
  entrypoint = casefold; provenance = file + `"L{lineno}-L{end_lineno}"`;
  `declared_inputs = {"parameters": [{"name", "annotation"}…]}` (class →
  `__init__` minus `self`; absent `__init__` → `[]`);
  `static_dependency_tags` = sorted unique first components of the module's
  `import`/`from` statements; `prerequisites = []`;
  `declared_input_schema_sha256` = canonical SHA-256 of the row's raw input
  schema (below).
- **CLI:** each `[project.scripts]` entry `name → "mod:func"`: category
  `CLI`, entrypoint `"{name} = {target}"`, normalized `"cli:{name}"`
  casefolded, provenance `pyproject.toml` + `"project.scripts.{name}"`,
  `declared_inputs = {"argv_tokens": [name]}`, tags = first component of
  target module, schema kind `CLI_TOKEN_GRAMMAR_V1`.
- **EXAMPLE / BENCHMARK / PROJECT_TEST (path-evidenced):** `.py` files whose
  first component is `examples` / `benchmarks` or `bench` / `tests` with
  name `test_*.py` or `*_test.py`. Entrypoints `"python {path}"` /
  `"python {path}"` / `"pytest {path}"`; normalized
  `"example:{path}"` / `"benchmark:{path}"` / `"pytest:{path}"`; declared
  inputs `{"argv_tokens": […]}`; tags `[]`; the raw schema is the fixed-argv
  record `{"kind": "ARGV_FIXED", "argv": […]}` (never eligible for
  E_COMMON); file bodies are not parsed.
- **Input-schema mapping (PUBLIC_API), by the casefolded set of parameter
  annotations:** ≥1 param and all in `{int,float,complex}` →
  `NUMERIC_ARRAY_DOMAIN_V1` `{kind, parameters, element_count,
  dtype: int64|float64, minimum: -1000000, maximum: 1000000}`; all `str` →
  `TEXT_IO_SCHEMA_V1` `{kind, fields, max_length: 256,
  charset: "printable_ascii"}`; all in `{bytes,bytearray,memoryview}` →
  `BINARY_RECORD_SCHEMA_V1` `{kind, fields, record_bytes: 32}`; zero params
  → no schema row; anything else → `JSON_SCHEMA_DRAFT2020_12_V1` object
  schema `{$schema, kind, type: "object", properties: {name: {type: …}},
  required: sorted(names), additionalProperties: false}` with int→integer,
  float→number, str→string, bool→boolean, list/tuple/sequence→array,
  dict/mapping→object, unknown→sorted eight-type union.
- **public_schemas rows:** `{schema_kind, raw_schema, provenance_path,
  provenance_span_or_key}` for PUBLIC_API (non-ARGV) + CLI rows with
  `raw_schema = {kind: "CLI_TOKEN_GRAMMAR_V1", program, tokens: {min: 0,
  max: 3}, vocabulary: sorted([name, "--help", "--version"])}`.
- **sites:** every `FunctionDef`/`AsyncFunctionDef` (any visibility,
  methods included) in public modules:
  `{path, symbol: dotted qualname, start_line: lineno,
  start_col: col_offset, end_line: end_lineno, end_col: end_col_offset}`.

- [ ] **B1 RED:** add the fixture repo and the rule-class tests below;
  run them; expect FAIL (no adapter file).
- [ ] **B2 GREEN:** implement the adapter; tests pass.

Rule-class tests (one per class, in `test_bridge_and_frames.py`):

1. category completeness + counts on the fixture repo (all five categories
   present; exclusion probe `build/generated.py` absent from `source_files`
   and sites);
2. public/private + `__all__` restriction (fixture `core.py` has `__all__`
   hiding one public-named function; `_internal.py` module and `_helper`
   function never appear);
3. schema-mapping classes: fixture exposes one numeric-only, one str-only,
   one bytes-only, one mixed-annotation, and one zero-param public function
   plus one CLI script; assert the exact `schema_kind` multiset and the
   zero-param absence;
4. determinism: two `run_adapter_discovery` invocations on the same
   snapshot produce byte-identical `artifact_sha256`;
5. fail-closed: snapshot without `pyproject.toml` →
   `EvidenceError` `E_ADAPTER_EXECUTION`;
6. wall: no `public_schemas` row has `provenance_path` under `tests/`,
   `examples/`, or `benchmarks/`;
7. sites: sorted canonical order, unique, include `_helper` and a method
   qualname `Accumulator.add`, all spans non-negative with
   `end_line ≥ start_line`.

### Task C: five real E_COMMON generators

Shared construction (each file self-contained, stdlib-only): the seed
stream is `block(i) = SHA256(b"P3-INPUT-STREAM-v1" + seed_be64 + i_be64)`;
`u64(i)` = first 8 bytes big-endian; envelope =
`{"schema_version": "p3-common-input-envelope-v1", "generator_id": ID,
"payload": payload}`; `raw_payload_sha256` = SHA-256 of canonical payload
JSON bytes + LF; invalid input → `{"failure_code": "<ID>_INVALID"}`.
Normative template (JSON_SCHEMA_DRAFT2020_12_V1): accept only an object
schema with `"type": "object"` and a dict `"properties"`; for each property
in sorted order derive the value from the stream by declared type
(integer → `u64 % 2_000_001 - 1_000_000`; number → integer/1000; string →
`"s" + block_hex[:8]`; boolean → `u64 % 2 == 1`; array → two integers;
object → `{}`; union list → deterministic pick `sorted(types)[u64 % len]`);
respect `required` ⊆ properties (else failure); payload
`{"arguments": {…}}`. The other four accept exactly the raw-schema shapes
frozen in Task B's mapping rule and construct: CLI → `argv = [program] +
vocabulary picks` with `min ≤ count ≤ max`; NUMERIC → `element_count`
values in `[minimum, maximum]` (float64 → value + `(u64 % 1000)/1000`
rounded to 6 places); TEXT → per-field text of length `1..min(max_length,64)`
over the frozen 37-character alphabet `a-z0-9space`; BINARY → per-field
`record_bytes` hex from the stream.

- [ ] **C1 RED:** parametrized generator tests (below); expect FAIL.
- [ ] **C2 GREEN:** implement the five files; tests pass.

Rule-class tests (parametrized over the five IDs where applicable):

1. valid schema → envelope with exact `schema_version`/`generator_id`, and
   `raw_payload_sha256 == sha256(canonical_json_bytes(payload))`;
2. determinism: same (schema, seed) twice → identical envelope bytes;
   seeds 0 vs 1 → different `raw_payload_sha256`;
3. invalid: non-JSON bytes, wrong `kind`, and subset violations → exact
   `<ID>_INVALID`;
4. conformance per kind: JSON payload has exactly the required properties
   with declared JSON types; CLI argv starts with program, tokens ⊆
   vocabulary, length within bounds; NUMERIC values within
   `[minimum, maximum]` and length `element_count`; TEXT fields over the
   frozen alphabet within length bound; BINARY fields are hex of
   `record_bytes` bytes.

### Task D: end-to-end + registry V2 + protocol V2

- [ ] **D1:** end-to-end test: real adapter registry (real file bytes read
  from `src/p3_v3/adapters/…`, snapshot-installed) → `run_adapter_discovery`
  → `derive_source_scale` → `build_public_behavior_frame` →
  `select_profiling_workload` → `build_common_inputs` with the real
  generator registry: 30 rows, ordinals `list(range(30))`, ≥1
  `COMMON_INPUT_EXECUTABLE`, scale class `S` for the fixture repo.
- [ ] **D2:** extend `build_phase0_protocol.py`: registry entries are built
  from the real implementation files (`implementation_path` =
  controller-root-relative POSIX path, `source_sha256` = file SHA-256;
  adapter entry `{PYTHON_PEP517_V1, python}`; five generator entries with
  `schema_kind == generator_id`, `output_schema = {generator_id,
  schema_version: "p3-common-input-envelope-v1"}`,
  `failure_code = "<ID>_INVALID"`). Run builder → validate-protocol PASS →
  double-run determinism.

### Task E: freeze receipt, report, commit

- [ ] **E1:** Ruff on all created/modified files; full `tests/p3_v3` in the
  clean worktree, outside the sandbox (expected: previous count + new
  tests, 0 failures).
- [ ] **E2:** task report
  `docs/review_20260812/task2_rule_engine_task_report.md` (receipts: test
  counts, protocol V2 SHA, registry hashes, ordinal-fix citation trail,
  declared-open items); tick charter Task 2 checkboxes + ledger entry.
- [ ] **E3:** one task-scoped commit
  (`feat(p3-v3): make real feature records source-derived`).

## Non-goals (binding)

- No CMAKE/MESON/AUTOTOOLS adapter implementations (frozen
  `ADAPTER_UNSUPPORTED` path covers those ecosystems until non-Python
  subjects enter).
- No E_CONTRACT generator implementations (contract-phase scope).
- No profiling runner or Phase 2 execution work.
- No verifier/lock hardening; no schema key/type changes; no changes to
  `tag_site_reachability` semantics.

## Self-review

- Spec coverage: acceptance 1→Task A; 2→Task B; 3→Task C; 4→Task D1;
  5→Task D2; 6→Task E; 7→Non-goals + report.
- The ordinal correction is justified by the SHA-pinned design (L459-461)
  and scientific plan §5.2.2 text, both already byte-bound into protocol
  V1; packages.py is touched only in the value domain of that rule.
- Type consistency: all schema/field names above were read from
  `bridge_and_frames.py` / `packages.py` current source, not invented;
  registry schema versions are `p3-adapter-registry-v1` /
  `p3-input-generator-registry-v1`.
