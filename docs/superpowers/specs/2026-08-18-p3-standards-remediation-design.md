# P3 Standards Remediation Design

**Status:** Approved design archived; implementation is not authorized
**Node:** `P1BP1I2Q3_CURSOR_VM_P3_STANDARDS_REMEDIATION_DESIGN_ARCHIVE`
**Type:** `GOVERNANCE_ONLY`
**Baseline:** `origin/main` `4444061dde0159a5edd62753fe3cef2d881a308c`
**Claims:** blocked
**Formal denominator membership:** false
**Attempt-2 authorized:** false

This document archives the approved five-part standards remediation. It is
not an implementation plan, Authorization, or implementation verdict. Writing
or merging this file does not authorize code, documentation edits beyond this
file, real qualification, or claim upgrades.

## Purpose

After pull request 15 merged the Cursor VM C++ compile-link qualification
into `main`, the public repository still presents itself as a P2-only
replication artefact, and the qualification test helpers still use untyped
option bags plus two overlapping process-group patches. The approved
remediation is a standards cleanup:

1. Reposition the repository as P3, with P2 retained as a read-only
   historical reproduction layer.
2. Introduce a frozen `CompilerIdentity` dataclass without changing
   external evidence schema or canonical bytes.
3. Introduce a frozen `QualificationScenario` dataclass that fully
   replaces `**opts`.
4. Merge the two process-group patch helpers and forbid a PID-probe
   regression.
5. Bind RED to GREEN, directed regression, static checks, and a real
   execution exclusion zone.

The remediation does not reopen qualification PASS semantics, resolver
rules, repository-drift rules, executable-evidence rules, CLI flags, or
the frozen qualification specification and plan.

## Frozen Adjacent Artifacts

The following files stay byte-identical. This remediation must not edit
them, rehash them, or treat their SHA-256 values as stale:

```text
docs/superpowers/specs/2026-08-18-p3-cursor-vm-cxx-link-qualification-design.md
ff438a10da0e762667fe358fb32082e2338f39f28c16620d5a15d8890e8dd8d5

docs/superpowers/plans/2026-08-18-p3-cursor-vm-cxx-link-qualification.md
9661ecb73043bb58adc9b6bad025b9051548602e74677643cb7866f4204e2901
```

`src/p3_v3/toolchain_qualification.py` continues to bind
`SPEC_PATH` and `SPEC_SHA256` to that specification. The remediation must
not change those constants.

Merged pull request 15 commits remain historical. This design starts from
`4444061dde0159a5edd62753fe3cef2d881a308c` on a new branch. It must not
rebase, rewrite, or amend those commits.

## Future Implementation Scope

When a later user-authorized implementation node exists, and only then,
the writable set is exactly:

```text
README.md
CONTRIBUTING.md
src/p3_v3/toolchain_qualification.py
tests/p3_v3/test_toolchain_qualification.py
```

`README.md` and `CONTRIBUTING.md` carry part 1. The production module
carries part 2. The qualification test module carries parts 3 and 4.
Part 5 is the verification contract for that later node.

The following remain out of scope even after implementation is
authorized:

- `scripts/p3_v3/qualify_cxx_link.py`
- every file under `src/p2/`, `data/`, `submission/`, `replication/`,
  `figs/`, `figures/`, and `archive/`
- P2 manuscripts and P2 citation files
- `REPRODUCIBILITY.md`, `DATASET.md`, `PROJECT_STRUCTURE.md`,
  `CHANGELOG.md`, `CITATION.cff`, and `docs/STATE.md`
- this specification after archival, except by a later explicit
  design-revision authorization
- Authorization files and implementation verdicts
- creation of `/tmp/p3-cxx-link-qualification`

No other production module is in scope. Adding a new source file,
renaming the CLI, or widening the writable set requires a new approved
design.

## Claim Ceiling

The remediation may establish only that the repository entry documents
describe P3 as the active project, that compiler identity and synthetic
scenarios are named frozen types, and that process-group tests share one
helper that cannot certify cleanup with `os.kill(pgid, 0)`.

