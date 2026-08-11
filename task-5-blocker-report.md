# Task 5 production-integration blocker report

## Scope and starting state

- Worktree: `/Users/limeng/Papers/P3-SemanticMutation/.worktrees/p3-v3-mef-align-repair-01`
- Starting commit: `9a280bcf26861625d8dc9084d6c033ae76dda0a9`
- Starting status: clean
- Read before implementation: the complete Exact cross-task contracts and Task 3,
  Task 4, and Task 5 briefs in
  `docs/superpowers/plans/2026-08-11-p3-v3-external-authority-lock-implementation.md`.
- Work remained offline and did not access P12, execute scientific jobs, install
  dependencies, push, open a PR, or merge.

## Focused RED evidence

Command:

```text
rtk env PYTHONPATH=src /opt/anaconda3/bin/python -m pytest \
  tests/p3_v3/test_cli.py::test_freeze_rq_markdown_bytes_are_the_claim_verifiers_authority \
  tests/p3_v3/test_cli.py::test_verify_evidence_accepts_locked_subject_root_profiling_cwd -q
```

Observed before the production fix: `2 failed`.

1. The real `freeze_authority_lock` path reached `prepare_authority` and failed
   on the Markdown RQ bytes with `E_AUTHORITY_LOCK_SCHEMA: protocol artifact
   rq_spec is not canonical JSON`.
2. The real `verify-evidence` CLI received the independently calculated literal
   SHA-256 of the lock bytes, authenticated the reclosed locked intents, and then
   failed with `E_PROFILE_ATTEMPT_BINDING` because profiling still compared the
   locked subject-root cwd with `controlled_subject_source_id`.

## Unique role-specific contracts

### RQ authority bytes

`rq_spec` is UTF-8 Markdown authority, not canonical JSON. Freeze reads its exact
regular-file bytes, validates the existing `### RQn：` role grammar, retains one
in-memory raw-authority envelope for PreparedAuthority validation, and commits
`SHA256(raw_rq_spec_bytes)` to the Authority Lock. Final claim reconstruction
reads and parses the byte-verified indexed copy through the same RQ parser. No
second persisted RQ artifact and no hand-authored lock are introduced. All other
protocol roles remain canonical JSON under their existing role-specific
validators.

### Subject-root cwd authority

For every locked intent derived from `cwd_role = SUBJECT_ROOT`, the sole stored
cwd identity is `subject:<subject_id>`. Final verification first authenticates
the complete intent against the Authority Lock and binds indexed subjects
one-to-one by `subject_id`; profiling then checks that locked subject identity.
`controlled_subject_source_id` remains a 64-hex source/material identity but is
not cwd authority.

## Minimal implementation

- `scripts/p3_v3/evidence.py`
  - treats only `rq_spec` as exact raw UTF-8 Markdown authority;
  - validates the raw envelope and digest in PreparedAuthority;
  - shares one RQ-heading parser between freeze preparation and claim
    reconstruction;
  - checks profiling cwd against `subject:<subject_id>`.
- `tests/p3_v3/test_cli.py`
  - adds the focused freeze/literal-digest/claim-reconstruction regression;
  - adds a real final-verifier regression with a literal external digest;
  - aligns Task 2/3 prepared-authority and profiling fixtures with the frozen
    contracts.
- `tests/p3_v3/test_synthetic_phase_path.py`
  - aligns the pending Task 5 profiling attempt fixture with
    `subject:<subject_id>`; the Task 5 fixture agent still owns the complete V3
    synthetic-path migration and matrix.

## GREEN and regression evidence

- Focused blocker nodes: `2 passed`.
- Task 3 freezer/lock/job selection over `test_cli.py`, `test_artifacts.py`, and
  `test_run_records.py`: `146 passed, 243 deselected`.
- Task 4 full regression over `test_cli.py`, `test_preflight.py`, and
  `test_run_records.py`: `401 passed`.
- Full `test_artifacts.py`: `32 passed`.
- Ruff 0.15.12 on all changed Python files: `All checks passed!`.
- `git diff --check`: clean.

Scientific claims remain blocked. These changes establish production contracts
only; they do not create scientific evidence or attest physical absence of P12
access.
