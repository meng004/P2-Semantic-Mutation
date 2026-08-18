"""One-shot C++ compile-link-run qualification evidence helpers."""

# Exact-type checks match p3_v3.artifacts.validate_exact_object.
# ruff: noqa: E721

from __future__ import annotations

import hashlib
import re
from collections.abc import Mapping
from pathlib import Path, PurePosixPath
from typing import Any

from p3_v3.artifacts import (
    EvidenceError,
    canonical_sha256,
    safe_relative_path,
    validate_exact_object,
    validate_sha256,
)


EXECUTION_CLASS = "PILOT_TOOLCHAIN_QUALIFICATION_ONLY"
CLAIMS = "blocked"
SPEC_PATH = Path(
    "docs/superpowers/specs/"
    "2026-08-18-p3-cursor-vm-cxx-link-qualification-design.md"
)
SPEC_SHA256 = (
    "ff438a10da0e762667fe358fb32082e2338f39f28c16620d5a15d8890e8dd8d5"
)
FROZEN_ROOT = Path("/tmp/p3-cxx-link-qualification")
SOURCE_NAME = "qualify.cpp"
EXECUTABLE_NAME = "qualify"
SOURCE_BYTES = b"int main(){return 0;}\n"
SOURCE_TEXT = SOURCE_BYTES.decode("utf-8")
SOURCE_SHA256 = hashlib.sha256(SOURCE_BYTES).hexdigest()
COMPILE_TIMEOUT_SECONDS = 60
RUN_TIMEOUT_SECONDS = 10
COMPILER_VERSION_TIMEOUT_SECONDS = 10
FORBIDDEN_ENV = (
    "CXX",
    "CC",
    "CPATH",
    "CPLUS_INCLUDE_PATH",
    "LIBRARY_PATH",
    "LD_LIBRARY_PATH",
    "LDFLAGS",
    "CXXFLAGS",
)
INTENT_SCHEMA = "p3-cxx-link-qualification-intent-v1"
PROCESS_SCHEMA = "p3-cxx-link-qualification-process-v1"
RESULT_SCHEMA = "p3-cxx-link-qualification-result-v1"
MANIFEST_SCHEMA = "p3-cxx-link-qualification-manifest-v1"
HOST_SCHEMA = "p3-cxx-link-qualification-host-v1"
REQUESTED_COMPILER = "c++"
JOB_COMPILE = "CXX_COMPILE_LINK"
JOB_RUN = "QUALIFIED_BINARY_RUN"
JOB_METADATA = "METADATA_CXX_VERSION"
_COMMIT_RE = re.compile(r"[0-9a-f]{40}")

