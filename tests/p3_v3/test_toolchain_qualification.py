from __future__ import annotations

import errno
import os
import signal
import subprocess
from pathlib import Path

import pytest

from p3_v3.artifacts import EvidenceError, read_canonical_json
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


def _git_env() -> dict[str, str]:
    env = dict(os.environ)
    env["GIT_CONFIG_GLOBAL"] = "/dev/null"
    env["GIT_CONFIG_NOSYSTEM"] = "1"
    env["GIT_CONFIG_COUNT"] = "0"
    return env


def _init_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    env = _git_env()
    subprocess.run(
        ["git", "init"],
        cwd=repo,
        check=True,
        capture_output=True,
        env=env,
    )
    subprocess.run(
        [
            "git",
            "-c",
            "user.name=t",
            "-c",
            "user.email=t@t.t",
            "commit",
            "--allow-empty",
            "-m",
            "init",
        ],
        cwd=repo,
        check=True,
        capture_output=True,
        env=env,
    )
    return repo


def _make_compiler(tmp_path: Path) -> Path:
    path = tmp_path / "toolchain" / "c++"
    path.parent.mkdir()
    path.write_bytes(b"fake-cxx")
    path.chmod(0o755)
    return path


class _Proc:
    def __init__(
        self,
        stdout: bytes = b"",
        stderr: bytes = b"",
        returncode: int = 0,
        timed_out: bool = False,
        cleanup_error: bool = False,
        wait_error: bool = False,
    ) -> None:
        self._stdout = stdout
        self._stderr = stderr
        self.returncode = returncode
        self._timed_out = timed_out
        self._cleanup_error = cleanup_error
        self._wait_error = wait_error
        self.pid = 2_000_000_000
        self._first = True

    def communicate(
        self, timeout: float | None = None
    ) -> tuple[bytes | None, bytes | None]:
        if self._wait_error and self._first:
            self._first = False
            raise OSError("synthetic wait io")
        if self._timed_out and self._first:
            self._first = False
            raise subprocess.TimeoutExpired(
                ["synthetic"],
                timeout,
                output=self._stdout,
                stderr=self._stderr,
            )
        if self._cleanup_error:
            raise OSError("synthetic reap failed")
        if self._timed_out:
            return None, None
        return self._stdout, self._stderr

    def poll(self) -> int | None:
        return None if self._timed_out and self._first else self.returncode

    def kill(self) -> None:
        return None


def _unexpected_popen(*_args: object, **_kwargs: object) -> None:
    raise AssertionError("popen must not be called")


def _run_synthetic_qualification(tmp_path: Path, **opts: object):
    repo = _init_repo(tmp_path)
    root = tmp_path / "qual"
    compiler = _make_compiler(tmp_path)
    calls: list[list[str]] = []
    env = dict(opts.get("env") or {})

    def which(name: str) -> str | None:
        if opts.get("missing_compiler"):
            return None
        if name == "c++":
            return str(compiler)
        return None

    def popen(argv: list[str], **kwargs: object) -> _Proc:
        assert kwargs.get("shell") is False
        assert kwargs.get("start_new_session") is True
        assert kwargs.get("stdout") is subprocess.PIPE
        assert kwargs.get("stderr") is subprocess.PIPE
        calls.append(list(argv))
        if argv[-1:] == ["--version"] or argv[-1] == "--version":
            if opts.get("metadata_popen_error"):
                raise PermissionError("synthetic metadata popen denied")
            if opts.get("observe_metadata_fs"):
                assert (root / "qualification-intent.json").is_file()
                assert (root / "qualify.cpp").is_file()
                assert not (root / "qualification-result.json").exists()
                assert not (root / "qualification-manifest.json").exists()
            if opts.get("metadata_wait_error"):
                return _Proc(
                    stdout=opts.get("compiler_version_stdout", b"partial"),
                    stderr=opts.get("compiler_version_stderr", b""),
                    wait_error=True,
                    cleanup_error=bool(opts.get("cleanup_error")),
                )
            if opts.get("compiler_version_timeout"):
                return _Proc(
                    stdout=opts.get("compiler_version_stdout", b"clang\n"),
                    stderr=opts.get("compiler_version_stderr", b""),
                    timed_out=True,
                    cleanup_error=bool(opts.get("cleanup_error")),
                )
            return _Proc(
                stdout=opts.get("compiler_version_stdout", b"clang\n"),
                stderr=opts.get("compiler_version_stderr", b""),
                returncode=int(opts.get("compiler_version_exit", 0)),
            )
        if "-std=c++14" in argv:
            if opts.get("compile_popen_error"):
                raise OSError("synthetic compile popen denied")
            if opts.get("create_regular_executable"):
                out = root / "qualify"
                out.write_bytes(b"ELF")
                out.chmod(0o755)
            if opts.get("create_symlink_executable"):
                target = root / "qualify.target"
                target.write_bytes(b"ELF")
                (root / "qualify").symlink_to(target)
            if opts.get("create_nonregular_executable"):
                (root / "qualify").mkdir()
            if opts.get("create_nonexecutable_executable"):
                out = root / "qualify"
                out.write_bytes(b"ELF")
                out.chmod(0o644)
            if opts.get("mutate_repo_during_compile") or (
                opts.get("mutate_repo_during_last_job")
                and opts.get("binary_unreached")
            ):
                (repo / "drift.txt").write_text("x")
            if opts.get("compile_wait_error"):
                return _Proc(
                    stdout=opts.get("compile_stdout", b""),
                    stderr=opts.get("compile_stderr", b""),
                    wait_error=True,
                    cleanup_error=bool(opts.get("cleanup_error")),
                )
            if opts.get("compile_timeout"):
                return _Proc(
                    timed_out=True,
                    cleanup_error=bool(opts.get("cleanup_error")),
                )
            return _Proc(
                stdout=opts.get("compile_stdout", b""),
                stderr=opts.get("compile_stderr", b""),
                returncode=int(opts.get("compile_exit", 0)),
            )
        if opts.get("binary_popen_error"):
            raise OSError("synthetic binary popen denied")
        if opts.get("mutate_repo_during_last_job"):
            (repo / "drift.txt").write_text("x")
        if opts.get("binary_timeout"):
            return _Proc(
                timed_out=True,
                cleanup_error=bool(opts.get("cleanup_error")),
            )
        return _Proc(
            stdout=opts.get("binary_stdout", b""),
            stderr=opts.get("binary_stderr", b""),
            returncode=int(opts.get("binary_exit", 0)),
        )

    if "create_regular_executable" not in opts:
        opts["create_regular_executable"] = True
    if opts.get("compiler_not_executable"):
        compiler.chmod(0o644)
    result = q.run_qualification(
        repo_root=repo,
        qualification_root=root,
        env=env,
        which=which,
        popen=popen,
    )
    manifest = read_canonical_json(root / "qualification-manifest.json")
    result["_calls"] = calls
    return result, manifest, root


