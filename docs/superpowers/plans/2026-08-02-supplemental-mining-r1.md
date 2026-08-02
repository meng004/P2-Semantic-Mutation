# Supplemental Mining R1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce an auditable, pre-readiness supplemental candidate handoff from six previously unmined whitelist repositories, increasing potential ready-project coverage without consulting or executing A2, category mapping, prediction, or detection results.

**Architecture:** A fresh Cursor VM freezes the search scope before network search, snapshots deterministic GitHub issue identifiers, reviews public issue/fix evidence under A1 and A3 only, and mechanically builds a separate candidate sheet whose A2 values are all `PENDING`. A dedicated checker binds every row to the frozen scope, search snapshot, review decision, and evidence record. Three commits preserve scope, payload, and handoff as separate audit stages.

**Tech Stack:** Python 3, pytest, GitHub CLI/REST API, CSV, JSON, SHA-256, Git.

## Global Constraints

- Execution environment: a fresh Cursor VM/session; do not reuse the Batch 3 readiness session.
- Branch: `cursor/grok-phase3-supplemental-mining-r1`.
- Immutable baseline: `0e208929ec4b6fc6ef8e49f6312c489be7ed4f8a` from `origin/codex/gpt-desktop-phase3-5`.
- Every shell command, including every pipeline component, must use the `rtk` prefix.
- Authority: `research/prereg_v2/external_slice_protocol.md` SHA256 `186b9734077035f63a1819569ecf45e645545862d045cb5ee899a7dd8f2841ca` and `docs/review_20260728/external_admission_runbook.md` SHA256 `a3ced473d0d4ab91c39480bb59e7032c05bd15f68e57ee277da71582b3256f05`.
- Existing 64-row candidate SHA256: `4b0296c3656219e77a03acf1e9a727f574651bbaf1650ae07f31f2c47294adb8`.
- Existing nine-row pilot SHA256: `77f729b1297ef24d4223d5277b093c93ad84711dfbbe69a1927398d49d387a0a`.
- Accepted readiness inputs remain immutable: Batch 1 SHA256 `9e56eef3d8e6fe4d908cf9c4d097835cb44303ee59ca2e1f10a3e35ea3df4a50`; Batch 2 SHA256 `7d922fca1cf87b6070c29173ad98003db5c70db182cad16755b77d35a06b1150`.
- This task may assess only A1 (public defect plus public fix) and A3 (float-vector to float/few-float numerical-kernel scope). Every A2 field must remain `PENDING`.
- Do not build either arm, write a reproducer, execute a trigger, inspect MR text, inspect mutation/kill data, assign a category, create an analysis alias, generate a prediction, or read detection results.
- Do not modify `data/external_slice/admission_sheet.csv`, `data/external_slice/admission_sheet.cursor_candidate.csv`, `data/external_slice/readiness_batch1.json`, `data/external_slice/readiness_batch2.json`, any reproduction artifact, `FREEZE.sha256`, annotation data, predictions, or runs.
- Preserve every reviewed exclusion. Do not replace excluded cases and do not search outside the frozen repositories or phrases.
- Stop after pushing the handoff commit. Local Desktop performs the admission gate before any new candidate may enter readiness.

## Fixed Scope and Stopping Rule

Repository order, canonical GitHub repository, and neutral-ID prefix:

| Order | Repository | Neutral-ID prefix | Scope restriction |
|---:|---|---|---|
| 1 | `pymc-devs/pymc` | `EXT-pymc-` | numerical kernels only |
| 2 | `cornellius-gp/gpytorch` | `EXT-gpytorch-` | numerical kernels only |
| 3 | `jonathf/chaospy` | `EXT-chaospy-` | numerical kernels only |
| 4 | `SALib/SALib` | `EXT-salib-` | numerical kernels only |
| 5 | `pytorch/pytorch` | `EXT-pytorch-` | linalg, optim, or special-function numerical components only |
| 6 | `jax-ml/jax` | `EXT-jax-` | linalg, optim, or special-function numerical components only |

Search phrases, in this exact order:

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

