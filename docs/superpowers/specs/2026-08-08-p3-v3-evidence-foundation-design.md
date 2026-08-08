# P3 v3 Minimum Evidence Foundation Design

## Material Passport

- Date: 2026-08-08
- Status: revised after targeted scientific review and workload-role separation;
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
6. profiling workloads cannot be confused with the independent inputs used to
   evaluate mutants and MR portfolios; and
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
research/p3_v3/evaluation-inputs.json
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
  independent evaluation-input construction rule;
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

The frozen categories are `PUBLIC_API`, `CLI`, `EXAMPLE`, `BENCHMARK`, and
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

The protocol freezes size-class-specific execution budgets and category quotas
before seeing frame contents or outcomes. Every nonempty executable category has
a quota of at least one; each size-class budget is at least five, and the budgets
are monotone from `S` through `M` to `L`. If the executable frame fits the
applicable budget, all executable rows are selected. If it does not, selection
first maximizes category coverage, then statically distinct entrypoints and
dependency signatures, with canonical `behavior_id` hash order as the only
tie-breaker. Dynamic coverage, execution success, mutation results, MR results,
project identity, and desired technique label cannot affect selection. Different
languages and build ecosystems use adapters that emit the same canonical
records; unsupported adapters fail visibly rather than falling back to hand
selection.

`profiling-results.json` retains every selected command, input, environment,
version, exit status, raw stream hash, call-trace hash, timeout, and failure. A
site reached by this workload may be tagged `OBSERVED_REACHABLE`. A statically
enumerated site not reached by it is tagged `UNPROFILED`, never
`NOT_APPLICABLE`. `NOT_APPLICABLE` requires the frozen static semantic
applicability predicate to fail.

`profiling_workload_sha256` identifies the canonical selected rows and their
declared inputs, not successful execution output. This prevents an execution
failure from silently changing subject identity or the sampling frame.

#### 6.4.3 Evaluation Inputs

`evaluation-inputs.json` contains the independent contract witnesses used later
to compare original programs, semantic mutants, syntactic mutants, and MR
portfolios. It is not derived from profiling success, project test outcomes,
mutant survival, MR kills, P12 defect identities, reference MRs, or real-fault
outcomes. A witness may be derived from the already frozen semantic contract and
canonical site under a frozen construction rule, but its identity and complete
generation provenance must close before the first evaluated mutant/MR job.

Evaluation inputs never change the public behavior frame, profiling workload,
program-scale class, primary technique stratum, subject ranking, or candidate-
site order. Invalid, non-activating, failed, and inconclusive witnesses remain in
the evidence funnel; a successful witness cannot replace them unless the
protocol had already declared the next deterministic candidate and its stopping
rule.

#### 6.4.4 Claim ceiling and sensitivity

Dynamic statements are limited to behavior exercised by the frozen profiling
workload or evaluation inputs. The study may claim whole-source static
enumeration only for the language/adapters and predicates actually supported;
it may not infer whole-program dynamic reachability from profiling. Technique-
stratified claims must report the public-frame category coverage, selected
fraction, profile failures, and `UNPROFILED` sites for every subject.

The analysis reports whether primary conclusions change under the prespecified
profiling sensitivity views: all successful selected behaviors, each category
removed in turn when at least two categories are present, and static-only
classification with ambiguous cases mapped to `TECH_UNCERTAIN`. These views do
not alter the frozen primary frame or permit post-outcome reselection.

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

All subject-specific contracts, domains, oracles, activation rules, witness
orders, canonical sites, and evaluation-input construction rules are
phase-closed before an evaluated-MR frame is built. Evaluation-input identities
close after contracts and sites but before the first evaluated mutant/MR job.
The contract and evaluation-input builders cannot read candidate/final MR
material or any mutant/MR outcome. In a sibling process, the MR builder receives
only permitted fixed source/build/public documentation and cannot read contracts,
slots, evaluation inputs, patches, certificates, or denominators.

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
behavior frame, profiling workload and reports, frozen contracts, evaluation
inputs, candidate slots, and proposal inputs. It forbids VCS metadata, bug
identities, buggy code, patches, MRs, outcomes, and expected-result commentary.

