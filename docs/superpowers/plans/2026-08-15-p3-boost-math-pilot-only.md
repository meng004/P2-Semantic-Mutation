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
3. Two outcome-blind hash chains freeze common inputs, sites, contracts, reconstructable patches, certification policy, and a sibling MR inventory.
4. `pilot-freeze.json` assembles only after both chains close. It binds source, harness, build, MR, oracle, tolerance, input, timeout, and command-template identities. It must not contain `authorization_b_sha256`.
5. Task 4 verifies authorization B and then writes `execution-plan.json` with the exact complete job inventory.
6. Authorized execution accepts only execution-plan `job_id` values, uses isolated original and mutant roots, and applies an executable kill oracle.
7. Closure writes `score-task.yml`, `experiment-ledger.yml`, `pilot-receipt.json`, and `docs/review_20260815/boost_math_pilot_evidence_package.md`.

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
- `data/p3_v3/pilot/boost_math/execution-plan.json`
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

Named schemas, and any future schema whose version starts with `p3-pilot-`, are pilot artifacts:

- `p3-pilot-plan-v1`
- `p3-pilot-source-manifest-v1`
- `p3-pilot-freeze-v1`
- `p3-pilot-execution-plan-v1`
- `p3-pilot-intent-v1`
- `p3-pilot-result-v1`
- `p3-pilot-certification-intent-v1`
- `p3-pilot-certification-result-v1`
- `p3-pilot-not-started-v1`
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

Runtime fields are not common. Intent and result use separate exact schemas below.

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

Path: `data/p3_v3/pilot/boost_math/pilot-freeze.json`. Produced only in Task 3 after authorization A. It must not contain `authorization_b_sha256`.

Declared additional keys:

```text
freeze_id: str
gate_id: "G2_SOURCE_AND_FREEZE"
source_manifest_sha256: str
harness_source_sha256: str
harness_artifact_path: str
build_descriptor_sha256: str
command_template_sha256: str
timeout_policy: dict
construction_contracts: list
semantic_mutants: list
syntactic_mutants: list
pairs: list
pilot_common_inputs: list
pilot_contract_inputs: list
evaluation_mrs: list
primary_planned_count: 480
sensitivity_planned_count: 80
evaluation_planned_count: 560
certification_planned_count: 8
build_planned_count: 11
original_execution_planned_count: 80
outcome_bytes_read: false
```

Cardinality remains 2/4/4/30/5 plus exactly 2 `evaluation_mr_id` values. Distinct semantic `site_id` values must be at least 2. The two `PILOT_CONTRACT` group `artifact_sha256` values must differ. `outcome_bytes_read=true` is `E_PILOT_FREEZE_INCOMPLETE`. Presence of `authorization_b_sha256` or `job_argv` on this schema is `E_PILOT_CHRONOLOGY`.

### Schema `p3-pilot-execution-plan-v1`

Path: `data/p3_v3/pilot/boost_math/execution-plan.json`. Produced only in Task 4 after authorization B is verified.

Declared additional keys:

```text
execution_plan_id: str
gate_id: "G3_EXECUTION"
freeze_sha256: str
source_manifest_sha256: str
authorization_b_sha256: str
jobs: list
build_jobs: list
certification_jobs: list
original_execution_jobs: list
primary_jobs: list
sensitivity_jobs: list
primary_planned_count: 480
sensitivity_planned_count: 80
evaluation_planned_count: 560
certification_planned_count: 8
build_planned_count: 11
original_execution_planned_count: 80
total_planned_count: 659
```

Each `jobs` item is an exact object:

```text
job_id: str
job_kind: str
evaluation_input_class: str | None
argv: list[str]
cwd_identity: str
tree_sha256: str
timeout_seconds: int
command_template_sha256: str
input_sha256: str | None
evaluation_mr_sha256: str | None
mutant_id: str | None
dependency_job_ids: list[str]
predecessor_sha256: list[str]
```

`job_kind` is one of `CMAKE_CONFIGURE`, `BASELINE_BUILD`, `BASELINE_SMOKE`, `MUTANT_BUILD`, `CERTIFICATION`, `ORIGINAL_EVALUATION`, `PRIMARY_EVALUATION`, `SENSITIVITY_EVALUATION`. `run_pilot_command` accepts a `job_id` only when it equals an item in `jobs`. Prefix matching such as `job-mutant-build-` is forbidden. Implicit fields `freeze["source_manifest"]` and `freeze["job_argv"]` are forbidden.

`jobs` is the concatenation, in this frozen order, of `build_jobs`, `certification_jobs`, `original_execution_jobs`, `primary_jobs`, and `sensitivity_jobs`. Lengths must be 11, 8, 80, 480, and 80. `total_planned_count` is 659.

Each `ORIGINAL_EVALUATION` job binds the original tree SHA-256, evaluation MR SHA-256, input SHA-256, `evaluation_input_class`, exact argv, timeout, command-template SHA-256, and predecessor hashes. Unique original runs are `2 evaluation MRs × 30 PILOT_COMMON` plus `2 evaluation MRs × 5 PILOT_CONTRACT × 2 contracts`, which is 80. Those 80 identities populate `original_execution_jobs` and are members of `jobs`. Implicit original execution, implicit cache, or excluding an original process from the executable count is `E_PILOT_OUTPUT_DRIFT`.

Each `PRIMARY_EVALUATION` and `SENSITIVITY_EVALUATION` job must include `dependency_job_ids` naming the corresponding original job and the required build and certification jobs. Evaluation rows remain 560. Original jobs are not extra mutant rows. A missing original identity is `E_PILOT_OUTPUT_DRIFT`.

### Schema `p3-pilot-intent-v1`

Path: `data/p3_v3/pilot/boost_math/attempts/<job_id>/1/intent.json`. Written atomically before launch. Exact additional keys:

```text
job_id: str
run_id: str
attempt: 1
gate_id: str
argv: list[str]
cwd_identity: str
timeout_seconds: int
started_at: str
execution_plan_sha256: str
```

Intent must not contain `ended_at`, `exit_code`, `stdout_sha256`, `stderr_sha256`, `terminal_status`, `failure_reason`, `wall_seconds`, `cpu_seconds`, or `peak_rss_bytes`. A forged terminal field is `E_PILOT_ORACLE`.

### Schema `p3-pilot-result-v1`

Path: `data/p3_v3/pilot/boost_math/attempts/<job_id>/1/result.json`. Written atomically after process termination. Exact additional keys:

```text
job_id: str
run_id: str
attempt: 1
intent_sha256: str
ended_at: str
exit_code: int | None
stdout_sha256: str | None
stderr_sha256: str | None
terminal_status: str
failure_reason: str
wall_seconds: float | None
cpu_seconds: float | None
peak_rss_bytes: int | None
```

Result must bind `intent_sha256` of the already written intent. If `intent.json` exists, a second launch of the same `run_id`/`job_id` is `E_PILOT_RETRY_FORBIDDEN` even when `result.json` is absent. Timeout writes result `TIMEOUT`. A not-started job must not write `result.json` and must not forge `intent_sha256`.

