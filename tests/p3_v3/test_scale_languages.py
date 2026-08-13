from __future__ import annotations

import hashlib
import random

import pytest

from p3_v3.artifacts import EvidenceError, canonical_json_bytes, canonical_sha256
from p3_v3.bridge_and_frames import (
    SourceSnapshot,
    SourceSnapshotEntry,
    _effective_line_count,
    derive_source_scale,
)


def _snapshot(shuffled_files: list[tuple[str, bytes]]) -> SourceSnapshot:
    entries = [
        SourceSnapshotEntry(
            relative_path=relative_path,
            mode="100644",
            sha256=hashlib.sha256(content).hexdigest(),
            content=content,
        )
        for relative_path, content in shuffled_files
    ]
    entries.sort(key=lambda entry: entry.relative_path.encode("utf-8"))
    return SourceSnapshot(entries=tuple(entries))


def _discovery(source_files: list[str]) -> dict:
    body = {
        "schema_version": "p3-adapter-discovery-v1",
        "adapter_id": "PYTHON_PEP517_V1",
        "ecosystem": "python",
        "discovery_status": "EXECUTABLE",
        "implementation_source_sha256": "31" * 32,
        "source_files": sorted(source_files),
        "declarations": [],
        "public_schemas": [],
        "sites": [],
        "unsupported_or_exclusion_reason": "",
    }
    return {**body, "artifact_sha256": canonical_sha256(body)}


def test_free_form_fortran_counts_code_not_comment_or_blank() -> None:
    raw = b"x = 1\n! comment\n\n"

    assert _effective_line_count("src/solver.f90", raw) == 1


def test_fixed_form_fortran_ignores_column_one_comment() -> None:
    raw = b"C comment\n      x = 1\n"

    assert _effective_line_count("src/solver.f", raw) == 1


def test_cuda_uses_cpp_line_comment_rule() -> None:
    raw = b"// comment\n__global__ void kernel() {}\n"

    assert _effective_line_count("src/kernel.cu", raw) == 1


def test_unsupported_julia_still_raises_scale_source_language() -> None:
    with pytest.raises(EvidenceError, match="E_SCALE_SOURCE_LANGUAGE"):
        _effective_line_count("src/solver.jl", b"x = 1\n")


def test_source_scale_is_byte_identical_on_rerun_with_shuffled_files() -> None:
    files = [
        ("src/solver.f90", b"! comment\nx = 1\n"),
        ("src/legacy.f", b"C comment\n      y = 2\n"),
        ("src/kernel.cu", b"// comment\n__global__ void kernel() {}\n"),
    ]
    random.Random(20260813).shuffle(files)
    snapshot = _snapshot(files)
    discovery = _discovery([relative_path for relative_path, _content in files])

    first = derive_source_scale(snapshot, discovery)
    second = derive_source_scale(snapshot, discovery)

    assert canonical_json_bytes(first) == canonical_json_bytes(second)