For every repository/phrase pair from `SCOPE.json`, construct the query from
the exact repository string and exact phrase string. For example, the first
query is:

```text
repo:pymc-devs/pymc is:issue is:closed created:<=2026-08-01 "wrong result"
```

The final query is the same fixed form using repository `jax-ml/jax` and phrase
`numerical instability`; the full Cartesian product contains exactly 66
queries.

Use GitHub Search API `sort=created`, `order=desc`, `per_page=20`. Store only issue identifiers, canonical URLs, timestamps, state, query provenance, and hashes of omitted public text; do not persist raw bodies, comments, or authentication material.

Within each repository, deduplicate by canonical issue URL and order the union by `(created_at descending, issue_number descending)`. Allocate neutral IDs in that order before A1/A3 decisions, starting at `01`; the current two admission sheets contain no IDs under any of the six new prefixes.

Review at most 20 unique issues per repository. Stop reviewing a repository at the first of:

1. five rows have A1 `PASS`, A3 `PASS`, A2 `PENDING`, and decision `ADMIT_PENDING_REPRO`;
2. 20 unique issues have been reviewed; or
3. the frozen deduplicated search union is exhausted.

All reviewed rows, including A1/A3 failures, must remain in the candidate sheet. Snapshot entries after the stopping point remain in the snapshot with `review_status=NOT_REVIEWED_AFTER_STOP`; they do not receive admission verdicts and do not enter the sheet. The target of five is an operational search budget, not a new scientific threshold and not a promise of readiness.

## File Map

Create:

```text
scripts/external_slice/mine_supplemental_r1.py
scripts/external_slice/check_supplemental_r1_admission.py
scripts/external_slice/check_supplemental_r1_handoff_hashes.py
tests/external_slice/test_mine_supplemental_r1.py
tests/external_slice/test_check_supplemental_r1_admission.py
data/external_slice/supplemental_r1/SCOPE.json
data/external_slice/supplemental_r1/SEARCH_SNAPSHOT.json
data/external_slice/supplemental_r1/REVIEW_QUEUE.json
data/external_slice/supplemental_r1/EVIDENCE_SNAPSHOT.json
data/external_slice/supplemental_r1/REVIEW_DECISIONS.json
data/external_slice/supplemental_r1/admission_sheet.cursor_candidate.csv
data/external_slice/supplemental_r1/admission_evidence/EXT-*/evidence.json
data/external_slice/supplemental_r1/COMMAND_LOG.json
data/external_slice/supplemental_r1/VERIFICATION_LOG.json
data/external_slice/supplemental_r1/HANDOFF_SUPPLEMENTAL_R1.json
```

Do not modify any pre-existing data file. The only pre-existing files permitted to change are none.

---

### Task 1: Initialize the isolated Cursor branch

**Files:** No files changed.

- [ ] **Step 1: Create the branch from the audited baseline**

```bash
rtk git fetch origin
rtk git switch -c cursor/grok-phase3-supplemental-mining-r1 0e208929ec4b6fc6ef8e49f6312c489be7ed4f8a
rtk git rev-parse HEAD
rtk git status --short --branch
```

Expected HEAD:

```text
0e208929ec4b6fc6ef8e49f6312c489be7ed4f8a
```

- [ ] **Step 2: Read governing documents without reading downstream results**

```bash
rtk sed -n '1,220p' research/prereg_v2/external_slice_protocol.md
rtk sed -n '1,260p' docs/review_20260728/external_admission_runbook.md
rtk sed -n '1,260p' data/external_slice/MINING_LOG.md
rtk sed -n '1,260p' docs/review_20260730/gate_a1c_readiness_batch2_audit.md
```

Do not open `data/external_slice/runs/`, predictions, category maps, MR text, or mutation/kill artifacts.

- [ ] **Step 3: Record environment and authenticate GitHub CLI**

```bash
rtk uname -a
rtk git --version
rtk python3 --version
rtk gh --version
rtk gh auth status
rtk gh api rate_limit --jq '{core:.resources.core,search:.resources.search,graphql:.resources.graphql}'
```

