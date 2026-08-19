"""Machine-check P2-B packet 2026-08-19-002 criteria 1-5.

Reads only this packet's artifacts and frozen Protocol V4. Does not
import toolchain qualification, pilot build, or create_intent, and
does not invoke a compiler.
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

from p3_v3.artifacts import canonical_sha256, read_canonical_json

REPO = Path(__file__).resolve().parents[2]
PILOT_DIR = REPO / "data" / "p3_v3" / "phase2_pilot_only"
SUBJECT_PATH = PILOT_DIR / "synthetic-subject.json"
SPEC_PASS_PATH = PILOT_DIR / "preflight-spec-pass.json"
SPEC_FAIL_PATH = PILOT_DIR / "preflight-spec-fail.json"
RESULT_PASS_PATH = PILOT_DIR / "preflight-result-pass.json"
RESULT_FAIL_PATH = PILOT_DIR / "preflight-result-fail.json"
TERMINALS_PATH = PILOT_DIR / "terminals.json"

EXPECTED_COMMIT = "4444061dde0159a5edd62753fe3cef2d881a308c"
ENV_LOCK_PATH = "data/p3_v3/protocol/environment_lock.json"
ENV_LOCK_SHA256 = (
    "7706b4ce272d09df13c5212b04ec0f2519932f4225d5eac0d052d3225c7ff35f"
)
SUBJECT_REL = "data/p3_v3/phase2_pilot_only/synthetic-subject.json"
PROTOCOL_PATH = "data/p3_v3/protocol/protocol.json"
PROTOCOL_SHA256 = (
    "240d8270d41802c9d5b86f30564eadd1a86fd9ed09de2c7e947d17c1a4d78519"
)
SUBJECT_ID = "p2b-pilot-only-synthetic-001"
PASS_SMOKE = [
    [
        "python3",
        "scripts/p3_v3/evidence.py",
        "validate-protocol",
        "--protocol",
        PROTOCOL_PATH,
    ]
]
FAIL_SMOKE = [["python3", "-c", "raise SystemExit(2)"]]
SUBJECT_KEYS = {
    "schema_version",
    "subject_id",
    "denominator",
    "formal_denominator_membership",
    "claims",
    "artifact_sha256",
}
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
    "subject_id",
    "denominator",
    "formal_denominator_membership",
    "claims",
    "pass_result_sha256",
    "fail_result_sha256",
    "artifact_sha256",
}
FORBIDDEN_TOKENS = (
    "c++",
    "cmake",
    "1f67" + "b3f3",
    "boost" + "_math",
    "qualify_cxx" + "_link",
    "pilot.py",
)


def _file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _body_without_artifact(value: dict) -> dict:
    return {key: item for key, item in value.items() if key != "artifact_sha256"}


def _shared_spec_fields(spec: dict) -> None:
    assert set(spec) == SPEC_KEYS
    assert spec["schema_version"] == "p3-preflight-v1"
    assert spec["phase_role"] == "CONSTRUCTION_A"
    assert spec["repository_identity"] == "github.com/meng004/P3-Semantic-Mutation"
    assert spec["expected_commit"] == EXPECTED_COMMIT
    assert spec["dependency_lock_path"] == ENV_LOCK_PATH
    assert spec["dependency_lock_sha256"] == ENV_LOCK_SHA256
    assert spec["timeout_seconds"] == 60
    assert spec["minimum_cpu_count"] == 1
    assert spec["minimum_memory_bytes"] == 1
    assert spec["minimum_disk_free_bytes"] == 1
    assert spec["worker_limit"] == 1


def test_packet_test_does_not_import_forbidden_modules():
    loaded = set(sys.modules)
    assert "p3_v3.toolchain_qualification" not in loaded
    assert "p3_v3.pilot_build" not in loaded
    assert "p3_v3.run_records" not in loaded
    assert "create_intent" not in globals()


def test_synthetic_subject_is_pilot_only_and_blocked():
    subject = read_canonical_json(SUBJECT_PATH)
    assert set(subject) == SUBJECT_KEYS
    assert subject["schema_version"] == "p3-p2b-synthetic-subject-v1"
    assert subject["subject_id"] == SUBJECT_ID
    assert subject["denominator"] == "PILOT_ONLY"
    assert subject["formal_denominator_membership"] is False
    assert subject["claims"] == "blocked"
    assert subject["artifact_sha256"] == canonical_sha256(
        _body_without_artifact(subject)
    )


def test_both_specs_bind_only_synthetic_subject_and_protocol_v4():
    subject_sha = _file_sha256(SUBJECT_PATH)
    expected_inputs = [
        {"path": SUBJECT_REL, "sha256": subject_sha},
        {"path": PROTOCOL_PATH, "sha256": PROTOCOL_SHA256},
    ]
    assert _file_sha256(REPO / PROTOCOL_PATH) == PROTOCOL_SHA256
    assert _file_sha256(REPO / ENV_LOCK_PATH) == ENV_LOCK_SHA256
    for path in (SPEC_PASS_PATH, SPEC_FAIL_PATH):
        spec = read_canonical_json(path)
        _shared_spec_fields(spec)
        assert spec["phase_inputs"] == expected_inputs
        paths = [item["path"] for item in spec["phase_inputs"]]
        assert paths == sorted(set(paths))


def test_smoke_commands_are_pass_validate_protocol_and_fail_exit_2():
    pass_spec = read_canonical_json(SPEC_PASS_PATH)
    fail_spec = read_canonical_json(SPEC_FAIL_PATH)
    assert pass_spec["smoke_commands"] == PASS_SMOKE
    assert fail_spec["smoke_commands"] == FAIL_SMOKE
    flattened = " ".join(
        arg
        for spec in (pass_spec, fail_spec)
        for argv in spec["smoke_commands"]
        for arg in argv
    )
    for token in FORBIDDEN_TOKENS:
        assert token not in flattened


def test_pass_and_fail_receipts_are_self_hashed():
    pass_result = read_canonical_json(RESULT_PASS_PATH)
    fail_result = read_canonical_json(RESULT_FAIL_PATH)
    for result in (pass_result, fail_result):
        assert result["schema_version"] == "p3-preflight-result-v1"
        assert result["phase_role"] == "CONSTRUCTION_A"
        assert result["commit"] == EXPECTED_COMMIT
        assert result["artifact_sha256"] == canonical_sha256(
            _body_without_artifact(result)
        )
    assert pass_result["status"] == "PASS"
    assert pass_result["failure_code"] == ""
    assert fail_result["status"] == "FAIL"
    assert fail_result["failure_code"] == "E_PREFLIGHT_SMOKE"


def test_terminals_bind_both_receipt_artifact_hashes():
    pass_result = read_canonical_json(RESULT_PASS_PATH)
    fail_result = read_canonical_json(RESULT_FAIL_PATH)
    terminals = read_canonical_json(TERMINALS_PATH)
    assert set(terminals) == TERMINAL_KEYS
    assert terminals["schema_version"] == "p3-p2b-terminals-v1"
    assert terminals["packet_id"] == "2026-08-19-002"
    assert terminals["scientific_target"] == "P2-B"
    assert terminals["subject_id"] == SUBJECT_ID
    assert terminals["denominator"] == "PILOT_ONLY"
    assert terminals["formal_denominator_membership"] is False
    assert terminals["claims"] == "blocked"
    assert terminals["pass_result_sha256"] == pass_result["artifact_sha256"]
    assert terminals["fail_result_sha256"] == fail_result["artifact_sha256"]
    assert terminals["artifact_sha256"] == canonical_sha256(
        _body_without_artifact(terminals)
    )
