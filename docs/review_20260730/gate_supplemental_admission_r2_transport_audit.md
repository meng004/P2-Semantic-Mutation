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

## 8. `SUPPLEMENTAL_ADMISSION_R2-transport-r3` re-review

- **Correction baseline:** `ebbafad20859c6f6fbb6990ca63e3af8703a3773`
- **Correction commit:** `e3973bf7e0cf5af47598cd79c04a8a6b689f59d6`
- **Remote binding:** correction commit equals the Cursor branch head
- **Live retrieval:** not run
- **Verdict:** `BLOCKED`

### 8.1 Closed findings and positive verification

The correction is the direct child of transport-r2. It emits exactly one page
record for each runner invocation, including every validation failure. The
checker now binds page log and manifest fields, response/variables hashes,
`after`/`endCursor`, next-request continuity, and retained page hashes.
`PUBLISH_COMMIT.json` is written last and seals the snapshot and complete page
map; its absence or one-field hash change is rejected.

The subprocess death suite uses real `os._exit(70)` checkpoints at every
promotion boundary and exercises subsequent owner recovery. The r2 lock,
run/code, queue rebuild, and failed-run archive tests remain green; no data file
changed in the correction diff.

Fresh verification produced `145 passed` in the targeted suite and
`405 passed, 10 warnings` in the full suite. Exact Ruff, compileall, and
`git diff --check` returned zero. Standards is `PASS` with no hard finding.

### 8.2 `SUPP-R2-FULL-TRAVERSAL-COVERAGE-001`

The checker reconstructs only repositories and pages present in the supplied
log/manifest. It does not derive the required six-repository order from
`SCOPE.json`, require one contiguous block for every repository, or parse each
retained response's `issues.pageInfo` to prove terminal pagination.

An independent positive payload was modified by removing every PyMC page entry
from command log and manifest and deleting its retained page. After recomputing
the manifest hash and `PUBLISH_COMMIT`, only five repositories remained, yet the
checker still printed `ADMISSION_CHECK_OK` and returned 0. A second independent
probe changed a retained page to `hasNextPage=true` with a new `endCursor`, then
resealed the supplied set; it was likewise accepted.

The publish seal proves integrity of the supplied set, not completeness against
the frozen scope. Incomplete retrieval can therefore be resealed and admitted.

### 8.3 Gate decision and r4 correction scope

Standards is `PASS`; Specification is `FAIL`. Accepted-ready remains 18. No
fresh retrieval, candidate generation, A1/A3 review, readiness, canonical
freeze, C4, labelling, prediction, or detection work is unlocked.

The only unlocked task is `SUPPLEMENTAL_ADMISSION_R2-transport-r4` on the same
Cursor branch, without `rtk` and without network retrieval. It must:

1. derive the exact repository sequence from `SCOPE.json` and require one
   nonempty, contiguous page block for each of all six repositories in that
   exact order;
2. parse every retained transport response and bind raw `pageInfo.endCursor`
   and `hasNextPage` to log/manifest values;
3. require each intermediate page to continue and each repository's final page
   to have `hasNextPage=false`;
4. independently verify stable `totalCount`, contiguous indices/cursors, unique
   issue identity, and total retained node count equal to `totalCount`;
5. add resealed negative tests for missing repository, reordered repository
   blocks, missing middle/terminal page, false terminality, total-count drift,
   and missing/duplicate nodes; and
6. retain all r2/r3 guarantees, commit, verify, push, and stop for transport-r4
   local review before any live retrieval.

## 9. `SUPPLEMENTAL_ADMISSION_R2-transport-r4` re-review

- **Correction baseline:** `e3973bf7e0cf5af47598cd79c04a8a6b689f59d6`
- **Correction commit:** `be88a04ae55058f49ac52ec1a9aa28eb17aa6e70`
- **Remote binding:** correction commit equals the Cursor branch head
- **Live retrieval:** not run
- **Verdict:** `BLOCKED`

