# Supplemental R3 Ref-Isolation Amendment Design

Date: 2026-08-05

## 1. Purpose

This design specifies an append-only protocol amendment that removes one
over-broad Supplemental R3 preflight condition without weakening the exclusion
of PR #6 Batch 3.

The failed Cursor execution proved that the original rule conflated two
different properties:

1. Batch 3 must not be an ancestor, input, fetched target, inspected object, or
   source of any Supplemental R3 result; and
2. an unrelated pre-existing remote-tracking ref happened to point at the
   Batch 3 commit.

Only the first property is scientifically and operationally relevant. The
amendment therefore replaces global ref-inventory purity with an
execution-input-closure rule.

## 2. Authority and fixed identities

The amendment descends from the independently audited failed execution:

| Item | Fixed identity |
| --- | --- |
| Main | `3c518b8467f74c9a6efd11f2db267f9f30e1c822` |
| PR #7 head | `8d3db94a18e026cb17a6319d88a3c5960df5c406` |
| PR #7 merge | `3c518b8467f74c9a6efd11f2db267f9f30e1c822` |
| R3 contract audit | `0e85691391dd80228dcf1d584d68f2194a6077d0` |
| Failed Cursor commit | `743f5552fd5912f2705f7f256dda0f5179393842` |
| Failure audit | `641345ec4d06bd9735e972c997d5e32a4c7e22c3` |
| Batch 3 deny identity | `f6f1888f361a524a481cc9505e567a8bc414b9ea` |

The new protocol identity is
`SUPPLEMENTAL_R3_EVIDENCE_AMENDMENT_01`. It is a successor authority for a
new execution, not a continuation or retry of the failed execution.

## 3. Preserved state and non-goals

The amendment does not change:

- the original Supplemental R3 contract or query bytes;
- the three repositories, cutoff, phrases, membership algorithm, or order;
- the per-repository target 2/3/3 or the no-replacement rule;
- the frozen R2 state 67/9/58;
- A2 `PENDING` or blank aliases and `analysis_id`;
- the R2 transport freeze or collision inputs;
- the A1/A3 decision rules;
- failure atomicity, all-or-nothing success, or no-retry semantics;
- the payload/handoff two-terminal-commit rule;
- the prohibition on readiness, r8, canonical freeze, downstream mutation,
  PR creation, or merge during evidence acquisition.

This amendment does not authorize a Cursor VM, issue discovery, evidence
request, candidate review, admission, or downstream execution.

## 4. Alternatives considered

### 4.1 Selected: append-only execution-closure amendment

Keep every frozen artifact byte-identical. Add an amendment overlay with a new
protocol identity and replace only the global ref-purity clause. This preserves
the complete audit trail and tests the property that matters: whether Batch 3
can influence the execution.

### 4.2 Rejected: delete or rewrite the pre-existing ref

Deleting, pruning, or moving the ref mutates environmental state and actively
handles a Batch 3 reference. It also makes correctness depend on cleanup rather
than on the protocol's input boundary.

### 4.3 Rejected: exempt one known ref name

An exception for
`refs/remotes/origin/cursor/grok-phase3-c3-readiness-batch3` would be brittle.
Renaming the ref would alter the result even though the execution dependency
graph remained unchanged.

## 5. Amendment artifacts

After this design is reviewed, the protocol-materialization commit will add:

1. `data/external_slice/supplemental_r3/amendments/AMENDMENT_01_REF_ISOLATION.json`
2. `data/external_slice/supplemental_r3/amendments/AMENDMENT_01_MANIFEST.json`
3. `docs/superpowers/plans/2026-08-05-supplemental-r3-ref-isolation-amendment.md`

The direct-child Local Desktop audit commit will add only:

4. `docs/review_20260805/gate_supplemental_r3_ref_isolation_amendment_audit.md`

No existing contract, R2, failure, source, test, query, or evidence artifact is
modified.

## 6. Execution-input closure

The execution-input closure is the complete set of identities and bytes that a
future Cursor run may use to determine membership, retrieve evidence, validate
artifacts, or create a payload:

- the authorized amendment audit commit and its ancestry;
- the exact fetch command and refspec used to obtain that authority;
- the original frozen Supplemental R3 JSON contracts and query documents;
- both Amendment 01 JSON files;
- R2 collision inputs and the R2 byte/tree freeze comparison set;
- R3 miner/checker/test source created by the future run;
- the platform-provisioned initial checkout identity, Git remote URL, and
  configured fetch refspecs;
- Git, GitHub CLI, Python, pytest, operating-system, and dependency-lock
  identities recorded by the run;
- raw GraphQL response bytes and their manifests;
- snapshot, queue, decision, candidate sheet, evidence, verification, payload,
  and handoff artifacts;
