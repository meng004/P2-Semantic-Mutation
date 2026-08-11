# P3 v3 External Authority Lock Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the circular sole-index evidence verifier with a deterministic
external Authority Lock whose independently supplied SHA-256 binds controller
and subject bytes, complete job intents, retry policy, origin authority, and
observational completion counts.

**Architecture:** Keep the existing five production modules and thin CLI. The
evidence module exposes two deep operations—freeze and verify—while artifacts
owns safe canonical file I/O and run-records owns intent/retry/completion
reconstruction. Final verification accepts an evidence index only after loading
an exact Authority Lock under a literal external digest; it never executes lock
or index content and never reads `.git` during verification.

**Tech Stack:** Python 3.11 target, canonical UTF-8 JSON, SHA-256, pytest, Ruff,
existing `src/p3_v3` modules and `scripts/p3_v3/evidence.py` CLI.

**Committed design base:** `248529c053010577aa6b507a5a2c92f547f97140`.
The implementation starts from its immediate child plan-carrier commit, whose
only committed delta is this plan file. The plan cannot embed that child commit
without creating a Git self-reference.

**Governing design:**
`docs/superpowers/specs/2026-08-11-p3-v3-external-authority-lock-design.md`,
SHA-256 `7cc6389b3c2ef731722a6956e0b0f6fd58967dba5b847b52fd9cb8856a208490`.

## Global Constraints

- Every Local Desktop shell command starts with `rtk`. Cursor VM commands remain
  outside this plan and are not authorized.
- No network, P12 access, real mutant, real MR, scientific job, claim upgrade,
  manuscript result, dependency installation, push, PR, merge, or force action.
- RQ1-RQ4 and every scientific result claim remain `blocked`.
- Do not add a production module or workflow framework. Modify only the existing
  artifacts, run-records, evidence CLI/module, tests, and evidence map named by
  this plan.
- No compatibility path for evidence Index V1 or the rejected self-authorizing
  V2.
- The expected Authority Lock SHA-256 is supplied only as a literal CLI argument
  from a later non-self-referential launch packet. It is never read from the
  index, lock, repository, environment, or evidence artifacts.
- The implementation plan cannot contain a future Authority Lock SHA-256. The
  later launch packet records both this plan's SHA-256 and the generated lock
  SHA-256.
- Authority Lock and index bytes are untrusted. Verification executes no
  subprocess, shell, socket, indexed command, or code loaded from the evidence
  root. After the running controller manifest and locked registries match the
  external lock, verification may call only those installed, source-hash-
  verified deterministic adapter/input-generator functions through the reviewed
  in-process registry seam. Their subprocess/DNS/socket attempts remain zero.
- `.git`, worktree administration, absolute paths, symlinks, special nodes,
  userinfo, tokens, passwords, authorization headers, and credential-bearing
  metadata never enter the Authority Lock or evidence package.
- Credential scanning applies only to persisted metadata/provenance. Subject
  source containing ordinary identifiers such as `password` or `token` is not a
  credential violation.
- Existing dirty worktree state is the rejected V2 prototype. Preserve its four
  load-bearing RED cases—coordinated reseal, execution relabel, `.git` symlink,
  and credential persistence—but remove its unsafe production implementation by
  targeted edits. Do not use `git reset`, `git checkout --`, or discard unrelated
  bytes.
- Functional RED/GREEN may use the existing offline
  `/opt/anaconda3/bin/python` when local `python3.11` lacks pytest. Record the
  exact Python 3.11 failure; do not claim Python 3.11 test success without it.
- Every task ends with a clean task-scoped commit and independent task review.

## Exact cross-task contracts

These schemas are frozen by this plan. Implementers may factor private helpers,
but may not rename, omit, or add authority fields.

### Authority Lock V1

The exact top-level keys are the ten keys listed in Task 1. Nested objects are:

```text
controller_repository:
  normalized_repository_identity
  base_commit
  base_tree
  tracked_source_manifest_sha256

subjects[] sorted by subject_id:
  subject_id
  repository_role
  normalized_repository_identity
  base_commit
  base_tree
  tracked_source_manifest_sha256
  build_descriptor_sha256
  adapter_id

governing_materials:
  scientific_plan_sha256
  evidence_design_sha256
  authority_lock_design_sha256
  implementation_plan_sha256
  controller_implementation_manifest_sha256

protocol:
  protocol_sha256
  rq_spec_sha256
  claim_ceiling_sha256
  p12_contract_sha256
  operator_catalogue_sha256
  mr_policy_sha256
  site_policy_sha256
  analysis_spec_sha256
  package_policy_sha256
  environment_lock_sha256
  job_derivation_policy_sha256

registries:
  adapter_registry_sha256
  input_generator_registry_sha256

preflight:
  normalized_repository_identity
  base_commit
  base_tree
  dependency_lock_sha256
  environment_policy_sha256
  required_capabilities
  forbidden_credential_fields

claim_policy:
  claim_ceiling_sha256
  required_status
```

Each `jobs[]` row has exactly the ten fields in design Section 5.5. SHA fields
are 64 lowercase hexadecimal except Git commit/tree fields, which are 40
lowercase hexadecimal. Lists are sorted and unique under their declared key.
`required_status` is exactly `blocked`. The lock has no self-hash field.

Every controller/subject manifest has exact keys
`schema_version, role, files`, with schema version
`P3_V3_TRACKED_SOURCE_MANIFEST_V1`. Each sorted `files[]` row has exact keys
`relative_path, mode, sha256`; manifests have no caller self-hash because their
complete canonical bytes are already committed by
`tracked_source_manifest_sha256`.

### Authority Inputs V1

`freeze-authority-lock` accepts canonical JSON with this exact schema:

```text
schema_version = P3_V3_AUTHORITY_INPUTS_V1
task_id
subjects[] sorted by subject_id:
  subject_id
  repository_role
  root
  build_descriptor_path
  adapter_id
governing_material_paths
protocol_artifact_paths
registry_artifact_paths
```

