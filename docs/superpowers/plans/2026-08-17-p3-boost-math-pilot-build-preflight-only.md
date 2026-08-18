# Boost.Math PILOT Build-Preflight-Only Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. This document authorizes only the single future build-preflight capability task below. After that task, stop for independent implementation review. Do not start production build-preflight. Do not create the build-preflight Authorization. Do not create a plan verdict or implementation verdict. Do not run CMake, CTest, or a compiler against the frozen Boost.Math source object.

**Goal:** Define one later capability that can, after an independent plan verdict, an independent implementation verdict, and a later exact user Authorization, attempt one consumer-harness CMAKE_CONFIGURE then BASELINE_BUILD then BASELINE_SMOKE sequence against the already prepared Boost.Math source object. This planning node writes the plan only. The later capability task uses runtime-generated synthetic CMake fixtures. It does not configure, compile, or execute real Boost.Math.

**Architecture:** Keep confirmatory `p3-v3-*` schemas unchanged. Add `src/p3_v3/pilot_build.py` as the only new production module. Formal plan-verdict archival must precede capability implementation. Formal implementation-verdict archival must precede Authorization and production execution. Production `run_build_preflight` then binds the frozen source-preparation identities, exclusive-creates one intent, writes one frozen consumer harness outside the source root, and runs exactly three jobs. Capability PASS still does not authorize real Boost.Math build-preflight.

**Tech Stack:** Python 3.11 or newer, existing `src/p3_v3/artifacts.py` exact-object helpers including `read_regular_file_snapshot` and `write_canonical_json`, existing `capture_materialized_tree` and `validate_materialized_tree_with_phase1` from `src/p3_v3/pilot_source.py`, CMake as the only consumer build tool, pytest with `PYTHONPATH=src`. Cursor VM has no `rtk`. Later implementation uses bare `python3`, `pytest`, `sha256sum`, `wc`, and `git`.

## Global Constraints

- Plan class is `PILOT_BUILD_PREFLIGHT_ONLY`.
- This document has exactly one future implementation task.
- This planning node does not run pytest, CMake, CTest, or a compiler.
- After this document is written, the requested review state is `PILOT_BUILD_PREFLIGHT_PLAN_REVIEW_CANDIDATE`. This document is not an independent PASS.
- Formal source-preparation state remains `PILOT_SOURCE_PREPARATION_PASS`.
- The later capability task uses only runtime-generated synthetic CMake fixtures.
- The later capability task does not read, configure, compile, or execute real Boost.Math.
- The later capability task does not create `data/p3_v3/pilot/boost_math/user-auth-build-preflight.txt`, `data/p3_v3/pilot/boost_math/build-preflight-intent.json`, or `data/p3_v3/pilot/boost_math/build-preflight-result.json`.
- After the later capability task, stop at an independent Sol High implementation review.
- Capability implementation PASS still does not authorize production build-preflight.
- Only a later exact Authorization may run one production attempt.
- `claims=blocked`.
- Formal denominator membership is false.
- `rq4_supported=false`.
- The complete plan `docs/superpowers/plans/2026-08-15-p3-boost-math-pilot-only.md` remains unfrozen and is not execution authority.
- This document contains no mutant, MR, certification, execution, profiling, or full-pilot implementation task.
- This planning node does not create Authorization or any reserved verdict file.
- The later capability task does not create Authorization or any reserved verdict file.
- `execution_class = PILOT_ONLY` and `denominator = PILOT_ONLY` on every durable pilot object defined here.
- `planned_count` is exactly 3. This stage does not inherit `build_planned_count=11` and does not count toward the complete 659-job inventory.
- PASS can support consumer-harness build readiness only. PASS is not a Boost.Math full-project build.
- CUDA absence is not a blocker.
- Native profiling is not a prerequisite.
- Timeout is terminal. There is no automatic rerun.

---

## Unique Successor DAG

This stage does not replay the source-preparation launch-packet / launch-verdict / machine-authority chain. The only successor order is:

```text
frozen plan
-> independent plan review
-> formal plan verdict archival
-> capability implementation
-> independent implementation review
-> formal implementation verdict archival
-> exact user Authorization
-> one production attempt
-> independent result review
```

Formal plan verdict archival must precede capability implementation. An unfrozen plan must not be implemented. Formal implementation verdict archival must precede Authorization and production execution.

Fail-closed rule: if the plan verdict, implementation verdict, Authorization, source-preparation PASS identities, or frozen tree identity is absent, has the wrong SHA-256, is not PASS, or fails exact-schema validation, `run_build_preflight` must raise and must write no intent, no result, no harness root, and no build root.

---

## Frozen Authority Identities

These files are identity-checked only. This plan does not modify them.

| Object | SHA-256 |
|---|---|
| Phase 1 final review `docs/review_20260815/phase1_sol_high_final_review.md` | `95345c4229e8e3dedd21e3f7da022fc5daeceb1018392dc1d0e3e35b00fa5a7d` |
| scientific charter `docs/superpowers/plans/2026-08-12-p3-return-to-scientific-critical-path.md` | `bd9234e3a26557e0036e42415528f983f2c18313295352ddffb4ccc076c1d5e4` |
| governing scientific plan `docs/superpowers/plans/2026-08-08-p3-semantic-mutant-argumentation-experiment.md` | `fea00496801c31ba074aa74742f5e6a77019ffc2e344642122a15462d7443830` |
| protocol `data/p3_v3/protocol/protocol.json` | `240d8270d41802c9d5b86f30564eadd1a86fd9ed09de2c7e947d17c1a4d78519` |
| environment lock `data/p3_v3/protocol/environment_lock.json` | `7706b4ce272d09df13c5212b04ec0f2519932f4225d5eac0d052d3225c7ff35f` |
| claim ceiling `data/p3_v3/protocol/claim_ceiling_authority.json` | `1f46b7cd97e6ddf6d65f6c52a552f4e4b6680a987a088d4f5a65ebc19bf017ed` |
| claim ledger `research/evidence/p3_claim_ledger_v1.3.0.yml` | `bf4979662697b2d0565bb70eec88b22673e84bee93b61234555342efb4082a68` |
| Phase 1 receipts `data/p3_v3/phase1_frames/receipts.json` | `8eeccfe4d1aebb09e6ee9ad2fadb82ac5b8697c40f602592faa6b3878692a440` |
| Pass-1 baseline manifest `data/p3_v3/phase1_frames/pass1_baseline_manifest.json` | `b0be90ded75a4242bf883698d2b8c3f0c55d70b1b0928d7068bc1a3797e4eb11` |
| source manifest file `data/p3_v3/pilot/boost_math/source-manifest.json` | `d774143f6a0dc6cf24a9ddda8b4e9760b3d547e03cbd21e16d84220f826073c5` |
| source-preparation result file `data/p3_v3/pilot/boost_math/source-preparation-result.json` | `6a525ff074f5ab67f4a58af0a4f7f2264f3888757513a8fc80fb6760c8b577b9` |
| source-preparation result verdict `docs/review_20260817/boost_math_pilot_source_preparation_result_sol_high_review.md` | `43cedfd21621496f61feec1418b2ec4d9e02b51096c477b0d221067d1e1ed7f2` |
| source-preparation reviewed commit | `44acee8882b004f50005cd39ca732bc6f09604fa` |
| normalized/materialized tree | `93a62859d7fdd6b2068e494bbe6e3e27180b874cbd27055ac27f941e507a90d8` |
| build descriptor | `68d2e0fd34b845bb0df22b29003f26259d5655d2ec80c18895ff36904db2d95d` |
| neutral snapshot | `74cdc825c3c728c25f5ea857af1565350515a4e631fb0a874c26e810ec437886` |
| controlled subject | `89b0e6791c611b465b9216e833e0c526a53ffd6946b5cd20de045e3641f43914` |
| controlled subject source | `e5f21a7d067d641d0a20bfc57c61e630d6f7588ef30235cea49c9a9cf950c7a7` |
| complete 2026-08-15 pilot plan `docs/superpowers/plans/2026-08-15-p3-boost-math-pilot-only.md` | `1612a6ee81773c7db97625ae3497fab31b93ad70f2ecaefce2fdd845bda73cca` |

The complete 2026-08-15 pilot plan remains an unfrozen candidate. It is readable design history only. It is not execution authority for this stage. In particular `build_planned_count=11` is not inherited.

---

## Read-Only Source Inspection

Before any source-file read, this planning node called `capture_materialized_tree` and `validate_materialized_tree_with_phase1` on `/tmp/p3-boost-math-pilot-production-source`.

Observed:

```text
tree SHA-256 = 93a62859d7fdd6b2068e494bbe6e3e27180b874cbd27055ac27f941e507a90d8
file count = 4396
total bytes = 95635487
```

No CMake, CTest, compiler, or source-defined executable was run. The source root was not written. Package C, P12 reveal, buggy revisions, patches, MR, and outcomes were not read.

Adopted public consumer-interface files, with SHA-256 of the exact bytes in the frozen tree:

| Source-relative path | SHA-256 | Why adopted |
|---|---|---|
| `CMakeLists.txt` | `eae9729bfcc3cb4ba5d21921a040a06ee0975b029e8d976fb55cd60322111fae` | Declares `add_library(boost_math INTERFACE)`, `target_include_directories(boost_math INTERFACE include)`, and `cmake_dependent_option(BOOST_MATH_STANDALONE "Use Boost.Math in standalone mode" ON "NOT BOOST_SUPERPROJECT_VERSION" OFF)`. When this file is the root project it also `include(CTest)` and `add_subdirectory(test)`. That full-project path is not used. |
| `README.md` | `9a8b2fd7ccc0ef9f08cbd6384ac3b1ebc2a25b695df72e63ad426bcc13407f4d` | Standalone Mode section states that defining `BOOST_MATH_STANDALONE` allows Boost.Math to be used without other Boost dependencies. |
| `include/boost/math/tools/is_standalone.hpp` | `83a9b1e4f131596ec61ff4de801ab917e89c1e2aa8f0f974d01d1ed6a9cb753f` | Auto-defines `BOOST_MATH_STANDALONE` when sibling Boost headers are absent. Production still forces `-DBOOST_MATH_STANDALONE=1` so `__has_include` of an unbound system Boost cannot silently disable standalone mode. |
| `include/boost/math/tools/config.hpp` | `8848794f913847071f46358548b63cc288281702efd0c1bcbaf785341f325ce5` | Gates non-standalone Boost dependencies behind `#ifndef BOOST_MATH_STANDALONE`. |
| `include/boost/math/constants/constants.hpp` | `06f55b132b6cb337ba298851b94cc92bc54209d90d29debdf39ae748aa19c2a7` | Public header-only constants API. Includes only `boost/math/*` headers plus the C++ standard library. Defines `boost::math::constants::pi`. |
| `example/CMakeLists.txt` | `56a2c06eca3591cfb545751ebafcb0101699f51d62ae50943c0e7fffa835d688` | Shows a consumer include of `${CMAKE_SOURCE_DIR}/include`. The example glob itself is not used. |

There is no `cmake/` directory in the frozen tree. `rg` of the top-level `CMakeLists.txt` found `project(`, `add_library(`, `target_include_directories(`, `cmake_dependent_option(`, and non-standalone `target_link_libraries` to other Boost components. Those other Boost components are not in this source object. The consumer harness therefore must stay in standalone mode and must not configure the Boost.Math repository as the CMake root.

`/usr/include/boost` was observed absent on the planning host. Absence is not acceptance. Production must still refuse unbound system Boost if it appears later.

This source evidence is sufficient for a minimal standalone consumer harness that includes only the frozen `include/` directory. It is not sufficient to claim a Boost.Math full-project build.

---

## Consumer Harness Boundary

The harness is a CMake consumer. It is not the Boost.Math repository build.

Harness rules:

- Write only to the frozen harness root. Never write the source root.
- Include only `/tmp/p3-boost-math-pilot-production-source/include`.
- Compile one fixed C++ executable named `boost_math_pilot_smoke`.
- Execute one public-behavior smoke: `boost::math::constants::pi<double>()` is in `(3.14, 3.15)`.
- Success is process exit 0.
- No mutant, MR, construction contract, or evaluation input.
- The candidate relations `erf(x) + erfc(x) ≈ 1` and `erf(-x) ≈ -erf(x)` are forbidden in harness bytes, tests, and production code.
- The smoke predicate is not a mutation oracle and is not a paper hypothesis.
- No network, random number, clock, or external input.

PASS of the three jobs supports consumer-harness build readiness only. It does not mean:

- complete Boost.Math build
- CTest suite PASS
- source profiling
- mutant compile success
- MR validity
- formal denominator membership
- RQ4 support
- paper Results or Contributions

If a later production host cannot compile this harness without mixing unbound Boost headers, the attempt must stop with `terminal_status = FAIL_INFRASTRUCTURE` and `failure_reason = MISSING_DEPENDENCY`. The harness bytes must not change to chase the environment.

Frozen harness `CMakeLists.txt` bytes (SHA-256 `2bdbb40e8d6fbd488ddde7bda4b855047361bedc1e7c4c9a5e72bf971d602a8b`, 1084 bytes, 33 LF, 0 CR):

```cmake
cmake_minimum_required(VERSION 3.5)
project(boost_math_pilot_build_preflight_harness LANGUAGES CXX)

set(BOOST_MATH_PILOT_SOURCE_INCLUDE
    "/tmp/p3-boost-math-pilot-production-source/include"
    CACHE PATH
    "Frozen Boost.Math public include root")

if(NOT BOOST_MATH_PILOT_SOURCE_INCLUDE STREQUAL
    "/tmp/p3-boost-math-pilot-production-source/include")
  message(FATAL_ERROR
    "BOOST_MATH_PILOT_SOURCE_INCLUDE is not the frozen include path")
endif()

if(DEFINED BOOST_ROOT OR DEFINED BOOST_INCLUDEDIR OR DEFINED Boost_INCLUDE_DIR
    OR DEFINED Boost_DIR)
  message(FATAL_ERROR "unbound Boost search variables are forbidden")
endif()

add_executable(boost_math_pilot_smoke smoke.cpp)
target_include_directories(
    boost_math_pilot_smoke
    PRIVATE
    "${BOOST_MATH_PILOT_SOURCE_INCLUDE}")
target_compile_definitions(
    boost_math_pilot_smoke
    PRIVATE
    BOOST_MATH_STANDALONE=1)
target_compile_features(boost_math_pilot_smoke PRIVATE cxx_std_14)
set_target_properties(
    boost_math_pilot_smoke
    PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}")
```

Frozen harness `smoke.cpp` bytes (SHA-256 `609c8990cef0cad5a1e448f11e8353dbc6c040e88778b72fac64ea6a6b4002ed`, 198 bytes, 11 LF, 0 CR):

```cpp
#include <boost/math/constants/constants.hpp>

int main()
{
    const double pi = boost::math::constants::pi<double>();
    if (pi > 3.14 && pi < 3.15)
    {
        return 0;
    }
    return 1;
}
```

---

## Three Production Jobs

Exactly three production jobs, in this unique order:

```text
CMAKE_CONFIGURE
-> BASELINE_BUILD
-> BASELINE_SMOKE
```

`planned_count = 3`.

If `CMAKE_CONFIGURE` is not PASS, then `BASELINE_BUILD` and `BASELINE_SMOKE` are `NOT_STARTED` with `failure_reason = DEPENDENCY_NOT_STARTED`.

If `BASELINE_BUILD` is not PASS, then `BASELINE_SMOKE` is `NOT_STARTED` with `failure_reason = DEPENDENCY_NOT_STARTED`.

Each job has exactly one terminal disposition: `PASS`, `FAIL`, `TIMEOUT`, `FAIL_INFRASTRUCTURE`, or `NOT_STARTED`.

`NOT_STARTED` must not invent process intent, an exit code, or stdout/stderr hashes or byte counts.

Frozen argv arrays:

```text
CMAKE_CONFIGURE =
  cmake
  -S /tmp/p3-boost-math-pilot-build-preflight-harness
  -B /tmp/p3-boost-math-pilot-build-preflight
  -G Unix Makefiles
  -DCMAKE_BUILD_TYPE=Release
  -DCMAKE_CXX_STANDARD=14
  -DCMAKE_CXX_STANDARD_REQUIRED=ON
  -DBOOST_MATH_STANDALONE=1
  -DBOOST_MATH_PILOT_SOURCE_INCLUDE=/tmp/p3-boost-math-pilot-production-source/include
  -DCMAKE_DISABLE_SOURCE_CHANGES=ON
  -DCMAKE_DISABLE_IN_SOURCE_BUILD=ON
  -DFETCHCONTENT_FULLY_DISCONNECTED=ON
  -DFETCHCONTENT_UPDATES_DISCONNECTED=ON
  -DCMAKE_FIND_USE_PACKAGE_REGISTRY=OFF
  -DCMAKE_FIND_USE_SYSTEM_PACKAGE_REGISTRY=OFF
  -DCMAKE_EXPORT_COMPILE_COMMANDS=ON

BASELINE_BUILD =
  cmake
  --build
  /tmp/p3-boost-math-pilot-build-preflight
  --parallel
  4

BASELINE_SMOKE =
  /tmp/p3-boost-math-pilot-build-preflight/boost_math_pilot_smoke
```

Timeouts:

- `CMAKE_CONFIGURE`: 900 seconds
- `BASELINE_BUILD`: 3600 seconds
- `BASELINE_SMOKE`: 1800 seconds
- outer process: 7200 seconds
- build parallelism: 4

Raw logs for every started job are written to:

```text
/tmp/p3-boost-math-pilot-build-preflight/logs/<job_id>.stdout
/tmp/p3-boost-math-pilot-build-preflight/logs/<job_id>.stderr
```

Those log files are independent-review evidence. They are not extra schema keys.

---

## Dependency Provenance

Fail-closed. Production must not:

- download a dependency
- run `git clone`, `git fetch`, or `git submodule`
- use CMake `FetchContent` to download
- use Conan, vcpkg, apt, pip, or brew to install
- mix unbound `/usr/include/boost`
- auto-search and accept an arbitrary system Boost
- modify the source root
- change the harness because a dependency is missing
- fix the environment and automatically rerun

Executable network contract:

- every child environment sets `FETCHCONTENT_FULLY_DISCONNECTED=ON` and `FETCHCONTENT_UPDATES_DISCONNECTED=ON`
- configure argv includes the same two CMake flags
- harness CMakeLists.txt contains no `FetchContent`, `file(DOWNLOAD)`, or `ExternalProject`
- if stdout, stderr, or argv contains `Downloading `, `Cloning into`, `Fetching `, `file(DOWNLOAD`, `-- Fetching`, `Resolving deltas`, `github.com`, `gitlab.com`, `bitbucket.org`, `FetchContent_Declare`, or `ExternalProject_Add`, the job is `FAIL_INFRASTRUCTURE` with `failure_reason = NETWORK_OR_DOWNLOAD_ATTEMPT`
- if `BOOST_ROOT`, `BOOST_INCLUDEDIR`, `Boost_DIR`, `CMAKE_PREFIX_PATH`, `CMAKE_INCLUDE_PATH`, `CPATH`, or `CPLUS_INCLUDE_PATH` names a Boost search path, production stops with `FAIL_INFRASTRUCTURE` / `SYSTEM_BOOST_FALLBACK` and does not unset the variable to continue
- if stdout, stderr, or argv contains `/usr/include/boost` or `/usr/local/include/boost`, the job is `FAIL_INFRASTRUCTURE` with `failure_reason = SYSTEM_BOOST_FALLBACK`

If `cmake` or a C++ compiler is absent, stop with `FAIL_INFRASTRUCTURE` / `MISSING_DEPENDENCY` and `infrastructure_phase=PRE_PROCESS`. Do not install it. Do not change the harness. Do not retry.

PASS of `BASELINE_BUILD` must prove the compiler used the frozen source object. Log-string scans are not enough. The compiler dependency file, `CMakeCache.txt`, `compile_commands.json`, and the smoke executable hashes are bound on the aggregate result. A Boost header outside `/tmp/p3-boost-math-pilot-production-source/include` is `FAIL_INFRASTRUCTURE/SYSTEM_BOOST_FALLBACK`.

---

## Frozen Paths

Future production source root:

```text
/tmp/p3-boost-math-pilot-production-source
```

Future build root:

```text
/tmp/p3-boost-math-pilot-build-preflight
```

Future harness root:

```text
/tmp/p3-boost-math-pilot-build-preflight-harness
```

Future intent:

```text
data/p3_v3/pilot/boost_math/build-preflight-intent.json
```

Future aggregate result:

```text
data/p3_v3/pilot/boost_math/build-preflight-result.json
```

Future Authorization:

```text
data/p3_v3/pilot/boost_math/user-auth-build-preflight.txt
```

CLI may keep `--source-root` and `--build-root`. The production function must require those values to equal the frozen paths. No other path, hash, timeout, job-count, harness, compiler, or argv override is accepted.

Pre-existing build root, harness root, intent, or result is fail-closed. Production must not delete or overwrite them.

All three roots must be safe, non-symlink, and must not escape the frozen `/tmp` paths. The source tree must be re-validated as the frozen tree SHA before the first child and must not drift between jobs.

---

## Authorization

This node does not create the Authorization file.

Exact bytes:

```text
AUTHORIZE_BOOSTMATH_PILOT_BUILD_PREFLIGHT\n
```

Raw bytes are `b"AUTHORIZE_BOOSTMATH_PILOT_BUILD_PREFLIGHT\n"`.

- SHA-256: `2265145a6b73a16e1ae06b3c5b12baa2a842ad7d700e60ed0de67393746cfb15`
- bytes: 42
- LF: 1
- CR: 0

This Authorization, when later created by the user, authorizes only one future build-preflight attempt. It does not authorize mutant, MR, certification, or full-pilot work. It does not authorize dependency download. It does not authorize retry. It does not unblock claims.

---

## Exact Schemas

Every durable object includes `execution_class = PILOT_ONLY`, `denominator = PILOT_ONLY`, `claims = blocked`, and `artifact_sha256` equal to the canonical SHA-256 of the object without that key.

Allowed job `terminal_status` values: `PASS`, `FAIL`, `TIMEOUT`, `FAIL_INFRASTRUCTURE`, `NOT_STARTED`.

The complete key and type maps, validators, constructors, and producers are the Python module in Task 1. They are not omitted here. The schema names are:

1. `p3-pilot-build-preflight-environment-v1`
2. `p3-pilot-build-preflight-intent-v1`
3. `p3-pilot-build-preflight-job-result-v1`
4. `p3-pilot-build-preflight-result-v1`

Intent binds: source-preparation verdict SHA, source manifest SHA, source-preparation result SHA, normalized tree SHA, controlled subject IDs, build descriptor SHA, Authorization hash, exact harness file hashes, exact three argv arrays, exact timeouts, exact dependency DAG, source/build/harness paths, the complete environment snapshot object, `environment_snapshot_sha256`, `implementation_verdict_sha256`, producer pid/starttime, and predecessor hashes that include the implementation-verdict file SHA.

Aggregate result binds: intent file SHA, the three exact job-result objects, source/preparation identities, `implementation_verdict_sha256`, the complete environment snapshot object, CMakeCache / compile_commands / dependency-list / smoke-executable hashes, terminal aggregate status, build-root identity/evidence, `no_retry=true`, `formal_denominator_membership=false`, `rq4_supported=false`, and `claims=blocked`.

Job result binds: `job_id`, `job_kind`, `dependency_job_ids`, `argv`, `timeout_seconds`, `process_started`, `process_group_terminated`, `infrastructure_phase`, `terminal_status`, `failure_reason`, `exit_code`, `stdout_sha256`, `stderr_sha256`, `stdout_bytes`, `stderr_bytes`, `started_at`, `ended_at`, `wall_seconds`, `cpu_seconds`, `peak_rss_bytes`, and `artifact_sha256`.

---

## Execution Contract

- `subprocess` uses an argv list, `shell=False`, and `start_new_session=True`.
- Intent is exclusive-created before the first child process starts.
- The implementation verdict and current production bytes are verified before intent, harness, build root, or result creation.
- The three-job attempt must not reuse an existing intent or an existing valid result.
- There is no retry.
- Every catchable exception after intent creation writes exactly one terminal result.
- An orphaned valid intent with no result and no live producer writes `FAIL_INFRASTRUCTURE/ORPHANED_INTENT_NO_PROCESS` and starts no child.
- Job timeout kills the process group and reaps. The runner also tracks the 7200-second outer deadline.
- Every started job produces one terminal result.
- Unstarted dependents are written as `NOT_STARTED`.
- stdout and stderr are hashed and counted as raw bytes.
- Source, build, and harness paths are safe and non-symlink.
- Production does not call confirmatory `run_preflight`.
- Production does not call a profiling runner.

---

## Implementation-Verdict Byte Closure

Formal implementation-verdict archival remains a later reserved file. This plan does not create it. The later production function must still treat that file as authority over the four reviewed implementation paths.

`validate_implementation_verdict` must require:

- `reviewed_commit` matches `^[0-9a-f]{40}$`
- the four reviewed paths are exactly:
  - `src/p3_v3/pilot_build.py`
  - `scripts/p3_v3/pilot.py`
  - `tests/p3_v3/test_pilot_build.py`
  - `tests/p3_v3/test_pilot.py`
- the six SHA-256 fields are lowercase SHA-256