### 9.1 Closed finding and positive verification

The correction is the direct child of transport-r3. The checker now derives
the exact six-repository sequence from `SCOPE.json`, requires one nonempty and
contiguous page block per repository in that order, binds raw
`pageInfo.hasNextPage` and `endCursor` to the manifest and command log, enforces
intermediate/final page terminality, and checks stable `totalCount`, contiguous
page indices, retained node counts, and per-repository node identity.

The resealed missing-repository escape from r3 is closed: deleting the complete
PyMC block and recomputing the manifest and `PUBLISH_COMMIT` now returns exit 1
with the exact five-versus-six repository mismatch. The correction changes only
the miner, checker, and their tests; no retrieval or data artifact changed.

Fresh verification produced `155 passed` in the targeted suite and
`415 passed, 10 warnings` in the full suite. Exact Ruff, compileall,
`git diff --check`, and the no-data-change check returned zero. Standards is
`PASS`; the non-gating maintainability smells are abbreviated local names,
two-pass raw-page decoding, and repeated primitive field bundles.

### 9.2 `SUPP-R2-CROSS-REPOSITORY-IDENTITY-001`

`verify_scope_page_coverage` recreates its node-ID, issue-number, and URL sets
inside each repository block. It therefore proves uniqueness only within one
repository, even though GitHub node IDs and canonical URLs are global
identities across the frozen six-repository corpus. It also does not require a
node URL's owner/repository path to match the enclosing `SCOPE.json`
repository.

An independent fully resealed probe copied the retained PyMC nodes into the
GPyTorch page while preserving that page's count, then recomputed the response
hash, manifest hash, and `PUBLISH_COMMIT`. The complete admission checker still
printed `ADMISSION_CHECK_OK` and returned 0. Thus a corpus containing duplicate
global IDs/URLs and nodes attributed to the wrong repository remains
admissible.

### 9.3 Gate decision and r5 correction scope

Standards is `PASS`; Specification is `FAIL`. Accepted-ready remains 18. No
fresh retrieval, candidate generation, A1/A3 review, readiness, canonical
freeze, C4, labelling, prediction, or detection work is unlocked.

The only unlocked task is `SUPPLEMENTAL_ADMISSION_R2-transport-r5` on the same
Cursor branch, without `rtk` and without network retrieval. It must:

1. maintain node-ID and canonical-URL uniqueness sets across all six repository
   blocks, while issue-number uniqueness may remain repository-scoped;
2. parse every retained issue URL and require its owner/repository to equal the
   enclosing frozen SCOPE repository;
3. add fully resealed negative tests for a cross-repository duplicate ID/URL
   and a wrong-repository canonical URL;
4. retain every r2-r4 regression and verification guarantee; and
5. commit, verify, push, and stop for transport-r5 local review before any live
   retrieval.

## 10. `SUPPLEMENTAL_ADMISSION_R2-transport-r5` final re-review

- **Correction baseline:** `be88a04ae55058f49ac52ec1a9aa28eb17aa6e70`
- **Correction commit:** `5a76aa6a9032283f5dc086f94c0c2c098d80b4c7`
- **Remote binding:** correction commit equals the Cursor branch head
- **Live retrieval:** not run
- **Verdict:** `PASS_WITH_DISCLOSURE`

### 10.1 Finding closure

`SUPP-R2-CROSS-REPOSITORY-IDENTITY-001` is closed. The checker initializes
node-ID and canonical-URL sets once before traversing the six repository blocks,
while issue-number state is recreated inside each block. The miner likewise
shares ID/URL state across all six retrieval calls and subtracts the shared-set
size at repository entry when checking that repository's `totalCount`.

Both producer and independent checker now require the exact canonical URL
`https://github.com/<SCOPE owner>/<SCOPE name>/issues/<number>`. Fully resealed
negative tests cover cross-repository duplicate ID, cross-repository duplicate
URL, and wrong-repository URL; a positive test proves that equal issue numbers
in different repositories remain allowed.

