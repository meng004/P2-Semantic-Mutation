# P3 v3 Minimum Evidence Foundation Design

## Material Passport

- Date: 2026-08-08
- Status: revised after targeted scientific review, workload-role separation,
  construct-conditioning repair, and missingness-estimand closure;
  implementation pending
- Scope: only the evidence controls required before controlled semantic-mutant work
- Parent scientific plan SHA-256:
  `911562938a14ad3955a6c1e38080185ba78e92dbf4401efcb10d7c169e4a2772`
- Governing principles SHA-256:
  `4aa9fb17bdfa8976387a4165445b2b0b72e653688187c958fa1beb022075780d`
- Existing P12 v1.1.2 contract SHA-256:
  `6247f3063952fa7c133ca574b5f9667c51b8d4636d84c40bce2753cf9e8bc427`
- Intended execution environment: Python 3.11 and fresh phase-scoped Cursor VMs
  using Grok 4.5 High
- This design authorizes no experiment, P12 reveal, network collection, mutant
  construction, MR execution, or Cursor VM launch.

## 1. Purpose

The foundation provides the smallest executable evidence channel needed to make
the P3 experiment reproducible and non-circular. It must prove:

1. the scientific protocol and analysis choices were frozen before outcomes;
2. controlled subjects were selected from a complete outcome-blind frame;
3. controlled construction saw repaired source but not the corresponding defect,
   reference MR, or real-fault outcome;
4. the controlled fixed source is the same program version later paired with the
   P12 real defect;
5. every planned job, including failures and inconclusive attempts, remains in
   the record;
6. profiling workloads, subject-level primary inputs, and contract-conditioned
   certification inputs cannot be confused with one another; and
7. every manuscript claim traces to an exact result artifact.

Passing this foundation does not support a paper result. It supports only the
existence of a reproducible, outcome-blind input and recording channel.

## 2. Minimum-necessary rule

An engineering mechanism is mandatory only when its failure could change a
scientific object, denominator, outcome, analysis, or claim. The foundation uses:

- canonical JSON as the only structured authority;
- SHA-256 content identity;
- exact Git/source-tree identities where version pairing matters;
- ordinary atomic file creation and replacement;
- one append-only attempt ledger;
- content-addressed package manifests;
- repeatable phase-specific preflight; and
- small study-specific validators.

The following are deliberately deferred because they do not directly strengthen
the current scientific claims:

- a generic schema algebra or generated JSON-Schema catalogue;
- canonical YAML and dual raw/semantic YAML identity;
- a generic claim-state transition framework;
- a custom Cursor controller or one-shot launch protocol;
- mandatory branch names, commit topology, push count, or packet self-hashing;
- platform-level claims of physical absence without provisioner attestation.

Markdown and YAML may be generated for readers, but the canonical JSON and atomic
result rows remain authoritative.

## 3. Authoritative artifacts

The minimum set is:

```text
research/p3_v3/protocol.json
research/p3_v3/p12-bridge.json
research/p3_v3/public-behavior-frame.json
research/p3_v3/profiling-workload.json
research/p3_v3/profiling-results.json
research/p3_v3/input-generator-registry.json
research/p3_v3/evaluation-inputs-common.json
research/p3_v3/evaluation-inputs-contract.json
research/p3_v3/subject-frames.json
research/p3_v3/mr-inventory-and-portfolios.json
research/p3_v3/attempt-ledger.jsonl
research/p3_v3/claim-evidence.json
data/p3_v3/manifests/package-a-construction.json
data/p3_v3/manifests/package-b-controlled-execution.json
data/p3_v3/manifests/package-c-real-holdout.json
data/p3_v3/phase-close/
data/p3_v3/jobs/
data/p3_v3/results/atomic-matrices/
data/p3_v3/results/generated/
data/p3_v3/evidence-package.md
```

Additional detailed files are authorities only when their path and SHA-256 are
listed in `protocol.json` or a package manifest.

Each phase-close filename is its exact canonical `phase_id` plus `.json`. Each
job owns a directory named by its canonical `job_id`, with attempt directories
named by positive decimal attempt number. Each attempt contains exactly one
`intent.json` followed by at most one terminal `result.json`.

## 4. Small implementation surface

The first implementation deliverable uses five focused modules and one thin CLI:

```text
src/p3_v3/artifacts.py
src/p3_v3/bridge_and_frames.py
src/p3_v3/packages.py
src/p3_v3/run_records.py
src/p3_v3/preflight.py
scripts/p3_v3/evidence.py
tests/p3_v3/
```

### 4.1 `artifacts.py`

Provides canonical JSON bytes, SHA-256, exact field/type validation, safe relative
paths, atomic same-directory writes, exclusive creation, and stable study-specific
error codes. It contains no P3 selection or analysis rule.

Canonical JSON uses UTF-8, sorted keys, compact separators, no NaN/infinity, and
exactly one terminal LF in files. An object self-hash excludes its own hash field.

### 4.2 `bridge_and_frames.py`

