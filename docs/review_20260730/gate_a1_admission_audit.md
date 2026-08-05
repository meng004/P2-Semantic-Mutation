# Gate A1a — C2 Admission Candidate Audit (Pre-readiness)

- **Initial audit time:** 2026-08-01T10:08:35+08:00
- **Finding-closure re-review:** 2026-08-01T11:17:18+08:00
- **Scope:** C2 candidate adjudication before dual-arm readiness execution
- **Current verdict:** `PASS_WITH_DISCLOSURE`
- **Open blockers:** 0; all four initial blockers are closed
- **Successor state:** The corrected 32-row A1∧A3 queue is unlocked for C3 readiness only. No row is finally admitted and no canonical admission freeze exists.

## 1. Audited lineage

| Role | Commit |
|---|---|
| C2 branch | `origin/codex/gpt-desktop-phase3-5-c2-admission` |
| C2 baseline | `e5737f3c1c88641bc783bf8449fd7c53a6178df9` |
| Initial C2 payload commit | `90640368d21fe2087a266d8726ec81c2e9c2c124` |
| Initial C2 handoff commit | `f31a508ae6409c18dca8229fbabdf77598e0345d` |
| Correction payload commit | `964fcafcbd977004536979fab950aec88cec7b32` |
| Correction handoff commit | `d4967e1c8221318ab624957f29955dd323cc49d9` |
| Local initial payload integration | `c5425d51fbe4bc878634c44ec2386fe7fb78dc6e` |
| Local initial handoff integration | `2ad1d40dd103fb1469dc8c9f5c05fa1a308ff258` |
| Local correction payload integration | `7da7599b1db873bb9058126c907ced93f033157b` |
| Local correction handoff integration | `25ae6f5d364823722ac7e29999412972153f8518` |
| Current handoff manifest | `data/external_slice/HANDOFF_ADMISSION.json` at `d4967e1c8221318ab624957f29955dd323cc49d9` |
| Current handoff SHA256 | `d366e8271b2dab4f2f8aa0927df02212ef7decf807f699f85240a876ddb5ce13` |

Each handoff is the direct child of its payload, and the correction payload is
the direct child of the initial handoff. The full immutable C2 chain was
integrated in order after the correction passed re-review. The user explicitly
authorized C2 to run in a new Codex task/worktree; therefore the departure from
the original Cursor/Grok executor assignment remains a non-blocking disclosure,
not an unapproved executor substitution.

## 2. Hash, structure, and execution verification

### 2.1 Initial handoff

| Artifact | Independently verified SHA256 |
|---|---|
| Sanitized 64-row input | `34e819ccffca48afb260a3ef99b0f23ec6c1f4198106a4c74932a5eb0b9b6bac` |
| Separate 9-row supplemental input | `77f729b1297ef24d4223d5277b093c93ad84711dfbbe69a1927398d49d387a0a` |
| Candidate sheet | `79eb9de7f9d53d4b4b574aeace93f4b474849d13c686e94c3c005ed3e8aae802` |
| Evidence tree | `84823edab5dfb72e35c8f2c21af35e97f415937cba28fdab20f4c24c8f85d122` |
| Candidate checker | `cd84515e5247cb4a18640839a6048611b799353a8a5cb23aef742034f6c7d92e` |
| Checker tests | `21ef6abb7a9130fc5ef94df6e152a33cb40ecc49d35d0f3640f2989423d421b4` |
| Frozen external-slice protocol | `186b9734077035f63a1819569ecf45e645545862d045cb5ee899a7dd8f2841ca` |
| Admission runbook | `a3ced473d0d4ab91c39480bb59e7032c05bd15f68e57ee277da71582b3256f05` |

### 2.2 Correction handoff

| Artifact | Independently verified SHA256 |
|---|---|
| Sanitized 64-row input | `34e819ccffca48afb260a3ef99b0f23ec6c1f4198106a4c74932a5eb0b9b6bac` |
| Separate 9-row supplemental input | `77f729b1297ef24d4223d5277b093c93ad84711dfbbe69a1927398d49d387a0a` |
| Corrected candidate sheet | `4b0296c3656219e77a03acf1e9a727f574651bbaf1650ae07f31f2c47294adb8` |
| Corrected evidence tree | `854a2e06f97a2cf2928504be4a4d55afd327be2da31ad3cc7975924b45bc43ae` |
| Corrected candidate checker | `4fed32a87ac22c4e17ea13c735cfd65430e1abcf41e139484172320d59df1428` |
| Corrected checker tests | `ddcef0dd58c0e11b82aa4666ce38c6419661787b00fb97da59808e372d76b50e` |
| Correction handoff | `d366e8271b2dab4f2f8aa0927df02212ef7decf807f699f85240a876ddb5ce13` |