`verify_reviewed_production_bytes` must use `read_regular_file_snapshot` on those four current files, compare each digest to the verdict, and finish before intent, harness, build root, or result creation. Any drift writes no output and fails closed.

`_require_plan_and_implementation_verdicts` returns `plan_sha256`, `plan_verdict_sha256`, and `implementation_verdict_sha256`. Intent and aggregate result bind `implementation_verdict_sha256`. `predecessor_sha256` must contain the implementation-verdict file SHA.

---

## Durable Environment Evidence

The durable intent must embed the complete exact environment snapshot object and its self-hash. Storing only `environment_snapshot_sha256` is not enough.

The snapshot must bind at least:

- resolved cmake executable path
- resolved C++ compiler path or null
- CMake version
- compiler identity and version, or null
- generator `Unix Makefiles`
- OS, Python, and Git identities
- `build_parallelism = 4`
- disconnected environment
- `system_boost_fallback_accepted = false`
- CUDA absence non-blocking
- `claims = blocked`

The intent validator must re-validate the embedded object and require `environment_snapshot.artifact_sha256 == environment_snapshot_sha256`. The aggregate result carries the same embedded object.

---

## Exact Terminal Semantics

Job `terminal_status` values are mutually exclusive. The field matrix is:

- `PASS`: `process_started=true`, `exit_code=0`, `failure_reason=null`, stdio hashes and counts present, timestamps and resource fields present, `process_group_terminated=false`, `infrastructure_phase=null`
- `FAIL`: `process_started=true`, nonzero or crash exit, `failure_reason` in `{NONZERO_EXIT, CRASH}`
- `TIMEOUT`: `process_started=true`, `exit_code=null`, `failure_reason=TIMEOUT`, and the process group was terminated
- `FAIL_INFRASTRUCTURE`: `infrastructure_phase` is `PRE_PROCESS` or `POST_PROCESS`. `PRE_PROCESS` has `process_started=false` and no forged process evidence. `POST_PROCESS` has `process_started=true` and stdio evidence.
- `NOT_STARTED`: `process_started=false`, `failure_reason=DEPENDENCY_NOT_STARTED`, and no forged exit, stdio, timestamps, or resource evidence

Result validator conservation:

- `planned_count == 3`
- `terminal_count == 3`
- `started_count` equals the number of jobs with `process_started=true`
- `not_started_count` equals the number of `NOT_STARTED` jobs
- job id, order, dependencies, and timeouts equal the frozen templates; argv equals the intent-bound resolved cmake/compiler argv
- configure not PASS implies build and smoke `NOT_STARTED`
- build not PASS implies smoke `NOT_STARTED`
- aggregate `terminal_status` and `failure_reason` equal the first non-PASS job
- all three PASS implies aggregate `PASS` and `failure_reason=null`

---

## Crash, Timeout, and No-Retry Reconciliation

Child processes start in an independent process group or session. A job timeout sends `SIGKILL` to the process group and then waits and reaps. After `Popen` succeeds, every path is inside a `try`/`finally` that kills and reaps the process group. The runner keeps an internal outer deadline of 7200 seconds. The future shell watchdog is `timeout 2h5m`, later than that deadline, so a terminal result can still be written.

After intent creation, every catchable exception normalizes to one terminal result. Production must not delete or overwrite intent, result, harness, or build root.

Reconciliation states are mutually exclusive and complete:

| State | Intent | Result | Live producer | Live child | Pair | Action |
|---|---|---|---|---|---|---|
| `FRESH` | absent | absent | no | no | n/a | start one new attempt |
| `INTENT_PRODUCER_LIVE` | valid | absent | yes | any | n/a | refuse; do not start another child |
| `INTENT_CHILD_LIVE` | valid | absent | no | yes | n/a | refuse; do not orphan-terminalize; do not start another child |
| `INTENT_ONLY_ORPHAN` | valid | absent | no | no | n/a | write `FAIL_INFRASTRUCTURE/ORPHANED_INTENT_NO_PROCESS`; start no child |
| `RESULT_TERMINAL` | valid | valid | any | any | yes | refuse; do not rerun |
| `RESULT_WITHOUT_INTENT` | absent | present | any | any | n/a | refuse |
| `INVALID_DURABLE` | any other combination, including a mismatched intent/result pair |  |  |  |  | refuse |

Source drift after a child, harness publication failure, and log or result publication failure have explicit terminal reasons. They must not leave an intent that cannot be reviewed.

---

## Compiler Source and Build Artifact Evidence

Keep the three-job DAG. Do not add a fourth job.

`CMAKE_CONFIGURE` argv is the frozen template plus the resolved cmake executable and `-DCMAKE_CXX_COMPILER=<resolved-path>`. `BASELINE_BUILD` uses the same resolved cmake path. Timeouts remain 900 / 3600 / 1800. The internal outer deadline remains 7200. Parallelism remains 4. Unbound `CXX` / `CC` / toolchain overrides are rejected.

If the resolved C++ compiler is absent, `CMAKE_CONFIGURE` is `FAIL_INFRASTRUCTURE/MISSING_DEPENDENCY` with `infrastructure_phase=PRE_PROCESS`. Do not install a compiler, change the harness, or retry.

If the internal outer deadline is already exhausted before a job starts, that job is `FAIL_INFRASTRUCTURE/OUTER_DEADLINE_EXHAUSTED`. It is not `MISSING_DEPENDENCY`. If the deadline expires while a child is running, the process group is killed and the job is `TIMEOUT`.

`BASELINE_BUILD` PASS requires a postcondition, still inside that job, that reads the actual compiler depfile:

`/tmp/p3-boost-math-pilot-build-preflight/CMakeFiles/boost_math_pilot_smoke.dir/smoke.cpp.o.d`

That file must be a regular non-symlink file. Production must not rerun `compiler -M`. The depfile must mention the frozen `smoke.cpp` and `include/boost/math/constants/constants.hpp`. Every path containing `/boost/` must start with `/tmp/p3-boost-math-pilot-production-source/include/`. `/usr/include/boost`, `/usr/local/include/boost`, or any other Boost root makes `BASELINE_BUILD` `FAIL_INFRASTRUCTURE/SYSTEM_BOOST_FALLBACK`. A missing or unreadable depfile is `FAIL_INFRASTRUCTURE/UNSUPPORTED_TOOLCHAIN`.

`compile_commands.json` must contain exactly one `smoke.cpp` entry. The entry may use `arguments` or a `command` string parsed by `shlex.split`. Production does not execute that command. The compiler realpath, frozen include path, and `BOOST_MATH_STANDALONE=1` must match the environment snapshot. System Boost include paths are forbidden.

`CMakeCache.txt` must record `CMAKE_GENERATOR=Unix Makefiles`, a `CMAKE_CXX_COMPILER` realpath equal to the environment snapshot, and source/build directories equal to the frozen harness and build roots.

The aggregate result binds and validates:

- `CMakeCache.txt` SHA-256
- `compile_commands.json` SHA-256
- compiler depfile SHA-256
- canonical dependency-list SHA-256
- `boost_math_pilot_smoke` executable SHA-256

`BASELINE_SMOKE` must execute the executable whose SHA-256 was recorded. Resolved cmake and compiler identities must match the intent environment snapshot, CMakeCache, and compile_commands.

`validate_attempt_pair(intent, intent_file_sha256, result)` is required before `RESULT_TERMINAL`. It re-checks intent SHA, environment snapshot object and hash, implementation-verdict SHA, source/preparation identities, Authorization SHA, harness hashes, predecessor = intent predecessor plus the intent file SHA, and job argv/timeout/DAG against that intent.

---

## Future Production CLI

The unique future CLI, not run by this node:

```text
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src timeout 2h5m \
  python3 scripts/p3_v3/pilot.py build-preflight \
  --source-root /tmp/p3-boost-math-pilot-production-source \
  --build-root /tmp/p3-boost-math-pilot-build-preflight
```

The CLI must not accept authorization, intent, result, expected-hash, timeout, job-count, harness, compiler, CMake argv, mutant, MR, or execution-plan overrides.

---

## Confirmation Isolation

All confirmatory entry points must fail-closed on the new `p3-pilot-build-preflight-*` schemas.

A build-preflight PASS:

- does not enter the formal denominator
- does not change the claim ledger
- does not support RQ4
- is not a complete Boost.Math build
- is not source profiling
- is not mutant compile success
- is not MR validity
- is not a paper Result or Contribution

`claims` remain `blocked`.

---

## Reserved Review Paths

Reserved. This node does not create them. The later capability task does not create them.

```text
docs/review_20260817/boost_math_pilot_build_preflight_plan_sol_high_review.md
docs/review_20260817/boost_math_pilot_build_preflight_implementation_sol_high_review.md
```

Plan verdict exact keys and types:

- `reviewed_plan_path`: str, must equal `docs/superpowers/plans/2026-08-17-p3-boost-math-pilot-build-preflight-only.md`
- `reviewed_plan_sha256`: str
- `verdict`: str, must equal `PASS`
- `authorized_state`: str, must equal `PILOT_BUILD_PREFLIGHT_PLAN_FROZEN`
- `claims`: str, must equal `blocked`

Implementation verdict exact keys and types:

- `reviewed_plan_path`: str
- `reviewed_plan_sha256`: str
- `reviewed_plan_verdict_sha256`: str
- `reviewed_commit`: str
- `reviewed_pilot_build_path`: str
- `reviewed_pilot_build_sha256`: str
- `reviewed_pilot_cli_path`: str
- `reviewed_pilot_cli_sha256`: str
- `reviewed_test_pilot_build_path`: str
- `reviewed_test_pilot_build_sha256`: str
- `reviewed_test_pilot_path`: str
- `reviewed_test_pilot_sha256`: str
- `verdict`: str, must equal `PASS`
- `authorized_state`: str, must equal `PILOT_BUILD_PREFLIGHT_IMPLEMENTATION_PASS`
- `claims`: str, must equal `blocked`

---

## Future File Map

Create:

- `src/p3_v3/pilot_build.py`
- `tests/p3_v3/test_pilot_build.py`

Modify:

- `scripts/p3_v3/pilot.py`
- `tests/p3_v3/test_pilot.py`

Do not modify `src/p3_v3/pilot_source.py`, `tests/p3_v3/test_pilot_source.py`, confirmatory schemas, protocol, Frame, claim ledger, source manifest, source-preparation result, or any existing plan, verdict, or authority.

This planning node does not create those future implementation files.

---

### Task 1: Build-Preflight Capability On Synthetic CMake Fixtures

**Files:**
- Create: `src/p3_v3/pilot_build.py`
- Create: `tests/p3_v3/test_pilot_build.py`
- Modify: `scripts/p3_v3/pilot.py`
- Modify: `tests/p3_v3/test_pilot.py`
- Do not create: `data/p3_v3/pilot/boost_math/user-auth-build-preflight.txt`, `data/p3_v3/pilot/boost_math/build-preflight-intent.json`, `data/p3_v3/pilot/boost_math/build-preflight-result.json`, `docs/review_20260817/boost_math_pilot_build_preflight_plan_sol_high_review.md`, `docs/review_20260817/boost_math_pilot_build_preflight_implementation_sol_high_review.md`

**Interfaces:**
- Consumes: `validate_exact_object`, `canonical_sha256`, `validate_sha256`, `write_canonical_json`, `read_regular_file_snapshot`, `EvidenceError`, `capture_materialized_tree`, `validate_materialized_tree_with_phase1`, `reject_confirmatory_pilot`
- Produces: environment / intent / job-result / aggregate-result validators, a three-job runner over synthetic CMake fixtures, a `build-preflight` CLI verb that requires frozen paths, and fail-closed unit tests
- Does not produce: a production intent, a production result, Authorization, a plan verdict, an implementation verdict, a freeze, an execution plan, a claim-ledger write, or a real Boost.Math configure/build/smoke

User authorization required: no. Gate: capability implementation only, and only after the plan verdict exists. This planning node does not start the gate. Capability PASS does not authorize production build-preflight.

- [ ] **Step 1: Confirm the plan verdict exists before any implementation edit**

The reserved file `docs/review_20260817/boost_math_pilot_build_preflight_plan_sol_high_review.md` must already be an archived PASS with `authorized_state = PILOT_BUILD_PREFLIGHT_PLAN_FROZEN` and `claims = blocked`. If it is absent, stop. Do not implement an unfrozen plan.

- [ ] **Step 2: Confirm the confirmatory baseline before any edit**

Run:

```text
env \
  GIT_CONFIG_GLOBAL=/dev/null \
  GIT_CONFIG_NOSYSTEM=1 \
  GIT_CONFIG_COUNT=0 \
  PYTHONPATH=src \
  python3 -m pytest tests/p3_v3 -q
```

Expected: exit 0. Do not edit until that baseline is green.

- [ ] **Step 3: Write the failing tests**

Create `tests/p3_v3/test_pilot_build.py` with this exact file:

```python
from __future__ import annotations

import hashlib
import os
from pathlib import Path

import pytest

from p3_v3.artifacts import EvidenceError
from p3_v3.pilot import reject_confirmatory_pilot


REQUIRED_BUILD_PREFLIGHT_TESTS = [
    "test_missing_source_preparation_pass_verdict",
    "test_source_manifest_hash_drift",
    "test_source_preparation_result_hash_drift",
    "test_source_tree_drift",
    "test_authorization_missing",
    "test_authorization_wrong_bytes",
    "test_preexisting_build_root",
    "test_preexisting_harness_root",
    "test_symlink_path_rejection",
    "test_exact_three_job_dag",
    "test_configure_failure_prevents_build_and_smoke",
    "test_build_failure_prevents_smoke",
    "test_configure_timeout",
    "test_build_timeout",
    "test_smoke_timeout",
    "test_stdout_stderr_hash_and_byte_counts",
    "test_no_shell_execution",
    "test_no_retry_on_existing_intent",
    "test_no_network_download_contract",
    "test_no_system_boost_fallback",
    "test_cuda_absence_is_non_blocking",
    "test_confirmatory_schema_leakage_rejection",
    "test_claims_denominator_rq4_invariants",
    "test_implementation_verdict_reviewed_path_commit_hash_drift",
    "test_implementation_verdict_sha_enters_intent_result_predecessor",
    "test_reviewed_production_bytes_runtime_drift",
    "test_durable_environment_snapshot_round_trip",
    "test_missing_compiler_exact_infrastructure_result",
    "test_terminal_status_exact_matrix",
    "test_result_count_conservation_and_aggregate",
    "test_configure_build_dependency_blocking",
    "test_process_group_timeout_terminates_descendants",
    "test_exception_after_intent_produces_terminal_result",
    "test_orphaned_intent_reconciliation_writes_no_new_process",
    "test_second_invocation_never_reruns",
    "test_source_drift_after_child_yields_terminal_failure",
    "test_system_boost_dependency_path_rejection",
    "test_frozen_source_dependency_closure_pass",
    "test_build_artifact_hashes_bound",
    "test_smoke_refuses_executable_hash_drift",
    "test_collect_baseline_build_evidence_pass",
    "test_collect_baseline_build_evidence_missing_frozen_include",
    "test_compile_commands_compiler_mismatch",
    "test_cmakecache_compiler_generator_root_drift",
    "test_system_boost_in_actual_depfile",
    "test_depfile_raw_and_canonical_hashes_enter_result",
    "test_configure_build_use_resolved_toolchain_argv",
    "test_producer_dead_child_live_not_orphan_terminal",
    "test_post_popen_exception_reaps_process_group",
    "test_outer_deadline_exhausted_not_missing_dependency",
    "test_validate_attempt_pair_rejects_drift",
    "test_mismatched_intent_result_is_not_result_terminal",
]


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _minimal_environment(pilot_build):
    environment = {
        "schema_version": "p3-pilot-build-preflight-environment-v1",
        "execution_class": "PILOT_ONLY",
        "denominator": "PILOT_ONLY",
        "cmake_executable": "cmake",
        "cmake_executable_path": "/usr/bin/cmake",
        "cmake_version": "cmake version 3.28.0",
        "cxx_compiler_executable": "c++",
        "cxx_compiler_path": "/usr/bin/c++",
        "cxx_compiler_identity": "c++ (Debian)",
        "cxx_compiler_version": "c++ (Debian)",
        "cmake_generator": "Unix Makefiles",
        "os_name": "Linux",
        "os_release": "6.12.0",
        "python_version": "3.11.0",
        "git_version": "git version 2.43.0",
        "build_parallelism": 4,
        "nvcc_present": False,
        "native_profiling_present": False,
        "cuda_absence_blocking": False,
        "fetchcontent_fully_disconnected": True,
        "system_boost_fallback_accepted": False,
        "disconnected_environment": dict(pilot_build.DISCONNECTED_ENVIRONMENT),
        "claims": "blocked",
    }
    return pilot_build.validate_environment_snapshot(pilot_build._self_hash(environment))



def _synthetic_specs(tmp_path: Path, configure, build, smoke, timeouts=None):
    timeouts = timeouts or (900, 3600, 1800)
    return (
        {
            "job_id": "CMAKE_CONFIGURE",
            "job_kind": "CMAKE_CONFIGURE",
            "dependency_job_ids": [],
            "argv": list(configure),
            "timeout_seconds": timeouts[0],
        },
        {
            "job_id": "BASELINE_BUILD",
            "job_kind": "BASELINE_BUILD",
            "dependency_job_ids": ["CMAKE_CONFIGURE"],
            "argv": list(build),
            "timeout_seconds": timeouts[1],
        },
        {
            "job_id": "BASELINE_SMOKE",
            "job_kind": "BASELINE_SMOKE",
            "dependency_job_ids": ["BASELINE_BUILD"],
            "argv": list(smoke),
            "timeout_seconds": timeouts[2],
        },
    )


def test_required_build_preflight_names_are_frozen():
    assert REQUIRED_BUILD_PREFLIGHT_TESTS == [
        "test_missing_source_preparation_pass_verdict",
        "test_source_manifest_hash_drift",
        "test_source_preparation_result_hash_drift",
        "test_source_tree_drift",
        "test_authorization_missing",
        "test_authorization_wrong_bytes",
        "test_preexisting_build_root",
        "test_preexisting_harness_root",
        "test_symlink_path_rejection",
        "test_exact_three_job_dag",
        "test_configure_failure_prevents_build_and_smoke",
        "test_build_failure_prevents_smoke",
        "test_configure_timeout",
        "test_build_timeout",
        "test_smoke_timeout",
        "test_stdout_stderr_hash_and_byte_counts",
        "test_no_shell_execution",
        "test_no_retry_on_existing_intent",
        "test_no_network_download_contract",
        "test_no_system_boost_fallback",
        "test_cuda_absence_is_non_blocking",
        "test_confirmatory_schema_leakage_rejection",
        "test_claims_denominator_rq4_invariants",
        "test_implementation_verdict_reviewed_path_commit_hash_drift",
        "test_implementation_verdict_sha_enters_intent_result_predecessor",
        "test_reviewed_production_bytes_runtime_drift",
        "test_durable_environment_snapshot_round_trip",
        "test_missing_compiler_exact_infrastructure_result",
        "test_terminal_status_exact_matrix",
        "test_result_count_conservation_and_aggregate",
        "test_configure_build_dependency_blocking",
        "test_process_group_timeout_terminates_descendants",
        "test_exception_after_intent_produces_terminal_result",
        "test_orphaned_intent_reconciliation_writes_no_new_process",
        "test_second_invocation_never_reruns",
        "test_source_drift_after_child_yields_terminal_failure",
        "test_system_boost_dependency_path_rejection",
        "test_frozen_source_dependency_closure_pass",
        "test_build_artifact_hashes_bound",
        "test_smoke_refuses_executable_hash_drift",
        "test_collect_baseline_build_evidence_pass",
        "test_collect_baseline_build_evidence_missing_frozen_include",
        "test_compile_commands_compiler_mismatch",
        "test_cmakecache_compiler_generator_root_drift",
        "test_system_boost_in_actual_depfile",
        "test_depfile_raw_and_canonical_hashes_enter_result",
        "test_configure_build_use_resolved_toolchain_argv",
        "test_producer_dead_child_live_not_orphan_terminal",
        "test_post_popen_exception_reaps_process_group",
        "test_outer_deadline_exhausted_not_missing_dependency",
        "test_validate_attempt_pair_rejects_drift",
        "test_mismatched_intent_result_is_not_result_terminal",
    ]


def test_missing_source_preparation_pass_verdict(tmp_path, monkeypatch):
    import p3_v3.pilot_build as pilot_build

    monkeypatch.setattr(
        pilot_build,
        "SOURCE_PREPARATION_RESULT_VERDICT_PATH",
        tmp_path / "missing-source-prep-verdict.md",
    )
    monkeypatch.setattr(pilot_build, "INTENT_PATH", tmp_path / "intent.json")
    monkeypatch.setattr(pilot_build, "RESULT_PATH", tmp_path / "result.json")
    monkeypatch.setattr(pilot_build, "FROZEN_SOURCE_ROOT", tmp_path / "source")
    monkeypatch.setattr(pilot_build, "FROZEN_BUILD_ROOT", tmp_path / "build")
    monkeypatch.setattr(pilot_build, "FROZEN_HARNESS_ROOT", tmp_path / "harness")
    monkeypatch.setattr(
        pilot_build,
        "AUTHORIZATION_PATH",
        tmp_path / "user-auth-build-preflight.txt",
    )
    (tmp_path / "user-auth-build-preflight.txt").write_bytes(
        pilot_build.AUTHORIZATION_BYTES
    )
    with pytest.raises(
        EvidenceError, match="E_PILOT_SOURCE_PREPARATION_RESULT_VERDICT|E_PILOT_BUILD_IDENTITY"
    ):
        pilot_build._require_source_preparation_identities()
    assert not (tmp_path / "intent.json").exists()
    assert not (tmp_path / "result.json").exists()


def test_source_manifest_hash_drift(tmp_path, monkeypatch):
    import p3_v3.pilot_build as pilot_build

    verdict = tmp_path / "source-prep-verdict.md"
    verdict.write_bytes(
        Path(
            "docs/review_20260817/"
            "boost_math_pilot_source_preparation_result_sol_high_review.md"
        ).read_bytes()
    )
    monkeypatch.setattr(
        pilot_build, "SOURCE_PREPARATION_RESULT_VERDICT_PATH", verdict
    )
    drifted = tmp_path / "source-manifest.json"
    drifted.write_bytes(b'{"drift":true}\n')
    monkeypatch.setattr(pilot_build, "SOURCE_MANIFEST_PATH", drifted)
    with pytest.raises(EvidenceError, match="E_PILOT_SOURCE_MANIFEST"):
        pilot_build._require_source_preparation_identities()


def test_source_preparation_result_hash_drift(tmp_path, monkeypatch):
    import p3_v3.pilot_build as pilot_build

    verdict = tmp_path / "source-prep-verdict.md"
    verdict.write_bytes(
        Path(
            "docs/review_20260817/"
            "boost_math_pilot_source_preparation_result_sol_high_review.md"
        ).read_bytes()
    )
    monkeypatch.setattr(
        pilot_build, "SOURCE_PREPARATION_RESULT_VERDICT_PATH", verdict
    )
    monkeypatch.setattr(
        pilot_build,
        "SOURCE_MANIFEST_PATH",
        Path("data/p3_v3/pilot/boost_math/source-manifest.json"),
    )
    drifted = tmp_path / "source-preparation-result.json"
    drifted.write_bytes(b'{"drift":true}\n')
    monkeypatch.setattr(pilot_build, "SOURCE_PREPARATION_RESULT_PATH", drifted)
    with pytest.raises(EvidenceError, match="E_PILOT_SOURCE_RESULT"):
        pilot_build._require_source_preparation_identities()


def test_source_tree_drift(tmp_path, monkeypatch):
    import p3_v3.pilot_build as pilot_build

    fake = tmp_path / "source"
    fake.mkdir()
    (fake / "only.txt").write_text("not the frozen tree\n", encoding="utf-8")
    monkeypatch.setattr(pilot_build, "FROZEN_SOURCE_ROOT", fake)
    with pytest.raises(EvidenceError, match="E_PILOT_SOURCE_TREE_MISMATCH"):
        pilot_build.require_frozen_source_tree(fake)


def test_authorization_missing(tmp_path, monkeypatch):
    import p3_v3.pilot_build as pilot_build

    monkeypatch.setattr(
        pilot_build,
        "AUTHORIZATION_PATH",
        tmp_path / "user-auth-build-preflight.txt",
    )
    with pytest.raises(EvidenceError, match="E_PILOT_BUILD_AUTH_ABSENT"):
        pilot_build._require_authorization()


def test_authorization_wrong_bytes(tmp_path, monkeypatch):
    import p3_v3.pilot_build as pilot_build

    path = tmp_path / "user-auth-build-preflight.txt"
    path.write_bytes(b"AUTHORIZE_BOOSTMATH_PILOT_PREPARATION\n")
    monkeypatch.setattr(pilot_build, "AUTHORIZATION_PATH", path)
    with pytest.raises(EvidenceError, match="E_PILOT_BUILD_AUTH"):
        pilot_build._require_authorization()


def test_preexisting_build_root(tmp_path):
    import p3_v3.pilot_build as pilot_build

    root = tmp_path / "build"
    root.mkdir()
    with pytest.raises(EvidenceError, match="E_PILOT_BUILD_PREEXISTING"):
        pilot_build.require_absent_path(root, "build-root")


def test_preexisting_harness_root(tmp_path):
    import p3_v3.pilot_build as pilot_build

    root = tmp_path / "harness"
    root.mkdir()
    with pytest.raises(EvidenceError, match="E_PILOT_BUILD_PREEXISTING"):
        pilot_build.require_absent_path(root, "harness-root")


def test_symlink_path_rejection(tmp_path):
    import p3_v3.pilot_build as pilot_build

    real = tmp_path / "real"
    link = tmp_path / "link"
    real.mkdir()
    link.symlink_to(real)
    with pytest.raises(EvidenceError, match="E_PILOT_BUILD_SYMLINK"):
        pilot_build.require_safe_directory(link, link, "source-root")


def test_exact_three_job_dag(tmp_path):
    import p3_v3.pilot_build as pilot_build

    specs = _synthetic_specs(
        tmp_path,
        ["python3", "-c", "print('configure')"],
        ["python3", "-c", "print('build')"],
        ["python3", "-c", "print('smoke')"],
    )
    results, _evidence = pilot_build.run_three_jobs(
        specs,
        env=dict(os.environ),
        log_root=tmp_path / "logs",
    )
    assert [item["job_id"] for item in results] == [
        "CMAKE_CONFIGURE",
        "BASELINE_BUILD",
        "BASELINE_SMOKE",
    ]
    assert [item["terminal_status"] for item in results] == ["PASS", "PASS", "PASS"]
    assert all(item["claims"] == "blocked" for item in results)


def test_configure_failure_prevents_build_and_smoke(tmp_path):
    import p3_v3.pilot_build as pilot_build

    specs = _synthetic_specs(
        tmp_path,
        ["python3", "-c", "raise SystemExit(2)"],
        ["python3", "-c", "print('build')"],
        ["python3", "-c", "print('smoke')"],
    )
    results, _evidence = pilot_build.run_three_jobs(
        specs,
        env=dict(os.environ),
        log_root=tmp_path / "logs",
    )
    assert results[0]["terminal_status"] == "FAIL"
    assert results[1]["terminal_status"] == "NOT_STARTED"
    assert results[2]["terminal_status"] == "NOT_STARTED"
    assert results[1]["failure_reason"] == "DEPENDENCY_NOT_STARTED"
    assert results[2]["failure_reason"] == "DEPENDENCY_NOT_STARTED"
    assert results[1]["exit_code"] is None
    assert results[1]["stdout_sha256"] is None


def test_build_failure_prevents_smoke(tmp_path):
    import p3_v3.pilot_build as pilot_build

    specs = _synthetic_specs(
        tmp_path,
        ["python3", "-c", "print('configure')"],
        ["python3", "-c", "raise SystemExit(3)"],
        ["python3", "-c", "print('smoke')"],
    )
    results, _evidence = pilot_build.run_three_jobs(
        specs,
        env=dict(os.environ),
        log_root=tmp_path / "logs",
    )
    assert results[0]["terminal_status"] == "PASS"
    assert results[1]["terminal_status"] == "FAIL"
    assert results[2]["terminal_status"] == "NOT_STARTED"
    assert results[2]["failure_reason"] == "DEPENDENCY_NOT_STARTED"


def test_configure_timeout(tmp_path):
    import p3_v3.pilot_build as pilot_build

    specs = _synthetic_specs(
        tmp_path,
        ["python3", "-c", "import time; time.sleep(2)"],
        ["python3", "-c", "print('build')"],
        ["python3", "-c", "print('smoke')"],
        timeouts=(0.2, 3600, 1800),
    )
    results, _evidence = pilot_build.run_three_jobs(
        specs,
        env=dict(os.environ),
        log_root=tmp_path / "logs",
    )
    assert results[0]["terminal_status"] == "TIMEOUT"
    assert results[1]["terminal_status"] == "NOT_STARTED"
    assert results[2]["terminal_status"] == "NOT_STARTED"


def test_build_timeout(tmp_path):
    import p3_v3.pilot_build as pilot_build

    specs = _synthetic_specs(
        tmp_path,
        ["python3", "-c", "print('configure')"],
        ["python3", "-c", "import time; time.sleep(2)"],
        ["python3", "-c", "print('smoke')"],
        timeouts=(900, 0.2, 1800),
    )
    results, _evidence = pilot_build.run_three_jobs(
        specs,
        env=dict(os.environ),
        log_root=tmp_path / "logs",
    )
    assert results[1]["terminal_status"] == "TIMEOUT"
    assert results[2]["terminal_status"] == "NOT_STARTED"


def test_smoke_timeout(tmp_path):
    import p3_v3.pilot_build as pilot_build

    specs = _synthetic_specs(
        tmp_path,
        ["python3", "-c", "print('configure')"],
        ["python3", "-c", "print('build')"],
        ["python3", "-c", "import time; time.sleep(2)"],
        timeouts=(900, 3600, 0.2),
    )
    results, _evidence = pilot_build.run_three_jobs(
        specs,
        env=dict(os.environ),
        log_root=tmp_path / "logs",
    )
    assert results[2]["terminal_status"] == "TIMEOUT"


def test_stdout_stderr_hash_and_byte_counts(tmp_path):
    import p3_v3.pilot_build as pilot_build

    specs = _synthetic_specs(
        tmp_path,
        ["python3", "-c", "import sys; sys.stdout.write('OUT'); sys.stderr.write('ERR')"],
        ["python3", "-c", "print('build')"],
        ["python3", "-c", "print('smoke')"],
    )
    results, _evidence = pilot_build.run_three_jobs(
        specs,
        env=dict(os.environ),
        log_root=tmp_path / "logs",
    )
    job = results[0]
    assert job["stdout_sha256"] == _sha256_bytes(b"OUT")
    assert job["stderr_sha256"] == _sha256_bytes(b"ERR")
    assert job["stdout_bytes"] == 3
    assert job["stderr_bytes"] == 3


def test_no_shell_execution(tmp_path, monkeypatch):
    import p3_v3.pilot_build as pilot_build

    seen = {}

    class FakeProc:
        returncode = 0
        pid = os.getpid()

        def communicate(self, timeout=None):
            return b"", b""

        def kill(self):
            return None

    def fake_popen(argv, stdout=None, stderr=None, shell=None, env=None, start_new_session=None):
        seen["argv"] = argv
        seen["shell"] = shell
        seen["start_new_session"] = start_new_session
        return FakeProc()

    spec = {
        "job_id": "CMAKE_CONFIGURE",
        "job_kind": "CMAKE_CONFIGURE",
        "dependency_job_ids": [],
        "argv": ["cmake", "-S", "harness", "-B", "build"],
        "timeout_seconds": 900,
    }
    pilot_build.execute_job(
        spec, env={"PATH": "/usr/bin"}, log_root=tmp_path / "logs", popen=fake_popen
    )
    assert seen["shell"] is False
    assert seen["start_new_session"] is True
    assert seen["argv"] == ["cmake", "-S", "harness", "-B", "build"]


def test_no_retry_on_existing_intent(tmp_path, monkeypatch):
    import p3_v3.pilot_build as pilot_build

    intent = tmp_path / "build-preflight-intent.json"
    intent.write_bytes(b"{}\n")
    monkeypatch.setattr(pilot_build, "INTENT_PATH", intent)
    monkeypatch.setattr(pilot_build, "RESULT_PATH", tmp_path / "result.json")
    monkeypatch.setattr(pilot_build, "FROZEN_SOURCE_ROOT", tmp_path / "source")
    monkeypatch.setattr(pilot_build, "FROZEN_BUILD_ROOT", tmp_path / "build")
    monkeypatch.setattr(pilot_build, "FROZEN_HARNESS_ROOT", tmp_path / "harness")
    with pytest.raises(EvidenceError, match="E_PILOT_BUILD_PREEXISTING"):
        pilot_build.run_build_preflight(tmp_path / "source", tmp_path / "build")


def test_no_network_download_contract():
    import p3_v3.pilot_build as pilot_build

    assert "-DFETCHCONTENT_FULLY_DISCONNECTED=ON" in pilot_build.CMAKE_CONFIGURE_ARGV
    assert "-DFETCHCONTENT_UPDATES_DISCONNECTED=ON" in pilot_build.CMAKE_CONFIGURE_ARGV
    assert (
        pilot_build.DISCONNECTED_ENVIRONMENT["FETCHCONTENT_FULLY_DISCONNECTED"] == "ON"
    )
    reason = pilot_build.detect_network_or_boost(
        b"Fetching Boost",
        b"",
        ["cmake"],
    )
    assert reason == "NETWORK_OR_DOWNLOAD_ATTEMPT"


def test_no_system_boost_fallback():
    import p3_v3.pilot_build as pilot_build

    with pytest.raises(EvidenceError, match="SYSTEM_BOOST_FALLBACK"):
        pilot_build.reject_system_boost_environment({"BOOST_ROOT": "/usr"})
    reason = pilot_build.detect_network_or_boost(
        b"",
        b"-I/usr/include/boost",
        ["c++"],
    )
    assert reason == "SYSTEM_BOOST_FALLBACK"
    assert "find_package(Boost" not in pilot_build.HARNESS_CMAKE_BYTES.decode("utf-8")
    assert b"/usr/include/boost" not in pilot_build.HARNESS_CMAKE_BYTES


def test_cuda_absence_is_non_blocking(monkeypatch):
    import p3_v3.pilot_build as pilot_build

    monkeypatch.setattr(
        pilot_build.shutil,
        "which",
        lambda name: None if name == "nvcc" else "/usr/bin/" + name,
    )
    monkeypatch.setattr(pilot_build, "probe_identity", lambda exe: None if exe is None else "probe")
    snapshot = pilot_build.make_environment_snapshot()
    assert snapshot["nvcc_present"] is False
    assert snapshot["cuda_absence_blocking"] is False
    assert snapshot["native_profiling_present"] is False
    assert snapshot["claims"] == "blocked"


def test_confirmatory_schema_leakage_rejection(tmp_path):
    from p3_v3.packages import verify_package
    from p3_v3.artifacts import canonical_sha256

    for schema in (
        "p3-pilot-build-preflight-intent-v1",
        "p3-pilot-build-preflight-job-result-v1",
        "p3-pilot-build-preflight-result-v1",
        "p3-pilot-build-preflight-environment-v1",
    ):
        value = {
            "schema_version": schema,
            "execution_class": "PILOT_ONLY",
            "denominator": "PILOT_ONLY",
            "claims": "blocked",
        }
        with pytest.raises(EvidenceError, match="E_PILOT_DENOMINATOR_LEAK"):
            reject_confirmatory_pilot(value, schema)
        manifest = {
            "schema_version": schema,
            "role": "CONSTRUCTION_A",
            "parents": [],
            "files": [],
            "package_tree_sha256": canonical_sha256([]),
            "artifact_sha256": "0" * 64,
        }
        with pytest.raises(EvidenceError, match="E_PILOT_DENOMINATOR_LEAK"):
            verify_package(tmp_path, manifest)


def test_claims_denominator_rq4_invariants():
    import p3_v3.pilot_build as pilot_build

    not_started = pilot_build.make_not_started_job(pilot_build.JOB_SPECS[1])
    assert not_started["claims"] == "blocked"
    assert not_started["execution_class"] == "PILOT_ONLY"
    assert not_started["denominator"] == "PILOT_ONLY"
    validated = _minimal_environment(pilot_build)
    assert validated["claims"] == "blocked"
    impl = "a" * 64
    intent = pilot_build.build_intent(validated, sorted([impl, "0" * 64]), impl)
    assert intent["claims"] == "blocked"
    assert intent["formal_denominator_membership"] is False
    assert intent["rq4_supported"] is False
    assert intent["no_retry"] is True
    assert intent["planned_count"] == 3
    assert intent["implementation_verdict_sha256"] == impl
    jobs = [
        pilot_build.make_not_started_job(spec) for spec in pilot_build.JOB_SPECS
    ]
    result = pilot_build.build_result(
        intent_sha256="1" * 64,
        environment=validated,
        jobs=jobs,
        predecessor=sorted(["1" * 64, impl]),
        implementation_verdict_sha256=impl,
        evidence=None,
    )
    assert result["claims"] == "blocked"
    assert result["formal_denominator_membership"] is False
    assert result["rq4_supported"] is False
    assert result["no_retry"] is True
    assert result["planned_count"] == 3


def test_capability_does_not_call_confirmatory_preflight():
    import p3_v3.pilot_build as pilot_build

    assert not hasattr(pilot_build, "run_preflight")
    source = Path(__file__).resolve().parents[2] / "src" / "p3_v3" / "pilot_build.py"
    text = source.read_text(encoding="utf-8")
    assert "run_preflight" not in text
    assert "erf(x)" not in text
    assert "erfc" not in text


def test_implementation_verdict_reviewed_path_commit_hash_drift():
    import p3_v3.pilot_build as pilot_build

    verdict = {
        "reviewed_plan_path": pilot_build.PLAN_PATH.as_posix(),
        "reviewed_plan_sha256": "0" * 64,
        "reviewed_plan_verdict_sha256": "1" * 64,
        "reviewed_commit": "44acee8882b004f50005cd39ca732bc6f09604fa",
        "reviewed_pilot_build_path": "src/wrong.py",
        "reviewed_pilot_build_sha256": "2" * 64,
        "reviewed_pilot_cli_path": "scripts/p3_v3/pilot.py",
        "reviewed_pilot_cli_sha256": "3" * 64,
        "reviewed_test_pilot_build_path": "tests/p3_v3/test_pilot_build.py",
        "reviewed_test_pilot_build_sha256": "4" * 64,
        "reviewed_test_pilot_path": "tests/p3_v3/test_pilot.py",
        "reviewed_test_pilot_sha256": "5" * 64,
        "verdict": "PASS",
        "authorized_state": "PILOT_BUILD_PREFLIGHT_IMPLEMENTATION_PASS",
        "claims": "blocked",
    }
    with pytest.raises(EvidenceError, match="E_PILOT_BUILD_IMPL_VERDICT"):
        pilot_build.validate_implementation_verdict(verdict, "0" * 64, "1" * 64)
    verdict["reviewed_pilot_build_path"] = "src/p3_v3/pilot_build.py"
    verdict["reviewed_commit"] = "NOTAGITSHA"
    with pytest.raises(EvidenceError, match="E_PILOT_BUILD_IMPL_VERDICT"):
        pilot_build.validate_implementation_verdict(verdict, "0" * 64, "1" * 64)


def test_implementation_verdict_sha_enters_intent_result_predecessor():
    import p3_v3.pilot_build as pilot_build

    env = _minimal_environment(pilot_build)
    impl = "b" * 64
    intent = pilot_build.build_intent(env, sorted([impl, "c" * 64]), impl)
    assert intent["implementation_verdict_sha256"] == impl
    assert impl in intent["predecessor_sha256"]
    jobs = [pilot_build.make_not_started_job(spec) for spec in pilot_build.JOB_SPECS]
    result = pilot_build.build_result(
        intent_sha256="d" * 64,
        environment=env,
        jobs=jobs,
        predecessor=sorted(["d" * 64, impl]),
        implementation_verdict_sha256=impl,
        evidence=None,
    )
    assert result["implementation_verdict_sha256"] == impl
    assert impl in result["predecessor_sha256"]


def test_reviewed_production_bytes_runtime_drift(tmp_path, monkeypatch):
    import p3_v3.pilot_build as pilot_build

    current = tmp_path / "src" / "p3_v3" / "pilot_build.py"
    current.parent.mkdir(parents=True)
    current.write_bytes(b"current-bytes\n")
    monkeypatch.setattr(
        pilot_build,
        "REVIEWED_IMPLEMENTATION_FILES",
        (
            (
                "reviewed_pilot_build_path",
                "reviewed_pilot_build_sha256",
                str(current),
            ),
        ),
    )
    verdict = {
        "reviewed_pilot_build_path": str(current),
        "reviewed_pilot_build_sha256": "0" * 64,
    }
    with pytest.raises(EvidenceError, match="E_PILOT_BUILD_PRODUCTION_BYTES"):
        pilot_build.verify_reviewed_production_bytes(verdict)


def test_durable_environment_snapshot_round_trip():
    import p3_v3.pilot_build as pilot_build

    env = _minimal_environment(pilot_build)
    impl = "f" * 64
    intent = pilot_build.build_intent(env, sorted([impl]), impl)
    again = pilot_build.validate_environment_snapshot(intent["environment_snapshot"])
    assert again["artifact_sha256"] == intent["environment_snapshot_sha256"]
    assert again["cmake_executable_path"] == "/usr/bin/cmake"
    assert again["cxx_compiler_path"] == "/usr/bin/c++"
    assert again["cmake_version"] == "cmake version 3.28.0"
    assert again["cmake_generator"] == "Unix Makefiles"


def test_missing_compiler_exact_infrastructure_result(tmp_path):
    import p3_v3.pilot_build as pilot_build

    env = _minimal_environment(pilot_build)
    env = dict(env)
    env["cxx_compiler_path"] = None
    env["cxx_compiler_executable"] = None
    env["cxx_compiler_identity"] = None
    env["cxx_compiler_version"] = None
    env.pop("artifact_sha256")
    env = pilot_build.validate_environment_snapshot(pilot_build._self_hash(env))
    specs = _synthetic_specs(
        tmp_path,
        ["python3", "-c", "print('configure')"],
        ["python3", "-c", "print('build')"],
        ["python3", "-c", "print('smoke')"],
    )
    results, _evidence = pilot_build.run_three_jobs(
        specs,
        env=dict(os.environ),
        log_root=tmp_path / "logs",
        environment=env,
    )
    assert results[0]["terminal_status"] == "FAIL_INFRASTRUCTURE"
    assert results[0]["failure_reason"] == "MISSING_DEPENDENCY"
    assert results[0]["process_started"] is False
    assert results[0]["infrastructure_phase"] == "PRE_PROCESS"
    assert results[1]["terminal_status"] == "NOT_STARTED"
    assert results[2]["terminal_status"] == "NOT_STARTED"


def _started_job(pilot_build, spec, **overrides):
    payload = {
        "schema_version": "p3-pilot-build-preflight-job-result-v1",
        "execution_class": "PILOT_ONLY",
        "denominator": "PILOT_ONLY",
        "job_id": spec["job_id"],
        "job_kind": spec["job_kind"],
        "dependency_job_ids": list(spec["dependency_job_ids"]),
        "argv": list(spec["argv"]),
        "timeout_seconds": spec["timeout_seconds"],
        "process_started": True,
        "process_group_terminated": False,
        "infrastructure_phase": None,
        "terminal_status": "PASS",
        "failure_reason": None,
        "exit_code": 0,
        "stdout_sha256": "a" * 64,
        "stderr_sha256": "b" * 64,
        "stdout_bytes": 1,
        "stderr_bytes": 1,
        "started_at": "2026-08-18T00:00:00Z",
        "ended_at": "2026-08-18T00:00:01Z",
        "wall_seconds": 1.0,
        "cpu_seconds": 0.1,
        "peak_rss_bytes": 1024,
        "claims": "blocked",
    }
    payload.update(overrides)
    return pilot_build.validate_job_result(pilot_build._self_hash(payload))


def test_terminal_status_exact_matrix():
    import p3_v3.pilot_build as pilot_build

    spec = {
        "job_id": "CMAKE_CONFIGURE",
        "job_kind": "CMAKE_CONFIGURE",
        "dependency_job_ids": [],
        "argv": ["cmake"],
        "timeout_seconds": 900,
    }
    passed = _started_job(pilot_build, spec)
    assert passed["terminal_status"] == "PASS"
    assert passed["process_started"] is True
    assert passed["failure_reason"] is None
    failed = _started_job(
        pilot_build,
        spec,
        terminal_status="FAIL",
        failure_reason="NONZERO_EXIT",
        exit_code=2,
    )
    assert failed["terminal_status"] == "FAIL"
    timed = _started_job(
        pilot_build,
        spec,
        terminal_status="TIMEOUT",
        failure_reason="TIMEOUT",
        exit_code=None,
        process_group_terminated=True,
    )
    assert timed["process_group_terminated"] is True
    not_started = pilot_build.make_not_started_job(spec)
    assert not_started["process_started"] is False
    assert not_started["failure_reason"] == "DEPENDENCY_NOT_STARTED"
    assert not_started["started_at"] is None
    pre = pilot_build.make_pre_process_infra_job(spec, "MISSING_DEPENDENCY")
    assert pre["terminal_status"] == "FAIL_INFRASTRUCTURE"
    assert pre["infrastructure_phase"] == "PRE_PROCESS"
    assert pre["process_started"] is False
    post = _started_job(
        pilot_build,
        spec,
        terminal_status="FAIL_INFRASTRUCTURE",
        failure_reason="SYSTEM_BOOST_FALLBACK",
        infrastructure_phase="POST_PROCESS",
        exit_code=1,
    )
    assert post["infrastructure_phase"] == "POST_PROCESS"
    for status in ("PASS", "FAIL", "TIMEOUT", "FAIL_INFRASTRUCTURE", "NOT_STARTED"):
        assert status in pilot_build.ALL_TERMINAL


def test_result_count_conservation_and_aggregate():
    import p3_v3.pilot_build as pilot_build

    env = _minimal_environment(pilot_build)
    impl = "1" * 64
    jobs = [
        pilot_build.make_pre_process_infra_job(pilot_build.JOB_SPECS[0], "MISSING_DEPENDENCY"),
        pilot_build.make_not_started_job(pilot_build.JOB_SPECS[1]),
        pilot_build.make_not_started_job(pilot_build.JOB_SPECS[2]),
    ]
    result = pilot_build.build_result(
        intent_sha256="2" * 64,
        environment=env,
        jobs=jobs,
        predecessor=sorted(["2" * 64, impl]),
        implementation_verdict_sha256=impl,
        evidence=None,
    )
    assert result["planned_count"] == 3
    assert result["terminal_count"] == 3
    assert result["started_count"] == 0
    assert result["not_started_count"] == 2
    assert result["terminal_status"] == "FAIL_INFRASTRUCTURE"
    assert result["failure_reason"] == "MISSING_DEPENDENCY"


def test_configure_build_dependency_blocking(tmp_path):
    test_configure_failure_prevents_build_and_smoke(tmp_path)
    test_build_failure_prevents_smoke(tmp_path)


def test_process_group_timeout_terminates_descendants(tmp_path):
    import time
    import p3_v3.pilot_build as pilot_build

    marker = tmp_path / "desc.pid"
    spec = {
        "job_id": "CMAKE_CONFIGURE",
        "job_kind": "CMAKE_CONFIGURE",
        "dependency_job_ids": [],
        "argv": [
            "python3",
            "-c",
            (
                "import pathlib, subprocess, sys, time\n"
                "child = subprocess.Popen(['sleep', '30'])\n"
                "pathlib.Path(sys.argv[1]).write_text(str(child.pid), encoding='utf-8')\n"
                "time.sleep(30)\n"
            ),
            str(marker),
        ],
        "timeout_seconds": 900,
    }
    result = pilot_build.execute_job(
        spec,
        env=dict(os.environ),
        log_root=tmp_path / "logs",
        timeout_seconds=0.2,
    )
    assert result["terminal_status"] == "TIMEOUT"
    assert result["process_group_terminated"] is True
    assert result["exit_code"] is None
    deadline = time.monotonic() + 3
    pid = int(marker.read_text(encoding="utf-8"))
    gone = False
    while time.monotonic() < deadline:
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            gone = True
            break
        time.sleep(0.05)
    assert gone is True


def test_exception_after_intent_produces_terminal_result(tmp_path, monkeypatch):
    import p3_v3.pilot_build as pilot_build

    source = tmp_path / "source"
    build = tmp_path / "build"
    harness = tmp_path / "harness"
    intent_path = tmp_path / "intent.json"
    result_path = tmp_path / "result.json"
    monkeypatch.setattr(pilot_build, "FROZEN_SOURCE_ROOT", source)
    monkeypatch.setattr(pilot_build, "FROZEN_BUILD_ROOT", build)
    monkeypatch.setattr(pilot_build, "FROZEN_HARNESS_ROOT", harness)
    monkeypatch.setattr(pilot_build, "INTENT_PATH", intent_path)
    monkeypatch.setattr(pilot_build, "RESULT_PATH", result_path)
    monkeypatch.setattr(pilot_build, "_require_authorization", lambda: "a" * 64)
    monkeypatch.setattr(pilot_build, "_require_source_preparation_identities", lambda: None)
    monkeypatch.setattr(
        pilot_build,
        "_require_plan_and_implementation_verdicts",
        lambda: ("0" * 64, "1" * 64, "2" * 64),
    )
    monkeypatch.setattr(pilot_build, "require_frozen_source_tree", lambda root: "3" * 64)
    monkeypatch.setattr(
        pilot_build,
        "make_environment_snapshot",
        lambda: _minimal_environment(pilot_build),
    )

    def boom(harness_root, cmake_bytes, cxx_bytes):
        raise EvidenceError("E_PILOT_BUILD_HARNESS", "HARNESS_PUBLICATION_FAILURE")

    monkeypatch.setattr(pilot_build, "write_harness", boom)
    written = pilot_build.run_build_preflight(source, build)
    assert intent_path.is_file()
    assert result_path.is_file()
    assert written["terminal_status"] == "FAIL_INFRASTRUCTURE"
    assert written["failure_reason"] == "HARNESS_PUBLICATION_FAILURE"
    assert written["jobs"][0]["process_started"] is False


def test_orphaned_intent_reconciliation_writes_no_new_process(tmp_path, monkeypatch):
    import p3_v3.pilot_build as pilot_build
    from p3_v3.artifacts import write_canonical_json

    assert (
        pilot_build.classify_reconciliation(
            intent_present=True,
            result_present=False,
            intent_valid=True,
            result_valid=False,
            producer_live=False,
            child_live=False,
            pair_valid=False,
        )
        == "INTENT_ONLY_ORPHAN"
    )
    env = _minimal_environment(pilot_build)
    impl = "7" * 64
    monkeypatch.setattr(pilot_build, "FROZEN_SOURCE_ROOT", tmp_path / "source")
    monkeypatch.setattr(pilot_build, "FROZEN_BUILD_ROOT", tmp_path / "build")
    monkeypatch.setattr(pilot_build, "FROZEN_HARNESS_ROOT", tmp_path / "harness")
    intent = pilot_build.build_intent(env, sorted([impl]), impl)
    intent_path = tmp_path / "intent.json"
    result_path = tmp_path / "result.json"
    write_canonical_json(intent_path, intent, exclusive=True)
    original = intent_path.read_bytes()
    monkeypatch.setattr(pilot_build, "INTENT_PATH", intent_path)
    monkeypatch.setattr(pilot_build, "RESULT_PATH", result_path)
    monkeypatch.setattr(pilot_build, "attempt_is_live", lambda pid, starttime: False)
    seen = []

    def fake_popen(*args, **kwargs):
        seen.append(args)
        raise AssertionError("orphan must not start a child")

    monkeypatch.setattr(pilot_build.subprocess, "Popen", fake_popen)
    written = pilot_build.run_build_preflight(tmp_path / "source", tmp_path / "build")
    assert written["failure_reason"] == "ORPHANED_INTENT_NO_PROCESS"
    assert written["jobs"][0]["process_started"] is False
    assert seen == []
    assert intent_path.read_bytes() == original
    assert result_path.is_file()


def test_second_invocation_never_reruns(tmp_path, monkeypatch):
    import p3_v3.pilot_build as pilot_build
    from p3_v3.artifacts import write_canonical_json

    assert (
        pilot_build.classify_reconciliation(
            intent_present=True,
            result_present=True,
            intent_valid=True,
            result_valid=True,
            producer_live=False,
            child_live=False,
            pair_valid=True,
        )
        == "RESULT_TERMINAL"
    )
    env = _minimal_environment(pilot_build)
    impl = "8" * 64
    monkeypatch.setattr(pilot_build, "FROZEN_SOURCE_ROOT", tmp_path / "source")
    monkeypatch.setattr(pilot_build, "FROZEN_BUILD_ROOT", tmp_path / "build")
    monkeypatch.setattr(pilot_build, "FROZEN_HARNESS_ROOT", tmp_path / "harness")
    intent = pilot_build.build_intent(env, sorted([impl]), impl)
    jobs = [
        pilot_build.make_pre_process_infra_job(
            spec, "ORPHANED_INTENT_NO_PROCESS"
        )
        if spec["job_id"] == "CMAKE_CONFIGURE"
        else pilot_build.make_not_started_job(spec)
        for spec in pilot_build.bind_job_specs(env)
    ]
    intent_path = tmp_path / "intent.json"
    result_path = tmp_path / "result.json"
    write_canonical_json(intent_path, intent, exclusive=True)
    result = pilot_build.build_result(
        intent_sha256=_sha256_bytes(intent_path.read_bytes()),
        environment=env,
        jobs=jobs,
        predecessor=sorted(
            [_sha256_bytes(intent_path.read_bytes()), *intent["predecessor_sha256"]]
        ),
        implementation_verdict_sha256=impl,
        evidence=None,
    )
    write_canonical_json(result_path, result, exclusive=True)
    before_intent = intent_path.read_bytes()
    before_result = result_path.read_bytes()
    monkeypatch.setattr(pilot_build, "INTENT_PATH", intent_path)
    monkeypatch.setattr(pilot_build, "RESULT_PATH", result_path)
    with pytest.raises(EvidenceError, match="E_PILOT_BUILD_PREEXISTING"):
        pilot_build.run_build_preflight(tmp_path / "source", tmp_path / "build")
    assert intent_path.read_bytes() == before_intent
    assert result_path.read_bytes() == before_result


def test_source_drift_after_child_yields_terminal_failure(tmp_path, monkeypatch):
    import p3_v3.pilot_build as pilot_build

    calls = {"n": 0}

    def fake_tree(source_root):
        calls["n"] += 1
        if calls["n"] == 1:
            return "a" * 64
        raise EvidenceError("E_PILOT_SOURCE_TREE_MISMATCH", "SOURCE_TREE_DRIFT")

    monkeypatch.setattr(pilot_build, "require_frozen_source_tree", fake_tree)
    specs = _synthetic_specs(
        tmp_path,
        ["python3", "-c", "print('configure')"],
        ["python3", "-c", "print('build')"],
        ["python3", "-c", "print('smoke')"],
    )
    results, _evidence = pilot_build.run_three_jobs(
        specs,
        env=dict(os.environ),
        log_root=tmp_path / "logs",
        source_root=tmp_path / "source",
    )
    assert results[0]["terminal_status"] == "FAIL_INFRASTRUCTURE"
    assert results[0]["failure_reason"] == "SOURCE_TREE_DRIFT"
    assert results[1]["terminal_status"] == "NOT_STARTED"


def test_system_boost_dependency_path_rejection():
    import p3_v3.pilot_build as pilot_build

    with pytest.raises(EvidenceError, match="SYSTEM_BOOST_FALLBACK"):
        pilot_build.reject_nonfrozen_boost_headers(
            ["/usr/include/boost/config.hpp"]
        )


def test_frozen_source_dependency_closure_pass():
    import p3_v3.pilot_build as pilot_build

    paths = [
        "/tmp/p3-boost-math-pilot-production-source/include/boost/math/constants/constants.hpp",
        "/usr/include/c++/13/cmath",
    ]
    pilot_build.reject_nonfrozen_boost_headers(paths)
    digest = _sha256_bytes(pilot_build.canonical_dependency_list_bytes(paths))
    assert len(digest) == 64


def test_build_artifact_hashes_bound():
    import p3_v3.pilot_build as pilot_build

    env = _minimal_environment(pilot_build)
    impl = "4" * 64
    jobs = [_started_job(pilot_build, spec) for spec in pilot_build.JOB_SPECS]
    evidence = {
        "cmake_cache_sha256": "6" * 64,
        "compile_commands_sha256": "7" * 64,
        "compiler_depfile_sha256": "a" * 64,
        "dependency_list_sha256": "8" * 64,
        "smoke_executable_sha256": "9" * 64,
    }
    result = pilot_build.build_result(
        intent_sha256="5" * 64,
        environment=env,
        jobs=jobs,
        predecessor=sorted(["5" * 64, impl]),
        implementation_verdict_sha256=impl,
        evidence=evidence,
    )
    assert result["cmake_cache_sha256"] == "6" * 64
    assert result["compile_commands_sha256"] == "7" * 64
    assert result["compiler_depfile_sha256"] == "a" * 64
    assert result["dependency_list_sha256"] == "8" * 64
    assert result["smoke_executable_sha256"] == "9" * 64
    assert result["terminal_status"] == "PASS"
    assert result["failure_reason"] is None


def test_smoke_refuses_executable_hash_drift(tmp_path):
    import p3_v3.pilot_build as pilot_build

    exe = tmp_path / "boost_math_pilot_smoke"
    exe.write_bytes(b"old-bytes\n")
    specs = _synthetic_specs(
        tmp_path,
        ["python3", "-c", "print('configure')"],
        ["python3", "-c", "print('build')"],
        [str(exe)],
    )
    results, _evidence = pilot_build.run_three_jobs(
        specs,
        env=dict(os.environ),
        log_root=tmp_path / "logs",
        expected_smoke_sha256="0" * 64,
    )
    assert results[0]["terminal_status"] == "PASS"
    assert results[1]["terminal_status"] == "PASS"
    assert results[2]["terminal_status"] == "FAIL_INFRASTRUCTURE"
    assert results[2]["failure_reason"] == "MISSING_DEPENDENCY"
    assert results[2]["process_started"] is False



def _synthetic_build_evidence_tree(
    tmp_path: Path,
    pilot_build,
    monkeypatch,
    *,
    include_flag=True,
    compiler="/usr/bin/c++",
    generator="Unix Makefiles",
    system_boost=False,
    cache_compiler=None,
    source_dir=None,
    binary_dir=None,
):
    build = tmp_path / "build"
    harness = tmp_path / "harness"
    dep_dir = build / "CMakeFiles" / "boost_math_pilot_smoke.dir"
    dep_dir.mkdir(parents=True)
    harness.mkdir()
    monkeypatch.setattr(pilot_build, "FROZEN_BUILD_ROOT", build)
    monkeypatch.setattr(pilot_build, "FROZEN_HARNESS_ROOT", harness)
    cache_compiler = compiler if cache_compiler is None else cache_compiler
    source_dir = harness.as_posix() if source_dir is None else source_dir
    binary_dir = build.as_posix() if binary_dir is None else binary_dir
    (build / "CMakeCache.txt").write_text(
        "\n".join(
            [
                f"CMAKE_GENERATOR:INTERNAL={generator}",
                f"CMAKE_CXX_COMPILER:FILEPATH={cache_compiler}",
                f"CMAKE_HOME_DIRECTORY:INTERNAL={source_dir}",
                f"CMAKE_BINARY_DIR:STATIC={binary_dir}",
                "",
            ]
        ),
        encoding="utf-8",
    )
    include = pilot_build.FROZEN_INCLUDE_PREFIX if include_flag else "/tmp/other-include"
    compile_argv = [compiler, f"-I{include}", "-DBOOST_MATH_STANDALONE=1", "-c", "smoke.cpp"]
    (build / "compile_commands.json").write_text(
        __import__("json").dumps(
            [
                {
                    "directory": build.as_posix(),
                    "file": (harness / "smoke.cpp").as_posix(),
                    "arguments": compile_argv,
                }
            ]
        ),
        encoding="utf-8",
    )
    (build / "boost_math_pilot_smoke").write_bytes(b"exe\n")
    boost_header = (
        "/usr/include/boost/math/constants/constants.hpp"
        if system_boost
        else pilot_build.FROZEN_CONSTANTS_HEADER
    )
    dep_text = (
        "CMakeFiles/boost_math_pilot_smoke.dir/smoke.cpp.o: "
        f"{(harness / 'smoke.cpp').as_posix()} "
        f"{boost_header} "
        "/usr/include/c++/13/cmath\n"
    )
    (dep_dir / "smoke.cpp.o.d").write_text(dep_text, encoding="utf-8")
    env = _minimal_environment(pilot_build)
    env = dict(env)
    env["cxx_compiler_path"] = compiler
    env.pop("artifact_sha256", None)
    env = pilot_build.validate_environment_snapshot(pilot_build._self_hash(env))
    return build, env


def test_collect_baseline_build_evidence_pass(tmp_path, monkeypatch):
    import p3_v3.pilot_build as pilot_build

    build, env = _synthetic_build_evidence_tree(tmp_path, pilot_build, monkeypatch)
    evidence = pilot_build.collect_baseline_build_evidence(build, env)
    assert len(evidence["compiler_depfile_sha256"]) == 64
    assert len(evidence["dependency_list_sha256"]) == 64
    assert evidence["compiler_depfile_sha256"] != evidence["dependency_list_sha256"]


def test_collect_baseline_build_evidence_missing_frozen_include(tmp_path, monkeypatch):
    import p3_v3.pilot_build as pilot_build

    build, env = _synthetic_build_evidence_tree(
        tmp_path, pilot_build, monkeypatch, include_flag=False
    )
    with pytest.raises(EvidenceError, match="UNSUPPORTED_TOOLCHAIN"):
        pilot_build.collect_baseline_build_evidence(build, env)


def test_compile_commands_compiler_mismatch(tmp_path, monkeypatch):
    import p3_v3.pilot_build as pilot_build

    build, env = _synthetic_build_evidence_tree(tmp_path, pilot_build, monkeypatch)
    env = dict(env)
    env["cxx_compiler_path"] = "/usr/bin/g++"
    env.pop("artifact_sha256", None)
    env = pilot_build.validate_environment_snapshot(pilot_build._self_hash(env))
    with pytest.raises(EvidenceError, match="compiler differs"):
        pilot_build.collect_baseline_build_evidence(build, env)


def test_cmakecache_compiler_generator_root_drift(tmp_path, monkeypatch):
    import p3_v3.pilot_build as pilot_build

    build, env = _synthetic_build_evidence_tree(
        tmp_path,
        pilot_build,
        monkeypatch,
        generator="Ninja",
    )
    with pytest.raises(EvidenceError, match="CMAKE_GENERATOR differs"):
        pilot_build.collect_baseline_build_evidence(build, env)
    build, env = _synthetic_build_evidence_tree(
        tmp_path / "compiler",
        pilot_build,
        monkeypatch,
        cache_compiler="/usr/bin/g++",
    )
    with pytest.raises(EvidenceError, match="CMakeCache compiler differs"):
        pilot_build.collect_baseline_build_evidence(build, env)
    build, env = _synthetic_build_evidence_tree(
        tmp_path / "root",
        pilot_build,
        monkeypatch,
        source_dir="/tmp/other-harness",
    )
    with pytest.raises(EvidenceError, match="CMake source directory differs"):
        pilot_build.collect_baseline_build_evidence(build, env)


def test_system_boost_in_actual_depfile(tmp_path, monkeypatch):
    import p3_v3.pilot_build as pilot_build

    build, env = _synthetic_build_evidence_tree(
        tmp_path, pilot_build, monkeypatch, system_boost=True
    )
    with pytest.raises(EvidenceError, match="SYSTEM_BOOST_FALLBACK"):
        pilot_build.collect_baseline_build_evidence(build, env)


def test_depfile_raw_and_canonical_hashes_enter_result():
    test_build_artifact_hashes_bound()


def test_configure_build_use_resolved_toolchain_argv():
    import p3_v3.pilot_build as pilot_build

    env = _minimal_environment(pilot_build)
    configure = pilot_build.bind_configure_argv(
        env["cmake_executable_path"], env["cxx_compiler_path"]
    )
    build = pilot_build.bind_build_argv(env["cmake_executable_path"])
    assert configure[0] == env["cmake_executable_path"]
    assert build[0] == env["cmake_executable_path"]
    assert "-DCMAKE_CXX_COMPILER=" + env["cxx_compiler_path"] in configure
    intent = pilot_build.build_intent(env, sorted(["b" * 64]), "b" * 64)
    assert intent["cmake_configure_argv"] == configure
    assert intent["baseline_build_argv"] == build


def test_producer_dead_child_live_not_orphan_terminal():
    import p3_v3.pilot_build as pilot_build

    assert (
        pilot_build.classify_reconciliation(
            intent_present=True,
            result_present=False,
            intent_valid=True,
            result_valid=False,
            producer_live=False,
            child_live=True,
            pair_valid=False,
        )
        == "INTENT_CHILD_LIVE"
    )
    assert "ORPHANED_INTENT_NO_PROCESS" not in {
        pilot_build.classify_reconciliation(
            intent_present=True,
            result_present=False,
            intent_valid=True,
            result_valid=False,
            producer_live=False,
            child_live=True,
            pair_valid=False,
        )
    }


def test_post_popen_exception_reaps_process_group(tmp_path, monkeypatch):
    import time
    import p3_v3.pilot_build as pilot_build

    marker = tmp_path / "desc.pid"
    spec = {
        "job_id": "CMAKE_CONFIGURE",
        "job_kind": "CMAKE_CONFIGURE",
        "dependency_job_ids": [],
        "argv": [
            "python3",
            "-c",
            (
                "import pathlib, subprocess, sys, time\n"
                "child = subprocess.Popen(['sleep', '30'])\n"
                "pathlib.Path(sys.argv[1]).write_text(str(child.pid), encoding='utf-8')\n"
                "time.sleep(30)\n"
            ),
            str(marker),
        ],
        "timeout_seconds": 900,
    }

    def boom(*args, **kwargs):
        deadline = time.monotonic() + 2
        while time.monotonic() < deadline and not marker.is_file():
            time.sleep(0.05)
        if not marker.is_file():
            raise OSError("identity publication failed before descendant pid")
        raise OSError("identity publication failed")

    monkeypatch.setattr(pilot_build, "write_process_identity", boom)
    with pytest.raises(OSError, match="identity publication failed"):
        pilot_build.execute_job(
            spec,
            env=dict(os.environ),
            log_root=tmp_path / "logs",
            timeout_seconds=5,
        )
    deadline = time.monotonic() + 3
    pid = int(marker.read_text(encoding="utf-8"))
    gone = False
    while time.monotonic() < deadline:
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            gone = True
            break
        time.sleep(0.05)
    assert gone is True


def test_outer_deadline_exhausted_not_missing_dependency(tmp_path):
    import time
    import p3_v3.pilot_build as pilot_build

    specs = _synthetic_specs(
        tmp_path,
        ["python3", "-c", "print('configure')"],
        ["python3", "-c", "print('build')"],
        ["python3", "-c", "print('smoke')"],
    )
    results, _evidence = pilot_build.run_three_jobs(
        specs,
        env=dict(os.environ),
        log_root=tmp_path / "logs",
        outer_deadline=time.monotonic() - 1,
    )
    assert results[0]["failure_reason"] == "OUTER_DEADLINE_EXHAUSTED"
    assert results[0]["failure_reason"] != "MISSING_DEPENDENCY"
    assert results[0]["process_started"] is False
    assert results[1]["terminal_status"] == "NOT_STARTED"


def test_validate_attempt_pair_rejects_drift():
    import p3_v3.pilot_build as pilot_build

    env = _minimal_environment(pilot_build)
    impl = "c" * 64
    intent = pilot_build.build_intent(env, sorted([impl]), impl)
    jobs = [
        pilot_build.make_pre_process_infra_job(spec, "ORPHANED_INTENT_NO_PROCESS")
        if spec["job_id"] == "CMAKE_CONFIGURE"
        else pilot_build.make_not_started_job(spec)
        for spec in pilot_build.bind_job_specs(env)
    ]
    intent_sha = "d" * 64
    result = pilot_build.build_result(
        intent_sha256=intent_sha,
        environment=env,
        jobs=jobs,
        predecessor=sorted([intent_sha, *intent["predecessor_sha256"]]),
        implementation_verdict_sha256=impl,
        evidence=None,
    )
    drifted = dict(result)
    drifted["intent_sha256"] = "e" * 64
    drifted.pop("artifact_sha256")
    drifted = pilot_build._self_hash(drifted)
    with pytest.raises(EvidenceError, match="E_PILOT_BUILD_PAIR"):
        pilot_build.validate_attempt_pair(intent, intent_sha, drifted)
    other_env = dict(env)
    other_env["python_version"] = "3.12.0"
    other_env.pop("artifact_sha256", None)
    other_env = pilot_build.validate_environment_snapshot(pilot_build._self_hash(other_env))
    env_drift = dict(result)
    env_drift["environment_snapshot"] = other_env
    env_drift["environment_snapshot_sha256"] = other_env["artifact_sha256"]
    env_drift.pop("artifact_sha256")
    env_drift = pilot_build._self_hash(env_drift)
    with pytest.raises(EvidenceError, match="E_PILOT_BUILD_PAIR"):
        pilot_build.validate_attempt_pair(intent, intent_sha, env_drift)
    impl_drift = dict(result)
    impl_drift["implementation_verdict_sha256"] = "0" * 64
    impl_drift["predecessor_sha256"] = sorted([intent_sha, "0" * 64])
    impl_drift.pop("artifact_sha256")
    impl_drift = pilot_build._self_hash(impl_drift)
    with pytest.raises(EvidenceError, match="E_PILOT_BUILD_PAIR"):
        pilot_build.validate_attempt_pair(intent, intent_sha, impl_drift)
    pred_drift = dict(result)
    pred_drift["predecessor_sha256"] = sorted(list(intent["predecessor_sha256"]))
    pred_drift.pop("artifact_sha256")
    pred_drift = pilot_build._self_hash(pred_drift)
    with pytest.raises(EvidenceError, match="E_PILOT_BUILD_PAIR"):
        pilot_build.validate_attempt_pair(intent, intent_sha, pred_drift)
    argv_drift = dict(result)
    jobs_drift = [dict(job) for job in argv_drift["jobs"]]
    jobs_drift[0] = dict(jobs_drift[0])
    jobs_drift[0]["argv"] = ["cmake"]
    jobs_drift[0].pop("artifact_sha256", None)
    jobs_drift[0] = pilot_build._self_hash(jobs_drift[0])
    argv_drift["jobs"] = jobs_drift
    argv_drift.pop("artifact_sha256")
    argv_drift = pilot_build._self_hash(argv_drift)
    with pytest.raises(EvidenceError, match="E_PILOT_BUILD_PAIR"):
        pilot_build.validate_attempt_pair(intent, intent_sha, argv_drift)


def test_mismatched_intent_result_is_not_result_terminal():
    import p3_v3.pilot_build as pilot_build

    assert (
        pilot_build.classify_reconciliation(
            intent_present=True,
            result_present=True,
            intent_valid=True,
            result_valid=True,
            producer_live=False,
            child_live=False,
            pair_valid=False,
        )
        == "INVALID_DURABLE"
    )
```