def test_preexisting_root_is_not_deleted_or_reused(tmp_path):
    root = tmp_path / "qualification"
    root.mkdir()
    marker = root / "owned"
    marker.write_bytes(b"unchanged")
    with pytest.raises(EvidenceError, match="E_QUALIFICATION_PREEXISTING"):
        q.run_qualification(
            repo_root=tmp_path,
            qualification_root=root,
            env={},
            which=lambda _name: "/usr/bin/c++",
            popen=_unexpected_popen,
        )
    assert marker.read_bytes() == b"unchanged"


@pytest.mark.parametrize("key", list(q.FORBIDDEN_ENV))
def test_forbidden_env_fails_before_root_or_process(tmp_path, key):
    root = tmp_path / "qual"
    with pytest.raises(EvidenceError, match="E_FORBIDDEN_ENV"):
        q.run_qualification(
            repo_root=tmp_path,
            qualification_root=root,
            env={key: "value"},
            which=lambda _name: "/usr/bin/c++",
            popen=_unexpected_popen,
        )
    assert not root.exists()


def test_empty_forbidden_env_is_bound_in_intent(tmp_path):
    env = {key: "" for key in q.FORBIDDEN_ENV}
    result, _manifest, root = _run_synthetic_qualification(tmp_path, env=env)
    intent = read_canonical_json(root / "qualification-intent.json")
    for key in q.FORBIDDEN_ENV:
        assert intent["relevant_environment"][key] == ""
    assert result["terminal_status"] == "PASS"


def test_successful_call_order_and_metadata_fs(tmp_path):
    result, _manifest, root = _run_synthetic_qualification(
        tmp_path,
        observe_metadata_fs=True,
    )
    compiler = tmp_path / "toolchain" / "c++"
    assert result["_calls"] == [
        [str(compiler), "--version"],
        [
            str(compiler),
            "-std=c++14",
            str(root / "qualify.cpp"),
            "-o",
            str(root / "qualify"),
        ],
        [str(root / "qualify")],
    ]
    assert result["terminal_status"] == "PASS"


def test_missing_compiler_writes_terminal_evidence(tmp_path):
    result, manifest, root = _run_synthetic_qualification(
        tmp_path,
        missing_compiler=True,
    )
    assert result["terminal_status"] == "FAIL"
    assert result["failure_reason"] == "MISSING_COMPILER"
    assert result["compiler_version"] is None
    assert all(job["terminal_status"] == "NOT_STARTED" for job in result["jobs"])
    intent = read_canonical_json(root / "qualification-intent.json")
    assert intent["compile_link_argv"] is None
    assert result["_calls"] == []
    paths = {entry["path"] for entry in manifest["files"]}
    assert "qualification-intent.json" in paths
    assert "qualification-result.json" in paths
    assert "qualify.cpp" in paths
    assert "CXX_COMPILE_LINK.stdout" not in paths


def test_runner_embeds_identical_captured_host_snapshot(tmp_path):
    result, manifest, root = _run_synthetic_qualification(tmp_path)
    intent = read_canonical_json(root / "qualification-intent.json")
    published = read_canonical_json(root / "qualification-result.json")
    assert published == {
        key: value for key, value in result.items() if key != "_calls"
    }
    assert intent["host_snapshot"] == published["host_snapshot"]
    assert intent["host_snapshot_sha256"] == published["host_snapshot_sha256"]
    assert (
        intent["host_snapshot"]["artifact_sha256"]
        == intent["host_snapshot_sha256"]
    )
    assert manifest["result_sha256"]


def test_compiler_version_timeout_blocks_workloads_and_closes_evidence(
    tmp_path,
):
    result, manifest, root = _run_synthetic_qualification(
        tmp_path,
        compiler_version_timeout=True,
    )
    assert result["compiler_version"]["terminal_status"] == "TIMEOUT"
    assert result["compiler_version"]["timeout_seconds"] == 10
    assert all(job["terminal_status"] == "NOT_STARTED" for job in result["jobs"])
    assert result["terminal_status"] == "FAIL"
    assert result["failure_reason"] == "METADATA_TIMEOUT"
    assert manifest["result_sha256"]
    assert (root / "METADATA_CXX_VERSION.stdout").is_file()


def test_compiler_version_nonzero_blocks_workloads(tmp_path):
    result, _manifest, _root = _run_synthetic_qualification(
        tmp_path,
        compiler_version_exit=2,
    )
    assert result["compiler_version"]["terminal_status"] == "FAIL"
    assert all(job["terminal_status"] == "NOT_STARTED" for job in result["jobs"])
    assert result["terminal_status"] == "FAIL"


