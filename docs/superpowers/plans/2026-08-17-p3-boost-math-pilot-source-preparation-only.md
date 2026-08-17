# Boost.Math PILOT_SOURCE_PREPARATION_ONLY Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. This document authorizes only the single future source-preparation capability task below. After that task, stop for independent review. Do not start production preparation. Do not create authorization A. Do not create a source-preparation plan verdict, capability verdict, launch authority, launch packet, or launch verdict.

**Goal:** Define one later capability that can hash, extract, and identity-check a caller-supplied archive under a fail-closed extractor and the Phase 1 normalized-tree algorithm. This planning node writes the plan only. The later capability task uses runtime-generated synthetic ZIP and TAR fixtures. It does not read a real Boost.Math archive and does not create a production source manifest, preparation result, authorization A, or launch authority.

**Architecture:** Keep confirmatory `p3-v3-*` schemas unchanged. Add `src/p3_v3/pilot_source.py` as the only new production module. The formal source-preparation plan verdict is archived before any capability implementation. Production `run_validate_source` then reads one verified snapshot of each machine authority in the unique acyclic topological order: source-preparation plan, plan verdict, capability verdict plus reviewed production bytes, Authorization A, launch packet, launch verdict, then launch authority. Only after that chain validates may the module snapshot an archive, extract into new staging, validate the Phase 1 tree on staging, and publish in the frozen order manifest, then materialize root, then PASS result. Capability PASS still does not authorize real preparation.

**Tech Stack:** Python 3.11 or newer, existing `src/p3_v3/artifacts.py` exact-object helpers including `read_regular_file_snapshot`, existing `SourceSnapshot`, `SourceSnapshotEntry`, and `canonical_source_tree_sha256` from `src/p3_v3/bridge_and_frames.py`, pytest with `PYTHONPATH=src`. Cursor VM has no `rtk`. Later implementation uses bare `python3`, `pytest`, `sha256sum`, `wc`, and `git`.

## Global Constraints

- Plan class is `PILOT_SOURCE_PREPARATION_ONLY`.
- This document has exactly one future implementation task.
- This planning node does not run pytest.
- After this document is written, the requested review state is `PILOT_PLAN_REVIEW_CANDIDATE`. This document is not an independent PASS.
- Formal foundation state remains `PILOT_IMPLEMENTATION_PASS`.
- Process location remains `PILOT_EXECUTION_AWAITING_USER_AUTHORIZATION`.
- The later capability task uses only runtime-generated synthetic ZIP and TAR fixtures.
- The later capability task does not read a real Boost.Math archive.
- The later capability task does not create `data/p3_v3/pilot/boost_math/source-manifest.json`, `data/p3_v3/pilot/boost_math/source-preparation-result.json`, `data/p3_v3/pilot/boost_math/source-preparation-launch.json`, or `data/p3_v3/pilot/boost_math/user-auth-preparation.txt`.
- After the later capability task, stop at an independent Sol High implementation review.
- Capability implementation PASS still does not authorize real preparation.
- Only later explicit Authorization A plus a separately reviewed and archived production launch authority may run production preparation.
- `claims=blocked`.
- Formal denominator membership is false.
- `rq4_supported=false`.
- The complete plan `docs/superpowers/plans/2026-08-15-p3-boost-math-pilot-only.md` remains unfrozen and is not execution authority.
- This document contains no build, CMake configure, contract, site, MR, mutant, certification, execution, or evidence-closure implementation task.
- This planning node does not create authorization A or any reserved verdict or launch file.
- The later capability task does not create authorization A or any reserved verdict or launch file.
- `execution_class = PILOT_ONLY` and `denominator = PILOT_ONLY` on every durable pilot object defined here.
- File count, directory names, and LOC cannot replace normalized tree identity.
- The frozen build descriptor hash is an authority label only. A source manifest does not prove CMake configure, compile, test, or public behavior PASS.
- A source manifest alone does not represent preparation PASS. Only a closed pair of that manifest and a valid PASS result represents preparation PASS.
- Archive SHA-256 and archive bytes are observed at production time from one opened snapshot. This plan does not invent unknown fixed archive hash or byte values.

---

## Three Independent Gates Plus Launch Authority

Frozen successor order. Any missing predecessor, hash mismatch, schema drift, or non-PASS state fail-closes every later gate and writes zero production outputs.

```text
G1_FOUNDATION_IMPLEMENTATION_PASS
-> independent source-preparation plan review
-> formal source-preparation plan verdict archival
-> capability implementation
-> independent capability implementation review
-> formal capability implementation verdict archival
-> user Authorization A
-> production launch packet
-> independent launch-packet review
-> launch Sol High verdict archival
-> exclusive-create source-preparation-launch.json
-> production source preparation
-> independent manifest/result review
```

Formal plan verdict archival must precede capability implementation. An unfrozen plan must not be implemented.

Machine-verifiable production authorities, distinct from historical G1:

1. Source-preparation plan formal verdict.
2. Source-preparation capability implementation formal verdict.
3. Separately reviewed production preparation launch authority.
4. Authorization A.

`G1_FOUNDATION_IMPLEMENTATION_PASS` remains the archived foundation implementation verdict. It is already PASS. It authorizes later independent plan review only. It does not authorize capability implementation before the source-preparation plan verdict exists. It is not a substitute for the four production authorities above.

Fail-closed rule: if any production authority is absent, has the wrong SHA-256, is not PASS, or fails exact-schema validation, `run_validate_source` must raise and must write no source manifest, no preparation result, and no materialize root.

---

## Frozen Authority Identities

These files are identity-checked only. This plan does not modify them.

| File | SHA-256 |
|---|---|
| `docs/superpowers/plans/2026-08-16-p3-boost-math-pilot-foundation-only.md` | `479931df4dd6562177e28c333305f3c55bbf081a596f5e7de337b8a92fa73463` |
| `docs/review_20260816/boost_math_pilot_foundation_plan_review_packet.md` | `e6fd4ab16b3db44711014e4fb9aeaa9b41405c5b37650c3fe790d5f9dfaf9e92` |
| `docs/review_20260816/boost_math_pilot_foundation_sol_high_review.md` | `da5f211b7eab665aca696f5cf1d214d30b0914dc9ccb2a585bfcc06cb97be07c` |
| `docs/review_20260817/boost_math_pilot_foundation_implementation_sol_high_review.md` | `e7e5e9519ae49eb08c450c4e16c56d7551528030916d9d8fe88f0ab91a7b1c9d` |
| `data/p3_v3/pilot/boost_math/pilot-plan.json` | `23d7fb802a2395d93a211862f205065ce1abd52e6ae2e74374aaf2bb624d4cf2` |
| `src/p3_v3/pilot.py` | `4689ed3940f87d3c7c3297bf58c786a3fb2d289cbc45556de35903b0e9111c46` |
| `scripts/p3_v3/pilot.py` | `44597b83d59f159d6a7fbf7fbc010b9b747a1aaf4a366ae1c1fd222314b9b7c9` |
| `tests/p3_v3/test_pilot.py` | `04a61415b6b6071c8a23d4ccf39c4f39b330d1a0530ae19805aa83e71e2515ff` |
| `src/p3_v3/artifacts.py` | `9f619073626003caa7d724a19655b5abae92318afd3f656494a0843613b6f57a` |
| `src/p3_v3/bridge_and_frames.py` | `978fa53c66ae15f9c51b5fa73dc03afdb2d23448f7714d752bccf92c09503ad0` |
| `docs/superpowers/plans/2026-08-15-p3-boost-math-pilot-only.md` | `1612a6ee81773c7db97625ae3497fab31b93ad70f2ecaefce2fdd845bda73cca` |
| `research/evidence/p3_claim_ledger_v1.3.0.yml` | `bf4979662697b2d0565bb70eec88b22673e84bee93b61234555342efb4082a68` |
| `data/p3_v3/protocol/protocol.json` | `240d8270d41802c9d5b86f30564eadd1a86fd9ed09de2c7e947d17c1a4d78519` |
| `data/p3_v3/protocol/environment_lock.json` | `7706b4ce272d09df13c5212b04ec0f2519932f4225d5eac0d052d3225c7ff35f` |
| `adapter-discovery` frame | `87fb9d05278c5c2e713c8a9d7f398cb1a1c84562df27b590e6d37f98fd7c1dd1` |
| `derived-subject` frame | `654a5c8a26b85013a44665dd92c59a66afee9f639ec7d28535d58357ec696f20` |
| `source-scale` frame | `dc9b56fe81bcf8301e6164f15007c6f57ee11e79cfff1b84e66906cb7de228d0` |

The 2026-08-15 complete pilot plan is a readable unfrozen reference. It is not current execution authority.

Historical foundation bindings remain identity labels only:

```text
docs/review_20260817/boost_math_pilot_foundation_implementation_sol_high_review.md
e7e5e9519ae49eb08c450c4e16c56d7551528030916d9d8fe88f0ab91a7b1c9d
data/p3_v3/pilot/boost_math/pilot-plan.json
23d7fb802a2395d93a211862f205065ce1abd52e6ae2e74374aaf2bb624d4cf2
```

Those two hashes do not authorize production preparation and are not a substitute for the source-preparation plan verdict, capability verdict, or launch authority.

---

## Safe Authority Snapshot Contract

Authorization A, the source-preparation plan verdict, the capability implementation verdict, the launch authority, the launch packet, the launch Sol High verdict, and the historical machine plan must not use `is_file` / `is_symlink` followed by `path.read_bytes`.

Every authority read uses `read_regular_file_snapshot` from `src/p3_v3/artifacts.py`, or an equivalent anchored no-symlink single-fd snapshot. Parse, exact-schema validation, file SHA-256, and predecessor membership must all consume that same raw byte snapshot. After validation, the producer must not reopen the path.

```python
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from p3_v3.artifacts import (
    EvidenceError,
    canonical_json_bytes,
    read_regular_file_snapshot,
    validate_exact_object,
    validate_sha256,
)


def read_authority_snapshot(path: Path, context: str) -> tuple[bytes, str]:
    try:
        raw, _mode = read_regular_file_snapshot(path, context)
    except EvidenceError as exc:
        if exc.code == "E_AUTHORITY_LOCK_PATH":
            raise EvidenceError(
                "E_PILOT_SOURCE_IDENTITY",
                f"{context} authority snapshot is absent or unsafe",
            ) from exc
        raise
    digest = hashlib.sha256(raw).hexdigest()
    validate_sha256(digest, f"{context}.sha256")
    return raw, digest


def parse_canonical_authority_object(raw: bytes, context: str) -> dict:
    try:
        value = json.loads(
            raw.decode("utf-8"),
            parse_constant=lambda token: (_ for _ in ()).throw(ValueError(token)),
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise EvidenceError("E_PILOT_SOURCE_IDENTITY", f"{context} is not JSON") from exc
    if not isinstance(value, dict) or canonical_json_bytes(value) != raw:
        raise EvidenceError(
            "E_PILOT_SOURCE_IDENTITY",
            f"{context} is not one canonical JSON object",
        )
    return value


def map_gate_error(exc: EvidenceError, gate_code: str) -> EvidenceError:
    if exc.code in {
        "E_SCHEMA_KEYS",
        "E_SCHEMA_TYPE",
        "E_SHA256",
        "E_CANONICAL_JSON",
        "E_JSON",
        "E_PILOT_SOURCE_IDENTITY",
    }:
        return EvidenceError(gate_code, str(exc))
    return exc
```

Replacement-race rule: if the path is replaced after the snapshot is taken, the producer still binds the already validated snapshot bytes, or it fail-closes. It must not reread the replaced path.

