"""Canonical, durable primitives for P3 v3 evidence artifacts."""

from __future__ import annotations

import hashlib
import json
import os
import re
import secrets
import stat
import tempfile
from collections.abc import Mapping
from pathlib import Path, PurePosixPath
from typing import Any

_SHA256_RE = re.compile(r"[0-9a-f]{64}")


class EvidenceError(ValueError):
    """A fail-closed validation error with a stable machine code."""

    def __init__(self, code: str, detail: str):
        super().__init__(f"{code}: {detail}")
        self.code = code


def canonical_json_bytes(value: Any) -> bytes:
    """Return canonical UTF-8 JSON with exactly one terminal LF."""

    try:
        text = json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
        return text.encode("utf-8") + b"\n"
    except (TypeError, ValueError, UnicodeEncodeError) as exc:
        raise EvidenceError("E_CANONICAL_JSON", str(exc)) from exc


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def file_sha256(path: str | Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def validate_sha256(value: Any, field: str) -> str:
    if not isinstance(value, str) or _SHA256_RE.fullmatch(value) is None:
        raise EvidenceError("E_SHA256", f"{field} must be 64 lowercase hexadecimal characters")
    return value


def validate_exact_object(
    value: Any,
    schema: Mapping[str, type | tuple[type, ...]],
    context: str,
) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise EvidenceError("E_SCHEMA_TYPE", f"{context} must be an object")
    if set(value) != set(schema):
        raise EvidenceError(
            "E_SCHEMA_KEYS",
            f"{context} keys differ: expected {sorted(schema)}, observed {sorted(value)}",
        )
    for key, expected in schema.items():
        observed = value[key]
        expected_types = expected if isinstance(expected, tuple) else (expected,)
        if type(observed) not in expected_types:
            names = ",".join(item.__name__ for item in expected_types)
            raise EvidenceError(
                "E_SCHEMA_TYPE", f"{context}.{key} must have exact type {names}"
            )
    return value


def safe_relative_path(value: Any) -> PurePosixPath:
    if not isinstance(value, str) or not value or "\\" in value or "\x00" in value:
        raise EvidenceError("E_PATH", "path must be a nonempty canonical POSIX string")
    path = PurePosixPath(value)
    parts = value.split("/")
    if path.is_absolute() or any(part in {"", ".", ".."} for part in parts):
        raise EvidenceError("E_PATH", f"unsafe relative path: {value!r}")
    if path.as_posix() != value:
        raise EvidenceError("E_PATH", f"noncanonical relative path: {value!r}")
    return path


def _write_all(fd: int, payload: bytes) -> None:
    view = memoryview(payload)
    while view:
        written = os.write(fd, view)
        if written <= 0:
            raise OSError("short write")
        view = view[written:]


def _close_quietly(fd: int | None) -> None:
    if fd is None:
        return
    try:
        os.close(fd)
    except OSError:
        pass


def _directory_open_flags() -> int:
    return (
        os.O_RDONLY
        | getattr(os, "O_DIRECTORY", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )


def _open_parent_directory(
    path: Path,
    *,
    create: bool,
    code: str,
    context: str,
) -> tuple[int, str]:
    """Open a path's parent one component at a time under anchored dirfds."""

    target = Path(path)
    name = target.name
    if not name or name in {".", ".."} or "\x00" in name:
        raise EvidenceError(code, f"{context} path is invalid")
    parent = target.parent
    parts = parent.parts
    if target.is_absolute():
        anchor = os.sep
        components = parts[1:]
    else:
        anchor = "."
        components = parts
    if any(part in {"", ".", ".."} or "\x00" in part for part in components):
        raise EvidenceError(code, f"{context} path is invalid")

    flags = _directory_open_flags()
    current_fd: int | None = None
    try:
        current_fd = os.open(anchor, flags)
        for component in components:
            try:
                next_fd = os.open(component, flags, dir_fd=current_fd)
            except FileNotFoundError:
                if not create:
                    raise
                os.mkdir(component, 0o755, dir_fd=current_fd)
                next_fd = os.open(component, flags, dir_fd=current_fd)
            previous_fd = current_fd
            current_fd = next_fd
            _close_quietly(previous_fd)
        return current_fd, name
    except EvidenceError:
        _close_quietly(current_fd)
        raise
    except OSError as exc:
        _close_quietly(current_fd)
        raise EvidenceError(code, f"{context} parent is unavailable") from exc


def _fsync_directory(
    directory: Path, *, directory_fd: int | None = None
) -> None:
    if directory_fd is not None:
        os.fsync(directory_fd)
        return
    fd, _name = _open_parent_directory(
        Path(directory) / ".fsync-anchor",
        create=False,
        code="E_ARTIFACT_WRITE",
        context="artifact directory",
    )
    try:
        os.fsync(fd)
    finally:
        _close_quietly(fd)


def _discard_temporary(path: Path) -> None:
    try:
        path.unlink(missing_ok=True)
    except OSError:
        pass


def write_canonical_json(path: str | Path, value: Any, *, exclusive: bool) -> None:
    """Durably create or atomically replace one canonical JSON file."""

    target = Path(path)
    payload = canonical_json_bytes(value)
    if exclusive:
        parent_fd: int | None = None
        temporary_name: str | None = None
        fd: int | None = None
        try:
            parent_fd, target_name = _open_parent_directory(
                target,
                create=True,
                code="E_ARTIFACT_WRITE",
                context="artifact",
            )
            flags = (
                os.O_WRONLY
                | os.O_CREAT
                | os.O_EXCL
                | getattr(os, "O_NOFOLLOW", 0)
            )
            for _attempt in range(128):
                candidate = f".{target_name}.{secrets.token_hex(12)}.tmp"
                try:
                    fd = os.open(candidate, flags, 0o644, dir_fd=parent_fd)
                except FileExistsError:
                    continue
                temporary_name = candidate
                break
            if fd is None or temporary_name is None:
                raise OSError("unable to allocate exclusive temporary file")
            _write_all(fd, payload)
            os.fsync(fd)
            os.close(fd)
            fd = None
            try:
                os.link(
                    temporary_name,
                    target_name,
                    src_dir_fd=parent_fd,
                    dst_dir_fd=parent_fd,
                    follow_symlinks=False,
                )
            except FileExistsError as exc:
                raise EvidenceError(
                    "E_EXISTS", f"artifact already exists: {target}"
                ) from exc
            os.unlink(temporary_name, dir_fd=parent_fd)
            temporary_name = None
            _fsync_directory(target.parent, directory_fd=parent_fd)
        except EvidenceError:
            _close_quietly(fd)
            if temporary_name is not None and parent_fd is not None:
                try:
                    os.unlink(temporary_name, dir_fd=parent_fd)
                except OSError:
                    pass
            raise
        except BaseException as exc:
            _close_quietly(fd)
            if temporary_name is not None and parent_fd is not None:
                try:
                    os.unlink(temporary_name, dir_fd=parent_fd)
                except OSError:
                    pass
            raise EvidenceError(
                "E_ARTIFACT_WRITE", f"unable to create artifact: {target}"
            ) from exc
        finally:
            _close_quietly(parent_fd)
        return

    target.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary_name = tempfile.mkstemp(prefix=f".{target.name}.", dir=target.parent)
    temporary = Path(temporary_name)
    try:
        _write_all(fd, payload)
        os.fsync(fd)
        os.close(fd)
        os.replace(temporary, target)
        _fsync_directory(target.parent)
    except BaseException:
        try:
            os.close(fd)
        except OSError:
            pass
        temporary.unlink(missing_ok=True)
        raise


def _lstat_regular_path(path: Path, context: str) -> Path:
    """Compatibility precheck; the subsequent dirfd chain is authoritative."""

    absolute = path if path.is_absolute() else Path.cwd() / path
    current = Path(absolute.parts[0])
    try:
        for index, part in enumerate(absolute.parts[1:], 1):
            current /= part
            info = current.lstat()
            is_target = index == len(absolute.parts) - 1
            if stat.S_ISLNK(info.st_mode):
                raise EvidenceError(
                    "E_AUTHORITY_LOCK_PATH", f"{context} path is not symlink-free"
                )
            if is_target and not stat.S_ISREG(info.st_mode):
                raise EvidenceError(
                    "E_AUTHORITY_LOCK_PATH", f"{context} path is not a regular file"
                )
            if not is_target and not stat.S_ISDIR(info.st_mode):
                raise EvidenceError(
                    "E_AUTHORITY_LOCK_PATH", f"{context} parent is not a directory"
                )
    except EvidenceError:
        raise
    except OSError as exc:
        raise EvidenceError(
            "E_AUTHORITY_LOCK_PATH", f"{context} path is unavailable"
        ) from exc
    return absolute


def read_regular_file_snapshot(path: Path, context: str) -> tuple[bytes, int]:
    """Read immutable bytes and mode from one anchored regular-file fd."""

    _lstat_regular_path(Path(path), context)
    parent_fd: int | None = None
    fd: int | None = None
    flags = (
        os.O_RDONLY
        | getattr(os, "O_NOFOLLOW", 0)
        | getattr(os, "O_NONBLOCK", 0)
    )
    try:
        parent_fd, name = _open_parent_directory(
            Path(path),
            create=False,
            code="E_AUTHORITY_LOCK_PATH",
            context=context,
        )
        fd = os.open(name, flags, dir_fd=parent_fd)
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            raise EvidenceError(
                "E_AUTHORITY_LOCK_PATH", f"{context} path is not a regular file"
            )
        chunks: list[bytes] = []
        while True:
            chunk = os.read(fd, 1024 * 1024)
            if not chunk:
                return b"".join(chunks), os.fstat(fd).st_mode
            chunks.append(chunk)
    except EvidenceError:
        raise
    except OSError as exc:
        raise EvidenceError(
            "E_AUTHORITY_LOCK_PATH", f"{context} path could not be read safely"
        ) from exc
    finally:
        _close_quietly(fd)
        _close_quietly(parent_fd)


def read_canonical_regular_bytes(path: Path, context: str) -> bytes:
    """Read one regular file through an anchored no-symlink dirfd chain."""

    raw, _mode = read_regular_file_snapshot(path, context)
    return raw


def read_canonical_regular_json(path: Path, context: str) -> dict[str, Any]:
    """Safely read one canonical JSON object from a regular file."""

    raw = read_canonical_regular_bytes(path, context)
    try:
        value = json.loads(
            raw.decode("utf-8"),
            parse_constant=lambda token: (_ for _ in ()).throw(ValueError(token)),
        )
        is_canonical = isinstance(value, dict) and canonical_json_bytes(value) == raw
    except (
        UnicodeDecodeError,
        json.JSONDecodeError,
        ValueError,
        EvidenceError,
    ) as exc:
        raise EvidenceError(
            "E_AUTHORITY_LOCK_SCHEMA", f"{context} is not canonical JSON"
        ) from exc
    if not is_canonical:
        raise EvidenceError(
            "E_AUTHORITY_LOCK_SCHEMA", f"{context} is not a canonical JSON object"
        )
    return value


def read_canonical_json(path: str | Path) -> Any:
    source = Path(path)
    raw = source.read_bytes()
    try:
        value = json.loads(
            raw.decode("utf-8"),
            parse_constant=lambda token: (_ for _ in ()).throw(ValueError(token)),
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise EvidenceError("E_JSON", f"invalid JSON: {source}") from exc
    if canonical_json_bytes(value) != raw:
        raise EvidenceError("E_NONCANONICAL_JSON", f"noncanonical JSON bytes: {source}")
    return value
