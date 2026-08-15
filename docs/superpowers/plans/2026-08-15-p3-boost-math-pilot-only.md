# Boost.Math PILOT_ONLY Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Every execution-bearing gate requires separate user authorization.

## Goal

Create a machine-isolated Boost.Math single-subject `PILOT_ONLY` path that later proves minimum end-to-end feasibility after independent reviews and two explicit user authorizations. This plan does not implement that path. This plan does not authorize source mounting, CMake configure, baseline build, mutant construction, mutant evaluation, preflight, profiling, or any confirmatory scientific run.

The unique later subject is the historically associated P12 item `C-BOOSTMATH-001` bound to neutral snapshot `74cdc825c3c728c25f5ea857af1565350515a4e631fb0a874c26e810ec437886`. Because that association already exists, the subject is `PILOT_ONLY` and must never enter a blind confirmatory denominator.

Success for a later authorized execution is a closed `PILOT_ONLY` evidence package whose schemas, `execution_class`, and `denominator` are rejected by every confirmatory entry point. Failure to find two specification-supported relations, four real semantic mutants, four paired syntactic baselines, or two independent evaluation MRs is a recorded stop, not a reason to shrink, replace, or relabel the frozen objects.

## Architecture

The later implementation adds a sibling namespace beside the existing confirmatory foundation. It reuses durable primitives and the CMake adapter. It does not extend Protocol V4, the claim ledger, Package A, Package B, Package C, or P12 reveal.

Reuse without modification of scientific meaning:

- `p3_v3.artifacts.EvidenceError`, `canonical_json_bytes`, `canonical_sha256`, `file_sha256`, `validate_exact_object`, `validate_sha256`, `write_canonical_json`, `read_canonical_json`, `safe_relative_path`
- `p3_v3.bridge_and_frames.SourceSnapshot`, `SourceSnapshotEntry`, `canonical_source_tree_sha256`
- `p3_v3.adapters.cmake_ctest_v1.discover(source_snapshot, build_descriptor: Mapping[str, Any]) -> dict[str, Any]`
- `p3_v3.packages.ALLOWED_CLASSES` remains the confirmatory class set and must stay free of `PILOT_ONLY`

New isolated module `src/p3_v3/pilot.py` owns every schema whose `schema_version` starts with `p3-pilot-`. New CLI `scripts/p3_v3/pilot.py` is the only command surface that may write under `data/p3_v3/pilot/`. Existing `scripts/p3_v3/evidence.py` confirmatory commands must reject any object whose `schema_version` starts with `p3-pilot-` or whose `execution_class` or `denominator` equals `PILOT_ONLY`.

Data flow after later authorization:

1. User-mounted public source archive is hashed, extracted under the reject rules in Task 2, and materialized.
2. `canonical_source_tree_sha256` must equal `93a62859d7fdd6b2068e494bbe6e3e27180b874cbd27055ac27f941e507a90d8`.
3. Two outcome-blind hash chains freeze common inputs, sites, contracts, patches, certification policy, and a sibling MR inventory.
4. `pilot-freeze.json` assembles only after both chains close.
5. Authorized execution uses a deterministic job builder, isolated original and mutant roots, and an executable kill oracle.
6. Closure writes `score-task.yml`, `experiment-ledger.yml`, `pilot-receipt.json`, and `docs/review_20260815/boost_math_pilot_evidence_package.md`.

## Tech Stack

- Language: Python 3.11 or newer, the same interpreter already used by `tests/p3_v3`
- Import path: `PYTHONPATH=src`
- Test runner: `python3 -m pytest`
- Artifact encoding: UTF-8, canonical JSON with sorted keys, separators `("," , ":")`, exactly one terminal LF, `allow_nan=False`
- YAML artifacts: UTF-8, LF, no tab indentation, parsed by `yaml.safe_load` only after a byte-identity hash is recorded
- Build stack for the later subject: CMake and C++, CPU-only
- Adapter: `CMAKE_CTEST_V1` / ecosystem `cmake`
- Hash: SHA-256 lowercase hex
- Time: UTC timestamps in `YYYY-MM-DDTHH:MM:SSZ`
- Process launch: `subprocess.run(argv, shell=False, capture_output=True, check=False)`
- Forbidden in this plan and in later pilot code: network download, Package C, P12 reveal, claim-ledger writes, Protocol V4 mutation, automatic retry, CUDA as a required capability

## Global Constraints

- Current repository state is `PHASE1_CLOSED`. This repaired plan may reach only `PILOT_PLAN_REVIEW_CANDIDATE`. `PILOT_PLAN_FROZEN` requires an independent GPT-5.6 Sol High PASS on the later fixed commit that contains this repaired file.
- `claims` remain `blocked` for C1 through C8 and RQ1 through RQ4. Later code must not import a writer for `research/evidence/p3_claim_ledger_v1.3.0.yml`.
- Pilot objects use `execution_class=PILOT_ONLY` and `denominator=PILOT_ONLY`. Confirmatory code continues to accept only `SYNTHETIC_INFRASTRUCTURE`, `NON_SCIENTIFIC_CONTROL`, and `REAL_SCIENTIFIC`.
- Native C++ profiling is not a precondition. Phase 1 profiling results for this subject are `ADAPTER_UNCERTAIN` with `failure_code=PHASE1_PROFILING_NOT_EXECUTED` and `primary_technique=TECH_UNCERTAIN`. Later pilot code must not call `scripts/p3_v3/evidence.py run-preflight` or any profiling runner as a gate.
- CUDA is not required. Absence of a CUDA toolchain is not `E_PILOT_SOURCE_IDENTITY`, not `E_PILOT_FREEZE_INCOMPLETE`, and not a stop condition.
- The historical site count 4,028 is not an input, not an acceptance number, and not a freeze field.
- `erf(x) + erfc(x) ≈ 1` and `erf(-x) ≈ -erf(x)` are non-binding candidates only. They must not appear as frozen `construction_contract_id` values unless a later authorized freeze cites mounted public specification evidence.
- After freeze, compile failure, non-trigger, non-kill, timeout, or an undesired matrix cannot replace a relation, site, operator, mutant, baseline, MR, input, or timeout.
- Automatic retry is forbidden. A new run requires a new `run_id` and a new explicit user authorization.
- This node and every later task are forbidden from reading Package C, P12 reveal, buggy revisions, defect patches, reference MR, evaluated MR, mutant outcome, or real-fault outcome while constructing or freezing objects.

## Authority and Frozen Inputs

| Object | Path | SHA-256 |
|---|---|---|
| Phase 1 Sol High final review | `docs/review_20260815/phase1_sol_high_final_review.md` | `95345c4229e8e3dedd21e3f7da022fc5daeceb1018392dc1d0e3e35b00fa5a7d` |
| Scientific charter | `docs/superpowers/plans/2026-08-12-p3-return-to-scientific-critical-path.md` | `bd9234e3a26557e0036e42415528f983f2c18313295352ddffb4ccc076c1d5e4` |
| Governing scientific plan | `docs/superpowers/plans/2026-08-08-p3-semantic-mutant-argumentation-experiment.md` | `fea00496801c31ba074aa74742f5e6a77019ffc2e344642122a15462d7443830` |
| Protocol V4 file | `data/p3_v3/protocol/protocol.json` | `240d8270d41802c9d5b86f30564eadd1a86fd9ed09de2c7e947d17c1a4d78519` |
| Environment lock | `data/p3_v3/protocol/environment_lock.json` | `7706b4ce272d09df13c5212b04ec0f2519932f4225d5eac0d052d3225c7ff35f` |
| Claim ceiling authority | `data/p3_v3/protocol/claim_ceiling_authority.json` | `1f46b7cd97e6ddf6d65f6c52a552f4e4b6680a987a088d4f5a65ebc19bf017ed` |
| Claim ledger | `research/evidence/p3_claim_ledger_v1.3.0.yml` | `bf4979662697b2d0565bb70eec88b22673e84bee93b61234555342efb4082a68` |
| Phase 1 receipts | `data/p3_v3/phase1_frames/receipts.json` | `8eeccfe4d1aebb09e6ee9ad2fadb82ac5b8697c40f602592faa6b3878692a440` |
| Pass-1 baseline manifest | `data/p3_v3/phase1_frames/pass1_baseline_manifest.json` | `b0be90ded75a4242bf883698d2b8c3f0c55d70b1b0928d7068bc1a3797e4eb11` |