---

## Canonical Source-Preparation Plan Verdict Gate

Frozen path, reserved, not created by this node or by the later capability task:

```text
docs/review_20260817/boost_math_pilot_source_preparation_sol_high_review.md
```

The file is one canonical JSON object with exactly one terminal LF. Extra text, Markdown prose, or a second object is `E_PILOT_SOURCE_PREPARATION_PLAN_VERDICT`. Exact keys and exact types:

```python
from pathlib import Path

from p3_v3.artifacts import EvidenceError, validate_exact_object, validate_sha256

CANONICAL_SOURCE_PREPARATION_PLAN_VERDICT_PATH = Path(
    "docs/review_20260817/boost_math_pilot_source_preparation_sol_high_review.md"
)
SOURCE_PREPARATION_PLAN_PATH = Path(
    "docs/superpowers/plans/"
    "2026-08-17-p3-boost-math-pilot-source-preparation-only.md"
)
SOURCE_PREPARATION_PLAN_VERDICT_EXACT = {
    "reviewed_plan_path": str,
    "reviewed_plan_sha256": str,
    "verdict": str,
    "authorized_state": str,
    "claims": str,
}


def validate_source_preparation_plan_verdict(
    value: object, markdown_plan_sha256: str
) -> dict:
    try:
        validated = validate_exact_object(
            value,
            SOURCE_PREPARATION_PLAN_VERDICT_EXACT,
            "source-preparation-plan-verdict",
        )
        validate_sha256(
            validated["reviewed_plan_sha256"],
            "source-preparation-plan-verdict.reviewed_plan_sha256",
        )
    except EvidenceError as exc:
        raise map_gate_error(exc, "E_PILOT_SOURCE_PREPARATION_PLAN_VERDICT") from exc
    if validated["reviewed_plan_path"] != SOURCE_PREPARATION_PLAN_PATH.as_posix():
        raise EvidenceError(
            "E_PILOT_SOURCE_PREPARATION_PLAN_VERDICT",
            "reviewed plan path differs",
        )
    if validated["reviewed_plan_sha256"] != markdown_plan_sha256:
        raise EvidenceError(
            "E_PILOT_SOURCE_PREPARATION_PLAN_VERDICT",
            "reviewed plan hash differs",
        )
    if validated["verdict"] != "PASS":
        raise EvidenceError(
            "E_PILOT_SOURCE_PREPARATION_PLAN_VERDICT",
            "verdict is not PASS",
        )
    if validated["authorized_state"] != "PILOT_SOURCE_PREPARATION_PLAN_FROZEN":
        raise EvidenceError(
            "E_PILOT_SOURCE_PREPARATION_PLAN_VERDICT",
            "authorized_state is not PILOT_SOURCE_PREPARATION_PLAN_FROZEN",
        )
    if validated["claims"] != "blocked":
        raise EvidenceError(
            "E_PILOT_SOURCE_PREPARATION_PLAN_VERDICT",
            "claims are not blocked",
        )
    return validated
```

A missing canonical file is `E_PILOT_SOURCE_PREPARATION_PLAN_VERDICT_ABSENT`. Hash mismatch, schema drift, or non-PASS is `E_PILOT_SOURCE_PREPARATION_PLAN_VERDICT`. Either case writes zero production outputs.

---

## Canonical Capability Implementation Verdict Gate

Frozen path, reserved, not created by this node or by the later capability task:

```text
docs/review_20260817/boost_math_pilot_source_preparation_implementation_sol_high_review.md
```

```python
from pathlib import Path

from p3_v3.artifacts import EvidenceError, validate_exact_object, validate_sha256

CANONICAL_SOURCE_PREPARATION_CAPABILITY_VERDICT_PATH = Path(
    "docs/review_20260817/"
    "boost_math_pilot_source_preparation_implementation_sol_high_review.md"
)
REVIEWED_PILOT_SOURCE_PATH = Path("src/p3_v3/pilot_source.py")
REVIEWED_PILOT_CLI_PATH = Path("scripts/p3_v3/pilot.py")
REVIEWED_TEST_PILOT_SOURCE_PATH = Path("tests/p3_v3/test_pilot_source.py")
REVIEWED_TEST_PILOT_PATH = Path("tests/p3_v3/test_pilot.py")
SOURCE_PREPARATION_CAPABILITY_VERDICT_EXACT = {
    "reviewed_plan_path": str,
    "reviewed_plan_sha256": str,
    "reviewed_plan_verdict_sha256": str,
    "reviewed_commit": str,
    "reviewed_pilot_source_path": str,
    "reviewed_pilot_source_sha256": str,
    "reviewed_pilot_cli_path": str,
    "reviewed_pilot_cli_sha256": str,
    "reviewed_test_pilot_source_path": str,
    "reviewed_test_pilot_source_sha256": str,
    "reviewed_test_pilot_path": str,
    "reviewed_test_pilot_sha256": str,
    "verdict": str,
    "authorized_state": str,
    "claims": str,
}


def validate_source_preparation_capability_verdict(
    value: object,
    markdown_plan_sha256: str,
    plan_verdict_sha256: str,
) -> dict:
    try:
        validated = validate_exact_object(
            value,
            SOURCE_PREPARATION_CAPABILITY_VERDICT_EXACT,
            "source-preparation-capability-verdict",
        )
    except EvidenceError as exc:
        raise map_gate_error(exc, "E_PILOT_SOURCE_PREPARATION_CAPABILITY_VERDICT") from exc
    commit = validated["reviewed_commit"]
    if type(commit) is not str or __import__("re").fullmatch(r"[0-9a-f]{40}", commit) is None:
        raise EvidenceError(
            "E_PILOT_SOURCE_PREPARATION_CAPABILITY_VERDICT",
            "reviewed_commit is not 40 lowercase hexadecimal characters",
        )
    expected_paths = {
        "reviewed_plan_path": SOURCE_PREPARATION_PLAN_PATH.as_posix(),
        "reviewed_pilot_source_path": REVIEWED_PILOT_SOURCE_PATH.as_posix(),
        "reviewed_pilot_cli_path": REVIEWED_PILOT_CLI_PATH.as_posix(),
        "reviewed_test_pilot_source_path": REVIEWED_TEST_PILOT_SOURCE_PATH.as_posix(),
        "reviewed_test_pilot_path": REVIEWED_TEST_PILOT_PATH.as_posix(),
    }
    for key, required in expected_paths.items():
        if validated[key] != required:
            raise EvidenceError(
                "E_PILOT_SOURCE_PREPARATION_CAPABILITY_VERDICT",
                f"{key} differs",
            )
    for key in (
        "reviewed_plan_sha256",
        "reviewed_plan_verdict_sha256",
        "reviewed_pilot_source_sha256",
        "reviewed_pilot_cli_sha256",
        "reviewed_test_pilot_source_sha256",
        "reviewed_test_pilot_sha256",
    ):
        try:
            validate_sha256(validated[key], f"capability-verdict.{key}")
        except EvidenceError as exc:
            raise map_gate_error(
                exc, "E_PILOT_SOURCE_PREPARATION_CAPABILITY_VERDICT"
            ) from exc
    if validated["reviewed_plan_sha256"] != markdown_plan_sha256:
        raise EvidenceError(
            "E_PILOT_SOURCE_PREPARATION_CAPABILITY_VERDICT",
            "reviewed plan hash differs",
        )
    if validated["reviewed_plan_verdict_sha256"] != plan_verdict_sha256:
        raise EvidenceError(
            "E_PILOT_SOURCE_PREPARATION_CAPABILITY_VERDICT",
            "reviewed plan verdict hash differs",
        )
    if validated["verdict"] != "PASS":
        raise EvidenceError(
            "E_PILOT_SOURCE_PREPARATION_CAPABILITY_VERDICT",
            "verdict is not PASS",
        )
    if validated["authorized_state"] != (
        "PILOT_SOURCE_PREPARATION_IMPLEMENTATION_PASS"
    ):
        raise EvidenceError(
            "E_PILOT_SOURCE_PREPARATION_CAPABILITY_VERDICT",
            "authorized_state is not PILOT_SOURCE_PREPARATION_IMPLEMENTATION_PASS",
        )
    if validated["claims"] != "blocked":
        raise EvidenceError(
            "E_PILOT_SOURCE_PREPARATION_CAPABILITY_VERDICT",
            "claims are not blocked",
        )
    return validated


def verify_reviewed_production_bytes(
    capability_verdict: dict,
) -> None:
    observed_source, source_digest = read_authority_snapshot(
        REVIEWED_PILOT_SOURCE_PATH, "reviewed-pilot-source"
    )
    observed_cli, cli_digest = read_authority_snapshot(
        REVIEWED_PILOT_CLI_PATH, "reviewed-pilot-cli"
    )
    del observed_source, observed_cli
    if source_digest != capability_verdict["reviewed_pilot_source_sha256"]:
        raise EvidenceError(
            "E_PILOT_SOURCE_PREPARATION_CAPABILITY_VERDICT",
            "runtime pilot_source.py bytes differ from the reviewed snapshot",
        )
    if cli_digest != capability_verdict["reviewed_pilot_cli_sha256"]:
        raise EvidenceError(
            "E_PILOT_SOURCE_PREPARATION_CAPABILITY_VERDICT",
            "runtime pilot CLI bytes differ from the reviewed snapshot",
        )
```

A missing file is `E_PILOT_SOURCE_PREPARATION_CAPABILITY_VERDICT_ABSENT`. Hash mismatch, schema drift, reviewed-commit mismatch, implementation-file drift, or non-PASS is `E_PILOT_SOURCE_PREPARATION_CAPABILITY_VERDICT`. Either case writes zero production outputs. The capability verdict must bind the formal plan verdict SHA-256. Test-file hashes are review evidence. Production re-snapshots only the production module and CLI and fail-closes on byte drift. Canonical-JSON, extra-key, wrong-type, and bad-SHA failures must surface as this gate code, not as raw `E_SCHEMA_KEYS` or `E_CANONICAL_JSON`.

---

## Reviewed Production Launch Machine Authority

Frozen path, reserved, exclusive-created only by a later launch archival node. This node and the later capability task must not create it:

```text
data/p3_v3/pilot/boost_math/source-preparation-launch.json
```

Related reserved paths, also not created here:

```text
docs/review_20260817/boost_math_pilot_source_preparation_launch_packet.md
docs/review_20260817/boost_math_pilot_source_preparation_launch_sol_high_review.md
```

