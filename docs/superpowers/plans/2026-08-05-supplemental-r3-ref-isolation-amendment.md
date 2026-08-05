# Supplemental R3 Ref-Isolation Amendment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Materialize and independently audit Amendment 01 so a later, separately approved Cursor VM can ignore unrelated stale refs without permitting Batch 3 ancestry, access, fetch, input, or lineage.

**Architecture:** Add an append-only amendment overlay beneath the existing Supplemental R3 root. One JSON defines the two-phase bootstrap/pre-network gate without repeating the deny SHA; a second manifest binds the amendment, design, frozen contracts, failure provenance, and allowed path set. A direct-child Local Desktop audit verifies the materialization without performing evidence acquisition or future RED-to-GREEN execution.

**Tech Stack:** Canonical JSON, Markdown, Python 3 standard library, SHA-256, Git, GitHub CLI, and pytest.

## Global Constraints

- Local Desktop shell commands use the `rtk` prefix.
- Branch: `codex/phase3-supplemental-r3-ref-isolation-amendment`.
- Design-spec commit: `e5bfb155fe3c2799da3bb51371db059153c68285`.
- Design-spec parent: `641345ec4d06bd9735e972c997d5e32a4c7e22c3`.
- Fixed main: `3c518b8467f74c9a6efd11f2db267f9f30e1c822`.
- Contract audit: `0e85691391dd80228dcf1d584d68f2194a6077d0`.
- Failed Cursor commit: `743f5552fd5912f2705f7f256dda0f5179393842`.
- Original Supplemental R3 contract and query bytes remain unchanged.
- R2 transport, collision inputs, state 67/9/58, shortfall 2/3/3, A2 `PENDING`, and blank aliases remain unchanged.
- The deny SHA is loaded only from the frozen SCOPE JSON pointer; neither Amendment JSON repeats its literal value.
- This session performs zero issue, GraphQL evidence, REST issue, browser membership, or manual evidence requests.
- No R3 miner/checker/test implementation, payload, handoff, readiness, r8, canonical freeze, PR, merge, or Cursor VM is created.
- Tooling problems may be diagnosed and corrected; identity, hash, lineage, scope, or freeze mismatches fail closed.

---

## File structure

| Path | Responsibility |
| --- | --- |
| `data/external_slice/supplemental_r3/amendments/AMENDMENT_01_REF_ISOLATION.json` | Normative replacement for global ref-purity, including bootstrap, pre-network, persistent access, occurrence, test-contract, and stop rules |
| `data/external_slice/supplemental_r3/amendments/AMENDMENT_01_MANIFEST.json` | Hash and authority binding for the amendment, design, original contracts, queries, failure provenance, R2 collision inputs, and allowed paths |
| `docs/superpowers/plans/2026-08-05-supplemental-r3-ref-isolation-amendment.md` | This executable Local Desktop plan |
| `docs/review_20260805/gate_supplemental_r3_ref_isolation_amendment_audit.md` | Direct-child independent governance audit and formal verdict |

No existing file is modified after the design-spec commit.

### Task 1: Revalidate authority and frozen inputs

**Files:**
- Read: `docs/superpowers/specs/2026-08-05-supplemental-r3-ref-isolation-amendment-design.md`
- Read: `data/external_slice/supplemental_r3/SCOPE.json`
- Read: `data/external_slice/supplemental_r3/CONTRACT_MANIFEST.json`
- Read: `data/external_slice/supplemental_r3/TRANSPORT_CONTRACT.json`
- Read: `data/external_slice/supplemental_r3/QUOTAS.json`
- Read: `data/external_slice/supplemental_r3/COLLISION_UNIVERSE.json`
- Read: `data/external_slice/supplemental_r3/FIRST_FAILURE.json`
- Read: `data/external_slice/supplemental_r3/COMMAND_LOG.json`

**Interfaces:**
- Consumes: immutable GitHub and Git identities listed in Global Constraints.
- Produces: a verified clean authority at the design-spec commit and the exact frozen hashes used by Task 2.

- [ ] **Step 1: Verify local authority and clean state**

