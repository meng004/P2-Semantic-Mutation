# Supplemental R2 Path-Scan CI Repair Implementation Plan

> **For agentic workers:** After a later node grants implementation,
> use superpowers:executing-plans task-by-task. This archival node
> forbids starting any Task. Do not edit production or test code here.

**Goal:** Stop the supplemental R2 forbidden-path gate from failing a
legal synthetic fixture because unrelated repository paths contain
readiness, freeze, annotation, prediction, or detection tokens.

**Architecture:** Design choice A. Delete the repo-wide
`git ls-files -co --exclude-standard` consumption from the three
existing `_forbidden_path_scan` functions. Keep the admission-root
and sibling-boundary `rglob`, `_classify_forbidden_rel`, the frozen
name regular expression, the historical unchanged-baseline exemption
for paths already in those scoped walks, and the separate transport
byte freeze. Do not add a shared helper file.

**Tech Stack:** Python 3.12 invoked as `/usr/bin/python3`, pytest,
existing `scripts/external_slice` checkers and miner.

## Global Constraints

- Implement against
  `docs/superpowers/specs/2026-08-19-supplemental-r2-path-scan-ci-repair-design.md`
  with SHA-256
  `76c46bb0d0cb51dd6380cebed9f02764a8a2acfb773a6937dd9312625ca8be22`.
- Design choice is A. Choice B (shared helper / new production file)
  is refused unless a later file-authorization node opens it.
- A later implementation node may edit only:
  - `scripts/external_slice/check_supplemental_r2_admission.py`
  - `scripts/external_slice/check_supplemental_r2_handoff_hashes.py`
  - `scripts/external_slice/mine_supplemental_r2.py`
  - `tests/external_slice/test_check_supplemental_r2_admission.py`
- Do not modify `.github/workflows`, PR 16, supplemental R2 data,
  handoff bytes, or `TRANSPORT_BASELINE_COMMIT`
  `020b60fb83f7eb1d34f143458fca62beab5aa398`.
- Do not relax `FORBIDDEN_PATH_NAME_RE`. Do not delete sentinel
  checks. Do not ignore the path scan. Do not xfail, skip, or delete
  `test_positive_admission_check`.
- Fail-closed remains required for: admission-root sentinels;
  sibling-boundary sentinels; `COMMAND_LOG.json` or
  `VERIFICATION_LOG.json` readiness or canonical-freeze records;
  transport byte drift; A2 other than `PENDING`; nonempty
  `analysis_id`; prohibited vocabulary; handoff/hash/binding
  mismatch.
- Use `/usr/bin/python3` only. Do not use `rtk`.
- Do not run `scripts/build_paper_numbers.py` in any form.
- Do not run real retrieval, GitHub mining, readiness, or canonical
  freeze. Do not run a real compiler, CMake, or Boost.Math.
- Keep this repair pull request draft. Do not merge. Do not copy
  commits from `cursor/p3-standards-remediation-c46c`.
- Claims stay blocked. Formal denominator membership stays false.
- `IMPLEMENTATION_AUTHORIZED=false` at archival. A later user node
  must grant implementation after Sol Spec + Standards review.
- `MERGE_AUTHORIZED=false`.

---

## File Structure

- Modify: `scripts/external_slice/check_supplemental_r2_admission.py`
  function `_forbidden_path_scan` (near line 1306). Delete only the
  repo-wide `git ls-files` consumption block.
- Modify: `scripts/external_slice/check_supplemental_r2_handoff_hashes.py`
  function `_forbidden_path_scan` (near line 343). Same deletion.
- Modify: `scripts/external_slice/mine_supplemental_r2.py`
  function `_forbidden_path_scan` (near line 2005). Same deletion.
- Modify: `tests/external_slice/test_check_supplemental_r2_admission.py`
  add focused RED tests before any production edit.
- Do not create a shared helper module.

Keep these unchanged:

```text
_classify_forbidden_rel(rel) -> tuple[bool, bool, bool]
_forbidden_path_scan(root, *, repo_root=None) -> tuple[bool, bool, bool]
# (forbidden_path_hit, readiness_file_hit, freeze_file_hit)
FORBIDDEN_PATH_NAME_RE
_transport_freeze_matches_baseline
rglob of root and root.parent
historical unchanged-baseline exemption inside _consume
```