### 10.2 Verification evidence

The correction is the direct child of transport-r4, and the remote branch head
equals the reviewed commit. The diff contains only the miner, admission
checker, and checker tests; no retrieval or data artifact changed. No prior r2-r4
test was removed.

Fresh Local Desktop verification produced `159 passed` in the targeted suite,
`419 passed, 10 warnings` in the full suite, and `4 passed` for the three
resealed identity attacks plus the cross-repository-number positive control.
Exact Ruff, compileall, `git diff --check`, and the no-data-change check all
returned zero. Standards is `PASS`; Specification is `PASS`.

Non-gating maintainability disclosures are duplicated canonical-URL validation
between producer and checker, raw string/set identity bundles, existing
`man`/`mans` abbreviations, and repeated reseal-test setup. Producer/checker
duplication is intentional independence for this evidence boundary.

### 10.3 Gate decision and only unlocked action

The transport correction gate closes as `PASS_WITH_DISCLOSURE`: it proves the
preflight implementation and synthetic fail-closed contracts, not a successful
live snapshot or admission result. Accepted-ready therefore remains 18.

Exactly one fresh Task 4 retrieval is now unlocked on the same Cursor VM branch
at `5a76aa6a...`, without `rtk`. No human A1/A3 review may begin in that run.
On hard failure, commit only the new diagnostic and command log, push, and stop
for Local Desktop audit. On success, commit the immutable transport pages,
snapshot, queue, publish seal, and command log, push, and stop for Local Desktop
transport-result audit. Candidate adjudication, readiness, canonical freeze,
C4, labelling, prediction, and detection remain locked.

## 11. Task 4 live transport-result audit

- **Retrieval baseline/code commit:** `5a76aa6a9032283f5dc086f94c0c2c098d80b4c7`
- **Published result commit:** `bc6cab5c6dbc83ab2d1185a3dd9f822f81de96fc`
- **Remote binding:** result commit equals the Cursor branch head
- **Run ID:** `0d76e415-0831-4417-b2fa-81b6ac046b2b`
- **Retrieval exit:** 0
- **Verdict:** `BLOCKED`

### 11.1 Observed-valid live result

The result commit is the single direct child of transport-r5. Its diff is
confined to the successful Task 4 artifacts: command log, 552 transport pages,
snapshot, queue, and publish seal; the obsolete live hard-fail diagnostic is
deleted. Frozen scope/transport/quota files and the sealed 992-entry historical
failed-run archive are byte-unchanged. No decision, evidence, candidate sheet,
handoff, A1/A3, readiness, or downstream artifact exists.

The live command log contains exactly one start, 552 unique and nonoverlapping
page commands, and one terminal success. Every entry has exit 0 and the same
run ID and producer code commit. Independent replay verifies six complete,
created-descending repository blocks, with page/node counts:

| Repository | Pages | Raw closed issues | Selected snapshot rows |
|---|---:|---:|---:|
| `pymc-devs/pymc` | 33 | 3,223 | 24 |
| `cornellius-gp/gpytorch` | 11 | 1,005 | 5 |
| `jonathf/chaospy` | 3 | 206 | 2 |
| `SALib/SALib` | 3 | 293 | 0 |
| `pytorch/pytorch` | 447 | 44,684 | 91 |
| `jax-ml/jax` | 55 | 5,491 | 34 |

All 54,902 raw nodes satisfy the accepted traversal checks. An independent
implementation of the cutoff, NFC/casefold phrase matching, per-phrase top-20,
union/deduplication, created-at/number ordering, source binding, record IDs, and
record hashes reproduces the committed 156 snapshot records exactly. Pure queue
reconstruction likewise reproduces all 156 rows, and `PUBLISH_COMMIT.json`
seals exactly the same 552 pages and snapshot.

