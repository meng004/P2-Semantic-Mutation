# P3 Standards Remediation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task.
> Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reposition the repository as P3 and remove the four reviewed
standards defects without changing qualification evidence or execution
semantics.

**Architecture:** Keep external qualification evidence flat and frozen.
Use a four-field CompilerIdentity as the single compiler-identity seam,
a frozen QualificationScenario for synthetic tests, and one
process-group patch helper that rejects every os.kill call. Preserve P2
as a read-only historical reproduction layer.

**Tech Stack:** Python 3.12, frozen dataclasses, pytest, ruff, canonical
JSON evidence, Markdown.

## Global Constraints

- Specification path:
  `docs/superpowers/specs/2026-08-18-p3-standards-remediation-design.md`
- Specification SHA-256:
  `641e673a0c82c38f864d8602e06c0ce21f58f0fcb3b8dc4425d444db909c7d6e`
- Implementation baseline is `origin/main`
  `4444061dde0159a5edd62753fe3cef2d881a308c`.
- Plan branch is `cursor/p3-standards-remediation-c46c`. Do not rebase,
  amend, or rewrite `316ddfd05cac999389d6be5c1de4e3074d9f6e3c` or
  earlier commits.
- The only writable implementation files are:
  `README.md`,
  `CONTRIBUTING.md`,
  `src/p3_v3/toolchain_qualification.py`,
  `tests/p3_v3/test_toolchain_qualification.py`.
- P2 read-only paths: `src/p2/`, P2-only tests, `data/`, `submission/`,
  `replication/`, `figs/`, `figures/`, `archive/`, P2 manuscripts, and
  P2 citation files. Do not edit `REPRODUCIBILITY.md`, `DATASET.md`,
  `PROJECT_STRUCTURE.md`, `CHANGELOG.md`, `CITATION.cff`, or
  `docs/STATE.md`.
- Do not regenerate or rewrite `data/results/paper_numbers_v4.json` or
  any other P2 SSOT file.
- Qualification evidence schema, schema strings, canonical JSON rules,
  and failure classifications stay unchanged.
- `SPEC_PATH` and `SPEC_SHA256` in
  `src/p3_v3/toolchain_qualification.py` stay
  `docs/superpowers/specs/2026-08-18-p3-cursor-vm-cxx-link-qualification-design.md`
  and
  `ff438a10da0e762667fe358fb32082e2338f39f28c16620d5a15d8890e8dd8d5`.
- Frozen qualification plan SHA-256 stays
  `9661ecb73043bb58adc9b6bad025b9051548602e74677643cb7866f4204e2901`.
- Do not run a real compiler, `scripts/p3_v3/qualify_cxx_link.py`,
  CMake, ninja, make, or Boost.Math.
- Do not create, delete, or reuse `/tmp/p3-cxx-link-qualification`.
- Do not create, delete, reuse, or install into
  `/tmp/p3-cxx-qualification-implementation-venv`.
- Do not authorize attempt-2. Keep `claims=blocked`,
  `formal_denominator_membership=false`, and
  `attempt_2_authorized=false`.
- Cursor VM commands must invoke `/usr/bin/python3` directly. Do not
  use `rtk` or any other repository-local command wrapper.
- Isolated test recipe, when a Task runs pytest:

```bash
export PYTHONDONTWRITEBYTECODE=1
export PYTHONNOUSERSITE=1
export PYTHONPATH=src:/tmp/p3-cxx-qualification-implementation-pip-target
TQ=tests/p3_v3/test_toolchain_qualification.py
```

- If that pip target is missing or a required command exits nonzero
  before the planned edit, stop. Do not install dependencies.

---

## File Responsibilities

```text
README.md
  P3 顶层入口；保留清晰的 P2 历史复现入口。

CONTRIBUTING.md
  P3 贡献范围、治理门槛、测试要求和 P2 只读政策。

src/p3_v3/toolchain_qualification.py
  CompilerIdentity 和 compiler identity validation seam。

tests/p3_v3/test_toolchain_qualification.py
  QualificationScenario、统一 process-group helper 及全部回归测试。
```

Do not create any other implementation file. Do not edit
`scripts/p3_v3/qualify_cxx_link.py`.

---

### Task 1: Entry, Baseline, And Frozen Evidence

**Files:**
- Read only. No implementation file is edited.
- No commit.

**Interfaces:**
- Consumes: current branch state and the isolated pip target.
- Produces: recorded SHA-256 values and a 168-passed baseline that
  later tasks must not lose except by adding the planned tests.

- [ ] **Step 1: Verify branch, HEAD, remotes, and cleanliness**

```bash
export GIT_CONFIG_GLOBAL=/dev/null
export GIT_CONFIG_NOSYSTEM=1
export GIT_CONFIG_COUNT=0
git fetch origin main cursor/p3-standards-remediation-c46c
git branch --show-current
git rev-parse HEAD
git rev-parse origin/cursor/p3-standards-remediation-c46c
git rev-parse origin/main
git status --porcelain
git rev-list --left-right --count \
  HEAD...origin/cursor/p3-standards-remediation-c46c
```

Expected:

```text
cursor/p3-standards-remediation-c46c
316ddfd05cac999389d6be5c1de4e3074d9f6e3c
316ddfd05cac999389d6be5c1de4e3074d9f6e3c
4444061dde0159a5edd62753fe3cef2d881a308c
0	0
```

Porcelain must be empty. If any value differs, stop.

- [ ] **Step 2: Confirm production root is absent**

```bash
test ! -e /tmp/p3-cxx-link-qualification && echo ROOT_ABSENT
```

Expected: `ROOT_ABSENT`. If the path exists, stop.

- [ ] **Step 3: Record failed venv and pip-target state**

```bash
stat -c '%y %n' /tmp/p3-cxx-qualification-implementation-venv
test -d /tmp/p3-cxx-qualification-implementation-pip-target \
  && echo PIP_TARGET_EXISTS
```

Expected: the failed venv exists with mtime
`2026-08-18 12:49:36.274466033 +0000` and
`PIP_TARGET_EXISTS`. Do not create, delete, or write either path.
If the pip target is missing, stop.

- [ ] **Step 4: Run the pre-edit directed baseline**

```bash
export PYTHONDONTWRITEBYTECODE=1
export PYTHONNOUSERSITE=1
export PYTHONPATH=src:/tmp/p3-cxx-qualification-implementation-pip-target
TQ=tests/p3_v3/test_toolchain_qualification.py
/usr/bin/python3 -m pytest -q -ra \
  tests/p3_v3/test_pilot.py \
  tests/p3_v3/test_pilot_build.py \
  tests/p3_v3/test_toolchain_qualification.py
```

Expected: `168 passed`, 0 failed, 0 skipped. If the count is not
168 or the command is nonzero, stop. Do not install packages.

- [ ] **Step 5: Record authority and implementation-file hashes**

```bash
sha256sum \
  docs/superpowers/specs/2026-08-18-p3-standards-remediation-design.md \
  docs/superpowers/specs/2026-08-18-p3-cursor-vm-cxx-link-qualification-design.md \
  docs/superpowers/plans/2026-08-18-p3-cursor-vm-cxx-link-qualification.md \
  docs/superpowers/plans/2026-08-19-p3-standards-remediation.md \
  README.md \
  CONTRIBUTING.md \
  src/p3_v3/toolchain_qualification.py \
  tests/p3_v3/test_toolchain_qualification.py \
  scripts/p3_v3/qualify_cxx_link.py
```

Expected specification and frozen qualification hashes:

```text
641e673a0c82c38f864d8602e06c0ce21f58f0fcb3b8dc4425d444db909c7d6e
ff438a10da0e762667fe358fb32082e2338f39f28c16620d5a15d8890e8dd8d5
9661ecb73043bb58adc9b6bad025b9051548602e74677643cb7866f4204e2901
```

Record the four implementation-file digests and the CLI digest.
This Task does not commit.

---

### Task 2: CompilerIdentity RED To GREEN

**Files:**
- Modify: `src/p3_v3/toolchain_qualification.py`
- Modify: `tests/p3_v3/test_toolchain_qualification.py`
- Test: `tests/p3_v3/test_toolchain_qualification.py`

