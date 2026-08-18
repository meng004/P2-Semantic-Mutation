# Cursor VM C++ Link Qualification Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a one-shot, fail-closed runner that determines whether a fresh
Cursor VM can compile, link, and execute one fixed C++14 program without
running CMake, Boost.Math, or build-preflight attempt-2.

**Architecture:** Add one deep module whose external interface is
`run_qualification`. It owns preconditions, canonical evidence, process-group
control, no-retry ordering, and terminal publication. A zero-argument script
is a thin adapter; tests exercise the module through injected compiler
resolution and process adapters.

**Tech Stack:** Python 3.11+, standard library, existing
`p3_v3.artifacts` canonical JSON helpers, pytest.

## Global Constraints

- Implement against specification
  `docs/superpowers/specs/2026-08-18-p3-cursor-vm-cxx-link-qualification-design.md`
  with SHA-256
  `ff438a10da0e762667fe358fb32082e2338f39f28c16620d5a15d8890e8dd8d5`.
- Create only:
  - `src/p3_v3/toolchain_qualification.py`
  - `tests/p3_v3/test_toolchain_qualification.py`
  - `scripts/p3_v3/qualify_cxx_link.py`
- Do not modify `src/p3_v3/pilot_build.py`, `scripts/p3_v3/pilot.py`, their
  tests, attempt-1 artifacts, authority files, claims, or the approved spec.
- Production qualification root is exactly
  `/tmp/p3-cxx-link-qualification`.
- Frozen source bytes are exactly `b"int main(){return 0;}\n"`.
- Compile-link timeout is 60 seconds; binary-run timeout is 10 seconds.
- The single compiler-version metadata invocation has a fixed timeout of
  10 seconds. Timeout writes terminal evidence and prevents both workload
  jobs.
- Exactly one compiler-version metadata invocation and at most two workload
  jobs are permitted.
- Use argv lists, `shell=False`, binary stdout/stderr, and
  `start_new_session=True`.
- No automatic retry, package manager, network, CMake, Boost.Math, mutant, MR,
  profiling, certification, or production build-preflight invocation.
- Unit tests must use synthetic adapters and temporary roots. Implementation
  work must not execute a real C++ compiler.
- Every persisted JSON object is canonical UTF-8 JSON with one terminal LF,
  no CR, exact keys, and `artifact_sha256` computed over the object without
  that field.
- `formal_denominator_membership=false`, `claims=blocked`, and
  `attempt_2_authorized=false` are invariant.
- Qualification implementation PASS does not authorize qualification
  execution or build-preflight attempt-2.
- `CXX_COMPILE_LINK` and `QUALIFIED_BINARY_RUN` PASS only when the job
  exits 0 and both stdout and stderr are zero bytes. Nonempty workload
  output is `UNEXPECTED_OUTPUT` and terminal FAIL.
- After the last process that may start ends, and before the terminal
  result is written, re-inspect HEAD plus tracked, staged, and untracked
  state. PASS requires the entry and final repository snapshots to be
  identical and clean. Drift is `REPOSITORY_DRIFT`.
- This plan-archive/repair node does not run qualification and therefore
  returns no logs. A later authorized real qualification must return
  canonical intent, result, and manifest plus lossless Base64 and readable
  text for every raw stdout/stderr file. That return protocol does not
  authorize execution here.

---

## File Structure

- `src/p3_v3/toolchain_qualification.py`
  - constants and exact schemas
  - intent/result/manifest validators and constructors
  - environment and repository entry/postcondition inspection
  - compiler path resolution
  - private one-shot host-snapshot capture
  - metadata/workload process execution and cleanup
  - one-shot orchestration through `run_qualification`
- `scripts/p3_v3/qualify_cxx_link.py`
  - zero-argument CLI adapter
  - fixed repository and qualification-root binding
  - terminal exit mapping only
- `tests/p3_v3/test_toolchain_qualification.py`
  - canonical schema tests
  - ordering and no-retry tests
  - process/output/timeout tests
  - terminal evidence and manifest tests
  - CLI adapter tests

The external module interface is deliberately small:

```python
def run_qualification(
    repo_root: Path,
    qualification_root: Path,
    env: Mapping[str, str],
    *,
    which: Callable[[str], str | None] = shutil.which,
    popen: Callable[..., Any] = subprocess.Popen,
) -> dict[str, Any]:
    """Run or terminally close one qualification attempt."""
```

All other seams are module-private.

---

### Task 1: Canonical Qualification Evidence

**Files:**

- Create: `src/p3_v3/toolchain_qualification.py`
- Create: `tests/p3_v3/test_toolchain_qualification.py`

**Interfaces:**

- Consumes:
  - `p3_v3.artifacts.EvidenceError`
  - `canonical_json_bytes`
  - `canonical_sha256`
  - `read_regular_file_snapshot`
  - `validate_exact_object`
  - `validate_sha256`
  - `write_canonical_json`
- Produces:
  - `validate_intent(value: object) -> dict[str, Any]`
  - `validate_process_evidence(value: object) -> dict[str, Any]`
  - `validate_result(value: object) -> dict[str, Any]`
  - `validate_manifest(value: object) -> dict[str, Any]`
  - `validate_host_snapshot(value: object) -> dict[str, Any]`
  - `validate_attempt_pair(
    intent: object,
    intent_file_sha256: str,
    result: object,
) -> tuple[dict[str, Any], dict[str, Any]]`
  - private `_self_hash(payload: dict[str, Any]) -> dict[str, Any]`

- [ ] **Step 1: Add constants and failing exact-schema tests**

The module constants are:

```python
EXECUTION_CLASS = "PILOT_TOOLCHAIN_QUALIFICATION_ONLY"
CLAIMS = "blocked"
SPEC_PATH = Path(
    "docs/superpowers/specs/"
    "2026-08-18-p3-cursor-vm-cxx-link-qualification-design.md"
)
SPEC_SHA256 = (
    "ff438a10da0e762667fe358fb32082e2338f39f28c16620d5a15d8890e8dd8d5"
)
FROZEN_ROOT = Path("/tmp/p3-cxx-link-qualification")
SOURCE_NAME = "qualify.cpp"
EXECUTABLE_NAME = "qualify"
SOURCE_BYTES = b"int main(){return 0;}\n"
COMPILE_TIMEOUT_SECONDS = 60
RUN_TIMEOUT_SECONDS = 10
COMPILER_VERSION_TIMEOUT_SECONDS = 10
FORBIDDEN_ENV = (
    "CXX",
    "CC",
    "CPATH",
    "CPLUS_INCLUDE_PATH",
    "LIBRARY_PATH",
    "LD_LIBRARY_PATH",
    "LDFLAGS",
    "CXXFLAGS",
)
```

Add tests that require:

```python
def test_frozen_constants_are_exact():
    import p3_v3.toolchain_qualification as q

    assert q.SOURCE_BYTES == b"int main(){return 0;}\n"
    assert q.FROZEN_ROOT == Path("/tmp/p3-cxx-link-qualification")
    assert q.COMPILE_TIMEOUT_SECONDS == 60
    assert q.RUN_TIMEOUT_SECONDS == 10
    assert q.COMPILER_VERSION_TIMEOUT_SECONDS == 10
    assert q.SPEC_SHA256 == (
        "ff438a10da0e762667fe358fb32082e2338f39f28c16620d5a15d8890e8dd8d5"
    )
```

Each validator must reject extra keys, missing keys, wrong types, noncanonical
self-hashes, `claims != "blocked"`, denominator membership other than false,
or attempt-2 authorization other than false.

- [ ] **Step 2: Run RED**

```bash
python3 -m pytest -q \
  tests/p3_v3/test_toolchain_qualification.py::test_frozen_constants_are_exact
```

Expected: collection/import failure because the module does not exist.

- [ ] **Step 3: Implement exact canonical object helpers**

Use these schema identities:

```python
INTENT_SCHEMA = "p3-cxx-link-qualification-intent-v1"
PROCESS_SCHEMA = "p3-cxx-link-qualification-process-v1"
RESULT_SCHEMA = "p3-cxx-link-qualification-result-v1"
MANIFEST_SCHEMA = "p3-cxx-link-qualification-manifest-v1"
HOST_SCHEMA = "p3-cxx-link-qualification-host-v1"
```