Boost.Math Phase 1 frames, all under `data/p3_v3/phase1_frames/out/`, suffix `74cdc825c3c728c25f5ea857af1565350515a4e631fb0a874c26e810ec437886`:

| File | SHA-256 |
|---|---|
| `adapter-discovery` | `87fb9d05278c5c2e713c8a9d7f398cb1a1c84562df27b590e6d37f98fd7c1dd1` |
| `derived-subject` | `654a5c8a26b85013a44665dd92c59a66afee9f639ec7d28535d58357ec696f20` |
| `evaluation-inputs-common` | `92d35c3cf98a1287703f8d00dd2343cfa792b2a0e035bce63d9850324f95b239` |
| `profiling-results` | `5a1de4c1a9e52efcc100a448e018229abc984bc350a805c530133f7e689cc133` |
| `profiling-workload` | `e6cd3b5054bdac30dea8e6fbc613c29758be6a97ead4d6d134d33dfdfc8c8380` |
| `public-behavior-frame` | `a740d5019a19ee354f07e73e7c542dd1d79fb8969a2af48d5ef7975e534da4d3` |
| `source-scale` | `dc9b56fe81bcf8301e6164f15007c6f57ee11e79cfff1b84e66906cb7de228d0` |
| `technique-profile` | `da09281afcfb30d41f6f52823afbca9a994a543ae1ef8b82198b5aea58a5c91f` |

Frozen subject facts that later code must copy verbatim into every pilot artifact:

- `p12_item_id`: `C-BOOSTMATH-001`
- `neutral_snapshot_id`: `74cdc825c3c728c25f5ea857af1565350515a4e631fb0a874c26e810ec437886`
- `normalized_source_tree_sha256`: `93a62859d7fdd6b2068e494bbe6e3e27180b874cbd27055ac27f941e507a90d8`
- `controlled_subject_source_id`: `e5f21a7d067d641d0a20bfc57c61e630d6f7588ef30235cea49c9a9cf950c7a7`
- `controlled_subject_id`: `89b0e6791c611b465b9216e833e0c526a53ffd6946b5cd20de045e3641f43914`
- `build_descriptor_sha256`: `68d2e0fd34b845bb0df22b29003f26259d5655d2ec80c18895ff36904db2d95d`
- `adapter_id`: `CMAKE_CTEST_V1`
- `ecosystem`: `cmake`
- `scale_class`: `L`
- `total_effective_lines`: `258766`
- `public_api_declaration_count`: `487`
- `selected_workload_rows`: `20`
- `primary_technique`: `TECH_UNCERTAIN`
- `execution_class`: `PILOT_ONLY`
- `denominator`: `PILOT_ONLY`
- `protocol_predecessor_sha256`: `240d8270d41802c9d5b86f30564eadd1a86fd9ed09de2c7e947d17c1a4d78519`
- `environment_lock_sha256`: `7706b4ce272d09df13c5212b04ec0f2519932f4225d5eac0d052d3225c7ff35f`
- `cpu_only`: `true`
- `cuda_required`: `false`

## Scientific Scope and Claim Ceiling

Pilot purpose: minimum end-to-end feasibility on one known-identity CPU-only subject.

Pilot non-purpose:

- The pilot does not enter the formal population denominator.
- The pilot does not support RQ4.
- The pilot does not support predictive-validity or incremental-value claims.
- The pilot does not compute inferential statistics, population effects, or cross-project generalization.
- After a later closed pilot, RQ1, RQ2, and RQ3 may at most become single-case observed-candidate notes inside the pilot evidence package. Observed status is decided only by a later independent evidence review. This plan does not grant that status.
- C1 through C8 and RQ1 through RQ4 stay `blocked`.
- `research/evidence/p3_claim_ledger_v1.3.0.yml` must remain byte-identical to `bf4979662697b2d0565bb70eec88b22673e84bee93b61234555342efb4082a68`.

Exact later freeze cardinality, unchanged:

| Object | Count | Rule |
|---|---|---|
| Construction contracts | 2 | Each must be supported by mounted public specification text |
| Semantic mutants | 4 | At least 2 distinct implementation sites |
| Syntactic baseline mutants | 4 | One-to-one pair with the 4 semantic mutants |
| `PILOT_COMMON` inputs | 30 | Shared across all 8 mutants; both contracts must share one executable input schema |
| `PILOT_CONTRACT` inputs | 5 per contract | The two contract groups must have distinct artifact identities |
| Independent evaluation MRs | 2 | Sibling inventory; does not change the 2/4/4/30/5 shorthand |

If those counts cannot be satisfied, the freeze command must write `data/p3_v3/pilot/boost_math/pilot-insufficiency.json` with `status=INSUFFICIENT` and exit 2 using `E_PILOT_FREEZE_INCOMPLETE`. It must not invent substitutes.

## File Map

Later Create files, none of which this repair node may create:

- `src/p3_v3/pilot.py`
- `scripts/p3_v3/pilot.py`
- `tests/p3_v3/test_pilot.py`
- `tests/p3_v3/test_pilot_leakage.py`
- `tests/p3_v3/test_pilot_extract.py`
- `tests/p3_v3/fixtures/pilot/valid_plan_min.json`
- `tests/p3_v3/fixtures/pilot/valid_source_manifest_min.json`
- `tests/p3_v3/fixtures/pilot/confirmatory_denied_plan.json`
- `data/p3_v3/pilot/boost_math/pilot-plan.json`
- `data/p3_v3/pilot/boost_math/score-task.yml`
- `data/p3_v3/pilot/boost_math/source-manifest.json`
- `data/p3_v3/pilot/boost_math/chain/pilot-common.json`
- `data/p3_v3/pilot/boost_math/chain/sites.json`
- `data/p3_v3/pilot/boost_math/chain/contracts.json`
- `data/p3_v3/pilot/boost_math/chain/pilot-contract.json`
- `data/p3_v3/pilot/boost_math/chain/semantic-patches.json`
- `data/p3_v3/pilot/boost_math/chain/syntactic-baselines.json`
- `data/p3_v3/pilot/boost_math/chain/certification-policy.json`
- `data/p3_v3/pilot/boost_math/chain/mr-inventory.json`
- `data/p3_v3/pilot/boost_math/pilot-freeze.json`
- `data/p3_v3/pilot/boost_math/experiment-ledger.yml`
- `data/p3_v3/pilot/boost_math/pilot-receipt.json`
- `data/p3_v3/pilot/boost_math/attempts/`
- `docs/review_20260815/boost_math_pilot_evidence_package.md`

Later Modify files:

- `src/p3_v3/packages.py`
- `src/p3_v3/run_records.py`
- `scripts/p3_v3/evidence.py`
- `tests/p3_v3/test_packages.py`
- `tests/p3_v3/test_run_records.py`
- `tests/p3_v3/test_cli.py`

Forbidden later Modify files:

- `research/evidence/p3_claim_ledger_v1.3.0.yml`
- `data/p3_v3/protocol/protocol.json`
- `data/p3_v3/protocol/environment_lock.json`
- `data/p3_v3/protocol/claim_ceiling_authority.json`
- `data/p3_v3/phase1_frames/receipts.json`
- every Boost.Math Phase 1 frame listed above

## Pilot Artifact Contracts

Five named schemas, and any future schema whose version starts with `p3-pilot-`, are pilot artifacts:

- `p3-pilot-plan-v1`
- `p3-pilot-source-manifest-v1`
- `p3-pilot-freeze-v1`
- `p3-pilot-attempt-v1`
- `p3-pilot-receipt-v1`

Common fields on every durable JSON pilot artifact, and only these common fields:

```text
schema_version: str
execution_class: "PILOT_ONLY"
denominator: "PILOT_ONLY"
p12_item_id: "C-BOOSTMATH-001"
neutral_snapshot_id: "74cdc825c3c728c25f5ea857af1565350515a4e631fb0a874c26e810ec437886"
normalized_source_tree_sha256: "93a62859d7fdd6b2068e494bbe6e3e27180b874cbd27055ac27f941e507a90d8"
controlled_subject_id: "89b0e6791c611b465b9216e833e0c526a53ffd6946b5cd20de045e3641f43914"
controlled_subject_source_id: "e5f21a7d067d641d0a20bfc57c61e630d6f7588ef30235cea49c9a9cf950c7a7"
predecessor_sha256: list[str]
artifact_sha256: str
```

`artifact_sha256` is `canonical_sha256` of the object with that field removed. `predecessor_sha256` is a sorted unique list of lowercase SHA-256 strings.

Only `p3-pilot-attempt-v1` additionally requires:

```text
argv: list[str]
cwd_identity: str
timeout_seconds: int
started_at: str
ended_at: str
exit_code: int | None
stdout_sha256: str
stderr_sha256: str
terminal_status: str
failure_reason: str
wall_seconds: float
cpu_seconds: float
peak_rss_bytes: int
run_id: str
job_id: str
attempt: 1
gate_id: str
```

`attempt` other than `1` is `E_PILOT_RETRY_FORBIDDEN`. `terminal_status` is one of `PASS`, `FAIL_SCIENTIFIC`, `FAIL_INFRASTRUCTURE`, `INCONCLUSIVE`, `INSUFFICIENT`, `TIMEOUT`.

Discriminator, fail-closed on unknown future schemas:

```python
from collections.abc import Mapping
from typing import Any

PILOT_EXECUTION_CLASS = "PILOT_ONLY"
PILOT_DENOMINATOR = "PILOT_ONLY"

def is_pilot_artifact(value: Mapping[str, Any]) -> bool:
    schema = value.get("schema_version")
    execution = value.get("execution_class")
    denominator = value.get("denominator")
    return (
        isinstance(schema, str)
        and schema.startswith("p3-pilot-")
    ) or execution == PILOT_EXECUTION_CLASS or denominator == PILOT_DENOMINATOR

def reject_confirmatory_pilot(value: Mapping[str, Any], context: str) -> None:
    if is_pilot_artifact(value):
        raise EvidenceError(
            "E_PILOT_DENOMINATOR_LEAK",
            f"{context} rejected PILOT_ONLY or p3-pilot schema",
        )
```

A confirmatory seam must call `is_pilot_artifact` before filename checks. An unknown `schema_version` such as `p3-pilot-future-v9` must be rejected.

### Schema `p3-pilot-plan-v1`

Machine plan artifact path: `data/p3_v3/pilot/boost_math/pilot-plan.json`.

Producer: Task 1 at `G1_IMPLEMENTATION`, only after an archived Sol High plan-review verdict file exists. The producer binds:

- `markdown_plan_sha256`: SHA-256 of this Markdown file
- `sol_high_plan_verdict_sha256`: SHA-256 of the archived independent review file
- `cardinality`: `{"relations":2,"semantic_mutants":4,"syntactic_mutants":4,"pilot_common":30,"pilot_contract_per_relation":5,"evaluation_mrs":2}`
- `timeouts`: `{"source_identity_validation":300,"cmake_configure":900,"baseline_build":3600,"baseline_public_behavior_smoke":1800,"mutant_build":900,"mutant_evaluation":600,"full_pilot":14400}`
- `non_binding_relation_candidates` with `binding=false`

This schema is not a source-identity document.

### Schema `p3-pilot-source-manifest-v1`

Path: `data/p3_v3/pilot/boost_math/source-manifest.json`.

Additional keys:

```text
archive_sha256: str
archive_bytes: int
build_descriptor_sha256: str
authorization_a_sha256: str
mount_path_sha256: str
extractor_policy_sha256: str
```

A source-manifest object must fail `validate_pilot_plan`. `validate_pilot_source_manifest` must require the exact identity fields listed above plus the common fields. Missing any identity field is `E_PILOT_SOURCE_IDENTITY`.

### Schema `p3-pilot-freeze-v1`

Path: `data/p3_v3/pilot/boost_math/pilot-freeze.json`.

Additional keys: `freeze_id`, `gate_id` equal to `G2_SOURCE_AND_FREEZE`, the seven construction-chain SHA-256 fields, `mr_inventory_sha256`, `construction_contracts`, `semantic_mutants`, `syntactic_mutants`, `pairs`, `pilot_common_inputs`, `pilot_contract_inputs`, `evaluation_mrs`, `outcome_bytes_read` equal to `false`. Cardinality is 2/4/4/30/5 plus exactly 2 `evaluation_mr_id` values. Distinct semantic `site_id` values must be at least 2. The two `PILOT_CONTRACT` group `artifact_sha256` values must differ. `outcome_bytes_read=true` is `E_PILOT_FREEZE_INCOMPLETE`.

### Schema `p3-pilot-attempt-v1`

Path pattern: `data/p3_v3/pilot/boost_math/attempts/<job_id>/1/intent.json` and `result.json`.

### Schema `p3-pilot-receipt-v1`

Additional keys: `receipt_id`, `gate_id` equal to `G4_EVIDENCE_PACKAGE`, `freeze_sha256`, `score_task_sha256`, `ledger_sha256`, `planned_count`, `started_count`, `terminal_count`, `not_started_count`, `claims_status` equal to `blocked`, `rq4_supported` equal to `false`, `formal_denominator_membership` equal to `false`.

Required error codes:

- `E_PILOT_SOURCE_IDENTITY`
- `E_PILOT_PACKAGE_CLASS`
- `E_PILOT_FREEZE_INCOMPLETE`
- `E_PILOT_DENOMINATOR_LEAK`
- `E_PILOT_RETRY_FORBIDDEN`
- `E_PILOT_OUTPUT_DRIFT`
- `E_PILOT_EXTRACT_UNSAFE`
- `E_PILOT_CHRONOLOGY`
- `E_PILOT_SELECTION`
- `E_PILOT_ORACLE`

## Gates and User Authorizations

Frozen order:

```text
G0_PLAN
  -> Sol High plan review
  -> G1_IMPLEMENTATION
  -> Sol High implementation review
  -> user explicit authorization for pilot preparation
  -> G2_SOURCE_AND_FREEZE
  -> Sol High freeze review
  -> user explicit authorization for mutant execution
  -> G3_EXECUTION
  -> G4_EVIDENCE_PACKAGE
  -> Sol High evidence review
```

A later executor must refuse to start a gate unless the previous gate artifact exists, its `terminal_status` is `PASS`, and its SHA-256 matches the recorded predecessor. Plan PASS does not authorize source build. Implementation PASS does not authorize source build or mutant execution.

User authorization A, required before Task 2 and Task 3: regular file `data/p3_v3/pilot/boost_math/user-auth-preparation.txt` whose exact bytes are `AUTHORIZE_BOOSTMATH_PILOT_PREPARATION\n`.

User authorization B, required before Task 4: regular file `data/p3_v3/pilot/boost_math/user-auth-execution.txt` whose exact bytes are `AUTHORIZE_BOOSTMATH_PILOT_EXECUTION\n`.

This planning node does not create those authorization files.

Every Task below must finish with RED, minimum GREEN, task-specific regression, the full suite `env PYTHONPATH=src python3 -m pytest tests/p3_v3 -q` expected exit 0, an exact staged-file list, and an independent review stop that does not automatically enter the next gate.

## Outcome-Blind Chronology

Construction chain, each stage writes one exclusive JSON file and records the predecessor SHA-256 list:

```text
PILOT_COMMON_FROZEN
-> SITE_FROZEN
-> CONTRACT_FROZEN
-> PILOT_CONTRACT_FROZEN
-> SEMANTIC_PATCH_FROZEN
-> SYNTACTIC_BASELINE_FROZEN
-> CERTIFICATION_POLICY_FROZEN
```

Sibling MR chain that must not read construction contracts, sites, patches, `PILOT_COMMON`, `PILOT_CONTRACT`, certification results, or outcomes:

```text
PUBLIC_SOURCE_AND_SPEC
-> MR_INVENTORY_FROZEN
```

`pilot-freeze.json` may be assembled only after both terminal files exist.

