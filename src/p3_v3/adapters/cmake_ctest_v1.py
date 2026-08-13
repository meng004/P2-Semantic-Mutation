r"""- Fail-closed guard: root `CMakeLists.txt` must exist and decode as UTF-8
  (with `errors="replace"` forbidden); otherwise `raise ValueError`.
- Build-file set: every non-excluded `CMakeLists.txt` and `*.cmake` file.
  Parse textually after stripping `#` line comments and cmake bracket
  comments `#[[ … ]]`.
- `PROJECT_TEST`: every `add_test(...)` occurrence. Grammar:
  `(?<![A-Za-z0-9_])add_test\s*\(\s*(?:NAME\s+)?([\"']?)([A-Za-z0-9_.:+/-]+)\1`
  (second group = test name; the lookbehind rejects wrapper macros such
  as `sundials_add_test`). Row: `entrypoint=f"ctest:{name}"`,
  `normalized_entrypoint` = its casefold, `provenance_path` = the build
  file, `provenance_span_or_key=f"L{lineno}"`, `declared_inputs=
  {"argv_tokens": ["ctest", "-R", f"^{name}$"]}`, schema =
  `_cli_grammar_schema("ctest")` (one shared `public_schemas` row per
  distinct provenance file+span — duplicate spans are emitted once),
  tags `[]`.
- `CLI` / `EXAMPLE` / `BENCHMARK`: every `(?<![A-Za-z0-9_])
  add_executable\s*\(\s*([\"']?)([A-Za-z0-9_.+-]+)\1` occurrence whose
  second group does not start with `${` and whose parenthesized argument
  group does not contain the standalone case-sensitive uppercase token
  `IMPORTED` or `ALIAS` (`\b(?:IMPORTED|ALIAS)\b` without IGNORECASE;
  lower-case file names such as `alias.c` never suppress). Category =
  `_path_category` of the declaring build file, else `CLI`. Row:
  `entrypoint=f"target:{name}"`, argv `[name]`, schema
  `_cli_grammar_schema(name)` with a `public_schemas` row for `CLI` rows
  only (deduplicated by provenance file+span like the test rows).
- `PUBLIC_API`: `_header_declarations`.
- `sites`: `_c_family_sites` over non-excluded `.c .cc .cpp .cxx .cu .h
  .hh .hpp .hxx .inl .cuh` files plus `_fortran_sites` over Fortran
  suffixes.
- `source_files`: shared rule 2."""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping
from typing import Any

# --- SHARED-ADAPTER-BLOCK-v1 begin ---
# Frozen shared discovery logic (plan 2026-08-13, normative rules 1-8).
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


def _utf8_text_or_none(raw):
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return None


def _scale_source_files(entries) -> list[str]:
    selected = []
    for path in entries:
        if _excluded(path):
            continue
        name = path.rsplit("/", 1)[-1].casefold()
        suffix = "." + name.rsplit(".", 1)[-1] if "." in name else ""
        if (
            (name == "cmakelists.txt" or suffix in _SCALE_SUFFIXES)
            and _utf8_text_or_none(entries[path]) is not None
        ):
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
                masked.append(" ")
                masked.append("\n" if text[index + 1] == "\n" else " ")
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
_C_TRANSPARENT_NAMESPACE = re.compile(
    r"^\s*(?:inline\s+)?namespace"
    r"(?:\s+[A-Za-z_][A-Za-z0-9_:]*)?\s*$"
)
_C_TRANSPARENT_EXTERN = re.compile(r'^\s*extern\s*"C(?:\+\+)?"\s*$')


def _c_brace_is_transparent(masked_line, source_line, col):
    return (
        _C_TRANSPARENT_NAMESPACE.match(masked_line[:col]) is not None
        or _C_TRANSPARENT_EXTERN.match(source_line[:col]) is not None
    )


