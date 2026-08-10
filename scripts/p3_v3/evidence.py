#!/usr/bin/env python3
"""Thin CLI for the P3 v3 minimum evidence foundation."""

from __future__ import annotations

import argparse
import stat
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from p3_v3.artifacts import (  # noqa: E402
    EvidenceError,
    canonical_json_bytes,
    canonical_sha256,
    file_sha256,
    read_canonical_json,
    validate_exact_object,
    validate_sha256,
    safe_relative_path,
    write_canonical_json,
)
from p3_v3.bridge_and_frames import (  # noqa: E402
    build_contract_inputs,
    build_subject_frames,
    close_slot,
    derive_subject_material,
    validate_adapter_registry,
    validate_contract_generator_registry,
    validate_input_generator_registry,
    validate_mr_inventory,
    validate_protocol,
    verify_pinned_bridge,
    verify_slot_chronology,
)
from p3_v3.packages import (  # noqa: E402
    PACKAGE_B_PRIMARY_CLASSES,
    PACKAGE_B_SENSITIVITY_CLASSES,
    build_package,
    verify_common_input_evidence,
    verify_materialized_package,
    verify_package,
)
from p3_v3.preflight import run_preflight  # noqa: E402
from p3_v3.run_records import (  # noqa: E402
    close_phase,
    verify_attempt_tree,
    verify_ledger,
    verify_phase_receipt,
)

SCIENTIFIC_PLAN_SHA256 = "fea00496801c31ba074aa74742f5e6a77019ffc2e344642122a15462d7443830"
EVIDENCE_DESIGN_SHA256 = "7e614e96aac833786d1b29580f8fae7d3f03c6567d7ca94f3e3c017addad2fa9"


def _write(payload: dict) -> None:
    sys.stdout.buffer.write(canonical_json_bytes(payload))


def _write_output(path: str | None, payload: dict) -> None:
    if path:
        write_canonical_json(path, payload, exclusive=True)


def _write_under(output_root: Path, name: str, payload: Any) -> None:
    target = output_root / name
    if target.resolve().parent != output_root.resolve():
        raise EvidenceError("E_OUTPUT_ROOT", f"refusing to write outside output-root: {name}")
    write_canonical_json(target, payload, exclusive=True)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    command = sub.add_parser("validate-protocol")
    command.add_argument("--protocol", required=True)
    command = sub.add_parser("verify-bridge")
    command.add_argument("--repo-root", required=True)
    command.add_argument("--lock", required=True)
    command.add_argument("--output")
    command = sub.add_parser("build-frames")
    command.add_argument("--bridge", required=True)
    command.add_argument("--subject-specs", required=True)
    command.add_argument("--adapter-root", required=True)
    command.add_argument("--generator-root", required=True)
    command.add_argument("--slots", required=True)
    command.add_argument("--contracts", required=True)
    command.add_argument("--applicability-map", required=True)
    command.add_argument("--output-root", required=True)
    command.add_argument("--contract-generator-registry")
    command.add_argument("--contract-generator-root")
    command = sub.add_parser("verify-mr-inventory")
    command.add_argument("--candidate-frame", required=True)
    command.add_argument("--custodian-receipt", required=True)
    command.add_argument("--final-inventory", required=True)
    command.add_argument("--portfolios", required=True)
    command = sub.add_parser("build-package")
    command.add_argument("--role", required=True)
    command.add_argument("--root", required=True)
    command.add_argument("--specs", required=True)
    command.add_argument("--parents", required=True)
    command.add_argument("--output", required=True)
    command.add_argument("--allowed-classes")
    command = sub.add_parser("verify-package")
    command.add_argument("--root", required=True)
    command.add_argument("--manifest", required=True)
    command = sub.add_parser("run-preflight")
    command.add_argument("--root", required=True)
    command.add_argument("--spec", required=True)
    command.add_argument("--output")
    command = sub.add_parser("verify-run-records")
    command.add_argument("--ledger", required=True)
    command = sub.add_parser("close-phase")
    command.add_argument("--phase-id", required=True)
    command.add_argument("--protocol-sha256", required=True)
    command.add_argument("--expected-jobs", required=True)
    command.add_argument("--ledger", required=True)
    command.add_argument("--output-manifest-sha256", required=True)
    command.add_argument("--output", required=True)
    command = sub.add_parser("verify-evidence")
    command.add_argument("--index", required=True)
    return parser


