# Gate SUPPLEMENTAL_ADMISSION_R1 — Supplemental Mining R1 Audit

- **Audit time:** `2026-08-02T09:55:39+08:00`
- **Cursor branch:** `origin/cursor/grok-phase3-supplemental-mining-r1`
- **Cursor lineage:** baseline `0e208929ec4b6fc6ef8e49f6312c489be7ed4f8a` → scope `e108b82d38e53d89991960266385edf62da9eefc` → payload `a1cc795f340c38b340550c6789ece72a00c4c316` → handoff `ac887e8a4a980dafca31c9ee803ec971a57698bc`
- **Draft PR:** #5, with head equal to the handoff commit
- **Verdict:** `BLOCKED`
- **Integration:** none; the three Cursor commits are not cherry-picked
- **Successor state:** supplemental readiness, A2 promotion, canonical admission freeze, C4, labelling, prediction, and detection remain locked
- **R3 re-audit:** handoff `e6110b104e3271dc31c74c6346eff808e0239048`; current verdict remains `BLOCKED`

## 1. Independent verification

The three Cursor commits are consecutive direct descendants of the audited baseline. The handoff manifest SHA256 is `4a57cb082203de0e79105e248e00e07b89d6762aa305dbc95871d5a91f8b3aab`.

Independent replay produced:

| Check | Result |
|---|---|
| Supplemental structural checker | exit 0; 56 reviewed rows, 12 proposed pending, 44 excluded |
| Handoff hash checker | exit 0; `HASH_CHECK_OK`, 8 files, 1 tree, 56 evidence records |
| Targeted tests | `18 passed` |
| Full tests | `278 passed, 10 warnings` |
| Reserved-term scan | raw `rg` exit 1, no output |
| Token scan | raw `rg` exit 1, no output |
| Prohibited-data scan | raw `rg` exit 1, no output |
| Immutable baseline/downstream paths | unchanged relative to baseline |
| Candidate A2 and aliases | 56/56 `PENDING`; 56/56 blank `analysis_id` |

These checks establish byte integrity and internal consistency of the submitted payload. They do not establish that its membership was selected by the frozen search rule.

## 2. Findings

### `SUPP-R1-SEARCH-SEMANTICS-001` — BLOCKER

The frozen plan requires 66 GitHub queries containing `is:issue is:closed` and requires neutral IDs to be allocated from the deduplicated union of those issue results. The committed search snapshot instead contains 262 returned items, all 262 marked as pull requests and zero marked as issues. The miner then applies an unregistered “pilot-compatible” PR→issue resolver in `scripts/external_slice/mine_supplemental_r1.py:508` and constructs the queue from issues referenced by those PRs.

The resulting queue contains 128 linked issues, including 21 with `state=open` and ten open issues among reviewed rows. Therefore it is not the frozen closed-issue search union. The exact first frozen command was independently replayed on 2026-08-02 and returned 20 issues and zero PRs. Consequently the queue membership, ID allocation/order, 56 reviews, and 12 proposed pending rows are not admissible outputs of the preregistered rule.

### `SUPP-R1-QUEUE-BINDING-001` — BLOCKER

The implementation cannot prove strict queue membership and order:

- `validate-decisions` checks only that a decision's neutral ID exists in the queue; it does not compare the decision's repository, issue URL/number, or review order to that queue record.
- An incorrect `review_order` reaches an explicit no-op at `mine_supplemental_r1.py:948`.
- The dedicated admission checker has no review-queue argument and checks the search snapshot only for allowed repository and phrase values.

A reordered or mismatched decision set can therefore pass while retaining matching hashes in mechanically rebuilt evidence. This violates the promised search→queue→decision→sheet→evidence binding.

### `SUPP-R1-HANDOFF-DISCLOSURE-001` — HIGH

The immutable handoff must list all unresolved findings. Its `unresolved_findings` records only repository exhaustion/quota outcomes; it omits that all 262 hits were PRs, that the PR→issue path was introduced, and that derived open issues entered an `is:closed` queue. The later chat disclosure is useful but cannot amend the pinned handoff artifact.

### `SUPP-R1-CODE-QUALITY-001` — NON-BLOCKING

Standards review identified a dead `for ... pass` loop at miner lines 813–815, duplicated decision sorting/repo assignment at lines 1010–1046, repeated small JSON/hash helpers, and a large multi-responsibility miner. These should be cleaned during correction where local, but they do not independently determine the gate verdict. The `cursor/...` branch differs from the public-contributor naming in `CONTRIBUTING.md`; the frozen internal execution plan explicitly required this branch, so no rename is required.