`governing_material_paths` has exactly
`scientific_plan, evidence_design, authority_lock_design, implementation_plan`;
the freezer derives `controller_implementation_manifest_sha256` from the
generated controller manifest. `protocol_artifact_paths` has exactly the eleven
protocol roles above, including `job_derivation_policy`; registry paths have
exactly `adapter_registry` and `input_generator_registry`.
Governing/protocol/registry paths are safe paths relative to
`--controller-root`. A subject root may be absolute or relative to the Authority
Inputs file's parent so separately checked-out repositories remain supported;
the freezer `lstat`s every component, rejects symlinks/special nodes, and never
copies the local path into the lock. Artifact-path absolutes and escapes fail.
Authority Inputs V1 rejects `base_intents`, `jobs`, result/completion
objects, expected lock digests, execution-scope labels, caller-supplied manifest
rows, caller-selected source-root subsets, and caller-supplied Git identities.
The controller role roots are fixed in production to `src/p3_v3`,
`scripts/p3_v3`, and `requirements-frozen.txt`; every subject uses its
complete tracked checkout. Fixed, local, non-network Git queries during freeze
derive normalized repository identity, commit, tree, and the complete
tracked-file set. Those five queries run with a minimal deterministic environment
and command-level configuration that disables fsmonitor, hooks, pagers,
credential helpers, interactive prompting, replacement refs, network protocols,
and optional locks. On Darwin and Linux the Git executable is the fixed
`/usr/bin/git`; every path component and the executable are mechanically checked
as root-owned, non-symlink, and non-group/world-writable, with an executable
regular file at the leaf. No caller `PATH` or other caller-derived execution
environment value is used. Local includes, executable `filter.*.clean/process`
configuration, and out-of-root Git metadata indirection fail before any query.
The fixed-HEAD stage inventory is the only tracked-file list;
each listed file is opened once through an anchored descriptor, and that one
immutable `(bytes, mode)` capture supplies Git binding, the manifest, and every
derived input. There is no second live source read.
Only normalized host/path identity enters the lock; raw remote transport and
userinfo never do.
The lock's `preflight.environment_policy_sha256` must equal
`protocol.environment_lock_sha256`; no second caller-selected environment
authority is accepted. Required capabilities and forbidden credential-field
names are parsed from that exact environment-lock artifact, not copied from
Authority Inputs.

### Job Derivation Policy V1

The canonical policy artifact named by `job_derivation_policy_sha256` has exact
keys:

```text
schema_version = P3_V3_JOB_DERIVATION_POLICY_V1
maximum_attempts
retry_trigger
templates[] sorted by template_id:
  template_id
  phase
  job_role
  object_source
  argv_template
  cwd_role
  environment_role
  input_roles
  seed_rule
  timeout_seconds
  repetition_ids
  execution_class
  p12_access_class
```

`object_source` selects only a prepared, byte-bound inventory from controller,
subjects, registries, or protocol artifacts. Expansion is the sorted Cartesian
product of the selected objects and `repetition_ids`. Every object selected by
one `object_source` must expose the same complete, sorted, unique input-role
set, and the template's `input_roles` must equal that set exactly. It is a
validated declaration of complete consumption, not a caller-controlled subset;
missing or extra roles fail before expansion. Job IDs, argv, cwd
identity, environment hash, input hashes, seed, timeout, and all object/MR/input
identities are derived by production code. No caller supplies a completed base
intent. Current foundation fixtures authorize only `SYNTHETIC_INFRASTRUCTURE`
and `NON_SCIENTIFIC_CONTROL` jobs; a later real-P12 lock requires a separately frozen
P12 inventory and is outside this plan.

The exact execution enums are
`SYNTHETIC_INFRASTRUCTURE`, `NON_SCIENTIFIC_CONTROL`, and `REAL_SCIENTIFIC`;
the exact P12-access enums are `FORBIDDEN`, `PERMITTED`, and `REQUIRED`.
`maximum_attempts` is 3 and `retry_trigger` is exactly
`FAIL_INFRASTRUCTURE`. `authorized_real_p12_job_count` counts locked jobs whose
access is `PERMITTED` or `REQUIRED`.
`recorded_real_scientific_terminal_count` counts reconstructed terminal jobs
whose locked execution class is `REAL_SCIENTIFIC`.
Every locked job must have a result in its final recorded attempt before a final
execution snapshot is valid. Every indexed phase receipt consumes all
reconstructed events for its phase and its expected-job inventory is derived
exactly from the Authority Lock jobs for that phase; neither an index-selected
subset nor a receipt-selected ledger prefix can close a phase.

Registry `implementation_path` is always a safe logical path relative to the
controller root, regardless of the registry artifact's own directory. Freeze,
installed-controller verification, and evidence reconstruction use that same
meaning, including for registries nested below the controller root.

The freezer's internal `PreparedAuthority` is an exact validated value, not a
serialized caller input. It contains:

```text
controller_repository + complete controller manifest
subjects[]:
  Authority Lock subject row
  complete source manifest
  verified build descriptor
  deterministic adapter discovery
  public behavior frame
  profiling workload
  deterministic common-input inventory
governing_materials + governing_artifacts with verified canonical bytes
protocol lock projection + protocol_artifacts with verified canonical bytes
registries lock projection + registry_artifacts with source-hash-verified installed implementations
preflight + parsed environment inventory
claim_policy
objects[] sorted by (object_source, inventory_id):
  object_source
  inventory_id
  subject_id
  object_type
  object_id
  mr_id
  evaluation_input_class
  evaluation_input_id
  inputs[] sorted by role: {role, sha256}
environments[] sorted by environment_role:
  environment_role
  environment_id
  environment_sha256
```

Preparation derives `objects` only from verified subject artifacts and the
locked synthetic-case catalogue in the P12 contract. Current allowed
`object_source` values are `SUBJECT`, `SUBJECT_BEHAVIOR`,
`SUBJECT_COMMON_INPUT`, and `SYNTHETIC_P12_CASE`; no caller-defined selector is
accepted. A future real-P12 selector requires a new externally frozen contract.

Template expansion has no shell syntax. Each `argv_template` item is either a
literal token without `$` or exactly one of
`${protocol_sha256}`, `${subject_id}`, `${object_id}`,
`${evaluation_input_id}`, `${environment_id}`, `${repetition_id}`. Substitution
replaces the complete argv token and never performs interpolation, quoting,
splitting, or evaluation. `cwd_role` is `CONTROLLER_ROOT` or `SUBJECT_ROOT` and
derives the stored identity `controller` or the literal `subject:` prefix
concatenated with `subject_id`—never a local
path. `environment_role` resolves exactly one prepared environment. Every
`input_roles` item resolves exactly one prepared object input, the list equals
the selected source's complete sorted unique role set, and `input_sha256` is
derived from every selected object's input hash before being sorted. No caller
subset can reduce intent authority. `seed_rule` is `NONE` or `REPETITION_ID`.

For each sorted template/object/repetition tuple, the job ID is the full
lowercase SHA-256 of canonical
`{template_id, object_source, inventory_id, repetition_id}`. Phase, job role,
timeout, execution class, and P12 access come from the template; protocol,
environment, inputs, object/MR/evaluation-input identities come from
`PreparedAuthority`; `attempt` is 1. The result must pass the existing exact
`_INTENT_SCHEMA` before its template hash is computed.

### Evidence Index V3 and origin receipt

Evidence Index V3 replaces V2 `preflight` and `execution_scope` with exact,
non-authoritative references:

