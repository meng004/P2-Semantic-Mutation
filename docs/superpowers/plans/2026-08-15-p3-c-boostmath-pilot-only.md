# P3 PILOT_ONLY C-BOOSTMATH-001 End-to-End Replay

> **For agentic workers:** REQUIRED SUB-SKILL: Use test-driven development.
> This plan is the only authorized implementation scope for this branch.
> Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replay one already-revealed Boost.Math case through the smallest
P3 execution chain (contract freeze → mutant fixture import → independent
certification → MR execution → comparison → evidence package) and record
whether an MR outcome difference is observed on this fixed environment,
fixed case, and fixed fixtures.

**Study identity (frozen):**

```text
study_role: PILOT_ONLY
execution_mode: RETROSPECTIVE_PIPELINE_REPLAY
confirmatory_eligible: false
selection_outcome_independent: false
excluded_from_35_subject_freeze: true
claim_ceiling: observed_single_case
```

**This plan answers only:**

1. Whether the minimal execution chain can complete on one revealed case.
2. Whether an MR outcome difference is observed on this fixed run.

**This plan does not answer:** semantic vs syntactic superiority; T1/B1/B2/A1
group ranking; generalization to Boost, numerical software, P12, or 35
subjects; RQ1–RQ4 support; C1–C8 upgrades; or any overall mutation-score /
RFDS / significance claim.

**Architecture:** One isolated Python module plus one thin CLI. Reuse
`p3_v3.artifacts` (`canonical_json_bytes`, `canonical_sha256`, `file_sha256`,
`write_canonical_json`, `read_canonical_json`). Do not extend
`scripts/p3_v3/evidence.py`, Authority Lock, generic schema, workflow engine,
formal Phase 2 runner, or 35-subject orchestration. Formal
`p3_v3.run_records` intent/result/claim schemas cannot express this pilot
(job roles, scientific outcomes, and claim statuses are Phase-2/P12-only and
require every claim to be `blocked`). The pilot therefore keeps its own
atomic-row and claim-ledger documents and only reuses hashing/write
primitives.

**Tech stack:** Python 3.12 stdlib + pytest, `g++ -O2 -std=c++14`, SHA-256,
canonical JSON, Git subprocesses with `shell=False`. No `rtk`.

## Frozen identities

| Object | Value |
|---|---|
| P3 start commit | `8cd3e2da8ab31cc313a17fed01dc63ea84d59690` |
| P3 start tree | `be48398268f8096b6872d9e918f3064fa13cea98` |
| Branch | `cursor/p3-c-boostmath-pilot-001` |
| Required P12 commit | `a324498e22b8bd6126de89cf3613680cfad94b3b` |
| Boost fixed short | `03ea9c8` |
| Boost buggy short | `75dcb3e` |
| Compile | `g++ -O2 -std=c++14 -I <boost-math-fixed>/include -I /usr/include` |

P12 required file SHA-256 values are those listed in the task brief. Historical
`results-partial.jsonl` is sealed until the fresh atomic ledger and comparison
are hash-sealed.

## Global constraints

- Do not change Phase 1 to `PHASE1_CLOSED`.
- Do not read or modify the formal 35-subject denominator, Package C, formal
  Phase 2 checkpoints, or paper results.
- Do not upgrade P3 C1–C8.
- Do not modify the P12 repository; P12 is a fixed read-only input.
- Do not merge `main` and do not create a PR.
- Do not replace a failing fixture, input, MR, compiler, optimization level,
  or source version to obtain a preferred outcome.
- Scientific jobs do not auto-retry. Only a documented transient
  infrastructure failure may retry the same job ID / input / command /
  versions, at most three attempts, all retained.
- At most two repair rounds. A third load-bearing failure stops and is
  handed to Sol.

## Allowed new files

- `src/p3_v3/pilot_c_boostmath.py`
- `scripts/p3_v3/run_c_boostmath_pilot.py`
- `tests/p3_v3/test_pilot_c_boostmath.py`
- `research/p3_v3/pilots/c-boostmath-001/`
- `data/p3_v3/pilots/c-boostmath-001/`
- `docs/review_20260815/c_boostmath_pilot_cursor_handoff.md`
- `.gitignore` entry for `.pilot-work/`

## Frozen acceptance criteria

The execution-side task passes only if all of the following hold:

1. P3 base commit/tree match the start values above.
2. P12 input commit or recorded fallback plus the five required file hashes
   match the task brief.