It does not establish toolchain readiness, Boost.Math build readiness,
attempt-2 authorization, formal denominator membership, RQ support, or
paper Results.

## Part 1. Repository Identity And The P2 Read-Only Layer

### 1.1 Current defect

`README.md` titles the repository as the P2 Semantic Mutation Score
audit replication artefact. `CONTRIBUTING.md` says a successor P3
framework will live in a separate repository and marks P3-directed
issues `out-of-scope-for-P2`. Those sentences are false after pull
request 15: this repository already contains `src/p3_v3/`,
`tests/p3_v3/`, `scripts/p3_v3/qualify_cxx_link.py`, and the frozen
qualification specification and plan.

### 1.2 Approved public identity

`README.md` becomes the P3 Semantic Mutation repository entry. The
opening identity must state all of the following:

- this GitHub repository is the P3 working tree, not a P2-only replica;
- active engineering in-tree is P3 v3 evidence infrastructure, the
  Boost.Math pilot with claims blocked, and the Cursor VM C++
  compile-link qualification;
- formal claims, formal denominator membership, and attempt-2 remain
  blocked;
- P2 remains present as a read-only historical reproduction layer for
  the IST Semantic Mutation Score audit.

The README layout section must list `src/p3_v3/`, `tests/p3_v3/`, and
`scripts/p3_v3/` beside the existing P2 paths. It must not delete the
P2 tree map. It must not present P2 commands as the only way to use
the repository.

`CONTRIBUTING.md` must identify this repository as the P3 project. It
must remove the sentence that P3 is a separate repository. It must
welcome P3 work that stays inside later-authorized file sets. It must
keep a P2 replication-report channel for historical reproduction
failures.

### 1.3 Historical P2 section

The P3 README must retain a clearly marked historical P2 section that
preserves the existing P2 smoke, cache-replay, and re-LLM command
blocks without rewriting their flags, environment variables, or
expected scientific meaning. That section may point to
`REPRODUCIBILITY.md` and `DATASET.md` instead of restating every P2
prose paragraph.

The remediation must not mint a paper DOI, invent an arXiv identifier,
or replace P2 citation stubs with fabricated identifiers. If the
current P2 citation block is copied into the historical section, its
existing stub strings stay as they are. The preferred form is a short
pointer to the existing P2 citation files rather than a rewritten
bibtex block.

`CONTRIBUTING.md` must not invent a new P2 pytest count or a new SSOT
rebuild command. It may keep the current P2 workflow sentences as
historical text, or replace them with a pointer to
`REPRODUCIBILITY.md` and the historical README section. It must not
treat the pre-existing 116-versus-192 P2 test-count disagreement as
in-scope cleanup.

### 1.4 P2 read-only constraint

P2 is read-only for this remediation and for the later implementation
node that executes this design. Read-only means:

- no new P2 operators, PUTs, MRs, metrics, or manuscript claims;
- no edit to `src/p2/`, P2-only tests, `data/`, `submission/`,
  `replication/`, P2 figures, or P2 manuscripts;
- no regeneration or rewrite of `data/results/paper_numbers_v4.json`
  or other P2 SSOT files;
- no reclassification of P2 results as P3 results;
- no move, delete, or in-place rewrite of P2 historical review files
  to make the repository "look like P3".

P2 paths remain readable. README and CONTRIBUTING may name those paths
as historical.

### 1.5 Compatibility-fix boundary

A compatibility fix is allowed only when all of the following hold:

1. The breaking change originated in an allowed file listed in Future
   Implementation Scope.
2. The fix itself stays inside that same allowed set.
3. The fix restores a previously documented P2 reproduction command or
   a previously passing qualification synthetic test.
4. The fix does not change P2 numbers, hashes, manuscript text, or
   qualification evidence schema.

Examples that are allowed:

- keeping P2 command blocks verbatim in the historical README section
  so existing replicators still have a copy-paste path;
- giving `QualificationScenario.create_regular_executable` default
  `True`, matching the current helper;
- mapping `CompilerIdentity` fields onto the existing flat JSON keys
  so current validators keep accepting the same objects.

Examples that are forbidden:

- editing `src/p2/` or P2 tests because README wording changed;
- "fixing" P2 SSOT drift discovered while rewriting CONTRIBUTING;
- changing qualification FAIL reasons so a new dataclass is easier to
  test;
- adding README badges, extra top-level docs, or CI workflow edits to
  advertise the P3 rename.

If an allowed-file change would be correct only after editing a
read-only P2 file, the change is out of scope and must be dropped.

## Part 2. Frozen `CompilerIdentity`

### 2.1 Current defect

`_resolve_compiler` returns an anonymous four-tuple. Host snapshot and
intent construction unpack that tuple by position. Reviewers cannot
name the object, and a later field insertion can silently shift
evidence keys.

### 2.2 Approved type

Add a frozen dataclass in `src/p3_v3/toolchain_qualification.py`:

```python
@dataclass(frozen=True)
class CompilerIdentity:
    requested_compiler: str
    resolved_compiler_path: str | None
    resolved_compiler_realpath: str | None
    resolved_path_regular: bool | None
    resolved_path_symlink: bool | None
```

Field names match the current host-snapshot keys. No additional
evidence field is introduced. In particular, execute-permission is
already folded into the unresolved-null rule and must not become a
new JSON key.

`frozen=True` is mandatory. Assignment to a field after construction
must raise `FrozenInstanceError` or `AttributeError`. The type is an
internal Python object. It must not appear as a nested JSON object in
intent, host snapshot, result, or manifest.

### 2.3 Construction rules

`_resolve_compiler` returns `CompilerIdentity`.

Resolved success:

- `requested_compiler` is the frozen name `c++`;
- `resolved_compiler_path` is the absolute resolved path;
- `resolved_compiler_realpath` is `os.path.realpath` of that path;
- `resolved_path_regular` is `True`;
- `resolved_path_symlink` is whether the resolved path itself is a
  symlink.

Unresolved or non-executable compiler, including the current
`OSError` resolver-close path:

- `requested_compiler` remains `c++`;
- the other four fields are `None`.

A convenience constructor such as `CompilerIdentity.unresolved()` is
allowed if and only if it produces exactly that five-field object.
It must not write files or call `which`.

`_capture_host_snapshot` and intent construction read attributes by
name. They must not keep a parallel tuple API. `_workload_argv`
continues to receive the resolved path string or `None`.

### 2.4 External schema and canonical bytes

The external evidence schema is unchanged.

Host snapshot keeps:

- `requested_compiler`
- `resolved_compiler_path`
- `resolved_compiler_realpath`
- `resolved_path_regular`
- `resolved_path_symlink`

Intent keeps:

- `requested_compiler`
- `resolved_compiler_path`
- `resolved_compiler_realpath`

Result and manifest gain no compiler object. The existing host
snapshot remains nested as it is today.

Projection into JSON must emit the same keys, types, null grouping,
and key order rules already enforced by `validate_host_snapshot` and
`validate_intent`. Canonical JSON remains sorted keys, compact
separators, one terminal LF, and `artifact_sha256` over the object
without that field.

Because host snapshots contain `os.uname()` fields, the remediation
must not freeze a host-wide golden SHA-256. Schema stability is
proved by:

- existing validators still accepting constructed objects;
- existing tests that read compiler keys continuing without rename;
- no nested `compiler_identity` key;
- no change to `INTENT_SCHEMA`, `HOST_SCHEMA`, `RESULT_SCHEMA`,
  `MANIFEST_SCHEMA`, or `PROCESS_SCHEMA` strings.

A successful synthetic qualification that is PASS today must remain
PASS. A FAIL reason that is `MISSING_COMPILER`,
`COMPILER_RESOLUTION_ERROR`, `INVALID_EXECUTABLE`, or
`REPOSITORY_DRIFT` today must keep that reason. The dataclass must
not upgrade any FAIL to PASS.

### 2.5 Tests required for part 2

New tests must prove:

1. `CompilerIdentity` is frozen.
2. `_resolve_compiler` returns `CompilerIdentity`, not a tuple.
3. A missing or non-executable compiler yields the unresolved
   four-null identity with `requested_compiler == "c++"`.