**Interfaces:**
- Consumes: current `_resolve_compiler` tuple,
  `_capture_host_snapshot(inspection, resolved_tuple)`,
  `_resolved_null_set(path, realpath, regular, symlink)`,
  `_resolved_success_set(path, realpath, regular, symlink)`,
  `_workload_argv(compiler_path, root)`, and
  `validate_host_snapshot(value)`.
- Produces:

```python
@dataclass(frozen=True)
class CompilerIdentity:
    path: str | None
    realpath: str | None
    regular: bool | None
    symlink: bool | None

    @classmethod
    def unresolved(cls) -> "CompilerIdentity":
        return cls(None, None, None, None)

    def classification(self) -> Literal["RESOLVED", "UNRESOLVED", "INVALID"]:
        ...
```

Classification semantics:

```text
UNRESOLVED:
  path, realpath, regular, and symlink are all None

RESOLVED:
  type(path) is str
  type(realpath) is str
  regular is True
  type(symlink) is bool

INVALID:
  every other combination
```

Do not add a four-parameter coupling helper. Classification lives
only on `CompilerIdentity.classification`.

- [ ] **Step 1: Add the Task 2 imports to the test module**

In `tests/p3_v3/test_toolchain_qualification.py`, add:

```python
import inspect
from dataclasses import FrozenInstanceError, fields
```

Keep the existing `from __future__ import annotations` first.

- [ ] **Step 2: Write the failing CompilerIdentity tests**

Append these functions to
`tests/p3_v3/test_toolchain_qualification.py`.

```python
def test_compiler_identity_is_frozen_four_field_type():
    names = [item.name for item in fields(q.CompilerIdentity)]
    assert names == ["path", "realpath", "regular", "symlink"]
    identity = q.CompilerIdentity("/a", "/b", True, False)
    with pytest.raises((FrozenInstanceError, AttributeError)):
        identity.path = "/c"


def test_compiler_identity_unresolved_is_four_none():
    identity = q.CompilerIdentity.unresolved()
    assert identity.path is None
    assert identity.realpath is None
    assert identity.regular is None
    assert identity.symlink is None
    assert identity.classification() == "UNRESOLVED"


def test_resolve_compiler_returns_compiler_identity(tmp_path):
    compiler = tmp_path / "c++"
    compiler.write_bytes(b"x")
    compiler.chmod(0o755)

    def which(name: str) -> str | None:
        assert name == q.REQUESTED_COMPILER
        return str(compiler)

    identity = q._resolve_compiler(which)
    assert type(identity) is q.CompilerIdentity
    assert not isinstance(identity, tuple)
    assert identity.path == str(compiler)
    assert identity.regular is True
    assert identity.classification() == "RESOLVED"


def test_resolve_compiler_missing_returns_unresolved():
    identity = q._resolve_compiler(lambda _name: None)
    assert type(identity) is q.CompilerIdentity
    assert identity == q.CompilerIdentity.unresolved()


def test_validate_host_snapshot_uses_compiler_identity_seam():
    source = inspect.getsource(q.validate_host_snapshot)
    assert "CompilerIdentity(" in source
    assert "classification(" in source
    assert "_resolved_null_set" not in source
    assert "_resolved_success_set" not in source
    assert hasattr(q, "CompilerIdentity")
    assert not hasattr(q, "_resolved_null_set")
    assert not hasattr(q, "_resolved_success_set")


def test_partial_null_compiler_identity_is_rejected():
    host = _host(resolved_path_regular=None)
    with pytest.raises(EvidenceError, match="E_COMPILER_IDENTITY"):
        q.validate_host_snapshot(host)


def test_wrong_compiler_path_type_is_rejected():
    host = _host(resolved_compiler_path=1)
    with pytest.raises(EvidenceError, match="E_COMPILER_IDENTITY"):
        q.validate_host_snapshot(host)


def test_wrong_compiler_realpath_type_is_rejected():
    host = _host(resolved_compiler_realpath=1)
    with pytest.raises(EvidenceError, match="E_COMPILER_IDENTITY"):
        q.validate_host_snapshot(host)


def test_wrong_compiler_bool_types_are_rejected():
    with pytest.raises(EvidenceError, match="E_COMPILER_IDENTITY"):
        q.validate_host_snapshot(_host(resolved_path_regular="yes"))
    with pytest.raises(EvidenceError, match="E_COMPILER_IDENTITY"):
        q.validate_host_snapshot(_host(resolved_path_symlink="no"))


def test_host_and_intent_keep_flat_requested_compiler(tmp_path):
    result, _manifest, root = _run_synthetic_qualification(tmp_path)
    intent = read_canonical_json(root / "qualification-intent.json")
    host = intent["host_snapshot"]
    assert "compiler_identity" not in intent
    assert "compiler_identity" not in host
    assert intent["requested_compiler"] == q.REQUESTED_COMPILER
    assert host["requested_compiler"] == q.REQUESTED_COMPILER
    assert host["resolved_compiler_path"] == intent["resolved_compiler_path"]
    assert host["resolved_compiler_realpath"] == (
        intent["resolved_compiler_realpath"]
    )
    assert set(host) >= {
        "requested_compiler",
        "resolved_compiler_path",
        "resolved_compiler_realpath",
        "resolved_path_regular",
        "resolved_path_symlink",
    }
```

- [ ] **Step 3: Run the Task 2 target tests and record RED**

```bash
export PYTHONDONTWRITEBYTECODE=1
export PYTHONNOUSERSITE=1
export PYTHONPATH=src:/tmp/p3-cxx-qualification-implementation-pip-target
TQ=tests/p3_v3/test_toolchain_qualification.py
/usr/bin/python3 -m pytest -q --tb=short \
  $TQ::test_compiler_identity_is_frozen_four_field_type \
  $TQ::test_compiler_identity_unresolved_is_four_none \
  $TQ::test_resolve_compiler_returns_compiler_identity \
  $TQ::test_resolve_compiler_missing_returns_unresolved \
  $TQ::test_validate_host_snapshot_uses_compiler_identity_seam \
  $TQ::test_partial_null_compiler_identity_is_rejected \
  $TQ::test_wrong_compiler_path_type_is_rejected \
  $TQ::test_wrong_compiler_realpath_type_is_rejected \
  $TQ::test_wrong_compiler_bool_types_are_rejected \
  $TQ::test_host_and_intent_keep_flat_requested_compiler
```

Expected: nonzero exit. Failures must be `CompilerIdentity` missing,
`_resolve_compiler` still returning a tuple, or
`_resolved_null_set` / `_resolved_success_set` still present. If the
suite is green, the tests are wrong; fix the tests, not production
code.

- [ ] **Step 4: Implement CompilerIdentity and the validator seam**

In `src/p3_v3/toolchain_qualification.py` change imports to:

```python
from dataclasses import dataclass
from typing import Any, Literal
```

Add the type after the imports and before `EXECUTION_CLASS`:

```python
@dataclass(frozen=True)
class CompilerIdentity:
    path: str | None
    realpath: str | None
    regular: bool | None
    symlink: bool | None

    @classmethod
    def unresolved(cls) -> "CompilerIdentity":
        return cls(None, None, None, None)

    def classification(self) -> Literal["RESOLVED", "UNRESOLVED", "INVALID"]:
        if (
            self.path is None
            and self.realpath is None
            and self.regular is None
            and self.symlink is None
        ):
            return "UNRESOLVED"
        if (
            type(self.path) is str
            and type(self.realpath) is str
            and self.regular is True
            and type(self.symlink) is bool
        ):
            return "RESOLVED"
        return "INVALID"
```

Delete `_resolved_null_set` and `_resolved_success_set` entirely.

Replace the four-primitive block in `validate_host_snapshot` with:

```python
    identity = CompilerIdentity(
        path=snapshot["resolved_compiler_path"],
        realpath=snapshot["resolved_compiler_realpath"],
        regular=snapshot["resolved_path_regular"],
        symlink=snapshot["resolved_path_symlink"],
    )
    kind = identity.classification()
    if kind == "UNRESOLVED":
        pass
    elif kind == "RESOLVED":
        _require_absolute(identity.path, "host_snapshot.resolved_compiler_path")
        _require_absolute(
            identity.realpath,
            "host_snapshot.resolved_compiler_realpath",
        )
    else:
        raise EvidenceError(
            "E_COMPILER_IDENTITY",
            "host_snapshot resolved identity fields are not coupled",
        )
```