Intent exact fields:

```text
schema_version
execution_class
claims
formal_denominator_membership
attempt_2_authorized
no_retry
repository_commit
host_snapshot
host_snapshot_sha256
spec_path
spec_sha256
qualification_root
requested_compiler
resolved_compiler_path
resolved_compiler_realpath
source_text
source_sha256
compile_link_argv
binary_run_argv
compile_timeout_seconds
run_timeout_seconds
compiler_version_timeout_seconds
relevant_environment
artifact_sha256
```

`compiler_version_timeout_seconds` must be exactly `10`. Compiler-version
process evidence `timeout_seconds` must also equal `10`.

`resolved_compiler_path`, `resolved_compiler_realpath`,
`compile_link_argv`, and `binary_run_argv` are null together when compiler
resolution fails. Otherwise paths are absolute and the argv arrays exactly
match the approved specification.

Process evidence exact fields:

```text
schema_version
execution_class
claims
process_role
job_id
argv
timeout_seconds
process_started
terminal_status
failure_reason
exit_code
started_at
ended_at
wall_seconds
process_group_terminated
stdout_sha256
stderr_sha256
stdout_bytes
stderr_bytes
artifact_sha256
```

Allowed `process_role`: `METADATA` or `WORKLOAD`.

Allowed terminal matrices:

- `PASS`: started, exit 0, hashes/counts/timestamps present.
  WORKLOAD PASS additionally requires `stdout_bytes == 0` and
  `stderr_bytes == 0`. METADATA PASS may include nonempty stdout/stderr.
- `FAIL`: started, nonzero exit, `NONZERO_EXIT`; or started WORKLOAD exit
  0 with nonempty stdout or stderr, `UNEXPECTED_OUTPUT`.
- `TIMEOUT`: started, null exit, `TIMEOUT`, process group terminated.
- `NOT_STARTED`: not started and no process/output/time evidence.

Compiler-version metadata may produce output. `CXX_COMPILE_LINK` and
`QUALIFIED_BINARY_RUN` cannot PASS when either stream has a nonzero byte
count. Nonempty compile-link output leaves `QUALIFIED_BINARY_RUN`
`NOT_STARTED`. Raw stdout/stderr are still written in full and, when
present, listed in the manifest.

Result exact fields:

```text
schema_version
execution_class
claims
formal_denominator_membership
attempt_2_authorized
no_retry
intent_sha256
repository_commit
host_snapshot
host_snapshot_sha256
spec_sha256
compiler_version
jobs
source_sha256
executable_sha256
executable_bytes
executable_regular
executable_symlink
terminal_status
failure_reason
artifact_sha256
```

`compiler_version` is a process-evidence object or null. `jobs` contains
exactly `CXX_COMPILE_LINK` and `QUALIFIED_BINARY_RUN` in that order. PASS
requires both workload jobs PASS, a regular non-symlink executable, and its
hash/size.

Executable evidence is present whenever `CXX_COMPILE_LINK` produced a valid
regular, non-symlink executable, even if `QUALIFIED_BINARY_RUN` later times
out or exits nonzero.

Executable evidence is null only when compile-link did not PASS or when no
valid regular, non-symlink executable was produced.

Aggregate PASS still requires both workload jobs PASS, zero workload
stdout/stderr, a matching clean repository postcondition, a regular
non-symlink executable, and its hash/size. Preserving executable evidence
after a binary-run failure does not upgrade the aggregate status.

Host snapshot exact fields:

```text
schema_version
os_name
os_release
kernel_release
machine
node_name
python_version
git_version
repository_commit
repository_clean
requested_compiler
resolved_compiler_path
resolved_compiler_realpath
resolved_path_regular
resolved_path_symlink
artifact_sha256
```

The host snapshot is a canonical self-hashed object.

`repository_clean` must be true. `requested_compiler` must equal `c++`.
`repository_commit` must be 40 lowercase hexadecimal characters and equal the
top-level intent/result repository commit.

If compiler resolution succeeds:

- `resolved_compiler_path` and `resolved_compiler_realpath` are absolute;
- `resolved_path_regular` is true for the realpath target;
- `resolved_path_symlink` records whether the path returned by executable
  resolution is a symlink.

If compiler resolution fails, both resolved paths and both identity booleans
are null.

Intent and result embed the same complete host snapshot object and require
`host_snapshot.artifact_sha256 == host_snapshot_sha256`.

`validate_host_snapshot` authenticates schema, types, null coupling,
`requested_compiler == "c++"`, `repository_clean is True`, a 40-character
lowercase hexadecimal `repository_commit`, and a canonical self-hash. It
must not compare archived OS, kernel, machine, node, Python, or Git fields
against the reviewer's current host.

Tamper semantics:

- mutate any host-snapshot field and leave `artifact_sha256` unchanged:
  `validate_host_snapshot` rejects the object;
- recompute a valid self-hash after mutation, then embed a snapshot that
  differs between intent and result: `validate_attempt_pair` rejects the
  pair.

`validate_attempt_pair` must check host snapshot, hash, repository commit,
spec hash, timeouts, source hash, argv, and intent file hash are completely
consistent.

Manifest exact fields:

```text
schema_version
execution_class
claims
formal_denominator_membership
attempt_2_authorized
no_retry
intent_sha256
result_sha256
files
artifact_sha256
```

Each `files` entry has exactly `path`, `sha256`, and `bytes`. Paths are unique,
relative, sorted, contain no `..`, and never include
`qualification-manifest.json`.

- [ ] **Step 4: Add validator tests**

Cover:

```python
def test_manifest_excludes_itself_and_is_self_hashed():
    manifest = _valid_manifest()
    assert q.validate_manifest(manifest) == manifest
    bad = dict(manifest)
    bad["files"] = [
        *manifest["files"],
        {
            "path": "qualification-manifest.json",
            "sha256": "a" * 64,
            "bytes": 1,
        },
    ]
    bad = q._self_hash({k: v for k, v in bad.items() if k != "artifact_sha256"})
    with pytest.raises(EvidenceError):
        q.validate_manifest(bad)
```

Also test unresolved compiler intent uses four null fields and cannot contain
invented workload argv.

Cover host snapshot binding:

```python
def test_intent_and_result_bind_same_host_snapshot():
    host = _valid_host_snapshot()
    intent = _valid_intent(host_snapshot=host)
    result = _valid_result(
        host_snapshot=host,
        host_snapshot_sha256=host["artifact_sha256"],
    )
    assert q.validate_intent(intent)["host_snapshot"] == host
    assert q.validate_result(result)["host_snapshot"] == host
```

Also test:

- a mutated host snapshot that is not re-self-hashed is rejected by
  `validate_host_snapshot`;
- a re-self-hashed host snapshot that differs between intent and result
  is rejected by `validate_attempt_pair`;
- host snapshot hash mismatch is rejected;
- unresolved compiler must use four null identity fields.

`validate_attempt_pair` must check host snapshot, hash, repository commit,
spec hash, timeouts, source hash, argv, and intent file hash are completely
consistent.

- [ ] **Step 5: Run GREEN**

```bash
python3 -m pytest -q tests/p3_v3/test_toolchain_qualification.py
```

Expected: all Task 1 tests pass.

- [ ] **Step 6: Commit Task 1**

```bash
git add \
  src/p3_v3/toolchain_qualification.py \
  tests/p3_v3/test_toolchain_qualification.py
git commit -m "feat(p3-v3): define C++ qualification evidence"
```

---

### Task 2: One-Shot Qualification Runner

**Files:**

- Modify: `src/p3_v3/toolchain_qualification.py`
- Modify: `tests/p3_v3/test_toolchain_qualification.py`

**Interfaces:**

- Consumes Task 1 validators and constructors.
- Produces:
  - `run_qualification(...) -> dict[str, Any]`
  - private `_inspect_repository(...) -> dict[str, Any]`
  - private `_capture_host_snapshot(...) -> dict[str, Any]`
  - private `_run_process(...) -> dict[str, Any]`
  - private `_write_terminal_result_and_manifest(...) -> dict[str, Any]`