## 3. Standards axis

One documented branch-naming discrepancy and four judgement-call smells were reported. The branch name is retained because it is explicitly fixed by the internal plan. The only correctness-relevant smell is the no-op `review_order` validation, promoted above to `SUPP-R1-QUEUE-BINDING-001` because it directly violates the specification.

## 4. Spec axis

Spec review found two blockers and one high-severity omission: the frozen issue-only universe was replaced by an unapproved PR-derived universe; the checker does not bind decisions to queue identity/order; and the handoff omits the material semantic divergence. The spec axis therefore fails.

## 5. Correction contract

Correction must remain on the same Cursor branch and start from `ac887e8a4a980dafca31c9ee803ec971a57698bc`. It must not reuse any of the 128 derived queue memberships or the 56 existing adjudications.

1. Remove the PR→issue search fallback. Treat any returned PR, non-closed item, incomplete result, missing query, changed query text, or nonzero request as a hard search failure.
2. Rerun all 66 exact frozen queries in a fresh Cursor VM/session. Persist their direct issue results only; deduplicate, order, and allocate IDs anew from that issue union.
3. Recollect public A1/A3 evidence and readjudicate strictly from the new queue. Keep every reviewed exclusion and leave every A2 value `PENDING`.
4. Extend tests with negative cases for PR search items, open items, missing/duplicate queries, altered query text/options, decision/queue URL mismatch, repository mismatch, issue-number mismatch, swapped order, skipped queue heads, and decisions beyond the stop boundary.
5. Bind the dedicated checker to `REVIEW_QUEUE.json` and require exact hashes and field equality along the full scope→search→queue→decision→sheet→evidence chain.
6. Regenerate all supplemental payload artifacts, verification log, and a new handoff manifest. The handoff must disclose this blocked lineage and explicitly close all three findings above.
7. Commit correction payload and correction handoff separately, push, and stop for `SUPPLEMENTAL_ADMISSION_R1-r2` local review. Do not begin dual-arm readiness.

## 6. Decision

PR #5 remains open but unaccepted. The twelve proposed rows are not approved candidates and must not enter readiness. Only the correction task in §5 is unlocked.

## 7. R2 correction re-audit

### 7.1 Intake and verification

R2 lineage is consecutive and remotely pinned:

```text
ac887e8a4a980dafca31c9ee803ec971a57698bc
  -> bc3a4e30f57f38f728b4f3971c05c07e6285f643  correction payload
  -> e007042074956e6c57a089cfed1ecc404b5723a4  correction handoff
```

Draft PR #5 and `origin/cursor/grok-phase3-supplemental-mining-r1` both point to
the correction handoff. Independent verification produced:

| Check | Result |
|---|---|
| Handoff hash checker | `HASH_CHECK_OK`; six files, zero trees/evidence |
| Withdrawal equality | old 56 `(neutral_id, decision)` pairs and R2 withdrawal pairs have identical canonical SHA256 `878d6851...` |
| Withdrawn artifacts | old snapshot, queue, decisions, sheet, evidence snapshot/tree all absent |
| Targeted tests | `22 passed` |
| Full R2 tests | `282 passed, 10 warnings` |
| Compileall | exit 0 |
| Token scan | raw `rg` exit 1, no output |
| Immutable admission/readiness/downstream paths | exit 0; unchanged from `0e208929...` |
| Diff whitespace | exit 0 |

The PR→issue fallback is removed and the official miner hard-fails on the first
PR-typed response. The previous 128 queue rows, 56 decisions, 12 pending IDs,
and 44 exclusions are withdrawn without substitution. No new candidate or
downstream artifact exists.

### 7.2 R2 findings

#### `SUPP-R1-R2-FULL-BINDING-001` — BLOCKER

`SUPP-R1-QUEUE-BINDING-001` is only partially fixed. The checker verifies query
identity and header hashes, but it does not reconstruct the deduplicated ordered
queue from `SEARCH_SNAPSHOT.json`. It also does not require complete field
equality between sheet, decision, and evidence records.

Two independent negative probes against `e0070420` both exited 0:

1. The snapshot retained issue 1 while queue, decision, sheet, and evidence were
   consistently replaced with issue 999. The checker printed `PASS`.
