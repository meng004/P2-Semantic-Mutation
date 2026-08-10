"""Content-addressed, role-separated phase packages."""

from __future__ import annotations

import os
import shutil
import stat
import tempfile
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from .artifacts import (
    EvidenceError,
    canonical_sha256,
    file_sha256,
    safe_relative_path,
    validate_exact_object,
    validate_sha256,
)

PACKAGE_A_CLASSES = {
    "PUBLIC_BEHAVIOR_FRAME",
    "PROFILING_WORKLOAD",
    "PROFILING_RESULT",
    "CONTRACT",
    "E_COMMON",
    "E_CONTRACT",
    "SLOT",
    "PROPOSAL_INPUT",
}
PACKAGE_B_CLASSES = {
    "DENOMINATOR",
    "PORTFOLIO",
    "E_COMMON_PRIMARY",
    "E_CONTRACT_SENSITIVITY",
    "EXECUTION_CODE",
}
PROPOSER_ALLOWED_CLASSES = {
    "SOURCE",
    "BUILD",
    "PUBLIC_DOC",
    "CONTRACT",
    "PROPOSAL_INPUT",
}

_CONSTRUCTION_A_BASE = {
    "SOURCE",
    "BUILD",
    "PUBLIC_DOC",
    "CONTRACT",
    "PROPOSAL_INPUT",
}
_CONTROLLED_B_BASE = {
    "SOURCE",
    "SEMANTIC_MUTANT",
    "SYNTACTIC_MUTANT",
    "MR",
    "JOB_INPUT",
}

ALLOWED_CLASSES = {
    "CONSTRUCTION_A": frozenset(_CONSTRUCTION_A_BASE | PACKAGE_A_CLASSES),
    "CONTROLLED_B": frozenset(_CONTROLLED_B_BASE | PACKAGE_B_CLASSES),
    "REAL_HOLDOUT_C": frozenset(
        {
            "P12_IDENTITY",
            "P12_BUGGY",
            "P12_REVEAL",
            "REAL_JOB_INPUT",
        }
    ),
}

PACKAGE_B_PRIMARY_CLASSES = frozenset(
    ALLOWED_CLASSES["CONTROLLED_B"] - {"E_CONTRACT_SENSITIVITY"}
)
PACKAGE_B_SENSITIVITY_CLASSES = frozenset(
    ALLOWED_CLASSES["CONTROLLED_B"] - {"E_COMMON_PRIMARY"}
)

_SPEC_SCHEMA = {"path": str, "class": str}
_FILE_SCHEMA = {"path": str, "class": str, "mode": int, "size": int, "sha256": str}
_MANIFEST_SCHEMA = {
    "schema_version": str,
    "role": str,
    "parents": list,
    "files": list,
    "package_tree_sha256": str,
    "artifact_sha256": str,
}
_COMMON_INVENTORY_SCHEMA = {
    "schema_version": str,
    "controlled_subject_source_id": str,
    "eligible_schema_count": int,
    "rows": list,
    "artifact_sha256": str,
}
_COMMON_ROW_SCHEMA = {
    "ordinal": int,
    "seed": int,
    "generator_id": (str, type(None)),
    "schema_kind": (str, type(None)),
    "schema_selection_key": (str, type(None)),
    "raw_schema_sha256": (str, type(None)),
    "schema_provenance_path": (str, type(None)),
    "schema_provenance_span_or_key": (str, type(None)),
    "generator_source_sha256": (str, type(None)),
    "status": str,
    "failure_code": str,
    "envelope": (dict, type(None)),
    "raw_payload_sha256": (str, type(None)),
    "input_id": str,
}
_COMMON_VALIDITY_SCHEMA = {
    "schema_version": str,
    "controlled_subject_source_id": str,
    "inventory_artifact_sha256": str,
    "rows": list,
    "sites": (list, type(None)),
    "contracts": (list, type(None)),
    "profile": (dict, type(None)),
    "frame_artifact_sha256": (str, type(None)),
    "artifact_sha256": str,
}
_COMMON_VALIDITY_ROW_SCHEMA = {
    "ordinal": int,
    "input_id": str,
    "raw_payload_sha256": (str, type(None)),
    "envelope": (dict, type(None)),
    "generator_id": (str, type(None)),
    "schema_kind": (str, type(None)),
    "schema_selection_key": (str, type(None)),
    "raw_schema_sha256": (str, type(None)),
    "seed": int,
    "status": str,
    "failure_code": str,
}