def _c_family_sites(path: str, text: str) -> list[dict]:
    masked = _mask_c_comments_and_strings(text)
    lines = masked.split("\n")
    source_lines = text.split("\n")
    sites: list[dict] = []
    brace_stack: list[bool] = []
    for line_index, line in enumerate(lines):
        source_line = source_lines[line_index]
        first_non_whitespace = next(
            (index for index, character in enumerate(line) if not character.isspace()),
            None,
        )
        if (
            not any(not transparent for transparent in brace_stack)
            and first_non_whitespace is not None
            and line[first_non_whitespace] not in {"#", "}", ";"}
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
        for col, character in enumerate(line):
            if character == "{":
                brace_stack.append(
                    _c_brace_is_transparent(line, source_line, col)
                )
            elif character == "}" and brace_stack:
                brace_stack.pop()
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
        code_line = line.split("!", 1)[0]
        if _FORTRAN_END.match(code_line):
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
        match = (
            _FORTRAN_SUBROUTINE.match(code_line)
            or _FORTRAN_FUNCTION.match(code_line)
        )
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


ADAPTER_ID = "CMAKE_CTEST_V1"
ECOSYSTEM = "cmake"
_ADD_TEST = re.compile(
    r"""(?<![A-Za-z0-9_])add_test\s*\(\s*(?:NAME\s+)?(["']?)([A-Za-z0-9_.:+/-]+)\1"""
)
_ADD_EXECUTABLE = re.compile(
    r"""(?<![A-Za-z0-9_])add_executable\s*\(\s*(["']?)([A-Za-z0-9_.+-]+)\1"""
)
_EXCLUDED_EXECUTABLE_KIND = re.compile(r"\b(?:IMPORTED|ALIAS)\b")
_BRACKET_COMMENT = re.compile(r"#\[\[.*?\]\]", re.DOTALL)
_LINE_COMMENT = re.compile(r"#[^\n]*")


def _mask_comment(match: re.Match[str]) -> str:
    return "".join("\n" if character == "\n" else " " for character in match.group())


def _strip_cmake_comments(text: str) -> str:
    without_brackets = _BRACKET_COMMENT.sub(_mask_comment, text)
    return _LINE_COMMENT.sub(_mask_comment, without_brackets)


def _decode(entries: dict[str, bytes], path: str) -> str:
    try:
        return entries[path].decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(f"CMake adapter input is not UTF-8: {path}") from exc


def _suffix(path: str) -> str:
    name = path.rsplit("/", 1)[-1]
    return ("." + name.rsplit(".", 1)[-1]).casefold() if "." in name else ""


def _cmake_build_files(entries: dict[str, bytes]) -> list[str]:
    return sorted(
        path
        for path in entries
        if not _excluded(path)
        and (
            path.rsplit("/", 1)[-1].casefold() == "cmakelists.txt"
            or _suffix(path) == ".cmake"
        )
    )


def _parenthesized_group(text: str, start: int) -> str:
    open_paren = text.find("(", start)
    if open_paren < 0:
        raise ValueError("matched CMake command has no opening parenthesis")
    depth = 0
    quote = ""
    escaped = False
    for index in range(open_paren, len(text)):
        character = text[index]
        if quote:
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == quote:
                quote = ""
            continue
        if character in {'"', "'"}:
            quote = character
        elif character == "(":
            depth += 1
        elif character == ")":
            depth -= 1
            if depth == 0:
                return text[open_paren : index + 1]
    raise ValueError("matched CMake command has an unclosed parenthesis")


def _build_declaration(
    category: str,
    path: str,
    line: int,
    entrypoint: str,
    argv: list[str],
    raw_schema: dict,
) -> dict:
    return {
        "category": category,
        "entrypoint": entrypoint,
        "normalized_entrypoint": entrypoint.casefold(),
        "provenance_path": path,
        "provenance_span_or_key": f"L{line}",
        "declared_inputs": {"argv_tokens": argv},
        "declared_input_schema_sha256": _canonical_sha256(raw_schema),
        "static_dependency_tags": [],
        "prerequisites": [],
    }


def _public_schema(path: str, line: int, raw_schema: dict) -> dict:
    return {
        "schema_kind": "CLI_TOKEN_GRAMMAR_V1",
        "raw_schema": raw_schema,
        "provenance_path": path,
        "provenance_span_or_key": f"L{line}",
    }


def discover(source_snapshot, build_descriptor: Mapping[str, Any]) -> dict[str, Any]:
    entries = {
        entry.relative_path: entry.content for entry in source_snapshot.entries
    }
    if "CMakeLists.txt" not in entries:
        raise ValueError("CMakeLists.txt is absent")
    _decode(entries, "CMakeLists.txt")

    declarations: list[dict] = []
    public_schemas: list[dict] = []
    public_schema_keys: set[tuple[str, str]] = set()

    def append_public_schema(path: str, line: int, raw_schema: dict) -> None:
        key = (path, f"L{line}")
        if key not in public_schema_keys:
            public_schema_keys.add(key)
            public_schemas.append(_public_schema(path, line, raw_schema))

    for path in _cmake_build_files(entries):
        text = _strip_cmake_comments(_decode(entries, path))
        events = [
            *(("test", match) for match in _ADD_TEST.finditer(text)),
            *(("executable", match) for match in _ADD_EXECUTABLE.finditer(text)),
        ]
        for kind, match in sorted(events, key=lambda event: event[1].start()):
            line = text.count("\n", 0, match.start()) + 1
            name = match.group(2)
            if kind == "test":
                raw_schema = _cli_grammar_schema("ctest")
                declarations.append(
                    _build_declaration(
                        "PROJECT_TEST",
                        path,
                        line,
                        f"ctest:{name}",
                        ["ctest", "-R", f"^{name}$"],
                        raw_schema,
                    )
                )
                append_public_schema(path, line, raw_schema)
                continue

            if name.startswith("${"):
                continue
            group = _parenthesized_group(text, match.start())
            if _EXCLUDED_EXECUTABLE_KIND.search(group):
                continue
            category = _path_category(path) or "CLI"
            raw_schema = _cli_grammar_schema(name)
            declarations.append(
                _build_declaration(
                    category,
                    path,
                    line,
                    f"target:{name}",
                    [name],
                    raw_schema,
                )
            )
            if category == "CLI":
                append_public_schema(path, line, raw_schema)

    declarations.extend(_header_declarations(entries))
    for path in sorted(entries):
        if _excluded(path) or _suffix(path) not in _PATH_EVIDENCE_SUFFIXES:
            continue
        category = _path_category(path)
        if category is not None:
            declarations.append(_source_evidenced_declaration(category, path))

    sites: list[dict] = []
    for path in sorted(entries):
        if _excluded(path):
            continue
        suffix = _suffix(path)
        if suffix in _C_FAMILY_SITE_SUFFIXES:
            text = _utf8_text_or_none(entries[path])
            if text is not None:
                sites.extend(_c_family_sites(path, text))
        elif suffix in _FORTRAN_SITE_SUFFIXES:
            text = _utf8_text_or_none(entries[path])
            if text is not None:
                sites.extend(_fortran_sites(path, text))

    return {
        "adapter_id": ADAPTER_ID,
        "ecosystem": ECOSYSTEM,
        "source_files": _scale_source_files(entries),
        "declarations": declarations,
        "public_schemas": public_schemas,
        "sites": sites,
    }