`stdout_sha256`, `stderr_sha256`, `wall_seconds`, `cpu_seconds`, and `peak_rss_bytes` may all be `null` only when `terminal_status=FAIL_INFRASTRUCTURE` and `failure_reason=ORPHANED_INTENT_NO_PROCESS`. A normally launched and terminated job must record the observed stdout hash, stderr hash, and resource metrics. Zero values or empty-output hashes must not stand in for unobserved evidence.

### Schema `p3-pilot-not-started-v1`

Path: `data/p3_v3/pilot/boost_math/attempts/<job_id>/1/not-started.json`. Independent exact artifact. It is written only for jobs that never received an intent. Exact additional keys:

```text
job_id: str
run_id: str
execution_plan_sha256: str
job_sha256: str
recorded_at: str
launched: false
terminal_status: "INCONCLUSIVE"
failure_reason: str
predecessor_sha256: list[str]
dependency_job_ids: list[str]
```

`failure_reason` is exactly `GLOBAL_TIMEOUT_NOT_STARTED` or `DEPENDENCY_NOT_STARTED`. A not-started disposition must not contain `intent_sha256`, `started_at`, `argv`, `exit_code`, or any terminal result field. Forging `intent_sha256` is `E_PILOT_ORACLE`.

`started_count` counts only jobs that already have a written intent. `not_started_count` counts only valid not-started dispositions. `terminal_count` equals valid results plus valid not-started dispositions.

If an intent exists and the process later disappears, a reconciler may write a `p3-pilot-result-v1` with `terminal_status=FAIL_INFRASTRUCTURE` and `failure_reason=ORPHANED_INTENT_NO_PROCESS` only after proving that no process still holds that `job_id`. That write binds the original `intent_sha256`. It must not launch a command and is not a retry. If the old process cannot be proved absent, the runner must BLOCK and must not close the receipt.

If a dependency job fails, every not-yet-started downstream job is retained and receives `DEPENDENCY_NOT_STARTED`. Evaluation rows must not be deleted.

### Schema `p3-pilot-certification-intent-v1`

Path: `data/p3_v3/pilot/boost_math/attempts/<job_id>/1/certification-intent.json`. Written atomically before any certification job launch. Exact additional keys:

```text
job_id: str
run_id: str
attempt: 1
gate_id: "G3_EXECUTION"
mutant_id: str
frozen_contract_sha256: str
frozen_patch_sha256: str
mutant_tree_sha256: str
execution_plan_sha256: str
started_at: str
```

Certification intent must not contain `terminal_state`, `ended_at`, `exit_code`, gate verdicts, or any caller-supplied `witness_policy` terminal. A forged terminal is `E_PILOT_FORGED_POLICY`.

### Schema `p3-pilot-certification-result-v1`

Path: `data/p3_v3/pilot/boost_math/attempts/<job_id>/1/certification-result.json`. Written atomically after the nine-gate derivation. Exact additional keys:

```text
job_id: str
run_id: str
attempt: 1
intent_sha256: str
ended_at: str
gates: dict
terminal_state: str
witness_sha256: str
```

`gates` and `terminal_state` are derived only from frozen identities plus immutable execution receipts. A caller-supplied result body is `E_PILOT_FORGED_POLICY`. Certification must not read MR kill outcomes.

### Schema `p3-pilot-receipt-v1`

Additional keys: `receipt_id`, `gate_id` equal to `G4_EVIDENCE_PACKAGE`, `freeze_sha256`, `execution_plan_sha256`, `score_task_sha256`, `ledger_sha256`, `build_planned_count`, `build_started_count`, `build_terminal_count`, `build_not_started_count`, `certification_planned_count`, `certification_started_count`, `certification_terminal_count`, `certification_not_started_count`, `primary_planned_count`, `primary_started_count`, `primary_terminal_count`, `primary_not_started_count`, `sensitivity_planned_count`, `sensitivity_started_count`, `sensitivity_terminal_count`, `sensitivity_not_started_count`, `evaluation_planned_count`, `original_execution_planned_count`, `original_execution_started_count`, `original_execution_terminal_count`, `original_execution_not_started_count`, `total_planned_count`, `total_started_count`, `total_terminal_count`, `total_not_started_count`, `claims_status` equal to `blocked`, `rq4_supported` equal to `false`, `formal_denominator_membership` equal to `false`.

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
- `E_PILOT_ORPHAN_UNRESOLVED`
- `E_PILOT_BYTES_TYPE`
- `E_PILOT_PATCH_HASH`
- `E_PILOT_PATCH_SCOPE`
- `E_PILOT_TREE_HASH`
- `E_PILOT_FORGED_POLICY`
- `E_PILOT_WITNESS_COLLISION`
- `E_PILOT_CERT_READS_MR`
- `E_PILOT_CERT_INCOMPLETE`
- `E_PILOT_FREEZE_IMPLICIT_FIELD`
- `E_PILOT_NO_ELIGIBLE_SITE`
- `E_PILOT_NO_ELIGIBLE_OPERATOR`
- `E_PILOT_CONTRACT_UNREPRESENTED`

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

No builder may accept a caller-chosen already-picked list as authority. Each builder enumerates the qualified set, sorts by the published total order below, and keeps only the first N items. First-N must use that published composite order directly. Sorting by undeclared `construction_contract_id` or hash order is `E_PILOT_SELECTION`.

- relation order: `(semantic_contract_family, public_doc_path, public_doc_span, declaration_path, declaration_span, relation_sha256)`
- site order: `(relative_path, source_span_start, source_span_end, site_sha256)`
- semantic operator order: `(semantic_contract_family, construction_mechanism, operator_id)`
- syntactic operator order: `(operator_id, relative_path, source_span_start, patch_sha256)`
- input order: `(generator_id, seed_sha256, ordinal, input_sha256)`
- MR order: `(semantic_signature, evaluation_mr_id)`
- semantic first-N composite order: `(relation order, site order, semantic operator order)`
- syntactic first-candidate composite order: `(shared site order, syntactic operator order)`

Contracts are sorted by relation order before enumeration. Sites, operators, inputs, and MRs are sorted by their published orders. Any permutation of an input sequence must emit identical selected identities and identical artifact SHA-256 values.

Frozen stronger assignment: exactly 2 semantic mutants per frozen construction contract (2+2). Each frozen construction contract must be represented by those 2 semantic mutants. A contract with fewer than 2 qualified identities is `E_PILOT_FREEZE_INCOMPLETE`. Tests must permute the input sequences and still obtain the same 2+2 coverage.

On a shared site, the syntactic baseline is the unique first candidate under the published syntactic operator order. A second candidate on that site is not selected.

