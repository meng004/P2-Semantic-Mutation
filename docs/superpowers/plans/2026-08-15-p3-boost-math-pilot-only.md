# Boost.Math PILOT_ONLY Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Every execution-bearing gate requires separate user authorization.

## Goal

Create a machine-isolated Boost.Math single-subject `PILOT_ONLY` path that can later prove minimum end-to-end feasibility after independent reviews and two explicit user authorizations. This plan does not implement that path. This plan does not authorize source mounting, CMake configure, baseline build, mutant construction, mutant evaluation, preflight, profiling, or any confirmatory scientific run.

The unique later subject is the historically associated P12 item `C-BOOSTMATH-001` bound to neutral snapshot `74cdc825c3c728c25f5ea857af1565350515a4e631fb0a874c26e810ec437886`. Because that association already exists, the subject is `PILOT_ONLY` and must never enter a blind confirmatory denominator.

Success for a later authorized execution is a closed `PILOT_ONLY` evidence package whose schemas, `execution_class`, and `denominator` are rejected by every confirmatory entry point. Failure to find two specification-supported relations, four real semantic mutants, or four paired syntactic baselines is a recorded stop, not a reason to shrink, replace, or relabel the frozen objects.

## Architecture

The later implementation adds a sibling namespace beside the existing confirmatory foundation. It reuses durable primitives and the CMake adapter. It does not extend Protocol V4, the claim ledger, Package A, Package B, Package C, or P12 reveal.

Reuse without modification of scientific meaning:

- `p3_v3.artifacts.EvidenceError`, `canonical_json_bytes`, `canonical_sha256`, `file_sha256`, `validate_exact_object`, `validate_sha256`, `write_canonical_json`, `read_canonical_json`, `safe_relative_path`
- `p3_v3.bridge_and_frames.SourceSnapshot`, `SourceSnapshotEntry`, `canonical_source_tree_sha256`
- `p3_v3.adapters.cmake_ctest_v1.discover(source_snapshot, build_descriptor: Mapping[str, Any]) -> dict[str, Any]`
- `p3_v3.packages.ALLOWED_CLASSES` remains the confirmatory class set and must stay free of `PILOT_ONLY`

New isolated module `src/p3_v3/pilot.py` owns every `p3-pilot-*-v1` schema. New CLI `scripts/p3_v3/pilot.py` is the only command surface that may write under `data/p3_v3/pilot/`. Existing `scripts/p3_v3/evidence.py` confirmatory commands must reject any object whose `schema_version` starts with `p3-pilot-` or whose `execution_class` or `denominator` equals `PILOT_ONLY`.

Data flow after later authorization:

1. User-mounted public source archive is hashed and materialized.
2. `canonical_source_tree_sha256` must equal `93a62859d7fdd6b2068e494bbe6e3e27180b874cbd27055ac27f941e507a90d8`.
3. Outcome-blind freeze writes `p3-pilot-freeze-v1` with exactly 2 relations, 4 semantic mutants, 4 paired syntactic mutants, 30 `PILOT_COMMON` inputs, and 5 `PILOT_CONTRACT` inputs per relation.
4. Authorized execution writes one `p3-pilot-attempt-v1` per command and never retries the same run identity.
5. Closure writes `score-task.yml`, `experiment-ledger.yml`, `pilot-receipt.json`, and `docs/review_20260815/boost_math_pilot_evidence_package.md`.

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

- Current repository state is `PHASE1_CLOSED`. This plan may reach only `PILOT_PLAN_REVIEW_CANDIDATE`. `PILOT_PLAN_FROZEN` requires an independent GPT-5.6 Sol High PASS on the fixed commit that adds this file.
- `claims` remain `blocked` for C1 through C8 and RQ1 through RQ4. Later code must not import a writer for `research/evidence/p3_claim_ledger_v1.3.0.yml`.
- Pilot objects use `execution_class=PILOT_ONLY` and `denominator=PILOT_ONLY`. Confirmatory code continues to accept only `SYNTHETIC_INFRASTRUCTURE`, `NON_SCIENTIFIC_CONTROL`, and `REAL_SCIENTIFIC`.
- Native C++ profiling is not a precondition. Phase 1 profiling results for this subject are `ADAPTER_UNCERTAIN` with `failure_code=PHASE1_PROFILING_NOT_EXECUTED` and `primary_technique=TECH_UNCERTAIN`. Later pilot code must not call `scripts/p3_v3/evidence.py run-preflight` or any profiling runner as a gate.
- CUDA is not required. Absence of a CUDA toolchain is not `E_PILOT_SOURCE_IDENTITY`, not `E_PILOT_FREEZE_INCOMPLETE`, and not a stop condition.
- The historical site count 4,028 is not an input, not an acceptance number, and not a freeze field.
- `erf(x) + erfc(x) ≈ 1` and `erf(-x) ≈ -erf(x)` are non-binding candidates only. They must not appear as frozen `relation_id` values in `pilot-freeze.json` unless a later authorized freeze cites mounted public specification evidence.
- After freeze, compile failure, non-trigger, non-kill, timeout, or an undesired matrix cannot replace a relation, site, operator, mutant, baseline, input, or timeout.
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
| `adapter-discovery-*.json` | `87fb9d05278c5c2e713c8a9d7f398cb1a1c84562df27b590e6d37f98fd7c1dd1` |
| `derived-subject-*.json` | `654a5c8a26b85013a44665dd92c59a66afee9f639ec7d28535d58357ec696f20` |
| `evaluation-inputs-common-*.json` | `92d35c3cf98a1287703f8d00dd2343cfa792b2a0e035bce63d9850324f95b239` |
| `profiling-results-*.json` | `5a1de4c1a9e52efcc100a448e018229abc984bc350a805c530133f7e689cc133` |
| `profiling-workload-*.json` | `e6cd3b5054bdac30dea8e6fbc613c29758be6a97ead4d6d134d33dfdfc8c8380` |
| `public-behavior-frame-*.json` | `a740d5019a19ee354f07e73e7c542dd1d79fb8969a2af48d5ef7975e534da4d3` |
| `source-scale-*.json` | `dc9b56fe81bcf8301e6164f15007c6f57ee11e79cfff1b84e66906cb7de228d0` |
| `technique-profile-*.json` | `da09281afcfb30d41f6f52823afbca9a994a543ae1ef8b82198b5aea58a5c91f` |

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