- [ ] **Step 4: Verify the baseline**

```bash
rtk shasum -a 256 research/prereg_v2/external_slice_protocol.md docs/review_20260728/external_admission_runbook.md data/external_slice/admission_sheet.cursor_candidate.csv data/external_slice/admission_sheet.csv data/external_slice/readiness_batch1.json data/external_slice/readiness_batch2.json
rtk env PYTHONPATH=src python3 -m pytest -q
```

Expected: the six hashes listed under Global Constraints and `260 passed`.

---

### Task 2: Freeze the search scope before network search

**Files:**
- Create: `data/external_slice/supplemental_r1/SCOPE.json`

**Interfaces:**
- Consumes: the exact baseline, repository list, phrases, and stopping rule above.
- Produces: immutable JSON consumed by every search, build, check, and handoff command.

- [ ] **Step 1: Create `SCOPE.json` with these exact semantic values**

```json
{
  "schema_version": 1,
  "task": "SUPPLEMENTAL_MINING_R1",
  "baseline_commit": "0e208929ec4b6fc6ef8e49f6312c489be7ed4f8a",
  "created_cutoff": "2026-08-01",
  "search_sort": "created",
  "search_order": "desc",
  "max_results_per_phrase": 20,
  "max_reviewed_per_repo": 20,
  "target_pending_per_repo": 5,
  "repositories": [
    {"repo": "pymc-devs/pymc", "id_prefix": "EXT-pymc-", "restriction": "numerical kernels only"},
    {"repo": "cornellius-gp/gpytorch", "id_prefix": "EXT-gpytorch-", "restriction": "numerical kernels only"},
    {"repo": "jonathf/chaospy", "id_prefix": "EXT-chaospy-", "restriction": "numerical kernels only"},
    {"repo": "SALib/SALib", "id_prefix": "EXT-salib-", "restriction": "numerical kernels only"},
    {"repo": "pytorch/pytorch", "id_prefix": "EXT-pytorch-", "restriction": "linalg, optim, or special-function numerical components only"},
    {"repo": "jax-ml/jax", "id_prefix": "EXT-jax-", "restriction": "linalg, optim, or special-function numerical components only"}
  ],
  "phrases": [
    "wrong result",
    "incorrect value",
    "numerical regression",
    "precision loss",
    "convergence failure",
    "conservation violation",
    "biased estimate",
    "wrong sign",
    "off by a factor",
    "accuracy regression",
    "numerical instability"
  ],
  "input_sha256": {
    "research/prereg_v2/external_slice_protocol.md": "186b9734077035f63a1819569ecf45e645545862d045cb5ee899a7dd8f2841ca",
    "docs/review_20260728/external_admission_runbook.md": "a3ced473d0d4ab91c39480bb59e7032c05bd15f68e57ee277da71582b3256f05",
    "data/external_slice/admission_sheet.cursor_candidate.csv": "4b0296c3656219e77a03acf1e9a727f574651bbaf1650ae07f31f2c47294adb8",
    "data/external_slice/admission_sheet.csv": "77f729b1297ef24d4223d5277b093c93ad84711dfbbe69a1927398d49d387a0a",
    "data/external_slice/readiness_batch1.json": "9e56eef3d8e6fe4d908cf9c4d097835cb44303ee59ca2e1f10a3e35ea3df4a50",
    "data/external_slice/readiness_batch2.json": "7d922fca1cf87b6070c29173ad98003db5c70db182cad16755b77d35a06b1150"
  },
  "forbidden_actions": [
    "A2 build or trigger execution",
    "reproducer creation",
    "MR or mutation/kill inspection",
    "category or analysis alias assignment",
    "prediction or detection-result access",
    "modification of existing admission, readiness, freeze, annotation, prediction, reproduction, or run artifacts"
  ]
}
```

- [ ] **Step 2: Validate and commit the scope before any search**

```bash
rtk python3 -m json.tool data/external_slice/supplemental_r1/SCOPE.json
rtk shasum -a 256 data/external_slice/supplemental_r1/SCOPE.json
rtk git diff --check
rtk git add data/external_slice/supplemental_r1/SCOPE.json
rtk git commit -m "data(external): freeze supplemental mining R1 scope"
```

