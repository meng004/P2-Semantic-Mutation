# Gate SUPPLEMENTAL_ADMISSION_R2 — Task 4 Transport Audit

- **Environment:** Local Desktop
- **Cursor branch:** `origin/cursor/grok-phase3-supplemental-mining-r2`
- **Baseline:** `d95d6277ee09479d638bb83d75562e9dc4348031`
- **Reviewed head:** `548702be000249bbb4262ffe3bf282f4e93b962c`
- **Pull request:** draft PR #7
- **Scope:** contract/code freeze plus first live `Repository.issues` retrieval
- **Verdict:** `BLOCKED`

## 1. Observed artifact state

The final tree contains only `SCOPE.json`, `TRANSPORT_CONTRACT.json`,
`QUOTAS.json`, `COMMAND_LOG.json`, and `RETRIEVAL_HARD_FAIL.json` under
`data/external_slice/supplemental_r2/`. No snapshot, queue, decision, sheet,
evidence, handoff, readiness, freeze, annotation, prediction, or detection
artifact was minted. This fail-closed output condition is necessary but not
sufficient to pass the gate.

The full lineage is:

1. `7ede024f2605bd3497e16648e44beb589b984020` — contract freeze;
2. `d989f713938d46b8a25519fafd5c465554d3da45` — miner/checkers/tests;
3. `2ea01bc954c351b6075cbd5cb36ff9527a5c8ce9` — request pacing;
4. `519ab9ad370fafcad6c15215b95f0bd5cd8d14ad` — runner import change;
5. `548702be000249bbb4262ffe3bf282f4e93b962c` — diagnostic commit.

The Task 4 handoff omitted commits 3 and 4.

## 2. Standards axis

**Result: FAIL.**

`tests/external_slice/test_mine_supplemental_r2.py:5` imports `hashlib` without
using it. Exact Ruff checking of the changed test reports F401. `git diff
--check`, compileall, the 109 targeted tests, and the full 369-test suite pass,
but passing tests do not waive the repository style gate.

## 3. Specification axis

**Result: FAIL.**

### `SUPP-R2-RUN-ONCE-001`

The frozen plan requires one miner invocation and an immediate stop on hard
failure. The committed log contains 992 entries, two page-zero requests for
each of the six repositories, and 460 duplicated
`(repository, page_index, after)` groups. The diagnostic is timestamped
`2026-08-02T14:14:29Z`, while 26 further requests continued and the final log
entry ended at `14:15:46Z`. The log therefore combines overlapping runs and is
not evidence of one frozen execution.

The recorded `unexpected_error` is not evidence that GitHub returned malformed
JSON. Response decoding at `mine_supplemental_r2.py:770-773` converts such an
error to the explicit `malformed_json` invariant. By contrast,
`append_command_log` at lines 123-132 performs an unlocked read/modify/rewrite
of the shared JSON file before response decoding. The observed duplicate and
overlapping timestamps are consistent with one process reading a partial file
written by another and reaching the generic exception handler.

### `SUPP-R2-CODE-BEFORE-LIVE-001`

The first logged request started at `2026-08-02T13:49:03Z`, but commit
`519ab9ad...` changed the runner at `13:49:39Z`. Hence the live command log
spans two source states and violates the requirement that execution code be
committed before the first network command. Commit `2ea01bc9...` preceded the
first request and is semantically acceptable, but both commits must be included
in future lineage disclosure.

### `SUPP-R2-UNEXPECTED-FAIL-CLEANUP-001`

The `HardFail` handler removes every downstream artifact and appends a terminal
failure entry. The generic exception handler at lines 963-980 removes only
snapshot, queue, and pages, and appends no terminal command-log entry. The
committed command log consequently contains zero `retrieve_hard_fail` entries.
This path is not fail-closed against stale decision, sheet, evidence, or handoff
artifacts and does not bind the diagnostic to the command provenance.

## 4. Verification evidence

| Check | Result |
|---|---|
| Remote/head binding | origin head equals `548702be...` |
| Targeted tests | `109 passed` |
| Full tests | `369 passed, 10 warnings` |
| Compileall | exit 0 |
| Exact Ruff on changed test | exit 1, F401 |
| Command log | 992 entries; 460 duplicate page/cursor groups |
| Terminal failure log entry | 0 |
| Candidate/admission payload | absent |

## 5. Gate decision and only unlocked correction

Task 4 is `BLOCKED`. The existing diagnostic and command log must be retained
as failed-run evidence but must not be reused to mint a snapshot or admission
payload. No A1/A3 review, readiness, canonical freeze, C4, labelling, category
map, prediction, or detection work is unlocked.