Validates the P12 bridge, derives the public behavior frame, selects the profiling
workload, recomputes permitted mechanical features, builds `C_CONSTRUCT` and
`C_CRITERION`, validates non-reference MR exclusion receipts, and freezes MR
portfolios. It cannot read P12 buggy source, patches, reference-MR content, any
mutant/MR result, or any real-fault outcome.

The module also constructs the subject-level `E_COMMON` input inventory before
semantic contracts/sites and the slot-level `E_CONTRACT` inventory after
contract/site freeze. It keeps their schemas, provenance, budgets, and consumers
separate.

### 4.3 `packages.py`

Builds and verifies package manifests, allowlists, regular-file bytes, normalized
paths, modes, sizes, and hashes. It rejects symlinks, devices, traversal, duplicate
normalized paths, and forbidden content classes. It copies only declared files
into a clean materialization; it does not fetch, upload, decrypt, or extract an
untrusted archive.

### 4.4 `run_records.py`

Creates immutable job intents and terminal results, appends attempt events, closes
a phase, and verifies the complete ledger plus phase-close receipts. It does not
execute scientific jobs or interpret their results.

### 4.5 `preflight.py`

Normalizes repository identity, verifies the exact commit and dependency lock,
checks declared phase inputs, and executes frozen smoke commands in a disposable
root. It creates only preflight attempt records and never creates a scientific
run or job ID.

### 4.6 CLI

The thin CLI exposes only:

```text
validate-protocol
verify-bridge
build-frames
verify-mr-inventory
build-package
verify-package
run-preflight
verify-run-records
close-phase
verify-evidence
```

It accepts explicit paths, uses `shell=False`, and contains no second copy of a
scientific rule. Local Desktop commands use `rtk`; Cursor VM commands invoke the
same project CLI without `rtk`.

## 5. Frozen protocol

`protocol.json` fixes at least:

- RQ1–RQ4 and the claim ceiling;
- P12 compatibility requirement and downgrade rule;
- semantic-contract and construction-mechanism catalogues;
- subject eligibility and feature derivation;
- public-behavior discovery, profiling-workload budgets and selection, and the
  independent `E_COMMON`/`E_CONTRACT` construction rules and frozen input-
  generator registry/source hashes;
- candidate slots, stopping rules, seeds, timeouts, and retry policy;
- canonical site enumeration, first-applicable-site selection, and
  subject/site/real-fault unit definitions;
- proposal provenance fields: exact provider/model label, prompt/context/raw
  response hashes, UTC timestamp, exposed generation metadata, and the literal
  `UNAVAILABLE_NOT_CLAIMED` for unavailable proprietary parameters;
- syntactic baseline and equivalence policy;
- MR source frame, semantic-signature algorithm, budgets, and sampling rule;
- primary and secondary measures;
- analysis, multiplicity, clustering, sensitivity, and missingness rules;
- the `P12_PAIRED` inferential ceiling, paired-versus-full pre-outcome coverage
  comparison, complete profile-failure funnel, and descriptive-only treatment of
  `P12_FULL`;
- required package roles, job fields, outputs, and prohibited claims; and
- hashes of referenced scripts, dependency lock, and detailed specifications.

The foundation validates these fixed fields but does not implement a generic
claim language. All result claims begin `blocked`. A later analysis command may
update `claim-evidence.json` only by applying the exact study-specific predicates
named in the protocol to frozen result artifacts.

## 6. P12-bound blinded bridge

### 6.1 Envelope

The identified P12 custodian publishes an envelope containing:

```text
schema_version
p12_release_id
p12_repository_identity
p12_contract_path
p12_contract_blob_sha
p12_package_root_sha256
p12_contract_sha256
eligible_inventory_root_sha256
eligible_item_count
records
trust_mode
artifact_sha256
```

`trust_mode` is exactly `PINNED_GIT_RELEASE`. The validator normalizes the P12
repository identity. A separate P3 consumer lock contains exactly
`repository_identity`, `release_commit_sha`, `bridge_path`, `bridge_blob_sha`,
`contract_path`, `contract_blob_sha`, and `package_root_sha256`. The validator
reads the bridge and contract from that exact commit and proves their Git blob
identities and package root. Release commit and bridge blob identities must not
appear inside the bridge they identify, because that would create a
self-referential Git object. This is the only minimum trust mode: the foundation
does not add a generic signature or PKI system. The bridge's `artifact_sha256`
excludes that field under the canonical self-hash rule, but a self-hash alone is
not accepted as proof of origin or completeness. If the pinned release cannot be
verified, RQ4 remains blocked.

### 6.2 Record

There is one visible record per eligible P12 fixed-version snapshot. P3 later
groups records resolving to the same controlled subject:

```text
neutral_snapshot_id
fixed_tree_commitment
normalized_source_tree_sha256
source_archive_sha256
build_descriptor_sha256
eligibility_reason
eligible_for_construct
eligible_for_criterion
```