```text
schema_version = P3_V3_EVIDENCE_INDEX_V3
phase_coverage
controller_source: {root, manifest}
subject_sources[] sorted by subject_id: {subject_id, root, manifest}
protocol
protocol_artifacts
adapter_registries
input_generator_registries
subjects
packages
mr_chain
job_root
ledger
phase_receipts
preflight_event
origin_receipt
p12
claims
artifact_sha256
```

All file fields use the existing exact `{path, sha256}` reference schema; root
fields use safe relative paths. Controller and subject source roots are fully
enumerated and compared to the Authority Lock manifests—no directory subtree is
exempt from symlink/special-node and undeclared-file checks.

The indexed Phase 0 preflight event has exact keys
`schema_version, normalized_repository_identity, base_commit, base_tree,
dependency_lock_sha256, environment_policy_sha256, capability_results,
event_sha256`. The canonical origin receipt has those stable authority fields,
the sorted required-capability projection, `preflight_event_sha256`, and its
ordinary artifact self-hash. Production
`reconstruct_origin_receipt(lock_preflight, preflight_event)` validates the
event, compares every locked stable field, rebuilds the receipt, and raises
`E_AUTHORITY_ORIGIN` on divergence. Raw origin URL, transport, userinfo, and
credential bytes are absent by construction. Local self-hashes preserve package
closure but never replace comparison with the external lock.
Credential scanning is applied before exact-schema projection to Authority
Inputs, Authority Lock, and Evidence Index metadata. It rejects exact and
composite credential keys plus credential-shaped string values such as Bearer
authorization and URI userinfo, without scanning `SourceSnapshot` source text.
`event_sha256` and the receipt artifact hash are computed from their respective
exact objects with only that object's own hash field removed.
Each sorted `capability_results[]` row has exact keys
`capability, status, observation_sha256`; status is `PASS` or `FAIL`. Every
locked required capability appears exactly once with `PASS`. Observations may
describe variable machine state only through their hashes and cannot redefine a
locked identity or policy.

## Pre-implementation recovery gate

The worktree intentionally contains the rejected, uncommitted self-authorizing
V2 prototype in exactly these paths:

```text
docs/release_2026-08-10/p3_v3_mef_align_evidence_map.md
scripts/p3_v3/evidence.py
src/p3_v3/run_records.py
tests/p3_v3/test_cli.py
tests/p3_v3/test_run_records.py
tests/p3_v3/test_synthetic_phase_path.py
```

Before Task 1, the original Task 7 implementer records the current diff SHA in
its existing report, then removes only those uncommitted prototype hunks through
targeted `apply_patch` edits. It must not use reset, checkout, clean, or rewrite
the two committed Authority Lock design commits. The four discoveries are
preserved as explicit RED requirements in Tasks 4 and 5 rather than as unsafe
implementation bytes: coordinated authority reseal, execution-class relabel,
`.git` symlink escape, and credential persistence.

Run before and after the targeted cleanup:

```bash
rtk git diff | rtk shasum -a 256
rtk git rev-parse HEAD
rtk git rev-list --count 248529c053010577aa6b507a5a2c92f547f97140..HEAD
rtk git diff --name-only 248529c053010577aa6b507a5a2c92f547f97140..HEAD
rtk git status --short
```

Before cleanup, require exactly one commit after the design base, require that
its complete changed-path set is only this implementation-plan path, and require
the worktree changed-path set to be exactly the six rejected V2 paths above.
Record the full plan-carrier commit ID. After cleanup, require the same HEAD and
ancestry results plus empty status. This gate creates no commit; Task 1 begins
from the clean plan-carrier commit.

---

### Task 1: Canonical Authority Lock schema, manifests, and safe loader

**Files:**
- Modify: `src/p3_v3/artifacts.py`
- Modify: `scripts/p3_v3/evidence.py`
- Modify: `tests/p3_v3/test_artifacts.py`
- Modify: `tests/p3_v3/test_cli.py`

**Interfaces:**
- Hardens existing:
  `write_canonical_json(path: Path, value: Any, exclusive=True) -> None` so a
  failed exclusive create never exposes a partial final path.
- Produces:
  `read_canonical_regular_bytes(path: Path, context: str) -> bytes`.
- Produces:
  `read_canonical_regular_json(path: Path, context: str) -> dict[str, Any]`.
- Produces:
  `build_tracked_source_manifest(root: Path, role_roots: Sequence[str], role: str) -> dict[str, Any]`.
- Produces:
  `validate_authority_lock(lock: Mapping[str, Any]) -> dict[str, Any]`.
- Produces:
  `load_authority_lock(lock_path: Path, expected_sha256: str) -> dict[str, Any]`.
- Consumes existing `canonical_json_bytes`, `validate_exact_object`,
  `validate_sha256`, `safe_relative_path`, and
  `write_canonical_json(..., exclusive=True)`.

- [ ] **Step 1: Verify the clean implementation base**

Run:

```bash
rtk git rev-parse HEAD
rtk git rev-list --count 248529c053010577aa6b507a5a2c92f547f97140..HEAD
rtk git diff --name-only 248529c053010577aa6b507a5a2c92f547f97140..HEAD
rtk git status --short
```

Require the recorded plan-carrier HEAD, exactly one commit since the fixed design
base, only this plan path in that committed delta, and empty status. The recovery
record, not the now-clean worktree, identifies the four rejected V2 discoveries
that Tasks 4 and 5 must reproduce as fresh RED tests.

- [ ] **Step 2: Write safe canonical-file RED tests**

Add tests equivalent to:

```python
def test_authority_lock_reader_rejects_symlink_and_special_nodes(tmp_path):
    target = tmp_path / "lock.json"
    write_canonical_json(target, {"schema_version": "P3_V3_AUTHORITY_LOCK_V1"}, exclusive=True)
    link = tmp_path / "lock-link.json"
    link.symlink_to(target)
    with pytest.raises(EvidenceError, match="E_AUTHORITY_LOCK_PATH"):
        read_canonical_regular_json(link, "authority lock")


def test_subject_source_words_are_not_credential_metadata(tmp_path):
    source = tmp_path / "subject.py"
    source.write_text("password = token\n", encoding="utf-8")
    manifest = build_tracked_source_manifest(
        tmp_path, ["."], "subject-source"
    )
    assert manifest["files"][0]["relative_path"] == "subject.py"
```

The first test must cover a symlinked parent, file symlink, FIFO/special node,
and noncanonical bytes. Add injected short-write, link failure, existing-target,
and directory-fsync failures. Before the atomic publish point, the final target
must be absent and temporary files must be removed; after a successful publish,
the target must contain all canonical bytes. Metadata-specific credential tests
belong in Step 4.

- [ ] **Step 3: Run the safe-file RED**

Run:

```bash
rtk env PYTHONPATH=src python3.11 -m pytest tests/p3_v3/test_artifacts.py -q -k 'authority_lock or canonical_regular or credential_metadata'
```

If pytest is unavailable, record that failure and run:

```bash
rtk env PYTHONPATH=src /opt/anaconda3/bin/python -m pytest tests/p3_v3/test_artifacts.py -q -k 'authority_lock or canonical_regular or credential_metadata'
```

Expected functional result: failures because the safe Authority Lock reader does
not exist.

- [ ] **Step 4: Write manifest and exact-schema RED tests**

Use the exact top-level keys:

```python
AUTHORITY_LOCK_KEYS = {
    "schema_version",
    "task_id",
    "controller_repository",
    "subjects",
    "governing_materials",
    "protocol",
    "registries",
    "preflight",
    "jobs",
    "claim_policy",
}
```

Use `schema_version == "P3_V3_AUTHORITY_LOCK_V1"`. Tests must prove:

- controller and two subjects have independent canonical manifests with exact
  `(relative_path, mode, sha256)` rows;
- controller manifest covers `src/p3_v3`, `scripts/p3_v3`, and the dependency
  lock used by verification;
- the manifest builder recursively inventories every node under exact role
  roots; a caller cannot omit an individual file by supplying a selective list;
- subject manifests use the complete prepared subject root, exclude only the
  ordinary `.git` directory, include vendor/fixture/generated source, and fail
  closed on transient environment/build directories;
- missing, extra, swapped, duplicated, or symlinked subject/manifests fail;
- `.git` and worktree files never enter a manifest;
- raw origin userinfo and metadata fields named `token`, `password`,
  `authorization`, or `credential` fail without echoing their values;
- a source file containing those words remains valid source;
- the lock rejects every missing/extra top-level or nested key; and
- changing any lock byte while retaining the expected digest fails before a
  lock field is exposed.

- [ ] **Step 5: Run manifest and lock RED tests**

Run:

```bash
rtk env PYTHONPATH=src /opt/anaconda3/bin/python -m pytest tests/p3_v3/test_artifacts.py tests/p3_v3/test_cli.py -q -k 'authority_lock or freeze_authority or controller_manifest or subject_manifest'
```

Expected: functional failures at missing manifest/loader interfaces, not at a
stale fixture hash.

- [ ] **Step 6: Implement the safe reader, manifest builder, validator, and loader**

The safe reader must `lstat` every path component, require one regular file,
read canonical bytes once, and return the parsed exact object. The manifest
builder recursively walks exact role roots, rejects overlapping or missing
roots, symlinks, special nodes, transient environment/build paths, and any
selective omission; it sorts all included regular files by UTF-8 relative path.
Harden the writer's exclusive branch by writing and fsyncing a same-directory
temporary regular file, publishing it with an atomic no-replace hard link,
unlinking the temporary name, and fsyncing the parent directory. Any failure
before the link leaves the final path absent; an existing target is never
overwritten; cleanup never removes a successfully published target.
An existing target retains `E_EXISTS`; other create-new failures are wrapped as
`E_ARTIFACT_WRITE` without printing payload bytes.
The loader must:

```python
def load_authority_lock(lock_path, expected_sha256):
    validate_sha256(expected_sha256, "authority_lock_sha256")
    raw = read_canonical_regular_bytes(lock_path, "authority lock")
    if hashlib.sha256(raw).hexdigest() != expected_sha256:
        raise EvidenceError("E_AUTHORITY_LOCK_DIGEST", "authority lock digest differs")
    value = json.loads(raw.decode("utf-8"))
    if canonical_json_bytes(value) != raw:
        raise EvidenceError("E_AUTHORITY_LOCK_SCHEMA", "authority lock is noncanonical")
    return validate_authority_lock(value)
```

`validate_authority_lock` validates all exact schemas, SHA formats, canonical
ordering, enum membership, and cross-field uniqueness. Job rows receive
structural validation here; Task 2 supplies their semantic derivation and
execution checks. The lock contains no caller self-hash.

- [ ] **Step 7: Run Task 1 GREEN and regression tests**

Run:

```bash
rtk env PYTHONPATH=src /opt/anaconda3/bin/python -m pytest tests/p3_v3/test_artifacts.py tests/p3_v3/test_cli.py -q -k 'authority_lock or controller_manifest or subject_manifest or credential'
rtk env PYTHONPATH=src /opt/anaconda3/bin/python -m pytest tests/p3_v3/test_artifacts.py tests/p3_v3/test_cli.py -q
rtk /Users/limeng/.cache/uv/archive-v0/mkYBmriZUfC1J9rk4DpCr/ruff-0.15.12.data/scripts/ruff check src/p3_v3/artifacts.py scripts/p3_v3/evidence.py tests/p3_v3/test_artifacts.py tests/p3_v3/test_cli.py
rtk git diff --check
```

- [ ] **Step 8: Commit Task 1**

```bash
rtk git add src/p3_v3/artifacts.py scripts/p3_v3/evidence.py tests/p3_v3/test_artifacts.py tests/p3_v3/test_cli.py
rtk git commit -m 'feat(p3-v3): validate external authority lock'
```

---

### Task 2: Locked intent templates, retry policy, and observational completion

**Files:**
- Modify: `src/p3_v3/run_records.py`
- Modify: `scripts/p3_v3/evidence.py`
- Modify: `tests/p3_v3/test_run_records.py`
- Modify: `tests/p3_v3/test_cli.py`

**Interfaces:**
- Consumes Task 1 validated Authority Lock and canonical locked `jobs` rows.
- Produces:
  `intent_template_sha256(intent: Mapping[str, Any]) -> str`.
- Produces:
  `derive_base_intents(prepared_authority: Mapping[str, Any], job_derivation_policy: Mapping[str, Any]) -> list[dict[str, Any]]`.
- Produces:
  `derive_locked_jobs(prepared_authority: Mapping[str, Any], job_derivation_policy: Mapping[str, Any]) -> list[dict[str, Any]]`.
- Produces:
  `reconstruct_attempt_records(job_root: Path) -> list[dict[str, Any]]` with
  exact validated intent/result pairs.
- Produces:
  `verify_locked_execution(locked_jobs: Sequence[Mapping[str, Any]], job_root: Path, ledger_path: Path) -> dict[str, Any]`.
- Returns exact completion keys
  `authorized_real_p12_job_count` and
  `recorded_real_scientific_terminal_count`.

The canonical Job Derivation Policy V1 is byte-indexed by the Authority Lock's
exact `protocol` mapping and has the exact cross-task schema above. It has no
caller self-hash. It specifies derivation templates, not completed jobs or
intents; its exact canonical bytes are bound by
`job_derivation_policy_sha256`.

- [ ] **Step 1: Remove unsafe execution-scope authority**

