"""Machine-check P2-C packet 2026-08-19-003 criteria 1-5.

Reads this packet's artifacts and frozen Phase 1 inputs. Does not invoke
a compiler and does not import qualification or pilot-build modules.
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

from p3_v3.artifacts import canonical_sha256, read_canonical_json

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "p3_v3" / "run_p2c_one_row.py"
JOBS = REPO / "data" / "p3_v3" / "phase2_profiling" / "jobs"
ATTEMPT = JOBS / "p2c-20260819-003" / "1"
INTENT_PATH = ATTEMPT / "intent.json"
RESULT_PATH = ATTEMPT / "result.json"
TERMINAL_PATH = REPO / "data" / "p3_v3" / "phase2_profiling" / "row-terminal.json"
WORKLOAD_REL = (
    "data/p3_v3/phase1_frames/out/"
    "profiling-workload-1f67b3f303a09aa91413a2b5451d156cdcd76d425833bdd12669a7d1e140ca72.json"
)
PROTOCOL_SHA256 = (
    "240d8270d41802c9d5b86f30564eadd1a86fd9ed09de2c7e947d17c1a4d78519"
)
RECEIPTS_SHA256 = (
    "8eeccfe4d1aebb09e6ee9ad2fadb82ac5b8697c40f602592faa6b3878692a440"
)
WORKLOAD_SHA256 = (
    "db46368cc3a8e78ffeceb60c38d46cd903ac49ddc779757ee94f1350bd15382d"
)
IDS_SHA256 = (
    "e398d0a7764d44514d467c9170ba663457b7d38169354c4a310ffa3ffc37eca6"
)
BEHAVIOR_ID = (
    "72e1a3e8e8dc8bf0e6c0bd3ad9634299dcc910686c46ce4794021f5ca2eae6db"
)
SNAPSHOT_ID = (
    "1f67b3f303a09aa91413a2b5451d156cdcd76d425833bdd12669a7d1e140ca72"
)
EMPTY_TRACE_SHA256 = (
    "37517e5f3dc66819f61f5a7bb8ace1921282415f10551d2defa5c3eb0985b570"
)
PLACEHOLDER_ENV = (
    "396e3df895988aafcaa276a51c6e2b6a46aef1f31017b84b2d22de4b81eb9007"
)
EVAL_INPUT_ID = (
    "60c34610710b065bb3e0d649ce5a5b5badcfdf7147829445f925f7bdaab899a8"
)
JOB_ID = "p2c-20260819-003"
FIXED_ARGV = [
    "python3",
    "scripts/p3_v3/run_p2c_one_row.py",
    "--root",
    ".",
    "--workload",
    WORKLOAD_REL,
    "--behavior-id",
    BEHAVIOR_ID,
    "--jobs-root",
    "data/p3_v3/phase2_profiling/jobs",
    "--job-id",
    JOB_ID,
    "--terminal-output",
    "data/p3_v3/phase2_profiling/row-terminal.json",
]
INTENT_KEYS = {
    "job_id",
    "protocol_sha256",
    "phase",
    "argv",
    "cwd_identity",
    "environment_sha256",
    "input_sha256",
    "seed",
    "timeout_seconds",
    "attempt",
    "object_type",
    "object_id",
    "mr_id",
    "evaluation_input_class",
    "evaluation_input_id",
    "repetition_id",
    "environment_id",
    "job_role",
}
RESULT_KEYS = {
    "job_id",
    "attempt",
    "status",
    "exit_code",
    "stdout_sha256",
    "stderr_sha256",
    "duration_seconds",
    "failure_code",
    "scientific_outcome",
    "call_trace_sha256",
    "call_trace_identity",
}
TERMINAL_KEYS = {
    "schema_version",
    "packet_id",
    "scientific_target",
    "neutral_snapshot_id",
    "discovery_status",
    "adapter_id",
    "behavior_id",
    "denominator",
    "formal_denominator_membership",
    "claims",
    "result_status",
    "result_failure_code",
    "workload_file_sha256",
    "selected_behavior_ids_sha256",
    "artifact_sha256",
}
SCRIPT_FORBIDDEN = (
    "c++",
    "cmake",
    "meson",
    "autotools",
    "qualify_cxx" + "_link",
    "boost" + "_math",
    "p3-phase1-" + "unexecuted",
    "PHASE1_PROFILING_" + "NOT_EXECUTED",
)


def _file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _body_without_artifact(value: dict) -> dict:
    return {key: item for key, item in value.items() if key != "artifact_sha256"}


def test_packet_test_does_not_import_qualification_or_pilot_build():
    loaded = set(sys.modules)
    assert "p3_v3.toolchain_qualification" not in loaded
    assert "p3_v3.pilot_build" not in loaded


def test_script_reuses_run_records_and_avoids_forbidden_tokens():
    source = SCRIPT.read_text(encoding="utf-8")
    assert SCRIPT.is_file()
    assert "from p3_v3.run_records import create_intent, write_result" in source
    lowered = source.lower()
    for token in SCRIPT_FORBIDDEN:
        assert token not in source
        assert token.lower() not in lowered


def test_intent_matches_frozen_one_row_contract():
    intent = read_canonical_json(INTENT_PATH)
    assert set(intent) == INTENT_KEYS
    assert intent["job_id"] == JOB_ID
    assert intent["protocol_sha256"] == PROTOCOL_SHA256
    assert intent["phase"] == "PHASE_1"
    assert intent["argv"] == FIXED_ARGV
    assert "p3-phase1-" + "unexecuted" not in intent["argv"]
    assert intent["cwd_identity"] == "github.com/meng004/P3-Semantic-Mutation"
    assert intent["input_sha256"] == sorted(
        {PROTOCOL_SHA256, RECEIPTS_SHA256, WORKLOAD_SHA256}
    )
    assert intent["seed"] is None
    assert intent["timeout_seconds"] == 60
    assert intent["attempt"] == 1
    assert intent["object_type"] == "PROFILING_BEHAVIOR"
    assert intent["object_id"] == BEHAVIOR_ID
    assert intent["mr_id"] == "not-applicable"
    assert intent["evaluation_input_class"] == "E_COMMON"
    assert intent["evaluation_input_id"] == EVAL_INPUT_ID
    assert intent["repetition_id"] == 1
    assert intent["environment_id"] == "p2c-one-row-2026-08-19-003"
    assert intent["job_role"] == "PROFILING"
    assert len(intent["environment_sha256"]) == 64
    assert intent["environment_sha256"] != PLACEHOLDER_ENV


def test_result_is_honest_missing_with_reason():
    intent = read_canonical_json(INTENT_PATH)
    result = read_canonical_json(RESULT_PATH)
    assert set(result) == RESULT_KEYS
    assert result["job_id"] == JOB_ID
    assert result["attempt"] == 1
    assert result["status"] == "MISSING_WITH_REASON"
    assert result["failure_code"] in {
        "E_SOURCE_TREE_ABSENT",
        "E_PROFILE_NO_PROCESS_ARGV",
    }
    assert result["failure_code"] != "PHASE1_PROFILING_" + "NOT_EXECUTED"
    assert result["scientific_outcome"] is None
    assert result["call_trace_sha256"] == EMPTY_TRACE_SHA256
    assert result["call_trace_sha256"] == canonical_sha256([])
    assert result["call_trace_identity"] == canonical_sha256(
        {
            "job_id": intent["job_id"],
            "attempt": 1,
            "behavior_id": intent["object_id"],
            "call_trace_sha256": result["call_trace_sha256"],
            "domain": "P3-PROFILING-TRACE-v1",
        }
    )
    assert len(result["stdout_sha256"]) == 64
    assert len(result["stderr_sha256"]) == 64
    assert result["duration_seconds"] >= 0
    assert result["exit_code"] is None or type(result["exit_code"]) is int


def test_row_terminal_is_one_row_and_blocked():
    result = read_canonical_json(RESULT_PATH)
    terminal = read_canonical_json(TERMINAL_PATH)
    workload = read_canonical_json(REPO / WORKLOAD_REL)
    assert set(terminal) == TERMINAL_KEYS
    assert terminal["schema_version"] == "p3-p2c-one-row-terminal-v1"
    assert terminal["packet_id"] == "2026-08-19-003"
    assert terminal["scientific_target"] == "P2-C"
    assert terminal["neutral_snapshot_id"] == SNAPSHOT_ID
    assert terminal["discovery_status"] == "EXECUTABLE"
    assert terminal["adapter_id"] == "CMAKE_CTEST_V1"
    assert terminal["behavior_id"] == BEHAVIOR_ID
    assert terminal["denominator"] == "PROFILING_ONE_ROW"
    assert terminal["formal_denominator_membership"] is False
    assert terminal["claims"] == "blocked"
    assert terminal["result_status"] == result["status"]
    assert terminal["result_failure_code"] == result["failure_code"]
    assert terminal["workload_file_sha256"] == WORKLOAD_SHA256
    assert _file_sha256(REPO / WORKLOAD_REL) == WORKLOAD_SHA256
    assert terminal["selected_behavior_ids_sha256"] == IDS_SHA256
    assert canonical_sha256(workload["selected_behavior_ids"]) == IDS_SHA256
    assert workload["selected_behavior_ids"][0] == BEHAVIOR_ID
    assert terminal["artifact_sha256"] == canonical_sha256(
        _body_without_artifact(terminal)
    )