Fresh verification produced `159 passed` in the targeted R2 suite and
`419 passed, 10 warnings` in the full suite. All 562 JSON files parse;
`git diff --check` and frozen/archive no-change checks return zero. The reserved
credential scan returns raw exit 1 with no match. Standards is `PASS`.

### 11.2 `SUPP-R2-RAW-SNAPSHOT-SEMANTIC-BINDING-001`

The committed live data is semantically correct, but the admission checker
does not prove that fact. `verify_scope_page_coverage` validates the raw
traversal, while `verify_snapshot_records` separately validates field presence,
self-hashes, frozen phrase membership/order, and nonempty claimed surfaces. It
never resolves `source_page_index`/`node_index` and reconstructs the referenced
raw issue's identity, timestamps, title/body hashes, labels, real phrase
surfaces, top-20 membership, union order, or complete snapshot cardinality.

A fully resealed synthetic probe changed a record whose raw title matched
`wrong result` to the frozen but absent phrase `incorrect value`, claimed a
fake title surface, recomputed the record hash, rebuilt queue/decision/evidence,
and recomputed `PUBLISH_COMMIT`. The complete checker printed `PAYLOAD_OK` and
`ADMISSION_CHECK_OK` and returned 0. This violates the frozen raw-page replay,
five-layer binding, and false-phrase negative requirements in sections 3.2,
4.1, 5(9), 6.2, and Task 4.

### 11.3 Distribution disclosure

The immutable snapshot already proves a structural quota shortfall before
human review: chaospy has at most two candidates against a target of three, and
SALib has zero against a target of three. Under the no-replacement rule, the
frozen route to six qualifying projects is therefore infeasible. Any eventual
R2 admission handoff must report `DISTRIBUTION_TARGET_AT_RISK`; PyTorch/JAX rows
may not substitute for chaospy/SALib without a separately reviewed amendment.

### 11.4 Gate decision and only unlocked correction

Specification is `FAIL`; A1/A3 remains locked. The live pages, snapshot, queue,
seal, and logs remain immutable observed evidence and must not be rerun or
regenerated.

The only unlocked task is `SUPPLEMENTAL_ADMISSION_R2-transport-result-r1` on
the same Cursor branch, without `rtk`, network access, or human review. It must:

1. make the checker independently reconstruct the exact ordered snapshot from
   the hash-bound raw pages using the frozen cutoff, matching, top-20, dedupe,
   ordering, source, field, and record-hash rules;
2. require exact full-record equality and cardinality against the committed
   snapshot before queue validation;
3. add fully resealed negatives for a frozen-but-false phrase/fake surface and
   mutations of title/body hashes, ordered labels, source page/index, missing,
   extra, and reordered snapshot records;
4. retain all r2-r5 and live-result artifacts byte-for-byte, pass targeted/full
   verification, commit, push, and stop for Local Desktop re-review; and
5. preserve the unavoidable chaospy/SALib distribution shortfall disclosure.

## 12. `SUPPLEMENTAL_ADMISSION_R2-transport-result-r1` re-review

- **Correction baseline:** `bc6cab5c6dbc83ab2d1185a3dd9f822f81de96fc`
- **Correction commit:** `1e5aee2329c9549ef665cc5cb6d487ebbab74b63`
- **Remote binding:** correction commit equals the Cursor branch head
- **Live data:** byte-identical to baseline
- **Verdict:** `BLOCKED`

### 12.1 Closed symptom and positive verification

The correction adds an ordered raw-page reconstruction before the existing
snapshot and queue checks. The exact previous attack now fails: after replacing
a real `wrong result` match with the frozen but absent phrase
`incorrect value`, rebuilding queue/decision/evidence and resealing
`PUBLISH_COMMIT`, the checker returns 1 at the `match_surfaces` field. The live
156-row snapshot also reconstructs successfully.