| Stage | Allowed inputs | Forbidden inputs | Output path | Schema / status | Predecessor hashes | Failure |
|---|---|---|---|---|---|---|
| `PILOT_COMMON_FROZEN` | source-manifest, public schemas from the mounted tree, generator registry, authorization A | contracts, sites, patches, MR definitions, outcomes | `data/p3_v3/pilot/boost_math/chain/pilot-common.json` | `p3-pilot-common-v1` | source-manifest, pilot-plan | `E_PILOT_FREEZE_INCOMPLETE` if length is not 30 or the two later contracts cannot share one executable schema |
| `SITE_FROZEN` | source-manifest, mounted headers and implementation files, `PILOT_COMMON` SHA-256 only | contract bodies, patches, MR definitions, outcomes | `data/p3_v3/pilot/boost_math/chain/sites.json` | `p3-pilot-sites-v1` | pilot-common | `E_PILOT_FREEZE_INCOMPLETE` if fewer than 2 distinct sites |
| `CONTRACT_FROZEN` | source-manifest, public docs, public declarations, site identities without patch bytes, `PILOT_COMMON` SHA-256 | patches, MR definitions, outcomes, `PILOT_CONTRACT` bodies | `data/p3_v3/pilot/boost_math/chain/contracts.json` | `p3-pilot-contracts-v1` | sites, pilot-common | `E_PILOT_FREEZE_INCOMPLETE` if fewer than 2 contracts or shared schema fails |
| `PILOT_CONTRACT_FROZEN` | frozen contracts, public input domain, generator registry | patches, MR definitions, outcomes, certification witnesses | `data/p3_v3/pilot/boost_math/chain/pilot-contract.json` | `p3-pilot-contract-inputs-v1` | contracts | `E_PILOT_FREEZE_INCOMPLETE` if not 5+5 or identities collide |
| `SEMANTIC_PATCH_FROZEN` | frozen contracts, frozen sites, operator catalogue, source snapshot | MR definitions, `PILOT_CONTRACT` payloads, outcomes, certification witnesses | `data/p3_v3/pilot/boost_math/chain/semantic-patches.json` | `p3-pilot-semantic-patches-v1` | contracts, sites | `E_PILOT_FREEZE_INCOMPLETE` if not 4 mutants or fewer than 2 sites |
| `SYNTACTIC_BASELINE_FROZEN` | frozen semantic mutants, syntactic operator catalogue, source snapshot | MR definitions, outcomes, certification results | `data/p3_v3/pilot/boost_math/chain/syntactic-baselines.json` | `p3-pilot-syntactic-baselines-v1` | semantic-patches | `E_PILOT_FREEZE_INCOMPLETE` if pairing is not 1:1 |
| `CERTIFICATION_POLICY_FROZEN` | frozen contracts and patches, witness-selection policy only | MR definitions, `PILOT_COMMON` payloads, `PILOT_CONTRACT` payloads, outcomes | `data/p3_v3/pilot/boost_math/chain/certification-policy.json` | `p3-pilot-certification-policy-v1` | semantic-patches, syntactic-baselines, contracts | `E_PILOT_CHRONOLOGY` if a witness identity equals any evaluation input |
| `MR_INVENTORY_FROZEN` | source-manifest, public docs, public headers | construction contracts, site selection, semantic patches, syntactic patches, `PILOT_COMMON`, `PILOT_CONTRACT`, certification results, outcomes | `data/p3_v3/pilot/boost_math/chain/mr-inventory.json` | `p3-pilot-mr-inventory-v1` | source-manifest, pilot-plan | `E_PILOT_FREEZE_INCOMPLETE` if fewer than 2 independent evaluation MRs |

Contract, site, patch, and input builders must not read candidate MR definitions, evaluated MR definitions, MR semantic signatures, or MR outcomes. The MR builder must not read construction contracts, site selection, semantic patches, syntactic patches, `PILOT_COMMON`, `PILOT_CONTRACT`, certification results, or outcomes. A read of a forbidden path is `E_PILOT_CHRONOLOGY`.

## Deterministic Selection

No builder may accept a caller-chosen already-picked list as authority. Each builder enumerates the qualified set, sorts by the total order below, and keeps only the first N items.

- relation order: `(semantic_contract_family, public_doc_path, public_doc_span, declaration_path, declaration_span, relation_sha256)`
- site order: `(relative_path, source_span_start, source_span_end, site_sha256)`
- semantic operator order: `(semantic_contract_family, construction_mechanism, operator_id)`
- syntactic operator order: `(operator_id, relative_path, source_span_start, patch_sha256)`
- input order: `(generator_id, seed_sha256, ordinal, input_sha256)`
- MR order: `(semantic_signature, evaluation_mr_id)`

`relation_sha256` is `canonical_sha256` of the relation identity fields excluding `artifact_sha256`. `site_sha256` is `canonical_sha256` of path and span. `semantic_signature` is `canonical_sha256` of `source_input_transform`, `follow_up_input_transform`, metamorphic predicate, tolerance class, and oracle direction.

If two construction contracts cannot share one executable input schema, raise `E_PILOT_FREEZE_INCOMPLETE`. Do not manufacture a shared input.

## Scientific Object Schemas

Each construction contract object:

```text
construction_contract_id: str
semantic_contract_family: str
public_doc_path: str
public_doc_sha256: str
public_doc_span: str
declaration_path: str
declaration_sha256: str
declaration_span: str
input_domain: dict
executable_predicate: dict
executable_oracle: dict
tolerance_class: str
tolerance_value: str
activation_obligation: str
expected_violation_direction: str
artifact_sha256: str
```

Each semantic mutant object:

```text
semantic_mutant_id: str
construction_contract_id: str
site_id: str
source_path: str
source_span_start: int
source_span_end: int
original_span_sha256: str
construction_mechanism: str
operator_id: str
patch_sha256: str
original_tree_sha256: str
mutant_tree_sha256: str
expected_semantic_effect: str
artifact_sha256: str
```

Each syntactic baseline object:

```text
syntactic_mutant_id: str
paired_semantic_mutant_id: str
shared_site_id: str
operator_id: str
patch_sha256: str
mutant_tree_sha256: str
artifact_sha256: str
```

Each independent evaluation MR object, exactly 2, outside the 2/4/4/30/5 shorthand:

```text
evaluation_mr_id: str
source_input_transform: dict
follow_up_input_transform: dict
metamorphic_predicate: dict
executable_oracle: dict
tolerance_class: str
tolerance_value: str
seed_policy: dict
timeout_seconds: int
semantic_signature: str
public_provenance_path: str
public_provenance_sha256: str
artifact_sha256: str
```

## Construction, Patch, and Certification Interfaces

