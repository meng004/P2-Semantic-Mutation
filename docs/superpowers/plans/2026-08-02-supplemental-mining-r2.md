# Supplemental Mining R2 Protocol-Revision Freeze and Execution Plan

> **For agentic workers:** REQUIRED SUB-SKILL: use `superpowers:executing-plans`
> in the fresh Cursor VM execution session. Use
> `superpowers:test-driven-development` for every implementation change and
> `superpowers:verification-before-completion` before each handoff. This plan is
> a design-only freeze; none of its execution tasks are authorized in the
> Local Desktop design session that creates it.

**Goal:** Replace the failed GitHub Search API transport with a genuinely
issue-typed, fail-closed retrieval protocol, while preserving the frozen R1
scope and pre-committing a distribution-aware route from 18 ready defects to
at least 24 ready defects and at least six H-RANK-qualifying projects.

**Architecture:** A locally audited design commit freezes the unchanged
whitelist, phrases, exclusion classes, blinding rules, and R1 review stopping
rule. Only after that local gate passes may a fresh Cursor VM create an
execution branch. The execution branch enumerates GitHub GraphQL
`Repository.issues` connections, never Search API result unions, and locally
applies the frozen title/body/label phrases. An atomic snapshot is minted only
after complete pagination and all transport checks pass. Dedicated validators
bind snapshot -> queue -> decision -> sheet -> evidence field by field, with
explicit negative tests for every identity edge. The execution handoff stops
before readiness.

**Tech stack:** Python 3, pytest, GitHub CLI GraphQL transport, JSON, CSV,
SHA-256, Git.

## 0. Design-only freeze boundary

The Local Desktop task that adds this file is authorized to:

- read the audited repository at baseline
  `a9101e8e05d3424c075bba5c717e39e299c7900c`;
- create and push branch `codex/phase3-supplemental-mining-r2-design`;
- write this plan and run local document/repository checks; and
- report whether the R2 design is internally complete.

It is not authorized to:

- call GitHub issue retrieval, Search API, REST issue listing, or GraphQL;
- create `SCOPE.json`, a snapshot, a review queue, a candidate, a decision,
  evidence, or a handoff payload;
- run any buggy or fixed arm, create a reproducer, or run readiness;
- inspect MR text, mutation/kill data, predictions, detection results, or
  downstream analysis artifacts;
- modify either admission sheet, any accepted readiness batch,
  `FREEZE.sha256`, annotations, predictions, or runs;
- create a Cursor VM execution branch before the Local Desktop design gate is
  explicitly recorded as `PASS`; or
- merge or cherry-pick PR #6. Its integration remains a separate explicit
  decision.

The design branch and its commit are not an admission or readiness artifact.
No scientific count changes merely because this plan is frozen.

**Command-prefix policy (frozen):** Cursor VM commands must not use `rtk`.
Only Local Desktop commands use the `rtk` prefix. Every command shown in the
future Cursor execution tasks in section 7 is therefore intentionally plain.

## 1. Frozen authority and inherited invariants

### 1.1 Immutable design baseline

| Authority | SHA-256 at baseline `a9101e8e...` |
|---|---|
| `research/prereg_v2/external_slice_protocol.md` | `186b9734077035f63a1819569ecf45e645545862d045cb5ee899a7dd8f2841ca` |
| `research/prereg_v2/hypotheses.md` | `c3622e0f20e7a43278eac5e7847479d07e85ed086765303d3f5812510202806c` |
| `docs/review_20260730/gate_supplemental_admission_r1_audit.md` | `b8e5cf3019c5032a80ff1356ffe18f8b73cbca63d7f088a5f0d8783fd06a256b` |
| `docs/review_20260730/gate_a1d_readiness_batch3_audit.md` | `2b744e504e60508dec5c59539804b7fe13915d41b752c6048503d50c2290833c` |
| `docs/review_20260730/phase3_5_dual_model_audit_ledger.md` | `21df540c097fcd126a27f20797ac16daf787a43b4aba6b15e960b18c949bd3a0` |
| R1 plan `docs/superpowers/plans/2026-08-02-supplemental-mining-r1.md` | `1c2df1d7f2516d58385e1cee6688c6633bf4307cf2328059a5e86e35923e7af5` |