Delete the rejected V2 production path that accepts a self-hashed
`execution_scope` as authority. Preserve its coordinated relabel test and change
the expected result from PASS/test-helper rejection to production
`E_AUTHORITY_EXECUTION_CLASS`.

- [ ] **Step 2: Write complete-intent and retry RED tests**

Parameterize every intent field already frozen by `_INTENT_SCHEMA`. For each
field other than `attempt`, mutate it, preserve job/input IDs when possible,
recompute all local hashes, and require `E_AUTHORITY_INTENT`.

Add Authority Inputs mutations proving that a caller-supplied `base_intents`,
`jobs`, completed intent row, execution class, or P12-access class is rejected
before inventory derivation. Mutate each prepared subject/protocol/registry
input and prove that the mechanically derived intent and locked job change or
fail; there is no path that simply accepts the caller's old intent. Add a real
`prepare_authority` -> `_subject_objects` -> `derive_locked_jobs` test that
commits tracked subject-source, selected-registry, and common-behavior drift and
proves that the complete derived input list, intent template, and locked job
change or fail. A direct mutation of a preconstructed `objects` mapping is not
sufficient evidence for this boundary.

Add explicit tests equivalent to:

```python
def test_intent_template_removes_only_attempt():
    first = _intent(attempt=1)
    retry = dict(first, attempt=2)
    assert intent_template_sha256(first) == intent_template_sha256(retry)
    assert intent_template_sha256(first) != intent_template_sha256(
        dict(first, seed=first["seed"] + 1)
    )


def test_locked_retry_requires_preceding_infrastructure_failure():
    job_root, ledger = _scientific_retry_attempt_tree()
    with pytest.raises(EvidenceError, match="E_AUTHORITY_INTENT"):
        verify_locked_execution(
            _locked_jobs(maximum_attempts=3), job_root, ledger
        )
```

Cover maximum attempt 3, attempt 4, noncontiguous attempts, retry after PASS,
retry after scientific failure, job omission/addition/duplication, and terminal
result without a locked base job.

- [ ] **Step 3: Run Task 2 RED**

```bash
rtk env PYTHONPATH=src /opt/anaconda3/bin/python -m pytest tests/p3_v3/test_run_records.py tests/p3_v3/test_cli.py -q -k 'authority_intent or locked_job or observational_completion or execution_relabel'
```

Expected: the current `execution_scope` path either passes coordinated relabels
or lacks the new locked-job interfaces.

- [ ] **Step 4: Implement locked intent and execution reconstruction**

`derive_base_intents` expands the frozen Job Derivation Policy V1 over only the
prepared, byte-bound object inventories. It derives every `_INTENT_SCHEMA`
field, sorts by job ID, and rejects duplicate expansions or a template that
names an unavailable object/input/environment role. Objects sharing an
`object_source` must have one identical sorted unique input-role set; every
template naming that source must declare exactly that complete set, and the
derived `input_sha256` contains every object input digest. `intent_template_sha256`
validates one derived production intent, removes only `attempt`, and hashes
canonical bytes. `derive_locked_jobs` first calls `derive_base_intents`, then
emits:

```python
{
    "job_id": intent["job_id"],
    "phase": intent["phase"],
    "job_role": intent["job_role"],
    "object_identity": f'{intent["object_type"]}:{intent["object_id"]}',
    "input_identity_sha256": canonical_sha256(intent["input_sha256"]),
    "intent_template_sha256": intent_template_sha256(intent),
    "maximum_attempts": job_derivation_policy["maximum_attempts"],
    "retry_trigger": job_derivation_policy["retry_trigger"],
    "execution_class": expanded_template["execution_class"],
    "p12_access_class": expanded_template["p12_access_class"],
}
```

Execution and access classes derive from the frozen template that produced the
intent, never from results, cwd, or a separate label artifact.
`verify_locked_execution` reuses the existing attempt tree and retry reducer,
reconstructs each exact intent/result pair from `job_root`, proves its canonical
event hashes and order equal `ledger_path`, compares every terminal intent
template, and returns only observational counts. Compact ledger events alone are
never treated as sufficient intent authority.

- [ ] **Step 5: Run Task 2 GREEN and regression tests**

```bash
rtk env PYTHONPATH=src /opt/anaconda3/bin/python -m pytest tests/p3_v3/test_run_records.py tests/p3_v3/test_cli.py -q -k 'authority_intent or locked_job or retry or observational_completion or execution_relabel'
rtk env PYTHONPATH=src /opt/anaconda3/bin/python -m pytest tests/p3_v3/test_run_records.py -q
rtk /Users/limeng/.cache/uv/archive-v0/mkYBmriZUfC1J9rk4DpCr/ruff-0.15.12.data/scripts/ruff check src/p3_v3/run_records.py scripts/p3_v3/evidence.py tests/p3_v3/test_run_records.py tests/p3_v3/test_cli.py
rtk git diff --check
```

- [ ] **Step 6: Commit Task 2**

```bash
rtk git add src/p3_v3/run_records.py scripts/p3_v3/evidence.py tests/p3_v3/test_run_records.py tests/p3_v3/test_cli.py
rtk git commit -m 'fix(p3-v3): bind locked jobs and completion'
```

---

### Task 3: Deterministic two-pass freezer and freeze CLI

**Files:**
- Modify: `scripts/p3_v3/evidence.py`
- Modify: `tests/p3_v3/test_cli.py`
- Modify: `tests/p3_v3/test_artifacts.py`

**Interfaces:**
- Consumes Task 1 manifest/lock validators and Task 2 `derive_base_intents` /
  `derive_locked_jobs`.
- Produces:
  `prepare_authority(controller_root: Path, authority_inputs: Mapping[str, Any]) -> dict[str, Any]` with the exact internal `PreparedAuthority` contract.
- Produces:
  `build_authority_lock(controller_root: Path, authority_inputs: Mapping[str, Any]) -> dict[str, Any]`.
- Produces:
  `freeze_authority_lock(controller_root: Path, authority_inputs_path: Path, output_path: Path) -> dict[str, Any]`.
- Adds CLI
  `freeze-authority-lock --controller-root ROOT --authority-inputs FILE --output FILE`.

- [ ] **Step 1: Write two-pass determinism and atomicity RED tests**

Tests must prove:

- differently ordered but semantically identical authority inputs freeze to
  byte-identical locks;
- Authority Inputs V1 exact top-level and nested schemas reject every missing,
  extra, duplicated, reordered, unsafe-path, and forbidden direct-intent field;
- preparation validates controller, every subject, governing materials,
  protocol/policies, registries, preflight data, and derivation inventories
  before output;
- inventory derivation uses Task 2 and cannot accept caller-provided base
  intents, `intent_template_sha256`, execution class, or P12-access class;