`relation_sha256` is `canonical_sha256` of the relation identity fields excluding `relation_sha256` and `artifact_sha256`. `site_sha256` is `canonical_sha256` of path and span. `semantic_signature` is `canonical_sha256` of `source_input_transform`, `follow_up_input_transform`, metamorphic predicate, tolerance class, and oracle direction.

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
relation_sha256: str
artifact_sha256: str
```

Each semantic mutant object:

```text
semantic_mutant_id: str
construction_contract_id: str
site_id: str
site_kind: str
source_path: str
source_span_start: int
source_span_end: int
original_span_sha256: str
replacement_base64: str
replacement_sha256: str
construction_mechanism: str
operator_id: str
patch_sha256: str
original_tree_sha256: str
mutant_tree_sha256: str
expected_semantic_effect: str
artifact_sha256: str
```

The semantic-patch freeze artifact must embed the complete JSON-safe `encode_patch` body, or an exact content-addressed reference that reconstructs that body. `patch_sha256` alone is insufficient.

Each syntactic baseline object:

```text
syntactic_mutant_id: str
paired_semantic_mutant_id: str
shared_site_id: str
operator_id: str
replacement_base64: str
replacement_sha256: str
original_span_sha256: str
patch_sha256: str
mutant_tree_sha256: str
artifact_sha256: str
```

The syntactic-baseline freeze artifact must likewise embed a reconstructable JSON-safe patch body or an exact content-addressed reference. Syntactic mutants inherit the paired semantic mutant's `PILOT_CONTRACT` input group.

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
import base64
import hashlib
import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from p3_v3.artifacts import EvidenceError, canonical_sha256, file_sha256, validate_exact_object, validate_sha256
from p3_v3.bridge_and_frames import SourceSnapshot, SourceSnapshotEntry, canonical_source_tree_sha256


def raw_sha256(data: bytes) -> str:
    if not isinstance(data, (bytes, bytearray)):
        raise EvidenceError("E_PILOT_BYTES_TYPE", "raw_sha256 accepts only bytes")
    return hashlib.sha256(bytes(data)).hexdigest()


def encode_patch(
    *,
    relative_path: str,
    original_span: bytes,
    replacement: bytes,
    source_span_start: int,
    source_span_end: int,
    source_file_sha256: str,
) -> dict[str, Any]:
    replacement_b64 = base64.b64encode(replacement).decode("ascii")
    body = {
        "relative_path": relative_path,
        "original_span_sha256": raw_sha256(original_span),
        "replacement_base64": replacement_b64,
        "replacement_sha256": raw_sha256(replacement),
        "source_span_start": source_span_start,
        "source_span_end": source_span_end,
        "source_file_sha256": source_file_sha256,
    }
    json.dumps(body, allow_nan=False)
    return {**body, "patch_sha256": canonical_sha256(body)}


def decode_patch(patch: Mapping[str, Any]) -> bytes:
    replacement = base64.b64decode(patch["replacement_base64"], validate=True)
    if raw_sha256(replacement) != patch["replacement_sha256"]:
        raise EvidenceError("E_PILOT_PATCH_HASH", "replacement hash mismatch")
    return replacement


def apply_frozen_patch(
    source_snapshot: SourceSnapshot,
    patch: Mapping[str, Any],
    *,
    expected_mutant_tree_sha256: str,
) -> SourceSnapshot:
    replacement = decode_patch(patch)
    entries: list[SourceSnapshotEntry] = []
    found = False
    for entry in source_snapshot.entries:
        if entry.relative_path != patch["relative_path"]:
            entries.append(
                SourceSnapshotEntry(
                    relative_path=entry.relative_path,
                    mode=entry.mode,
                    sha256=entry.sha256,
                    content=entry.content,
                )
            )
            continue
        found = True
        if entry.sha256 != patch["source_file_sha256"]:
            raise EvidenceError("E_PILOT_PATCH_HASH", "source file hash mismatch")
        original = entry.content[patch["source_span_start"]:patch["source_span_end"]]
        if raw_sha256(original) != patch["original_span_sha256"]:
            raise EvidenceError("E_PILOT_PATCH_HASH", "original span hash mismatch")
        content = (
            entry.content[:patch["source_span_start"]]
            + replacement
            + entry.content[patch["source_span_end"]:]
        )
        entries.append(
            SourceSnapshotEntry(
                relative_path=entry.relative_path,
                mode=entry.mode,
                sha256=raw_sha256(content),
                content=content,
            )
        )
    if not found:
        raise EvidenceError("E_PILOT_PATCH_SCOPE", "patched path missing")
    entries.sort(key=lambda item: item.relative_path.encode("utf-8"))
    snapshot = SourceSnapshot(entries=tuple(entries))
    if canonical_source_tree_sha256(snapshot) != expected_mutant_tree_sha256:
        raise EvidenceError("E_PILOT_TREE_HASH", "materialized tree hash mismatch")
    return snapshot


def _relation_key(contract: Mapping[str, Any]) -> tuple[Any, ...]:
    return (
        contract["semantic_contract_family"],
        contract["public_doc_path"],
        contract["public_doc_span"],
        contract["declaration_path"],
        contract["declaration_span"],
        contract["relation_sha256"],
    )


def _site_key(site: Mapping[str, Any]) -> tuple[Any, ...]:
    return (
        site["relative_path"],
        site["source_span_start"],
        site["source_span_end"],
        site["site_sha256"],
    )


def _semantic_operator_key(operator: Mapping[str, Any]) -> tuple[Any, ...]:
    return (
        operator["semantic_contract_family"],
        operator["construction_mechanism"],
        operator["operator_id"],
    )


def _syntactic_operator_key(operator: Mapping[str, Any], site: Mapping[str, Any], patch_sha256: str) -> tuple[Any, ...]:
    return (
        operator["operator_id"],
        site["relative_path"],
        site["source_span_start"],
        patch_sha256,
    )


def _mutant_id(mutant: Mapping[str, Any]) -> str:
    semantic = mutant.get("semantic_mutant_id")
    syntactic = mutant.get("syntactic_mutant_id")
    if isinstance(semantic, str) and syntactic is None:
        return semantic
    if isinstance(syntactic, str) and semantic is None:
        return syntactic
    raise EvidenceError(
        "E_PILOT_SELECTION",
        "mutant id must be exactly one of semantic_mutant_id or syntactic_mutant_id",
    )


def build_semantic_mutants(
    contracts: Sequence[Mapping[str, Any]],
    sites: Sequence[Mapping[str, Any]],
    operator_catalogue: Mapping[str, Any],
    source_snapshot: SourceSnapshot,
) -> list[dict[str, Any]]:
    if len(contracts) != 2:
        raise EvidenceError("E_PILOT_FREEZE_INCOMPLETE", "need exactly 2 contracts")
    qualified: list[tuple[tuple[Any, ...], dict[str, Any]]] = []
    for contract in contracts:
        for site in sites:
            for operator in operator_catalogue["operators"]:
                if operator["semantic_contract_family"] != contract["semantic_contract_family"]:
                    continue
                if site["site_kind"] not in operator["allowed_site_kinds"]:
                    continue
                if not _site_satisfies_precondition(site, operator):
                    continue
                identity = _materialize_semantic_mutant(source_snapshot, site, operator, contract)
                if identity["construction_contract_id"] != contract["construction_contract_id"]:
                    continue
                if "composite_order" in identity:
                    raise EvidenceError("E_PILOT_SELECTION", "composite_order must not enter a durable mutant")
                key = (
                    _relation_key(contract),
                    _site_key(site),
                    _semantic_operator_key(operator),
                )
                qualified.append((key, identity))
    qualified.sort(key=lambda item: item[0])
    selected: list[dict[str, Any]] = []
    per_contract: dict[str, int] = {}
    for _key, item in qualified:
        contract_id = item["construction_contract_id"]
        if per_contract.get(contract_id, 0) >= 2:
            continue
        selected.append(item)
        per_contract[contract_id] = per_contract.get(contract_id, 0) + 1
    if any(per_contract.get(item["construction_contract_id"], 0) != 2 for item in contracts):
        raise EvidenceError("E_PILOT_CONTRACT_UNREPRESENTED", "2+2 contract coverage failed")
    if len(selected) != 4:
        raise EvidenceError("E_PILOT_FREEZE_INCOMPLETE", "need 4 semantic mutants")
    return selected


def build_syntactic_baselines(
    semantic_mutants: Sequence[Mapping[str, Any]],
    operator_catalogue: Mapping[str, Any],
    source_snapshot: SourceSnapshot,
) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    for semantic in semantic_mutants:
        site = {
            "relative_path": semantic["source_path"],
            "source_span_start": semantic["source_span_start"],
            "site_kind": semantic["site_kind"],
        }
        candidates: list[tuple[tuple[Any, ...], Mapping[str, Any]]] = []
        for operator in operator_catalogue["operators"]:
            if operator["family"] != "syntactic":
                continue
            if semantic["site_kind"] not in operator["allowed_site_kinds"]:
                continue
            identity = _materialize_syntactic_mutant(source_snapshot, semantic, operator)
            key = _syntactic_operator_key(operator, site, identity["patch_sha256"])
            candidates.append((key, identity))
        if not candidates:
            raise EvidenceError("E_PILOT_NO_ELIGIBLE_OPERATOR", semantic["site_id"])
        candidates.sort(key=lambda item: item[0])
        selected.append(candidates[0][1])
    if len(selected) != 4:
        raise EvidenceError("E_PILOT_FREEZE_INCOMPLETE", "need 4 syntactic baselines")
    return selected


def certify_mutant(
    *,
    intent: Mapping[str, Any],
    freeze: Mapping[str, Any],
    receipts: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    validate_exact_object(intent, PILOT_CERTIFICATION_INTENT_EXACT, "pilot_certification_intent")
    intent_body = {key: value for key, value in intent.items() if key != "artifact_sha256"}
    if intent["artifact_sha256"] != canonical_sha256(intent_body):
        raise EvidenceError("E_PILOT_OUTPUT_DRIFT", "certification intent artifact_sha256 mismatch")
    required = (
        "patch_scope",
        "build_and_execution",
        "public_interface",
        "activation",
        "original_contract",
        "mutant_contract",
        "stability",
        "non_equivalence_witness",
        "uniqueness",
    )
    evidence = _derive_certification_gates(intent, freeze, receipts)
    if set(evidence) != set(required):
        raise EvidenceError("E_PILOT_CERT_INCOMPLETE", "nine-gate evidence missing")
    if "witness_policy" in intent or "terminal_state" in intent:
        raise EvidenceError("E_PILOT_FORGED_POLICY", "caller-supplied certification terminals are rejected")
    witness = evidence["non_equivalence_witness"]["witness_sha256"]
    forbidden = set(freeze["pilot_common_input_sha256s"]) | set(freeze["pilot_contract_input_sha256s"]) | set(freeze["mr_evaluation_input_sha256s"])
    if witness in forbidden:
        raise EvidenceError("E_PILOT_WITNESS_COLLISION", "witness equals a published evaluation input")
    if evidence["non_equivalence_witness"].get("mr_kill_outcome") is not None:
        raise EvidenceError("E_PILOT_CERT_READS_MR", "certification must not read MR kill outcomes")
    receipt_hashes = sorted({item["artifact_sha256"] for item in receipts})
    body = {
        "schema_version": "p3-pilot-certification-result-v1",
        "execution_class": "PILOT_ONLY",
        "denominator": "PILOT_ONLY",
        "p12_item_id": freeze["p12_item_id"],
        "neutral_snapshot_id": freeze["neutral_snapshot_id"],
        "normalized_source_tree_sha256": freeze["normalized_source_tree_sha256"],
        "controlled_subject_id": freeze["controlled_subject_id"],
        "controlled_subject_source_id": freeze["controlled_subject_source_id"],
        "predecessor_sha256": sorted(
            {
                intent["artifact_sha256"],
                intent["frozen_contract_sha256"],
                intent["frozen_patch_sha256"],
                intent["mutant_tree_sha256"],
                *receipt_hashes,
            }
        ),
        "job_id": intent["job_id"],
        "run_id": intent["run_id"],
        "attempt": 1,
        "intent_sha256": intent["artifact_sha256"],
        "ended_at": _utc_now(),
        "gates": evidence,
        "terminal_state": _derive_terminal_state(evidence),
        "witness_sha256": witness,
    }
    body["artifact_sha256"] = canonical_sha256(body)
    validate_exact_object(
        body,
        PILOT_CERTIFICATION_RESULT_EXACT,
        "pilot_certification_result",
    )
    return body


def build_evaluation_jobs(
    freeze: Mapping[str, Any],
    mutants: Sequence[Mapping[str, Any]],
    mrs: Sequence[Mapping[str, Any]],
    common_inputs: Sequence[Mapping[str, Any]],
    contract_inputs_by_mutant: Mapping[str, Sequence[Mapping[str, Any]]],
) -> dict[str, list[dict[str, Any]]]:
    if "authorization_b_sha256" in freeze or "job_argv" in freeze or "source_manifest" in freeze:
        raise EvidenceError("E_PILOT_FREEZE_IMPLICIT_FIELD", "freeze must not carry auth B or implicit job fields")
    primary: list[dict[str, Any]] = []
    sensitivity: list[dict[str, Any]] = []
    for mutant in mutants:
        mutant_id = _mutant_id(mutant)
        for mr in mrs:
            for row in common_inputs:
                primary.append(_evaluation_job(freeze, mutant, mr, row, "PILOT_COMMON"))
            inherited = contract_inputs_by_mutant[mutant_id]
            if len(inherited) != 5:
                raise EvidenceError("E_PILOT_FREEZE_INCOMPLETE", "each mutant binds exactly 5 PILOT_CONTRACT inputs")
            for row in inherited:
                sensitivity.append(
                    _evaluation_job(
                        freeze,
                        mutant,
                        mr,
                        row,
                        "PILOT_CONTRACT",
                    )
                )
    primary.sort(key=lambda item: item["job_id"])
    sensitivity.sort(key=lambda item: item["job_id"])
    if len(primary) != 8 * 2 * 30:
        raise EvidenceError("E_PILOT_FREEZE_INCOMPLETE", "primary_planned_count must be 480")
    if len(sensitivity) != 8 * 2 * 5:
        raise EvidenceError("E_PILOT_FREEZE_INCOMPLETE", "sensitivity_planned_count must be 80")
    return {
        "primary": primary,
        "sensitivity": sensitivity,
        "primary_planned_count": 480,
        "sensitivity_planned_count": 80,
        "evaluation_planned_count": 560,
    }


def _evaluation_job(
    freeze: Mapping[str, Any],
    mutant: Mapping[str, Any],
    mr: Mapping[str, Any],
    row: Mapping[str, Any],
    input_class: str,
) -> dict[str, Any]:
    job_kind = "PRIMARY_EVALUATION" if input_class == "PILOT_COMMON" else "SENSITIVITY_EVALUATION"
    mutant_id = _mutant_id(mutant)
    argv = _rebuild_argv(
        command_template_sha256=freeze["command_template_sha256"],
        job_kind=job_kind,
        tree_sha256=mutant["mutant_tree_sha256"],
        input_sha256=row["input_sha256"],
        evaluation_mr_sha256=mr["artifact_sha256"],
        timeout_seconds=freeze["timeout_policy"]["mutant_evaluation"],
    )
    original_job_id = _job_id(
        "ORIGINAL_EVALUATION",
        mr["evaluation_mr_id"],
        row["input_sha256"],
        input_class,
    )
    return {
        "job_id": _job_id(job_kind, mutant_id, mr["evaluation_mr_id"], row["input_sha256"]),
        "job_kind": job_kind,
        "evaluation_input_class": input_class,
        "argv": argv,
        "command_template_sha256": freeze["command_template_sha256"],
        "cwd_identity": _cwd_identity(mutant["mutant_tree_sha256"]),
        "tree_sha256": mutant["mutant_tree_sha256"],
        "timeout_seconds": freeze["timeout_policy"]["mutant_evaluation"],
        "input_sha256": row["input_sha256"],
        "evaluation_mr_sha256": mr["artifact_sha256"],
        "mutant_id": mutant_id,
        "dependency_job_ids": sorted(
            {
                original_job_id,
                *_required_build_job_ids(freeze, mutant_id),
                *_required_certification_job_ids(freeze, mutant_id),
            }
        ),
        "predecessor_sha256": sorted(
            {
                freeze["source_manifest_sha256"],
                freeze["command_template_sha256"],
                mutant["artifact_sha256"],
                mr["artifact_sha256"],
                row["input_sha256"],
            }
        ),
    }


def build_original_execution_jobs(
    freeze: Mapping[str, Any],
    mrs: Sequence[Mapping[str, Any]],
    common_inputs: Sequence[Mapping[str, Any]],
    contract_inputs_by_contract: Mapping[str, Sequence[Mapping[str, Any]]],
) -> list[dict[str, Any]]:
    jobs: list[dict[str, Any]] = []
    for mr in mrs:
        for row in common_inputs:
            jobs.append(_original_execution_job(freeze, mr, row, "PILOT_COMMON"))
        for rows in contract_inputs_by_contract.values():
            if len(rows) != 5:
                raise EvidenceError("E_PILOT_FREEZE_INCOMPLETE", "each contract binds exactly 5 PILOT_CONTRACT inputs")
            for row in rows:
                jobs.append(_original_execution_job(freeze, mr, row, "PILOT_CONTRACT"))
    jobs.sort(key=lambda item: item["job_id"])
    if len(jobs) != 80:
        raise EvidenceError("E_PILOT_FREEZE_INCOMPLETE", "original_execution_planned_count must be 80")
    return jobs


def _original_execution_job(
    freeze: Mapping[str, Any],
    mr: Mapping[str, Any],
    row: Mapping[str, Any],
    input_class: str,
) -> dict[str, Any]:
    argv = _rebuild_argv(
        command_template_sha256=freeze["command_template_sha256"],
        job_kind="ORIGINAL_EVALUATION",
        tree_sha256=freeze["normalized_source_tree_sha256"],
        input_sha256=row["input_sha256"],
        evaluation_mr_sha256=mr["artifact_sha256"],
        timeout_seconds=freeze["timeout_policy"]["mutant_evaluation"],
    )
    return {
        "job_id": _job_id("ORIGINAL_EVALUATION", mr["evaluation_mr_id"], row["input_sha256"], input_class),
        "job_kind": "ORIGINAL_EVALUATION",
        "evaluation_input_class": input_class,
        "argv": argv,
        "command_template_sha256": freeze["command_template_sha256"],
        "cwd_identity": _cwd_identity(freeze["normalized_source_tree_sha256"]),
        "tree_sha256": freeze["normalized_source_tree_sha256"],
        "timeout_seconds": freeze["timeout_policy"]["mutant_evaluation"],
        "input_sha256": row["input_sha256"],
        "evaluation_mr_sha256": mr["artifact_sha256"],
        "mutant_id": None,
        "dependency_job_ids": _required_build_job_ids(freeze, None),
        "predecessor_sha256": sorted(
            {
                freeze["source_manifest_sha256"],
                freeze["command_template_sha256"],
                mr["artifact_sha256"],
                row["input_sha256"],
            }
        ),
    }
```

