# Cursor VM Execution Ledger (Phase 3–5)

Branch: `cursor/grok-phase3-5-execution`  
Baseline: `main@d91083af4b368457245adbcc4d55ac2b2f786822`  
Model: Grok 4.5 High Fast  
Cloud agent: `bc-0bd9c61b-5482-450b-8739-2da3e98dff82`

| task/gate | VM/session | baseline commit | exact command | environment | input hash | output hash | exit code | failure/retry | output commit | auditor verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| C0 / ledger | bc-0bd9c61b-5482-450b-8739-2da3e98dff82 | 785a95a4ba9f0b98403b6c65445f7f2eef602391 | create `data/external_slice/CURSOR_EXECUTION_LEDGER.md` | Python 3.12.3; Linux 6.12.94+ x86_64; gcc 13.3.0; pytest 233→241 | n/a | see HANDOFF_IMPORT.json | 0 | none | pending fill | pending Gate A0 |
| C1 / A0 | bc-0bd9c61b-5482-450b-8739-2da3e98dff82 | 785a95a4ba9f0b98403b6c65445f7f2eef602391 | `PYTHONPATH=src python3 scripts/external_slice/import_defect4mr_pool.py --repo meng004/P12-Defect4MR --commit 2bf7c2401c846544e715d879eb639e8c3bf44067 --output data/external_slice/defect4mr_import/candidates_sanitized.json` | same + `github_token` Contents API | git_blob `1469a2e2b15dcb2cdf59d185f3ec92f58fb77189`; sha256 `0f797c10da5e7b3e12656f0062aa55b0dc3e31c701249ee5f05f4e744171786e` | sanitized sha256 `34e819ccffca48afb260a3ef99b0f23ec6c1f4198106a4c74932a5eb0b9b6bac` | 0 | 1 wording retry for reserved token in IMPORT_LOG | pending fill | pending Gate A0 |

## C1 verification snapshot

- Census: 64 = 35 verified_full + 16 candidate_full + 12 rejected + 1 candidate_needs_oracle
- Leak grep over `data/external_slice/defect4mr_import`: no matches (exit 1)
- Pytest: `241 passed`
- Raw ledger copied into P3 tree: no
- Handoff manifest: `data/external_slice/HANDOFF_IMPORT.json`

## Session retirement

After push of C1, this VM/session requests local Gate A0 and must not start C2 admission in-session.
