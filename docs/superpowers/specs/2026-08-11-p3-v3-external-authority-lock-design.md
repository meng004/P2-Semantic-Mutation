# P3 v3 External Authority Lock Design

## Material passport

- Date: 2026-08-11
- Repair task: `P3-V3-MEF-ALIGN-REPAIR-01-AUTHORITY-LOCK`
- Implementation base: `ca52482e35afb64b907fe0cdd4c0ff13f38c050e`
- Parent repair design SHA-256:
  `bd7f7f26cbc70fc81a797753507d5f4a2528064827cbd90989789c3afd7ede55`
- Parent implementation plan SHA-256:
  `18c28c68302933b96afd6f9666a7d47a5ca200aee1fa7491b586fed319ef86f5`
- Branch: `codex/p3-v3-mef-align-repair-01`
- Scope: design, implementation, synthetic fixtures, tests, and audit evidence
  needed to introduce an external Authority Lock.
- Prohibited: P12 access, network collection, real mutant or MR execution,
  scientific jobs, claim upgrades, manuscript results, push, PR, or merge.

## 1. Problem and governing decision

The former final-verification contract accepted one caller-controlled input:

```text
verify-evidence --index PATH
```

That interface can prove internal consistency but cannot prove an external
historical fact. A coordinated rewrite can change the origin receipt,
execution labels, protocol references, phase receipts, index, and every local
hash together. With no value fixed outside that rewrite, the verifier has no
independent basis for rejecting it.

The rejected V2 prototype attempted to reconstruct origin by executing commands
named by the index and by indexing a Git repository. That approach is invalid:

- indexed commands are an execution-injection surface;
- a repository and its claimed origin can be rewritten together;
- `.git` may contain symlinks, out-of-root metadata, and credentials;
- execution labels can be relabelled with the completion object; and
- self-hashes do not create an external trust root.

The governing decision is to add a canonical Authority Lock whose expected
SHA-256 is frozen outside the evidence package before evidence production. The
final verifier accepts the evidence index only under that independently supplied
digest.

## 2. Claim ceiling

This repair may establish only the following infrastructure claim:

> Given an independently frozen Authority Lock digest, the verifier detects
> divergence between the locked execution authority and the indexed evidence
> package.

It does not establish that an experiment ran, that P12 was accessed, that a
mutant or MR was effective, or that any RQ is supported. RQ1-RQ4 and every
scientific result claim remain `blocked`.

## 3. Trust model

### 3.1 Trusted inputs

The verifier trusts only:

1. its reviewed implementation bytes;
2. the literal expected Authority Lock SHA-256 supplied by an independently
   frozen execution plan or launch packet; and
3. the canonical Authority Lock bytes that match that literal digest.

The expected digest must not be read from the evidence index, the Authority
Lock itself, a repository config, an environment variable, or an evidence
artifact.

### 3.2 Untrusted inputs

The following are untrusted until reconstructed and compared with the lock:

- the evidence index and every artifact it names;
- receipts, ledgers, result rows, completion metadata, and self-hashes;
- repository paths, remotes, configs, worktrees, and Git metadata;
- job roles, execution classes, and P12-access labels declared by results; and
- all paths or command-like strings found in evidence.

### 3.3 Threats in scope

The design rejects:

- coordinated evidence/index/protocol resealing;
- coordinated execution-role and completion relabelling;
- origin receipt replacement;
- missing, extra, duplicated, or reordered locked jobs;
- symlink and special-node traversal;
- `.git` or credential material entering the evidence package; and
- attempts to make final verification execute index-supplied commands.

The design does not claim protection against compromise of the implementation
binary, the independently frozen launch packet, or the process that freezes the
expected digest. Those are distinct supply-chain authorities.

## 4. Authority Lock lifecycle

### 4.1 Freeze

Before any evidence-producing job, Local Desktop materializes one canonical
Authority Lock from reviewed, non-secret inputs. The lock is written outside
the mutable evidence root. Its SHA-256 is recorded literally in the execution
plan or launch packet and supplied later to final verification.

