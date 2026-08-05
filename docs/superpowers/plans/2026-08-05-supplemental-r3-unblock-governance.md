# Supplemental R3 Unblock Governance Design Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:executing-plans` for the separately authorized Cursor VM run,
> `superpowers:test-driven-development` for every implementation change, and
> `superpowers:verification-before-completion` before either future handoff.
> This document authorizes design only. It does not authorize R3 retrieval,
> admission, readiness, or any downstream scientific action.

**Goal:** Define a lawful, replayable way to obtain enough new candidate
evidence to address the frozen GPyTorch/chaospy/SALib shortfall 2/3/3 without
mutating R2, importing PR #6 Batch 3, changing quotas, or starting readiness.

**Architecture:** Adopt an append-only `supplemental_r3` successor protocol.
Its contract, queries, repositories, phrases, collision set, stopping rules,
and raw-page formats are committed before the first network request. A fresh
transport tree produces a replayable snapshot, then binds snapshot -> queue ->
decision -> sheet -> evidence; the frozen R2 transport is compared byte/tree
for identity and is never used as writable membership state.

**Tech Stack:** Python 3, pytest, GitHub CLI GraphQL, canonical JSON, CSV,
SHA-256, and Git.

## Global Constraints

- Design baseline and remote `main` are exactly
  `3c518b8467f74c9a6efd11f2db267f9f30e1c822`.
- PR #7 head is `8d3db94a18e026cb17a6319d88a3c5960df5c406`;
  its merge commit is the fixed main SHA.
- The accepted R2 payload is
  `7d27f287601b45f895749fb507eaff72d746a4de`; the local audit merge is
  `be017d25d125cfd72aca48995dcdf616f7d55829`.
- PR #6 Batch 3 head
  `f6f1888f361a524a481cc9505e567a8bc414b9ea` is a denylisted identity. It
  must not be fetched, opened, inspected, merged, cherry-picked, used as an
  ancestor, or used as a source of payload, IDs, hashes, paths, files, or
  lineage.
- The frozen state remains 67 decisions / 9 `ADMIT_PENDING_REPRO` / 58
  `EXCLUDED`, with all A2 values `PENDING` and all `analysis_id`/aliases blank.
- The shortfall remains GPyTorch 2 / chaospy 3 / SALib 3 and the status remains
  `DISTRIBUTION_TARGET_AT_RISK` until a separately audited successor payload
  proves otherwise.
- No current design action creates `supplemental_r3`, raw pages, a queue,
  decisions, a sheet, evidence, payload, handoff, readiness, r8, or a canonical
  freeze.

---

## 1. Local Desktop design boundary

This design session may add only this plan and
`docs/review_20260805/gate_supplemental_r3_unblock_design_audit.md`. It may
verify the fixed GitHub identities, read frozen main artifacts, run the stated
repository tests, create the two required documentation commits, and push the
design branch. It may not perform issue discovery, fetch issue evidence,
adjudicate an R3 row, implement an R3 miner/checker, or invoke readiness.

The design branch itself changes no scientific count. A pushed design is only
an auditable permission boundary for a later, separately authorized, single
Cursor VM execution.

## 2. Evidence findings that constrain the design

The conclusions below are bound to the frozen files on main, not to a new
search or manual browsing session.