Exact later freeze cardinality:

| Object | Count | Rule |
|---|---|---|
| Semantic relations | 2 | Each must be supported by mounted public specification text |
| Semantic mutants | 4 | At least 2 distinct implementation sites |
| Syntactic baseline mutants | 4 | One-to-one pair with the 4 semantic mutants |
| `PILOT_COMMON` inputs | 30 | Shared across all 8 mutants |
| `PILOT_CONTRACT` inputs | 5 per relation | The two relation groups must have distinct artifact identities |

If those counts cannot be satisfied from mounted public specification and source evidence, the freeze command must write `data/p3_v3/pilot/boost_math/pilot-insufficiency.json` with `status=INSUFFICIENT` and exit 2 using `E_PILOT_FREEZE_INCOMPLETE`. It must not invent substitutes.

## File Map

Later Create files, none of which this node may create:

- `src/p3_v3/pilot.py`
- `scripts/p3_v3/pilot.py`
- `tests/p3_v3/test_pilot.py`
- `tests/p3_v3/test_pilot_leakage.py`
- `tests/p3_v3/fixtures/pilot/valid_plan_min.json`
- `tests/p3_v3/fixtures/pilot/confirmatory_denied_plan.json`
- `data/p3_v3/pilot/boost_math/score-task.yml`
- `data/p3_v3/pilot/boost_math/source-manifest.json`
- `data/p3_v3/pilot/boost_math/pilot-freeze.json`
- `data/p3_v3/pilot/boost_math/experiment-ledger.yml`
- `data/p3_v3/pilot/boost_math/pilot-receipt.json`
- `data/p3_v3/pilot/boost_math/attempts/`
- `docs/review_20260815/boost_math_pilot_evidence_package.md`

Later Modify files:

- `src/p3_v3/packages.py` (reject `PILOT_ONLY` and `p3-pilot-*` at confirmatory package seams)
- `src/p3_v3/run_records.py` (reject `PILOT_ONLY` at `_validate_locked_jobs` and `validate_claim_ledger`)
- `scripts/p3_v3/evidence.py` (reject pilot schemas in `freeze-authority-lock`, `build-package`, `verify-package`, `verify-run-records`, `close-phase`, `verify-evidence`, and `run-preflight`)
- `tests/p3_v3/test_packages.py` (add confirmatory rejection cases)
- `tests/p3_v3/test_run_records.py` (add confirmatory rejection cases)
- `tests/p3_v3/test_cli.py` (add confirmatory CLI rejection cases)

Later Test files:

- `tests/p3_v3/test_pilot.py`
- `tests/p3_v3/test_pilot_leakage.py`
- the three confirmatory test modules listed above

Forbidden later Modify files:

- `research/evidence/p3_claim_ledger_v1.3.0.yml`
- `data/p3_v3/protocol/protocol.json`
- `data/p3_v3/protocol/environment_lock.json`
- `data/p3_v3/protocol/claim_ceiling_authority.json`
- `data/p3_v3/phase1_frames/receipts.json`
- every `data/p3_v3/phase1_frames/out/*-74cdc825c3c728c25f5ea857af1565350515a4e631fb0a874c26e810ec437886.json`

## Pilot Artifact Contracts

Every durable JSON pilot artifact must include these exact keys in addition to schema-specific keys:

```text
schema_version: str
execution_class: "PILOT_ONLY"
denominator: "PILOT_ONLY"
p12_item_id: "C-BOOSTMATH-001"
neutral_snapshot_id: "74cdc825c3c728c25f5ea857af1565350515a4e631fb0a874c26e810ec437886"
normalized_source_tree_sha256: "93a62859d7fdd6b2068e494bbe6e3e27180b874cbd27055ac27f941e507a90d8"
protocol_predecessor_sha256: "240d8270d41802c9d5b86f30564eadd1a86fd9ed09de2c7e947d17c1a4d78519"
environment_sha256: str
input_sha256: list[str]
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
artifact_sha256: str
```

`artifact_sha256` is `canonical_sha256` of the object with that field removed. `input_sha256` must be sorted unique lowercase SHA-256 strings. `cwd_identity` is SHA-256 of the resolved POSIX cwd string. `terminal_status` is one of `PASS`, `FAIL_SCIENTIFIC`, `FAIL_INFRASTRUCTURE`, `INCONCLUSIVE`, `INSUFFICIENT`, `TIMEOUT`.

### Schema `p3-pilot-plan-v1`

Additional keys: `plan_id`, `gate_id` equal to `G0_PLAN`, `subject` object, `cardinality` object, `timeouts` object, `non_binding_relation_candidates` list. `cardinality` is exactly `{"relations":2,"semantic_mutants":4,"syntactic_mutants":4,"pilot_common":30,"pilot_contract_per_relation":5}`. `timeouts` is exactly `{"source_identity_validation":300,"cmake_configure":900,"baseline_build":3600,"baseline_public_behavior_smoke":1800,"mutant_build":900,"mutant_evaluation":600,"full_pilot":14400}`. `non_binding_relation_candidates` may list the two erf identities as strings and must set `binding` to `false`.

### Schema `p3-pilot-freeze-v1`

Additional keys: `freeze_id`, `gate_id` equal to `G2_SOURCE_AND_FREEZE`, `source_manifest_sha256`, `relations`, `semantic_mutants`, `syntactic_mutants`, `pairs`, `pilot_common_inputs`, `pilot_contract_inputs`, `outcome_bytes_read` equal to `false`. `relations` length 2. `semantic_mutants` length 4. `syntactic_mutants` length 4. `pairs` length 4 and each item is `{"semantic_mutant_id":str,"syntactic_mutant_id":str}`. Distinct semantic `site_id` values must be at least 2. `pilot_common_inputs` length 30. `pilot_contract_inputs` is a list of two objects, each with `relation_id` and `inputs` length 5. The two `artifact_sha256` values of those contract groups must differ. Any `outcome_bytes_read=true` is `E_PILOT_FREEZE_INCOMPLETE`.

### Schema `p3-pilot-attempt-v1`

Additional keys: `run_id`, `attempt` equal to `1`, `job_id`, `object_type`, `object_id`, `gate_id`, `wall_seconds`, `cpu_seconds`, `peak_rss_bytes`. `attempt` other than `1` is `E_PILOT_RETRY_FORBIDDEN`. A second write to the same `run_id` directory is `E_PILOT_RETRY_FORBIDDEN`.

### Schema `p3-pilot-receipt-v1`

Additional keys: `receipt_id`, `gate_id` equal to `G4_EVIDENCE_PACKAGE`, `freeze_sha256`, `score_task_sha256`, `ledger_sha256`, `attempt_count`, `claims_status` equal to `blocked`, `rq4_supported` equal to `false`, `formal_denominator_membership` equal to `false`.

Required error codes, each raised as `EvidenceError(code, detail)`:

- `E_PILOT_SOURCE_IDENTITY`: mounted tree, archive, or descriptor does not bind the frozen identities
- `E_PILOT_PACKAGE_CLASS`: a confirmatory package or role received a pilot class or schema
- `E_PILOT_FREEZE_INCOMPLETE`: cardinality, pairing, specification support, or outcome-blindness failed
- `E_PILOT_DENOMINATOR_LEAK`: a confirmatory denominator, claim ledger, P12 job, or authority lock received `PILOT_ONLY` or a `p3-pilot-*` object
- `E_PILOT_RETRY_FORBIDDEN`: retry, replacement after timeout, or reuse of a terminal `run_id`
- `E_PILOT_OUTPUT_DRIFT`: rewritten bytes, non-canonical JSON, or a path outside `data/p3_v3/pilot/`

Confirmatory rejection rule: `scripts/p3_v3/evidence.py` and `p3_v3.packages` / `p3_v3.run_records` must inspect `schema_version`, `execution_class`, and `denominator` before filename checks. A file named `intent.json` that contains `execution_class=PILOT_ONLY` must still be rejected at a confirmatory entry.

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

A later executor must refuse to start a gate unless the previous gate artifact exists, its `terminal_status` is `PASS`, and its SHA-256 matches the recorded predecessor. Plan PASS does not authorize source build. Implementation PASS does not authorize source build or mutant execution. Those two user authorizations are independent and must be quoted verbatim in the later attempt `argv` input hashes.

User authorization A, required before Task 2 and Task 3: a regular file `data/p3_v3/pilot/boost_math/user-auth-preparation.txt` whose exact bytes are `AUTHORIZE_BOOSTMATH_PILOT_PREPARATION\n` and whose SHA-256 is recorded in the source-manifest `input_sha256`.

