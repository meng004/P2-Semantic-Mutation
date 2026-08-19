# P3 Compiler-Alias CI Repair Design

**Status:** Design archived; implementation is not authorized
**Node:** `P1BP1I2Q9_CURSOR_VM_P3_COMPILER_ALIAS_CI_REPAIR_SPEC_PLAN`
**Type:** `GOVERNANCE_ONLY`
**Baseline:** `origin/main` `4444061dde0159a5edd62753fe3cef2d881a308c`
**Claims:** blocked
**Formal denominator membership:** false
**Attempt-2 authorized:** false
**Real qualification authorized:** false
**Merge authorized:** false
**Design choice:** A (test-only; keep production realpath identity)

This document archives the approved semantics for removing host coupling
from P3 pilot-build compiler-mismatch tests. It is not an implementation
plan or implementation verdict. Writing or merging this file does not
authorize code edits, workflow edits, CI repair, or claim upgrades.

This repair is independent of pull requests 16 and 17. It must not copy
commits from `cursor/p3-standards-remediation-c46c` or
`cursor/supplemental-r2-path-scan-ci-repair-c46c`.

## Purpose

The GitHub Actions `sanity-check` job `Run pytest (Path-A cache replay
smoke)` now reaches `tests/p3_v3/test_pilot_build.py` after the
supplemental R2 path-scan gate is no longer the first `--maxfail=1`
failure on pull request 17. The next failure is host-dependent.

`test_compile_commands_compiler_mismatch` sets the environment snapshot
`cxx_compiler_path` to `/usr/bin/g++` while the synthetic
`compile_commands.json` and `CMakeCache.txt` still record `/usr/bin/c++`.
It expects `collect_baseline_build_evidence` to raise `EvidenceError`
matching `compiler differs`.

Production compares those paths with `os.path.realpath`. On GitHub
Actions `ubuntu-latest`, `/usr/bin/c++` and `/usr/bin/g++` commonly
resolve to the same binary, so the test does not raise. On this Cursor
VM, `/usr/bin/c++` resolves to LLVM clang and `/usr/bin/g++` resolves to
`g++-13`, so the same test passes. That is host coupling, not a pull
request 16 or 17 regression.

The frozen pilot-build contract already requires realpath equality. The
repair must keep that production contract and make the mismatch oracles
host-independent.

## Frozen CI Evidence

| Item | Value |
|---|---|
| Workflow | `sanity-check` |
| Check | `Run pytest (Path-A cache replay smoke)` |
| Command | `pytest -q --maxfail=1` with `PYTHONPATH=src` |
| Test | `test_compile_commands_compiler_mismatch` |
| Path | `tests/p3_v3/test_pilot_build.py` |
| Line | 1306 |
| Error | `Failed: DID NOT RAISE EvidenceError` |
| Count | `1 failed, 1196 passed, 9 warnings` |
| PR 17 run | `32225095224` job `95983092497` at `fb20947a` |
| main run | `32146789008` at `4444061d` (stopped earlier) |

`origin/main` still fails first on supplemental R2 path-scan because of
`--maxfail=1`. The compiler-alias defect is already present on
`origin/main`; it is only shadowed there.

The same `/usr/bin/c++` versus `/usr/bin/g++` pair appears in
`test_cmakecache_compiler_generator_root_drift` as `cache_compiler`.
That case did not run on the frozen GitHub job. It has the same alias
risk and must be repaired in the same node.

## Current Defect

`src/p3_v3/pilot_build.py` `collect_baseline_build_evidence` does:

```text
os.path.realpath(cache_compiler) != os.path.realpath(compiler)
os.path.realpath(compile_argv[0]) != os.path.realpath(compiler)
```

The 2026-08-17 pilot-build plan already freezes that realpath rule.
`/usr/bin/c++` and `/usr/bin/g++` are not a portable mismatch pair.

Local read-only reproduction on this VM:

