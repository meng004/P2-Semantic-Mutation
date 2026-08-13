r"""MESON_TEST_V1 (subject: B-POCKETFFT-004 — a meson-python SciPy tree)

- Fail-closed guard: root `meson.build` must exist; otherwise ValueError.
- Build-file set: every non-excluded `meson.build` and `*.meson` file,
  `#` comments stripped.
- `PROJECT_TEST`: `test\s*\(\s*'([^']+)'` and
  `benchmark\s*\(\s*'([^']+)'` (benchmark occurrences map to `BENCHMARK`).
  Rows like the cmake test rule with `entrypoint=f"meson-test:{name}"`, argv
  `["meson", "test", name]`, schema `_cli_grammar_schema("meson")`.
- `CLI`/`EXAMPLE`/`BENCHMARK` targets: `executable\s*\(\s*'([^']+)'` with
  `_path_category` of the declaring build file, else `CLI`; rows shaped as
  in the cmake rule.
- Python-package branch: when root `pyproject.toml` exists with a
  non-empty `[project].name`, additionally apply — verbatim — the
  `PYTHON_PEP517_V1` module rules (package roots, public modules,
  `PUBLIC_API` declarations with signature-derived schemas,
  `[project.scripts]` CLI rows, path-evidenced `.py`
  `EXAMPLE`/`BENCHMARK`/`PROJECT_TEST` rows, python `sites`). When it does not
  exist, apply `_header_declarations` + `_c_family_sites` as in cmake.
- `source_files`: shared rule 2 (meson.build files themselves are not
  scale-countable and stay out).
"""

from __future__ import annotations

import ast
import hashlib
import json
import re
import tomllib
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

ADAPTER_ID = "MESON_TEST_V1"
ECOSYSTEM = "meson"
_NUMERIC_ANNOTATIONS = {"int", "float", "complex"}
_TEXT_ANNOTATIONS = {"str"}
_BINARY_ANNOTATIONS = {"bytes", "bytearray", "memoryview"}
_JSON_TYPE_BY_ANNOTATION = {
    "int": "integer",
    "float": "number",
    "complex": "number",
    "str": "string",
    "bool": "boolean",
    "list": "array",
    "tuple": "array",
    "sequence": "array",
    "set": "array",
    "frozenset": "array",
    "dict": "object",
    "mapping": "object",
}
_JSON_ANY = ["array", "boolean", "integer", "null", "number", "object", "string"]
_MESON_TEST = re.compile(r"test\s*\(\s*'([^']+)'")
_MESON_BENCHMARK = re.compile(r"benchmark\s*\(\s*'([^']+)'")
_MESON_EXECUTABLE = re.compile(r"executable\s*\(\s*'([^']+)'")


def _normalized_annotation(node: ast.AST | None) -> str:
    if node is None:
        return ""
    text = ast.unparse(node).strip().casefold()
    return text.split("[", 1)[0].strip()


def _signature_parameters(node: ast.AST, *, drop_first: bool) -> tuple[list[dict], bool]:
    arguments = node.args
    collected = [*arguments.posonlyargs, *arguments.args, *arguments.kwonlyargs]
    if drop_first and collected:
        collected = collected[1:]
    parameters = [
        {"name": item.arg, "annotation": _normalized_annotation(item.annotation)}
        for item in collected
    ]
    has_variadic = arguments.vararg is not None or arguments.kwarg is not None
    return parameters, has_variadic


def _input_schema(parameters: list[dict], has_variadic: bool) -> tuple[str | None, dict]:
    if not parameters and not has_variadic:
        return None, {"kind": "NO_INPUT"}
    annotations = {item["annotation"] for item in parameters}
    names = [item["name"] for item in parameters]
    if not has_variadic and annotations and annotations <= _NUMERIC_ANNOTATIONS:
        dtype = "int64" if annotations <= {"int"} else "float64"
        return "NUMERIC_ARRAY_DOMAIN_V1", {
            "kind": "NUMERIC_ARRAY_DOMAIN_V1",
            "parameters": names,
            "element_count": len(names),
            "dtype": dtype,
            "minimum": -1000000,
            "maximum": 1000000,
        }
    if not has_variadic and annotations and annotations <= _TEXT_ANNOTATIONS:
        return "TEXT_IO_SCHEMA_V1", {
            "kind": "TEXT_IO_SCHEMA_V1",
            "fields": names,
            "max_length": 256,
            "charset": "printable_ascii",
        }
    if not has_variadic and annotations and annotations <= _BINARY_ANNOTATIONS:
        return "BINARY_RECORD_SCHEMA_V1", {
            "kind": "BINARY_RECORD_SCHEMA_V1",
            "fields": names,
            "record_bytes": 32,
        }
    properties = {
        item["name"]: {
            "type": _JSON_TYPE_BY_ANNOTATION.get(item["annotation"], _JSON_ANY)
        }
        for item in parameters
    }
    return "JSON_SCHEMA_DRAFT2020_12_V1", {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "kind": "JSON_SCHEMA_DRAFT2020_12_V1",
        "type": "object",
        "properties": properties,
        "required": sorted(properties),
        "additionalProperties": False,
    }