4. Host snapshot and intent still expose the flat keys listed above.
5. Validators reject a host snapshot that adds an unknown compiler
   key or nests identity under a new name.

## Part 3. Frozen `QualificationScenario`

### 3.1 Current defect

`_run_synthetic_qualification(tmp_path, **opts: object)` accepts an
untyped keyword bag. Call sites cannot be checked for misspelled
flags. Defaults such as `create_regular_executable` are patched into
the mutable `opts` dict after the helper starts.

### 3.2 Approved type

Add a frozen dataclass in `tests/p3_v3/test_toolchain_qualification.py`.
It is a test helper, not an evidence type, and must not be written
into qualification JSON.

```python
@dataclass(frozen=True)
class QualificationScenario:
    env: Mapping[str, str] = field(default_factory=dict)
    missing_compiler: bool = False
    compiler_not_executable: bool = False
    metadata_popen_error: bool = False
    observe_metadata_fs: bool = False
    metadata_wait_error: bool = False
    compiler_version_timeout: bool = False
    compiler_version_exit: int = 0
    compiler_version_stdout: bytes | None = None
    compiler_version_stderr: bytes = b""
    cleanup_error: bool = False
    compile_popen_error: bool = False
    create_regular_executable: bool = True
    create_symlink_executable: bool = False
    create_nonregular_executable: bool = False
    create_nonexecutable_executable: bool = False
    mutate_repo_during_compile: bool = False
    mutate_repo_during_last_job: bool = False
    binary_unreached: bool = False
    compile_wait_error: bool = False
    compile_timeout: bool = False
    compile_exit: int = 0
    compile_stdout: bytes = b""
    compile_stderr: bytes = b""
    binary_popen_error: bool = False
    binary_timeout: bool = False
    binary_exit: int = 0
    binary_stdout: bytes = b""
    binary_stderr: bytes = b""
```

These fields are the closed set. They are exactly the keys currently
read from `opts`. Adding a field requires a new approved design.
Removing a field is forbidden while any current synthetic branch
still needs it.

### 3.3 Helper signature

```python
def _run_synthetic_qualification(
    tmp_path: Path,
    scenario: QualificationScenario | None = None,
) -> tuple[dict[str, Any], dict[str, Any], Path]:
```

`scenario is None` means `QualificationScenario()`. The helper must
not accept `**opts`, `**kwargs`, or an untyped mapping of flags.
Call sites that currently pass keywords must pass
`QualificationScenario(...)`.

The helper copies `scenario.env` into a new `dict` before calling
`run_qualification`. The frozen scenario object is never mutated.
The current mutable assignment
`opts["create_regular_executable"] = True` is deleted; the dataclass
default already supplies that value.

### 3.4 Preserved helper semantics

The synthetic `which` and `popen` branches keep their current
meaning. The only default that stays branch-dependent is compiler
version stdout:

- if `compiler_version_stdout is None` and `metadata_wait_error` is
  true, the metadata process uses `b"partial"`;
- if `compiler_version_stdout is None` otherwise, the metadata
  process uses `b"clang\n"`;
- if `compiler_version_stdout` is provided, that value is used.

All other defaults match the field table above. Tests that currently
pass `create_regular_executable=False` continue to do so on the
dataclass.

The helper still returns `(result, manifest, root)` and still attaches
`result["_calls"]`. It still uses a synthetic compiler path and a
synthetic `_Proc.pid` of `2000000000`. It still must not resolve or
execute a real `c++`.

### 3.5 Tests required for part 3

New or updated tests must prove:

1. `QualificationScenario` is frozen.
2. `_run_synthetic_qualification` rejects leftover keyword flags.
   The approved form is a helper signature without `**opts`; a
   direct call with an unknown attribute must be a type or
   `AttributeError` at construction time, not a silently ignored
   flag.
3. A no-argument `QualificationScenario()` still produces a
   synthetic PASS with a regular executable, matching today's
   default helper.
4. Every current call site is converted. After conversion, the
   test module contains no `**opts` on this helper and no
   `opts.get`.

Existing scenario outcomes stay the same: forbidden-env, missing
compiler, timeout cleanup, waiter I/O, drift, and invalid
executable cases must not change terminal status or failure
reason.