Certification records the nine gates from immutable receipts: patch scope, build and execution, public-interface preservation, activation, original contract, mutant contract, stability, non-equivalence witness, and uniqueness. Terminal states are exactly `CONFIRMED_NON_EQUIVALENT`, `CERTIFIED_EQUIVALENT`, `EQUIVALENCE_UNRESOLVED`, `TRIGGER_UNEXERCISED`, `INVALID_MUTANT`, `DUPLICATE_MUTANT`, and `INFRASTRUCTURE_UNRESOLVED`. The witness is the first qualifying identity from the frozen certification domain under the published total order. Caller-supplied `witness_policy` terminals and forged result bodies are rejected.

`certification_witness_sha256` must not equal any `PILOT_COMMON`, `PILOT_CONTRACT`, or MR evaluation input SHA-256. Only `CONFIRMED_NON_EQUIVALENT` may enter a strict kill-rate description. Every other object remains in the complete funnel and must not be replaced.

States `PATCH_FROZEN` and `CERTIFICATION_WITNESS_SELECTED` are recorded as `gate_id` values on the semantic-patch and certification-policy artifacts.

## Execution and Kill Oracle

`run_pilot_command` accepts only a `job_id` that equals one item in `execution-plan.json` `jobs`. It must refuse prefix matching, including `job-mutant-build-`. It must reconstruct argv from the inventory item or from the frozen `command_template_sha256` plus that item's complete rebuild fields. It must not read `freeze["job_argv"]` or `freeze["source_manifest"]`. An unknown `job_id` or argv mismatch is `E_PILOT_ORACLE`.