User authorization B, required before Task 4: a regular file `data/p3_v3/pilot/boost_math/user-auth-execution.txt` whose exact bytes are `AUTHORIZE_BOOSTMATH_PILOT_EXECUTION\n` and whose SHA-256 is recorded in every execution attempt `input_sha256`.

This planning node does not create those authorization files.

### Task 1: Independent PILOT_ONLY Schemas and Leakage Guards

User authorization required: no. Gate: `G1_IMPLEMENTATION` after Sol High plan PASS only.

Create:

- `src/p3_v3/pilot.py`
- `scripts/p3_v3/pilot.py`
- `tests/p3_v3/test_pilot.py`
- `tests/p3_v3/test_pilot_leakage.py`
- `tests/p3_v3/fixtures/pilot/valid_plan_min.json`
- `tests/p3_v3/fixtures/pilot/confirmatory_denied_plan.json`

Modify:

- `src/p3_v3/packages.py`
- `src/p3_v3/run_records.py`
- `scripts/p3_v3/evidence.py`
- `tests/p3_v3/test_packages.py`
- `tests/p3_v3/test_run_records.py`
- `tests/p3_v3/test_cli.py`

Consumes: the authority hashes in section Authority and Frozen Inputs; existing functions `validate_exact_object`, `canonical_sha256`, `EvidenceError`.

Produces: importable validators and confirmatory rejection. Produces no `data/p3_v3/pilot/boost_math/` scientific artifact.

Required signatures in `src/p3_v3/pilot.py`:

```python
from collections.abc import Mapping
from typing import Any

PILOT_SCHEMAS = (
    "p3-pilot-plan-v1",
    "p3-pilot-freeze-v1",
    "p3-pilot-attempt-v1",
    "p3-pilot-receipt-v1",
)
PILOT_EXECUTION_CLASS = "PILOT_ONLY"
PILOT_DENOMINATOR = "PILOT_ONLY"

def is_pilot_artifact(value: Mapping[str, Any]) -> bool:
    schema = value.get("schema_version")
    execution = value.get("execution_class")
    denominator = value.get("denominator")
    return (
        schema in PILOT_SCHEMAS
        or execution == PILOT_EXECUTION_CLASS
        or denominator == PILOT_DENOMINATOR
    )

def reject_confirmatory_pilot(value: Mapping[str, Any], context: str) -> None:
    if is_pilot_artifact(value):
        raise EvidenceError(
            "E_PILOT_DENOMINATOR_LEAK",
            f"{context} rejected PILOT_ONLY or p3-pilot schema",
        )

def validate_pilot_plan(value: Mapping[str, Any]) -> dict[str, Any]:
    return _validate_named_schema(value, "p3-pilot-plan-v1")

def validate_pilot_freeze(value: Mapping[str, Any]) -> dict[str, Any]:
    return _validate_named_schema(value, "p3-pilot-freeze-v1")

def validate_pilot_attempt(value: Mapping[str, Any]) -> dict[str, Any]:
    return _validate_named_schema(value, "p3-pilot-attempt-v1")

def validate_pilot_receipt(value: Mapping[str, Any]) -> dict[str, Any]:
    return _validate_named_schema(value, "p3-pilot-receipt-v1")
```

`_validate_named_schema` must use `validate_exact_object`, verify `artifact_sha256`, force `execution_class=PILOT_ONLY`, force `denominator=PILOT_ONLY`, and force the frozen Boost.Math identity fields.

In `src/p3_v3/packages.py`, `build_package` and `_validate_manifest` must call `reject_confirmatory_pilot` on the manifest and on every file payload that is canonical JSON. A `class` value `PILOT_ONLY` is `E_PILOT_PACKAGE_CLASS`.

In `src/p3_v3/run_records.py`, `_validate_locked_jobs` must treat `execution_class=PILOT_ONLY` as `E_PILOT_DENOMINATOR_LEAK` rather than the generic `E_AUTHORITY_EXECUTION_CLASS`. `validate_claim_ledger` must reject any evidence reference whose path starts with `data/p3_v3/pilot/` or whose referenced bytes validate as a pilot schema.

In `scripts/p3_v3/evidence.py`, each confirmatory command listed in File Map must load candidate JSON and call `reject_confirmatory_pilot` before any write.

RED, expected exit 1:

```text
env PYTHONPATH=src python3 -m pytest tests/p3_v3/test_pilot.py tests/p3_v3/test_pilot_leakage.py -q
```

Minimum GREEN, expected exit 0:

```text
env PYTHONPATH=src python3 -m pytest tests/p3_v3/test_pilot.py tests/p3_v3/test_pilot_leakage.py -q
```

`tests/p3_v3/test_pilot.py` must include:

- `test_validate_pilot_plan_roundtrip` writes a minimal valid plan through `write_canonical_json` and reads it back
- `test_pilot_plan_rejects_real_scientific` expects `E_PILOT_DENOMINATOR_LEAK` when `execution_class` is `REAL_SCIENTIFIC`
- `test_pilot_attempt_rejects_attempt_two` expects `E_PILOT_RETRY_FORBIDDEN`

`tests/p3_v3/test_pilot_leakage.py` must include:

- `test_build_package_rejects_pilot_class` expects `E_PILOT_PACKAGE_CLASS`
- `test_validate_claim_ledger_rejects_pilot_reference` expects `E_PILOT_DENOMINATOR_LEAK`
- `test_evidence_verify_package_rejects_pilot_schema` invokes `scripts/p3_v3/evidence.py verify-package` and expects exit 1
- `test_filename_alone_is_insufficient` feeds a confirmatory-looking filename that contains `execution_class=PILOT_ONLY` and still expects rejection

Regression, expected exit 0:

```text
env PYTHONPATH=src python3 -m pytest tests/p3_v3/test_artifacts.py tests/p3_v3/test_packages.py tests/p3_v3/test_run_records.py tests/p3_v3/test_cli.py -q
```

Independent stop: Sol High implementation review. Do not mount source. Do not create `user-auth-preparation.txt`.

### Task 2: Source Identity and Materialization Validation

User authorization required: yes, authorization A. Gate: `G2_SOURCE_AND_FREEZE` first half.

Create:

- `data/p3_v3/pilot/boost_math/source-manifest.json` (only after authorization A and a user-mounted archive)
- later helper functions in `src/p3_v3/pilot.py` named below

Modify:

- `src/p3_v3/pilot.py`
- `scripts/p3_v3/pilot.py`
- `tests/p3_v3/test_pilot.py`

Consumes: user-mounted public archive path supplied as `--archive`; authorization file `data/p3_v3/pilot/boost_math/user-auth-preparation.txt`; frozen identities in Authority and Frozen Inputs.

Produces: `p3-pilot-plan-v1` source-manifest body written as `source-manifest.json` with `schema_version` still using the common pilot keys plus:

```text
archive_sha256: str
archive_bytes: int
normalized_source_tree_sha256: str
build_descriptor_sha256: str
neutral_snapshot_id: str
mount_path_sha256: str
authorization_sha256: str
```

Required signatures:

```python
def load_mounted_archive(archive_path: str, timeout_seconds: int = 300) -> bytes:
    return _read_regular_file_with_timeout(archive_path, timeout_seconds)

def materialize_public_source(archive_bytes: bytes, target_root: str) -> None:
    _extract_regular_files_only(archive_bytes, target_root)

def build_source_snapshot(target_root: str) -> SourceSnapshot:
    return _snapshot_regular_files(target_root)

def validate_boostmath_source_identity(
    archive_bytes: bytes,
    snapshot: SourceSnapshot,
    build_descriptor: Mapping[str, Any],
    authorization_path: str,
) -> dict[str, Any]:
    tree = canonical_source_tree_sha256(snapshot)
    if tree != "93a62859d7fdd6b2068e494bbe6e3e27180b874cbd27055ac27f941e507a90d8":
        raise EvidenceError("E_PILOT_SOURCE_IDENTITY", "normalized tree differs")
    if canonical_sha256(build_descriptor) != "68d2e0fd34b845bb0df22b29003f26259d5655d2ec80c18895ff36904db2d95d":
        raise EvidenceError("E_PILOT_SOURCE_IDENTITY", "build descriptor differs")
    return _source_manifest_body(archive_bytes, snapshot, build_descriptor, authorization_path)
```

Identity proof is the conjunction of archive SHA-256, archive byte count, `canonical_source_tree_sha256`, `build_descriptor_sha256`, and `neutral_snapshot_id`. File count, directory names, and declaration counts are not sufficient and must not appear in the pass predicate.

CLI:

```text
env PYTHONPATH=src python3 scripts/p3_v3/pilot.py validate-source \
  --archive /absolute/user-mounted/boost-math.archive \
  --authorization data/p3_v3/pilot/boost_math/user-auth-preparation.txt \
  --output data/p3_v3/pilot/boost_math/source-manifest.json
```

Expected exit 0 only when the frozen tree hash matches. Missing authorization file, network fetch, or Package C path is `E_PILOT_SOURCE_IDENTITY` or `E_PILOT_PACKAGE_CLASS` and exit 1. Timeout at 300 seconds writes a terminal attempt with `terminal_status=TIMEOUT` and must not retry.

RED, expected exit 1:

```text
env PYTHONPATH=src python3 -m pytest tests/p3_v3/test_pilot.py::test_source_identity_rejects_wrong_tree -q
```

Minimum GREEN, expected exit 0:

```text
env PYTHONPATH=src python3 -m pytest tests/p3_v3/test_pilot.py::test_source_identity_rejects_wrong_tree tests/p3_v3/test_pilot.py::test_source_identity_accepts_matching_tree_fixture -q
```

The accepting test must use a tiny synthetic snapshot whose `canonical_source_tree_sha256` is monkeypatched or whose fixture bytes are constructed so the function compares against an injected expected digest. It must not download Boost.Math and must not read Package C.

