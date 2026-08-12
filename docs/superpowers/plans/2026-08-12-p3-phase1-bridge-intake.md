# P3 Phase 1 Bridge Intake Runbook (Charter Task 3)

- Date: 2026-08-12
- Scope: what the P12 custodian must produce and deliver so P3 can run
  `verify-bridge` and start Phase 1 (scientific plan §5.1.1, §14 Phase 1).
- Helper: `scripts/p3_v3/build_p12_bridge.py` (computes every hash with the
  frozen P3 formulas; end-to-end smoke-verified on 2026-08-12:
  build → commit → lock → `verify-bridge` PASS).
- Custodian: the P12 Defect4MR maintainer. Local repo:
  `/Users/limeng/Papers/P12-Defect4MR`
  (normalized identity `github.com/meng004/P12-Defect4MR`).

## 0. Decision gates (custodian answers before building)

1. **Governing contract** (remediation-matrix row 38): either an explicitly
   compatible successor P12 contract, or the frozen v1.1.2 contract under its
   own estimand (conservative default; primary RQ4 stays within v1.1.2
   semantics). The chosen contract file must live in the P12 repository at
   `p12_contract_path`. If v1.1.2 is chosen, the file must be byte-identical
   to P3's frozen copy
   (`docs/protocols/P3_P12_CONSUMER_ACCEPTANCE_DATA_USE_PROTOCOL_v1.1.2.md`,
   SHA-256 `6247f3063952fa7c133ca574b5f9667c51b8d4636d84c40bce2753cf9e8bc427`).
   If a successor contract is chosen, P3 re-emits the Phase 0 protocol (V3)
   to bind it before Phase 1 runs.
2. **Eligible inventory**: every eligible P12 item appears as one record for
   its fixed-version snapshot, with `eligible_for_construct` /
   `eligible_for_criterion` set per the P12 admission rule. The inventory is
   complete and immutable: no later substitution, no repair by swapping
   subjects. (RQ4's existing confirmatory floor is 17 projects / 60 families;
   a smaller honest inventory is acceptable and is reported as a power
   limitation.)
3. **Package root method**: `p12_package_root_sha256` identifies the
   immutable P12 package. Either supply the value directly or point the
   helper at `package_manifest_root` (it hashes a canonical
   `{path, byte_sha256}` manifest, domain `P12-PACKAGE-ROOT-v1`). The method
   is recorded in `receipts.txt` and must be published with the release.

## 1. Blinding rules (hard constraints)

- Snapshot directories and archives contain **only fixed-version source**:
  no `.git`, no buggy revision, no defect patch, no issue/PR identity, no
  defect family, no reference MRs, no outcomes.
- No transient outputs in snapshots (`build/`, `dist/`, `__pycache__/`,
  `.venv/`, `node_modules/`, …): the normalized-tree hash fails closed on
  them.
- `reveal_ledger.SEALED.json` (tree OIDs + nonces) is **Package C
  material**: custodian keeps it sealed until the Phase 7 reveal. Never
  deliver it with the bridge.
- Do not tell P3 which record corresponds to which defect, project, or
  release note. Record labels exist only in the custodian config and the
  sealed ledger.

## 2. Per-record materials (for every eligible fixed snapshot)

| Material | How to produce | Bound as |
|---|---|---|
| Fixed tree OID | in the subject repo: `git rev-parse '<fixed_commit>^{tree}'` | sealed ledger + commitment |
| Snapshot dir | `git archive --format=tar <tree_oid> \| tar -x -C <dir>` | `normalized_source_tree_sha256` |
| Source archive | the same `git archive --format=tar <tree_oid> > <name>.tar` | `source_archive_sha256` (delivered to P3) |
| Build descriptor | canonical JSON (sorted keys, compact `,`/`:` separators, one trailing LF), e.g. `{"ecosystem":"python"}` + build metadata; must not carry discovery fields (declarations/sites/schemas…) | `build_descriptor_sha256` (delivered to P3) |
| Eligibility | reason string + two booleans | bridge record |

The helper derives `neutral_snapshot_id`, draws a fresh 32-byte nonce, and
computes `fixed_tree_commitment = SHA256("P3-FIXED-TREE-v1" ||
package_root_hex || tree_oid_hex || nonce_bytes)`.