_HOST_TYPES: Mapping[str, type | tuple[type, ...]] = {
    "schema_version": str,
    "os_name": str,
    "os_release": str,
    "kernel_release": str,
    "machine": str,
    "node_name": str,
    "python_version": str,
    "git_version": str,
    "repository_commit": str,
    "repository_clean": bool,
    "requested_compiler": str,
    "resolved_compiler_path": (str, type(None)),
    "resolved_compiler_realpath": (str, type(None)),
    "resolved_path_regular": (bool, type(None)),
    "resolved_path_symlink": (bool, type(None)),
    "artifact_sha256": str,
}
_PROCESS_TYPES: Mapping[str, type | tuple[type, ...]] = {
    "schema_version": str,
    "execution_class": str,
    "claims": str,
    "process_role": str,
    "job_id": str,
    "argv": (list, type(None)),
    "timeout_seconds": (int, type(None)),
    "process_started": bool,
    "terminal_status": str,
    "failure_reason": (str, type(None)),
    "exit_code": (int, type(None)),
    "started_at": (str, type(None)),
    "ended_at": (str, type(None)),
    "wall_seconds": (float, type(None)),
    "process_group_terminated": (bool, type(None)),
    "stdout_sha256": (str, type(None)),
    "stderr_sha256": (str, type(None)),
    "stdout_bytes": (int, type(None)),
    "stderr_bytes": (int, type(None)),
    "artifact_sha256": str,
}
_INTENT_TYPES: Mapping[str, type | tuple[type, ...]] = {
    "schema_version": str,
    "execution_class": str,
    "claims": str,
    "formal_denominator_membership": bool,
    "attempt_2_authorized": bool,
    "no_retry": bool,
    "repository_commit": str,
    "host_snapshot": dict,
    "host_snapshot_sha256": str,
    "spec_path": str,
    "spec_sha256": str,
    "qualification_root": str,
    "requested_compiler": str,
    "resolved_compiler_path": (str, type(None)),
    "resolved_compiler_realpath": (str, type(None)),
    "source_text": str,
    "source_sha256": str,
    "compile_link_argv": (list, type(None)),
    "binary_run_argv": (list, type(None)),
    "compile_timeout_seconds": int,
    "run_timeout_seconds": int,
    "compiler_version_timeout_seconds": int,
    "relevant_environment": dict,
    "artifact_sha256": str,
}
_RESULT_TYPES: Mapping[str, type | tuple[type, ...]] = {
    "schema_version": str,
    "execution_class": str,
    "claims": str,
    "formal_denominator_membership": bool,
    "attempt_2_authorized": bool,
    "no_retry": bool,
    "intent_sha256": str,
    "repository_commit": str,
    "host_snapshot": dict,
    "host_snapshot_sha256": str,
    "spec_sha256": str,
    "compiler_version": (dict, type(None)),
    "jobs": list,
    "source_sha256": str,
    "executable_sha256": (str, type(None)),
    "executable_bytes": (int, type(None)),
    "executable_regular": (bool, type(None)),
    "executable_symlink": (bool, type(None)),
    "terminal_status": str,
    "failure_reason": (str, type(None)),
    "artifact_sha256": str,
}
_MANIFEST_TYPES: Mapping[str, type | tuple[type, ...]] = {
    "schema_version": str,
    "execution_class": str,
    "claims": str,
    "formal_denominator_membership": bool,
    "attempt_2_authorized": bool,
    "no_retry": bool,
    "intent_sha256": str,
    "result_sha256": str,
    "files": list,
    "artifact_sha256": str,
}
_FILE_TYPES: Mapping[str, type | tuple[type, ...]] = {
    "path": str,
    "sha256": str,
    "bytes": int,
}


def _self_hash(payload: dict[str, Any]) -> dict[str, Any]:
    body = {key: payload[key] for key in payload if key != "artifact_sha256"}
    return {**body, "artifact_sha256": canonical_sha256(body)}


def _require_self_hash(payload: dict[str, Any], context: str) -> None:
    digest = canonical_sha256(
        {key: payload[key] for key in payload if key != "artifact_sha256"}
    )
    if payload.get("artifact_sha256") != digest:
        raise EvidenceError(
            "E_SELF_HASH",
            f"{context} artifact_sha256 is not canonical",
        )


def _require_commit(value: str, context: str) -> str:
    if _COMMIT_RE.fullmatch(value) is None:
        raise EvidenceError(
            "E_COMMIT",
            f"{context} must be 40 lowercase hexadecimal characters",
        )
    return value


def _require_invariants(value: Mapping[str, Any], context: str) -> None:
    if value.get("execution_class") != EXECUTION_CLASS:
        raise EvidenceError("E_CLASS", f"{context} execution_class is frozen")
    if value.get("claims") != CLAIMS:
        raise EvidenceError("E_CLAIMS", f"{context} claims must be blocked")
    if "formal_denominator_membership" in value:
        if value["formal_denominator_membership"] is not False:
            raise EvidenceError(
                "E_DENOMINATOR",
                f"{context} formal_denominator_membership must be false",
            )
    if "attempt_2_authorized" in value:
        if value["attempt_2_authorized"] is not False:
            raise EvidenceError(
                "E_ATTEMPT2",
                f"{context} attempt_2_authorized must be false",
            )
    if "no_retry" in value and value["no_retry"] is not True:
        raise EvidenceError("E_NO_RETRY", f"{context} no_retry must be true")