Regression, expected exit 0:

```text
env PYTHONPATH=src python3 -m pytest tests/p3_v3/test_pilot.py tests/p3_v3/test_pilot_leakage.py tests/p3_v3/test_bridge_and_frames.py -q
```

Independent stop: source-manifest exists and Sol High may review it together with the later freeze. Do not configure CMake. Do not compile. Do not read mutant outcomes because none exist.

### Task 3: Outcome-Blind Contract, Site, MR, and Input Freeze

User authorization required: yes, the same authorization A. Gate: `G2_SOURCE_AND_FREEZE` second half. Outcome bytes read: forbidden.

Create:

- `data/p3_v3/pilot/boost_math/pilot-freeze.json` or `data/p3_v3/pilot/boost_math/pilot-insufficiency.json`

Modify:

- `src/p3_v3/pilot.py`
- `scripts/p3_v3/pilot.py`
- `tests/p3_v3/test_pilot.py`

Consumes: `source-manifest.json`; mounted public headers and public documentation only; Phase 1 public-behavior frame `a740d5019a19ee354f07e73e7c542dd1d79fb8969a2af48d5ef7975e534da4d3` as a declaration catalog, not as a site-acceptance count.

Produces: `p3-pilot-freeze-v1` with the 2/4/4/30/5 cardinality.

Required signatures:

```python
def select_specification_relations(
    public_doc_bytes_by_path: Mapping[str, bytes],
    source_snapshot: SourceSnapshot,
) -> list[dict[str, Any]]:
    return _relations_from_public_spec(public_doc_bytes_by_path, source_snapshot)

def freeze_pilot_objects(
    relations: list[dict[str, Any]],
    semantic_mutants: list[dict[str, Any]],
    syntactic_mutants: list[dict[str, Any]],
    common_inputs: list[dict[str, Any]],
    contract_groups: list[dict[str, Any]],
    source_manifest: Mapping[str, Any],
) -> dict[str, Any]:
    return validate_pilot_freeze(
        _assemble_freeze(
            relations,
            semantic_mutants,
            syntactic_mutants,
            common_inputs,
            contract_groups,
            source_manifest,
        )
    )
```

Selection rules:

- A relation is admissible only when a public document span and a public header declaration both name the same mathematical identity.
- The two erf strings may be proposed by an operator. The freeze function must accept them only when those spans exist in the mounted tree. This plan does not freeze them.
- Semantic mutants must be real edits at implementation sites in the mounted tree. Distinct `site_id` count must be at least 2.
- Each syntactic baseline must share the same `site_id` as its semantic pair and must use a syntactic operator from `data/p3_v3/protocol/operator_catalogue.md` without reading any kill result.
- `PILOT_COMMON` has length 30 and a single `artifact_sha256`.
- Each `PILOT_CONTRACT` group has length 5. `contract_groups[0]["artifact_sha256"] != contract_groups[1]["artifact_sha256"]`.
- Timeouts copied from the plan schema are immutable after freeze.

CLI:

```text
env PYTHONPATH=src python3 scripts/p3_v3/pilot.py freeze \
  --source-manifest data/p3_v3/pilot/boost_math/source-manifest.json \
  --authorization data/p3_v3/pilot/boost_math/user-auth-preparation.txt \
  --output data/p3_v3/pilot/boost_math/pilot-freeze.json
```

Expected exit 0 on a complete freeze. Expected exit 2 and `E_PILOT_FREEZE_INCOMPLETE` when the 2/4/4/30/5 rule fails. Expected exit 1 if any function opens a path containing `outcome`, `kill-matrix`, `PackageC`, or `p12-reveal`.

RED, expected exit 1:

```text
env PYTHONPATH=src python3 -m pytest tests/p3_v3/test_pilot.py::test_freeze_rejects_count_three_relations -q
```

Minimum GREEN, expected exit 0:

```text
env PYTHONPATH=src python3 -m pytest tests/p3_v3/test_pilot.py::test_freeze_rejects_count_three_relations tests/p3_v3/test_pilot.py::test_freeze_accepts_exact_244305_fixture tests/p3_v3/test_pilot.py::test_freeze_rejects_reused_contract_identity tests/p3_v3/test_pilot.py::test_freeze_rejects_outcome_bytes_read -q
```

Regression, expected exit 0:

```text
env PYTHONPATH=src python3 -m pytest tests/p3_v3/test_pilot.py tests/p3_v3/test_pilot_leakage.py -q
```

Independent stop: Sol High freeze review. Do not compile mutants. Do not evaluate inputs against mutants.

### Task 4: Authorized Boost.Math Pilot Execution

User authorization required: yes, authorization B. Gate: `G3_EXECUTION` after Sol High freeze PASS.

Create:

- `data/p3_v3/pilot/boost_math/attempts/<job_id>/1/intent.json`
- `data/p3_v3/pilot/boost_math/attempts/<job_id>/1/result.json`