```text
/usr/bin/c++ -> /etc/alternatives/c++ -> /usr/lib/llvm-18/bin/clang
/usr/bin/g++ -> g++-13 -> /usr/bin/x86_64-linux-gnu-g++-13
realpath equal: false
test_compile_commands_compiler_mismatch: PASS
```

GitHub Actions reproduction (frozen log):

```text
DID NOT RAISE EvidenceError
```

Do not treat the local PASS as proof that the CI test is sound.

## Approved Semantics

### Allowed behavior

Mismatch tests may use only identities whose realpaths cannot coincide
on a legal host. The portable form is a `tmp_path` compiler path that is
not a symlink of `/usr/bin/c++` and is not `/usr/bin/g++`.

A later optional test may prove the realpath contract in the opposite
direction: two `tmp_path` paths that share a realpath through a symlink
must be accepted. That test must not use the host `/usr/bin/c++` and
`/usr/bin/g++` pair.

### Required fail-closed behavior

Production must continue to reject:

- a CMakeCache compiler whose realpath differs from the snapshot;
- a `compile_commands` argv0 whose realpath differs from the snapshot;
- generator, source-root, or build-root drift;
- missing frozen include or `BOOST_MATH_STANDALONE=1`;
- system Boost markers;
- claims other than `blocked`.

Do not switch production to lexical string inequality. That would reject
a legal `c++` / `g++` alias pair and contradict the frozen realpath
contract.

Do not xfail, skip, or delete the failing test. Do not skip
`tests/p3_v3` in the workflow.

### Design choice

This design selects option A: edit only the mismatch oracles in
`tests/p3_v3/test_pilot_build.py`. Keep `os.path.realpath` in
`src/p3_v3/pilot_build.py`.

Option B, lexical path compare in production, is refused. Option C, a
new shared helper file, is refused.

## Future Implementation Scope

A later implementation node, if authorized, may edit only:

```text
tests/p3_v3/test_pilot_build.py
```

This archival node must not edit that file.

## Required Tests For A Later Node

New or revised tests must prove:

1. `test_compile_commands_compiler_mismatch` still raises
   `EvidenceError` matching `compiler differs` when the snapshot path
   and `compile_commands` argv0 have different realpaths, using a
   `tmp_path` identity rather than `/usr/bin/g++`.
2. The CMakeCache compiler-drift case in
   `test_cmakecache_compiler_generator_root_drift` still raises
   `CMakeCache compiler differs` when cache and snapshot realpaths
   differ, again without `/usr/bin/g++` as the mismatch oracle.
3. A host-independent alias pair (a regular file and a symlink to it
   under `tmp_path`) is accepted by `collect_baseline_build_evidence`.
4. Existing generator, source-root, missing-include, and system-Boost
   fail-closed tests continue to pass.
5. The GitHub Actions command `pytest -q --maxfail=1` is no longer
   stopped by this test. Path-scan remains a separate repair.

## Non-Goals

This design does not:

- change `.github/workflows` or skip `tests/p3_v3`;
- xfail, skip, or delete the failing test;
- change `src/p3_v3/pilot_build.py` or qualification modules;
- change supplemental R2 scanners or pull request 17;
- run CMake, a real compiler, ninja, make, or Boost.Math;
- run readiness, canonical freeze, retrieval, or SSOT writes;
- attribute the failure to pull request 16 or 17;
- authorize implementation, merge, attempt-2, or claim upgrades.

## Governance Stop

After this specification and the matching plan are committed and
pushed on the independent repair branch, work stops for Sol
review. Implementation remains unauthorized until a later user
node raises IMPLEMENTATION_AUTHORIZED from false after Sol review
and writes a 40-character IMPLEMENTATION_ENTRY in that instruction.

Pull requests 16 and 17 stay untouched. This repair pull request
stays draft.

## Self-Review Record

- Incomplete-marker scan: none found.
- Design choice A is stated; B and C are refused.
- Fail-closed list is explicit.
- Future write set is one test file.
- Pull requests 16 and 17 are out of scope.
- Implementation authorization is withheld.
