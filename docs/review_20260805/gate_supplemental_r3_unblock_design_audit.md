# Supplemental R3 Unblock Governance Design: Local Desktop Audit

**Verdict: `R3_UNBLOCK_DESIGN_FEASIBLE_WITH_CONDITIONS`.** The append-only
successor design is internally complete and preserves the frozen scientific
and transport boundaries. Existing evidence does not establish that eight
qualifying candidates exist, so the verdict is conditional and does not
authorize R3 retrieval, admission, readiness, or canonical freeze.

## Fixed identity gate

The Local Desktop gate ran the four prescribed GitHub checks once, in order,
without correction or retry.

| Identity | Observed and required value | Result |
| --- | --- | --- |
| Active GitHub account | `meng004` | PASS |
| Remote main | `3c518b8467f74c9a6efd11f2db267f9f30e1c822` | PASS |
| PR #7 | merged to `main`; head `8d3db94a18e026cb17a6319d88a3c5960df5c406`; merge `3c518b8467f74c9a6efd11f2db267f9f30e1c822` | PASS |
| CI run | `30985348887`, `completed/success`, head equals main | PASS |
| CI job | `92238715535`, `completed/success` | PASS |

The accepted R2 payload remains
`7d27f287601b45f895749fb507eaff72d746a4de`; the audit merge identity is
`be017d25d125cfd72aca48995dcdf616f7d55829`. PR #6 Batch 3 head
`f6f1888f361a524a481cc9505e567a8bc414b9ea` remains explicitly excluded.

## Worktree gate

The design worktree was created from the fixed main SHA on branch
`codex/phase3-supplemental-r3-unblock-design` at
`/tmp/P3-SemanticMutation-r3-unblock-design`. Initial `HEAD` matched main and
`git status --short --branch` reported only the exact branch line, proving the
worktree was clean before design work.

## Frozen evidence audit

| Required fact | Evidence inspected | Result |
| --- | --- | --- |
| 67 decisions / 9 admitted / 58 excluded | R2 decisions and handoff totals | PASS |
| All A2 `PENDING` | R2 handoff confirmation and decision fields | PASS |
| All aliases/`analysis_id` blank | R2 handoff confirmation and decision fields | PASS |
| GPyTorch has one counted admission | `EXT-gpytorch-03` is the only `ADMIT_PENDING_REPRO` row | PASS |
| Four remaining GPyTorch rows have frozen exclusions | `-01` no public fix; `-02`/`-04` API redesign; `-05` crash-only | PASS |
| chaospy has one conditional lead only | `EXT-chaospy-01` lacks identifiable merged public-fix evidence; `-02` is API redesign | PASS |
| SALib queue size is zero | R2 queue repository counts omit SALib | PASS |
| Existing evidence cannot cover 2/3/3 | R2 handoff shortfalls are GPyTorch 2, chaospy 3, SALib 3 | PASS |
| Risk disclosure retained | `DISTRIBUTION_TARGET_AT_RISK` | PASS |
| Batch 3 excluded | Accepted R2 local audit explicitly excludes PR #6 head | PASS |

The evidence-strength ruling is deliberately narrow: the present files support
the need for eight new, distinct, repository-specific records. They do not
support a claim that those records can actually be found. No R2 excluded row,
including `EXT-chaospy-01`, is promoted or rewritten by the design.

## Route ruling

- Route A is lawful but permanently leaves `R3_BLOCKED`; it cannot recover the
  shortfall from the frozen R2 universe.
- Route B is accepted conditionally. Its append-only contract freezes the
  repositories, GraphQL `Repository.issues` transport, expanded phrases,
  replayable raw issue/fix pages, hashes, deduplication, 2/3/3 stop rules,
  A1/A3 gates, blind fields, five-layer bindings, Batch 3 exclusion, R2
  transport freeze, and payload/handoff ancestry before acquisition.
- Route C is rejected because quota or cross-repository substitution changes
  the frozen distribution target and replacement policy. It requires a new
  scientific protocol amendment and a separate governance audit.

## Design completeness checks

| Required design item | Audit result |
| --- | --- |
| Legal boundary for a new evidence protocol | Complete |
| Decision to retain GitHub GraphQL `Repository.issues` | Complete |
| Exact repository, cutoff, phrase, normalization, and membership changes | Complete |
| New R3 transport isolated from byte-identical R2 transport | Complete |
| Raw response and issue-page formats | Complete |
| Query, variables, response, and page-manifest SHA-256 | Complete |
| Deduplication and no issue/fix multi-quota reuse | Complete |
| Independent GPyTorch/chaospy/SALib stopping rules | Complete |
| A1/A3 admission with A2 `PENDING` and blank `analysis_id` | Complete |
| Snapshot -> queue -> decision -> sheet -> evidence contract | Complete |
| PR #6 Batch 3 exclusion | Complete |
| R2 transport freeze Git-object plus byte/tree comparison | Complete |
| RED -> GREEN and guard-isolated matrix | Complete |
| Filename tokens at bare/prefix/suffix/infix positions, with `prefreeze`/`freezeout` nonmatches | Complete |
| Terminal payload and direct-child handoff commits | Complete |
| Single Cursor VM run and first-failure/no-retry stop | Complete |

## Scope audit

This design adds only:

- `docs/superpowers/plans/2026-08-05-supplemental-r3-unblock-governance.md`;
- `docs/review_20260805/gate_supplemental_r3_unblock_design_audit.md`.

It does not create or modify `supplemental_r3` data, miner/checker production
code, tests, R2 artifacts, the canonical admission sheet, readiness,
reproduction, annotation, prediction, results, `FREEZE.sha256`, r8, a handoff,
or canonical freeze. The design contains a conditional Cursor VM instruction
draft only because the formal verdict is one of the two verdicts that permits
such a draft.

## Conditions carried forward

The future execution remains blocked until a separate instruction supplies the
immutable audited design authority and authorizes one fresh Cursor VM. That run
must freeze its contract before networking, remain free of Batch 3 lineage,
preserve R2 transport freeze, capture replayable raw evidence, meet all three
repository stops without duplicate reuse, pass the full test matrix once, and
stop after the payload/handoff push. Any failure, ambiguity, insufficient
repository yield, or identity mismatch changes the execution verdict to
`R3_UNBLOCK_DESIGN_BLOCKED` and permits neither retry nor partial candidate
payload.
