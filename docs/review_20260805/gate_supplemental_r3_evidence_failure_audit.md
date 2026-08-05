# Supplemental R3 Evidence Failure — Local Desktop Independent Audit

Date: 2026-08-05
Environment: ChatGPT Desktop local audit
Repository: `meng004/P3-Semantic-Mutation`
Audit branch: `codex/phase3-supplemental-r3-evidence-failure-audit`

## Verdict

**Failure-path audit: PASS.**
**Protocol verdict remains: `R3_UNBLOCK_DESIGN_BLOCKED`.**

The Cursor VM stopped at the frozen Phase 1 Batch 3 fetched-ref denylist gate.
The committed failure branch is a direct child of the authorized contract
audit, contains only the two required failure-provenance artifacts, contains no
R3 evidence payload, and has no pull request. This audit does not authorize a
retry, resume, evidence acquisition, readiness, r8, canonical freeze, or any
downstream mutation.

## Fixed identity results

| Identity | Expected | Independently observed | Result |
| --- | --- | --- | --- |
| Remote repository | `meng004/P3-Semantic-Mutation` | `meng004/P3-Semantic-Mutation` | PASS |
| Remote main | `3c518b8467f74c9a6efd11f2db267f9f30e1c822` | same | PASS |
| PR #7 head | `8d3db94a18e026cb17a6319d88a3c5960df5c406` | same | PASS |
| PR #7 merge | `3c518b8467f74c9a6efd11f2db267f9f30e1c822` | same | PASS |
| CI run/job | `30985348887 / 92238715535` | completed / success at fixed main | PASS |
| Contract audit | `0e85691391dd80228dcf1d584d68f2194a6077d0` | sole parent of failure commit | PASS |
| Cursor failure branch | `cursor/grok-phase3-supplemental-r3-evidence` | same | PASS |
| Cursor failure commit | `743f5552fd5912f2705f7f256dda0f5179393842` | remote ref and local HTTPS clone agree | PASS |

The fixed-main-to-failure first-parent increment is exactly:

1. `4f40da2bb77d766aadec90e9a6c8c21a0cd26c49`
2. `b1981a0432d735de5a2a3892db514620e1376729`
3. `951ab3a9f212e257aeab37bf7a7f147417dbc36b`
4. `0e07f7cf224d5be146fe3e22c61946244bc8b095`
5. `0e85691391dd80228dcf1d584d68f2194a6077d0`
6. `743f5552fd5912f2705f7f256dda0f5179393842`

The denylisted Batch 3 SHA
`f6f1888f361a524a481cc9505e567a8bc414b9ea` is absent from this ancestry.
The audit clone fetched only the Cursor failure branch over HTTPS. Its refs do
not name the Batch 3 SHA. This audit did not fetch, show, cat-file, checkout,
merge, or otherwise inspect Batch 3.

## Failure artifact matrix

| Artifact | Git status from contract parent | SHA-256 | Audit result |
| --- | --- | --- | --- |
| `data/external_slice/supplemental_r3/FIRST_FAILURE.json` | added | `160621cfd947770008805452a80b2724e619036cb2771ed9c29fc626bb943f00` | PASS |
| `data/external_slice/supplemental_r3/COMMAND_LOG.json` | added | `08eebe09a27ce442c316b36ff21223b3a65a46eb457f8a398b7feccaf822a234` | PASS |

No other path differs between the contract audit and the Cursor failure
commit. `git diff --check` passes.

## Failure record binding

The two JSON artifacts parse successfully and agree on:

- protocol `SUPPLEMENTAL_R3_EVIDENCE`;
- verdict `R3_UNBLOCK_DESIGN_BLOCKED`;
- stage `phase1_identity_clean_state_gate`;
- contract head `0e85691391dd80228dcf1d584d68f2194a6077d0`;
- failure class `batch3_denylist_present_in_fetched_refs`;
- hit ref
  `refs/remotes/origin/cursor/grok-phase3-c3-readiness-batch3`;
- raw exit code `1`;
- matching `stderr_sha256`;
- zero completed evidence requests;
- no retry;
- no partial payload; and
- no neutral ID, repository, successful page, or cursor.

`COMMAND_LOG.json` contains ten ordered Phase 1 entries. The first nine exit
successfully and the tenth, `batch3_not_in_fetched_refs`, exits `1`.
Exactly one Git fetch is recorded, limited to the authorized contract-freeze
ref. No GraphQL evidence, REST issue listing/search, browser membership, or
manual issue command appears in the provenance.

## Atomicity and frozen-boundary results

| Boundary | Evidence | Result |
| --- | --- | --- |
| Failure-only tree | Git object diff contains exactly the two JSON artifacts above | PASS |
| No raw discovery/evidence | No `transport_pages`, `issue_pages`, or `fix_pages` paths | PASS |
| No snapshot or review payload | No R3 snapshot, queue, decision, sheet, evidence manifest, payload, or handoff | PASS |
| No R3 implementation | No Supplemental R3 miner, checker, or test path | PASS |
| R2 transport freeze | Git diff over `supplemental_r2` and canonical admission sheet is empty | PASS |
| Batch 3 lineage exclusion | Denylisted SHA absent from fixed-main ancestry increment | PASS |
| A2 and aliases | No candidate/admission artifact exists to mutate these fields | PASS |
| Downstream freeze | No readiness, r8, canonical-freeze, or downstream output | PASS |
| Pull request | GitHub query for all states and the Cursor head returns `[]` | PASS |

The committed provenance reports all evidence-network counters as zero, and
the failure tree contains no acquired evidence. Git objects cannot independently
prove a client's exact number of push operations or provide a server-side
history of every absent client request. Accordingly, this audit confirms the
terminal remote state and the internally consistent required provenance; it
does not strengthen those two operational claims beyond the available source
records.

## Replayed checks

The independent audit replayed:

- local `gh` authentication and repository identity;
- remote main, PR #7, CI run/job, Cursor ref, commit, and parent identity;
- GitHub fixed-main comparison and PR lookup;
- fresh HTTPS single-branch clone at the failure commit;
- exact parent, first-parent lineage, and ref scans;
- exact changed-path and `git diff --check` checks;
- R2 frozen-path zero-diff check;
- SHA-256 calculation for both failure artifacts;
- JSON schema/value/cross-file invariant assertions; and
- complete Supplemental R3 path and implementation-path absence assertions.

All checks passed. No production test suite was run because the Cursor failure
commit contains no production code or test change and the frozen execution
stopped before implementation.

## Governance consequence

The Cursor stop is contract-compliant. It does not make Supplemental R3
evidence feasible and does not change the frozen 67/9/58 state, A2
`PENDING`, blank aliases, shortfall 2/3/3, or
`DISTRIBUTION_TARGET_AT_RISK`.

The failed execution may not be resumed or retried under the frozen contract.
Any later acquisition attempt requires a separately authorized protocol
amendment and a new Local Desktop governance audit that explicitly resolves the
fetched-ref denylist precondition without inspecting, importing, or depending
on Batch 3.