Run:

```bash
rtk git rev-parse HEAD
rtk git rev-parse HEAD^
rtk git status --short --branch
```

Expected: HEAD is `e5bfb155fe3c2799da3bb51371db059153c68285`, its parent is `641345ec4d06bd9735e972c997d5e32a4c7e22c3`, and the worktree contains only this uncommitted plan.

- [ ] **Step 2: Verify remote fixed identities with local `gh`**

Run:

```bash
rtk gh repo view --json nameWithOwner,url,defaultBranchRef
rtk gh api repos/meng004/P3-Semantic-Mutation/git/ref/heads/main --jq .object.sha
rtk gh pr view 7 --repo meng004/P3-Semantic-Mutation --json number,state,headRefOid,mergeCommit,baseRefName
rtk gh run view 30985348887 --repo meng004/P3-Semantic-Mutation --job 92238715535 --json databaseId,status,conclusion,headSha,jobs
rtk gh api repos/meng004/P3-Semantic-Mutation/git/ref/heads/cursor/grok-phase3-supplemental-r3-evidence --jq .object.sha
rtk gh api repos/meng004/P3-Semantic-Mutation/git/ref/heads/codex/phase3-supplemental-r3-evidence-failure-audit --jq .object.sha
```

Expected:

```text
repository = meng004/P3-Semantic-Mutation
main = 3c518b8467f74c9a6efd11f2db267f9f30e1c822
PR #7 state/head/merge = MERGED / 8d3db94a18e026cb17a6319d88a3c5960df5c406 / 3c518b8467f74c9a6efd11f2db267f9f30e1c822
CI run/job = 30985348887 / 92238715535, completed/success at fixed main
failed Cursor branch = 743f5552fd5912f2705f7f256dda0f5179393842
failure audit branch = 641345ec4d06bd9735e972c997d5e32a4c7e22c3
```

These are GitHub identity reads, not evidence requests.

- [ ] **Step 3: Recompute frozen input hashes**

Run:

```bash
rtk shasum -a 256 data/external_slice/supplemental_r3/SCOPE.json data/external_slice/supplemental_r3/TRANSPORT_CONTRACT.json data/external_slice/supplemental_r3/QUOTAS.json data/external_slice/supplemental_r3/COLLISION_UNIVERSE.json data/external_slice/supplemental_r3/queries/discovery.graphql data/external_slice/supplemental_r3/queries/issue_evidence.graphql data/external_slice/supplemental_r3/queries/fix_evidence.graphql data/external_slice/supplemental_r3/FIRST_FAILURE.json data/external_slice/supplemental_r3/COMMAND_LOG.json docs/review_20260805/gate_supplemental_r3_evidence_failure_audit.md docs/superpowers/specs/2026-08-05-supplemental-r3-ref-isolation-amendment-design.md
```

Expected hashes:

```text
SCOPE.json                 67d16148e1055ca9a96302ff737e7443ecf23bb1683badc1c1a13c49f99db0f1
TRANSPORT_CONTRACT.json    42188051bb12032037949a0052bb9f0b429a882a8dfd38a3d4074efcc7d5e107
QUOTAS.json                50742a93aca5d269d84303c82393e47de85746d6ba58bf079b27678d66574bb2
COLLISION_UNIVERSE.json    7633db6fb1a19f5a815e2870a6f112be0cc1be7903d26fe658df4b549a332d3a
discovery.graphql          80d1287f692c2b42f326ef364ddffe5ce44f3dd81fa1c03444d83e6ebb2996c6
issue_evidence.graphql     c9c6f583325b5530072f5df5779fae20e04974c62265305956421e75ad6bb862
fix_evidence.graphql       033173f0675b3bdbe69fa9911e2169557c2001e3f6c02541f4c699c6f16435eb
FIRST_FAILURE.json         160621cfd947770008805452a80b2724e619036cb2771ed9c29fc626bb943f00
COMMAND_LOG.json           08eebe09a27ce442c316b36ff21223b3a65a46eb457f8a398b7feccaf822a234
failure audit Markdown     b31473e8167b888b392845abf7b128a3a65f9139d102258e1f3706bfbee46124
design spec Markdown       f81ca2a949ea6df0e2768386a9f188fff69fb52a2e46ae0abcb56094ee59c12a
```