## Part 4. One Process-Group Helper And No PID Probe

### 4.1 Current defect

The test module defines `_patch_group_signals` and
`_patch_group_probe`. Both record `getpgid` and `killpg`, and both
distinguish `SIGKILL` from signal `0`. They differ only in the
`os.kill` fallback:

- `_patch_group_signals` records `os.kill` and does not raise;
- `_patch_group_probe` raises `ProcessLookupError` on
  `os.kill(pid, 0)` so a leader-reaped, group-still-present case
  can be shown.

Two helpers invite a regression to `os.kill(pgid, 0)` as the
group-absence probe.

### 4.2 Approved helper

Delete both helpers. Replace them with one helper in the same test
module:

```python
def _patch_process_group(
    monkeypatch: pytest.MonkeyPatch,
    *,
    terminate_error: BaseException | None = None,
    probe_error: BaseException | None = None,
    leader_pid_absent: bool = False,
) -> list[tuple[object, ...]]:
```

Behavior:

- `getpgid(pid)` records `("getpgid", pid)` and returns `pid`;
- `killpg(pgid, SIGKILL)` records `("killpg", pgid, SIGKILL)` and
  raises `terminate_error` when that argument is not `None`;
- `killpg(pgid, 0)` records `("killpg", pgid, 0)` and raises
  `probe_error` when that argument is not `None`;
- any other `killpg` signal raises `AssertionError`;
- `os.kill(pid, sig)` records `("kill", pid, sig)`;
- if `leader_pid_absent` is true and `sig == 0`, `os.kill` raises
  `ProcessLookupError("leader pid is gone")`.

`terminate_error` applies only to `SIGKILL`. `probe_error` applies
only to `killpg(..., 0)`. The two exception arguments must not be
consulted for the other phase. This keeps termination and probing
from sharing one exception by accident.

Call-site mapping:

- former `_patch_group_signals(..., killpg_error=E)` becomes
  `_patch_process_group(..., terminate_error=E)`;
- former `_patch_group_probe(...)` becomes
  `_patch_process_group(..., leader_pid_absent=True)`;
- former `_patch_group_probe(..., probe_error=E)` becomes
  `_patch_process_group(leader_pid_absent=True, probe_error=E)`.

After the merge, the names `_patch_group_signals` and
`_patch_group_probe` must not remain as aliases.

### 4.3 Production probe rule

`_process_group_absent(pgid)` stays a process-group probe:

```python
try:
    os.killpg(pgid, 0)
except ProcessLookupError:
    return True
except OSError as exc:
    return exc.errno == errno.ESRCH
return False
```

Only `ProcessLookupError` or `errno.ESRCH` means the group is
absent. A normal return, `PermissionError`, `EPERM`, `EINVAL`, or
any other `OSError` returns `False` and cannot certify cleanup.

Cleanup certification is unchanged: the leader must be reaped and
the frozen process group must be confirmed absent. Leader
`os.kill` remains a best-effort fallback only. It must not prove
group absence.

The remediation must not replace `os.killpg(pgid, 0)` with
`os.kill(pgid, 0)`, `os.kill(pid, 0)`, `/proc` reads, or
`pidfd` checks.

### 4.4 Tests required for part 4

Keep and, if needed, retarget the existing probe tests so they
still prove:

1. `_process_group_absent` calls `os.killpg(pgid, 0)` and does not
   call `os.kill`.
2. When the leader is gone and `killpg(pgid, 0)` succeeds, timeout
   is `FAIL` / `PROCESS_CLEANUP_FAILED` /
   `process_group_terminated=false`.
3. The same scene under waiter `OSError` yields the same triple.
4. `PermissionError`, `EPERM`, other `OSError`, and a successful
   probe return do not certify cleanup.
5. Recorded calls include `("killpg", pgid, 0)` and do not include
   `("kill", pgid, 0)` as the absence probe.
6. The test module defines exactly one process-group patch helper.

A test that imported the old helper names must be updated. Adding a
third helper that wraps `os.kill` as a group probe is forbidden.

## Part 5. Verification Contract And Exclusion Zone