def test_compile_stdout_is_unexpected_output_and_blocks_binary(tmp_path):
    result, manifest, root = _run_synthetic_qualification(
        tmp_path,
        compile_exit=0,
        compile_stdout=b"warning\n",
        create_regular_executable=True,
    )
    assert result["jobs"][0]["terminal_status"] == "FAIL"
    assert result["jobs"][0]["failure_reason"] == "UNEXPECTED_OUTPUT"
    assert result["jobs"][1]["terminal_status"] == "NOT_STARTED"
    assert result["terminal_status"] == "FAIL"
    assert result["failure_reason"] == "UNEXPECTED_OUTPUT"
    assert result["executable_sha256"] is not None
    assert result["executable_bytes"] is not None
    assert result["executable_regular"] is True
    assert result["executable_symlink"] is False
    assert (root / "CXX_COMPILE_LINK.stdout").read_bytes() == b"warning\n"
    paths = {entry["path"] for entry in manifest["files"]}
    assert "CXX_COMPILE_LINK.stdout" in paths
    assert "qualify" in paths


def test_compile_stderr_is_unexpected_output_and_blocks_binary(tmp_path):
    result, manifest, _root = _run_synthetic_qualification(
        tmp_path,
        compile_stderr=b"note\n",
        create_regular_executable=True,
    )
    assert result["jobs"][0]["failure_reason"] == "UNEXPECTED_OUTPUT"
    assert result["jobs"][1]["terminal_status"] == "NOT_STARTED"
    assert result["executable_regular"] is True
    assert "qualify" in {entry["path"] for entry in manifest["files"]}


def test_binary_stdout_is_unexpected_output(tmp_path):
    result, manifest, _root = _run_synthetic_qualification(
        tmp_path,
        binary_stdout=b"hi\n",
    )
    assert result["jobs"][0]["terminal_status"] == "PASS"
    assert result["jobs"][1]["failure_reason"] == "UNEXPECTED_OUTPUT"
    assert result["failure_reason"] == "UNEXPECTED_OUTPUT"
    assert result["executable_regular"] is True
    assert "qualify" in {entry["path"] for entry in manifest["files"]}


def test_binary_stderr_is_unexpected_output(tmp_path):
    result, _manifest, _root = _run_synthetic_qualification(
        tmp_path,
        binary_stderr=b"err\n",
    )
    assert result["jobs"][1]["failure_reason"] == "UNEXPECTED_OUTPUT"
    assert result["executable_regular"] is True


def test_missing_or_symlink_executable_clears_grouped_evidence(tmp_path):
    result, manifest, _root = _run_synthetic_qualification(
        tmp_path,
        compile_exit=0,
        create_regular_executable=False,
        create_symlink_executable=True,
    )
    assert result["jobs"][1]["terminal_status"] == "NOT_STARTED"
    assert result["executable_sha256"] is None
    assert result["executable_bytes"] is None
    assert result["executable_regular"] is None
    assert result["executable_symlink"] is None
    assert "qualify" not in {entry["path"] for entry in manifest["files"]}


def test_missing_executable_clears_grouped_evidence(tmp_path):
    result, manifest, _root = _run_synthetic_qualification(
        tmp_path,
        create_regular_executable=False,
    )
    assert result["jobs"][1]["terminal_status"] == "NOT_STARTED"
    assert result["executable_sha256"] is None
    assert "qualify" not in {entry["path"] for entry in manifest["files"]}


def test_nonregular_executable_clears_grouped_evidence(tmp_path):
    result, manifest, _root = _run_synthetic_qualification(
        tmp_path,
        create_regular_executable=False,
        create_nonregular_executable=True,
    )
    assert result["jobs"][1]["terminal_status"] == "NOT_STARTED"
    assert result["executable_sha256"] is None
    assert "qualify" not in {entry["path"] for entry in manifest["files"]}


def test_compile_nonzero_keeps_valid_executable_evidence(tmp_path):
    result, manifest, _root = _run_synthetic_qualification(
        tmp_path,
        compile_exit=3,
        create_regular_executable=True,
    )
    assert result["jobs"][0]["terminal_status"] == "FAIL"
    assert result["jobs"][0]["failure_reason"] == "NONZERO_EXIT"
    assert result["jobs"][1]["terminal_status"] == "NOT_STARTED"
    assert result["executable_regular"] is True
    assert "qualify" in {entry["path"] for entry in manifest["files"]}


def test_compile_timeout_keeps_valid_executable_evidence(tmp_path):
    result, manifest, _root = _run_synthetic_qualification(
        tmp_path,
        compile_timeout=True,
        create_regular_executable=True,
    )
    assert result["jobs"][0]["terminal_status"] == "TIMEOUT"
    assert result["jobs"][1]["terminal_status"] == "NOT_STARTED"
    assert result["executable_regular"] is True
    assert "qualify" in {entry["path"] for entry in manifest["files"]}


def test_timeout_uses_final_null_fallback(tmp_path):
    result, _manifest, _root = _run_synthetic_qualification(
        tmp_path,
        compiler_version_timeout=True,
        compiler_version_stdout=b"partial",
    )
    version = result["compiler_version"]
    assert version["terminal_status"] == "TIMEOUT"
    assert version["stdout_bytes"] == len(b"partial")


def test_pass_requires_matching_clean_repository_postcondition(tmp_path):
    result, manifest, _root = _run_synthetic_qualification(tmp_path)
    assert result["terminal_status"] == "PASS"
    assert result["failure_reason"] is None
    assert result["formal_denominator_membership"] is False
    assert result["attempt_2_authorized"] is False
    assert result["claims"] == "blocked"
    assert result["jobs"][0]["stdout_bytes"] == 0
    assert result["jobs"][0]["stderr_bytes"] == 0
    assert result["jobs"][1]["stdout_bytes"] == 0
    assert result["jobs"][1]["stderr_bytes"] == 0
    assert result["host_snapshot"]["repository_clean"] is True
    paths = [entry["path"] for entry in manifest["files"]]
    assert paths == sorted(set(paths))
    assert "qualification-manifest.json" not in paths