```python
from pathlib import Path

from p3_v3.artifacts import (
    EvidenceError,
    canonical_sha256,
    validate_exact_object,
    validate_sha256,
)

SOURCE_PREPARATION_LAUNCH_PATH = Path(
    "data/p3_v3/pilot/boost_math/source-preparation-launch.json"
)
SOURCE_PREPARATION_LAUNCH_PACKET_PATH = Path(
    "docs/review_20260817/boost_math_pilot_source_preparation_launch_packet.md"
)
SOURCE_PREPARATION_LAUNCH_VERDICT_PATH = Path(
    "docs/review_20260817/"
    "boost_math_pilot_source_preparation_launch_sol_high_review.md"
)
SOURCE_PREPARATION_LAUNCH_EXACT = {
    "schema_version": str,
    "execution_class": str,
    "denominator": str,
    "source_preparation_plan_path": str,
    "source_preparation_plan_sha256": str,
    "source_preparation_plan_verdict_path": str,
    "source_preparation_plan_verdict_sha256": str,
    "capability_implementation_verdict_path": str,
    "capability_implementation_verdict_sha256": str,
    "production_launch_packet_path": str,
    "production_launch_packet_sha256": str,
    "launch_sol_high_verdict_path": str,
    "launch_sol_high_verdict_sha256": str,
    "authorization_a_sha256": str,
    "claims": str,
    "artifact_sha256": str,
}
SOURCE_PREPARATION_LAUNCH_VERDICT_EXACT = {
    "reviewed_packet_path": str,
    "reviewed_packet_sha256": str,
    "plan_verdict_sha256": str,
    "capability_verdict_sha256": str,
    "authorization_a_sha256": str,
    "verdict": str,
    "authorized_state": str,
    "claims": str,
}


def validate_source_preparation_launch(
    value: object,
    *,
    plan_sha256: str,
    plan_verdict_sha256: str,
    capability_verdict_sha256: str,
    launch_packet_sha256: str,
    launch_verdict_sha256: str,
    authorization_a_sha256: str,
) -> dict:
    try:
        validated = validate_exact_object(
            value, SOURCE_PREPARATION_LAUNCH_EXACT, "source-preparation-launch"
        )
    except EvidenceError as exc:
        raise map_gate_error(exc, "E_PILOT_SOURCE_PREPARATION_LAUNCH") from exc
    if validated["schema_version"] != "p3-pilot-source-preparation-launch-v1":
        raise EvidenceError("E_PILOT_SOURCE_PREPARATION_LAUNCH", "schema differs")
    if validated["execution_class"] != "PILOT_ONLY":
        raise EvidenceError("E_PILOT_SOURCE_PREPARATION_LAUNCH", "class differs")
    if validated["denominator"] != "PILOT_ONLY":
        raise EvidenceError("E_PILOT_SOURCE_PREPARATION_LAUNCH", "denominator differs")
    if validated["claims"] != "blocked":
        raise EvidenceError("E_PILOT_SOURCE_PREPARATION_LAUNCH", "claims are not blocked")
    expected = {
        "source_preparation_plan_path": SOURCE_PREPARATION_PLAN_PATH.as_posix(),
        "source_preparation_plan_sha256": plan_sha256,
        "source_preparation_plan_verdict_path": (
            CANONICAL_SOURCE_PREPARATION_PLAN_VERDICT_PATH.as_posix()
        ),
        "source_preparation_plan_verdict_sha256": plan_verdict_sha256,
        "capability_implementation_verdict_path": (
            CANONICAL_SOURCE_PREPARATION_CAPABILITY_VERDICT_PATH.as_posix()
        ),
        "capability_implementation_verdict_sha256": capability_verdict_sha256,
        "production_launch_packet_path": (
            SOURCE_PREPARATION_LAUNCH_PACKET_PATH.as_posix()
        ),
        "production_launch_packet_sha256": launch_packet_sha256,
        "launch_sol_high_verdict_path": (
            SOURCE_PREPARATION_LAUNCH_VERDICT_PATH.as_posix()
        ),
        "launch_sol_high_verdict_sha256": launch_verdict_sha256,
        "authorization_a_sha256": authorization_a_sha256,
    }
    for key, required in expected.items():
        if key.endswith("_sha256"):
            validate_sha256(validated[key], f"source-preparation-launch.{key}")
        if validated[key] != required:
            raise EvidenceError(
                "E_PILOT_SOURCE_PREPARATION_LAUNCH",
                f"{key} differs from the verified snapshot chain",
            )
    body = {key: validated[key] for key in validated if key != "artifact_sha256"}
    if validated["artifact_sha256"] != canonical_sha256(body):
        raise EvidenceError("E_PILOT_SOURCE_PREPARATION_LAUNCH", "self-hash differs")
    return validated


def validate_source_preparation_launch_verdict(
    value: object,
    *,
    packet_sha256: str,
    plan_verdict_sha256: str,
    capability_verdict_sha256: str,
    authorization_a_sha256: str,
) -> dict:
    try:
        validated = validate_exact_object(
            value,
            SOURCE_PREPARATION_LAUNCH_VERDICT_EXACT,
            "source-preparation-launch-verdict",
        )
    except EvidenceError as exc:
        raise map_gate_error(exc, "E_PILOT_SOURCE_PREPARATION_LAUNCH") from exc
    if validated["reviewed_packet_path"] != (
        SOURCE_PREPARATION_LAUNCH_PACKET_PATH.as_posix()
    ):
        raise EvidenceError("E_PILOT_SOURCE_PREPARATION_LAUNCH", "packet path differs")
    if validated["reviewed_packet_sha256"] != packet_sha256:
        raise EvidenceError("E_PILOT_SOURCE_PREPARATION_LAUNCH", "packet hash differs")
    if validated["plan_verdict_sha256"] != plan_verdict_sha256:
        raise EvidenceError(
            "E_PILOT_SOURCE_PREPARATION_LAUNCH",
            "plan verdict hash differs",
        )
    if validated["capability_verdict_sha256"] != capability_verdict_sha256:
        raise EvidenceError(
            "E_PILOT_SOURCE_PREPARATION_LAUNCH",
            "capability verdict hash differs",
        )
    if validated["authorization_a_sha256"] != authorization_a_sha256:
        raise EvidenceError(
            "E_PILOT_SOURCE_PREPARATION_LAUNCH",
            "authorization A hash differs",
        )
    if validated["verdict"] != "PASS":
        raise EvidenceError("E_PILOT_SOURCE_PREPARATION_LAUNCH", "verdict is not PASS")
    if validated["authorized_state"] != "PILOT_SOURCE_PREPARATION_LAUNCH_FROZEN":
        raise EvidenceError(
            "E_PILOT_SOURCE_PREPARATION_LAUNCH",
            "authorized_state is not PILOT_SOURCE_PREPARATION_LAUNCH_FROZEN",
        )
    if validated["claims"] != "blocked":
        raise EvidenceError(
            "E_PILOT_SOURCE_PREPARATION_LAUNCH",
            "claims are not blocked",
        )
    return validated
```

A missing launch authority is `E_PILOT_SOURCE_PREPARATION_LAUNCH_ABSENT`. Hash mismatch, schema drift, or non-PASS is `E_PILOT_SOURCE_PREPARATION_LAUNCH`. Either case writes zero production outputs.

The launch packet is exclusive-created only after Authorization A exists. The launch verdict reviews only the launch packet and the already frozen predecessors: plan verdict SHA-256, capability verdict SHA-256, and Authorization A SHA-256. It must not contain `reviewed_launch_path` or `reviewed_launch_sha256`. `source-preparation-launch.json` is exclusive-created only after that launch verdict is archived. No predecessor of the launch authority may cite the launch authority hash. Launch authority binds the capability verdict file SHA-256. Test-file hashes remain review evidence inside the capability verdict; production re-snapshots only `src/p3_v3/pilot_source.py` and `scripts/p3_v3/pilot.py`.

---

## Authorization A

Frozen production path:

```text
data/p3_v3/pilot/boost_math/user-auth-preparation.txt
```

Exact bytes, including the single terminal LF:

```text
AUTHORIZE_BOOSTMATH_PILOT_PREPARATION\n
```

Frozen identity:

- SHA-256: `502c6407aa368a26948db10cc1ca0d1c91f66c8bfe702aa02f01f275c9df04b6`
- bytes: 38
- LF: 1

Authorization A is a successor of the capability implementation verdict and a predecessor of the launch packet. This planning node does not create that file. The later capability task does not create that file. Production CLI must not accept an authorization-path override. Tests may monkeypatch the frozen path constant onto a temporary regular file. Tests must still require the exact 38 bytes and the frozen SHA-256. A missing or unsafe snapshot is `E_PILOT_PREPARATION_AUTH_ABSENT`. Wrong bytes or a wrong hash is `E_PILOT_PREPARATION_AUTH`. Either authorization failure writes no source manifest, no preparation result, and no materialize root.

```python
from __future__ import annotations

from pathlib import Path

from p3_v3.artifacts import EvidenceError

AUTHORIZATION_A_PATH = Path("data/p3_v3/pilot/boost_math/user-auth-preparation.txt")
AUTHORIZATION_A_BYTES = b"AUTHORIZE_BOOSTMATH_PILOT_PREPARATION\n"
AUTHORIZATION_A_SHA256 = (
    "502c6407aa368a26948db10cc1ca0d1c91f66c8bfe702aa02f01f275c9df04b6"
)


def verify_authorization_a(path: Path = AUTHORIZATION_A_PATH) -> tuple[bytes, str]:
    try:
        raw, digest = read_authority_snapshot(path, "authorization-a")
    except EvidenceError as exc:
        if exc.code == "E_PILOT_SOURCE_IDENTITY":
            raise EvidenceError(
                "E_PILOT_PREPARATION_AUTH_ABSENT",
                "authorization A is absent or unsafe",
            ) from exc
        raise
    if raw != AUTHORIZATION_A_BYTES or digest != AUTHORIZATION_A_SHA256:
        raise EvidenceError(
            "E_PILOT_PREPARATION_AUTH",
            "authorization A bytes or hash differ",
        )
    return raw, digest
```

---

## Acyclic Authority Dependency Graph

Frozen directed edges mean "must exist before". The graph must be a DAG. Launch authority must not be a predecessor of the launch verdict.

```python
AUTHORITY_DEPENDENCY_EDGES = [
    ("source_preparation_plan", "plan_verdict"),
    ("plan_verdict", "capability_verdict"),
    ("capability_verdict", "authorization_a"),
    ("authorization_a", "launch_packet"),
    ("plan_verdict", "launch_packet"),
    ("capability_verdict", "launch_packet"),
    ("launch_packet", "launch_verdict"),
    ("plan_verdict", "launch_verdict"),
    ("capability_verdict", "launch_verdict"),
    ("authorization_a", "launch_verdict"),
    ("source_preparation_plan", "launch_authority"),
    ("plan_verdict", "launch_authority"),
    ("capability_verdict", "launch_authority"),
    ("launch_packet", "launch_authority"),
    ("launch_verdict", "launch_authority"),
    ("authorization_a", "launch_authority"),
    ("launch_authority", "source_manifest"),
    ("authorization_a", "source_manifest"),
    ("source_manifest", "pass_result"),
]
UNIQUE_AUTHORITY_ORDER = [
    "source_preparation_plan",
    "plan_verdict",
    "capability_verdict",
    "authorization_a",
    "launch_packet",
    "launch_verdict",
    "launch_authority",
    "source_manifest",
    "pass_result",
]
PROCESS_ORDER = [
    "G1_FOUNDATION_IMPLEMENTATION_PASS",
    "independent_source_preparation_plan_review",
    "formal_source_preparation_plan_verdict_archival",
    "capability_implementation",
    "independent_capability_implementation_review",
    "formal_capability_implementation_verdict_archival",
    "user_authorization_a",
    "production_launch_packet",
    "independent_launch_packet_review",
    "launch_sol_high_verdict_archival",
    "exclusive_create_source_preparation_launch",
    "production_source_preparation",
    "independent_manifest_result_review",
]
PROCESS_AUTHORITY_PROJECTION = list(UNIQUE_AUTHORITY_ORDER)


def count_topological_authority_orders(
    edges: list[tuple[str, str]],
    limit: int = 2,
) -> int:
    nodes = {node for edge in edges for node in edge}
    outgoing: dict[str, list[str]] = {node: [] for node in nodes}
    incoming = {node: 0 for node in nodes}
    for start, end in edges:
        outgoing[start].append(end)
        incoming[end] += 1
    found = 0

    def walk(indeg: dict[str, int], ready: list[str], placed: int) -> None:
        nonlocal found
        if found >= limit:
            return
        if placed == len(nodes):
            found += 1
            return
        if not ready:
            raise ValueError("authority dependency graph contains a cycle")
        for index in range(len(ready)):
            if found >= limit:
                return
            node = ready[index]
            next_ready = ready[:index] + ready[index + 1 :]
            next_indeg = dict(indeg)
            for nxt in outgoing[node]:
                next_indeg[nxt] -= 1
                if next_indeg[nxt] == 0:
                    next_ready.append(nxt)
            walk(next_indeg, next_ready, placed + 1)

    start_ready = [node for node, value in incoming.items() if value == 0]
    walk(incoming, start_ready, 0)
    return found


def require_unique_topological_authority_order(
    edges: list[tuple[str, str]],
) -> list[str]:
    nodes = {node for edge in edges for node in edge}
    outgoing: dict[str, list[str]] = {node: [] for node in nodes}
    incoming = {node: 0 for node in nodes}
    for start, end in edges:
        outgoing[start].append(end)
        incoming[end] += 1
    order: list[str] = []
    remaining = set(nodes)
    while remaining:
        ready = [node for node in remaining if incoming[node] == 0]
        if not ready:
            raise ValueError("authority dependency graph contains a cycle")
        if len(ready) > 1:
            raise ValueError(
                "authority dependency graph has a non-unique topological order"
            )
        node = ready[0]
        order.append(node)
        remaining.remove(node)
        for nxt in outgoing[node]:
            incoming[nxt] -= 1
    if count_topological_authority_orders(edges, limit=2) != 1:
        raise ValueError(
            "authority dependency graph has a non-unique topological order"
        )
    if order != UNIQUE_AUTHORITY_ORDER:
        raise ValueError("unique topological order differs from the frozen sequence")
    return order
```

