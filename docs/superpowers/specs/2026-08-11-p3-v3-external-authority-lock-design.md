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

1. the controller implementation identity and bytes committed by the Authority
   Lock;
2. the literal expected Authority Lock SHA-256 supplied by a separately frozen,
   non-self-referential launch packet; and
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

Local Desktop creates one Authority Lock through two deterministic passes:

1. **Authority preparation:** validate and commit the controller repository,
   every subject repository/materialization, governing documents, protocol,
   policies, registries, preflight policy, and job-derivation rules. This pass
   performs no scientific, profiling, P12, mutant, or MR execution.
2. **Inventory derivation:** from only those prepared bytes, deterministically
   derive the complete subject identities and base-job intent templates,
   validate the derivation against the protocol, and insert that exact inventory
   into the candidate lock. This pass also performs no evidence-producing job.

The completed canonical lock is then written outside the mutable evidence root.
Its SHA-256 is recorded literally in a separate launch packet before the first
evidence-producing intent. The implementation plan is already an input to the
lock and therefore must not embed the resulting lock digest. The launch packet
records both the fixed implementation-plan digest and the resulting lock digest,
avoiding a self-hash cycle. The same prepared inputs must always produce
byte-identical lock bytes.

Freezing the lock is not evidence collection and does not unlock scientific
claims. Any byte change after freeze creates a new digest and therefore a new
authorization identity.

### 4.2 Execute

The execution controller consumes the frozen lock read-only. Preflight and job
intents use identities already named by the lock. They may record observations,
but may not redefine the expected repository, policy, job role, execution
class, or P12-access class.

### 4.3 Verify

The freeze interface is:

```text
freeze-authority-lock \
  --controller-root PATH \
  --authority-inputs PATH \
  --output PATH
```

`authority-inputs` is a canonical, exact-schema declaration of subject roots
and governing artifact paths. It is an input to deterministic freezing, never a
trusted verification artifact. The freezer reads only safe regular tracked
bytes, may execute only source-hash-verified deterministic adapters through their
reviewed in-process interface, invokes no evidence-producing or scientific
executable, performs no network operation, and writes the output atomically with
create-new semantics. It may inspect live Git metadata only during freeze to
compare commit/tree and normalize origin in memory; it never copies `.git` or raw
origin/userinfo bytes into the lock. If `--output` already exists, it fails
rather than overwriting it.

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

No Authority Lock, evidence, or index content is executed at any step.

### 4.4 Publish

A byte-identical copy of the lock may be published with the evidence package,
but the package copy is not the trust anchor. Reproduction supplies the
independently recorded expected digest and verifies the published copy against
it.

## 5. Canonical schema

The Authority Lock is UTF-8 canonical JSON with an exact top-level schema.
Canonicalization uses the repository's reviewed `canonical_json_bytes`
implementation: sorted object keys, compact separators, JSON booleans/null,
integers only for numeric authority fields, no floats, no Unicode escaping,
and exactly one trailing LF. Duplicate keys, byte-order marks, non-UTF-8 input,
and noncanonical re-encodings fail.

The exact top-level schema is:

```text
schema_version
task_id
controller_repository
subjects
governing_materials
protocol
registries
preflight
jobs
claim_policy
```

### 5.1 Controller and subject authority

`controller_repository` contains the reviewed verifier/controller identity:

```text
normalized_repository_identity
base_commit
base_tree
tracked_source_manifest_sha256
```

`subjects` is a sorted, nonempty exact list. Each row contains:

```text
subject_id
repository_role
normalized_repository_identity
base_commit
base_tree
tracked_source_manifest_sha256
build_descriptor_sha256
adapter_id
```

- The repository identity is host/path form with scheme, userinfo, query,
  fragment, and credentials removed.
- Commit and tree are 40 lowercase hexadecimal object identities.
- The controller manifest covers the verifier implementation, thin CLI, schema
  validators, and dependency lock used by verification.
- Every subject has its own repository/materialization commitment; no aggregate
  digest may hide subject membership, repository role, or per-subject paths.
- Each tracked-source manifest is canonical JSON with exact rows
  `(relative_path, mode, sha256)`, sorted by UTF-8 relative path. It covers every
  safe tracked regular file required by that role and forbids missing, extra,
  duplicate, symlink, and special-node entries.
- Manifests never contain `.git`, worktree administration files, untracked
  credential files, absolute paths, or path escapes.
- Final verification reads indexed canonical controller/subject source
  artifacts and compares each exact manifest; it does not inspect or trust a
  live `.git` directory.

### 5.2 Governing materials and protocol

`governing_materials` locks the scientific plan, evidence design, this design,
the already-final implementation plan, and the controller implementation
manifest by SHA-256. The later launch packet records the Authority Lock digest
beside those governing identities; neither the design nor implementation plan
embeds its own resulting lock digest, and the packet may not derive that digest
from the evidence package.

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
the lock and hash-linked, exact-schema preflight event fields. These fields are
validated records, not signed platform attestations, and therefore do not prove
that a physical command ran. The verifier does not rerun a command from the
index. Variable machine observations such as free memory or disk are evidence
observations, not origin authority, and cannot redefine the lock.

### 5.5 Job and execution authority

`jobs` is a sorted exact list. Each row contains:

```text
job_id
phase
job_role
object_identity
input_identity_sha256
intent_template_sha256
maximum_attempts
retry_trigger
execution_class
p12_access_class
```

