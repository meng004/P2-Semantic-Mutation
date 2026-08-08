"""Pinned P12 bridge verification and deterministic P3 subject frames."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any, Mapping, Sequence

from .artifacts import (
    EvidenceError,
    canonical_json_bytes,
    canonical_sha256,
    safe_relative_path,
    validate_exact_object,
    validate_sha256,
)


_GIT_OID_RE = re.compile(r"[0-9a-f]{40}")
_SCALES = {"S", "M", "L"}
_TECHNIQUES = {
    "HYBRID_NATIVE",
    "TENSOR_AUTODIFF",
    "PROBABILISTIC_SURROGATE",
    "ITERATIVE_STOCHASTIC",
    "ARRAY_NUMERICAL",
    "SCALAR_CONTROL",
    "TECH_UNCERTAIN",
}

_LOCK_SCHEMA = {
    "repository_identity": str,
    "release_commit_sha": str,
    "bridge_path": str,
    "bridge_blob_sha": str,
    "contract_path": str,
    "contract_blob_sha": str,
    "package_root_sha256": str,
}
_BRIDGE_SCHEMA = {
    "schema_version": str,
    "p12_release_id": str,
    "p12_repository_identity": str,
    "p12_contract_path": str,
    "p12_contract_blob_sha": str,
    "p12_package_root_sha256": str,
    "p12_contract_sha256": str,
    "eligible_inventory_root_sha256": str,
    "eligible_item_count": int,
    "records": list,
    "trust_mode": str,
    "artifact_sha256": str,
}
_RECORD_SCHEMA = {
    "neutral_snapshot_id": str,
    "fixed_tree_commitment": str,
    "normalized_source_tree_sha256": str,
    "source_archive_sha256": str,
    "build_descriptor_sha256": str,
    "eligibility_reason": str,
    "eligible_for_construct": bool,
    "eligible_for_criterion": bool,
}
_FEATURE_SCHEMA = {
    "neutral_snapshot_id": str,
    "public_workload_set_sha256": str,
    "scale_class": str,
    "primary_technique": str,
    "technique_vector": list,
    "sites": list,
}
_SITE_SCHEMA = {
    "path": str,
    "symbol": str,
    "start_line": int,
    "start_col": int,
    "end_line": int,
    "end_col": int,
}
_REVEAL_SCHEMA = {
    "neutral_snapshot_id": str,
    "fixed_git_tree_oid": str,
    "reveal_nonce": str,
    "normalized_source_tree_sha256": str,
}


def _git(root: Path, *args: str) -> bytes:
    result = subprocess.run(
        ["git", "-C", str(root), *args],
        capture_output=True,
        shell=False,
        check=False,
    )
    if result.returncode != 0:
        raise EvidenceError("E_PINNED_GIT", f"git {' '.join(args)} failed")
    return result.stdout


def _git_oid(value: Any, field: str) -> str:
    if not isinstance(value, str) or _GIT_OID_RE.fullmatch(value) is None:
        raise EvidenceError("E_GIT_OID", f"{field} must be 40 lowercase hexadecimal characters")
    return value


def _canonical_document(raw: bytes, context: str) -> dict[str, Any]:
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise EvidenceError("E_BRIDGE_JSON", f"{context} is not valid JSON") from exc
    if not isinstance(value, dict) or canonical_json_bytes(value) != raw:
        raise EvidenceError("E_BRIDGE_CANONICAL", f"{context} is not canonical JSON")
    return value


def _neutral_snapshot_id(record: Mapping[str, Any], package_root: str) -> str:
    return canonical_sha256(
        {
            "p12_package_root_sha256": package_root,
            "normalized_source_tree_sha256": record["normalized_source_tree_sha256"],
            "source_archive_sha256": record["source_archive_sha256"],
            "domain": "P3-NEUTRAL-SNAPSHOT-v1",
        }
    )


def validate_bridge_document(bridge: dict[str, Any], consumer_lock: Mapping[str, Any]) -> dict:
    lock = validate_exact_object(dict(consumer_lock), _LOCK_SCHEMA, "consumer_lock")
    _git_oid(lock["release_commit_sha"], "consumer_lock.release_commit_sha")
    _git_oid(lock["bridge_blob_sha"], "consumer_lock.bridge_blob_sha")
    _git_oid(lock["contract_blob_sha"], "consumer_lock.contract_blob_sha")
    safe_relative_path(lock["bridge_path"])
    safe_relative_path(lock["contract_path"])
    validate_sha256(lock["package_root_sha256"], "consumer_lock.package_root_sha256")

    validate_exact_object(bridge, _BRIDGE_SCHEMA, "bridge")
    if bridge["schema_version"] != "p3-p12-bridge-v1":
        raise EvidenceError("E_BRIDGE_VERSION", "unsupported bridge schema")
    if bridge["trust_mode"] != "PINNED_GIT_RELEASE":
        raise EvidenceError("E_BRIDGE_TRUST", "bridge trust mode is not pinned Git")
    body = {key: value for key, value in bridge.items() if key != "artifact_sha256"}
    if bridge["artifact_sha256"] != canonical_sha256(body):
        raise EvidenceError("E_BRIDGE_HASH", "bridge canonical self-hash differs")
    if (
        bridge["p12_repository_identity"] != lock["repository_identity"]
        or bridge["p12_contract_path"] != lock["contract_path"]
        or bridge["p12_contract_blob_sha"] != lock["contract_blob_sha"]
        or bridge["p12_package_root_sha256"] != lock["package_root_sha256"]
    ):
        raise EvidenceError("E_BRIDGE_LOCK", "bridge identity differs from consumer lock")
    validate_sha256(bridge["p12_contract_sha256"], "bridge.p12_contract_sha256")
    validate_sha256(
        bridge["eligible_inventory_root_sha256"], "bridge.eligible_inventory_root_sha256"
    )
    records: list[dict[str, Any]] = []
    for index, record in enumerate(bridge["records"]):
        try:
            validate_exact_object(record, _RECORD_SCHEMA, f"bridge.records[{index}]")
        except EvidenceError as exc:
            if exc.code == "E_SCHEMA_KEYS":
                raise EvidenceError("E_BRIDGE_RECORD_KEYS", str(exc)) from exc
            raise
        for field in (
            "neutral_snapshot_id",
            "fixed_tree_commitment",
            "normalized_source_tree_sha256",
            "source_archive_sha256",
            "build_descriptor_sha256",
        ):
            validate_sha256(record[field], f"bridge.records[{index}].{field}")
        if record["neutral_snapshot_id"] != _neutral_snapshot_id(
            record, bridge["p12_package_root_sha256"]
        ):
            raise EvidenceError("E_NEUTRAL_ID", f"record {index} neutral ID differs")
        records.append(record)
    if bridge["eligible_item_count"] != len(records):
        raise EvidenceError("E_BRIDGE_COUNT", "eligible item count differs")
    if bridge["eligible_inventory_root_sha256"] != canonical_sha256(records):
        raise EvidenceError("E_BRIDGE_INVENTORY", "eligible inventory root differs")
    if len({record["fixed_tree_commitment"] for record in records}) != len(records):
        raise EvidenceError("E_BRIDGE_COMMITMENT_DUPLICATE", "duplicate tree commitment")
    return bridge


def verify_pinned_bridge(repo_root: str | Path, consumer_lock: Mapping[str, Any]) -> dict:
    root = Path(repo_root)
    lock = validate_exact_object(dict(consumer_lock), _LOCK_SCHEMA, "consumer_lock")
    commit = _git_oid(lock["release_commit_sha"], "consumer_lock.release_commit_sha")
    observed_commit = _git(root, "rev-parse", commit).decode().strip()
    if observed_commit != commit:
        raise EvidenceError("E_PINNED_COMMIT", "release commit does not resolve exactly")
    bridge_path = safe_relative_path(lock["bridge_path"]).as_posix()
    contract_path = safe_relative_path(lock["contract_path"]).as_posix()
    bridge_blob = _git(root, "rev-parse", f"{commit}:{bridge_path}").decode().strip()
    if bridge_blob != lock["bridge_blob_sha"]:
        raise EvidenceError("E_PINNED_BRIDGE_BLOB", "bridge Git blob differs")
    contract_blob = _git(root, "rev-parse", f"{commit}:{contract_path}").decode().strip()
    if contract_blob != lock["contract_blob_sha"]:
        raise EvidenceError("E_PINNED_CONTRACT_BLOB", "contract Git blob differs")
    bridge_raw = _git(root, "show", f"{commit}:{bridge_path}")
    contract_raw = _git(root, "show", f"{commit}:{contract_path}")
    bridge = validate_bridge_document(_canonical_document(bridge_raw, "bridge"), lock)
    if hashlib.sha256(contract_raw).hexdigest() != bridge["p12_contract_sha256"]:
        raise EvidenceError("E_CONTRACT_SHA256", "contract raw SHA-256 differs")
    return bridge


def _controlled_subject_id(record: Mapping[str, Any], feature: Mapping[str, Any]) -> str:
    return canonical_sha256(
        {
            "normalized_source_tree_sha256": record["normalized_source_tree_sha256"],
            "build_descriptor_sha256": record["build_descriptor_sha256"],
            "public_workload_set_sha256": feature["public_workload_set_sha256"],
            "domain": "P3-SUBJECT-v1",
        }
    )


def _sites(subject_id: str, values: Sequence[Any]) -> list[dict[str, Any]]:
    sites: list[dict[str, Any]] = []
    for index, value in enumerate(values):
        site = validate_exact_object(value, _SITE_SCHEMA, f"site[{index}]")
        safe_relative_path(site["path"])
        if any(type(site[field]) is not int or site[field] < 0 for field in _SITE_SCHEMA if field.endswith(("line", "col"))):
            raise EvidenceError("E_SITE_SPAN", f"site {index} has invalid span")
        body = {"controlled_subject_id": subject_id, **site, "domain": "P3-SITE-v1"}
        sites.append({**site, "site_id": canonical_sha256(body)})
    sites.sort(
        key=lambda item: (
            item["path"],
            item["symbol"],
            item["start_line"],
            item["start_col"],
            item["end_line"],
            item["end_col"],
            item["site_id"],
        )
    )
    if len({item["site_id"] for item in sites}) != len(sites):
        raise EvidenceError("E_SITE_DUPLICATE", "duplicate canonical site")
    return sites


def build_subject_frames(
    verified_bridge: Mapping[str, Any],
    feature_records: Sequence[Mapping[str, Any]],
    construct_limit: int = 18,
) -> dict[str, Any]:
    if type(construct_limit) is not int or construct_limit < 1:
        raise EvidenceError("E_CONSTRUCT_LIMIT", "construct limit must be positive")
    records = verified_bridge.get("records")
    if not isinstance(records, list):
        raise EvidenceError("E_BRIDGE_RECORDS", "verified bridge records are absent")
    features: dict[str, Mapping[str, Any]] = {}
    for index, candidate in enumerate(feature_records):
        feature = validate_exact_object(candidate, _FEATURE_SCHEMA, f"features[{index}]")
        neutral = validate_sha256(feature["neutral_snapshot_id"], "feature.neutral_snapshot_id")
        validate_sha256(feature["public_workload_set_sha256"], "feature.workload")
        if neutral in features:
            raise EvidenceError("E_FEATURE_DUPLICATE", f"duplicate feature record: {neutral}")
        if feature["scale_class"] not in _SCALES:
            raise EvidenceError("E_SCALE", f"invalid scale: {feature['scale_class']}")
        if feature["primary_technique"] not in _TECHNIQUES:
            raise EvidenceError("E_TECHNIQUE", "invalid primary technique")
        vector = feature["technique_vector"]
        if (
            not vector
            or any(item not in _TECHNIQUES for item in vector)
            or vector != sorted(set(vector))
            or feature["primary_technique"] not in vector
        ):
            raise EvidenceError("E_TECHNIQUE", "technique vector is not canonical")
        features[neutral] = feature
    record_ids = {record["neutral_snapshot_id"] for record in records}
    if set(features) != record_ids:
        raise EvidenceError("E_FEATURE_COVERAGE", "feature records do not cover bridge exactly")

    profiles: dict[str, dict[str, Any]] = {}
    eligibility: dict[str, dict[str, bool]] = {}
    for record in records:
        neutral = record["neutral_snapshot_id"]
        feature = features[neutral]
        subject_id = _controlled_subject_id(record, feature)
        profile = {
            "controlled_subject_id": subject_id,
            "normalized_source_tree_sha256": record["normalized_source_tree_sha256"],
            "build_descriptor_sha256": record["build_descriptor_sha256"],
            "public_workload_set_sha256": feature["public_workload_set_sha256"],
            "scale_class": feature["scale_class"],
            "primary_technique": feature["primary_technique"],
            "technique_vector": list(feature["technique_vector"]),
            "sites": _sites(subject_id, feature["sites"]),
            "neutral_snapshot_ids": [neutral],
        }
        existing = profiles.get(subject_id)
        if existing is not None:
            comparable = {**existing, "neutral_snapshot_ids": [neutral]}
            if comparable != profile:
                raise EvidenceError("E_SUBJECT_ALIAS_CONFLICT", "subject aliases conflict")
            existing["neutral_snapshot_ids"].append(neutral)
            existing["neutral_snapshot_ids"].sort()
        else:
            profiles[subject_id] = profile
        state = eligibility.setdefault(subject_id, {"construct": False, "criterion": False})
        state["construct"] = state["construct"] or record["eligible_for_construct"]
        state["criterion"] = state["criterion"] or record["eligible_for_criterion"]

    subjects = [profiles[key] for key in sorted(profiles)]
    candidates: list[tuple[str, str, str, str]] = []
    for subject in subjects:
        subject_id = subject["controlled_subject_id"]
        if eligibility[subject_id]["construct"]:
            key = canonical_sha256(
                {
                    "controlled_subject_id": subject_id,
                    "scale_class": subject["scale_class"],
                    "technique_vector": subject["technique_vector"],
                    "domain": "P3-C1",
                }
            )
            candidates.append(
                (subject["scale_class"], subject["primary_technique"], key, subject_id)
            )
    candidates.sort(key=lambda item: (item[2], item[3]))
    selected: list[str] = []
    used_cells: set[tuple[str, str]] = set()
    for scale, technique, _, subject_id in candidates:
        if (scale, technique) not in used_cells and len(selected) < construct_limit:
            selected.append(subject_id)
            used_cells.add((scale, technique))
    for _, _, _, subject_id in candidates:
        if subject_id not in selected and len(selected) < construct_limit:
            selected.append(subject_id)
    criterion = sorted(
        subject_id for subject_id, state in eligibility.items() if state["criterion"]
    )
    body = {
        "schema_version": "p3-subject-frames-v1",
        "subjects": subjects,
        "c_construct": selected,
        "c_criterion": criterion,
    }
    return {**body, "artifact_sha256": canonical_sha256(body)}


def verify_reveal(
    bridge_record: Mapping[str, Any],
    reveal_record: Mapping[str, Any],
    package_root: str,
    *,
    observed_tree_oid: str,
    observed_normalized_sha256: str,
) -> None:
    validate_exact_object(dict(bridge_record), _RECORD_SCHEMA, "bridge_record")
    reveal = validate_exact_object(dict(reveal_record), _REVEAL_SCHEMA, "reveal_record")
    validate_sha256(package_root, "package_root")
    fixed_oid = _git_oid(reveal["fixed_git_tree_oid"], "reveal.fixed_git_tree_oid")
    if not isinstance(reveal["reveal_nonce"], str) or re.fullmatch(
        r"[0-9a-f]{64}", reveal["reveal_nonce"]
    ) is None:
        raise EvidenceError("E_REVEAL_NONCE", "reveal nonce must encode 32 bytes")
    validate_sha256(reveal["normalized_source_tree_sha256"], "reveal.normalized_source")
    commitment = hashlib.sha256(
        b"P3-FIXED-TREE-v1"
        + package_root.encode("ascii")
        + fixed_oid.encode("ascii")
        + bytes.fromhex(reveal["reveal_nonce"])
    ).hexdigest()
    if commitment != bridge_record["fixed_tree_commitment"]:
        raise EvidenceError("E_REVEAL_COMMITMENT", "fixed-tree commitment does not open")
    if reveal["neutral_snapshot_id"] != bridge_record["neutral_snapshot_id"]:
        raise EvidenceError("E_REVEAL_ID", "neutral snapshot ID differs")
    if observed_tree_oid != fixed_oid:
        raise EvidenceError("E_REVEAL_TREE", "observed Git tree differs")
    if (
        reveal["normalized_source_tree_sha256"]
        != bridge_record["normalized_source_tree_sha256"]
        or observed_normalized_sha256 != bridge_record["normalized_source_tree_sha256"]
    ):
        raise EvidenceError("E_REVEAL_SOURCE", "normalized source differs")
