# Supplemental R3 Ref-Isolation Amendment — Local Desktop Governance Audit

Date: 2026-08-06
Environment: ChatGPT Desktop local audit
Repository: `meng004/P3-Semantic-Mutation`
Branch: `codex/phase3-supplemental-r3-ref-isolation-amendment`
Protocol: `SUPPLEMENTAL_R3_EVIDENCE_AMENDMENT_01`

## Verdict

**`R3_REF_ISOLATION_AMENDMENT_FEASIBLE_WITH_CONDITIONS`**

The append-only amendment is internally consistent, replayable from raw bytes,
and limited to replacing global ref-inventory purity with execution-input
closure. It does not weaken Batch 3 ancestry, fetch-target, object-access,
active-input, payload-lineage, no-retry, quota, transport, or downstream
prohibitions. The original contracts and queries, R2 collision inputs, and
failure provenance remain byte-identical.

This verdict authorizes only a separately reviewed Cursor VM instruction bound
to the terminal audit commit. It does not authorize running Cursor, requesting
evidence, implementing the future gate, admitting candidates, or producing a
payload or handoff.

## Fixed identity review

| Identity | Required value | Independently observed | Result |
| --- | --- | --- | --- |
| Repository | `meng004/P3-Semantic-Mutation` | same | PASS |
| Remote main | `3c518b8467f74c9a6efd11f2db267f9f30e1c822` | same | PASS |
| PR #7 head | `8d3db94a18e026cb17a6319d88a3c5960df5c406` | same | PASS |
| PR #7 merge | `3c518b8467f74c9a6efd11f2db267f9f30e1c822` | same | PASS |
| Main CI run/job | `30985348887 / 92238715535` | completed/success at fixed main | PASS |
| Contract audit | `0e85691391dd80228dcf1d584d68f2194a6077d0` | fixed authority | PASS |
| Failed Cursor commit | `743f5552fd5912f2705f7f256dda0f5179393842` | fixed failure provenance | PASS |
| Failure audit | `641345ec4d06bd9735e972c997d5e32a4c7e22c3` | sole parent of design spec | PASS |
| Design spec | `e5bfb155fe3c2799da3bb51371db059153c68285` | sole parent is failure audit | PASS |
| Materialization | `b6bf1995b6acc4fc7b847697a90dd86c22238396` | sole parent is design spec | PASS |

The Batch 3 deny identity was loaded only from the frozen SCOPE field and
compared textually with the frozen contract-manifest copy. This audit did not
fetch, resolve, show, inspect, enumerate, delete, or otherwise use the Batch 3
object or ref as an execution input.

## Required linear authority chain

| Position | Commit resolution | Sole parent | Changed-path result |
| --- | --- | --- | --- |
| Design spec | `e5bfb155fe3c2799da3bb51371db059153c68285` | `641345ec4d06bd9735e972c997d5e32a4c7e22c3` | design spec only, previously audited |
| Materialization | `b6bf1995b6acc4fc7b847697a90dd86c22238396` | `e5bfb155fe3c2799da3bb51371db059153c68285` | exactly plan plus two Amendment JSON files |
| Local audit | `SELF` | materialization commit | this audit report only; verified after commit |

The materialization commit contains no merge and no unlisted file. A quiet Git
comparison proves no change to R2, the canonical admission sheet, original R3
contracts or queries, failure artifacts, scripts, or tests.

## Frozen artifact replay

### Original Supplemental R3 contracts and queries

| Artifact | SHA-256 | Result |
| --- | --- | --- |
| `SCOPE.json` | `67d16148e1055ca9a96302ff737e7443ecf23bb1683badc1c1a13c49f99db0f1` | PASS |
| `CONTRACT_MANIFEST.json` | `4c570326c65f4b45cebc9ea73c5485826dcf0c3d21d43d254dae3fb64e38620e` | PASS |
| `TRANSPORT_CONTRACT.json` | `42188051bb12032037949a0052bb9f0b429a882a8dfd38a3d4074efcc7d5e107` | PASS |
| `QUOTAS.json` | `50742a93aca5d269d84303c82393e47de85746d6ba58bf079b27678d66574bb2` | PASS |
| `COLLISION_UNIVERSE.json` | `7633db6fb1a19f5a815e2870a6f112be0cc1be7903d26fe658df4b549a332d3a` | PASS |
| `queries/discovery.graphql` | `80d1287f692c2b42f326ef364ddffe5ce44f3dd81fa1c03444d83e6ebb2996c6` | PASS |
| `queries/issue_evidence.graphql` | `c9c6f583325b5530072f5df5779fae20e04974c62265305956421e75ad6bb862` | PASS |
| `queries/fix_evidence.graphql` | `033173f0675b3bdbe69fa9911e2169557c2001e3f6c02541f4c699c6f16435eb` | PASS |

