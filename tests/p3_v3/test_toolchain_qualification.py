from __future__ import annotations

from pathlib import Path

import pytest

from p3_v3.artifacts import EvidenceError
import p3_v3.toolchain_qualification as q


COMMIT = "a" * 40
EMPTY = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
ROOT = "/tmp/qual-test"
CXX = "/usr/bin/c++"


def _host(**overrides: object) -> dict:
    payload = {
        "schema_version": q.HOST_SCHEMA,
        "os_name": "Linux",
        "os_release": "archived-os",
        "kernel_release": "archived-kernel",
        "machine": "x86_64",
        "node_name": "archived-node",
        "python_version": "3.12.3",
        "git_version": "git version 2.43.0",
        "repository_commit": COMMIT,
        "repository_clean": True,
        "requested_compiler": "c++",
        "resolved_compiler_path": CXX,
        "resolved_compiler_realpath": CXX,
        "resolved_path_regular": True,
        "resolved_path_symlink": False,
    }
    payload.update(overrides)
    return q._self_hash(payload)


def _unresolved_host() -> dict:
    return _host(
        resolved_compiler_path=None,
        resolved_compiler_realpath=None,
        resolved_path_regular=None,
        resolved_path_symlink=None,
    )


def _process(
    *,
    role: str,
    job_id: str,
    status: str,
    argv: list[str] | None,
    timeout: int | None,
    **overrides: object,
) -> dict:
    started = status != "NOT_STARTED"
    payload = {
        "schema_version": q.PROCESS_SCHEMA,
        "execution_class": q.EXECUTION_CLASS,
        "claims": q.CLAIMS,
        "process_role": role,
        "job_id": job_id,
        "argv": argv,
        "timeout_seconds": timeout,
        "process_started": started,
        "terminal_status": status,
        "failure_reason": None,
        "exit_code": 0 if status == "PASS" else None,
        "started_at": "t0" if started else None,
        "ended_at": "t1" if started else None,
        "wall_seconds": 0.01 if started else None,
        "process_group_terminated": False if started else None,
        "stdout_sha256": EMPTY if started else None,
        "stderr_sha256": EMPTY if started else None,
        "stdout_bytes": 0 if started else None,
        "stderr_bytes": 0 if started else None,
    }
    if status == "FAIL":
        payload["failure_reason"] = "NONZERO_EXIT"
        payload["exit_code"] = 7
    if status == "TIMEOUT":
        payload["failure_reason"] = "TIMEOUT"
        payload["exit_code"] = None
        payload["process_group_terminated"] = True
    payload.update(overrides)
    return q._self_hash(payload)


def _metadata(status: str = "PASS") -> dict:
    return _process(
        role="METADATA",
        job_id=q.JOB_METADATA,
        status=status,
        argv=[CXX, "--version"],
        timeout=10,
    )


def _compile(status: str = "PASS", **overrides: object) -> dict:
    return _process(
        role="WORKLOAD",
        job_id=q.JOB_COMPILE,
        status=status,
        argv=[CXX, "-std=c++14", f"{ROOT}/qualify.cpp", "-o", f"{ROOT}/qualify"],
        timeout=60,
        **overrides,
    )


def _run(status: str = "PASS", **overrides: object) -> dict:
    return _process(
        role="WORKLOAD",
        job_id=q.JOB_RUN,
        status=status,
        argv=[f"{ROOT}/qualify"],
        timeout=10,
        **overrides,
    )