The correction evidence-tree hash uses paths relative to
`data/external_slice`, followed by NUL, each file SHA256, and newline, in sorted
order. Independent recomputation over 64 files reproduced `854a2e06...`.

The initial payload was archived into an isolated temporary directory before
running the checker and tests. The independent initial results were:

- exact 12-column schema;
- 64 Defect4MR rows, 64 unique neutral IDs, and 64 evidence directories;
- 9 supplemental pilot rows remained separate and shared no IDs with the 64;
- A1 distribution: 35 `PASS`, 29 `FAIL`;
- A2 distribution: 64 `PENDING`, 0 `PASS`, 0 `REPRO_FAILED`;
- A3 distribution submitted: 59 `PASS`, 5 `FAIL`;
- decision distribution submitted: 35 `ADMIT_PENDING_REPRO`, 29 `EXCLUDED`;
- 0 nonblank `analysis_id` values;
- targeted checker tests: `14 passed`;
- full suite: `255 passed, 10 warnings`;
- prohibited-vocabulary scan: no output, expected exit 1.

No `FREEZE.sha256`, canonical replacement of `admission_sheet.csv`, prediction,
kill result, or run artifact appears in the C2 diff.

## 3. Per-case evidence audit

The 64 case rows plus one aggregate verifier finding are recorded in
`gate_a1_findings.csv`. Each case row extracts the issue URL, public fix URL,
immutable buggy/fixed SHAs, submitted criteria, submitted decision, expected C2
dual-arm evidence state, independent criterion assessment, and any finding.

For all 35 submitted A1-pass rows, the public tracker entry was independently
resolved: 31 GitHub issue/PR pages, three GitLab issue pages, and one Netlib
LAPACK tracker entry were accessible. All 35 public fixed commits were also
resolved independently. In every case the fixed commit's first parent exactly
matched the recorded `buggy_sha` (32 GitHub and three GitLab parent checks).
The six rows using a fix PR recorded the PR merge commit exactly.

The submitted candidate and evidence rows were compared in source order with
all 64 sanitized records. Sixty-three records shared a public source URL with
their evidence file. `EXT-sundials-04` was the single non-overlap: its sanitized
source points to the v7.7.0 release/changelog while the evidence points directly
to commit `3fe0bcdd...`; the sanitized revision text itself names that exact
commit, so the current mapping was manually confirmed. This manual result does
not cure the verifier defect in finding `A1-SOURCE-BINDING-001`.

All 64 rows correctly leave A2 `PENDING`. This is the expected C2 mining state,
not evidence of final admission. A future successful Gate A1a may authorize only
the A1-and-A3-passing queue to enter C3. Final admission remains exactly
A1 ∧ A2 ∧ A3 after an auditable same-trigger two-arm reproduction. Until then,
no row is `ready`, no canonical admission freeze exists, and A2/C4 remains
locked.

## 4. Initial blockers and closure status

### A1-SCOPE-001 — `EXT-pocketfft-02` — CLOSED

The submitted mechanism is integer overflow in `good_size_*`, whose input and
output are `size_t`. The public fix adds typed unsigned-integer bounds and may
throw when the requested transform size is too large. This is an integer planning
helper, not a callable adaptable from float-vector input to float/few-float
output under the frozen A3 definition. Submitted `A3=PASS` and
`ADMIT_PENDING_REPRO` must become `A3=FAIL` and `EXCLUDED`.

### A1-SCOPE-002 — `EXT-blis-01` — CLOSED

The repaired BLIS `amaxv` contract returns the index of the first
maximum-magnitude or NaN element. Its observable result is an integer index, not
a float or few-float output. Under the frozen signature requirement this cannot
be admitted without an explicit amendment authorizing integer-index outputs.
Submitted `A3=PASS` and `ADMIT_PENDING_REPRO` must become `A3=FAIL` and
`EXCLUDED`, or the authors must amend the protocol before re-review.

### A1-SCOPE-003 — `EXT-petsc-04` — CLOSED

The public issue and fix concern the MPI communicator attached to ordering index
sets and dispatch of `MatGetOrdering`. The output is communicator/permutation
metadata, not a float/few-float numerical-kernel result. Submitted `A3=PASS` and
`ADMIT_PENDING_REPRO` must become `A3=FAIL` and `EXCLUDED`.