R1/R4 is evidence of a safe withdrawal, not a reusable candidate lineage. Its
old 128-row queue, 56 decisions, 44 exclusions, and 12 proposed rows remain
withdrawn. R2 must not import their neutral IDs, order, decisions, or evidence.
R2 inherits the scientific exclusion *classes* below; it does not inherit the
invalid R1 membership or adjudications.

### 1.2 Scientific scope that R2 may not amend

The repository whitelist remains exactly the six-repository R1 `SCOPE.json`
whitelist, in this exact order and with the same restrictions and ID prefixes:

| Order | Repository | ID prefix | Restriction |
|---:|---|---|---|
| 1 | `pymc-devs/pymc` | `EXT-pymc-` | numerical kernels only |
| 2 | `cornellius-gp/gpytorch` | `EXT-gpytorch-` | numerical kernels only |
| 3 | `jonathf/chaospy` | `EXT-chaospy-` | numerical kernels only |
| 4 | `SALib/SALib` | `EXT-salib-` | numerical kernels only |
| 5 | `pytorch/pytorch` | `EXT-pytorch-` | linalg, optim, or special-function numerical components only |
| 6 | `jax-ml/jax` | `EXT-jax-` | linalg, optim, or special-function numerical components only |

This remains a subset of the protocol section 2.1 whitelist. `GPy` remains
excluded. No repository may be added, removed, reordered, or replaced by
execution.

The inclusive-OR phrases remain, in this exact order:

1. `wrong result`
2. `incorrect value`
3. `numerical regression`
4. `precision loss`
5. `convergence failure`
6. `conservation violation`
7. `biased estimate`
8. `wrong sign`
9. `off by a factor`
10. `accuracy regression`
11. `numerical instability`

The created-at cutoff remains exactly `2026-08-01`. Matching is
case-insensitive over the issue title, body, and complete label
name set, exactly as protocol section 2.2 states. There is no synonym
expansion, stemming, fuzzy matching, comment search, or post-result phrase
addition.

The exclusion classes remain exactly:

- crash-only;
- build/packaging;
- API misuse;
- documentation;
- performance-only;
- test-infrastructure; and
- behaviour change that is intended API redesign.

Admission remains A1 + A3 only in this task. A2 is always `PENDING`. A row is
`ADMIT_PENDING_REPRO` iff A1 and A3 are both `PASS` and no frozen exclusion
class applies. All reviewed exclusions are retained in the R2 decision and
candidate artifacts and are never replaced.

### 1.3 Blind policy that R2 may not amend

- Admission IDs remain neutral `EXT-<repo>-<NN>` IDs.
- `analysis_id` is blank in every R2 artifact.
- Operator/fiber labels and vocabulary are forbidden.
- MR text, MR execution, mutation/kill data, prediction, detection, and
  downstream result access are forbidden.
- A2 stays `PENDING`; no build, trigger, or dual-arm result may be created or
  consulted.
- Only public issue/fix evidence needed for A1/A3 is visible to reviewers.
- Existing canonical sheets, readiness files, reproduction artifacts, and
  freeze registries are immutable throughout R2 admission.

## 2. Distribution-aware quota freeze

### 2.1 Audited starting state

Gate A1d-r3 accepted 18 ready defects across 11 projects. The counts relevant
to the H-RANK floor are:

| Project/group | Accepted ready before R2 | Qualifying before R2 |
|---|---:|---|
| `LLNL/sundials` | 4 | yes |
| `statsmodels/statsmodels` | 3 | yes |
| `numpy/numpy` | 2 | no |
| `scipy/scipy` | 2 | no |
| `scikit-learn/scikit-learn` | 1 | no |
| `Reference-LAPACK/lapack` | 1 | no |
| each of the six unchanged R1 repositories | 0 | no |

Five other projects have one accepted ready defect each. None belongs to the
unchanged R1 repository whitelist, so none may substitute for an R2 quota
miss.

The lower bound “at least six additional ready defects” cannot by itself
satisfy the H-RANK project-distribution floor under the unchanged R1
whitelist. All six R1 repositories currently contribute zero accepted-ready
defects, and a new qualifying project requires three. Six successes can create
at most two new qualifying projects, raising the total from two to four. To
reach six qualifying projects without changing the whitelist, R2 must target
at least twelve ready defects distributed as three each across four fixed
repositories. This is a feasibility consequence of the frozen floor, not a
new scientific threshold.