Lexicographic ready-set tie-breaking is not a uniqueness proof. `require_unique_topological_authority_order` rejects a cycle and rejects any graph with more than one legal topological order. The unique production snapshot order is exactly `UNIQUE_AUTHORITY_ORDER`. Authorization A is not an initial ready node. It becomes ready only after the capability verdict. The launch packet becomes ready only after Authorization A. Concrete production read sequence:

1. Source-preparation plan markdown snapshot.
2. Source-preparation plan verdict snapshot, parsed and validated against the plan snapshot hash.
3. Capability implementation verdict snapshot, parsed and validated against the plan snapshot hash and the plan-verdict snapshot hash.
4. Safe single-fd snapshots of `src/p3_v3/pilot_source.py` and `scripts/p3_v3/pilot.py`; require those digests to equal the capability verdict. Missing files or byte drift write zero production outputs.
5. Authorization A snapshot and exact-byte check.
6. Launch packet snapshot, which may exist only after Authorization A.
7. Launch verdict snapshot, parsed and validated against the packet, plan-verdict, capability-verdict, and Authorization A snapshot hashes. The launch verdict must not mention a launch-authority hash.
8. Launch authority snapshot, parsed and validated against every snapshot hash from steps 1 through 7, including the launch-verdict snapshot hash.

Missing capability verdict, missing launch authority, schema drift, or runtime production-byte drift writes zero production outputs.

Gate-chain predecessor set used by both the source manifest and every FAIL result:

```python
def gate_chain_predecessor_sha256(
    plan_sha256: str,
    plan_verdict_sha256: str,
    capability_verdict_sha256: str,
    launch_sha256: str,
    authorization_a_sha256: str,
) -> list[str]:
    return sorted(
        [
            plan_sha256,
            plan_verdict_sha256,
            capability_verdict_sha256,
            launch_sha256,
            authorization_a_sha256,
        ]
    )
```

PASS result predecessor equals that list plus the source-manifest file SHA-256, then sorted again.

---

## Fixed Subject Identities

Copy these labels exactly. Presence of a label does not prove that a real archive was opened.

- `p12_item_id = C-BOOSTMATH-001`
- `neutral_snapshot_id = 74cdc825c3c728c25f5ea857af1565350515a4e631fb0a874c26e810ec437886`
- `normalized_source_tree_sha256 = 93a62859d7fdd6b2068e494bbe6e3e27180b874cbd27055ac27f941e507a90d8`
- `controlled_subject_source_id = e5f21a7d067d641d0a20bfc57c61e630d6f7588ef30235cea49c9a9cf950c7a7`
- `controlled_subject_id = 89b0e6791c611b465b9216e833e0c526a53ffd6946b5cd20de045e3641f43914`
- `build_descriptor_sha256 = 68d2e0fd34b845bb0df22b29003f26259d5655d2ec80c18895ff36904db2d95d`
- `adapter_id = CMAKE_CTEST_V1`
- `ecosystem = cmake`
- `execution_class = PILOT_ONLY`
- `denominator = PILOT_ONLY`
- `cpu_only = true`
- `cuda_required = false`

`build_descriptor_sha256` is a frozen authority label. The source manifest records that label. It does not prove CMake configure PASS, compile PASS, test PASS, or public-behavior PASS.

---

## Approved Future File Map

The later implementation task may create only:

- `src/p3_v3/pilot_source.py`
- `tests/p3_v3/test_pilot_source.py`

The later implementation task may modify only:

- `scripts/p3_v3/pilot.py`
- `tests/p3_v3/test_pilot.py`

The later implementation task must not modify:

- `src/p3_v3/artifacts.py`
- `src/p3_v3/bridge_and_frames.py`
- `src/p3_v3/packages.py`
- `src/p3_v3/run_records.py`
- protocol files
- the claim ledger
- Phase 1 Frame files
- the foundation plan verdict
- the foundation implementation verdict
- the machine plan
- the complete 2026-08-15 plan

The later implementation task must not create any new artifact under `data/p3_v3/pilot/boost_math/`.

Reserved production paths, exclusive-created only by later separately authorized archival or production nodes:

- `data/p3_v3/pilot/boost_math/source-manifest.json`
- `data/p3_v3/pilot/boost_math/source-preparation-result.json`
- `data/p3_v3/pilot/boost_math/source-preparation-launch.json`
- `data/p3_v3/pilot/boost_math/user-auth-preparation.txt`
- `docs/review_20260817/boost_math_pilot_source_preparation_sol_high_review.md`
- `docs/review_20260817/boost_math_pilot_source_preparation_implementation_sol_high_review.md`
- `docs/review_20260817/boost_math_pilot_source_preparation_launch_packet.md`
- `docs/review_20260817/boost_math_pilot_source_preparation_launch_sol_high_review.md`

---

## Archive Snapshot Contract

Immutable snapshot:

```python
from __future__ import annotations

import hashlib
import os
import stat
from dataclasses import dataclass
from pathlib import Path

from p3_v3.artifacts import EvidenceError


@dataclass(frozen=True)
class ArchiveSnapshot:
    raw: bytes
    sha256: str
    size: int
    archive_format: str


def detect_archive_format(raw: bytes) -> str:
    zip_magic = raw.startswith(b"PK\x03\x04") or raw.startswith(b"PK\x05\x06")
    tar_magic = len(raw) >= 262 and raw[257:262] == b"ustar"
    if zip_magic and tar_magic:
        raise EvidenceError(
            "E_PILOT_ARCHIVE_FORMAT",
            "archive format is ambiguous",
        )
    if zip_magic:
        return "ZIP"
    if tar_magic:
        return "TAR"
    raise EvidenceError(
        "E_PILOT_ARCHIVE_FORMAT",
        "archive format is unsupported or corrupt",
    )


def read_production_archive_bytes(archive_path: str | Path) -> ArchiveSnapshot:
    path = Path(archive_path)
    flags = os.O_RDONLY | os.O_CLOEXEC
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        fd = os.open(path, flags)
    except OSError as exc:
        raise EvidenceError("E_PILOT_ARCHIVE_UNSAFE", "archive cannot be opened") from exc
    try:
        before = os.fstat(fd)
        if not stat.S_ISREG(before.st_mode):
            raise EvidenceError(
                "E_PILOT_ARCHIVE_UNSAFE",
                "archive is not a regular file",
            )
        chunks: list[bytes] = []
        while True:
            chunk = os.read(fd, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        after = os.fstat(fd)
        if (
            before.st_dev,
            before.st_ino,
            before.st_size,
            before.st_mtime_ns,
        ) != (
            after.st_dev,
            after.st_ino,
            after.st_size,
            after.st_mtime_ns,
        ):
            raise EvidenceError(
                "E_PILOT_ARCHIVE_UNSAFE",
                "archive identity changed during read",
            )
        raw = b"".join(chunks)
        if len(raw) != before.st_size:
            raise EvidenceError(
                "E_PILOT_ARCHIVE_UNSAFE",
                "archive size differs from st_size",
            )
        digest = hashlib.sha256(raw).hexdigest()
        archive_format = detect_archive_format(raw)
        return ArchiveSnapshot(
            raw=raw,
            sha256=digest,
            size=before.st_size,
            archive_format=archive_format,
        )
    finally:
        os.close(fd)
```

Hard rules:

- Use one `os.open`.
- Use `O_RDONLY | O_CLOEXEC`.
- Add `O_NOFOLLOW` when the platform provides it.
- `os.fstat` must prove a regular file.
- Compare `st_dev`, `st_ino`, `st_size`, and `st_mtime_ns` before and after the read.
- Read all bytes from that same opened descriptor.
- Hash those same raw bytes.
- The read length must equal `st_size`.
- Do not hash a path and then reopen the path for extraction.
- Do not follow a symlink.
- Do not accept a directory, FIFO, device, or socket.
- Detect archive format from bytes, not from the filename suffix.
- After the snapshot returns, the extractor may consume only `snapshot.raw`.

---

## Extractor Policy

Exact policy object. `extractor_policy_sha256 = canonical_sha256(EXTRACTOR_POLICY_V1)`.

```python
EXTRACTOR_POLICY_V1 = {
    "schema_version": "p3-pilot-extractor-policy-v1",
    "accepted_formats": ["TAR", "ZIP"],
    "strip_single_top_level_directory": True,
    "max_member_count": 100000,
    "max_member_bytes": 536870912,
    "max_total_uncompressed_bytes": 4294967296,
    "reject_absolute_paths": True,
    "reject_parent_traversal": True,
    "reject_backslash_paths": True,
    "reject_nul_paths": True,
    "reject_symlinks": True,
    "reject_hardlinks": True,
    "reject_devices": True,
    "reject_fifos": True,
    "reject_sockets": True,
    "reject_duplicate_normalized_paths": True,
    "reject_casefold_collisions": True,
    "reject_target_escape": True,
    "reject_encrypted_zip_members": True,
}

EXTRACTOR_POLICY_SHA256 = (
    "e482ea272a6836099b9dc52deab7d799e24c571c9433fdafe2cff6de48bbb229"
)
```

The later implementation must compute `canonical_sha256(EXTRACTOR_POLICY_V1)` and require that it equal `EXTRACTOR_POLICY_SHA256`.

The extractor must reject all of the following and raise `E_PILOT_EXTRACT_UNSAFE` or, for format problems, `E_PILOT_ARCHIVE_FORMAT`:

- POSIX absolute path
- Windows absolute path
- `..` traversal
- backslash path
- NUL in a path
- symlink
- hardlink
- device
- FIFO
- socket
- ZIP encrypted member
- duplicate normalized path
- Unicode casefold collision
- target-root escape
- member count above `max_member_count`
- one member whose streamed bytes exceed `max_member_bytes`
- total streamed uncompressed bytes above `max_total_uncompressed_bytes`
- unsupported archive format
- corrupt archive
- archive format ambiguity

Member-count, single-member, and total-uncompressed limits are enforced by actual streamed read and write byte counts. Archive metadata sizes are not trusted as the limit authority.

