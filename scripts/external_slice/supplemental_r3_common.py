#!/usr/bin/env python3
"""Fail-closed primitives for the Supplemental R3 Addendum 03 bundle."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import re
import stat
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Sequence


class GateError(RuntimeError):
    """An invariant failure that permanently closes the current runner."""


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def utc_now() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def atomic_write_bytes(path: Path, value: bytes, *, mode: int = 0o600) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, raw_tmp = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
    tmp = Path(raw_tmp)
    try:
        os.fchmod(fd, mode)
        with os.fdopen(fd, "wb") as handle:
            handle.write(value)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
        dir_fd = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(dir_fd)
        finally:
            os.close(dir_fd)
    except Exception:
        if tmp.exists():
            tmp.unlink()
        raise


def load_authority_contract(root: Path) -> dict[str, Any]:
    root = Path(root)
    base = root / "data/external_slice/supplemental_r3"
    try:
        scope = json.loads((base / "SCOPE.json").read_text(encoding="utf-8"))
        contract_manifest = json.loads((base / "CONTRACT_MANIFEST.json").read_text(encoding="utf-8"))
        amendment_manifest = json.loads(
            (base / "amendments/AMENDMENT_01_MANIFEST.json").read_text(encoding="utf-8")
        )
    except Exception as exc:
        raise GateError(f"authority_contract_json: {exc}") from exc
    contract_hashes = contract_manifest.get("contract_artifacts_sha256")
    amendment_hashes = amendment_manifest.get("original_contract_artifacts_sha256")
    if not isinstance(contract_hashes, dict) or contract_hashes != amendment_hashes:
        raise GateError("authority_manifest_hash_set")
    for relative, expected in contract_hashes.items():
        path = root / relative
        if not path.is_file() or path.is_symlink() or sha256_file(path) != expected:
            raise GateError(f"frozen_contract_hash: {relative}")
    deny = scope.get("batch3_denylist", {}).get("head_sha")
    if not isinstance(deny, str) or not re.fullmatch(r"[0-9a-f]{40}", deny):
        raise GateError("batch3_deny_scope")
    if contract_manifest.get("batch3_denylist", {}).get("head_sha") != deny:
        raise GateError("batch3_deny_manifest")
    return {
        "scope": scope,
        "contract_manifest": contract_manifest,
        "amendment_manifest": amendment_manifest,
        "batch3_deny_sha": deny,
    }


def verify_batch3_head_ancestry(*, root: Path, runner: Any) -> dict[str, Any]:
    deny = load_authority_contract(Path(root))["batch3_deny_sha"]
    stdout, stderr = runner.run(["git", "-C", str(Path(root)), "rev-list", "HEAD"])
    try:
        ancestry = stdout.decode("ascii").splitlines()
    except UnicodeDecodeError as exc:
        runner.fail_invariant("batch3_active_ancestry", "non_ascii")
        raise GateError("batch3_active_ancestry") from exc
    if (
        stderr
        or not ancestry
        or any(not re.fullmatch(r"[0-9a-f]{40}", value) for value in ancestry)
        or deny in ancestry
    ):
        runner.fail_invariant("batch3_active_ancestry", "membership")
        raise GateError("batch3_active_ancestry")
    return {"count": len(ancestry), "sha256": sha256_bytes(stdout)}


def verify_batch3_active_paths(*, root: Path, paths: Sequence[Path]) -> int:
    deny_bytes = load_authority_contract(Path(root))["batch3_deny_sha"].encode("ascii")
    checked = 0
    for value in paths:
        path = Path(value)
        if not path.is_file() or path.is_symlink():
            raise GateError("batch3_active_payload")
        if deny_bytes in path.read_bytes():
            raise GateError("batch3_active_payload")
        checked += 1
    if checked == 0:
        raise GateError("batch3_active_payload")
    return checked


def verify_frozen_inputs(
    *,
    root: Path,
    authority: str,
    runner: "TerminalCommandRunner",
    expected_r2_entries: Sequence[dict[str, str]] | None = None,
    expected_original_r3_entries: Sequence[dict[str, str]] | None = None,
    expected_admission_sheet: dict[str, str] | None = None,
) -> dict[str, Any]:
    if not re.fullmatch(r"[0-9a-f]{40}", authority):
        raise GateError("authority_sha")
    contract = load_authority_contract(Path(root))
    root_text = str(Path(root))
    r2_tree_raw, _ = runner.run([
        "git", "-C", root_text, "rev-parse", f"{authority}:data/external_slice/supplemental_r2"
    ])
    r2_tree = r2_tree_raw.decode("ascii", errors="strict").strip()
    if r2_tree != "2e8fe75233bed73c9facb1c66b5d72b6a172487d":
        raise GateError("r2_tree")
    tree_raw, _ = runner.run([
        "git", "-C", root_text, "ls-tree", "-r", "-z", authority, "--",
        "data/external_slice/supplemental_r2",
    ])
    r2_entries: list[dict[str, str]] = []
    for raw_item in tree_raw.split(b"\0"):
        if not raw_item:
            continue
        metadata, raw_path = raw_item.split(b"\t", 1)
        mode, object_type, oid = metadata.decode("ascii").split()
        path = raw_path.decode("utf-8")
        blob, _ = runner.run(["git", "-C", root_text, "show", f"{authority}:{path}"])
        r2_entries.append({
            "path": path,
            "mode": mode,
            "type": object_type,
            "oid": oid,
            "sha256": sha256_bytes(blob),
        })
    paths = [entry["path"] for entry in r2_entries]
    if len(paths) != 634 or len(paths) != len(set(paths)):
        raise GateError("r2_path_count")
    if expected_r2_entries is not None and r2_entries != list(expected_r2_entries):
        raise GateError("r2_entry_manifest")
    admission_raw, _ = runner.run([
        "git", "-C", root_text, "rev-parse", f"{authority}:data/external_slice/admission_sheet.csv"
    ])
    admission_blob = admission_raw.decode("ascii", errors="strict").strip()
    if admission_blob != "5ef073d4d6297639695491c46d20733236bede52":
        raise GateError("admission_blob")
    admission_bytes, _ = runner.run([
        "git", "-C", root_text, "show", f"{authority}:data/external_slice/admission_sheet.csv"
    ])
    admission_binding = {
        "blob": admission_blob,
        "sha256": sha256_bytes(admission_bytes),
    }
    if (
        admission_binding["sha256"]
        != "77f729b1297ef24d4223d5277b093c93ad84711dfbbe69a1927398d49d387a0a"
        or expected_admission_sheet is not None
        and admission_binding != expected_admission_sheet
    ):
        raise GateError("admission_sheet_binding")
    if expected_original_r3_entries is not None:
        original_raw, _ = runner.run([
            "git", "-C", root_text, "ls-tree", "-r", "-z", authority, "--",
            "data/external_slice/supplemental_r3",
        ])
        original_entries: list[dict[str, str]] = []
        for raw_item in original_raw.split(b"\0"):
            if not raw_item:
                continue
            metadata, raw_path = raw_item.split(b"\t", 1)
            mode, object_type, oid = metadata.decode("ascii").split()
            path = raw_path.decode("utf-8")
            blob, _ = runner.run(["git", "-C", root_text, "show", f"{authority}:{path}"])
            original_entries.append({
                "path": path,
                "mode": mode,
                "type": object_type,
                "oid": oid,
                "sha256": sha256_bytes(blob),
            })
        if original_entries != list(expected_original_r3_entries):
            raise GateError("original_r3_entry_manifest")
        for entry in original_entries:
            path = Path(root) / entry["path"]
            try:
                path_stat = os.lstat(path)
            except OSError as exc:
                raise GateError(f'original_r3_worktree: {entry["path"]}: {exc}') from exc
            if entry["mode"] == "120000":
                if not stat.S_ISLNK(path_stat.st_mode):
                    raise GateError(f'original_r3_mode: {entry["path"]}')
                current_bytes = os.readlink(path).encode("utf-8")
                current_mode = "120000"
            else:
                if not stat.S_ISREG(path_stat.st_mode) or stat.S_ISLNK(path_stat.st_mode):
                    raise GateError(f'original_r3_mode: {entry["path"]}')
                current_bytes = path.read_bytes()
                current_mode = "100755" if path_stat.st_mode & 0o111 else "100644"
            if current_mode != entry["mode"] or sha256_bytes(current_bytes) != entry["sha256"]:
                raise GateError(f'original_r3_worktree: {entry["path"]}')
        r3_root = Path(root) / "data/external_slice/supplemental_r3"
        actual_r3_paths = {
            path.relative_to(Path(root)).as_posix()
            for path in r3_root.rglob("*")
            if path.is_file() or path.is_symlink()
        }
        allowed_new = {
            "data/external_slice/supplemental_r3/EXECUTION_BUNDLE_AMENDMENT_01_BOOTSTRAP_ADDENDUM_03.json",
            "data/external_slice/supplemental_r3/LOCAL_RED_LOG_AMENDMENT_01_BOOTSTRAP_ADDENDUM_03.json",
            "data/external_slice/supplemental_r3/LOCAL_GREEN_LOG_AMENDMENT_01_BOOTSTRAP_ADDENDUM_03.json",
        }
        vm_seal = "data/external_slice/supplemental_r3/PRE_NETWORK_AUTHORITY.json"
        if (Path(root) / vm_seal).is_file():
            allowed_new.add(vm_seal)
        if actual_r3_paths != {entry["path"] for entry in original_entries} | allowed_new:
            raise GateError("original_r3_path_set")
    runner.run([
        "git", "-C", root_text, "diff", "--quiet", authority, "--",
        "data/external_slice/supplemental_r2", "data/external_slice/admission_sheet.csv",
    ])
    status_raw, _ = runner.run([
        "git", "-C", root_text, "status", "--porcelain=v1", "--untracked-files=all", "--",
        "data/external_slice/supplemental_r2", "data/external_slice/admission_sheet.csv",
    ])
    if status_raw:
        raise GateError("frozen_worktree_drift")
    return {
        "r2_tree": r2_tree,
        "r2_path_count": len(paths),
        "admission_blob": admission_blob,
        "batch3_deny_consistent": bool(contract["batch3_deny_sha"]),
    }


_FORBIDDEN_TOKEN_RE = re.compile(
    r"(?i)(?<![A-Za-z0-9])(?:readiness|r8|canonical_freeze|canonical-freeze|"
    r"admission_freeze|admission-freeze|freeze|merge|pr)(?![A-Za-z0-9])"
)


def guard_tokens(parts: Sequence[str]) -> None:
    for part in parts:
        if _FORBIDDEN_TOKEN_RE.search(str(part)):
            raise GateError(f"forbidden_token: {part}")


def audit_network_source_closure(root: Path, relative_paths: Sequence[str]) -> dict[str, Any]:
    forbidden_imports = {"socket", "requests", "httpx", "urllib", "aiohttp", "ftplib"}
    subprocess_files: set[str] = set()
    for relative in relative_paths:
        path = Path(root) / relative
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=relative)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                modules = {alias.name.split(".", 1)[0] for alias in node.names}
            elif isinstance(node, ast.ImportFrom):
                modules = {str(node.module).split(".", 1)[0]}
            else:
                modules = set()
            if modules:
                if modules & forbidden_imports:
                    raise GateError(f"forbidden_network_import: {relative}")
                if "subprocess" in modules:
                    subprocess_files.add(relative)
            if isinstance(node, ast.Call):
                is_os_system = (
                    isinstance(node.func, ast.Attribute)
                    and node.func.attr == "system"
                    and isinstance(node.func.value, ast.Name)
                    and node.func.value.id == "os"
                )
                uses_shell = any(
                    keyword.arg == "shell"
                    and isinstance(keyword.value, ast.Constant)
                    and keyword.value.value is True
                    for keyword in node.keywords
                )
                if is_os_system or uses_shell:
                    raise GateError(f"forbidden_shell_transport: {relative}")
    allowed_subprocess_files = {
        "scripts/external_slice/supplemental_r3_common.py",
        "scripts/external_slice/supplemental_r3_bootstrap.py",
        "scripts/external_slice/check_supplemental_r3_handoff_hashes.py",
    }
    if subprocess_files != allowed_subprocess_files:
        raise GateError(f"subprocess_source_closure: {sorted(subprocess_files)!r}")
    return {
        "python_network_imports": [],
        "subprocess_files": sorted(subprocess_files),
        "live_endpoint": ["gh", "api", "graphql"],
    }


Executor = Callable[[Sequence[str]], tuple[int, bytes, bytes]]


def _is_frozen_python_command(
    argv: Sequence[str], *, python_executable: str = "python3"
) -> bool:
    values = list(argv)
    if values == [python_executable, "-m", "pytest", "-q", "--maxfail=1"]:
        return True
    if len(values) != 9:
        return False
    report = values[7]
    return (
        values
        == [
            python_executable,
            "tests/external_slice/run_supplemental_r3_bootstrap_addendum_03_tdd_matrix.py",
            "--phase",
            "green",
            "--manifest",
            "tests/external_slice/supplemental_r3_bootstrap_addendum_03_tdd_nodes.json",
            "--report",
            report,
            "--vm-run",
        ]
        and bool(
            re.fullmatch(
                r"/tmp/supplemental-r3-a01-bootstrap-addendum-03-[^/]+/vm-green-report\.json",
                report,
            )
        )
    )


def _default_executor(argv: Sequence[str]) -> tuple[int, bytes, bytes]:
    proc = subprocess.run(list(argv), capture_output=True, check=False, shell=False)
    return proc.returncode, proc.stdout, proc.stderr


class TerminalCommandRunner:
    """Append-only argv runner that rejects all work after first failure."""

    def __init__(
        self,
        journal_path: Path,
        *,
        executor: Executor | None = None,
        shutdown_allowlist: Sequence[Sequence[str]] = (),
        python_executable: str = "python3",
    ) -> None:
        self.journal_path = Path(journal_path)
        self.executor = executor or _default_executor
        self.terminal = False
        self.sequence = 0
        self.evidence_request_count = 0
        self._request_keys: set[str] = set()
        self._active_operations: set[str] = set()
        self.success_closed = False
        self._push_used = False
        frozen_shutdown = {("git", "status", "--porcelain=v1")}
        if any(tuple(argv) not in frozen_shutdown for argv in shutdown_allowlist):
            raise GateError("shutdown_allowlist")
        self._shutdown_allowlist = {tuple(argv) for argv in shutdown_allowlist}
        self._shutdown_used = False
        if python_executable != "python3" and not Path(python_executable).is_absolute():
            raise GateError("python_executable")
        self._python_executable = python_executable
        self._load_existing_journal()

    def _load_existing_journal(self) -> None:
        if not self.journal_path.exists():
            return
        if not self.journal_path.is_file() or self.journal_path.is_symlink():
            raise GateError("journal_type")
        records: list[dict[str, Any]] = []
        for raw_line in self.journal_path.read_bytes().splitlines(keepends=True):
            try:
                record = json.loads(raw_line.decode("utf-8"))
            except Exception as exc:
                raise GateError(f"journal_json: {exc}") from exc
            if raw_line != canonical_json_bytes(record) + b"\n":
                raise GateError("journal_not_canonical")
            records.append(record)
        if records and [row.get("sequence") for row in records] != list(range(1, len(records) + 1)):
            raise GateError("journal_sequence")
        self.sequence = len(records)
        evidence_keys = {
            str(row["request_key"])
            for row in records
            if row.get("evidence_request") is True and row.get("request_key")
        }
        self.evidence_request_count = len(evidence_keys)
        self._request_keys = {
            str(row["request_key"]) for row in records if row.get("request_key")
        }
        pending = {
            str(row["request_key"])
            for row in records
            if row.get("stage") == "request_intent" and row.get("request_key")
        }
        resolved = {
            str(row["request_key"])
            for row in records
            if row.get("stage") in {"command", "invariant_failure"} and row.get("request_key")
        }
        pending_operations = {
            str(row["operation_key"])
            for row in records
            if row.get("stage") == "operation_intent" and row.get("operation_key")
        }
        resolved_operations = {
            str(row["operation_key"])
            for row in records
            if row.get("stage") in {"operation", "invariant_failure"}
            and row.get("operation_key")
        }
        pending_pushes = {
            str(row["push_key"])
            for row in records
            if row.get("stage") == "push_intent" and row.get("push_key")
        }
        resolved_pushes = {
            str(row["push_key"])
            for row in records
            if row.get("stage") == "push_completion" and row.get("push_key")
        }
        self.terminal = bool(pending - resolved) or bool(
            pending_operations - resolved_operations
        ) or bool(
            pending_pushes - resolved_pushes
        ) or any(
            row.get("runner_state") in {"terminal", "success_closed"} for row in records
        )
        self.success_closed = any(
            row.get("runner_state") == "success_closed" for row in records
        )
        self._push_used = any(
            row.get("stage") == "push_completion"
            and row.get("argv")
            == [
                "git", "push", "-u", "origin",
                "cursor/grok-phase3-supplemental-r3-amendment-01-bootstrap-addendum-03-evidence",
            ]
            and row.get("exit_code") == 0
            for row in records
        )
        self._shutdown_used = any(row.get("stage") == "shutdown_command" for row in records)

    def _append(self, record: dict[str, Any]) -> None:
        self.journal_path.parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(self.journal_path, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o600)
        try:
            os.write(fd, canonical_json_bytes(record) + b"\n")
            os.fsync(fd)
        finally:
            os.close(fd)

    def _fail_invariant(
        self,
        reason: str,
        argv: Sequence[str],
        *,
        evidence_request: bool = False,
        request_key: str | None = None,
    ) -> None:
        self.terminal = True
        self.sequence += 1
        error = reason.encode("utf-8")
        self._append({
            "sequence": self.sequence,
            "stage": "invariant_failure",
            "argv": list(argv),
            "started_at_utc": utc_now(),
            "ended_at_utc": utc_now(),
            "exit_code": 125,
            "stdout_sha256": sha256_bytes(b""),
            "stderr_sha256": sha256_bytes(error),
            "evidence_request": evidence_request,
            "evidence_request_count": self.evidence_request_count,
            "request_key": request_key,
            "runner_state": "terminal",
            "failure": reason,
        })

    def fail_invariant(self, stage: str, reason: str) -> None:
        if self.terminal:
            raise GateError("runner_terminal")
        self._fail_invariant(f"{stage}: {reason}", ["internal", stage])

    def record_terminal_context(self, stage: str, error: BaseException) -> None:
        """Append failure context without reopening a terminal runner."""
        self.sequence += 1
        encoded = f"{type(error).__name__}: {error}".encode("utf-8")
        self._append({
            "sequence": self.sequence,
            "stage": "terminal_context",
            "operation_name": stage,
            "started_at_utc": utc_now(),
            "ended_at_utc": utc_now(),
            "exit_code": 125,
            "stdout_sha256": sha256_bytes(b""),
            "stderr_sha256": sha256_bytes(encoded),
            "evidence_request": False,
            "evidence_request_count": self.evidence_request_count,
            "runner_state": "terminal",
            "failure": encoded.decode("utf-8"),
        })

    def begin_operation(self, name: str, metadata: dict[str, Any]) -> str:
        """Fsync a mutation intent before any internal filesystem operation."""
        if self.terminal:
            raise GateError("runner_terminal")
        if not isinstance(name, str) or not name or not isinstance(metadata, dict):
            self._fail_invariant("invalid_operation", ["internal", str(name)])
            raise GateError("invalid_operation")
        try:
            guard_tokens([name, canonical_json_bytes(metadata).decode("utf-8")])
        except GateError as exc:
            self._fail_invariant(str(exc), ["internal", name])
            raise
        operation_key = f"{self.sequence + 1}:{name}"
        self.sequence += 1
        self._append({
            "sequence": self.sequence,
            "stage": "operation_intent",
            "operation_name": name,
            "operation_key": operation_key,
            "metadata": metadata,
            "started_at_utc": utc_now(),
            "ended_at_utc": None,
            "evidence_request": False,
            "evidence_request_count": self.evidence_request_count,
            "runner_state": "pending",
        })
        self._active_operations.add(operation_key)
        return operation_key

    def complete_operation(self, operation_key: str, metadata: dict[str, Any]) -> None:
        if self.terminal:
            raise GateError("runner_terminal")
        if operation_key not in self._active_operations or not isinstance(metadata, dict):
            self._fail_invariant("operation_key", ["internal", "complete-operation"])
            raise GateError("operation_key")
        try:
            guard_tokens([canonical_json_bytes(metadata).decode("utf-8")])
        except GateError as exc:
            self._fail_invariant(str(exc), ["internal", "complete-operation"])
            raise
        self.sequence += 1
        self._append({
            "sequence": self.sequence,
            "stage": "operation",
            "operation_key": operation_key,
            "metadata": metadata,
            "started_at_utc": None,
            "ended_at_utc": utc_now(),
            "evidence_request": False,
            "evidence_request_count": self.evidence_request_count,
            "runner_state": "active",
        })
        self._active_operations.remove(operation_key)

    def run(
        self,
        argv: Sequence[str],
        *,
        evidence_request: bool = False,
        request_key: str | None = None,
        push_handoff_commit: str | None = None,
        push_preflight_sha256: str | None = None,
    ) -> tuple[bytes, bytes]:
        if self.terminal:
            if self.success_closed:
                raise GateError("runner_success_closed")
            key = tuple(argv)
            if key not in self._shutdown_allowlist or self._shutdown_used:
                raise GateError("runner_terminal")
            self._shutdown_used = True
            started = utc_now()
            try:
                exit_code, stdout, stderr = self.executor(key)
            except Exception as exc:
                self.sequence += 1
                encoded = f"shutdown_executor_error: {exc}".encode("utf-8")
                self._append({
                    "sequence": self.sequence,
                    "stage": "shutdown_command",
                    "argv": list(argv),
                    "started_at_utc": started,
                    "ended_at_utc": utc_now(),
                    "exit_code": 125,
                    "stdout_sha256": sha256_bytes(b""),
                    "stderr_sha256": sha256_bytes(encoded),
                    "evidence_request": False,
                    "evidence_request_count": self.evidence_request_count,
                    "request_key": None,
                    "runner_state": "terminal",
                    "failure": encoded.decode("utf-8"),
                })
                raise GateError(encoded.decode("utf-8")) from exc
            self.sequence += 1
            self._append({
                "sequence": self.sequence,
                "stage": "shutdown_command",
                "argv": list(argv),
                "started_at_utc": started,
                "ended_at_utc": utc_now(),
                "exit_code": int(exit_code),
                "stdout_sha256": sha256_bytes(stdout),
                "stderr_sha256": sha256_bytes(stderr),
                "evidence_request": False,
                "evidence_request_count": self.evidence_request_count,
                "request_key": None,
                "runner_state": "terminal",
            })
            if exit_code != 0:
                raise GateError("shutdown_command_failed")
            return stdout, stderr
        if not argv or any(not isinstance(part, str) or not part for part in argv):
            self._fail_invariant("invalid_argv", argv)
            raise GateError("invalid_argv")
        try:
            guard_tokens(argv)
            if any(part in {"|", "||", "&&", ";", ">", ">>"} for part in argv):
                raise GateError("shell_metacharacter")
            if argv[0] in {"curl", "wget", "http", "https", "ssh", "scp", "nc", "ncat"}:
                raise GateError("forbidden_network_command")
            if argv[0] == self._python_executable and not _is_frozen_python_command(
                argv, python_executable=self._python_executable
            ):
                raise GateError("forbidden_python_command")
            if argv[0] not in {"git", "gh", self._python_executable}:
                raise GateError("forbidden_executable")
            if argv[0] == "gh" and list(argv[:3]) != ["gh", "api", "graphql"]:
                raise GateError("forbidden_network_command")
            if list(argv[:3]) == ["gh", "api", "graphql"] and not evidence_request:
                raise GateError("unmarked_evidence_request")
            if evidence_request and list(argv[:3]) != ["gh", "api", "graphql"]:
                raise GateError("forbidden_network_command")
            if argv[0] == "git":
                git_args = list(argv[1:])
                while git_args[:1] == ["-C"] and len(git_args) >= 2:
                    git_args = git_args[2:]
                if git_args[:1] in (["for-each-ref"], ["show-ref"], ["fsck"]):
                    raise GateError("forbidden_git_inventory")
                if git_args[:2] == ["rev-list", "--all"]:
                    raise GateError("forbidden_git_inventory")
                if git_args[:1] in (["rebase"], ["cherry-pick"]):
                    raise GateError("forbidden_git_operation")
                if git_args[:1] in (["fetch"], ["pull"], ["clone"]):
                    raise GateError("forbidden_network_command")
                allowed_git_commands = {
                    "add", "commit", "config", "diff", "diff-tree", "ls-tree",
                    "push", "remote", "rev-list", "rev-parse", "show", "status",
                    "switch",
                }
                if not git_args or git_args[0] not in allowed_git_commands:
                    raise GateError("forbidden_git_operation")
                if git_args[:1] == ["push"] and any(part in {"-f", "--force", "--force-with-lease"} for part in git_args):
                    raise GateError("forbidden_force_push")
                if git_args[:1] == ["push"] and git_args != [
                    "push", "-u", "origin",
                    "cursor/grok-phase3-supplemental-r3-amendment-01-bootstrap-addendum-03-evidence",
                ]:
                    raise GateError("forbidden_git_operation")
                if git_args[:1] == ["push"] and self._push_used:
                    raise GateError("duplicate_push")
                if git_args[:1] == ["config"] and git_args != [
                    "config", "--get-all", "remote.origin.fetch"
                ]:
                    raise GateError("forbidden_git_operation")
                if git_args[:1] == ["remote"] and git_args != ["remote", "get-url", "origin"]:
                    raise GateError("forbidden_git_operation")
                if git_args[:1] == ["commit"] and git_args not in [
                    ["commit", "-m", "evidence(external): seal Supplemental R3 environment"],
                    ["commit", "-m", "evidence(external): publish Supplemental R3 payload"],
                    ["commit", "-m", "evidence(external): add Supplemental R3 handoff"],
                ]:
                    raise GateError("forbidden_git_operation")
                if git_args[:1] == ["add"] and (
                    len(git_args) < 2
                    or any(
                        part.startswith("-")
                        or not part.startswith("data/external_slice/supplemental_r3/")
                        for part in git_args[1:]
                    )
                ):
                    raise GateError("forbidden_git_operation")
                if git_args[:1] == ["switch"] and not (
                    len(git_args) == 4
                    and git_args[1:3] == [
                        "-c",
                        "cursor/grok-phase3-supplemental-r3-amendment-01-bootstrap-addendum-03-evidence",
                    ]
                    and re.fullmatch(r"[0-9a-f]{40}", git_args[3])
                ):
                    raise GateError("forbidden_git_operation")
            is_push = list(argv) == [
                "git", "push", "-u", "origin",
                "cursor/grok-phase3-supplemental-r3-amendment-01-bootstrap-addendum-03-evidence",
            ]
            if is_push and not re.fullmatch(r"[0-9a-f]{40}", str(push_handoff_commit or "")):
                raise GateError("push_handoff_commit")
            if is_push and not re.fullmatch(r"[0-9a-f]{64}", str(push_preflight_sha256 or "")):
                raise GateError("push_preflight_sha256")
            if not is_push and push_handoff_commit is not None:
                raise GateError("push_handoff_commit")
            if not is_push and push_preflight_sha256 is not None:
                raise GateError("push_preflight_sha256")
        except GateError as exc:
            self._fail_invariant(str(exc), argv)
            raise
        if evidence_request:
            if not request_key or request_key in self._request_keys:
                self._fail_invariant("duplicate_request", argv, request_key=request_key)
                raise GateError("duplicate_request")
            self._request_keys.add(request_key)
            self.evidence_request_count += 1
        started = utc_now()
        is_push = list(argv) == [
            "git", "push", "-u", "origin",
            "cursor/grok-phase3-supplemental-r3-amendment-01-bootstrap-addendum-03-evidence",
        ]
        push_key: str | None = None
        if evidence_request:
            self.sequence += 1
            self._append({
                "sequence": self.sequence,
                "stage": "request_intent",
                "argv": list(argv),
                "started_at_utc": started,
                "ended_at_utc": None,
                "exit_code": None,
                "stdout_sha256": None,
                "stderr_sha256": None,
                "evidence_request": True,
                "evidence_request_count": self.evidence_request_count,
                "request_key": request_key,
                "runner_state": "pending",
            })
        if is_push:
            pre_push_bytes = self.journal_path.read_bytes() if self.journal_path.exists() else b""
            pre_push_record_count = self.sequence
            push_key = f"{self.sequence + 1}:push"
            self.sequence += 1
            self._append({
                "sequence": self.sequence,
                "stage": "push_intent",
                "push_key": push_key,
                "argv": list(argv),
                "handoff_commit": push_handoff_commit,
                "preflight_sha256": push_preflight_sha256,
                "pre_push_journal_record_count": pre_push_record_count,
                "pre_push_journal_sha256": sha256_bytes(pre_push_bytes),
                "started_at_utc": started,
                "ended_at_utc": None,
                "exit_code": None,
                "stdout_sha256": None,
                "stderr_sha256": None,
                "evidence_request": False,
                "evidence_request_count": self.evidence_request_count,
                "request_key": None,
                "runner_state": "pending",
            })
        try:
            exit_code, stdout, stderr = self.executor(tuple(argv))
        except Exception as exc:
            self._fail_invariant(
                f"executor_error: {exc}",
                argv,
                evidence_request=evidence_request,
                request_key=request_key,
            )
            raise GateError(f"executor_error: {exc}") from exc
        ended = utc_now()
        self.sequence += 1
        failed = exit_code != 0
        successful_push = (
            not failed
            and list(argv)
            == [
                "git", "push", "-u", "origin",
                "cursor/grok-phase3-supplemental-r3-amendment-01-bootstrap-addendum-03-evidence",
            ]
        )
        record = {
            "sequence": self.sequence,
            "stage": "push_completion" if is_push else "command",
            "argv": list(argv),
            "started_at_utc": started,
            "ended_at_utc": ended,
            "exit_code": int(exit_code),
            "stdout_sha256": sha256_bytes(stdout),
            "stderr_sha256": sha256_bytes(stderr),
            "evidence_request": evidence_request,
            "evidence_request_count": self.evidence_request_count,
            "request_key": request_key,
            "runner_state": (
                "terminal" if failed else "success_closed" if successful_push else "active"
            ),
        }
        if is_push:
            record.update({
                "push_key": push_key,
                "handoff_commit": push_handoff_commit,
                "preflight_sha256": push_preflight_sha256,
            })
        self._append(record)
        if failed:
            self.terminal = True
            raise GateError(f"command_failed: {list(argv)!r}")
        if successful_push:
            self._push_used = True
            self.success_closed = True
            self.terminal = True
        return stdout, stderr


def persist_cli_failure(journal_path: Path, stage: str, error: BaseException) -> None:
    runner = TerminalCommandRunner(Path(journal_path))
    if runner.terminal:
        runner.record_terminal_context(stage, error)
        return
    runner.fail_invariant(stage, f"{type(error).__name__}: {error}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    run_command = commands.add_parser("run-command")
    run_command.add_argument("--journal", type=Path, required=True)
    run_command.add_argument("command_argv", nargs=argparse.REMAINDER)
    shutdown = commands.add_parser("run-shutdown-diagnostic")
    shutdown.add_argument("--journal", type=Path, required=True)
    return parser


def main(
    argv: Sequence[str] | None = None,
    *,
    executor: Executor | None = None,
) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "run-shutdown-diagnostic":
        shutdown_argv = ["git", "status", "--porcelain=v1"]
        runner = TerminalCommandRunner(
            args.journal,
            executor=executor,
            shutdown_allowlist=[shutdown_argv],
        )
        if not runner.terminal:
            raise GateError("shutdown_not_terminal")
        stdout, stderr = runner.run(shutdown_argv)
        sys.stdout.buffer.write(stdout)
        sys.stdout.buffer.flush()
        sys.stderr.buffer.write(stderr)
        sys.stderr.buffer.flush()
        return 0
    if args.command != "run-command" or not args.command_argv:
        raise GateError("run_command_argv")
    command_argv = list(args.command_argv)
    if command_argv[:1] == ["--"]:
        command_argv = command_argv[1:]
    if not command_argv:
        raise GateError("run_command_argv")
    runner = TerminalCommandRunner(args.journal, executor=executor)
    stdout, stderr = runner.run(command_argv)
    sys.stdout.buffer.write(stdout)
    sys.stdout.buffer.flush()
    sys.stderr.buffer.write(stderr)
    sys.stderr.buffer.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