### 2.2 Fixed R2 distribution quota

| Quota order | Repository | Additional ready target | Resulting project count |
|---:|---|---:|---:|
| 1 | `pymc-devs/pymc` | 3 | 3 |
| 2 | `cornellius-gp/gpytorch` | 3 | 3 |
| 3 | `jonathf/chaospy` | 3 | 3 |
| 4 | `SALib/SALib` | 3 | 3 |
| 5 | `pytorch/pytorch` | 0 | 0 |
| 6 | `jax-ml/jax` | 0 | 0 |

If the four positive quotas are met, the cumulative state is at least 30 ready
defects and six qualifying projects: the four above plus SUNDIALS and
statsmodels. This satisfies the requested lower bounds of at least six new
ready defects and n >= 24, while also satisfying the independent J >= 6 floor.
An exact n=24 endpoint is not jointly feasible with J >= 6 under the unchanged
R1 whitelist. The targets are fixed before retrieval and may not be reassigned
after seeing issue yield, admission decisions, or readiness outcomes.

All six repositories remain in retrieval and admission scope under the
unchanged R1 stopping rule. PyTorch and JAX have zero R2 readiness quota: their
R2 admission rows may be retained as pending evidence but may not replace a
miss in one of the four positive-quota repositories without a new amendment.

R2 admission does not claim the ready targets have been met. It only seeks an
ordered, auditable supply of A1/A3-passing rows for later, separately
authorized readiness. A later readiness plan must consume cases in frozen
per-repository queue order, retain every `REPRO_FAILED`, and stop when the
repository quota is met or its frozen candidate queue is exhausted.

### 2.3 Unchanged R1 review stopping rule

For each of the six frozen repositories, review at most 20 unique issues. Stop
review at the first of:

1. five rows in that repository have A1 `PASS`, A3 `PASS`, A2 `PENDING`, and
   decision `ADMIT_PENDING_REPRO`;
2. 20 unique issues have been reviewed; or
3. the frozen deduplicated issue union is exhausted.

Items after the stop remain in the snapshot and queue with
`NOT_REVIEWED_AFTER_STOP`. They do not receive a verdict and do not enter the
candidate sheet. The target of five is an unchanged search/review budget, not
a readiness claim and not a replacement rule.

If the R2 handoff does not contain enough pending candidates to make every
ready quota feasible, it reports `DISTRIBUTION_TARGET_AT_RISK` and stops for
local audit. It does not search another project, increase the review cap,
change phrases, reuse withdrawn R1 rows, or run readiness.

## 3. Issue-typed retrieval transport

### 3.1 Required transport

The only permitted discovery transport is GitHub GraphQL
`Repository.issues`, invoked through `gh api graphql`. The frozen query must
select:

```graphql
repository(owner: $owner, name: $name) {
  issues(
    first: 100,
    after: $after,
    states: [CLOSED],
    orderBy: {field: CREATED_AT, direction: DESC}
  ) {
    totalCount
    pageInfo { hasNextPage endCursor }
    nodes {
      __typename
      id
      number
      url
      state
      title
      bodyText
      createdAt
      updatedAt
      closedAt
      labels(first: 100) {
        pageInfo { hasNextPage endCursor }
        nodes { name }
      }
    }
  }
}
```

The exact canonical query document, operation name, selected fields, page
size, state, ordering, and SHA-256 are frozen in `TRANSPORT_CONTRACT.json`
before any network call. The miner reads that file and refuses an inline or
changed query document.

Forbidden transports include:

- REST `/search/issues`;
- `gh search issues`;
- GraphQL `search(...)` or `SearchResultItemConnection`;
- REST `/repos/{owner}/{repo}/issues`, because that endpoint can contain pull
  requests; and
- browser/manual search used as queue membership evidence.

### 3.2 Complete pagination and local phrase selection

For each of the six frozen repositories, fetch the entire closed-issue
connection in created-descending order. Do not stop fetching merely because
phrase or review targets have been reached. Full traversal makes pagination
completeness and phrase exhaustion independently auditable.