Do not run a GitHub search before this commit exists.

---

### Task 3: Implement the deterministic miner and admission checker with TDD

**Files:**
- Create: `scripts/external_slice/mine_supplemental_r1.py`
- Create: `scripts/external_slice/check_supplemental_r1_admission.py`
- Create: `scripts/external_slice/check_supplemental_r1_handoff_hashes.py`
- Create: `tests/external_slice/test_mine_supplemental_r1.py`
- Create: `tests/external_slice/test_check_supplemental_r1_admission.py`

**Interfaces:**
- `mine_supplemental_r1.py search --scope PATH --snapshot PATH --queue PATH --command-log PATH`
- `mine_supplemental_r1.py collect-evidence --scope PATH --queue PATH --snapshot PATH --output PATH --command-log PATH`
- `mine_supplemental_r1.py validate-decisions --scope PATH --snapshot PATH --queue PATH --decisions PATH --existing-sheet PATH --pilot-sheet PATH`
- `mine_supplemental_r1.py build --scope PATH --snapshot PATH --decisions PATH --sheet PATH --evidence-root PATH`
- `check_supplemental_r1_admission.py --scope PATH --snapshot PATH --decisions PATH --sheet PATH --evidence-root PATH --existing-sheet PATH --pilot-sheet PATH`
- `check_supplemental_r1_handoff_hashes.py --handoff PATH`

- [ ] **Step 1: Write failing miner tests**

Tests must prove, using mocked GitHub responses:

```text
scope repository and phrase order is preserved
every query contains is:issue, is:closed, and created:<=2026-08-01
per_page is 20 and sort/order are created/desc
duplicate issue URLs collapse to one queue record
queue order is created_at descending then issue number descending
neutral IDs are assigned before decisions and start at 01 per repository
review stops at five eligible decisions, 20 reviewed issues, or exhaustion
records after the stop are retained as NOT_REVIEWED_AFTER_STOP
raw authentication values and raw issue bodies are never persisted
```

- [ ] **Step 2: Write failing checker tests**

Tests must reject:

```text
a repository or phrase outside SCOPE.json
a changed input hash or baseline
a neutral-ID collision with either existing admission sheet
a duplicate issue URL or duplicate nonblank buggy/fixed pair across any pool
an A2 value other than PENDING
ADMIT_PENDING_REPRO unless A1 and A3 both PASS
missing full buggy/fixed SHAs on an A1 PASS row
missing public issue and fix URLs on an A1 PASS row
nonblank analysis_id
a mechanism sentence or rationale containing reserved/downstream vocabulary
a sheet row without a matching evidence record
an evidence record whose scope/search/decision hashes do not match
more than five pending rows or more than 20 reviewed rows for one repository
loss of any reviewed exclusion
any modification of the six immutable baseline inputs
```

- [ ] **Step 3: Run the RED tests**

```bash
rtk env PYTHONPATH=src python3 -m pytest tests/external_slice/test_mine_supplemental_r1.py tests/external_slice/test_check_supplemental_r1_admission.py -q
```

Expected: failure because the scripts do not exist or required behavior is unimplemented. Record the exact result in `COMMAND_LOG.json` later as `TDD_RED`.

- [ ] **Step 4: Implement the three CLIs**

Implementation requirements:

- use `subprocess.run` with argument arrays, never shell interpolation;
- call `gh api -X GET search/issues` with fixed query fields;
- retain exact command, cwd, UTC timestamp, exit code, stdout SHA256, and sanitized stderr tail;
- never store an environment token or an authorization header;
- canonical JSON uses UTF-8, `sort_keys=True`, two-space indentation, and a trailing newline;
- canonical CSV uses the exact 12-column runbook header;
- evidence rows contain `source_pool=supplemental_mining_r1`, `scope_sha256`, `search_snapshot_sha256`, `review_decisions_sha256`, issue/fix URLs, full SHAs where A1 passes, three criteria, three case-specific rationales, evidence URLs, and the mechanism sentence;
- the handoff checker recomputes every declared file and per-case evidence SHA256 and exits nonzero on any mismatch.