2. Only the sheet `fixed_sha` was changed while the decision and evidence kept
   the original SHA. The checker again printed `PASS`.

Therefore the claimed exact
scope→search→queue→decision→sheet→evidence binding is not established. The
committed tests cover several queue/decision mismatches, but do not cover
queue-vs-snapshot membership/order or general sheet/decision/evidence field
divergence.

#### `SUPP-R1-R2-DIAGNOSTIC-PROVENANCE-001` — HIGH

`SEARCH_DIAGNOSTIC_R2.json` lists 66 exact query strings and aggregate counts of
0 issues / 262 PRs, but `COMMAND_LOG.json` contains only the first official
`gh api` request. The diagnostic rows contain neither returned identifiers nor
response hashes, timestamps, or per-query command provenance. The critical
wrapper command that produced official exit 2 is also absent from the command
and verification logs.

The “fresh 66-query diagnostic” claim is therefore `insufficient`, not a cleared
result. Local Desktop replay of the exact first query on 2026-08-02 returned 20
issue objects and zero PRs. This does not negate the recorded Cursor VM hard
failure, but requires the claim to be scoped to that VM and prevents a broad
claim that no admissible GitHub issue union exists.

#### `SUPP-R1-R2-STYLE-001` — LOW / NON-BLOCKING

Standards review found four changed Python lines over the documented 100-column
limit and a judgement-call duplication risk because query/stop policies are
implemented independently in miner and checker. The independent checker may
intentionally duplicate policy; if so, equivalence tests should make that
choice explicit.

### 7.3 Finding disposition

| Original finding | R2 disposition |
|---|---|
| `SUPP-R1-SEARCH-SEMANTICS-001` | `CLOSED`: fallback removed; hard fail implemented; invalid set withdrawn |
| `SUPP-R1-HANDOFF-DISCLOSURE-001` | `CLOSED`: blocked lineage and withdrawal are disclosed |
| `SUPP-R1-QUEUE-BINDING-001` | `OPEN/PARTIAL`: promoted to `SUPP-R1-R2-FULL-BINDING-001` |

### 7.4 R3 correction contract

Use a new Cursor VM/session without `rtk`, on the same branch starting from
`e007042074956e6c57a089cfed1ecc404b5723a4`.

1. Reconstruct the expected queue mechanically from snapshot direct issue
   items using the frozen deduplication, ordering, neutral-ID, and phrase
   provenance rules. Require exact record equality with `REVIEW_QUEUE.json`.
2. Require exact equality for all duplicated fields across queue, decision,
   sheet, and evidence: ID, repository, issue number/URL, fix URL, buggy/fixed
   SHAs, mechanism, A1/A2/A3, verdict, exclusion reason, alias, rationales, and
   evidence URLs. Hash equality alone is not field binding.
3. Add regression tests that reproduce both exit-0 escapes above. Also add
   explicit missing-query, duplicate-query, queue-vs-snapshot membership/order,
   and every cross-artifact field-mismatch negative test.
4. Either remove the 66-query diagnostic claim or generate it with a committed
   diagnostic command that logs all 66 exact commands, exits, timestamps, and
   response hashes/identifiers. Scope any anomalous response claim to the exact
   Cursor VM environment; record the official wrapper command and exit 2.
5. Retain the withdrawal and artifact absences. Do not restore or reuse any R1
   candidate membership and do not start readiness.
6. Commit a correction payload and direct-child handoff separately, push, and
   stop for `SUPPLEMENTAL_ADMISSION_R1-r3`.

### 7.5 R2 decision

R2 remains `BLOCKED`. The safe withdrawal is verified, but the correction
payload/handoff are not integrated because the central full-binding claim is
false and the 66-query diagnostic claim is not command-auditable. Only the R3
correction contract above is unlocked.

## 8. R3 correction re-audit

### 8.1 Intake and verification

R3 lineage is consecutive and remotely pinned:

```text
e007042074956e6c57a089cfed1ecc404b5723a4
  -> 72a11bc0bf39c9d667bbaab9aa198b85c48c13af  correction payload
  -> e6110b104e3271dc31c74c6346eff808e0239048  correction handoff
```

Draft PR #5 and the remote Cursor branch both point to the handoff. Independent
verification produced:

| Check | Result |
|---|---|
| Handoff hash checker | `HASH_CHECK_OK`; six files, zero trees/evidence |
| Two R2 exit-0 probes | both now exit 1 with the expected binding error |
| Withdrawal equality | canonical `(neutral_id, decision)` SHA256 remains `878d6851...` |
| Inadmissible artifacts | old candidate/search/queue/decision/evidence and R2 diagnostic all absent |
| Targeted tests | `33 passed` |
| Full R3 tests | `293 passed, 10 warnings` |
| Compileall | exit 0 |
| Token scan | raw `rg` exit 1, no output |
| Immutable admission/readiness/downstream paths | exit 0; unchanged |
| Diff whitespace | exit 0 |

R3 deletes the unauditable 66-query diagnostic claim, retains a scoped Cursor
VM first-query hard failure with exact wrapper command/exit provenance, and
keeps the full withdrawal. No candidate or readiness artifact is restored.

### 8.2 R3 findings

#### `SUPP-R1-R3-PHRASE-PROVENANCE-001` — BLOCKER

The checker reconstructs queue records from snapshot items, but uses
`cloned.setdefault("phrase", query.get("phrase"))`. This preserves an arbitrary
item-level phrase instead of deriving or validating it against the enclosing
frozen query. Snapshot validation checks the query identity but never checks
`item.phrase == query.phrase`.

An independent negative probe changed the sole snapshot item's phrase to
`"tampered phrase"`, rebuilt the queue and hashes through the R3 helper, and
left all scientific fields otherwise valid. The checker exited 0 and printed:

```text
PASS: supplemental mining R1 admission structural check (full binding)
```

Thus queue phrase provenance is still trusted rather than bound to the frozen
query. This directly violates R3 contract §7.4(1), so
`SUPP-R1-R2-FULL-BINDING-001` remains `OPEN/PARTIAL`.

#### `SUPP-R1-R3-NEGATIVE-COVERAGE-001` — MEDIUM / NON-BLOCKING

R3 adds the two required escape regressions plus missing/duplicate query,
queue-order, fixed-SHA, mechanism, rationale, fix-URL, exclusion, and alias
negatives. It does not add explicit tests for every promised cross-artifact
field mismatch, including evidence neutral ID/issue URL, sheet repository,
buggy SHA, verdict, the three criteria individually, evidence mechanism/SHAs,
and evidence URLs. Most bindings are present in code, but the R3 “every mismatch
negative” test requirement is only partial.

#### `SUPP-R1-R3-STYLE-001` — LOW / NON-BLOCKING

Standards review found no hard violation. It noted low-risk raw-dictionary data
clumps in the cross-artifact comparison helper and duplicated dynamic-module
loading in tests.

### 8.3 Finding disposition

| Finding | R3 disposition |
|---|---|
| `SUPP-R1-R2-DIAGNOSTIC-PROVENANCE-001` | `CLOSED`: claim/artifact withdrawn; scoped wrapper command and exit 2 logged |
| Two R2 concrete binding escapes | `CLOSED`: independent probes now exit 1 |
| `SUPP-R1-R2-FULL-BINDING-001` | `OPEN/PARTIAL`: phrase provenance escape remains |

### 8.4 R4 correction contract

Use a new Cursor VM/session without `rtk`, on the same branch starting from
`e6110b104e3271dc31c74c6346eff808e0239048`.

1. For every snapshot item, require item repository and phrase to equal the
   enclosing exact query, or derive those fields exclusively from the query.
   Reject an explicit mismatch rather than silently preserving it.
2. Add a regression reproducing the exact `"tampered phrase"` exit-0 probe and
   require nonzero exit. Add the remaining explicit field-mismatch negatives
   listed in `SUPP-R1-R3-NEGATIVE-COVERAGE-001`.
3. Preserve the now-correct queue reconstruction, full field comparisons,
   diagnostic withdrawal, wrapper provenance, old-set withdrawal, and all
   candidate/readiness absences.
4. Update the handoff to close the R3 phrase-provenance finding without making
   any new search or candidate claim.
5. Commit correction payload and direct-child handoff separately, push, and
   stop for `SUPPLEMENTAL_ADMISSION_R1-r4`. Do not start readiness.

### 8.5 R3 decision

R3 remains `BLOCKED`. The two R2 escape findings and diagnostic-provenance gap
are closed, but frozen phrase provenance can still pass with a tampered item.
The R3 payload/handoff are not integrated; only the R4 correction above is
unlocked.