def _intent(host: dict | None = None, **overrides: object) -> dict:
    snapshot = _host() if host is None else host
    resolved = snapshot["resolved_compiler_path"]
    payload = {
        "schema_version": q.INTENT_SCHEMA,
        "execution_class": q.EXECUTION_CLASS,
        "claims": q.CLAIMS,
        "formal_denominator_membership": False,
        "attempt_2_authorized": False,
        "no_retry": True,
        "repository_commit": COMMIT,
        "host_snapshot": snapshot,
        "host_snapshot_sha256": snapshot["artifact_sha256"],
        "spec_path": q.SPEC_PATH.as_posix(),
        "spec_sha256": q.SPEC_SHA256,
        "qualification_root": ROOT,
        "requested_compiler": "c++",
        "resolved_compiler_path": resolved,
        "resolved_compiler_realpath": snapshot["resolved_compiler_realpath"],
        "source_text": q.SOURCE_TEXT,
        "source_sha256": q.SOURCE_SHA256,
        "compile_link_argv": None
        if resolved is None
        else [CXX, "-std=c++14", f"{ROOT}/qualify.cpp", "-o", f"{ROOT}/qualify"],
        "binary_run_argv": None if resolved is None else [f"{ROOT}/qualify"],
        "compile_timeout_seconds": 60,
        "run_timeout_seconds": 10,
        "compiler_version_timeout_seconds": 10,
        "relevant_environment": {"PATH": "/usr/bin"},
    }
    payload.update(overrides)
    return q._self_hash(payload)


def _result(host: dict | None = None, **overrides: object) -> dict:
    snapshot = _host() if host is None else host
    payload = {
        "schema_version": q.RESULT_SCHEMA,
        "execution_class": q.EXECUTION_CLASS,
        "claims": q.CLAIMS,
        "formal_denominator_membership": False,
        "attempt_2_authorized": False,
        "no_retry": True,
        "intent_sha256": EMPTY,
        "repository_commit": COMMIT,
        "host_snapshot": snapshot,
        "host_snapshot_sha256": snapshot["artifact_sha256"],
        "spec_sha256": q.SPEC_SHA256,
        "compiler_version": _metadata(),
        "jobs": [_compile(), _run()],
        "source_sha256": q.SOURCE_SHA256,
        "executable_sha256": EMPTY,
        "executable_bytes": 16,
        "executable_regular": True,
        "executable_symlink": False,
        "terminal_status": "PASS",
        "failure_reason": None,
    }
    payload.update(overrides)
    return q._self_hash(payload)


def _manifest(**overrides: object) -> dict:
    payload = {
        "schema_version": q.MANIFEST_SCHEMA,
        "execution_class": q.EXECUTION_CLASS,
        "claims": q.CLAIMS,
        "formal_denominator_membership": False,
        "attempt_2_authorized": False,
        "no_retry": True,
        "intent_sha256": EMPTY,
        "result_sha256": EMPTY,
        "files": [
            {
                "path": "qualification-intent.json",
                "sha256": EMPTY,
                "bytes": 8,
            },
            {"path": "qualify.cpp", "sha256": EMPTY, "bytes": 22},
        ],
    }
    payload.update(overrides)
    return q._self_hash(payload)


def test_frozen_constants_are_exact():
    assert q.SOURCE_BYTES == b"int main(){return 0;}\n"
    assert q.FROZEN_ROOT == Path("/tmp/p3-cxx-link-qualification")
    assert q.COMPILE_TIMEOUT_SECONDS == 60
    assert q.RUN_TIMEOUT_SECONDS == 10
    assert q.COMPILER_VERSION_TIMEOUT_SECONDS == 10
    assert q.SPEC_SHA256 == (
        "ff438a10da0e762667fe358fb32082e2338f39f28c16620d5a15d8890e8dd8d5"
    )


def test_validators_reject_schema_and_invariant_errors():
    host = _host()
    extra = dict(host)
    extra["bonus"] = "no"
    extra = q._self_hash({k: extra[k] for k in extra if k != "artifact_sha256"})
    with pytest.raises(EvidenceError):
        q.validate_host_snapshot(extra)
    missing = {k: v for k, v in host.items() if k != "os_name"}
    with pytest.raises(EvidenceError):
        q.validate_host_snapshot(missing)
    bad_claim = _intent(claims="open")
    with pytest.raises(EvidenceError):
        q.validate_intent(bad_claim)
    bad_den = _intent(formal_denominator_membership=True)
    with pytest.raises(EvidenceError):
        q.validate_intent(bad_den)
    bad_attempt = _intent(attempt_2_authorized=True)
    with pytest.raises(EvidenceError):
        q.validate_intent(bad_attempt)
    hashed = dict(host)
    hashed["artifact_sha256"] = "b" * 64
    with pytest.raises(EvidenceError):
        q.validate_host_snapshot(hashed)