Keep the existing
`snapshot["requested_compiler"] != REQUESTED_COMPILER` check on the
external object. Do not store that name on `CompilerIdentity`.

Replace `_resolve_compiler` with:

```python
def _resolve_compiler(
    which: Callable[[str], str | None],
) -> CompilerIdentity:
    resolved = which(REQUESTED_COMPILER)
    if resolved is None or resolved == "":
        return CompilerIdentity.unresolved()
    path = resolved if os.path.isabs(resolved) else str(Path(resolved).resolve())
    real = os.path.realpath(path)
    symlink = os.path.islink(path)
    regular = os.path.isfile(real) and not os.path.islink(real)
    if not regular:
        return CompilerIdentity.unresolved()
    if not os.access(path, os.X_OK) or not os.access(real, os.X_OK):
        return CompilerIdentity.unresolved()
    return CompilerIdentity(path, real, True, symlink)
```

Replace `_capture_host_snapshot` with:

```python
def _capture_host_snapshot(
    inspection: Mapping[str, Any],
    identity: CompilerIdentity,
) -> dict[str, Any]:
    uname = os.uname()
    return _self_hash(
        {
            "schema_version": HOST_SCHEMA,
            "os_name": uname.sysname,
            "os_release": uname.version,
            "kernel_release": uname.release,
            "machine": uname.machine,
            "node_name": uname.nodename,
            "python_version": platform.python_version(),
            "git_version": inspection["git_version"],
            "repository_commit": inspection["repository_commit"],
            "repository_clean": True,
            "requested_compiler": REQUESTED_COMPILER,
            "resolved_compiler_path": identity.path,
            "resolved_compiler_realpath": identity.realpath,
            "resolved_path_regular": identity.regular,
            "resolved_path_symlink": identity.symlink,
        }
    )
```

In `run_qualification`, after `os.mkdir(qualification_root)`:

```python
    resolution_error = False
    try:
        identity = _resolve_compiler(which)
    except OSError:
        identity = CompilerIdentity.unresolved()
        resolution_error = True
    host = _capture_host_snapshot(entry, identity)
    _write_exclusive_bytes(qualification_root / SOURCE_NAME, SOURCE_BYTES)
    compile_argv, run_argv = _workload_argv(
        identity.path,
        str(qualification_root),
    )
```

In the intent object, set:

```python
            "requested_compiler": REQUESTED_COMPILER,
            "resolved_compiler_path": identity.path,
            "resolved_compiler_realpath": identity.realpath,
```

Do not keep `resolved[0]` or `resolved[1]`. Do not change
`INTENT_SCHEMA`, `HOST_SCHEMA`, `RESULT_SCHEMA`, `MANIFEST_SCHEMA`,
`PROCESS_SCHEMA`, `SPEC_PATH`, `SPEC_SHA256`, or failure reasons.

- [ ] **Step 5: Run Task 2 tests and the qualification file**

```bash
export PYTHONDONTWRITEBYTECODE=1
export PYTHONNOUSERSITE=1
export PYTHONPATH=src:/tmp/p3-cxx-qualification-implementation-pip-target
TQ=tests/p3_v3/test_toolchain_qualification.py
/usr/bin/python3 -m pytest -q --tb=short \
  $TQ::test_compiler_identity_is_frozen_four_field_type \
  $TQ::test_compiler_identity_unresolved_is_four_none \
  $TQ::test_resolve_compiler_returns_compiler_identity \
  $TQ::test_resolve_compiler_missing_returns_unresolved \
  $TQ::test_validate_host_snapshot_uses_compiler_identity_seam \
  $TQ::test_partial_null_compiler_identity_is_rejected \
  $TQ::test_wrong_compiler_path_type_is_rejected \
  $TQ::test_wrong_compiler_realpath_type_is_rejected \
  $TQ::test_wrong_compiler_bool_types_are_rejected \
  $TQ::test_host_and_intent_keep_flat_requested_compiler
/usr/bin/python3 -m pytest -q --tb=short \
  tests/p3_v3/test_toolchain_qualification.py
```

Expected: target tests pass; full qualification file passes. Do not
upgrade any FAIL reason to PASS.

- [ ] **Step 6: Commit only the two allowed files**

```bash
git add -- \
  src/p3_v3/toolchain_qualification.py \
  tests/p3_v3/test_toolchain_qualification.py
git diff --cached --name-only
git commit -m "refactor(p3-v3): name compiler identity"
```

Expected staged set is exactly those two paths.

---

### Task 3: QualificationScenario RED To GREEN

**Files:**
- Modify: `tests/p3_v3/test_toolchain_qualification.py`
- Test: `tests/p3_v3/test_toolchain_qualification.py`

**Interfaces:**
- Consumes: `_run_synthetic_qualification(tmp_path, **opts: object)`
  and every current keyword call site listed in Step 5.
- Produces:

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


def _run_synthetic_qualification(
    tmp_path: Path,
    scenario: QualificationScenario | None = None,
) -> tuple[dict[str, Any], dict[str, Any], Path]:
    ...
```

If `scenario is None`, construct `QualificationScenario()`.

- [ ] **Step 1: Add dataclass imports used by the scenario type**

In `tests/p3_v3/test_toolchain_qualification.py`:

```python
from collections.abc import Mapping
from dataclasses import dataclass, field, fields, FrozenInstanceError
from typing import Any
```

If Task 2 already imported `fields` and `FrozenInstanceError`, keep
one import line. Do not import `dataclass` in the production module
for this Task.

- [ ] **Step 2: Write the failing QualificationScenario tests**

Append:

```python
def test_qualification_scenario_is_frozen():
    names = [item.name for item in fields(QualificationScenario)]
    assert "env" in names
    assert "create_regular_executable" in names
    scenario = QualificationScenario()
    with pytest.raises((FrozenInstanceError, AttributeError)):
        scenario.missing_compiler = True


def test_qualification_scenario_rejects_unknown_field():
    with pytest.raises(TypeError):
        QualificationScenario(unknown_flag=True)


def test_default_qualification_scenario_stays_synthetic_pass(tmp_path):
    result, _manifest, root = _run_synthetic_qualification(tmp_path)
    assert result["terminal_status"] == "PASS"
    qualify = root / "qualify"
    assert qualify.is_file()
    assert os.access(qualify, os.X_OK)


def test_synthetic_helper_rejects_legacy_keyword_flags(tmp_path):
    with pytest.raises(TypeError):
        _run_synthetic_qualification(tmp_path, missing_compiler=True)


def test_synthetic_helper_has_no_var_keyword():
    kinds = {
        item.kind
        for item in inspect.signature(
            _run_synthetic_qualification
        ).parameters.values()
    }
    assert inspect.Parameter.VAR_KEYWORD not in kinds


def test_synthetic_helper_source_has_no_opts_bag():
    source = inspect.getsource(_run_synthetic_qualification)
    assert "opts.get" not in source
    assert "**opts" not in source
```

- [ ] **Step 3: Run the Task 3 target tests and record RED**

```bash
export PYTHONDONTWRITEBYTECODE=1
export PYTHONNOUSERSITE=1
export PYTHONPATH=src:/tmp/p3-cxx-qualification-implementation-pip-target
TQ=tests/p3_v3/test_toolchain_qualification.py
/usr/bin/python3 -m pytest -q --tb=short \
  $TQ::test_qualification_scenario_is_frozen \
  $TQ::test_qualification_scenario_rejects_unknown_field \
  $TQ::test_default_qualification_scenario_stays_synthetic_pass \
  $TQ::test_synthetic_helper_rejects_legacy_keyword_flags \
  $TQ::test_synthetic_helper_has_no_var_keyword \
  $TQ::test_synthetic_helper_source_has_no_opts_bag