### 5.1 RED then GREEN

Each of parts 2, 3, and 4 is implemented test-first when a later
node authorizes implementation.

- Write or retarget the tests first.
- Run those tests and record a real RED that fails for the missing
  type, leftover `**opts`, split helpers, or PID probe, not for a
  typo.
- Apply the smallest production or test-helper change that turns
  that RED green.
- Do not start from a green suite and backfill tests.

Part 1 is documentation. It has no pytest RED. Proof is a review of
the README and CONTRIBUTING sentences against sections 1.2 through
1.5, plus the static checks in section 5.3.

### 5.2 Directed regression

After GREEN, and still without real compiler execution, run this
suite in order:

1. the new or retargeted tests for the part just changed;
2. `tests/p3_v3/test_toolchain_qualification.py` in full;
3. `tests/p3_v3/test_pilot.py`,
   `tests/p3_v3/test_pilot_build.py`, and
   `tests/p3_v3/test_toolchain_qualification.py` together.

The directed three-file suite is the regression gate. A later
implementation node reports the collected count from that command.
This design does not freeze a historical count as a pass/fail
threshold because adding the part-2 and part-3 tests will increase
the number.

Use `/usr/bin/python3` with `PYTHONDONTWRITEBYTECODE=1`,
`PYTHONNOUSERSITE=1`, and `PYTHONPATH` that includes `src` plus the
already-present isolated third-party target on the VM, if one
exists. Do not create, delete, or reuse
`/tmp/p3-cxx-qualification-implementation-venv`.

### 5.3 Static checks

On the files actually edited in that later node:

- ruff check must pass;
- `python3 -m py_compile` must pass;
- no line longer than 100 characters;
- `git diff --check` must pass;
- staged paths must be a subset of the Future Implementation Scope
  set.

This archival node runs `git diff --check` on the specification
alone.

### 5.4 Real execution exclusion zone

The following are forbidden in this archival node and in any later
implementation of this design:

- running `scripts/p3_v3/qualify_cxx_link.py`;
- invoking a real `c++`, `cc`, Clang, GCC, `cmake`, `ninja`,
  `make`, or Boost.Math build;
- creating, deleting, or reusing `/tmp/p3-cxx-link-qualification`;
- authorizing or executing attempt-2;
- writing an Authorization or implementation verdict;
- changing `claims=blocked`,
  `formal_denominator_membership=false`, or
  `attempt_2_authorized=false`;
- editing the frozen qualification specification or plan;
- installing packages into a failed virtualenv;
- using a repository-local command wrapper in place of
  `/usr/bin/python3`.

Synthetic `which` and `popen` remain the only compiler interaction
allowed in tests.

### 5.5 Governance stop

After this specification is committed and pushed, work stops for
user review of the archived file. The next authorized step is
review of this specification. Writing an implementation plan,
invoking an implementation skill, or editing any allowed
implementation file is forbidden until the user approves the
written specification and issues a separate implementation
authorization.

## Non-Goals

This design does not:

- run or rerun qualification on a Cursor VM;
- repair attempt-1 evidence;
- change compile-link argv, timeouts, frozen source bytes, or
  production root;
- introduce `CompilerIdentity` into CLI output;
- share `QualificationScenario` with production code;
- generate JSON Schema files;
- rewrite `docs/STATE.md` or other P2 session notes;
- reconcile historical P2 documentation counts;
- merge this branch to `main` as part of archival.

## Self-Review Record

Completed during archival, before commit:

- Incomplete-marker scan: none found.
- Schema contradiction versus the frozen qualification spec: none.
  External keys and schema strings stay unchanged.
- Test-permission contradiction: none. Synthetic tests stay
  required and real runs stay forbidden.
- P2 read-only rule: stated in 1.4; compatibility boundary in 1.5.
- Writable-set contradiction: Future Implementation Scope is the
  only later write set.
- Implementation authorization: explicitly withheld.
- `git diff --check`: required on this file before commit.

## Approval And Stop

The five-part design was approved before this archival node. This
file is the archival record. User review of this file is still
required before any implementation plan or code. Design archival
is not implementation authorization.