Append these tests to `tests/p3_v3/test_pilot.py`:

```python
def test_build_preflight_cli_accepts_only_frozen_roots():
    import scripts.p3_v3.pilot as pilot_cli

    parser = pilot_cli.build_parser()
    args = parser.parse_args(
        [
            "build-preflight",
            "--source-root",
            "/tmp/p3-boost-math-pilot-production-source",
            "--build-root",
            "/tmp/p3-boost-math-pilot-build-preflight",
        ]
    )
    assert args.command == "build-preflight"
    assert args.source_root == "/tmp/p3-boost-math-pilot-production-source"
    assert args.build_root == "/tmp/p3-boost-math-pilot-build-preflight"


def test_build_preflight_cli_rejects_overrides():
    import scripts.p3_v3.pilot as pilot_cli

    parser = pilot_cli.build_parser()
    forbidden = [
        ["build-preflight", "--authorization", "x"],
        ["build-preflight", "--intent", "x"],
        ["build-preflight", "--output", "x"],
        ["build-preflight", "--expected-hash", "x"],
        ["build-preflight", "--timeout", "1"],
        ["build-preflight", "--job-count", "3"],
        ["build-preflight", "--harness", "x"],
        ["build-preflight", "--compiler", "x"],
        ["build-preflight", "--cmake-argv", "x"],
        ["build-preflight", "--mutant", "x"],
        ["build-preflight", "--mr", "x"],
        ["build-preflight", "--execution-plan", "x"],
    ]
    for argv in forbidden:
        try:
            parser.parse_args(argv)
        except SystemExit:
            continue
        raise AssertionError(f"override was accepted: {argv}")
```

- [ ] **Step 4: Run tests to verify they fail**

Run:

```text
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m pytest \
  tests/p3_v3/test_pilot_build.py -q
```

Expected: FAIL because `p3_v3.pilot_build` is not importable, with `ModuleNotFoundError: No module named 'p3_v3.pilot_build'`.

Run:

```text
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m pytest \
  tests/p3_v3/test_pilot.py::test_build_preflight_cli_accepts_only_frozen_roots -q
```

Expected: FAIL because the `build-preflight` subparser does not exist.

- [ ] **Step 5: Write the minimal implementation**

Create `src/p3_v3/pilot_build.py` with this exact file:

```python
"""Pilot-only Boost.Math consumer-harness build-preflight capability."""

from __future__ import annotations

import hashlib
import json
import os
import platform
import re
import shlex
import resource
import shutil
import signal
import stat
import subprocess
import time
from pathlib import Path
from typing import Any

from p3_v3.artifacts import (
    EvidenceError,
    canonical_json_bytes,
    canonical_sha256,
    read_regular_file_snapshot,
    validate_exact_object,
    validate_sha256,
    write_canonical_json,
)
from p3_v3.pilot import reject_confirmatory_pilot
from p3_v3.pilot_source import (
    capture_materialized_tree,
    validate_materialized_tree_with_phase1,
)

PILOT_EXECUTION_CLASS = "PILOT_ONLY"
PILOT_DENOMINATOR = "PILOT_ONLY"
P12_ITEM_ID = "C-BOOSTMATH-001"
NEUTRAL_SNAPSHOT_ID = (
    "74cdc825c3c728c25f5ea857af1565350515a4e631fb0a874c26e810ec437886"
)
FROZEN_NORMALIZED_SOURCE_TREE_SHA256 = (
    "93a62859d7fdd6b2068e494bbe6e3e27180b874cbd27055ac27f941e507a90d8"
)
CONTROLLED_SUBJECT_ID = (
    "89b0e6791c611b465b9216e833e0c526a53ffd6946b5cd20de045e3641f43914"
)
CONTROLLED_SUBJECT_SOURCE_ID = (
    "e5f21a7d067d641d0a20bfc57c61e630d6f7588ef30235cea49c9a9cf950c7a7"
)
BUILD_DESCRIPTOR_SHA256 = (
    "68d2e0fd34b845bb0df22b29003f26259d5655d2ec80c18895ff36904db2d95d"
)
SOURCE_PREPARATION_RESULT_VERDICT_SHA256 = (
    "43cedfd21621496f61feec1418b2ec4d9e02b51096c477b0d221067d1e1ed7f2"
)
SOURCE_MANIFEST_FILE_SHA256 = (
    "d774143f6a0dc6cf24a9ddda8b4e9760b3d547e03cbd21e16d84220f826073c5"
)
SOURCE_PREPARATION_RESULT_FILE_SHA256 = (
    "6a525ff074f5ab67f4a58af0a4f7f2264f3888757513a8fc80fb6760c8b577b9"
)
SOURCE_PREPARATION_REVIEWED_COMMIT = "44acee8882b004f50005cd39ca732bc6f09604fa"

FROZEN_SOURCE_ROOT = Path("/tmp/p3-boost-math-pilot-production-source")
FROZEN_BUILD_ROOT = Path("/tmp/p3-boost-math-pilot-build-preflight")
FROZEN_HARNESS_ROOT = Path("/tmp/p3-boost-math-pilot-build-preflight-harness")
INTENT_PATH = Path("data/p3_v3/pilot/boost_math/build-preflight-intent.json")
RESULT_PATH = Path("data/p3_v3/pilot/boost_math/build-preflight-result.json")
AUTHORIZATION_PATH = Path(
    "data/p3_v3/pilot/boost_math/user-auth-build-preflight.txt"
)
SOURCE_MANIFEST_PATH = Path("data/p3_v3/pilot/boost_math/source-manifest.json")
SOURCE_PREPARATION_RESULT_PATH = Path(
    "data/p3_v3/pilot/boost_math/source-preparation-result.json"
)
SOURCE_PREPARATION_RESULT_VERDICT_PATH = Path(
    "docs/review_20260817/"
    "boost_math_pilot_source_preparation_result_sol_high_review.md"
)
PLAN_PATH = Path(
    "docs/superpowers/plans/"
    "2026-08-17-p3-boost-math-pilot-build-preflight-only.md"
)
PLAN_VERDICT_PATH = Path(
    "docs/review_20260817/"
    "boost_math_pilot_build_preflight_plan_sol_high_review.md"
)
IMPLEMENTATION_VERDICT_PATH = Path(
    "docs/review_20260817/"
    "boost_math_pilot_build_preflight_implementation_sol_high_review.md"
)

AUTHORIZATION_BYTES = b"AUTHORIZE_BOOSTMATH_PILOT_BUILD_PREFLIGHT\n"
AUTHORIZATION_SHA256 = (
    "2265145a6b73a16e1ae06b3c5b12baa2a842ad7d700e60ed0de67393746cfb15"
)

HARNESS_CMAKE_BYTES = (
    b"cmake_minimum_required(VERSION 3.5)\n"
    b"project(boost_math_pilot_build_preflight_harness LANGUAGES CXX)\n"
    b"\n"
    b"set(BOOST_MATH_PILOT_SOURCE_INCLUDE\n"
    b'    "/tmp/p3-boost-math-pilot-production-source/include"\n'
    b"    CACHE PATH\n"
    b'    "Frozen Boost.Math public include root")\n'
    b"\n"
    b"if(NOT BOOST_MATH_PILOT_SOURCE_INCLUDE STREQUAL\n"
    b'    "/tmp/p3-boost-math-pilot-production-source/include")\n'
    b"  message(FATAL_ERROR\n"
    b'    "BOOST_MATH_PILOT_SOURCE_INCLUDE is not the frozen include path")\n'
    b"endif()\n"
    b"\n"
    b"if(DEFINED BOOST_ROOT OR DEFINED BOOST_INCLUDEDIR OR DEFINED Boost_INCLUDE_DIR\n"
    b"    OR DEFINED Boost_DIR)\n"
    b'  message(FATAL_ERROR "unbound Boost search variables are forbidden")\n'
    b"endif()\n"
    b"\n"
    b"add_executable(boost_math_pilot_smoke smoke.cpp)\n"
    b"target_include_directories(\n"
    b"    boost_math_pilot_smoke\n"
    b"    PRIVATE\n"
    b'    "${BOOST_MATH_PILOT_SOURCE_INCLUDE}")\n'
    b"target_compile_definitions(\n"
    b"    boost_math_pilot_smoke\n"
    b"    PRIVATE\n"
    b"    BOOST_MATH_STANDALONE=1)\n"
    b"target_compile_features(boost_math_pilot_smoke PRIVATE cxx_std_14)\n"
    b"set_target_properties(\n"
    b"    boost_math_pilot_smoke\n"
    b"    PROPERTIES\n"
    b'    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}")\n'
)
HARNESS_CXX_BYTES = (
    b"#include <boost/math/constants/constants.hpp>\n"
    b"\n"
    b"int main()\n"
    b"{\n"
    b"    const double pi = boost::math::constants::pi<double>();\n"
    b"    if (pi > 3.14 && pi < 3.15)\n"
    b"    {\n"
    b"        return 0;\n"
    b"    }\n"
    b"    return 1;\n"
    b"}\n"
)
HARNESS_CMAKE_SHA256 = hashlib.sha256(HARNESS_CMAKE_BYTES).hexdigest()
HARNESS_CXX_SHA256 = hashlib.sha256(HARNESS_CXX_BYTES).hexdigest()

CMAKE_CONFIGURE_TIMEOUT_SECONDS = 900
BASELINE_BUILD_TIMEOUT_SECONDS = 3600
BASELINE_SMOKE_TIMEOUT_SECONDS = 1800
OUTER_TIMEOUT_SECONDS = 7200
SHELL_WATCHDOG = "2h5m"
BUILD_PARALLELISM = 4
PLANNED_COUNT = 3
COMPILER_DEPFILE_RELATIVE = (
    "CMakeFiles/boost_math_pilot_smoke.dir/smoke.cpp.o.d"
)
FROZEN_CONSTANTS_HEADER = (
    "/tmp/p3-boost-math-pilot-production-source/include/"
    "boost/math/constants/constants.hpp"
)
FROZEN_SMOKE_CXX = "/tmp/p3-boost-math-pilot-build-preflight-harness/smoke.cpp"
FORBIDDEN_TOOLCHAIN_ENV = (
    "CXX",
    "CC",
    "CMAKE_CXX_COMPILER",
    "CMAKE_C_COMPILER",
)

CMAKE_CONFIGURE_ARGV = [
    "cmake",
    "-S",
    "/tmp/p3-boost-math-pilot-build-preflight-harness",
    "-B",
    "/tmp/p3-boost-math-pilot-build-preflight",
    "-G",
    "Unix Makefiles",
    "-DCMAKE_BUILD_TYPE=Release",
    "-DCMAKE_CXX_STANDARD=14",
    "-DCMAKE_CXX_STANDARD_REQUIRED=ON",
    "-DBOOST_MATH_STANDALONE=1",
    "-DBOOST_MATH_PILOT_SOURCE_INCLUDE=/tmp/p3-boost-math-pilot-production-source/include",
    "-DCMAKE_DISABLE_SOURCE_CHANGES=ON",
    "-DCMAKE_DISABLE_IN_SOURCE_BUILD=ON",
    "-DFETCHCONTENT_FULLY_DISCONNECTED=ON",
    "-DFETCHCONTENT_UPDATES_DISCONNECTED=ON",
    "-DCMAKE_FIND_USE_PACKAGE_REGISTRY=OFF",
    "-DCMAKE_FIND_USE_SYSTEM_PACKAGE_REGISTRY=OFF",
    "-DCMAKE_EXPORT_COMPILE_COMMANDS=ON",
]
BASELINE_BUILD_ARGV = [
    "cmake",
    "--build",
    "/tmp/p3-boost-math-pilot-build-preflight",
    "--parallel",
    "4",
]
BASELINE_SMOKE_ARGV = [
    "/tmp/p3-boost-math-pilot-build-preflight/boost_math_pilot_smoke"
]
DEPENDENCY_DAG = [
    ["CMAKE_CONFIGURE", "BASELINE_BUILD"],
    ["BASELINE_BUILD", "BASELINE_SMOKE"],
]
JOB_SPECS = (
    {
        "job_id": "CMAKE_CONFIGURE",
        "job_kind": "CMAKE_CONFIGURE",
        "dependency_job_ids": [],
        "argv": CMAKE_CONFIGURE_ARGV,
        "timeout_seconds": CMAKE_CONFIGURE_TIMEOUT_SECONDS,
    },
    {
        "job_id": "BASELINE_BUILD",
        "job_kind": "BASELINE_BUILD",
        "dependency_job_ids": ["CMAKE_CONFIGURE"],
        "argv": BASELINE_BUILD_ARGV,
        "timeout_seconds": BASELINE_BUILD_TIMEOUT_SECONDS,
    },
    {
        "job_id": "BASELINE_SMOKE",
        "job_kind": "BASELINE_SMOKE",
        "dependency_job_ids": ["BASELINE_BUILD"],
        "argv": BASELINE_SMOKE_ARGV,
        "timeout_seconds": BASELINE_SMOKE_TIMEOUT_SECONDS,
    },
)

DISCONNECTED_ENVIRONMENT = {
    "FETCHCONTENT_FULLY_DISCONNECTED": "ON",
    "FETCHCONTENT_UPDATES_DISCONNECTED": "ON",
}
FORBIDDEN_BOOST_ENV = (
    "BOOST_ROOT",
    "BOOST_INCLUDEDIR",
    "Boost_DIR",
    "CMAKE_PREFIX_PATH",
    "CMAKE_INCLUDE_PATH",
    "CPATH",
    "CPLUS_INCLUDE_PATH",
)
NETWORK_MARKERS = (
    b"Downloading ",
    b"Cloning into",
    b"Fetching ",
    b"file(DOWNLOAD",
    b"-- Fetching",
    b"Resolving deltas",
    b"github.com",
    b"gitlab.com",
    b"bitbucket.org",
    b"FetchContent_Declare",
    b"ExternalProject_Add",
)
SYSTEM_BOOST_MARKERS = (
    "/usr/include/boost",
    "/usr/local/include/boost",
)
FROZEN_INCLUDE_PREFIX = "/tmp/p3-boost-math-pilot-production-source/include"
FROZEN_CMAKE_GENERATOR = "Unix Makefiles"
GIT_OID_RE = re.compile(r"^[0-9a-f]{40}$")
REVIEWED_IMPLEMENTATION_FILES = (
    (
        "reviewed_pilot_build_path",
        "reviewed_pilot_build_sha256",
        "src/p3_v3/pilot_build.py",
    ),
    (
        "reviewed_pilot_cli_path",
        "reviewed_pilot_cli_sha256",
        "scripts/p3_v3/pilot.py",
    ),
    (
        "reviewed_test_pilot_build_path",
        "reviewed_test_pilot_build_sha256",
        "tests/p3_v3/test_pilot_build.py",
    ),
    (
        "reviewed_test_pilot_path",
        "reviewed_test_pilot_sha256",
        "tests/p3_v3/test_pilot.py",
    ),
)
FAIL_REASONS = frozenset({"NONZERO_EXIT", "CRASH"})
INFRA_REASONS_PRE_PROCESS = frozenset(
    {
        "MISSING_DEPENDENCY",
        "SYSTEM_BOOST_FALLBACK",
        "UNSUPPORTED_TOOLCHAIN",
        "ORPHANED_INTENT_NO_PROCESS",
        "HARNESS_PUBLICATION_FAILURE",
        "RESULT_PUBLICATION_FAILURE",
        "OUTER_DEADLINE_EXHAUSTED",
    }
)
INFRA_REASONS_POST_PROCESS = frozenset(
    {
        "NETWORK_OR_DOWNLOAD_ATTEMPT",
        "SYSTEM_BOOST_FALLBACK",
        "MISSING_DEPENDENCY",
        "UNSUPPORTED_TOOLCHAIN",
        "SOURCE_TREE_DRIFT",
        "LOG_PUBLICATION_FAILURE",
    }
)
RECONCILIATION_STATES = frozenset(
    {
        "FRESH",
        "INTENT_PRODUCER_LIVE",
        "INTENT_CHILD_LIVE",
        "INTENT_ONLY_ORPHAN",
        "RESULT_TERMINAL",
        "RESULT_WITHOUT_INTENT",
        "INVALID_DURABLE",
    }
)

PLAN_VERDICT_EXACT = {
    "reviewed_plan_path": str,
    "reviewed_plan_sha256": str,
    "verdict": str,
    "authorized_state": str,
    "claims": str,
}
IMPLEMENTATION_VERDICT_EXACT = {
    "reviewed_plan_path": str,
    "reviewed_plan_sha256": str,
    "reviewed_plan_verdict_sha256": str,
    "reviewed_commit": str,
    "reviewed_pilot_build_path": str,
    "reviewed_pilot_build_sha256": str,
    "reviewed_pilot_cli_path": str,
    "reviewed_pilot_cli_sha256": str,
    "reviewed_test_pilot_build_path": str,
    "reviewed_test_pilot_build_sha256": str,
    "reviewed_test_pilot_path": str,
    "reviewed_test_pilot_sha256": str,
    "verdict": str,
    "authorized_state": str,
    "claims": str,
}
SOURCE_PREPARATION_RESULT_VERDICT_EXACT = {
    "authorized_state": str,
    "claims": str,
    "materialized_tree_sha256": str,
    "reviewed_commit": str,
    "reviewed_source_manifest_path": str,
    "reviewed_source_manifest_sha256": str,
    "reviewed_source_preparation_result_path": str,
    "reviewed_source_preparation_result_sha256": str,
    "verdict": str,
}
BUILD_PREFLIGHT_ENVIRONMENT_EXACT = {
    "schema_version": str,
    "execution_class": str,
    "denominator": str,
    "cmake_executable": str,
    "cmake_executable_path": str,
    "cmake_version": str,
    "cxx_compiler_executable": (str, type(None)),
    "cxx_compiler_path": (str, type(None)),
    "cxx_compiler_identity": (str, type(None)),
    "cxx_compiler_version": (str, type(None)),
    "cmake_generator": str,
    "os_name": str,
    "os_release": str,
    "python_version": str,
    "git_version": (str, type(None)),
    "build_parallelism": int,
    "nvcc_present": bool,
    "native_profiling_present": bool,
    "cuda_absence_blocking": bool,
    "fetchcontent_fully_disconnected": bool,
    "system_boost_fallback_accepted": bool,
    "disconnected_environment": dict,
    "claims": str,
    "artifact_sha256": str,
}
BUILD_PREFLIGHT_INTENT_EXACT = {
    "schema_version": str,
    "execution_class": str,
    "denominator": str,
    "plan_class": str,
    "p12_item_id": str,
    "neutral_snapshot_id": str,
    "normalized_source_tree_sha256": str,
    "controlled_subject_id": str,
    "controlled_subject_source_id": str,
    "build_descriptor_sha256": str,
    "source_preparation_verdict_sha256": str,
    "source_manifest_sha256": str,
    "source_preparation_result_sha256": str,
    "source_preparation_reviewed_commit": str,
    "implementation_verdict_sha256": str,
    "authorization_sha256": str,
    "harness_cmake_sha256": str,
    "harness_cxx_sha256": str,
    "source_root": str,
    "build_root": str,
    "harness_root": str,
    "cmake_configure_argv": list,
    "baseline_build_argv": list,
    "baseline_smoke_argv": list,
    "cmake_configure_timeout_seconds": int,
    "baseline_build_timeout_seconds": int,
    "baseline_smoke_timeout_seconds": int,
    "outer_timeout_seconds": int,
    "build_parallelism": int,
    "planned_count": int,
    "dependency_dag": list,
    "environment_snapshot": dict,
    "environment_snapshot_sha256": str,
    "producer_pid": int,
    "producer_starttime": str,
    "predecessor_sha256": list,
    "no_retry": bool,
    "claims": str,
    "formal_denominator_membership": bool,
    "rq4_supported": bool,
    "artifact_sha256": str,
}
BUILD_PREFLIGHT_JOB_RESULT_EXACT = {
    "schema_version": str,
    "execution_class": str,
    "denominator": str,
    "job_id": str,
    "job_kind": str,
    "dependency_job_ids": list,
    "argv": list,
    "timeout_seconds": int,
    "process_started": bool,
    "process_group_terminated": (bool, type(None)),
    "infrastructure_phase": (str, type(None)),
    "terminal_status": str,
    "failure_reason": (str, type(None)),
    "exit_code": (int, type(None)),
    "stdout_sha256": (str, type(None)),
    "stderr_sha256": (str, type(None)),
    "stdout_bytes": (int, type(None)),
    "stderr_bytes": (int, type(None)),
    "started_at": (str, type(None)),
    "ended_at": (str, type(None)),
    "wall_seconds": (float, type(None)),
    "cpu_seconds": (float, type(None)),
    "peak_rss_bytes": (int, type(None)),
    "claims": str,
    "artifact_sha256": str,
}
BUILD_PREFLIGHT_RESULT_EXACT = {
    "schema_version": str,
    "execution_class": str,
    "denominator": str,
    "p12_item_id": str,
    "neutral_snapshot_id": str,
    "normalized_source_tree_sha256": str,
    "controlled_subject_id": str,
    "controlled_subject_source_id": str,
    "build_descriptor_sha256": str,
    "source_preparation_verdict_sha256": str,
    "source_manifest_sha256": str,
    "source_preparation_result_sha256": str,
    "implementation_verdict_sha256": str,
    "intent_sha256": str,
    "authorization_sha256": str,
    "environment_snapshot": dict,
    "environment_snapshot_sha256": str,
    "harness_cmake_sha256": str,
    "harness_cxx_sha256": str,
    "cmake_cache_sha256": (str, type(None)),
    "compile_commands_sha256": (str, type(None)),
    "compiler_depfile_sha256": (str, type(None)),
    "dependency_list_sha256": (str, type(None)),
    "smoke_executable_sha256": (str, type(None)),
    "source_root": str,
    "build_root": str,
    "harness_root": str,
    "planned_count": int,
    "started_count": int,
    "terminal_count": int,
    "not_started_count": int,
    "jobs": list,
    "terminal_status": str,
    "failure_reason": (str, type(None)),
    "build_root_exists": bool,
    "build_root_is_symlink": bool,
    "no_retry": bool,
    "claims": str,
    "formal_denominator_membership": bool,
    "rq4_supported": bool,
    "predecessor_sha256": list,
    "artifact_sha256": str,
}

STARTED_TERMINAL = {"PASS", "FAIL", "TIMEOUT", "FAIL_INFRASTRUCTURE"}
ALL_TERMINAL = STARTED_TERMINAL | {"NOT_STARTED"}


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _self_hash(payload: dict[str, Any]) -> dict[str, Any]:
    body = {key: payload[key] for key in payload if key != "artifact_sha256"}
    return {**payload, "artifact_sha256": canonical_sha256(body)}


def read_authority_snapshot(path: Path, context: str) -> tuple[bytes, str]:
    try:
        raw, _mode = read_regular_file_snapshot(path, context)
    except EvidenceError as exc:
        if exc.code == "E_AUTHORITY_LOCK_PATH":
            raise EvidenceError(
                "E_PILOT_BUILD_IDENTITY",
                f"{context} authority snapshot is absent or unsafe",
            ) from exc
        raise
    digest = _sha256_bytes(raw)
    validate_sha256(digest, f"{context}.sha256")
    return raw, digest


def parse_canonical_json_object(raw: bytes, context: str) -> dict[str, Any]:
    try:
        value = json.loads(
            raw.decode("utf-8"),
            parse_constant=lambda token: (_ for _ in ()).throw(ValueError(token)),
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise EvidenceError("E_PILOT_BUILD_IDENTITY", f"{context} is not JSON") from exc
    if not isinstance(value, dict) or canonical_json_bytes(value) != raw:
        raise EvidenceError(
            "E_PILOT_BUILD_IDENTITY",
            f"{context} is not one canonical JSON object",
        )
    return value


def require_safe_directory(path: Path, expected: Path, context: str) -> Path:
    if path != expected:
        raise EvidenceError(
            "E_PILOT_BUILD_PATH",
            f"{context} must equal the frozen path",
        )
    if path.as_posix() != expected.as_posix():
        raise EvidenceError("E_PILOT_BUILD_PATH", f"{context} is not canonical")
    if not str(path).startswith("/tmp/"):
        raise EvidenceError("E_PILOT_BUILD_PATH", f"{context} escaped /tmp")
    try:
        info = path.lstat()
    except OSError as exc:
        raise EvidenceError(
            "E_PILOT_BUILD_PATH",
            f"{context} is unavailable",
        ) from exc
    if stat.S_ISLNK(info.st_mode):
        raise EvidenceError("E_PILOT_BUILD_SYMLINK", f"{context} is a symlink")
    if not stat.S_ISDIR(info.st_mode):
        raise EvidenceError("E_PILOT_BUILD_PATH", f"{context} is not a directory")
    return path


def require_absent_path(path: Path, context: str) -> None:
    if os.path.lexists(path):
        raise EvidenceError(
            "E_PILOT_BUILD_PREEXISTING",
            f"{context} already exists",
        )


def require_frozen_source_tree(source_root: Path) -> str:
    require_safe_directory(source_root, FROZEN_SOURCE_ROOT, "source-root")
    snapshot = capture_materialized_tree(source_root)
    observed = validate_materialized_tree_with_phase1(snapshot)
    if observed != FROZEN_NORMALIZED_SOURCE_TREE_SHA256:
        raise EvidenceError("E_PILOT_SOURCE_TREE_MISMATCH", observed)
    if len(snapshot.entries) != 4396:
        raise EvidenceError("E_PILOT_SOURCE_TREE_MISMATCH", "file count differs")
    total = sum(len(entry.content) for entry in snapshot.entries)
    if total != 95635487:
        raise EvidenceError("E_PILOT_SOURCE_TREE_MISMATCH", "total bytes differ")
    return observed


def reject_system_boost_environment(env: dict[str, str]) -> None:
    for key in FORBIDDEN_BOOST_ENV:
        value = env.get(key)
        if not value:
            continue
        lowered = value.lower()
        if "boost" in lowered or any(marker in value for marker in SYSTEM_BOOST_MARKERS):
            raise EvidenceError(
                "E_PILOT_SYSTEM_BOOST",
                "SYSTEM_BOOST_FALLBACK",
            )


def detect_network_or_boost(stdout: bytes, stderr: bytes, argv: list[str]) -> str | None:
    joined = b"\0".join(item.encode("utf-8") for item in argv)
    haystack = stdout + b"\n" + stderr + b"\n" + joined
    for marker in SYSTEM_BOOST_MARKERS:
        if marker.encode("utf-8") in haystack:
            return "SYSTEM_BOOST_FALLBACK"
    for marker in NETWORK_MARKERS:
        if marker in haystack:
            return "NETWORK_OR_DOWNLOAD_ATTEMPT"
    return None


def validate_plan_verdict(value: object, plan_sha256: str) -> dict[str, Any]:
    validated = validate_exact_object(
        value, PLAN_VERDICT_EXACT, "build-preflight-plan-verdict"
    )
    validate_sha256(validated["reviewed_plan_sha256"], "plan-verdict.reviewed_plan_sha256")
    if validated["reviewed_plan_path"] != PLAN_PATH.as_posix():
        raise EvidenceError("E_PILOT_BUILD_PLAN_VERDICT", "reviewed plan path differs")
    if validated["reviewed_plan_sha256"] != plan_sha256:
        raise EvidenceError("E_PILOT_BUILD_PLAN_VERDICT", "reviewed plan hash differs")
    if validated["verdict"] != "PASS":
        raise EvidenceError("E_PILOT_BUILD_PLAN_VERDICT", "verdict is not PASS")
    if validated["authorized_state"] != "PILOT_BUILD_PREFLIGHT_PLAN_FROZEN":
        raise EvidenceError("E_PILOT_BUILD_PLAN_VERDICT", "authorized_state differs")
    if validated["claims"] != "blocked":
        raise EvidenceError("E_PILOT_BUILD_PLAN_VERDICT", "claims are not blocked")
    return validated


def validate_source_preparation_result_verdict(value: object) -> dict[str, Any]:
    validated = validate_exact_object(
        value,
        SOURCE_PREPARATION_RESULT_VERDICT_EXACT,
        "source-preparation-result-verdict",
    )
    if validated["verdict"] != "PASS":
        raise EvidenceError(
            "E_PILOT_SOURCE_PREPARATION_RESULT_VERDICT",
            "source-preparation verdict is not PASS",
        )
    if validated["authorized_state"] != "PILOT_SOURCE_PREPARATION_PASS":
        raise EvidenceError(
            "E_PILOT_SOURCE_PREPARATION_RESULT_VERDICT",
            "authorized_state differs",
        )
    if validated["claims"] != "blocked":
        raise EvidenceError(
            "E_PILOT_SOURCE_PREPARATION_RESULT_VERDICT",
            "claims are not blocked",
        )
    if validated["reviewed_source_manifest_sha256"] != SOURCE_MANIFEST_FILE_SHA256:
        raise EvidenceError(
            "E_PILOT_SOURCE_PREPARATION_RESULT_VERDICT",
            "source manifest hash differs",
        )
    if (
        validated["reviewed_source_preparation_result_sha256"]
        != SOURCE_PREPARATION_RESULT_FILE_SHA256
    ):
        raise EvidenceError(
            "E_PILOT_SOURCE_PREPARATION_RESULT_VERDICT",
            "source-preparation result hash differs",
        )
    if validated["materialized_tree_sha256"] != FROZEN_NORMALIZED_SOURCE_TREE_SHA256:
        raise EvidenceError(
            "E_PILOT_SOURCE_PREPARATION_RESULT_VERDICT",
            "tree hash differs",
        )
    if validated["reviewed_commit"] != SOURCE_PREPARATION_REVIEWED_COMMIT:
        raise EvidenceError(
            "E_PILOT_SOURCE_PREPARATION_RESULT_VERDICT",
            "reviewed commit differs",
        )
    return validated


def producer_identity() -> tuple[int, str]:
    pid = os.getpid()
    stat_text = Path(f"/proc/{pid}/stat").read_text(encoding="utf-8")
    rparen = stat_text.rfind(")")
    fields = stat_text[rparen + 2 :].split()
    return pid, fields[19]


def attempt_is_live(pid: int, starttime: str) -> bool:
    path = Path(f"/proc/{pid}/stat")
    if not path.is_file():
        return False
    stat_text = path.read_text(encoding="utf-8")
    rparen = stat_text.rfind(")")
    fields = stat_text[rparen + 2 :].split()
    return fields[19] == starttime


def read_proc_starttime(pid: int) -> str:
    stat_text = Path(f"/proc/{pid}/stat").read_text(encoding="utf-8")
    rparen = stat_text.rfind(")")
    fields = stat_text[rparen + 2 :].split()
    return fields[19]


def process_group_has_members(pgid: int) -> bool:
    for entry in Path("/proc").iterdir():
        if not entry.name.isdigit():
            continue
        try:
            stat_text = (entry / "stat").read_text(encoding="utf-8")
        except OSError:
            continue
        rparen = stat_text.rfind(")")
        fields = stat_text[rparen + 2 :].split()
        if len(fields) > 2 and fields[2] == str(pgid):
            return True
    return False


def classify_reconciliation(
    *,
    intent_present: bool,
    result_present: bool,
    intent_valid: bool,
    result_valid: bool,
    producer_live: bool,
    child_live: bool,
    pair_valid: bool,
) -> str:
    if not intent_present and not result_present:
        return "FRESH"
    if not intent_present and result_present:
        return "RESULT_WITHOUT_INTENT"
    if intent_present and result_present:
        if intent_valid and result_valid and pair_valid:
            return "RESULT_TERMINAL"
        return "INVALID_DURABLE"
    if intent_present and not result_present and intent_valid:
        if producer_live:
            return "INTENT_PRODUCER_LIVE"
        if child_live:
            return "INTENT_CHILD_LIVE"
        return "INTENT_ONLY_ORPHAN"
    return "INVALID_DURABLE"


def probe_identity(executable: str | None) -> str | None:
    if executable is None:
        return None
    try:
        completed = subprocess.run(
            [executable, "--version"],
            check=False,
            capture_output=True,
            timeout=5,
            shell=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    blob = (completed.stdout or b"") + (completed.stderr or b"")
    text = blob.decode("utf-8", "replace").strip()
    if not text:
        return None
    return text.splitlines()[0]


def parse_dependency_paths(dep_text: str) -> list[str]:
    stripped = dep_text.replace("\\\n", " ")
    if ":" in stripped:
        stripped = stripped.split(":", 1)[1]
    paths = [item.strip() for item in stripped.split() if item.strip()]
    return sorted(dict.fromkeys(paths))


def reject_nonfrozen_boost_headers(paths: list[str]) -> None:
    for path in paths:
        posix = path.replace("\\", "/")
        lowered = posix.lower()
        if "/boost/" not in lowered and not lowered.endswith("/boost"):
            continue
        if not posix.startswith(FROZEN_INCLUDE_PREFIX + "/"):
            raise EvidenceError("E_PILOT_SYSTEM_BOOST", "SYSTEM_BOOST_FALLBACK")


def canonical_dependency_list_bytes(paths: list[str]) -> bytes:
    return ("".join(f"{item}\n" for item in sorted(paths))).encode("utf-8")


def bind_configure_argv(cmake_path: str, cxx_path: str | None) -> list[str]:
    argv = [cmake_path, *CMAKE_CONFIGURE_ARGV[1:]]
    if cxx_path is not None:
        argv.append("-DCMAKE_CXX_COMPILER=" + cxx_path)
    return argv


def bind_build_argv(cmake_path: str) -> list[str]:
    return [cmake_path, *BASELINE_BUILD_ARGV[1:]]


def bind_job_specs(environment: dict[str, Any]) -> tuple[dict[str, Any], ...]:
    cmake_path = environment["cmake_executable_path"]
    cxx_path = environment["cxx_compiler_path"]
    argvs = (
        bind_configure_argv(cmake_path, cxx_path),
        bind_build_argv(cmake_path),
        list(BASELINE_SMOKE_ARGV),
    )
    bound = []
    for spec, argv in zip(JOB_SPECS, argvs, strict=True):
        item = dict(spec)
        item["argv"] = list(argv)
        bound.append(item)
    return tuple(bound)


def reject_unbound_toolchain(env: dict[str, str], resolved_cxx: str | None) -> None:
    for key in FORBIDDEN_TOOLCHAIN_ENV:
        value = env.get(key)
        if not value:
            continue
        if resolved_cxx is None or os.path.realpath(value) != os.path.realpath(resolved_cxx):
            raise EvidenceError("E_PILOT_MISSING_DEPENDENCY", "MISSING_DEPENDENCY")


def parse_cmake_cache(text: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in text.splitlines():
        if not line or line.startswith("#") or line.startswith("//"):
            continue
        if ":" not in line or "=" not in line:
            continue
        key = line.split(":", 1)[0]
        value = line.split("=", 1)[1]
        values[key] = value
    return values


def smoke_compile_argv(compile_db: list[object]) -> list[str]:
    matches = []
    for entry in compile_db:
        if not isinstance(entry, dict):
            continue
        file_name = str(entry.get("file", ""))
        if Path(file_name).name != "smoke.cpp":
            continue
        matches.append(entry)
    if len(matches) != 1:
        raise EvidenceError("E_PILOT_MISSING_DEPENDENCY", "UNSUPPORTED_TOOLCHAIN")
    entry = matches[0]
    if isinstance(entry.get("arguments"), list):
        return [str(item) for item in entry["arguments"]]
    command = entry.get("command")
    if not isinstance(command, str):
        raise EvidenceError("E_PILOT_MISSING_DEPENDENCY", "UNSUPPORTED_TOOLCHAIN")
    return shlex.split(command)


def ensure_safe_log_root(log_root: Path) -> Path:
    if os.path.lexists(log_root) and log_root.is_symlink():
        raise EvidenceError("E_PILOT_BUILD_SYMLINK", "log-root is a symlink")
    log_root.mkdir(parents=True, exist_ok=True)
    if log_root.is_symlink() or not log_root.is_dir():
        raise EvidenceError("E_PILOT_BUILD_PATH", "log-root is unsafe")
    return log_root


def write_process_identity(
    log_root: Path,
    spec: dict[str, Any],
    pid: int,
    pgid: int,
    starttime: str,
) -> None:
    payload = {
        "job_id": spec["job_id"],
        "pid": pid,
        "pgid": pgid,
        "starttime": starttime,
    }
    write_canonical_json(log_root / f"{spec['job_id']}.identity.json", payload, exclusive=True)


def load_process_identities(log_root: Path) -> list[dict[str, Any]]:
    if not log_root.is_dir():
        return []
    records = []
    for path in sorted(log_root.glob("*.identity.json")):
        raw, _digest = read_authority_snapshot(path, "process-identity")
        records.append(parse_canonical_json_object(raw, "process-identity"))
    return records


def child_records_are_live(records: list[dict[str, Any]]) -> bool:
    for record in records:
        if attempt_is_live(int(record["pid"]), str(record["starttime"])):
            return True
        if process_group_has_members(int(record["pgid"])):
            return True
    return False


def terminate_and_reap_process_group(pgid: int | None, proc: Any) -> None:
    controller_pgid = os.getpgrp()
    still_running = proc is not None and proc.poll() is None
    own_group = pgid is not None and pgid == controller_pgid
    if own_group and (proc is None or proc.pid == os.getpid()):
        return
    if still_running and pgid is not None:
        try:
            os.killpg(pgid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    if proc is not None:
        try:
            proc.communicate(timeout=5)
        except Exception:
            try:
                proc.wait(timeout=5)
            except Exception:
                pass
    if pgid is not None and not own_group and process_group_has_members(pgid):
        try:
            os.killpg(pgid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        deadline = time.monotonic() + 2
        while time.monotonic() < deadline and process_group_has_members(pgid):
            time.sleep(0.05)



def validate_implementation_verdict(
    value: object, plan_sha256: str, plan_verdict_sha256: str
) -> dict[str, Any]:
    validated = validate_exact_object(
        value,
        IMPLEMENTATION_VERDICT_EXACT,
        "build-preflight-implementation-verdict",
    )
    for key in (
        "reviewed_plan_sha256",
        "reviewed_plan_verdict_sha256",
        "reviewed_pilot_build_sha256",
        "reviewed_pilot_cli_sha256",
        "reviewed_test_pilot_build_sha256",
        "reviewed_test_pilot_sha256",
    ):
        validate_sha256(validated[key], f"implementation-verdict.{key}")
    if GIT_OID_RE.fullmatch(validated["reviewed_commit"]) is None:
        raise EvidenceError(
            "E_PILOT_BUILD_IMPL_VERDICT",
            "reviewed_commit is not 40 lowercase hexadecimal characters",
        )
    if validated["reviewed_plan_path"] != PLAN_PATH.as_posix():
        raise EvidenceError("E_PILOT_BUILD_IMPL_VERDICT", "reviewed plan path differs")
    if validated["reviewed_plan_sha256"] != plan_sha256:
        raise EvidenceError("E_PILOT_BUILD_IMPL_VERDICT", "reviewed plan hash differs")
    if validated["reviewed_plan_verdict_sha256"] != plan_verdict_sha256:
        raise EvidenceError("E_PILOT_BUILD_IMPL_VERDICT", "plan verdict hash differs")
    for path_key, _sha_key, expected in REVIEWED_IMPLEMENTATION_FILES:
        if validated[path_key] != expected:
            raise EvidenceError(
                "E_PILOT_BUILD_IMPL_VERDICT",
                f"{path_key} differs",
            )
    if validated["verdict"] != "PASS":
        raise EvidenceError("E_PILOT_BUILD_IMPL_VERDICT", "verdict is not PASS")
    if validated["authorized_state"] != "PILOT_BUILD_PREFLIGHT_IMPLEMENTATION_PASS":
        raise EvidenceError("E_PILOT_BUILD_IMPL_VERDICT", "authorized_state differs")
    if validated["claims"] != "blocked":
        raise EvidenceError("E_PILOT_BUILD_IMPL_VERDICT", "claims are not blocked")
    return validated


def verify_reviewed_production_bytes(verdict: dict[str, Any]) -> None:
    for path_key, sha_key, expected in REVIEWED_IMPLEMENTATION_FILES:
        if verdict[path_key] != expected:
            raise EvidenceError("E_PILOT_BUILD_PRODUCTION_BYTES", f"{path_key} differs")
        raw, digest = read_authority_snapshot(Path(expected), path_key)
        if digest != verdict[sha_key]:
            raise EvidenceError(
                "E_PILOT_BUILD_PRODUCTION_BYTES",
                f"{expected} drifted from the implementation verdict",
            )
        if _sha256_bytes(raw) != digest:
            raise EvidenceError("E_PILOT_BUILD_PRODUCTION_BYTES", "snapshot hash drifted")


def validate_environment_snapshot(value: object) -> dict[str, Any]:
    validated = validate_exact_object(
        value,
        BUILD_PREFLIGHT_ENVIRONMENT_EXACT,
        "p3-pilot-build-preflight-environment-v1",
    )
    reject_confirmatory_pilot(validated, "build-preflight-environment")
    if validated["schema_version"] != "p3-pilot-build-preflight-environment-v1":
        raise EvidenceError("E_PILOT_BUILD_ENVIRONMENT", "schema differs")
    if validated["execution_class"] != PILOT_EXECUTION_CLASS:
        raise EvidenceError("E_PILOT_BUILD_ENVIRONMENT", "class differs")
    if validated["denominator"] != PILOT_DENOMINATOR:
        raise EvidenceError("E_PILOT_BUILD_ENVIRONMENT", "denominator differs")
    if validated["claims"] != "blocked":
        raise EvidenceError("E_PILOT_BUILD_ENVIRONMENT", "claims are not blocked")
    if validated["system_boost_fallback_accepted"] is not False:
        raise EvidenceError("E_PILOT_BUILD_ENVIRONMENT", "system Boost fallback accepted")
    if validated["fetchcontent_fully_disconnected"] is not True:
        raise EvidenceError("E_PILOT_BUILD_ENVIRONMENT", "FetchContent is not disconnected")
    if validated["cuda_absence_blocking"] is not False:
        raise EvidenceError("E_PILOT_BUILD_ENVIRONMENT", "CUDA absence must be non-blocking")
    if validated["native_profiling_present"] is not False:
        raise EvidenceError("E_PILOT_BUILD_ENVIRONMENT", "profiling is not a prerequisite")
    if validated["disconnected_environment"] != DISCONNECTED_ENVIRONMENT:
        raise EvidenceError("E_PILOT_BUILD_ENVIRONMENT", "disconnected environment differs")
    if validated["cmake_generator"] != FROZEN_CMAKE_GENERATOR:
        raise EvidenceError("E_PILOT_BUILD_ENVIRONMENT", "generator differs")
    if validated["build_parallelism"] != BUILD_PARALLELISM:
        raise EvidenceError("E_PILOT_BUILD_ENVIRONMENT", "parallelism differs")
    if not validated["cmake_executable_path"] or not validated["cmake_version"]:
        raise EvidenceError("E_PILOT_BUILD_ENVIRONMENT", "cmake identity is incomplete")
    body = {key: validated[key] for key in validated if key != "artifact_sha256"}
    if validated["artifact_sha256"] != canonical_sha256(body):
        raise EvidenceError("E_PILOT_BUILD_ENVIRONMENT", "self-hash differs")
    return validated


def _require_stdio(validated: dict[str, Any]) -> None:
    if validated["stdout_sha256"] is None or validated["stderr_sha256"] is None:
        raise EvidenceError("E_PILOT_BUILD_JOB", "started job must hash stdio")
    validate_sha256(validated["stdout_sha256"], "job.stdout_sha256")
    validate_sha256(validated["stderr_sha256"], "job.stderr_sha256")
    if type(validated["stdout_bytes"]) is not int or validated["stdout_bytes"] < 0:
        raise EvidenceError("E_PILOT_BUILD_JOB", "stdout_bytes is invalid")
    if type(validated["stderr_bytes"]) is not int or validated["stderr_bytes"] < 0:
        raise EvidenceError("E_PILOT_BUILD_JOB", "stderr_bytes is invalid")
    if validated["started_at"] is None or validated["ended_at"] is None:
        raise EvidenceError("E_PILOT_BUILD_JOB", "started job must have timestamps")
    if validated["wall_seconds"] is None:
        raise EvidenceError("E_PILOT_BUILD_JOB", "started job must have wall time")
    if validated["cpu_seconds"] is None or validated["peak_rss_bytes"] is None:
        raise EvidenceError("E_PILOT_BUILD_JOB", "started job must have rusage")


def _require_no_process_evidence(validated: dict[str, Any]) -> None:
    if validated["exit_code"] is not None:
        raise EvidenceError("E_PILOT_BUILD_JOB", "unstarted job must not have exit_code")
    if validated["stdout_sha256"] is not None or validated["stderr_sha256"] is not None:
        raise EvidenceError("E_PILOT_BUILD_JOB", "unstarted job must not forge hashes")
    if validated["stdout_bytes"] is not None or validated["stderr_bytes"] is not None:
        raise EvidenceError("E_PILOT_BUILD_JOB", "unstarted job must not forge byte counts")
    if validated["wall_seconds"] is not None:
        raise EvidenceError("E_PILOT_BUILD_JOB", "unstarted job must not have wall time")
    if validated["cpu_seconds"] is not None or validated["peak_rss_bytes"] is not None:
        raise EvidenceError("E_PILOT_BUILD_JOB", "unstarted job must not have rusage")
    if validated["process_group_terminated"] is not None:
        raise EvidenceError("E_PILOT_BUILD_JOB", "unstarted job must not claim a process group")


def validate_job_result(value: object) -> dict[str, Any]:
    validated = validate_exact_object(
        value,
        BUILD_PREFLIGHT_JOB_RESULT_EXACT,
        "p3-pilot-build-preflight-job-result-v1",
    )
    if validated["schema_version"] != "p3-pilot-build-preflight-job-result-v1":
        raise EvidenceError("E_PILOT_BUILD_JOB", "schema differs")
    if validated["execution_class"] != PILOT_EXECUTION_CLASS:
        raise EvidenceError("E_PILOT_BUILD_JOB", "class differs")
    if validated["denominator"] != PILOT_DENOMINATOR:
        raise EvidenceError("E_PILOT_BUILD_JOB", "denominator differs")
    if validated["claims"] != "blocked":
        raise EvidenceError("E_PILOT_BUILD_JOB", "claims are not blocked")
    if validated["terminal_status"] not in ALL_TERMINAL:
        raise EvidenceError("E_PILOT_BUILD_JOB", "terminal status differs")
    if type(validated["argv"]) is not list or any(
        type(item) is not str for item in validated["argv"]
    ):
        raise EvidenceError("E_PILOT_BUILD_JOB", "argv is invalid")
    if type(validated["dependency_job_ids"]) is not list or any(
        type(item) is not str for item in validated["dependency_job_ids"]
    ):
        raise EvidenceError("E_PILOT_BUILD_JOB", "dependency_job_ids are invalid")
    status = validated["terminal_status"]
    if status == "PASS":
        if validated["process_started"] is not True:
            raise EvidenceError("E_PILOT_BUILD_JOB", "PASS must start a process")
        if validated["exit_code"] != 0:
            raise EvidenceError("E_PILOT_BUILD_JOB", "PASS must have exit_code 0")
        if validated["failure_reason"] is not None:
            raise EvidenceError("E_PILOT_BUILD_JOB", "PASS must not carry a failure")
        if validated["infrastructure_phase"] is not None:
            raise EvidenceError("E_PILOT_BUILD_JOB", "PASS must not set infrastructure_phase")
        if validated["process_group_terminated"] is not False:
            raise EvidenceError("E_PILOT_BUILD_JOB", "PASS must not kill the process group")
        _require_stdio(validated)
    elif status == "FAIL":
        if validated["process_started"] is not True:
            raise EvidenceError("E_PILOT_BUILD_JOB", "FAIL must start a process")
        if validated["failure_reason"] not in FAIL_REASONS:
            raise EvidenceError("E_PILOT_BUILD_JOB", "FAIL reason is not frozen")
        if validated["failure_reason"] == "NONZERO_EXIT" and (
            validated["exit_code"] is None or validated["exit_code"] == 0
        ):
            raise EvidenceError("E_PILOT_BUILD_JOB", "NONZERO_EXIT must have a nonzero exit")
        if validated["failure_reason"] == "CRASH" and validated["exit_code"] is not None:
            raise EvidenceError("E_PILOT_BUILD_JOB", "CRASH must not invent exit_code")
        if validated["infrastructure_phase"] is not None:
            raise EvidenceError("E_PILOT_BUILD_JOB", "FAIL must not set infrastructure_phase")
        _require_stdio(validated)
    elif status == "TIMEOUT":
        if validated["process_started"] is not True:
            raise EvidenceError("E_PILOT_BUILD_JOB", "TIMEOUT must start a process")
        if validated["exit_code"] is not None:
            raise EvidenceError("E_PILOT_BUILD_JOB", "TIMEOUT must have null exit_code")
        if validated["failure_reason"] != "TIMEOUT":
            raise EvidenceError("E_PILOT_BUILD_JOB", "TIMEOUT reason differs")
        if validated["process_group_terminated"] is not True:
            raise EvidenceError("E_PILOT_BUILD_JOB", "TIMEOUT must terminate the process group")
        if validated["infrastructure_phase"] is not None:
            raise EvidenceError("E_PILOT_BUILD_JOB", "TIMEOUT must not set infrastructure_phase")
        _require_stdio(validated)
    elif status == "FAIL_INFRASTRUCTURE":
        if validated["infrastructure_phase"] not in {"PRE_PROCESS", "POST_PROCESS"}:
            raise EvidenceError("E_PILOT_BUILD_JOB", "infrastructure_phase differs")
        if validated["infrastructure_phase"] == "PRE_PROCESS":
            if validated["process_started"] is not False:
                raise EvidenceError("E_PILOT_BUILD_JOB", "PRE_PROCESS must not start")
            if validated["failure_reason"] not in INFRA_REASONS_PRE_PROCESS:
                raise EvidenceError("E_PILOT_BUILD_JOB", "PRE_PROCESS reason is not frozen")
            _require_no_process_evidence(validated)
        else:
            if validated["process_started"] is not True:
                raise EvidenceError("E_PILOT_BUILD_JOB", "POST_PROCESS must start")
            if validated["failure_reason"] not in INFRA_REASONS_POST_PROCESS:
                raise EvidenceError("E_PILOT_BUILD_JOB", "POST_PROCESS reason is not frozen")
            _require_stdio(validated)
    elif status == "NOT_STARTED":
        if validated["process_started"] is not False:
            raise EvidenceError("E_PILOT_BUILD_JOB", "NOT_STARTED must not start")
        if validated["failure_reason"] != "DEPENDENCY_NOT_STARTED":
            raise EvidenceError("E_PILOT_BUILD_JOB", "NOT_STARTED reason differs")
        if validated["infrastructure_phase"] is not None:
            raise EvidenceError("E_PILOT_BUILD_JOB", "NOT_STARTED must not set infrastructure_phase")
        if validated["started_at"] is not None or validated["ended_at"] is not None:
            raise EvidenceError("E_PILOT_BUILD_JOB", "NOT_STARTED must not have timestamps")
        _require_no_process_evidence(validated)
    body = {key: validated[key] for key in validated if key != "artifact_sha256"}
    if validated["artifact_sha256"] != canonical_sha256(body):
        raise EvidenceError("E_PILOT_BUILD_JOB", "self-hash differs")
    return validated


def validate_intent(value: object) -> dict[str, Any]:
    validated = validate_exact_object(
        value, BUILD_PREFLIGHT_INTENT_EXACT, "p3-pilot-build-preflight-intent-v1"
    )
    if validated["schema_version"] != "p3-pilot-build-preflight-intent-v1":
        raise EvidenceError("E_PILOT_BUILD_INTENT", "schema differs")
    if validated["execution_class"] != PILOT_EXECUTION_CLASS:
        raise EvidenceError("E_PILOT_BUILD_INTENT", "class differs")
    if validated["denominator"] != PILOT_DENOMINATOR:
        raise EvidenceError("E_PILOT_BUILD_INTENT", "denominator differs")
    if validated["plan_class"] != "PILOT_BUILD_PREFLIGHT_ONLY":
        raise EvidenceError("E_PILOT_BUILD_INTENT", "plan class differs")
    if validated["claims"] != "blocked":
        raise EvidenceError("E_PILOT_BUILD_INTENT", "claims are not blocked")
    if validated["formal_denominator_membership"] is not False:
        raise EvidenceError("E_PILOT_BUILD_INTENT", "denominator membership must be false")
    if validated["rq4_supported"] is not False:
        raise EvidenceError("E_PILOT_BUILD_INTENT", "rq4_supported must be false")
    if validated["no_retry"] is not True:
        raise EvidenceError("E_PILOT_BUILD_INTENT", "no_retry must be true")
    if validated["planned_count"] != PLANNED_COUNT:
        raise EvidenceError("E_PILOT_BUILD_INTENT", "planned_count must be 3")
    if validated["build_parallelism"] != BUILD_PARALLELISM:
        raise EvidenceError("E_PILOT_BUILD_INTENT", "parallelism must be 4")
    if validated["cmake_configure_timeout_seconds"] != CMAKE_CONFIGURE_TIMEOUT_SECONDS:
        raise EvidenceError("E_PILOT_BUILD_INTENT", "configure timeout differs")
    if validated["baseline_build_timeout_seconds"] != BASELINE_BUILD_TIMEOUT_SECONDS:
        raise EvidenceError("E_PILOT_BUILD_INTENT", "build timeout differs")
    if validated["baseline_smoke_timeout_seconds"] != BASELINE_SMOKE_TIMEOUT_SECONDS:
        raise EvidenceError("E_PILOT_BUILD_INTENT", "smoke timeout differs")
    if validated["outer_timeout_seconds"] != OUTER_TIMEOUT_SECONDS:
        raise EvidenceError("E_PILOT_BUILD_INTENT", "outer timeout differs")
    snapshot = validate_environment_snapshot(validated["environment_snapshot"])
    if snapshot["artifact_sha256"] != validated["environment_snapshot_sha256"]:
        raise EvidenceError("E_PILOT_BUILD_INTENT", "environment snapshot hash differs")
    if validated["cmake_configure_argv"] != bind_configure_argv(
        snapshot["cmake_executable_path"], snapshot["cxx_compiler_path"]
    ):
        raise EvidenceError("E_PILOT_BUILD_INTENT", "configure argv differs")
    if validated["baseline_build_argv"] != bind_build_argv(snapshot["cmake_executable_path"]):
        raise EvidenceError("E_PILOT_BUILD_INTENT", "build argv differs")
    if validated["baseline_smoke_argv"] != BASELINE_SMOKE_ARGV:
        raise EvidenceError("E_PILOT_BUILD_INTENT", "smoke argv differs")
    if validated["dependency_dag"] != DEPENDENCY_DAG:
        raise EvidenceError("E_PILOT_BUILD_INTENT", "dependency dag differs")
    if validated["source_root"] != FROZEN_SOURCE_ROOT.as_posix():
        raise EvidenceError("E_PILOT_BUILD_INTENT", "source root differs")
    if validated["build_root"] != FROZEN_BUILD_ROOT.as_posix():
        raise EvidenceError("E_PILOT_BUILD_INTENT", "build root differs")
    if validated["harness_root"] != FROZEN_HARNESS_ROOT.as_posix():
        raise EvidenceError("E_PILOT_BUILD_INTENT", "harness root differs")
    if validated["authorization_sha256"] != AUTHORIZATION_SHA256:
        raise EvidenceError("E_PILOT_BUILD_INTENT", "authorization hash differs")
    if validated["harness_cmake_sha256"] != HARNESS_CMAKE_SHA256:
        raise EvidenceError("E_PILOT_BUILD_INTENT", "harness cmake hash differs")
    if validated["harness_cxx_sha256"] != HARNESS_CXX_SHA256:
        raise EvidenceError("E_PILOT_BUILD_INTENT", "harness cxx hash differs")
    if validated["normalized_source_tree_sha256"] != FROZEN_NORMALIZED_SOURCE_TREE_SHA256:
        raise EvidenceError("E_PILOT_BUILD_INTENT", "tree hash differs")
    if (
        validated["source_preparation_verdict_sha256"]
        != SOURCE_PREPARATION_RESULT_VERDICT_SHA256
    ):
        raise EvidenceError("E_PILOT_BUILD_INTENT", "source-preparation verdict differs")
    if validated["source_manifest_sha256"] != SOURCE_MANIFEST_FILE_SHA256:
        raise EvidenceError("E_PILOT_BUILD_INTENT", "source manifest hash differs")
    if validated["source_preparation_result_sha256"] != SOURCE_PREPARATION_RESULT_FILE_SHA256:
        raise EvidenceError("E_PILOT_BUILD_INTENT", "source-preparation result differs")
    validate_sha256(
        validated["implementation_verdict_sha256"],
        "intent.implementation_verdict_sha256",
    )
    if validated["implementation_verdict_sha256"] not in validated["predecessor_sha256"]:
        raise EvidenceError(
            "E_PILOT_BUILD_INTENT",
            "predecessor_sha256 must contain implementation_verdict_sha256",
        )
    body = {key: validated[key] for key in validated if key != "artifact_sha256"}
    if validated["artifact_sha256"] != canonical_sha256(body):
        raise EvidenceError("E_PILOT_BUILD_INTENT", "self-hash differs")
    return validated


def validate_result(value: object) -> dict[str, Any]:
    validated = validate_exact_object(
        value, BUILD_PREFLIGHT_RESULT_EXACT, "p3-pilot-build-preflight-result-v1"
    )
    if validated["schema_version"] != "p3-pilot-build-preflight-result-v1":
        raise EvidenceError("E_PILOT_BUILD_RESULT", "schema differs")
    if validated["execution_class"] != PILOT_EXECUTION_CLASS:
        raise EvidenceError("E_PILOT_BUILD_RESULT", "class differs")
    if validated["denominator"] != PILOT_DENOMINATOR:
        raise EvidenceError("E_PILOT_BUILD_RESULT", "denominator differs")
    if validated["claims"] != "blocked":
        raise EvidenceError("E_PILOT_BUILD_RESULT", "claims are not blocked")
    if validated["formal_denominator_membership"] is not False:
        raise EvidenceError("E_PILOT_BUILD_RESULT", "denominator membership must be false")
    if validated["rq4_supported"] is not False:
        raise EvidenceError("E_PILOT_BUILD_RESULT", "rq4_supported must be false")
    if validated["no_retry"] is not True:
        raise EvidenceError("E_PILOT_BUILD_RESULT", "no_retry must be true")
    if validated["planned_count"] != PLANNED_COUNT:
        raise EvidenceError("E_PILOT_BUILD_RESULT", "planned_count must be 3")
    if validated["terminal_count"] != PLANNED_COUNT:
        raise EvidenceError("E_PILOT_BUILD_RESULT", "terminal_count must be 3")
    if type(validated["jobs"]) is not list or len(validated["jobs"]) != 3:
        raise EvidenceError("E_PILOT_BUILD_RESULT", "jobs must be exactly 3")
    jobs = [validate_job_result(item) for item in validated["jobs"]]
    order = [item["job_id"] for item in jobs]
    if order != ["CMAKE_CONFIGURE", "BASELINE_BUILD", "BASELINE_SMOKE"]:
        raise EvidenceError("E_PILOT_BUILD_RESULT", "job order differs")
    started = sum(1 for item in jobs if item["process_started"] is True)
    not_started = sum(1 for item in jobs if item["terminal_status"] == "NOT_STARTED")
    if validated["started_count"] != started:
        raise EvidenceError("E_PILOT_BUILD_RESULT", "started_count is not conserved")
    if validated["not_started_count"] != not_started:
        raise EvidenceError("E_PILOT_BUILD_RESULT", "not_started_count is not conserved")
    for job, spec in zip(jobs, JOB_SPECS, strict=True):
        if job["job_id"] != spec["job_id"] or job["job_kind"] != spec["job_kind"]:
            raise EvidenceError("E_PILOT_BUILD_RESULT", "job identity differs")
        if job["dependency_job_ids"] != list(spec["dependency_job_ids"]):
            raise EvidenceError("E_PILOT_BUILD_RESULT", "job dependencies differ")
        if job["timeout_seconds"] != spec["timeout_seconds"]:
            raise EvidenceError("E_PILOT_BUILD_RESULT", "job timeout differs")
    if jobs[0]["terminal_status"] != "PASS":
        if jobs[1]["terminal_status"] != "NOT_STARTED" or jobs[2]["terminal_status"] != "NOT_STARTED":
            raise EvidenceError("E_PILOT_BUILD_RESULT", "configure failure must block dependents")
    elif jobs[1]["terminal_status"] != "PASS":
        if jobs[2]["terminal_status"] != "NOT_STARTED":
            raise EvidenceError("E_PILOT_BUILD_RESULT", "build failure must block smoke")
    first_bad = next((item for item in jobs if item["terminal_status"] != "PASS"), None)
    if first_bad is None:
        if validated["terminal_status"] != "PASS" or validated["failure_reason"] is not None:
            raise EvidenceError("E_PILOT_BUILD_RESULT", "all-PASS aggregate differs")
    else:
        if validated["terminal_status"] != first_bad["terminal_status"]:
            raise EvidenceError("E_PILOT_BUILD_RESULT", "aggregate status differs")
        if validated["failure_reason"] != first_bad["failure_reason"]:
            raise EvidenceError("E_PILOT_BUILD_RESULT", "aggregate failure_reason differs")
    if jobs[1]["terminal_status"] == "PASS":
        for key in (
            "cmake_cache_sha256",
            "compile_commands_sha256",
            "compiler_depfile_sha256",
            "dependency_list_sha256",
            "smoke_executable_sha256",
        ):
            validate_sha256(validated[key], f"result.{key}")
    elif first_bad is not None and jobs[1]["terminal_status"] != "PASS":
        for key in (
            "cmake_cache_sha256",
            "compile_commands_sha256",
            "compiler_depfile_sha256",
            "dependency_list_sha256",
            "smoke_executable_sha256",
        ):
            if validated[key] is not None:
                raise EvidenceError("E_PILOT_BUILD_RESULT", f"{key} must be null")
    snapshot = validate_environment_snapshot(validated["environment_snapshot"])
    if snapshot["artifact_sha256"] != validated["environment_snapshot_sha256"]:
        raise EvidenceError("E_PILOT_BUILD_RESULT", "environment snapshot hash differs")
    validate_sha256(
        validated["implementation_verdict_sha256"],
        "result.implementation_verdict_sha256",
    )
    if validated["implementation_verdict_sha256"] not in validated["predecessor_sha256"]:
        raise EvidenceError(
            "E_PILOT_BUILD_RESULT",
            "predecessor_sha256 must contain implementation_verdict_sha256",
        )
    body = {key: validated[key] for key in validated if key != "artifact_sha256"}
    if validated["artifact_sha256"] != canonical_sha256(body):
        raise EvidenceError("E_PILOT_BUILD_RESULT", "self-hash differs")
    return validated


def validate_attempt_pair(
    intent: object, intent_file_sha256: str, result: object
) -> tuple[dict[str, Any], dict[str, Any]]:
    validated_intent = validate_intent(intent)
    validated_result = validate_result(result)
    validate_sha256(intent_file_sha256, "attempt.intent_file_sha256")
    if validated_result["intent_sha256"] != intent_file_sha256:
        raise EvidenceError("E_PILOT_BUILD_PAIR", "intent file SHA differs")
    if validated_result["environment_snapshot"] != validated_intent["environment_snapshot"]:
        raise EvidenceError("E_PILOT_BUILD_PAIR", "environment snapshot differs")
    if (
        validated_result["environment_snapshot_sha256"]
        != validated_intent["environment_snapshot_sha256"]
    ):
        raise EvidenceError("E_PILOT_BUILD_PAIR", "environment snapshot hash differs")
    if (
        validated_result["implementation_verdict_sha256"]
        != validated_intent["implementation_verdict_sha256"]
    ):
        raise EvidenceError("E_PILOT_BUILD_PAIR", "implementation verdict SHA differs")
    for key in (
        "source_preparation_verdict_sha256",
        "source_manifest_sha256",
        "source_preparation_result_sha256",
        "normalized_source_tree_sha256",
        "controlled_subject_id",
        "controlled_subject_source_id",
        "build_descriptor_sha256",
        "authorization_sha256",
        "harness_cmake_sha256",
        "harness_cxx_sha256",
        "source_root",
        "build_root",
        "harness_root",
    ):
        if validated_result[key] != validated_intent[key]:
            raise EvidenceError("E_PILOT_BUILD_PAIR", f"{key} differs")
    expected_predecessor = sorted(
        [intent_file_sha256, *validated_intent["predecessor_sha256"]]
    )
    if validated_result["predecessor_sha256"] != expected_predecessor:
        raise EvidenceError("E_PILOT_BUILD_PAIR", "predecessor set differs")
    expected_argvs = [
        validated_intent["cmake_configure_argv"],
        validated_intent["baseline_build_argv"],
        validated_intent["baseline_smoke_argv"],
    ]
    expected_timeouts = [
        validated_intent["cmake_configure_timeout_seconds"],
        validated_intent["baseline_build_timeout_seconds"],
        validated_intent["baseline_smoke_timeout_seconds"],
    ]
    for job, argv, timeout, spec in zip(
        validated_result["jobs"], expected_argvs, expected_timeouts, JOB_SPECS, strict=True
    ):
        if job["argv"] != argv:
            raise EvidenceError("E_PILOT_BUILD_PAIR", "job argv differs from intent")
        if job["timeout_seconds"] != timeout:
            raise EvidenceError("E_PILOT_BUILD_PAIR", "job timeout differs from intent")
        if job["dependency_job_ids"] != list(spec["dependency_job_ids"]):
            raise EvidenceError("E_PILOT_BUILD_PAIR", "job DAG differs from intent")
    return validated_intent, validated_result


def make_not_started_job(spec: dict[str, Any]) -> dict[str, Any]:
    payload = {
        "schema_version": "p3-pilot-build-preflight-job-result-v1",
        "execution_class": PILOT_EXECUTION_CLASS,
        "denominator": PILOT_DENOMINATOR,
        "job_id": spec["job_id"],
        "job_kind": spec["job_kind"],
        "dependency_job_ids": list(spec["dependency_job_ids"]),
        "argv": list(spec["argv"]),
        "timeout_seconds": spec["timeout_seconds"],
        "process_started": False,
        "process_group_terminated": None,
        "infrastructure_phase": None,
        "terminal_status": "NOT_STARTED",
        "failure_reason": "DEPENDENCY_NOT_STARTED",
        "exit_code": None,
        "stdout_sha256": None,
        "stderr_sha256": None,
        "stdout_bytes": None,
        "stderr_bytes": None,
        "started_at": None,
        "ended_at": None,
        "wall_seconds": None,
        "cpu_seconds": None,
        "peak_rss_bytes": None,
        "claims": "blocked",
    }
    return validate_job_result(_self_hash(payload))


def make_pre_process_infra_job(spec: dict[str, Any], reason: str) -> dict[str, Any]:
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    payload = {
        "schema_version": "p3-pilot-build-preflight-job-result-v1",
        "execution_class": PILOT_EXECUTION_CLASS,
        "denominator": PILOT_DENOMINATOR,
        "job_id": spec["job_id"],
        "job_kind": spec["job_kind"],
        "dependency_job_ids": list(spec["dependency_job_ids"]),
        "argv": list(spec["argv"]),
        "timeout_seconds": spec["timeout_seconds"],
        "process_started": False,
        "process_group_terminated": None,
        "infrastructure_phase": "PRE_PROCESS",
        "terminal_status": "FAIL_INFRASTRUCTURE",
        "failure_reason": reason,
        "exit_code": None,
        "stdout_sha256": None,
        "stderr_sha256": None,
        "stdout_bytes": None,
        "stderr_bytes": None,
        "started_at": now,
        "ended_at": now,
        "wall_seconds": None,
        "cpu_seconds": None,
        "peak_rss_bytes": None,
        "claims": "blocked",
    }
    return validate_job_result(_self_hash(payload))


def make_environment_snapshot() -> dict[str, Any]:
    cmake_path = shutil.which("cmake")
    cxx_path = shutil.which("c++") or shutil.which("g++")
    if cmake_path is None:
        raise EvidenceError("E_PILOT_MISSING_DEPENDENCY", "MISSING_DEPENDENCY")
    cmake_version = probe_identity(cmake_path)
    if cmake_version is None:
        raise EvidenceError("E_PILOT_MISSING_DEPENDENCY", "MISSING_DEPENDENCY")
    cxx_identity = probe_identity(cxx_path)
    payload = {
        "schema_version": "p3-pilot-build-preflight-environment-v1",
        "execution_class": PILOT_EXECUTION_CLASS,
        "denominator": PILOT_DENOMINATOR,
        "cmake_executable": "cmake",
        "cmake_executable_path": cmake_path,
        "cmake_version": cmake_version,
        "cxx_compiler_executable": None if cxx_path is None else Path(cxx_path).name,
        "cxx_compiler_path": cxx_path,
        "cxx_compiler_identity": cxx_identity,
        "cxx_compiler_version": cxx_identity,
        "cmake_generator": FROZEN_CMAKE_GENERATOR,
        "os_name": platform.system(),
        "os_release": platform.release(),
        "python_version": platform.python_version(),
        "git_version": probe_identity(shutil.which("git")),
        "build_parallelism": BUILD_PARALLELISM,
        "nvcc_present": shutil.which("nvcc") is not None,
        "native_profiling_present": False,
        "cuda_absence_blocking": False,
        "fetchcontent_fully_disconnected": True,
        "system_boost_fallback_accepted": False,
        "disconnected_environment": dict(DISCONNECTED_ENVIRONMENT),
        "claims": "blocked",
    }
    return validate_environment_snapshot(_self_hash(payload))


def collect_baseline_build_evidence(
    build_root: Path,
    environment: dict[str, Any],
) -> dict[str, str]:
    cache = build_root / "CMakeCache.txt"
    commands = build_root / "compile_commands.json"
    executable = build_root / "boost_math_pilot_smoke"
    dep_file = build_root / COMPILER_DEPFILE_RELATIVE
    for path in (cache, commands, executable, dep_file):
        if path.is_symlink() or not path.is_file():
            raise EvidenceError("E_PILOT_MISSING_DEPENDENCY", "UNSUPPORTED_TOOLCHAIN")
        raw, _mode = read_regular_file_snapshot(path, path.name)
        if path == dep_file:
            dep_raw = raw
    cache_text = cache.read_text(encoding="utf-8")
    values = parse_cmake_cache(cache_text)
    if values.get("CMAKE_GENERATOR") != FROZEN_CMAKE_GENERATOR:
        raise EvidenceError("E_PILOT_BUILD_ENVIRONMENT", "CMAKE_GENERATOR differs")
    compiler = environment["cxx_compiler_path"]
    if compiler is None:
        raise EvidenceError("E_PILOT_MISSING_DEPENDENCY", "MISSING_DEPENDENCY")
    cache_compiler = values.get("CMAKE_CXX_COMPILER")
    if cache_compiler is None or os.path.realpath(cache_compiler) != os.path.realpath(compiler):
        raise EvidenceError("E_PILOT_BUILD_ENVIRONMENT", "CMakeCache compiler differs")
    source_dir = values.get("CMAKE_HOME_DIRECTORY") or values.get("CMAKE_SOURCE_DIR")
    binary_dir = values.get("CMAKE_BINARY_DIR") or values.get("CMAKE_CACHEFILE_DIR")
    if source_dir != FROZEN_HARNESS_ROOT.as_posix():
        raise EvidenceError("E_PILOT_BUILD_ENVIRONMENT", "CMake source directory differs")
    if binary_dir != FROZEN_BUILD_ROOT.as_posix():
        raise EvidenceError("E_PILOT_BUILD_ENVIRONMENT", "CMake build directory differs")
    try:
        compile_db = json.loads(commands.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise EvidenceError("E_PILOT_MISSING_DEPENDENCY", "UNSUPPORTED_TOOLCHAIN") from exc
    if not isinstance(compile_db, list):
        raise EvidenceError("E_PILOT_MISSING_DEPENDENCY", "UNSUPPORTED_TOOLCHAIN")
    compile_argv = smoke_compile_argv(compile_db)
    if os.path.realpath(compile_argv[0]) != os.path.realpath(compiler):
        raise EvidenceError("E_PILOT_BUILD_ENVIRONMENT", "compile_commands compiler differs")
    joined = " ".join(compile_argv)
    if FROZEN_INCLUDE_PREFIX not in joined:
        raise EvidenceError("E_PILOT_MISSING_DEPENDENCY", "UNSUPPORTED_TOOLCHAIN")
    if "BOOST_MATH_STANDALONE=1" not in joined:
        raise EvidenceError("E_PILOT_MISSING_DEPENDENCY", "UNSUPPORTED_TOOLCHAIN")
    for marker in SYSTEM_BOOST_MARKERS:
        if marker in joined:
            raise EvidenceError("E_PILOT_SYSTEM_BOOST", "SYSTEM_BOOST_FALLBACK")
    dep_text = dep_raw.decode("utf-8")
    paths = parse_dependency_paths(dep_text)
    smoke_path = (FROZEN_HARNESS_ROOT / "smoke.cpp").as_posix()
    if smoke_path not in paths and "smoke.cpp" not in dep_text:
        raise EvidenceError("E_PILOT_MISSING_DEPENDENCY", "UNSUPPORTED_TOOLCHAIN")
    if FROZEN_CONSTANTS_HEADER not in paths and FROZEN_CONSTANTS_HEADER not in dep_text:
        raise EvidenceError("E_PILOT_MISSING_DEPENDENCY", "UNSUPPORTED_TOOLCHAIN")
    reject_nonfrozen_boost_headers(paths)
    return {
        "cmake_cache_sha256": _sha256_bytes(cache.read_bytes()),
        "compile_commands_sha256": _sha256_bytes(commands.read_bytes()),
        "compiler_depfile_sha256": _sha256_bytes(dep_raw),
        "dependency_list_sha256": _sha256_bytes(canonical_dependency_list_bytes(paths)),
        "smoke_executable_sha256": _sha256_bytes(executable.read_bytes()),
    }


def write_harness(harness_root: Path, cmake_bytes: bytes, cxx_bytes: bytes) -> None:
    require_absent_path(harness_root, "harness-root")
    try:
        os.mkdir(harness_root)
        cmake_path = harness_root / "CMakeLists.txt"
        cxx_path = harness_root / "smoke.cpp"
        cmake_path.write_bytes(cmake_bytes)
        cxx_path.write_bytes(cxx_bytes)
    except OSError as exc:
        raise EvidenceError("E_PILOT_BUILD_HARNESS", "HARNESS_PUBLICATION_FAILURE") from exc
    if _sha256_bytes(cmake_path.read_bytes()) != _sha256_bytes(cmake_bytes):
        raise EvidenceError("E_PILOT_BUILD_HARNESS", "HARNESS_PUBLICATION_FAILURE")
    if _sha256_bytes(cxx_path.read_bytes()) != _sha256_bytes(cxx_bytes):
        raise EvidenceError("E_PILOT_BUILD_HARNESS", "HARNESS_PUBLICATION_FAILURE")


def execute_job(
    spec: dict[str, Any],
    *,
    env: dict[str, str],
    log_root: Path,
    popen=subprocess.Popen,
    timeout_seconds: int | None = None,
) -> dict[str, Any]:
    reject_system_boost_environment(env)
    argv = list(spec["argv"])
    if any(not isinstance(item, str) for item in argv):
        raise EvidenceError("E_PILOT_BUILD_ARGV", "argv items must be strings")
    ensure_safe_log_root(log_root)
    started_at = time.time()
    effective_timeout = spec["timeout_seconds"] if timeout_seconds is None else timeout_seconds
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    proc = None
    pgid = None
    stdout = b""
    stderr = b""
    timed_out = False
    process_group_terminated = False
    try:
        proc = popen(
            argv,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False,
            env=env,
            start_new_session=True,
        )
    except FileNotFoundError:
        return make_pre_process_infra_job(spec, "MISSING_DEPENDENCY")
    try:
        try:
            pgid = os.getpgid(proc.pid)
        except ProcessLookupError:
            pgid = proc.pid
        starttime = read_proc_starttime(proc.pid)
        write_process_identity(log_root, spec, proc.pid, pgid, starttime)
        stdout, stderr = proc.communicate(timeout=effective_timeout)
    except subprocess.TimeoutExpired:
        timed_out = True
        process_group_terminated = True
        stdout, stderr = b"", b""
    finally:
        if pgid is not None:
            try:
                os.killpg(pgid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        terminate_and_reap_process_group(pgid, proc)
        if timed_out:
            process_group_terminated = True
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    stdout = stdout or b""
    stderr = stderr or b""
    try:
        (log_root / f"{spec['job_id']}.stdout").write_bytes(stdout)
        (log_root / f"{spec['job_id']}.stderr").write_bytes(stderr)
    except OSError as exc:
        raise EvidenceError("E_PILOT_BUILD_LOG", "LOG_PUBLICATION_FAILURE") from exc
    ended_at = time.time()
    detected = detect_network_or_boost(stdout, stderr, argv)
    exit_code = None if proc is None else proc.returncode
    cpu_seconds = float(
        (after.ru_utime + after.ru_stime) - (before.ru_utime + before.ru_stime)
    )
    peak_rss_bytes = int(after.ru_maxrss) * 1024
    if timed_out:
        terminal_status = "TIMEOUT"
        failure_reason = "TIMEOUT"
        recorded_exit = None
        infrastructure_phase = None
    elif detected == "NETWORK_OR_DOWNLOAD_ATTEMPT":
        terminal_status = "FAIL_INFRASTRUCTURE"
        failure_reason = "NETWORK_OR_DOWNLOAD_ATTEMPT"
        recorded_exit = exit_code
        infrastructure_phase = "POST_PROCESS"
    elif detected == "SYSTEM_BOOST_FALLBACK":
        terminal_status = "FAIL_INFRASTRUCTURE"
        failure_reason = "SYSTEM_BOOST_FALLBACK"
        recorded_exit = exit_code
        infrastructure_phase = "POST_PROCESS"
    elif exit_code == 0:
        terminal_status = "PASS"
        failure_reason = None
        recorded_exit = 0
        infrastructure_phase = None
    elif exit_code is None or exit_code < 0:
        terminal_status = "FAIL"
        failure_reason = "CRASH"
        recorded_exit = None
        infrastructure_phase = None
    else:
        terminal_status = "FAIL"
        failure_reason = "NONZERO_EXIT"
        recorded_exit = exit_code
        infrastructure_phase = None
    payload = {
        "schema_version": "p3-pilot-build-preflight-job-result-v1",
        "execution_class": PILOT_EXECUTION_CLASS,
        "denominator": PILOT_DENOMINATOR,
        "job_id": spec["job_id"],
        "job_kind": spec["job_kind"],
        "dependency_job_ids": list(spec["dependency_job_ids"]),
        "argv": argv,
        "timeout_seconds": spec["timeout_seconds"],
        "process_started": True,
        "process_group_terminated": process_group_terminated,
        "infrastructure_phase": infrastructure_phase,
        "terminal_status": terminal_status,
        "failure_reason": failure_reason,
        "exit_code": recorded_exit,
        "stdout_sha256": _sha256_bytes(stdout),
        "stderr_sha256": _sha256_bytes(stderr),
        "stdout_bytes": len(stdout),
        "stderr_bytes": len(stderr),
        "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(started_at)),
        "ended_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(ended_at)),
        "wall_seconds": float(ended_at - started_at),
        "cpu_seconds": cpu_seconds,
        "peak_rss_bytes": peak_rss_bytes,
        "claims": "blocked",
    }
    return validate_job_result(_self_hash(payload))


def run_three_jobs(
    specs: tuple[dict[str, Any], ...] | list[dict[str, Any]],
    *,
    env: dict[str, str],
    log_root: Path,
    popen=subprocess.Popen,
    source_root: Path | None = None,
    environment: dict[str, Any] | None = None,
    outer_deadline: float | None = None,
    expected_smoke_sha256: str | None = None,
    collect_evidence=None,
) -> tuple[list[dict[str, Any]], dict[str, str] | None]:
    if len(specs) != 3:
        raise EvidenceError("E_PILOT_BUILD_DAG", "planned_count must be 3")
    ids = [spec["job_id"] for spec in specs]
    if ids != ["CMAKE_CONFIGURE", "BASELINE_BUILD", "BASELINE_SMOKE"]:
        raise EvidenceError("E_PILOT_BUILD_DAG", "job order differs")
    results: list[dict[str, Any]] = []
    prior_pass = True
    tree_before = None
    evidence = None
    if source_root is not None:
        tree_before = require_frozen_source_tree(source_root)
    if environment is not None and environment["cxx_compiler_path"] is None:
        results.append(make_pre_process_infra_job(specs[0], "MISSING_DEPENDENCY"))
        results.append(make_not_started_job(specs[1]))
        results.append(make_not_started_job(specs[2]))
        return results, None
    for spec in specs:
        if not prior_pass:
            results.append(make_not_started_job(spec))
            continue
        remaining = None
        if outer_deadline is not None:
            remaining = outer_deadline - time.monotonic()
            if remaining <= 0:
                results.append(make_pre_process_infra_job(spec, "OUTER_DEADLINE_EXHAUSTED"))
                prior_pass = False
                continue
        timeout_seconds = spec["timeout_seconds"]
        if remaining is not None:
            timeout_seconds = min(timeout_seconds, max(1, int(remaining)))
        if spec["job_id"] == "BASELINE_SMOKE" and expected_smoke_sha256 is not None:
            executable = Path(spec["argv"][0])
            if (
                not executable.is_file()
                or _sha256_bytes(executable.read_bytes()) != expected_smoke_sha256
            ):
                results.append(make_pre_process_infra_job(spec, "MISSING_DEPENDENCY"))
                prior_pass = False
                continue
        result = execute_job(
            spec,
            env=env,
            log_root=log_root,
            popen=popen,
            timeout_seconds=timeout_seconds,
        )
        if source_root is not None:
            try:
                tree_after = require_frozen_source_tree(source_root)
                if tree_after != tree_before:
                    raise EvidenceError("E_PILOT_SOURCE_TREE_MISMATCH", "SOURCE_TREE_DRIFT")
            except EvidenceError:
                overlay = dict(result)
                overlay["terminal_status"] = "FAIL_INFRASTRUCTURE"
                overlay["failure_reason"] = "SOURCE_TREE_DRIFT"
                overlay["infrastructure_phase"] = "POST_PROCESS"
                overlay.pop("artifact_sha256", None)
                result = validate_job_result(_self_hash(overlay))
        if (
            spec["job_id"] == "BASELINE_BUILD"
            and result["terminal_status"] == "PASS"
            and collect_evidence is not None
            and environment is not None
        ):
            try:
                evidence = collect_evidence(FROZEN_BUILD_ROOT, environment)
                expected_smoke_sha256 = evidence["smoke_executable_sha256"]
            except EvidenceError as exc:
                reason = str(exc).split(":", 1)[-1].strip()
                if reason not in INFRA_REASONS_POST_PROCESS:
                    reason = "UNSUPPORTED_TOOLCHAIN"
                overlay = dict(result)
                overlay["terminal_status"] = "FAIL_INFRASTRUCTURE"
                overlay["failure_reason"] = reason
                overlay["infrastructure_phase"] = "POST_PROCESS"
                overlay.pop("artifact_sha256", None)
                result = validate_job_result(_self_hash(overlay))
        results.append(result)
        prior_pass = result["terminal_status"] == "PASS"
    return results, evidence


def _require_authorization() -> str:
    if not os.path.lexists(AUTHORIZATION_PATH):
        raise EvidenceError("E_PILOT_BUILD_AUTH_ABSENT", "authorization is absent")
    raw, digest = read_authority_snapshot(AUTHORIZATION_PATH, "build-preflight-auth")
    if raw != AUTHORIZATION_BYTES or digest != AUTHORIZATION_SHA256:
        raise EvidenceError("E_PILOT_BUILD_AUTH", "authorization bytes differ")
    return digest


def _require_source_preparation_identities() -> None:
    raw, digest = read_authority_snapshot(
        SOURCE_PREPARATION_RESULT_VERDICT_PATH,
        "source-preparation-result-verdict",
    )
    if digest != SOURCE_PREPARATION_RESULT_VERDICT_SHA256:
        raise EvidenceError(
            "E_PILOT_SOURCE_PREPARATION_RESULT_VERDICT",
            "source-preparation verdict hash differs",
        )
    validate_source_preparation_result_verdict(parse_canonical_json_object(raw, "verdict"))
    _manifest_raw, manifest_digest = read_authority_snapshot(
        SOURCE_MANIFEST_PATH, "source-manifest"
    )
    if manifest_digest != SOURCE_MANIFEST_FILE_SHA256:
        raise EvidenceError("E_PILOT_SOURCE_MANIFEST", "source manifest hash differs")
    _result_raw, result_digest = read_authority_snapshot(
        SOURCE_PREPARATION_RESULT_PATH, "source-preparation-result"
    )
    if result_digest != SOURCE_PREPARATION_RESULT_FILE_SHA256:
        raise EvidenceError(
            "E_PILOT_SOURCE_RESULT",
            "source-preparation result hash differs",
        )


def _require_plan_and_implementation_verdicts() -> tuple[str, str, str]:
    plan_raw, plan_digest = read_authority_snapshot(PLAN_PATH, "build-preflight-plan")
    verdict_raw, verdict_digest = read_authority_snapshot(
        PLAN_VERDICT_PATH, "build-preflight-plan-verdict"
    )
    validate_plan_verdict(parse_canonical_json_object(verdict_raw, "plan-verdict"), plan_digest)
    impl_raw, impl_digest = read_authority_snapshot(
        IMPLEMENTATION_VERDICT_PATH, "build-preflight-implementation-verdict"
    )
    impl_verdict = validate_implementation_verdict(
        parse_canonical_json_object(impl_raw, "implementation-verdict"),
        plan_digest,
        verdict_digest,
    )
    verify_reviewed_production_bytes(impl_verdict)
    return plan_digest, verdict_digest, impl_digest


def build_intent(
    environment: dict[str, Any],
    predecessor: list[str],
    implementation_verdict_sha256: str,
) -> dict[str, Any]:
    pid, starttime = producer_identity()
    payload = {
        "schema_version": "p3-pilot-build-preflight-intent-v1",
        "execution_class": PILOT_EXECUTION_CLASS,
        "denominator": PILOT_DENOMINATOR,
        "plan_class": "PILOT_BUILD_PREFLIGHT_ONLY",
        "p12_item_id": P12_ITEM_ID,
        "neutral_snapshot_id": NEUTRAL_SNAPSHOT_ID,
        "normalized_source_tree_sha256": FROZEN_NORMALIZED_SOURCE_TREE_SHA256,
        "controlled_subject_id": CONTROLLED_SUBJECT_ID,
        "controlled_subject_source_id": CONTROLLED_SUBJECT_SOURCE_ID,
        "build_descriptor_sha256": BUILD_DESCRIPTOR_SHA256,
        "source_preparation_verdict_sha256": SOURCE_PREPARATION_RESULT_VERDICT_SHA256,
        "source_manifest_sha256": SOURCE_MANIFEST_FILE_SHA256,
        "source_preparation_result_sha256": SOURCE_PREPARATION_RESULT_FILE_SHA256,
        "source_preparation_reviewed_commit": SOURCE_PREPARATION_REVIEWED_COMMIT,
        "implementation_verdict_sha256": implementation_verdict_sha256,
        "authorization_sha256": AUTHORIZATION_SHA256,
        "harness_cmake_sha256": HARNESS_CMAKE_SHA256,
        "harness_cxx_sha256": HARNESS_CXX_SHA256,
        "source_root": FROZEN_SOURCE_ROOT.as_posix(),
        "build_root": FROZEN_BUILD_ROOT.as_posix(),
        "harness_root": FROZEN_HARNESS_ROOT.as_posix(),
        "cmake_configure_argv": bind_configure_argv(
            environment["cmake_executable_path"], environment["cxx_compiler_path"]
        ),
        "baseline_build_argv": bind_build_argv(environment["cmake_executable_path"]),
        "baseline_smoke_argv": list(BASELINE_SMOKE_ARGV),
        "cmake_configure_timeout_seconds": CMAKE_CONFIGURE_TIMEOUT_SECONDS,
        "baseline_build_timeout_seconds": BASELINE_BUILD_TIMEOUT_SECONDS,
        "baseline_smoke_timeout_seconds": BASELINE_SMOKE_TIMEOUT_SECONDS,
        "outer_timeout_seconds": OUTER_TIMEOUT_SECONDS,
        "build_parallelism": BUILD_PARALLELISM,
        "planned_count": PLANNED_COUNT,
        "dependency_dag": [list(edge) for edge in DEPENDENCY_DAG],
        "environment_snapshot": environment,
        "environment_snapshot_sha256": environment["artifact_sha256"],
        "producer_pid": pid,
        "producer_starttime": starttime,
        "predecessor_sha256": list(predecessor),
        "no_retry": True,
        "claims": "blocked",
        "formal_denominator_membership": False,
        "rq4_supported": False,
    }
    return validate_intent(_self_hash(payload))


def build_result(
    *,
    intent_sha256: str,
    environment: dict[str, Any],
    jobs: list[dict[str, Any]],
    predecessor: list[str],
    implementation_verdict_sha256: str,
    evidence: dict[str, str] | None,
) -> dict[str, Any]:
    started = [job for job in jobs if job["process_started"] is True]
    not_started = [job for job in jobs if job["terminal_status"] == "NOT_STARTED"]
    first_bad = next((job for job in jobs if job["terminal_status"] != "PASS"), None)
    if first_bad is None:
        terminal_status = "PASS"
        failure_reason = None
        if evidence is None:
            raise EvidenceError("E_PILOT_BUILD_RESULT", "PASS must bind build artifacts")
        cache_sha = evidence["cmake_cache_sha256"]
        commands_sha = evidence["compile_commands_sha256"]
        depfile_sha = evidence["compiler_depfile_sha256"]
        dep_sha = evidence["dependency_list_sha256"]
        smoke_sha = evidence["smoke_executable_sha256"]
    else:
        terminal_status = first_bad["terminal_status"]
        failure_reason = first_bad["failure_reason"]
        cache_sha = None if evidence is None else evidence.get("cmake_cache_sha256")
        commands_sha = None if evidence is None else evidence.get("compile_commands_sha256")
        depfile_sha = None if evidence is None else evidence.get("compiler_depfile_sha256")
        dep_sha = None if evidence is None else evidence.get("dependency_list_sha256")
        smoke_sha = None if evidence is None else evidence.get("smoke_executable_sha256")
    payload = {
        "schema_version": "p3-pilot-build-preflight-result-v1",
        "execution_class": PILOT_EXECUTION_CLASS,
        "denominator": PILOT_DENOMINATOR,
        "p12_item_id": P12_ITEM_ID,
        "neutral_snapshot_id": NEUTRAL_SNAPSHOT_ID,
        "normalized_source_tree_sha256": FROZEN_NORMALIZED_SOURCE_TREE_SHA256,
        "controlled_subject_id": CONTROLLED_SUBJECT_ID,
        "controlled_subject_source_id": CONTROLLED_SUBJECT_SOURCE_ID,
        "build_descriptor_sha256": BUILD_DESCRIPTOR_SHA256,
        "source_preparation_verdict_sha256": SOURCE_PREPARATION_RESULT_VERDICT_SHA256,
        "source_manifest_sha256": SOURCE_MANIFEST_FILE_SHA256,
        "source_preparation_result_sha256": SOURCE_PREPARATION_RESULT_FILE_SHA256,
        "implementation_verdict_sha256": implementation_verdict_sha256,
        "intent_sha256": intent_sha256,
        "authorization_sha256": AUTHORIZATION_SHA256,
        "environment_snapshot": environment,
        "environment_snapshot_sha256": environment["artifact_sha256"],
        "harness_cmake_sha256": HARNESS_CMAKE_SHA256,
        "harness_cxx_sha256": HARNESS_CXX_SHA256,
        "cmake_cache_sha256": cache_sha,
        "compile_commands_sha256": commands_sha,
        "compiler_depfile_sha256": depfile_sha,
        "dependency_list_sha256": dep_sha,
        "smoke_executable_sha256": smoke_sha,
        "source_root": FROZEN_SOURCE_ROOT.as_posix(),
        "build_root": FROZEN_BUILD_ROOT.as_posix(),
        "harness_root": FROZEN_HARNESS_ROOT.as_posix(),
        "planned_count": PLANNED_COUNT,
        "started_count": len(started),
        "terminal_count": len(jobs),
        "not_started_count": len(not_started),
        "jobs": jobs,
        "terminal_status": terminal_status,
        "failure_reason": failure_reason,
        "build_root_exists": os.path.lexists(FROZEN_BUILD_ROOT),
        "build_root_is_symlink": os.path.islink(FROZEN_BUILD_ROOT),
        "no_retry": True,
        "claims": "blocked",
        "formal_denominator_membership": False,
        "rq4_supported": False,
        "predecessor_sha256": list(predecessor),
    }
    return validate_result(_self_hash(payload))


def _write_terminal_result(
    *,
    intent_sha256: str,
    environment: dict[str, Any],
    jobs: list[dict[str, Any]],
    predecessor: list[str],
    implementation_verdict_sha256: str,
    evidence: dict[str, str] | None,
) -> dict[str, Any]:
    if os.path.lexists(RESULT_PATH):
        raise EvidenceError("E_PILOT_BUILD_PREEXISTING", "result already exists")
    result = build_result(
        intent_sha256=intent_sha256,
        environment=environment,
        jobs=jobs,
        predecessor=predecessor,
        implementation_verdict_sha256=implementation_verdict_sha256,
        evidence=evidence,
    )
    write_canonical_json(RESULT_PATH, result, exclusive=True)
    return result


def run_build_preflight(source_root: Path, build_root: Path) -> dict[str, Any]:
    if source_root != FROZEN_SOURCE_ROOT or build_root != FROZEN_BUILD_ROOT:
        raise EvidenceError("E_PILOT_BUILD_PATH", "CLI paths must equal frozen paths")
    intent_exists = os.path.lexists(INTENT_PATH)
    result_exists = os.path.lexists(RESULT_PATH)
    intent_obj = None
    result_obj = None
    intent_digest = None
    intent_valid = False
    result_valid = False
    producer_live = False
    child_live = False
    pair_valid = False
    if intent_exists:
        try:
            raw, intent_digest = read_authority_snapshot(INTENT_PATH, "existing-intent")
            intent_obj = validate_intent(parse_canonical_json_object(raw, "existing-intent"))
            intent_valid = True
            producer_live = attempt_is_live(
                intent_obj["producer_pid"],
                intent_obj["producer_starttime"],
            )
            child_live = child_records_are_live(
                load_process_identities(FROZEN_BUILD_ROOT / "logs")
            )
        except EvidenceError:
            intent_valid = False
    if result_exists:
        try:
            raw, _digest = read_authority_snapshot(RESULT_PATH, "existing-result")
            result_obj = validate_result(parse_canonical_json_object(raw, "existing-result"))
            result_valid = True
        except EvidenceError:
            result_valid = False
    if intent_valid and result_valid and intent_obj is not None and result_obj is not None:
        try:
            validate_attempt_pair(intent_obj, intent_digest or "", result_obj)
            pair_valid = True
        except EvidenceError:
            pair_valid = False
    state = classify_reconciliation(
        intent_present=intent_exists,
        result_present=result_exists,
        intent_valid=intent_valid,
        result_valid=result_valid,
        producer_live=producer_live,
        child_live=child_live,
        pair_valid=pair_valid,
    )
    if state == "RESULT_TERMINAL":
        raise EvidenceError("E_PILOT_BUILD_PREEXISTING", "result already exists")
    if state in {"INTENT_PRODUCER_LIVE", "INTENT_CHILD_LIVE"}:
        raise EvidenceError("E_PILOT_BUILD_PREEXISTING", "original attempt is still live")
    if state == "RESULT_WITHOUT_INTENT" or state == "INVALID_DURABLE":
        raise EvidenceError("E_PILOT_BUILD_PREEXISTING", "durable objects are inconsistent")
    if state == "INTENT_ONLY_ORPHAN":
        environment = intent_obj["environment_snapshot"]
        specs = bind_job_specs(environment)
        jobs = [
            make_pre_process_infra_job(specs[0], "ORPHANED_INTENT_NO_PROCESS"),
            make_not_started_job(specs[1]),
            make_not_started_job(specs[2]),
        ]
        return _write_terminal_result(
            intent_sha256=_sha256_bytes(INTENT_PATH.read_bytes()),
            environment=environment,
            jobs=jobs,
            predecessor=sorted(
                [_sha256_bytes(INTENT_PATH.read_bytes()), *intent_obj["predecessor_sha256"]]
            ),
            implementation_verdict_sha256=intent_obj["implementation_verdict_sha256"],
            evidence=None,
        )
    require_absent_path(FROZEN_BUILD_ROOT, "build-root")
    require_absent_path(FROZEN_HARNESS_ROOT, "harness-root")
    env = dict(os.environ)
    reject_system_boost_environment(env)
    env.update(DISCONNECTED_ENVIRONMENT)
    _require_authorization()
    _require_source_preparation_identities()
    plan_digest, verdict_digest, impl_digest = _require_plan_and_implementation_verdicts()
    require_frozen_source_tree(FROZEN_SOURCE_ROOT)
    environment = make_environment_snapshot()
    reject_unbound_toolchain(env, environment["cxx_compiler_path"])
    specs = bind_job_specs(environment)
    predecessor = sorted(
        [
            plan_digest,
            verdict_digest,
            impl_digest,
            SOURCE_PREPARATION_RESULT_VERDICT_SHA256,
            SOURCE_MANIFEST_FILE_SHA256,
            SOURCE_PREPARATION_RESULT_FILE_SHA256,
            AUTHORIZATION_SHA256,
            environment["artifact_sha256"],
        ]
    )
    intent = build_intent(environment, predecessor, impl_digest)
    write_canonical_json(INTENT_PATH, intent, exclusive=True)
    intent_sha256 = _sha256_bytes(INTENT_PATH.read_bytes())
    outer_deadline = time.monotonic() + OUTER_TIMEOUT_SECONDS
    jobs = [make_not_started_job(spec) for spec in specs]
    evidence = None
    try:
        write_harness(FROZEN_HARNESS_ROOT, HARNESS_CMAKE_BYTES, HARNESS_CXX_BYTES)
        os.mkdir(FROZEN_BUILD_ROOT)
        ensure_safe_log_root(FROZEN_BUILD_ROOT / "logs")
        jobs, evidence = run_three_jobs(
            specs,
            env=env,
            log_root=FROZEN_BUILD_ROOT / "logs",
            source_root=FROZEN_SOURCE_ROOT,
            environment=environment,
            outer_deadline=outer_deadline,
            expected_smoke_sha256=None,
            collect_evidence=collect_baseline_build_evidence,
        )
    except EvidenceError as exc:
        detail = str(exc)
        reason = "RESULT_PUBLICATION_FAILURE"
        if "SOURCE_TREE" in detail or "SOURCE_TREE_DRIFT" in detail:
            reason = "SOURCE_TREE_DRIFT"
        elif "HARNESS" in detail:
            reason = "HARNESS_PUBLICATION_FAILURE"
        elif "LOG_PUBLICATION" in detail:
            reason = "LOG_PUBLICATION_FAILURE"
        elif "SYSTEM_BOOST" in detail:
            reason = "SYSTEM_BOOST_FALLBACK"
        while len(jobs) < 3:
            jobs.append(make_not_started_job(specs[len(jobs)]))
        if all(job["terminal_status"] == "NOT_STARTED" for job in jobs):
            jobs = [
                make_pre_process_infra_job(specs[0], reason),
                make_not_started_job(specs[1]),
                make_not_started_job(specs[2]),
            ]
        return _write_terminal_result(
            intent_sha256=intent_sha256,
            environment=environment,
            jobs=jobs,
            predecessor=sorted([intent_sha256, *predecessor]),
            implementation_verdict_sha256=impl_digest,
            evidence=evidence,
        )
    except Exception:
        jobs = [
            make_pre_process_infra_job(specs[0], "RESULT_PUBLICATION_FAILURE"),
            make_not_started_job(specs[1]),
            make_not_started_job(specs[2]),
        ]
        return _write_terminal_result(
            intent_sha256=intent_sha256,
            environment=environment,
            jobs=jobs,
            predecessor=sorted([intent_sha256, *predecessor]),
            implementation_verdict_sha256=impl_digest,
            evidence=None,
        )
    return _write_terminal_result(
        intent_sha256=intent_sha256,
        environment=environment,
        jobs=jobs,
        predecessor=sorted([intent_sha256, *predecessor]),
        implementation_verdict_sha256=impl_digest,
        evidence=evidence,
    )
```