Every page must satisfy all of the following before the next request:

- request exit code is zero and stdout is parseable JSON;
- `repository` and `issues` are non-null;
- page `totalCount` equals the first page's value;
- `after` equals the previous page's `endCursor`;
- page index is contiguous and no cursor repeats;
- every node has `__typename == "Issue"`, `state == "CLOSED"`, non-null
  `closedAt`, a canonical `/issues/<number>` URL, and no `/pull/` URL;
- issue node IDs, issue numbers, and URLs are unique within the repository;
- label pagination is complete (`labels.pageInfo.hasNextPage == false`); and
- the terminal page has `issues.pageInfo.hasNextPage == false` and the total
  number of unique nodes equals `totalCount`.

Any violation is a hard failure. On hard failure, write only a diagnostic
`RETRIEVAL_HARD_FAIL.json` and command log; do not mint a snapshot, queue,
decision, sheet, evidence tree, or candidate handoff.

After complete traversal, discard nodes with `createdAt` later than the frozen
cutoff `2026-08-01T23:59:59Z`. For each remaining issue, normalize title,
body, and labels only by Unicode NFC plus case-folding; do not remove
punctuation or rewrite spacing.
Record every exact phrase match and its source surface. For each phrase, retain
the first 20 matches in the connection's created-descending order. Union the
11 phrase lists per repository (66 frozen repository/phrase identities in
total), deduplicate each repository union by canonical issue URL, and order by
`(createdAt descending, issue number descending)`. Neutral IDs are assigned in
that order before any A1/A3 decision.

### 3.3 Atomicity and query identity

Retrieval writes raw, credential-scrubbed GraphQL pages to a temporary
directory. Only after all six repositories reach a complete terminal page
and the whole snapshot passes validation may the directory be atomically
renamed into `transport_pages/` and `ISSUE_SNAPSHOT.json` be minted.

Each command-log record binds:

- repository and page index;
- exact operation name;
- canonical query-document SHA-256;
- canonical variables and variables SHA-256;
- `after` cursor and returned `endCursor`;
- response-page SHA-256;
- exit code and stderr SHA-256; and
- start/end UTC timestamps.

The snapshot repeats the query-document hash and a hash of the ordered page
manifest. A changed owner/name, state, order, page size, cursor, cutoff,
operation name, selected field set, or query-document byte is query identity
drift and must hard-fail.

## 4. Artifact map and field-level binding

The future Cursor execution branch creates only:

```text
scripts/external_slice/mine_supplemental_r2.py
scripts/external_slice/check_supplemental_r2_admission.py
scripts/external_slice/check_supplemental_r2_handoff_hashes.py
tests/external_slice/test_mine_supplemental_r2.py
tests/external_slice/test_check_supplemental_r2_admission.py
data/external_slice/supplemental_r2/SCOPE.json
data/external_slice/supplemental_r2/TRANSPORT_CONTRACT.json
data/external_slice/supplemental_r2/QUOTAS.json
data/external_slice/supplemental_r2/transport_pages/*.json
data/external_slice/supplemental_r2/ISSUE_SNAPSHOT.json
data/external_slice/supplemental_r2/REVIEW_QUEUE.json
data/external_slice/supplemental_r2/REVIEW_DECISIONS.json
data/external_slice/supplemental_r2/EVIDENCE_SNAPSHOT.json
data/external_slice/supplemental_r2/admission_sheet.cursor_candidate.csv
data/external_slice/supplemental_r2/admission_evidence/EXT-*/evidence.json
data/external_slice/supplemental_r2/COMMAND_LOG.json
data/external_slice/supplemental_r2/VERIFICATION_LOG.json
data/external_slice/supplemental_r2/HANDOFF_SUPPLEMENTAL_R2.json
```

No pre-existing file may change.

### 4.1 Snapshot record

Every snapshot item contains and validates:

```text
snapshot_record_id
repository
repository_order
issue_node_id
issue_number
issue_url
state
created_at
updated_at
closed_at
title_sha256
body_text_sha256
ordered_labels
matched_phrases
match_surfaces
source_page_index
source_page_sha256
query_document_sha256
variables_sha256
node_index
snapshot_record_sha256
```