_SUBJECT_SPEC_SCHEMA = {
    "neutral_snapshot_id": str,
    "source_root": str,
    "source_record": dict,
    "build_descriptor": dict,
    "adapter_registry": dict,
    "input_generator_registry": dict,
    "profiling_results": dict,
}


def _subject_specs_by_neutral(
    bridge: Mapping[str, Any], subject_specs: Any
) -> list[tuple[dict[str, Any], Mapping[str, Any]]]:
    records = bridge.get("records") if isinstance(bridge, Mapping) else None
    if not isinstance(records, list):
        raise EvidenceError("E_BRIDGE_RECORDS", "verified bridge records are absent")
    records_by_neutral: dict[str, Mapping[str, Any]] = {}
    for index, record in enumerate(records):
        if not isinstance(record, Mapping):
            raise EvidenceError("E_BRIDGE_RECORDS", f"records[{index}] must be an object")
        neutral = validate_sha256(
            record.get("neutral_snapshot_id"), f"records[{index}].neutral_snapshot_id"
        )
        if neutral in records_by_neutral:
            raise EvidenceError("E_BRIDGE_RECORDS", "duplicate bridge neutral ID")
        records_by_neutral[neutral] = record
    if not isinstance(subject_specs, list):
        raise EvidenceError("E_SUBJECT_SPEC", "subject-specs must be a list")
    specs_by_neutral: dict[str, dict[str, Any]] = {}
    for index, candidate in enumerate(subject_specs):
        if not isinstance(candidate, Mapping):
            raise EvidenceError("E_SUBJECT_SPEC", f"subject_specs[{index}] must be an object")
        spec = validate_exact_object(
            dict(candidate), _SUBJECT_SPEC_SCHEMA, f"subject_specs[{index}]"
        )
        neutral = validate_sha256(
            spec["neutral_snapshot_id"], f"subject_specs[{index}].neutral_snapshot_id"
        )
        if neutral in specs_by_neutral:
            raise EvidenceError(
                "E_SUBJECT_SPEC_COVERAGE", f"duplicate subject specification: {neutral}"
            )
        specs_by_neutral[neutral] = spec
    if set(specs_by_neutral) != set(records_by_neutral):
        raise EvidenceError(
            "E_SUBJECT_SPEC_COVERAGE",
            "subject specifications do not cover bridge exactly",
        )
    return [
        (specs_by_neutral[neutral], records_by_neutral[neutral])
        for neutral in sorted(records_by_neutral)
    ]


