"""Behavior tests for the real MESON_TEST_V1 discovery adapter."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from p3_v3.adapters import meson_test_v1
from p3_v3.bridge_and_frames import (
    SourceSnapshot,
    SourceSnapshotEntry,
    _declaration_is_structurally_valid,
)


_FIXTURES = Path(__file__).parent / "fixtures" / "adapter_trees"
_E_COMMON_KINDS = {
    "JSON_SCHEMA_DRAFT2020_12_V1",
    "CLI_TOKEN_GRAMMAR_V1",
    "NUMERIC_ARRAY_DOMAIN_V1",
    "TEXT_IO_SCHEMA_V1",
    "BINARY_RECORD_SCHEMA_V1",
}
_NORMATIVE_DOCSTRING = r"""- Fail-closed guard: root `meson.build` must exist; otherwise ValueError.
- Build-file set: every non-excluded `meson.build` and `*.meson` file,
  `#` comments stripped.
- `PROJECT_TEST`: `(?<![A-Za-z0-9_])test\s*\(\s*'([^']+)'` rows with
  `entrypoint=f"meson-test:{name}"`, argv `["meson", "test", name]`,
  schema `_cli_grammar_schema("meson")` and a `public_schemas` row.
  `(?<![A-Za-z0-9_])benchmark\s*\(\s*'([^']+)'` occurrences map to
  `BENCHMARK` with `entrypoint=f"meson-benchmark:{name}"`, argv
  `["meson", "test", "--benchmark", name]`, the same schema hash, and
  **no** `public_schemas` row (amendment 2026-08-13: benchmark row shape
  frozen as implemented).
- `CLI`/`EXAMPLE`/`BENCHMARK` targets:
  `(?<![A-Za-z0-9_])executable\s*\(\s*'([^']+)'` with `_path_category` of
  the declaring build file, else `CLI`; rows shaped as in the cmake rule
  (amendment 2026-08-13 round 2: the lookbehind literal was missing from
  this bullet while the code and the test/benchmark bullet carried it).
- Python-package branch: when root `pyproject.toml` exists with a
  non-empty `[project].name`, additionally apply — verbatim — the
  `PYTHON_PEP517_V1` module rules (package roots, public modules,
  `PUBLIC_API` declarations with signature-derived schemas,
  `[project.scripts]` CLI rows, path-evidenced `.py`
  EXAMPLE/BENCHMARK/PROJECT_TEST rows, python `sites`).
- In **both** branches the adapter additionally applies
  `_header_declarations`, `_c_family_sites`, and `_fortran_sites`
  (amendment 2026-08-13: the additive route is frozen — meson-python
  subjects like SciPy carry public C headers and compiled sources whose
  surface must not vanish because a pyproject exists). A
  `(category, provenance_path)` pair is emitted once; first writer wins.
- `source_files`: shared rule 2 (meson.build files themselves are not
  scale-countable and stay out)."""


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


def _assert_common_contract(result: dict) -> None:
    assert set(result) == {
        "adapter_id",
        "ecosystem",
        "source_files",
        "declarations",
        "public_schemas",
        "sites",
    }
    assert result["adapter_id"] == "MESON_TEST_V1"
    assert result["ecosystem"] == "meson"
    for declaration in result["declarations"]:
        assert _declaration_is_structurally_valid(declaration) == (True, "")
    assert {
        row["schema_kind"] for row in result["public_schemas"]
    } <= _E_COMMON_KINDS


def test_discovers_c_meson_tests_benchmarks_cli_headers_and_sites() -> None:
    result = meson_test_v1.discover(
        _snapshot(_FIXTURES / "meson_c_mini"), {}
    )

    _assert_common_contract(result)
    declarations = result["declarations"]
    assert [
        row["entrypoint"] for row in declarations if row["category"] == "PROJECT_TEST"
    ] == ["meson-test:t1"]
    assert [
        row["entrypoint"] for row in declarations if row["category"] == "BENCHMARK"
    ] == ["meson-benchmark:b1"]
    cli = [row for row in declarations if row["category"] == "CLI"]
    assert [(row["entrypoint"], row["declared_inputs"]) for row in cli] == [
        ("target:mtool", {"argv_tokens": ["mtool"]})
    ]
    assert [
        row["entrypoint"] for row in declarations if row["category"] == "PUBLIC_API"
    ] == ["include/m/m.h"]
    assert result["source_files"] == ["include/m/m.h", "src/m.c"]
    assert any(
        site["path"] == "src/m.c" and site["symbol"] == "src/m.c:m_add"
        for site in result["sites"]
    )
    assert not any(
        "phantom" in row["entrypoint"] for row in result["declarations"]
    )


def test_docstring_is_the_amended_normative_rule() -> None:
    assert meson_test_v1.__doc__ == _NORMATIVE_DOCSTRING


def test_public_schemas_are_deduplicated_by_provenance() -> None:
    raw = (
        b"project('same-line')\n"
        b"test('same', runner); executable('tool', 'tool.c')\n"
    )
    snapshot = SourceSnapshot(
        entries=(
            SourceSnapshotEntry(
                relative_path="meson.build",
                mode="100644",
                sha256=hashlib.sha256(raw).hexdigest(),
                content=raw,
            ),
        )
    )

    result = meson_test_v1.discover(snapshot, {})

    assert len(result["declarations"]) == 2
    assert len(result["public_schemas"]) == 1
    assert {
        (row["provenance_path"], row["provenance_span_or_key"])
        for row in result["public_schemas"]
    } == {("meson.build", "L2")}


def test_discovers_python_package_branch_and_meson_tests() -> None:
    result = meson_test_v1.discover(
        _snapshot(_FIXTURES / "meson_py_mini"), {}
    )

    _assert_common_contract(result)
    declarations = result["declarations"]
    public_api = next(
        row
        for row in declarations
        if row["category"] == "PUBLIC_API" and row["entrypoint"] == "mini:go"
    )
    assert public_api["declared_inputs"] == {
        "parameters": [{"name": "x", "annotation": "int"}]
    }
    assert any(
        row["schema_kind"] == "NUMERIC_ARRAY_DOMAIN_V1"
        and row["provenance_path"] == "src/mini/__init__.py"
        for row in result["public_schemas"]
    )
    assert any(
        row["category"] == "PROJECT_TEST"
        and row["entrypoint"] == "pytest tests/test_go.py"
        and row["declared_inputs"] == {"argv_tokens": ["pytest", "tests/test_go.py"]}
        for row in declarations
    )
    assert any(
        row["category"] == "PROJECT_TEST"
        and row["entrypoint"] == "meson-test:py-t1"
        for row in declarations
    )
    assert any(
        site["path"] == "src/mini/__init__.py"
        and site["symbol"] == "mini:go"
        for site in result["sites"]
    )


def test_requires_root_meson_build() -> None:
    with pytest.raises(ValueError, match="meson.build"):
        meson_test_v1.discover(SourceSnapshot(entries=()), {})


@pytest.mark.parametrize("fixture_name", ["meson_c_mini", "meson_py_mini"])
def test_discovery_is_deterministic(fixture_name: str) -> None:
    snapshot = _snapshot(_FIXTURES / fixture_name)

    first = meson_test_v1.discover(snapshot, {})
    second = meson_test_v1.discover(snapshot, {})

    assert json.dumps(first, sort_keys=True, separators=(",", ":")) == json.dumps(
        second, sort_keys=True, separators=(",", ":")
    )