- [ ] **Step 1: Add RED tests for entry preconditions**

Tests must prove:

```python
def test_preexisting_root_is_not_deleted_or_reused(tmp_path):
    root = tmp_path / "qualification"
    root.mkdir()
    marker = root / "owned"
    marker.write_bytes(b"unchanged")
    with pytest.raises(EvidenceError, match="E_QUALIFICATION_PREEXISTING"):
        q.run_qualification(
            repo_root=tmp_path,
            qualification_root=root,
            env={},
            which=lambda _name: "/usr/bin/c++",
            popen=_unexpected_popen,
        )
    assert marker.read_bytes() == b"unchanged"
```

For every forbidden environment key, a nonempty value must fail before root
creation and before any process call. Empty or absent values are accepted and
bound in the intent snapshot.

- [ ] **Step 2: Add RED tests for ordering**

The process adapter records each invocation. At the compiler-version call it
must observe:

```text
qualification-intent.json exists
qualify.cpp exists
qualification-result.json absent
qualification-manifest.json absent
```

The expected successful call order is exactly:

```text
<resolved-cxx> --version
<resolved-cxx> -std=c++14 <root>/qualify.cpp -o <root>/qualify
<root>/qualify
```

No other compiler or workload call is allowed.

- [ ] **Step 3: Implement entry and intent publication**

The orchestrator order is:

```text
validate repository clean state and forbidden environment
record the entry repository snapshot
exclusive-create qualification root
resolve c++ using injected which/filesystem operations
capture the host snapshot once
write exact qualify.cpp
exclusive-create qualification-intent.json
run compiler-version metadata probe once
run compile-link once if metadata PASS
validate generated executable
run binary once if compile-link PASS
re-inspect the repository
exclusive-create qualification-result.json
exclusive-create qualification-manifest.json last
return validated result
```

Use `os.mkdir` for root creation. Never call deletion, rename, cleanup, or
overwrite operations on existing evidence.

Repository inspection may use read-only Git metadata commands but must not
change Git configuration or the worktree.

Private `_inspect_repository` records `repository_commit`,
`repository_clean`, and the exact tracked, staged, and untracked porcelain.
The entry snapshot is taken before root creation. The final snapshot is
taken after the last process that may start has ended and before the
terminal result is exclusive-created. PASS requires both snapshots to be
identical and clean. Drift yields terminal FAIL / `REPOSITORY_DRIFT`,
preserves already-written process evidence, and still exclusive-creates
result and manifest.

Private `_capture_host_snapshot` runs once after compiler filesystem
resolution and before exclusive-create of `qualification-intent.json`.
Field sources:

- `os_name`: `os.uname().sysname`
- `os_release`: `os.uname().version`
- `kernel_release`: `os.uname().release`
- `machine`: `os.uname().machine`
- `node_name`: `os.uname().nodename`
- `python_version`: `platform.python_version()`
- `git_version`: stdout of the same read-only Git inspection channel used
  for commit and clean-state probes, not a qualification workload job
- `repository_commit` / `repository_clean`: `_inspect_repository`
- `requested_compiler`: exactly `c++`
- resolved path, realpath, regular-file, and symlink identity: controller
  filesystem APIs after `which("c++")`, without executing the compiler

The captured object is self-hashed once and embedded identically in intent
and result, including `host_snapshot_sha256`. Synthetic runner tests must
read the published `qualification-intent.json` and
`qualification-result.json` and assert that binding. Validators must not
re-query the current machine to accept or reject those archived fields.

- [ ] **Step 4: Implement unresolved compiler terminal evidence**

When `which("c++")` returns null:

- write source and intent;
- intent compiler and workload argv fields are null;
- compiler-version evidence is null;
- both jobs are `NOT_STARTED`;
- result is terminal FAIL with `MISSING_COMPILER`;
- write manifest;
- call `popen` zero times.

Add a test validating the canonical files and manifest inventory.

Synthetic runner tests initialize a temporary Git repository at
`repo_root` so entry and postcondition inspection can run without touching
the project worktree. They must not use the production qualification root.
The helper `_run_synthetic_qualification` returns
`(result, manifest, root)`.