### Failure provenance and R2 collision inputs

| Artifact | SHA-256 | Result |
| --- | --- | --- |
| `FIRST_FAILURE.json` | `160621cfd947770008805452a80b2724e619036cb2771ed9c29fc626bb943f00` | PASS |
| `COMMAND_LOG.json` | `08eebe09a27ce442c316b36ff21223b3a65a46eb457f8a398b7feccaf822a234` | PASS |
| Failure audit Markdown | `b31473e8167b888b392845abf7b128a3a65f9139d102258e1f3706bfbee46124` | PASS |
| R2 `REVIEW_QUEUE.json` | `5ae6038910fdc3ed7fa93502d0b92ec43b70f0f021663cd0d4468bead7c4344e` | PASS |
| Canonical `admission_sheet.csv` | `77f729b1297ef24d4223d5277b093c93ad84711dfbbe69a1927398d49d387a0a` | PASS |

## Amendment artifact matrix

| Artifact | SHA-256 | Binding result |
| --- | --- | --- |
| Design spec Markdown | `f81ca2a949ea6df0e2768386a9f188fff69fb52a2e46ae0abcb56094ee59c12a` | manifest matches raw bytes |
| `AMENDMENT_01_REF_ISOLATION.json` | `272fd6cb1ac146627f5ea42d1db10cbb082277a6a0396d887abd1e5d6d202ade` | manifest matches raw bytes |
| `AMENDMENT_01_MANIFEST.json` | `6a0135b6defe55fa400b7f8d224770bdaa225832fd78d3de9f19816965343d64` | independently recomputed |
| Implementation plan Markdown | `e60146e551f1b187f4424a71fc556b82a874e612a17b6132bbec0f30b103d5a9` | independently recomputed |

Both JSON files parse. Neither contains the literal deny identity. The
manifest's allowed path list exactly equals the materialization commit path
set, and every listed frozen hash was recomputed from raw file bytes.

## Superseded and preserved clauses

| Boundary | Amendment effect | Audit result |
| --- | --- | --- |
| Global ref-inventory purity | Superseded only as an admission gate | PASS |
| Execution-input closure | Becomes the replacement boundary | PASS |
| Deny occurrence policy | Unchanged; SCOPE remains the normative source | PASS |
| HEAD ancestry exclusion | Preserved at bootstrap and pre-network gates | PASS |
| Fetch-target exclusion | Preserved; one no-tags, single-ref authorization fetch only | PASS |
| Object/ref access | Preserved; deny-targeting reads and mutations remain forbidden | PASS |
| Active input and payload lineage | Preserved; Batch 3 origin remains forbidden | PASS |
| Failure atomicity and retry | Preserved; stop-first, no partial payload, no retry/resume | PASS |
| R2 transport and collision inputs | Preserved byte-for-byte | PASS |
| Quota and no replacement | Preserved | PASS |
| Readiness and downstream actions | Still forbidden | PASS |

The amendment is ref-name invariant. It does not grant an exception to a known
remote-tracking ref and does not make success depend on deleting or renaming
one.

## Bootstrap and pre-network gate review

| Gate | Frozen requirements | Result now |
| --- | --- | --- |
| Bootstrap | exact audit HEAD; clean tree; fixed main ancestry; textual deny absence from `rev-list HEAD`; one exact authorization fetch; zero evidence requests | Contract is explicit and mechanically testable |
| Pre-network | audit ancestry; clean tree; exact linear authorized suffix; no merge/unlisted commit; frozen hashes and pre-network checks pass; zero evidence requests | Contract is explicit and mechanically testable |
| Persistent phase | no deny fetch/read/resolve/delete; no global inventory admission gate; no Batch 3 input or lineage | Prohibitions remain active throughout |

The bootstrap observation window begins with the first recorded Cursor command.
A platform-provisioned checkout before that window is recorded as an input,
including initial HEAD, remote URL, and configured fetch refspecs. It is not
silently counted as an in-window fetch.

An unrelated stale ref is outside the execution closure only while no command
enumerates, resolves, deletes, fetches, or reads it. Any such command brings the
ref into the closure and triggers the applicable deny/access check.

## Deny-occurrence and Batch 3 exclusion proof

