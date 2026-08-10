"""Repeatable, non-scientific preflight for one phase environment."""

from __future__ import annotations

import fcntl
import hashlib
import os
import platform
import re
import shutil
import subprocess
import tempfile
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from .artifacts import (
    EvidenceError,
    canonical_sha256,
    file_sha256,
    safe_relative_path,
    validate_exact_object,
    validate_sha256,
)

_SPEC_SCHEMA = {
    "schema_version": str,
    "repository_identity": str,
    "expected_commit": str,
    "dependency_lock_path": str,
    "dependency_lock_sha256": str,
    "phase_inputs": list,
    "smoke_commands": list,
    "timeout_seconds": int,
    "phase_role": str,
    "minimum_cpu_count": int,
    "minimum_memory_bytes": int,
    "minimum_disk_free_bytes": int,
    "worker_limit": int,
}
_INPUT_SCHEMA = {"path": str, "sha256": str}
_GIT_OID_RE = re.compile(r"[0-9a-f]{40}")
_PHASE_ROLES_AB = frozenset({"CONSTRUCTION_A", "CONTROLLED_B"})
_PHASE_ROLES = _PHASE_ROLES_AB | frozenset({"REAL_HOLDOUT_C"})
_PACKAGE_C_MARKERS = ("package-c", "REAL_HOLDOUT", "holdout")
_DARWIN_AVAILABLE_PAGE_CLASSES = frozenset(
    {"free", "inactive", "speculative", "purgeable"}
)


def _normalize_repository_origin(raw: str) -> tuple[str, str]:
    # Cursor VMs rewrite remotes via insteadOf and may inject HTTPS userinfo.
    candidate = re.sub(r"^(https://)[^/@]+@", r"\1", raw)
    patterns = (
        ("HTTPS", r"https://github.com/([^/]+/[^/]+?)(?:\.git)?$"),
        ("SSH", r"git@github.com:([^/]+/[^/]+?)(?:\.git)?$"),
        ("SSH", r"ssh://git@github.com/([^/]+/[^/]+?)(?:\.git)?$"),
    )
    for transport, pattern in patterns:
        match = re.fullmatch(pattern, candidate)
        if match:
            return f"github.com/{match.group(1)}", transport
    raise EvidenceError("E_REPOSITORY_IDENTITY", "unsupported repository origin")


def normalize_repository_identity(raw: str) -> str:
    return _normalize_repository_origin(raw)[0]


def _git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), *args],
        capture_output=True,
        text=True,
        shell=False,
        check=False,
    )
    if result.returncode != 0:
        raise EvidenceError("E_PREFLIGHT_GIT", f"git {' '.join(args)} failed")
    return result.stdout.strip()