```python
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from p3_v3.artifacts import EvidenceError, canonical_sha256, file_sha256, validate_exact_object, validate_sha256
from p3_v3.bridge_and_frames import SourceSnapshot, canonical_source_tree_sha256


def build_semantic_mutants(
    contracts: Sequence[Mapping[str, Any]],
    sites: Sequence[Mapping[str, Any]],
    operator_catalogue: Mapping[str, Any],
    source_snapshot: SourceSnapshot,
) -> list[dict[str, Any]]:
    if len(contracts) != 2:
        raise EvidenceError("E_PILOT_FREEZE_INCOMPLETE", "need exactly 2 contracts")
    ordered_sites = sorted(
        sites,
        key=lambda item: (
            item["relative_path"],
            item["source_span_start"],
            item["source_span_end"],
            item["site_sha256"],
        ),
    )
    operators = sorted(
        operator_catalogue["semantic_operators"],
        key=lambda item: (
            item["semantic_contract_family"],
            item["construction_mechanism"],
            item["operator_id"],
        ),
    )
    original_tree = canonical_source_tree_sha256(source_snapshot)
    produced: list[dict[str, Any]] = []
    for contract in contracts:
        family_ops = [
            item
            for item in operators
            if item["semantic_contract_family"] == contract["semantic_contract_family"]
        ]
        if not family_ops:
            raise EvidenceError("E_PILOT_SELECTION", "no operator for contract family")
        for site in ordered_sites:
            for operator in family_ops:
                original_span = source_snapshot.read_bytes(site["relative_path"])[
                    site["source_span_start"] : site["source_span_end"]
                ]
                patch = {
                    "path": site["relative_path"],
                    "start": site["source_span_start"],
                    "end": site["source_span_end"],
                    "replacement": operator["replacement_template"],
                }
                applied = apply_frozen_patch(
                    source_snapshot,
                    patch,
                    canonical_sha256(original_span),
                )
                body = {
                    "semantic_mutant_id": canonical_sha256(
                        {
                            "construction_contract_id": contract["construction_contract_id"],
                            "site_id": site["site_id"],
                            "operator_id": operator["operator_id"],
                        }
                    ),
                    "construction_contract_id": contract["construction_contract_id"],
                    "site_id": site["site_id"],
                    "source_path": site["relative_path"],
                    "source_span_start": site["source_span_start"],
                    "source_span_end": site["source_span_end"],
                    "original_span_sha256": canonical_sha256(original_span),
                    "construction_mechanism": operator["construction_mechanism"],
                    "operator_id": operator["operator_id"],
                    "patch_sha256": applied["patch_sha256"],
                    "original_tree_sha256": original_tree,
                    "mutant_tree_sha256": applied["mutant_tree_sha256"],
                    "expected_semantic_effect": contract["expected_violation_direction"],
                }
                produced.append({**body, "artifact_sha256": canonical_sha256(body)})
    produced.sort(
        key=lambda item: (
            item["construction_contract_id"],
            item["source_path"],
            item["source_span_start"],
            item["artifact_sha256"],
        )
    )
    selected = produced[:4]
    if len(selected) != 4 or len({item["site_id"] for item in selected}) < 2:
        raise EvidenceError("E_PILOT_FREEZE_INCOMPLETE", "need 4 semantic mutants on 2 sites")
    return selected


def build_syntactic_baselines(
    semantic_mutants: Sequence[Mapping[str, Any]],
    syntactic_operator_catalogue: Mapping[str, Any],
    source_snapshot: SourceSnapshot,
) -> list[dict[str, Any]]:
    if len(semantic_mutants) != 4:
        raise EvidenceError("E_PILOT_FREEZE_INCOMPLETE", "need 4 semantic mutants first")
    operators = sorted(
        syntactic_operator_catalogue["syntactic_operators"],
        key=lambda item: (
            item["operator_id"],
            item["relative_path"],
            item["source_span_start"],
            item["patch_sha256"],
        ),
    )
    produced: list[dict[str, Any]] = []
    for mutant in semantic_mutants:
        matches = [
            item
            for item in operators
            if item["relative_path"] == mutant["source_path"]
            and item["source_span_start"] == mutant["source_span_start"]
        ]
        if not matches:
            raise EvidenceError("E_PILOT_SELECTION", "no syntactic operator on shared site")
        operator = matches[0]
        applied = apply_frozen_patch(
            source_snapshot,
            operator["patch"],
            mutant["original_span_sha256"],
        )
        body = {
            "syntactic_mutant_id": canonical_sha256(
                {
                    "paired_semantic_mutant_id": mutant["semantic_mutant_id"],
                    "operator_id": operator["operator_id"],
                    "patch_sha256": applied["patch_sha256"],
                }
            ),
            "paired_semantic_mutant_id": mutant["semantic_mutant_id"],
            "shared_site_id": mutant["site_id"],
            "operator_id": operator["operator_id"],
            "patch_sha256": applied["patch_sha256"],
            "mutant_tree_sha256": applied["mutant_tree_sha256"],
        }
        produced.append({**body, "artifact_sha256": canonical_sha256(body)})
    if len(produced) != 4:
        raise EvidenceError("E_PILOT_FREEZE_INCOMPLETE", "need 4 paired syntactic baselines")
    return produced


def apply_frozen_patch(
    original_tree: SourceSnapshot,
    patch: Mapping[str, Any],
    expected_original_span_sha256: str,
) -> dict[str, Any]:
    path = patch["path"]
    start = patch["start"]
    end = patch["end"]
    raw = original_tree.read_bytes(path)
    span = raw[start:end]
    if canonical_sha256(span) != expected_original_span_sha256:
        raise EvidenceError("E_PILOT_SOURCE_IDENTITY", "original span differs")
    replacement = patch["replacement"]
    if type(replacement) is not bytes:
        raise EvidenceError("E_PILOT_SELECTION", "patch replacement must be bytes")
    mutated = raw[:start] + replacement + raw[end:]
    entries = []
    for entry in original_tree.entries:
        content = mutated if entry.relative_path == path else entry.content
        entries.append(
            {
                "path": entry.relative_path,
                "byte_sha256": canonical_sha256(content)
                if entry.relative_path == path
                else entry.sha256,
            }
        )
    entries.sort(key=lambda item: item["path"])
    return {
        "patch_sha256": canonical_sha256(dict(patch) | {"replacement_sha256": canonical_sha256(replacement)}),
        "mutant_tree_sha256": canonical_sha256(
            {"domain": "P3-NORMALIZED-SOURCE-TREE-v1", "files": entries}
        ),
        "replacement_sha256": canonical_sha256(replacement),
    }


def certify_mutant(
    original_tree: SourceSnapshot,
    mutant_tree: SourceSnapshot,
    contract: Mapping[str, Any],
    witness_policy: Mapping[str, Any],
) -> dict[str, Any]:
    required = (
        "patch_scope",
        "build_terminal",
        "public_interface_preservation",
        "activation",
        "original_contract_result",
        "mutant_contract_result",
        "stability",
        "certification_witness_sha256",
        "uniqueness",
    )
    record = {key: witness_policy[key] for key in required}
    witness = record["certification_witness_sha256"]
    validate_sha256(witness, "certification_witness_sha256")
    forbidden = set(witness_policy["evaluation_input_sha256"])
    if witness in forbidden:
        raise EvidenceError("E_PILOT_CHRONOLOGY", "witness overlaps evaluation inputs")
    original_ok = record["original_contract_result"] == "SATISFIED"
    mutant_violates = record["mutant_contract_result"] == "VIOLATED"
    if record["build_terminal"] != "PASS":
        state = "INFRASTRUCTURE_UNRESOLVED"
    elif record["public_interface_preservation"] != "PRESERVED":
        state = "INVALID_MUTANT"
    elif record["uniqueness"] != "UNIQUE":
        state = "DUPLICATE_MUTANT"
    elif record["activation"] != "ACTIVATED":
        state = "TRIGGER_UNEXERCISED"
    elif original_ok and record["mutant_contract_result"] == "SATISFIED":
        state = "CERTIFIED_EQUIVALENT"
    elif original_ok and mutant_violates and record["stability"] == "STABLE":
        state = "CONFIRMED_NON_EQUIVALENT"
    else:
        state = "EQUIVALENCE_UNRESOLVED"
    body = {
        "construction_contract_id": contract["construction_contract_id"],
        "original_tree_sha256": canonical_source_tree_sha256(original_tree),
        "mutant_tree_sha256": canonical_source_tree_sha256(mutant_tree),
        "terminal_state": state,
        **record,
    }
    return {**body, "artifact_sha256": canonical_sha256(body)}


def build_evaluation_jobs(
    freeze: Mapping[str, Any],
    source_manifest: Mapping[str, Any],
) -> list[dict[str, Any]]:
    if freeze["schema_version"] != "p3-pilot-freeze-v1":
        raise EvidenceError("E_PILOT_CHRONOLOGY", "jobs require assembled freeze")
    jobs: list[dict[str, Any]] = []
    mutants = list(freeze["semantic_mutants"]) + list(freeze["syntactic_mutants"])
    for mutant in mutants:
        tree = mutant["mutant_tree_sha256"]
        mutant_id = mutant.get("semantic_mutant_id") or mutant["syntactic_mutant_id"]
        for mr in freeze["evaluation_mrs"]:
            for row in freeze["pilot_common_inputs"]:
                identity = {
                    "source_manifest_sha256": source_manifest["artifact_sha256"],
                    "build_descriptor_sha256": source_manifest["build_descriptor_sha256"],
                    "freeze_sha256": freeze["artifact_sha256"],
                    "original_tree_sha256": mutant["original_tree_sha256"]
                    if "original_tree_sha256" in mutant
                    else source_manifest["normalized_source_tree_sha256"],
                    "mutant_tree_sha256": tree,
                    "harness_source_sha256": freeze["harness_source_sha256"],
                    "input_sha256": row["input_sha256"],
                    "evaluation_mr_sha256": mr["artifact_sha256"],
                    "timeout_seconds": mr["timeout_seconds"],
                    "authorization_b_sha256": freeze["authorization_b_sha256"],
                }
                job = {
                    "job_id": canonical_sha256(identity),
                    "evaluation_mr_id": mr["evaluation_mr_id"],
                    "mutant_id": mutant_id,
                    "input_sha256": row["input_sha256"],
                    **identity,
                }
                jobs.append(job)
    jobs.sort(key=lambda item: item["job_id"])
    planned_count = 8 * 2 * 30
    if len(jobs) != planned_count:
        raise EvidenceError("E_PILOT_FREEZE_INCOMPLETE", "evaluation-cell count differs")
    return jobs
```

Certification records patch scope, build terminal, public interface preservation, activation, original contract result, mutant contract result, stability, certification witness, and uniqueness. Terminal states are exactly `CONFIRMED_NON_EQUIVALENT`, `CERTIFIED_EQUIVALENT`, `EQUIVALENCE_UNRESOLVED`, `TRIGGER_UNEXERCISED`, `INVALID_MUTANT`, `DUPLICATE_MUTANT`, and `INFRASTRUCTURE_UNRESOLVED`.

`certification_witness_sha256` must not equal any `PILOT_COMMON`, `PILOT_CONTRACT`, or MR evaluation input SHA-256. Only `CONFIRMED_NON_EQUIVALENT` may enter a strict kill-rate description. Every other object remains in the complete funnel and must not be replaced.