def _regular_file(root: Path, relative: str) -> Path:
    path = root / safe_relative_path(relative)
    try:
        info = path.lstat()
    except FileNotFoundError as exc:
        raise EvidenceError("E_PACKAGE_MISSING", f"declared file is absent: {relative}") from exc
    if not stat.S_ISREG(info.st_mode) or path.is_symlink():
        raise EvidenceError("E_PACKAGE_FILE_TYPE", f"not a regular file: {relative}")
    return path


def _validate_role(role: Any) -> str:
    if not isinstance(role, str) or role not in ALLOWED_CLASSES:
        raise EvidenceError("E_PACKAGE_ROLE", f"unsupported package role: {role!r}")
    return role


def _resolve_allowed_classes(role: str, allowed_classes: Sequence[str] | set[str] | frozenset[str] | None) -> frozenset[str]:
    role_classes = ALLOWED_CLASSES[role]
    if allowed_classes is None:
        return role_classes
    selected = frozenset(allowed_classes)
    if not selected <= role_classes:
        raise EvidenceError(
            "E_PACKAGE_ALLOWED_CLASSES",
            f"allowed_classes is not a subset of {role}",
        )
    return selected


def build_package(
    role: str,
    source_root: str | Path,
    file_specs: Sequence[Mapping[str, Any]],
    parents: Sequence[str],
    allowed_classes: Sequence[str] | set[str] | frozenset[str] | None = None,
) -> dict[str, Any]:
    role = _validate_role(role)
    effective_classes = _resolve_allowed_classes(role, allowed_classes)
    root = Path(source_root)
    for index, parent in enumerate(parents):
        validate_sha256(parent, f"parents[{index}]")
    if list(parents) != sorted(set(parents)):
        raise EvidenceError("E_PACKAGE_PARENTS", "parent hashes must be sorted and unique")
    files: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, candidate in enumerate(file_specs):
        spec = validate_exact_object(dict(candidate), _SPEC_SCHEMA, f"file_specs[{index}]")
        relative = safe_relative_path(spec["path"]).as_posix()
        if relative in seen:
            raise EvidenceError("E_PACKAGE_DUPLICATE", f"duplicate path: {relative}")
        seen.add(relative)
        if spec["class"] not in effective_classes:
            raise EvidenceError(
                "E_PACKAGE_CONTENT_CLASS",
                f"{spec['class']} is forbidden in {role}",
            )
        path = _regular_file(root, relative)
        info = path.stat()
        files.append(
            {
                "path": relative,
                "class": spec["class"],
                "mode": stat.S_IMODE(info.st_mode),
                "size": info.st_size,
                "sha256": file_sha256(path),
            }
        )
    files.sort(key=lambda item: item["path"])
    body = {
        "schema_version": "p3-package-manifest-v1",
        "role": role,
        "parents": list(parents),
        "files": files,
        "package_tree_sha256": canonical_sha256(files),
    }
    return {**body, "artifact_sha256": canonical_sha256(body)}


def _validate_manifest(manifest: Mapping[str, Any]) -> dict[str, Any]:
    value = validate_exact_object(dict(manifest), _MANIFEST_SCHEMA, "manifest")
    body = {key: item for key, item in value.items() if key != "artifact_sha256"}
    if value["artifact_sha256"] != canonical_sha256(body):
        raise EvidenceError("E_PACKAGE_MANIFEST_HASH", "manifest self-hash differs")
    if value["schema_version"] != "p3-package-manifest-v1":
        raise EvidenceError("E_PACKAGE_VERSION", "unsupported package manifest")
    role = _validate_role(value["role"])
    if value["parents"] != sorted(set(value["parents"])):
        raise EvidenceError("E_PACKAGE_PARENTS", "parent hashes are not canonical")
    for index, parent in enumerate(value["parents"]):
        validate_sha256(parent, f"manifest.parents[{index}]")
    paths: list[str] = []
    for index, candidate in enumerate(value["files"]):
        record = validate_exact_object(candidate, _FILE_SCHEMA, f"manifest.files[{index}]")
        relative = safe_relative_path(record["path"]).as_posix()
        paths.append(relative)
        if record["class"] not in ALLOWED_CLASSES[role]:
            raise EvidenceError("E_PACKAGE_CONTENT_CLASS", "manifest contains forbidden class")
        if type(record["mode"]) is not int or not 0 <= record["mode"] <= 0o7777:
            raise EvidenceError("E_PACKAGE_MODE", f"invalid mode: {relative}")
        if type(record["size"]) is not int or record["size"] < 0:
            raise EvidenceError("E_PACKAGE_SIZE", f"invalid size: {relative}")
        validate_sha256(record["sha256"], f"manifest.files[{index}].sha256")
    if paths != sorted(set(paths)):
        raise EvidenceError("E_PACKAGE_DUPLICATE", "manifest paths are not sorted and unique")
    if value["package_tree_sha256"] != canonical_sha256(value["files"]):
        raise EvidenceError("E_PACKAGE_TREE", "package tree hash differs")
    return value