def _require_absolute(value: str | None, context: str) -> None:
    if value is None:
        return
    if not value.startswith("/") or value.endswith("/") or "\x00" in value:
        raise EvidenceError("E_PATH", f"{context} must be an absolute path")


def _require_string_list(value: list[Any] | None, context: str) -> None:
    if value is None:
        return
    if any(type(item) is not str for item in value):
        raise EvidenceError("E_ARGV", f"{context} items must be strings")


def _resolved_null_set(
    path: str | None,
    realpath: str | None,
    regular: bool | None,
    symlink: bool | None,
) -> bool:
    fields = (path, realpath, regular, symlink)
    return all(item is None for item in fields)


def _resolved_success_set(
    path: str | None,
    realpath: str | None,
    regular: bool | None,
    symlink: bool | None,
) -> bool:
    return (
        type(path) is str
        and type(realpath) is str
        and regular is True
        and type(symlink) is bool
    )


def validate_host_snapshot(value: object) -> dict[str, Any]:
    snapshot = validate_exact_object(value, _HOST_TYPES, "host_snapshot")
    if snapshot["schema_version"] != HOST_SCHEMA:
        raise EvidenceError("E_SCHEMA", "host_snapshot schema_version is frozen")
    _require_commit(snapshot["repository_commit"], "host_snapshot.repository_commit")
    if snapshot["repository_clean"] is not True:
        raise EvidenceError(
            "E_REPO_CLEAN",
            "host_snapshot.repository_clean must be true",
        )
    if snapshot["requested_compiler"] != REQUESTED_COMPILER:
        raise EvidenceError(
            "E_COMPILER",
            "host_snapshot.requested_compiler must equal c++",
        )
    path = snapshot["resolved_compiler_path"]
    realpath = snapshot["resolved_compiler_realpath"]
    regular = snapshot["resolved_path_regular"]
    symlink = snapshot["resolved_path_symlink"]
    if _resolved_null_set(path, realpath, regular, symlink):
        pass
    elif _resolved_success_set(path, realpath, regular, symlink):
        _require_absolute(path, "host_snapshot.resolved_compiler_path")
        _require_absolute(realpath, "host_snapshot.resolved_compiler_realpath")
    else:
        raise EvidenceError(
            "E_COMPILER_IDENTITY",
            "host_snapshot resolved identity fields are not coupled",
        )
    validate_sha256(snapshot["artifact_sha256"], "host_snapshot.artifact_sha256")
    _require_self_hash(snapshot, "host_snapshot")
    return snapshot


def _validate_not_started(process: Mapping[str, Any], context: str) -> None:
    if process["process_started"] is not False:
        raise EvidenceError("E_PROCESS", f"{context} NOT_STARTED started")
    for key in (
        "exit_code",
        "started_at",
        "ended_at",
        "wall_seconds",
        "process_group_terminated",
        "stdout_sha256",
        "stderr_sha256",
        "stdout_bytes",
        "stderr_bytes",
    ):
        if process[key] is not None:
            raise EvidenceError(
                "E_PROCESS",
                f"{context} NOT_STARTED invented {key}",
            )


def _validate_started_output(process: Mapping[str, Any], context: str) -> None:
    if process["process_started"] is not True:
        raise EvidenceError("E_PROCESS", f"{context} must have started")
    if process["started_at"] is None or process["ended_at"] is None:
        raise EvidenceError("E_PROCESS", f"{context} timestamps are required")
    if type(process["wall_seconds"]) is not float:
        raise EvidenceError("E_PROCESS", f"{context} wall_seconds is required")
    validate_sha256(process["stdout_sha256"], f"{context}.stdout_sha256")
    validate_sha256(process["stderr_sha256"], f"{context}.stderr_sha256")
    if type(process["stdout_bytes"]) is not int or process["stdout_bytes"] < 0:
        raise EvidenceError("E_PROCESS", f"{context} stdout_bytes is invalid")
    if type(process["stderr_bytes"]) is not int or process["stderr_bytes"] < 0:
        raise EvidenceError("E_PROCESS", f"{context} stderr_bytes is invalid")


