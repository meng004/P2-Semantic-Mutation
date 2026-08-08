# P3 v3 Evidence Foundation Design

## Material Passport

- Date: 2026-08-08
- Status: proposed implementation-foundation design; user review required
- Scope: P3 v3 governance artifacts, deterministic frames, MR isolation,
  evidence packages, and repeatable preflight
- Parent scientific plan SHA-256:
  `c433ea69f51049f50da9b14d53eb7654c9bf2c7843485ebf4dbc7080887c6ab5`
- Governing principles SHA-256:
  `4aa9fb17bdfa8976387a4165445b2b0b72e653688187c958fa1beb022075780d`
- Existing P12 v1.1.2 consumer contract SHA-256:
  `6247f3063952fa7c133ca574b5f9667c51b8d4636d84c40bce2753cf9e8bc427`
- Intended implementation environment: Python 3.11, standard library, PyYAML,
  pytest, fresh phase-scoped Cursor VMs using Grok 4.5 High
- This design authorizes no experiment, network collection, P12 Holdout opening,
  mutant construction, MR execution, or Cursor VM launch.

## 1. Purpose

The evidence foundation converts the approved P3 scientific plan into a small
set of enforceable interfaces. It exists to make later semantic-mutant work
scientifically reviewable before expensive construction or execution begins.

It must answer five questions mechanically:

1. Which claims, subjects, fixed versions, MRs, and retry rules were frozen?
2. Can the diversity and criterion cohorts be recomputed without outcomes?
3. Can a construction process prove that buggy revisions, reference MRs, and
   real-fault outcomes were physically unavailable?
4. Can every artifact be identified by canonical content rather than filename or
   mutable branch state?
5. Can platform failures be diagnosed and repeated without consuming or
   contaminating a scientific run?

Passing this foundation does not support a paper result. It supports only the
claim that the experiment has a reproducible, non-circular input channel.

## 2. Selected approach

Three implementation approaches were considered:

1. Extend the existing Supplemental R2/R3 scripts. This reuses mature hashing
   and admission checks, but it also imports one-shot execution assumptions and
   a large monolithic protocol surface that is not part of P3 v3.
2. Build a focused `p3_v3` library over proven repository patterns. This is the
   selected approach. It reuses canonical encoding, atomic writes, stable error
   codes, and negative-test conventions while keeping P3 v3 interfaces small.
3. Encode the workflow only in Cursor launch prose. This is rejected because a
   launch packet is not an audited executable interface and previously allowed
   platform-specific failures before scientific work began.

The foundation is implemented as importable modules with one thin CLI. No
scientific rule is implemented only as natural-language Cursor instruction.

## 3. Scope

### 3.1 In scope

- canonical JSON and canonical semantic hashing for YAML governance artifacts;
- exact, versioned artifact schemas;
- `score-task`, claim-ledger, experiment-ledger, and contract-compatibility
  validation;
- deterministic `C_CONSTRUCT` and exhaustive unique-version `C_CRITERION`
  frames;
- independent evaluation-MR inventory and reference-MR exclusion receipts;
- bounded, deterministic MR portfolio sampling;
- Package A, B, and C commitment/manifests and absence verification;
- a repeatable, non-scientific capability preflight;
- stable error codes, append-only attempt records, and claim-state projection;
- synthetic fixtures and negative tests for all boundaries.

### 3.2 Out of scope

- semantic-contract authoring and operator applicability decisions;
- Grok patch proposal;
- patch application or mutant certification;
- syntactic-mutant generation;
- MR or P12 real-fault execution;
- RQ1–RQ4 statistical analysis;
- acquisition of P12 Holdout contents;
- language-independent operator IR, language adapters, or automatic site binding;
- final Cursor launch instructions.

## 4. Architectural boundaries

The implementation is split into eight focused modules under `src/p3_v3/`.

### 4.1 `artifact_core.py`

Responsibilities:

- canonical JSON bytes using UTF-8, sorted keys, compact separators, and no
  trailing newline;
- SHA-256 for bytes, files, canonical objects, and tree manifests;
- exact-key/type/value validation primitives;
- canonical YAML generation for human-facing governance documents;
- raw-file SHA and semantic canonical-object SHA for YAML;
- same-directory atomic writes with file fsync, `os.replace`, and parent-directory
  fsync;
- exclusive creation for immutable artifacts;
- stable `P3ArtifactError(code, detail)` failures.

