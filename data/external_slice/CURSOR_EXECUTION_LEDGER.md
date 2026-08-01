# Cursor VM Execution Ledger (Phase 3–5)

Branch: `cursor/grok-phase3-5-execution`  
Baseline: `main@d91083af4b368457245adbcc4d55ac2b2f786822`  
Model: Grok 4.5 High Fast  
Cloud agent: `bc-0bd9c61b-5482-450b-8739-2da3e98dff82`

| task/gate | VM/session | baseline commit | exact command | environment | input hash | output hash | exit code | failure/retry | output commit | auditor verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| C0 / ledger | bc-0bd9c61b-5482-450b-8739-2da3e98dff82 | 785a95a4ba9f0b98403b6c65445f7f2eef602391 | create `data/external_slice/CURSOR_EXECUTION_LEDGER.md` | Python 3.12.3; Linux 6.12.94+ x86_64; gcc 13.3.0; pytest 233→241 | n/a | see HANDOFF_IMPORT.json | 0 | none | a789bcecbd9d0544c223d4401fa101909694fbbb | pending Gate A0 |
| C1 / A0 | bc-0bd9c61b-5482-450b-8739-2da3e98dff82 | 785a95a4ba9f0b98403b6c65445f7f2eef602391 | `PYTHONPATH=src python3 scripts/external_slice/import_defect4mr_pool.py --repo meng004/P12-Defect4MR --commit 2bf7c2401c846544e715d879eb639e8c3bf44067 --output data/external_slice/defect4mr_import/candidates_sanitized.json` | same + `github_token` Contents API | git_blob `1469a2e2b15dcb2cdf59d185f3ec92f58fb77189`; sha256 `0f797c10da5e7b3e12656f0062aa55b0dc3e31c701249ee5f05f4e744171786e` | sanitized sha256 `34e819ccffca48afb260a3ef99b0f23ec6c1f4198106a4c74932a5eb0b9b6bac` | 0 | 1 wording retry for reserved token in IMPORT_LOG | a789bcecbd9d0544c223d4401fa101909694fbbb | pending Gate A0 |

## C1 verification snapshot

- Census: 64 = 35 verified_full + 16 candidate_full + 12 rejected + 1 candidate_needs_oracle
- Leak grep over `data/external_slice/defect4mr_import`: no matches (exit 1)
- Pytest: `241 passed`
- Raw ledger copied into P3 tree: no
- Handoff manifest: `data/external_slice/HANDOFF_IMPORT.json`

## Session retirement

After push of C1, this VM/session requests local Gate A0 and must not start C2 admission in-session.


## C3 Batch 1 — digest-pinned readiness (this session)

| task/gate | VM/session | baseline commit | exact command | environment | input hash | output hash | exit code | failure/retry | output commit | auditor verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| C3 / A1b batch1 | bc-1d216e6e-25c0-46ef-9f68-b1d417f18f57 | 533f8e26cd7d87e48afaceaa9424a3f7ed38a997 | dual-arm rebuild for EXT-numpy-03, EXT-sundials-07, EXT-scipy-04; see HANDOFF_REPRO_BATCH1.json | Python host 3.12.3 + CPython 3.9.18; gcc 13.3; cmake 3.28.3; docker 29.1.3 (GHCR 403) | admission candidate sheet + Gate A1a unlock | readiness_batch1.json + reproduction/<id>/* + reproducers | 0 for host rebuilds; 1 for GHCR pull | GHCR 403 → host rebuild; py39 ssl rebuild; numpy submodule retry | see handoff after push | pending Gate A1b |

### Batch 1 snapshot

- Queue source: Gate A1a corrected 32-row A1∧A3 queue only
- Selected: 3 digest-pinned cases in that queue (content-matched)
- Results: 3/3 proposed `crit_dual_arm_repro=PASS` with same trigger/input/seed=0
- Candidate sheet A2 left `PENDING` (C2 checker contract); promotion deferred to Gate A1b
- Stopped after batch 1 push; C4 / labelling / category-map freeze / predictive freeze / detection runs not started


## C3 Batch 1 correction — Gate A1b finding fix (this session)

| task/gate | VM/session | baseline commit | exact command | environment | input hash | output hash | exit code | failure/retry | output commit | auditor verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| C3 / A1b batch1 correction | bc-1d216e6e-25c0-46ef-9f68-b1d417f18f57 | 607acb044856101d8744f62cd2f7173a396c99b5 | `python3 scripts/external_slice/rebuild_c3_batch1_provenance.py`; see per-case COMMANDS.json + BATCH1_COMMAND_LOG.json | host rebuild with hash locks; Python 3.9.18 / 3.12.3; gcc/g++/cmake recorded | blocked A1b report @6419fbe3 + prior batch1 artifacts | corrected reproduction locks/commands/environment + readiness_batch1.json | per-arm trigger exits buggy=1 fixed=0; GHCR pulls exit=1 | closes A1B-HANDOFF-CMD-001 and A1B-LOCK-PROVENANCE-001; Batch 2 still locked | see correction handoff after push | pending Gate A1b re-review |

### Correction snapshot

- Fresh reconstruction in `/tmp/c3_batch1_fix`
- Exact per-arm source/download/build/install/trigger/capture commands with exit codes committed
- Hash-locked requirements + source archive/tree hashes + SUNDIALS build-tool pins committed under each case `locks/`
- Candidate-sheet A2 remains PENDING; no Batch 2


## C3 Batch 2 — remaining 29-queue readiness (this session)

| task/gate | VM/session | baseline commit | exact command | environment | input hash | output hash | exit code | failure/retry | output commit | auditor verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| C3 / A1c batch2 | bc-1d216e6e-25c0-46ef-9f68-b1d417f18f57 | 09da03a4585130dfb57428983f05ef7a4fb914bc | `python3 scripts/external_slice/run_c3_batch2_readiness.py`; see HANDOFF_REPRO_BATCH2.json + per-case COMMANDS.json | host dual-arm; Python 3.12.3 / 3.9.18; g++/gfortran/cmake; Julia 1.10.5; no GPU; no riscv qemu | BATCH2_MEMBERSHIP.json frozen from Gate A1a queue minus Batch 1 | readiness_batch2.json + reproduction/<id>/* + reproducers/harnesses | see per-case trigger exits; platform gates recorded | no replacement; freia/eigen retries; sheet A2 PENDING | see handoff after push | pending Gate A1c |

### Batch 2 snapshot

- Queue source: Gate A1a corrected 32-row A1∧A3 queue minus Batch 1 three digest-pinned cases (29 frozen members)
- Membership freeze commit: c94684faadbb4b02f8685360255cc374c15183c8
- Results: proposed PASS/REPRO_FAILED only in readiness_batch2.json; candidate sheet A2 left PENDING
- Stopped after Batch 2 push; C4 / labelling / category-map freeze / predictive freeze / detection runs not started