A synthetic PASS or FAIL runner test must read the published intent and
result files and prove:

```python
def test_runner_embeds_identical_captured_host_snapshot(tmp_path):
    result, manifest, root = _run_synthetic_qualification(tmp_path)
    intent = _read_canonical_json(root / "qualification-intent.json")
    published = _read_canonical_json(root / "qualification-result.json")
    assert published == result
    assert intent["host_snapshot"] == published["host_snapshot"]
    assert intent["host_snapshot_sha256"] == published["host_snapshot_sha256"]
    assert (
        intent["host_snapshot"]["artifact_sha256"]
        == intent["host_snapshot_sha256"]
    )
```

- [ ] **Step 5: Implement `_run_process` with cumulative output semantics**

`_run_process` must:

- call injected `popen` once with argv list, `shell=False`,
  `stdout=PIPE`, `stderr=PIPE`, `start_new_session=True`;
- use `communicate(timeout=...)` as the waiter;
- preserve `TimeoutExpired.stdout/stderr`;
- after kill/reap, treat final cumulative snapshots as replacements;
- retain earlier snapshots only when the final snapshot is null;
- never concatenate cumulative snapshots;
- kill the process group on timeout and reap it;
- write raw stdout/stderr exclusively before returning evidence.

Add tests for timeout, final-null fallback, nonzero exit, and no duplicate
output.

- [ ] **Step 6: Implement dependency blocking**

Tests must prove:

- compiler-version failure → both workload jobs `NOT_STARTED`;
- compile-link failure → binary run `NOT_STARTED`;
- compile timeout → binary run `NOT_STARTED`;
- nonempty compile-link stdout or stderr → `UNEXPECTED_OUTPUT` and
  binary run `NOT_STARTED`;
- missing or symlink output executable → binary run `NOT_STARTED`;
- binary nonzero → terminal FAIL;
- nonempty binary stdout or stderr → `UNEXPECTED_OUTPUT` and terminal
  FAIL;
- no blocked job receives forged stdout/stderr, timestamps, exit code, or
  process-started state.

Generic nonzero remains `NONZERO_EXIT`; no Boost.Math failure classification
is introduced here.

Add metadata-timeout closure:

```python
def test_compiler_version_timeout_blocks_workloads_and_closes_evidence(
    tmp_path,
):
    result, manifest, root = _run_synthetic_qualification(
        tmp_path,
        compiler_version_timeout=True,
    )
    assert result["compiler_version"]["terminal_status"] == "TIMEOUT"
    assert result["compiler_version"]["timeout_seconds"] == 10
    assert all(job["terminal_status"] == "NOT_STARTED" for job in result["jobs"])
    assert result["terminal_status"] == "FAIL"
    assert result["failure_reason"] == "METADATA_TIMEOUT"
    assert manifest["result_sha256"]
```

Compiler-version metadata must:

- be invoked exactly once;
- kill and reap the process group after timeout;
- leave both workload jobs unstarted;
- still exclusive-create result and manifest;
- persist metadata stdout/stderr under the cumulative snapshot rule;
- allow nonempty metadata output without treating it as
  `UNEXPECTED_OUTPUT`.

Cover unexpected workload output as four independent cases:

```python
def test_compile_stdout_is_unexpected_output_and_blocks_binary(tmp_path):
    result, manifest, root = _run_synthetic_qualification(
        tmp_path,
        compile_exit=0,
        compile_stdout=b"warning\n",
        create_regular_executable=True,
    )
    assert result["jobs"][0]["terminal_status"] == "FAIL"
    assert result["jobs"][0]["failure_reason"] == "UNEXPECTED_OUTPUT"
    assert result["jobs"][1]["terminal_status"] == "NOT_STARTED"
    assert result["terminal_status"] == "FAIL"
    assert result["failure_reason"] == "UNEXPECTED_OUTPUT"
    assert (root / "CXX_COMPILE_LINK.stdout").read_bytes() == b"warning\n"
    assert "CXX_COMPILE_LINK.stdout" in {
        entry["path"] for entry in manifest["files"]
    }
```