def _dispatch_build_frames(args: argparse.Namespace) -> dict:
    bridge = read_canonical_json(args.bridge)
    indexed_specs = _subject_specs_by_neutral(
        bridge, read_canonical_json(args.subject_specs)
    )
    derived_subjects = []
    for spec, record in indexed_specs:
        prepared = {
            **spec,
            "adapter_registry": validate_adapter_registry(
                spec["adapter_registry"], args.adapter_root
            ),
            "input_generator_registry": validate_input_generator_registry(
                spec["input_generator_registry"], args.generator_root
            ),
        }
        derived_subjects.append(derive_subject_material(prepared, record))
    subject_frames = build_subject_frames(bridge, derived_subjects)

    output_root = Path(args.output_root)
    output_root.mkdir(parents=True, exist_ok=True)
    written = []
    artifact_names = {
        "adapter_discovery": "adapter-discovery",
        "source_scale": "source-scale",
        "public_behavior_frame": "public-behavior-frame",
        "profiling_workload": "profiling-workload",
        "common_inputs": "evaluation-inputs-common",
        "profiling_results": "profiling-results",
        "technique_profile": "technique-profile",
    }
    for material in derived_subjects:
        neutral = material["neutral_snapshot_id"]
        for field, stem in artifact_names.items():
            name = f"{stem}-{neutral}.json"
            _write_under(output_root, name, material[field])
            written.append(name)
        name = f"derived-subject-{neutral}.json"
        _write_under(output_root, name, material)
        written.append(name)
    _write_under(output_root, "subject-frames.json", subject_frames)
    written.append("subject-frames.json")

    slots = read_canonical_json(args.slots)
    contracts = read_canonical_json(args.contracts)
    applicability_map = read_canonical_json(args.applicability_map)
    if not isinstance(slots, list):
        raise EvidenceError("E_SLOTS", "slots must be a list")
    if not isinstance(contracts, Mapping):
        raise EvidenceError("E_CONTRACTS", "contracts must be an object")
    if not isinstance(applicability_map, Mapping):
        raise EvidenceError("E_APPLICABILITY", "applicability-map must be an object")
    subjects_by_id = {
        subject["controlled_subject_id"]: subject for subject in subject_frames["subjects"]
    }
    contract_registry = None
    for index, slot in enumerate(slots):
        if not isinstance(slot, Mapping):
            raise EvidenceError("E_SLOTS", f"slots[{index}] must be an object")
        subject = subjects_by_id.get(slot.get("controlled_subject_id"))
        if subject is None:
            raise EvidenceError(
                "E_SLOTS",
                f"slots[{index}] controlled_subject_id is not in subject frames",
            )
        sites = subject["sites"]

        def predicate(site: Mapping[str, Any], _map=applicability_map) -> bool:
            value = _map.get(site["site_id"], False)
            if type(value) is not bool:
                raise EvidenceError(
                    "E_APPLICABILITY",
                    f"applicability for {site['site_id']} must be bool",
                )
            return value

        closure = close_slot(slot, sites, predicate)
        slot_name = f"slot-closure-{closure['slot_id']}.json"
        _write_under(output_root, slot_name, closure)
        written.append(slot_name)
        if closure["path"] != "APPLICABLE":
            continue
        contract = contracts.get(closure["slot_id"])
        if contract is None:
            continue
        if contract_registry is None:
            if not args.contract_generator_registry or not args.contract_generator_root:
                raise EvidenceError(
                    "E_CONTRACT_GENERATOR",
                    "applicable slot contracts require --contract-generator-registry/root",
                )
            contract_registry = validate_contract_generator_registry(
                read_canonical_json(args.contract_generator_registry),
                args.contract_generator_root,
            )
        inventory = build_contract_inputs(closure, contract, contract_registry)
        contract_name = f"evaluation-inputs-contract-{closure['slot_id']}.json"
        _write_under(output_root, contract_name, inventory)
        written.append(contract_name)
    return {
        "status": "PASS",
        "output_root": str(output_root),
        "artifacts": sorted(written),
        "common_input_count": sum(
            len(material["common_inputs"]["rows"])
            for material in derived_subjects
        ),
        "subject_count": len(subject_frames["subjects"]),
    }