| Finding | Frozen evidence | Consequence |
| --- | --- | --- |
| Totals are 67/9/58 | `supplemental_r2/HANDOFF_SUPPLEMENTAL_R2.json` and `REVIEW_DECISIONS.json` | No count may be reinterpreted in design. |
| GPyTorch queue has five rows | `REVIEW_QUEUE.json` | Only `EXT-gpytorch-03` is admitted; the other four remain frozen exclusions. |
| GPyTorch exclusions are final | `REVIEW_DECISIONS.json` | `-01` lacks a public fix, `-02` and `-04` are intended API redesigns, and `-05` is crash-only. |
| chaospy queue has two rows | `REVIEW_QUEUE.json` | `EXT-chaospy-01` is only a conditional lead because original fix evidence is absent; `-02` is intended API redesign. Neither may be rewritten into R3 membership. |
| SALib queue size is zero | R2 queue repository counts | There is no frozen SALib row to admit. |
| Shortfalls are 2/3/3 | R2 handoff `quota_feasibility.shortfalls` | Existing evidence cannot fill any of the missing eight slots. |
| Blind invariants hold | R2 handoff confirmations | A2 stays `PENDING`; aliases and `analysis_id` stay blank. |
| Batch 3 is excluded | `gate_supplemental_admission_r2_audit.md` | The successor must descend from accepted main only and must not inspect Batch 3. |

The evidence supports a design for acquisition. It does **not** support the
claim that eight qualifying issues exist. That claim remains insufficient
until a frozen successor execution captures and audits them.

## 3. Route comparison and ruling

| Route | Scientific effect | Governance result | Ruling |
| --- | --- | --- | --- |
| A. Preserve the current evidence scope | The exhausted R2 queue and final exclusions remain unchanged. | Shortfall 2/3/3 cannot be recovered. | Lawful but permanently `R3_BLOCKED`. |
| B. Append-only successor evidence protocol | Creates a new, precommitted evidence universe while preserving R2 byte-for-byte. | Can lawfully test whether eight new, repository-specific candidates exist. | **Recommended, with the conditions in this plan.** |
| C. Amend quotas or allow cross-repository substitution | Changes the frozen distribution target and `replacement_policy=forbidden`. | Requires an independent scientific protocol amendment and a new governance audit. | Rejected by this design. |

Route B is the only authorized design. It may produce exactly the missing
repository-specific supply: at least two new GPyTorch, three new chaospy, and
three new SALib A1/A3-passing rows. An issue/fix pair counts once and only for
its own repository; over-yield in one repository never substitutes for
another.

## 4. Supplemental R3 legal boundary

The future protocol identity is `SUPPLEMENTAL_R3_EVIDENCE`, with an isolated
root `data/external_slice/supplemental_r3/`. Before the first network request,
one immutable contract commit must freeze all of the following:

1. the fixed main/design authority and the Batch 3 denylist;
2. the three repositories and their exact order;
3. the discovery and issue-evidence GraphQL query documents as bytes;
4. the cutoff, selected fields, pagination rules, phrases, normalization, and
   membership algorithm;
5. the pre-existing collision universe and its input SHA-256 values;
6. the per-repository stopping rules and fixed 2/3/3 supply target;
7. the A1/A3 rules, exclusion classes, and blind invariants;
8. raw file names, canonical JSON rules, manifests, and all binding fields;
9. failure atomicity, no-retry policy, and payload/handoff structure; and
10. the R2 transport byte/tree comparison set.

Changing any frozen item after a network request invalidates the entire run.
The run stops without a candidate payload; a revised attempt requires a new
protocol amendment and a new Local Desktop audit, not a retry.

## 5. Frozen discovery contract

### 5.1 Repositories and cutoff

Discovery is limited to these repositories in this order:

1. `cornellius-gp/gpytorch`, numerical kernels only;
2. `jonathf/chaospy`, numerical kernels only; and
3. `SALib/SALib`, numerical kernels only.

The created-at cutoff is `2026-08-05T07:31:15Z`, the fixed PR #7 merge time.
No other repository, fork, mirror, organization search, issue transfer target,
or cross-repository fix may enter membership. `known_issue_urls` is frozen as
an empty list: manual browsing and reviewer-supplied URLs are not discovery
sources.

### 5.2 Continue GitHub GraphQL `Repository.issues`

The successor continues GitHub GraphQL `Repository.issues` because it yields
issue-typed, repository-scoped, completely pageable raw evidence. The frozen
operation is `SupplementalR3RepositoryIssues`. It requests all `CLOSED` issues
in `CREATED_AT DESC` order with page size 100 and selects:

```text
repository.nameWithOwner
repository.issues.totalCount
repository.issues.pageInfo.{hasNextPage,endCursor}
repository.issues.nodes.{__typename,id,number,url,state,title,bodyText,
createdAt,updatedAt,closedAt}
repository.issues.nodes.labels.pageInfo.{hasNextPage,endCursor}
repository.issues.nodes.labels.nodes.name
```

Every connection is traversed to a terminal page before local phrase matching.
The hard failures inherited from R2 remain: nonzero exit, timeout, malformed
JSON, GraphQL errors, null repository/connection, non-`Issue` node, non-closed
state, null `closedAt`, pull URL, incomplete labels, cursor drift, total-count
drift, missing/reordered/duplicate page, query identity drift, or unique-node
count unequal to `totalCount`.

### 5.3 Frozen phrase expansion and membership

Matching is case-insensitive after Unicode NFC plus case-folding over title,
body, and the complete label-name set. There is no stemming, fuzzy matching,
comment matching, synonym generation, or phrase addition after retrieval.

The ordered common phrases are:

1. `incorrect result`
2. `wrong value`
3. `inaccurate result`
4. `inaccurate value`
5. `floating point error`
6. `rounding error`
7. `loss of precision`
8. `precision issue`
9. `overflow`
10. `underflow`
11. `returns nan`
12. `returns inf`
13. `fails to converge`
14. `convergence issue`
15. `unstable result`
16. `variance estimate`
17. `sensitivity index`

Append these ordered repository-specific phrases after the common list:

| Repository | Additional phrases in order |
| --- | --- |
| GPyTorch | `cholesky`, `positive definite`, `covariance matrix`, `predictive variance`, `marginal log likelihood`, `posterior mean`, `kernel value` |
| chaospy | `quadrature error`, `polynomial expansion`, `moment error`, `distribution parameter`, `recurrence coefficient`, `orthogonal polynomial`, `sample mismatch` |
| SALib | `sobol index`, `second order index`, `confidence interval`, `saltelli sample`, `morris measure`, `delta index`, `sensitivity estimate` |

Each phrase retains every cutoff-eligible match. The per-repository union is
deduplicated and ordered by `(createdAt DESC, issue number DESC)`. There is no
per-phrase result cap and no yield-dependent reordering. A row is excluded from
the R3 queue if its repository/node/number/canonical issue URL collides with
R2 `REVIEW_QUEUE.json`, the fixed-main canonical admission sheet, or another
R3 row. A collision is retained in a collision log but can never count.

The changed phrases create new successor membership only. They do not rewrite
R2 raw pages, snapshots, queue membership, IDs, decisions, or evidence. In
particular, `EXT-chaospy-01` remains an R2 exclusion and cannot be rescued into
the 3-new-chaospy requirement.

### 5.4 Neutral IDs and no reuse

IDs are assigned before review in the frozen union order, continuing after the
largest R2 queue ordinal:

- GPyTorch begins at `EXT-gpytorch-06`;
- chaospy begins at `EXT-chaospy-03`; and
- SALib begins at `EXT-salib-01`.

Every reviewed exclusion retains its assigned ID. IDs are never renumbered
after a decision, and a later row never replaces an excluded ID. A canonical
issue URL, issue node ID, issue number, fixed SHA, or issue/fix pair may appear
in at most one R3 record. The same issue or fix cannot fill two quotas.

## 6. Issue-page and raw-response evidence

The contract freezes a second GraphQL operation,
`SupplementalR3IssueEvidence`, before discovery. For each row reached in queue
order, it retrieves the issue identity/body/labels, complete comments, and
complete issue timeline/cross-reference evidence needed to locate a public fix.
The selected fields, page sizes, item types, cursors, and query bytes are fixed
in the contract. Reviewer-supplied browser content cannot enter the record.