def test_compile_failure_still_reports_repository_drift(tmp_path):
    result, _manifest, root = _run_synthetic_qualification(
        tmp_path,
        compile_exit=3,
        create_regular_executable=True,
        mutate_repo_during_compile=True,
    )
    assert result["jobs"][0]["terminal_status"] == "FAIL"
    assert result["jobs"][0]["failure_reason"] == "NONZERO_EXIT"
    assert result["jobs"][1]["terminal_status"] == "NOT_STARTED"
    assert result["terminal_status"] == "FAIL"
    assert result["failure_reason"] == "REPOSITORY_DRIFT"
    assert (root / "qualification-result.json").is_file()
    assert (root / "qualification-manifest.json").is_file()


def test_repository_drift_fails_and_preserves_process_evidence(tmp_path):
    result, _manifest, root = _run_synthetic_qualification(
        tmp_path,
        mutate_repo_during_last_job=True,
    )
    assert result["terminal_status"] == "FAIL"
    assert result["failure_reason"] == "REPOSITORY_DRIFT"
    assert result["jobs"][0]["terminal_status"] == "PASS"
    assert result["jobs"][1]["terminal_status"] == "PASS"
    assert (root / "qualification-result.json").is_file()
    assert (root / "qualification-manifest.json").is_file()


def test_binary_failure_preserves_compiled_executable_evidence(tmp_path):
    result, manifest, _root = _run_synthetic_qualification(
        tmp_path,
        compile_exit=0,
        create_regular_executable=True,
        binary_exit=7,
    )
    assert result["terminal_status"] == "FAIL"
    assert result["failure_reason"] == "NONZERO_EXIT"
    assert result["jobs"][0]["terminal_status"] == "PASS"
    assert result["jobs"][1]["terminal_status"] == "FAIL"
    assert result["executable_sha256"] is not None
    assert result["executable_bytes"] is not None
    assert result["executable_regular"] is True
    assert result["executable_symlink"] is False
    assert "qualify" in {entry["path"] for entry in manifest["files"]}


def test_binary_timeout_preserves_compiled_executable_evidence(tmp_path):
    result, manifest, _root = _run_synthetic_qualification(
        tmp_path,
        binary_timeout=True,
    )
    assert result["jobs"][1]["terminal_status"] == "TIMEOUT"
    assert result["executable_regular"] is True
    assert "qualify" in {entry["path"] for entry in manifest["files"]}


def test_not_started_process_start_error_is_allowed():
    job = _compile("NOT_STARTED", failure_reason="PROCESS_START_ERROR")
    validated = q.validate_process_evidence(job)
    assert validated["process_started"] is False
    assert validated["failure_reason"] == "PROCESS_START_ERROR"
    assert validated["exit_code"] is None
    assert validated["started_at"] is None


def test_not_started_process_start_error_rejects_invented_state():
    job = _compile(
        "NOT_STARTED",
        failure_reason="PROCESS_START_ERROR",
        exit_code=1,
    )
    with pytest.raises(EvidenceError):
        q.validate_process_evidence(job)


def test_process_wait_error_requires_group_terminated():
    job = _process(
        role="METADATA",
        job_id=q.JOB_METADATA,
        status="FAIL",
        argv=[CXX, "--version"],
        timeout=10,
        failure_reason="PROCESS_WAIT_ERROR",
        exit_code=None,
        process_group_terminated=True,
    )
    assert q.validate_process_evidence(job)["failure_reason"] == (
        "PROCESS_WAIT_ERROR"
    )
    bad = _process(
        role="METADATA",
        job_id=q.JOB_METADATA,
        status="FAIL",
        argv=[CXX, "--version"],
        timeout=10,
        failure_reason="PROCESS_WAIT_ERROR",
        exit_code=None,
        process_group_terminated=False,
    )
    with pytest.raises(EvidenceError):
        q.validate_process_evidence(bad)


def test_process_cleanup_failed_rejects_terminated_true():
    job = _compile(
        "FAIL",
        failure_reason="PROCESS_CLEANUP_FAILED",
        exit_code=None,
        process_group_terminated=True,
    )
    with pytest.raises(EvidenceError):
        q.validate_process_evidence(job)


def test_started_fail_rejects_missing_timestamps():
    job = _compile(
        "FAIL",
        failure_reason="PROCESS_WAIT_ERROR",
        exit_code=None,
        process_group_terminated=True,
        started_at=None,
    )
    with pytest.raises(EvidenceError):
        q.validate_process_evidence(job)


def test_not_started_rejects_unknown_failure_reason():
    job = _compile("NOT_STARTED", failure_reason="NONZERO_EXIT")
    with pytest.raises(EvidenceError):
        q.validate_process_evidence(job)


def test_metadata_popen_error_closes_terminal_evidence(tmp_path):
    result, manifest, root = _run_synthetic_qualification(
        tmp_path,
        metadata_popen_error=True,
    )
    version = result["compiler_version"]
    assert version["process_started"] is False
    assert version["terminal_status"] == "NOT_STARTED"
    assert version["failure_reason"] == "PROCESS_START_ERROR"
    assert all(job["terminal_status"] == "NOT_STARTED" for job in result["jobs"])
    assert result["terminal_status"] == "FAIL"
    assert result["failure_reason"] == "PROCESS_START_ERROR"
    assert (root / "qualification-result.json").is_file()
    assert (root / "qualification-manifest.json").is_file()
    assert not (root / "METADATA_CXX_VERSION.stdout").exists()
    assert not (root / "METADATA_CXX_VERSION.stderr").exists()
    assert manifest["result_sha256"]


