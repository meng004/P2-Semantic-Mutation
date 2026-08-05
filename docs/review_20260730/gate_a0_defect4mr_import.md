# Gate A0 — Defect4MR Sanitized Import Audit

**Audit time:** 2026-07-31T22:38:33+08:00  
**Verdict:** `PASS_WITH_DISCLOSURE`  
**Blockers:** 0  
**Successor state:** C2 / Gate A1 admission execution is unlocked in a new session.

## 1. Audited lineage

| Role | Commit |
|---|---|
| Cursor branch | `origin/cursor/grok-phase3-5-execution` |
| Cursor baseline | `785a95a4ba9f0b98403b6c65445f7f2eef602391` |
| Cursor payload commit | `a789bcecbd9d0544c223d4401fa101909694fbbb` |
| Cursor handoff commit | `e72faa2d7b7469eba75b8a4e240083dc76de90dd` |
| Local payload integration | `e3d9cdc673f92072ffefdcd1baafa295f1ee2cbb` |
| Local handoff integration | `2b35fd30fd96091ad835d194fc63a72b24794b02` |
| Handoff manifest | `data/external_slice/HANDOFF_IMPORT.json` at `e72faa2d7b7469eba75b8a4e240083dc76de90dd` |

The handoff commit is the direct child of the payload commit. The five Gate A0
required artifacts are unchanged between them.

## 2. Provenance and hash verification

| Artifact | Independently verified value |
|---|---|
| Source repository | `meng004/P12-Defect4MR` |
| Source commit | `2bf7c2401c846544e715d879eb639e8c3bf44067` |
| Source path | `data/ledgers/candidates.json` |
| Source Git blob | `1469a2e2b15dcb2cdf59d185f3ec92f58fb77189` |
| Source bytes SHA256 | `0f797c10da5e7b3e12656f0062aa55b0dc3e31c701249ee5f05f4e744171786e` |
| Import script SHA256 | `292a8da4840060a26dac8cc844ee52dff4d3d179828f93d3f5a88fa74658f16f` |
| Contract test SHA256 | `7ba189e6039abe63de3368349bd565daed4a6f7e7b2d6c18decc1aa156d5de5c` |
| Sanitized manifest SHA256 | `34e819ccffca48afb260a3ef99b0f23ec6c1f4198106a4c74932a5eb0b9b6bac` |
| Provenance SHA256 | `af7e9c522967bcccaba02db2361a1aadaf11fb64219b4a5bafcaab4cc89de152` |
| Import log SHA256 | `384134afddba35ca8e5e08d5965474ac9996a38e0d344165ce60dfe6af0834fe` |
| Final execution ledger SHA256 | `ca034af0cfeda092efce50524fc4165a453722bc70c6583fce402087e1acb74e` |
| Final handoff manifest SHA256 | `e96cf128d2642a139b10503163129e827ad0d38de9346cfd0bd518a8b3c2e3ef` |

The private GitHub contents endpoint independently resolved the pinned path at
the pinned commit to the declared blob. Decoding that blob independently
reproduced the declared source SHA256. An offline replay of the committed import
script over those bytes produced sanitized SHA256 `34e819...`; `cmp` confirmed
byte-for-byte identity with the committed manifest.

## 3. Gate checklist

| Requirement | Evidence | Result |
|---|---|---|
| Exact provenance | Repository, commit, path, blob and source SHA256 independently verified | PASS |
| Exactly 64 rows | `jq 'length'` returned `64` | PASS |
| Status distribution | 35 `verified_full`, 16 `candidate_full`, 12 `rejected`, 1 `candidate_needs_oracle` | PASS |
| Unique provisional IDs | 64 rows and 64 unique IDs | PASS |
| Field allowlist | Every row has exactly: `provisional_id`, `project`, `status`, `evidence_depth`, `source_urls`, `revisions`, `modified_files`, `exclusions_checked`; no extras | PASS |
| Leakage exclusion | Required `rg` pattern returned exit 1 with no output | PASS |
| Raw-ledger isolation | Diff and test scan show no raw `candidates.json` under the P3 tree | PASS |
| No admission judgment | Import code only fetches, pins, filters, validates and records provenance; the sanitized schema has no admission decision field | PASS |
| Import session retirement | Import log and handoff explicitly retire the C1 VM/session from later roles | PASS |
| Targeted tests | `8 passed` | PASS |
| Full suite | `241 passed, 10 warnings` | PASS |

The exact required leakage scan was:

```text
rtk rg -n -i 'mr_mapping|proposed_mr_oracle|reviewer_note|reproduction_risk|kill|fiber|analysis_id' data/external_slice/defect4mr_import
# exit 1; no output
```

The local audit used Python 3.11.9 on macOS; the Cursor handoff separately
records Python 3.12.3 on Linux with the same targeted and full-suite outcomes.

