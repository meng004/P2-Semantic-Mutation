# Task 4 Report: Real CMake/Meson/Autotools Discovery Adapters

- Date: 2026-08-13
- Plan: `docs/superpowers/plans/2026-08-13-p3-task4-real-build-adapters.md`
  (amended rounds 1-2 during review; amendments recorded in the plan's
  normative sections and decision record)
- Execution: subagent-driven (implementers `gpt-5.6-sol-high`, reviewers
  `claude-fable-5-thinking-max`, per the user-fixed division of labor);
  controller committed per task after review; SDD ledger in the plan
  workspace.

## Commits

| Commit | Content |
|---|---|
| `3745c66d` | Task A — scale engine fortran + cuda line rules |
| `fa9d493a` | Task B — real CMAKE_CTEST_V1 |
| `e303c689` | Task C — real MESON_TEST_V1 |
| `afe7e2f0` | Task D — real AUTOTOOLS_MAKECHECK_V1 |
| `e7417e55` | B fix round 1 (lookbehind, IMPORTED/ALIAS case-sensitivity, schema dedup, docstring, force-added fixture) |
| `a1a20df3` | C fix round 1 (docstring char-equality, lookbehind + phantom guard, schema dedup) |
| `375929dd` | D fix round 1 (non-vacuous `test:=` distractor fixture) |
| `0b7088e1` | Shared block v1.1 lockstep (newline-preserving masking, namespace/extern-C transparent braces, fortran inline-comment cut, UTF-8 decodability rule) + drift guard |
| `83753bfd` | Round-2 adjudications (meson docstring realignment, pairwise drift guard) |
| `b5e1645c` | Protocol V4 re-emit with the real adapter registry |

## Receipts

- **validate-protocol V4:** PASS, `protocol_sha256
  240d8270d41802c9d5b86f30564eadd1a86fd9ed09de2c7e947d17c1a4d78519`;
  diff confined to `adapter_registry.json` (three real source hashes) and
  `protocol.json` (registry hash + artifact self-hash).
- **Freeze-point suite:** `893 passed in 361.79s`, clean worktree at
  `b5e1645c`, unsandboxed (868 baseline + 25 adapter/scale tests).
- **Blind smoke over the 28 delivered cmake/meson/autotools subjects**
  (neutral IDs only; harness reads the intake delivery, labels never
  appear): 28/28 returned per the seam contract, zero unhandled
  exceptions — **23 OK, 5 FAIL_CLOSED**, every failure the verbatim
  fail-closed receipt `CMakeLists.txt is absent`.

### Smoke table (neutral-ID prefix, per-category declaration counts)