def test_compile_popen_error_closes_terminal_evidence(tmp_path):
    result, _manifest, root = _run_synthetic_qualification(
        tmp_path,
        compile_popen_error=True,
    )
    assert result["compiler_version"]["terminal_status"] == "PASS"
    compile_job = result["jobs"][0]
    assert compile_job["process_started"] is False
    assert compile_job["terminal_status"] == "NOT_STARTED"
    assert compile_job["failure_reason"] == "PROCESS_START_ERROR"
    assert result["jobs"][1]["terminal_status"] == "NOT_STARTED"
    assert result["terminal_status"] == "FAIL"
    assert result["failure_reason"] == "PROCESS_START_ERROR"
    assert (root / "qualification-result.json").is_file()
    assert (root / "qualification-manifest.json").is_file()
    assert not (root / "CXX_COMPILE_LINK.stdout").exists()
    assert not (root / "CXX_COMPILE_LINK.stderr").exists()


def test_binary_popen_error_keeps_executable_and_closes(tmp_path):
    result, manifest, root = _run_synthetic_qualification(
        tmp_path,
        binary_popen_error=True,
    )
    assert result["compiler_version"]["terminal_status"] == "PASS"
    assert result["jobs"][0]["terminal_status"] == "PASS"
    run_job = result["jobs"][1]
    assert run_job["process_started"] is False
    assert run_job["terminal_status"] == "NOT_STARTED"
    assert run_job["failure_reason"] == "PROCESS_START_ERROR"
    assert result["terminal_status"] == "FAIL"
    assert result["failure_reason"] == "PROCESS_START_ERROR"
    assert result["executable_regular"] is True
    assert result["executable_symlink"] is False
    assert result["executable_sha256"] is not None
    assert (root / "qualification-result.json").is_file()
    assert (root / "qualification-manifest.json").is_file()
    assert "qualify" in {entry["path"] for entry in manifest["files"]}
    assert not (root / "QUALIFIED_BINARY_RUN.stdout").exists()
    assert not (root / "QUALIFIED_BINARY_RUN.stderr").exists()


def _patch_group_signals(
    monkeypatch: pytest.MonkeyPatch,
    *,
    killpg_error: BaseException | None = None,
    probe_error: BaseException | None = None,
) -> list[tuple[object, ...]]:
    recorded: list[tuple[object, ...]] = []

    def fake_getpgid(pid: int) -> int:
        recorded.append(("getpgid", pid))
        return pid

    def fake_killpg(pgid: int, sig: int) -> None:
        recorded.append(("killpg", pgid, sig))
        if sig == signal.SIGKILL:
            if killpg_error is not None:
                raise killpg_error
            return
        if sig == 0:
            if probe_error is not None:
                raise probe_error
            return
        raise AssertionError(f"unexpected killpg signal: {sig}")

    def fake_kill(pid: int, sig: int) -> None:
        recorded.append(("kill", pid, sig))

    monkeypatch.setattr(q.os, "getpgid", fake_getpgid)
    monkeypatch.setattr(q.os, "killpg", fake_killpg)
    monkeypatch.setattr(q.os, "kill", fake_kill)
    return recorded


def _patch_group_probe(
    monkeypatch: pytest.MonkeyPatch,
    *,
    terminate_error: BaseException | None = None,
    probe_error: BaseException | None = None,
) -> list[tuple[object, ...]]:
    recorded: list[tuple[object, ...]] = []

    def fake_getpgid(pid: int) -> int:
        recorded.append(("getpgid", pid))
        return pid

    def fake_killpg(pgid: int, sig: int) -> None:
        recorded.append(("killpg", pgid, sig))
        if sig == signal.SIGKILL:
            if terminate_error is not None:
                raise terminate_error
            return
        if sig == 0:
            if probe_error is not None:
                raise probe_error
            return
        raise AssertionError(f"unexpected killpg signal: {sig}")

    def fake_kill(pid: int, sig: int) -> None:
        recorded.append(("kill", pid, sig))
        if sig == 0:
            raise ProcessLookupError("leader pid is gone")

    monkeypatch.setattr(q.os, "getpgid", fake_getpgid)
    monkeypatch.setattr(q.os, "killpg", fake_killpg)
    monkeypatch.setattr(q.os, "kill", fake_kill)
    return recorded


def test_process_group_absent_uses_killpg_zero(monkeypatch):
    recorded: list[tuple[int, int]] = []

    def fake_killpg(pgid: int, sig: int) -> None:
        recorded.append((pgid, sig))
        raise ProcessLookupError("gone")

    def fake_kill(*_args: object) -> None:
        raise AssertionError("os.kill must not probe process groups")

    monkeypatch.setattr(q.os, "killpg", fake_killpg)
    monkeypatch.setattr(q.os, "kill", fake_kill)
    assert q._process_group_absent(2_000_000_000) is True
    assert recorded == [(2_000_000_000, 0)]


def test_process_group_absent_rejects_non_esrch_results(monkeypatch):
    cases: list[BaseException | None] = [
        None,
        PermissionError("denied"),
        OSError(errno.EPERM, "operation not permitted"),
        OSError(errno.EINVAL, "invalid argument"),
    ]

    def fake_kill(*_args: object) -> None:
        raise AssertionError("os.kill must not probe process groups")

    monkeypatch.setattr(q.os, "kill", fake_kill)
    for probe in cases:
        def fake_killpg(_pgid: int, sig: int, error=probe) -> None:
            assert sig == 0
            if error is not None:
                raise error

        monkeypatch.setattr(q.os, "killpg", fake_killpg)
        assert q._process_group_absent(7) is False


def test_process_group_absent_esrch_is_absent(monkeypatch):
    def fake_killpg(_pgid: int, sig: int) -> None:
        assert sig == 0
        raise OSError(errno.ESRCH, "no such process")

    def fake_kill(*_args: object) -> None:
        raise AssertionError("os.kill must not probe process groups")

    monkeypatch.setattr(q.os, "killpg", fake_killpg)
    monkeypatch.setattr(q.os, "kill", fake_kill)
    assert q._process_group_absent(7) is True


