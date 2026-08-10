# P3 v3 Minimum-Evidence Alignment Repair 01 Design

## Material Passport

- Date: 2026-08-10
- Repair task: `P3-V3-MEF-ALIGN-REPAIR-01`
- Immutable repair base:
  `9f28080c8b3ed9e25f96a0fcf0444bc92715ca76`
- Governing scientific plan SHA-256:
  `fea00496801c31ba074aa74742f5e6a77019ffc2e344642122a15462d7443830`
- Governing evidence-design SHA-256:
  `7e614e96aac833786d1b29580f8fae7d3f03c6567d7ca94f3e3c017addad2fa9`
- Parent implementation-plan SHA-256:
  `7c55ab41327395b819571da3931f142e916ac9d96910fec10b7d3cdd6e6c4ab3`
- Repair branch: `codex/p3-v3-mef-align-repair-01`
- This design authorizes only code, synthetic fixtures, tests, and audit
  documentation. It authorizes no P12 reveal, real mutant, real MR execution,
  scientific job, network collection, manuscript result, PR, or merge.

## 1. Purpose and acceptance state

Repair the four blocking classes found by independent audit of the minimum
evidence foundation:

1. caller-controlled frame, scale, workload, and site authority;
2. incomplete adapter discovery and non-executable `E_COMMON` flow;
3. a shallow final evidence verifier that accepts fabricated evidence;
4. nonportable preflight, credential persistence, and failed quality gates.

The repair also closes the directly coupled audit findings: exact retry
invariants, MR chronology proof, profiling fallback order, and evidence-map
mutation coverage. Completion returns the foundation to a synthetic readiness
state only. RQ1-RQ4 remain `blocked`.

## 2. Chosen approach

Use a targeted deepening of the existing five production modules and thin CLI.
Do not add a workflow framework, generic schema engine, or new production
module.

Rejected alternatives:

- **Assertion-only patch:** quicker, but leaves caller-provided declarations,
  scale, and sites as hidden scientific authorities and repeats the original
  self-certification defect.
- **Large module split:** cleaner in isolation, but expands the frozen
  implementation surface before scientific behavior is stable and creates an
  unnecessary migration.

The chosen approach makes existing seams deeper: registered adapters produce
discoveries; frame construction derives rather than accepts features; run
records reconstruct retries and outcomes; and `verify-evidence` consumes a
fixed evidence index and independently rebuilds every claimed binding.

## 3. Scientific authority flow

### 3.1 Registered adapter execution

`validate_adapter_registry` continues to prove the exact four adapter IDs,
implementation paths, and source hashes. Its normalized return also carries an
internal verified source-root capability, following the existing generator
registry pattern.

Each registered adapter exposes exactly:

```python
def discover(source_root: Path, build_descriptor: Mapping[str, Any]) -> Mapping[str, Any]
```

The return schema is exact:

```text
adapter_id
ecosystem
source_files
declarations
public_schemas
sites
```

- `source_files` is a sorted unique list of safe regular-file paths used for
  scale counting. Paths under vendored, generated, test-fixture, environment,
  VCS, and build-output directories are rejected.
- `declarations` contains every adapter-discovered public behavior, including
  invalid declarations with public provenance.
- `public_schemas` contains only publicly derived input schemas and their
  provenance. Project-test bodies and fixtures are forbidden.
- `sites` contains syntax-aware canonical path, resolved symbol, and span rows.

The caller cannot provide any of these four collections. The loader invokes
only the source-hash-verified module for the selected ecosystem. Unsupported
ecosystems produce an explicit `ADAPTER_UNSUPPORTED` discovery receipt, zero
executable behaviors, zero public schemas, and zero sites; no manual fallback is
accepted.

Synthetic adapter modules remain test fixtures. They are real executable
registry implementations used to prove the loader and authority boundary, not
production evidence about P12.

### 3.2 Program scale