- [ ] **Step 5: Run GREEN tests and compile checks**

```bash
rtk env PYTHONPATH=src python3 -m pytest tests/external_slice/test_mine_supplemental_r1.py tests/external_slice/test_check_supplemental_r1_admission.py -q
rtk python3 -m compileall -q scripts/external_slice/mine_supplemental_r1.py scripts/external_slice/check_supplemental_r1_admission.py scripts/external_slice/check_supplemental_r1_handoff_hashes.py
```

Expected: all targeted tests pass and compileall exits 0.

---

### Task 4: Execute the frozen search and collect public evidence

**Files:**
- Create: `SEARCH_SNAPSHOT.json`
- Create: `REVIEW_QUEUE.json`
- Create: `EVIDENCE_SNAPSHOT.json`
- Create/update: `COMMAND_LOG.json`

- [ ] **Step 1: Recheck repository identity and availability**

```bash
rtk gh repo view pymc-devs/pymc --json nameWithOwner,url,isArchived
rtk gh repo view cornellius-gp/gpytorch --json nameWithOwner,url,isArchived
rtk gh repo view jonathf/chaospy --json nameWithOwner,url,isArchived
rtk gh repo view SALib/SALib --json nameWithOwner,url,isArchived
rtk gh repo view pytorch/pytorch --json nameWithOwner,url,isArchived
rtk gh repo view jax-ml/jax --json nameWithOwner,url,isArchived
```

Expected: all six canonical names match and `isArchived=false`. If any repository is unavailable or renamed, stop and report a finding; do not substitute another repository.

- [ ] **Step 2: Run all 66 frozen searches**

```bash
rtk env PYTHONPATH=src python3 scripts/external_slice/mine_supplemental_r1.py search \
  --scope data/external_slice/supplemental_r1/SCOPE.json \
  --snapshot data/external_slice/supplemental_r1/SEARCH_SNAPSHOT.json \
  --queue data/external_slice/supplemental_r1/REVIEW_QUEUE.json \
  --command-log data/external_slice/supplemental_r1/COMMAND_LOG.json
```

The script must abort on any GitHub exit other than 0. Do not silently skip a failed phrase. A retry may occur only with the identical query and must remain in the command log.

- [ ] **Step 3: Collect issue, timeline, fix, parent, and patch metadata for the review queue**

```bash
rtk env PYTHONPATH=src python3 scripts/external_slice/mine_supplemental_r1.py collect-evidence \
  --scope data/external_slice/supplemental_r1/SCOPE.json \
  --queue data/external_slice/supplemental_r1/REVIEW_QUEUE.json \
  --snapshot data/external_slice/supplemental_r1/SEARCH_SNAPSHOT.json \
  --output data/external_slice/supplemental_r1/EVIDENCE_SNAPSHOT.json \
  --command-log data/external_slice/supplemental_r1/COMMAND_LOG.json
```

The evidence snapshot must record public URLs, immutable commit identities, changed-file paths, status/merge metadata, and hashes of fetched public text/diffs. It must not store raw issue bodies, comments, patches, credentials, or downstream study data.

- [ ] **Step 4: Validate the mechanical search outputs**

```bash
rtk python3 -m json.tool data/external_slice/supplemental_r1/SEARCH_SNAPSHOT.json
rtk python3 -m json.tool data/external_slice/supplemental_r1/REVIEW_QUEUE.json
rtk python3 -m json.tool data/external_slice/supplemental_r1/EVIDENCE_SNAPSHOT.json
rtk python3 -m json.tool data/external_slice/supplemental_r1/COMMAND_LOG.json
rtk shasum -a 256 data/external_slice/supplemental_r1/SCOPE.json data/external_slice/supplemental_r1/SEARCH_SNAPSHOT.json data/external_slice/supplemental_r1/REVIEW_QUEUE.json data/external_slice/supplemental_r1/EVIDENCE_SNAPSHOT.json data/external_slice/supplemental_r1/COMMAND_LOG.json
```