Replace `scripts/p3_v3/pilot.py` with this exact file:

```python
#!/usr/bin/env python3
"""Foundation-only CLI for the Boost.Math pilot plan."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from p3_v3.artifacts import EvidenceError, read_canonical_json  # noqa: E402
from p3_v3.pilot import validate_pilot_plan, write_pilot_plan  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pilot")
    sub = parser.add_subparsers(dest="command", required=True)
    write = sub.add_parser("write-plan")
    write.add_argument("--markdown", required=True)
    write.add_argument("--output", required=True)
    validate = sub.add_parser("validate-plan")
    validate.add_argument("--plan", required=True)
    source = sub.add_parser("validate-source")
    source.add_argument("--archive", required=True)
    source.add_argument("--materialize-root", required=True)
    preflight = sub.add_parser("build-preflight")
    preflight.add_argument("--source-root", required=True)
    preflight.add_argument("--build-root", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "write-plan":
            write_pilot_plan(args.markdown, args.output)
        elif args.command == "validate-plan":
            validate_pilot_plan(read_canonical_json(args.plan))
        elif args.command == "validate-source":
            from p3_v3.pilot_source import run_validate_source

            run_validate_source(Path(args.archive), Path(args.materialize_root))
        elif args.command == "build-preflight":
            from p3_v3.pilot_build import run_build_preflight

            run_build_preflight(Path(args.source_root), Path(args.build_root))
        else:
            raise EvidenceError("E_CLI_COMMAND", f"unsupported command: {args.command}")
    except EvidenceError as exc:
        print(exc, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 6: Run the new tests to verify they pass**

Run:

```text
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m pytest \
  tests/p3_v3/test_pilot_build.py tests/p3_v3/test_pilot.py -q