Also test compile stderr, binary stdout, and binary stderr independently.
Binary unexpected output may preserve executable evidence because
compile-link PASS already occurred. Compile unexpected output leaves
executable evidence null because compile-link did not PASS. Raw logs for
the started job remain on disk and in the manifest.

- [ ] **Step 7: Implement PASS and manifest closure**

A synthetic PASS adapter must create a regular executable at the frozen output
path during the compile-link call and must not write to `repo_root`. Assert:

```python
assert result["terminal_status"] == "PASS"
assert result["failure_reason"] is None
assert result["formal_denominator_membership"] is False
assert result["attempt_2_authorized"] is False
assert result["claims"] == "blocked"
assert result["jobs"][0]["stdout_bytes"] == 0
assert result["jobs"][0]["stderr_bytes"] == 0
assert result["jobs"][1]["stdout_bytes"] == 0
assert result["jobs"][1]["stderr_bytes"] == 0
```

PASS also requires the entry and final repository snapshots to be identical
and clean. Add:

```python
def test_pass_requires_matching_clean_repository_postcondition(tmp_path):
    result, manifest, root = _run_synthetic_qualification(tmp_path)
    assert result["terminal_status"] == "PASS"
    assert result["host_snapshot"]["repository_clean"] is True
```

A synthetic drift adapter writes one untracked file under `repo_root`
during the last started process. After that process ends, the runner
re-inspects the repository and must close as follows:

```python
def test_repository_drift_fails_and_preserves_process_evidence(tmp_path):
    result, manifest, root = _run_synthetic_qualification(
        tmp_path,
        mutate_repo_during_last_job=True,
    )
    assert result["terminal_status"] == "FAIL"
    assert result["failure_reason"] == "REPOSITORY_DRIFT"
    assert result["jobs"][0]["terminal_status"] == "PASS"
    assert result["jobs"][1]["terminal_status"] == "PASS"
    assert (root / "qualification-result.json").is_file()
    assert (root / "qualification-manifest.json").is_file()
```

Manifest inventory must:

- be sorted and unique;
- exclude itself;
- include intent, result, source, executable, compiler-version logs, and both
  workload log pairs;
- bind exact file hashes and byte counts;
- omit files for unstarted jobs.

Task 2 must prove binary failure preserves compiled executable evidence:

```python
def test_binary_failure_preserves_compiled_executable_evidence(tmp_path):
    result, manifest, root = _run_synthetic_qualification(
        tmp_path,
        compile_exit=0,
        create_regular_executable=True,
        binary_exit=7,
    )
    assert result["terminal_status"] == "FAIL"
    assert result["failure_reason"] == "NONZERO_EXIT"
    assert result["jobs"][0]["terminal_status"] == "PASS"
    assert result["jobs"][1]["terminal_status"] == "FAIL"
    assert result["executable_sha256"] is not None
    assert result["executable_bytes"] is not None
    assert result["executable_regular"] is True
    assert result["executable_symlink"] is False
    assert "qualify" in {entry["path"] for entry in manifest["files"]}
```

Also test that binary timeout likewise preserves executable evidence.

- [ ] **Step 8: Run Task 2 GREEN**

```bash
python3 -m pytest -q tests/p3_v3/test_toolchain_qualification.py
```

Expected: all tests pass with zero skip and zero xfail.

- [ ] **Step 9: Commit Task 2**

```bash
git add \
  src/p3_v3/toolchain_qualification.py \
  tests/p3_v3/test_toolchain_qualification.py
git commit -m "feat(p3-v3): run one-shot C++ qualification"
```

---

### Task 3: Zero-Argument CLI Adapter And Regression Closure

**Files:**

- Create: `scripts/p3_v3/qualify_cxx_link.py`
- Modify: `tests/p3_v3/test_toolchain_qualification.py`

**Interfaces:**

- Consumes:
  - `run_qualification`
  - `FROZEN_ROOT`
- Produces:
  - `build_parser() -> argparse.ArgumentParser`
  - `main(argv: list[str] | None = None) -> int`

- [ ] **Step 1: Add CLI RED tests**

The parser accepts no qualification overrides. The following must fail parser
validation:

```text
--compiler
--root
--timeout
--source
--output
--retry
--cmake
--boost-root
--attempt-2
```

Monkeypatch `run_qualification` and assert the adapter passes:

```python
repo_root == Path(script.__file__).resolve().parents[2]
qualification_root == FROZEN_ROOT
env == dict(os.environ)
```

- [ ] **Step 2: Implement the thin adapter**

The script imports the source tree using the established `scripts/p3_v3`
pattern and exposes no runtime path/compiler/timeout overrides.

Exit mapping:

```text
0 = terminal qualification PASS
1 = terminal qualification FAIL with result/manifest published
2 = pre-evidence EvidenceError
```

The CLI prints only the final qualification status and evidence-root path.
Child stdout/stderr remain solely in evidence files.

- [ ] **Step 3: Run CLI unit tests**

```bash
python3 -m pytest -q tests/p3_v3/test_toolchain_qualification.py
```

Expected: all qualification tests pass, zero skip/xfail.

- [ ] **Step 4: Run existing directed regression**

```bash
python3 -m pytest -q -ra \
  tests/p3_v3/test_pilot.py \
  tests/p3_v3/test_pilot_build.py \
  tests/p3_v3/test_toolchain_qualification.py
```

Expected:

- all collected tests pass;
- zero failed, skipped, or xfailed;
- no production qualification root is created.

- [ ] **Step 5: Run static verification**

```bash
python3 -m ruff check \
  src/p3_v3/toolchain_qualification.py \
  scripts/p3_v3/qualify_cxx_link.py \
  tests/p3_v3/test_toolchain_qualification.py

python3 -m py_compile \
  src/p3_v3/toolchain_qualification.py \
  scripts/p3_v3/qualify_cxx_link.py \
  tests/p3_v3/test_toolchain_qualification.py

awk 'length($0)>100 {print FNR ":" length($0) ":" $0}' \
  src/p3_v3/toolchain_qualification.py \
  scripts/p3_v3/qualify_cxx_link.py \
  tests/p3_v3/test_toolchain_qualification.py

git diff --check
```

Expected: all commands exit 0 and the `awk` command prints nothing.

- [ ] **Step 6: Prove production isolation**

Before commit:

```bash
test ! -e /tmp/p3-cxx-link-qualification
git diff --name-status
git diff --stat
git diff --check
```

The complete implementation range must contain only:

```text
A src/p3_v3/toolchain_qualification.py
A scripts/p3_v3/qualify_cxx_link.py
A tests/p3_v3/test_toolchain_qualification.py
```

No Authorization, qualification evidence, attempt-2 artifact, compiler output,
build root, harness root, or claim-ledger change is permitted.

- [ ] **Step 7: Commit Task 3**

```bash
git add \
  scripts/p3_v3/qualify_cxx_link.py \
  tests/p3_v3/test_toolchain_qualification.py
git commit -m "feat(p3-v3): expose C++ qualification CLI"
```

- [ ] **Step 8: Final implementation handoff**

After the three commits, run the complete directed suite once more, push
normally, fetch, and report:

- entry and final commits;
- complete commit range;
- exact changed paths;
- RED and GREEN commands with exits/counts/wall times;
- static-check results;
- final file SHA-256 values;
- `HEAD == origin/main`;
- branch divergence `+0 -0`;
- clean tracked/staged/untracked state;
- proof `/tmp/p3-cxx-link-qualification` remains absent.

Stop after implementation handoff. Do not run
`scripts/p3_v3/qualify_cxx_link.py`. Sol review and separate user authorization
are required before any real compiler qualification.

## Evidence-Return Boundary

This implementation-plan node does not run qualification. There are no
qualification logs, Base64 transcripts, or evidence files to return.

`QUALIFICATION_AUTHORIZED=false` and `ATTEMPT_2_AUTHORIZED=false` remain
in force. Completing this plan repair does not authorize implementation
execution, compiler invocation, or attempt-2.

A later, separately authorized real qualification must return the
canonical intent, result, and manifest, plus lossless Base64 and readable
text for every raw stdout/stderr file, exactly as the approved
specification requires. That return protocol is not an execution
authorization for this node.