```python
from __future__ import annotations

from p3_v3.artifacts import EvidenceError


class StreamedLimitCounter:
    def __init__(self, policy: dict) -> None:
        self.max_member_count = policy["max_member_count"]
        self.max_member_bytes = policy["max_member_bytes"]
        self.max_total_uncompressed_bytes = policy["max_total_uncompressed_bytes"]
        self.member_count = 0
        self.total_bytes = 0
        self._open = False
        self._current_member_bytes = 0

    def begin_member(self) -> None:
        if self._open:
            raise EvidenceError("E_PILOT_EXTRACT_UNSAFE", "member is already open")
        prospective_count = self.member_count + 1
        if prospective_count > self.max_member_count:
            raise EvidenceError("E_PILOT_EXTRACT_UNSAFE", "member count exceeds policy")
        self.member_count = prospective_count
        self._current_member_bytes = 0
        self._open = True

    def consume_chunk(self, chunk_length: object) -> None:
        if type(chunk_length) is not int or chunk_length < 0:
            raise EvidenceError(
                "E_PILOT_EXTRACT_UNSAFE",
                "chunk length must be a nonnegative int",
            )
        if not self._open:
            raise EvidenceError("E_PILOT_EXTRACT_UNSAFE", "no open member")
        prospective_member = self._current_member_bytes + chunk_length
        prospective_total = self.total_bytes + chunk_length
        if prospective_member > self.max_member_bytes:
            raise EvidenceError(
                "E_PILOT_EXTRACT_UNSAFE",
                "streamed member bytes exceed policy",
            )
        if prospective_total > self.max_total_uncompressed_bytes:
            raise EvidenceError(
                "E_PILOT_EXTRACT_UNSAFE",
                "streamed total bytes exceed policy",
            )
        self._current_member_bytes = prospective_member
        self.total_bytes = prospective_total

    def end_member(self) -> None:
        if not self._open:
            raise EvidenceError("E_PILOT_EXTRACT_UNSAFE", "no open member")
        self._open = False
```

The extractor loop must use a fixed upper-bound chunk size. It must call `begin_member()` before any content, call `consume_chunk(len(chunk))` before writing that chunk to staging, and call `end_member()` after the member ends. A failed `consume_chunk` must not write that chunk. Archive metadata sizes may be used only to reject early. They must not replace the actual byte counter.

Extraction writes into a newly created staging directory. The caller-supplied materialize root must not exist at the start of a fresh PASS attempt. Success atomically renames the staging directory onto that root only after the source manifest has been exclusive-created. Failure may delete only the staging directory created by that attempt. The extractor must not delete or replace a pre-existing materialize root.

`strip_single_top_level_directory` applies only when every accepted member shares one nonempty top-level directory component that is actually a directory layer. A single top-level regular file must return `None` and must not be stripped. The decision must be independent of member order.

```python
from __future__ import annotations


def shared_top_level_directory(member_names: list[str]) -> str | None:
    records: list[tuple[str, bool]] = []
    for name in member_names:
        first, separator, remainder = name.partition("/")
        if not first:
            return None
        is_directory_layer = bool(separator) or name.endswith("/")
        records.append((first, is_directory_layer))
    tops = {first for first, _is_directory_layer in records}
    if len(tops) != 1:
        return None
    top = next(iter(tops))
    has_directory_layer = any(
        first == top and is_directory_layer for first, is_directory_layer in records
    )
    has_file_named_top = any(
        first == top and not is_directory_layer for first, is_directory_layer in records
    )
    if has_file_named_top or not has_directory_layer:
        return None
    return top
```

`shared_top_level_directory(["readme.txt"])` must return `None`. `shared_top_level_directory(["pkg/a", "pkg/b"])` and `shared_top_level_directory(["pkg/b", "pkg/a"])` must both return `pkg`.

---

## Normalized Tree Binding

Reuse without changing scientific meaning:

- `SourceSnapshot`
- `SourceSnapshotEntry`
- `canonical_source_tree_sha256`

Source: `src/p3_v3/bridge_and_frames.py`. Do not invent a second tree-hash algorithm. Do not modify that module.

Materialized tree capture must:

- walk the complete payload root;
- sort relative paths by UTF-8 path bytes;
- `lstat` every node;
- reject a symlink or special node with `E_PILOT_EXTRACT_UNSAFE`;
- read each regular file through one regular-file snapshot, reusing `read_regular_file_snapshot` from `src/p3_v3/artifacts.py`;
- project mode only to `100644` or `100755`;
- build a complete `SourceSnapshot`;
- call `canonical_source_tree_sha256(snapshot)` on the production tree-validation seam;
- use that returned hash for the frozen-hash comparison;
- require the result to equal `93a62859d7fdd6b2068e494bbe6e3e27180b874cbd27055ac27f941e507a90d8` on the production seam.

```python
from __future__ import annotations

import os
import stat
from pathlib import Path

from p3_v3.artifacts import EvidenceError, read_regular_file_snapshot
from p3_v3.bridge_and_frames import (
    SourceSnapshot,
    SourceSnapshotEntry,
    canonical_source_tree_sha256,
)

FROZEN_NORMALIZED_SOURCE_TREE_SHA256 = (
    "93a62859d7fdd6b2068e494bbe6e3e27180b874cbd27055ac27f941e507a90d8"
)


def _projected_mode(mode: int) -> str:
    if mode & 0o111:
        return "100755"
    return "100644"


def capture_materialized_tree(payload_root: Path) -> SourceSnapshot:
    entries: list[SourceSnapshotEntry] = []
    for dirpath, dirnames, filenames in os.walk(payload_root, followlinks=False):
        for name in list(dirnames) + list(filenames):
            full = Path(dirpath) / name
            info = os.lstat(full)
            if stat.S_ISLNK(info.st_mode) or not (
                stat.S_ISREG(info.st_mode) or stat.S_ISDIR(info.st_mode)
            ):
                raise EvidenceError(
                    "E_PILOT_EXTRACT_UNSAFE",
                    f"materialized node is not a regular file or directory: {full}",
                )
            if stat.S_ISDIR(info.st_mode):
                continue
            relative = full.relative_to(payload_root).as_posix()
            raw, raw_mode = read_regular_file_snapshot(full, "materialized-source")
            entries.append(
                SourceSnapshotEntry(
                    relative_path=relative,
                    mode=_projected_mode(raw_mode),
                    sha256=__import__("hashlib").sha256(raw).hexdigest(),
                    content=raw,
                )
            )
    entries.sort(key=lambda item: item.relative_path.encode("utf-8"))
    return SourceSnapshot(entries=tuple(entries))


def validate_materialized_tree_with_phase1(snapshot: SourceSnapshot) -> str:
    if type(snapshot) is not SourceSnapshot:
        raise EvidenceError("E_PILOT_SOURCE_TREE_MISMATCH", "snapshot type differs")
    observed = canonical_source_tree_sha256(snapshot)
    if observed != FROZEN_NORMALIZED_SOURCE_TREE_SHA256:
        raise EvidenceError(
            "E_PILOT_SOURCE_TREE_MISMATCH",
            observed,
        )
    return observed
```

The production seam is `validate_materialized_tree_with_phase1`. It must receive the `SourceSnapshot` produced by `capture_materialized_tree`, call Phase 1 `canonical_source_tree_sha256` exactly, use that return value for the frozen-hash comparison, and must not call a second tree-hash implementation.

Capability-unit tests use synthetic trees. Those trees will not equal the frozen Boost.Math hash unless a test spies the Phase 1 function. `test_wrong_materialized_tree_writes_failure_result` must prove that a non-frozen tree writes `SOURCE_TREE_MISMATCH`, records the actual observed hash, and does not write a source manifest or materialize root. Tests may monkeypatch output-path constants onto `tmp_path`. Tests must not write production files under `data/p3_v3/pilot/boost_math/`.

---

## Crash-Safe Publication Order

Fresh PASS attempt, after the complete gate chain and Authorization A have validated and after output reconciliation says a fresh attempt is legal:

1. Verify every authority snapshot in `UNIQUE_AUTHORITY_ORDER`, including Authorization A after the capability verdict and before the launch packet, and verify the initial output state.
2. Obtain one stable `ArchiveSnapshot` from a single archive fd.
3. Unpack only into a newly created staging directory.
4. On that staging payload, finish a complete `SourceSnapshot`, Phase 1 tree hash, file count, and total bytes.
5. On tree mismatch or extraction failure: delete only that staging directory; do not create a materialize root; do not create a source manifest; then exclusive-create the FAIL result last, if and only if the gate chain was already valid.
6. On success, construct the PASS manifest object and the PASS result object in memory and validate both before any durable write.
7. Frozen publication order:
   1. source manifest exclusive-create
   2. atomic rename of the validated staging directory onto the materialize root
   3. PASS result exclusive-create last

A source manifest by itself does not represent PASS. Only the closed pair of that manifest and a valid PASS result represents preparation PASS. The PASS result is always the final PASS commit point.

---

## Reconciliation State Table

First safely parse any existing manifest or result. If either durable object fails schema, self-hash, or predecessor checks, return exactly `INVALID_DURABLE_OBJECT`. That state is not mixed with presence states.

M means manifest, R means result, D means materialize root. The twelve states below are mutually exclusive. Every reachable presence, status, and validity combination hits exactly one state.

| State | Manifest | Result | Root | Action |
|---|---|---|---|---|
| `FRESH` | M0 | R0 | D0 | run the frozen publication order |
| `ORPHAN_ROOT` | M0 | R0 | D1 | fail closed; do not delete the root |
| `MANIFEST_ONLY` | valid M1 | R0 | D0 | verify the existing manifest, current gate chain, and the same archive snapshot; restage; revalidate tree, count, and bytes; rename; exclusive-create the PASS result |
| `MANIFEST_AND_ROOT` | valid M1 | R0 | D1 | safely capture the existing root; require tree hash, file count, and total bytes to equal the manifest; exclusive-create the PASS result; do not rename again |
| `FAILURE_TERMINAL` | M0 | valid FAIL | D0 | treat as terminal; do not overwrite |
| `INVALID_FAILURE_ROOT` | M0 | valid FAIL | D1 | fail closed; do not delete the root or the FAIL result |
| `INVALID_FAILURE_MANIFEST` | M1 | valid FAIL | D0 or D1 | fail closed; FAIL result plus manifest must not continue |
| `INVALID_PASS_NO_MANIFEST` | M0 | valid PASS | D0 or D1 | fail closed; do not invent a manifest |
| `INVALID_PASS_NO_ROOT` | valid M1 | valid PASS | D0 | fail closed; PASS without a root is incomplete |
| `ALREADY_COMPLETE` | valid M1 | valid PASS | D1, and manifest, result, and root agree | re-verify root tree, count, and bytes; report already complete; do not create a second result |
| `INVALID_CLOSED_PAIR` | valid M1 | valid PASS | D1, but pair or root disagrees | fail closed; do not delete or overwrite |
| `INVALID_DURABLE_OBJECT` | any present durable object has invalid schema, hash, or predecessor | any | any | fail closed; do not delete or overwrite |