def test_timeout_fails_when_killpg_zero_probe_succeeds(tmp_path, monkeypatch):
    recorded = _patch_group_probe(monkeypatch)
    result, _manifest, root = _run_synthetic_qualification(
        tmp_path,
        compiler_version_timeout=True,
    )
    version = result["compiler_version"]
    assert version["terminal_status"] == "FAIL"
    assert version["failure_reason"] == "PROCESS_CLEANUP_FAILED"
    assert version["process_group_terminated"] is False
    assert (root / "qualification-result.json").is_file()
    assert ("killpg", 2_000_000_000, signal.SIGKILL) in recorded
    assert ("killpg", 2_000_000_000, 0) in recorded
    assert ("kill", 2_000_000_000, 0) not in recorded


def test_wait_error_fails_when_killpg_zero_probe_succeeds(tmp_path, monkeypatch):
    recorded = _patch_group_probe(monkeypatch)
    result, _manifest, root = _run_synthetic_qualification(
        tmp_path,
        metadata_wait_error=True,
    )
    version = result["compiler_version"]
    assert version["terminal_status"] == "FAIL"
    assert version["failure_reason"] == "PROCESS_CLEANUP_FAILED"
    assert version["process_group_terminated"] is False
    assert (root / "qualification-result.json").is_file()
    assert ("killpg", 2_000_000_000, 0) in recorded
    assert ("kill", 2_000_000_000, 0) not in recorded


def test_timeout_fails_when_killpg_zero_probe_is_permission(tmp_path, monkeypatch):
    recorded = _patch_group_probe(
        monkeypatch,
        probe_error=PermissionError("denied"),
    )
    result, _manifest, _root = _run_synthetic_qualification(
        tmp_path,
        compiler_version_timeout=True,
    )
    version = result["compiler_version"]
    assert version["terminal_status"] == "FAIL"
    assert version["failure_reason"] == "PROCESS_CLEANUP_FAILED"
    assert version["process_group_terminated"] is False
    assert ("killpg", 2_000_000_000, 0) in recorded
    assert ("kill", 2_000_000_000, 0) not in recorded


def test_timeout_cleanup_succeeds_when_leader_reaped_and_pgid_absent(
    tmp_path,
    monkeypatch,
):
    recorded = _patch_group_signals(
        monkeypatch,
        probe_error=ProcessLookupError("gone"),
    )
    result, _manifest, _root = _run_synthetic_qualification(
        tmp_path,
        compiler_version_timeout=True,
    )
    version = result["compiler_version"]
    assert version["terminal_status"] == "TIMEOUT"
    assert version["process_group_terminated"] is True
    assert version["failure_reason"] == "TIMEOUT"
    assert ("killpg", 2_000_000_000, signal.SIGKILL) in recorded
    assert ("killpg", 2_000_000_000, 0) in recorded
    assert ("kill", 2_000_000_000, 0) not in recorded
    assert recorded[0] == ("getpgid", 2_000_000_000)
    assert recorded.count(("getpgid", 2_000_000_000)) == 1
    assert result["_calls"] == [
        [str(tmp_path / "toolchain" / "c++"), "--version"]
    ]


def test_timeout_cleanup_fails_when_pgid_still_exists(tmp_path, monkeypatch):
    recorded = _patch_group_signals(monkeypatch)
    result, _manifest, root = _run_synthetic_qualification(
        tmp_path,
        compiler_version_timeout=True,
    )
    version = result["compiler_version"]
    assert version["terminal_status"] == "FAIL"
    assert version["failure_reason"] == "PROCESS_CLEANUP_FAILED"
    assert version["process_group_terminated"] is False
    assert all(job["terminal_status"] == "NOT_STARTED" for job in result["jobs"])
    assert (root / "qualification-result.json").is_file()
    assert ("killpg", 2_000_000_000, signal.SIGKILL) in recorded
    assert ("killpg", 2_000_000_000, 0) in recorded
    assert ("kill", 2_000_000_000, 0) not in recorded
    assert result["_calls"] == [
        [str(tmp_path / "toolchain" / "c++"), "--version"]
    ]


def test_timeout_cleanup_fails_when_killpg_fails_and_only_leader_killed(
    tmp_path,
    monkeypatch,
):
    recorded = _patch_group_signals(
        monkeypatch,
        killpg_error=PermissionError("denied"),
        probe_error=ProcessLookupError("gone"),
    )
    result, _manifest, root = _run_synthetic_qualification(
        tmp_path,
        compiler_version_timeout=True,
    )
    version = result["compiler_version"]
    assert version["terminal_status"] == "FAIL"
    assert version["failure_reason"] == "PROCESS_CLEANUP_FAILED"
    assert version["process_group_terminated"] is False
    assert (root / "qualification-result.json").is_file()
    assert (root / "qualification-manifest.json").is_file()
    assert ("killpg", 2_000_000_000, signal.SIGKILL) in recorded
    assert result["_calls"] == [
        [str(tmp_path / "toolchain" / "c++"), "--version"]
    ]


def test_metadata_timeout_cleanup_failure_closes_evidence(tmp_path):
    result, _manifest, root = _run_synthetic_qualification(
        tmp_path,
        compiler_version_timeout=True,
        cleanup_error=True,
        compiler_version_stdout=b"partial",
    )
    version = result["compiler_version"]
    assert version["terminal_status"] == "FAIL"
    assert version["failure_reason"] == "PROCESS_CLEANUP_FAILED"
    assert version["process_started"] is True
    assert version["process_group_terminated"] is False
    assert version["stdout_bytes"] == len(b"partial")
    assert all(job["terminal_status"] == "NOT_STARTED" for job in result["jobs"])
    assert result["terminal_status"] == "FAIL"
    assert result["failure_reason"] == "PROCESS_CLEANUP_FAILED"
    assert (root / "qualification-result.json").is_file()
    assert (root / "qualification-manifest.json").is_file()
    assert (root / "METADATA_CXX_VERSION.stdout").read_bytes() == b"partial"
    compiler = tmp_path / "toolchain" / "c++"
    assert result["_calls"] == [[str(compiler), "--version"]]