When captured issue evidence exposes a same-repository public commit or merged
fix reference, a precommitted `SupplementalR3FixEvidence` operation captures
the commit OID, canonical URL, parents, repository, and public metadata. A fix
not linked by the captured issue evidence fails A1; reviewers may not search
for a replacement fix manually.

Raw bytes are stored without JSON reformatting, key sorting, newline changes,
or wrapper insertion:

```text
data/external_slice/supplemental_r3/
  transport_pages/{repo_order}_{owner}_{repo}_page_{index:04d}.json
  issue_pages/{neutral_id}/issue_page_{index:04d}.json
  fix_pages/{neutral_id}/fix_page_{index:04d}.json
  page_manifests/discovery_pages.json
  page_manifests/{neutral_id}_issue_pages.json
  page_manifests/{neutral_id}_fix_pages.json
```

`issue_pages/...` are the original GraphQL response bytes and therefore the
original issue-page evidence for this protocol. A canonical
`ISSUE_PAGE_SNAPSHOT.json` separately summarizes selected values; it never
replaces the raw response.

Each ordered page-manifest entry contains:

```text
protocol, operation_name, repository, neutral_id_or_blank, page_index,
after_cursor, end_cursor, has_next_page, total_count, node_count,
query_sha256, variables_sha256, raw_response_sha256,
stderr_sha256, exit_code, started_at_utc, ended_at_utc
```

The query SHA-256 is over the exact UTF-8 query-document bytes. Variables are
serialized as UTF-8 canonical JSON with sorted keys, separators `,` and `:`,
and no trailing newline before variables SHA-256 is computed. Raw-response
SHA-256 is over stdout bytes exactly as written. The page-manifest SHA-256 is
over the canonical JSON encoding of the complete ordered entry array. The
snapshot repeats all three hashes and rejects any replay mismatch.

Temporary raw pages live outside the published tree. Publication is an atomic
rename only after all three discovery connections and every page manifest
validate. No partial snapshot or queue is minted on a retrieval failure.

## 7. Independent stopping and all-or-nothing success

The queues are reviewed independently in repository order. Each repository
stops at the first of:

| Repository | Success stop | Failure stop |
| --- | --- | --- |
| GPyTorch | 2 new distinct `ADMIT_PENDING_REPRO` rows | Its complete frozen R3 union is exhausted before 2 |
| chaospy | 3 new distinct `ADMIT_PENDING_REPRO` rows | Its complete frozen R3 union is exhausted before 3 |
| SALib | 3 new distinct `ADMIT_PENDING_REPRO` rows | Its complete frozen R3 union is exhausted before 3 |

Items after a repository success stop remain in the snapshot and queue as
`NOT_REVIEWED_AFTER_STOP`; they have no decision and cannot substitute later.
All reviewed exclusions remain. The whole run succeeds only when all three
success stops are reached. If any repository reaches its failure stop, or any
command/check/test fails, the VM writes only a first-failure diagnostic and
command provenance, creates no partial candidate payload, performs no retry,
and stops.

## 8. A1/A3 admission and blind policy

Admission remains A1 plus A3 only:

- **A1 public real-fix evidence:** the captured item is an issue, the captured
  issue evidence identifies a same-repository public fix, `buggy_sha` and
  `fixed_sha` are distinct full lowercase 40-hex OIDs, the fixed commit's raw
  page and parents validate, and `public_fix_url` is the canonical public URL
  for `fixed_sha`. A missing or ambiguous linkage fails A1.
- **A3 numerical scope:** the issue and fix evidence establish a wrong numeric
  value, numerical instability, convergence/precision/sensitivity error, or a
  numerical-kernel semantic fault within the repository restriction. The R2
  exclusion classes remain frozen: crash-only, build/packaging, API misuse,
  documentation, performance-only, test-infrastructure, and intended API
  redesign. Any applicable class fails A3.
- **A2 remains `PENDING`:** no reproducer, buggy/fixed-arm execution, readiness,
  MR assignment, mutation result, prediction, or downstream result is allowed.