Primary evaluation uses only `PILOT_COMMON`. Sensitivity evaluation uses only `PILOT_CONTRACT`. `PILOT_CONTRACT` rows must not enter primary aggregation. Every evaluation row carries `evaluation_input_class`.

Both semantic and syntactic mutants enter the complete certification funnel. Certification jobs form an independent inventory of 8. The certifier input set is frozen contract, patch, and tree identities plus actual execution receipts. Witnesses are the first qualifying identity from the frozen certification domain under the published total order. A witness must not equal any `PILOT_COMMON`, `PILOT_CONTRACT`, or MR evaluation input. Certification must not read MR kill outcomes. Only a `CONFIRMED_NON_EQUIVALENT` state derived from the nine gates may enter a strict kill-rate description.

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
- write `p3-pilot-not-started-v1` for every not-yet-started job in the complete 659-job inventory, with `failure_reason=GLOBAL_TIMEOUT_NOT_STARTED` or `DEPENDENCY_NOT_STARTED`
- never write `result.json` or `intent_sha256` for a not-started job
- retain every frozen row, started or not
- refuse a receipt that marks a not-started row as `PASS`

Frozen inventory counts:

```text
build_planned_count = 11
certification_planned_count = 8
original_execution_planned_count = 2 * 30 + 2 * 5 * 2 = 80
primary_planned_count = 8 mutants * 2 evaluation_mr_id * 30 PILOT_COMMON = 480
sensitivity_planned_count = 8 mutants * 2 evaluation_mr_id * 5 PILOT_CONTRACT = 80
evaluation_planned_count = 480 + 80 = 560
total_planned_count = 11 + 8 + 80 + 480 + 80 = 659
```