- every recorded command that can read or mutate Git objects or refs.

An unrelated pre-existing local or remote-tracking ref is outside the closure
unless a command resolves, fetches, checks out, merges, compares, opens, scans
for object identity, or otherwise reads it.

## 7. Replacement gate

The original requirement that no local branch or remote ref may point at the
deny identity is superseded. The amended gate has two explicit lifecycle
phases.

### 7.1 Bootstrap gate

The bootstrap observation window begins with the first recorded command inside
the authorized Cursor task. A platform-provisioned clone or checkout completed
before that command is outside the fetch-count window, but its HEAD, remote
URL, and configured fetch refspecs are recorded as inputs.

Before creating or changing any file, the run must prove:

1. HEAD equals the immutable Amendment 01 Local Desktop audit commit.
2. The worktree is clean.
3. Fixed main is an ancestor of HEAD.
4. The exact first-parent authority chain equals the audited chain.
5. A textual comparison of commit IDs emitted by `git rev-list HEAD` finds no
   deny identity. The gate does not resolve the deny identity as an object.
6. Inside the observation window, the only authorization fetch is exactly one
   no-tags, single-ref fetch of the Amendment 01 audit branch.
7. No executed fetch refspec names the Batch 3 branch, deny identity, wildcard
   branch namespace, or any unapproved ref.
8. No evidence request has occurred.

### 7.2 Pre-network gate

The future run may create the frozen test/code commits authorized by the
implementation plan. Immediately before the first evidence request, it must
prove:

1. the Amendment 01 Local Desktop audit commit is an ancestor of current HEAD;
2. current HEAD is clean and its first-parent suffix after the audit commit is
   exactly the ordered, hash-bound set of authorized contract/test/code commits;
3. there is no merge commit or unlisted commit in that suffix;
4. fixed main remains an ancestor and a textual `git rev-list HEAD` comparison
   still contains no deny identity;
5. original contracts, Amendment 01 files, queries, R2 freeze inputs, failure
   provenance, source, tests, environment identities, and command provenance
   all match their frozen hashes;
6. every required pre-network test and static check has passed;
7. no evidence request has yet occurred.

### 7.3 Persistent access and input prohibitions

Across both gates and the later execution:

1. no command targets the deny identity or Batch 3 ref with `show`,
   `cat-file`, `checkout`, `switch`, `merge`, `rebase`,
   `cherry-pick`, `diff`, `log`, `branch --contains`,
   `merge-base`, or an equivalent object-reading operation;
2. no active input, manifest identity, source payload, copied artifact, issue
   record, fix record, collision key, or handoff lineage originates from Batch
   3;
3. command provenance contains no global ref/object inventory used as an
   admission condition, including `git for-each-ref`.

The mere existence of an unrelated pre-existing ref is neither success
evidence nor failure evidence. It is intentionally not enumerated.

## 8. Deny-identity occurrence policy

The deny identity may occur only in two classes.

### 8.1 Active machine-readable fields

The sole normative source of the deny identity remains:

- `data/external_slice/supplemental_r3/SCOPE.json#/batch3_denylist/head_sha`.

The frozen copy in
`CONTRACT_MANIFEST.json#/batch3_denylist/head_sha` is only an equality check
against that source. `AMENDMENT_01_REF_ISOLATION.json` does not repeat the
deny identity. It records only:

- the SCOPE path and JSON pointer;
- the frozen SCOPE file SHA-256; and
- the required equality-check path in `CONTRACT_MANIFEST.json`.

The amendment manifest also omits the literal deny identity. Future source
code, tests, command arguments, refspecs, manifests, and payloads load the value
from the SCOPE field and must not embed another literal copy. Therefore
Amendment 01 changes only the global ref-purity rule and does not amend the
frozen occurrence policy. Amendment design, plan, and audit prose are
`contract_audit_explanation` occurrences, not scientific inputs.

### 8.2 Immutable provenance and governance narrative

Existing plans, audits, and failure records necessarily name the deny identity.
They are not membership or evidence inputs. The amendment manifest binds the
following failure provenance byte-for-byte:

| Artifact | SHA-256 |
| --- | --- |
| `FIRST_FAILURE.json` | `160621cfd947770008805452a80b2724e619036cb2771ed9c29fc626bb943f00` |
| `COMMAND_LOG.json` | `08eebe09a27ce442c316b36ff21223b3a65a46eb457f8a398b7feccaf822a234` |
| Failure audit Markdown | `b31473e8167b888b392845abf7b128a3a65f9139d102258e1f3706bfbee46124` |

Any byte drift in these immutable provenance artifacts is a hard failure.
Governance prose added by this amendment may name the identity for audit
explanation, but governance Markdown is excluded from scientific inputs.

