from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from p3_v3.adapters import autotools_makecheck_v1
from p3_v3.bridge_and_frames import (
    SourceSnapshot,
    SourceSnapshotEntry,
    _declaration_is_structurally_valid,
)


FIXTURE_ROOT = (
    Path(__file__).parent / "fixtures" / "adapter_trees" / "autotools_mini"
)
E_COMMON_KINDS = {
    "JSON_SCHEMA_DRAFT2020_12_V1",
    "CLI_TOKEN_GRAMMAR_V1",
    "NUMERIC_ARRAY_DOMAIN_V1",
    "TEXT_IO_SCHEMA_V1",
    "BINARY_RECORD_SCHEMA_V1",
}


def _snapshot(root: Path) -> SourceSnapshot:
    entries = []
    for path in sorted(root.rglob("*")):
        if path.is_file():
            raw = path.read_bytes()
            entries.append(
                SourceSnapshotEntry(
                    relative_path=path.relative_to(root).as_posix(),
                    mode="100644",
                    sha256=hashlib.sha256(raw).hexdigest(),
                    content=raw,
                )
            )
    return SourceSnapshot(entries=tuple(entries))


def _canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def test_discovers_frozen_autotools_surface() -> None:
    result = autotools_makecheck_v1.discover(_snapshot(FIXTURE_ROOT), {})

    assert set(result) == {
        "adapter_id",
        "ecosystem",
        "source_files",
        "declarations",
        "public_schemas",
        "sites",
    }
    assert result["adapter_id"] == "AUTOTOOLS_MAKECHECK_V1"
    assert result["ecosystem"] == "autotools"
    assert result["source_files"] == [
        "examples/e.f",
        "include/a/a.h",
        "src/a.c",
        "testsuite/t_a.c",
    ]

    declarations = result["declarations"]
    assert [
        (
            row["category"],
            row["entrypoint"],
            row["provenance_path"],
            row["provenance_span_or_key"],
        )
        for row in declarations
    ] == [
        ("PROJECT_TEST", "make:check", "Makefile", "L1"),
        ("PROJECT_TEST", "make:test", "Makefile", "L4"),
        ("PUBLIC_API", "include/a/a.h", "include/a/a.h", "path"),
        ("PROJECT_TEST", "testsuite/t_a.c", "testsuite/t_a.c", "path"),
        ("EXAMPLE", "examples/e.f", "examples/e.f", "path"),
    ]
    assert len(
        [row for row in declarations if row["entrypoint"].startswith("make:")]
    ) == 2
    assert [row for row in declarations if row["category"] == "CLI"] == []
    assert declarations[0]["declared_inputs"] == {"argv_tokens": ["make", "check"]}
    assert declarations[1]["declared_inputs"] == {"argv_tokens": ["make", "test"]}
    assert all(_declaration_is_structurally_valid(row) == (True, "") for row in declarations)

    assert len(result["public_schemas"]) == 2
    assert {row["schema_kind"] for row in result["public_schemas"]} <= E_COMMON_KINDS
    assert [
        (row["provenance_path"], row["provenance_span_or_key"])
        for row in result["public_schemas"]
    ] == [("Makefile", "L1"), ("Makefile", "L4")]
    assert all(
        row["schema_kind"] == "CLI_TOKEN_GRAMMAR_V1"
        and row["raw_schema"]
        == {
            "kind": "CLI_TOKEN_GRAMMAR_V1",
            "program": "make",
            "tokens": {"min": 0, "max": 3},
            "vocabulary": ["--help", "--version", "make"],
        }
        for row in result["public_schemas"]
    )

    sites_by_path = {}
    for site in result["sites"]:
        sites_by_path.setdefault(site["path"], []).append(site)
    assert set(sites_by_path) == {"examples/e.f", "src/a.c", "testsuite/t_a.c"}
    assert [site["symbol"] for site in sites_by_path["src/a.c"]] == ["src/a.c:add"]
    assert [site["symbol"] for site in sites_by_path["testsuite/t_a.c"]] == [
        "testsuite/t_a.c:test_add"
    ]
    assert sites_by_path["examples/e.f"] == [
        {
            "path": "examples/e.f",
            "symbol": "examples/e.f:example",
            "start_line": 2,
            "start_col": 6,
            "end_line": 3,
            "end_col": 28,
        }
    ]


def test_discovery_is_deterministic() -> None:
    snapshot = _snapshot(FIXTURE_ROOT)

    first = autotools_makecheck_v1.discover(snapshot, {})
    second = autotools_makecheck_v1.discover(snapshot, {})

    assert _canonical_json(first) == _canonical_json(second)


def test_fails_closed_without_root_configure(tmp_path: Path) -> None:
    (tmp_path / "Makefile").write_text("check:\n", encoding="utf-8")

    with pytest.raises(ValueError, match="configure"):
        autotools_makecheck_v1.discover(_snapshot(tmp_path), {})


def test_fails_closed_on_non_utf8_root_makefile(tmp_path: Path) -> None:
    (tmp_path / "configure").write_text("#!/bin/sh\n", encoding="utf-8")
    (tmp_path / "Makefile").write_bytes(b"check:\n\xff")

    with pytest.raises(ValueError, match="Makefile"):
        autotools_makecheck_v1.discover(_snapshot(tmp_path), {})