`neutral_snapshot_id` is deterministically derived from the P12 package root,
normalized source-tree SHA-256, and source-archive SHA-256. It is not chosen by
the custodian. The custodian computes:

```text
fixed_tree_commitment = SHA256(
  "P3-FIXED-TREE-v1" || p12_package_root_sha256 ||
  fixed_git_tree_oid || reveal_nonce
)
```

Here `||` is byte concatenation; the domain and lowercase hexadecimal identities
are ASCII bytes, and `reveal_nonce` is exactly 32 random bytes.

The visible bridge excludes `fixed_git_tree_oid` and `reveal_nonce` as well as
issue, PR, buggy commit, fixed commit, patch, changed symbols, defect family,
reference MR, and all outcomes. The OID and nonce exist only in Package C until
Phase 7.

### 6.3 Feature authority and completeness

P3 derives the public behavior frame, profiling workload, scale,
dependency-cone, program-level implementation-technique features, and
mutation-site enumeration from the permitted fixed source, build descriptor,
and public documentation using frozen rules. Custodian-supplied workloads,
strata, targets, and sites are neither accepted nor used for selection.

The program-version experimental unit is:

```text
controlled_subject_id = SHA256(canonical_json({
  normalized_source_tree_sha256,
  build_descriptor_sha256,
  profiling_workload_sha256,
  domain: "P3-SUBJECT-v1"
}))
```

Each candidate `site_id` is separately derived from
`controlled_subject_id`, canonical relative path, resolved symbol, and source
span, then ordered by path, symbol, span, and site hash. Program-level technique
labels define sampling strata; site-level tags are secondary analysis metadata.

The bridge validator checks record count, unique commitments, deterministic
neutral snapshot IDs and alias groups, inventory root, package root, release
binding, and all hashes. `C_CRITERION`
contains every unique eligible `controlled_subject_id`. Records resolving to the
same controlled subject reuse one profile; conflicting source/build/workload
commitments are a hard failure. An absent or extra item is a hard
compatibility failure, not an opportunity to select a replacement.

### 6.4 Three distinct workload-related authorities

The design separates three objects that answer different scientific questions.
They cannot be substituted for one another.

#### 6.4.1 Public Behavior Frame

`public-behavior-frame.json` is the complete, outcome-blind enumeration of
publicly evidenced ways to exercise the fixed program version. Discovery reads
only the normalized fixed source, build descriptor, dependency metadata, and
public project documentation. Before constructing the frame, P3 computes:

```text
controlled_subject_source_id = SHA256(canonical_json({
  normalized_source_tree_sha256,
  build_descriptor_sha256,
  domain: "P3-SOURCE-v1"
}))
```

The artifact has an exact `category_accounting` entry for every frozen category,
including categories with zero discovered behaviors. Each discovered frame row
records, at minimum:

```text
controlled_subject_source_id
behavior_id
category
provenance_path
provenance_span_or_key
entrypoint
declared_inputs
prerequisites
discovery_status
unsupported_or_exclusion_reason
artifact_sha256
```

The frozen category order is `PUBLIC_API`, `CLI`, `EXAMPLE`, `BENCHMARK`, then
`PROJECT_TEST`. A project need not contain every category. Missing categories
remain explicit in `category_accounting`; unsupported build systems and invalid
public declarations remain explicit provenance-bearing rows. None is removed
from the denominator or triggers replacement by another subject. Project tests
may therefore describe a public behavior, but they do not become evaluation
evidence merely by entering this frame.

Discovery is mechanical and exhaustive relative to the declared file kinds and
adapters. This proves frame completeness under the frozen discovery rule; it
does not by itself prove that repository materials represent all real-world use.

#### 6.4.2 Profiling Workload

`profiling-workload.json` is a deterministic, outcome-blind subset of the public
behavior frame used only to obtain dependency-cone, call-trace, implementation-
technique, and observed-reachability evidence. Selection occurs before mutant
construction, MR inventory, evaluation-input execution, and every defect or
kill outcome is available.

Before bridge intake, the protocol freezes an `adapter-registry.json` with exact
adapter source hashes. The confirmatory allowlist is
`PYTHON_PEP517_V1`, `CMAKE_CTEST_V1`, `MESON_TEST_V1`, and
`AUTOTOOLS_MAKECHECK_V1`; CMake/Autotools adapters may cover C, C++, Fortran, and
CUDA projects without changing the emitted schema. Every other ecosystem is
`ADAPTER_UNSUPPORTED`, remains in category/subject accounting, and cannot be
recovered by hand-selected commands.

The exact Profiling Workload budgets are `B_S=10`, `B_M=15`, and `B_L=20` rows
per controlled subject. Each executable row has:

```text
diversity_signature_sha256 = SHA256(canonical_json({
  category,
  normalized_entrypoint,
  sorted_static_dependency_tags,
  declared_input_schema_sha256,
  domain: "P3-PROFILE-DIVERSITY-v1"
}))
```