Freezing the lock is not evidence collection and does not unlock scientific
claims. Any byte change after freeze creates a new digest and therefore a new
authorization identity.

### 4.2 Execute

The execution controller consumes the frozen lock read-only. Preflight and job
intents use identities already named by the lock. They may record observations,
but may not redefine the expected repository, policy, job role, execution
class, or P12-access class.

### 4.3 Verify

The final interface is:

```text
verify-evidence \
  --index PATH \
  --authority-lock PATH \
  --authority-lock-sha256 64_LOWERCASE_HEX
```

Verification order is fail-closed:

1. reject a malformed expected digest;
2. load the lock through a no-symlink, regular-file-only path;
3. require canonical bytes and the exact expected digest;
4. validate the lock's exact schema and semantic invariants;
5. load and validate the evidence index;
6. reconstruct origin, job, completion, and artifact bindings under the lock;
7. run the existing evidence reconstruction gates; and
8. emit only infrastructure counts and the verified lock/index digests.

No evidence or index content is executed at any step.

### 4.4 Publish

A byte-identical copy of the lock may be published with the evidence package,
but the package copy is not the trust anchor. Reproduction supplies the
independently recorded expected digest and verifies the published copy against
it.

## 5. Canonical schema

The Authority Lock is canonical JSON with an exact top-level schema:

```text
schema_version
task_id
repository
governing_materials
protocol
registries
preflight
jobs
claim_policy
```

### 5.1 Repository authority

`repository` contains only stable, non-secret identities:

```text
normalized_repository_identity
base_commit
base_tree
tracked_source_manifest_sha256
```

- The repository identity is host/path form with scheme, userinfo, query,
  fragment, and credentials removed.
- Commit and tree are 40 lowercase hexadecimal object identities.
- The tracked-source manifest covers safe project files required by the
  experiment. It never contains `.git`, worktree administration files,
  untracked credential files, absolute paths, symlinks, or special nodes.
- Final verification reads indexed canonical source artifacts and compares the
  manifest; it does not inspect or trust a live `.git` directory.

### 5.2 Governing materials and protocol

`governing_materials` locks the scientific plan, evidence design, this design,
and the implementation plan by SHA-256.

`protocol` locks the canonical protocol and every policy artifact referenced by
it. The mapping is exact, nonempty, safe-path-independent, and sorted by frozen
role. A policy cannot be added by adding a new index member; it must already be
named by the lock.

### 5.3 Registries

`registries` locks the exact adapter and input-generator registry bytes and the
implementation-source hashes they authorize. Empty registries, duplicate roles,
and caller-added implementations fail.

### 5.4 Preflight authority

`preflight` contains data, never commands:

```text
normalized_repository_identity
base_commit
base_tree
dependency_lock_sha256
environment_policy_sha256
required_capabilities
forbidden_credential_fields
```

The final verifier reconstructs the canonical origin/preflight receipt from
the lock and authenticated preflight event fields. It does not rerun a command
from the index. Variable machine observations such as free memory or disk are
evidence observations, not origin authority, and cannot redefine the lock.

### 5.5 Job and execution authority

`jobs` is a sorted exact list. Each row contains:

```text
job_id
phase
job_role
object_identity
input_identity_sha256
execution_class
p12_access_class
```

`execution_class` is one of the frozen protocol values, including distinct
synthetic-infrastructure, real-scientific, and non-scientific-control classes.
`p12_access_class` states whether the job is forbidden, permitted, or required
to touch the separately authorized P12 envelope.

Final completion metadata is derived from terminal intent/result pairs matched
one-to-one to these locked rows. It is not derived from cwd names, result labels,
or a caller-supplied execution-scope artifact. Missing, extra, duplicate, or
relabeled jobs fail.

### 5.6 Claim policy

`claim_policy` locks the exact claim-ceiling artifact and requires every
scientific claim to remain `blocked` for this foundation task. Completion cannot
upgrade a claim.

## 6. Module boundaries