Modify:

- `src/p3_v3/pilot.py`
- `scripts/p3_v3/pilot.py`
- `tests/p3_v3/test_pilot.py`

Consumes: `pilot-freeze.json`; `user-auth-execution.txt`; mounted source already validated in Task 2.

Produces: one `p3-pilot-attempt-v1` per command. Job ids are exactly:

- `job-source-already-closed` is not re-run
- `job-cmake-configure`
- `job-baseline-build`
- `job-baseline-smoke`
- `job-mutant-build-<semantic_or_syntactic_id>` for each of the 8 mutants
- `job-mutant-eval-<mutant_id>-<input_class>-<input_id>` for each frozen evaluation cell

Timeouts: configure 900 s, baseline build 3600 s, baseline smoke 1800 s, each mutant build 900 s, each mutant evaluation 600 s, whole pilot wall 14400 s. A timeout is terminal. The timed-out object stays in the freeze. The executor must not replace it.

Required signatures:

```python
def create_pilot_intent(attempt_dir: str, intent: Mapping[str, Any]) -> None:
    validate_pilot_attempt({**dict(intent), "ended_at": intent["started_at"], "exit_code": None, "stdout_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", "stderr_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", "terminal_status": "INCONCLUSIVE", "failure_reason": "", "artifact_sha256": ""})
    write_canonical_json(Path(attempt_dir) / "intent.json", _complete_attempt(intent), exclusive=True)

def run_pilot_command(intent: Mapping[str, Any]) -> dict[str, Any]:
    return _run_once(intent)

def write_pilot_result(attempt_dir: str, result: Mapping[str, Any]) -> None:
    write_canonical_json(Path(attempt_dir) / "result.json", validate_pilot_attempt(result), exclusive=True)
```

`_run_once` must set `shell=False`, enforce `timeout_seconds`, hash stdout and stderr, record `wall_seconds`, `cpu_seconds`, and `peak_rss_bytes`, and refuse a second call with the same `run_id`.

CUDA missing is ignored. CMake extra flags must not add `-DCMAKE_CUDA_COMPILER` as a required cache entry.

CLI:

```text
env PYTHONPATH=src python3 scripts/p3_v3/pilot.py execute \
  --freeze data/p3_v3/pilot/boost_math/pilot-freeze.json \
  --authorization data/p3_v3/pilot/boost_math/user-auth-execution.txt \
  --attempt-root data/p3_v3/pilot/boost_math/attempts
```

Expected exit 0 when every frozen job has a terminal attempt. Expected exit 1 on missing authorization B, on any retry, or on output written outside `data/p3_v3/pilot/`.

RED, expected exit 1:

```text
env PYTHONPATH=src python3 -m pytest tests/p3_v3/test_pilot.py::test_execute_rejects_missing_authorization_b -q
```

Minimum GREEN, expected exit 0:

```text
env PYTHONPATH=src python3 -m pytest tests/p3_v3/test_pilot.py::test_execute_rejects_missing_authorization_b tests/p3_v3/test_pilot.py::test_execute_records_timeout_without_retry tests/p3_v3/test_pilot.py::test_execute_rejects_second_run_id -q
```

Those tests must use a fake command such as `python3 -c "import time; time.sleep(5)"` with `timeout_seconds=1`. They must not invoke CMake on Boost.Math in the unit suite.

Regression, expected exit 0:

```text
env PYTHONPATH=src python3 -m pytest tests/p3_v3/test_pilot.py tests/p3_v3/test_pilot_leakage.py tests/p3_v3/test_run_records.py -q
```

Independent stop: all frozen jobs terminal. Do not open claim ledger. Do not call `close_phase` or `verify-evidence`.

### Task 5: Evidence Closure and Reproducibility Package

User authorization required: no additional authorization. Gate: `G4_EVIDENCE_PACKAGE` after `G3_EXECUTION` terminals exist.

Create:

- `data/p3_v3/pilot/boost_math/score-task.yml`
- `data/p3_v3/pilot/boost_math/experiment-ledger.yml`
- `data/p3_v3/pilot/boost_math/pilot-receipt.json`
- `docs/review_20260815/boost_math_pilot_evidence_package.md`

Modify:

- `src/p3_v3/pilot.py`
- `scripts/p3_v3/pilot.py`
- `tests/p3_v3/test_pilot.py`

Consumes: freeze, every attempt result, source-manifest.

Produces: the five evidence objects named in section 10.6 of the authorizing packet.

`score-task.yml` exact keys:

```text
research_question: "Can a known-identity CPU-only Boost.Math subject complete a 2/4/4/30/5 PILOT_ONLY path without entering the formal denominator?"
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
deterministic_reproducibility_policy: "same archive bytes, same freeze, same argv, same timeout, no retry"
stopping_rule: "first terminal result per run_id; full-pilot wall 14400 seconds"
claims: "blocked"
```

