"""Real PYTHON_PEP517_V1 adapter: source-derived discovery for PEP 517 subjects.

Frozen discovery rule (P3 v3, 2026-08-12). Executed only through the verified
in-process registry seam; stdlib-only; no output, no network, no imports of
controller modules.

- The snapshot must contain a root ``pyproject.toml`` whose ``[project].name``
  is a non-empty string; otherwise discovery raises and fails closed.
- ``source_files``: every non-excluded snapshot path with suffix ``.py``,
  ``.pyi``, ``.pyx``, or ``.pxd`` (exclusion rule inlined below, a frozen copy
  of the controller's excluded-path rule).
- Package roots: ``src/<top>`` directories containing ``__init__.py``; when
  none exist, flat ``<top>`` directories containing ``__init__.py``.
- Public modules: ``.py`` files under a package root where no path component
  after the root is ``_``-prefixed (the literal ``__init__.py`` is allowed and
  maps to the package module).
- ``PUBLIC_API``: module-level public functions and classes; when the module
  binds ``__all__`` to a list of string constants, only those names.
- ``CLI``: ``[project.scripts]`` entries.
- ``EXAMPLE`` / ``BENCHMARK`` / ``PROJECT_TEST``: path-evidenced ``.py`` files
  under ``examples/``, ``benchmarks/`` or ``bench/``, and ``tests/``
  (``test_*.py`` or ``*_test.py``); their bodies are never parsed.
- Input schemas derive only from PUBLIC_API signatures and
  ``[project.scripts]``. Annotation mapping over the casefolded generic-free
  parameter annotations: all in ``{int, float, complex}`` →
  ``NUMERIC_ARRAY_DOMAIN_V1``; all ``str`` → ``TEXT_IO_SCHEMA_V1``; all in
  ``{bytes, bytearray, memoryview}`` → ``BINARY_RECORD_SCHEMA_V1``; zero
  parameters → ``{"kind": "NO_INPUT"}`` and no schema row; anything else
  (including ``*args``/``**kwargs``) → ``JSON_SCHEMA_DRAFT2020_12_V1``.
- Sites: every function and method definition in public modules.
"""

from __future__ import annotations

import ast
import hashlib
import json
import tomllib
from collections.abc import Mapping
from typing import Any

ADAPTER_ID = "PYTHON_PEP517_V1"
ECOSYSTEM = "python"
_SOURCE_SUFFIXES = (".py", ".pyi", ".pyx", ".pxd")
_EXCLUDED_PARTS = {
    ".bzr", ".git", ".hg", ".svn", ".tox", ".venv", "_build", "__pycache__",
    "build", "cmakefiles", "debug", "dist", "env", "external", "fixture",
    "fixtures", "generated", "node_modules", "out", "release",
    "relwithdebinfo", "minsizerel", "site-packages", "target", "testdata",
    "third-party", "third_party", "vendor", "vendored", "vendors", "venv",
    ".ninja_deps", ".ninja_log", "build.ninja", "cmakecache.txt",
    "compile_commands.json",
}
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


def _canonical_sha256(value: Any) -> str:
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


def discover(source_snapshot, build_descriptor: Mapping[str, Any]) -> dict[str, Any]:
    entries = {
        entry.relative_path: entry.content for entry in source_snapshot.entries
    }
    pyproject_raw = entries.get("pyproject.toml")
    if pyproject_raw is None:
        raise ValueError("pyproject.toml is absent")
    try:
        pyproject = tomllib.loads(pyproject_raw.decode("utf-8"))
    except (UnicodeDecodeError, tomllib.TOMLDecodeError) as exc:
        raise ValueError("pyproject.toml is invalid") from exc
    project = pyproject.get("project")
    if not isinstance(project, dict) or not isinstance(project.get("name"), str) or not project["name"]:
        raise ValueError("pyproject [project].name is absent")

    source_files = sorted(
        path
        for path in entries
        if path.endswith(_SOURCE_SUFFIXES) and not _excluded(path)
    )

    python_paths = [path for path in entries if path.endswith(".py") and not _excluded(path)]
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

    declarations: list[dict] = []
    public_schemas: list[dict] = []
    sites: list[dict] = []

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
            raw_schema = {
                "kind": "CLI_TOKEN_GRAMMAR_V1",
                "program": name,
                "tokens": {"min": 0, "max": 3},
                "vocabulary": sorted({name, "--help", "--version"}),
            }
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
            declarations.append(
                _argv_declaration(
                    "EXAMPLE",
                    path,
                    f"python {path}",
                    f"example:{path}".casefold(),
                    ["python", path],
                )
            )
        elif first in {"benchmarks", "bench"}:
            declarations.append(
                _argv_declaration(
                    "BENCHMARK",
                    path,
                    f"python {path}",
                    f"benchmark:{path}".casefold(),
                    ["python", path],
                )
            )
        elif first == "tests" and (
            name.startswith("test_") and name.endswith(".py")
            or name.endswith("_test.py")
        ):
            declarations.append(
                _argv_declaration(
                    "PROJECT_TEST",
                    path,
                    f"pytest {path}",
                    f"pytest:{path}".casefold(),
                    ["pytest", path],
                )
            )

    return {
        "adapter_id": ADAPTER_ID,
        "ecosystem": ECOSYSTEM,
        "source_files": source_files,
        "declarations": declarations,
        "public_schemas": public_schemas,
        "sites": sites,
    }
