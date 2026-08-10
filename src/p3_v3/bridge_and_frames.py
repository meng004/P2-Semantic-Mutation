"""Pinned P12 bridge verification and deterministic P3 subject frames."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from decimal import Decimal
from fractions import Fraction
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from .artifacts import (
    EvidenceError,
    canonical_json_bytes,
    canonical_sha256,
    file_sha256,
    safe_relative_path,
    validate_exact_object,
    validate_sha256,
)


_GIT_OID_RE = re.compile(r"[0-9a-f]{40}")
_SCALE_ORDER = ("S", "M", "L")
_TECHNIQUE_ORDER = (
    "HYBRID_NATIVE",
    "TENSOR_AUTODIFF",
    "PROBABILISTIC_SURROGATE",
    "ITERATIVE_STOCHASTIC",
    "ARRAY_NUMERICAL",
    "SCALAR_CONTROL",
    "TECH_UNCERTAIN",
)
_SCALES = set(_SCALE_ORDER)
_TECHNIQUES = set(_TECHNIQUE_ORDER)

PROFILING_BUDGETS = {"S": 10, "M": 15, "L": 20}
BEHAVIOR_CATEGORY_ORDER = [
    "PUBLIC_API",
    "CLI",
    "EXAMPLE",
    "BENCHMARK",
    "PROJECT_TEST",
]
CONFIRMATORY_ADAPTERS = {
    "PYTHON_PEP517_V1",
    "CMAKE_CTEST_V1",
    "MESON_TEST_V1",
    "AUTOTOOLS_MAKECHECK_V1",
}
_ADAPTER_ECOSYSTEMS = {
    "PYTHON_PEP517_V1": "python",
    "CMAKE_CTEST_V1": "cmake",
    "MESON_TEST_V1": "meson",
    "AUTOTOOLS_MAKECHECK_V1": "autotools",
}
_BEHAVIOR_CATEGORIES = set(BEHAVIOR_CATEGORY_ORDER)
_PROFILE_TECHNIQUES = tuple(
    technique for technique in _TECHNIQUE_ORDER if technique != "TECH_UNCERTAIN"
)
_UNRESOLVED_STATUSES = frozenset(
    {"FAILURE", "TIMEOUT", "MISSING_TRACE", "ADAPTER_UNCERTAIN"}
)
P12_OUTCOME_STATES = [
    "MR_VIOLATION",
    "MR_SATISFIED",
    "DECLARED_EXCEPTION_OR_TIMEOUT_VIOLATION",
    "SCIENTIFIC_INCONCLUSIVE",
    "INFRASTRUCTURE_UNRESOLVED",
]
P12_PRIMARY_ESTIMAND = "INTENTION_TO_EVALUATE_LOWER_BOUND"
INFRASTRUCTURE_RETRY_LIMIT = 3
E_COMMON_COUNT = 30
E_CONTRACT_COUNT = 5

_PROTOCOL_SCHEMA = {
    "schema_version": str,
    "scientific_plan_sha256": str,
    "evidence_design_sha256": str,
    "claims_initial_status": str,
    "rq_spec_sha256": str,
    "claim_ceiling_sha256": str,
    "p12_contract_sha256": str,
    "operator_catalogue_sha256": str,
    "adapter_registry_sha256": str,
    "input_generator_registry_sha256": str,
    "mr_policy_sha256": str,
    "site_policy_sha256": str,
    "analysis_spec_sha256": str,
    "package_policy_sha256": str,
    "environment_lock_sha256": str,
    "profiling_budgets": dict,
    "behavior_category_order": list,
    "technique_order": list,
    "e_common_count": int,
    "e_contract_count": int,
    "p12_outcome_states": list,
    "p12_primary_estimand": str,
    "infrastructure_retry_limit": int,
    "artifact_sha256": str,
}
_PROTOCOL_HASH_FIELDS = (
    "scientific_plan_sha256",
    "evidence_design_sha256",
    "rq_spec_sha256",
    "claim_ceiling_sha256",
    "p12_contract_sha256",
    "operator_catalogue_sha256",
    "adapter_registry_sha256",
    "input_generator_registry_sha256",
    "mr_policy_sha256",
    "site_policy_sha256",
    "analysis_spec_sha256",
    "package_policy_sha256",
    "environment_lock_sha256",
)
_MR_INVENTORY_SCHEMA = {
    "schema_version": str,
    "candidate_frame_sha256": str,
    "custodian_receipt_sha256": str,
    "final_inventory_sha256": str,
    "portfolios_sha256": str,
    "chronology": list,
    "artifact_sha256": str,
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
_CANONICAL_SITE_SCHEMA = {**_SITE_SCHEMA, "site_id": str}
_REVEAL_SCHEMA = {
    "neutral_snapshot_id": str,
    "fixed_git_tree_oid": str,
    "reveal_nonce": str,
    "normalized_source_tree_sha256": str,
}
_ADAPTER_ENTRY_SCHEMA = {
    "adapter_id": str,
    "ecosystem": str,
    "implementation_path": str,
    "source_sha256": str,
}
_ADAPTER_REGISTRY_SCHEMA = {
    "schema_version": str,
    "adapters": list,
    "artifact_sha256": str,
}
_SOURCE_RECORD_SCHEMA = {
    "normalized_source_tree_sha256": str,
    "build_descriptor_sha256": str,
}
def validate_protocol(
    protocol: Mapping[str, Any],
    expected_plan_sha256: str,
    expected_design_sha256: str,
) -> dict[str, Any]:
    value = validate_exact_object(dict(protocol), _PROTOCOL_SCHEMA, "protocol")
    if value["schema_version"] != "p3-protocol-v1":
        raise EvidenceError("E_PROTOCOL", "protocol version differs")
    if value["claims_initial_status"] != "blocked":
        raise EvidenceError("E_PROTOCOL", "claims_initial_status must be blocked")
    for field in _PROTOCOL_HASH_FIELDS:
        validate_sha256(value[field], field)
    validate_sha256(value["artifact_sha256"], "artifact_sha256")
    validate_sha256(expected_plan_sha256, "expected_plan_sha256")
    validate_sha256(expected_design_sha256, "expected_design_sha256")
    body = {key: item for key, item in value.items() if key != "artifact_sha256"}
    if value["artifact_sha256"] != canonical_sha256(body):
        raise EvidenceError("E_PROTOCOL_HASH", "protocol canonical self-hash differs")
    if (
        value["scientific_plan_sha256"] != expected_plan_sha256
        or value["evidence_design_sha256"] != expected_design_sha256
    ):
        raise EvidenceError("E_PROTOCOL_AUTHORITY", "protocol authority hashes differ")
    if value["profiling_budgets"] != PROFILING_BUDGETS:
        raise EvidenceError("E_PROTOCOL", "profiling_budgets differ")
    if value["behavior_category_order"] != BEHAVIOR_CATEGORY_ORDER:
        raise EvidenceError("E_PROTOCOL", "behavior_category_order differs")
    if value["technique_order"] != list(_TECHNIQUE_ORDER):
        raise EvidenceError("E_PROTOCOL", "technique_order differs")
    if value["e_common_count"] != E_COMMON_COUNT or value["e_contract_count"] != E_CONTRACT_COUNT:
        raise EvidenceError("E_PROTOCOL_COUNTS", "evaluation input counts differ")
    if value["p12_outcome_states"] != P12_OUTCOME_STATES:
        raise EvidenceError("E_PROTOCOL_OUTCOMES", "p12_outcome_states order differs")
    if value["p12_primary_estimand"] != P12_PRIMARY_ESTIMAND:
        raise EvidenceError("E_PROTOCOL", "p12_primary_estimand differs")
    if value["infrastructure_retry_limit"] != INFRASTRUCTURE_RETRY_LIMIT:
        raise EvidenceError("E_PROTOCOL_RETRY", "infrastructure_retry_limit differs")
    return value


def validate_mr_inventory(inventory: Mapping[str, Any]) -> dict[str, Any]:
    value = validate_exact_object(dict(inventory), _MR_INVENTORY_SCHEMA, "mr_inventory")
    body = {key: item for key, item in value.items() if key != "artifact_sha256"}
    if value["artifact_sha256"] != canonical_sha256(body):
        raise EvidenceError("E_MR_INVENTORY_HASH", "MR inventory self-hash differs")
    for field in (
        "candidate_frame_sha256",
        "custodian_receipt_sha256",
        "final_inventory_sha256",
        "portfolios_sha256",
    ):
        validate_sha256(value[field], field)
    if value["chronology"] != [
        "candidate_frame",
        "custodian_receipt",
        "final_inventory",
        "portfolios",
    ]:
        raise EvidenceError("E_MR_CHRONOLOGY", "MR freeze chronology differs")
    return value


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


def select_first_applicable_site(
    sites: Sequence[Mapping[str, Any]],
    predicate: Callable[[Mapping[str, Any]], bool],
) -> str | None:
    """Select the first applicable canonical site without transferring the slot."""

    canonical: list[dict[str, Any]] = []
    for index, candidate in enumerate(sites):
        site = validate_exact_object(
            dict(candidate), _CANONICAL_SITE_SCHEMA, f"canonical_sites[{index}]"
        )
        safe_relative_path(site["path"])
        validate_sha256(site["site_id"], f"canonical_sites[{index}].site_id")
        canonical.append(site)
    def order(item: Mapping[str, Any]) -> tuple[Any, ...]:
        return (
            item["path"],
            item["symbol"],
            item["start_line"],
            item["start_col"],
            item["end_line"],
            item["end_col"],
            item["site_id"],
        )
    if canonical != sorted(canonical, key=order):
        raise EvidenceError("E_SITE_ORDER", "sites are not in canonical order")
    for site in canonical:
        applicable = predicate(site)
        if type(applicable) is not bool:
            raise EvidenceError("E_APPLICABILITY_RESULT", "predicate must return bool")
        if applicable:
            return site["site_id"]
    return None


def select_construct_subjects(
    subjects: Sequence[Mapping[str, Any]],
    eligible_subject_ids: set[str],
    *,
    limit: int = 18,
) -> list[str]:
    """Apply the frozen cell order and strict round-robin construction sampling."""

    if type(limit) is not int or limit < 1:
        raise EvidenceError("E_CONSTRUCT_LIMIT", "construct limit must be positive")
    buckets: dict[tuple[str, str], list[tuple[str, str]]] = {}
    observed: set[str] = set()
    for subject in subjects:
        subject_id = validate_sha256(
            subject.get("controlled_subject_id"), "subject.controlled_subject_id"
        )
        if subject_id in observed:
            raise EvidenceError("E_SUBJECT_DUPLICATE", "duplicate controlled subject")
        observed.add(subject_id)
        if subject_id not in eligible_subject_ids:
            continue
        scale = subject.get("scale_class")
        technique = subject.get("primary_technique")
        vector = subject.get("technique_vector")
        if scale not in _SCALES or technique not in _TECHNIQUES or not isinstance(vector, list):
            raise EvidenceError("E_SUBJECT_PROFILE", "subject sampling profile is invalid")
        selection_key = canonical_sha256(
            {
                "controlled_subject_id": subject_id,
                "scale_class": scale,
                "technique_vector": vector,
                "domain": "P3-C1",
            }
        )
        buckets.setdefault((scale, technique), []).append((selection_key, subject_id))
    for bucket in buckets.values():
        bucket.sort()
    selected: list[str] = []
    scale_rank = {value: index for index, value in enumerate(_SCALE_ORDER)}
    technique_rank = {value: index for index, value in enumerate(_TECHNIQUE_ORDER)}
    cells = sorted(
        buckets, key=lambda cell: (scale_rank[cell[0]], technique_rank[cell[1]])
    )
    round_index = 0
    while len(selected) < limit:
        progressed = False
        for cell in cells:
            bucket = buckets[cell]
            if round_index < len(bucket):
                selected.append(bucket[round_index][1])
                progressed = True
                if len(selected) == limit:
                    break
        if not progressed:
            break
        round_index += 1
    return selected


def build_subject_frames(
    verified_bridge: Mapping[str, Any],
    feature_records: Sequence[Mapping[str, Any]],
    construct_limit: int = 18,
    *,
    technique_profile: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    if type(construct_limit) is not int or construct_limit < 1:
        raise EvidenceError("E_CONSTRUCT_LIMIT", "construct limit must be positive")
    derived_primary: str | None = None
    derived_vector: list[str] | None = None
    if technique_profile is not None:
        if not isinstance(technique_profile, Mapping):
            raise EvidenceError("E_TECHNIQUE_PROFILE", "technique_profile must be an object")
        derived_primary = technique_profile.get("primary_technique")
        if derived_primary not in _TECHNIQUES:
            raise EvidenceError("E_TECHNIQUE_PROFILE", "invalid derived primary technique")
        confirmed = technique_profile.get("confirmed_tags")
        if not isinstance(confirmed, list) or any(
            item not in _TECHNIQUES for item in confirmed
        ):
            raise EvidenceError("E_TECHNIQUE_PROFILE", "confirmed_tags must be technique labels")
        derived_vector = sorted(set(confirmed) | {derived_primary})
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
        if derived_primary is not None and derived_vector is not None:
            feature = {
                **feature,
                "primary_technique": derived_primary,
                "technique_vector": list(derived_vector),
            }
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
    selected = select_construct_subjects(
        subjects,
        {subject_id for subject_id, state in eligibility.items() if state["construct"]},
        limit=construct_limit,
    )
    criterion = sorted(
        subject_id for subject_id, state in eligibility.items() if state["criterion"]
    )
    construct_cells = {
        (subject["scale_class"], subject["primary_technique"])
        for subject in subjects
        if eligibility[subject["controlled_subject_id"]]["construct"]
    }
    empty_construct_cells = [
        {
            "scale_class": scale,
            "primary_technique": technique,
            "status": "EMPTY_FRAME",
        }
        for scale in _SCALE_ORDER
        for technique in _TECHNIQUE_ORDER
        if (scale, technique) not in construct_cells
    ]
    body = {
        "schema_version": "p3-subject-frames-v1",
        "subjects": subjects,
        "c_construct": selected,
        "c_criterion": criterion,
        "empty_construct_cells": empty_construct_cells,
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


def validate_adapter_registry(registry: Mapping[str, Any], source_root: str | Path) -> dict[str, Any]:
    value = validate_exact_object(dict(registry), _ADAPTER_REGISTRY_SCHEMA, "adapter_registry")
    if value["schema_version"] != "p3-adapter-registry-v1":
        raise EvidenceError("E_ADAPTER_REGISTRY", "adapter registry version differs")
    body = {key: item for key, item in value.items() if key != "artifact_sha256"}
    if value["artifact_sha256"] != canonical_sha256(body):
        raise EvidenceError("E_ADAPTER_REGISTRY_HASH", "adapter registry self-hash differs")
    adapters = value["adapters"]
    if not isinstance(adapters, list) or len(adapters) != len(CONFIRMATORY_ADAPTERS):
        raise EvidenceError("E_ADAPTER_ALLOWLIST", "adapter registry must list confirmatory adapters exactly")
    root = Path(source_root)
    seen: set[str] = set()
    normalized: list[dict[str, Any]] = []
    for index, candidate in enumerate(adapters):
        entry = validate_exact_object(candidate, _ADAPTER_ENTRY_SCHEMA, f"adapters[{index}]")
        adapter_id = entry["adapter_id"]
        if adapter_id not in CONFIRMATORY_ADAPTERS:
            raise EvidenceError("E_ADAPTER_ALLOWLIST", f"adapter not confirmatory: {adapter_id}")
        if adapter_id in seen:
            raise EvidenceError("E_ADAPTER_DUPLICATE", f"duplicate adapter: {adapter_id}")
        seen.add(adapter_id)
        if entry["ecosystem"] != _ADAPTER_ECOSYSTEMS[adapter_id]:
            raise EvidenceError("E_ADAPTER_ECOSYSTEM", f"ecosystem differs for {adapter_id}")
        relative = safe_relative_path(entry["implementation_path"])
        validate_sha256(entry["source_sha256"], f"adapters[{index}].source_sha256")
        absolute = root / relative.as_posix()
        if not absolute.is_file() or absolute.is_symlink():
            raise EvidenceError(
                "E_ADAPTER_SOURCE",
                f"adapter implementation missing: {entry['implementation_path']}",
            )
        if file_sha256(absolute) != entry["source_sha256"]:
            raise EvidenceError(
                "E_ADAPTER_SOURCE_HASH",
                f"adapter source hash differs: {adapter_id}",
            )
        normalized.append(entry)
    if seen != CONFIRMATORY_ADAPTERS:
        raise EvidenceError("E_ADAPTER_ALLOWLIST", "confirmatory adapter set differs")
    return {
        "schema_version": value["schema_version"],
        "adapters": normalized,
        "artifact_sha256": value["artifact_sha256"],
    }


def _controlled_subject_source_id(source_record: Mapping[str, Any]) -> str:
    return canonical_sha256(
        {
            "normalized_source_tree_sha256": source_record["normalized_source_tree_sha256"],
            "build_descriptor_sha256": source_record["build_descriptor_sha256"],
            "domain": "P3-SOURCE-v1",
        }
    )


def _ecosystem_to_adapter(registry: Mapping[str, Any]) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for entry in registry["adapters"]:
        mapping[entry["ecosystem"]] = entry["adapter_id"]
    return mapping


def _declaration_is_structurally_valid(declaration: Mapping[str, Any]) -> tuple[bool, str]:
    category = declaration.get("category")
    if category not in _BEHAVIOR_CATEGORIES:
        return False, "category is not a frozen behavior category"
    entrypoint = declaration.get("entrypoint")
    normalized = declaration.get("normalized_entrypoint")
    if not isinstance(entrypoint, str) or not entrypoint:
        return False, "entrypoint is empty"
    if not isinstance(normalized, str) or not normalized:
        return False, "normalized_entrypoint is empty"
    try:
        validate_sha256(
            declaration.get("declared_input_schema_sha256"),
            "declared_input_schema_sha256",
        )
    except EvidenceError:
        return False, "declared_input_schema_sha256 is invalid"
    tags = declaration.get("static_dependency_tags")
    if not isinstance(tags, list) or any(not isinstance(tag, str) for tag in tags):
        return False, "static_dependency_tags must be a string list"
    prerequisites = declaration.get("prerequisites")
    if not isinstance(prerequisites, list) or any(not isinstance(item, str) for item in prerequisites):
        return False, "prerequisites must be a string list"
    if "declared_inputs" not in declaration:
        return False, "declared_inputs missing"
    span = declaration.get("provenance_span_or_key")
    if not isinstance(span, str) or not span:
        return False, "provenance_span_or_key missing"
    return True, ""


def _diversity_signature(row: Mapping[str, Any]) -> str:
    return canonical_sha256(
        {
            "category": row["category"],
            "normalized_entrypoint": row["normalized_entrypoint"],
            "sorted_static_dependency_tags": sorted(set(row["static_dependency_tags"])),
            "declared_input_schema_sha256": row["declared_input_schema_sha256"],
            "domain": "P3-PROFILE-DIVERSITY-v1",
        }
    )


def _behavior_id(source_id: str, row: Mapping[str, Any]) -> str:
    return canonical_sha256(
        {
            "controlled_subject_source_id": source_id,
            "category": row["category"],
            "provenance_path": row["provenance_path"],
            "provenance_span_or_key": row["provenance_span_or_key"],
            "normalized_entrypoint": row["normalized_entrypoint"],
            "domain": "P3-BEHAVIOR-v1",
        }
    )


def build_public_behavior_frame(
    source_record: Mapping[str, Any],
    declarations: Sequence[Mapping[str, Any]],
    adapter_registry: Mapping[str, Any],
) -> dict[str, Any]:
    source = validate_exact_object(dict(source_record), _SOURCE_RECORD_SCHEMA, "source_record")
    validate_sha256(source["normalized_source_tree_sha256"], "normalized_source_tree_sha256")
    validate_sha256(source["build_descriptor_sha256"], "build_descriptor_sha256")
    registry = validate_exact_object(
        dict(adapter_registry), _ADAPTER_REGISTRY_SCHEMA, "adapter_registry"
    )
    if {entry["adapter_id"] for entry in registry["adapters"]} != CONFIRMATORY_ADAPTERS:
        raise EvidenceError("E_ADAPTER_ALLOWLIST", "adapter registry is incomplete")
    ecosystem_adapters = _ecosystem_to_adapter(registry)
    source_id = _controlled_subject_source_id(source)
    rows: list[dict[str, Any]] = []
    for index, raw in enumerate(declarations):
        if not isinstance(raw, Mapping):
            raise EvidenceError("E_DECLARATION", f"declarations[{index}] must be an object")
        declaration = dict(raw)
        provenance_path = declaration.get("provenance_path")
        if not isinstance(provenance_path, str) or not provenance_path.strip():
            raise EvidenceError("E_PROVENANCE", f"declarations[{index}] lacks public provenance")
        safe_relative_path(provenance_path)
        provenance_span = declaration.get("provenance_span_or_key")
        if not isinstance(provenance_span, str):
            provenance_span = ""
        ecosystem = declaration.get("ecosystem")
        if not isinstance(ecosystem, str) or not ecosystem:
            raise EvidenceError("E_DECLARATION", f"declarations[{index}] ecosystem missing")
        valid, reason = _declaration_is_structurally_valid(declaration)
        adapter_id = ecosystem_adapters.get(ecosystem)
        if adapter_id is None:
            discovery_status = "ADAPTER_UNSUPPORTED"
            exclusion = "ecosystem has no confirmatory adapter; hand-selected commands are forbidden"
            diversity = None
            behavior_fields = {
                "category": declaration.get("category")
                if declaration.get("category") in _BEHAVIOR_CATEGORIES
                else "PUBLIC_API",
                "entrypoint": declaration.get("entrypoint")
                if isinstance(declaration.get("entrypoint"), str)
                else "",
                "normalized_entrypoint": declaration.get("normalized_entrypoint")
                if isinstance(declaration.get("normalized_entrypoint"), str)
                else "",
                "declared_inputs": declaration.get("declared_inputs", {}),
                "declared_input_schema_sha256": declaration.get("declared_input_schema_sha256")
                if isinstance(declaration.get("declared_input_schema_sha256"), str)
                else "0" * 64,
                "static_dependency_tags": list(declaration.get("static_dependency_tags") or []),
                "prerequisites": list(declaration.get("prerequisites") or []),
            }
            if behavior_fields["category"] not in _BEHAVIOR_CATEGORIES:
                behavior_fields["category"] = "PUBLIC_API"
        elif not valid:
            discovery_status = "INVALID_DECLARATION"
            exclusion = reason or "declaration is invalid"
            diversity = None
            behavior_fields = {
                "category": declaration["category"]
                if declaration.get("category") in _BEHAVIOR_CATEGORIES
                else "PUBLIC_API",
                "entrypoint": declaration.get("entrypoint")
                if isinstance(declaration.get("entrypoint"), str)
                else "",
                "normalized_entrypoint": declaration.get("normalized_entrypoint")
                if isinstance(declaration.get("normalized_entrypoint"), str)
                else "",
                "declared_inputs": declaration.get("declared_inputs", {}),
                "declared_input_schema_sha256": declaration.get("declared_input_schema_sha256")
                if isinstance(declaration.get("declared_input_schema_sha256"), str)
                and len(str(declaration.get("declared_input_schema_sha256"))) == 64
                else "0" * 64,
                "static_dependency_tags": [
                    tag
                    for tag in list(declaration.get("static_dependency_tags") or [])
                    if isinstance(tag, str)
                ],
                "prerequisites": [
                    item
                    for item in list(declaration.get("prerequisites") or [])
                    if isinstance(item, str)
                ],
            }
        else:
            discovery_status = "EXECUTABLE"
            exclusion = ""
            behavior_fields = {
                "category": declaration["category"],
                "entrypoint": declaration["entrypoint"],
                "normalized_entrypoint": declaration["normalized_entrypoint"],
                "declared_inputs": declaration["declared_inputs"],
                "declared_input_schema_sha256": validate_sha256(
                    declaration["declared_input_schema_sha256"],
                    "declared_input_schema_sha256",
                ),
                "static_dependency_tags": list(declaration["static_dependency_tags"]),
                "prerequisites": list(declaration["prerequisites"]),
            }
            diversity = _diversity_signature(behavior_fields)
        row_body = {
            "controlled_subject_source_id": source_id,
            "category": behavior_fields["category"],
            "provenance_path": provenance_path,
            "provenance_span_or_key": provenance_span,
            "entrypoint": behavior_fields["entrypoint"],
            "normalized_entrypoint": behavior_fields["normalized_entrypoint"],
            "declared_inputs": behavior_fields["declared_inputs"],
            "declared_input_schema_sha256": behavior_fields["declared_input_schema_sha256"],
            "static_dependency_tags": sorted(set(behavior_fields["static_dependency_tags"]))
            if discovery_status == "EXECUTABLE"
            else list(behavior_fields["static_dependency_tags"]),
            "prerequisites": list(behavior_fields["prerequisites"]),
            "ecosystem": ecosystem,
            "adapter_id": adapter_id,
            "discovery_status": discovery_status,
            "unsupported_or_exclusion_reason": exclusion,
            "diversity_signature_sha256": diversity,
        }
        behavior_id = _behavior_id(source_id, row_body)
        row = {**row_body, "behavior_id": behavior_id}
        row_hash_body = {key: value for key, value in row.items()}
        rows.append({**row, "artifact_sha256": canonical_sha256(row_hash_body)})

    rows.sort(
        key=lambda item: (
            BEHAVIOR_CATEGORY_ORDER.index(item["category"])
            if item["category"] in _BEHAVIOR_CATEGORIES
            else len(BEHAVIOR_CATEGORY_ORDER),
            item["provenance_path"],
            item["provenance_span_or_key"],
            item["normalized_entrypoint"],
            item["behavior_id"],
        )
    )
    accounting = []
    for category in BEHAVIOR_CATEGORY_ORDER:
        category_rows = [row for row in rows if row["category"] == category]
        accounting.append(
            {
                "category": category,
                "discovered_count": len(category_rows),
                "executable_count": sum(
                    1 for row in category_rows if row["discovery_status"] == "EXECUTABLE"
                ),
                "adapter_unsupported_count": sum(
                    1
                    for row in category_rows
                    if row["discovery_status"] == "ADAPTER_UNSUPPORTED"
                ),
                "invalid_count": sum(
                    1
                    for row in category_rows
                    if row["discovery_status"] == "INVALID_DECLARATION"
                ),
            }
        )
    body = {
        "schema_version": "p3-public-behavior-frame-v1",
        "controlled_subject_source_id": source_id,
        "category_accounting": accounting,
        "rows": rows,
    }
    return {**body, "artifact_sha256": canonical_sha256(body)}


def select_profiling_workload(frame: Mapping[str, Any], scale_class: str) -> dict[str, Any]:
    if scale_class not in PROFILING_BUDGETS:
        raise EvidenceError("E_SCALE", f"invalid scale_class: {scale_class}")
    if not isinstance(frame, Mapping) or "rows" not in frame:
        raise EvidenceError("E_FRAME", "public behavior frame rows are absent")
    budget = PROFILING_BUDGETS[scale_class]
    source_id = frame.get("controlled_subject_source_id")
    validate_sha256(source_id, "controlled_subject_source_id")
    buckets: dict[str, list[dict[str, Any]]] = {category: [] for category in BEHAVIOR_CATEGORY_ORDER}
    for index, candidate in enumerate(frame["rows"]):
        if not isinstance(candidate, Mapping):
            raise EvidenceError("E_FRAME_ROW", f"rows[{index}] must be an object")
        if candidate.get("discovery_status") != "EXECUTABLE":
            continue
        category = candidate.get("category")
        if category not in _BEHAVIOR_CATEGORIES:
            raise EvidenceError("E_FRAME_ROW", f"rows[{index}] category is invalid")
        behavior_id = validate_sha256(candidate.get("behavior_id"), f"rows[{index}].behavior_id")
        diversity = candidate.get("diversity_signature_sha256")
        if not isinstance(diversity, str):
            diversity = _diversity_signature(candidate)
        else:
            validate_sha256(diversity, f"rows[{index}].diversity_signature_sha256")
        buckets[category].append(
            {
                "behavior_id": behavior_id,
                "category": category,
                "diversity_signature_sha256": diversity,
                "normalized_entrypoint": candidate.get("normalized_entrypoint"),
                "declared_input_schema_sha256": candidate.get("declared_input_schema_sha256"),
                "static_dependency_tags": list(candidate.get("static_dependency_tags") or []),
                "provenance_path": candidate.get("provenance_path"),
                "provenance_span_or_key": candidate.get("provenance_span_or_key"),
                "entrypoint": candidate.get("entrypoint"),
            }
        )
    for category, items in buckets.items():
        items.sort(key=lambda item: (item["diversity_signature_sha256"], item["behavior_id"]))
    selected: list[dict[str, Any]] = []
    selected_ids: list[str] = []
    selected_set: set[str] = set()
    seen_diversity: set[str] = set()
    # First pass: one lowest row from each nonempty executable category.
    for category in BEHAVIOR_CATEGORY_ORDER:
        if len(selected) >= budget:
            break
        bucket = buckets[category]
        if not bucket:
            continue
        choice = bucket[0]
        selected.append(choice)
        selected_ids.append(choice["behavior_id"])
        selected_set.add(choice["behavior_id"])
        seen_diversity.add(choice["diversity_signature_sha256"])
    # Subsequent passes: prefer unseen diversity signatures, then lowest behavior_id.
    while len(selected) < budget:
        progressed = False
        for category in BEHAVIOR_CATEGORY_ORDER:
            if len(selected) >= budget:
                break
            remaining = [
                item for item in buckets[category] if item["behavior_id"] not in selected_set
            ]
            if not remaining:
                continue
            unseen = [
                item
                for item in remaining
                if item["diversity_signature_sha256"] not in seen_diversity
            ]
            pool = unseen if unseen else remaining
            pool.sort(key=lambda item: (item["diversity_signature_sha256"], item["behavior_id"]))
            choice = pool[0]
            selected.append(choice)
            selected_ids.append(choice["behavior_id"])
            selected_set.add(choice["behavior_id"])
            seen_diversity.add(choice["diversity_signature_sha256"])
            progressed = True
        if not progressed:
            break
    counts = {
        category: sum(1 for item in selected if item["category"] == category)
        for category in BEHAVIOR_CATEGORY_ORDER
        if any(item["category"] == category for item in selected)
    }
    body = {
        "schema_version": "p3-profiling-workload-v1",
        "controlled_subject_source_id": source_id,
        "scale_class": scale_class,
        "budget": budget,
        "category_order": list(BEHAVIOR_CATEGORY_ORDER),
        "selected_rows": selected,
        "selected_behavior_ids": selected_ids,
        "selected_category_counts": counts,
    }
    return {**body, "artifact_sha256": canonical_sha256(body)}


def _serialize_fraction(value: Fraction) -> str:
    text = format(Decimal(value.numerator) / Decimal(value.denominator), "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text or "0"


def classify_technique(
    workload: Mapping[str, Any],
    profiling_results: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    if not isinstance(workload, Mapping):
        raise EvidenceError("E_WORKLOAD", "profiling workload must be an object")
    selected_rows = workload.get("selected_rows")
    if not isinstance(selected_rows, list):
        raise EvidenceError("E_WORKLOAD", "selected_rows are absent")
    selected: list[dict[str, Any]] = []
    selected_ids: list[str] = []
    seen_ids: set[str] = set()
    for index, candidate in enumerate(selected_rows):
        if not isinstance(candidate, Mapping):
            raise EvidenceError("E_WORKLOAD_ROW", f"selected_rows[{index}] must be an object")
        behavior_id = validate_sha256(
            candidate.get("behavior_id"), f"selected_rows[{index}].behavior_id"
        )
        category = candidate.get("category")
        if category not in _BEHAVIOR_CATEGORIES:
            raise EvidenceError("E_WORKLOAD_ROW", f"selected_rows[{index}] category is invalid")
        if behavior_id in seen_ids:
            raise EvidenceError("E_WORKLOAD_ROW", f"duplicate selected behavior: {behavior_id}")
        seen_ids.add(behavior_id)
        selected.append({"behavior_id": behavior_id, "category": category})
        selected_ids.append(behavior_id)
    if not isinstance(profiling_results, Sequence) or isinstance(profiling_results, (str, bytes)):
        raise EvidenceError("E_PROFILE_RESULTS", "profiling_results must be a sequence")
    results_by_id: dict[str, Mapping[str, Any]] = {}
    for index, candidate in enumerate(profiling_results):
        if not isinstance(candidate, Mapping):
            raise EvidenceError("E_PROFILE_RESULTS", f"profiling_results[{index}] must be an object")
        behavior_id = validate_sha256(
            candidate.get("behavior_id"), f"profiling_results[{index}].behavior_id"
        )
        if behavior_id not in seen_ids:
            raise EvidenceError(
                "E_PROFILE_RESULTS",
                f"result behavior is not in workload: {behavior_id}",
            )
        if behavior_id in results_by_id:
            raise EvidenceError("E_PROFILE_RESULTS", f"duplicate result: {behavior_id}")
        results_by_id[behavior_id] = candidate
    if set(results_by_id) != seen_ids:
        missing = sorted(seen_ids - set(results_by_id))
        raise EvidenceError(
            "E_PROFILE_RESULTS",
            f"profiling results do not cover selected rows: {missing[0]}",
        )

    categories = [
        category
        for category in BEHAVIOR_CATEGORY_ORDER
        if any(row["category"] == category for row in selected)
    ]
    if not categories:
        return {
            "lower_scores": {},
            "upper_scores": {},
            "confirmed_tags": [],
            "possible_tags": [],
            "primary_technique": "TECH_UNCERTAIN",
            "category_funnel": [],
        }

    category_size = Fraction(len(categories))
    lower: dict[str, Fraction] = {technique: Fraction(0) for technique in _PROFILE_TECHNIQUES}
    upper: dict[str, Fraction] = {technique: Fraction(0) for technique in _PROFILE_TECHNIQUES}
    funnel: list[dict[str, Any]] = []
    unresolved_total = 0
    missing_success_category = False

    for category in categories:
        category_rows = [row for row in selected if row["category"] == category]
        n_c = len(category_rows)
        success_count = 0
        unresolved_count = 0
        technique_counts = {technique: 0 for technique in _PROFILE_TECHNIQUES}
        for row in category_rows:
            result = results_by_id[row["behavior_id"]]
            status = result.get("status")
            tags = result.get("technique_tags")
            if status in _UNRESOLVED_STATUSES:
                unresolved_count += 1
                continue
            if status != "SUCCESS":
                raise EvidenceError(
                    "E_PROFILE_RESULTS",
                    f"unsupported profiling status for {row['behavior_id']}: {status!r}",
                )
            success_count += 1
            if tags is None:
                tags = []
            if not isinstance(tags, list) or any(not isinstance(tag, str) for tag in tags):
                raise EvidenceError(
                    "E_PROFILE_RESULTS",
                    f"technique_tags must be a string list for {row['behavior_id']}",
                )
            for tag in tags:
                if tag == "TECH_UNCERTAIN":
                    continue
                if tag not in _TECHNIQUES:
                    raise EvidenceError(
                        "E_PROFILE_RESULTS",
                        f"unknown technique tag for {row['behavior_id']}: {tag}",
                    )
                technique_counts[tag] += 1
        if success_count == 0:
            missing_success_category = True
        unresolved_total += unresolved_count
        n_fraction = Fraction(n_c)
        for technique in _PROFILE_TECHNIQUES:
            a_ct = Fraction(technique_counts[technique])
            lower[technique] += (a_ct / n_fraction) / category_size
            upper[technique] += ((a_ct + Fraction(unresolved_count)) / n_fraction) / category_size
        funnel.append(
            {
                "category": category,
                "n_c": n_c,
                "successful_count": success_count,
                "unresolved_count": unresolved_count,
                "technique_counts": {
                    technique: count
                    for technique, count in technique_counts.items()
                    if count > 0
                },
            }
        )

    confirmed_tags = [
        technique for technique in _PROFILE_TECHNIQUES if lower[technique] > 0
    ]
    possible_tags = [
        technique for technique in _PROFILE_TECHNIQUES if upper[technique] > 0
    ]
    lower_scores = {
        technique: _serialize_fraction(lower[technique]) for technique in confirmed_tags
    }
    upper_scores = {
        technique: _serialize_fraction(upper[technique]) for technique in possible_tags
    }

    if missing_success_category:
        primary = "TECH_UNCERTAIN"
    elif unresolved_total == 0:
        best_score = max((lower[technique] for technique in _PROFILE_TECHNIQUES), default=Fraction(0))
        if best_score <= 0:
            primary = "TECH_UNCERTAIN"
        else:
            winners = [
                technique
                for technique in _PROFILE_TECHNIQUES
                if lower[technique] == best_score
            ]
            primary = winners[0]
    else:
        primary = "TECH_UNCERTAIN"
        for technique in _PROFILE_TECHNIQUES:
            rival_upper = max(
                (
                    upper[other]
                    for other in _PROFILE_TECHNIQUES
                    if other != technique
                ),
                default=Fraction(0),
            )
            if lower[technique] > rival_upper:
                primary = technique
                break

    return {
        "lower_scores": lower_scores,
        "upper_scores": upper_scores,
        "confirmed_tags": confirmed_tags,
        "possible_tags": possible_tags,
        "primary_technique": primary,
        "category_funnel": funnel,
    }