```python
from __future__ import annotations

RECONCILIATION_STATES = (
    "FRESH",
    "ORPHAN_ROOT",
    "MANIFEST_ONLY",
    "MANIFEST_AND_ROOT",
    "FAILURE_TERMINAL",
    "INVALID_FAILURE_ROOT",
    "INVALID_FAILURE_MANIFEST",
    "INVALID_PASS_NO_MANIFEST",
    "INVALID_PASS_NO_ROOT",
    "ALREADY_COMPLETE",
    "INVALID_CLOSED_PAIR",
    "INVALID_DURABLE_OBJECT",
)


def classify_reconciliation(
    *,
    manifest_present: bool,
    result_present: bool,
    root_present: bool,
    manifest_valid: bool,
    result_valid: bool,
    result_status: str | None,
    closed_pair_consistent: bool,
) -> str:
    if manifest_present and not manifest_valid:
        return "INVALID_DURABLE_OBJECT"
    if result_present and not result_valid:
        return "INVALID_DURABLE_OBJECT"
    if not manifest_present and not result_present and not root_present:
        return "FRESH"
    if not manifest_present and not result_present and root_present:
        return "ORPHAN_ROOT"
    if manifest_present and not result_present and not root_present:
        return "MANIFEST_ONLY"
    if manifest_present and not result_present and root_present:
        return "MANIFEST_AND_ROOT"
    if (
        not manifest_present
        and result_present
        and result_status == "FAIL_INFRASTRUCTURE"
    ):
        if root_present:
            return "INVALID_FAILURE_ROOT"
        return "FAILURE_TERMINAL"
    if manifest_present and result_present and result_status == "FAIL_INFRASTRUCTURE":
        return "INVALID_FAILURE_MANIFEST"
    if not manifest_present and result_present and result_status == "PASS":
        return "INVALID_PASS_NO_MANIFEST"
    if (
        manifest_present
        and result_present
        and result_status == "PASS"
        and not root_present
    ):
        return "INVALID_PASS_NO_ROOT"
    if manifest_present and result_present and result_status == "PASS" and root_present:
        if closed_pair_consistent:
            return "ALREADY_COMPLETE"
        return "INVALID_CLOSED_PAIR"
    raise AssertionError("unclassified reconciliation combination")


def enumerate_reconciliation_cases() -> list[tuple]:
    cases: list[tuple] = []
    for manifest_present in (False, True):
        for result_present in (False, True):
            for root_present in (False, True):
                manifest_valids = (True,) if not manifest_present else (True, False)
                result_valids = (True,) if not result_present else (True, False)
                if not result_present:
                    result_statuses = (None,)
                else:
                    result_statuses = ("FAIL_INFRASTRUCTURE", "PASS")
                for manifest_valid in manifest_valids:
                    for result_valid in result_valids:
                        for result_status in result_statuses:
                            need_pair = (
                                manifest_present
                                and result_present
                                and root_present
                                and manifest_valid
                                and result_valid
                                and result_status == "PASS"
                            )
                            consistents = (True, False) if need_pair else (True,)
                            for closed_pair_consistent in consistents:
                                state = classify_reconciliation(
                                    manifest_present=manifest_present,
                                    result_present=result_present,
                                    root_present=root_present,
                                    manifest_valid=manifest_valid,
                                    result_valid=result_valid,
                                    result_status=result_status,
                                    closed_pair_consistent=closed_pair_consistent,
                                )
                                cases.append(
                                    (
                                        manifest_present,
                                        result_present,
                                        root_present,
                                        manifest_valid,
                                        result_valid,
                                        result_status,
                                        closed_pair_consistent,
                                        state,
                                    )
                                )
    return cases
```

Hard rules:

- FAIL result and manifest together must fail closed.
- PASS result missing a manifest or a root must fail closed.
- `ALREADY_COMPLETE` must re-verify root tree hash, file count, and total bytes.
- Invalid or orphan durable objects must not be deleted or overwritten.
- Future tests must enumerate every combination through `enumerate_reconciliation_cases`.

---

## Source Manifest Exact Schema

`PILOT_SOURCE_MANIFEST_EXACT` has these exact keys and exact types. No extra key is legal.

```python
PILOT_SOURCE_MANIFEST_EXACT = {
    "schema_version": str,
    "execution_class": str,
    "denominator": str,
    "p12_item_id": str,
    "neutral_snapshot_id": str,
    "normalized_source_tree_sha256": str,
    "controlled_subject_id": str,
    "controlled_subject_source_id": str,
    "predecessor_sha256": list,
    "archive_sha256": str,
    "archive_bytes": int,
    "archive_format": str,
    "build_descriptor_sha256": str,
    "authorization_a_sha256": str,
    "extractor_policy_sha256": str,
    "materialized_file_count": int,
    "materialized_total_bytes": int,
    "artifact_sha256": str,
}
```

Required literals after `validate_exact_object(value, PILOT_SOURCE_MANIFEST_EXACT, "p3-pilot-source-manifest-v1")`:

- `schema_version = p3-pilot-source-manifest-v1`
- `execution_class = PILOT_ONLY`
- `denominator = PILOT_ONLY`
- `p12_item_id`, `neutral_snapshot_id`, `normalized_source_tree_sha256`, `controlled_subject_id`, `controlled_subject_source_id`, and `build_descriptor_sha256` equal the frozen subject identities
- `archive_format` is `ZIP` or `TAR`
- `authorization_a_sha256` equals `502c6407aa368a26948db10cc1ca0d1c91f66c8bfe702aa02f01f275c9df04b6`
- `extractor_policy_sha256` equals `e482ea272a6836099b9dc52deab7d799e24c571c9433fdafe2cff6de48bbb229`
- `predecessor_sha256` equals `gate_chain_predecessor_sha256` of the verified snapshots of the source-preparation plan, the source-preparation plan verdict, the capability implementation verdict, the launch authority, and Authorization A
- `artifact_sha256` is `canonical_sha256` of the object with that field removed
- `archive_bytes > 0` and `type(archive_bytes) is int`
- `materialized_file_count > 0` and `type(materialized_file_count) is int`
- `materialized_total_bytes >= 0` and `type(materialized_total_bytes) is int`

A `bool` must not pass exact-type validation for `archive_bytes`, `materialized_file_count`, or `materialized_total_bytes`. Every non-`None` SHA field must pass `validate_sha256`.

`archive_sha256` and `archive_bytes` are copied from the `ArchiveSnapshot` that was actually opened. This plan does not invent those production values.

Production path, reserved:

```text
data/p3_v3/pilot/boost_math/source-manifest.json
```

Only a later separately authorized production preparation node may exclusive-create that file. A source-manifest object must fail `validate_pilot_plan`.

---

## Preparation Result Exact Schema

`PILOT_SOURCE_PREPARATION_RESULT_EXACT` has these exact keys and exact types. No extra key is legal.

```python
PILOT_SOURCE_PREPARATION_RESULT_EXACT = {
    "schema_version": str,
    "execution_class": str,
    "denominator": str,
    "p12_item_id": str,
    "neutral_snapshot_id": str,
    "normalized_source_tree_sha256": str,
    "controlled_subject_id": str,
    "controlled_subject_source_id": str,
    "predecessor_sha256": list,
    "terminal_status": str,
    "failure_reason": (str, type(None)),
    "source_manifest_sha256": (str, type(None)),
    "archive_sha256": (str, type(None)),
    "archive_bytes": (int, type(None)),
    "materialized_tree_sha256": (str, type(None)),
    "artifact_sha256": str,
}
```

Production path, reserved:

```text
data/p3_v3/pilot/boost_math/source-preparation-result.json
```

Required rules after `validate_exact_object(value, PILOT_SOURCE_PREPARATION_RESULT_EXACT, "p3-pilot-source-preparation-result-v1")`:

- `schema_version` equals `p3-pilot-source-preparation-result-v1`
- `execution_class` equals `PILOT_ONLY`
- `denominator` equals `PILOT_ONLY`
- subject identity fields equal the frozen labels
- `terminal_status` is `PASS` or `FAIL_INFRASTRUCTURE`
- `artifact_sha256` is `canonical_sha256` of the object with that field removed
- every non-`None` SHA field passes `validate_sha256`
- `archive_bytes` is `int` or `None`, never `bool`

PASS rules:

- `failure_reason is None`
- `source_manifest_sha256` is a nonempty SHA-256
- `archive_sha256`, `archive_bytes`, and `materialized_tree_sha256` are nonempty
- `materialized_tree_sha256` equals `93a62859d7fdd6b2068e494bbe6e3e27180b874cbd27055ac27f941e507a90d8`
- `predecessor_sha256` equals the source-manifest predecessors plus the source-manifest file SHA-256, sorted

Authorization missing or invalid, or any gate-chain authority missing, hash-mismatched, drifted, or non-PASS: create no result, because preparation is not authorized.

---

## FAIL Result Evidence Matrix

`FAIL_RESULT_EVIDENCE` is exact. Each `failure_reason` freezes field presence, root existence, and manifest existence. Fields that were never obtained from a stable archive snapshot must be `None`. A failure result must not claim a source manifest. `source_manifest_sha256` is `None` on every FAIL row. FAIL predecessor is the gate-chain set only.

| failure_reason | archive_sha256 | archive_bytes | materialized_tree_sha256 | source_manifest_sha256 | materialize root | source manifest | predecessor |
|---|---|---|---|---|---|---|---|
| `ARCHIVE_UNSAFE` | `None` | `None` | `None` | `None` | must be absent for this attempt | must be absent | gate chain |
| `ARCHIVE_FORMAT_UNSUPPORTED` | observed pair if a stable snapshot existed, else `None` | same pairing rule | `None` | `None` | must be absent | must be absent | gate chain |
| `EXTRACTION_UNSAFE` | observed snapshot pair, required | observed snapshot pair, required | `None`; must not invent a tree hash | `None` | must be absent | must be absent | gate chain |
| `SOURCE_TREE_MISMATCH` | observed snapshot pair, required | observed snapshot pair, required | actual mismatched tree hash, required | `None` | must be absent | must be absent | gate chain |

Pairing rule: `archive_sha256` and `archive_bytes` are both `None` or both present. A present pair must equal the stable `ArchiveSnapshot`. `SOURCE_TREE_MISMATCH` must record the actual observed `canonical_source_tree_sha256` return value, not the frozen expected hash.

Error-code mapping:

| Code | When | Writes result |
|---|---|---|
| `E_PILOT_PREPARATION_AUTH_ABSENT` | authorization snapshot absent or unsafe | no |
| `E_PILOT_PREPARATION_AUTH` | authorization bytes or hash differ | no |
| `E_PILOT_SOURCE_PREPARATION_PLAN_VERDICT_ABSENT` | plan verdict missing | no |
| `E_PILOT_SOURCE_PREPARATION_PLAN_VERDICT` | plan verdict hash, schema, or PASS check fails | no |
| `E_PILOT_SOURCE_PREPARATION_CAPABILITY_VERDICT_ABSENT` | capability verdict missing | no |
| `E_PILOT_SOURCE_PREPARATION_CAPABILITY_VERDICT` | capability verdict hash, schema, or PASS check fails | no |
| `E_PILOT_SOURCE_PREPARATION_LAUNCH_ABSENT` | launch authority missing | no |
| `E_PILOT_SOURCE_PREPARATION_LAUNCH` | launch authority hash, schema, or PASS check fails | no |
| `E_PILOT_SOURCE_IDENTITY` | subject label mismatch or unsafe authority snapshot mapping | no |
| `E_PILOT_SOURCE_OUTPUT_EXISTS` | durable objects forbid a fresh write after reconciliation | no |
| `E_PILOT_SOURCE_ORPHAN_ROOT` | root exists without manifest and result | no |
| `E_PILOT_ARCHIVE_UNSAFE` | snapshot rejects the archive path or identity | yes, `ARCHIVE_UNSAFE` |
| `E_PILOT_ARCHIVE_FORMAT` | unsupported, corrupt, or ambiguous format | yes, `ARCHIVE_FORMAT_UNSUPPORTED` |
| `E_PILOT_EXTRACT_UNSAFE` | extractor policy violation | yes, `EXTRACTION_UNSAFE` |
| `E_PILOT_SOURCE_TREE_MISMATCH` | materialized tree hash differs | yes, `SOURCE_TREE_MISMATCH` |