---

### Task 5: Adjudicate A1 and A3 without executing A2

**Files:**
- Create: `data/external_slice/supplemental_r1/REVIEW_DECISIONS.json`

**Interfaces:**
- Consumes: the frozen queue and evidence snapshot.
- Produces: one decision for every reviewed queue record through each repository's stopping point.

- [ ] **Step 1: Review records strictly in queue order**

For each record, inspect only the public issue page, public fix/PR metadata, immutable patch metadata, and relevant source signature. Apply exactly:

- A1 PASS only when a public defect report and identifiable public fix commit are linked. `fixed_sha` is the merged fix commit, or the immutable unmerged head only where the runbook permits it; `buggy_sha` is its first parent.
- A3 PASS only for a numerical kernel adaptable from float-vector input to float or few-float output.
- A2 is always `PENDING`; its rationale states that no same-trigger dual-arm result is claimed in this task.
- Decision is `ADMIT_PENDING_REPRO` iff A1 and A3 pass; otherwise `EXCLUDED` with a case-specific reason.
- Mechanism sentence is one present-tense numerical-effect sentence with no category or downstream-testing language.

Each JSON decision must contain exactly:

```text
neutral_id, repo, issue_number, issue_url, fix_url, buggy_sha, fixed_sha,
mechanism_sentence, crit_real_defect, crit_dual_arm_repro, crit_in_scope,
decision, exclusion_reason, analysis_id, rationales, evidence_urls,
review_order, review_status
```

`analysis_id` is empty and `review_status` is `REVIEWED`. Keep every reviewed exclusion. Mark later queue entries mechanically as `NOT_REVIEWED_AFTER_STOP` in the queue, not in `REVIEW_DECISIONS.json`.

- [ ] **Step 2: Validate decision JSON before building outputs**

```bash
rtk python3 -m json.tool data/external_slice/supplemental_r1/REVIEW_DECISIONS.json
rtk env PYTHONPATH=src python3 scripts/external_slice/mine_supplemental_r1.py validate-decisions \
  --scope data/external_slice/supplemental_r1/SCOPE.json \
  --snapshot data/external_slice/supplemental_r1/SEARCH_SNAPSHOT.json \
  --queue data/external_slice/supplemental_r1/REVIEW_QUEUE.json \
  --decisions data/external_slice/supplemental_r1/REVIEW_DECISIONS.json \
  --existing-sheet data/external_slice/admission_sheet.cursor_candidate.csv \
  --pilot-sheet data/external_slice/admission_sheet.csv
```

Expected: exit 0. Any scope, order, duplicate ID/issue/SHA, A1/A3 logic, A2,
quota, cap, or loss-of-exclusion failure must be corrected before proceeding.

---

### Task 6: Build and verify the separate candidate payload

**Files:**
- Create: `admission_sheet.cursor_candidate.csv`
- Create: `admission_evidence/EXT-*/evidence.json`
- Create: `VERIFICATION_LOG.json`

- [ ] **Step 1: Build the candidate sheet and evidence tree mechanically**

```bash
rtk env PYTHONPATH=src python3 scripts/external_slice/mine_supplemental_r1.py build \
  --scope data/external_slice/supplemental_r1/SCOPE.json \
  --snapshot data/external_slice/supplemental_r1/SEARCH_SNAPSHOT.json \
  --decisions data/external_slice/supplemental_r1/REVIEW_DECISIONS.json \
  --sheet data/external_slice/supplemental_r1/admission_sheet.cursor_candidate.csv \
  --evidence-root data/external_slice/supplemental_r1/admission_evidence
```

- [ ] **Step 2: Run the dedicated checker**

