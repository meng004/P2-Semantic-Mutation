# Sol High read-only final review packet — Phase 1 frames

Reviewer: GPT-5.6 Sol High (read-only). Executor: Grok 4.6 High.
Current status: **`PHASE1_CLOSURE_CANDIDATE`**. Do not mark
`PHASE1_CLOSED` unless this review PASSes. Do not start post-Phase-1
performance work from this packet.

Repository: `/Users/limeng/Papers/P3-SemanticMutation`
Branch: `main` @ `04d081c9010f8fb17a1290a0ceec6f3921f7eda3` =
`origin/main`.

## 1. CA-01 original review

Controller amendment CA-01: **PASS**.

Allowed: reuse 281 pass-1 files; 128 MiB only for exact root-relative
`subject-frames.json`; 90 MiB for every other artifact; raw canonical
JSON remains scientific identity; Git stores `subject-frames.json.gz`;
run only the unstarted shuffle pass 2; one named implementation round.

Forbidden: rerun pass 1; strip subjects/sites; change
`p3-subject-frames-v1`; rewrite raw `subject-frames.json` bytes; treat
gzip bytes as scientific identity; use checkpoint/cache for pass 2;
raise the global 90 MiB cap; install Git LFS; start post-Phase-1
performance work.

Sol High CA-01 amendment review verdict recorded in receipts: **PASS**.

## 2. CA-01 implementation diff

Commit `693ae67f` — continuation script, 22 regression tests, exact
`.gitignore` path `data/p3_v3/phase1_frames/out/subject-frames.json`,
plan amendment. Original `build_phase1_frames.py` was not edited.

```text
git show --stat 693ae67f
```

## 3. CA-02 funnel adjudication

Planned expectation only: 3 / 5 / 27.
**Actual: 3 / 9 / 23**
(`ADAPTER_UNSUPPORTED` / `ADAPTER_EXECUTION_FAILED` / `EXECUTABLE`).

Four extra Python fail-closed reasons, verbatim, not relabeled:

- `09d68a08…` `pyproject [project].name is absent`
- `0e5083ae…` `pyproject.toml is absent`
- `4bd7cd89…` `pyproject [project].name is absent`
- `8fc2d329…` `pyproject.toml is absent`

Python executable coverage drop is a Phase 1 limitation. Claims stay
`blocked`.

## 4. Pass 1 baseline

`data/p3_v3/phase1_frames/pass1_baseline_manifest.json`
file SHA-256 `b0be90ded75a4242bf883698d2b8c3f0c55d70b1b0928d7068bc1a3797e4eb11`.

281 regular files; 0 missing; 0 extra; all canonical JSON; all top-level
`artifact_sha256` self-hashes valid. `subject-frames.json` size
101,778,506; raw SHA-256 `588ff835…304b`; internal `83941b10…ff4a`.

## 5. Shuffle raw-byte identity

Continuation exit 0; wall 13,440.041 s; subject_count 35;
common_input_count 1050; file set 281/281; all raw SHA-256 identical;
`shuffle_byte_identical=true`; slot-closure 0; all `TECH_UNCERTAIN`.
Checkpoint/cache was not used for pass 2. Pass 1 was not rerun.

## 6. Gzip transport verification

Command `gzip -n -9`; Apple gzip 479; compressed size 21,898,797;
compressed SHA-256 `93499f5aaa…2ff7` (matches the observed reference
because the implementation matched). Decompressed bytes equal raw JSON;
canonical; internal self-hash valid.

Restore order: decompress → raw file SHA-256 → canonical equality →
internal artifact self-hash.

Scientific identity = raw SHA-256. Compressed SHA-256 = transport only.

## 7. Receipts

`data/p3_v3/phase1_frames/receipts.json` (status `PASS`, claims
`blocked`). Includes CA-01/CA-02, Sol High CA-01 verdict, baseline
hash, raw/compressed identities, actual 3/9/23, per-neutral
`discovery_status` and original failure reasons, 35 `TECH_UNCERTAIN`,
1050 common-input rows.

## 8. Clean-worktree suite

`.worktrees/p3-v3-phase1-frames-freeze` at `54a72576`, unsandboxed:
**`934 passed in 564.00s`**, exit 0. Worktree removed after the run.

## 9. Commits / push

| Commit | Role |
|---|---|
| `693ae67f` | CA-01 implementation |
| `54a72576` | frames + gzip + receipts |
| `04d081c9` | task report + charter + ledger |

`HEAD` = `origin/main` = `04d081c9`. No force push. Raw
`subject-frames.json` is not in the tree.

## 10. Task report / charter

- Report: `docs/review_20260814/phase1_frames_task_report.md`
- Charter Task 3 checkbox 2 ticked in
  `docs/superpowers/plans/2026-08-12-p3-return-to-scientific-critical-path.md`
- Decision ledger 2026-08-14/15 records the original 90 MiB stop, the
  101,778,506-byte aggregate, CA-01, Sol High PASS, unstripped JSON,
  gzip transport, actual 3/9/23, and the four Python reasons.

Protocol V4 unchanged
(`240d8270d41802c9d5b86f30564eadd1a86fd9ed09de2c7e947d17c1a4d78519`).
