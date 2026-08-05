# Supplemental R3 Evidence Contract Freeze: Local Desktop Audit

**Scope:** pre-network contract creation only.

**Verdict:** `R3_CONTRACT_FREEZE_READY_FOR_SEPARATE_EXECUTION`, subject to the
static checks and full-suite result recorded below. This audit does not
authorize issue retrieval, evidence acquisition, admission, readiness, r8,
canonical freeze, or Cursor VM creation.

## Identity gate

| Check | Required value | Result |
| --- | --- | --- |
| Remote design branch | `b1981a0432d735de5a2a3892db514620e1376729` | PASS |
| Contract-freeze baseline | `b1981a0432d735de5a2a3892db514620e1376729` | PASS |
| Baseline direct parent | `4f40da2bb77d766aadec90e9a6c8c21a0cd26c49` | PASS |
| Design-plan direct parent | `3c518b8467f74c9a6efd11f2db267f9f30e1c822` | PASS |
| Contract-freeze worktree | `/tmp/P3-SemanticMutation-r3-contract-freeze` | PASS |
| Worktree branch and initial state | `codex/phase3-supplemental-r3-contract-freeze`, clean | PASS |

The Batch 3 denylisted head SHA
`f6f1888f361a524a481cc9505e567a8bc414b9ea` appears only in the explicit
denylist fields and this audit explanation. It was not fetched, opened,
inspected, merged, cherry-picked, or used as a source of payload, IDs, hashes,
paths, files, or lineage.

## Frozen contract

The contract files are independent UTF-8 query/JSON artifacts and are bound by
`CONTRACT_MANIFEST.json` before any evidence request:

| Artifact | SHA-256 |
| --- | --- |
| `SCOPE.json` | `67d16148e1055ca9a96302ff737e7443ecf23bb1683badc1c1a13c49f99db0f1` |
| `TRANSPORT_CONTRACT.json` | `42188051bb12032037949a0052bb9f0b429a882a8dfd38a3d4074efcc7d5e107` |
| `QUOTAS.json` | `50742a93aca5d269d84303c82393e47de85746d6ba58bf079b27678d66574bb2` |
| `COLLISION_UNIVERSE.json` | `7633db6fb1a19f5a815e2870a6f112be0cc1be7903d26fe658df4b549a332d3a` |
| `queries/discovery.graphql` | `80d1287f692c2b42f326ef364ddffe5ce44f3dd81fa1c03444d83e6ebb2996c6` |
| `queries/issue_evidence.graphql` | `c9c6f583325b5530072f5df5779fae20e04974c62265305956421e75ad6bb862` |
| `queries/fix_evidence.graphql` | `033173f0675b3bdbe69fa9911e2169557c2001e3f6c02541f4c699c6f16435eb` |
| `CONTRACT_MANIFEST.json` | `4c570326c65f4b45cebc9ea73c5485826dcf0c3d21d43d254dae3fb64e38620e` |

The frozen scope is exactly `SUPPLEMENTAL_R3_EVIDENCE` with repositories in
the order GPyTorch, chaospy, SALib; cutoff
`2026-08-05T07:31:15Z`; `known_issue_urls=[]`; fixed quotas 2/3/3;
`replacement_policy=forbidden`; no issue/node/URL/fix/issue-fix reuse; A2
`PENDING`; and blank `analysis_id`/alias fields. Discovery continues the
issue-typed GraphQL `Repository.issues` operation, while issue and fix evidence
use the separately frozen operations and query bytes. Page sizes, selected
fields, timeline item types, variables, cursor advancement, raw-byte hashes,
manifest hashes, and hard-failure behavior are explicit in
`TRANSPORT_CONTRACT.json`.

## Collision and transport boundaries

`COLLISION_UNIVERSE.json` binds the complete SHA-256 values of the fixed-main
R2 review queue and canonical admission sheet, plus every collision URL, issue
node ID, issue number, and known fix SHA derived from those two files. No
collision data came from Batch 3 or the prior dirty workspace.

The R2 transport baseline is commit
`020b60fb83f7eb1d34f143458fca62beab5aa398`, with every required path recorded
in both the transport contract and manifest. The R3 root is disjoint and no R2
transport file is rewritten, copied, relabeled, or rehashed into R3
membership.

## Zero-network confirmation

The manifest records zero evidence requests: zero GitHub issue requests, zero
GraphQL requests, zero REST requests, zero browser requests, and no manual
membership search. Git fetch/branch operations were limited to fixed Git
lineage and are not evidence acquisition. No transport page, issue page, fix
page, snapshot, queue, decision, sheet, evidence, miner/checker, test,
command-log, payload, handoff, readiness, r8, or canonical-freeze artifact was
created.

## Legacy R2 guard compatibility

The mandated audit filename contains the independent token `freeze`. The
existing R2 repo-wide path guard therefore rejected the otherwise valid R2
positive fixtures while this new audit was present. The authorized recovery
adds one exact-path governance allowlist entry to each of the three deliberately
independent R2 guard implementations and one regression test. The regression
test proves the required audit path is classified as governance documentation
while an `_audit_copy.md` near miss remains forbidden. No wildcard, directory,
or general `freeze` token exemption was added.

This compatibility repair modifies only:

- `scripts/external_slice/mine_supplemental_r2.py`;
- `scripts/external_slice/check_supplemental_r2_admission.py`;
- `scripts/external_slice/check_supplemental_r2_handoff_hashes.py`; and
- `tests/external_slice/test_check_supplemental_r2_admission.py`.

It does not modify the R2 transport freeze set or any R2 scientific artifact.

## Required static gate record

The following commands are the only gates for this pre-network contract:

1. `python3 -m json.tool` succeeds for all five JSON contract files;
2. the exact R2 transport path set has an empty Git diff against the frozen
   transport baseline;
3. the repository full suite exits zero;
4. `git diff --check` exits zero; and
5. final status contains only the nine allowed new paths before staging.

Any failed gate changes the result to `R3_CONTRACT_FREEZE_BLOCKED`; no retry,
repair, evidence request, or partial payload is permitted.