_INDEX_SCHEMA = {
    "schema_version": str,
    "phase_coverage": list,
    "protocol": dict,
    "adapter_registries": list,
    "input_generator_registries": list,
    "subjects": list,
    "packages": list,
    "mr_chain": dict,
    "job_root": str,
    "ledger": dict,
    "phase_receipts": list,
    "p12": dict,
    "claims": dict,
    "artifact_sha256": str,
}
_REFERENCE_SCHEMA = {"path": str, "sha256": str}
_SUBJECT_INDEX_SCHEMA = {
    "phase": str,
    "controlled_subject_source_id": str,
    "controlled_subject_id": str,
    "public_frame": dict,
    "profiling_workload": dict,
    "profiling_results": dict,
    "common_inputs": dict,
    "common_input_validity": dict,
    "slot_artifacts": list,
}
_SLOT_INDEX_SCHEMA = {
    "slot_id": str,
    "controlled_subject_id": str,
    "artifact": dict,
}
_PACKAGE_INDEX_SCHEMA = {
    "phase": str,
    "input_role": str,
    "root": str,
    "manifest": dict,
}
_RECEIPT_INDEX_SCHEMA = {
    "phase": str,
    "receipt": dict,
    "expected_jobs": dict,
    "output_manifest": dict,
}
_MR_CHAIN_INDEX_SCHEMA = {
    "candidate_frame": dict,
    "custodian_receipt": dict,
    "final_inventory": dict,
    "portfolios": dict,
}
_P12_INDEX_SCHEMA = {"denominator": dict, "result_rows": dict, "summary": dict}
_PHASES = tuple(f"PHASE_{number}" for number in range(8))


def _indexed_directory(root: Path, relative: Any, seen: set[str], context: str) -> Path:
    normalized = safe_relative_path(relative).as_posix()
    if normalized in seen:
        raise EvidenceError("E_INDEX_DUPLICATE", f"duplicate indexed path: {normalized}")
    seen.add(normalized)
    path = root / normalized
    try:
        info = path.lstat()
    except FileNotFoundError as exc:
        raise EvidenceError("E_INDEX_PATH", f"missing indexed directory: {normalized}") from exc
    if path.is_symlink() or not stat.S_ISDIR(info.st_mode):
        raise EvidenceError("E_INDEX_PATH", f"indexed directory is unsafe: {normalized}")
    return path


def _indexed_file(
    root: Path,
    candidate: Any,
    seen: set[str],
    loaded: dict[str, Any],
    context: str,
    *,
    canonical: bool = True,
) -> tuple[Path, Any]:
    reference = validate_exact_object(candidate, _REFERENCE_SCHEMA, context)
    relative = safe_relative_path(reference["path"]).as_posix()
    validate_sha256(reference["sha256"], f"{context}.sha256")
    if relative in seen:
        raise EvidenceError("E_INDEX_DUPLICATE", f"duplicate indexed path: {relative}")
    seen.add(relative)
    path = root / relative
    try:
        info = path.lstat()
    except FileNotFoundError as exc:
        raise EvidenceError("E_INDEX_PATH", f"missing indexed file: {relative}") from exc
    if path.is_symlink() or not stat.S_ISREG(info.st_mode):
        raise EvidenceError("E_INDEX_PATH", f"indexed file is unsafe: {relative}")
    if file_sha256(path) != reference["sha256"]:
        raise EvidenceError("E_INDEX_FILE_HASH", f"indexed bytes differ: {relative}")
    value = read_canonical_json(path) if canonical else None
    loaded[relative] = value
    return path, value


def _phase(value: Any, coverage: list[str], context: str) -> str:
    if type(value) is not str or value not in _PHASES or value not in coverage:
        raise EvidenceError("E_INDEX_PHASE", f"{context} has an unknown phase")
    return value