### A1-SOURCE-BINDING-001 — checker cannot prove 64-member identity — CLOSED

`check_external_admission.py` confirms only that `source_index` equals the CSV
row position and that every evidence record carries the aggregate sanitized
manifest hash. It never binds an evidence record to the corresponding sanitized
member. A synchronized permutation, rename, or replacement of candidate and
evidence rows can therefore pass while violating the requirement that each of
the 64 source members was adjudicated exactly once. Add a non-leaking per-record
binding (for example a hash of the exact sanitized record) and negative tests
that swap two members; then rerun the full case audit.

Correction payload `964fcafc...` changes the three submitted A3 values to FAIL,
derives EXCLUDED decisions, adds per-record canonical source hashes with a
swap-negative test, and replaces the generic scope text with 64 case-specific
rationales. Independent recomputation confirmed 64 distinct record hashes and
64 distinct scope rationales. The required all-case review additionally found
`EXT-fftw-05`; its integer MPI size metadata was conservatively changed to A3
FAIL while its pre-existing A1 FAIL / EXCLUDED decision remained unchanged.

## 5. Non-blocking disclosures and hardening findings

- `A1-A2-PENDING-001`: all A2 values being `PENDING` is correct for C2 and is
  not a blocker by itself. It prohibits canonical freeze and limits the eventual
  unlock to C3 readiness only.
- `A1-EXECUTOR-SEPARATION-001`: the C2 branch/environment differs from the
  original Cursor/Grok assignment, but the user explicitly authorized a new
  Codex session for C2. Preserve this authorization disclosure downstream.
- `A1-VALIDATOR-SCOPE-001` — closed: the checker now rejects every non-PENDING
  A2 value and explicitly states that it cannot establish final admission or a
  canonical freeze.
- `A1-REAL-DEFECT-CHECK-001` — partially hardened and non-blocking: the checker
  now requires public issue/equivalent-tracker and fix URLs for A1 PASS. Hosting
  API resolution and `buggy_sha == first_parent(fixed_sha)` remain independent
  audit checks; all 35 current PASS rows were already verified.
- `A1-NEUTRAL-ID-CHECK-001` — closed for the current contract: negative tests
  reject the frozen category and analysis-alias prefixes, and all 64 current IDs
  remain neutral.
- `STARTUP-CONFLICT-001` remains unchanged and applies only before the Gate A2
  DEF-CAL draw; it does not alter this verdict.

## 6. Exact audit commands and results

```text
rtk git fetch origin
# exit 0; remote C2 ref resolved to f31a508a...
rtk git log --format='%H %P %s' -2 f31a508ae6409c18dca8229fbabdf77598e0345d
# exit 0; handoff -> payload -> passed A0 baseline
rtk git diff --name-status e5737f3c1c88641bc783bf8449fd7c53a6178df9..f31a508ae6409c18dca8229fbabdf77598e0345d
# exit 0; candidate sheet, 64 evidence files, checker/test, handoff only
rtk shasum -a 256 data/external_slice/admission_sheet.cursor_candidate.csv scripts/check_external_admission.py tests/external_slice/test_check_external_admission.py data/external_slice/defect4mr_import/candidates_sanitized.json data/external_slice/admission_sheet.csv
# exit 0; hashes match HANDOFF_ADMISSION.json
rtk rg --files data/external_slice/admission_evidence | rtk sort | rtk xargs rtk shasum -a 256 | rtk shasum -a 256
# exit 0; 84823edab5df... aggregate hash
rtk env PYTHONPATH=src /Users/limeng/Papers/P3-SemanticMutation/.venv/bin/python scripts/check_external_admission.py --sheet data/external_slice/admission_sheet.cursor_candidate.csv
# exit 0; 64 candidate rows, 64 evidence records, 9 separate pilot rows
rtk env PYTHONPATH=src /Users/limeng/Papers/P3-SemanticMutation/.venv/bin/python -m pytest tests/external_slice/test_check_external_admission.py -q
# exit 0; 14 passed
rtk env PYTHONPATH=src /Users/limeng/Papers/P3-SemanticMutation/.venv/bin/python -m pytest -q
# exit 0; 255 passed, 10 warnings
rtk rg -n -i 'mr_mapping|proposed_mr_oracle|\bkill\b|\bfiber\b|\boperator\b|prediction|analysis_id[^,]*[^,[:space:]]' data/external_slice/admission_sheet.cursor_candidate.csv data/external_slice/admission_evidence
# exit 1; no output (expected clean result)
rtk gh api repos/<owner>/<repo>/commits/<fixed_sha> --jq '[.sha,.parents[0].sha,.html_url,.commit.message]|@tsv'
# 32/32 GitHub fixed commits resolved; 32/32 first parents matched buggy_sha
rtk curl -sS https://gitlab.com/api/v4/projects/<project>/repository/commits/<fixed_sha>
# 3/3 GitLab fixed commits resolved; 3/3 first parents matched buggy_sha
```