It does not know any P3 scientific field names. Other modules depend on it; it
depends only on the standard library and PyYAML.

### 4.2 `schema_registry.py`

Responsibilities:

- define a small internal schema algebra for exact objects, lists, enums,
  strings, integers, booleans, nulls, and SHA/timestamp/path formats;
- validate runtime objects using that single registry;
- emit reviewable JSON Schema 2020-12 documents into `schemas/p3_v3/`;
- reject extra keys by default;
- expose stable schema IDs and version compatibility rules.

Committed JSON Schema documents are generated views, not a second authority. A
test regenerates them and requires byte equality. This avoids a new runtime
dependency and prevents hand-written schema files from drifting away from the
validators.

### 4.3 `governance.py`

Responsibilities:

- exact validation of score task, claim ledger, experiment ledger header, and
  P12 contract-compatibility record;
- claim-status transition rules;
- append-only JSONL experiment-event validation;
- projection of JSONL events into the human-readable experiment-ledger YAML;
- closure between every claim evidence reference and a declared artifact or run.

It cannot inspect experimental result values to upgrade a claim. It verifies
that a separately frozen evidence rule authorizes the transition.

### 4.4 `subject_frames.py`

Responsibilities:

- validate blinded fixed-snapshot records;
- compute source-size and implementation-technique strata from frozen mechanical
  features;
- build the hash-ranked `C_CONSTRUCT` diversity frame;
- build `C_CRITERION` by enumerating every unique eligible fixed snapshot without
  sampling;
- record overlap between cohorts without duplicating artifacts or executions;
- preserve `EMPTY_FRAME`, failed classification, and unpaired records.

This module cannot read buggy revisions, bug patches, reference MRs, or MR
outcomes.

### 4.5 `mr_inventory.py`

Responsibilities:

- validate the predeclared P3 evaluation-MR source frame;
- compute outcome-free canonical MR semantic signatures;
- verify custodian-issued reference-MR exclusion receipts without receiving the
  reference MR;
- classify invalid, flaky, excluded, uncertain, and independently evaluable MRs;
- build deterministic descriptive and confirmatory portfolios;
- implement bounded combinadic unranking without enumerating the full subset
  lattice.

It cannot add an MR after controlled or real-fault results exist.

### 4.6 `evidence_packages.py`

Responsibilities:

- build and verify content-addressed package manifests;
- reject symlinks, sockets, devices, path traversal, duplicate normalized paths,
  and non-regular files;
- enforce package-specific allowlists and forbidden paths/identity classes;
- compute package tree hashes from sorted file records;
- materialize a clean package directory from allowlisted sources;
- verify raw bytes after materialization;
- create the blinded fixed-snapshot bridge and Holdout commitment receipt.

It does not upload, fetch, decrypt, or open Holdout contents.

### 4.7 `preflight.py`

Responsibilities:

- validate repository identity using normalized owner/repository identity rather
  than one remote URL spelling;
- record OS, architecture, CPU, memory, disk, Python, compiler, and dependency
  lock identity;
- verify subprocess, exclusive-create, fsync, atomic replace, file lock, and
  parallel worker capabilities in a disposable temporary root;
- verify offline availability of declared inputs;
- execute only declared smoke commands with timeouts and captured streams;
- emit a preflight report and immutable attempt record.

Preflight never creates a scientific run ID and never opens an experiment event
ledger beyond its own `PREFLIGHT_*` event class.

### 4.8 `foundation_cli.py`

This is the only public command surface for the foundation. It parses arguments,
loads exact inputs, calls one library operation, prints one canonical result, and
maps `P3ArtifactError.code` to a nonzero exit. It contains no scientific rule.

The planned script entry point is:

```text
python3 scripts/p3_v3/foundation.py <subcommand> ...
```

The implementation plan must not embed a second controller in a Cursor prompt.

### 4.9 Planned file surface

```text
src/p3_v3/__init__.py
src/p3_v3/artifact_core.py
src/p3_v3/schema_registry.py
src/p3_v3/governance.py
src/p3_v3/subject_frames.py
src/p3_v3/mr_inventory.py
src/p3_v3/evidence_packages.py
src/p3_v3/preflight.py
src/p3_v3/foundation_cli.py
scripts/p3_v3/foundation.py
schemas/p3_v3/*.schema.json
tests/p3_v3/
tests/fixtures/p3_v3/
```