def _load_evidence_index(index_path: str | Path) -> tuple[dict[str, Any], dict[str, Any]]:
    source = Path(index_path)
    value = validate_exact_object(read_canonical_json(source), _INDEX_SCHEMA, "evidence_index")
    if value["schema_version"] != "P3_V3_EVIDENCE_INDEX_V1":
        raise EvidenceError("E_INDEX_SCHEMA", "evidence index schema version differs")
    body = {key: item for key, item in value.items() if key != "artifact_sha256"}
    validate_sha256(value["artifact_sha256"], "evidence_index.artifact_sha256")
    if value["artifact_sha256"] != canonical_sha256(body):
        raise EvidenceError("E_INDEX_HASH", "evidence index self-hash differs")
    coverage = value["phase_coverage"]
    if any(type(item) is not str or item not in _PHASES for item in coverage):
        raise EvidenceError("E_INDEX_PHASE", "phase coverage contains an unknown phase")
    if coverage != sorted(set(coverage), key=_PHASES.index):
        raise EvidenceError("E_INDEX_PHASE", "phase coverage is not sorted and unique")

    root = source.parent
    seen: set[str] = set()
    loaded: dict[str, Any] = {}
    protocol_path, protocol = _indexed_file(root, value["protocol"], seen, loaded, "protocol")
    ledger_path, _ = _indexed_file(
        root, value["ledger"], seen, loaded, "ledger", canonical=False
    )
    claims_path, claims = _indexed_file(root, value["claims"], seen, loaded, "claims")
    job_root = _indexed_directory(root, value["job_root"], seen, "job_root")

    for collection_name in ("adapter_registries", "input_generator_registries"):
        for index, reference in enumerate(value[collection_name]):
            _indexed_file(root, reference, seen, loaded, f"{collection_name}[{index}]")

    subjects: list[dict[str, Any]] = []
    for index, candidate in enumerate(value["subjects"]):
        subject = validate_exact_object(candidate, _SUBJECT_INDEX_SCHEMA, f"subjects[{index}]")
        _phase(subject["phase"], coverage, f"subjects[{index}]")
        validate_sha256(
            subject["controlled_subject_source_id"],
            f"subjects[{index}].controlled_subject_source_id",
        )
        validate_sha256(
            subject["controlled_subject_id"], f"subjects[{index}].controlled_subject_id"
        )
        material = dict(subject)
        for field in (
            "public_frame",
            "profiling_workload",
            "profiling_results",
            "common_inputs",
            "common_input_validity",
        ):
            _, material[field] = _indexed_file(
                root, subject[field], seen, loaded, f"subjects[{index}].{field}"
            )
        slots = []
        for slot_index, candidate_slot in enumerate(subject["slot_artifacts"]):
            slot_entry = validate_exact_object(
                candidate_slot,
                _SLOT_INDEX_SCHEMA,
                f"subjects[{index}].slot_artifacts[{slot_index}]",
            )
            validate_sha256(
                slot_entry["slot_id"],
                f"subjects[{index}].slot_artifacts[{slot_index}].slot_id",
            )
            if slot_entry["controlled_subject_id"] != subject["controlled_subject_id"]:
                raise EvidenceError(
                    "E_SLOT_COORDINATE", "slot controlled-subject coordinate differs"
                )
            _, slot = _indexed_file(
                root,
                slot_entry["artifact"],
                seen,
                loaded,
                f"subjects[{index}].slot_artifacts[{slot_index}]",
            )
            slots.append({**slot_entry, "artifact": slot})
        material["slot_artifacts"] = slots
        subjects.append(material)

    packages: list[dict[str, Any]] = []
    for index, candidate in enumerate(value["packages"]):
        entry = validate_exact_object(candidate, _PACKAGE_INDEX_SCHEMA, f"packages[{index}]")
        _phase(entry["phase"], coverage, f"packages[{index}]")
        if entry["input_role"] not in {"A", "B_PRIMARY", "B_SENSITIVITY", "C"}:
            raise EvidenceError("E_PACKAGE_INPUT_ROLE", "package input role is unknown")
        package_root = _indexed_directory(root, entry["root"], seen, f"packages[{index}].root")
        _, manifest = _indexed_file(
            root, entry["manifest"], seen, loaded, f"packages[{index}].manifest"
        )
        packages.append({**entry, "root": package_root, "manifest": manifest})

    receipts: list[dict[str, Any]] = []
    for index, candidate in enumerate(value["phase_receipts"]):
        entry = validate_exact_object(candidate, _RECEIPT_INDEX_SCHEMA, f"phase_receipts[{index}]")
        _phase(entry["phase"], coverage, f"phase_receipts[{index}]")
        material = dict(entry)
        for field in ("receipt", "expected_jobs", "output_manifest"):
            _, material[field] = _indexed_file(
                root, entry[field], seen, loaded, f"phase_receipts[{index}].{field}"
            )
        receipts.append(material)

    mr_chain: dict[str, Any] = {}
    if value["mr_chain"]:
        chain = validate_exact_object(value["mr_chain"], _MR_CHAIN_INDEX_SCHEMA, "mr_chain")
        for field, reference in chain.items():
            _, mr_chain[field] = _indexed_file(root, reference, seen, loaded, f"mr_chain.{field}")
    p12: dict[str, Any] = {}
    if value["p12"]:
        p12_index = validate_exact_object(value["p12"], _P12_INDEX_SCHEMA, "p12")
        for field, reference in p12_index.items():
            _, p12[field] = _indexed_file(root, reference, seen, loaded, f"p12.{field}")

    indexed_directories = [value["job_root"], *[entry["root"] for entry in value["packages"]]]
    indexed_paths = set(seen) | {source.name}
    for path in root.rglob("*"):
        relative = path.relative_to(root).as_posix()
        inside_indexed_directory = any(
            relative == directory or relative.startswith(f"{directory}/")
            for directory in indexed_directories
        )
        parent_of_indexed_path = any(
            indexed.startswith(f"{relative}/") for indexed in indexed_paths
        )
        if (
            relative in indexed_paths
            or inside_indexed_directory
            or parent_of_indexed_path
        ):
            continue
        raise EvidenceError("E_INDEX_UNINDEXED", f"unindexed path: {relative}")

    if coverage:
        phase_set = set(coverage)
        if (
            not packages
            or not receipts
            or {entry["phase"] for entry in packages} != phase_set
            or {entry["phase"] for entry in receipts} != phase_set
        ):
            raise EvidenceError("E_INDEX_COVERAGE", "phase package/receipt coverage is incomplete")
    else:
        raise EvidenceError("E_INDEX_COVERAGE", "phase coverage must be nonempty")
    if any(_PHASES.index(phase) >= 1 for phase in coverage) and (
        not value["adapter_registries"]
        or not value["input_generator_registries"]
        or not subjects
    ):
        raise EvidenceError("E_INDEX_COVERAGE", "subject evidence coverage is incomplete")
    if any(_PHASES.index(phase) >= 4 for phase in coverage) and not mr_chain:
        raise EvidenceError("E_INDEX_COVERAGE", "MR chain coverage is incomplete")
    if "PHASE_7" in coverage and not p12:
        raise EvidenceError("E_INDEX_COVERAGE", "P12 coverage is incomplete")
    return value, {
        "root": root,
        "protocol_path": protocol_path,
        "protocol": protocol,
        "ledger_path": ledger_path,
        "claims_path": claims_path,
        "claims": claims,
        "job_root": job_root,
        "subjects": subjects,
        "packages": packages,
        "receipts": receipts,
        "mr_chain": mr_chain,
        "p12": p12,
    }