Scale is derived from adapter-declared source files after core validation. The
core counts nonblank, noncomment source lines using the adapter's frozen
language comment rules and records per-file counts plus the total:

```text
S: total < 10,000
M: 10,000 <= total < 100,000
L: total >= 100,000
```

The CLI no longer accepts `--scale-class`.

### 3.3 Public frame, workload, common inputs, and sites

For each fixed subject materialization:

```text
verified source/build identity
-> execute pinned adapter
-> discovery receipt
-> Public Behavior Frame, including public_schemas
-> derived scale
-> outcome-blind Profiling Workload
-> 30 predetermined E_COMMON rows
-> profiling result ingestion
-> failure-conservative technique profile
-> derived subject profile and canonical sites
```

`build_public_behavior_frame` consumes the adapter discovery receipt, not a
caller declarations list. It preserves `public_schemas` so
`build_common_inputs` can produce executable candidates when an eligible
schema exists.

The CLI no longer accepts `--declarations` or `--features`. The subject profile
uses only the actual workload artifact SHA-256, derived scale, derived technique
profile, and adapter-enumerated sites. Any bridge alias sharing the same
source/build/workload reuses that derived profile.

The batch input to `build-frames` is an exact subject-specification list. Every
row binds a bridge neutral ID to its verified source root, build descriptor,
adapter registry, input-generator registry, and profiling-result artifact.
Each bridge record must have exactly one row; missing, duplicate, or extra rows
fail before outputs. This supports different program scales and implementation
technologies without applying one subject's profile to another.

### 3.4 Profiling selection correction

The first category pass retains the lowest
`(diversity_signature_sha256, behavior_id)`. Later rounds prefer the lowest
unseen diversity signature; after unseen signatures are exhausted, selection is
by lowest remaining `behavior_id` only. A regression fixture makes the two
orders disagree and proves the frozen fallback.

## 4. Evidence reconstruction

### 4.1 Fixed evidence index

`verify-evidence` accepts one `--index` path. The canonical index has an exact
schema and identifies, with expected SHA-256, all required artifacts:

```text
protocol
adapter registries
input-generator registries
public frames
profiling workloads and results
subject frames
common-input inventories and validity receipts
slot artifacts
MR frame/receipt/inventory/portfolio chain
package roots and manifests
job root
ledger
phase-close receipts
P12 denominator
P12 result rows
P12 summary
claim ledger
```

Every collection required by the declared phase coverage is nonempty. Paths are
safe, unique, and read as exact canonical bytes. An index self-hash is useful for
identity but never substitutes for reconstruction.

### 4.2 Independent validators

The final verifier performs these operations rather than checking declared
fields:

1. validate the protocol and compare every referenced registry/policy artifact
   hash with the bytes named in the index;
2. verify every package against its materialized root, not just its manifest;
3. reconstruct the event stream from the immutable attempt tree and require
   byte equality with the supplied ledger;
4. recompute every phase-close receipt from the reconstructed ledger, expected
   job inventory, and output manifest;
5. validate exact `E_COMMON`/validity schemas, ordinals, identities, statuses,
   self-hashes, and their pre-consumer chronology;
6. validate every slot chronology and input-role separation;
7. verify the MR artifact parent chain;
8. verify the frozen P12 denominator, read Phase 7 P12 terminal results from the
   attempt tree, regenerate lower/upper/complete-case summaries, and require
   canonical equality with the supplied summary;
9. validate the exact claim-ledger schema/self-hash and require all claims
   `blocked`.

A PASS requires at least one package, phase receipt, and declared phase artifact
set. Empty optional lists cannot represent a complete evidence set.

### 4.3 MR chronology

The four MR artifacts form a hash-parent chain:

```text
candidate frame
-> custodian receipt(parent=candidate)
-> final inventory(parent=receipt)
-> portfolios(parent=final inventory)
```

`validate_mr_inventory` receives and validates the four canonical artifacts,
their exact types, hashes, parent links, and fail-closed receipt state. A literal
chronology list is not evidence.