Stop on any mismatch.

### Task 2: Materialize the normative Amendment JSON

**Files:**
- Create: `data/external_slice/supplemental_r3/amendments/AMENDMENT_01_REF_ISOLATION.json`

**Interfaces:**
- Consumes: frozen SCOPE path, JSON pointer, file hash, design authority, and failure authority from Task 1.
- Produces: canonical JSON for `SUPPLEMENTAL_R3_EVIDENCE_AMENDMENT_01` without a literal deny SHA.

- [ ] **Step 1: Create the amendment directory and JSON through `apply_patch`**

The JSON must have this exact field structure and values:

```json
{
  "schema_version": 1,
  "protocol": "SUPPLEMENTAL_R3_EVIDENCE_AMENDMENT_01",
  "amendment_id": "AMENDMENT_01_REF_ISOLATION",
  "parent_protocol": "SUPPLEMENTAL_R3_EVIDENCE",
  "authority": {
    "fixed_main": "3c518b8467f74c9a6efd11f2db267f9f30e1c822",
    "contract_audit": "0e85691391dd80228dcf1d584d68f2194a6077d0",
    "failed_cursor_commit": "743f5552fd5912f2705f7f256dda0f5179393842",
    "failure_audit": "641345ec4d06bd9735e972c997d5e32a4c7e22c3",
    "design_spec_commit": "e5bfb155fe3c2799da3bb51371db059153c68285",
    "materialization_commit_resolution": "SELF",
    "authorized_audit_commit_resolution": "SOLE_DIRECT_CHILD_LOCAL_AUDIT_COMMIT"
  },
  "supersession": {
    "scope": "global_ref_inventory_purity_only",
    "replacement": "execution_input_closure",
    "occurrence_policy_changed": false
  },
  "deny_identity_source": {
    "path": "data/external_slice/supplemental_r3/SCOPE.json",
    "json_pointer": "/batch3_denylist/head_sha",
    "file_sha256": "67d16148e1055ca9a96302ff737e7443ecf23bb1683badc1c1a13c49f99db0f1",
    "consistency_check": {
      "path": "data/external_slice/supplemental_r3/CONTRACT_MANIFEST.json",
      "json_pointer": "/batch3_denylist/head_sha"
    },
    "literal_repetition_in_amendment_forbidden": true
  },
  "bootstrap_gate": {
    "observation_window_start": "first recorded command inside authorized Cursor task",
    "platform_provisioned_checkout_before_window": true,
    "record_platform_head_remote_and_fetch_refspecs": true,
    "required_initial_head_source": "SOLE_DIRECT_CHILD_LOCAL_AUDIT_COMMIT",
    "clean_worktree": true,
    "fixed_main_is_ancestor": true,
    "deny_identity_absent_from_rev_list_head": true,
    "deny_object_resolution_forbidden": true,
    "authorization_fetch": {
      "count": 1,
      "no_tags": true,
      "wildcards": false,
      "source_ref": "refs/heads/codex/phase3-supplemental-r3-ref-isolation-amendment",
      "destination_ref": "refs/remotes/origin/codex/phase3-supplemental-r3-ref-isolation-amendment"
    },
    "evidence_request_count": 0
  },
  "pre_network_gate": {
    "audit_commit_is_ancestor": true,
    "clean_worktree": true,
    "linear_authorized_suffix": true,
    "merge_commits_forbidden": true,
    "unlisted_commits_forbidden": true,
    "authorized_commit_manifest_path": "data/external_slice/supplemental_r3/PRE_NETWORK_AUTHORITY.json",
    "fixed_main_is_ancestor": true,
    "deny_identity_absent_from_rev_list_head": true,
    "all_frozen_hashes_match": true,
    "all_required_pre_network_checks_pass": true,
    "evidence_request_count": 0
  },
  "persistent_prohibitions": {
    "global_ref_inventory_as_gate": false,
    "forbidden_git_operations": [
      "fetch deny ref or identity",
      "show deny ref or identity",
      "cat-file deny ref or identity",
      "checkout deny ref or identity",
      "switch deny ref or identity",
      "merge deny ref or identity",
      "rebase deny ref or identity",
      "cherry-pick deny ref or identity",
      "diff deny ref or identity",
      "log deny ref or identity",
      "branch --contains deny identity",
      "merge-base deny identity"
    ],
    "batch3_ancestry_input_payload_lineage": false,
    "preexisting_unrelated_refs_enumerated": false,
    "preexisting_unrelated_refs_deleted": false,
    "preexisting_unrelated_refs_resolved": false
  },
  "future_test_contract": {
    "deny_value_loaded_from_scope": true,
    "stale_ref_fixture": "in_memory_ref_map",
    "command_runner_spy_required": true,
    "ref_rename_invariance_required": true,
    "negative_result": "fail_before_retrieval",
    "negative_evidence_request_count": 0,
    "partial_payload_forbidden": true,
    "retry_forbidden": true
  },
  "preserved_invariants": {
    "r2_state": {"total": 67, "admit_pending_repro": 9, "excluded": 58},
    "shortfall": {"gpytorch": 2, "chaospy": 3, "salib": 3},
    "status": "DISTRIBUTION_TARGET_AT_RISK",
    "A2": "PENDING",
    "analysis_id": "",
    "alias": "",
    "r2_transport_freeze": true,
    "quota_replacement": false,
    "readiness": false,
    "r8": false,
    "canonical_freeze": false,
    "downstream_mutation": false
  },
  "failure_policy": {
    "first_failure_stops": true,
    "diagnostic_only": true,
    "partial_payload": false,
    "retry": false,
    "resume_failed_execution": false
  }
}
```