`snapshot_record_sha256` is computed over a canonical serialization of every
preceding field. The raw page remains hash-bound for independent replay of
type, state, phrase matching, and ordering.

### 4.2 Snapshot -> queue binding

Every queue row copies exactly:

```text
snapshot_record_id, snapshot_record_sha256, repository, repository_order,
issue_node_id, issue_number, issue_url, state, created_at, matched_phrases,
source_page_sha256
```

It adds only `neutral_id`, `union_order`, `repository_review_order`, and
`review_status`. Queue reconstruction from the snapshot must be a pure
function. The checker independently reconstructs the full ordered queue and
requires byte-equivalent semantic records, exact cardinality, no missing or
extra rows, and contiguous order/IDs.

### 4.3 Queue -> decision binding

Every reviewed decision copies exactly:

```text
neutral_id, snapshot_record_id, snapshot_record_sha256, repository,
issue_node_id, issue_number, issue_url, repository_review_order,
matched_phrases
```

It adds only public A1/A3 review fields:

```text
buggy_sha, fixed_sha, public_issue_url, public_fix_url, mechanism,
exclusion_class, crit_real_public_fix, crit_in_numerical_scope,
crit_dual_arm_repro=PENDING, decision, decision_reason
```

Decision order must equal the reviewed queue prefix. A decision for
`NOT_REVIEWED_AFTER_STOP`, a reordered decision, or any copied-field mismatch
hard-fails. A1 `PASS` requires full 40-hex buggy/fixed SHAs and public issue/fix
URLs. `ADMIT_PENDING_REPRO` requires A1=PASS, A3=PASS, A2=PENDING, and blank
exclusion class. An excluded decision requires one frozen exclusion class or
an explicit A1/A3 failure and remains present.

### 4.4 Decision -> sheet binding

Every sheet row is mechanically derived from one reviewed decision and binds:

```text
neutral_id, source_cohort, repository, issue_url, buggy_sha, fixed_sha,
mechanism, crit_real_public_fix, crit_dual_arm_repro,
crit_in_numerical_scope, decision, decision_reason
```

`source_cohort` is exactly `supplemental_r2`; A2 is exactly `PENDING`; and
`analysis_id` is exactly blank. Sheet ordering equals decision ordering. There
are no hand-edited fields and no row without a reviewed decision.

### 4.5 Decision -> evidence binding

Each evidence record copies exactly:

```text
neutral_id, snapshot_record_id, snapshot_record_sha256, repository,
issue_node_id, issue_number, issue_url, buggy_sha, fixed_sha,
public_issue_url, public_fix_url, mechanism, exclusion_class,
crit_real_public_fix, crit_dual_arm_repro, crit_in_numerical_scope, decision
```

`EVIDENCE_SNAPSHOT.json` is the ordered manifest of per-case evidence paths and
SHA-256 values. The checker requires one and only one evidence record per
reviewed decision and cross-checks every copied field against both decision
and sheet.

### 4.6 Handoff binding

The handoff binds:

- audited design commit and exact execution baseline;
- scope, transport contract, quota, code, test, page-manifest, snapshot,
  queue, decision, sheet, evidence-tree, command-log, and verification-log
  SHA-256 values;
- exact counts by repository, review status, decision, exclusion class, and
  quota feasibility;
- every executed command and raw exit code;
- environment and GitHub CLI versions;
- unresolved anomalies and shortfalls; and
- confirmations that A2 is all `PENDING`, `analysis_id` is all blank,
  forbidden data is absent, no readiness ran, and no existing file changed.

The handoff commit is a direct child of the payload commit. Its own file uses
the existing `SELF` resolution convention and the hash checker verifies the
direct-parent relationship.

## 5. Mandatory hard failures

The miner and checker must return nonzero and mint no candidate payload for:

1. any pull request by `__typename`, URL shape, or response structure;
2. any issue whose state is not `CLOSED` or whose `closedAt` is null;
3. an absent terminal page, `hasNextPage=true` at capture end, repeated or
   skipped cursor, changed `totalCount`, missing page, incomplete labels, or
   unique-node count different from `totalCount`;
4. any query-document, operation, variable, repository, cutoff, state, order,
   page-size, or cursor identity drift;
