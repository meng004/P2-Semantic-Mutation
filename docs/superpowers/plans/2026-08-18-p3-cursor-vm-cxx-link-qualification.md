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

---

## File Structure

- `src/p3_v3/toolchain_qualification.py`
  - constants and exact schemas
  - intent/result/manifest validators and constructors
  - environment and repository preconditions
  - compiler path resolution
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
relevant_environment
artifact_sha256
```

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
- `FAIL`: started, nonzero exit, `NONZERO_EXIT`.
- `TIMEOUT`: started, null exit, `TIMEOUT`, process group terminated.
- `NOT_STARTED`: not started and no process/output/time evidence.

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
hash/size. Any other terminal state requires unavailable executable evidence
to be null.

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
exclusive-create qualification root
resolve c++ using injected which/filesystem operations
write exact qualify.cpp
exclusive-create qualification-intent.json
run compiler-version metadata probe once
run compile-link once if metadata PASS
validate generated executable
run binary once if compile-link PASS
exclusive-create qualification-result.json
exclusive-create qualification-manifest.json last
return validated result
```

Use `os.mkdir` for root creation. Never call deletion, rename, cleanup, or
overwrite operations on existing evidence.

Repository inspection may use read-only Git metadata commands but must not
change Git configuration or the worktree.

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
- missing or symlink output executable → binary run `NOT_STARTED`;
- binary nonzero → terminal FAIL;
- no blocked job receives forged stdout/stderr, timestamps, exit code, or
  process-started state.

Generic nonzero remains `NONZERO_EXIT`; no Boost.Math failure classification
is introduced here.

- [ ] **Step 7: Implement PASS and manifest closure**

A synthetic PASS adapter must create a regular executable at the frozen output
path during the compile-link call. Assert:

```python
assert result["terminal_status"] == "PASS"
assert result["failure_reason"] is None
assert result["formal_denominator_membership"] is False
assert result["attempt_2_authorized"] is False
assert result["claims"] == "blocked"
```

Manifest inventory must:

- be sorted and unique;
- exclude itself;
- include intent, result, source, executable, compiler-version logs, and both
  workload log pairs;
- bind exact file hashes and byte counts;
- omit files for unstarted jobs.

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
