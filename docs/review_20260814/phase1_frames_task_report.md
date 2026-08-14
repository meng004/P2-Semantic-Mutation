# Phase 1 Frame Derivation Task Report

- Date: 2026-08-14 / 2026-08-15
- Plan: `docs/superpowers/plans/2026-08-14-p3-phase1-frame-derivation.md`
  (CA-01 / CA-02 controller amendment recorded in the plan)
- Execution: Grok 4.6 High on `main`; independent final review remains
  GPT-5.6 Sol High (read-only). Claims stay `blocked`.

## Commits

| Commit | Content |
|---|---|
| `40a69fee` | Task A — adapter/zero-schema stay in the ITT funnel |
| `dce028c9` | Task B — unresolved Phase 1 profiling receipts |
| `420820c9` | Task C — extract/spec/`build_phase1_frames` driver |
| `bac7ec05` | Task D repair — resumable checkpoints and stderr progress |
| `693ae67f` | CA-01 continuation, tests, exact `.gitignore`, plan amendment |
| `54a72576` | 280 ordinary raw JSON + `subject-frames.json.gz` + receipts |

## Frozen scientific product

Production pass 1 reused in full (281 files). Shuffle pass 2 was the only
new derivation. Schema `p3-subject-frames-v1` is unchanged. Raw
`subject-frames.json` bytes were not stripped or rewritten.

| Quantity | Value |
|---|---|
| Subjects | 35 |
| Common-input rows | 1050 |
| Ordinary committed JSON | 280 |
| Slot-closure artifacts | 0 |
| `primary_technique` | `TECH_UNCERTAIN` on all 35 |
| Claims | `blocked` |

### Subject-frames scientific identity (raw JSON)

| Field | Value |
|---|---|
| Local raw filename | `data/p3_v3/phase1_frames/out/subject-frames.json` |
| Size | 101,778,506 bytes |
| Raw file SHA-256 | `588ff83530c16ef2647b523c157bf5585320dae17754918364db8bd96c5e304b` |
| Internal `artifact_sha256` | `83941b10d7df119d4e593dba70438fa77de5fc9177e67154d0d248595cf6ff4a` |

Git does not store the raw aggregate. Restore order: decompress → raw
file SHA-256 → canonical byte equality → internal artifact self-hash.

### Lossless gzip transport

| Field | Value |
|---|---|
| Committed filename | `data/p3_v3/phase1_frames/out/subject-frames.json.gz` |
| Command | `gzip -n -9` (stdin/stdout `-c` at write time) |
| Implementation | Apple gzip 479 |
| Compressed size | 21,898,797 bytes |
| Compressed SHA-256 | `93499f5aaa2a37bbeb29ee5e452533f6c7c054a12936f25a022a29d28f302ff7` |
| Decompression byte-identical | true |

Compressed SHA-256 is a transport integrity identity only.

## Pass 1 stop (correct under the original freeze)

The original driver completed production `build-frames`, then exited 2 at
`E_ARTIFACT_SIZE: artifact exceeds 90 MiB: subject-frames.json`. Shuffle
pass 2 had not started. That stop was required by the frozen 90 MiB gate.
The 101,778,506-byte aggregate was left intact.

## CA-01 / CA-02

CA-01 PASS (Sol High amendment review: PASS) authorized one named
implementation round: reuse the 281 pass-1 files; 128 MiB only for the
exact root-relative path `subject-frames.json`; every other artifact stays
at 90 MiB; keep raw JSON as scientific authority; Git stores gzip;
run only shuffle pass 2 through
`scripts/p3_v3/continue_phase1_frames_after_size_gate.py`; do not use
checkpoint/cache as a substitute; do not rerun pass 1; do not introduce
Git LFS.

CA-02 PASS records the **actual** discovery funnel. The plan's 3 / 5 / 27
is historical expectation only.

## Shuffle pass 2

| Field | Value |
|---|---|
| Exit code | 0 |
| Wall time | 13,440.041 s |
| File set | 281 / 281 identical |
| All raw SHA-256 | identical |
| `shuffle_byte_identical` | true |
| Checkpoint/cache used for pass 2 | false |

## Actual funnel (CA-02)

| Status | Planned (expectation only) | Actual |
|---|---|---|
| `ADAPTER_UNSUPPORTED` | 3 | **3** |
| `ADAPTER_EXECUTION_FAILED` | 5 | **9** |
| `EXECUTABLE` | 27 | **23** |

The four extra Python fail-closed subjects were **not** relabeled
`EXECUTABLE`. Original reasons, retained verbatim:

| Neutral | Reason |
|---|---|
| `09d68a08…ed0fef` | `pyproject [project].name is absent` |
| `0e5083ae…1b32` | `pyproject.toml is absent` |
| `4bd7cd89…92af` | `pyproject [project].name is absent` |
| `8fc2d329…15c8` | `pyproject.toml is absent` |

Python executable coverage is therefore 0/4 rather than the planned 4/4.
This is recorded as a Phase 1 limitation. The five cmake
`CMakeLists.txt is absent` receipts and three julia
`ADAPTER_UNSUPPORTED` receipts are unchanged.

Common-input row statuses: 600 `COMMON_INPUT_EXECUTABLE`, 450
`COMMON_INPUT_UNAVAILABLE` (12 non-executable subjects × 30, plus three
`EXECUTABLE` subjects with zero eligible schemas × 30).

## Bindings (unchanged protocol V4)

- Protocol file SHA-256:
  `240d8270d41802c9d5b86f30564eadd1a86fd9ed09de2c7e947d17c1a4d78519`
- Pass-1 baseline manifest SHA-256:
  `b0be90ded75a4242bf883698d2b8c3f0c55d70b1b0928d7068bc1a3797e4eb11`
- Receipts: `data/p3_v3/phase1_frames/receipts.json`

## Freeze-point suite

Clean worktree `.worktrees/p3-v3-phase1-frames-freeze` at `54a72576`,
unsandboxed: **`934 passed in 564.00s`**, exit 0. The worktree was
removed after the run.

## Next

Status after a successful `git push origin main` is
`PHASE1_CLOSURE_CANDIDATE`, not `PHASE1_CLOSED`. Sol High must complete
the independent read-only final review before `PHASE1_CLOSED`. Do not
start post-Phase-1 performance work before that review PASSes.