## Frozen CI Evidence

| Item | Value |
|---|---|
| Workflow | `sanity-check` |
| Check | `Run pytest (Path-A cache replay smoke)` |
| Command | `pytest -q --maxfail=1` with `PYTHONPATH=src` |
| Test | `test_positive_admission_check` line 600 |
| Error | `assert 1 == 0` / forbidden-path present |
| main run | `32146789008` at `4444061d` |
| PR 16 run | `32213892143` job `95951674266` at `081bb617` |

This is a preexisting `origin/main` failure. It is not a PR 16
regression.

## Why The Positive Fixture Fails

`verify_admission(root)` calls `_compute_confirmations`, which calls
`_forbidden_path_scan(root, repo_root=repo_root)` with default
`repo_root = Path(__file__).resolve().parents[2]` (the real
workspace). The scan lists every tracked and untracked path under
that workspace, then classifies names with `FORBIDDEN_PATH_NAME_RE`.
Legitimate later files such as

```text
docs/review_20260812/phase0_protocol_freeze_task_report.md
docs/superpowers/plans/2026-08-12-p3-phase0-protocol-freeze.md
```

match the `freeze` token and are newer than transport baseline
`020b60fb`, so `forbidden_data_absent` becomes false.

The admission-root and sibling `rglob` walks are not the defect.
They must stay.

---

### Task 1: Confirm Repair Entry And Withheld Authorization

**Files:**
- Read only: this plan, the design spec, `origin/main`

**Interfaces:**
- Consumes: spec SHA-256
  `76c46bb0d0cb51dd6380cebed9f02764a8a2acfb773a6937dd9312625ca8be22`
- Produces: a written entry record. No code edits.

- [ ] **Step 1: Refuse to start without a later grant**

Stop if the current user node has not granted implementation after
Sol Spec + Standards review. Archival of this plan is not a grant.
`IMPLEMENTATION_AUTHORIZED=false` until that later node.

- [ ] **Step 2: Confirm the independent repair branch**

```bash
git fetch origin
git rev-parse --abbrev-ref HEAD
git rev-parse origin/main
git merge-base HEAD origin/main
git status --porcelain
```

Expected:

```text
cursor/supplemental-r2-path-scan-ci-repair-c46c
4444061dde0159a5edd62753fe3cef2d881a308c
4444061dde0159a5edd62753fe3cef2d881a308c
```

Working tree clean except the four allowed files after later edits.
Do not start from PR 16. Do not cherry-pick PR 16 commits.

- [ ] **Step 3: Confirm the design digest**

```bash
/usr/bin/python3 - <<'PY'
from hashlib import sha256
from pathlib import Path
p = Path(
    "docs/superpowers/specs/"
    "2026-08-19-supplemental-r2-path-scan-ci-repair-design.md"
)
digest = sha256(p.read_bytes()).hexdigest()
print(digest)
assert digest == (
    "76c46bb0d0cb51dd6380cebed9f02764a8a2acfb773a6937dd9312625ca8be22"
)
PY
```

Expected: the printed digest matches the assertion.

---

### Task 2: Write Focused RED Tests First

**Files:**
- Modify:
  `tests/external_slice/test_check_supplemental_r2_admission.py`
- Do not modify the three scripts in this task.

**Interfaces:**
- Consumes: `seed_root`, `build_valid_payload`, `both_checkers_fail`,
  `checker`, `handoff_mod`, `miner`, `ROOT`
- Produces: four new tests named below

- [ ] **Step 1: Add the isolation helper and tests**

Insert after `test_positive_admission_check`. Do not write freeze
files into the real workspace. Use `tmp_path` only.