### 4.4 Retry identity

For attempts after attempt 1, `reduce_attempts` compares the canonical intent
body after removing only `attempt`. The following must therefore remain exact:

```text
job_id, protocol, phase, argv, cwd, environment, all input hashes, seed,
timeout, object/MR/input/repetition/environment identities, and job role
```

Only the attempt number may change, and only a preceding
`FAIL_INFRASTRUCTURE` permits that change. Mutation tests alter each invariant
field independently.

## 5. Preflight portability and secret handling

### 5.1 Memory probe

The available-memory probe uses:

1. POSIX `SC_PAGE_SIZE * SC_AVPHYS_PAGES` when both exist;
2. on Darwin, exact argv `vm_stat`, parsed with its reported page size and the
   free, inactive, speculative, and purgeable page classes;
3. otherwise, explicit `UNAVAILABLE`.

The Darwin parser is a pure function tested with a frozen output fixture. The
subprocess uses `shell=False`, captures both streams, and has a fixed timeout.
Unavailable memory with a positive minimum remains a preflight failure, but a
supported Darwin host no longer fails merely because `SC_AVPHYS_PAGES` is
absent.

### 5.2 Repository identity and credentials

Preflight normalizes an SSH or HTTPS remote in memory. The canonical receipt
contains only:

```text
repository_identity
origin_transport
origin_sha256
```

It never stores or prints raw HTTPS userinfo. `origin_sha256` hashes the exact
raw value for audit correlation without disclosure. Mutation tests assert that
a token placed in the origin is absent from canonical receipt bytes and CLI
stdout.

### 5.3 Quality gate

Restore the intentional `# noqa: E402` import annotations required by the
standalone CLI's explicit `src` path bootstrap. Remove duplicate dictionary
keys. The required Ruff command must pass under the repository's configured
Ruff version.

## 6. Tests and mutation gates

Every production change follows RED -> GREEN. Required negative cases include:

- caller-provided declarations, scale, workload SHA, sites, or technique labels
  are rejected or have no API path;
- omitting one adapter-discovered public behavior changes the adapter receipt
  and cannot be hidden by a caller input;
- shuffled adapter output regenerates byte-identical frame/site artifacts;
- different S/M/L and Python/CMake synthetic subjects receive independent
  workloads and profiles;
- eligible public schemas generate at least one executable `E_COMMON` row;
- fabricated/rehash-mutated common input, summary, claim ledger, phase receipt,
  MR link, package byte, retry field, or evidence-index membership fails;
- zero packages, receipts, slots when required, or P12 results fail;
- macOS memory fallback passes a positive minimum and malformed `vm_stat` is
  `UNAVAILABLE`;
- HTTPS userinfo never appears in output bytes;
- the profiling fallback chooses the lowest remaining `behavior_id`.

The synthetic Phase 0 -> Phase 7 path must use two subjects with different
ecosystems and scale classes, execute pinned synthetic adapters, produce
executable common inputs, and pass only through the reconstructed final verifier.
It continues to block network sockets and uses no real P12 or scientific job.

## 7. Acceptance criteria

Repair 01 passes only when:

1. all caller-controlled frame/scale/workload/site authority paths are absent;
2. pinned adapter execution is the only discovery path and supplies public
   schemas to `E_COMMON`;
3. subject profiles are independent across at least two technologies and sizes;
4. the published forgery reproducer fails at the first invalid artifact;
5. final summary, phase receipt, MR chronology, package bytes, and retry identity
   are independently reconstructed;
6. focused tests pass on local Python 3.11/macOS and Cursor-compatible Linux;
7. the complete repository suite, Ruff, and `git diff --check` pass;
8. the repaired evidence map cites mutation tests for all previously
   self-declared boundaries;
9. all claims remain `blocked`, with zero real P12 access and zero scientific
   jobs.

After these gates pass, the implementation still requires independent
Standards, Spec, and research-evidence review before controlled-experiment
planning.