def _module_all(tree: ast.Module) -> list[str] | None:
    for node in tree.body:
        if isinstance(node, ast.Assign):
            targets = [
                target.id
                for target in node.targets
                if isinstance(target, ast.Name)
            ]
            if "__all__" in targets and isinstance(node.value, (ast.List, ast.Tuple)):
                names = []
                for element in node.value.elts:
                    if not (
                        isinstance(element, ast.Constant)
                        and isinstance(element.value, str)
                    ):
                        return None
                    names.append(element.value)
                return names
    return None


def _module_import_tags(tree: ast.Module) -> list[str]:
    tags: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                tags.add(alias.name.split(".", 1)[0])
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            tags.add(node.module.split(".", 1)[0])
    return sorted(tags)


def _collect_sites(path: str, dotted_module: str, tree: ast.Module) -> list[dict]:
    sites: list[dict] = []

    def visit(node: ast.AST, stack: tuple[str, ...]) -> None:
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                qualname = ".".join((*stack, child.name))
                sites.append(
                    {
                        "path": path,
                        "symbol": f"{dotted_module}:{qualname}",
                        "start_line": child.lineno,
                        "start_col": child.col_offset,
                        "end_line": child.end_lineno,
                        "end_col": child.end_col_offset,
                    }
                )
                visit(child, (*stack, child.name))
            elif isinstance(child, ast.ClassDef):
                visit(child, (*stack, child.name))

    visit(tree, ())
    return sites


def _argv_declaration(
    category: str,
    path: str,
    entrypoint: str,
    normalized: str,
    argv: list[str],
) -> dict:
    schema = {"kind": "ARGV_FIXED", "argv": argv}
    return {
        "category": category,
        "entrypoint": entrypoint,
        "normalized_entrypoint": normalized,
        "provenance_path": path,
        "provenance_span_or_key": "path",
        "declared_inputs": {"argv_tokens": argv},
        "declared_input_schema_sha256": _canonical_sha256(schema),
        "static_dependency_tags": [],
        "prerequisites": [],
    }


def _strip_meson_comments(text: str) -> str:
    masked: list[str] = []
    quote = ""
    escaped = False
    in_comment = False
    for character in text:
        if character == "\n":
            masked.append("\n")
            in_comment = False
            escaped = False
            continue
        if in_comment:
            masked.append(" ")
            continue
        if quote:
            masked.append(character)
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == quote:
                quote = ""
            continue
        if character in {"'", '"'}:
            quote = character
            masked.append(character)
        elif character == "#":
            in_comment = True
            masked.append(" ")
        else:
            masked.append(character)
    return "".join(masked)


def _line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def _meson_declaration(
    category: str,
    path: str,
    span: str,
    entrypoint: str,
    normalized: str,
    argv: list[str],
    schema: dict,
) -> dict:
    return {
        "category": category,
        "entrypoint": entrypoint,
        "normalized_entrypoint": normalized,
        "provenance_path": path,
        "provenance_span_or_key": span,
        "declared_inputs": {"argv_tokens": argv},
        "declared_input_schema_sha256": _canonical_sha256(schema),
        "static_dependency_tags": [],
        "prerequisites": [],
    }