## 9. Future RED-to-GREEN requirements

The later Cursor implementation must begin with failing tests and include the
following matrix:

| Case | Required result |
| --- | --- |
| Synthetic unrelated pre-existing ref map contains deny identity loaded from SCOPE | PASS without resolving or deleting the ref |
| Same ref is renamed | Same PASS result |
| Deny identity appears in HEAD ancestry ID stream | FAIL before retrieval |
| Fixed main or exact authority chain differs | FAIL before retrieval |
| Fetch command uses wildcard or names an unapproved ref | FAIL before retrieval |
| Fetch, show, cat-file, checkout, merge, or cherry-pick targets deny identity/ref | FAIL before retrieval |
| Active input manifest claims Batch 3 lineage or payload | FAIL before retrieval |
| Temporary fixture injects a second literal deny identity loaded from SCOPE | FAIL before retrieval |
| Immutable failure provenance changes by one byte | FAIL before retrieval |
| R2 frozen byte/tree changes | FAIL before retrieval |
| Pre-existing unrelated refs differ while the execution closure is identical | Identical gate result |

Negative tests must prove the first violated invariant, nonzero exit, zero
evidence requests, no partial payload, and no retry. The positive stale-ref
test must prove that no ref deletion, ref resolution, or Batch 3 object read is
performed. It uses an injected command-runner spy and an in-memory ref-map
fixture; the spy fails on ref enumeration, deletion, resolution, or an
object-reading command. Renaming the synthetic ref must leave both the verdict
and spy call trace unchanged. Test source obtains the deny value from SCOPE and
does not contain the literal SHA.

All original Supplemental R3 RED-to-GREEN, guard-isolated filename-token,
five-layer binding, quota, collision, transport, and payload/handoff tests
remain mandatory.

## 10. Local Desktop governance audit

The Local Desktop audit must independently verify:

- fixed GitHub identities and the complete authority parent chain;
- byte identity of all original contract, query, R2, and failure artifacts;
- JSON validity and exact hashes of both amendment files;
- the amendment changes only the global ref-purity clause;
- the replacement gate is based on ancestry, executed refspecs, active inputs,
  and command provenance;
- no clause authorizes reading, fetching, deleting, or resolving Batch 3;
- the future positive/negative matrix is complete, mechanically testable,
  hash-bound as a mandatory acceptance criterion, and assigns every negative
  case a fail-before-retrieval result;
- the stale-ref invariance and command-spy requirements are explicitly frozen;
- zero issue, GraphQL evidence, REST issue, browser, or manual membership
  requests occurred during amendment and audit;
- no R3 implementation, payload, handoff, readiness, r8, canonical freeze,
  PR, or merge was created.

The Local Desktop audit does not claim that future RED-to-GREEN tests have
executed. Their actual RED and GREEN outputs are conditions for the later
Cursor payload and its independent audit.

The audit may return
`R3_REF_ISOLATION_AMENDMENT_FEASIBLE_WITH_CONDITIONS` only if every item
passes. Otherwise it returns `R3_REF_ISOLATION_AMENDMENT_BLOCKED`.

## 11. Commit and branch structure

The branch is
`codex/phase3-supplemental-r3-ref-isolation-amendment`.

Its required linear history is:

1. design-spec commit, sole parent
   `641345ec4d06bd9735e972c997d5e32a4c7e22c3`;
2. protocol-materialization commit, sole parent the design-spec commit;
3. Local Desktop governance-audit commit, sole parent the materialization
   commit.

Only the third commit is the terminal remote branch head. The branch is pushed
after all local checks pass. No PR is created.

## 12. Stop conditions

The amendment and audit stop as blocked if any of the following occurs:

- a fixed identity, parent, hash, path set, or byte comparison differs;
- an original contract or frozen R2/failure artifact changes;
- the amendment relaxes ancestry, fetch-target, input-lineage, object-access,
  no-retry, quota, blind, transport, or downstream boundaries;
- the replacement gate depends on a specific stale ref name;
- the design requires inspecting, deleting, or resolving Batch 3;
- evidence networking or a downstream action occurs;
- static validation, repository tests, or `git diff --check` fails.

Tooling or environment problems may be diagnosed and corrected within the
Local Desktop audit, but governance mismatches remain fail-closed.

## 13. Resulting authorization boundary

A successful amendment audit authorizes only the generation of a new,
immutable Cursor VM instruction bound to the terminal audit commit. It does not
authorize running that instruction.

The failed Cursor execution and its verdict remain immutable. A later Cursor
run is a new `SUPPLEMENTAL_R3_EVIDENCE_AMENDMENT_01` execution with its own
branch, command log, failure atomicity, and terminal verdict.