Each test file mirrors one production module. Synthetic fixture directories are
split by visible package role so a negative test cannot accidentally depend on
real P12 material.

## 5. Canonical artifact rules

### 5.1 Identity pair

Every committed artifact has two identities:

- `raw_sha256`: SHA-256 of exact file bytes;
- `semantic_sha256`: SHA-256 of the parsed value encoded as canonical JSON.

For canonical JSON artifacts these hashes differ only when the file includes the
required final newline. The manifest records both. For YAML, raw layout changes
may alter `raw_sha256` while the semantic identity remains stable; any frozen
artifact nevertheless requires both declared hashes to match.

### 5.2 Canonical JSON file bytes

Canonical JSON files use:

```python
json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
```

followed by exactly one LF in the file. Hashes of semantic values exclude that
LF; hashes of file bytes include it.

### 5.3 Canonical YAML file bytes

Governance YAML uses `yaml.safe_dump` with sorted keys, Unicode enabled, block
style, LF line endings, and exactly one terminal LF. Aliases, custom tags,
multiple documents, duplicate keys, and non-JSON scalar types are rejected.

### 5.4 Self-hash rule

An object with `artifact_sha256` computes that value over the canonical object
with `artifact_sha256` removed. Parent artifacts are referenced by both exact
path and raw SHA-256. No object hashes bytes containing its own hash.

### 5.5 Tree identity

A package tree hash is the canonical SHA-256 of the ordered list:

```text
(normalized_relative_path, mode, size, raw_sha256)
```

Directory mtimes, uid, gid, inode, traversal order, and archive compression do
not enter scientific identity.

## 6. Stable artifact schemas

All records contain `schema_version`, `artifact_id`, `created_at_utc`, and parent
artifact references. Version `p3-v3.1` is the first implementation version.
Unknown fields fail validation rather than being silently retained.

Frozen artifact builders receive `created_at_utc` as an explicit input from the
freeze manifest and never read the wall clock. Rebuilding with the same inputs
therefore produces the same bytes. Attempt events and preflight reports may read
the wall clock because their identity describes a new attempt rather than a
regeneration of a frozen scientific object.

### 6.1 Score task

Required fields:

```text
schema_version
artifact_id
created_at_utc
research_questions
subjects
metrics
baselines
inputs
outputs
seed_policy
stopping_rules
retry_policy
prohibited_claims
parent_plan_sha256
artifact_sha256
```

The five semantic-contract families and the separate construction-mechanism axis
are explicit values, not free-text aliases.

### 6.2 Claim ledger

Each claim contains exactly:

```text
claim_id
claim_text
status
permitted_sections
upgrade_rule_id
evidence_refs
limitations
last_transition_event
```

Allowed status transitions are:

```text
speculative -> blocked
blocked -> insufficient | observed | qualified | supported
insufficient -> blocked | observed | qualified | supported
observed -> blocked | insufficient | qualified | supported
qualified -> blocked | insufficient | observed | supported
supported -> blocked | insufficient | observed | qualified
```

Every transition is an append-only event. A downgrade is always allowed with a
reason. An upgrade requires the frozen `upgrade_rule_id` and all referenced
evidence artifacts. No manuscript text can change status.

### 6.3 Experiment ledger

`research/p3_v3/experiment-ledger.yml` is a generated, human-readable projection.
The authority is `data/p3_v3/raw/experiment-events.jsonl`.

Each event contains exactly:

```text
event_id
sequence
recorded_at_utc
event_class
protocol_version
job_id
attempt
command_argv
cwd_identity
environment_sha256
input_refs
output_refs
exit_code
status
failure_code
previous_event_sha256
event_sha256
```

The event hash excludes `event_sha256` and includes
`previous_event_sha256`. Sequence starts at one and is contiguous. The writer
opens the file with append and lock semantics, fsyncs the event, then fsyncs the
parent directory after first creation. A loader rejects partial final lines,
forked hashes, duplicated IDs, and pending attempts represented as success.

The central event log has exactly one writer. A parallel worker writes a
content-addressed event segment in its own job directory; it never appends to the
central JSONL. A later reducer validates every segment and appends them in frozen
job-ID and attempt order. The file lock detects an accidental second writer; it
is not a supported multiwriter coordination mechanism.

### 6.4 P12 contract compatibility

The compatibility record contains:

```text
p12_package_version
p12_contract_raw_sha256
p12_contract_semantic_sha256
admission_rule
primary_estimand
permits_p3_paired_reanalysis
provides_atomic_non_reference_mr_ledger
provides_blinded_fixed_snapshot_bridge
project_floor
real_fault_family_floor
minimum_families_per_project
maximum_project_fraction
disposition
reason_codes
```

Only `disposition=COMPATIBLE_SUCCESSOR` permits primary RQ4. The frozen v1.1.2
contract must validate as `LEGACY_ESTIMAND_ONLY`, never as a compatible successor.

## 7. Blinded fixed-snapshot bridge

P3 must build controlled mutants on fixed code, but it must not see which real
bug that code repairs. The bridge resolves this apparent conflict.

The P12 custodian emits one record per unique fixed snapshot containing:

```text
neutral_subject_id
fixed_snapshot_tree_sha256
source_archive_sha256
build_descriptor_sha256
license_class
repository_scale_features
technique_features
eligible_for_construct
eligible_for_criterion
custodian_receipt_sha256
```

It excludes repository URL, issue/PR identity, buggy commit, fixed commit, patch,
changed symbols, defect family, reference MR, and all outcomes. Package A carries
the fixed source archive named only by `neutral_subject_id` and hash.

The fixed source and public documentation may reveal the upstream project. The
guarantee is bug blindness—not project anonymity. No claim or audit may describe
Package A as hiding programming language, library, or project identity when those
are inferable from allowed source bytes.

At Phase 7, Package C reveals the custodian mapping between neutral subject IDs
and exact P12 buggy/fixed identities. The mapping is append-only and must cover
every criterion-frame record. A missing or duplicated mapping is a hard failure;
it cannot be repaired by substituting another subject.

## 8. Deterministic subject frames

### 8.1 Feature authority

Scale and technique classification consumes only fields in the blinded bridge.
Repository scale uses frozen nonblank, noncomment source-line counts. Technique
uses the frozen multi-label vector and the exact primary-label precedence in the
scientific plan. `TECH_UNCERTAIN` remains a visible value.

### 8.2 `C_CONSTRUCT`

The builder:

1. validates the complete eligible blinded frame;
2. partitions by scale × primary technique;
3. ranks each cell by
   `SHA256(fixed_snapshot_tree_sha256 || neutral_subject_id || "P3-C1")`;
4. selects one per nonempty cell;
5. continues round-robin by within-cell rank until 18 subjects or exhaustion;
6. emits `EMPTY_FRAME` for every unfilled target cell;
7. never replaces a selected subject after any later failure.

### 8.3 `C_CRITERION`

The builder includes every unique eligible `fixed_snapshot_tree_sha256` from the
compatible successor bridge. There is no rank, quota, random seed, or sampling
step. Multiple neutral IDs with the same tree are preserved as aliases pointing
to one execution identity. Conflicting archives for the same tree fail.

### 8.4 Cohort overlap

When a fixed tree belongs to both cohorts, one artifact has both role tags. It
contributes once to construction and execution ledgers. Analysis code later
decides which estimand consumes that row; the foundation never duplicates it.

## 9. Evaluation-MR independence

### 9.1 Candidate source frame

Each candidate evaluation MR must trace to program specifications, public
documentation, or a P3 MR artifact whose timestamp and content hash predate
Package C opening. Its admission cannot mention a P12 bug, patch, issue, reference
MR, or outcome.

### 9.2 Canonical semantic signature

The signature is the canonical SHA-256 of:

```text
signature_schema_version
source_input_transformation
followup_input_transformation
metamorphic_predicate
tolerance_class
oracle_direction
```

Names, comments, formatting, and implementation language do not enter the
signature. Any element that cannot be represented mechanically yields
`SIGNATURE_UNCERTAIN`.

### 9.3 Custodian exclusion receipt

The Holdout custodian receives candidate MR IDs and signatures and compares them
with reference MRs. It returns only:

```text
candidate_mr_id
decision
reason_code
candidate_signature_sha256
comparison_commitment_sha256
p12_package_root_sha256
candidate_inventory_sha256
comparison_algorithm_sha256
custodian_receipt_sha256
```

Allowed decisions are `KEEP`, `EXCLUDE_REFERENCE`, `EXCLUDE_EXACT_VARIANT`,
`EXCLUDE_SEMANTIC_DUPLICATE`, and `EXCLUDE_UNCERTAIN`. Construction never
receives the reference identity or signature. Missing receipts fail closed. If
no MR remains, the subject becomes `NO_INDEPENDENT_EVALUATION_MR` and remains in
the ledger but outside MR-set comparison claims.