Selection first takes one row from every nonempty executable category in frozen
category order, choosing the lowest `(diversity_signature_sha256, behavior_id)`.
It then cycles through the same category order, first taking the lowest row with
an unseen diversity signature and, after those are exhausted, the lowest
remaining `behavior_id`, until the applicable size budget or frame is exhausted.
Thus category counts differ by at most one until a category exhausts. Dynamic
coverage, execution success, mutation results, MR results, project identity, and
desired technique label cannot affect selection.

These are fixed resource budgets, not a power claim. When all five behavior
categories are executable they allocate at least two, three, and four rows per
category before exhaustion for `S`, `M`, and `L`, respectively. The report must
retain the achieved category counts and cannot interpret this convenience
budget as representative of all real-world use.

`profiling-results.json` retains every selected command, input, environment,
version, exit status, raw stream hash, call-trace hash, timeout, and failure. A
site reached by this workload may be tagged `OBSERVED_REACHABLE`. A statically
enumerated site not reached by it is tagged `UNPROFILED`, never
`NOT_APPLICABLE`. `NOT_APPLICABLE` requires the frozen static semantic
applicability predicate to fail.

`profiling_workload_sha256` identifies the canonical selected rows and their
declared inputs, not successful execution output. This prevents an execution
failure from silently changing subject identity or the sampling frame.

Technique scoring is category-balanced and failure-conservative. Let `C` be the
nonempty selected categories, `n_c` all selected rows in category `c`, `a_ct`
successful rows tagged with technique `t`, and `u_c` rows without a usable trace
because of failure, timeout, or adapter uncertainty:

```text
L_t = (1 / |C|) * sum_c (a_ct / n_c)
U_t = (1 / |C|) * sum_c ((a_ct + u_c) / n_c)
```

Every category must have at least one successful trace; if any category lacks
one, the subject is `TECH_UNCERTAIN`. Otherwise, with no unresolved rows, the
exact maximum uses the frozen technique order only as a tie-break. With any
unresolved row, a primary technique is assigned only when one `t` satisfies
`L_t > max_{q != t}(U_q)`; otherwise the subject is `TECH_UNCERTAIN`. Confirmed
multi-label tags have `L_t > 0`; possible tags with `U_t > 0` are retained
separately and cannot define strata. `C_CONSTRUCT` uses only this primary label.

#### 6.4.3 Common and contract-specific Evaluation Inputs

`E_COMMON` and `E_CONTRACT` are separate authorities with disjoint primary
consumers.

Before bridge intake, `input-generator-registry.json` freezes each generator ID,
accepted schema/domain kind, exact implementation path and source SHA-256,
canonical output schema, and failure code. The `E_COMMON` allowlist is
`JSON_SCHEMA_DRAFT2020_12_V1`, `CLI_TOKEN_GRAMMAR_V1`,
`NUMERIC_ARRAY_DOMAIN_V1`, `TEXT_IO_SCHEMA_V1`, and
`BINARY_RECORD_SCHEMA_V1`. The `E_CONTRACT` allowlist is
`CONTRACT_ENUM_DOMAIN_V1`, `CONTRACT_NUMERIC_DOMAIN_V1`,
`CONTRACT_ARRAY_DOMAIN_V1`, `CONTRACT_SEQUENCE_DOMAIN_V1`, and
`CONTRACT_RELATION_PAIR_DOMAIN_V1`. Unregistered kinds are unavailable; there is
no model- or author-generated fallback.

`evaluation-inputs-common.json` contains exactly 30 subject-level input
candidates. It is constructed immediately after the Public Behavior Frame and
before semantic-contract families, sites, patches, evaluated MRs, P12 identities,
or any execution outcome are available. Its generator reads only the normalized
fixed source/build metadata, public input schemas, and public documentation. It
cannot read `PROJECT_TEST` bodies, fixtures, recorded outputs, profiling
results, contracts, or sites. Candidate ordinal `i` is `0..29`; its seed is the
first unsigned 64 bits of `SHA256(canonical_json({domain:
"P3-E-COMMON-SEED-v1", controlled_subject_source_id, ordinal: i}))`.
The 30 ordinals are the denominator: invalid or non-executable candidates remain
`COMMON_INPUT_INVALID` and are never replaced. If no registered adapter can emit
a public input schema, all ordinals are `COMMON_INPUT_UNAVAILABLE`; manual input
creation is forbidden. Thirty is a fixed exposure budget, not a statistical
power guarantee; achieved valid counts and invalid/unavailable counts are always
reported.

Eligible public schema records are canonicalized, deduplicated by raw schema
SHA-256, and ordered by `(schema_selection_key, raw_schema_sha256)`, where
`schema_selection_key` is the SHA-256 of the canonical schema record excluding
subject/project aliases. Ordinal `i` uses schema index `i mod k`, where `k` is
the number of eligible schemas, and invokes only the registry implementation for
that schema kind with its frozen canonical schema bytes and seed. The generator
must return one canonical input envelope and raw payload hash or a stable
invalid/unavailable code. This rule plus the registry source hash determines the
candidate bytes; observed execution never chooses a schema or replacement.