States `PATCH_FROZEN` and `CERTIFICATION_WITNESS_SELECTED` are recorded as `gate_id` values on the semantic-patch and certification-policy artifacts.

## Execution and Kill Oracle

`run_pilot_command` must refuse any argv that is not the exact argv reconstructed from `build_evaluation_jobs` or from the named build jobs `job-cmake-configure`, `job-baseline-build`, `job-baseline-smoke`, and `job-mutant-build-<id>`. An unknown argv is `E_PILOT_ORACLE`.

Each mutant executes in an isolated materialization and build root whose directory name is the `mutant_tree_sha256`. The original tree uses a separate root named by `normalized_source_tree_sha256`.

Each evaluation cell must persist:

```text
original_source_output_sha256
original_follow_up_output_sha256
mutant_source_output_sha256
mutant_follow_up_output_sha256
original_oracle_value
mutant_oracle_value
tolerance_class
tolerance_value
original_relation_verdict
mutant_relation_verdict
kill_verdict
stdout_sha256
stderr_sha256
wall_seconds
cpu_seconds
peak_rss_bytes
terminal_status
```

Kill rule:

- `kill` only when original relation satisfies the `executable_oracle` within tolerance and mutant relation violates beyond tolerance
- `non_kill` when both original and mutant satisfy
- `inconclusive` when original does not satisfy, any execution fails, or either oracle is not computable
- compile failure, timeout, and infrastructure failure are never `kill`

The ledger must emit a semantic kill vector and a syntactic kill vector, each indexed by `mutant_id`, `evaluation_mr_id`, and `input_sha256`.

## Monitoring and Global Timeout

The future runner must:

- write a process-alive heartbeat at least every 30 seconds to `data/p3_v3/pilot/boost_math/heartbeat.json`
- atomically replace `data/p3_v3/pilot/boost_math/checkpoint.json` after every terminal job
- never retry
- refuse to start a `run_id` whose attempt directory already exists
- stop starting new jobs when wall time reaches 14400 seconds
- record every not-yet-started frozen job as `terminal_status=INCONCLUSIVE` and `failure_reason=GLOBAL_TIMEOUT_NOT_STARTED`
- retain every frozen row, started or not
- refuse a receipt that marks a not-started row as `PASS`

Frozen evaluation-cell count:

```text
planned_count = (4 semantic + 4 syntactic) * 2 evaluation_mr_id * 30 PILOT_COMMON
planned_count = 8 * 2 * 30
planned_count = 480
started_count + not_started_count = planned_count
terminal_count = started_count
```

Closure must assert `planned_count == started_count + not_started_count` and `terminal_count == started_count`. A mismatch is `E_PILOT_OUTPUT_DRIFT`.

### Task 1: Independent PILOT_ONLY Schemas and Leakage Guards

User authorization required: no. Gate: `G1_IMPLEMENTATION` after Sol High plan PASS only.

Create: `src/p3_v3/pilot.py`, `scripts/p3_v3/pilot.py`, `tests/p3_v3/test_pilot.py`, `tests/p3_v3/test_pilot_leakage.py`, `tests/p3_v3/test_pilot_extract.py`, `tests/p3_v3/fixtures/pilot/valid_plan_min.json`, `tests/p3_v3/fixtures/pilot/valid_source_manifest_min.json`, `tests/p3_v3/fixtures/pilot/confirmatory_denied_plan.json`, `data/p3_v3/pilot/boost_math/pilot-plan.json`.

Modify: `src/p3_v3/packages.py`, `src/p3_v3/run_records.py`, `scripts/p3_v3/evidence.py`, `tests/p3_v3/test_packages.py`, `tests/p3_v3/test_run_records.py`, `tests/p3_v3/test_cli.py`.

Consumes: authority hashes; `validate_exact_object`; archived Sol High plan verdict.

Produces: validators, confirmatory rejection, and `p3-pilot-plan-v1` at `data/p3_v3/pilot/boost_math/pilot-plan.json` generated from this Markdown plan hash and the archived Sol High plan verdict hash. Produces no source-manifest.

`validate_pilot_plan` and `validate_pilot_source_manifest` are distinct exact-object validators. A source-manifest must fail plan validation.

Required future tests:

- `test_unknown_pilot_schema_is_rejected_by_confirmatory_path`
- `test_source_manifest_cannot_validate_as_pilot_plan`
- `test_source_manifest_requires_exact_identity_fields`

In `src/p3_v3/packages.py`, `build_package` and `_validate_manifest` must call `reject_confirmatory_pilot`. A `class` value `PILOT_ONLY` is `E_PILOT_PACKAGE_CLASS`.

In `src/p3_v3/run_records.py`, `_validate_locked_jobs` must treat `execution_class=PILOT_ONLY` as `E_PILOT_DENOMINATOR_LEAK`. `validate_claim_ledger` must reject any evidence reference whose path starts with `data/p3_v3/pilot/` or whose bytes start with a `p3-pilot-` schema.

Staged files at Task 1 close: exactly the Create and Modify paths listed in this Task.

RED, expected exit 1:

```text
env PYTHONPATH=src python3 -m pytest tests/p3_v3/test_pilot.py tests/p3_v3/test_pilot_leakage.py -q
```

Minimum GREEN, expected exit 0:

```text
env PYTHONPATH=src python3 -m pytest tests/p3_v3/test_pilot.py tests/p3_v3/test_pilot_leakage.py -q
```

Task-specific regression, expected exit 0:

```text
env PYTHONPATH=src python3 -m pytest tests/p3_v3/test_artifacts.py tests/p3_v3/test_packages.py tests/p3_v3/test_run_records.py tests/p3_v3/test_cli.py -q
```

Final complete suite, expected exit 0:

```text
env PYTHONPATH=src python3 -m pytest tests/p3_v3 -q
```

Independent stop: Sol High implementation review. Do not mount source. Do not enter Task 2.

### Task 2: Source Identity and Materialization Validation

User authorization required: yes, authorization A. Gate: `G2_SOURCE_AND_FREEZE` first half.

Create: `data/p3_v3/pilot/boost_math/source-manifest.json` only after authorization A and a user-mounted archive.

Modify: `src/p3_v3/pilot.py`, `scripts/p3_v3/pilot.py`, `tests/p3_v3/test_pilot.py`, `tests/p3_v3/test_pilot_extract.py`.

Consumes: `--archive`, authorization A, frozen identities.

Produces: `p3-pilot-source-manifest-v1` at `source-manifest.json`.

Extractor `extract_public_archive(archive_bytes: bytes, target_root: str, expected_archive_sha256: str) -> None` must reject and raise `E_PILOT_EXTRACT_UNSAFE` for:

- absolute member path
- `..` traversal
- symlink member
- hardlink member
- device node
- FIFO
- socket
- duplicate normalized path
- case-fold path collision
- extraction target escape outside `target_root`
- archive bytes that change after the opening SHA-256 check

PASS requires the conjunction of archive SHA-256, archive bytes, normalized tree SHA-256 `93a62859d7fdd6b2068e494bbe6e3e27180b874cbd27055ac27f941e507a90d8`, build descriptor SHA-256 `68d2e0fd34b845bb0df22b29003f26259d5655d2ec80c18895ff36904db2d95d`, neutral snapshot `74cdc825c3c728c25f5ea857af1565350515a4e631fb0a874c26e810ec437886`, controlled subject identity `89b0e6791c611b465b9216e833e0c526a53ffd6946b5cd20de045e3641f43914`, and authorization A SHA-256. File count, directory names, and declaration counts are not sufficient.

Fixture tests may inject a digest. The production `G2_SOURCE_AND_FREEZE` seam `validate_boostmath_source_identity` must hard-code the production identities above and persist the real receipt. A monkeypatched expected digest is not production-binding evidence.

CLI:

```text
env PYTHONPATH=src python3 scripts/p3_v3/pilot.py validate-source \
  --archive /absolute/user-mounted/boost-math.archive \
  --authorization data/p3_v3/pilot/boost_math/user-auth-preparation.txt \
  --output data/p3_v3/pilot/boost_math/source-manifest.json
```

Staged files: `src/p3_v3/pilot.py`, `scripts/p3_v3/pilot.py`, `tests/p3_v3/test_pilot.py`, `tests/p3_v3/test_pilot_extract.py`, and the source-manifest if produced.

RED, expected exit 1:

```text
env PYTHONPATH=src python3 -m pytest tests/p3_v3/test_pilot_extract.py -q
```