The receipt is valid only when its P12 package root matches the compatible
successor commitment, its candidate inventory hash matches the submitted
candidate frame, its comparison algorithm hash matches the frozen signature
implementation, and its own self-hash is correct. A standalone receipt hash has
no authority.

### 9.4 Portfolio sampling

Singleton, full, and leave-one-out portfolios are descriptive. Full enumeration
is allowed only when `q <= 12` and never supplies inferential degrees of freedom.

Confirmatory budgets are `1`, `2`, `4`, and `q`. For each nontrivial budget below
`q`, the sampler chooses at most 20 unique combination ranks using a SHA-256
counter stream keyed by subject ID, budget, inventory hash, and `P3-MRSET-v1`.
Ranks are mapped to combinations by combinadic unranking. Rejection sampling
handles repeated ranks. The algorithm fails rather than enumerating all
combinations when its declared attempt ceiling of 10,000 counter values is
reached.

## 10. Physical evidence packages

### 10.1 Common manifest

Each package manifest contains:

```text
package_id
package_role
schema_version
created_at_utc
parent_artifacts
allowlist_id
denylist_id
files
tree_sha256
artifact_sha256
```

Each file record contains normalized path, POSIX mode, size, raw SHA-256, and
content class. Paths are sorted by UTF-8 byte order.

### 10.2 Package A — construction

Allowed content classes:

- blinded fixed source snapshot;
- public documentation and build metadata;
- frozen semantic-contract catalogue and candidate slot;
- contract predicate, domain, oracle, tolerance, and witness-search policy;
- proposer prompt and response schema.

Forbidden content classes and paths:

- `.git` and every VCS metadata directory;
- repository, issue, PR, buggy or fixed commit identities;
- bug patches, defect-family labels, changed-symbol lists;
- candidate or reference MR source/signatures;
- syntactic-mutant identities or outcomes;
- any experiment result or manuscript expected-effect statement about an MR.

### 10.3 Package B — controlled execution

Package B has two append-free, content-addressed layers:

1. Phase 4 freezes `PACKAGE_B_SEMANTIC`, containing original fixed snapshots,
   certified semantic-mutant trees, and the semantic denominator manifest.
2. Phase 5 freezes `PACKAGE_B_FINAL`, referencing the exact semantic-layer hash
   and adding the syntactic-mutant trees, syntactic denominator, non-reference MR
   inventory, portfolios, controlled job-list inputs, and execution code.

Final assembly verifies and copies the semantic layer without changing a byte.
Neither layer contains a Package C mapping, buggy tree, reference MR, or real-
fault result. Phase 6 accepts only `PACKAGE_B_FINAL`.

### 10.4 Package C — real Holdout

The P12 custodian builds Package C outside the construction and controlled-
execution environments. Before Phase 7, P3 receives only:

- package root SHA-256;
- contract compatibility record;
- blinded fixed-snapshot bridge;
- candidate-MR exclusion receipts.

Package C contents are provisioned only to a new Phase 7 VM after Package B,
controlled denominators, MR portfolios, analysis code, and controlled results
are sealed. Package C never enters the earlier VM filesystem, encrypted or
otherwise.

### 10.5 Phase-scoped VMs

Physical absence is stronger than an application allowlist. The implementation
therefore uses at least two clean execution environments:

1. construction and controlled execution receive Packages A then B, but never C;
2. real-fault work starts in a new environment only after the controlled phase
   closes.

Within Phase 7, three least-privilege sandboxes are distinct:

1. the family mapper receives Package C behavioral/patch records and the frozen
   operator catalogue, but no Package B or MR material;
2. the leakage auditor receives Package C identities plus only the controlled
   patch/tree/symbol/signature projection, but no MR definitions or kill outcomes;
3. after both outputs freeze, the real-fault executor receives Package C
   executable pairs and the non-reference MR runtime slice of `PACKAGE_B_FINAL`,
   but no controlled kill matrix.

A phase transition is a hash-verified artifact handoff, not a resumed shell or
conversation. Later implementation plans may split the first environment again
for resource reasons, but may not combine C with pre-freeze construction.

## 11. Repeatable preflight

### 11.1 Statuses

Preflight emits one of:

- `PREFLIGHT_PASS`;
- `PREFLIGHT_FAIL_CAPABILITY`;
- `PREFLIGHT_FAIL_IDENTITY`;
- `PREFLIGHT_FAIL_DEPENDENCY`;
- `PREFLIGHT_FAIL_INPUT`;
- `PREFLIGHT_FAIL_SMOKE`.

No preflight status is a scientific result. Every attempt is retained and may be
rerun after diagnosis with a new attempt ID.

### 11.2 Remote normalization

Repository identity is normalized to lowercase `owner/repository` after parsing
HTTPS or SSH syntax and stripping an optional `.git`. The raw remote is recorded,
but raw spelling is not an equality gate. The expected normalized identity is
frozen in the preflight specification.

### 11.3 Capability probes

All probes run in a unique disposable directory outside scientific artifact
roots. They verify:

- exclusive file creation;
- full write and readback;
- file and directory fsync;
- atomic same-filesystem replace;
- advisory file locking;
- subprocess stream capture and timeout;
- declared maximum worker count under CPU and memory limits;
- subject smoke commands with frozen argv and environment, executed against a
  disposable materialization with a separate output root.

Probe files are deleted only after their hashes and status are recorded in the
preflight report. Their contents never become scientific evidence.

### 11.4 Scientific authorization boundary

Scientific authorization begins only when all of these exist and validate:

- `PREFLIGHT_PASS` report;
- frozen governance artifacts;
- frozen cohort and MR frames;
- exact package manifest for the phase;
- canonical job list;
- first append-only scientific `RUN_INTENT` event.

Failure before `RUN_INTENT` does not consume a scientific run. Failure after it
follows the experiment retry policy and remains in the ledger.

## 12. Failure and retry semantics

Errors use stable codes grouped by boundary:

```text
E_CANON_*
E_SCHEMA_*
E_GOV_*
E_FRAME_*
E_MR_*
E_PACKAGE_*
E_PREFLIGHT_*
E_LEDGER_*
```

The CLI emits no stack trace on an expected validation failure. It writes one
canonical error object to stderr and exits nonzero. Unexpected exceptions retain
the stable outer code `E_INTERNAL_UNCLASSIFIED`, include the exception class but
not secrets or Holdout identities, and are recorded in the relevant non-
scientific or scientific attempt ledger.

Retries follow the scientific plan:

- repeatable preflight may be rerun without a scientific run ID;
- transient infrastructure work may have at most three attempts with identical
  job identity, argv, inputs, and seed;
- deterministic schema, code, contract, or identity failure is not retried under
  the same protocol version;
- repair increments protocol version and reruns the complete affected phase;
- no successful rerun erases a failure.

## 13. CLI surface

The foundation exposes these subcommands:

```text
emit-schemas
validate-governance
validate-p12-contract
build-subject-frames
build-mr-candidate-frame
verify-reference-exclusions
finalize-mr-inventory
build-portfolios
build-package
verify-package
run-preflight
validate-ledger
project-ledger
```

Every subcommand accepts explicit paths and produces one declared output. No
subcommand discovers a repository root through `cwd`, shell variables, globbing,
or mutable Git branch names. Commands use `shell=False`. Local Desktop invokes
them with `rtk`; Cursor VM invokes the same Python CLI without `rtk`.

## 14. Test design

Implementation is test-driven. Tests live under `tests/p3_v3/` and use only
synthetic fixtures.

### 14.1 Canonical artifact tests

- Unicode, key order, line ending, and numeric-type fixtures have fixed hashes;
- YAML aliases, tags, duplicate keys, NaN, infinity, and timestamps are rejected;
- interrupted atomic writes leave either old or new complete bytes;
- short-write injection fails without publishing a partial artifact;
- parent-directory fsync is exercised through an injectable filesystem adapter.

### 14.2 Governance and ledger tests

- missing, extra, or wrong-type fields fail with stable codes;
- every legal and illegal claim transition is covered;
- missing evidence references cannot upgrade a claim;
- event sequence gaps, duplicate IDs, broken previous hashes, partial lines, and
  pending-as-success records fail;
- failed and inconclusive events remain in the projected ledger.

### 14.3 Frame tests

- `C_CONSTRUCT` selection is invariant to input ordering;
- empty cells remain explicit;
- exact tree aliases do not duplicate execution;
- `C_CRITERION` includes every unique eligible fixed tree;
- adding outcomes to a fixture is rejected as a forbidden field;
- no failed subject is replaced.

