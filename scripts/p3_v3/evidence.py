#!/usr/bin/env python3
"""Thin CLI for the P3 v3 minimum evidence foundation."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from p3_v3.artifacts import (
    EvidenceError,
    canonical_json_bytes,
    canonical_sha256,
    file_sha256,
    read_canonical_json,
    write_canonical_json,
)
from p3_v3.bridge_and_frames import (
    build_common_inputs,
    build_contract_inputs,
    build_public_behavior_frame,
    build_subject_frames,
    classify_technique,
    close_slot,
    select_profiling_workload,
    validate_adapter_registry,
    validate_contract_generator_registry,
    validate_input_generator_registry,
    validate_mr_inventory,
    validate_protocol,
    verify_pinned_bridge,
    verify_slot_chronology,
)
from p3_v3.packages import (
    build_package,
    validate_package_manifest,
    verify_package,
)
from p3_v3.preflight import run_preflight
from p3_v3.run_records import (
    close_phase,
    verify_ledger,
    verify_p12_denominator,
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
    command.add_argument("--source-record", required=True)
    command.add_argument("--adapter-registry", required=True)
    command.add_argument("--adapter-root", required=True)
    command.add_argument("--declarations", required=True)
    command.add_argument("--input-generator-registry", required=True)
    command.add_argument("--generator-root", required=True)
    command.add_argument("--profiling-results", required=True)
    command.add_argument("--features", required=True)
    command.add_argument("--slots", required=True)
    command.add_argument("--contracts", required=True)
    command.add_argument("--applicability-map", required=True)
    command.add_argument("--scale-class", required=True)
    command.add_argument("--output-root", required=True)
    command.add_argument("--contract-generator-registry")
    command.add_argument("--contract-generator-root")
    command = sub.add_parser("verify-mr-inventory")
    command.add_argument("--inventory", required=True)
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
    command.add_argument("--protocol", required=True)
    command.add_argument("--manifest", action="append", default=[])
    command.add_argument("--ledger", required=True)
    command.add_argument("--phase-receipt", action="append", default=[])
    command.add_argument("--slot-artifacts", action="append", default=[])
    command.add_argument("--common-inputs", required=True)
    command.add_argument("--denominator", required=True)
    command.add_argument("--p12-summary", required=True)
    command.add_argument("--claims", required=True)
    return parser


def _dispatch_build_frames(args: argparse.Namespace) -> dict:
    output_root = Path(args.output_root)
    output_root.mkdir(parents=True, exist_ok=True)
    bridge = read_canonical_json(args.bridge)
    source_record = read_canonical_json(args.source_record)
    adapter_registry = validate_adapter_registry(
        read_canonical_json(args.adapter_registry), args.adapter_root
    )
    declarations = read_canonical_json(args.declarations)
    if not isinstance(declarations, list):
        raise EvidenceError("E_DECLARATIONS", "declarations must be a list")
    frame = build_public_behavior_frame(source_record, declarations, adapter_registry)
    workload = select_profiling_workload(frame, args.scale_class)
    generator_registry = validate_input_generator_registry(
        read_canonical_json(args.input_generator_registry), args.generator_root
    )
    common_inputs = build_common_inputs(source_record, frame, generator_registry)
    profiling_results = read_canonical_json(args.profiling_results)
    if not isinstance(profiling_results, list):
        raise EvidenceError("E_PROFILE_RESULTS", "profiling-results must be a list")
    technique_profile = classify_technique(workload, profiling_results)
    technique_body = dict(technique_profile)
    technique_profile = {
        **technique_body,
        "artifact_sha256": canonical_sha256(technique_body),
    }
    features = read_canonical_json(args.features)
    if not isinstance(features, list):
        raise EvidenceError("E_FEATURES", "features must be a list")
    subject_frames = build_subject_frames(
        bridge, features, technique_profile=technique_profile
    )
    _write_under(output_root, "public-behavior-frame.json", frame)
    _write_under(output_root, "profiling-workload.json", workload)
    _write_under(output_root, "evaluation-inputs-common.json", common_inputs)
    _write_under(output_root, "technique-profile.json", technique_profile)
    _write_under(output_root, "subject-frames.json", subject_frames)

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
    written = [
        "public-behavior-frame.json",
        "profiling-workload.json",
        "evaluation-inputs-common.json",
        "technique-profile.json",
        "subject-frames.json",
    ]
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
        "common_input_count": len(common_inputs["rows"]),
        "subject_count": len(subject_frames["subjects"]),
    }


def _verify_phase_receipt(receipt: Mapping[str, Any], ledger_path: str) -> None:
    required = {
        "phase_id",
        "protocol_sha256",
        "expected_job_inventory_sha256",
        "expected_job_count",
        "terminal_result_count",
        "ledger_event_count",
        "ledger_head_sha256",
        "ledger_raw_sha256",
        "output_manifest_sha256",
        "artifact_sha256",
    }
    if set(receipt) != required:
        raise EvidenceError("E_PHASE_RECEIPT", "phase receipt keys are not exact")
    body = {key: value for key, value in receipt.items() if key != "artifact_sha256"}
    if receipt["artifact_sha256"] != canonical_sha256(body):
        raise EvidenceError("E_PHASE_RECEIPT", "phase receipt self-hash differs")
    ledger_raw = Path(ledger_path).read_bytes()
    if receipt["ledger_raw_sha256"] != __import__("hashlib").sha256(ledger_raw).hexdigest():
        raise EvidenceError("E_PHASE_RECEIPT", "phase receipt ledger hash differs")


def _dispatch_verify_evidence(args: argparse.Namespace) -> dict:
    protocol = validate_protocol(
        read_canonical_json(args.protocol),
        SCIENTIFIC_PLAN_SHA256,
        EVIDENCE_DESIGN_SHA256,
    )
    if protocol.get("claims_initial_status") != "blocked":
        raise EvidenceError("E_CLAIMS", "protocol claims_initial_status must be blocked")
    for manifest_path in args.manifest:
        validate_package_manifest(read_canonical_json(manifest_path))
    events = verify_ledger(args.ledger)
    for receipt_path in args.phase_receipt:
        _verify_phase_receipt(read_canonical_json(receipt_path), args.ledger)
    for slot_path in args.slot_artifacts:
        verify_slot_chronology(read_canonical_json(slot_path))
    common_inputs = read_canonical_json(args.common_inputs)
    if not isinstance(common_inputs, Mapping) or "rows" not in common_inputs:
        raise EvidenceError("E_COMMON_INPUTS", "common inputs rows are absent")
    if len(common_inputs["rows"]) != 30:
        raise EvidenceError("E_COMMON_INPUTS", "common inputs must contain 30 rows")
    roles = {row.get("status") for row in common_inputs["rows"]}
    if not roles:
        raise EvidenceError("E_COMMON_INPUTS", "common input roles are empty")
    frozen = verify_p12_denominator(read_canonical_json(args.denominator))
    summary = read_canonical_json(args.p12_summary)
    if not isinstance(summary, Mapping):
        raise EvidenceError("E_P12_SUMMARY", "p12 summary must be an object")
    if summary.get("denominator_sha256") != frozen["artifact_sha256"]:
        raise EvidenceError("E_P12_SUMMARY", "summary does not bind frozen denominator")
    if summary.get("planned_count") != frozen["planned_count"]:
        raise EvidenceError("E_P12_SUMMARY", "summary planned_count differs")
    body = {key: value for key, value in summary.items() if key != "artifact_sha256"}
    if summary.get("artifact_sha256") != canonical_sha256(body):
        raise EvidenceError("E_P12_SUMMARY", "summary self-hash differs")
    claims = read_canonical_json(args.claims)
    claim_rows = claims.get("claims") if isinstance(claims, Mapping) else None
    if not isinstance(claim_rows, list) or not claim_rows:
        raise EvidenceError("E_CLAIMS", "claims list is absent")
    if any(row.get("status") != "blocked" for row in claim_rows):
        raise EvidenceError("E_CLAIMS", "all claims must remain blocked")
    return {
        "status": "PASS",
        "protocol_sha256": file_sha256(args.protocol),
        "ledger_event_count": len(events),
        "manifest_count": len(args.manifest),
        "phase_receipt_count": len(args.phase_receipt),
        "slot_artifact_count": len(args.slot_artifacts),
        "claims_status": "blocked",
        "denominator_sha256": frozen["artifact_sha256"],
        "p12_summary_sha256": summary["artifact_sha256"],
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
        value = validate_mr_inventory(read_canonical_json(args.inventory))
        return {"status": "PASS", "inventory_sha256": canonical_sha256(value)}
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