`evaluation-inputs-contract.json` contains exactly five candidates for each
statically applicable slot. It is constructed after site and contract freeze but
before patch proposal. Candidate ordinal `j` is `0..4`; its seed is the first
unsigned 64 bits of `SHA256(canonical_json({domain:
"P3-E-CONTRACT-SEED-v1", controlled_subject_id, slot_id, ordinal: j}))`. It may
read the frozen contract/domain/site but cannot read a
patch, evaluated MR, P12 defect/reference MR, profiling outcome, or any kill or
real-fault outcome. Invalid/non-activating candidates remain in the slot funnel
and are never replaced. Five is a fixed certification-support budget and cannot
be used to claim exhaustive activation coverage.

Each contract names exactly one registered contract-domain generator before
patch proposal. All five ordinals invoke that generator with the frozen
canonical contract/domain bytes and their seeds. An unsupported domain produces
five explicit `CONTRACT_INPUT_UNAVAILABLE` records; it cannot trigger a new
generator, contract edit, site substitution, or manual witness input.

Primary RQ3 and RQ4 comparisons of semantic mutants, syntactic mutants, and P12
buggy/fixed pairs use only `E_COMMON`. `E_CONTRACT` may be used for prepatch
activation checks, certification support, and a separately labelled secondary
contract-conditioned sensitivity analysis; it cannot contribute to the primary
SMS, real-fault detection fraction, or `Delta_sem`. A certification witness
found after observing a patch belongs to neither inventory.

After all 30 ordinals freeze, a separate pre-outcome fixed-source validation
classifies each as executable, invalid, or unavailable. Primary execution job
inventories use only the executable fixed-source identities, while the 30-row
generation/validity funnel remains mandatory. This validity result cannot alter
sites, contracts, subject strata, patches, or MR inventories.

Neither inventory is copied from the Profiling Workload or project tests. A
public test input may coincide with `E_COMMON` only when the frozen public-schema
generator independently emits byte-identical canonical input at its predetermined
ordinal. Input identities and complete generation provenance close before their
consumers execute.

Evaluation inputs never change the public behavior frame, profiling workload,
program-scale class, primary technique stratum, subject ranking, or candidate-
site order.

#### 6.4.4 Claim ceiling and sensitivity

Dynamic statements are limited to behavior exercised by the frozen profiling
workload or evaluation inputs. The study may claim whole-source static
enumeration only for the language/adapters and predicates actually supported;
it may not infer whole-program dynamic reachability from profiling. Technique-
stratified claims must report the public-frame category coverage, selected
fraction, profile failures, and `UNPROFILED` sites for every subject.

The primary technique label uses the category-balanced lower/upper rule above.
The analysis reports whether conclusions change under prespecified secondary
views: complete-case successful traces, each category removed in turn when at
least two categories are present, and static-only classification with ambiguous
cases mapped to `TECH_UNCERTAIN`. These views do not alter the frozen primary
frame or permit post-outcome reselection.

### 6.5 Phase 7 reveal

The revealed mapping covers every bridge record exactly once. For every mapping:

```text
git_tree(revealed_fixed_commit) == fixed_git_tree_oid
normalized_tree(revealed_fixed_commit) == normalized_source_tree_sha256
SHA256("P3-FIXED-TREE-v1" || p12_package_root_sha256 ||
       fixed_git_tree_oid || reveal_nonce) == fixed_tree_commitment
```

A mismatch remains an unpaired failure. It cannot be repaired by using a nearby
commit or another subject.

## 7. Deterministic subject frames

### 7.1 `C_CONSTRUCT`

For each complete eligible record, P3 computes:

```text
subject_selection_key = SHA256(canonical_json({
  controlled_subject_id,
  scale_class,
  technique_vector,
  domain: "P3-C1"
}))
```

The builder partitions by scale × primary technique and uses the total order
`(subject_selection_key, controlled_subject_id)`, selects the lowest pair in
each nonempty cell, and continues round-robin until 18 subjects or exhaustion.
Cells iterate in the frozen order scale `S`, `M`, `L`, then technique
`HYBRID_NATIVE`, `TENSOR_AUTODIFF`, `PROBABILISTIC_SURROGATE`,
`ITERATIVE_STOCHASTIC`, `ARRAY_NUMERICAL`, `SCALAR_CONTROL`, `TECH_UNCERTAIN`.
Empty cells and failed classifications remain explicit. Input order, neutral snapshot ID,
project name, defect identity, and outcomes cannot change ranking.

### 7.2 `C_CRITERION`

The builder includes every unique eligible `controlled_subject_id` from the
compatible bridge. There is no random or hash sampling path. Multiple P12 faults
sharing a tree reuse one controlled profile but remain distinct real-fault rows.
Failed profiles remain failed pairings and are never replaced.

### 7.3 MR independence

`E_COMMON` closes before contracts and sites. Each declared slot then follows one
of exactly two paths:

```text
APPLICABILITY_CLOSED_NOT_APPLICABLE
```

or

```text
SITE_FROZEN -> CONTRACT_FROZEN -> E_CONTRACT_FROZEN
-> PATCH_FROZEN -> CERTIFICATION_WITNESS_SELECTED -> TERMINAL_STATE
```

A `NOT_APPLICABLE` slot has no contract, `E_CONTRACT`, patch, or certification
witness. Every applicable slot closes `E_CONTRACT` before patch proposal. The
contract and input builders cannot read candidate/final MR material or any
mutant/MR outcome. In a sibling process, the MR builder receives only permitted
fixed source/build/public documentation and cannot read contracts, slots, either
input inventory, patches, certificates, or denominators.

The MR builder first freezes the complete candidate frame and semantic
signatures. A custodian receipt then compares those canonical semantic
signatures with P12 reference MRs and returns only candidate ID, decision, reason,
candidate inventory hash, P12 root, and comparison algorithm hash. Missing,
uncertain, reference, exact-variant, and semantic-duplicate cases are excluded
before outcomes. The final inventory freezes only after the receipt, and
portfolios freeze only after the final inventory. Reference MR source or identity
never enters Packages A or B.

## 8. Phase packages and isolation claim

### 8.1 Manifest

Each package manifest records role, parent artifact hashes, sorted file records,
and package tree SHA-256. A file record contains normalized relative path, POSIX
mode, size, raw SHA-256, and content class.

### 8.2 Package A

Contains blinded fixed source, build metadata, public documentation, the public
behavior frame, profiling workload and reports, frozen contracts, `E_COMMON`,
`E_CONTRACT`, candidate slots, and proposal inputs. The proposer receives a clean
allowlisted materialization that excludes profiling results and both input
inventories. Package A forbids VCS metadata, bug identities, buggy code, patches,
MRs, outcomes, and expected-result commentary.

### 8.3 Package B

Contains frozen originals, certified semantic-mutant trees, syntactic-mutant
trees, denominators, non-reference MR inventory, portfolios, `E_COMMON` primary
job-list inputs, separately labelled `E_CONTRACT` sensitivity inputs, and
execution code. Primary job manifests reject `E_CONTRACT` identities. It forbids
Package C mappings, buggy trees, reference MRs, and real-fault outcomes.

### 8.4 Package C

Contains P12 buggy/fixed identities, each bridge record's sealed
`fixed_git_tree_oid` and `reveal_nonce`, and real-fault execution material. It is
supplied only to a new Phase 7 environment after the controlled phase-close
receipt freezes Package B, denominators, portfolios, matrices, mapping rules,
leakage algorithm, and analysis code.

The supported claim is phase-separated package and process isolation. A stronger
claim that Package C was physically unavailable to the platform requires an
external provisioner attestation. Package manifests and directory scans do not
prove platform-wide non-possession.

## 9. Attempt ledger and phase close

### 9.1 Job intent and result

Before a scientific job's first side effect, exclusively create and fsync
`intent.json` containing job ID, protocol hash, phase, argv, cwd identity,
environment hash, input hashes, seed, timeout, and attempt number. A terminal
`result.json` records exit/status, output hashes, duration, and failure code.
The intent is never overwritten.

Allowed terminal states are `PASS`, `FAIL_SCIENTIFIC`, `FAIL_INFRASTRUCTURE`,
`INCONCLUSIVE`, and `MISSING_WITH_REASON`. A pending intent after interruption is
evidence, not permission to erase or silently rerun it.

### 9.2 Attempt ledger

Preflight receipts are separate non-scientific artifacts. Parallel workers write
only immutable job-local intent/result pairs. After the frozen attempt inventory
is complete, one reducer exclusively creates one immutable JSONL ledger in
canonical job-ID and contiguous attempt order. Retry is represented by the next
attempt of the same job; only a completed infrastructure failure permits it, and
at most three attempts are retained. Ledger events have contiguous sequence, a
unique `(job_id, attempt, kind)` identity, previous hash, and self-hash. The
reducer operation and phase-close receipt are separate child artifacts rather
than mutations of the ledger.

### 9.3 Phase-close receipt

A phase closes with:

```text
phase_id
protocol_sha256
expected_job_inventory_sha256
expected_job_count
terminal_result_count
ledger_event_count
ledger_head_sha256
ledger_raw_sha256
output_manifest_sha256
artifact_sha256
```

The next phase names this receipt as a parent. This detects ledger suffix removal;
a previous-hash chain alone is insufficient.

### 9.4 P12 outcome and missingness estimand

Before Package C is mounted and before any Phase 7 outcome is opened, freeze the
exact `P12_PAIRED` membership, every eligible real-fault × MR-portfolio ×
`E_COMMON` job, and the denominator receipt. Only `E_COMMON` candidates already
classified as executable on the controlled fixed version enter this planned
paired denominator. Their membership cannot change after buggy/fixed execution.
Inputs rejected before reveal remain `COMMON_INPUT_INVALID` or
`COMMON_INPUT_UNAVAILABLE` in the construction funnel and are not silently
replaced.