Correction re-review commands:

```text
rtk shasum -a 256 data/external_slice/HANDOFF_ADMISSION.json data/external_slice/admission_sheet.cursor_candidate.csv scripts/check_external_admission.py tests/external_slice/test_check_external_admission.py
# exit 0; correction hashes matched handoff
rtk env PYTHONPATH=src /Users/limeng/Papers/P3-SemanticMutation/.venv/bin/python scripts/check_external_admission.py --sheet data/external_slice/admission_sheet.cursor_candidate.csv
# exit 0; pre-readiness C2 candidate only; 64 rows, 64 bound evidence records, 9 separate pilot rows
rtk env PYTHONPATH=src /Users/limeng/Papers/P3-SemanticMutation/.venv/bin/python -m pytest tests/external_slice/test_check_external_admission.py -q
# exit 0; 19 passed
rtk env PYTHONPATH=src /Users/limeng/Papers/P3-SemanticMutation/.venv/bin/python -m pytest -q
# exit 0; 260 passed, 10 warnings
rtk rg -n -i 'mr_mapping|proposed_mr_oracle|\bkill\b|\bfiber\b|\boperator\b|prediction|analysis_id[^,]*[^,[:space:]]' data/external_slice/admission_sheet.cursor_candidate.csv data/external_slice/admission_evidence
# exit 1; no output (expected clean result)
```

## 7. Initial verdict and required correction (historical)

At audit commit `c18d9cdb...`, Gate A1a was `BLOCKED`. The C2 payload and handoff
were not integrated, C3 was not unlocked, and no canonical admission artifact or
freeze was generated.

A correction handoff must:

1. correct the three A3 rows and derived decisions, or provide a frozen author
   amendment where applicable;
2. re-review all submitted A3-pass rows with case-specific rationales;
3. add auditable per-member source binding and a swap-negative test;
4. harden public-issue and neutral-ID checks;
5. rerun the targeted checker, full suite, hash verification, and leakage scan;
6. preserve all 64 rows, all failures, blank analysis aliases, and the separate
   nine-row supplemental pilot.

Only a zero-blocker re-review may integrate the candidate payload and authorize
the corrected A1∧A3 queue to enter C3. Canonical `admission_sheet.csv` and
`FREEZE.sha256` remain deferred until C3 supplies final A2 evidence.

## 8. Finding-closure re-review

### 8.1 Reproduced results

The correction handoff was independently archived and tested. Results:

- exact handoff SHA256 `d366e827...` and all declared output hashes matched;
- checker passed with its explicit pre-readiness-only notice;
- targeted tests: `19 passed`;
- full suite: `260 passed, 10 warnings`;
- leakage scan: no output, expected exit 1;
- 64 candidate rows, 64 bound evidence files, 64 distinct per-record source
  hashes, and 64 distinct case-specific scope rationales;
- corrected distributions: A1 35/29, A2 64 PENDING, A3 55/9, decisions 32/32,
  and zero nonblank `analysis_id` values;
- the initial and corrected sheets retain identical row order, IDs, repositories,
  issue URLs, buggy/fixed SHAs, mechanisms, A1, A2, and blank aliases; only the
  four audited A3 rows and their derived fields changed;
- no canonical sheet, freeze file, C3 reproduction, run artifact, Gate A1 report,
  or audit-ledger path changed in the correction branch.

The 35 public fixed-parent relationships verified during the initial audit were
unchanged by the correction. The offline checker still does not query hosting
APIs to prove those relationships; current-case parent verification therefore
remains an auditor responsibility and is carried as a disclosure, not a blocker.

### 8.2 Current verdict and unlock

Gate A1a now has zero open blockers and is `PASS_WITH_DISCLOSURE`.

The 32 rows satisfying submitted A1 PASS and corrected A3 PASS are authorized
only to enter C3 dual-arm readiness. All 64 rows remain A2 PENDING. No row is
finally admitted, no ready-count claim is permitted, and canonical
`admission_sheet.csv` / `FREEZE.sha256` remain deferred until C3 evidence has
been audited. A2/C4, fiber mapping, predictions, kill execution, and later gates
remain locked.