```

Expected: nonzero exit because `QualificationScenario` is missing
and `_run_synthetic_qualification` still has `**opts`.
`test_synthetic_helper_rejects_legacy_keyword_flags` must fail
while the helper still accepts `missing_compiler=True`.
`test_synthetic_helper_has_no_var_keyword` must fail while
`VAR_KEYWORD` remains.

- [ ] **Step 4: Add QualificationScenario and rewrite the helper**

Place this class above `_run_synthetic_qualification`:

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

Replace `_run_synthetic_qualification` with:

```python
def _run_synthetic_qualification(
    tmp_path: Path,
    scenario: QualificationScenario | None = None,
) -> tuple[dict[str, Any], dict[str, Any], Path]:
    if scenario is None:
        scenario = QualificationScenario()
    repo = _init_repo(tmp_path)
    root = tmp_path / "qual"
    compiler = _make_compiler(tmp_path)
    calls: list[list[str]] = []
    env = dict(scenario.env)
    if scenario.compiler_version_stdout is not None:
        version_stdout = scenario.compiler_version_stdout
    elif scenario.metadata_wait_error:
        version_stdout = b"partial"
    else:
        version_stdout = b"clang\n"

    def which(name: str) -> str | None:
        if scenario.missing_compiler:
            return None
        if name == "c++":
            return str(compiler)
        return None

    def popen(argv: list[str], **kwargs: object) -> _Proc:
        assert kwargs.get("shell") is False
        assert kwargs.get("start_new_session") is True
        assert kwargs.get("stdout") is subprocess.PIPE
        assert kwargs.get("stderr") is subprocess.PIPE
        calls.append(list(argv))
        if argv[-1:] == ["--version"] or argv[-1] == "--version":
            if scenario.metadata_popen_error:
                raise PermissionError("synthetic metadata popen denied")
            if scenario.observe_metadata_fs:
                assert (root / "qualification-intent.json").is_file()
                assert (root / "qualify.cpp").is_file()
                assert not (root / "qualification-result.json").exists()
                assert not (root / "qualification-manifest.json").exists()
            if scenario.metadata_wait_error:
                return _Proc(
                    stdout=version_stdout,
                    stderr=scenario.compiler_version_stderr,
                    wait_error=True,
                    cleanup_error=scenario.cleanup_error,
                )
            if scenario.compiler_version_timeout:
                return _Proc(
                    stdout=version_stdout,
                    stderr=scenario.compiler_version_stderr,
                    timed_out=True,
                    cleanup_error=scenario.cleanup_error,
                )
            return _Proc(
                stdout=version_stdout,
                stderr=scenario.compiler_version_stderr,
                returncode=scenario.compiler_version_exit,
            )
        if "-std=c++14" in argv:
            if scenario.compile_popen_error:
                raise OSError("synthetic compile popen denied")
            if scenario.create_regular_executable:
                out = root / "qualify"
                out.write_bytes(b"ELF")
                out.chmod(0o755)
            if scenario.create_symlink_executable:
                target = root / "qualify.target"
                target.write_bytes(b"ELF")
                (root / "qualify").symlink_to(target)
            if scenario.create_nonregular_executable:
                (root / "qualify").mkdir()
            if scenario.create_nonexecutable_executable:
                out = root / "qualify"
                out.write_bytes(b"ELF")
                out.chmod(0o644)
            if scenario.mutate_repo_during_compile or (
                scenario.mutate_repo_during_last_job
                and scenario.binary_unreached
            ):
                (repo / "drift.txt").write_text("x")
            if scenario.compile_wait_error:
                return _Proc(
                    stdout=scenario.compile_stdout,
                    stderr=scenario.compile_stderr,
                    wait_error=True,
                    cleanup_error=scenario.cleanup_error,
                )
            if scenario.compile_timeout:
                return _Proc(
                    timed_out=True,
                    cleanup_error=scenario.cleanup_error,
                )
            return _Proc(
                stdout=scenario.compile_stdout,
                stderr=scenario.compile_stderr,
                returncode=scenario.compile_exit,
            )
        if scenario.binary_popen_error:
            raise OSError("synthetic binary popen denied")
        if scenario.mutate_repo_during_last_job:
            (repo / "drift.txt").write_text("x")
        if scenario.binary_timeout:
            return _Proc(
                timed_out=True,
                cleanup_error=scenario.cleanup_error,
            )
        return _Proc(
            stdout=scenario.binary_stdout,
            stderr=scenario.binary_stderr,
            returncode=scenario.binary_exit,
        )

    if scenario.compiler_not_executable:
        compiler.chmod(0o644)
    result = q.run_qualification(
        repo_root=repo,
        qualification_root=root,
        env=env,
        which=which,
        popen=popen,
    )
    manifest = read_canonical_json(root / "qualification-manifest.json")
    result["_calls"] = calls
    return result, manifest, root
```

Do not write `opts["create_regular_executable"] = True`. Do not
resolve or execute a real `c++`.

- [ ] **Step 5: Convert every current keyword call site**

Replace each helper invocation as follows. Do not leave a keyword
flag on `_run_synthetic_qualification`.

```python
_run_synthetic_qualification(tmp_path, env=env)
# becomes
_run_synthetic_qualification(
    tmp_path,
    QualificationScenario(env=env),
)

_run_synthetic_qualification(tmp_path, observe_metadata_fs=True)
# becomes
_run_synthetic_qualification(
    tmp_path,
    QualificationScenario(observe_metadata_fs=True),
)

_run_synthetic_qualification(tmp_path, missing_compiler=True)
# becomes
_run_synthetic_qualification(
    tmp_path,
    QualificationScenario(missing_compiler=True),
)

_run_synthetic_qualification(tmp_path)
# stays
_run_synthetic_qualification(tmp_path)

_run_synthetic_qualification(
    tmp_path,
    compiler_version_timeout=True,
)
# becomes
_run_synthetic_qualification(
    tmp_path,
    QualificationScenario(compiler_version_timeout=True),
)

_run_synthetic_qualification(tmp_path, compiler_version_exit=2)
# becomes
_run_synthetic_qualification(
    tmp_path,
    QualificationScenario(compiler_version_exit=2),
)

_run_synthetic_qualification(
    tmp_path,
    compile_exit=0,
    compile_stdout=b"warning\n",
    create_regular_executable=True,
)
# becomes
_run_synthetic_qualification(
    tmp_path,
    QualificationScenario(
        compile_exit=0,
        compile_stdout=b"warning\n",
        create_regular_executable=True,
    ),
)

_run_synthetic_qualification(
    tmp_path,
    compile_stderr=b"note\n",
    create_regular_executable=True,
)
# becomes
_run_synthetic_qualification(
    tmp_path,
    QualificationScenario(
        compile_stderr=b"note\n",
        create_regular_executable=True,
    ),
)

_run_synthetic_qualification(tmp_path, binary_stdout=b"hi\n")
# becomes
_run_synthetic_qualification(
    tmp_path,
    QualificationScenario(binary_stdout=b"hi\n"),
)

_run_synthetic_qualification(tmp_path, binary_stderr=b"err\n")
# becomes
_run_synthetic_qualification(
    tmp_path,
    QualificationScenario(binary_stderr=b"err\n"),
)

_run_synthetic_qualification(
    tmp_path,
    compile_exit=0,
    create_regular_executable=False,
    create_symlink_executable=True,
)
# becomes
_run_synthetic_qualification(
    tmp_path,
    QualificationScenario(
        compile_exit=0,
        create_regular_executable=False,
        create_symlink_executable=True,
    ),
)

_run_synthetic_qualification(
    tmp_path,
    create_regular_executable=False,
)
# becomes
_run_synthetic_qualification(
    tmp_path,
    QualificationScenario(create_regular_executable=False),
)

_run_synthetic_qualification(
    tmp_path,
    create_regular_executable=False,
    create_nonregular_executable=True,
)
# becomes
_run_synthetic_qualification(
    tmp_path,
    QualificationScenario(
        create_regular_executable=False,
        create_nonregular_executable=True,
    ),
)

_run_synthetic_qualification(
    tmp_path,
    compile_exit=3,
    create_regular_executable=True,
)
# becomes
_run_synthetic_qualification(
    tmp_path,
    QualificationScenario(
        compile_exit=3,
        create_regular_executable=True,
    ),
)

_run_synthetic_qualification(
    tmp_path,
    compile_timeout=True,
    create_regular_executable=True,
)
# becomes
_run_synthetic_qualification(
    tmp_path,
    QualificationScenario(
        compile_timeout=True,
        create_regular_executable=True,
    ),
)