def test_nonexecutable_output_clears_grouped_evidence(tmp_path):
    result, manifest, root = _run_synthetic_qualification(
        tmp_path,
        compile_exit=0,
        create_regular_executable=False,
        create_nonexecutable_executable=True,
    )
    assert result["jobs"][0]["terminal_status"] == "PASS"
    assert result["jobs"][1]["terminal_status"] == "NOT_STARTED"
    assert result["terminal_status"] == "FAIL"
    assert result["failure_reason"] == "INVALID_EXECUTABLE"
    assert result["executable_sha256"] is None
    assert result["executable_bytes"] is None
    assert result["executable_regular"] is None
    assert result["executable_symlink"] is None
    assert "qualify" not in {entry["path"] for entry in manifest["files"]}
    assert (root / "qualify").is_file()
    assert not os.access(root / "qualify", os.X_OK)


def test_nonexecutable_compiler_is_unresolved(tmp_path):
    result, _manifest, root = _run_synthetic_qualification(
        tmp_path,
        compiler_not_executable=True,
    )
    assert result["terminal_status"] == "FAIL"
    assert result["failure_reason"] == "MISSING_COMPILER"
    assert result["compiler_version"] is None
    assert result["_calls"] == []
    intent = read_canonical_json(root / "qualification-intent.json")
    assert intent["resolved_compiler_path"] is None
    assert intent["compile_link_argv"] is None


def test_compile_timeout_cleanup_failure_closes_evidence(tmp_path):
    result, manifest, root = _run_synthetic_qualification(
        tmp_path,
        compile_timeout=True,
        cleanup_error=True,
        create_regular_executable=True,
    )
    compile_job = result["jobs"][0]
    assert result["compiler_version"]["terminal_status"] == "PASS"
    assert compile_job["terminal_status"] == "FAIL"
    assert compile_job["failure_reason"] == "PROCESS_CLEANUP_FAILED"
    assert compile_job["process_started"] is True
    assert compile_job["process_group_terminated"] is False
    assert result["jobs"][1]["terminal_status"] == "NOT_STARTED"
    assert result["terminal_status"] == "FAIL"
    assert result["failure_reason"] == "PROCESS_CLEANUP_FAILED"
    assert (root / "qualification-result.json").is_file()
    assert (root / "qualification-manifest.json").is_file()
    assert len(result["_calls"]) == 2
    assert result["executable_regular"] is True
    assert "qualify" in {entry["path"] for entry in manifest["files"]}


def test_metadata_wait_error_cleans_up_and_closes(tmp_path, monkeypatch):
    recorded = _patch_group_signals(
        monkeypatch,
        probe_error=ProcessLookupError("gone"),
    )
    result, _manifest, root = _run_synthetic_qualification(
        tmp_path,
        metadata_wait_error=True,
    )
    version = result["compiler_version"]
    assert version["process_started"] is True
    assert version["terminal_status"] == "FAIL"
    assert version["failure_reason"] == "PROCESS_WAIT_ERROR"
    assert version["process_group_terminated"] is True
    assert all(job["terminal_status"] == "NOT_STARTED" for job in result["jobs"])
    assert result["terminal_status"] == "FAIL"
    assert result["failure_reason"] == "PROCESS_WAIT_ERROR"
    assert (root / "qualification-result.json").is_file()
    assert (root / "qualification-manifest.json").is_file()
    assert (root / "METADATA_CXX_VERSION.stdout").read_bytes() == b"partial"
    assert ("killpg", 2_000_000_000, signal.SIGKILL) in recorded
    assert ("killpg", 2_000_000_000, 0) in recorded
    assert ("kill", 2_000_000_000, 0) not in recorded
    assert result["_calls"] == [
        [str(tmp_path / "toolchain" / "c++"), "--version"]
    ]


def test_metadata_wait_error_cleanup_failure_closes(tmp_path):
    result, _manifest, root = _run_synthetic_qualification(
        tmp_path,
        metadata_wait_error=True,
        cleanup_error=True,
    )
    version = result["compiler_version"]
    assert version["terminal_status"] == "FAIL"
    assert version["failure_reason"] == "PROCESS_CLEANUP_FAILED"
    assert version["process_group_terminated"] is False
    assert all(job["terminal_status"] == "NOT_STARTED" for job in result["jobs"])
    assert (root / "qualification-result.json").is_file()
    assert (root / "qualification-manifest.json").is_file()
    assert result["_calls"] == [
        [str(tmp_path / "toolchain" / "c++"), "--version"]
    ]


def test_compile_wait_error_cleans_up_and_closes(tmp_path, monkeypatch):
    _patch_group_signals(
        monkeypatch,
        probe_error=ProcessLookupError("gone"),
    )
    result, manifest, root = _run_synthetic_qualification(
        tmp_path,
        compile_wait_error=True,
        create_regular_executable=True,
    )
    compile_job = result["jobs"][0]
    assert result["compiler_version"]["terminal_status"] == "PASS"
    assert compile_job["process_started"] is True
    assert compile_job["terminal_status"] == "FAIL"
    assert compile_job["failure_reason"] == "PROCESS_WAIT_ERROR"
    assert compile_job["process_group_terminated"] is True
    assert result["jobs"][1]["terminal_status"] == "NOT_STARTED"
    assert result["failure_reason"] == "PROCESS_WAIT_ERROR"
    assert (root / "qualification-result.json").is_file()
    assert (root / "CXX_COMPILE_LINK.stdout").is_file()
    assert len(result["_calls"]) == 2
    assert result["executable_regular"] is True
    assert "qualify" in {entry["path"] for entry in manifest["files"]}


