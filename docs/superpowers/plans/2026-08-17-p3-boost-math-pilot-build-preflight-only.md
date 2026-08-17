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

If `cmake` or a C++ compiler is absent, stop with `FAIL_INFRASTRUCTURE` / `MISSING_DEPENDENCY`. Do not install it.

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

Intent binds: source-preparation verdict SHA, source manifest SHA, source-preparation result SHA, normalized tree SHA, controlled subject IDs, build descriptor SHA, Authorization hash, exact harness file hashes, exact three argv arrays, exact timeouts, exact dependency DAG, source/build/harness paths, environment snapshot hash, and predecessor hashes.

Aggregate result binds: intent file SHA, the three exact job-result objects, source/preparation identities, terminal aggregate status, build-root identity/evidence, `no_retry=true`, `formal_denominator_membership=false`, `rq4_supported=false`, and `claims=blocked`.

Job result binds: `job_id`, `job_kind`, `dependency_job_ids`, `argv`, `timeout_seconds`, `started`, `terminal_status`, `failure_reason`, `exit_code`, `stdout_sha256`, `stderr_sha256`, `stdout_bytes`, `stderr_bytes`, `started_at`, `ended_at`, `wall_seconds`, `cpu_seconds`, `peak_rss_bytes`, and `artifact_sha256`.

---

## Execution Contract

- `subprocess` uses an argv list and `shell=False`.
- Intent is exclusive-created before the first child process starts.
- The three-job attempt must not reuse an existing intent.
- There is no retry.
- Every started job produces one terminal result.
- Unstarted dependents are written as `NOT_STARTED`.
- stdout and stderr are hashed and counted as raw bytes.
- Source, build, and harness paths are safe and non-symlink.
- Production does not call confirmatory `run_preflight`.
- Production does not call a profiling runner.

---

## Future Production CLI

The unique future CLI, not run by this node:

```text
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src timeout 2h \
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
]


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


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
    results = pilot_build.run_three_jobs(
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
    results = pilot_build.run_three_jobs(
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
    results = pilot_build.run_three_jobs(
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
    results = pilot_build.run_three_jobs(
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
    results = pilot_build.run_three_jobs(
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
    results = pilot_build.run_three_jobs(
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
    results = pilot_build.run_three_jobs(
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

        def communicate(self, timeout=None):
            return b"", b""

        def kill(self):
            return None

    def fake_popen(argv, stdout=None, stderr=None, shell=None, env=None):
        seen["argv"] = argv
        seen["shell"] = shell
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

    monkeypatch.setattr(pilot_build.shutil, "which", lambda name: None if name == "nvcc" else "/usr/bin/" + name)
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
    environment = {
        "schema_version": "p3-pilot-build-preflight-environment-v1",
        "execution_class": "PILOT_ONLY",
        "denominator": "PILOT_ONLY",
        "cmake_executable": "cmake",
        "cxx_compiler_executable": None,
        "nvcc_present": False,
        "native_profiling_present": False,
        "cuda_absence_blocking": False,
        "fetchcontent_fully_disconnected": True,
        "system_boost_fallback_accepted": False,
        "disconnected_environment": dict(pilot_build.DISCONNECTED_ENVIRONMENT),
        "claims": "blocked",
    }
    validated = pilot_build.validate_environment_snapshot(
        pilot_build._self_hash(environment)
    )
    assert validated["claims"] == "blocked"
    intent = pilot_build.build_intent(validated, ["0" * 64])
    assert intent["claims"] == "blocked"
    assert intent["formal_denominator_membership"] is False
    assert intent["rq4_supported"] is False
    assert intent["no_retry"] is True
    assert intent["planned_count"] == 3
    jobs = [
        pilot_build.make_not_started_job(spec) for spec in pilot_build.JOB_SPECS
    ]
    result = pilot_build.build_result(
        intent_sha256="1" * 64,
        environment=validated,
        jobs=jobs,
        predecessor=["1" * 64],
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
import resource
import shutil
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
BUILD_PARALLELISM = 4
PLANNED_COUNT = 3

CMAKE_CONFIGURE_ARGV = [
    "cmake",
    "-S",
    "/tmp/p3-boost-math-pilot-build-preflight-harness",
    "-B",
    "/tmp/p3-boost-math-pilot-build-preflight",
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
    "cxx_compiler_executable": (str, type(None)),
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
    "environment_snapshot_sha256": str,
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
    "started": bool,
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
    "intent_sha256": str,
    "authorization_sha256": str,
    "environment_snapshot_sha256": str,
    "harness_cmake_sha256": str,
    "harness_cxx_sha256": str,
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
    if validated["reviewed_plan_path"] != PLAN_PATH.as_posix():
        raise EvidenceError("E_PILOT_BUILD_IMPL_VERDICT", "reviewed plan path differs")
    if validated["reviewed_plan_sha256"] != plan_sha256:
        raise EvidenceError("E_PILOT_BUILD_IMPL_VERDICT", "reviewed plan hash differs")
    if validated["reviewed_plan_verdict_sha256"] != plan_verdict_sha256:
        raise EvidenceError("E_PILOT_BUILD_IMPL_VERDICT", "plan verdict hash differs")
    if validated["verdict"] != "PASS":
        raise EvidenceError("E_PILOT_BUILD_IMPL_VERDICT", "verdict is not PASS")
    if validated["authorized_state"] != "PILOT_BUILD_PREFLIGHT_IMPLEMENTATION_PASS":
        raise EvidenceError("E_PILOT_BUILD_IMPL_VERDICT", "authorized_state differs")
    if validated["claims"] != "blocked":
        raise EvidenceError("E_PILOT_BUILD_IMPL_VERDICT", "claims are not blocked")
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
    body = {key: validated[key] for key in validated if key != "artifact_sha256"}
    if validated["artifact_sha256"] != canonical_sha256(body):
        raise EvidenceError("E_PILOT_BUILD_ENVIRONMENT", "self-hash differs")
    return validated


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
    if validated["terminal_status"] == "NOT_STARTED":
        if validated["started"] is not False:
            raise EvidenceError("E_PILOT_BUILD_JOB", "NOT_STARTED must not start")
        if validated["exit_code"] is not None:
            raise EvidenceError("E_PILOT_BUILD_JOB", "NOT_STARTED must not have exit_code")
        if validated["stdout_sha256"] is not None or validated["stderr_sha256"] is not None:
            raise EvidenceError("E_PILOT_BUILD_JOB", "NOT_STARTED must not forge hashes")
        if validated["stdout_bytes"] is not None or validated["stderr_bytes"] is not None:
            raise EvidenceError("E_PILOT_BUILD_JOB", "NOT_STARTED must not forge byte counts")
        if validated["started_at"] is not None or validated["ended_at"] is not None:
            raise EvidenceError("E_PILOT_BUILD_JOB", "NOT_STARTED must not have timestamps")
        if validated["wall_seconds"] is not None:
            raise EvidenceError("E_PILOT_BUILD_JOB", "NOT_STARTED must not have wall time")
        if validated["cpu_seconds"] is not None or validated["peak_rss_bytes"] is not None:
            raise EvidenceError("E_PILOT_BUILD_JOB", "NOT_STARTED must not have rusage")
        if validated["failure_reason"] != "DEPENDENCY_NOT_STARTED":
            raise EvidenceError("E_PILOT_BUILD_JOB", "NOT_STARTED reason differs")
    else:
        if validated["started"] is not True:
            raise EvidenceError("E_PILOT_BUILD_JOB", "started job must set started")
        if validated["stdout_sha256"] is None or validated["stderr_sha256"] is None:
            raise EvidenceError("E_PILOT_BUILD_JOB", "started job must hash stdio")
        validate_sha256(validated["stdout_sha256"], "job.stdout_sha256")
        validate_sha256(validated["stderr_sha256"], "job.stderr_sha256")
        if type(validated["stdout_bytes"]) is not int or validated["stdout_bytes"] < 0:
            raise EvidenceError("E_PILOT_BUILD_JOB", "stdout_bytes is invalid")
        if type(validated["stderr_bytes"]) is not int or validated["stderr_bytes"] < 0:
            raise EvidenceError("E_PILOT_BUILD_JOB", "stderr_bytes is invalid")
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
    if validated["cmake_configure_argv"] != CMAKE_CONFIGURE_ARGV:
        raise EvidenceError("E_PILOT_BUILD_INTENT", "configure argv differs")
    if validated["baseline_build_argv"] != BASELINE_BUILD_ARGV:
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
    if type(validated["jobs"]) is not list or len(validated["jobs"]) != 3:
        raise EvidenceError("E_PILOT_BUILD_RESULT", "jobs must be exactly 3")
    jobs = [validate_job_result(item) for item in validated["jobs"]]
    order = [item["job_id"] for item in jobs]
    if order != ["CMAKE_CONFIGURE", "BASELINE_BUILD", "BASELINE_SMOKE"]:
        raise EvidenceError("E_PILOT_BUILD_RESULT", "job order differs")
    body = {key: validated[key] for key in validated if key != "artifact_sha256"}
    if validated["artifact_sha256"] != canonical_sha256(body):
        raise EvidenceError("E_PILOT_BUILD_RESULT", "self-hash differs")
    return validated


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
        "started": False,
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


def make_environment_snapshot() -> dict[str, Any]:
    cmake = shutil.which("cmake")
    if cmake is None:
        raise EvidenceError("E_PILOT_MISSING_DEPENDENCY", "MISSING_DEPENDENCY")
    payload = {
        "schema_version": "p3-pilot-build-preflight-environment-v1",
        "execution_class": PILOT_EXECUTION_CLASS,
        "denominator": PILOT_DENOMINATOR,
        "cmake_executable": "cmake",
        "cxx_compiler_executable": shutil.which("c++") or shutil.which("g++"),
        "nvcc_present": shutil.which("nvcc") is not None,
        "native_profiling_present": False,
        "cuda_absence_blocking": False,
        "fetchcontent_fully_disconnected": True,
        "system_boost_fallback_accepted": False,
        "disconnected_environment": dict(DISCONNECTED_ENVIRONMENT),
        "claims": "blocked",
    }
    return validate_environment_snapshot(_self_hash(payload))


def write_harness(harness_root: Path, cmake_bytes: bytes, cxx_bytes: bytes) -> None:
    require_absent_path(harness_root, "harness-root")
    os.mkdir(harness_root)
    cmake_path = harness_root / "CMakeLists.txt"
    cxx_path = harness_root / "smoke.cpp"
    cmake_path.write_bytes(cmake_bytes)
    cxx_path.write_bytes(cxx_bytes)
    if _sha256_bytes(cmake_path.read_bytes()) != _sha256_bytes(cmake_bytes):
        raise EvidenceError("E_PILOT_BUILD_HARNESS", "cmake bytes drifted")
    if _sha256_bytes(cxx_path.read_bytes()) != _sha256_bytes(cxx_bytes):
        raise EvidenceError("E_PILOT_BUILD_HARNESS", "cxx bytes drifted")


def execute_job(
    spec: dict[str, Any],
    *,
    env: dict[str, str],
    log_root: Path,
    popen=subprocess.Popen,
) -> dict[str, Any]:
    reject_system_boost_environment(env)
    argv = list(spec["argv"])
    if any(not isinstance(item, str) for item in argv):
        raise EvidenceError("E_PILOT_BUILD_ARGV", "argv items must be strings")
    started_at = time.time()
    timeout_seconds = spec["timeout_seconds"]
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    try:
        proc = popen(
            argv,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False,
            env=env,
        )
    except FileNotFoundError as exc:
        payload = {
            "schema_version": "p3-pilot-build-preflight-job-result-v1",
            "execution_class": PILOT_EXECUTION_CLASS,
            "denominator": PILOT_DENOMINATOR,
            "job_id": spec["job_id"],
            "job_kind": spec["job_kind"],
            "dependency_job_ids": list(spec["dependency_job_ids"]),
            "argv": argv,
            "timeout_seconds": timeout_seconds,
            "started": True,
            "terminal_status": "FAIL_INFRASTRUCTURE",
            "failure_reason": "MISSING_DEPENDENCY",
            "exit_code": None,
            "stdout_sha256": _sha256_bytes(b""),
            "stderr_sha256": _sha256_bytes(str(exc).encode("utf-8")),
            "stdout_bytes": 0,
            "stderr_bytes": len(str(exc).encode("utf-8")),
            "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(started_at)),
            "ended_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "wall_seconds": 0.0,
            "cpu_seconds": 0.0,
            "peak_rss_bytes": 0,
            "claims": "blocked",
        }
        return validate_job_result(_self_hash(payload))
    timed_out = False
    try:
        stdout, stderr = proc.communicate(timeout=timeout_seconds)
    except subprocess.TimeoutExpired:
        timed_out = True
        proc.kill()
        stdout, stderr = proc.communicate()
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    stdout = stdout or b""
    stderr = stderr or b""
    log_root.mkdir(parents=True, exist_ok=True)
    (log_root / f"{spec['job_id']}.stdout").write_bytes(stdout)
    (log_root / f"{spec['job_id']}.stderr").write_bytes(stderr)
    ended_at = time.time()
    detected = detect_network_or_boost(stdout, stderr, argv)
    exit_code = proc.returncode
    cpu_seconds = float(
        (after.ru_utime + after.ru_stime) - (before.ru_utime + before.ru_stime)
    )
    peak_rss_bytes = int(after.ru_maxrss) * 1024
    if timed_out:
        terminal_status = "TIMEOUT"
        failure_reason = "TIMEOUT"
    elif detected == "NETWORK_OR_DOWNLOAD_ATTEMPT":
        terminal_status = "FAIL_INFRASTRUCTURE"
        failure_reason = "NETWORK_OR_DOWNLOAD_ATTEMPT"
    elif detected == "SYSTEM_BOOST_FALLBACK":
        terminal_status = "FAIL_INFRASTRUCTURE"
        failure_reason = "SYSTEM_BOOST_FALLBACK"
    elif exit_code == 0:
        terminal_status = "PASS"
        failure_reason = None
    elif exit_code is None or exit_code < 0:
        terminal_status = "FAIL"
        failure_reason = "CRASH"
    else:
        terminal_status = "FAIL"
        failure_reason = "NONZERO_EXIT"
    payload = {
        "schema_version": "p3-pilot-build-preflight-job-result-v1",
        "execution_class": PILOT_EXECUTION_CLASS,
        "denominator": PILOT_DENOMINATOR,
        "job_id": spec["job_id"],
        "job_kind": spec["job_kind"],
        "dependency_job_ids": list(spec["dependency_job_ids"]),
        "argv": argv,
        "timeout_seconds": timeout_seconds,
        "started": True,
        "terminal_status": terminal_status,
        "failure_reason": failure_reason,
        "exit_code": None if timed_out or (exit_code is not None and exit_code < 0) else exit_code,
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
) -> list[dict[str, Any]]:
    if len(specs) != 3:
        raise EvidenceError("E_PILOT_BUILD_DAG", "planned_count must be 3")
    ids = [spec["job_id"] for spec in specs]
    if ids != ["CMAKE_CONFIGURE", "BASELINE_BUILD", "BASELINE_SMOKE"]:
        raise EvidenceError("E_PILOT_BUILD_DAG", "job order differs")
    results: list[dict[str, Any]] = []
    prior_pass = True
    tree_before = None
    if source_root is not None:
        tree_before = require_frozen_source_tree(source_root)
    for spec in specs:
        if not prior_pass:
            results.append(make_not_started_job(spec))
            continue
        result = execute_job(spec, env=env, log_root=log_root, popen=popen)
        results.append(result)
        if source_root is not None:
            tree_after = require_frozen_source_tree(source_root)
            if tree_after != tree_before:
                raise EvidenceError("E_PILOT_SOURCE_TREE_MISMATCH", "tree drifted")
        prior_pass = result["terminal_status"] == "PASS"
    return results


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


def _require_plan_and_implementation_verdicts() -> tuple[str, str]:
    plan_raw, plan_digest = read_authority_snapshot(PLAN_PATH, "build-preflight-plan")
    verdict_raw, verdict_digest = read_authority_snapshot(
        PLAN_VERDICT_PATH, "build-preflight-plan-verdict"
    )
    validate_plan_verdict(parse_canonical_json_object(verdict_raw, "plan-verdict"), plan_digest)
    impl_raw, _impl_digest = read_authority_snapshot(
        IMPLEMENTATION_VERDICT_PATH, "build-preflight-implementation-verdict"
    )
    validate_implementation_verdict(
        parse_canonical_json_object(impl_raw, "implementation-verdict"),
        plan_digest,
        verdict_digest,
    )
    return plan_digest, verdict_digest


def build_intent(environment: dict[str, Any], predecessor: list[str]) -> dict[str, Any]:
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
        "authorization_sha256": AUTHORIZATION_SHA256,
        "harness_cmake_sha256": HARNESS_CMAKE_SHA256,
        "harness_cxx_sha256": HARNESS_CXX_SHA256,
        "source_root": FROZEN_SOURCE_ROOT.as_posix(),
        "build_root": FROZEN_BUILD_ROOT.as_posix(),
        "harness_root": FROZEN_HARNESS_ROOT.as_posix(),
        "cmake_configure_argv": list(CMAKE_CONFIGURE_ARGV),
        "baseline_build_argv": list(BASELINE_BUILD_ARGV),
        "baseline_smoke_argv": list(BASELINE_SMOKE_ARGV),
        "cmake_configure_timeout_seconds": CMAKE_CONFIGURE_TIMEOUT_SECONDS,
        "baseline_build_timeout_seconds": BASELINE_BUILD_TIMEOUT_SECONDS,
        "baseline_smoke_timeout_seconds": BASELINE_SMOKE_TIMEOUT_SECONDS,
        "outer_timeout_seconds": OUTER_TIMEOUT_SECONDS,
        "build_parallelism": BUILD_PARALLELISM,
        "planned_count": PLANNED_COUNT,
        "dependency_dag": [list(edge) for edge in DEPENDENCY_DAG],
        "environment_snapshot_sha256": environment["artifact_sha256"],
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
) -> dict[str, Any]:
    started = [job for job in jobs if job["started"] is True]
    not_started = [job for job in jobs if job["terminal_status"] == "NOT_STARTED"]
    first_bad = next(
        (job for job in jobs if job["terminal_status"] != "PASS"),
        None,
    )
    if first_bad is None:
        terminal_status = "PASS"
        failure_reason = None
    else:
        terminal_status = first_bad["terminal_status"]
        failure_reason = first_bad["failure_reason"]
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
        "intent_sha256": intent_sha256,
        "authorization_sha256": AUTHORIZATION_SHA256,
        "environment_snapshot_sha256": environment["artifact_sha256"],
        "harness_cmake_sha256": HARNESS_CMAKE_SHA256,
        "harness_cxx_sha256": HARNESS_CXX_SHA256,
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


def run_build_preflight(source_root: Path, build_root: Path) -> dict[str, Any]:
    if source_root != FROZEN_SOURCE_ROOT or build_root != FROZEN_BUILD_ROOT:
        raise EvidenceError("E_PILOT_BUILD_PATH", "CLI paths must equal frozen paths")
    require_absent_path(INTENT_PATH, "intent")
    require_absent_path(RESULT_PATH, "result")
    require_absent_path(FROZEN_BUILD_ROOT, "build-root")
    require_absent_path(FROZEN_HARNESS_ROOT, "harness-root")
    env = dict(os.environ)
    reject_system_boost_environment(env)
    env.update(DISCONNECTED_ENVIRONMENT)
    _require_authorization()
    _require_source_preparation_identities()
    plan_digest, verdict_digest = _require_plan_and_implementation_verdicts()
    require_frozen_source_tree(FROZEN_SOURCE_ROOT)
    environment = make_environment_snapshot()
    predecessor = sorted(
        [
            plan_digest,
            verdict_digest,
            SOURCE_PREPARATION_RESULT_VERDICT_SHA256,
            SOURCE_MANIFEST_FILE_SHA256,
            SOURCE_PREPARATION_RESULT_FILE_SHA256,
            AUTHORIZATION_SHA256,
            environment["artifact_sha256"],
        ]
    )
    intent = build_intent(environment, predecessor)
    write_canonical_json(INTENT_PATH, intent, exclusive=True)
    intent_sha256 = _sha256_bytes(INTENT_PATH.read_bytes())
    write_harness(FROZEN_HARNESS_ROOT, HARNESS_CMAKE_BYTES, HARNESS_CXX_BYTES)
    os.mkdir(FROZEN_BUILD_ROOT)
    jobs = run_three_jobs(
        JOB_SPECS,
        env=env,
        log_root=FROZEN_BUILD_ROOT / "logs",
        source_root=FROZEN_SOURCE_ROOT,
    )
    result = build_result(
        intent_sha256=intent_sha256,
        environment=environment,
        jobs=jobs,
        predecessor=sorted([intent_sha256, *predecessor]),
    )
    write_canonical_json(RESULT_PATH, result, exclusive=True)
    return result
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