Result writes in the last four rows happen only after the complete gate chain and Authorization A have validated. They still do not write a source manifest or a materialize root.

---

## Production Gate Interface

The later implementation may add exactly one new verb to `scripts/p3_v3/pilot.py`:

```text
validate-source
```

The parser accepts only:

- `--archive`
- `--materialize-root`

The parser must not accept:

- authorization path
- output path
- expected archive hash
- expected tree hash
- expected build descriptor hash
- implementation verdict path
- machine plan path
- extractor policy override
- launch authority path
- plan verdict path
- capability verdict path

All of those authority paths, output paths, and frozen identities are module constants in `src/p3_v3/pilot_source.py`.

Existing `tests/p3_v3/test_cli.py::test_pilot_cli_forbids_source_and_execution_verbs` calls `parse_args(["validate-source"])` and expects `SystemExit`. Keep `--archive` and `--materialize-root` required so that call still exits. Do not modify `tests/p3_v3/test_cli.py`. Do not add a default archive path.

This plan does not contain an executable production command that names a fictional archive path. The real production command is written only in a later user-authorized, separately reviewed launch packet.

```python
from __future__ import annotations

import argparse


def add_validate_source_parser(sub: argparse._SubParsersAction) -> None:
    command = sub.add_parser("validate-source")
    command.add_argument("--archive", required=True)
    command.add_argument("--materialize-root", required=True)
```

`write-plan` and `validate-plan` remain. Forbidden verbs remain `extract`, `freeze`, `execute`, and `certify`.

---

## Explicitly Forbidden Extensions

The later implementation task must not:

- download or clone Boost.Math;
- read Package C or a P12 reveal;
- read buggy revisions, patches, reference or evaluated MRs, or outcomes;
- run CMake, a compiler, CTest, or public behavior;
- design a contract, site, MR, mutant, or certification;
- create a freeze, execution plan, attempt, score task, ledger event, or evidence package;
- modify confirmatory schemas;
- modify the claim ledger;
- interpret a source manifest as build PASS or scientific PASS;
- interpret a capability unit test as production preparation;
- create authorization A;
- create a plan verdict, capability verdict, launch authority, launch packet, or launch verdict;
- enter production preparation automatically;
- create any file under `data/p3_v3/pilot/boost_math/`.

---

### Task 1: Pilot Source-Preparation Capability On Synthetic Fixtures

**Files:**
- Create: `src/p3_v3/pilot_source.py`, `tests/p3_v3/test_pilot_source.py`
- Modify: `scripts/p3_v3/pilot.py`, `tests/p3_v3/test_pilot.py`
- Do not create: `data/p3_v3/pilot/boost_math/user-auth-preparation.txt`, `data/p3_v3/pilot/boost_math/source-manifest.json`, `data/p3_v3/pilot/boost_math/source-preparation-result.json`, `data/p3_v3/pilot/boost_math/source-preparation-launch.json`, `docs/review_20260817/boost_math_pilot_source_preparation_sol_high_review.md`, `docs/review_20260817/boost_math_pilot_source_preparation_implementation_sol_high_review.md`

**Interfaces:**
- Consumes: `validate_exact_object(value, schema, context)`, `canonical_sha256`, `validate_sha256`, `write_canonical_json`, `read_canonical_json`, `read_regular_file_snapshot`, `EvidenceError`, `SourceSnapshot`, `SourceSnapshotEntry`, `canonical_source_tree_sha256`
- Produces: `ArchiveSnapshot`, `read_production_archive_bytes`, `EXTRACTOR_POLICY_V1`, gate-chain validators, source-manifest and preparation-result validators, a fail-closed extractor, reconciliation, a `validate-source` CLI verb, and synthetic-fixture unit tests
- Does not produce: a production source manifest, a production preparation result, authorization A, a launch authority, a freeze, an execution plan, a claim-ledger write, or a production launch packet

User authorization required: no. Gate: capability implementation only. This planning node does not start the gate. Capability PASS does not authorize production preparation.

- [ ] **Step 1: Confirm the confirmatory baseline before any edit**

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

- [ ] **Step 2: Write the failing tests**

Create `tests/p3_v3/test_pilot_source.py` with at least these exact names:

```python
REQUIRED_SOURCE_PREPARATION_TESTS = [
    "test_authorization_absent_writes_no_output",
    "test_authorization_wrong_bytes_writes_no_output",
    "test_implementation_verdict_hash_mismatch_fails_closed",
    "test_machine_plan_hash_mismatch_fails_closed",
    "test_capability_verdict_absent_writes_no_output",
    "test_launch_authority_absent_writes_no_output",
    "test_runtime_production_bytes_drift_writes_no_output",
    "test_authority_snapshot_binds_validated_bytes_on_replacement_race",
    "test_capability_verdict_requires_reviewed_commit",
    "test_capability_verdict_binds_implementation_files",
    "test_authority_dependency_graph_has_exactly_one_topological_order",
    "test_reconciliation_classifier_is_total_and_exclusive",
    "test_streamed_chunk_exceeds_member_limit_before_write",
    "test_streamed_chunks_exceed_total_limit",
    "test_overlimit_chunk_is_not_written",
    "test_streamed_chunk_length_rejects_bool_and_negative",
    "test_member_count_checked_before_content",
    "test_plan_verdict_rejects_noncanonical",
    "test_plan_verdict_rejects_extra_key",
    "test_plan_verdict_rejects_wrong_type",
    "test_plan_verdict_rejects_bad_sha",
    "test_capability_verdict_rejects_noncanonical",
    "test_capability_verdict_rejects_extra_key",
    "test_capability_verdict_rejects_wrong_type",
    "test_capability_verdict_rejects_bad_sha",
    "test_launch_verdict_rejects_noncanonical",
    "test_launch_verdict_rejects_extra_key",
    "test_launch_verdict_rejects_wrong_type",
    "test_launch_verdict_rejects_bad_sha",
    "test_launch_authority_rejects_noncanonical",
    "test_launch_authority_rejects_extra_key",
    "test_launch_authority_rejects_wrong_type",
    "test_launch_authority_rejects_bad_sha",
    "test_archive_snapshot_rejects_symlink",
    "test_archive_snapshot_rejects_non_regular_file",
    "test_archive_snapshot_hashes_same_fd_bytes",
    "test_archive_snapshot_rejects_identity_change",
    "test_archive_format_uses_bytes_not_suffix",
    "test_zip_rejects_parent_traversal",
    "test_zip_rejects_symlink",
    "test_zip_rejects_encrypted_member",
    "test_tar_rejects_parent_traversal",
    "test_tar_rejects_symlink",
    "test_tar_rejects_hardlink",
    "test_extractor_rejects_casefold_collision",
    "test_extractor_rejects_duplicate_normalized_path",
    "test_extractor_rejects_member_limit",
    "test_extractor_rejects_total_bytes_limit",
    "test_streamed_member_bytes_cannot_exceed_declared_policy_limit",
    "test_single_top_level_selection_is_order_invariant",
    "test_single_top_level_file_is_not_stripped",
    "test_materialized_tree_uses_phase1_canonical_hash",
    "test_phase1_tree_hash_function_is_called_by_production_seam",
    "test_wrong_materialized_tree_writes_failure_result",
    "test_source_manifest_exact_keys",
    "test_source_manifest_predecessors_are_exact",
    "test_source_manifest_cannot_validate_as_pilot_plan",
    "test_pass_result_binds_source_manifest",
    "test_outputs_are_exclusive",
    "test_crash_after_manifest_publication",
    "test_crash_after_materialize_root_rename",
    "test_manifest_only_recovery",
    "test_manifest_and_root_recovery",
    "test_tampered_manifest_refuses_recovery",
    "test_orphan_root_without_manifest_refuses_recovery",
    "test_result_is_always_the_final_pass_commit_point",
    "test_tree_mismatch_leaves_materialize_root_and_manifest_absent",
    "test_validate_source_cli_has_no_authority_overrides",
    "test_capability_implementation_creates_no_production_artifact",
]
```

Minimum bodies that the later task must implement:

```python
from __future__ import annotations

from pathlib import Path

import pytest

from p3_v3.artifacts import EvidenceError
from p3_v3.bridge_and_frames import SourceSnapshot


def test_authorization_absent_writes_no_output(tmp_path, monkeypatch):
    import p3_v3.pilot_source as pilot_source

    monkeypatch.setattr(
        pilot_source,
        "AUTHORIZATION_A_PATH",
        tmp_path / "user-auth-preparation.txt",
    )
    monkeypatch.setattr(
        pilot_source,
        "SOURCE_MANIFEST_PATH",
        tmp_path / "source-manifest.json",
    )
    monkeypatch.setattr(
        pilot_source,
        "SOURCE_PREPARATION_RESULT_PATH",
        tmp_path / "source-preparation-result.json",
    )
    with pytest.raises(EvidenceError, match="E_PILOT_PREPARATION_AUTH_ABSENT"):
        pilot_source.run_validate_source(
            tmp_path / "missing.zip",
            tmp_path / "materialize",
        )
    assert not (tmp_path / "source-manifest.json").exists()
    assert not (tmp_path / "source-preparation-result.json").exists()
    assert not (tmp_path / "materialize").exists()


def test_capability_verdict_absent_writes_no_output(tmp_path, monkeypatch):
    import p3_v3.pilot_source as pilot_source

    monkeypatch.setattr(
        pilot_source,
        "CANONICAL_SOURCE_PREPARATION_CAPABILITY_VERDICT_PATH",
        tmp_path / "missing-capability-verdict.md",
    )
    monkeypatch.setattr(
        pilot_source,
        "SOURCE_MANIFEST_PATH",
        tmp_path / "source-manifest.json",
    )
    monkeypatch.setattr(
        pilot_source,
        "SOURCE_PREPARATION_RESULT_PATH",
        tmp_path / "source-preparation-result.json",
    )
    with pytest.raises(
        EvidenceError, match="E_PILOT_SOURCE_PREPARATION_CAPABILITY_VERDICT_ABSENT"
    ):
        pilot_source.run_validate_source(
            tmp_path / "missing.zip",
            tmp_path / "materialize",
        )
    assert not (tmp_path / "source-manifest.json").exists()
    assert not (tmp_path / "source-preparation-result.json").exists()


def test_launch_authority_absent_writes_no_output(tmp_path, monkeypatch):
    import p3_v3.pilot_source as pilot_source

    monkeypatch.setattr(
        pilot_source,
        "SOURCE_PREPARATION_LAUNCH_PATH",
        tmp_path / "missing-launch.json",
    )
    monkeypatch.setattr(
        pilot_source,
        "SOURCE_MANIFEST_PATH",
        tmp_path / "source-manifest.json",
    )
    monkeypatch.setattr(
        pilot_source,
        "SOURCE_PREPARATION_RESULT_PATH",
        tmp_path / "source-preparation-result.json",
    )
    with pytest.raises(
        EvidenceError, match="E_PILOT_SOURCE_PREPARATION_LAUNCH_ABSENT"
    ):
        pilot_source.run_validate_source(
            tmp_path / "missing.zip",
            tmp_path / "materialize",
        )
    assert not (tmp_path / "source-manifest.json").exists()
    assert not (tmp_path / "source-preparation-result.json").exists()


def test_archive_snapshot_hashes_same_fd_bytes(tmp_path):
    from p3_v3.pilot_source import read_production_archive_bytes

    archive = tmp_path / "fixture.zip"
    archive.write_bytes(b"PK\x03\x04" + b"synthetic-zip-bytes")
    snapshot = read_production_archive_bytes(archive)
    assert snapshot.sha256 == __import__("hashlib").sha256(snapshot.raw).hexdigest()
    assert snapshot.size == len(snapshot.raw)
    assert snapshot.archive_format == "ZIP"


def test_single_top_level_file_is_not_stripped():
    from p3_v3.pilot_source import shared_top_level_directory

    assert shared_top_level_directory(["readme.txt"]) is None
    assert shared_top_level_directory(["pkg/a", "pkg/b"]) == "pkg"
    assert shared_top_level_directory(["pkg/b", "pkg/a"]) == "pkg"


def test_authority_dependency_graph_has_exactly_one_topological_order():
    from p3_v3.pilot_source import (
        AUTHORITY_DEPENDENCY_EDGES,
        UNIQUE_AUTHORITY_ORDER,
        count_topological_authority_orders,
        require_unique_topological_authority_order,
    )

    order = require_unique_topological_authority_order(AUTHORITY_DEPENDENCY_EDGES)
    assert count_topological_authority_orders(AUTHORITY_DEPENDENCY_EDGES) == 1
    assert order == UNIQUE_AUTHORITY_ORDER
    missing_capability_to_auth = [
        edge
        for edge in AUTHORITY_DEPENDENCY_EDGES
        if edge != ("capability_verdict", "authorization_a")
    ]
    with pytest.raises(ValueError, match="non-unique topological order"):
        require_unique_topological_authority_order(missing_capability_to_auth)
    assert count_topological_authority_orders(missing_capability_to_auth) != 1
    missing_auth_to_packet = [
        edge
        for edge in AUTHORITY_DEPENDENCY_EDGES
        if edge != ("authorization_a", "launch_packet")
    ]
    with pytest.raises(ValueError, match="non-unique topological order"):
        require_unique_topological_authority_order(missing_auth_to_packet)
    assert count_topological_authority_orders(missing_auth_to_packet) != 1


def test_reconciliation_classifier_is_total_and_exclusive():
    from p3_v3.pilot_source import (
        RECONCILIATION_STATES,
        classify_reconciliation,
        enumerate_reconciliation_cases,
    )

    cases = enumerate_reconciliation_cases()
    observed = {case[-1] for case in cases}
    assert observed == set(RECONCILIATION_STATES)
    for case in cases:
        again = classify_reconciliation(
            manifest_present=case[0],
            result_present=case[1],
            root_present=case[2],
            manifest_valid=case[3],
            result_valid=case[4],
            result_status=case[5],
            closed_pair_consistent=case[6],
        )
        assert again == case[-1]


def test_streamed_chunk_length_rejects_bool_and_negative():
    from p3_v3.pilot_source import EXTRACTOR_POLICY_V1, StreamedLimitCounter

    counter = StreamedLimitCounter(EXTRACTOR_POLICY_V1)
    counter.begin_member()
    with pytest.raises(EvidenceError, match="E_PILOT_EXTRACT_UNSAFE"):
        counter.consume_chunk(True)
    with pytest.raises(EvidenceError, match="E_PILOT_EXTRACT_UNSAFE"):
        counter.consume_chunk(-1)


def test_member_count_checked_before_content():
    from p3_v3.pilot_source import EXTRACTOR_POLICY_V1, StreamedLimitCounter

    policy = dict(EXTRACTOR_POLICY_V1)
    policy["max_member_count"] = 1
    counter = StreamedLimitCounter(policy)
    counter.begin_member()
    counter.end_member()
    with pytest.raises(EvidenceError, match="E_PILOT_EXTRACT_UNSAFE"):
        counter.begin_member()


def test_runtime_production_bytes_drift_writes_no_output(tmp_path, monkeypatch):
    import p3_v3.pilot_source as pilot_source

    monkeypatch.setattr(
        pilot_source,
        "REVIEWED_PILOT_SOURCE_PATH",
        tmp_path / "drifted-pilot-source.py",
    )
    (tmp_path / "drifted-pilot-source.py").write_text("drifted\n", encoding="utf-8")
    monkeypatch.setattr(
        pilot_source,
        "SOURCE_MANIFEST_PATH",
        tmp_path / "source-manifest.json",
    )
    monkeypatch.setattr(
        pilot_source,
        "SOURCE_PREPARATION_RESULT_PATH",
        tmp_path / "source-preparation-result.json",
    )
    with pytest.raises(
        EvidenceError, match="E_PILOT_SOURCE_PREPARATION_CAPABILITY_VERDICT"
    ):
        pilot_source.run_validate_source(
            tmp_path / "missing.zip",
            tmp_path / "materialize",
        )
    assert not (tmp_path / "source-manifest.json").exists()
    assert not (tmp_path / "source-preparation-result.json").exists()


def test_phase1_tree_hash_function_is_called_by_production_seam(tmp_path, monkeypatch):
    import p3_v3.pilot_source as pilot_source
    from p3_v3.bridge_and_frames import SourceSnapshot

    payload = tmp_path / "payload"
    payload.mkdir()
    (payload / "readme.txt").write_bytes(b"synthetic\n")
    snapshot = pilot_source.capture_materialized_tree(payload)
    calls: list[object] = []

    def spy(value):
        calls.append(value)
        return pilot_source.FROZEN_NORMALIZED_SOURCE_TREE_SHA256

    monkeypatch.setattr(pilot_source, "canonical_source_tree_sha256", spy)
    observed = pilot_source.validate_materialized_tree_with_phase1(snapshot)
    assert calls == [snapshot]
    assert type(calls[0]) is SourceSnapshot
    assert observed == pilot_source.FROZEN_NORMALIZED_SOURCE_TREE_SHA256


def test_materialized_tree_uses_phase1_canonical_hash(tmp_path, monkeypatch):
    import p3_v3.pilot_source as pilot_source
    from p3_v3.bridge_and_frames import canonical_source_tree_sha256 as phase1

    payload = tmp_path / "payload"
    payload.mkdir()
    (payload / "readme.txt").write_bytes(b"synthetic\n")
    snapshot = pilot_source.capture_materialized_tree(payload)
    seen: list[str] = []

    def spy(value):
        digest = phase1(value)
        seen.append(digest)
        return digest

    monkeypatch.setattr(pilot_source, "canonical_source_tree_sha256", spy)
    with pytest.raises(EvidenceError, match="E_PILOT_SOURCE_TREE_MISMATCH"):
        pilot_source.validate_materialized_tree_with_phase1(snapshot)
    assert seen == [phase1(snapshot)]
    assert seen[0] != pilot_source.FROZEN_NORMALIZED_SOURCE_TREE_SHA256


def test_validate_source_cli_has_no_authority_overrides():
    import scripts.p3_v3.pilot as pilot_cli

    parser = pilot_cli.build_parser()
    forbidden = [
        "--authorization",
        "--output",
        "--expected-archive-hash",
        "--expected-tree-hash",
        "--expected-build-descriptor-hash",
        "--implementation-verdict",
        "--machine-plan",
        "--extractor-policy",
        "--launch-authority",
        "--plan-verdict",
        "--capability-verdict",
    ]
    for flag in forbidden:
        with pytest.raises(SystemExit):
            parser.parse_args(
                [
                    "validate-source",
                    "--archive",
                    "synthetic.zip",
                    "--materialize-root",
                    "synthetic-root",
                    flag,
                    "forged",
                ]
            )
```

Also add, in `tests/p3_v3/test_pilot.py`, a CLI acceptance check that `validate-source` exists and accepts only `--archive` and `--materialize-root`. Keep every existing foundation assertion. Keep `p3_v3.pilot` free of `write_source_manifest` and `validate_pilot_source_manifest`; those names, if present, live only on `p3_v3.pilot_source`.

Synthetic ZIP and TAR fixtures are built at runtime with `zipfile` and `tarfile` in `tmp_path`. Do not read, mount, or unpack a real Boost.Math archive.

- [ ] **Step 3: Run RED**

Run:

```text
env \
  GIT_CONFIG_GLOBAL=/dev/null \
  GIT_CONFIG_NOSYSTEM=1 \
  GIT_CONFIG_COUNT=0 \
  PYTHONPATH=src \
  python3 -m pytest tests/p3_v3/test_pilot_source.py -q
```

Expected: exit 1 because `p3_v3.pilot_source` does not yet exist.

- [ ] **Step 4: Write the minimal implementation**

`src/p3_v3/pilot_source.py` must define the constants, authority snapshot helpers, gate-chain validators, `ArchiveSnapshot`, `read_production_archive_bytes`, `EXTRACTOR_POLICY_V1`, streamed limit counter, authorization verification, extractor, tree capture, `validate_materialized_tree_with_phase1`, `PILOT_SOURCE_MANIFEST_EXACT`, `PILOT_SOURCE_PREPARATION_RESULT_EXACT`, reconciliation, and `run_validate_source(archive, materialize_root)`.

`scripts/p3_v3/pilot.py` gains only the `validate-source` verb specified above. It calls `run_validate_source` with the two parsed paths and no other caller-supplied authority.

Production constants remain the reserved paths. Tests monkeypatch those constants. The capability task still does not create a file under `data/p3_v3/pilot/boost_math/`.

- [ ] **Step 5: Run minimum GREEN**

Run:

```text
env \
  GIT_CONFIG_GLOBAL=/dev/null \
  GIT_CONFIG_NOSYSTEM=1 \
  GIT_CONFIG_COUNT=0 \
  PYTHONPATH=src \
  python3 -m pytest \
  tests/p3_v3/test_pilot_source.py \
  tests/p3_v3/test_pilot.py \
  -q
```

Expected: exit 0.

- [ ] **Step 6: Run the complete confirmatory suite**

Run:

```text
env \
  GIT_CONFIG_GLOBAL=/dev/null \
  GIT_CONFIG_NOSYSTEM=1 \
  GIT_CONFIG_COUNT=0 \
  PYTHONPATH=src \
  python3 -m pytest tests/p3_v3 -q
```

Expected: exit 0. Existing confirmatory tests must keep passing. `test_pilot_cli_forbids_source_and_execution_verbs` must still see `SystemExit` for `parse_args(["validate-source"])` because the two arguments remain required.

- [ ] **Step 7: Stop for independent implementation review**

Stage only the approved Create and Modify paths. Do not create authorization A. Do not create a production source manifest. Do not create a production preparation result. Do not create launch authority. Do not enter production preparation. Requested state after this task is an independent capability implementation review candidate. Task 1 PASS does not authorize real preparation.

---

## Commands This Planning Node Must Not Run

The pytest commands above are future implementation commands. This planning node must not run them. This planning node must not run a build, preflight, profiling, mutant, MR, or production command.

---

## Stop Conditions

Stop immediately if implementation would require:

- modifying a file outside the approved map;
- creating authorization A;
- creating a production source manifest, preparation result, or launch authority;
- creating a reserved verdict file;
- reading a real Boost.Math archive;
- designing contract, site, MR, mutant, certification, execution, or evidence-closure procedures;
- changing an authority, protocol, ledger, or Frame file;
- treating a capability PASS as production authorization;
- treating a source manifest as build PASS or scientific PASS.

---

## Claim Ceiling

`claims=blocked`. Formal denominator membership is false. RQ4 is not supported. The claim ledger must remain byte-identical to `bf4979662697b2d0565bb70eec88b22673e84bee93b61234555342efb4082a68`.
