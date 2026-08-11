"""Canonical, durable primitives for P3 v3 evidence artifacts."""

from __future__ import annotations

import hashlib
import json
import os
import re
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
    except (TypeError, ValueError) as exc:
        raise EvidenceError("E_CANONICAL_JSON", str(exc)) from exc
    return text.encode("utf-8") + b"\n"


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


def _fsync_directory(directory: Path) -> None:
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
    fd = os.open(directory, flags)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def write_canonical_json(path: str | Path, value: Any, *, exclusive: bool) -> None:
    """Durably create or atomically replace one canonical JSON file."""

    target = Path(path)
    payload = canonical_json_bytes(value)
    if exclusive:
        temporary: Path | None = None
        fd: int | None = None
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            fd, temporary_name = tempfile.mkstemp(
                prefix=f".{target.name}.", suffix=".tmp", dir=target.parent
            )
            temporary = Path(temporary_name)
            os.fchmod(fd, 0o644)
            _write_all(fd, payload)
            os.fsync(fd)
            os.close(fd)
            fd = None
            try:
                os.link(temporary, target)
            except FileExistsError as exc:
                raise EvidenceError(
                    "E_EXISTS", f"artifact already exists: {target}"
                ) from exc
            temporary.unlink()
            temporary = None
            _fsync_directory(target.parent)
        except EvidenceError:
            if fd is not None:
                try:
                    os.close(fd)
                except OSError:
                    pass
            if temporary is not None:
                temporary.unlink(missing_ok=True)
            raise
        except BaseException as exc:
            if fd is not None:
                try:
                    os.close(fd)
                except OSError:
                    pass
            if temporary is not None:
                temporary.unlink(missing_ok=True)
            raise EvidenceError(
                "E_ARTIFACT_WRITE", f"unable to create artifact: {target}"
            ) from exc
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
    absolute = path if path.is_absolute() else Path.cwd() / path
    parts = absolute.parts
    current = Path(parts[0])
    try:
        for index, part in enumerate(parts[1:], 1):
            current /= part
            info = current.lstat()
            is_target = index == len(parts) - 1
            if stat.S_ISLNK(info.st_mode):
                raise EvidenceError(
                    "E_AUTHORITY_LOCK_PATH", f"{context} path is not symlink-free"
                )
            if is_target:
                if not stat.S_ISREG(info.st_mode):
                    raise EvidenceError(
                        "E_AUTHORITY_LOCK_PATH",
                        f"{context} path is not a regular file",
                    )
            elif not stat.S_ISDIR(info.st_mode):
                raise EvidenceError(
                    "E_AUTHORITY_LOCK_PATH",
                    f"{context} parent is not a directory",
                )
    except EvidenceError:
        raise
    except OSError as exc:
        raise EvidenceError(
            "E_AUTHORITY_LOCK_PATH", f"{context} path is unavailable"
        ) from exc
    return absolute


def read_canonical_regular_bytes(path: Path, context: str) -> bytes:
    """Read one symlink-free regular file without resolving path components."""

    source = _lstat_regular_path(Path(path), context)
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(source, flags)
        try:
            if not stat.S_ISREG(os.fstat(fd).st_mode):
                raise EvidenceError(
                    "E_AUTHORITY_LOCK_PATH", f"{context} path is not a regular file"
                )
            chunks: list[bytes] = []
            while True:
                chunk = os.read(fd, 1024 * 1024)
                if not chunk:
                    return b"".join(chunks)
                chunks.append(chunk)
        finally:
            os.close(fd)
    except EvidenceError:
        raise
    except OSError as exc:
        raise EvidenceError(
            "E_AUTHORITY_LOCK_PATH", f"{context} path could not be read safely"
        ) from exc


def read_canonical_regular_json(path: Path, context: str) -> dict[str, Any]:
    """Safely read one canonical JSON object from a regular file."""

    raw = read_canonical_regular_bytes(path, context)
    try:
        value = json.loads(
            raw.decode("utf-8"),
            parse_constant=lambda token: (_ for _ in ()).throw(ValueError(token)),
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise EvidenceError(
            "E_AUTHORITY_LOCK_SCHEMA", f"{context} is not canonical JSON"
        ) from exc
    if not isinstance(value, dict) or canonical_json_bytes(value) != raw:
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