def _stream_sha(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _parse_darwin_vm_stat(raw: bytes) -> int:
    text = raw.decode("ascii", errors="strict")
    page_size = None
    pages: dict[str, int] = {}
    for line in text.splitlines():
        header = re.fullmatch(
            r"Mach Virtual Memory Statistics: \(page size of ([0-9]+) bytes\)",
            line,
        )
        if header:
            if page_size is not None:
                raise ValueError("duplicate page size")
            page_size = int(header.group(1))
            continue
        page_class = re.fullmatch(
            r"Pages (free|inactive|speculative|purgeable):\s+([0-9]+)\.",
            line,
        )
        if page_class:
            name = page_class.group(1)
            if name in pages:
                raise ValueError("duplicate page class")
            pages[name] = int(page_class.group(2))
    if page_size is None or page_size < 1:
        raise ValueError("invalid page size")
    if pages.keys() != _DARWIN_AVAILABLE_PAGE_CLASSES:
        raise ValueError("missing page class")
    available = page_size * sum(pages.values())
    if available < 1:
        raise ValueError("available memory is not positive")
    return available


def _available_memory_bytes(executor=subprocess.run) -> int | None:
    try:
        page_size = os.sysconf("SC_PAGE_SIZE")
        avail_pages = os.sysconf("SC_AVPHYS_PAGES")
    except (AttributeError, OSError, ValueError):
        page_size = None
        avail_pages = None
    if (
        type(page_size) is int
        and type(avail_pages) is int
        and page_size > 0
        and avail_pages > 0
    ):
        return page_size * avail_pages
    if platform.system() != "Darwin":
        return None
    try:
        result = executor(
            ["vm_stat"],
            capture_output=True,
            shell=False,
            check=False,
            timeout=5,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0:
        return None
    try:
        return _parse_darwin_vm_stat(result.stdout)
    except (AttributeError, TypeError, ValueError):
        return None


def _probe_atomic_replace(_root: Path) -> str:
    probe_dir = Path(tempfile.mkdtemp(prefix="p3-preflight-atomic-"))
    try:
        source = probe_dir / "source"
        destination = probe_dir / "destination"
        source.write_bytes(b"atomic-source")
        destination.write_bytes(b"atomic-destination")
        os.replace(source, destination)
        if destination.is_file() and destination.read_bytes() == b"atomic-source":
            return "PASS"
        return "FAIL"
    except OSError:
        return "FAIL"
    finally:
        shutil.rmtree(probe_dir, ignore_errors=True)


def _probe_file_lock(_root: Path) -> str:
    handle = None
    path = None
    try:
        handle, path = tempfile.mkstemp(prefix="p3-preflight-lock-")
        fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        fcntl.flock(handle, fcntl.LOCK_UN)
        return "PASS"
    except OSError:
        return "FAIL"
    finally:
        if handle is not None:
            os.close(handle)
        if path is not None:
            try:
                os.unlink(path)
            except OSError:
                pass


def _path_has_package_c_marker(path: str) -> bool:
    lowered = path.lower()
    for marker in _PACKAGE_C_MARKERS:
        if marker.lower() in lowered or marker in path:
            return True
    return False


def run_preflight(
    repo_root: str | Path,
    specification: Mapping[str, Any],
    executor=subprocess.run,
) -> dict[str, Any]:
    root = Path(repo_root)
    spec = validate_exact_object(dict(specification), _SPEC_SCHEMA, "preflight")
    if spec["schema_version"] != "p3-preflight-v1":
        raise EvidenceError("E_PREFLIGHT_VERSION", "unsupported preflight schema")
    if not _GIT_OID_RE.fullmatch(spec["expected_commit"]):
        raise EvidenceError("E_PREFLIGHT_COMMIT", "expected commit is not a Git SHA-1")
    if type(spec["timeout_seconds"]) is not int or spec["timeout_seconds"] < 1:
        raise EvidenceError("E_PREFLIGHT_TIMEOUT", "timeout must be a positive integer")
    if spec["phase_role"] not in _PHASE_ROLES:
        raise EvidenceError("E_PREFLIGHT_PHASE_ROLE", "unsupported phase role")
    for key in (
        "minimum_cpu_count",
        "minimum_memory_bytes",
        "minimum_disk_free_bytes",
    ):
        if type(spec[key]) is not int or spec[key] < 0:
            raise EvidenceError("E_PREFLIGHT_RESOURCE", f"{key} must be a non-negative integer")
    if type(spec["worker_limit"]) is not int or spec["worker_limit"] < 1:
        raise EvidenceError("E_PREFLIGHT_WORKER", "worker_limit must be a positive integer")

    raw_origin = _git(root, "remote", "get-url", "origin")
    identity, origin_transport = _normalize_repository_origin(raw_origin)
    origin_sha256 = _stream_sha(raw_origin.encode("utf-8"))
    if identity != spec["repository_identity"]:
        raise EvidenceError("E_PREFLIGHT_REPOSITORY", "normalized repository identity differs")
    head = _git(root, "rev-parse", "HEAD")
    if head != spec["expected_commit"]:
        raise EvidenceError("E_PREFLIGHT_COMMIT", "HEAD differs from expected commit")
    if _git(root, "status", "--porcelain=v1", "--untracked-files=no"):
        raise EvidenceError("E_PREFLIGHT_DIRTY", "tracked worktree is dirty")

    lock_path = root / safe_relative_path(spec["dependency_lock_path"])
    validate_sha256(spec["dependency_lock_sha256"], "dependency_lock_sha256")
    if not lock_path.is_file() or file_sha256(lock_path) != spec["dependency_lock_sha256"]:
        raise EvidenceError("E_PREFLIGHT_DEPENDENCY_LOCK", "dependency lock differs")
    inputs: list[dict[str, str]] = []
    for index, candidate in enumerate(spec["phase_inputs"]):
        item = validate_exact_object(candidate, _INPUT_SCHEMA, f"phase_inputs[{index}]")
        path = safe_relative_path(item["path"]).as_posix()
        validate_sha256(item["sha256"], f"phase_inputs[{index}].sha256")
        if spec["phase_role"] in _PHASE_ROLES_AB and _path_has_package_c_marker(path):
            raise EvidenceError(
                "E_PREFLIGHT_PACKAGE_C",
                f"Package C path forbidden for {spec['phase_role']}: {path}",
            )
        absolute = root / path
        if not absolute.is_file() or absolute.is_symlink() or file_sha256(absolute) != item["sha256"]:
            raise EvidenceError("E_PREFLIGHT_INPUT", f"phase input differs: {path}")
        inputs.append({"path": path, "sha256": item["sha256"]})
    if [item["path"] for item in inputs] != sorted({item["path"] for item in inputs}):
        raise EvidenceError("E_PREFLIGHT_INPUT_ORDER", "phase inputs are not sorted and unique")

    cpu_count = os.cpu_count()
    if cpu_count is None:
        if spec["minimum_cpu_count"] > 0:
            raise EvidenceError("UNAVAILABLE", "cpu_count is unavailable on this platform")
        cpu_count = 0
    elif cpu_count < spec["minimum_cpu_count"]:
        raise EvidenceError("E_PREFLIGHT_CPU", "cpu_count below minimum_cpu_count")

    memory_available = _available_memory_bytes()
    if memory_available is None:
        if spec["minimum_memory_bytes"] > 0:
            raise EvidenceError("UNAVAILABLE", "available memory is unavailable on this platform")
    elif memory_available < spec["minimum_memory_bytes"]:
        raise EvidenceError("E_PREFLIGHT_MEMORY", "available memory below minimum_memory_bytes")

    disk = shutil.disk_usage(root)
    if disk.free < spec["minimum_disk_free_bytes"]:
        raise EvidenceError("E_PREFLIGHT_DISK", "disk free bytes below minimum_disk_free_bytes")

    declared_worker_limit = spec["worker_limit"]
    worker_limit = (
        min(declared_worker_limit, cpu_count) if cpu_count > 0 else declared_worker_limit
    )

    atomic_replace_status = _probe_atomic_replace(root)
    file_lock_status = _probe_file_lock(root)

    smoke: list[dict[str, Any]] = []
    failure_code = ""
    if atomic_replace_status != "PASS":
        failure_code = "E_PREFLIGHT_ATOMIC_REPLACE"
    elif file_lock_status != "PASS":
        failure_code = "E_PREFLIGHT_FILE_LOCK"
    else:
        for index, argv in enumerate(spec["smoke_commands"]):
            if not isinstance(argv, list) or not argv or any(
                type(arg) is not str or not arg for arg in argv
            ):
                raise EvidenceError("E_PREFLIGHT_ARGV", f"smoke command {index} is invalid")
            try:
                result = executor(
                    argv,
                    cwd=root,
                    capture_output=True,
                    shell=False,
                    timeout=spec["timeout_seconds"],
                    check=False,
                )
            except subprocess.TimeoutExpired as exc:
                stdout = exc.stdout or b""
                stderr = exc.stderr or b""
                smoke.append(
                    {
                        "argv": argv,
                        "exit_code": None,
                        "stdout_sha256": _stream_sha(stdout),
                        "stderr_sha256": _stream_sha(stderr),
                        "status": "TIMEOUT",
                    }
                )
                failure_code = "E_PREFLIGHT_TIMEOUT"
                break
            smoke.append(
                {
                    "argv": argv,
                    "exit_code": result.returncode,
                    "stdout_sha256": _stream_sha(result.stdout),
                    "stderr_sha256": _stream_sha(result.stderr),
                    "status": "PASS" if result.returncode == 0 else "FAIL",
                }
            )
            if result.returncode != 0:
                failure_code = "E_PREFLIGHT_SMOKE"
                break

    body = {
        "schema_version": "p3-preflight-result-v1",
        "status": "FAIL" if failure_code else "PASS",
        "failure_code": failure_code,
        "repository_identity": identity,
        "origin_transport": origin_transport,
        "origin_sha256": origin_sha256,
        "commit": head,
        "phase_role": spec["phase_role"],
        "platform": platform.system(),
        "machine": platform.machine(),
        "python": platform.python_version(),
        "cpu_count": cpu_count,
        "memory_available_bytes": memory_available,
        "disk_free_bytes": disk.free,
        "declared_worker_limit": declared_worker_limit,
        "worker_limit": worker_limit,
        "atomic_replace_status": atomic_replace_status,
        "file_lock_status": file_lock_status,
        "phase_inputs": inputs,
        "smoke": smoke,
    }
    return {**body, "artifact_sha256": canonical_sha256(body)}