```python
def _init_decoy_git(repo: Path) -> None:
    subprocess.run(
        ["git", "init"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )


def test_real_repo_docs_protocol_freeze_does_not_hit_seeded_root(
    tmp_path: Path,
) -> None:
    """Workspace docs with freeze tokens must not classify a fixture."""
    root = seed_root(tmp_path)
    hit, readiness, freeze = checker._forbidden_path_scan(
        root, repo_root=ROOT
    )
    assert (hit, readiness, freeze) == (False, False, False)
    hit_h, readiness_h, freeze_h = (
        handoff_mod._forbidden_path_scan(root, repo_root=ROOT)
    )
    hit_m, readiness_m, freeze_m = miner._forbidden_path_scan(
        root, repo_root=ROOT
    )
    assert (hit_h, readiness_h, freeze_h) == (False, False, False)
    assert (hit_m, readiness_m, freeze_m) == (False, False, False)


def test_unrelated_docs_protocol_freeze_outside_sibling_is_ignored(
    tmp_path: Path,
) -> None:
    """A new decoy freeze path outside sibling must not be a hit."""
    decoy_repo = tmp_path
    admission_home = decoy_repo / "admission_home"
    root = seed_root(admission_home)
    unrelated = (
        decoy_repo
        / "docs"
        / "review_20260812"
        / "phase0_protocol_freeze_task_report.md"
    )
    unrelated.parent.mkdir(parents=True, exist_ok=True)
    unrelated.write_text(
        "unrelated protocol freeze note\n",
        encoding="utf-8",
    )
    _init_decoy_git(decoy_repo)
    hit, readiness, freeze = checker._forbidden_path_scan(
        root, repo_root=decoy_repo
    )
    assert (hit, readiness, freeze) == (False, False, False)


def test_admission_root_protocol_freeze_file_still_rejected(
    tmp_path: Path,
) -> None:
    root = seed_root(tmp_path)
    build_valid_payload(root, admits_per_quota_repo=3)
    (root / "protocol_freeze.md").write_text("x\n", encoding="utf-8")
    seal_handoff_bundle(root)
    both_checkers_fail(root)
    hit, readiness, freeze = checker._forbidden_path_scan(
        root, repo_root=tmp_path
    )
    assert hit is True
    assert freeze is True
    assert readiness is False


def test_three_forbidden_path_scan_classifications_match(
    tmp_path: Path,
) -> None:
    admission_home = tmp_path / "admission_home"
    root = seed_root(admission_home)
    unrelated = (
        tmp_path
        / "docs"
        / "superpowers"
        / "plans"
        / "2026-08-12-p3-phase0-protocol-freeze.md"
    )
    unrelated.parent.mkdir(parents=True, exist_ok=True)
    unrelated.write_text("unrelated\n", encoding="utf-8")
    (root / "readiness_note.md").write_text("x\n", encoding="utf-8")
    (admission_home / "freeze.json").write_text("{}\n", encoding="utf-8")
    _init_decoy_git(tmp_path)
    scanned = [
        mod._forbidden_path_scan(root, repo_root=tmp_path)
        for mod in (checker, handoff_mod, miner)
    ]
    assert scanned[0] == scanned[1] == scanned[2]
    hit, readiness, freeze = scanned[0]
    assert hit is True
    assert readiness is True
    assert freeze is True
```

Keep
`test_full_chain_downstream_token_filename_positions_rejected`
as the sibling-boundary contract. Do not rewrite it.

- [ ] **Step 2: Record focused RED**

```bash
PYTHONPATH=src /usr/bin/python3 -m pytest -q --maxfail=1 \
  tests/external_slice/test_check_supplemental_r2_admission.py::\
test_real_repo_docs_protocol_freeze_does_not_hit_seeded_root
```

Expected before the production edit: FAIL. The real workspace
`git ls-files` still feeds `_consume` with
`docs/review_20260812/phase0_protocol_freeze_task_report.md` or
`docs/superpowers/plans/2026-08-12-p3-phase0-protocol-freeze.md`,
so the assertion `(False, False, False)` fails.

Also record the existing CI gate, still without production edits:

```bash
PYTHONPATH=src /usr/bin/python3 -m pytest -q --maxfail=1 \
  tests/external_slice/test_check_supplemental_r2_admission.py::\
test_positive_admission_check
```

Expected before the production edit:

```text
AssertionError: assert 1 == 0
ERROR: forbidden data or downstream path present
```

Do not xfail, skip, or delete either test.