`intent_template_sha256` is the canonical SHA-256 of the complete production
intent after removing only `attempt`. It therefore commits protocol, phase,
argv, cwd identity, environment, all input hashes, seed, timeout, object/MR/input
and repetition identities, environment identity, and job role. No individual
field may be omitted merely because another aggregate input digest exists.

`maximum_attempts` and `retry_trigger` lock the existing failure-only retry
policy. Every attempt after 1 must retain the same intent template and must be
preceded by the exact permitted infrastructure-failure state. Inventory
derivation freezes base jobs, not a guessed number of future result records.

`execution_class` is one of the frozen protocol values, including distinct
synthetic-infrastructure, real-scientific, and non-scientific-control classes.
`p12_access_class` states whether the job is forbidden, permitted, or required
to touch the separately authorized P12 envelope.

Final completion metadata is derived from terminal intent/result pairs matched
one-to-one to these locked base-job rows and their retry policy. It is not
derived from cwd names, result labels, or a caller-supplied execution-scope
artifact. Missing, extra, duplicate, or relabeled jobs fail.

The completion vocabulary is deliberately observational:

```text
authorized_real_p12_job_count
recorded_real_scientific_terminal_count
```

Zero means that the lock authorized no such job or that the reconstructed
terminal ledger contains no such record. It does not prove platform-level
physical non-access. A claim of physical absence requires a separately scoped
and independently verified platform attestation and is outside this design.

### 5.6 Claim policy

`claim_policy` locks the exact claim-ceiling artifact and requires every
scientific claim to remain `blocked` for this foundation task. Completion cannot
upgrade a claim.

## 6. Module boundaries

### Authority Lock validator

The existing evidence module owns deterministic lock freezing, canonical lock
loading, external digest comparison, schema validation, and reconstruction
orchestration. Its interface remains two deep operations—freeze and verify—and
it exposes one narrow validated-lock value to downstream checks. It must not
become a generic trust framework.

### Run-record reconstruction

The existing run-record module reconstructs terminal intent/result pairs,
recomputes each intent template, validates failure-only retry transitions, and
matches them to validated locked jobs. It derives completion counts and classes
from that match. It never accepts an execution classification as authority from
an evidence result.

### Preflight

The existing preflight module remains the runtime capability checker. Final
verification may reuse pure normalization/validation functions, but must not
execute commands or read Git metadata named by the evidence index.

### CLI

The CLI remains thin: it exposes the freeze and verify interfaces, calls the
evidence module, and prints only verified infrastructure identities and counts.

## 7. Failure behavior

All failures are fail-closed and occur before a PASS record:

- `E_AUTHORITY_LOCK_DIGEST`: malformed or mismatched external digest;
- `E_AUTHORITY_LOCK_SCHEMA`: noncanonical, missing, extra, or invalid fields;
- `E_AUTHORITY_LOCK_PATH`: symlink, special node, unsafe path, or path escape;
- `E_AUTHORITY_ORIGIN`: receipt/repository divergence from the lock;
- `E_AUTHORITY_MANIFEST`: controller or subject manifest divergence;
- `E_AUTHORITY_JOB_SET`: missing, extra, duplicate, or reordered job authority;
- `E_AUTHORITY_INTENT`: intent-template or retry-policy divergence;
- `E_AUTHORITY_EXECUTION_CLASS`: result/intent role or access-class divergence;
- `E_AUTHORITY_CREDENTIAL`: credential-bearing field or forbidden Git material;
- existing evidence errors for downstream artifact reconstruction.

The verifier does not repair, rewrite, fetch, execute, or retry.

## 8. Test design

### 8.1 Positive path

A two-subject synthetic Phase 0-7 package uses one independently frozen lock,
two repositories/materializations, two ecosystems, S/M scales, blocked claims,
zero authorized real-P12 jobs, and zero recorded real-scientific terminal jobs.
Final verification succeeds only with the exact external digest.

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
11. change any intent field or retry transition while retaining job/input IDs;
12. omit, add, or swap a controller or subject repository/manifest;
13. supply a valid lock/index containing command-like strings while spies prove
    that verifier subprocess and socket attempt counts remain exactly zero.

Every case must fail at the intended production boundary. Test-only composite
oracles do not count as final verification.

Credential checks apply to Authority Lock/index metadata, repository identities,
preflight metadata, and persisted provenance fields. They do not reject subject
source merely because program text contains words such as `password` or `token`.
Dedicated fixtures prove both secret-metadata rejection and source-code
noninterference.

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
2. deterministic two-pass freezing is byte-identical and atomic, and precedes
   every evidence-producing intent;
3. controller plus every subject has an exact independently enumerable tracked
   manifest;
4. the lock and index have exact canonical schemas and safe regular-file reads;
5. coordinated resealing fails without changing the independent digest;
6. complete intent templates, retry policy, execution classification, and P12
   authorization derive from locked jobs plus terminal events;
7. reported zero counts are explicitly recorded/authorized counts, not claims of
   physical platform absence;
8. subprocess and socket spies remain exactly zero during final verification,
   and no `.git` or credential bytes are persisted;
9. the complete two-subject synthetic path passes;
10. every root-of-trust mutation fails through production final verification;
11. all P3 tests and required quality gates pass or an environment-only blocker
   is reported without overstating completion; and
12. RQ1-RQ4 and all scientific result claims remain blocked.
