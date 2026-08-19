"""Machine-check P2-A packet 2026-08-19-001 criteria 1-5.

Reads only this packet's artifacts and frozen Phase 1 / Protocol V4
inputs. Does not import toolchain qualification or pilot build modules,
does not invoke a compiler, and does not re-run ``run-preflight``.
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

from p3_v3.artifacts import canonical_sha256, read_canonical_json

REPO = Path(__file__).resolve().parents[2]
PREFLIGHT_DIR = REPO / "data" / "p3_v3" / "phase2_preflight"
SPEC_PATH = PREFLIGHT_DIR / "preflight-spec.json"
RESULT_PATH = PREFLIGHT_DIR / "preflight-result.json"
TERMINAL_PATH = PREFLIGHT_DIR / "subject-terminal.json"

EXPECTED_COMMIT = "4444061dde0159a5edd62753fe3cef2d881a308c"
ENV_LOCK_PATH = "data/p3_v3/protocol/environment_lock.json"
ENV_LOCK_SHA256 = (
    "7706b4ce272d09df13c5212b04ec0f2519932f4225d5eac0d052d3225c7ff35f"
)
WORKLOAD_PATH = (
    "data/p3_v3/phase1_frames/out/"
    "profiling-workload-1f67b3f303a09aa91413a2b5451d156cdcd76d425833bdd12669a7d1e140ca72.json"
)
WORKLOAD_SHA256 = (
    "db46368cc3a8e78ffeceb60c38d46cd903ac49ddc779757ee94f1350bd15382d"
)
RECEIPTS_PATH = "data/p3_v3/phase1_frames/receipts.json"
RECEIPTS_SHA256 = (
    "8eeccfe4d1aebb09e6ee9ad2fadb82ac5b8697c40f602592faa6b3878692a440"
)
PROTOCOL_PATH = "data/p3_v3/protocol/protocol.json"
PROTOCOL_SHA256 = (
    "240d8270d41802c9d5b86f30564eadd1a86fd9ed09de2c7e947d17c1a4d78519"
)
NEUTRAL_SNAPSHOT_ID = (
    "1f67b3f303a09aa91413a2b5451d156cdcd76d425833bdd12669a7d1e140ca72"
)
SMOKE_COMMANDS = [
    [
        "python3",
        "scripts/p3_v3/evidence.py",
        "validate-protocol",
        "--protocol",
        PROTOCOL_PATH,
    ],
    [
        "python3",
        "-c",
        (
            "import json;p=json.load(open("
            f"'{WORKLOAD_PATH}'));"
            "assert p['schema_version']=='p3-profiling-workload-v1';"
            "assert p['scale_class']=='L';"
            "print('WORKLOAD_BOUND')"
        ),
    ],
]
SPEC_KEYS = {
    "schema_version",
    "repository_identity",
    "expected_commit",
    "dependency_lock_path",
    "dependency_lock_sha256",
    "phase_inputs",
    "smoke_commands",
    "timeout_seconds",
    "phase_role",
    "minimum_cpu_count",
    "minimum_memory_bytes",
    "minimum_disk_free_bytes",
    "worker_limit",
}
TERMINAL_KEYS = {
    "schema_version",
    "packet_id",
    "scientific_target",
    "neutral_snapshot_id",
    "discovery_status",
    "adapter_id",
    "denominator",
    "formal_denominator_membership",
    "claims",
    "preflight_status",
    "preflight_result_sha256",
    "artifact_sha256",
}
FORBIDDEN_SMOKE_TOKENS = (
    "c++",
    "cmake",
    "meson",
    "autotools",
    "qualify_cxx_link",
    "pilot.py",
    "Boost.Math",
    "boost_math",
)


def _file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _body_without_artifact(value: dict) -> dict:
    return {key: item for key, item in value.items() if key != "artifact_sha256"}


def test_packet_test_does_not_import_qualification_or_pilot_build():
    loaded = set(sys.modules)
    assert "p3_v3.toolchain_qualification" not in loaded
    assert "p3_v3.pilot_build" not in loaded


def test_preflight_spec_matches_construction_a_lock():
    spec = read_canonical_json(SPEC_PATH)
    assert set(spec) == SPEC_KEYS
    assert spec["schema_version"] == "p3-preflight-v1"
    assert spec["phase_role"] == "CONSTRUCTION_A"
    assert spec["repository_identity"] == "github.com/meng004/P3-Semantic-Mutation"
    assert spec["expected_commit"] == EXPECTED_COMMIT
    assert spec["dependency_lock_path"] == ENV_LOCK_PATH
    assert spec["dependency_lock_sha256"] == ENV_LOCK_SHA256
    assert _file_sha256(REPO / ENV_LOCK_PATH) == ENV_LOCK_SHA256
    assert spec["timeout_seconds"] == 60
    assert spec["minimum_cpu_count"] == 1
    assert spec["minimum_memory_bytes"] == 1
    assert spec["minimum_disk_free_bytes"] == 1
    assert spec["worker_limit"] == 1


def test_phase_inputs_are_exactly_three_frozen_bindings():
    spec = read_canonical_json(SPEC_PATH)
    expected = [
        {"path": WORKLOAD_PATH, "sha256": WORKLOAD_SHA256},
        {"path": RECEIPTS_PATH, "sha256": RECEIPTS_SHA256},
        {"path": PROTOCOL_PATH, "sha256": PROTOCOL_SHA256},
    ]
    assert spec["phase_inputs"] == expected
    paths = [item["path"] for item in spec["phase_inputs"]]
    assert paths == sorted(set(paths))
    for item in expected:
        assert _file_sha256(REPO / item["path"]) == item["sha256"]


def test_smoke_commands_are_protocol_and_workload_probe_only():
    spec = read_canonical_json(SPEC_PATH)
    assert spec["smoke_commands"] == SMOKE_COMMANDS
    flattened = " ".join(arg for argv in spec["smoke_commands"] for arg in argv)
    for token in FORBIDDEN_SMOKE_TOKENS:
        assert token not in flattened


def test_preflight_result_is_self_hashed_receipt():
    result = read_canonical_json(RESULT_PATH)
    assert result["schema_version"] == "p3-preflight-result-v1"
    assert result["status"] in {"PASS", "FAIL"}
    if result["status"] == "PASS":
        assert result["failure_code"] == ""
    else:
        assert isinstance(result["failure_code"], str)
        assert result["failure_code"] != ""
    assert result["phase_role"] == "CONSTRUCTION_A"
    assert result["commit"] == EXPECTED_COMMIT
    assert result["artifact_sha256"] == canonical_sha256(_body_without_artifact(result))
    assert result["phase_inputs"] == [
        {"path": WORKLOAD_PATH, "sha256": WORKLOAD_SHA256},
        {"path": RECEIPTS_PATH, "sha256": RECEIPTS_SHA256},
        {"path": PROTOCOL_PATH, "sha256": PROTOCOL_SHA256},
    ]


def test_subject_terminal_is_preflight_only_and_blocked():
    result = read_canonical_json(RESULT_PATH)
    terminal = read_canonical_json(TERMINAL_PATH)
    assert set(terminal) == TERMINAL_KEYS
    assert terminal["schema_version"] == "p3-p2a-subject-terminal-v1"
    assert terminal["packet_id"] == "2026-08-19-001"
    assert terminal["scientific_target"] == "P2-A"
    assert terminal["neutral_snapshot_id"] == NEUTRAL_SNAPSHOT_ID
    assert terminal["discovery_status"] == "EXECUTABLE"
    assert terminal["adapter_id"] == "CMAKE_CTEST_V1"
    assert terminal["denominator"] == "PREFLIGHT_ONLY"
    assert terminal["formal_denominator_membership"] is False
    assert terminal["claims"] == "blocked"
    assert terminal["preflight_status"] == result["status"]
    assert terminal["preflight_result_sha256"] == result["artifact_sha256"]
    assert terminal["artifact_sha256"] == canonical_sha256(
        _body_without_artifact(terminal)
    )