The diff contains only the checker and its tests. Retrieval pages, live log,
snapshot, queue, seal, frozen files, and historical failed-run archive are
unchanged. No network, retrieval, A1/A3, decision, evidence, or downstream work
ran. Fresh verification produced `168 passed` in the targeted R2 suite and
`428 passed, 10 warnings` in the full suite. Exact Ruff, compileall,
`git diff --check`, and live-data no-change checks returned zero. Standards is
`PASS`.

### 12.2 `SUPP-R2-CHECKER-INDEPENDENCE-001`

The checker does not independently implement cutoff handling, NFC/casefold
matching, per-phrase top-20 selection, union/deduplication, ordering, or record
construction. Its new reconstruction calls the producer's
`miner.select_phrase_union` directly. A semantic error shared by the producer
and this imported function therefore self-confirms instead of being detected by
an independent evidence boundary.

This does not satisfy the explicit transport-result-r1 requirement that the
checker independently reconstruct the frozen selection and record semantics.

### 12.3 `SUPP-R2-RAW-NODE-VALIDATION-001`

The reconstruction checks that each raw node is a dictionary, while the
existing coverage pass checks ID, number, canonical URL, and global identity.
Neither pass independently requires `__typename == Issue`, `state == CLOSED`,
non-null `closedAt`, or a complete label connection.

An independent fully resealed probe changed one raw node's `__typename` to
`PullRequest`, updated page/manifest/source hashes, rebuilt queue, decisions,
sheet, evidence, and `PUBLISH_COMMIT`, and then ran the complete checker. It
still printed `ADMISSION_CHECK_OK` and returned 0. The raw type and completeness
contracts in frozen sections 3.2, 4.1, and 5(1-3,9) remain fail-open.

### 12.4 Negative-test isolation gap

The named frozen-phrase negative uses `fabricated frozen phrase`, which is not
one of the eleven frozen phrases and is rejected by the old membership check.
It does not reproduce the real frozen-but-absent-phrase attack. In addition,
`fully_reseal_snapshot` only refreshes the snapshot and publish seal; it does
not rebuild queue, decisions, sheet, or evidence. Most new negatives would
therefore remain green through stale downstream mismatches even if the new raw
binding were removed.

### 12.5 Gate decision and r2 correction scope

Specification is `FAIL`; live data remains immutable observed-valid evidence,
and the structural chaospy/SALib shortfall disclosure remains unchanged. A1/A3
and every downstream task stay locked.

The only unlocked task is `SUPPLEMENTAL_ADMISSION_R2-transport-result-r2` on
the same Cursor branch, without `rtk`, network access, retrieval, or human
review. It must:

1. implement checker-owned cutoff, normalization, phrase-surface matching,
   per-phrase top-20, dedupe, ordering, and full record construction without
   calling the producer selection/record builders;
2. independently validate every raw node's Issue typename, CLOSED state,
   non-null closure, canonical URL, required fields, and complete labels before
   selection;
3. make fully resealed tests use a real frozen-but-absent phrase and rebuild all
   downstream bindings, so removing raw reconstruction makes the tests fail;
4. add likewise isolated, fully resealed `PullRequest` and incomplete-label
   attacks; and
5. preserve all live data byte-for-byte, pass targeted/full verification,
   commit, push, and stop for Local Desktop r2 re-review.

## 13. `SUPPLEMENTAL_ADMISSION_R2-transport-result-r2` re-review

- **Correction baseline:** `1e5aee2329c9549ef665cc5cb6d487ebbab74b63`
- **Correction commit:** `8076d82f8c02209ad33416594ee30e7183e8b7c6`
- **Remote binding:** correction commit equals the Cursor branch head
- **Live-data baseline:** `bc6cab5c6dbc83ab2d1185a3dd9f822f81de96fc`
- **Live data:** byte-identical to baseline
- **Verdict:** `BLOCKED`

### 13.1 Closed implementation findings