5. any nonzero `gh`/subprocess exit, timeout, malformed JSON, null repository,
   GraphQL `errors`, or partial stdout;
6. use of Search API, REST issue listing, manual search, or a PR-to-issue
   resolver;
7. a repository, phrase, exclusion class, or quota outside the frozen files;
8. duplicate URL/node/number, neutral-ID collision, reordered union, missing
   reviewed exclusion, or substitution after a failure;
9. any mismatch across the five binding layers in section 4;
10. non-`PENDING` A2, nonblank `analysis_id`, downstream vocabulary, or
    forbidden path access; and
11. a zero exit after any required validation or test reports failure.

Diagnostics must identify the first violated invariant and preserve command
provenance. A diagnostic is not a snapshot and cannot unlock review.

## 6. Required negative-test matrix

### 6.1 Transport and completeness negatives

Mocked tests must independently reject:

- an `Issue` node changed to `PullRequest`;
- an `/issues/` URL changed to `/pull/`;
- `CLOSED` changed to `OPEN` or `closedAt` removed;
- a middle page removed, duplicated, or reordered;
- a repeated cursor, wrong `after`, or changed `endCursor`;
- a final `hasNextPage=true`;
- a changed or inconsistent `totalCount`;
- an incomplete label connection;
- a GraphQL `errors` array with HTTP/command exit zero;
- malformed or partial JSON;
- command exit 1 with otherwise plausible stdout;
- query document, operation name, owner, name, state, ordering, page size, or
  cutoff changed by one value; and
- any call path containing `/search/issues`, `gh search`, `search(`, REST
  issues listing, or PR-to-issue resolution.

### 6.2 Snapshot and queue negatives

For each copied field in section 4.2, mutate exactly one value and require a
nonzero checker exit. Also test missing/extra/duplicate snapshot items, wrong
phrase order, false phrase match, changed match surface, changed raw-page hash,
changed snapshot-record hash, reordered union, noncontiguous order, wrong
neutral ID, and a row wrongly marked after/before the review stop.

### 6.3 Queue and decision negatives

For each copied field in section 4.3, mutate exactly one value and require a
nonzero checker exit. Also test missing/extra/reordered decisions, a decision
for a non-reviewed row, invalid exclusion class, omitted reviewed exclusion,
short SHA, missing public URL, A1/A3/decision inconsistency, non-PENDING A2,
and substitution of a later row after an exclusion.

### 6.4 Decision, sheet, and evidence negatives

For every field listed in sections 4.4 and 4.5, mutate the sheet alone and the
evidence alone in separate tests. Also reject missing/extra/duplicate sheet or
evidence rows, changed evidence path/hash, wrong cohort, nonblank alias,
forbidden vocabulary, hand-edited order, sheet/evidence disagreement, and
candidate rows derived from `NOT_REVIEWED_AFTER_STOP`.

### 6.5 Quota and handoff negatives

Reject changed starting counts, target repositories, quota values/order,
replacement repositories, an incorrect n/J projection, misleading quota-met
claims, missing shortfall disclosure, stale code/test hashes, incorrect
artifact counts, omitted hard failure, non-direct-child handoff, and any
handoff claiming readiness execution or canonical freeze.

Every negative must assert both nonzero exit and absence of newly minted
snapshot/candidate artifacts. Merely checking an error message is insufficient.

## 7. Future execution tasks

These tasks remain locked until a Local Desktop gate explicitly accepts the
design commit. `<R2_DESIGN_FREEZE_COMMIT>` must be replaced by that immutable
commit, not by a branch name.

### Task 1: Create the fresh Cursor VM execution branch

```bash
git fetch origin
git switch -c cursor/grok-phase3-supplemental-mining-r2 <R2_DESIGN_FREEZE_COMMIT>
git rev-parse HEAD
git status --short --branch
```

Expected: HEAD equals the audited design commit and the worktree is clean.
Do not merge PR #6 as part of branch setup.

### Task 2: Freeze scope, transport, and quotas before retrieval

Create `SCOPE.json`, `TRANSPORT_CONTRACT.json`, and `QUOTAS.json` with the
exact semantic values in sections 1-3 and the authoritative hashes in section
1. Commit them together before any network request:

```bash
python3 -m json.tool data/external_slice/supplemental_r2/SCOPE.json
python3 -m json.tool data/external_slice/supplemental_r2/TRANSPORT_CONTRACT.json
python3 -m json.tool data/external_slice/supplemental_r2/QUOTAS.json
git diff --check
git add data/external_slice/supplemental_r2/SCOPE.json data/external_slice/supplemental_r2/TRANSPORT_CONTRACT.json data/external_slice/supplemental_r2/QUOTAS.json
git commit -m "data(external): freeze supplemental mining R2 contract"
```

### Task 3: Implement the transport and validators test-first

Write all section 6 tests using synthetic/mocked GraphQL pages. Confirm RED,
implement the minimum production code, then confirm GREEN. No live retrieval
is allowed while tests are being authored.

```bash
env PYTHONPATH=src python3 -m pytest tests/external_slice/test_mine_supplemental_r2.py -q
env PYTHONPATH=src python3 -m pytest tests/external_slice/test_check_supplemental_r2_admission.py -q
git diff --check
```

The code commit must precede the first live retrieval command and must include
no snapshot, queue, decision, sheet, or evidence artifact.

### Task 4: Retrieve the complete issue snapshot

Run the miner once against all six frozen repositories. If any hard
failure occurs, commit only the diagnostic and command log, push, and stop for
Local Desktop audit. On success, independently validate page completeness,
query identity, phrase selection, deduplication, ordering, and ID allocation
before review begins.

No human A1/A3 review may begin until the immutable snapshot commit exists.

### Task 5: Review A1/A3 and build the bound payload

Review in exact queue order under the unchanged stop rule. Retain every
exclusion, keep A2 `PENDING`, keep aliases blank, collect only public A1/A3
evidence, and mechanically build the sheet and evidence manifest. Run the full
checker and every negative test.

### Task 6: Verify, commit, push, and stop

```bash
env PYTHONPATH=src python3 -m pytest tests/external_slice/test_mine_supplemental_r2.py tests/external_slice/test_check_supplemental_r2_admission.py -q
env PYTHONPATH=src python3 -m pytest -q
python3 scripts/external_slice/check_supplemental_r2_admission.py --root data/external_slice/supplemental_r2
python3 scripts/external_slice/check_supplemental_r2_handoff_hashes.py --handoff data/external_slice/supplemental_r2/HANDOFF_SUPPLEMENTAL_R2.json
git diff --check
git status --short --branch
```

Commit payload and handoff separately. Push the Cursor branch and stop at
`Gate SUPPLEMENTAL_ADMISSION_R2`. Do not run readiness, modify canonical
sheets, write `FREEZE.sha256`, assign aliases, inspect downstream results, or
create another branch.

## 8. Local Desktop gate after future execution

Local Desktop must independently verify:

1. execution lineage descends directly from the audited R2 design commit;
2. the scope, transport, and quota commit predates every retrieval artifact;
3. no Search API/REST issue-list/PR resolver path exists or ran;
4. all six issue connections are complete and issue-typed;
5. query identity and raw page hashes replay exactly;
6. local phrase selection and queue reconstruction are exact;
7. every field across snapshot, queue, decision, sheet, and evidence binds;
8. all promised negative tests fail closed;
9. all reviewed exclusions remain and no substitution occurred;
10. A2 is entirely `PENDING`, aliases are blank, and blind scans are clean;
11. no readiness, canonical freeze, or downstream artifact was created; and
12. quota feasibility/shortfall is disclosed without claiming ready success.

The only verdicts are `PASS`, `PASS_WITH_DISCLOSURE`, or `BLOCKED`. A passing
R2 admission gate may authorize a new, separately planned readiness session;
it does not itself change the ready count. Canonical freeze remains blocked
until accepted readiness evidence proves n >= 24 and at least six projects
with at least three ready defects each.

## 9. Frozen successor state

After this design plan passes Local Desktop review:

- the only newly unlocked action is creation of a fresh Cursor VM execution
  branch from the immutable design commit;
- PR #6 integration remains undecided and outside this task;
- no search, candidate creation, or readiness has occurred in the design
  lineage; and
- any requested change to repositories, phrases, exclusions, blind policy,
  quota allocation, stopping rule, transport, or binding contract requires a
  new locally reviewed amendment before execution.