The normative deny value remains
`SCOPE.json#/batch3_denylist/head_sha`; the frozen
`CONTRACT_MANIFEST.json#/batch3_denylist/head_sha` is used only for equality.
The new machine-readable files record the source path, JSON pointer, and SCOPE
hash instead of copying the value. Future code, tests, commands, manifests,
payloads, and handoffs must load it from SCOPE and may not add a literal copy.

The exclusion is therefore independent of whether an unrelated pre-existing
ref happens to point at the deny identity. It still fails closed if the deny
identity appears in HEAD ancestry, an executed fetch target, an object-reading
command, an active manifest/input, or payload/handoff lineage. The frozen
failure records remain audit provenance only and are not scientific inputs.

## Future RED-to-GREEN acceptance contract

| Future case | Required result and proof |
| --- | --- |
| Synthetic unrelated stale ref contains SCOPE-loaded deny value | PASS; spy proves no enumeration, resolution, deletion, or object read |
| Synthetic ref is renamed | Identical verdict and identical command-spy trace |
| Deny value appears in HEAD ancestry ID stream | FAIL before retrieval; nonzero exit and zero requests |
| Main or exact authority chain differs | FAIL before retrieval |
| Fetch is wildcarded or names an unapproved ref | FAIL before retrieval |
| A Git command targets deny identity/ref | FAIL before retrieval |
| Active input or payload claims Batch 3 lineage | FAIL before retrieval |
| A second literal deny identity is injected | FAIL before retrieval |
| Failure provenance or R2 frozen bytes drift | FAIL before retrieval |
| Unrelated refs change but execution closure does not | Identical gate result |

The future implementation must use an in-memory ref-map fixture and an injected
command-runner spy. Every negative case must identify the first violated
invariant, exit nonzero before retrieval, record zero evidence requests, create
no partial payload, and perform no retry. Original guard-isolated,
filename-token, five-layer binding, quota, collision, transport, and
payload/handoff tests remain mandatory.

Local Desktop audit does not claim future RED-to-GREEN execution. The RED and
GREEN outputs, command-spy trace, pre-network authority manifest, environment
closure, retrieved raw evidence, quota fulfillment, five-layer bindings, and
payload/handoff checks are conditions for a later separately approved Cursor
execution and independent audit.

## Preserved scientific and governance state

| State | Preserved value | Result |
| --- | --- | --- |
| R2 partition | 67 total / 9 admit-pending-repro / 58 excluded | PASS |
| Repository shortfall | 2 / 3 / 3 | PASS |
| Risk | `DISTRIBUTION_TARGET_AT_RISK` | PASS |
| A2 | all `PENDING` | PASS |
| `analysis_id` and alias | blank | PASS |
| R2 transport freeze | unchanged | PASS |
| Quota replacement | forbidden | PASS |
| Readiness, r8, canonical freeze | not started | PASS |
| Downstream mutation | none | PASS |
| Evidence requests in this amendment/audit | zero | PASS |
| R3 implementation, payload, handoff | absent | PASS |
| Pull request and merge | absent | PASS |

No issue, GraphQL evidence, REST issue, browser membership, or manual
membership request was made. No snapshot, queue, decision, candidate sheet,
evidence manifest, pre-network authority manifest, payload, or handoff was
created.

## Verification performed

- Exact parent and three-path materialization checks passed.
- Quiet diff over every frozen R2, contract, query, failure, source, and test
  path passed.
- Raw-byte hash replay and cross-file JSON assertions passed as
  `independent-amendment-replay: PASS`.
- Static Amendment manifest validation passed as `amendment-manifest: PASS`.
- `git diff --check` passed.
- The materialization run passed `481 passed, 10 warnings`.
- A separate Local Desktop audit run passed `481 passed, 10 warnings` in
  656.67 seconds.

The warnings are the existing numerical convergence warnings exercised by the
unchanged test suite; no test failed.

## Conditions, risks, and stop rules

The verdict remains conditional because the later Cursor implementation and
its RED-to-GREEN outputs do not yet exist. A later execution is blocked at the
first mismatch in identity, parent chain, hash, executed refspec, clean state,
ancestry ID stream, authorized suffix, environment closure, command-spy trace,
deny occurrence, active-input lineage, quota, field binding, R2 freeze, or
transport/downstream boundary.

It is also blocked if any command enumerates, resolves, deletes, fetches, or
reads the stale deny ref/object; if evidence networking occurs before all
pre-network checks pass; if an evidence request, partial payload, retry, or
resume follows a failed invariant; or if any frozen artifact changes.

The failed Cursor execution remains immutable and cannot be resumed. Any later
run is a new protocol execution from the terminal audit commit, under a new
instruction and separate approval.