- no profiling, P12, mutant, MR, scientific executable, or network call occurs
  during freeze; the only subprocesses permitted are fixed local Git identity,
  tree, origin-normalization, and tracked-file queries constructed by production
  code, never by Authority Inputs text;
- for controller and every subject checkout, the exact read-only Git query set
  is `rev-parse HEAD`, then `rev-parse <captured-commit>^{tree}`, followed by
  `status --porcelain=v1 --ignore-submodules=all`, `remote get-url origin`, and
  `ls-files --stage -z`; each tracked row is parsed
  as exact `(mode, blob_oid, stage=0, path)` authority, and one anchored live-byte
  snapshot must match its fixed-HEAD Git blob SHA-1 and regular-file mode before
  the same explicit immutable `(relative_path, mode, sha256, content)` values feed
  manifest, adapter discovery, frame, scale, workload, common-input, and site
  derivation without temporary materialization or later source-root reads. Every
  query carries the deterministic environment and command-level safeguards
  specified above; repository fsmonitor/hook/helper/pager/filter/submodule
  configuration cannot spawn a child, local includes, executable filters, and
  out-of-root metadata fail before queries, and no sixth subprocess is permitted.
  Nonzero exit, dirty status, malformed
  output, credential-bearing normalized identity, or live/fixed-HEAD byte/mode
  drift fails before output;
- source-hash-verified deterministic adapters may run only through the reviewed
  in-process registry interface;
- raw Git origin/userinfo is normalized in memory and absent from output;
- create-new output refuses overwrite; and
- an injected write failure leaves no readable partial output while the parent
  directory is fsynced by the existing canonical writer.

- [ ] **Step 2: Run Task 3 RED**

```bash
rtk env PYTHONPATH=src /opt/anaconda3/bin/python -m pytest tests/p3_v3/test_cli.py tests/p3_v3/test_artifacts.py -q -k 'freeze_authority or authority_determinism or authority_atomicity or freeze_zero_execution'
```

Expected: missing freezer/CLI failures after Task 1 and Task 2 remain GREEN.

- [ ] **Step 3: Implement deterministic lock construction**

Use this ordering inside `prepare_authority` and `build_authority_lock`:

```python
inputs = validate_authority_inputs(authority_inputs)
prepared = prepare_authority(controller_root, inputs)
jobs = derive_locked_jobs(prepared, prepared["job_derivation_policy"])
return validate_authority_lock({
    "schema_version": "P3_V3_AUTHORITY_LOCK_V1",
    "task_id": inputs["task_id"],
    "controller_repository": prepared["controller_repository"],
    "subjects": [row["authority_row"] for row in prepared["subjects"]],
    "governing_materials": prepared["governing_materials"],
    "protocol": prepared["protocol"],
    "registries": prepared["registries"],
    "preflight": prepared["preflight"],
    "jobs": jobs,
    "claim_policy": prepared["claim_policy"],
})
```

The internal helper names may remain private, but the ordering, data authority,
and output schema are fixed. `prepare_authority` retains the verified canonical
bytes and derived inventories required by Task 2; the lock projection keeps only
their externally committed identities. The freezer validates Authority Inputs
V1 before any Git query, and no caller-provided completed intent enters the
prepared value. No future lock digest is embedded.

- [ ] **Step 4: Implement exclusive freeze and thin CLI**

```python
def freeze_authority_lock(controller_root, authority_inputs_path, output_path):
    inputs = read_canonical_regular_json(authority_inputs_path, "authority inputs")
    lock = build_authority_lock(controller_root, inputs)
    write_canonical_json(output_path, lock, exclusive=True)
    return lock
```

CLI stdout contains only `authority_lock_sha256`,
`controller_manifest_sha256`, and `subject_count`.

- [ ] **Step 5: Run Task 3 GREEN and regression tests**

```bash
rtk env PYTHONPATH=src /opt/anaconda3/bin/python -m pytest tests/p3_v3/test_cli.py tests/p3_v3/test_artifacts.py tests/p3_v3/test_run_records.py -q -k 'freeze_authority or authority_lock or locked_job'
rtk /Users/limeng/.cache/uv/archive-v0/mkYBmriZUfC1J9rk4DpCr/ruff-0.15.12.data/scripts/ruff check scripts/p3_v3/evidence.py tests/p3_v3/test_cli.py tests/p3_v3/test_artifacts.py
rtk git diff --check
```

- [ ] **Step 6: Commit Task 3**

```bash
rtk git add scripts/p3_v3/evidence.py tests/p3_v3/test_cli.py tests/p3_v3/test_artifacts.py
rtk git commit -m 'feat(p3-v3): freeze external authority lock'
```

---

### Task 4: Final verifier integration and zero-execution security gate

**Files:**
- Modify: `scripts/p3_v3/evidence.py`
- Modify: `tests/p3_v3/test_cli.py`
- Modify: `tests/p3_v3/test_preflight.py`

**Interfaces:**
- Consumes Task 1 `load_authority_lock`, Task 2
  `verify_locked_execution`.
- Produces:
  `verify_running_controller(lock: Mapping[str, Any], controller_manifest: Mapping[str, Any], locked_registries: Mapping[str, Any]) -> dict[str, Any]`, which
  derives the controller root from the installed evidence module, compares every
  manifest-named runtime byte, and resolves only installed locked registries.
- Produces:
  `reconstruct_origin_receipt(lock_preflight: Mapping[str, Any], preflight_event: Mapping[str, Any]) -> dict[str, Any]`.
- Changes `verify-evidence` interface to require `--index`,
  `--authority-lock`, and `--authority-lock-sha256`.
- Migrates only to the exact Evidence Index V3 contract above. It adds exact
  references for controller/subject source roots and manifests plus the
  canonical origin receipt; it removes V2 `preflight` and `execution_scope` and
  never contains or repeats the expected Authority Lock digest.

- [ ] **Step 1: Write external-digest and coordinated-reseal RED tests**

Through the real CLI, require:

- missing or malformed `--authority-lock-sha256` fails before index loading;
- changed lock with unchanged expected digest fails `E_AUTHORITY_LOCK_DIGEST`;
- changed lock and fully reclosed index/protocol/receipts still fail the digest;
- changed origin receipt with all package-local hashes reclosed fails
  `E_AUTHORITY_ORIGIN`;
- changed Phase 0 preflight event with its event/receipt/index hashes all
  reclosed still fails `E_AUTHORITY_ORIGIN` against the lock's stable fields;
- controller/subject source replacement with a reclosed index fails
  `E_AUTHORITY_MANIFEST`; and
- installed-controller or installed adapter bytes differing from the lock fail
  before any adapter call;
- execution relabel with reclosed completion fails
  `E_AUTHORITY_EXECUTION_CLASS`.