_run_synthetic_qualification(
    tmp_path,
    compiler_version_timeout=True,
    compiler_version_stdout=b"partial",
)
# becomes
_run_synthetic_qualification(
    tmp_path,
    QualificationScenario(
        compiler_version_timeout=True,
        compiler_version_stdout=b"partial",
    ),
)

_run_synthetic_qualification(
    tmp_path,
    compile_exit=3,
    create_regular_executable=True,
    mutate_repo_during_compile=True,
)
# becomes
_run_synthetic_qualification(
    tmp_path,
    QualificationScenario(
        compile_exit=3,
        create_regular_executable=True,
        mutate_repo_during_compile=True,
    ),
)

_run_synthetic_qualification(
    tmp_path,
    mutate_repo_during_last_job=True,
)
# becomes
_run_synthetic_qualification(
    tmp_path,
    QualificationScenario(mutate_repo_during_last_job=True),
)

_run_synthetic_qualification(
    tmp_path,
    compile_exit=0,
    create_regular_executable=True,
    binary_exit=7,
)
# becomes
_run_synthetic_qualification(
    tmp_path,
    QualificationScenario(
        compile_exit=0,
        create_regular_executable=True,
        binary_exit=7,
    ),
)

_run_synthetic_qualification(tmp_path, binary_timeout=True)
# becomes
_run_synthetic_qualification(
    tmp_path,
    QualificationScenario(binary_timeout=True),
)

_run_synthetic_qualification(tmp_path, metadata_popen_error=True)
# becomes
_run_synthetic_qualification(
    tmp_path,
    QualificationScenario(metadata_popen_error=True),
)

_run_synthetic_qualification(tmp_path, compile_popen_error=True)
# becomes
_run_synthetic_qualification(
    tmp_path,
    QualificationScenario(compile_popen_error=True),
)

_run_synthetic_qualification(tmp_path, binary_popen_error=True)
# becomes
_run_synthetic_qualification(
    tmp_path,
    QualificationScenario(binary_popen_error=True),
)

_run_synthetic_qualification(
    tmp_path,
    compiler_version_timeout=True,
    cleanup_error=True,
    compiler_version_stdout=b"partial",
)
# becomes
_run_synthetic_qualification(
    tmp_path,
    QualificationScenario(
        compiler_version_timeout=True,
        cleanup_error=True,
        compiler_version_stdout=b"partial",
    ),
)

_run_synthetic_qualification(
    tmp_path,
    compile_exit=0,
    create_regular_executable=False,
    create_nonexecutable_executable=True,
)
# becomes
_run_synthetic_qualification(
    tmp_path,
    QualificationScenario(
        compile_exit=0,
        create_regular_executable=False,
        create_nonexecutable_executable=True,
    ),
)

_run_synthetic_qualification(
    tmp_path,
    compiler_not_executable=True,
)
# becomes
_run_synthetic_qualification(
    tmp_path,
    QualificationScenario(compiler_not_executable=True),
)

_run_synthetic_qualification(
    tmp_path,
    compile_timeout=True,
    cleanup_error=True,
    create_regular_executable=True,
)
# becomes
_run_synthetic_qualification(
    tmp_path,
    QualificationScenario(
        compile_timeout=True,
        cleanup_error=True,
        create_regular_executable=True,
    ),
)

_run_synthetic_qualification(tmp_path, metadata_wait_error=True)
# becomes
_run_synthetic_qualification(
    tmp_path,
    QualificationScenario(metadata_wait_error=True),
)

_run_synthetic_qualification(
    tmp_path,
    metadata_wait_error=True,
    cleanup_error=True,
)
# becomes
_run_synthetic_qualification(
    tmp_path,
    QualificationScenario(
        metadata_wait_error=True,
        cleanup_error=True,
    ),
)

_run_synthetic_qualification(
    tmp_path,
    compile_wait_error=True,
    create_regular_executable=True,
)
# becomes
_run_synthetic_qualification(
    tmp_path,
    QualificationScenario(
        compile_wait_error=True,
        create_regular_executable=True,
    ),
)

_run_synthetic_qualification(
    tmp_path,
    compile_wait_error=True,
    cleanup_error=True,
    create_regular_executable=True,
)
# becomes
_run_synthetic_qualification(
    tmp_path,
    QualificationScenario(
        compile_wait_error=True,
        cleanup_error=True,
        create_regular_executable=True,
    ),
)
```

After conversion, `rg -n 'opts\\.get|\\*\\*opts' tests/p3_v3/test_toolchain_qualification.py`
must print nothing.

- [ ] **Step 6: Run Task 3 tests and the qualification file**

```bash
export PYTHONDONTWRITEBYTECODE=1
export PYTHONNOUSERSITE=1
export PYTHONPATH=src:/tmp/p3-cxx-qualification-implementation-pip-target
TQ=tests/p3_v3/test_toolchain_qualification.py
/usr/bin/python3 -m pytest -q --tb=short \
  $TQ::test_qualification_scenario_is_frozen \
  $TQ::test_qualification_scenario_rejects_unknown_field \
  $TQ::test_default_qualification_scenario_stays_synthetic_pass \
  $TQ::test_synthetic_helper_rejects_legacy_keyword_flags \
  $TQ::test_synthetic_helper_has_no_var_keyword \
  $TQ::test_synthetic_helper_source_has_no_opts_bag
/usr/bin/python3 -m pytest -q --tb=short \
  tests/p3_v3/test_toolchain_qualification.py
```

Expected: target tests pass; full qualification file passes.
Terminal statuses and failure reasons stay the same as Task 1.

- [ ] **Step 7: Commit only the test module**

```bash
git add -- tests/p3_v3/test_toolchain_qualification.py
git diff --cached --name-only
git commit -m "refactor(p3-v3): type qualification scenarios"
```

Expected staged set is exactly that one path.

---

### Task 4: Unified Process-Group Helper RED To GREEN

**Files:**
- Modify: `tests/p3_v3/test_toolchain_qualification.py`
- Test: `tests/p3_v3/test_toolchain_qualification.py`

**Interfaces:**
- Consumes: `_patch_group_signals` and `_patch_group_probe`.
- Produces:

```python
def _patch_process_group(
    monkeypatch: pytest.MonkeyPatch,
    *,
    terminate_error: BaseException | None = None,
    probe_error: BaseException | None = None,
) -> list[tuple[object, ...]]:
    ...
```

Do not add any other parameter. Do not change production
`_process_group_absent`.

- [ ] **Step 1: Write the failing process-group helper tests**

Append:

```python
def test_patch_process_group_exists_and_old_helpers_do_not():
    assert hasattr(q, "_process_group_absent")
    source = Path("tests/p3_v3/test_toolchain_qualification.py").read_text()
    assert "def _patch_process_group(" in source
    assert "def _patch_group_signals(" not in source
    assert "def _patch_group_probe(" not in source


def test_patch_process_group_signature_has_no_pid_probe_parameter():
    params = inspect.signature(_patch_process_group).parameters
    assert set(params) == {
        "monkeypatch",
        "terminate_error",
        "probe_error",
    }


def test_patch_process_group_uses_separate_killpg_errors(monkeypatch):
    recorded = _patch_process_group(
        monkeypatch,
        terminate_error=PermissionError("term"),
        probe_error=OSError(errno.ESRCH, "gone"),
    )
    with pytest.raises(PermissionError, match="term"):
        q.os.killpg(7, signal.SIGKILL)
    with pytest.raises(OSError) as exc_info:
        q.os.killpg(7, 0)
    assert exc_info.value.errno == errno.ESRCH
    q.os.getpgid(9)
    assert ("getpgid", 9) in recorded
    with pytest.raises(AssertionError):
        q.os.killpg(7, 9)


def test_patch_process_group_rejects_os_kill(monkeypatch):
    _patch_process_group(monkeypatch)
    with pytest.raises(AssertionError):
        q.os.kill(2_000_000_000, 0)
    with pytest.raises(AssertionError):
        q.os.kill(2_000_000_000, signal.SIGKILL)