Receipt conservation is required for each category, including original execution, and for the total:

```text
category_started_count + category_not_started_count = category_planned_count
category_terminal_count = category_started_count + category_not_started_count
total_started_count + total_not_started_count = 659
total_terminal_count = 659
```

`started_count` counts only written intents. `not_started_count` counts only not-started dispositions. `terminal_count` equals valid results plus valid not-started dispositions. A mismatch is `E_PILOT_OUTPUT_DRIFT`. Global timeout writes `GLOBAL_TIMEOUT_NOT_STARTED` for every unstarted job in the 659-item inventory, including build, certification, original, primary, and sensitivity jobs. After a started intent, a disappeared process may be reconciled to `ORPHANED_INTENT_NO_PROCESS` without launching a command and without retry. Timeout writes result `TIMEOUT`. Existing intent forbids retry of the same `run_id`/`job_id`.

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
- `test_intent_and_result_schemas_are_distinct`
- `test_intent_rejects_forged_terminal_fields`
- `test_raw_bytes_never_enter_canonical_sha256`
- `test_patch_json_is_serializable`
- `test_patch_replays_to_source_snapshot_tree_hash`
- `test_exact_job_keys_match_producer`
- `test_composite_order_not_in_durable_artifact`
- `test_execution_plan_self_hash_and_source_manifest_binding`

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

Production archive reading must use one opened file descriptor for identity, hash, and buffering:

```python
import os


def read_production_archive_bytes(archive_path: str) -> bytes:
    fd = os.open(archive_path, os.O_RDONLY)
    try:
        before = os.fstat(fd)
        chunks: list[bytes] = []
        while True:
            chunk = os.read(fd, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        after = os.fstat(fd)
        if (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) != (
            after.st_dev,
            after.st_ino,
            after.st_size,
            after.st_mtime_ns,
        ):
            raise EvidenceError("E_PILOT_EXTRACT_UNSAFE", "archive identity changed during read")
        data = b"".join(chunks)
        if len(data) != before.st_size:
            raise EvidenceError("E_PILOT_EXTRACT_UNSAFE", "archive size changed during read")
        return data
    finally:
        os.close(fd)
```

`extract_public_archive` consumes only those already verified immutable bytes. Hashing a path and then reopening that path for unpack is `E_PILOT_EXTRACT_UNSAFE`. Fixture digest injection must not enter this production seam.

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
- archive bytes whose `raw_sha256` differs from `expected_archive_sha256`

PASS requires the conjunction of archive SHA-256, archive bytes, normalized tree SHA-256 `93a62859d7fdd6b2068e494bbe6e3e27180b874cbd27055ac27f941e507a90d8`, build descriptor SHA-256 `68d2e0fd34b845bb0df22b29003f26259d5655d2ec80c18895ff36904db2d95d`, neutral snapshot `74cdc825c3c728c25f5ea857af1565350515a4e631fb0a874c26e810ec437886`, controlled subject identity `89b0e6791c611b465b9216e833e0c526a53ffd6946b5cd20de045e3641f43914`, and authorization A SHA-256. File count, directory names, and declaration counts are not sufficient.

Fixture tests may inject a digest only inside test helpers. The production `G2_SOURCE_AND_FREEZE` seam `validate_boostmath_source_identity` must hard-code the production identities above, call `read_production_archive_bytes`, and persist the real receipt. A monkeypatched expected digest is not production-binding evidence.

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
env PYTHONPATH=src python3 -m pytest tests/p3_v3/test_pilot_extract.py tests/p3_v3/test_pilot.py::test_source_identity_rejects_wrong_tree tests/p3_v3/test_pilot.py::test_source_manifest_cannot_validate_as_pilot_plan tests/p3_v3/test_pilot.py::test_source_manifest_requires_exact_identity_fields tests/p3_v3/test_pilot_extract.py::test_archive_same_fd_hash_and_buffer tests/p3_v3/test_pilot_extract.py::test_archive_rejects_hash_then_reopen -q
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

Produces: hash-chained freeze artifacts and the assembled `p3-pilot-freeze-v1`. Freeze must include reconstructable patch bodies, `harness_source_sha256`, `command_template_sha256`, `primary_planned_count=480`, `sensitivity_planned_count=80`, and `evaluation_planned_count=560`. Freeze must omit `authorization_b_sha256` and `job_argv`.

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
env PYTHONPATH=src python3 -m pytest tests/p3_v3/test_pilot.py::test_freeze_rejects_count_three_relations tests/p3_v3/test_pilot.py::test_freeze_accepts_exact_244305_fixture tests/p3_v3/test_pilot.py::test_freeze_rejects_reused_contract_identity tests/p3_v3/test_pilot.py::test_mr_builder_rejects_contract_bytes tests/p3_v3/test_pilot.py::test_contract_builder_rejects_mr_bytes tests/p3_v3/test_pilot.py::test_selection_keeps_first_n_total_order tests/p3_v3/test_pilot.py::test_first_n_published_order_is_permutation_invariant tests/p3_v3/test_pilot.py::test_two_plus_two_contract_coverage tests/p3_v3/test_pilot.py::test_syntactic_first_candidate_on_shared_site tests/p3_v3/test_pilot.py::test_freeze_rejects_authorization_b tests/p3_v3/test_pilot.py::test_raw_bytes_never_enter_canonical_sha256 tests/p3_v3/test_pilot.py::test_patch_replays_to_source_snapshot_tree_hash tests/p3_v3/test_pilot.py::test_composite_order_not_in_durable_artifact -q
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