def validate_process_evidence(value: object) -> dict[str, Any]:
    process = validate_exact_object(value, _PROCESS_TYPES, "process")
    if process["schema_version"] != PROCESS_SCHEMA:
        raise EvidenceError("E_SCHEMA", "process schema_version is frozen")
    _require_invariants(process, "process")
    role = process["process_role"]
    job_id = process["job_id"]
    if role not in {"METADATA", "WORKLOAD"}:
        raise EvidenceError("E_ROLE", "process_role must be METADATA or WORKLOAD")
    if role == "METADATA" and job_id != JOB_METADATA:
        raise EvidenceError("E_JOB", "METADATA job_id is frozen")
    if role == "WORKLOAD" and job_id not in {JOB_COMPILE, JOB_RUN}:
        raise EvidenceError("E_JOB", "WORKLOAD job_id is frozen")
    _require_string_list(process["argv"], "process.argv")
    status = process["terminal_status"]
    reason = process["failure_reason"]
    if status == "NOT_STARTED":
        _validate_not_started(process, "process")
    elif status == "PASS":
        _validate_started_output(process, "process")
        if process["exit_code"] != 0 or reason is not None:
            raise EvidenceError("E_PROCESS", "PASS requires exit 0 and no reason")
        if process["process_group_terminated"] is not False:
            raise EvidenceError("E_PROCESS", "PASS must not terminate the group")
        if role == "WORKLOAD" and (
            process["stdout_bytes"] != 0 or process["stderr_bytes"] != 0
        ):
            raise EvidenceError(
                "E_UNEXPECTED_OUTPUT",
                "WORKLOAD PASS requires zero stdout and stderr",
            )
    elif status == "FAIL":
        _validate_started_output(process, "process")
        if type(process["process_group_terminated"]) is not bool:
            raise EvidenceError("E_PROCESS", "FAIL cleanup state is required")
        if (
            type(process["exit_code"]) is int
            and process["exit_code"] != 0
            and reason == "NONZERO_EXIT"
        ):
            pass
        elif (
            role == "WORKLOAD"
            and process["exit_code"] == 0
            and reason == "UNEXPECTED_OUTPUT"
            and (
                process["stdout_bytes"] > 0 or process["stderr_bytes"] > 0
            )
        ):
            pass
        else:
            raise EvidenceError("E_PROCESS", "FAIL terminal matrix is invalid")
    elif status == "TIMEOUT":
        _validate_started_output(process, "process")
        if process["exit_code"] is not None or reason != "TIMEOUT":
            raise EvidenceError("E_PROCESS", "TIMEOUT matrix is invalid")
        if process["process_group_terminated"] is not True:
            raise EvidenceError("E_PROCESS", "TIMEOUT must terminate the group")
    else:
        raise EvidenceError("E_PROCESS", "terminal_status is not allowed")
    if role == "METADATA" and process["timeout_seconds"] not in {
        None,
        COMPILER_VERSION_TIMEOUT_SECONDS,
    }:
        raise EvidenceError(
            "E_TIMEOUT",
            "compiler-version timeout_seconds must equal 10",
        )
    if job_id == JOB_COMPILE and process["timeout_seconds"] not in {
        None,
        COMPILE_TIMEOUT_SECONDS,
    }:
        raise EvidenceError("E_TIMEOUT", "compile-link timeout must equal 60")
    if job_id == JOB_RUN and process["timeout_seconds"] not in {
        None,
        RUN_TIMEOUT_SECONDS,
    }:
        raise EvidenceError("E_TIMEOUT", "binary-run timeout must equal 10")
    validate_sha256(process["artifact_sha256"], "process.artifact_sha256")
    _require_self_hash(process, "process")
    return process