- **Blind fields remain blank:** `analysis_id`, alias, operator, fiber, MR, kill,
  annotation, prediction, and result fields are absent or blank as contracted.

A decision is `ADMIT_PENDING_REPRO` if and only if A1 and A3 are `PASS`, A2 is
`PENDING`, no exclusion class applies, and all raw/hash bindings pass.

## 9. Five-layer binding contract

### 9.1 Snapshot

Each `ISSUE_SNAPSHOT.json` row contains:

```text
snapshot_record_id, repository, repository_order, issue_node_id,
issue_number, issue_url, state, created_at, updated_at, closed_at,
title_sha256, body_text_sha256, ordered_labels, matched_phrases,
match_surfaces, source_page_index, source_page_sha256,
discovery_query_sha256, discovery_variables_sha256,
discovery_page_manifest_sha256, node_index, snapshot_record_sha256
```

`snapshot_record_sha256` covers the canonical serialization of every preceding
field. The checker reconstructs phrase matching and ordering from raw pages.

### 9.2 Queue

Each `REVIEW_QUEUE.json` row copies every snapshot identity/hash field needed
for replay and adds only:

```text
neutral_id, union_order, repository_review_order, collision_status,
review_status
```

The checker independently reconstructs the complete queue, exact IDs, status
boundary, cardinality, and ordering. Missing, extra, duplicate, renumbered, or
reordered rows fail closed.

### 9.3 Decision

Each reviewed `REVIEW_DECISIONS.json` row copies the queue identity and adds:

```text
issue_page_manifest_sha256, fix_page_manifest_sha256,
buggy_sha, fixed_sha, public_issue_url, public_fix_url, mechanism,
exclusion_class, crit_real_public_fix, crit_in_numerical_scope,
crit_dual_arm_repro, decision, decision_reason, analysis_id
```

Decision order equals the reviewed queue prefix. `analysis_id` is blank and
`crit_dual_arm_repro` is `PENDING`. There is no decision for
`NOT_REVIEWED_AFTER_STOP`.

### 9.4 Sheet

`admission_sheet.cursor_candidate.csv` is mechanically derived from decisions
and binds:

```text
neutral_id, source_cohort, repository, issue_url, buggy_sha, fixed_sha,
mechanism, crit_real_public_fix, crit_dual_arm_repro,
crit_in_numerical_scope, decision, decision_reason, analysis_id
```

`source_cohort` is exactly `supplemental_r3`. Sheet order equals decision order;
there are no hand-edited values. This is not the canonical admission sheet.

### 9.5 Evidence and handoff

Every reviewed row has exactly one
`admission_evidence/{neutral_id}/evidence.json` copying the decision identity,
raw-page manifest hashes, A1/A3 fields, and decision. `EVIDENCE_SNAPSHOT.json`
is the ordered path/SHA-256 manifest. The checker requires one-to-one agreement
among decision, sheet, evidence, issue pages, fix pages, and manifests.

`HANDOFF_SUPPLEMENTAL_R3.json` binds the fixed design authority, contract/code/
test commits, R2 freeze comparison, every artifact hash/tree hash, exact counts,
per-repository stop reason, executed commands and exit codes, environment
versions, confirmations, and unresolved limitations. It must disclose that
readiness and canonical freeze did not run.

## 10. Batch 3 exclusion and R2 transport isolation

The future branch is created from the exact audited design authority carried
by the Local Desktop handoff. Before any file creation or network request, the
VM must prove:

- HEAD equals the authorized design authority and the worktree is clean;
- the fixed main is an ancestor;
- the Batch 3 SHA is not an ancestor;
- no remote ref, local branch, commit message, manifest, source artifact, or
  input identity other than the contract's single denylist field names the
  Batch 3 SHA; and
- no Batch 3 ref is fetched or opened to perform these checks.

The R3 root is append-only and disjoint from R2. The immutable R2 transport set
is exactly:

```text
data/external_slice/supplemental_r2/SCOPE.json
data/external_slice/supplemental_r2/TRANSPORT_CONTRACT.json
data/external_slice/supplemental_r2/QUOTAS.json
data/external_slice/supplemental_r2/ISSUE_SNAPSHOT.json
data/external_slice/supplemental_r2/COMMAND_LOG.json
data/external_slice/supplemental_r2/PUBLISH_COMMIT.json
data/external_slice/supplemental_r2/transport_pages/**
data/external_slice/supplemental_r2/failed_runs/**
```

Before the first R3 request and again immediately before payload commit, the
validator performs both comparisons:

1. a Git-object diff from R2 transport freeze commit
   `020b60fb83f7eb1d34f143458fca62beab5aa398` over the exact set above; and
2. a byte/tree manifest comparison against the accepted main copies.

Both comparisons must be empty/equal. No R2 raw page may be copied, relabeled,
or rehashed into R3 membership. A mismatch stops the run without retry or
candidate payload.

## 11. RED -> GREEN and guard-isolated test matrix

No production R3 code or live request precedes the tests. Each row begins RED
against absent/minimal code, then becomes GREEN with the smallest implementation.
Every negative asserts nonzero exit, first violated invariant, and absence of a
new snapshot/candidate payload.

| Test family | RED mutations | GREEN invariant |
| --- | --- | --- |
| Contract precedence | request timestamp before/equal contract commit, changed query/phrase/repository/cutoff | Contract commit strictly predates all requests and bytes replay. |
| GraphQL issue type | `PullRequest`, `/pull/`, open state, null close time, GraphQL error | Only complete closed `Issue` nodes enter raw snapshot. |
| Pagination | missing/duplicate/reordered page, cursor drift, changed total, incomplete labels | Full connection and exact ordered page manifest replay. |
| Hashes | one-byte query, variables, response, or manifest mutation | All SHA-256 values recompute exactly. |
| Membership | false phrase match, post-cutoff issue, wrong repo, manual URL, R2 collision | Frozen local matcher alone reconstructs the queue. |
| Deduplication | duplicate URL/node/number/fix SHA, cross-quota issue/fix reuse | One canonical row and one repository quota per issue/fix. |
| Stops | review after success, substitution after exclusion, cross-repo fill | Independent 2/3/3 stops and no replacement. |
| A1/A3 | short SHA, unrelated fix, cross-repo fix, missing raw link, exclusion misclassified | Exact A1/A3 biconditional and A2 `PENDING`. |
| Five layers | mutate each copied field separately, missing/extra/reordered row | Snapshot -> queue -> decision -> sheet -> evidence is exact. |
| R2 freeze | mutate one frozen byte or add/remove a transport path | Git-object and byte/tree comparisons both remain equal. |
| Batch 3 | make denylisted SHA an ancestor or inject its identity outside the sole denylist field | Lineage/input scan fails before retrieval. |
| Atomicity | fail each required command/check/test | Diagnostic only; no partial candidate payload and no retry. |
| Payload/handoff | stale hash, non-direct parent, self-resolution drift | Handoff is the sole direct child of payload. |

### 11.1 Filename-token boundary matrix

The repo-wide new/changed-path guard treats ASCII letters/digits as token
characters and `_`, `-`, `.`, path separators, and string boundaries as token
delimiters. It rejects these independent filename tokens at every position:

| Token | Bare | Prefix | Suffix | Infix |
| --- | --- | --- | --- | --- |
| `readiness` | `readiness.json` | `readiness_batch.json` | `batch_readiness.json` | `batch_readiness_report.json` |
| `freeze` | `freeze.json` | `freeze_batch.json` | `batch_freeze.json` | `batch_freeze_report.json` |
| `canonical_freeze` | `canonical_freeze.json` | `canonical_freeze_batch.json` | `batch_canonical_freeze.json` | `batch_canonical_freeze_report.json` |