Create: `data/p3_v3/pilot/boost_math/execution-plan.json`, `data/p3_v3/pilot/boost_math/attempts/<job_id>/1/intent.json` and `result.json`, `not-started.json` where required, certification intent/result files, `heartbeat.json`, `checkpoint.json`.

Modify: `src/p3_v3/pilot.py`, `scripts/p3_v3/pilot.py`, `tests/p3_v3/test_pilot.py`.

Consumes: `pilot-freeze.json`, authorization B, validated source-manifest SHA-256, exact build descriptor identity.

Produces: `p3-pilot-execution-plan-v1` after authorization B verification. Each inventory job has exactly one terminal disposition:
(intent.json + result.json) XOR not-started.json.
A job that already has `intent.json` must not write `not-started.json`. A job that never received an intent must not write `result.json`. The not-started `failure_reason` is exactly `GLOBAL_TIMEOUT_NOT_STARTED` or `DEPENDENCY_NOT_STARTED`. Certification jobs that start write `p3-pilot-certification-intent-v1` and `p3-pilot-certification-result-v1`.

```python
def build_execution_plan(
    freeze: Mapping[str, Any],
    authorization_b_path: Path,
    source_manifest_sha256: str,
) -> dict[str, Any]:
    validate_exact_object(freeze, PILOT_FREEZE_EXACT, "pilot_freeze")
    freeze_body = {key: value for key, value in freeze.items() if key != "artifact_sha256"}
    if freeze["artifact_sha256"] != canonical_sha256(freeze_body):
        raise EvidenceError("E_PILOT_OUTPUT_DRIFT", "freeze artifact_sha256 mismatch")
    if "authorization_b_sha256" in freeze or "job_argv" in freeze or "source_manifest" in freeze:
        raise EvidenceError("E_PILOT_CHRONOLOGY", "freeze must not contain authorization B or implicit fields")
    auth_bytes = authorization_b_path.read_bytes()
    if auth_bytes != b"AUTHORIZE_BOOSTMATH_PILOT_EXECUTION\n":
        raise EvidenceError("E_PILOT_ORACLE", "authorization B bytes differ")
    authorization_b_sha256 = raw_sha256(auth_bytes)
    if authorization_b_sha256 != file_sha256(authorization_b_path):
        raise EvidenceError("E_PILOT_ORACLE", "authorization B hash mismatch")
    if source_manifest_sha256 != freeze["source_manifest_sha256"]:
        raise EvidenceError("E_PILOT_SOURCE_IDENTITY", "source_manifest_sha256 differs from freeze binding")
    inventories = _build_complete_inventories(freeze)
    jobs = (
        inventories["build_jobs"]
        + inventories["certification_jobs"]
        + inventories["original_execution_jobs"]
        + inventories["primary_jobs"]
        + inventories["sensitivity_jobs"]
    )
    if (
        len(inventories["build_jobs"]) != 11
        or len(inventories["certification_jobs"]) != 8
        or len(inventories["original_execution_jobs"]) != 80
        or len(inventories["primary_jobs"]) != 480
        or len(inventories["sensitivity_jobs"]) != 80
        or len(jobs) != 659
    ):
        raise EvidenceError("E_PILOT_FREEZE_INCOMPLETE", "execution-plan inventory counts differ")
    body = {
        "schema_version": "p3-pilot-execution-plan-v1",
        "execution_class": "PILOT_ONLY",
        "denominator": "PILOT_ONLY",
        "p12_item_id": freeze["p12_item_id"],
        "neutral_snapshot_id": freeze["neutral_snapshot_id"],
        "normalized_source_tree_sha256": freeze["normalized_source_tree_sha256"],
        "controlled_subject_id": freeze["controlled_subject_id"],
        "controlled_subject_source_id": freeze["controlled_subject_source_id"],
        "predecessor_sha256": sorted(
            {
                freeze["artifact_sha256"],
                source_manifest_sha256,
                authorization_b_sha256,
            }
        ),
        "execution_plan_id": canonical_sha256(
            {
                "freeze_sha256": freeze["artifact_sha256"],
                "authorization_b_sha256": authorization_b_sha256,
            }
        ),
        "gate_id": "G3_EXECUTION",
        "freeze_sha256": freeze["artifact_sha256"],
        "source_manifest_sha256": source_manifest_sha256,
        "authorization_b_sha256": authorization_b_sha256,
        "jobs": jobs,
        "build_jobs": inventories["build_jobs"],
        "certification_jobs": inventories["certification_jobs"],
        "original_execution_jobs": inventories["original_execution_jobs"],
        "primary_jobs": inventories["primary_jobs"],
        "sensitivity_jobs": inventories["sensitivity_jobs"],
        "primary_planned_count": 480,
        "sensitivity_planned_count": 80,
        "evaluation_planned_count": 560,
        "certification_planned_count": 8,
        "build_planned_count": 11,
        "original_execution_planned_count": 80,
        "total_planned_count": 659,
    }
    body["artifact_sha256"] = canonical_sha256(body)
    validate_exact_object(
        body,
        PILOT_EXECUTION_PLAN_EXACT,
        "pilot_execution_plan",
    )
    return body


def run_pilot_command(intent: Mapping[str, Any], execution_plan: Mapping[str, Any]) -> dict[str, Any]:
    inventory = {job["job_id"]: job for job in execution_plan["jobs"]}
    if intent["job_id"] not in inventory:
        raise EvidenceError("E_PILOT_ORACLE", "job_id is not in the exact execution-plan inventory")
    job = inventory[intent["job_id"]]
    if intent["argv"] != job["argv"]:
        raise EvidenceError("E_PILOT_ORACLE", "argv differs from execution-plan inventory")
    return _execute_isolated(intent, job)


def reconcile_orphaned_intent(intent: Mapping[str, Any], process_absent: bool) -> dict[str, Any]:
    validate_exact_object(intent, PILOT_INTENT_EXACT, "pilot_intent")
    intent_body = {key: value for key, value in intent.items() if key != "artifact_sha256"}
    if intent["artifact_sha256"] != canonical_sha256(intent_body):
        raise EvidenceError("E_PILOT_OUTPUT_DRIFT", "intent artifact_sha256 mismatch")
    if not process_absent:
        raise EvidenceError("E_PILOT_ORPHAN_UNRESOLVED", "old process cannot be proved absent")
    body = {
        "schema_version": "p3-pilot-result-v1",
        "execution_class": "PILOT_ONLY",
        "denominator": "PILOT_ONLY",
        "p12_item_id": intent["p12_item_id"],
        "neutral_snapshot_id": intent["neutral_snapshot_id"],
        "normalized_source_tree_sha256": intent["normalized_source_tree_sha256"],
        "controlled_subject_id": intent["controlled_subject_id"],
        "controlled_subject_source_id": intent["controlled_subject_source_id"],
        "predecessor_sha256": sorted({intent["artifact_sha256"]}),
        "job_id": intent["job_id"],
        "run_id": intent["run_id"],
        "attempt": 1,
        "intent_sha256": intent["artifact_sha256"],
        "ended_at": _utc_now(),
        "exit_code": None,
        "stdout_sha256": None,
        "stderr_sha256": None,
        "terminal_status": "FAIL_INFRASTRUCTURE",
        "failure_reason": "ORPHANED_INTENT_NO_PROCESS",
        "wall_seconds": None,
        "cpu_seconds": None,
        "peak_rss_bytes": None,
    }
    body["artifact_sha256"] = canonical_sha256(body)
    validate_exact_object(body, PILOT_RESULT_EXACT, "pilot_result")
    return body
```