- [ ] **Step 2: Validate JSON syntax and absence of the deny literal**

Run:

```bash
rtk python3 -c 'import hashlib, json
from pathlib import Path
root = Path("data/external_slice/supplemental_r3")
scope_path = root / "SCOPE.json"
contract_manifest_path = root / "CONTRACT_MANIFEST.json"
amendment_path = root / "amendments/AMENDMENT_01_REF_ISOLATION.json"
scope = json.loads(scope_path.read_text())
contract_manifest = json.loads(contract_manifest_path.read_text())
amendment = json.loads(amendment_path.read_text())
deny = scope["batch3_denylist"]["head_sha"]
assert deny == contract_manifest["batch3_denylist"]["head_sha"]
assert deny.encode() not in amendment_path.read_bytes()
assert hashlib.sha256(scope_path.read_bytes()).hexdigest() == amendment["deny_identity_source"]["file_sha256"]
assert amendment["supersession"]["occurrence_policy_changed"] is False
assert amendment["bootstrap_gate"]["evidence_request_count"] == 0
assert amendment["pre_network_gate"]["evidence_request_count"] == 0
print("amendment-json: PASS")'
```

Expected: `amendment-json: PASS`.

### Task 3: Materialize the Amendment manifest and commit

**Files:**
- Create: `data/external_slice/supplemental_r3/amendments/AMENDMENT_01_MANIFEST.json`
- Include: `docs/superpowers/plans/2026-08-05-supplemental-r3-ref-isolation-amendment.md`

**Interfaces:**
- Consumes: amendment bytes and all frozen hashes from Tasks 1–2.
- Produces: a materialization commit containing exactly the plan and two Amendment JSON files.

- [ ] **Step 1: Compute the amendment SHA-256**

Run:

```bash
rtk shasum -a 256 data/external_slice/supplemental_r3/amendments/AMENDMENT_01_REF_ISOLATION.json
```

Record the exact result in the manifest.

- [ ] **Step 2: Create the manifest through `apply_patch`**

The manifest must contain:

```json
{
  "schema_version": 1,
  "protocol": "SUPPLEMENTAL_R3_EVIDENCE_AMENDMENT_01",
  "amendment_id": "AMENDMENT_01_REF_ISOLATION",
  "authority": {
    "design_spec_commit": "e5bfb155fe3c2799da3bb51371db059153c68285",
    "materialization_commit_resolution": "SELF",
    "authorized_audit_commit_resolution": "SOLE_DIRECT_CHILD_LOCAL_AUDIT_COMMIT"
  },
  "design_spec": {
    "path": "docs/superpowers/specs/2026-08-05-supplemental-r3-ref-isolation-amendment-design.md",
    "sha256": "f81ca2a949ea6df0e2768386a9f188fff69fb52a2e46ae0abcb56094ee59c12a"
  },
  "amendment": {
    "path": "data/external_slice/supplemental_r3/amendments/AMENDMENT_01_REF_ISOLATION.json",
    "sha256": "272fd6cb1ac146627f5ea42d1db10cbb082277a6a0396d887abd1e5d6d202ade"
  },
  "original_contract_artifacts_sha256": {
    "data/external_slice/supplemental_r3/SCOPE.json": "67d16148e1055ca9a96302ff737e7443ecf23bb1683badc1c1a13c49f99db0f1",
    "data/external_slice/supplemental_r3/TRANSPORT_CONTRACT.json": "42188051bb12032037949a0052bb9f0b429a882a8dfd38a3d4074efcc7d5e107",
    "data/external_slice/supplemental_r3/QUOTAS.json": "50742a93aca5d269d84303c82393e47de85746d6ba58bf079b27678d66574bb2",
    "data/external_slice/supplemental_r3/COLLISION_UNIVERSE.json": "7633db6fb1a19f5a815e2870a6f112be0cc1be7903d26fe658df4b549a332d3a",
    "data/external_slice/supplemental_r3/queries/discovery.graphql": "80d1287f692c2b42f326ef364ddffe5ce44f3dd81fa1c03444d83e6ebb2996c6",
    "data/external_slice/supplemental_r3/queries/issue_evidence.graphql": "c9c6f583325b5530072f5df5779fae20e04974c62265305956421e75ad6bb862",
    "data/external_slice/supplemental_r3/queries/fix_evidence.graphql": "033173f0675b3bdbe69fa9911e2169557c2001e3f6c02541f4c699c6f16435eb"
  },
  "failure_provenance_sha256": {
    "data/external_slice/supplemental_r3/FIRST_FAILURE.json": "160621cfd947770008805452a80b2724e619036cb2771ed9c29fc626bb943f00",
    "data/external_slice/supplemental_r3/COMMAND_LOG.json": "08eebe09a27ce442c316b36ff21223b3a65a46eb457f8a398b7feccaf822a234",
    "docs/review_20260805/gate_supplemental_r3_evidence_failure_audit.md": "b31473e8167b888b392845abf7b128a3a65f9139d102258e1f3706bfbee46124"
  },
  "r2_collision_inputs_sha256": {
    "data/external_slice/supplemental_r2/REVIEW_QUEUE.json": "5ae6038910fdc3ed7fa93502d0b92ec43b70f0f021663cd0d4468bead7c4344e",
    "data/external_slice/admission_sheet.csv": "77f729b1297ef24d4223d5277b093c93ad84711dfbbe69a1927398d49d387a0a"
  },
  "allowed_new_paths": [
    "data/external_slice/supplemental_r3/amendments/AMENDMENT_01_MANIFEST.json",
    "data/external_slice/supplemental_r3/amendments/AMENDMENT_01_REF_ISOLATION.json",
    "docs/superpowers/plans/2026-08-05-supplemental-r3-ref-isolation-amendment.md"
  ],
  "forbidden_outputs": [
    "transport_pages",
    "issue_pages",
    "fix_pages",
    "snapshot",
    "queue",
    "decision",
    "sheet",
    "evidence",
    "miner",
    "checker",
    "tests",
    "payload",
    "handoff",
    "readiness",
    "r8",
    "canonical_freeze"
  ],
  "zero_network_confirmation": {
    "evidence_request_count": 0,
    "github_issue_requests": 0,
    "graphql_requests": 0,
    "rest_requests": 0,
    "browser_requests": 0,
    "manual_membership_search": false
  }
}
```

