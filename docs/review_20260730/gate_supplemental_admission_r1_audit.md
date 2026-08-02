# Gate SUPPLEMENTAL_ADMISSION_R1 — Supplemental Mining R1 Audit

- **Audit time:** `2026-08-02T09:55:39+08:00`
- **Cursor branch:** `origin/cursor/grok-phase3-supplemental-mining-r1`
- **Cursor lineage:** baseline `0e208929ec4b6fc6ef8e49f6312c489be7ed4f8a` → scope `e108b82d38e53d89991960266385edf62da9eefc` → payload `a1cc795f340c38b340550c6789ece72a00c4c316` → handoff `ac887e8a4a980dafca31c9ee803ec971a57698bc`
- **Draft PR:** #5, with head equal to the handoff commit
- **Verdict:** `BLOCKED`
- **Integration:** none; the three Cursor commits are not cherry-picked
- **Successor state:** supplemental readiness, A2 promotion, canonical admission freeze, C4, labelling, prediction, and detection remain locked

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
