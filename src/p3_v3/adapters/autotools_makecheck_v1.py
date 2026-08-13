r"""AUTOTOOLS_MAKECHECK_V1 (subjects: BLIS ×2, PETSc ×2)

- Fail-closed guard: a root `configure` file must exist; otherwise
  ValueError.
- `PROJECT_TEST` (make targets): scan root makefiles in the frozen name
  order `GNUmakefile`, `makefile`, `Makefile`, plus `gmakefile` and
  `gmakefile.test` when present; a line matching `^(check|test)\s*:` (not
  `:=`) yields one row per distinct target name over all files:
  `entrypoint=f"make:{target}"`, provenance = the first file (in frozen
  order) declaring it with `provenance_span_or_key=f"L{lineno}"`, argv
  `["make", target]`, schema `_cli_grammar_schema("make")`.
- `PROJECT_TEST` (path evidence): files with suffix in `.c .cc .cpp .cxx
  .f .f90 .py` under any casefolded component in `{tests, testsuite}` →
  source-evidenced rows (shared rule 6 shape, category `PROJECT_TEST`).
- `EXAMPLE`/`BENCHMARK`: `_path_category` source-evidenced rows.
- `PUBLIC_API`: `_header_declarations`.
- `CLI`: no static rule (autotools target enumeration requires configure
  execution, which is forbidden) — zero-count, retained by the frame.
- `sites`: `_c_family_sites` + `_fortran_sites`.
- `source_files`: shared rule 2.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping
from typing import Any

# --- SHARED-ADAPTER-BLOCK-v1 begin ---
# Frozen shared discovery logic (plan 2026-08-13, normative rules 1-7).
# This block is inlined byte-identically in CMAKE_CTEST_V1, MESON_TEST_V1,
# and AUTOTOOLS_MAKECHECK_V1; a drift-guard test asserts equality.

_EXCLUDED_PARTS = {
    ".bzr", ".git", ".hg", ".svn", ".tox", ".venv", "_build", "__pycache__",
    "build", "cmakefiles", "debug", "dist", "env", "external", "fixture",
    "fixtures", "generated", "node_modules", "out", "release",
    "relwithdebinfo", "minsizerel", "site-packages", "target", "testdata",
    "third-party", "third_party", "vendor", "vendored", "vendors", "venv",
    ".ninja_deps", ".ninja_log", "build.ninja", "cmakecache.txt",
    "compile_commands.json",
}
_SCALE_SUFFIXES = (
    ".c", ".cc", ".cpp", ".cxx", ".h", ".hh", ".hpp", ".hxx", ".inl",
    ".cu", ".cuh", ".py", ".pyi", ".pyx", ".pxd", ".cmake",
    ".f", ".for", ".f77", ".f90", ".f95", ".f03", ".f08",
)
_C_FAMILY_SITE_SUFFIXES = (
    ".c", ".cc", ".cpp", ".cxx", ".cu", ".h", ".hh", ".hpp", ".hxx",
    ".inl", ".cuh",
)
_FORTRAN_SITE_SUFFIXES = (".f", ".for", ".f77", ".f90", ".f95", ".f03", ".f08")
_FORTRAN_FIXED_FORM_SUFFIXES = (".f", ".for", ".f77")
_HEADER_SUFFIXES = (".h", ".hh", ".hpp", ".hxx", ".inl", ".cuh")
_PATH_EVIDENCE_SUFFIXES = (".c", ".cc", ".cpp", ".cxx", ".cu", ".f", ".f90", ".py")
_C_KEYWORDS = {"if", "else", "for", "while", "switch", "return", "do"}


def _canonical_sha256(value):
    raw = (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        .encode("utf-8")
        + b"\n"
    )
    return hashlib.sha256(raw).hexdigest()


def _excluded(relative_path: str) -> bool:
    parts = [part.casefold() for part in relative_path.split("/")]
    return any(
        part in _EXCLUDED_PARTS
        or part.startswith("cmake-build-")
        or part.startswith("build-")
        for part in parts
    )


def _scale_source_files(entries) -> list[str]:
    selected = []
    for path in entries:
        if _excluded(path):
            continue
        name = path.rsplit("/", 1)[-1].casefold()
        suffix = "." + name.rsplit(".", 1)[-1] if "." in name else ""
        if name == "cmakelists.txt" or suffix in _SCALE_SUFFIXES:
            selected.append(path)
    return sorted(selected)


def _mask_c_comments_and_strings(text: str) -> str:
    masked = []
    index = 0
    state = "code"
    quote = ""
    length = len(text)
    while index < length:
        character = text[index]
        if state == "code":
            if text.startswith("//", index):
                state = "line_comment"
                masked.append("  ")
                index += 2
                continue
            if text.startswith("/*", index):
                state = "block_comment"
                masked.append("  ")
                index += 2
                continue
            if character in {'"', "'"}:
                state = "string"
                quote = character
                masked.append(character)
                index += 1
                continue
            masked.append(character)
            index += 1
            continue
        if character == "\n":
            masked.append("\n")
            if state == "line_comment":
                state = "code"
            index += 1
            continue
        if state == "line_comment":
            masked.append(" ")
            index += 1
            continue
        if state == "block_comment":
            if text.startswith("*/", index):
                state = "code"
                masked.append("  ")
                index += 2
                continue
            masked.append(" ")
            index += 1
            continue
        if state == "string":
            if character == "\\" and index + 1 < length:
                masked.append("  ")
                index += 2
                continue
            if character == quote:
                state = "code"
                masked.append(character)
                index += 1
                continue
            masked.append(" ")
            index += 1
            continue
    return "".join(masked)


_C_IDENTIFIER_BEFORE_PAREN = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)\s*$")


def _c_family_sites(path: str, text: str) -> list[dict]:
    masked = _mask_c_comments_and_strings(text)
    lines = masked.split("\n")
    sites: list[dict] = []
    depth = 0
    line_index = 0
    total = len(lines)
    while line_index < total:
        line = lines[line_index]
        if (
            depth == 0
            and line
            and not line[0].isspace()
            and line[0] not in {"#", "}", ";"}
        ):
            paren = line.find("(")
            if paren > 0:
                match = _C_IDENTIFIER_BEFORE_PAREN.search(line[:paren])
                if match is not None and match.group(1) not in _C_KEYWORDS:
                    closed = _scan_to_matching_paren(lines, line_index, paren)
                    if closed is not None:
                        close_line, close_col = closed
                        brace = _next_code_token(lines, close_line, close_col + 1)
                        if brace is not None and brace[2] == "{":
                            end = _scan_to_matching_brace(lines, brace[0], brace[1])
                            if end is not None:
                                end_line, end_col = end
                                sites.append(
                                    {
                                        "path": path,
                                        "symbol": f"{path}:{match.group(1)}",
                                        "start_line": line_index + 1,
                                        "start_col": match.start(1),
                                        "end_line": end_line + 1,
                                        "end_col": end_col + 1,
                                    }
                                )
                                depth = 0
                                line_index = end_line
                                line = lines[line_index]
                                depth -= line[: end_col + 1].count("{")
                                depth += line[: end_col + 1].count("}")
        depth += line.count("{") - line.count("}")
        line_index += 1
    return sites


def _scan_to_matching_paren(lines, line_index, col):
    depth = 0
    for row in range(line_index, len(lines)):
        line = lines[row]
        start = col if row == line_index else 0
        for position in range(start, len(line)):
            character = line[position]
            if character == "(":
                depth += 1
            elif character == ")":
                depth -= 1
                if depth == 0:
                    return row, position
    return None


def _next_code_token(lines, line_index, col):
    for row in range(line_index, len(lines)):
        line = lines[row]
        start = col if row == line_index else 0
        for position in range(start, len(line)):
            if not line[position].isspace():
                return row, position, line[position]
    return None


def _scan_to_matching_brace(lines, line_index, col):
    depth = 0
    for row in range(line_index, len(lines)):
        line = lines[row]
        start = col if row == line_index else 0
        for position in range(start, len(line)):
            character = line[position]
            if character == "{":
                depth += 1
            elif character == "}":
                depth -= 1
                if depth == 0:
                    return row, position
    return None


_FORTRAN_SUBROUTINE = re.compile(
    r"^\s*(?:(?:pure|impure|elemental|recursive|module)\s+)*"
    r"subroutine\s+([a-z][a-z0-9_]*)",
    re.IGNORECASE,
)
_FORTRAN_FUNCTION = re.compile(
    r"^\s*(?:(?:pure|impure|elemental|recursive|module)\s+)*"
    r"(?:(?:integer|real|logical|character|complex|double\s+precision"
    r"|type\s*\([^)]*\)|class\s*\([^)]*\))(?:\s*\(\s*[a-z0-9_=*]+\s*\))?\s+)?"
    r"function\s+([a-z][a-z0-9_]*)",
    re.IGNORECASE,
)
_FORTRAN_END = re.compile(
    r"^\s*end\s*(?:(?:subroutine|function)(?:\s+[a-z][a-z0-9_]*)?)?\s*$",
    re.IGNORECASE,
)


def _fortran_is_comment(line: str, fixed_form: bool) -> bool:
    stripped = line.lstrip()
    if not stripped or stripped.startswith("!"):
        return True
    return fixed_form and line[0] in {"c", "C", "*", "d", "D"}


def _fortran_sites(path: str, text: str) -> list[dict]:
    fixed_form = ("." + path.rsplit(".", 1)[-1]).casefold() in _FORTRAN_FIXED_FORM_SUFFIXES
    lines = text.split("\n")
    sites: list[dict] = []
    stack: list[tuple[str, int, int]] = []
    for index, line in enumerate(lines):
        if _fortran_is_comment(line, fixed_form):
            continue
        if _FORTRAN_END.match(line):
            if stack:
                name, start_line, start_col = stack.pop()
                if not stack:
                    sites.append(
                        {
                            "path": path,
                            "symbol": f"{path}:{name}",
                            "start_line": start_line,
                            "start_col": start_col,
                            "end_line": index + 1,
                            "end_col": len(line),
                        }
                    )
            continue
        match = _FORTRAN_SUBROUTINE.match(line) or _FORTRAN_FUNCTION.match(line)
        if match is not None:
            stack.append(
                (
                    match.group(1).casefold(),
                    index + 1,
                    len(line) - len(line.lstrip()),
                )
            )
    return sites


def _header_declarations(entries) -> list[dict]:
    declarations: list[dict] = []
    for path in sorted(entries):
        if _excluded(path):
            continue
        name = path.rsplit("/", 1)[-1]
        suffix = ("." + name.rsplit(".", 1)[-1]).casefold() if "." in name else ""
        parts = [part.casefold() for part in path.split("/")]
        if suffix in _HEADER_SUFFIXES and "include" in parts[:-1]:
            declarations.append(
                {
                    "category": "PUBLIC_API",
                    "entrypoint": path,
                    "normalized_entrypoint": f"header:{path}".casefold(),
                    "provenance_path": path,
                    "provenance_span_or_key": "path",
                    "declared_inputs": {"header": path},
                    "declared_input_schema_sha256": _canonical_sha256(
                        {"kind": "HEADER_SURFACE_V1", "path": path}
                    ),
                    "static_dependency_tags": [],
                    "prerequisites": [],
                }
            )
    return declarations


def _path_category(relative_path: str):
    parts = [part.casefold() for part in relative_path.split("/")[:-1]]
    if "examples" in parts:
        return "EXAMPLE"
    if "benchmarks" in parts or "bench" in parts:
        return "BENCHMARK"
    return None


def _source_evidenced_declaration(category: str, path: str) -> dict:
    return {
        "category": category,
        "entrypoint": path,
        "normalized_entrypoint": f"{category}:{path}".casefold(),
        "provenance_path": path,
        "provenance_span_or_key": "path",
        "declared_inputs": {"source_path": path},
        "declared_input_schema_sha256": _canonical_sha256(
            {"kind": "SOURCE_EVIDENCED_V1", "path": path}
        ),
        "static_dependency_tags": [],
        "prerequisites": [],
    }


def _cli_grammar_schema(program: str) -> dict:
    return {
        "kind": "CLI_TOKEN_GRAMMAR_V1",
        "program": program,
        "tokens": {"min": 0, "max": 3},
        "vocabulary": sorted({program, "--help", "--version"}),
    }
# --- SHARED-ADAPTER-BLOCK-v1 end ---


ADAPTER_ID = "AUTOTOOLS_MAKECHECK_V1"
ECOSYSTEM = "autotools"
_MAKEFILE_NAMES = (
    "GNUmakefile",
    "makefile",
    "Makefile",
    "gmakefile",
    "gmakefile.test",
)
_MAKE_TARGET = re.compile(r"^(check|test)\s*:(?!=)")


def discover(source_snapshot, build_descriptor: Mapping[str, Any]) -> dict[str, Any]:
    entries = {
        entry.relative_path: entry.content for entry in source_snapshot.entries
    }
    if "configure" not in entries:
        raise ValueError("root configure is absent")

    declarations: list[dict] = []
    public_schemas: list[dict] = []
    seen_targets: set[str] = set()
    make_schema = _cli_grammar_schema("make")
    for path in _MAKEFILE_NAMES:
        raw = entries.get(path)
        if raw is None:
            continue
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ValueError(f"root makefile is not valid UTF-8: {path}") from exc
        for lineno, line in enumerate(text.splitlines(), start=1):
            match = _MAKE_TARGET.match(line)
            if match is None:
                continue
            target = match.group(1)
            if target in seen_targets:
                continue
            seen_targets.add(target)
            span = f"L{lineno}"
            declarations.append(
                {
                    "category": "PROJECT_TEST",
                    "entrypoint": f"make:{target}",
                    "normalized_entrypoint": f"make:{target}".casefold(),
                    "provenance_path": path,
                    "provenance_span_or_key": span,
                    "declared_inputs": {"argv_tokens": ["make", target]},
                    "declared_input_schema_sha256": _canonical_sha256(make_schema),
                    "static_dependency_tags": [],
                    "prerequisites": [],
                }
            )
            public_schemas.append(
                {
                    "schema_kind": "CLI_TOKEN_GRAMMAR_V1",
                    "raw_schema": make_schema,
                    "provenance_path": path,
                    "provenance_span_or_key": span,
                }
            )

    declarations.extend(_header_declarations(entries))

    evidence_seen: set[tuple[str, str]] = set()
    evidence_paths = []
    for path in sorted(entries):
        if _excluded(path):
            continue
        name = path.rsplit("/", 1)[-1]
        suffix = ("." + name.rsplit(".", 1)[-1]).casefold() if "." in name else ""
        if suffix in _PATH_EVIDENCE_SUFFIXES:
            evidence_paths.append(path)

    for path in evidence_paths:
        parts = {part.casefold() for part in path.split("/")[:-1]}
        pair = ("PROJECT_TEST", path)
        if parts & {"tests", "testsuite"} and pair not in evidence_seen:
            declarations.append(_source_evidenced_declaration(*pair))
            evidence_seen.add(pair)

    for path in evidence_paths:
        category = _path_category(path)
        if category is None:
            continue
        pair = (category, path)
        if pair not in evidence_seen:
            declarations.append(_source_evidenced_declaration(*pair))
            evidence_seen.add(pair)

    sites: list[dict] = []
    for path in sorted(entries):
        if _excluded(path):
            continue
        name = path.rsplit("/", 1)[-1]
        suffix = ("." + name.rsplit(".", 1)[-1]).casefold() if "." in name else ""
        if suffix not in _C_FAMILY_SITE_SUFFIXES + _FORTRAN_SITE_SUFFIXES:
            continue
        try:
            text = entries[path].decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ValueError(f"source file is not valid UTF-8: {path}") from exc
        if suffix in _C_FAMILY_SITE_SUFFIXES:
            sites.extend(_c_family_sites(path, text))
        else:
            sites.extend(_fortran_sites(path, text))

    return {
        "adapter_id": ADAPTER_ID,
        "ecosystem": ECOSYSTEM,
        "source_files": _scale_source_files(entries),
        "declarations": declarations,
        "public_schemas": public_schemas,
        "sites": sites,
    }