def test_compile_wait_error_cleanup_failure_closes(tmp_path):
    result, _manifest, root = _run_synthetic_qualification(
        tmp_path,
        compile_wait_error=True,
        cleanup_error=True,
        create_regular_executable=True,
    )
    compile_job = result["jobs"][0]
    assert compile_job["failure_reason"] == "PROCESS_CLEANUP_FAILED"
    assert compile_job["process_group_terminated"] is False
    assert result["jobs"][1]["terminal_status"] == "NOT_STARTED"
    assert result["failure_reason"] == "PROCESS_CLEANUP_FAILED"
    assert (root / "qualification-result.json").is_file()
    assert len(result["_calls"]) == 2


def test_resolver_oserror_closes_terminal_evidence(tmp_path):
    repo = _init_repo(tmp_path)
    root = tmp_path / "qual"

    def boom(_name: str) -> str | None:
        raise OSError("synthetic resolver failed")

    result = q.run_qualification(
        repo_root=repo,
        qualification_root=root,
        env={},
        which=boom,
        popen=_unexpected_popen,
    )
    intent = read_canonical_json(root / "qualification-intent.json")
    host = intent["host_snapshot"]
    assert root.is_dir()
    assert (root / "qualify.cpp").is_file()
    assert (root / "qualification-result.json").is_file()
    assert (root / "qualification-manifest.json").is_file()
    assert intent["resolved_compiler_path"] is None
    assert intent["resolved_compiler_realpath"] is None
    assert intent["compile_link_argv"] is None
    assert intent["binary_run_argv"] is None
    assert host["resolved_compiler_path"] is None
    assert host["resolved_compiler_realpath"] is None
    assert host["resolved_path_regular"] is None
    assert host["resolved_path_symlink"] is None
    assert result["compiler_version"] is None
    assert all(job["terminal_status"] == "NOT_STARTED" for job in result["jobs"])
    assert result["terminal_status"] == "FAIL"
    assert result["failure_reason"] == "COMPILER_RESOLUTION_ERROR"
    assert not (root / "METADATA_CXX_VERSION.stdout").exists()
    assert not (root / "CXX_COMPILE_LINK.stdout").exists()
    assert not (root / "QUALIFIED_BINARY_RUN.stdout").exists()


def test_resolver_oserror_with_drift_is_repository_drift(tmp_path):
    repo = _init_repo(tmp_path)
    root = tmp_path / "qual"

    def boom(_name: str) -> str | None:
        (repo / "drift.txt").write_text("x")
        raise OSError("synthetic resolver failed")

    result = q.run_qualification(
        repo_root=repo,
        qualification_root=root,
        env={},
        which=boom,
        popen=_unexpected_popen,
    )
    assert result["failure_reason"] == "REPOSITORY_DRIFT"
    assert result["compiler_version"] is None
    assert (root / "qualification-result.json").is_file()
    assert (root / "qualification-manifest.json").is_file()
    assert root.is_dir()


def test_resolver_assertion_error_is_not_swallowed(tmp_path):
    repo = _init_repo(tmp_path)
    root = tmp_path / "qual"

    def boom(_name: str) -> str | None:
        raise AssertionError("test programming error")

    with pytest.raises(AssertionError, match="test programming error"):
        q.run_qualification(
            repo_root=repo,
            qualification_root=root,
            env={},
            which=boom,
            popen=_unexpected_popen,
        )
    assert root.is_dir()
    assert not (root / "qualification-result.json").exists()


def test_entry_git_inspect_error_is_evidence_error(tmp_path):
    root = tmp_path / "qual"
    with pytest.raises(EvidenceError, match="E_GIT"):
        q.run_qualification(
            repo_root=tmp_path,
            qualification_root=root,
            env={},
            which=lambda _name: "/usr/bin/c++",
            popen=_unexpected_popen,
        )
    assert not root.exists()


_CLI_FORBIDDEN = (
    "--compiler",
    "--root",
    "--timeout",
    "--source",
    "--output",
    "--retry",
    "--cmake",
    "--boost-root",
    "--attempt-2",
)


def test_cli_parser_rejects_qualification_overrides():
    import scripts.p3_v3.qualify_cxx_link as qualify_cli

    parser = qualify_cli.build_parser()
    for flag in _CLI_FORBIDDEN:
        with pytest.raises(SystemExit):
            parser.parse_args([flag])
        with pytest.raises(SystemExit):
            parser.parse_args([flag, "x"])


def test_cli_binds_frozen_repo_root_and_environ(monkeypatch, capsys):
    import scripts.p3_v3.qualify_cxx_link as qualify_cli

    seen: dict[str, object] = {}

    def fake_run(repo_root, qualification_root, env, **_kwargs):
        seen["repo_root"] = repo_root
        seen["qualification_root"] = qualification_root
        seen["env"] = env
        return {"terminal_status": "PASS"}

    monkeypatch.setattr(qualify_cli, "run_qualification", fake_run)
    assert qualify_cli.main([]) == 0
    assert seen["repo_root"] == Path(qualify_cli.__file__).resolve().parents[2]
    assert seen["qualification_root"] == q.FROZEN_ROOT
    assert seen["env"] == dict(os.environ)
    captured = capsys.readouterr()
    assert captured.out == f"PASS {q.FROZEN_ROOT}\n"
    assert captured.err == ""


def test_cli_fail_exit_one_when_result_published(monkeypatch, capsys):
    import scripts.p3_v3.qualify_cxx_link as qualify_cli

    monkeypatch.setattr(
        qualify_cli,
        "run_qualification",
        lambda *_args, **_kwargs: {"terminal_status": "FAIL"},
    )
    assert qualify_cli.main([]) == 1
    assert capsys.readouterr().out == f"FAIL {q.FROZEN_ROOT}\n"


def test_cli_pre_evidence_error_exits_two(monkeypatch):
    import scripts.p3_v3.qualify_cxx_link as qualify_cli

    def boom(*_args, **_kwargs):
        raise EvidenceError("E_QUALIFICATION_PREEXISTING", "already exists")

    monkeypatch.setattr(qualify_cli, "run_qualification", boom)
    assert qualify_cli.main([]) == 2