def test_timeout_group_present_is_cleanup_failed(tmp_path, monkeypatch):
    recorded = _patch_process_group(monkeypatch)
    result, _manifest, _root = _run_synthetic_qualification(
        tmp_path,
        QualificationScenario(compiler_version_timeout=True),
    )
    version = result["compiler_version"]
    assert version["terminal_status"] == "FAIL"
    assert version["failure_reason"] == "PROCESS_CLEANUP_FAILED"
    assert version["process_group_terminated"] is False
    assert ("killpg", 2_000_000_000, signal.SIGKILL) in recorded
    assert ("killpg", 2_000_000_000, 0) in recorded
    assert not any(item[0] == "kill" for item in recorded)


def test_wait_error_group_present_is_cleanup_failed(tmp_path, monkeypatch):
    recorded = _patch_process_group(monkeypatch)
    result, _manifest, _root = _run_synthetic_qualification(
        tmp_path,
        QualificationScenario(metadata_wait_error=True),
    )
    version = result["compiler_version"]
    assert version["terminal_status"] == "FAIL"
    assert version["failure_reason"] == "PROCESS_CLEANUP_FAILED"
    assert version["process_group_terminated"] is False
    assert ("killpg", 2_000_000_000, 0) in recorded
    assert not any(item[0] == "kill" for item in recorded)
```

- [ ] **Step 2: Run the Task 4 target tests and record RED**

```bash
export PYTHONDONTWRITEBYTECODE=1
export PYTHONNOUSERSITE=1
export PYTHONPATH=src:/tmp/p3-cxx-qualification-implementation-pip-target
TQ=tests/p3_v3/test_toolchain_qualification.py
/usr/bin/python3 -m pytest -q --tb=short \
  $TQ::test_patch_process_group_exists_and_old_helpers_do_not \
  $TQ::test_patch_process_group_signature_has_no_pid_probe_parameter \
  $TQ::test_patch_process_group_uses_separate_killpg_errors \
  $TQ::test_patch_process_group_rejects_os_kill \
  $TQ::test_timeout_group_present_is_cleanup_failed \
  $TQ::test_wait_error_group_present_is_cleanup_failed
```

Expected: nonzero exit because `_patch_process_group` is missing
or `_patch_group_signals` / `_patch_group_probe` still exist.

- [ ] **Step 3: Replace the two helpers with one helper**

Delete `_patch_group_signals` and `_patch_group_probe`. Do not leave
aliases. Insert:

```python
def _patch_process_group(
    monkeypatch: pytest.MonkeyPatch,
    *,
    terminate_error: BaseException | None = None,
    probe_error: BaseException | None = None,
) -> list[tuple[object, ...]]:
    recorded: list[tuple[object, ...]] = []

    def fake_getpgid(pid: int) -> int:
        recorded.append(("getpgid", pid))
        return pid

    def fake_killpg(pgid: int, sig: int) -> None:
        recorded.append(("killpg", pgid, sig))
        if sig == signal.SIGKILL:
            if terminate_error is not None:
                raise terminate_error
            return
        if sig == 0:
            if probe_error is not None:
                raise probe_error
            return
        raise AssertionError(f"unexpected killpg signal: {sig}")

    def fake_kill(*_args: object) -> None:
        raise AssertionError("os.kill must not probe process groups")

    monkeypatch.setattr(q.os, "getpgid", fake_getpgid)
    monkeypatch.setattr(q.os, "killpg", fake_killpg)
    monkeypatch.setattr(q.os, "kill", fake_kill)
    return recorded
```

Do not read `/proc`. Do not use pidfd. Do not call `os.kill` inside
the helper except to install `fake_kill`.

- [ ] **Step 4: Retarget every current helper call**

```text
_patch_group_signals(..., killpg_error=E)
  -> _patch_process_group(..., terminate_error=E)

_patch_group_signals(..., probe_error=E)
  -> _patch_process_group(..., probe_error=E)

_patch_group_signals(..., killpg_error=E, probe_error=F)
  -> _patch_process_group(..., terminate_error=E, probe_error=F)

_patch_group_signals(monkeypatch)
  -> _patch_process_group(monkeypatch)

_patch_group_probe(monkeypatch)
  -> _patch_process_group(monkeypatch)

_patch_group_probe(monkeypatch, probe_error=E)
  -> _patch_process_group(monkeypatch, probe_error=E)
```

Exact replacements required in the current tests:

```python
# test_timeout_fails_when_killpg_zero_probe_succeeds
recorded = _patch_process_group(monkeypatch)

# test_wait_error_fails_when_killpg_zero_probe_succeeds
recorded = _patch_process_group(monkeypatch)

# test_timeout_fails_when_killpg_zero_probe_is_permission
recorded = _patch_process_group(
    monkeypatch,
    probe_error=PermissionError("denied"),
)

# test_timeout_cleanup_succeeds_when_leader_reaped_and_pgid_absent
recorded = _patch_process_group(
    monkeypatch,
    probe_error=ProcessLookupError("gone"),
)

# test_timeout_cleanup_fails_when_pgid_still_exists
recorded = _patch_process_group(monkeypatch)

# test_timeout_cleanup_fails_when_killpg_fails_and_only_leader_killed
recorded = _patch_process_group(
    monkeypatch,
    terminate_error=PermissionError("denied"),
    probe_error=ProcessLookupError("gone"),
)

# test_metadata_wait_error_cleans_up_and_closes
recorded = _patch_process_group(
    monkeypatch,
    probe_error=ProcessLookupError("gone"),
)

# test_compile_wait_error_cleans_up_and_closes
_patch_process_group(
    monkeypatch,
    probe_error=ProcessLookupError("gone"),
)
```

A no-error `_patch_process_group(monkeypatch)` makes
`killpg(pgid, 0)` return normally, which means the group still
exists. `ProcessLookupError` and `ESRCH` are applied only through
`probe_error` on `killpg(..., 0)`.

After replacement,
`rg -n '_patch_group_signals|_patch_group_probe' tests/p3_v3/test_toolchain_qualification.py`
must print nothing.

Do not modify `q._process_group_absent`. Do not add a third helper.

- [ ] **Step 5: Run Task 4 tests and the qualification file**

```bash
export PYTHONDONTWRITEBYTECODE=1
export PYTHONNOUSERSITE=1
export PYTHONPATH=src:/tmp/p3-cxx-qualification-implementation-pip-target
TQ=tests/p3_v3/test_toolchain_qualification.py
/usr/bin/python3 -m pytest -q --tb=short \
  $TQ::test_patch_process_group_exists_and_old_helpers_do_not \
  $TQ::test_patch_process_group_signature_has_no_pid_probe_parameter \
  $TQ::test_patch_process_group_uses_separate_killpg_errors \
  $TQ::test_patch_process_group_rejects_os_kill \
  $TQ::test_timeout_group_present_is_cleanup_failed \
  $TQ::test_wait_error_group_present_is_cleanup_failed \
  tests/p3_v3/test_toolchain_qualification.py \
  -k 'process_group_absent or killpg_zero or timeout_cleanup or wait_error'
/usr/bin/python3 -m pytest -q --tb=short \
  tests/p3_v3/test_toolchain_qualification.py