`_execute_isolated` must materialize the bound tree into a root named by that tree SHA-256, launch `argv` with `shell=False`, enforce `timeout_seconds`, hash stdout and stderr, record `wall_seconds`, `cpu_seconds`, and `peak_rss_bytes`, write a heartbeat at least every 30 seconds, write intent before launch, write result after termination bound to `intent_sha256`, and refuse a second call when `intent.json` already exists for that `run_id`/`job_id`. `reconcile_orphaned_intent` must not call `_execute_isolated` and must not start a process.

CUDA missing is ignored. CMake extra flags must not add `-DCMAKE_CUDA_COMPILER` as a required cache entry.

CLI:

```text
env PYTHONPATH=src python3 scripts/p3_v3/pilot.py plan-execution \
  --freeze data/p3_v3/pilot/boost_math/pilot-freeze.json \
  --authorization data/p3_v3/pilot/boost_math/user-auth-execution.txt \
  --output data/p3_v3/pilot/boost_math/execution-plan.json
env PYTHONPATH=src python3 scripts/p3_v3/pilot.py execute \
  --execution-plan data/p3_v3/pilot/boost_math/execution-plan.json \
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
env PYTHONPATH=src python3 -m pytest tests/p3_v3/test_pilot.py::test_execute_rejects_missing_authorization_b tests/p3_v3/test_pilot.py::test_execute_rejects_unknown_argv tests/p3_v3/test_pilot.py::test_execute_records_timeout_without_retry tests/p3_v3/test_pilot.py::test_execute_rejects_second_run_id tests/p3_v3/test_pilot.py::test_kill_requires_original_satisfy_and_mutant_violate tests/p3_v3/test_pilot.py::test_global_timeout_marks_not_started tests/p3_v3/test_pilot.py::test_run_pilot_command_rejects_prefix_job_id tests/p3_v3/test_pilot.py::test_execution_plan_requires_exact_job_inventory tests/p3_v3/test_pilot.py::test_primary_count_480 tests/p3_v3/test_pilot.py::test_sensitivity_count_80 tests/p3_v3/test_pilot.py::test_evaluation_count_560 tests/p3_v3/test_pilot.py::test_original_count_80 tests/p3_v3/test_pilot.py::test_total_count_659 tests/p3_v3/test_pilot.py::test_mutant_jobs_bind_original_dependency tests/p3_v3/test_pilot.py::test_not_started_does_not_require_intent tests/p3_v3/test_pilot.py::test_orphan_reconciliation_does_not_launch tests/p3_v3/test_pilot.py::test_pilot_contract_excluded_from_primary tests/p3_v3/test_pilot.py::test_certify_rejects_forged_policy tests/p3_v3/test_pilot.py::test_certify_rejects_forged_result tests/p3_v3/test_pilot.py::test_certify_derives_terminal_from_receipts_only tests/p3_v3/test_pilot.py::test_certification_schema_is_result_v1 tests/p3_v3/test_pilot.py::test_exact_job_keys_match_producer tests/p3_v3/test_pilot.py::test_execution_plan_self_hash_and_source_manifest_binding -q
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

Independent stop: all frozen jobs have exactly one terminal disposition, either `(intent.json + result.json)` or `not-started.json` with `GLOBAL_TIMEOUT_NOT_STARTED` or `DEPENDENCY_NOT_STARTED`. Do not open the claim ledger. Do not enter Task 5 automatically.

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
stopping_rule: "first terminal result per run_id; full-pilot wall 14400 seconds; GLOBAL_TIMEOUT_NOT_STARTED or DEPENDENCY_NOT_STARTED for unstarted rows"
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

Receipt conservation: build, certification, original-execution, primary, sensitivity, and total counters must each satisfy started + not_started = planned and terminal = planned. Primary planned is 480. Sensitivity planned is 80. Evaluation planned is 560. Original planned is 80. Total planned is 659. A not-started row cannot be `PASS` and cannot bind a forged `intent_sha256`. Receipt closure accepts both `GLOBAL_TIMEOUT_NOT_STARTED` and `DEPENDENCY_NOT_STARTED`. `claims_status` is `blocked`. `rq4_supported` is `false`. `formal_denominator_membership` is `false`.

CLI:

```text
env PYTHONPATH=src python3 scripts/p3_v3/pilot.py close \
  --freeze data/p3_v3/pilot/boost_math/pilot-freeze.json \
  --execution-plan data/p3_v3/pilot/boost_math/execution-plan.json \
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

- The named schemas validate, and unknown `p3-pilot-` schemas are rejected
- Confirmatory `build-package`, `verify-package`, `verify-run-records`, `close-phase`, `verify-evidence`, `freeze-authority-lock`, and `run-preflight` reject pilot objects with `E_PILOT_DENOMINATOR_LEAK` or `E_PILOT_PACKAGE_CLASS`
- Source identity binds archive SHA-256, archive bytes, normalized tree, build descriptor, snapshot, controlled subject identity, and authorization A
- Freeze cardinality is 2/4/4/30/5 with paired mutants, distinct contract-group identities, two independent evaluation MRs, reconstructable patches, and no authorization B
- Construction and MR chains are hash-chained and mutually unread
- Selection uses the published total orders, 2+2 coverage, and permutation-invariant first-N
- Task 4 writes `execution-plan.json` only after authorization B and binds the exact 659-job inventory
- Two user authorization files were hashed into the relevant artifacts
- Timeouts are the frozen integers; every unstarted execution-plan job receives `p3-pilot-not-started-v1`
- Build=11, certification=8, original=80, primary=480, sensitivity=80, evaluation=560, and total=659 counters conserve
- `score-task.yml` and `experiment-ledger.yml` exist and the receipt says `claims_status=blocked`, `rq4_supported=false`, and `formal_denominator_membership=false`
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