The Task 3 Step 1 result must equal
`272fd6cb1ac146627f5ea42d1db10cbb082277a6a0396d887abd1e5d6d202ade`.
Any other result is a hard stop.

- [ ] **Step 3: Run static contract validation**

Stage exactly the three materialization files and capture the staged path set:

```bash
rtk git add data/external_slice/supplemental_r3/amendments/AMENDMENT_01_REF_ISOLATION.json data/external_slice/supplemental_r3/amendments/AMENDMENT_01_MANIFEST.json docs/superpowers/plans/2026-08-05-supplemental-r3-ref-isolation-amendment.md
rtk proxy git diff --cached --name-only > /tmp/supplemental-r3-amendment-paths.txt
```

Run:

```bash
rtk python3 -c 'import hashlib, json
from pathlib import Path
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
root = Path("data/external_slice/supplemental_r3")
amendment_path = root / "amendments/AMENDMENT_01_REF_ISOLATION.json"
manifest_path = root / "amendments/AMENDMENT_01_MANIFEST.json"
scope = json.loads((root / "SCOPE.json").read_text())
contract_manifest = json.loads((root / "CONTRACT_MANIFEST.json").read_text())
amendment = json.loads(amendment_path.read_text())
manifest = json.loads(manifest_path.read_text())
deny = scope["batch3_denylist"]["head_sha"]
assert deny == contract_manifest["batch3_denylist"]["head_sha"]
assert deny.encode() not in amendment_path.read_bytes()
assert deny.encode() not in manifest_path.read_bytes()
for path_text, expected in manifest["original_contract_artifacts_sha256"].items():
    assert sha(Path(path_text)) == expected
for path_text, expected in manifest["failure_provenance_sha256"].items():
    assert sha(Path(path_text)) == expected
for path_text, expected in manifest["r2_collision_inputs_sha256"].items():
    assert sha(Path(path_text)) == expected
assert sha(amendment_path) == manifest["amendment"]["sha256"]
assert sha(Path(manifest["design_spec"]["path"])) == manifest["design_spec"]["sha256"]
assert "bootstrap_gate" in amendment and "pre_network_gate" in amendment
assert amendment["bootstrap_gate"] is not amendment["pre_network_gate"]
assert amendment["bootstrap_gate"]["evidence_request_count"] == 0
assert amendment["pre_network_gate"]["evidence_request_count"] == 0
assert all(value == 0 for key, value in manifest["zero_network_confirmation"].items() if key != "manual_membership_search")
assert manifest["zero_network_confirmation"]["manual_membership_search"] is False
staged = Path("/tmp/supplemental-r3-amendment-paths.txt").read_text().splitlines()
assert staged == manifest["allowed_new_paths"]
for forbidden in ("transport_pages", "issue_pages", "fix_pages"):
    assert not (root / forbidden).exists()
for forbidden in ("ISSUE_SNAPSHOT.json", "REVIEW_QUEUE.json", "REVIEW_DECISIONS.json", "admission_sheet.cursor_candidate.csv", "EVIDENCE_SNAPSHOT.json", "HANDOFF_SUPPLEMENTAL_R3.json", "PRE_NETWORK_AUTHORITY.json"):
    assert not (root / forbidden).exists()
assert not any("supplemental_r3" in p.name.lower() for p in Path("scripts/external_slice").rglob("*") if p.is_file())
assert not any("supplemental_r3" in p.name.lower() for p in Path("tests/external_slice").rglob("*") if p.is_file())
print("amendment-manifest: PASS")'
```

Expected: `amendment-manifest: PASS`.

- [ ] **Step 4: Run repository validation**

Run:

```bash
rtk proxy git diff --check
rtk env PYTHONPATH=src /Users/limeng/Papers/P3-SemanticMutation/.venv/bin/python -m pytest -q
```

Expected: `481 passed, 10 warnings` and no diff-check output.

- [ ] **Step 5: Commit the three-file materialization**

Verify the staged path set is exactly:

```text
data/external_slice/supplemental_r3/amendments/AMENDMENT_01_MANIFEST.json
data/external_slice/supplemental_r3/amendments/AMENDMENT_01_REF_ISOLATION.json
docs/superpowers/plans/2026-08-05-supplemental-r3-ref-isolation-amendment.md
```

Commit:

```bash
rtk git commit -m "governance: materialize supplemental r3 ref isolation amendment"
```

Record the full materialization SHA. Do not push yet.

### Task 4: Perform the Local Desktop governance audit

**Files:**
- Create: `docs/review_20260805/gate_supplemental_r3_ref_isolation_amendment_audit.md`

**Interfaces:**
- Consumes: the materialization commit, original frozen contracts, Amendment JSON files, validation outputs, and GitHub identities.
- Produces: the sole direct-child audit commit and either `R3_REF_ISOLATION_AMENDMENT_FEASIBLE_WITH_CONDITIONS` or `R3_REF_ISOLATION_AMENDMENT_BLOCKED`.

- [ ] **Step 1: Verify materialization parent and path set**

Run:

```bash
rtk git rev-parse HEAD^
rtk git diff-tree --no-commit-id --name-status -r HEAD
rtk proxy git diff HEAD^ HEAD --check
rtk git diff --quiet HEAD^ HEAD -- data/external_slice/supplemental_r2 data/external_slice/admission_sheet.csv data/external_slice/supplemental_r3/SCOPE.json data/external_slice/supplemental_r3/TRANSPORT_CONTRACT.json data/external_slice/supplemental_r3/QUOTAS.json data/external_slice/supplemental_r3/COLLISION_UNIVERSE.json data/external_slice/supplemental_r3/queries data/external_slice/supplemental_r3/FIRST_FAILURE.json data/external_slice/supplemental_r3/COMMAND_LOG.json scripts tests
```

Expected: parent is `e5bfb155fe3c2799da3bb51371db059153c68285`;
the changed paths are exactly the manifest, amendment, and plan; all quiet-diff
checks exit zero.

- [ ] **Step 2: Independently execute all static and repository checks**

Recompute every hash from raw bytes:

```bash
rtk python3 -c 'import hashlib, json
from pathlib import Path
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
root = Path("data/external_slice/supplemental_r3")
amendment_path = root / "amendments/AMENDMENT_01_REF_ISOLATION.json"
manifest_path = root / "amendments/AMENDMENT_01_MANIFEST.json"
scope = json.loads((root / "SCOPE.json").read_text())
contract_manifest = json.loads((root / "CONTRACT_MANIFEST.json").read_text())
amendment = json.loads(amendment_path.read_text())
manifest = json.loads(manifest_path.read_text())
deny = scope["batch3_denylist"]["head_sha"]
assert deny == contract_manifest["batch3_denylist"]["head_sha"]
assert deny.encode() not in amendment_path.read_bytes()
assert deny.encode() not in manifest_path.read_bytes()
for field in ("original_contract_artifacts_sha256", "failure_provenance_sha256", "r2_collision_inputs_sha256"):
    for path_text, expected in manifest[field].items():
        assert sha(Path(path_text)) == expected
assert sha(amendment_path) == manifest["amendment"]["sha256"]
assert sha(Path(manifest["design_spec"]["path"])) == manifest["design_spec"]["sha256"]
assert amendment["supersession"] == {"scope": "global_ref_inventory_purity_only", "replacement": "execution_input_closure", "occurrence_policy_changed": False}
assert amendment["bootstrap_gate"]["evidence_request_count"] == 0
assert amendment["pre_network_gate"]["evidence_request_count"] == 0
assert all(value == 0 for key, value in manifest["zero_network_confirmation"].items() if key != "manual_membership_search")
assert manifest["zero_network_confirmation"]["manual_membership_search"] is False
print("independent-amendment-replay: PASS")'
rtk proxy git diff HEAD^ HEAD --check
rtk env PYTHONPATH=src /Users/limeng/Papers/P3-SemanticMutation/.venv/bin/python -m pytest -q
```

Expected: `independent-amendment-replay: PASS`, no diff-check output, and
`481 passed, 10 warnings`. Do not substitute the materialization run's output
for this audit run.