def _validate_compiler_binding(
    path: str | None,
    realpath: str | None,
    compile_argv: list[Any] | None,
    run_argv: list[Any] | None,
    root: str,
    context: str,
) -> None:
    unresolved = path is None and realpath is None
    if unresolved:
        if compile_argv is not None or run_argv is not None:
            raise EvidenceError(
                "E_ARGV",
                f"{context} unresolved compiler cannot invent workload argv",
            )
        return
    if type(path) is not str or type(realpath) is not str:
        raise EvidenceError("E_COMPILER", f"{context} resolved paths are coupled")
    _require_absolute(path, f"{context}.resolved_compiler_path")
    _require_absolute(realpath, f"{context}.resolved_compiler_realpath")
    expected_compile = [
        path,
        "-std=c++14",
        f"{root}/{SOURCE_NAME}",
        "-o",
        f"{root}/{EXECUTABLE_NAME}",
    ]
    expected_run = [f"{root}/{EXECUTABLE_NAME}"]
    if compile_argv != expected_compile or run_argv != expected_run:
        raise EvidenceError("E_ARGV", f"{context} workload argv is frozen")


def validate_intent(value: object) -> dict[str, Any]:
    intent = validate_exact_object(value, _INTENT_TYPES, "intent")
    if intent["schema_version"] != INTENT_SCHEMA:
        raise EvidenceError("E_SCHEMA", "intent schema_version is frozen")
    _require_invariants(intent, "intent")
    _require_commit(intent["repository_commit"], "intent.repository_commit")
    host = validate_host_snapshot(intent["host_snapshot"])
    validate_sha256(intent["host_snapshot_sha256"], "intent.host_snapshot_sha256")
    if host["artifact_sha256"] != intent["host_snapshot_sha256"]:
        raise EvidenceError("E_HOST_HASH", "intent host snapshot hash differs")
    if host["repository_commit"] != intent["repository_commit"]:
        raise EvidenceError("E_COMMIT", "intent host commit differs")
    if intent["spec_path"] != SPEC_PATH.as_posix():
        raise EvidenceError("E_SPEC", "intent spec_path is frozen")
    if intent["spec_sha256"] != SPEC_SHA256:
        raise EvidenceError("E_SPEC", "intent spec_sha256 is frozen")
    validate_sha256(intent["spec_sha256"], "intent.spec_sha256")
    if intent["requested_compiler"] != REQUESTED_COMPILER:
        raise EvidenceError("E_COMPILER", "intent requested_compiler must equal c++")
    if intent["source_text"] != SOURCE_TEXT:
        raise EvidenceError("E_SOURCE", "intent source_text is frozen")
    if intent["source_sha256"] != SOURCE_SHA256:
        raise EvidenceError("E_SOURCE", "intent source_sha256 is frozen")
    if intent["compile_timeout_seconds"] != COMPILE_TIMEOUT_SECONDS:
        raise EvidenceError("E_TIMEOUT", "intent compile timeout must equal 60")
    if intent["run_timeout_seconds"] != RUN_TIMEOUT_SECONDS:
        raise EvidenceError("E_TIMEOUT", "intent run timeout must equal 10")
    if (
        intent["compiler_version_timeout_seconds"]
        != COMPILER_VERSION_TIMEOUT_SECONDS
    ):
        raise EvidenceError(
            "E_TIMEOUT",
            "intent compiler_version_timeout_seconds must equal 10",
        )
    env = intent["relevant_environment"]
    if any(type(key) is not str or type(val) is not str for key, val in env.items()):
        raise EvidenceError("E_ENV", "relevant_environment must be string pairs")
    _require_string_list(intent["compile_link_argv"], "intent.compile_link_argv")
    _require_string_list(intent["binary_run_argv"], "intent.binary_run_argv")
    _validate_compiler_binding(
        intent["resolved_compiler_path"],
        intent["resolved_compiler_realpath"],
        intent["compile_link_argv"],
        intent["binary_run_argv"],
        intent["qualification_root"],
        "intent",
    )
    if intent["resolved_compiler_path"] != host["resolved_compiler_path"]:
        raise EvidenceError("E_COMPILER", "intent compiler path differs from host")
    if intent["resolved_compiler_realpath"] != host["resolved_compiler_realpath"]:
        raise EvidenceError(
            "E_COMPILER",
            "intent compiler realpath differs from host",
        )
    validate_sha256(intent["artifact_sha256"], "intent.artifact_sha256")
    _require_self_hash(intent, "intent")
    return intent