def _apply_python_branch(
    entries: dict[str, bytes],
    project: dict,
    declarations: list[dict],
    public_schemas: list[dict],
    sites: list[dict],
    seen_path_evidence: set[tuple[str, str]],
) -> None:
    python_paths = [
        path for path in entries if path.endswith(".py") and not _excluded(path)
    ]
    src_roots = sorted(
        {
            path.split("/")[1]
            for path in python_paths
            if path.startswith("src/")
            and len(path.split("/")) == 3
            and path.split("/")[2] == "__init__.py"
        }
    )
    if src_roots:
        package_roots = [f"src/{name}" for name in src_roots]
    else:
        package_roots = sorted(
            {
                path.split("/")[0]
                for path in python_paths
                if len(path.split("/")) == 2 and path.split("/")[1] == "__init__.py"
            }
        )

    for root in package_roots:
        prefix = f"{root}/"
        top = root.split("/")[-1]
        for path in sorted(path for path in python_paths if path.startswith(prefix)):
            relative_parts = path[len(prefix):].split("/")
            if any(
                part.startswith("_") and part != "__init__.py"
                for part in relative_parts
            ):
                continue
            module_parts = [top, *relative_parts]
            if module_parts[-1] == "__init__.py":
                module_parts = module_parts[:-1]
            else:
                module_parts[-1] = module_parts[-1][: -len(".py")]
            dotted_module = ".".join(module_parts)
            try:
                tree = ast.parse(entries[path].decode("utf-8"))
            except (UnicodeDecodeError, SyntaxError) as exc:
                raise ValueError(f"public module is unparseable: {path}") from exc
            exported = _module_all(tree)
            tags = _module_import_tags(tree)
            sites.extend(_collect_sites(path, dotted_module, tree))
            for node in tree.body:
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    name = node.name
                    parameters, has_variadic = _signature_parameters(
                        node, drop_first=False
                    )
                elif isinstance(node, ast.ClassDef):
                    name = node.name
                    initializer = next(
                        (
                            child
                            for child in node.body
                            if isinstance(
                                child, (ast.FunctionDef, ast.AsyncFunctionDef)
                            )
                            and child.name == "__init__"
                        ),
                        None,
                    )
                    if initializer is None:
                        parameters, has_variadic = [], False
                    else:
                        parameters, has_variadic = _signature_parameters(
                            initializer, drop_first=True
                        )
                else:
                    continue
                if name.startswith("_"):
                    continue
                if exported is not None and name not in exported:
                    continue
                span = f"L{node.lineno}-L{node.end_lineno}"
                schema_kind, raw_schema = _input_schema(parameters, has_variadic)
                declarations.append(
                    {
                        "category": "PUBLIC_API",
                        "entrypoint": f"{dotted_module}:{name}",
                        "normalized_entrypoint": f"{dotted_module}:{name}".casefold(),
                        "provenance_path": path,
                        "provenance_span_or_key": span,
                        "declared_inputs": {"parameters": parameters},
                        "declared_input_schema_sha256": _canonical_sha256(raw_schema),
                        "static_dependency_tags": tags,
                        "prerequisites": [],
                    }
                )
                if schema_kind is not None:
                    public_schemas.append(
                        {
                            "schema_kind": schema_kind,
                            "raw_schema": raw_schema,
                            "provenance_path": path,
                            "provenance_span_or_key": span,
                        }
                    )

    scripts = project.get("scripts")
    if isinstance(scripts, dict):
        for name in sorted(scripts):
            target = scripts[name]
            if not isinstance(target, str) or not name:
                raise ValueError("pyproject [project.scripts] entry is invalid")
            raw_schema = _cli_grammar_schema(name)
            span = f"project.scripts.{name}"
            declarations.append(
                {
                    "category": "CLI",
                    "entrypoint": f"{name} = {target}",
                    "normalized_entrypoint": f"cli:{name}".casefold(),
                    "provenance_path": "pyproject.toml",
                    "provenance_span_or_key": span,
                    "declared_inputs": {"argv_tokens": [name]},
                    "declared_input_schema_sha256": _canonical_sha256(raw_schema),
                    "static_dependency_tags": sorted(
                        {target.split(":", 1)[0].split(".", 1)[0]}
                    ),
                    "prerequisites": [],
                }
            )
            public_schemas.append(
                {
                    "schema_kind": "CLI_TOKEN_GRAMMAR_V1",
                    "raw_schema": raw_schema,
                    "provenance_path": "pyproject.toml",
                    "provenance_span_or_key": span,
                }
            )

    for path in sorted(python_paths):
        first = path.split("/")[0]
        name = path.split("/")[-1]
        if first == "examples":
            category = "EXAMPLE"
            declaration = _argv_declaration(
                category,
                path,
                f"python {path}",
                f"example:{path}".casefold(),
                ["python", path],
            )
        elif first in {"benchmarks", "bench"}:
            category = "BENCHMARK"
            declaration = _argv_declaration(
                category,
                path,
                f"python {path}",
                f"benchmark:{path}".casefold(),
                ["python", path],
            )
        elif first == "tests" and (
            name.startswith("test_") and name.endswith(".py")
            or name.endswith("_test.py")
        ):
            category = "PROJECT_TEST"
            declaration = _argv_declaration(
                category,
                path,
                f"pytest {path}",
                f"pytest:{path}".casefold(),
                ["pytest", path],
            )
        else:
            continue
        key = (category, path)
        if key not in seen_path_evidence:
            declarations.append(declaration)
            seen_path_evidence.add(key)