## 3. Custodian procedure

1. Prepare per-record materials (§2) and write `custodian_config.json`
   (schema in the helper docstring).
2. Run (from the P3 checkout):
   `/opt/anaconda3/bin/python scripts/p3_v3/build_p12_bridge.py
   --config <config.json> --output-dir <out>`
   → `bridge.json`, `consumer_lock.template.json`,
   `reveal_ledger.SEALED.json`, `receipts.txt`.
3. In the P12 repository: place `bridge.json` at the lock template's
   `bridge_path` (default `bridge/p3_bridge_v1.json`) and the contract at
   `p12_contract_path`; commit; record `git rev-parse HEAD`.
4. Fill `release_commit_sha` in the lock template (keep canonical JSON), save
   as `consumer_lock.json`.
5. Seal `reveal_ledger.SEALED.json` custodian-side (Package C).
6. Deliver to P3: the P12 checkout (or its commit fetched locally),
   `consumer_lock.json`, all source archives, all build descriptors.
   Suggested layout: `data/p3_v3/p12_intake/{consumer_lock.json,
   archives/, descriptors/}`.

## 4. P3-side verification (intake gate)

```bash
PYTHONPATH=src /opt/anaconda3/bin/python scripts/p3_v3/evidence.py \
  verify-bridge \
  --repo-root /Users/limeng/Papers/P12-Defect4MR \
  --lock data/p3_v3/p12_intake/consumer_lock.json \
  --output data/p3_v3/p12_intake/verified_bridge.json
```

Expected: `{"status": "PASS", "bridge_sha256": "<64 hex>"}`. The verifier
re-resolves the pinned commit, re-derives both Git blob OIDs, re-checks the
bridge self-hash, every record's neutral ID, the inventory root/count, and
commitment uniqueness. Avoid symlinked output parents (macOS: use
`/private/tmp/...` or a workspace path; the atomic writer rejects symlink
components by design).

After PASS, P3 additionally checks each delivered archive/descriptor hash
against its bridge record before any Phase 1 derivation.

## 4.1 Parallel prep status (2026-08-12 night, while a P12 VM task runs)

Read-only custodian prep was executed in the neutral workdir
`~/Papers/p12-bridge-workdir/` (outside both repositories; its
worksheet/resolved files map records to defects and must never enter the P3
evidence chain):

- `worksheet.json` — all 35 `verified_full` items extracted from
  `data/ledgers/candidates.json` with repo/commit/ecosystem guesses
  (ecosystem distribution: cmake 24, autotools 4, julia 3, python 4; three
  records need repo-URL confirmation: E-PETSC-001, E-PETSC-004,
  F-EIGEN-001 — GitLab-hosted).
- `export_snapshots.py` — per-record upstream partial clone → fixed-commit
  and tree-OID resolution → `git archive` delivery archive → snapshot dir →
  canonical build descriptor; `--emit-config` assembles
  `custodian_config.json`.
- Pilot receipt (B-POCKETFFT-001): commit `fb21e4016b96`, tree
  `24341306a51e`, archive `41dd6ac3fbeb…`; snapshot passes P3's
  `canonical_source_tree_sha256`
  (`dd179f0a23cc71da6a7bf61de226a9396b732f91c8b2528c20150da8560a949e`).

Deferred until the running P12 task completes (repo writes / content-derived
values): committing the contract copy into the P12 repo, computing the
package root from release content, and the bridge release commit itself.

Load-bearing finding for Phase 1 (not for the bridge): with 24 cmake + 4
autotools subjects, the fail-closed CMAKE/MESON/AUTOTOOLS adapter stubs must
become real discovery rules before full-inventory frame derivation; the 3
julia subjects take the frozen `ADAPTER_UNSUPPORTED` path (no confirmatory
adapter by design); only 4 subjects are python-buildable today.

## 5. What P3 does next (no further custodian action)

Phase 1 frame derivation (scale, Public Behavior Frame, profiling-workload
selection, `E_COMMON`) runs from the verified bridge + archives under a new
task-scoped plan. The custodian returns only at Phase 7 with the sealed
reveal ledger.