def _validate_executable_group(result: Mapping[str, Any]) -> None:
    fields = (
        result["executable_sha256"],
        result["executable_bytes"],
        result["executable_regular"],
        result["executable_symlink"],
    )
    if all(item is None for item in fields):
        return
    digest, size, regular, symlink = fields
    if digest is None or type(size) is not int or size < 0:
        raise EvidenceError("E_EXECUTABLE", "executable evidence is incomplete")
    validate_sha256(digest, "result.executable_sha256")
    if regular is not True or symlink is not False:
        raise EvidenceError(
            "E_EXECUTABLE",
            "present executable must be regular and non-symlink",
        )


def validate_result(value: object) -> dict[str, Any]:
    result = validate_exact_object(value, _RESULT_TYPES, "result")
    if result["schema_version"] != RESULT_SCHEMA:
        raise EvidenceError("E_SCHEMA", "result schema_version is frozen")
    _require_invariants(result, "result")
    _require_commit(result["repository_commit"], "result.repository_commit")
    host = validate_host_snapshot(result["host_snapshot"])
    validate_sha256(result["host_snapshot_sha256"], "result.host_snapshot_sha256")
    if host["artifact_sha256"] != result["host_snapshot_sha256"]:
        raise EvidenceError("E_HOST_HASH", "result host snapshot hash differs")
    if host["repository_commit"] != result["repository_commit"]:
        raise EvidenceError("E_COMMIT", "result host commit differs")
    if result["spec_sha256"] != SPEC_SHA256:
        raise EvidenceError("E_SPEC", "result spec_sha256 is frozen")
    validate_sha256(result["spec_sha256"], "result.spec_sha256")
    validate_sha256(result["intent_sha256"], "result.intent_sha256")
    if result["source_sha256"] != SOURCE_SHA256:
        raise EvidenceError("E_SOURCE", "result source_sha256 is frozen")
    version = result["compiler_version"]
    if version is not None:
        version = validate_process_evidence(version)
        if version["process_role"] != "METADATA":
            raise EvidenceError("E_ROLE", "compiler_version must be METADATA")
        if version["timeout_seconds"] != COMPILER_VERSION_TIMEOUT_SECONDS:
            raise EvidenceError(
                "E_TIMEOUT",
                "compiler-version timeout_seconds must equal 10",
            )
    jobs = result["jobs"]
    if len(jobs) != 2:
        raise EvidenceError("E_JOBS", "result.jobs must contain exactly two jobs")
    compiled = validate_process_evidence(jobs[0])
    ran = validate_process_evidence(jobs[1])
    if compiled["job_id"] != JOB_COMPILE or ran["job_id"] != JOB_RUN:
        raise EvidenceError("E_JOBS", "result.jobs order is frozen")
    if compiled["process_role"] != "WORKLOAD" or ran["process_role"] != "WORKLOAD":
        raise EvidenceError("E_JOBS", "workload roles are frozen")
    result["jobs"] = [compiled, ran]
    result["compiler_version"] = version
    _validate_executable_group(result)
    status = result["terminal_status"]
    if status == "PASS":
        if result["failure_reason"] is not None:
            raise EvidenceError("E_RESULT", "PASS failure_reason must be null")
        if version is None or version["terminal_status"] != "PASS":
            raise EvidenceError("E_RESULT", "PASS requires metadata PASS")
        if compiled["terminal_status"] != "PASS" or ran["terminal_status"] != "PASS":
            raise EvidenceError("E_RESULT", "PASS requires both workload jobs PASS")
        if result["executable_sha256"] is None:
            raise EvidenceError("E_RESULT", "PASS requires executable evidence")
    elif status != "FAIL":
        raise EvidenceError("E_RESULT", "terminal_status must be PASS or FAIL")
    elif result["failure_reason"] is None:
        raise EvidenceError("E_RESULT", "FAIL requires failure_reason")
    validate_sha256(result["artifact_sha256"], "result.artifact_sha256")
    _require_self_hash(result, "result")
    return result