Do not commit in this task if the later node prefers one
implementation commit after GREEN. If the later node splits
commits, the RED-only commit may land first on this same branch.

---

### Task 3: Minimal Parallel Repair In Three Functions

**Files:**
- Modify: `scripts/external_slice/check_supplemental_r2_admission.py`
  around the block beginning
  `# Repo-wide tracked + untracked paths.`
- Modify: `scripts/external_slice/check_supplemental_r2_handoff_hashes.py`
  same block
- Modify: `scripts/external_slice/mine_supplemental_r2.py`
  same block

**Interfaces:**
- Consumes: existing `_consume`, `scan_roots`, `_classify_forbidden_rel`
- Produces: the same return triple, now sourced only from scoped walks

- [ ] **Step 1: Delete the ls-files consumption in all three files**

Remove this exact block from each `_forbidden_path_scan`. Leave the
`rglob` walk that follows it.

```python
    # Repo-wide tracked + untracked paths.
    proc = subprocess.run(
        ["git", "ls-files", "-co", "--exclude-standard"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode == 0:
        for rel in proc.stdout.splitlines():
            _consume(rel)
```

Do not change `_classify_forbidden_rel`. Do not change
`FORBIDDEN_PATH_NAME_RE`. Do not remove the `ls-tree` baseline index
used by `_consume`. Do not remove the `root` / `root.parent` walk.
Do not add a helper module.

After the deletion, `_forbidden_path_scan` classifies a path only
when the `rglob` walk finds it under `root` or `root.parent`, or
when that walk encounters a frozen transport path that already
participates in `_transport_freeze_matches_baseline`. Unrelated
`docs/...protocol_freeze...` paths are outside those roots.

- [ ] **Step 2: Confirm the three deletions are identical in spirit**

```bash
/usr/bin/python3 - <<'PY'
from pathlib import Path
needles = [
    '["git", "ls-files", "-co", "--exclude-standard"]',
    "git ls-files -co --exclude-standard",
]
files = [
    Path("scripts/external_slice/check_supplemental_r2_admission.py"),
    Path("scripts/external_slice/check_supplemental_r2_handoff_hashes.py"),
    Path("scripts/external_slice/mine_supplemental_r2.py"),
]
for path in files:
    text = path.read_text(encoding="utf-8")
    for needle in needles:
        assert needle not in text, (path, needle)
    assert "def _forbidden_path_scan(" in text
    assert "scan_roots" in text
    assert "FORBIDDEN_PATH_NAME_RE" in text
print("scoped path-scan deletions confirmed")
PY
```

Expected: `scoped path-scan deletions confirmed`

---

### Task 4: Record Focused GREEN

**Files:**
- Test only. No further production edits unless a RED still fails
  for a scoped-boundary reason.

- [ ] **Step 1: Re-run the new isolation tests**

```bash
PYTHONPATH=src /usr/bin/python3 -m pytest -q --maxfail=1 \
  tests/external_slice/test_check_supplemental_r2_admission.py::\
test_real_repo_docs_protocol_freeze_does_not_hit_seeded_root \
  tests/external_slice/test_check_supplemental_r2_admission.py::\
test_unrelated_docs_protocol_freeze_outside_sibling_is_ignored \
  tests/external_slice/test_check_supplemental_r2_admission.py::\
test_admission_root_protocol_freeze_file_still_rejected \
  tests/external_slice/test_check_supplemental_r2_admission.py::\
test_three_forbidden_path_scan_classifications_match
```

Expected: all four PASS.

- [ ] **Step 2: Restore the CI-positive gate**

```bash
PYTHONPATH=src /usr/bin/python3 -m pytest -q --maxfail=1 \
  tests/external_slice/test_check_supplemental_r2_admission.py::\
test_positive_admission_check
```

Expected: PASS (`exit 0`).

- [ ] **Step 3: Keep the sibling fail-closed contract**

```bash
PYTHONPATH=src /usr/bin/python3 -m pytest -q --maxfail=1 \
  tests/external_slice/test_check_supplemental_r2_admission.py::\
test_full_chain_downstream_token_filename_positions_rejected
```

Expected: PASS for every filename parameter.

---

### Task 5: Full external_slice And Actions Pytest Gate