def discover(
    source_snapshot, build_descriptor: Mapping[str, Any]
) -> dict[str, Any]:
    entries = {
        entry.relative_path: entry.content for entry in source_snapshot.entries
    }
    if "meson.build" not in entries:
        raise ValueError("root meson.build is absent")

    declarations: list[dict] = []
    public_schemas: list[dict] = []
    sites: list[dict] = []
    seen_path_evidence: set[tuple[str, str]] = set()

    build_paths = sorted(
        path
        for path in entries
        if not _excluded(path)
        and (
            path.rsplit("/", 1)[-1].casefold() == "meson.build"
            or path.casefold().endswith(".meson")
        )
    )
    for path in build_paths:
        try:
            text = entries[path].decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ValueError(f"Meson build file is not UTF-8: {path}") from exc
        masked = _strip_meson_comments(text)
        meson_schema = _cli_grammar_schema("meson")
        for match in _MESON_TEST.finditer(masked):
            name = match.group(1)
            span = f"L{_line_number(masked, match.start())}"
            declarations.append(
                _meson_declaration(
                    "PROJECT_TEST",
                    path,
                    span,
                    f"meson-test:{name}",
                    f"meson-test:{name}".casefold(),
                    ["meson", "test", name],
                    meson_schema,
                )
            )
            public_schemas.append(
                {
                    "schema_kind": "CLI_TOKEN_GRAMMAR_V1",
                    "raw_schema": meson_schema,
                    "provenance_path": path,
                    "provenance_span_or_key": span,
                }
            )
        for match in _MESON_BENCHMARK.finditer(masked):
            name = match.group(1)
            span = f"L{_line_number(masked, match.start())}"
            declarations.append(
                _meson_declaration(
                    "BENCHMARK",
                    path,
                    span,
                    f"meson-benchmark:{name}",
                    f"meson-benchmark:{name}".casefold(),
                    ["meson", "test", "--benchmark", name],
                    meson_schema,
                )
            )
        for match in _MESON_EXECUTABLE.finditer(masked):
            name = match.group(1)
            span = f"L{_line_number(masked, match.start())}"
            category = _path_category(path) or "CLI"
            raw_schema = _cli_grammar_schema(name)
            declarations.append(
                _meson_declaration(
                    category,
                    path,
                    span,
                    f"target:{name}",
                    f"target:{name}".casefold(),
                    [name],
                    raw_schema,
                )
            )
            if category == "CLI":
                public_schemas.append(
                    {
                        "schema_kind": "CLI_TOKEN_GRAMMAR_V1",
                        "raw_schema": raw_schema,
                        "provenance_path": path,
                        "provenance_span_or_key": span,
                    }
                )

    declarations.extend(_header_declarations(entries))

    pyproject_raw = entries.get("pyproject.toml")
    if pyproject_raw is not None:
        try:
            pyproject = tomllib.loads(pyproject_raw.decode("utf-8"))
        except (UnicodeDecodeError, tomllib.TOMLDecodeError) as exc:
            raise ValueError("pyproject.toml is invalid") from exc
        project = pyproject.get("project")
        if (
            not isinstance(project, dict)
            or not isinstance(project.get("name"), str)
            or not project["name"]
        ):
            raise ValueError("pyproject [project].name is absent")
        _apply_python_branch(
            entries,
            project,
            declarations,
            public_schemas,
            sites,
            seen_path_evidence,
        )

    for path in sorted(entries):
        if _excluded(path):
            continue
        name = path.rsplit("/", 1)[-1]
        suffix = ("." + name.rsplit(".", 1)[-1]).casefold() if "." in name else ""
        category = _path_category(path)
        key = (category, path)
        if (
            category is not None
            and suffix in _PATH_EVIDENCE_SUFFIXES
            and key not in seen_path_evidence
        ):
            declarations.append(_source_evidenced_declaration(category, path))
            seen_path_evidence.add(key)

    for path in sorted(entries):
        if _excluded(path):
            continue
        name = path.rsplit("/", 1)[-1]
        suffix = ("." + name.rsplit(".", 1)[-1]).casefold() if "." in name else ""
        if suffix not in _C_FAMILY_SITE_SUFFIXES:
            continue
        try:
            text = entries[path].decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ValueError(f"C-family source is not UTF-8: {path}") from exc
        sites.extend(_c_family_sites(path, text))

    for path in sorted(entries):
        if _excluded(path):
            continue
        name = path.rsplit("/", 1)[-1]
        suffix = ("." + name.rsplit(".", 1)[-1]).casefold() if "." in name else ""
        if suffix not in _FORTRAN_SITE_SUFFIXES:
            continue
        try:
            text = entries[path].decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ValueError(f"Fortran source is not UTF-8: {path}") from exc
        sites.extend(_fortran_sites(path, text))

    return {
        "adapter_id": ADAPTER_ID,
        "ecosystem": ECOSYSTEM,
        "source_files": _scale_source_files(entries),
        "declarations": declarations,
        "public_schemas": public_schemas,
        "sites": sites,
    }
