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