### Exact audit commands and exit codes

```text
rtk git show --stat --oneline e72faa2d
# exit 0
rtk git show --stat --oneline a789bcec
# exit 0
rtk git diff 785a95a4ba9f0b98403b6c65445f7f2eef602391..e72faa2d --name-status
# exit 0; seven added A0 handoff/payload paths

rtk gh api 'repos/meng004/P12-Defect4MR/contents/data/ledgers/candidates.json?ref=2bf7c2401c846544e715d879eb639e8c3bf44067' --jq '.sha + " " + .path'
# exit 0; 1469a2e2b15dcb2cdf59d185f3ec92f58fb77189 data/ledgers/candidates.json
rtk gh api repos/meng004/P12-Defect4MR/git/blobs/1469a2e2b15dcb2cdf59d185f3ec92f58fb77189 --jq .content | rtk base64 --decode | rtk shasum -a 256
# exit 0; 0f797c10da5e7b3e12656f0062aa55b0dc3e31c701249ee5f05f4e744171786e

rtk shasum -a 256 scripts/external_slice/import_defect4mr_pool.py tests/external_slice/test_import_defect4mr_pool.py data/external_slice/defect4mr_import/candidates_sanitized.json data/external_slice/defect4mr_import/PROVENANCE.json data/external_slice/defect4mr_import/IMPORT_LOG.md data/external_slice/CURSOR_EXECUTION_LEDGER.md data/external_slice/HANDOFF_IMPORT.json
# exit 0; values in §2
rtk jq 'length' data/external_slice/defect4mr_import/candidates_sanitized.json
# exit 0; 64
rtk jq 'group_by(.status) | map({status: .[0].status, count: length})' data/external_slice/defect4mr_import/candidates_sanitized.json
# exit 0; 35/16/12/1
rtk jq '{rows:length, unique_ids:([.[].provisional_id]|unique|length), all_key_sets:([.[]|keys]|unique)}' data/external_slice/defect4mr_import/candidates_sanitized.json
# exit 0; rows=64, unique_ids=64, one exact eight-key set
rtk rg -n -i 'mr_mapping|proposed_mr_oracle|reviewer_note|reproduction_risk|kill|fiber|analysis_id' data/external_slice/defect4mr_import
# exit 1; no output (required clean result)

rtk env PYTHONPATH=src /Users/limeng/Papers/P3-SemanticMutation/.venv/bin/python scripts/external_slice/import_defect4mr_pool.py --repo meng004/P12-Defect4MR --commit 2bf7c2401c846544e715d879eb639e8c3bf44067 --output /private/tmp/p3-a0-audit.6PXs1N/regen/candidates_sanitized.json --source-file /private/tmp/p3-a0-audit.6PXs1N/candidates.raw.json
# exit 0; replay SHA256 34e819ccffca48afb260a3ef99b0f23ec6c1f4198106a4c74932a5eb0b9b6bac
rtk cmp data/external_slice/defect4mr_import/candidates_sanitized.json /private/tmp/p3-a0-audit.6PXs1N/regen/candidates_sanitized.json
# exit 0; byte-identical
rtk env PYTHONPATH=src /Users/limeng/Papers/P3-SemanticMutation/.venv/bin/python -m pytest tests/external_slice/test_import_defect4mr_pool.py -q
# exit 0; 8 passed
rtk env PYTHONPATH=src /Users/limeng/Papers/P3-SemanticMutation/.venv/bin/python -m pytest -q
# exit 0; 241 passed, 10 warnings
```

## 4. Findings and disclosures

### A0-HANDOFF-SPLIT-001 — non-blocking disclosure

`HANDOFF_IMPORT.json` records `a789bcec...` as `output_commit`, while the final
`CURSOR_EXECUTION_LEDGER.md` hash belongs to its direct child `e72faa2d`. The
handoff manifest itself also correctly notes that its hash is self-referential.
This is a two-commit handoff expression, not a single-snapshot output commit.

This does not impair the method or the five required Gate A0 artifacts: all five
are identical in both commits and their hashes match the handoff. Downstream
records must preserve the distinction between payload commit `a789bcec...` and
handoff commit `e72faa2d`.

`STARTUP-CONFLICT-001` remains open only as a Gate A2 precondition: before the
DEF-CAL draw, the v1.0.0 release-manifest ID set and order must be crosswalked to
the pinned commit ledger. It is not an A0 blocker and does not alter A0
provenance.

## 5. Verdict and unlock

Gate A0 has zero blockers and passes with the handoff-split disclosure above.
The sanitized import is admitted to the single local lineage. C2 may start only
in a new session reading this integrated commit; the retired C1 VM/session must
not adjudicate admission.