```

Expected: target tests pass; full qualification file passes. Any
test that uses `_patch_process_group` must turn RED immediately if
production code or a helper calls `os.kill`.

- [ ] **Step 6: Commit only the test module**

```bash
git add -- tests/p3_v3/test_toolchain_qualification.py
git diff --cached --name-only
git commit -m "refactor(p3-v3): unify process-group test helper"
```

Expected staged set is exactly that one path.

---

### Task 5: Rewrite The P3 Repository Entry

**Files:**
- Modify: `README.md`
- Modify: `CONTRIBUTING.md`

**Interfaces:**
- Consumes: the approved Part 1 identity rules.
- Produces: P3-first public documents with a historical P2 section.

- [ ] **Step 1: Rewrite README.md with this exact section set**

Write `README.md` as:

~~~~markdown
# P3 Semantic Mutation

This GitHub repository is the P3 Semantic Mutation working tree.
It is not a P2-only replica.

## Status And Claim Ceiling

Formal claims remain blocked. Formal denominator membership is
false. Attempt-2 is not authorized. Nothing in this repository
entry upgrades those invariants.

## Active P3 Work

Current in-tree engineering is:

- P3 v3 evidence infrastructure under `src/p3_v3/` and
  `tests/p3_v3/`
- the Boost.Math pilot, with claims blocked
- the Cursor VM C++ compile-link qualification in
  `src/p3_v3/toolchain_qualification.py` and
  `scripts/p3_v3/qualify_cxx_link.py`

Qualification PASS, if later authorized and obtained, proves only
that one frozen C++14 program compiled, linked, and ran on that
VM. It does not authorize Boost.Math, CMake, attempt-2, or paper
Results.

## Repository Layout

```
.
├── src/p3_v3/           # P3 v3 evidence, pilot, and qualification
├── tests/p3_v3/         # P3 v3 synthetic tests
├── scripts/p3_v3/       # P3 CLIs, including qualify_cxx_link.py
├── docs/superpowers/    # P3 designs and implementation plans
├── src/p2/              # historical P2 implementation, read-only
├── tests/               # includes historical P2 tests
├── scripts/             # includes historical P2 campaign scripts
├── data/                # historical P2 SSOT and caches, read-only
├── submission/          # historical P2 IST bundle, read-only
├── replication/         # historical P2 Zenodo bundle, read-only
└── third_party/p1_avp/  # locked P1 AVP reference
```

## Testing

P3 qualification tests use synthetic `which` and `popen`. They
must not resolve or execute a host `c++`. Do not hard-code a
passing-test total in this file; report the count from the command
that was actually run.

The isolated Cursor VM recipe, when that environment is present,
is `/usr/bin/python3` with `PYTHONPATH` including `src` and the
already-provisioned third-party target. Do not reuse a failed
virtualenv.

## Governance And Production Authorization

Editing this repository does not authorize:

- running `scripts/p3_v3/qualify_cxx_link.py`
- invoking a real compiler, CMake, or Boost.Math
- creating `/tmp/p3-cxx-link-qualification`
- attempt-2
- claim or denominator upgrades

Those actions require a later explicit user authorization.

## Historical P2 Reproduction Layer

P2 is a read-only historical reproduction layer for the IST
Semantic Mutation Score audit. Do not add P2 operators, rewrite
P2 numbers, or edit P2 manuscripts as part of P3 work.

The following historical commands keep their original flags and
environment variables.

### P2 smoke

```bash
git clone <this-repo>.git p2-sms-audit
cd p2-sms-audit
python3.12 -m venv .venv
.venv/bin/pip install -r requirements-frozen.txt

PYTHONPATH=src .venv/bin/pytest tests/ -q

PYTHONPATH=src SMS_VERSION=v4 P2_PRIMARY_VERSION=v3b \
  .venv/bin/python scripts/build_paper_numbers.py
```

Expected historical outcome: `data/results/paper_numbers_v4.json`
is rewritten byte-identically. If
`git diff data/results/paper_numbers_v4.json` is empty, the
historical SSOT is verified.

### P2 cache replay

```bash
PYTHONPATH=src .venv/bin/python scripts/operator_campaign.py \
    --replay-from-cache

PYTHONPATH=src .venv/bin/python scripts/compute_rq2_v4_mp5.py
PYTHONPATH=src .venv/bin/python scripts/compute_rq3_friedman.py
PYTHONPATH=src .venv/bin/python scripts/compute_rq4.py

PYTHONPATH=src .venv/bin/python scripts/compute_lrca_v4_mp5.py

PYTHONPATH=src .venv/bin/python scripts/p2_vs_syntactic_ast_diff_batch.py

PYTHONPATH=src SMS_VERSION=v4 P2_PRIMARY_VERSION=v3b \
  .venv/bin/python scripts/build_paper_numbers.py

PYTHONPATH=src .venv/bin/python scripts/generate_figures.py
```

### P2 re-LLM

```bash
cp .env.example .env

PYTHONPATH=src .venv/bin/python scripts/cross_source_campaign.py \
    --concurrency 6 --temperature 0
```

See `REPRODUCIBILITY.md` and `DATASET.md` for the historical P2
cost table, licences, and artefact provenance.

## Citation And Legacy Artefacts

P2 citation files remain in `replication/` and `CITATION.cff`.
This file does not mint an arXiv identifier or a DOI.

Historical P2 manuscript and submission files remain under
`submission/` and the P2 manuscript names. They are read-only.
~~~~

Do not copy fabricated bibliographic identifiers into the new
README. Point at the existing citation files instead.

- [ ] **Step 2: Rewrite CONTRIBUTING.md with this exact section set**

Write `CONTRIBUTING.md` as:

```markdown
# Contributing

This repository is the P3 Semantic Mutation project. P2 remains
present as a read-only historical reproduction layer.

## Repository Scope

- This **is** the P3 working tree.
- This **is not** a general-purpose mutation-testing framework.
- P3 work lives in `src/p3_v3/`, `tests/p3_v3/`, `scripts/p3_v3/`,
  and later-authorized documentation under `docs/superpowers/`.
- P2 trees are historical. They are not a second active product
  surface.

## P3 Contributions

Welcome through issues and pull requests:

- synthetic tests and documentation for existing P3 v3 modules
- fixes that stay inside a later-authorized writable set
- reports that a documented P3 command failed in a synthetic or
  authorized environment

P3 issues are in scope for this repository. Do not mark them as
belonging to another repository.

## P2 Read-Only Historical Layer

P2 replication-failure reports remain welcome. When opening one,
include the command, the last 50 lines of output, Python and OS
identity, and whether cache replay or re-LLM was used.

Do not accept changes that:

- edit `src/p2/`, P2-only tests, `data/`, `submission/`,
  `replication/`, or P2 manuscripts
- change `data/results/paper_numbers_v4.json` or other P2 SSOT
  files
- reclassify P2 results as P3 results

## Required Design And Review Gates

Implementation of a new P3 behaviour starts only after an
approved design specification and a user-authorized
implementation plan. Design archival is not implementation
authorization.

## Testing Requirements

For P3 qualification and pilot work, run the isolated
`/usr/bin/python3` pytest recipe documented in the active plan.
Report the count the command printed. Do not treat a historical
P2 count as the P3 gate.

P2 historical reproduction, when requested, follows
`REPRODUCIBILITY.md`. This file does not introduce a new P2
pytest total or a new SSOT rebuild command.

## Production Authorization Boundary

Do not run `scripts/p3_v3/qualify_cxx_link.py`, a real compiler,
CMake, or Boost.Math in an ordinary pull request. Those paths
require a separate user authorization. Do not create
`/tmp/p3-cxx-link-qualification` to "try the CLI".

## Code Style

- Python follows the existing style: PEP 8 with 100-character
  lines.
- Commit messages use imperative mood ("add X", "fix Y").
- English for documents that ship as the public repository
  entry. Chinese is acceptable in `docs/theory/`.

## Issue And Pull Request Evidence

A P3 pull request must list:

- the authorization or plan node, if any
- files changed
- the exact pytest command and the printed result
- confirmation that production qualification was not run
```

Delete every sentence that says P3 belongs in a separate
repository. Delete the fixed `116 passed` requirement. Delete the
old "small P2 fixes only" welcome table.

- [ ] **Step 3: Scan the new documents**

```bash
python3 - <<'PY'
from pathlib import Path
files = [Path("README.md"), Path("CONTRIBUTING.md")]
needles = [
    "separate repository",
    "out-of-scope-for-P2",
    "116 passed",
]
required = [
    ("README.md", "P3 Semantic Mutation"),
    ("README.md", "read-only historical"),
    ("README.md", "attempt-2"),
    ("CONTRIBUTING.md", "P3 Semantic Mutation"),
    ("CONTRIBUTING.md", "read-only historical"),
    ("CONTRIBUTING.md", "separate user authorization"),
]
for path in files:
    text = path.read_text()
    for needle in needles:
        if needle in text:
            raise SystemExit(f"forbidden {needle} in {path}")
for path_name, needle in required:
    text = Path(path_name).read_text()
    if needle not in text:
        raise SystemExit(f"missing {needle} in {path_name}")