```bash
rtk env PYTHONPATH=src python3 scripts/external_slice/check_supplemental_r1_admission.py \
  --scope data/external_slice/supplemental_r1/SCOPE.json \
  --snapshot data/external_slice/supplemental_r1/SEARCH_SNAPSHOT.json \
  --decisions data/external_slice/supplemental_r1/REVIEW_DECISIONS.json \
  --sheet data/external_slice/supplemental_r1/admission_sheet.cursor_candidate.csv \
  --evidence-root data/external_slice/supplemental_r1/admission_evidence \
  --existing-sheet data/external_slice/admission_sheet.cursor_candidate.csv \
  --pilot-sheet data/external_slice/admission_sheet.csv
```

Expected: exit 0 with counts for searched, deduplicated, reviewed, pending, excluded, and stopped-by reason per repository.

- [ ] **Step 3: Run the exact runbook reserved-term scan**

```bash
rtk rg -n '(?i)(^|[^[:alnum:]_])(C\x45|O\x53|H\x50|T\x46|S\x49|f\x69ber|strat\x75m)([^[:alnum:]_]|$)' data/external_slice/supplemental_r1/admission_sheet.cursor_candidate.csv data/external_slice/supplemental_r1/REVIEW_DECISIONS.json data/external_slice/supplemental_r1/admission_evidence
```

Expected: raw `rg` exit 1 and no output.

- [ ] **Step 4: Run token and prohibited-data scans**

```bash
rtk rg -n 'ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|Bearer [A-Za-z0-9][A-Za-z0-9._-]{15,}' data/external_slice/supplemental_r1
rtk rg -n -i 'mr_mapping|proposed_mr_oracle|reviewer_note|reproduction_risk|\bkill\b|prediction|detection_result' data/external_slice/supplemental_r1/admission_sheet.cursor_candidate.csv data/external_slice/supplemental_r1/REVIEW_DECISIONS.json data/external_slice/supplemental_r1/admission_evidence
```

Expected: each command returns raw `rg` exit 1 and no output.

- [ ] **Step 5: Prove existing evidence and later-stage paths are unchanged**

```bash
rtk git diff --quiet 0e208929ec4b6fc6ef8e49f6312c489be7ed4f8a -- data/external_slice/admission_sheet.csv
rtk git diff --quiet 0e208929ec4b6fc6ef8e49f6312c489be7ed4f8a -- data/external_slice/admission_sheet.cursor_candidate.csv
rtk git diff --quiet 0e208929ec4b6fc6ef8e49f6312c489be7ed4f8a -- data/external_slice/readiness_batch1.json data/external_slice/readiness_batch2.json data/external_slice/reproduction data/external_slice/FREEZE.sha256 data/external_slice/annotation data/external_slice/predictions_frozen.json data/external_slice/runs
```

Expected: all three commands exit 0.

- [ ] **Step 6: Run targeted and full tests**

```bash
rtk env PYTHONPATH=src python3 -m pytest tests/external_slice/test_mine_supplemental_r1.py tests/external_slice/test_check_supplemental_r1_admission.py -q
rtk env PYTHONPATH=src python3 -m pytest -q
rtk git diff --check
```

Expected: targeted tests pass, full suite is at least the 260-test audited baseline plus new tests, and diff check exits 0.

- [ ] **Step 7: Write `VERIFICATION_LOG.json`**

Record every verification command above with exact command string, cwd, timestamp, exit code, stdout/stderr tail, expected raw clean-scan exit 1, and normalized checker result. Do not claim a scan is clean only from a wrapper exit; retain the raw `rg` exit.

- [ ] **Step 8: Commit the complete payload**

```bash
rtk git add scripts/external_slice/mine_supplemental_r1.py scripts/external_slice/check_supplemental_r1_admission.py scripts/external_slice/check_supplemental_r1_handoff_hashes.py tests/external_slice/test_mine_supplemental_r1.py tests/external_slice/test_check_supplemental_r1_admission.py data/external_slice/supplemental_r1
rtk git commit -m "data(external): build supplemental mining R1 candidate"
```

Do not include the handoff manifest in this payload commit.

---

### Task 7: Create the immutable handoff, verify hashes, push, and stop

**Files:**
- Create: `data/external_slice/supplemental_r1/HANDOFF_SUPPLEMENTAL_R1.json`

- [ ] **Step 1: Create the handoff manifest**

It must record:

```text
task=SUPPLEMENTAL_MINING_R1
gate_requested=SUPPLEMENTAL_ADMISSION_R1
branch and full baseline/scope/payload commits
scope/search/queue/evidence/decision/sheet/evidence-tree hashes
repository-by-repository searched/deduplicated/reviewed/pending/excluded/stopped counts
exact command log and verification log paths
environment and GitHub CLI versions
all exits, failures, retries, and unresolved findings
all reviewed exclusions
confirmation that A2 is entirely PENDING
confirmation that no existing admission/readiness/freeze/downstream artifact changed
forbidden actions confirmed absent
successor lock: no readiness for new rows before local gate PASS
```

The handoff commit cannot embed its own SHA. Set `handoff_commit.value` to `SELF`, require its direct parent to equal the full payload commit, and explain resolution with `rtk git rev-parse HEAD`.

- [ ] **Step 2: Run the handoff hash checker**

```bash
rtk env PYTHONPATH=src python3 scripts/external_slice/check_supplemental_r1_handoff_hashes.py \
  --handoff data/external_slice/supplemental_r1/HANDOFF_SUPPLEMENTAL_R1.json
```

Expected: exit 0 and `HASH_CHECK_OK` with zero mismatches. If the checker writes a timestamped result, restore the committed candidate bytes before final hashing or exclude that result file from self-referential hashes.

- [ ] **Step 3: Perform final validation**

```bash
rtk python3 -m json.tool data/external_slice/supplemental_r1/HANDOFF_SUPPLEMENTAL_R1.json
rtk env PYTHONPATH=src python3 scripts/external_slice/check_supplemental_r1_admission.py \
  --scope data/external_slice/supplemental_r1/SCOPE.json \
  --snapshot data/external_slice/supplemental_r1/SEARCH_SNAPSHOT.json \
  --decisions data/external_slice/supplemental_r1/REVIEW_DECISIONS.json \
  --sheet data/external_slice/supplemental_r1/admission_sheet.cursor_candidate.csv \
  --evidence-root data/external_slice/supplemental_r1/admission_evidence \
  --existing-sheet data/external_slice/admission_sheet.cursor_candidate.csv \
  --pilot-sheet data/external_slice/admission_sheet.csv
rtk env PYTHONPATH=src python3 -m pytest -q
rtk git diff --check
```

- [ ] **Step 4: Commit only the handoff manifest**

```bash
rtk git add data/external_slice/supplemental_r1/HANDOFF_SUPPLEMENTAL_R1.json
rtk git commit -m "docs(external): hand off supplemental mining R1 for audit"
```

- [ ] **Step 5: Verify three-stage ancestry and push**

```bash
rtk git log -3 --oneline --decorate
rtk git diff --name-status 0e208929ec4b6fc6ef8e49f6312c489be7ed4f8a..HEAD
rtk git status --short --branch
rtk git push -u origin cursor/grok-phase3-supplemental-mining-r1
rtk git rev-parse HEAD
```

- [ ] **Step 6: Stop for local audit**

Report the full scope, payload, and handoff SHAs; per-repository counts; all failed/retried commands; checker/test results; and unresolved findings. Do not start dual-arm reproduction, do not merge into another branch, and do not open any downstream result artifact.

## Self-Review Checklist

- [ ] All six repositories are within protocol §2.1 and were independently confirmed active.
- [ ] No previously mined repository is silently substituted into R1.
- [ ] Search cutoff, phrase order, result cap, review cap, and pending quota are frozen before search.
- [ ] Search selection is independent of A2 outcomes because A2 is never run or read.
- [ ] All reviewed failures remain present; no convenience replacement occurs.
- [ ] Candidate and evidence schemas contain no category, alias, MR, kill, prediction, or result fields.
- [ ] Existing candidate, pilot, readiness, freeze, annotation, prediction, reproduction, and run paths are unchanged.
- [ ] Scope, payload, and handoff are three separate commits.
- [ ] The handoff declares all hashes and exact commands and the hash checker passes.
- [ ] The session stops after push for local Desktop audit.