Each planned Phase 7 row has exactly one terminal scientific outcome:

- `MR_VIOLATION`: the frozen MR oracle reports a violation;
- `MR_SATISFIED`: the frozen MR oracle reports satisfaction;
- `DECLARED_EXCEPTION_OR_TIMEOUT_VIOLATION`: only when the pre-outcome frozen MR
  oracle declares that exact exception or timeout to be a violation;
- `SCIENTIFIC_INCONCLUSIVE`: an output exists but the frozen oracle cannot
  classify it;
- `INFRASTRUCTURE_UNRESOLVED`: the prespecified infrastructure attempts are
  exhausted without a scientific result.

The primary intention-to-evaluate lower-bound detection rate retains every
planned row in the denominator. `MR_VIOLATION` and a declared exception/timeout
violation contribute one; every other terminal outcome contributes zero. A
prespecified upper-bound sensitivity changes only `SCIENTIFIC_INCONCLUSIVE` and
`INFRASTRUCTURE_UNRESOLVED` to one; `MR_SATISFIED` remains zero. Complete-case
analysis is secondary and cannot replace the lower-bound primary estimand.
Project and budget aggregation for RQ4 uses the lower-bound row outcomes and
reports the two missingness classes separately. Neither execution success nor
the direction of an MR result may add, remove, or reweight a `P12_PAIRED` item.

## 10. Repeatable phase preflight

Preflight verifies normalized `owner/repository`, exact commit, clean declared
input materialization, OS/architecture, dependency lock, CPU/memory/disk,
subprocess capture, timeout, atomic writes, file locking, worker limit, and frozen
smoke commands.

It receives inputs for the current phase only. Package A/B preflight cannot name,
mount, or inspect Package C. A failure records raw stream hashes and a stable
reason, may be diagnosed, and may be rerun under a new preflight attempt ID. It
does not consume a scientific job or create `RUN_INTENT`.

Scientific authorization begins only after preflight passes, protocol and phase
inputs validate, the canonical job inventory is frozen, and the first job intent
is durably created.

## 11. Retry policy

- Preflight may be rerun after diagnosis.
- A transient infrastructure operation may have at most three prespecified
  attempts with identical job identity, inputs, command, and seed.
- A deterministic code, schema, contract, identity, or scientific failure is not
  retried under the same protocol version.
- Repair increments the protocol version and reruns the complete affected phase.
- Every earlier intent, failure, inconclusive result, and repair remains in the
  ledger and phase-close accounting.

## 12. Tests

All foundation tests use synthetic fixtures. The minimum matrix proves:

1. canonical JSON and every declared one-byte mutation behave deterministically;
2. pinned repository/release/path/blob/package-root mutations fail;
3. visible bridge bytes containing a fixed tree OID or reveal nonce fail, and a
   commitment, nonce, OID, normalized-tree, or source-archive mutation fails at
   reveal;
4. public-behavior discovery is input-order invariant, accounts for every
   missing category, retains every unsupported and invalid declaration, and
   rejects any discovered behavior without public provenance;
5. the adapter registry accepts only the four frozen adapter IDs and exact
   source hashes; an unsupported ecosystem remains `ADAPTER_UNSUPPORTED` and
   cannot fall back to a hand-selected command;
6. profiling selection enforces `B_S=10`, `B_M=15`, and `B_L=20`, covers
   categories in frozen round-robin order, prefers unseen static diversity
   signatures, is invariant to input order and injected outcomes, and retains
   every selected execution failure;
7. category-balanced technique intervals count failed/uncertain rows in their
   original category denominators; a robust winner is assigned only under the
   frozen lower-versus-upper rule, otherwise the result is `TECH_UNCERTAIN`;
8. `E_COMMON` always materializes 30 predetermined ordinals before contracts or
   sites, is invariant to injected contract, patch, MR, P12, and execution
   outcomes, cannot read project-test bodies or fixtures, uses the exact frozen
   generator registry/schema round-robin to reproduce payload bytes, and never
   replaces an invalid or unavailable ordinal;
9. only a statically applicable slot materializes its five predetermined
   `E_CONTRACT` ordinals through its predeclared registry generator; an
   unsupported domain yields five unavailable rows, while an inapplicable slot closes on the
   `APPLICABILITY_CLOSED_NOT_APPLICABLE` path with no contract, patch, input, or
   witness artifact;
10. primary job construction rejects every `E_CONTRACT` or post-patch
    certification-witness identity, while a separately labelled sensitivity
    job rejects `E_COMMON`/`E_CONTRACT` role confusion;
11. an unexecuted static site is `UNPROFILED`, and only a failed static semantic
   predicate can produce `NOT_APPLICABLE`;
12. `controlled_subject_id` is stable across bridge aliases while conflicting
   source/build/profiling-workload inputs fail, and `site_id` changes do not
   change the program-level sampling stratum;