`experiment-ledger.yml` must contain one record per mutant and one cell per MR-input pair with fields `verdict` in `{kill,non_kill,inconclusive}`, `compile_failure`, `timeout`, `infrastructure_failure`, `non_equivalence_unproven`, `untriggered`, `wall_seconds`, `cpu_seconds`, `peak_rss_bytes`, and `failed_attempts` listing every terminal non-PASS attempt. It must not contain a retry of the same `run_id`.

Required signatures:

```python
def write_score_task(path: str, freeze: Mapping[str, Any]) -> None:
    _write_utf8_yaml(path, _score_task_body(freeze))

def write_experiment_ledger(path: str, freeze: Mapping[str, Any], attempts: list[Mapping[str, Any]]) -> None:
    _write_utf8_yaml(path, _ledger_body(freeze, attempts))

def close_pilot_receipt(
    freeze: Mapping[str, Any],
    score_task_bytes: bytes,
    ledger_bytes: bytes,
    attempts: list[Mapping[str, Any]],
) -> dict[str, Any]:
    return validate_pilot_receipt(_receipt_body(freeze, score_task_bytes, ledger_bytes, attempts))
```

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

Expected exit 0 when the receipt self-hash matches and `claims_status=blocked`. Expected exit 1 if the receipt would set `rq4_supported=true` or `formal_denominator_membership=true`.

RED, expected exit 1:

```text
env PYTHONPATH=src python3 -m pytest tests/p3_v3/test_pilot.py::test_receipt_rejects_rq4_supported -q
```

Minimum GREEN, expected exit 0:

```text
env PYTHONPATH=src python3 -m pytest tests/p3_v3/test_pilot.py::test_receipt_rejects_rq4_supported tests/p3_v3/test_pilot.py::test_close_writes_blocked_receipt tests/p3_v3/test_pilot.py::test_close_rejects_claim_ledger_write -q
```

Regression, expected exit 0:

```text
env PYTHONPATH=src python3 -m pytest tests/p3_v3/test_pilot.py tests/p3_v3/test_pilot_leakage.py tests/p3_v3/test_packages.py tests/p3_v3/test_run_records.py tests/p3_v3/test_cli.py -q
```

Independent stop: Sol High evidence review. Do not upgrade claims. Do not start a second subject.

## Stop Conditions

Stop and return BLOCK, writing the named error when an artifact exists:

- HEAD or `origin/main` is not the authorized task start commit
- any authority hash differs
- Package C, P12 reveal, patch, reference MR, evaluated MR, or outcome bytes are required
- Boost.Math source would be downloaded or taken from Package C
- `canonical_source_tree_sha256` is not `93a62859d7fdd6b2068e494bbe6e3e27180b874cbd27055ac27f941e507a90d8`
- confirmatory entry points cannot reject pilot artifacts by schema and `execution_class`
- a task tries to treat the pilot as confirmatory or to support RQ4
- a task writes the claim ledger
- a task replaces a frozen relation, site, mutant, baseline, MR, input, or timeout after seeing a result
- a task retries a `run_id` or treats timeout as non-terminal
- CUDA absence is used as a blocker
- native profiling is used as a precondition
- a third file outside this plan's File Map is required for the scientific path

## Acceptance Criteria

A later authorized execution may close only when all of the following are true:

- Schemas `p3-pilot-plan-v1`, `p3-pilot-freeze-v1`, `p3-pilot-attempt-v1`, and `p3-pilot-receipt-v1` validate
- Confirmatory `build-package`, `verify-package`, `verify-run-records`, `close-phase`, `verify-evidence`, `freeze-authority-lock`, and `run-preflight` reject pilot objects with `E_PILOT_DENOMINATOR_LEAK` or `E_PILOT_PACKAGE_CLASS`
- Source identity binds archive SHA-256, archive bytes, normalized tree `93a62859d7fdd6b2068e494bbe6e3e27180b874cbd27055ac27f941e507a90d8`, build descriptor `68d2e0fd34b845bb0df22b29003f26259d5655d2ec80c18895ff36904db2d95d`, and snapshot `74cdc825c3c728c25f5ea857af1565350515a4e631fb0a874c26e810ec437886`
- Freeze cardinality is 2/4/4/30/5 with paired semantic and syntactic mutants and distinct contract-group identities
- Two user authorization files were hashed into the relevant artifacts
- Timeouts are the frozen integers and appear as terminal states when exceeded
- `score-task.yml` and `experiment-ledger.yml` exist and the receipt says `claims_status=blocked`
- Claim ledger bytes are unchanged
- CUDA was not required
- Native profiling was not executed as a gate
- No production confirmatory path ran

This planning node accepts only the creation of this file and its review packet.

## Review Handoff

Requested reviewer: GPT-5.6 Sol High, reasoning setting high.

Requested state after an independent PASS: `PILOT_PLAN_FROZEN`. Until that PASS exists, the repository state remains `PILOT_PLAN_REVIEW_CANDIDATE`.

The reviewer must not start Task 1. The reviewer must not mount Boost.Math. The reviewer must not treat this plan as production scientific intent. Claims stay `blocked`.