The positive CLI call constructs `expected_lock_sha256` in the Python test and
passes that exact string as an argv element. No shell variable or environment
lookup is allowed.

- [ ] **Step 2: Write the no-execution and credential RED tests**

Invoke the production parser/dispatch/verifier in the pytest process—never via a
child CLI process—and patch `subprocess.run`, `subprocess.Popen`, `os.system`,
`socket.socket`, `socket.create_connection`, `socket.getaddrinfo`, and every
existing executor seam with spies. Use a valid lock/index whose untrusted string
fields contain plausible argv and URL text. Verification must either validate
harmless data or reject its schema, while every process, DNS, connection, and
socket attempt counter remains exactly zero. A separate parser test verifies the
three required CLI arguments without weakening the in-process spy boundary.
Record installed deterministic adapter/generator invocation counts separately;
the positive subject path must use the lock-matched installed implementations,
while any loader rooted under the evidence package has count zero.

Add metadata fixtures for HTTPS userinfo, bearer token, authorization field,
`.git/config`, symlinked manifest, and out-of-root path. Assert that neither
stderr nor stdout includes the secret value.

- [ ] **Step 3: Run Task 4 RED**

```bash
rtk env PYTHONPATH=src /opt/anaconda3/bin/python -m pytest tests/p3_v3/test_cli.py tests/p3_v3/test_preflight.py -q -k 'external_authority or coordinated_reseal or no_execution or authority_origin or authority_manifest or authority_credential'
```

Expected: current sole-index or rejected V2 paths either accept a coordinated
rewrite, execute an indexed command, or lack required authority arguments.

- [ ] **Step 4: Integrate lock-first final verification**

Update parser and dispatch so the first semantic operation is:

```python
validated_lock = load_authority_lock(
    Path(args.authority_lock), args.authority_lock_sha256
)
```

Only after lock validation may a pure `_load_evidence_index` run. It accepts
only V3 exact keys and first loads the controller manifest and registry bytes;
their canonical SHA-256s must match the lock. Before any in-process adapter
call, `verify_running_controller` compares every manifest-named runtime byte and
installed registry implementation with those locked bytes. No implementation
path under the evidence root is executable. Index loading then exhaustively
enumerates each controller/subject
source root, and compares the resulting canonical manifests and locked SHA-256s.
Match controller and subject IDs one-to-one, load the separately indexed exact
`preflight_event`, call `reconstruct_origin_receipt`, compare the declared
receipt bytes, call `verify_locked_execution` with the indexed `job_root` and
`ledger`, then execute the existing
package/ledger/phase/P12/claim reconstruction gates. Subject rederivation calls
only the installed, lock-matched deterministic registry functions. No raw
transport or Git metadata is read, and subprocess/DNS/socket spies remain zero
during those calls.

The PASS object contains only:

```python
{
    "status": "PASS",
    "authority_lock_sha256": args.authority_lock_sha256,
    "evidence_index_sha256": file_sha256(args.index),
    "subject_count": len(validated_lock["subjects"]),
    "authorized_real_p12_job_count": completion[
        "authorized_real_p12_job_count"
    ],
    "recorded_real_scientific_terminal_count": completion[
        "recorded_real_scientific_terminal_count"
    ],
    "claims_status": "blocked",
}
```

Do not emit `real_p12_access: false` or claim physical absence.

- [ ] **Step 5: Run Task 4 GREEN and complete related regression tests**

```bash
rtk env PYTHONPATH=src /opt/anaconda3/bin/python -m pytest tests/p3_v3/test_cli.py tests/p3_v3/test_preflight.py tests/p3_v3/test_run_records.py -q -k 'authority or preflight or verify_evidence or execution_scope or completion'
rtk env PYTHONPATH=src /opt/anaconda3/bin/python -m pytest tests/p3_v3/test_cli.py tests/p3_v3/test_preflight.py tests/p3_v3/test_run_records.py -q
rtk /Users/limeng/.cache/uv/archive-v0/mkYBmriZUfC1J9rk4DpCr/ruff-0.15.12.data/scripts/ruff check scripts/p3_v3/evidence.py tests/p3_v3/test_cli.py tests/p3_v3/test_preflight.py
rtk git diff --check
```

- [ ] **Step 6: Commit Task 4**

```bash
rtk git add scripts/p3_v3/evidence.py tests/p3_v3/test_cli.py tests/p3_v3/test_preflight.py
rtk git commit -m 'fix(p3-v3): verify evidence against authority lock'
```

---

### Task 5: Two-subject root-of-trust matrix and evidence map

**Files:**
- Modify: `tests/p3_v3/test_synthetic_phase_path.py`
- Modify: `tests/p3_v3/test_artifacts.py`
- Modify: `tests/p3_v3/test_cli.py`
- Modify: `docs/release_2026-08-10/p3_v3_mef_align_evidence_map.md`

**Interfaces:**
- Consumes Task 3 freeze CLI and Task 4 verify CLI.
- Produces one synthetic Authority Lock for two subject
  repositories/materializations and passes its independently computed digest as
  a literal argv value.
- Produces no real P12, mutant, MR, network, or scientific evidence.

- [ ] **Step 1: Replace the rejected V2 synthetic fixture**

Remove fixture-only origin/completion oracles, indexed command execution,
`.git` indexing, and caller-controlled execution-scope authority. Build the
fixture in this order:

1. Python PEP 517/S subject and CMake/CTest/M subject;
2. controller and per-subject canonical manifests;
3. governing/policy/registry and preflight authority inputs;
4. prepared deterministic subject/object/environment inventories and the
   locked Job Derivation Policy V1—never completed caller intents;
5. `freeze-authority-lock`, which derives base intents/jobs, and an independently
   computed lock digest;
6. Phase 0-7 attempt tree, ledger, receipts, packages, slots, MR chain, P12
   synthetic denominator/results/summary, blocked claims, and evidence index;
7. final `verify-evidence` with all three required authority arguments.

- [ ] **Step 2: Preserve and extend the rehash-resistant matrix**

Retain the existing 22 scientific-evidence mutations and add exact root tests:

- lock-only mutation;
- lock plus complete evidence reseal under the original external digest;
- coordinated origin/protocol/attempt/ledger/receipt/index reseal;
- coordinated execution-role/completion relabel;
- controller omission and subject swap;
- each complete intent field and retry transition;
- lock/index symlink and special node;
- `.git` and credential metadata;
- command-like untrusted strings with subprocess/socket spy counts zero; and
- subject source containing `password = token` without metadata false positive.

Every test recomputes package-local hashes and asserts the exact production error
or zero-execution property.

- [ ] **Step 3: Run the synthetic RED then GREEN matrix**