The only unlocked action is a correction on the same Cursor VM branch from
`548702be...`, without `rtk`:

1. add an exclusive single-run guard that rejects a concurrent second process
   before any network request;
2. make command-log writes atomic and bind every entry, diagnostic, and
   terminal record to one immutable run ID and code commit;
3. route generic exceptions through the same complete cleanup and terminal-log
   contract as typed hard failures;
4. add regression tests for concurrency, partial log writes, generic-exception
   cleanup, terminal diagnostic binding, and code/run identity;
5. remove the unused import and pass the exact Ruff gate;
6. commit the correction before any new live retrieval, push, and stop for
   `SUPPLEMENTAL_ADMISSION_R2-transport-r1` local re-review.

A fresh live retrieval is not authorized by this gate. It may run exactly once
only after the correction commit receives a separate local re-review pass.

## 6. `SUPPLEMENTAL_ADMISSION_R2-transport-r1` re-review

- **Correction baseline:** `548702be000249bbb4262ffe3bf282f4e93b962c`
- **Correction commit:** `62fe052d017d66c9ac054442ee31cd9e3303705b`
- **Remote binding:** correction commit equals the Cursor branch head
- **Live retrieval:** not run
- **Verdict:** `BLOCKED`

### 6.1 Closed findings and positive verification

The correction is the direct child of the blocked baseline. It adds a
non-blocking POSIX lock before runner invocation, same-directory atomic command
log replacement, shared owner-side failure cleanup and terminal logging, and
run/code fields. The prior F401 is closed. The original 992-entry command log
and retrieval diagnostic are byte-unchanged, and the diff contains only the
miner and its tests.

Independent verification produced `113 passed` in the targeted suite and
`373 passed, 10 warnings` in the full suite. Exact Ruff, compileall, and
`git diff --check` all returned zero.

### 6.2 `SUPP-R2-LOCK-LOSER-MUTATION-001`

Lock acquisition correctly precedes every network call, but a lock loser still
executes global cleanup at `mine_supplemental_r2.py:1171-1186`. An independent
probe held `RETRIEVE.lock`, created owner snapshot/queue sentinels, and invoked
a second retrieval. The loser returned 1 with zero runner calls but deleted
both sentinels. A real second process can therefore remove artifacts published
by the active owner before that owner releases its lock.

The lock-loser path must be non-mutating with respect to the owner's command
log, diagnostic, snapshot, queue, pages, and downstream artifacts. It may emit
stderr or write a run-scoped rejection outside the owner's namespace.

### 6.3 `SUPP-R2-RUN-BINDING-FAILOPEN-001`

The new run/code fields are present but not fail-closed:

- `append_command_log` uses `setdefault` for entry fields, so an entry can keep
  run/code values that conflict with the authoritative arguments;
- `resolve_code_commit` accepts an arbitrary environment string without a
  full-SHA/current-HEAD check;
- `cmd_build_queue` rewrites the queue without preserving run/code fields; and
- neither supplemental checker reads or validates run/code fields or command
  log identity.

An independent positive payload passed the admission checker. After changing
the snapshot `run_id`, the checker still returned 0; after independently
changing the queue `code_commit`, it again returned 0. The added success test
checks only that correctly supplied values are copied; it is not the claimed
negative binding test.

### 6.4 Remaining frozen-transport defects

Two pre-existing transport requirements also remain unsafe for a fresh run:

1. Page command-log entries are written before response validation and never
   receive the returned `endCursor`, although the frozen plan requires every
   page log entry to bind it. A synthetic successful run confirmed the field is
   absent.
2. Lines 1117-1146 label publication atomic but remove/create/copy the final
   page directory and then write snapshot and queue non-atomically. A process
   death during this sequence can leave partial published artifacts. This is
   not the temporary-directory atomic rename required by section 3.3.

In addition, `init_command_log` targets the canonical path directly and would
overwrite the retained 992-entry failed-run evidence on the next retrieval.
The failed run needs an immutable archived namespace/hash manifest before a new
run can be authorized; it cannot be silently replaced.

### 6.5 Gate decision and r2 correction scope

Standards is `PASS`; Specification is `FAIL`. Fresh retrieval remains locked,
and accepted-ready remains 18. No candidate, A1/A3 review, readiness, freeze,
C4, labelling, prediction, or detection task is unlocked.

The only unlocked task is `SUPPLEMENTAL_ADMISSION_R2-transport-r2` on the same
Cursor branch, without `rtk` and without network retrieval. It must:

1. make lock-loser handling non-mutating;
2. validate one full-SHA code commit equal to the executing checkout and enforce
   exact run/code equality across log entries, diagnostic, snapshot, queue, and
   checker reconstruction;
3. preserve run/code during every rebuild and add one-field mutation negatives;
4. log validated returned `endCursor` on every page;
5. implement crash-safe atomic publication of pages, snapshot, and queue;
6. preserve the existing failed-run log/diagnostic immutably rather than
   overwriting them; and
7. commit, verify, push, and stop for local transport-r2 review before any live
   retrieval.

## 7. `SUPPLEMENTAL_ADMISSION_R2-transport-r2` re-review

- **Correction baseline:** `62fe052d017d66c9ac054442ee31cd9e3303705b`
- **Correction commit:** `ebbafad20859c6f6fbb6990ca63e3af8703a3773`
- **Remote binding:** correction commit equals the Cursor branch head
- **Live retrieval:** not run
- **Verdict:** `BLOCKED`

### 7.1 Closed findings and positive verification

The correction is the direct child of transport-r1. Independent probes confirm
that a lock loser now performs zero network and zero filesystem mutation;
run/code conflicts and illegal code commits fail before ownership; queue rebuild
and payload generation retain run/code; and the admission checker rejects
one-field run/code changes in log entries, snapshot, and queue.

The sealed archive contains the unchanged 992-entry log and original diagnostic.
Its two archived SHA-256 values exactly match the live originals and its manifest
records the correct count, timestamp, and invariant. The live files are
byte-unchanged relative to transport-r1.

Fresh verification produced `128 passed` in the targeted suite and
`388 passed, 10 warnings` in the full suite. Exact Ruff, compileall, and
`git diff --check` returned zero. Standards is `PASS` with no hard finding.

### 7.2 `SUPP-R2-ENDCURSOR-BINDING-001`

Successful page entries now record the verified `endCursor`, but the checker
validates only run/code fields. It does not reconstruct log-to-page-manifest
identity or compare repository/page order, `after`, `endCursor`, variables hash,
response-page hash, or next-request cursor continuity.

An independent positive payload passed. Changing only the first page log
entry's `endCursor` to `TAMPERED` still produced `ADMISSION_CHECK_OK` and exit 0.
The generation-side field therefore is not yet an auditable binding.

### 7.3 `SUPP-R2-FAILED-PAGE-PROVENANCE-001`

For nonzero exits and malformed JSON, the attempted command is logged. For a
parseable response that fails `validate_page`, however, the exception occurs
before either `base_entry` or `success_entry` is appended. A probe changed only
the first node typename to `PullRequest`; retrieval returned 1, but the command
log contained only `retrieve_start` and `retrieve_terminal_failure`, with zero
page entries. The executed request, response hash, variables, and timestamps
were therefore absent from the failed-run provenance.

Every runner invocation must create exactly one page command record. Validation
failures should retain the base fields plus explicit failed validation status
and invariant; only successful validation may mark `endCursor` as verified.

### 7.4 `SUPP-R2-PUBLISH-CRASH-ATOMICITY-001`

`crash_safe_publish` stages data but promotes `transport_pages` first and then
writes final snapshot and queue separately. The regression test raises an
ordinary `OSError`, so the outer exception handler runs cleanup; it does not
simulate process death.

An independent forked probe called `os._exit(77)` immediately after page
promotion and before the final snapshot write. The resulting root contained
`transport_pages/` and `.publish_staging/`, while snapshot and queue were absent.
Thus publication is neither one atomic unit nor covered at every real crash
boundary.

Use a run-scoped immutable publish directory plus one atomically replaced,
hash-bound commit pointer/manifest, or an explicit journal with rollback. Add
child-process death tests at every promotion boundary; checker acceptance must
depend on the single committed publish identity.

### 7.5 Gate decision and r3 correction scope

Standards is `PASS`; Specification is `FAIL`. Accepted-ready remains 18. No
fresh retrieval, candidate generation, A1/A3 review, readiness, canonical
freeze, C4, labelling, prediction, or detection work is unlocked.

The only unlocked task is `SUPPLEMENTAL_ADMISSION_R2-transport-r3` on the same
Cursor branch, without `rtk` and without network retrieval. It must:

1. independently reconstruct command-log/page-manifest/next-request pagination
   and fail on one-field mutations of every bound page field;
2. record exactly one page command entry for every runner invocation, including
   every `validate_page` failure;
3. replace sequential final publication with one fail-closed committed publish
   identity and test real process death at every boundary;
4. retain all r2 lock, run/code, archive, lint, and test guarantees; and
5. commit, verify, push, and stop for transport-r3 local review before any live
   retrieval.