def test_manifest_excludes_itself_and_is_self_hashed():
    manifest = _manifest()
    assert q.validate_manifest(manifest) == manifest
    bad = dict(manifest)
    bad["files"] = [
        *manifest["files"],
        {
            "path": "qualification-manifest.json",
            "sha256": "a" * 64,
            "bytes": 1,
        },
    ]
    bad = q._self_hash({k: v for k, v in bad.items() if k != "artifact_sha256"})
    with pytest.raises(EvidenceError):
        q.validate_manifest(bad)


def test_unresolved_compiler_intent_uses_four_null_fields():
    host = _unresolved_host()
    intent = _intent(host)
    validated = q.validate_intent(intent)
    assert validated["resolved_compiler_path"] is None
    assert validated["resolved_compiler_realpath"] is None
    assert validated["compile_link_argv"] is None
    assert validated["binary_run_argv"] is None
    invented = _intent(
        host,
        compile_link_argv=[CXX, "-std=c++14", f"{ROOT}/qualify.cpp", "-o", "x"],
        binary_run_argv=[f"{ROOT}/qualify"],
    )
    with pytest.raises(EvidenceError):
        q.validate_intent(invented)


def test_intent_and_result_bind_same_host_snapshot():
    host = _host()
    intent = _intent(host)
    result = _result(
        host,
        host_snapshot_sha256=host["artifact_sha256"],
    )
    assert q.validate_intent(intent)["host_snapshot"] == host
    assert q.validate_result(result)["host_snapshot"] == host


def test_host_snapshot_tamper_without_rehash_is_rejected():
    host = _host()
    tampered = dict(host)
    tampered["os_name"] = "ForgedOS"
    with pytest.raises(EvidenceError):
        q.validate_host_snapshot(tampered)


def test_rehashed_host_mismatch_is_rejected_by_attempt_pair():
    host = _host()
    other = _host(os_name="OtherOS")
    intent = _intent(host)
    result = _result(other, host_snapshot_sha256=other["artifact_sha256"])
    with pytest.raises(EvidenceError):
        q.validate_attempt_pair(intent, EMPTY, result)


def test_host_snapshot_hash_mismatch_is_rejected():
    host = _host()
    intent = _intent(host, host_snapshot_sha256="c" * 64)
    with pytest.raises(EvidenceError):
        q.validate_intent(intent)


def test_unresolved_host_uses_four_null_identity_fields():
    host = _unresolved_host()
    validated = q.validate_host_snapshot(host)
    assert validated["resolved_compiler_path"] is None
    assert validated["resolved_compiler_realpath"] is None
    assert validated["resolved_path_regular"] is None
    assert validated["resolved_path_symlink"] is None


def test_workload_pass_rejects_nonempty_output():
    job = _compile(stdout_bytes=1)
    with pytest.raises(EvidenceError):
        q.validate_process_evidence(job)


def test_metadata_pass_allows_nonempty_output():
    meta = _metadata()
    meta = _process(
        role="METADATA",
        job_id=q.JOB_METADATA,
        status="PASS",
        argv=[CXX, "--version"],
        timeout=10,
        stdout_bytes=12,
        stdout_sha256="d" * 64,
    )
    assert q.validate_process_evidence(meta)["stdout_bytes"] == 12


def test_validate_attempt_pair_accepts_consistent_objects():
    host = _host()
    intent = _intent(host)
    result = _result(host)
    pair = q.validate_attempt_pair(intent, EMPTY, result)
    assert pair[0]["host_snapshot"] == pair[1]["host_snapshot"]