def validate_package_manifest(manifest: Mapping[str, Any]) -> dict[str, Any]:
    """Validate package manifest structure and self-hash without filesystem binding."""

    return _validate_manifest(manifest)


def verify_package(source_root: str | Path, manifest: Mapping[str, Any]) -> None:
    root = Path(source_root)
    value = _validate_manifest(manifest)
    declared = {item["path"] for item in value["files"]}
    observed: set[str] = set()
    for path in root.rglob("*"):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            raise EvidenceError("E_PACKAGE_FILE_TYPE", f"symlink present: {relative}")
        if path.is_file():
            observed.add(relative)
    if observed != declared:
        raise EvidenceError(
            "E_PACKAGE_FILE_SET",
            f"file set differs: missing={sorted(declared - observed)}, extra={sorted(observed - declared)}",
        )
    for record in value["files"]:
        path = _regular_file(root, record["path"])
        info = path.stat()
        if stat.S_IMODE(info.st_mode) != record["mode"]:
            raise EvidenceError("E_PACKAGE_MODE", f"mode differs: {record['path']}")
        if info.st_size != record["size"]:
            raise EvidenceError("E_PACKAGE_SIZE", f"size differs: {record['path']}")
        if file_sha256(path) != record["sha256"]:
            raise EvidenceError("E_PACKAGE_SHA256", f"bytes differ: {record['path']}")


def verify_materialized_package(
    package_root: str | Path, manifest: Mapping[str, Any]
) -> dict[str, Any]:
    """Validate a manifest and require exact bytes at its materialized root."""

    root = Path(package_root)
    try:
        info = root.lstat()
    except FileNotFoundError as exc:
        raise EvidenceError("E_PACKAGE_MISSING", f"package root is absent: {root}") from exc
    if root.is_symlink() or not stat.S_ISDIR(info.st_mode):
        raise EvidenceError("E_PACKAGE_FILE_TYPE", f"package root is unsafe: {root}")
    value = _validate_manifest(manifest)
    verify_package(root, value)
    return value


def _verified_self_hash(artifact: Mapping[str, Any], context: str) -> dict[str, Any]:
    value = dict(artifact)
    digest = validate_sha256(value.get("artifact_sha256"), f"{context}.artifact_sha256")
    body = {key: item for key, item in value.items() if key != "artifact_sha256"}
    if digest != canonical_sha256(body):
        raise EvidenceError("E_COMMON_HASH", f"{context} self-hash differs")
    return value


