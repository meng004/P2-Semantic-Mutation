# P3 v3 Phase 0 authority: Blinded bridge and phase-separated package policy

> Authority ID: p3-v3-phase0-package-policy-v1
> Date frozen: 2026-08-12
> Governing plan: docs/superpowers/plans/2026-08-08-p3-semantic-mutant-argumentation-experiment.md
> Governing plan SHA-256: fea00496801c31ba074aa74742f5e6a77019ffc2e344642122a15462d7443830
> Source sections (verbatim, 1-based inclusive plan lines): Section 5.1.1 P12-bound blinded fixed-snapshot bridge (L250-L307); Section 12 Non-circular mapping of P12 faults (L998-L1055)
> Scope: verbatim extract for hash-binding and operational reference; the
> governing plan remains the sole scientific authority. All claims remain
> blocked (research/evidence/p3_claim_ledger_v1.3.0.yml).

### 5.1.1 P12-bound blinded fixed-snapshot bridge

P3 needs repaired source code for controlled construction but must not receive
the corresponding defect, patch, reference MR, or outcome. An identified P12
custodian therefore publishes a bridge before P3 construction begins. The bridge
envelope is bound to the immutable successor P12 package and contains:

- `p12_package_root_sha256` and the compatible contract hash;
- the complete eligible-inventory root and item count;
- one record for every eligible P12 fixed-version snapshot; P3 later groups
  records resolving to the same controlled subject;
- for each visible record, a `fixed_tree_commitment`, normalized source-tree
  SHA-256, source archive hash, build descriptor hash, and eligibility reason;
- a deterministic `neutral_snapshot_id` derived from the package root and
  normalized source-tree/source-archive hashes; and
- a `PINNED_GIT_RELEASE` identity containing the normalized P12 repository,
  release ID, P12 contract path and blob SHA, and benchmark package root.

The P3 consumer lock—not the bridge file itself—pins the exact release commit,
bridge path/blob SHA, contract path/blob SHA, and package root. Keeping the
release commit and bridge blob outside the bridge avoids a self-referential Git
object while still binding the bytes mechanically.

The visible bridge never contains the fixed Git tree OID. The custodian computes:

```text
fixed_tree_commitment = SHA256(
  "P3-FIXED-TREE-v1" || p12_package_root_sha256 ||
  fixed_git_tree_oid || reveal_nonce
)
```

Here `||` is byte concatenation; the domain and lowercase hexadecimal identities
are ASCII bytes, and `reveal_nonce` is exactly 32 random bytes.

The custodian keeps `fixed_git_tree_oid` and a fresh `reveal_nonce` sealed in Package C.
The bridge validator reads the bridge and P12 contract as exact blobs from the
pinned release commit and recomputes their Git blob identities. This
`PINNED_GIT_RELEASE` mode is the only accepted origin rule; the study introduces
no generic signing or PKI subsystem. If P12 cannot supply this pinned release
binding, primary RQ4 remains blocked.

The bridge excludes issue/PR identity, buggy commit, fixed commit, defect patch,
changed symbols, defect family, reference MR, and every outcome. From the
permitted fixed source, build metadata, dependency metadata, and public
documentation, P3 independently derives the Public Behavior Frame, Profiling
Workload, source scale, implementation-technique features, and canonical
mutation-site enumeration. The custodian does not assign workloads, strata, or
sites used for selection.

At Phase 7 the revealed mapping must cover every bridge record exactly once. For
each mapping, P3 verifies the reveal nonce, recomputes the commitment, verifies
the revealed fixed commit's Git tree OID, and recomputes the normalized source
tree. All must match the controlled snapshot. A missing record, an extra eligible
P12 item, or any commitment/tree mismatch is retained as an unpaired failure and
cannot be repaired by substituting another subject. A self-hash alone is not
accepted as evidence of origin or completeness.

## 12. Non-circular mapping of P12 faults

The P12-to-semantic-contract-family mapper consumes only frozen buggy/fixed
identities, the defect patch, independently recorded behavioral contract
metadata, and the operator catalogue. It cannot read MR source, MR identities,
or kill outcomes.

The mapper emits one of:

- `DIRECT`;
- `ADJACENT`;
- `OUT_OF_SCOPE`;
- `UNCERTAIN`.

Classification is rule-based and schema validated. Ambiguous multi-family cases
become `UNCERTAIN`; Grok or an author may explain an uncertainty but cannot
promote it into `P12_DIRECT`. All mapping states remain in the primary
family-agnostic `P12_PAIRED` analysis. The mapping registry and its hash are
frozen before any P12 MR outcome is opened to the analysis process.

After the P12 buggy layer is opened, a mechanical leakage audit compares every
controlled mutant with every paired real fault by exact patch hash, mutant tree,
changed-symbol set, and canonical semantic signature. Exact patch/tree matches
are tagged `REAL_FAULT_DUPLICATE_POSITIVE_CONTROL` and excluded from primary
incremental-value modelling; canonical-signature matches without exact identity
remain in a prespecified sensitivity analysis. Counts and exclusions are
reported, never replaced.

### 12.1 Phase-separated evidence partitions

Logical allowlists are supplemented by three content-addressed packages:

1. `PACKAGE_A_CONSTRUCTION`: fixed source snapshots, documentation, Public
   Behavior Frames, Profiling Workloads/results, frozen contracts, independent
   `E_COMMON` and `E_CONTRACT` inventories, and proposal inputs, with
   process-specific allowlists so the proposer cannot read profiling results or
   either input inventory;
   no `.git`, buggy revisions, MR files, reference-MR signatures, or outcomes;
2. `PACKAGE_B_CONTROLLED_EXECUTION`: certified original/mutant trees and the
   non-reference MR inventory, with `E_COMMON` as the only primary job input and
   `E_CONTRACT` confined to a separately labelled sensitivity inventory; no P12
   buggy tree or real-fault result;
3. `PACKAGE_C_REAL_HOLDOUT`: P12 buggy/fixed identities and execution material,
   mounted only after Packages A and B, controlled denominators, non-reference
   portfolios, and analysis code are sealed. Immediately after mounting, an
   isolated mapper and leakage-audit processes may read Package C, but no
   evaluated MR may execute on a P12 bug until their outputs are frozen.

Each package has an independent manifest and tree hash. Each phase process
receives only the package required by that phase. A clean verifier checks
absence, not merely non-use, of forbidden paths and identities.

The defensible claim is **phase-separated package and process isolation**. P3
may claim stronger platform-level physical absence only if the VM provisioner
produces an independently verifiable attestation of the newly created environment
and its mounted inputs. A directory scan, package self-hash, or Cursor conversation
statement does not by itself prove that the platform never possessed Package C.