### 8.3 Package B

Contains frozen originals, certified semantic-mutant trees, syntactic-mutant
trees, denominators, non-reference MR inventory, portfolios, job-list inputs, and
execution code. It forbids Package C mappings, buggy trees, reference MRs, and
real-fault outcomes.

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
5. profiling selection covers categories before adding a second row from a
   category, uses only static diversity plus hash tie-breaking, is unchanged by
   injected execution, mutant, MR, or real-fault outcomes, and retains every
   selected execution failure in the profiling results;
6. project tests in the public behavior frame cannot enter evaluation inputs
   without independently satisfying the frozen witness-construction rule;
7. an unexecuted static site is `UNPROFILED`, and only a failed static semantic
   predicate can produce `NOT_APPLICABLE`;
8. `controlled_subject_id` is stable across bridge aliases while conflicting
   source/build/profiling-workload inputs fail, and `site_id` changes do not
   change the program-level sampling stratum;
9. `C_CONSTRUCT` is input-order invariant, neutral-ID independent, and uses the
   exact `(selection_key, controlled_subject_id)` tie order;
10. `C_CRITERION` includes every unique eligible controlled subject and has no
   sampling path;
11. custodian-provided workloads/strata/sites cannot influence selection, and
   each slot selects the first applicable canonical site or remains
   `NOT_APPLICABLE`;
12. contract and evaluation-input phase close must predate the candidate-MR
   frame and first evaluated job, and either builder rejects the other sibling's
   forbidden material;
13. candidate-MR frame, custodian receipt, final inventory, and portfolios must
   form that exact order; missing or uncertain receipts fail closed;
14. proposal records reject missing prompt/context/response hashes and use
    `UNAVAILABLE_NOT_CLAIMED` rather than fabricated provider parameters;
15. Package A/B forbidden content and Package C early presence fail;
16. a job cannot produce a result without an earlier immutable intent;
17. failed, interrupted, and inconclusive jobs survive reduction;
18. ledger suffix truncation is detected by the phase-close receipt;
19. corrected preflight can pass without modifying the scientific ledger; and
20. a synthetic Phase 0→Phase 7 path verifies exact commitment opening and
    fixed-tree pairing.

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
4. the profiling workload regenerates byte-identically without reading dynamic
   coverage or any mutant, MR, P12 defect, or real-fault outcome, and its result
   funnel retains all selected failures;
5. evaluation inputs have independent provenance, close before evaluated jobs,
   and cannot alter profiles, strata, subject ranks, or site order;
6. profile coverage and `UNPROFILED` funnels bound every dynamic claim, and
   unobserved reachability cannot be reported as `NOT_APPLICABLE`;
7. both subject frames and site enumerations regenerate byte-identically from
   shuffled inputs and use the declared experimental units;
8. contracts and evaluation-input identities phase-close before the isolated
   candidate-MR frame and first evaluated job exist;
9. reference MRs and semantic duplicates cannot enter P3 portfolios, and the
   candidate-frame -> receipt -> final-inventory -> portfolio order is proven;
10. Package A and B materialize and verify without forbidden content;
11. repeatable preflight completes an actual synthetic end-to-end CLI path;
12. scientific intent precedes every synthetic job side effect;
13. phase close detects missing, duplicate, pending, and truncated records;
14. all claim entries remain blocked until result predicates are implemented;
15. RQ4 claim validation limits inference to `P12_PAIRED`, requires the full
    construction-failure funnel and paired-versus-full pre-outcome coverage
    comparison, and treats `P12_FULL` as descriptive only;
16. the focused and repository test suites pass; and
17. no live P12 Holdout, real outcome, or Cursor launch was used to obtain the
    result.

## 14. Scope boundary

After user approval, one implementation plan covers only the five modules, CLI,
and focused tests in Section 4. Semantic patch construction, certification,
syntactic mutation, MR execution, P12 reveal, statistical analysis, and Cursor VM
instructions remain later scientific deliverables.

Before adding a new infrastructure component, its plan must name the scientific
failure it prevents and why an existing JSON/hash/package/job primitive cannot
prevent it. Otherwise the component is deferred.