```bash
rtk env PYTHONPATH=src python3.11 -m pytest tests/p3_v3/test_synthetic_phase_path.py -q
rtk env PYTHONPATH=src /opt/anaconda3/bin/python -m pytest tests/p3_v3/test_synthetic_phase_path.py -q
```

The Python 3.11 environment failure is recorded if unchanged. Functional GREEN
requires one positive path and every mutation passing its expected rejection.

- [ ] **Step 4: Rewrite the evidence map**

For each Authority Lock design requirement, cite:

- exact production function;
- exact positive test node;
- exact mutation test node; and
- the two-subject end-to-end node.

The map states that verified zero counts mean authorized/recorded counts only,
that no platform physical-absence claim is made, and that all scientific claims
remain blocked. Remove every reference to test-only reconstruction helpers and
the rejected V2 execution scope.

- [ ] **Step 5: Run complete Task 5 acceptance**

```bash
rtk env PYTHONPATH=src /opt/anaconda3/bin/python -m pytest tests/p3_v3 -q
rtk env PYTHONPATH=src /opt/anaconda3/bin/python -m pytest -q
rtk /Users/limeng/.cache/uv/archive-v0/mkYBmriZUfC1J9rk4DpCr/ruff-0.15.12.data/scripts/ruff check src/p3_v3 scripts/p3_v3 tests/p3_v3
rtk git diff --check 9f28080c8b3ed9e25f96a0fcf0444bc92715ca76
rtk git status --short
```

If the repository suite remains blocked by the independently confirmed
statsmodels/SciPy environment mismatch, record the exact collection error and do
not claim repository-suite PASS. No installation or network repair is
authorized.

- [ ] **Step 6: Commit Task 5**

```bash
rtk git add tests/p3_v3/test_synthetic_phase_path.py tests/p3_v3/test_artifacts.py tests/p3_v3/test_cli.py docs/release_2026-08-10/p3_v3_mef_align_evidence_map.md
rtk git commit -m 'test(p3-v3): close authority lock evidence matrix'
```

---

### Task 6: Frozen-commit verification and independent dual audit

**Files:**
- Create only git-ignored SDD reports and review packages under this plan's
  `.superpowers/sdd` workspace.
- Do not modify production, test, design, plan, or evidence-map bytes during the
  audit.

**Interfaces:**
- Consumes the clean Task 5 commit.
- Produces a fixed commit/tree/design/plan identity, fresh verification report,
  and two independent read-only audit verdicts.
- Does not push, create a PR, merge, access P12, or launch Cursor VM.

- [ ] **Step 1: Freeze identities before audit**

Run and record:

```bash
rtk git rev-parse HEAD
rtk git rev-parse HEAD^{tree}
rtk shasum -a 256 docs/superpowers/specs/2026-08-11-p3-v3-external-authority-lock-design.md docs/superpowers/plans/2026-08-11-p3-v3-external-authority-lock-implementation.md
rtk git status --porcelain=v1
rtk git diff --check 9f28080c8b3ed9e25f96a0fcf0444bc92715ca76
```

Status must be empty. Any moving target restarts the audit from a newly frozen
identity; it does not inherit an earlier verdict.

- [ ] **Step 2: Run fresh verification**

Run the Task 5 acceptance commands again without modifying files. Record exact
Python versions, test counts, Ruff version, environment-only blockers, and zero
network/P12/scientific execution.

- [ ] **Step 3: Run independent specification/research-evidence audit**

The audit checks non-circular external anchoring, claim ceiling, multi-subject
authority, complete intent/retry binding, observational completion semantics,
rehash-resistant mutations, and evidence-map traceability. Any load-bearing
finding blocks completion.

- [ ] **Step 4: Run independent operational/security audit**

The audit checks canonical/safe I/O, atomic create-new freeze, no symlink/special
node traversal, no credential persistence, literal external digest use,
subprocess/socket spy zero, CLI ordering, no V1/V2 fallback, and worktree
cleanliness. Any load-bearing finding blocks completion.

- [ ] **Step 5: Recheck frozen identities**

Repeat Step 1. Both audits apply only if commit, tree, design/plan hashes, and
clean status are unchanged.

- [ ] **Step 6: Record the terminal state**

The only successful infrastructure verdict is:

```text
P3_V3_EXTERNAL_AUTHORITY_LOCK_IMPLEMENTATION_COMPLETE
claims_status: blocked
real_p12_access: not_attested
authorized_real_p12_job_count: 0
recorded_real_scientific_terminal_count: 0
push: not_authorized
cursor_vm: not_authorized
```

Do not produce a Cursor VM launch packet or scientific-execution authorization
in this plan.

### Task 6 Repair D: Final operational closure

The final operational audit identified five fail-closed gaps, repaired together
under RED/GREEN tests:

- final execution snapshots require a result for every locked job's final
  attempt, and phase receipts consume the complete phase event set with the
  Authority Lock's exact phase job inventory;
- the five freezer Git subprocesses use deterministic environment and
  command-level safeguards, reject includes/out-of-root metadata, and remain the
  only subprocesses at that boundary;
- registry implementation paths have one controller-root-relative meaning in
  freeze and verification, with nested registries covered positively;
- composite credential keys and Bearer/userinfo-shaped metadata values fail at
  the Authority Inputs, lock, and index boundaries while source snapshots remain
  outside metadata scanning; and
- each tracked checkout file is captured once through the anchored reader, with
  one immutable snapshot supplying fixed-HEAD verification, manifests, and all
  derived authority inputs.

The repair changes no Authority Lock, Authority Inputs, Evidence Index, receipt,
or result schema fields. It strengthens derivation, path interpretation, and
verification only. Scientific execution, P12 access, claim upgrades, network,
push, PR, and merge remain unauthorized.

### Task 6 Repair D2: Fixed executable and metadata-execution closure

The independent D2 review tightened three existing boundaries without changing
any artifact schema:

- Darwin and Linux freeze use only the mechanically validated absolute
  `/usr/bin/git`, never caller `PATH`; the five subprocesses receive a literal
  minimal environment with pagers disabled rather than executable pager names.
- The safe local `.git/config` and `.git/config.worktree` bytes are inspected
  before the first subprocess. Modern `[filter "name"]` and legacy
  `[filter.name]` sections defining `clean` or `process` both fail closed, and
  the status query explicitly includes
  `--ignore-submodules=all`. The query count remains exactly five and neither
  filter nor submodule configuration may produce a child process.
- Credential-metadata component scanning covers `key` and `secret`, including
  snake-case and camel-case forms such as `api_key`, `apiKey`, and
  `client_secret`, with stable `E_CREDENTIAL_METADATA` precedence at Authority
  Inputs, lock, and Evidence Index boundaries. The exact
  `forbidden_credential_fields` policy key remains exempt, and SourceSnapshot
  source bytes remain outside metadata scanning.