The checker now owns cutoff parsing, NFC/casefold normalization, phrase-surface
matching, per-phrase top-20 selection, URL deduplication, repository ordering,
and full snapshot-record construction. A test replaces all corresponding
producer functions with exceptions while the checker still verifies the valid
payload. The previous `SUPP-R2-CHECKER-INDEPENDENCE-001` finding is therefore
closed.

The checker also adds explicit raw-node checks for Issue typename, CLOSED state,
non-null `closedAt`, canonical issue URL, required fields, and label nodes. A
fully synchronized and resealed independent probe confirms that a raw
`PullRequest` mutation is rejected after updating the page hash, manifest,
snapshot source hashes and record hashes and rebuilding queue, decisions,
sheet, evidence, and the publish seal. The previous raw-type symptom is closed.

### 13.2 `SUPP-R2-LABEL-PAGINATION-FAILOPEN-001`

The complete-label check remains fail-open. At
`check_supplemental_r2_admission.py:240-245`, missing `pageInfo` is replaced by
an empty dictionary and the checker rejects only when `hasNextPage is True`.
Consequently a missing field, JSON `null`, or another non-boolean value is
accepted, although the frozen contract requires the exact condition
`labels.pageInfo.hasNextPage == false`.

The independent probe changed a selected raw issue first by deleting
`hasNextPage` and then by setting it to `null`. For each mutation it updated the
raw-page SHA, page manifest, all affected snapshot source hashes and record
hashes, rebuilt queue, decisions, candidate sheet and evidence, and recomputed
`PUBLISH_COMMIT.json`. In both cases the complete checker printed
`ADMISSION_CHECK_OK` and returned 0. Controls using `PullRequest` and literal
boolean `true` returned nonzero under the same full rebuild. This isolates a
real semantic fail-open rather than a stale-hash rejection.

### 13.3 `SUPP-R2-RAW-NEGATIVE-ISOLATION-001`

The committed `PullRequest` and incomplete-label tests call
`fully_reseal_snapshot`, but that helper refreshes only manifest page hashes and
the publish seal. It does not synchronize snapshot `source_page_sha256`, record
hashes, or downstream queue/decision/sheet/evidence artifacts. Both tests
therefore remain green on stale binding mismatches even if the intended
raw-node validator is disabled. They do not satisfy section 12.5(4)'s isolated,
fully resealed negative-test requirement.

The real frozen-but-absent phrase test does rebuild all downstream bindings and
is valid. The test-quality finding is confined to the two raw-page semantic
attacks.

### 13.4 Verification evidence

The correction is a single direct child of r1 and changes only the checker and
checker tests. Fresh Local Desktop verification produced `172 passed` in the
targeted R2 suite and `432 passed, 10 warnings` in the full suite. Exact Ruff,
compileall, `git diff --check`, and the live-data byte check all returned zero.

Standards and Specification both report `FAIL` because the complete-label
contract is still fail-open and the named negative tests do not isolate their
target semantic guards. Passing the committed suites does not override these
adversarial results.

### 13.5 Gate decision and r3 correction scope

A1/A3 and every downstream task remain locked. The 552 live pages, 156-row
snapshot and queue, command log, publish seal, frozen files, and historical
failed-run archive remain immutable observed evidence. Retrieval must not be
rerun. The structural chaospy/SALib shortfall and required
`DISTRIBUTION_TARGET_AT_RISK` disclosure are unchanged.

The only unlocked task is
`SUPPLEMENTAL_ADMISSION_R2-transport-result-r3` on the same Cursor branch,
without `rtk`, network access, retrieval, A1/A3 review, or downstream work. It
must:

1. require `labels` and `labels.pageInfo` to be dictionaries and require
   `labels.pageInfo.hasNextPage is False` exactly;
2. replace the `PullRequest` and incomplete-label negatives with isolated
   helpers that synchronize raw-page/manifest/snapshot hashes and rebuild every
   downstream binding before invoking the full checker;