def verify_common_input_evidence(
    inventory: Mapping[str, Any],
    validity: Mapping[str, Any],
    *,
    controlled_subject_source_id: str,
    public_frame: Mapping[str, Any],
    profiling_workload: Mapping[str, Any],
    consumer_input_ids: Sequence[str],
) -> dict[str, Any]:
    """Validate exact E_COMMON identities and their pre-consumer validity receipt."""

    from .bridge_and_frames import (  # local import keeps package construction shallow
        E_COMMON_COUNT,
        E_COMMON_GENERATOR_IDS,
        _common_input_id,
        _common_input_seed,
    )

    source_id = validate_sha256(
        controlled_subject_source_id, "controlled_subject_source_id"
    )
    frame = _verified_self_hash(public_frame, "public_frame")
    workload = _verified_self_hash(profiling_workload, "profiling_workload")
    if (
        frame.get("controlled_subject_source_id") != source_id
        or workload.get("controlled_subject_source_id") != source_id
    ):
        raise EvidenceError(
            "E_COMMON_IDENTITY", "frame/workload subject identity differs"
        )
    value = validate_exact_object(
        dict(inventory), _COMMON_INVENTORY_SCHEMA, "common_inputs"
    )
    if value["schema_version"] != "p3-evaluation-inputs-common-v1":
        raise EvidenceError("E_COMMON_SCHEMA", "common input schema version differs")
    if value["controlled_subject_source_id"] != source_id:
        raise EvidenceError("E_COMMON_IDENTITY", "common input subject differs")
    if type(value["eligible_schema_count"]) is bool or value["eligible_schema_count"] < 0:
        raise EvidenceError("E_COMMON_SCHEMA", "eligible schema count is invalid")
    inventory_body = {
        key: item for key, item in value.items() if key != "artifact_sha256"
    }
    if value["artifact_sha256"] != canonical_sha256(inventory_body):
        raise EvidenceError("E_COMMON_HASH", "common input inventory self-hash differs")
    if len(value["rows"]) != E_COMMON_COUNT:
        raise EvidenceError("E_COMMON_ROWS", "common input row count differs")
    generator_ids = set(E_COMMON_GENERATOR_IDS)
    rows: list[dict[str, Any]] = []
    input_ids: set[str] = set()
    for index, candidate in enumerate(value["rows"], 1):
        row = validate_exact_object(candidate, _COMMON_ROW_SCHEMA, f"common_inputs.rows[{index}]")
        if row["ordinal"] != index or type(row["seed"]) is bool:
            raise EvidenceError("E_COMMON_ORDINAL", f"common input ordinal {index} differs")
        if row["seed"] != _common_input_seed(source_id, index):
            raise EvidenceError("E_COMMON_SEED", f"common input seed {index} differs")
        status = row["status"]
        identity_fields = (
            "generator_id",
            "schema_kind",
            "schema_selection_key",
            "raw_schema_sha256",
            "schema_provenance_path",
            "schema_provenance_span_or_key",
            "generator_source_sha256",
        )
        if status == "COMMON_INPUT_UNAVAILABLE":
            if any(row[field] is not None for field in identity_fields):
                raise EvidenceError("E_COMMON_IDENTITY", "unavailable row has schema identity")
            if (
                row["failure_code"] != "COMMON_INPUT_UNAVAILABLE"
                or row["envelope"] is not None
                or row["raw_payload_sha256"] is not None
            ):
                raise EvidenceError("E_COMMON_STATUS", "unavailable row payload differs")
        elif status in {"COMMON_INPUT_EXECUTABLE", "COMMON_INPUT_INVALID"}:
            if row["generator_id"] not in generator_ids:
                raise EvidenceError("E_COMMON_GENERATOR", "generator identity differs")
            if row["schema_kind"] != row["generator_id"]:
                raise EvidenceError("E_COMMON_SCHEMA", "schema/generator identity differs")
            for field in (
                "schema_selection_key",
                "raw_schema_sha256",
                "generator_source_sha256",
            ):
                validate_sha256(row[field], f"common_inputs.rows[{index}].{field}")
            if not row["schema_provenance_path"] or not row["schema_provenance_span_or_key"]:
                raise EvidenceError("E_COMMON_SCHEMA", "schema provenance is absent")
            safe_relative_path(row["schema_provenance_path"])
            if status == "COMMON_INPUT_EXECUTABLE":
                if row["failure_code"] or row["envelope"] is None:
                    raise EvidenceError("E_COMMON_STATUS", "executable row payload differs")
                validate_sha256(
                    row["raw_payload_sha256"],
                    f"common_inputs.rows[{index}].raw_payload_sha256",
                )
            elif (
                not row["failure_code"]
                or row["envelope"] is not None
                or row["raw_payload_sha256"] is not None
            ):
                raise EvidenceError("E_COMMON_STATUS", "invalid row payload differs")
        else:
            raise EvidenceError("E_COMMON_STATUS", f"unknown common status: {status}")
        expected_input_id = _common_input_id(
            source_id,
            index,
            generator_id=row["generator_id"],
            schema_selection_key=row["schema_selection_key"],
            raw_schema_sha256=row["raw_schema_sha256"],
            schema_provenance_path=row["schema_provenance_path"],
            schema_provenance_span_or_key=row["schema_provenance_span_or_key"],
            generator_source_sha256=row["generator_source_sha256"],
            raw_payload_sha256=row["raw_payload_sha256"],
            status=status,
            failure_code=row["failure_code"],
        )
        if row["input_id"] != expected_input_id or row["input_id"] in input_ids:
            raise EvidenceError("E_COMMON_INPUT_ID", "common input identity differs")
        input_ids.add(row["input_id"])
        rows.append(row)

    receipt = validate_exact_object(
        dict(validity), _COMMON_VALIDITY_SCHEMA, "common_input_validity"
    )
    if receipt["schema_version"] != "p3-common-input-validity-v1":
        raise EvidenceError("E_COMMON_VALIDITY", "validity schema version differs")
    receipt_body = {
        key: item for key, item in receipt.items() if key != "artifact_sha256"
    }
    if receipt["artifact_sha256"] != canonical_sha256(receipt_body):
        raise EvidenceError("E_COMMON_HASH", "validity receipt self-hash differs")
    if (
        receipt["controlled_subject_source_id"] != source_id
        or receipt["inventory_artifact_sha256"] != value["artifact_sha256"]
        or receipt["frame_artifact_sha256"] != frame["artifact_sha256"]
        or len(receipt["rows"]) != E_COMMON_COUNT
    ):
        raise EvidenceError("E_COMMON_VALIDITY", "validity receipt binding differs")
    valid_by_id: dict[str, str] = {}
    projected_fields = tuple(_COMMON_VALIDITY_ROW_SCHEMA)
    for index, (source_row, candidate) in enumerate(
        zip(rows, receipt["rows"], strict=True), 1
    ):
        row = validate_exact_object(
            candidate, _COMMON_VALIDITY_ROW_SCHEMA, f"common_input_validity.rows[{index}]"
        )
        for field in projected_fields:
            if field == "status":
                continue
            if row[field] != source_row[field]:
                raise EvidenceError("E_COMMON_VALIDITY", "validity row identity differs")
        if row["status"] not in {
            "COMMON_INPUT_EXECUTABLE",
            "COMMON_INPUT_INVALID",
            "COMMON_INPUT_UNAVAILABLE",
        }:
            raise EvidenceError("E_COMMON_VALIDITY", "validity row status differs")
        if source_row["status"] != "COMMON_INPUT_EXECUTABLE" and row["status"] != source_row["status"]:
            raise EvidenceError("E_COMMON_VALIDITY", "validity upgraded a frozen row")
        valid_by_id[row["input_id"]] = row["status"]
    consumers = list(consumer_input_ids)
    if len(consumers) != len(set(consumers)) or any(
        type(input_id) is not str for input_id in consumers
    ):
        raise EvidenceError("E_COMMON_CHRONOLOGY", "consumer input IDs are duplicated")
    if any(valid_by_id.get(input_id) != "COMMON_INPUT_EXECUTABLE" for input_id in consumers):
        raise EvidenceError(
            "E_COMMON_CHRONOLOGY", "consumer used input before executable validity"
        )
    return {"inventory": value, "validity": receipt}


