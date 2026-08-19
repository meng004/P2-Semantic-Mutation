# P3 Compiler-Alias CI Repair Implementation Plan

> **For agentic workers:** Use executing-plans only after Sol sets
> IMPLEMENTATION_EXECUTABLE to true on this plan and writes a 40-character
> IMPLEMENTATION_ENTRY. This archival node forbids starting any Task.
> Do not edit production or test code here.

**Goal:** Make P3 pilot-build compiler-mismatch tests host-independent
so a legal `c++` / `g++` alias on GitHub Actions no longer skips the
`EvidenceError` that the tests expect.

**Architecture:** Design choice A. Keep `os.path.realpath` in
`collect_baseline_build_evidence`. Replace `/usr/bin/g++` mismatch
oracles with `tmp_path` identities. Add one host-independent alias
acceptance test. Do not add a helper module.

**Tech Stack:** Python 3.12 invoked as `/usr/bin/python3`, pytest,
existing `p3_v3.pilot_build`.

## Global Constraints

- Implement against
  `docs/superpowers/specs/2026-08-19-p3-compiler-alias-ci-repair-design.md`
  with SHA-256
  `a12dd1c0687b93a0866956744b95e8fdddb70ce25177181a1e246514da00bbd2`.
- Design choice is A. Choice B (lexical production compare) and
  choice C (new helper file) are refused.
- A later implementation node may edit only
  `tests/p3_v3/test_pilot_build.py`.
- Do not modify `src/p3_v3/pilot_build.py`, qualification modules,
  `.github/workflows`, supplemental R2 scanners, PR 16, or PR 17.
- Keep production realpath compare at
  `collect_baseline_build_evidence` cache and compile_commands
  checks.
- Use `/usr/bin/python3` only. Do not use `rtk`.
- Do not run CMake, a real compiler, ninja, make, or Boost.Math.
- Do not run `scripts/build_paper_numbers.py` in any form.
- Do not run real retrieval, GitHub mining, readiness, or freeze.
- Keep this repair pull request draft. Do not merge.
- Claims stay blocked. Formal denominator membership stays false.
- Archiving this plan does not authorize implementation.
- `IMPLEMENTATION_AUTHORIZED=false` at archival.
- `IMPLEMENTATION_ENTRY` must be the full 40-character commit SHA
  that Sol writes in the implementation instruction after PASS.
  If that instruction omits `IMPLEMENTATION_ENTRY`, stop. Do not
  derive it from the origin tip, branch name, merge-base, PR head,
  or clock time. Local HEAD and the origin repair tip must both
  equal that SHA. An unknown later commit is a stop.
- `MERGE_AUTHORIZED=false`.

---

## File Structure

- Modify: `tests/p3_v3/test_pilot_build.py`
  - `test_compile_commands_compiler_mismatch`
  - `test_cmakecache_compiler_generator_root_drift`
  - add `test_compile_commands_compiler_alias_is_same_compiler`
- Do not modify `src/p3_v3/pilot_build.py`.

## Frozen CI Evidence

| Item | Value |
|---|---|
| Workflow | `sanity-check` |
| Command | `pytest -q --maxfail=1` with `PYTHONPATH=src` |
| Test | `test_compile_commands_compiler_mismatch` |
| Error | `DID NOT RAISE EvidenceError` |
| PR 17 run | `32225095224` at `fb20947a` |
| main run | `32146789008` at `4444061d` (shadowed) |

---

### Task 1: Confirm Repair Entry And Withheld Authorization

**Files:**
- Read only: this plan, the design spec, `origin/main`

**Interfaces:**
- Consumes: spec SHA-256
  `a12dd1c0687b93a0866956744b95e8fdddb70ce25177181a1e246514da00bbd2`
- Produces: a written entry record. No code edits.

Frozen invariant values:

```text
branch: cursor/p3-compiler-alias-ci-repair-c46c
origin/main: 4444061dde0159a5edd62753fe3cef2d881a308c
merge-base: 4444061dde0159a5edd62753fe3cef2d881a308c
```

- [ ] **Step 1: Refuse unless implementation is executable**

Archiving this plan is not a grant. Stop unless Sol has set
`IMPLEMENTATION_EXECUTABLE` to true and written
`IMPLEMENTATION_ENTRY` as a full 40-character SHA.

- [ ] **Step 2: Freeze and verify the exact implementation entry**

Do not start from PR 16 or PR 17. Do not cherry-pick those
commits. Do not reset, rebase, amend, or force-push to hide a
mismatch. If any value differs, stop.

```bash
git fetch origin
git rev-parse --abbrev-ref HEAD
git rev-parse HEAD
git rev-parse origin/cursor/p3-compiler-alias-ci-repair-c46c
git rev-parse origin/main
git merge-base HEAD origin/main
git rev-list --left-right --count \
  HEAD...origin/cursor/p3-compiler-alias-ci-repair-c46c
git status --porcelain
```

Required results:

```text
branch = cursor/p3-compiler-alias-ci-repair-c46c
HEAD = IMPLEMENTATION_ENTRY
origin repair tip = IMPLEMENTATION_ENTRY
origin/main = 4444061dde0159a5edd62753fe3cef2d881a308c
merge-base = 4444061dde0159a5edd62753fe3cef2d881a308c
ahead/behind = 0	0
porcelain = empty
```

- [ ] **Step 3: Confirm the design digest**

```bash
/usr/bin/python3 - <<'PY'
from hashlib import sha256
from pathlib import Path
p = Path(
    "docs/superpowers/specs/"
    "2026-08-19-p3-compiler-alias-ci-repair-design.md"
)
digest = sha256(p.read_bytes()).hexdigest()
print(digest)
assert digest == (
    "a12dd1c0687b93a0866956744b95e8fdddb70ce25177181a1e246514da00bbd2"
)
PY
```

---

### Task 2: Record The Host-Coupled RED Signature

**Files:** none. Read-only pytest only.

- [ ] **Step 1: Record the local host realpaths**

```bash
/usr/bin/python3 - <<'PY'
import os
print(os.path.realpath("/usr/bin/c++"))
print(os.path.realpath("/usr/bin/g++"))
print(os.path.realpath("/usr/bin/c++") == os.path.realpath("/usr/bin/g++"))
PY
```

On this Cursor VM the equality is false. On GitHub Actions it is
true. Do not treat a local PASS as a closed defect.

- [ ] **Step 2: Run the current mismatch test**

```bash
PYTHONPATH=src /usr/bin/python3 -m pytest -q --maxfail=1 \
  tests/p3_v3/test_pilot_build.py::test_compile_commands_compiler_mismatch
```

If this VM still reports PASS, record that fact and keep the
frozen GitHub signature as the RED:

```text
Failed: DID NOT RAISE <class 'p3_v3.artifacts.EvidenceError'>
tests/p3_v3/test_pilot_build.py:1306
```

Do not xfail, skip, or delete the test.

---

### Task 3: Replace Host-Coupled Oracles

**Files:**
- Modify: `tests/p3_v3/test_pilot_build.py`

**Interfaces:**
- Consumes: `_synthetic_build_evidence_tree`,
  `validate_environment_snapshot`, `_self_hash`,
  `collect_baseline_build_evidence`
- Produces: host-independent mismatch and alias tests

- [ ] **Step 1: Change the compile_commands mismatch oracle**

Replace the `/usr/bin/g++` assignment with a `tmp_path` identity
that cannot share a realpath with `/usr/bin/c++`.

```python
def test_compile_commands_compiler_mismatch(tmp_path, monkeypatch):
    import p3_v3.pilot_build as pilot_build

    build, env = _synthetic_build_evidence_tree(tmp_path, pilot_build, monkeypatch)
    env = dict(env)
    env["cxx_compiler_path"] = str(tmp_path / "other-cxx")
    env.pop("artifact_sha256", None)
    env = pilot_build.validate_environment_snapshot(pilot_build._self_hash(env))
    with pytest.raises(EvidenceError, match="compiler differs"):
        pilot_build.collect_baseline_build_evidence(build, env)
```

- [ ] **Step 2: Change the CMakeCache mismatch oracle**

In `test_cmakecache_compiler_generator_root_drift`, replace
`cache_compiler="/usr/bin/g++"` with a `tmp_path` identity:

```python
    other = tmp_path / "cache-other-cxx"
    build, env = _synthetic_build_evidence_tree(
        tmp_path / "compiler",
        pilot_build,
        monkeypatch,
        cache_compiler=str(other),
    )
    with pytest.raises(EvidenceError, match="CMakeCache compiler differs"):
        pilot_build.collect_baseline_build_evidence(build, env)
```

Do not change the generator-drift or source-root-drift cases.

- [ ] **Step 3: Add a host-independent alias acceptance test**

Insert after `test_compile_commands_compiler_mismatch`:

```python
def test_compile_commands_compiler_alias_is_same_compiler(
    tmp_path, monkeypatch
):
    import p3_v3.pilot_build as pilot_build

    real = tmp_path / "real-cxx"
    real.write_bytes(b"compiler\n")
    alias = tmp_path / "alias-cxx"
    alias.symlink_to(real)
    build, env = _synthetic_build_evidence_tree(
        tmp_path,
        pilot_build,
        monkeypatch,
        compiler=str(alias),
    )
    env = dict(env)
    env["cxx_compiler_path"] = str(real)
    env.pop("artifact_sha256", None)
    env = pilot_build.validate_environment_snapshot(
        pilot_build._self_hash(env)
    )
    evidence = pilot_build.collect_baseline_build_evidence(build, env)
    assert len(evidence["compiler_depfile_sha256"]) == 64
```

This locks the frozen realpath contract: symlink alias is the
same compiler. It must not use `/usr/bin/c++` or `/usr/bin/g++`.

---

### Task 4: Focused GREEN

- [ ] **Step 1: Run the repaired and new tests**