The hyphen spelling `canonical-freeze` is tested identically. Larger lexical
tokens such as `prefreeze.json`, `freezeout.json`, `prereadiness.json`, and
`readinessout.json` must not be false positives.

For each rejected filename, a guard-isolated test uses the same attack bytes
in both phases: the fully sealed bundle passes before injection, fails after
the new sibling path is injected and unrelated hashes are resealed, then passes
only when the path guard alone is replaced with a no-hit test double in the
producer, admission checker, and handoff checker. This proves the guard, rather
than an incidental hash mismatch, caused rejection. Non-token cases remain
GREEN with the real guard.

## 12. Future commit and handoff structure

The future Cursor VM may create preparatory contract and test/code commits,
but the successful scientific handoff ends with exactly two terminal commits:

1. **Payload commit:** contains the complete R3 transport, snapshot, queue,
   decisions, candidate sheet, evidence tree, verification log, and the code/
   tests that validate them; it does not contain the handoff file.
2. **Handoff commit:** the sole direct child of the payload commit, containing
   only `HANDOFF_SUPPLEMENTAL_R3.json` and any handoff hash manifest explicitly
   frozen by the contract. Its self identity uses the existing `SELF`
   resolution convention.

No commit follows the handoff in that execution. The branch is pushed once and
the VM stops. No PR is created, no merge is performed, and no readiness or
canonical freeze branch is created.

The current Local Desktop design uses the separately required two commits:
plan first, local audit second, with the audit commit's direct parent equal to
the plan commit.

## 13. Single Cursor VM instruction draft

This draft becomes usable only after the Local Desktop audit records
`R3_UNBLOCK_DESIGN_FEASIBLE` or
`R3_UNBLOCK_DESIGN_FEASIBLE_WITH_CONDITIONS` and a later user instruction
supplies the immutable pushed design authority.

> Start one fresh Cursor VM from the immutable audited design authority. Verify
> identity, clean state, main ancestry, Batch 3 exclusion, and R2 byte/tree
> identity before creating anything. Freeze and commit the complete
> `SUPPLEMENTAL_R3_EVIDENCE` contract before any network request. Write the
> negative tests first and obtain RED, implement the minimum miner/checkers and
> obtain GREEN, then perform exactly one complete three-repository retrieval.
> Review only the replayable frozen queue and captured raw issue/fix pages in
> order. Stop each repository at its fixed success or exhaustion rule; retain
> exclusions; keep A2 `PENDING` and aliases/`analysis_id` blank. On the first
> failure, identity mismatch, insufficient repository yield, or ambiguous
> evidence, write only first-failure provenance, create no partial candidate
> payload, do not retry, push no success handoff, and stop. On all-three success,
> run the full frozen matrix once, create the terminal payload then direct-child
> handoff commits, push once, and stop without PR, merge, readiness, r8, or
> canonical freeze.

The VM may not split retrieval across sessions, resume a failed run, repair an
artifact after a failed gate, or use a second VM to complete missing evidence.

## 14. Formal verdict and conditions

**Verdict: `R3_UNBLOCK_DESIGN_FEASIBLE_WITH_CONDITIONS`.**

The design is legally coherent because Route B separates a precommitted,
replayable successor from immutable R2 and preserves the distribution and
blind policies. The conditions are substantive:

1. a new contract commit and independent Local Desktop gate must precede the
   first network request;
2. the later VM must prove Batch 3 exclusion and R2 byte/tree identity;
3. all discovery and A1 evidence must be replayable from frozen raw responses;
4. the run must independently produce 2/3/3 new, nonduplicated candidates;
5. all A2 values remain `PENDING`, and aliases/`analysis_id` remain blank;
6. every RED -> GREEN, guard-isolated, binding, freeze, and atomicity test must
   pass without retry; and
7. success ends at the payload/handoff branch push, before readiness.

If any condition fails, the only lawful execution verdict is
`R3_UNBLOCK_DESIGN_BLOCKED`. This plan does not predict that the candidate
yield condition will be met.