- [ ] **Step 3: Audit the amendment semantics**

The audit report must distinguish:

- **proved now:** identities, hashes, unchanged path sets, absence of deny
  literal in Amendment JSON, two-phase gate structure, zero evidence requests,
  frozen future test contract, and no downstream outputs;
- **condition for later Cursor execution:** actual RED and GREEN outputs,
  command-spy trace, pre-network authority manifest, evidence retrieval,
  quotas, five-layer bindings, and payload/handoff checks;
- **not authorized:** running Cursor or evidence acquisition.

The report must state that an unrelated stale ref is outside the execution
closure only while no command enumerates, resolves, deletes, fetches, or reads
it.

- [ ] **Step 4: Create the audit report and validate it**

The report contains:

1. fixed identity table;
2. three-commit parent-chain table;
3. original contract and failure-provenance hash table;
4. Amendment JSON hash table;
5. superseded/preserved clause matrix;
6. bootstrap/pre-network gate review;
7. occurrence-policy proof;
8. future test-contract matrix;
9. R2, quota, blind, transport, readiness, and downstream confirmations;
10. limitations and stop conditions;
11. formal verdict.

Run:

```bash
rtk python3 -c 'from pathlib import Path
p = Path("docs/review_20260805/gate_supplemental_r3_ref_isolation_amendment_audit.md")
t = p.read_text()
for token in ("T"+"BD", "TO"+"DO", "implement"+" later", "fill in"+" details"):
    assert token not in t
assert "R3_REF_ISOLATION_AMENDMENT_FEASIBLE_WITH_CONDITIONS" in t or "R3_REF_ISOLATION_AMENDMENT_BLOCKED" in t
assert "Local Desktop audit does not claim future RED-to-GREEN execution" in t
assert not any(line.endswith(" ") or line.endswith("\t") for line in t.splitlines())
print("audit-report: PASS")'
rtk proxy git diff --check
```

Expected: `audit-report: PASS` and no diff-check output.

- [ ] **Step 5: Commit the direct-child audit**

Stage only the audit report and commit:

```bash
rtk git add docs/review_20260805/gate_supplemental_r3_ref_isolation_amendment_audit.md
rtk git diff --cached --name-status
rtk proxy git diff --cached --check
rtk git commit -m "audit: verify supplemental r3 ref isolation amendment"
```

Assert its sole parent is the materialization commit and its only changed path
is the audit report.

- [ ] **Step 6: Push once and verify remote terminal state**

Push:

```bash
rtk proxy env GIT_TERMINAL_PROMPT=0 git push -u origin codex/phase3-supplemental-r3-ref-isolation-amendment
```

Use local `gh` to run:

```bash
rtk gh api repos/meng004/P3-Semantic-Mutation/git/ref/heads/codex/phase3-supplemental-r3-ref-isolation-amendment --jq .object.sha
rtk gh api 'repos/meng004/P3-Semantic-Mutation/commits/codex%2Fphase3-supplemental-r3-ref-isolation-amendment' --jq '{sha: .sha, parents: [.parents[].sha]}'
rtk gh pr list --repo meng004/P3-Semantic-Mutation --state all --head codex/phase3-supplemental-r3-ref-isolation-amendment --json number,state,url,headRefOid
```

Expected: both remote reads equal the full SHA printed by
`rtk git rev-parse HEAD`, the sole parent equals the materialization commit,
and the PR list is `[]`.

Stop. Do not generate or execute Cursor instructions in this plan.

## Plan self-review checklist

- [ ] Every requirement in the approved design spec maps to a task above.
- [ ] No existing frozen file is listed for modification.
- [ ] Amendment JSON does not repeat the deny SHA.
- [ ] Bootstrap and pre-network gates are separately materialized and audited.
- [ ] Local Desktop does not claim future RED-to-GREEN execution.
- [ ] The materialization and audit commits preserve the approved three-commit topology.
- [ ] All commands for Local Desktop use the `rtk` prefix.
- [ ] No evidence acquisition or downstream action is included.