| Neutral (8) | Eco | Status | src_files | PUB/CLI/EX/BM/PT | schemas | sites | s |
|---|---|---|---|---|---|---|---|
| 1f67b3f3 | cmake | OK | 1689 | 168/1/320/41/15 | 16 | 24227 | 3.3 |
| 24ab4a18 | cmake | OK | 1418 | 132/2/302/41/15 | 17 | 22438 | 2.9 |
| 3019d9a6 | autotools | OK | 1863 | 68/0/18/0/58 | 2 | 2312 | 2.5 |
| 36403210 | cmake | OK | 1711 | 168/0/321/41/18 | 18 | 24425 | 3.2 |
| 3c6e698f | cmake | OK | 1838 | 38/0/0/0/0 | 0 | 6496 | 2.2 |
| 494c35cb | cmake | OK | 25631 | 57/6/234/13/9 | 15 | 62240 | 36.1 |
| 4e7e9556 | meson | OK | 1311 | 1975/1/3/26/0 | 980 | 10811 | 2.5 |
| 643985b0 | cmake | OK | 1500 | 138/1/307/41/15 | 16 | 23844 | 3.3 |
| 6e05301e | cmake | OK | 1401 | 0/5/81/77/3 | 8 | 3338 | 1.6 |
| 734d6acc | cmake | OK | 1018 | 109/1/317/0/4 | 5 | 11066 | 2.2 |
| 748ce0fa | cmake | FAIL_CLOSED | — | CMakeLists.txt is absent | — | — | 0.4 |
| 74cdc825 | cmake | OK | 1786 | 487/0/0/0/0 | 0 | 4028 | 2.8 |
| 75c0e11c | autotools | OK | 3801 | 247/0/73/22/870 | 2 | 23732 | 8.2 |
| 76adbf41 | cmake | FAIL_CLOSED | — | CMakeLists.txt is absent | — | — | 2.4 |
| 82247005 | cmake | OK | 973 | 109/0/302/0/0 | 0 | 9286 | 2.1 |
| 84b70a11 | cmake | OK | 10788 | 8/44/4/1/118 | 162 | 57397 | 16.7 |
| 92b4ec54 | cmake | OK | 5619 | 8/24/4/0/12 | 36 | 5994 | 3.6 |
| 95e5fd62 | cmake | FAIL_CLOSED | — | CMakeLists.txt is absent | — | — | 1.9 |
| 9a76cacc | cmake | OK | 1499 | 138/1/307/41/15 | 16 | 23842 | 3.4 |
| a15c7019 | cmake | FAIL_CLOSED | — | CMakeLists.txt is absent | — | — | 0.0 |
| a6fc16a5 | cmake | OK | 6452 | 8/32/8/0/14 | 46 | 6671 | 4.5 |
| aa19a201 | cmake | OK | 6343 | 8/24/4/0/12 | 36 | 6715 | 4.0 |
| b2bfbf1e | cmake | OK | 1206 | 127/2/353/45/17 | 19 | 14029 | 2.7 |
| b3e0d3cd | autotools | OK | 1628 | 165/0/18/0/55 | 2 | 2048 | 2.3 |
| b50a524e | cmake | FAIL_CLOSED | — | CMakeLists.txt is absent | — | — | 0.0 |
| bb43dfe2 | autotools | OK | 3870 | 237/0/79/23/955 | 2 | 24785 | 9.6 |
| d782e757 | cmake | OK | 1709 | 168/0/321/41/18 | 18 | 24378 | 3.6 |
| f5f00bc4 | cmake | OK | 4169 | 17/25/0/0/9 | 34 | 2409 | 6.1 |

## Review trail

- Per-task independent reviews (round 1): B ❌ (5 findings), C ❌ (2
  adjudicated + mechanical), D ❌ (1 finding), then fix rounds; scoped
  re-reviews verdicted every finding ADDRESSED; shared-block v1.1 task
  reviewed **Approved** with one Important (reference-file dependency)
  resolved by round-2 amendment.
- Plan amendments (rounds 1-2, recorded in the plan): fortran end-regex
  anchoring + inline-comment cut; C-family transparent braces +
  effective-depth candidacy; UTF-8 decodability rule 8; textual-fidelity
  rule 9 + pairwise drift guard; cmake/meson grammar lookbehinds +
  case-sensitive IMPORTED/ALIAS; meson additive route + benchmark row
  shape frozen; fixture hardening (B counts, D distractor placement).
- Deferred minors: SDD ledger `progress.md` (plan workspace), triaged at
  the final whole-branch review.

## Declared-open items (honest receipts, no repair-by-substitution)

1. **Five cmake-descriptor subjects fail closed** (`CMakeLists.txt is
   absent`): their frozen, hash-bound build descriptors say `cmake` but
   the delivered trees carry no root `CMakeLists.txt` (subdir-cmake or
   non-cmake trees). Descriptors are immutable at the pinned P12 release;
   these subjects remain explicit discovery failures in the
   intention-to-evaluate funnel. A future P12 release could correct the
   descriptors; no P3-side patching is permitted.
2. **Zero-count categories** observed and retained (e.g. header-only
   subjects whose headers live outside an `include/` component yield 0
   PUBLIC_API rows; autotools CLI is zero by design).
3. Scale-language engine now covers cmake/python/cpp/cuda/fortran;
   meson.build files themselves remain outside `source_files` (not
   scale-countable) per the frozen rule.

## Next

Phase 1 frame derivation (`build-frames`) is unblocked for the 23+4
discoverable subjects; it needs a task-scoped plan (subject specs, slots,
contracts, applicability map inputs) per the charter sequencing note.