### 14.4 MR tests

- signature-equivalent implementations hash identically after permitted
  normalization;
- semantically different predicates do not collide in fixtures;
- missing or uncertain custodian receipts exclude rather than promote an MR;
- reference-MR identifiers never appear in emitted inventory bytes;
- combinadic samples are deterministic, unique, bounded, and never enumerate the
  full lattice for `q > 12`.

### 14.5 Package tests

- symlink, special file, traversal, duplicate normalized path, forbidden suffix,
  and forbidden content class fail;
- Package A rejects bug, MR, VCS, and outcome fixtures;
- Package B rejects P12 mappings and real-fault results;
- a one-byte source mutation changes file, tree, and package hashes;
- materialization followed by verification reproduces exact bytes;
- Package C content is absent from the Phase A/B fixture root.

### 14.6 Preflight tests

- HTTPS and SSH remotes normalize to the same repository identity;
- a wrong owner/repository fails before any scientific event;
- capability failures remain repeatable preflight events;
- smoke failure records stdout/stderr hashes and timeout status;
- the first scientific `RUN_INTENT` is impossible without all frozen inputs;
- rerunning a corrected preflight does not alter any scientific ledger.

## 15. Security and confidentiality

- Paths, JSON, YAML, archives, and P12 materials are untrusted inputs.
- Archive extraction is never used; package materialization copies individually
  verified regular files.
- Relative paths are normalized and must remain below the declared root.
- Secrets, environment variables, tokens, home-directory contents, and raw
  Holdout identities are never included in reports.
- Error messages use neutral subject IDs before Phase 7.
- Package manifests store content classes so absence rules can be verified
  without scanning for secret literal values.
- No network transport exists in the foundation library.

## 16. Scientific traceability

The foundation implements the following scientific-plan protections:

| Scientific requirement | Foundation enforcement |
|---|---|
| Semantic and construction axes remain distinct | Exact score-task and frame enums |
| P12 v1.1.2 is not reinterpreted | Contract compatibility disposition |
| Reference MR cannot evaluate P3 | Custodian exclusion receipts and non-reference inventory |
| Diversity selection is outcome blind | Hash-ranked blinded `C_CONSTRUCT` frame |
| RQ4 pairing is not favorable sampling | Exhaustive unique-tree `C_CRITERION` frame |
| Bug details cannot guide construction | Blinded fixed-snapshot bridge and Package A deny rules |
| Failed attempts remain evidence | Hash-chained append-only event ledger |
| Platform failure is not scientific failure | Repeatable preflight before `RUN_INTENT` |
| Holdout opens after controlled freeze | Phase-scoped VMs and Package C commitment |
| Claims cannot outrun evidence | Exact claim transitions and evidence closure |

## 17. Acceptance criteria

This design is implemented only when all criteria below pass:

1. The schema emitter produces byte-identical schema artifacts across two clean
   Python 3.11 environments using the frozen dependency lock.
2. All governance artifacts validate with exact fields, identities, and parent
   hashes; every one-byte mutation used by the test matrix is rejected.
3. `C_CONSTRUCT` and `C_CRITERION` regenerate byte-identically from shuffled
   synthetic inputs.
4. `C_CRITERION` has no sampling code path.
5. Reference-MR exclusion can be verified without reference identity or source
   appearing in P3 output bytes.
6. Package A and B verifiers prove forbidden classes absent and reproduce exact
   tree hashes after materialization.
7. Package C has only a commitment and blinded bridge visible before Phase 7.
8. Preflight can fail, be diagnosed, and pass on a later attempt while the
   scientific ledger remains nonexistent.
9. A scientific `RUN_INTENT` cannot be recorded until all required frozen hashes
   validate.
10. The complete focused test suite and the existing repository test suite pass.

## 18. Implementation-plan boundary

After user approval, one implementation plan will cover only this evidence
foundation. It will create the `src/p3_v3/`, `scripts/p3_v3/`,
`tests/p3_v3/`, `schemas/p3_v3/`, and synthetic fixture surfaces needed above.
It will not construct mutants or access live P12 Holdout material.

Semantic construction/certification, controlled MR execution, and P12
integration remain three later, separately reviewed implementation plans. No
Cursor launch packet is generated until all four implementation plans, their
tests, and repeatable preflight have passed.