```bash
PYTHONPATH=src /usr/bin/python3 -m pytest -q --maxfail=1 \
  tests/p3_v3/test_pilot_build.py::test_compile_commands_compiler_mismatch \
  tests/p3_v3/test_pilot_build.py::test_compile_commands_compiler_alias_is_same_compiler \
  tests/p3_v3/test_pilot_build.py::test_cmakecache_compiler_generator_root_drift
```

Expected: all collected tests PASS.

- [ ] **Step 2: Run the pilot_build file**

```bash
PYTHONPATH=src /usr/bin/python3 -m pytest -q --maxfail=1 \
  tests/p3_v3/test_pilot_build.py
```

Expected: the file PASS count is recorded. Existing fail-closed
cases remain in that run.

---

### Task 5: Root Pytest Gate

- [ ] **Step 1: Reproduce the Actions pytest command**

```bash
PYTHONPATH=src /usr/bin/python3 -m pytest -q --maxfail=1
```

Expected on this repair branch from `origin/main`: the first
failure may still be supplemental R2 path-scan. That is a
separate repair. This node is done only when the compiler-alias
test is no longer a failure mode.

If the first failure is still
`test_compile_commands_compiler_mismatch`, stop and report.

Do not edit the workflow. Do not xfail path-scan. Do not treat
path-scan as authorization to widen scope.

- [ ] **Step 2: Do not run SSOT or live builds**

Do not run `scripts/build_paper_numbers.py`.
Do not run CMake, ninja, make, a real compiler, or Boost.Math.

---

### Task 6: Scope Check, Independent Commit, Draft Stop

**Files:** only `tests/p3_v3/test_pilot_build.py`

Working-tree checks see uncommitted, staged, and untracked paths.
`origin/main...HEAD` sees only already-committed history.

- [ ] **Step 1: Working-tree scope before commit**

```bash
git status --porcelain
git diff --check
git diff --name-only
git diff --cached --name-only
git ls-files --others --exclude-standard
```

The only path that may appear is:

```text
tests/p3_v3/test_pilot_build.py
```

Any other modified, staged, or untracked path is a stop.

- [ ] **Step 2: Independent commit**

```bash
git add tests/p3_v3/test_pilot_build.py
git commit -m "test(p3-v3): decouple compiler mismatch from host aliases"
```

Do not amend, squash, or rebase already-pushed commits.

- [ ] **Step 3: Committed-history scope after commit, before push**

```bash
git diff --check origin/main...HEAD
git diff --name-only origin/main...HEAD
git show --name-only --format= HEAD
git rev-list --left-right --count \
  HEAD...origin/cursor/p3-compiler-alias-ci-repair-c46c
```

`origin/main...HEAD` may contain only:

```text
docs/superpowers/specs/2026-08-19-p3-compiler-alias-ci-repair-design.md
docs/superpowers/plans/2026-08-19-p3-compiler-alias-ci-repair.md
tests/p3_v3/test_pilot_build.py
```

The newest implementation commit may contain only the test file.
Push-time ahead/behind must be `1	0`.

- [ ] **Step 4: Push and keep the repair pull request draft**

```bash
git push -u origin cursor/p3-compiler-alias-ci-repair-c46c
```

Do not mark the repair PR ready. Do not merge. Do not edit PR 16
or PR 17.

- [ ] **Step 5: Confirm remote sync and the other pull requests**

```bash
git rev-parse HEAD
git rev-parse origin/cursor/p3-compiler-alias-ci-repair-c46c
git rev-list --left-right --count \
  HEAD...origin/cursor/p3-compiler-alias-ci-repair-c46c
gh pr view 16 \
  --repo meng004/P3-Semantic-Mutation \
  --json state,isDraft,headRefOid
gh pr view 17 \
  --repo meng004/P3-Semantic-Mutation \
  --json state,isDraft,headRefOid
```

Required:

```text
HEAD = origin repair tip
ahead/behind = 0	0
PR 16 state=OPEN isDraft=false
PR 16 headRefOid=081bb6176d25d47f9bd58ee688c12dadae06fa68
PR 17 state=OPEN isDraft=true
PR 17 headRefOid=fb20947a102934415dd201665971a711ccc4e0d5
```

The new repair PR must stay OPEN and draft.

---

## Non-Goals

This plan does not:

- change `.github/workflows` or skip `tests/p3_v3`
- xfail, skip, or delete the failing test
- change production `os.path.realpath` compares
- change qualification, supplemental R2, PR 16, or PR 17
- run CMake, a real compiler, or Boost.Math
- treat plan archival as an executable implementation grant

## Governance Stop

Archiving this plan does not authorize implementation. A later
user node must still grant implementation and write
`IMPLEMENTATION_ENTRY` after Sol Spec + Standards PASS.

The repair pull request stays draft. Pull requests 16 and 17 stay
untouched. Merge stays unauthorized.

## Self-Review Record

- Spec coverage: realpath contract kept, host oracles removed,
  alias acceptance test, one-file write set, PR isolation.
- Entry is fail-closed on an explicit Sol SHA.
- Incomplete-marker scan: clean.
- Execution is not offered from this archival node.