def validate_manifest(value: object) -> dict[str, Any]:
    manifest = validate_exact_object(value, _MANIFEST_TYPES, "manifest")
    if manifest["schema_version"] != MANIFEST_SCHEMA:
        raise EvidenceError("E_SCHEMA", "manifest schema_version is frozen")
    _require_invariants(manifest, "manifest")
    validate_sha256(manifest["intent_sha256"], "manifest.intent_sha256")
    validate_sha256(manifest["result_sha256"], "manifest.result_sha256")
    files = manifest["files"]
    seen: set[str] = set()
    paths: list[str] = []
    for index, entry in enumerate(files):
        item = validate_exact_object(entry, _FILE_TYPES, f"manifest.files[{index}]")
        path = item["path"]
        if path == "qualification-manifest.json":
            raise EvidenceError(
                "E_MANIFEST",
                "manifest must not list itself",
            )
        safe_relative_path(path)
        if ".." in PurePosixPath(path).parts:
            raise EvidenceError("E_PATH", "manifest path must not contain ..")
        validate_sha256(item["sha256"], f"manifest.files[{index}].sha256")
        if item["bytes"] < 0:
            raise EvidenceError("E_MANIFEST", "file byte count is invalid")
        if path in seen:
            raise EvidenceError("E_MANIFEST", "manifest paths must be unique")
        seen.add(path)
        paths.append(path)
        files[index] = item
    if paths != sorted(paths):
        raise EvidenceError("E_MANIFEST", "manifest paths must be sorted")
    validate_sha256(manifest["artifact_sha256"], "manifest.artifact_sha256")
    _require_self_hash(manifest, "manifest")
    return manifest


def validate_attempt_pair(
    intent: object,
    intent_file_sha256: str,
    result: object,
) -> tuple[dict[str, Any], dict[str, Any]]:
    validated_intent = validate_intent(intent)
    validated_result = validate_result(result)
    validate_sha256(intent_file_sha256, "attempt.intent_file_sha256")
    if validated_result["intent_sha256"] != intent_file_sha256:
        raise EvidenceError("E_PAIR", "intent file SHA differs")
    if validated_result["host_snapshot"] != validated_intent["host_snapshot"]:
        raise EvidenceError("E_PAIR", "host snapshot differs")
    if (
        validated_result["host_snapshot_sha256"]
        != validated_intent["host_snapshot_sha256"]
    ):
        raise EvidenceError("E_PAIR", "host snapshot hash differs")
    for key in (
        "repository_commit",
        "spec_sha256",
        "source_sha256",
    ):
        if validated_result[key] != validated_intent[key]:
            raise EvidenceError("E_PAIR", f"{key} differs")
    if (
        validated_result["jobs"][0]["timeout_seconds"]
        not in {None, validated_intent["compile_timeout_seconds"]}
    ):
        raise EvidenceError("E_PAIR", "compile timeout differs")
    if (
        validated_result["jobs"][1]["timeout_seconds"]
        not in {None, validated_intent["run_timeout_seconds"]}
    ):
        raise EvidenceError("E_PAIR", "run timeout differs")
    version = validated_result["compiler_version"]
    if version is not None:
        if (
            version["timeout_seconds"]
            != validated_intent["compiler_version_timeout_seconds"]
        ):
            raise EvidenceError("E_PAIR", "metadata timeout differs")
        expected = None
        if validated_intent["resolved_compiler_path"] is not None:
            expected = [
                validated_intent["resolved_compiler_path"],
                "--version",
            ]
        if version["argv"] != expected:
            raise EvidenceError("E_PAIR", "metadata argv differs")
    if validated_result["jobs"][0]["argv"] != validated_intent["compile_link_argv"]:
        raise EvidenceError("E_PAIR", "compile-link argv differs")
    if validated_result["jobs"][1]["argv"] != validated_intent["binary_run_argv"]:
        raise EvidenceError("E_PAIR", "binary-run argv differs")
    return validated_intent, validated_result