def _dispatch_verify_evidence(args: argparse.Namespace) -> dict:
    index, material = _load_evidence_index(args.index)
    validate_protocol(
        material["protocol"], SCIENTIFIC_PLAN_SHA256, EVIDENCE_DESIGN_SHA256
    )
    manifests = []
    for package in material["packages"]:
        manifest = verify_materialized_package(package["root"], package["manifest"])
        classes = {record["class"] for record in manifest["files"]}
        role = package["input_role"]
        if role == "A" and manifest["role"] != "CONSTRUCTION_A":
            raise EvidenceError("E_PACKAGE_INPUT_ROLE", "A package has a non-A manifest")
        if role in {"B_PRIMARY", "B_SENSITIVITY"} and manifest["role"] != "CONTROLLED_B":
            raise EvidenceError("E_PACKAGE_INPUT_ROLE", "B package has a non-B manifest")
        if role == "B_PRIMARY" and not classes <= PACKAGE_B_PRIMARY_CLASSES:
            raise EvidenceError("E_PACKAGE_INPUT_ROLE", "primary B package contains sensitivity input")
        if role == "B_SENSITIVITY" and not classes <= PACKAGE_B_SENSITIVITY_CLASSES:
            raise EvidenceError("E_PACKAGE_INPUT_ROLE", "sensitivity B package contains primary input")
        if role == "C" and manifest["role"] != "REAL_HOLDOUT_C":
            raise EvidenceError("E_PACKAGE_INPUT_ROLE", "C package has a non-C manifest")
        manifests.append(manifest)

    events = verify_attempt_tree(material["job_root"], material["ledger_path"])
    protocol_sha256 = file_sha256(material["protocol_path"])
    attempt_common_ids: set[str] = set()
    for intent_path in material["job_root"].rglob("intent.json"):
        intent = read_canonical_json(intent_path)
        if intent.get("protocol_sha256") != protocol_sha256:
            raise EvidenceError(
                "E_PROTOCOL_BINDING", "attempt intent is bound to another protocol"
            )
        if intent.get("evaluation_input_class") == "E_COMMON":
            attempt_common_ids.add(intent["evaluation_input_id"])
    for entry in material["receipts"]:
        receipt = entry["receipt"]
        if receipt.get("protocol_sha256") != protocol_sha256:
            raise EvidenceError(
                "E_PROTOCOL_BINDING", "phase receipt is bound to another protocol"
            )
        event_count = receipt.get("ledger_event_count")
        if type(event_count) is not int or not 0 <= event_count <= len(events):
            raise EvidenceError("E_PHASE_RECEIPT", "receipt ledger prefix is invalid")
        verify_phase_receipt(
            receipt,
            events[:event_count],
            entry["expected_jobs"],
            entry["output_manifest"],
        )
        if receipt["phase_id"] != entry["phase"]:
            raise EvidenceError("E_PHASE_RECEIPT", "indexed phase differs from receipt")

    if material["mr_chain"]:
        validate_mr_inventory(
            material["mr_chain"]["candidate_frame"],
            material["mr_chain"]["custodian_receipt"],
            material["mr_chain"]["final_inventory"],
            material["mr_chain"]["portfolios"],
        )

    slot_count = 0
    slot_ids: set[str] = set()
    unassigned_attempt_ids = set(attempt_common_ids) if material["subjects"] else set()
    for subject in material["subjects"]:
        subject_consumed_ids: set[str] = set()
        inventory_ids = {
            row.get("input_id") for row in subject["common_inputs"].get("rows", [])
        }
        subject_attempt_ids = unassigned_attempt_ids & inventory_ids
        subject_consumed_ids.update(subject_attempt_ids)
        unassigned_attempt_ids -= subject_attempt_ids
        for slot_entry in subject["slot_artifacts"]:
            slot = slot_entry["artifact"]
            verify_slot_chronology(slot)
            slot_id = validate_sha256(slot.get("slot_id"), "slot.slot_id")
            if slot_id != slot_entry["slot_id"]:
                raise EvidenceError("E_SLOT_COORDINATE", "slot artifact coordinate differs")
            coordinate = f"{slot_entry['controlled_subject_id']}:{slot_id}"
            if coordinate in slot_ids:
                raise EvidenceError("E_SLOT_COORDINATE", "duplicate slot identity")
            slot_ids.add(coordinate)
            common_ids = slot["e_common_input_ids"]
            contract_ids = slot["e_contract_input_ids"]
            if set(common_ids) & set(contract_ids):
                raise EvidenceError("E_SLOT_INPUT_ROLE", "slot A/B input roles overlap")
            subject_consumed_ids.update(common_ids)
            slot_count += 1
        verify_common_input_evidence(
            subject["common_inputs"],
            subject["common_input_validity"],
            controlled_subject_source_id=subject["controlled_subject_source_id"],
            public_frame=subject["public_frame"],
            profiling_workload=subject["profiling_workload"],
            consumer_input_ids=sorted(subject_consumed_ids),
        )
    if unassigned_attempt_ids:
        raise EvidenceError(
            "E_COMMON_CHRONOLOGY", "attempt consumed an unknown common input"
        )
    return {
        "status": "PASS",
        "index_sha256": file_sha256(args.index),
        "phase_coverage": index["phase_coverage"],
        "manifest_count": len(manifests),
        "phase_receipt_count": len(material["receipts"]),
        "slot_artifact_count": slot_count,
        "ledger_event_count": len(events),
    }