Minimum GREEN, expected exit 0:

```text
env PYTHONPATH=src python3 -m pytest tests/p3_v3/test_pilot_extract.py tests/p3_v3/test_pilot.py::test_source_identity_rejects_wrong_tree tests/p3_v3/test_pilot.py::test_source_manifest_cannot_validate_as_pilot_plan tests/p3_v3/test_pilot.py::test_source_manifest_requires_exact_identity_fields -q
```

Task-specific regression, expected exit 0:

```text
env PYTHONPATH=src python3 -m pytest tests/p3_v3/test_pilot.py tests/p3_v3/test_pilot_leakage.py tests/p3_v3/test_pilot_extract.py tests/p3_v3/test_bridge_and_frames.py -q
```

Final complete suite, expected exit 0:

```text
env PYTHONPATH=src python3 -m pytest tests/p3_v3 -q
```

Independent stop: source-manifest exists. Do not configure CMake. Do not enter Task 3 automatically.

### Task 3: Outcome-Blind Contract, Site, MR, and Input Freeze

User authorization required: yes, authorization A. Gate: `G2_SOURCE_AND_FREEZE` second half. Outcome bytes read: forbidden.

Create: the seven construction-chain files, `mr-inventory.json`, and either `pilot-freeze.json` or `pilot-insufficiency.json`.

Modify: `src/p3_v3/pilot.py`, `scripts/p3_v3/pilot.py`, `tests/p3_v3/test_pilot.py`.

Consumes: source-manifest; mounted public headers and public documentation; operator catalogue bytes; generator registry. Does not consume Phase 1 site counts as acceptance.

Produces: hash-chained freeze artifacts and the assembled `p3-pilot-freeze-v1`.

CLI:

```text
env PYTHONPATH=src python3 scripts/p3_v3/pilot.py freeze-common --source-manifest data/p3_v3/pilot/boost_math/source-manifest.json --output data/p3_v3/pilot/boost_math/chain/pilot-common.json
env PYTHONPATH=src python3 scripts/p3_v3/pilot.py freeze-sites --pilot-common data/p3_v3/pilot/boost_math/chain/pilot-common.json --output data/p3_v3/pilot/boost_math/chain/sites.json
env PYTHONPATH=src python3 scripts/p3_v3/pilot.py freeze-contracts --sites data/p3_v3/pilot/boost_math/chain/sites.json --output data/p3_v3/pilot/boost_math/chain/contracts.json
env PYTHONPATH=src python3 scripts/p3_v3/pilot.py freeze-pilot-contract --contracts data/p3_v3/pilot/boost_math/chain/contracts.json --output data/p3_v3/pilot/boost_math/chain/pilot-contract.json
env PYTHONPATH=src python3 scripts/p3_v3/pilot.py freeze-semantic-patches --contracts data/p3_v3/pilot/boost_math/chain/contracts.json --sites data/p3_v3/pilot/boost_math/chain/sites.json --output data/p3_v3/pilot/boost_math/chain/semantic-patches.json
env PYTHONPATH=src python3 scripts/p3_v3/pilot.py freeze-syntactic-baselines --semantic-patches data/p3_v3/pilot/boost_math/chain/semantic-patches.json --output data/p3_v3/pilot/boost_math/chain/syntactic-baselines.json
env PYTHONPATH=src python3 scripts/p3_v3/pilot.py freeze-certification-policy --semantic-patches data/p3_v3/pilot/boost_math/chain/semantic-patches.json --output data/p3_v3/pilot/boost_math/chain/certification-policy.json
env PYTHONPATH=src python3 scripts/p3_v3/pilot.py freeze-mr-inventory --source-manifest data/p3_v3/pilot/boost_math/source-manifest.json --output data/p3_v3/pilot/boost_math/chain/mr-inventory.json
env PYTHONPATH=src python3 scripts/p3_v3/pilot.py assemble-freeze --chain-root data/p3_v3/pilot/boost_math/chain --output data/p3_v3/pilot/boost_math/pilot-freeze.json
```

Expected exit 0 on a complete freeze. Expected exit 2 and `E_PILOT_FREEZE_INCOMPLETE` when 2/4/4/30/5 or the two `evaluation_mr_id` values fail. Expected exit 1 on `E_PILOT_CHRONOLOGY` if a builder opens a forbidden path.

Staged files: the Task 3 Create and Modify paths only.

RED, expected exit 1:

```text
env PYTHONPATH=src python3 -m pytest tests/p3_v3/test_pilot.py::test_freeze_rejects_count_three_relations tests/p3_v3/test_pilot.py::test_mr_builder_rejects_contract_bytes -q
```

Minimum GREEN, expected exit 0:

```text
env PYTHONPATH=src python3 -m pytest tests/p3_v3/test_pilot.py::test_freeze_rejects_count_three_relations tests/p3_v3/test_pilot.py::test_freeze_accepts_exact_244305_fixture tests/p3_v3/test_pilot.py::test_freeze_rejects_reused_contract_identity tests/p3_v3/test_pilot.py::test_mr_builder_rejects_contract_bytes tests/p3_v3/test_pilot.py::test_contract_builder_rejects_mr_bytes tests/p3_v3/test_pilot.py::test_selection_keeps_first_n_total_order -q
```

Task-specific regression, expected exit 0:

```text
env PYTHONPATH=src python3 -m pytest tests/p3_v3/test_pilot.py tests/p3_v3/test_pilot_leakage.py -q
```

Final complete suite, expected exit 0:

```text
env PYTHONPATH=src python3 -m pytest tests/p3_v3 -q
```

Independent stop: Sol High freeze review. Do not compile mutants. Do not enter Task 4 automatically.

### Task 4: Authorized Boost.Math Pilot Execution

User authorization required: yes, authorization B. Gate: `G3_EXECUTION` after Sol High freeze PASS.

Create: `data/p3_v3/pilot/boost_math/attempts/<job_id>/1/intent.json` and `result.json`, `heartbeat.json`, `checkpoint.json`.

Modify: `src/p3_v3/pilot.py`, `scripts/p3_v3/pilot.py`, `tests/p3_v3/test_pilot.py`.

Consumes: `pilot-freeze.json`, authorization B, validated source-manifest, exact build descriptor.

Produces: one `p3-pilot-attempt-v1` per reconstructed job, including evaluation cells with original and mutant oracle fields.

```python
def run_pilot_command(intent: Mapping[str, Any], freeze: Mapping[str, Any]) -> dict[str, Any]:
    expected = {job["job_id"]: job for job in build_evaluation_jobs(freeze, freeze["source_manifest"])}
    build_ids = {
        "job-cmake-configure",
        "job-baseline-build",
        "job-baseline-smoke",
    }
    if intent["job_id"] not in expected and intent["job_id"] not in build_ids and not intent["job_id"].startswith("job-mutant-build-"):
        raise EvidenceError("E_PILOT_ORACLE", "argv is not a reconstructed job")
    if intent["argv"] != freeze["job_argv"][intent["job_id"]]:
        raise EvidenceError("E_PILOT_ORACLE", "argv differs from freeze")
    return _execute_isolated(intent, freeze)
```

`_execute_isolated` must materialize the bound tree into a root named by that tree SHA-256, launch `argv` with `shell=False`, enforce `timeout_seconds`, hash stdout and stderr, record `wall_seconds`, `cpu_seconds`, and `peak_rss_bytes`, write a heartbeat at least every 30 seconds, and refuse a second call with the same `run_id`.

CUDA missing is ignored. CMake extra flags must not add `-DCMAKE_CUDA_COMPILER` as a required cache entry.

CLI:

```text
env PYTHONPATH=src python3 scripts/p3_v3/pilot.py execute \
  --freeze data/p3_v3/pilot/boost_math/pilot-freeze.json \
  --authorization data/p3_v3/pilot/boost_math/user-auth-execution.txt \
  --attempt-root data/p3_v3/pilot/boost_math/attempts
```

Staged files: Task 4 Create and Modify paths only.

RED, expected exit 1:

```text
env PYTHONPATH=src python3 -m pytest tests/p3_v3/test_pilot.py::test_execute_rejects_missing_authorization_b tests/p3_v3/test_pilot.py::test_execute_rejects_unknown_argv -q
```

Minimum GREEN, expected exit 0:

```text
env PYTHONPATH=src python3 -m pytest tests/p3_v3/test_pilot.py::test_execute_rejects_missing_authorization_b tests/p3_v3/test_pilot.py::test_execute_rejects_unknown_argv tests/p3_v3/test_pilot.py::test_execute_records_timeout_without_retry tests/p3_v3/test_pilot.py::test_execute_rejects_second_run_id tests/p3_v3/test_pilot.py::test_kill_requires_original_satisfy_and_mutant_violate tests/p3_v3/test_pilot.py::test_global_timeout_marks_not_started -q
```

Those tests must use a fake command such as `python3 -c "import time; time.sleep(5)"` with `timeout_seconds=1`. They must not invoke CMake on Boost.Math in the unit suite.

Task-specific regression, expected exit 0:

```text
env PYTHONPATH=src python3 -m pytest tests/p3_v3/test_pilot.py tests/p3_v3/test_pilot_leakage.py tests/p3_v3/test_run_records.py -q
```

Final complete suite, expected exit 0:

```text
env PYTHONPATH=src python3 -m pytest tests/p3_v3 -q
```

Independent stop: all frozen jobs terminal or marked `GLOBAL_TIMEOUT_NOT_STARTED`. Do not open the claim ledger. Do not enter Task 5 automatically.

### Task 5: Evidence Closure and Reproducibility Package

User authorization required: no additional authorization. Gate: `G4_EVIDENCE_PACKAGE` after `G3_EXECUTION` terminals exist.

Create:

- `data/p3_v3/pilot/boost_math/score-task.yml`
- `data/p3_v3/pilot/boost_math/experiment-ledger.yml`
- `data/p3_v3/pilot/boost_math/pilot-receipt.json`
- `docs/review_20260815/boost_math_pilot_evidence_package.md`

Modify: `src/p3_v3/pilot.py`, `scripts/p3_v3/pilot.py`, `tests/p3_v3/test_pilot.py`.

`score-task.yml` exact keys:

```text
research_question: "Can a known-identity CPU-only Boost.Math subject complete a 2/4/4/30/5 PILOT_ONLY path with two independent evaluation MRs without entering the formal denominator?"
subject: "C-BOOSTMATH-001"
metrics:
  - mutant_compile_terminal
  - kill
  - non_kill
  - inconclusive
  - untriggered
  - timeout
  - infrastructure_failure
  - non_equivalence_unproven
baseline: "paired syntactic mutant on the same site"
inputs:
  - PILOT_COMMON
  - PILOT_CONTRACT
outputs:
  - pilot-receipt.json
  - experiment-ledger.yml
deterministic_reproducibility_policy: "same archive bytes, same freeze, same reconstructed argv, same timeout, no retry"
stopping_rule: "first terminal result per run_id; full-pilot wall 14400 seconds; GLOBAL_TIMEOUT_NOT_STARTED for unstarted rows"
claims: "blocked"
```

`experiment-ledger.yml` must contain one record per mutant and one cell per `evaluation_mr_id` and input with `kill_verdict` in `{kill,non_kill,inconclusive}`, plus compile failure, timeout, infrastructure failure, `EQUIVALENCE_UNRESOLVED`, untriggered, wall time, CPU time, peak RSS, and every terminal non-PASS attempt. It must not retry a `run_id`.

`boost_math_pilot_evidence_package.md` must contain, in this order:

1. project and pilot RQ summary
2. score-task summary
3. source, freeze, attempt, ledger, and receipt hashes
4. per-mutant evidence table
5. per-MR kill matrix
6. complete failure funnel
7. candidate claim table
8. blocked and insufficient claims
9. preserved limitations
10. next-experiment requirements
11. reproducibility status

Candidate claim table rules:

- RQ1, RQ2, and RQ3 must not modify the formal claim ledger
- status before evidence review is `blocked`
- a later reviewer may at most assign single-case observed
- RQ4 is never unlocked by this pilot
- the table must not use population or cross-project wording

Receipt conservation: `planned_count`, `started_count`, `terminal_count`, and `not_started_count` must satisfy the 480-cell formula. A not-started row cannot be `PASS`.

CLI:

```text
env PYTHONPATH=src python3 scripts/p3_v3/pilot.py close \
  --freeze data/p3_v3/pilot/boost_math/pilot-freeze.json \
  --attempt-root data/p3_v3/pilot/boost_math/attempts \
  --score-task data/p3_v3/pilot/boost_math/score-task.yml \
  --ledger data/p3_v3/pilot/boost_math/experiment-ledger.yml \
  --receipt data/p3_v3/pilot/boost_math/pilot-receipt.json \
  --evidence-package docs/review_20260815/boost_math_pilot_evidence_package.md
```

Staged files: Task 5 Create and Modify paths only.

RED, expected exit 1:

```text
env PYTHONPATH=src python3 -m pytest tests/p3_v3/test_pilot.py::test_receipt_rejects_rq4_supported tests/p3_v3/test_pilot.py::test_receipt_rejects_not_started_pass -q
```

Minimum GREEN, expected exit 0:

```text
env PYTHONPATH=src python3 -m pytest tests/p3_v3/test_pilot.py::test_receipt_rejects_rq4_supported tests/p3_v3/test_pilot.py::test_close_writes_blocked_receipt tests/p3_v3/test_pilot.py::test_close_rejects_claim_ledger_write tests/p3_v3/test_pilot.py::test_receipt_count_conservation -q
```

Task-specific regression, expected exit 0:

```text
env PYTHONPATH=src python3 -m pytest tests/p3_v3/test_pilot.py tests/p3_v3/test_pilot_leakage.py tests/p3_v3/test_packages.py tests/p3_v3/test_run_records.py tests/p3_v3/test_cli.py -q
```

Final complete suite, expected exit 0:

```text
env PYTHONPATH=src python3 -m pytest tests/p3_v3 -q
```

Independent stop: Sol High evidence review. Do not upgrade claims. Do not start a second subject.

## Stop Conditions

Stop and return BLOCK, writing the named error when an artifact exists:

- HEAD or `origin/main` is not the authorized task start commit
- any authority hash differs
- Package C, P12 reveal, patch, reference MR, evaluated MR, or outcome bytes are required
- Boost.Math source would be downloaded or taken from Package C
- `canonical_source_tree_sha256` is not `93a62859d7fdd6b2068e494bbe6e3e27180b874cbd27055ac27f941e507a90d8`
- confirmatory entry points cannot reject unknown `p3-pilot-` schemas
- a task tries to treat the pilot as confirmatory or to support RQ4
- a task writes the claim ledger
- a task replaces a frozen relation, site, mutant, baseline, MR, input, or timeout after seeing a result
- a task retries a `run_id` or treats timeout as non-terminal
- CUDA absence is used as a blocker
- native profiling is used as a precondition
- a third file outside this plan's File Map is required for the scientific path

## Acceptance Criteria

A later authorized execution may close only when all of the following are true:

- The five named schemas validate, and unknown `p3-pilot-` schemas are rejected
- Confirmatory `build-package`, `verify-package`, `verify-run-records`, `close-phase`, `verify-evidence`, `freeze-authority-lock`, and `run-preflight` reject pilot objects with `E_PILOT_DENOMINATOR_LEAK` or `E_PILOT_PACKAGE_CLASS`
- Source identity binds archive SHA-256, archive bytes, normalized tree, build descriptor, snapshot, controlled subject identity, and authorization A
- Freeze cardinality is 2/4/4/30/5 with paired mutants, distinct contract-group identities, and two independent evaluation MRs
- Construction and MR chains are hash-chained and mutually unread
- Selection uses the published total orders and first-N rule
- Two user authorization files were hashed into the relevant artifacts
- Timeouts are the frozen integers; unstarted rows are `GLOBAL_TIMEOUT_NOT_STARTED`
- `planned_count`, `started_count`, `terminal_count`, and `not_started_count` conserve
- `score-task.yml` and `experiment-ledger.yml` exist and the receipt says `claims_status=blocked`
- Claim ledger bytes are unchanged
- CUDA was not required
- Native profiling was not executed as a gate
- No production confirmatory path ran
- `G1_IMPLEMENTATION` closed only after `env PYTHONPATH=src python3 -m pytest tests/p3_v3 -q` exited 0

This repair node accepts only revisions of this file and its review packet.

## Review Handoff

Requested reviewer: GPT-5.6 Sol High, reasoning setting high.

Requested state after an independent PASS: `PILOT_PLAN_FROZEN`. Until that PASS exists, the repository state remains `PILOT_PLAN_REVIEW_CANDIDATE`.

The reviewer must not start Task 1. The reviewer must not mount Boost.Math. The reviewer must not treat this plan as production scientific intent. Claims stay `blocked`.