```

Expected: PASS. These tests use synthetic CMake fixtures and local `python3 -c` argv only. They must not configure, compile, or execute `/tmp/p3-boost-math-pilot-production-source`.

- [ ] **Step 7: Task-specific regression plus full `tests/p3_v3`**

Run:

```text
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m pytest tests/p3_v3 -q
```

Expected: exit 0.

- [ ] **Step 8: ruff and format check**

Run:

```text
ruff check src/p3_v3/pilot_build.py tests/p3_v3/test_pilot_build.py scripts/p3_v3/pilot.py tests/p3_v3/test_pilot.py
ruff format --check src/p3_v3/pilot_build.py tests/p3_v3/test_pilot_build.py scripts/p3_v3/pilot.py tests/p3_v3/test_pilot.py
```

Expected: exit 0. If the repository has no ruff, use the project’s existing lint command on the same four files. Do not format unrelated files.

- [ ] **Step 9: Commit only the four implementation files**

```text
git add src/p3_v3/pilot_build.py tests/p3_v3/test_pilot_build.py scripts/p3_v3/pilot.py tests/p3_v3/test_pilot.py
git diff --cached --name-status
```

Cached name-status must be exactly:

```text
M	scripts/p3_v3/pilot.py
A	src/p3_v3/pilot_build.py
M	tests/p3_v3/test_pilot.py
A	tests/p3_v3/test_pilot_build.py
```

```text
git commit -m "feat(p3-v3): add Boost.Math build-preflight capability"
```

- [ ] **Step 10: Stop for independent implementation review**

Do not create Authorization. Do not create the implementation verdict. Do not run the production CLI. Do not configure or compile real Boost.Math.

---

## What This Plan Does Not Authorize

This plan does not authorize:

- production build-preflight
- dependency download or environment repair
- retry
- mutant generation or compilation
- MR construction or evaluation
- certification
- source profiling
- confirmatory `run-preflight`
- claim-ledger mutation
- formal denominator membership
- RQ4 support
- paper Results or Contributions
- a Boost.Math full-project build
- inheritance of the unfrozen 2026-08-15 11-job or 659-job inventories