3. cover missing, `null`, non-boolean, and literal `true` `hasNextPage` values,
   plus a positive literal `false` control;
4. prove that disabling the intended typename or label guard makes its
   corresponding negative fail, so no stale-hash check can self-confirm it;
5. preserve live data byte-for-byte, pass targeted/full/static verification,
   commit, push, and stop for Local Desktop r3 re-review.

## 14. `SUPPLEMENTAL_ADMISSION_R2-transport-result-r3` re-review

- **Correction baseline:** `8076d82f8c02209ad33416594ee30e7183e8b7c6`
- **Correction commit:** `020b60fb83f7eb1d34f143458fca62beab5aa398`
- **Remote binding:** correction commit equals the Cursor branch head
- **Live-data baseline:** `bc6cab5c6dbc83ab2d1185a3dd9f822f81de96fc`
- **Live data:** byte-identical to baseline
- **Verdict:** `PASS_WITH_DISCLOSURE`

### 14.1 Finding closure

`SUPP-R2-LABEL-PAGINATION-FAILOPEN-001` is closed. The checker now requires
`labels` and `labels.pageInfo` to be dictionaries, requires an explicit
`hasNextPage` member, and accepts only the literal boolean `False`. Missing,
null, string, and literal-true values fail closed.

`SUPP-R2-RAW-NEGATIVE-ISOLATION-001` is also closed. The raw-page tamper helper
updates page and manifest hashes, every affected snapshot source hash and
record hash, command-log page bindings and the publish seal, then rebuilds the
queue, decisions, sheet, and evidence. The focused matrix rejects a
`PullRequest`; absent/null labels; absent/null pageInfo; and absent, null,
non-boolean, or true `hasNextPage`. Literal false remains a passing positive
control.

The two guard-removal controls prove semantic isolation. With every other
binding unchanged, mapping only the attacked typename back to Issue changes
the fully synchronized PullRequest case from rejection to acceptance. Likewise,
changing only the attacked true `hasNextPage` to false changes the label case
from rejection to acceptance. The negative tests therefore no longer depend on
stale hashes or unrelated downstream mismatches.

### 14.2 Verification evidence

The correction is the single direct child of r2 and changes only the admission
checker and its tests. Fresh Local Desktop verification produced `182 passed`
in the targeted R2 suite, `442 passed, 10 warnings` in the full suite, and
`12 passed` in the focused raw-type/label/positive-control/guard-removal matrix.
Exact Ruff, compileall, `git diff --check`, and the live-data byte check all
returned zero. Standards is `PASS`; Specification is `PASS`.

No retrieval, A1/A3 review, readiness, canonical freeze, or downstream work is
present in the correction.

### 14.3 Gate decision and only unlocked execution

The transport-result correction gate closes as `PASS_WITH_DISCLOSURE`. The
disclosure is not a checker defect: the immutable snapshot contains only two
chaospy candidates and zero SALib candidates, so the frozen four-project quota
and J=6 route are structurally infeasible. Every later handoff must retain
`DISTRIBUTION_TARGET_AT_RISK`; PyTorch/JAX rows may not substitute for either
shortfall. Accepted-ready remains 18 because no A2/readiness run has occurred.

Only Task 5/6 A1+A3 admission review is now unlocked on the same Cursor VM
branch at `020b60fb...`, without `rtk` and without network retrieval. Review
must follow the exact six-repository queue order and frozen stop rule, retain
every exclusion, use only public A1/A3 evidence, keep A2 `PENDING` and
`analysis_id` blank, and build the decision, sheet, evidence, verification-log,
payload, and direct-child handoff artifacts. After pushing those two commits,
stop for `SUPPLEMENTAL_ADMISSION_R2` local audit.

Readiness, candidate replacement, new search/retrieval, canonical freeze, C4,
labelling, prediction, and detection remain locked.