def dispatch(args: argparse.Namespace) -> dict:
    if args.command == "validate-protocol":
        validate_protocol(
            read_canonical_json(args.protocol),
            SCIENTIFIC_PLAN_SHA256,
            EVIDENCE_DESIGN_SHA256,
        )
        return {"status": "PASS", "protocol_sha256": file_sha256(args.protocol)}
    if args.command == "verify-bridge":
        bridge = verify_pinned_bridge(args.repo_root, read_canonical_json(args.lock))
        _write_output(args.output, bridge)
        return {"status": "PASS", "bridge_sha256": canonical_sha256(bridge)}
    if args.command == "build-frames":
        return _dispatch_build_frames(args)
    if args.command == "verify-mr-inventory":
        value = validate_mr_inventory(
            read_canonical_json(args.candidate_frame),
            read_canonical_json(args.custodian_receipt),
            read_canonical_json(args.final_inventory),
            read_canonical_json(args.portfolios),
        )
        return {
            "status": "PASS",
            "inventory_sha256": value["final_inventory"]["artifact_sha256"],
        }
    if args.command == "build-package":
        allowed = None
        if args.allowed_classes:
            allowed = read_canonical_json(args.allowed_classes)
            if not isinstance(allowed, list):
                raise EvidenceError("E_PACKAGE_ALLOWED_CLASSES", "allowed-classes must be a list")
        manifest = build_package(
            args.role,
            args.root,
            read_canonical_json(args.specs),
            read_canonical_json(args.parents),
            allowed_classes=allowed,
        )
        _write_output(args.output, manifest)
        return {"status": "PASS", "manifest_sha256": canonical_sha256(manifest)}
    if args.command == "verify-package":
        verify_package(args.root, read_canonical_json(args.manifest))
        return {"status": "PASS", "manifest_sha256": file_sha256(args.manifest)}
    if args.command == "run-preflight":
        result = run_preflight(args.root, read_canonical_json(args.spec))
        _write_output(args.output, result)
        return result
    if args.command == "verify-run-records":
        events = verify_ledger(args.ledger)
        return {
            "status": "PASS",
            "event_count": len(events),
            "ledger_sha256": file_sha256(args.ledger),
        }
    if args.command == "close-phase":
        receipt = close_phase(
            args.phase_id,
            args.protocol_sha256,
            read_canonical_json(args.expected_jobs),
            args.ledger,
            args.output_manifest_sha256,
        )
        _write_output(args.output, receipt)
        return {"status": "PASS", "receipt_sha256": canonical_sha256(receipt)}
    if args.command == "verify-evidence":
        return _dispatch_verify_evidence(args)
    raise EvidenceError("E_CLI_COMMAND", f"unsupported command: {args.command}")


def main() -> int:
    try:
        payload = dispatch(build_parser().parse_args())
    except EvidenceError as exc:
        sys.stderr.buffer.write(canonical_json_bytes({"status": "FAIL", "code": exc.code}))
        return 2
    _write(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