**Files:** none beyond the four allowed paths already edited

- [ ] **Step 1: Run the complete external_slice targeted suite**

```bash
PYTHONPATH=src /usr/bin/python3 -m pytest -q --maxfail=1 \
  tests/external_slice
```

Expected: all tests PASS. Record the `N passed` count. Existing
tamper, binding, transport-freeze, A2, vocabulary, and handoff
tests must remain in that run.

- [ ] **Step 2: Reproduce the GitHub Actions pytest gate**

```bash
PYTHONPATH=src /usr/bin/python3 -m pytest -q --maxfail=1
```

Expected: the same command used by `.github/workflows/sanity.yml`
exits 0. Do not edit the workflow to skip `external_slice`. Do not
shrink the root suite to P3.

If this command fails on an unrelated test, stop and report. Do not
xfail. Do not delete tests. Do not treat an unrelated failure as
authorization to widen scope.

- [ ] **Step 3: Do not run SSOT or live mining**

Do not run `scripts/build_paper_numbers.py`.
Do not run `mine_supplemental_r2.py` retrieve against GitHub.
Do not run readiness or canonical freeze.

---

### Task 6: Scope Check, Independent Commit, Draft Stop

**Files:** only the four allowed implementation files

- [ ] **Step 1: Whitespace and scope**

```bash
git diff --check origin/main...HEAD
git diff --name-only origin/main...HEAD
```

Allowed names after this later implementation:

```text
docs/superpowers/specs/2026-08-19-supplemental-r2-path-scan-ci-repair-design.md
docs/superpowers/plans/2026-08-19-supplemental-r2-path-scan-ci-repair.md
scripts/external_slice/check_supplemental_r2_admission.py
scripts/external_slice/check_supplemental_r2_handoff_hashes.py
scripts/external_slice/mine_supplemental_r2.py
tests/external_slice/test_check_supplemental_r2_admission.py
```

Any other path is a stop.

- [ ] **Step 2: Independent commit on the repair branch**

```bash
git add \
  scripts/external_slice/check_supplemental_r2_admission.py \
  scripts/external_slice/check_supplemental_r2_handoff_hashes.py \
  scripts/external_slice/mine_supplemental_r2.py \
  tests/external_slice/test_check_supplemental_r2_admission.py
git commit -m "fix(external-slice): scope supplemental R2 path scan"
```

Do not amend, squash, or rebase already-pushed commits.
Do not commit PR 16 files.

- [ ] **Step 3: Push and keep the repair pull request draft**

```bash
git push -u origin cursor/supplemental-r2-path-scan-ci-repair-c46c
```

Leave the repair pull request OPEN and draft for Sol review.
Do not mark it ready. Do not merge. Do not edit PR 16.

- [ ] **Step 4: Confirm PR 16 is untouched**

```bash
gh pr view 16 \
  --repo meng004/P3-Semantic-Mutation \
  --json state,isDraft,headRefOid
```

Expected:

```text
state=OPEN
isDraft=false
headRefOid=081bb6176d25d47f9bd58ee688c12dadae06fa68
```

---

## Non-Goals

This plan does not:

- change `.github/workflows` or skip `external_slice` tests
- xfail, skip, or delete the failing test
- shrink the root suite to P3 only
- change `TRANSPORT_BASELINE_COMMIT`
- rewrite supplemental R2 data, handoff, or freeze results
- run readiness, canonical freeze, retrieval, or GitHub mining
- attribute the failure to pull request 16
- grant implementation, merge, attempt-2, or claim upgrades
- adopt choice B or add a production helper file

## Governance Stop

This file is a future-work archive. Writing it does not authorize
implementation. After Sol Spec + Standards review, a later user
node must still grant implementation before any Task starts.

The repair pull request stays draft. Pull request 16 stays OPEN and
ready. Merge stays unauthorized.

## Self-Review Record

- Spec coverage: coupling removal, fail-closed list, choice A,
  four-file write set, RED-before-GREEN, Actions pytest gate,
  no SSOT / mining / freeze, PR 16 isolation.
- Incomplete-marker scan: clean.
- Authorization strings remain false at archival.
- Execution is not offered from this archival node.