3. Boost fixed/buggy full SHA and tree SHA are recorded and uniquely resolved.
4. `contract.json` timestamp/hash precede the P3 pilot patch-import artifact.
5. Both fixtures have a legal terminal certification state.
6. No post-failure substitution of mutant, input, or MR.
7. Every planned MR job has a terminal atomic row.
8. Comparison rebuilds from atomic rows alone.
9. Historical results are read only after fresh close.
10. score/experiment/claim ledgers and evidence package are complete.
11. Formal Phase 2, 35-subject artifacts, and C1–C8 files are unchanged.
12. No manuscript body edits.
13. `PYTHONPATH=src python3 -m pytest tests/p3_v3/test_pilot_c_boostmath.py -q`
    passes, plus directly related new-module tests.

## Claim ceiling

Pilot claim ledger may record only:

- `PILOT_C0_PIPELINE_EXECUTED`: `supported` or `observed` only if the full
  chain produced every terminal artifact.
- `PILOT_C1_SINGLE_CASE_MR_DIFFERENCE`: `observed` only if fresh atomic rows
  directly show a difference. Wording must begin with
  “In this retrospective pilot run...”.

All P3 C1–C8 and every cross-project / superiority / criterion-validity /
35-subject / generation-validity / outcome-blindness claim remain `blocked`.

---

### Task 1: Write failing tests for the isolated pilot

**Files:**
- Create: `tests/p3_v3/test_pilot_c_boostmath.py`

**Covered behaviors:**
- lineage fields are exactly the frozen identity
- contract freeze contains the required scientific fields and is immutable
  after write
- historical JSONL cannot be opened before fresh ledger/comparison seals
- fixture import discloses outcome-informed, non-denominator status
- certification uses an independent probe, not T1/B1/B2/A1 verdict code
- legal certification terminal states only
- atomic rows bind the required identity fields
- comparison rebuilds from atomic rows
- claim ledger enforces the pilot ceiling
- no mutant substitution after a fixture failure

- [ ] **Step 1: Write the focused failing tests**
- [ ] **Step 2: Run RED**

```bash
PYTHONPATH=src python3 -m pytest tests/p3_v3/test_pilot_c_boostmath.py -q
```

Expected: collection or import fails because `p3_v3.pilot_c_boostmath` does
not exist.

---

### Task 2: Implement the isolated runner

**Files:**
- Create: `src/p3_v3/pilot_c_boostmath.py`
- Create: `scripts/p3_v3/run_c_boostmath_pilot.py`

**Stage order (hard):**

1. Record environment and identities.
2. Freeze `contract.json` and hash it.
3. Import the two historical fixtures and disclose their limits.
4. Build and run the independent differential probe.
5. Close certification for `roots_m037` (nine gates) and `roots_m003`
   (syntactic-comparator subset).
6. Freeze the historical MR inventory.
7. Run the inventory three times on the fixed original; mark any non-PASS
   MR `INVALID_ON_FIXED_BASELINE` without replacement.
8. Run the same inventory, inputs, and three repetitions on fixed original,
   `roots_m037`, `roots_m003`, and buggy `75dcb3e`.
9. Hash-seal the atomic ledger, then emit comparison from those rows.
10. Only then read historical `results-partial.jsonl` and write the
    fresh-vs-historical replay comparison.
11. Write score/experiment/claim ledgers and the evidence package.

- [ ] **Step 3: Implement the minimal module and CLI**
- [ ] **Step 4: Run GREEN on the task-scoped tests**

```bash
PYTHONPATH=src python3 -m pytest tests/p3_v3/test_pilot_c_boostmath.py -q
```

- [ ] **Step 5: First commit**

```text
feat(p3-v3): add isolated boostmath pilot runner
```

---

### Task 3: Execute the scientific replay and record evidence

**Files:**
- Create: `data/p3_v3/pilots/c-boostmath-001/**`
- Create: `research/p3_v3/pilots/c-boostmath-001/{score-task,experiment-ledger,claim-ledger}.yml`
- Create: `research/p3_v3/pilots/c-boostmath-001/evidence-package.md`
- Create: `docs/review_20260815/c_boostmath_pilot_cursor_handoff.md`

- [ ] **Step 6: Run the CLI once; do not retune after seeing outcomes**
- [ ] **Step 7: Write ledgers, evidence package, and Sol handoff**
- [ ] **Step 8: Second commit**

```text
exp(p3-v3): record C-BOOSTMATH-001 pilot evidence
```

- [ ] **Step 9: Push the execution branch only**

```bash
git push -u origin cursor/p3-c-boostmath-pilot-001
```

No merge. No PR. Status remains `PENDING_SOL_REVIEW` and
`NOT AUTHORIZED FOR 35-SUBJECT EXPANSION`.
