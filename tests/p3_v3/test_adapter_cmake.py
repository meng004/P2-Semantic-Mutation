import hashlib
import json
from pathlib import Path

import pytest

from p3_v3.adapters import cmake_ctest_v1
from p3_v3.bridge_and_frames import (
    SourceSnapshot,
    SourceSnapshotEntry,
    _declaration_is_structurally_valid,
)


_FIXTURE = Path(__file__).parent / "fixtures" / "adapter_trees" / "cmake_mini"
_E_COMMON_KINDS = {
    "JSON_SCHEMA_DRAFT2020_12_V1",
    "CLI_TOKEN_GRAMMAR_V1",
    "NUMERIC_ARRAY_DOMAIN_V1",
    "TEXT_IO_SCHEMA_V1",
    "BINARY_RECORD_SCHEMA_V1",
}


def _snapshot(root):
    entries = []
    for p in sorted(root.rglob("*")):
        if p.is_file():
            raw = p.read_bytes()
            entries.append(
                SourceSnapshotEntry(
                    relative_path=p.relative_to(root).as_posix(),
                    mode="100644",
                    sha256=hashlib.sha256(raw).hexdigest(),
                    content=raw,
                )
            )
    return SourceSnapshot(entries=tuple(entries))


def test_discovers_frozen_cmake_fixture_contract():
    result = cmake_ctest_v1.discover(_snapshot(_FIXTURE), {})

    assert set(result) == {
        "adapter_id",
        "ecosystem",
        "source_files",
        "declarations",
        "public_schemas",
        "sites",
    }
    assert result["adapter_id"] == "CMAKE_CTEST_V1"
    assert result["ecosystem"] == "cmake"

    by_category = {}
    for declaration in result["declarations"]:
        by_category.setdefault(declaration["category"], []).append(
            declaration["entrypoint"]
        )
        assert _declaration_is_structurally_valid(declaration) == (True, "")

    assert by_category == {
        "PROJECT_TEST": ["ctest:mini_smoke", "ctest:mini_named"],
        "CLI": ["target:mini_tool"],
        "EXAMPLE": ["target:mini_demo", "examples/demo.c"],
        "PUBLIC_API": ["include/mini/api.h"],
        "BENCHMARK": ["bench/perf.cu"],
    }
    assert {
        row["schema_kind"] for row in result["public_schemas"]
    } <= _E_COMMON_KINDS
    assert len(result["public_schemas"]) == 3

    assert [
        (site["path"], site["symbol"])
        for site in result["sites"]
    ] == [
        ("fortran/solver.f90", "fortran/solver.f90:mini_solve"),
        ("fortran/solver.f90", "fortran/solver.f90:mini_energy"),
        ("src/lib.c", "src/lib.c:mini_helper"),
        ("src/lib.c", "src/lib.c:mini_add"),
        ("src/lib.c", "src/lib.c:mini_scale"),
    ]
    assert "build/generated.c" not in result["source_files"]
    assert not any(
        site["path"].startswith("build/") for site in result["sites"]
    )


def test_discovery_is_deterministic():
    snapshot = _snapshot(_FIXTURE)

    first = cmake_ctest_v1.discover(snapshot, {})
    second = cmake_ctest_v1.discover(snapshot, {})

    assert json.dumps(first, sort_keys=True).encode() == json.dumps(
        second, sort_keys=True
    ).encode()


def test_missing_root_cmakelists_fails_closed():
    with pytest.raises(ValueError):
        cmake_ctest_v1.discover(SourceSnapshot(entries=()), {})


def test_non_utf8_root_cmakelists_fails_closed():
    raw = b"\xff"
    snapshot = SourceSnapshot(
        entries=(
            SourceSnapshotEntry(
                relative_path="CMakeLists.txt",
                mode="100644",
                sha256=hashlib.sha256(raw).hexdigest(),
                content=raw,
            ),
        )
    )

    with pytest.raises(ValueError):
        cmake_ctest_v1.discover(snapshot, {})