### Authority Lock validator

The existing evidence module owns canonical lock loading, digest comparison,
schema validation, and reconstruction orchestration. It exposes one narrow
validated-lock value to downstream checks. It must not become a generic trust
framework.

### Run-record reconstruction

The existing run-record module reconstructs terminal intent/result pairs and
matches them to validated locked jobs. It derives completion counts and classes
from that match. It never accepts an execution classification as authority from
an evidence result.

### Preflight

The existing preflight module remains the runtime capability checker. Final
verification may reuse pure normalization/validation functions, but must not
execute commands or read Git metadata named by the evidence index.

### CLI

The CLI remains thin: it parses three explicit paths/values, calls the evidence
validator, and prints only verified infrastructure identities and counts.

## 7. Failure behavior

All failures are fail-closed and occur before a PASS record:

- `E_AUTHORITY_LOCK_DIGEST`: malformed or mismatched external digest;
- `E_AUTHORITY_LOCK_SCHEMA`: noncanonical, missing, extra, or invalid fields;
- `E_AUTHORITY_LOCK_PATH`: symlink, special node, unsafe path, or path escape;
- `E_AUTHORITY_ORIGIN`: receipt/repository divergence from the lock;
- `E_AUTHORITY_JOB_SET`: missing, extra, duplicate, or reordered job authority;
- `E_AUTHORITY_EXECUTION_CLASS`: result/intent role or access-class divergence;
- `E_AUTHORITY_CREDENTIAL`: credential-bearing field or forbidden Git material;
- existing evidence errors for downstream artifact reconstruction.

The verifier does not repair, rewrite, fetch, execute, or retry.

## 8. Test design

### 8.1 Positive path

A two-subject synthetic Phase 0-7 package uses one independently frozen lock,
two ecosystems, S/M scales, blocked claims, no P12 access, and zero real
scientific jobs. Final verification succeeds only with the exact external
digest.

### 8.2 Root-of-trust mutations

Each negative test recomputes every package-local self-hash:

1. change the index while retaining the lock;
2. change the lock while retaining the expected digest;
3. change both lock and index while retaining the expected digest;
4. coordinate origin receipt, protocol references, attempts, ledger, receipts,
   completion, and index resealing;
5. coordinate execution-role and completion relabelling;
6. omit, add, duplicate, or reorder a locked job;
7. replace tracked source bytes and reseal the evidence index;
8. supply a lock or evidence path through a symlink;
9. introduce `.git`, userinfo, token, password, authorization, or credential
   material;
10. insert an argv, shell fragment, or executable path into an authority field.

Every case must fail at the intended production boundary. Test-only composite
oracles do not count as final verification.

### 8.3 Regression and evidence map

The existing rehash-resistant matrix remains. The evidence map names, for every
design requirement, the production function, positive test, mutation test, and
end-to-end boundary. It states explicitly that the package proves
infrastructure semantics only.

## 9. Migration

- Index V1 and the rejected self-authorizing V2 are not accepted by the new
  final verifier; no compatibility shim is provided.
- Preserve the coordinated-reseal, execution-relabel, symlink, and credential
  REDs from the rejected prototype.
- Remove unsafe code that executes indexed commands or reads `.git` content.
- Replace test-only origin/completion reconstruction with production checks
  anchored by the external digest.
- Update the implementation plan before resuming code changes.

## 10. Acceptance criteria

The design is complete only when:

1. the external expected digest is mandatory and cannot be sourced from the
   evidence package;
2. the lock and index have exact canonical schemas and safe regular-file reads;
3. coordinated resealing fails without changing the independent digest;
4. execution classification and P12 access derive from locked jobs plus terminal
   events;
5. no indexed command executes and no `.git` or credential bytes are persisted;
6. the complete two-subject synthetic path passes;
7. every root-of-trust mutation fails through production final verification;
8. all P3 tests and required quality gates pass or an environment-only blocker
   is reported without overstating completion; and
9. RQ1-RQ4 and all scientific result claims remain blocked.