def _project_manifest(
    manifest: Mapping[str, Any],
    allowed_classes: frozenset[str],
) -> dict[str, Any]:
    files = [dict(item) for item in manifest["files"] if item["class"] in allowed_classes]
    body = {
        "schema_version": manifest["schema_version"],
        "role": manifest["role"],
        "parents": list(manifest["parents"]),
        "files": files,
        "package_tree_sha256": canonical_sha256(files),
    }
    return {**body, "artifact_sha256": canonical_sha256(body)}


def materialize_package(
    source_root: str | Path,
    target_root: str | Path,
    manifest: Mapping[str, Any],
    allowed_classes: Sequence[str] | set[str] | frozenset[str] | None = None,
) -> None:
    source = Path(source_root)
    target = Path(target_root)
    verify_package(source, manifest)
    effective_classes = _resolve_allowed_classes(manifest["role"], allowed_classes)
    active_manifest: Mapping[str, Any] = (
        manifest
        if allowed_classes is None
        else _project_manifest(manifest, effective_classes)
    )
    if target.exists():
        raise EvidenceError("E_PACKAGE_TARGET_EXISTS", f"target exists: {target}")
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix=f".{target.name}.", dir=target.parent))
    try:
        for record in active_manifest["files"]:
            destination = temporary / safe_relative_path(record["path"])
            destination.parent.mkdir(parents=True, exist_ok=True)
            with (source / record["path"]).open("rb") as reader, destination.open("xb") as writer:
                shutil.copyfileobj(reader, writer)
                writer.flush()
                os.fsync(writer.fileno())
            os.chmod(destination, record["mode"])
        verify_package(temporary, active_manifest)
        temporary.rename(target)
    except BaseException:
        shutil.rmtree(temporary, ignore_errors=True)
        raise