13. `C_CONSTRUCT` is input-order invariant, neutral-ID independent, and uses the
   exact `(selection_key, controlled_subject_id)` tie order;
14. `C_CRITERION` includes every unique eligible controlled subject and has no
   sampling path;
15. custodian-provided workloads/strata/sites cannot influence selection, and
   each slot selects the first applicable canonical site or remains
   `NOT_APPLICABLE`;
16. the `E_COMMON` identity receipt predates site/contract construction and its
    validity receipt predates the primary job inventory; every applicable slot's
    `E_CONTRACT` receipt predates its patch; all predate their first consumer, and
    sibling builders reject forbidden material;
17. candidate-MR frame, custodian receipt, final inventory, and portfolios must
   form that exact order; missing or uncertain receipts fail closed;
18. proposal records reject missing prompt/context/response hashes and use
    `UNAVAILABLE_NOT_CLAIMED` rather than fabricated provider parameters;
19. Package A/B forbidden content and Package C early presence fail;
20. a job cannot produce a result without an earlier immutable intent;
21. failed, interrupted, and inconclusive jobs survive reduction;
22. the Phase 7 denominator and `P12_PAIRED` membership cannot change after
    outcomes; lower-bound, upper-bound, and complete-case calculations implement
    the exact frozen terminal-state rules and report both missingness classes;
23. ledger suffix truncation is detected by the phase-close receipt;
24. corrected preflight can pass without modifying the scientific ledger; and
25. a synthetic Phase 0→Phase 7 path verifies exact commitment opening,
    fixed-tree pairing, and the frozen P12 missingness estimand.

The implementation does not wait for generic framework tests. The first release
is complete when this focused matrix and the repository regression suite pass.

## 13. Acceptance criteria

The minimum evidence foundation is ready for the controlled-experiment
implementation plan only when:

1. the P12 bridge is authenticated, complete, and exact-version verifiable;
2. the visible bridge discloses no fixed Git tree OID and every Phase 7 reveal
   opens its commitment and normalized source snapshot exactly;
3. the public behavior frame regenerates completely from permitted public
   evidence and retains missing, unsupported, and invalid declarations;
4. the profiling workload uses only the exact adapter registry, budgets, category
   round-robin, and static diversity rule; it regenerates byte-identically
   without reading dynamic coverage or any mutant, MR, P12 defect, or real-fault
   outcome, and its result funnel retains all selected failures;
5. technique classification uses category-equal lower/upper scores, never drops
   failed profiling rows, and yields `TECH_UNCERTAIN` when no robust winner exists;
6. all 30 `E_COMMON` ordinals close before sites/contracts and are the only
   primary RQ3/RQ4 inputs; their schema selection and bytes regenerate from the
   frozen input-generator registry; each applicable slot's five `E_CONTRACT`
   ordinals close before its patch through its predeclared generator and enter
   only activation, certification, or labelled sensitivity analyses;
7. the two terminal slot paths reject contract/input/patch artifacts for
   `NOT_APPLICABLE` slots and reject missing `E_CONTRACT` for applicable slots;
8. neither input inventory can alter profiles, strata, subject ranks, or site
   order, and no post-patch certification witness can enter either inventory;
9. profile coverage and `UNPROFILED` funnels bound every dynamic claim, and
   unobserved reachability cannot be reported as `NOT_APPLICABLE`;
10. both subject frames and site enumerations regenerate byte-identically from
   shuffled inputs and use the declared experimental units;
11. contracts and input identities phase-close in their declared chronology
    before the isolated candidate-MR frame and first evaluated job exist;
12. reference MRs and semantic duplicates cannot enter P3 portfolios, and the
   candidate-frame -> receipt -> final-inventory -> portfolio order is proven;
13. Package A and B materialize and verify without forbidden content;
14. repeatable preflight completes an actual synthetic end-to-end CLI path;
15. scientific intent precedes every synthetic job side effect;
16. phase close detects missing, duplicate, pending, and truncated records;
17. all claim entries remain blocked until result predicates are implemented;
18. RQ4 claim validation limits inference to frozen `P12_PAIRED`, uses the
   intention-to-evaluate lower-bound as primary, reports upper-bound and
   complete-case sensitivities plus unresolved counts, requires the full
   construction-failure funnel and paired-versus-full pre-outcome coverage
   comparison, and treats `P12_FULL` as descriptive only;
19. the focused and repository test suites pass; and
20. no live P12 Holdout, real outcome, or Cursor launch was used to obtain the
    result.

## 14. Scope boundary

After user approval, one implementation plan covers only the five modules, CLI,
and focused tests in Section 4. Semantic patch construction, certification,
syntactic mutation, MR execution, P12 reveal, statistical analysis, and Cursor VM
instructions remain later scientific deliverables.

Before adding a new infrastructure component, its plan must name the scientific
failure it prevents and why an existing JSON/hash/package/job primitive cannot
prevent it. Otherwise the component is deferred.