print("DOC_SCAN_OK")
PY
git diff --check -- README.md CONTRIBUTING.md
```

Expected: `DOC_SCAN_OK` and `git diff --check` exit 0.
No line in either file is longer than 100 characters.

- [ ] **Step 4: Commit only the two documents**

```bash
git add -- README.md CONTRIBUTING.md
git diff --cached --name-only
git commit -m "docs: reposition repository for P3"
```

Expected staged set is exactly those two paths.

---

### Task 6: Final Verification And Handoff

**Files:**
- Read only, except for verification commands.
- No extra commit. Tasks 2 through 5 are the only implementation
  commits.

**Interfaces:**
- Consumes: the four implementation commits.
- Produces: a clean branch ready for Sol code review.

- [ ] **Step 1: Run the qualification file**

```bash
export PYTHONDONTWRITEBYTECODE=1
export PYTHONNOUSERSITE=1
export PYTHONPATH=src:/tmp/p3-cxx-qualification-implementation-pip-target
TQ=tests/p3_v3/test_toolchain_qualification.py
/usr/bin/python3 -m pytest -q --tb=short \
  tests/p3_v3/test_toolchain_qualification.py
```

Expected: all collected tests pass.

- [ ] **Step 2: Run the three-file directed regression**

```bash
export PYTHONDONTWRITEBYTECODE=1
export PYTHONNOUSERSITE=1
export PYTHONPATH=src:/tmp/p3-cxx-qualification-implementation-pip-target
TQ=tests/p3_v3/test_toolchain_qualification.py
/usr/bin/python3 -m pytest -q --tb=short \
  tests/p3_v3/test_pilot.py \
  tests/p3_v3/test_pilot_build.py \
  tests/p3_v3/test_toolchain_qualification.py
```

Expected: all collected tests pass. Report the printed count. Do
not treat 168 as a ceiling after the new tests were added.

- [ ] **Step 3: Run ruff on the four implementation files**

```bash
export PYTHONDONTWRITEBYTECODE=1
export PYTHONNOUSERSITE=1
export PYTHONPATH=src:/tmp/p3-cxx-qualification-implementation-pip-target
TQ=tests/p3_v3/test_toolchain_qualification.py
/usr/bin/python3 -m ruff check \
  README.md \
  CONTRIBUTING.md \
  src/p3_v3/toolchain_qualification.py \
  tests/p3_v3/test_toolchain_qualification.py
```

If ruff refuses Markdown, run it on the two Python files only and
record that Markdown was checked by the width command below.
Expected: exit 0.

- [ ] **Step 4: Byte-compile without writing the repository**

```bash
PYTHONPYCACHEPREFIX=/tmp/p3-standards-remediation-pyc \
  /usr/bin/python3 -m py_compile \
  src/p3_v3/toolchain_qualification.py \
  tests/p3_v3/test_toolchain_qualification.py
test ! -e src/p3_v3/__pycache__
test ! -e tests/p3_v3/__pycache__
```

Expected: exit 0 and no new `__pycache__` under the repository.

- [ ] **Step 5: Check line width on the four implementation files**

```bash
python3 - <<'PY'
from pathlib import Path
files = [
    Path("README.md"),
    Path("CONTRIBUTING.md"),
    Path("src/p3_v3/toolchain_qualification.py"),
    Path("tests/p3_v3/test_toolchain_qualification.py"),
]
bad = []
for path in files:
    for index, line in enumerate(path.read_text().splitlines(), 1):
        if len(line) > 100:
            bad.append(f"{path}:{index}:{len(line)}")
print("OVER_100=" + str(len(bad)))
for item in bad:
    print(item)
if bad:
    raise SystemExit(1)
PY
```

Expected: `OVER_100=0`.

- [ ] **Step 6: Run git whitespace check against main**

```bash
git diff --check origin/main...HEAD
```

Expected: exit 0.

- [ ] **Step 7: Confirm the complete diff scope**

```bash
git diff --name-only origin/main...HEAD
```

Expected paths, and only these paths:

```text
README.md
CONTRIBUTING.md
docs/superpowers/specs/2026-08-18-p3-standards-remediation-design.md
docs/superpowers/plans/2026-08-19-p3-standards-remediation.md
src/p3_v3/toolchain_qualification.py
tests/p3_v3/test_toolchain_qualification.py
```

The spec and this plan are already archived. Implementation commits
may touch only the four approved files.

- [ ] **Step 8: Recheck frozen qualification hashes**

```bash
sha256sum \
  docs/superpowers/specs/2026-08-18-p3-cursor-vm-cxx-link-qualification-design.md \
  docs/superpowers/plans/2026-08-18-p3-cursor-vm-cxx-link-qualification.md \
  docs/superpowers/specs/2026-08-18-p3-standards-remediation-design.md
```

Expected:

```text
ff438a10da0e762667fe358fb32082e2338f39f28c16620d5a15d8890e8dd8d5
9661ecb73043bb58adc9b6bad025b9051548602e74677643cb7866f4204e2901
641e673a0c82c38f864d8602e06c0ce21f58f0fcb3b8dc4425d444db909c7d6e
```

- [ ] **Step 9: Confirm production root still absent**

```bash
test ! -e /tmp/p3-cxx-link-qualification && echo ROOT_ABSENT
```

Expected: `ROOT_ABSENT`.

- [ ] **Step 10: Confirm the failed venv mtime is unchanged**

```bash
stat -c '%y' /tmp/p3-cxx-qualification-implementation-venv
```

Expected: `2026-08-18 12:49:36.274466033 +0000`.

- [ ] **Step 11: Confirm the CLI file is unchanged**

```bash
git diff --name-only origin/main...HEAD \
  -- scripts/p3_v3/qualify_cxx_link.py
```

Expected: empty output.

- [ ] **Step 12: Confirm schema constants and spec bindings**

```bash
python3 - <<'PY'
from pathlib import Path
text = Path("src/p3_v3/toolchain_qualification.py").read_text()
required = [
    'INTENT_SCHEMA = "p3-cxx-link-qualification-intent-v1"',
    'PROCESS_SCHEMA = "p3-cxx-link-qualification-process-v1"',
    'RESULT_SCHEMA = "p3-cxx-link-qualification-result-v1"',
    'MANIFEST_SCHEMA = "p3-cxx-link-qualification-manifest-v1"',
    'HOST_SCHEMA = "p3-cxx-link-qualification-host-v1"',
    'ff438a10da0e762667fe358fb32082e2338f39f28c16620d5a15d8890e8dd8d5',
    "2026-08-18-p3-cursor-vm-cxx-link-qualification-design.md",
]
for item in required:
    if item not in text:
        raise SystemExit("missing " + item)
print("SCHEMA_BINDINGS_OK")
PY
```

Expected: `SCHEMA_BINDINGS_OK`.

- [ ] **Step 13: Confirm commit history, push, and draft PR**

Implementation history must be exactly these four commits after
the already-archived spec and plan commits, in order:

```text
refactor(p3-v3): name compiler identity
refactor(p3-v3): type qualification scenarios
refactor(p3-v3): unify process-group test helper
docs: reposition repository for P3
```

Do not add a fifth "fix everything" commit. If a check fails, repair
inside the Task that owns the file and amend only if that Task's
commit has not been pushed and the Task still owns the change.
After the four commits exist:

```bash
git status --porcelain
git rev-list --left-right --count \
  HEAD...origin/cursor/p3-standards-remediation-c46c
git push -u origin cursor/p3-standards-remediation-c46c
```

Keep pull request 16 OPEN and draft. Do not mark it ready. Do not
merge it. Do not write an implementation verdict. Do not run
`scripts/p3_v3/qualify_cxx_link.py`. Stop and wait for Sol code
review.

---

## Plan Self-Review

| Spec requirement | Task |
|---|---|
| P3 public identity and P2 read-only layer | Task 5 |
| Four-field `CompilerIdentity` and projection | Task 2 |
| Validator identity seam; delete four-parameter helpers | Task 2 |
| `QualificationScenario` closed field set | Task 3 |
| Unified `_patch_process_group`; no PID probe | Task 4 |
| RED to GREEN, directed regression, static checks | Tasks 1-6 |
| Real-execution exclusion zone | Global Constraints, Tasks 1 and 6 |
| Four-file writable set | Global Constraints, Task 6 Step 7 |

Incomplete-marker scan must find none of: incomplete-work tokens
or omitted field lists. Helper names stay
`CompilerIdentity`, `classification`, `QualificationScenario`,
`_run_synthetic_qualification`, and `_patch_process_group` in every
Task. No Task says to copy another Task. No Task adds a fifth
implementation file. No Task runs a real compiler or
`qualify_cxx_link.py`.
