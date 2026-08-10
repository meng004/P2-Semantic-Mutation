from __future__ import annotations

import hashlib
import json
import os
import shutil
import socket
import subprocess
import sys
from pathlib import Path

import pytest

import p3_v3.bridge_and_frames as frames_module
from p3_v3.artifacts import canonical_json_bytes, canonical_sha256, read_canonical_json
from p3_v3.bridge_and_frames import (
    APPLICABLE_SLOT_CHRONOLOGY,
    P12_OUTCOME_STATES,
    build_contract_inputs,
    build_public_behavior_frame,
    canonical_source_tree_sha256,
    close_slot,
    derive_subject_material,
    run_adapter_discovery,
    select_profiling_workload,
    validate_adapter_registry,
    validate_common_inputs_on_fixed_source,
    validate_contract_generator_registry,
    validate_input_generator_registry,
)
from p3_v3.packages import (
    PACKAGE_B_PRIMARY_CLASSES,
    PACKAGE_B_SENSITIVITY_CLASSES,
    build_package,
)
from p3_v3.run_records import (
    close_phase,
    create_intent,
    freeze_p12_denominator,
    recompute_p12_summary,
    reconstruct_attempt_events,
    write_result,
)
from tests.p3_v3.test_cli import (
    _blocked_claim_ledger,
    _indexed_reference,
    _install_protocol_authorities,
    _protocol_body,
    _write_evidence_index,
    _write_protocol,
)

ROOT = Path(__file__).resolve().parents[2]
CLI = ROOT / "scripts/p3_v3/evidence.py"
PUBLIC_FIXTURES = Path(__file__).resolve().parent / "fixtures/public_behavior"
CONTRACT_GENERATOR_TEMPLATE = '''\
def generate(domain: dict, seed: int):
    return {{
        "envelope": {{
            "generator_id": "{generator_id}",
            "schema_version": "p3-contract-input-envelope-v1",
            "seed": seed,
        }},
        "raw_payload_sha256": __import__("hashlib").sha256(
            __import__("json").dumps(domain, sort_keys=True).encode()
            + seed.to_bytes(8, "big")
        ).hexdigest(),
    }}
'''
PHASES = [f"PHASE_{number}" for number in range(8)]
SOCKET_BLOCKED_CLI = """
import runpy
import socket
import sys

def blocked(*_args, **_kwargs):
    raise OSError("network disabled in synthetic Phase 0 through Phase 7 CLI")

socket.create_connection = blocked
socket.getaddrinfo = blocked
sys.argv = sys.argv[1:]
runpy.run_path(sys.argv[0], run_name="__main__")
"""
SOCKET_BLOCKED_SMOKE = """
import socket

def blocked(*_args, **_kwargs):
    raise OSError("network disabled in synthetic preflight smoke")

socket.create_connection = blocked
socket.getaddrinfo = blocked
print("synthetic preflight")
"""


@pytest.fixture(autouse=True)
def _block_network(monkeypatch):
    def blocked(*_args, **_kwargs):
        raise OSError("network disabled in synthetic Phase 0 through Phase 7 path")

    monkeypatch.setattr(socket, "create_connection", blocked)
    monkeypatch.setattr(socket, "getaddrinfo", blocked)


def _cli(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-c", SOCKET_BLOCKED_CLI, str(CLI), *args],
        capture_output=True,
        check=False,
        text=True,
        env={**os.environ, "PYTHONPATH": str(ROOT / "src")},
    )


def _git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        capture_output=True,
        check=True,
        text=True,
    ).stdout.strip()


def _write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_json_bytes(value))


def _self_hashed(body: dict) -> dict:
    return {**body, "artifact_sha256": canonical_sha256(body)}


def _refresh_self_hash(value: dict) -> None:
    if "artifact_sha256" in value:
        value["artifact_sha256"] = canonical_sha256(
            {key: item for key, item in value.items() if key != "artifact_sha256"}
        )


def _profiling_receipt(
    workload: dict,
    source_record: dict,
    neutral_snapshot_id: str,
    adapter_source_sha256: str,
    module: str,
    symbol: str,
) -> dict:
    results = []
    for selected in workload["selected_rows"]:
        trace = [
            {
                "sequence": 1,
                "module": module,
                "symbol": symbol,
                "call_kind": "PYTHON_CALL",
                "argument_types": ["float"],
                "keyword_names": [],
            }
        ]
        results.append(
            {
                "behavior_id": selected["behavior_id"],
                "status": "SUCCESS",
                "argv": ["synthetic-profiler", selected["behavior_id"]],
                "input_sha256": [canonical_sha256({"behavior": selected["behavior_id"]})],
                "environment_sha256": canonical_sha256({"environment": "synthetic"}),
                "runner_version": "synthetic-profiler-v1",
                "exit_code": 0,
                "stdout_sha256": canonical_sha256({"stream": "stdout"}),
                "stderr_sha256": canonical_sha256({"stream": "stderr"}),
                "call_trace": trace,
                "call_trace_sha256": canonical_sha256(trace),
                "timed_out": False,
                "failure_code": "",
                "observed_site_ids": [],
            }
        )
    body = {
        "schema_version": "p3-profiling-results-v1",
        "neutral_snapshot_id": neutral_snapshot_id,
        "controlled_subject_source_id": workload["controlled_subject_source_id"],
        **source_record,
        "profiling_workload_sha256": workload["artifact_sha256"],
        "adapter_implementation_source_sha256": adapter_source_sha256,
        "runner_implementation_source_sha256": hashlib.sha256(
            Path(frames_module.__file__).read_bytes()
        ).hexdigest(),
        "results": sorted(results, key=lambda row: row["behavior_id"]),
    }
    return _self_hashed(body)


def _make_subject_source(
    evidence_root: Path,
    name: str,
    fixture_name: str,
    effective_lines: int,
) -> tuple[Path, dict, dict]:
    source_root = evidence_root / f"subjects/{name}"
    source_root.mkdir(parents=True)
    fixture = json.loads((PUBLIC_FIXTURES / fixture_name).read_text())
    source_path = source_root / fixture["source_files"][0]
    source_path.parent.mkdir(parents=True)
    if fixture["ecosystem"] == "python":
        source_path.write_text("value = 1\n" * effective_lines, encoding="utf-8")
    else:
        source_path.write_text("int value = 1;\n" * effective_lines, encoding="utf-8")
    manifest = source_root / f"adapter-{fixture['ecosystem']}.json"
    _write_json(manifest, fixture)
    descriptor = {
        "ecosystem": fixture["ecosystem"],
        "manifest_path": manifest.name,
        "reverse": False,
    }
    source_record = {
        "normalized_source_tree_sha256": canonical_source_tree_sha256(source_root),
        "build_descriptor_sha256": canonical_sha256(descriptor),
    }
    return source_root, descriptor, source_record


def _neutral_id(package_root: str, source_record: dict, archive_sha256: str) -> str:
    return canonical_sha256(
        {
            "p12_package_root_sha256": package_root,
            "normalized_source_tree_sha256": source_record[
                "normalized_source_tree_sha256"
            ],
            "source_archive_sha256": archive_sha256,
            "domain": "P3-NEUTRAL-SNAPSHOT-v1",
        }
    )


def _local_bridge(
    tmp_path: Path,
    records: list[dict],
    package_root: str,
) -> tuple[Path, dict]:
    repo = tmp_path / "synthetic-p12-repository"
    repo.mkdir()
    _git(repo, "init")
    _git(repo, "config", "user.name", "Synthetic Fixture")
    _git(repo, "config", "user.email", "fixture@example.invalid")
    _git(repo, "remote", "add", "origin", "https://github.com/Example/P12-Defect4MR.git")
    contract = {"schema_version": "p12-p3-contract-v2", "scope": "synthetic-only"}
    _write_json(repo / "release/contract.json", contract)
    contract_blob = _git(repo, "hash-object", "release/contract.json")
    body = {
        "schema_version": "p3-p12-bridge-v1",
        "p12_release_id": "synthetic-local-v1",
        "p12_repository_identity": "Example/P12-Defect4MR",
        "p12_contract_path": "release/contract.json",
        "p12_contract_blob_sha": contract_blob,
        "p12_package_root_sha256": package_root,
        "p12_contract_sha256": hashlib.sha256(
            (repo / "release/contract.json").read_bytes()
        ).hexdigest(),
        "eligible_inventory_root_sha256": canonical_sha256(records),
        "eligible_item_count": len(records),
        "records": records,
        "trust_mode": "PINNED_GIT_RELEASE",
    }
    _write_json(repo / "release/bridge.json", _self_hashed(body))
    (repo / "requirements.lock").write_text("fixture==1\n", encoding="utf-8")
    (repo / "input.json").write_text("{}\n", encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "synthetic bridge")
    commit = _git(repo, "rev-parse", "HEAD")
    lock = {
        "repository_identity": "Example/P12-Defect4MR",
        "release_commit_sha": commit,
        "bridge_path": "release/bridge.json",
        "bridge_blob_sha": _git(repo, "rev-parse", f"{commit}:release/bridge.json"),
        "contract_path": "release/contract.json",
        "contract_blob_sha": _git(repo, "rev-parse", f"{commit}:release/contract.json"),
        "package_root_sha256": package_root,
    }
    return repo, lock


def _contract_generator_registry(root: Path) -> dict:
    from p3_v3.bridge_and_frames import E_CONTRACT_GENERATOR_IDS

    generators = []
    for generator_id in E_CONTRACT_GENERATOR_IDS:
        relative = f"generators/{generator_id.lower()}.py"
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            CONTRACT_GENERATOR_TEMPLATE.format(generator_id=generator_id),
            encoding="utf-8",
        )
        generators.append(
            {
                "generator_id": generator_id,
                "schema_kind": generator_id,
                "implementation_path": relative,
                "source_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "output_schema": {
                    "generator_id": generator_id,
                    "schema_version": "p3-contract-input-envelope-v1",
                },
                "failure_code": f"{generator_id}_INVALID",
            }
        )
    return _self_hashed(
        {
            "schema_version": "p3-contract-generator-registry-v1",
            "generators": generators,
        }
    )


def _write_subject_index(
    evidence_root: Path,
    name: str,
    material: dict,
    bridge_record: dict,
    source_root: Path,
    source_record: dict,
    descriptor: dict,
    profiling_results: dict,
    adapter_registry: dict,
    generator_registry: dict,
    protocol_sha256: str,
    jobs: dict[str, list[str]],
) -> dict:
    validity = validate_common_inputs_on_fixed_source(
        material["common_inputs"],
        lambda row: row["status"],
        sites=[],
        contracts=[],
        profile={},
        frame_artifact_sha256=material["public_behavior_frame"]["artifact_sha256"],
    )
    artifact_root = evidence_root / f"subject-artifacts/{name}"
    artifacts = {
        "bridge_record": bridge_record,
        "source_record": source_record,
        "build_descriptor": descriptor,
        "adapter_discovery": material["adapter_discovery"],
        "source_scale": material["source_scale"],
        "public_frame": material["public_behavior_frame"],
        "profiling_workload": material["profiling_workload"],
        "profiling_results": profiling_results,
        "common_inputs": material["common_inputs"],
        "common_input_validity": validity,
        "technique_profile": material["technique_profile"],
        "sites": material["subject"]["sites"],
        "subject": material["subject"],
    }
    references = {}
    for field, artifact in artifacts.items():
        path = artifact_root / f"{field}.json"
        _write_json(path, artifact)
        references[field] = _indexed_reference(evidence_root, path)

    trace_entries = []
    common_id = material["common_inputs"]["rows"][0]["input_id"]
    for ordinal, row in enumerate(profiling_results["results"], start=1):
        job_id = f"profile-{name}-{ordinal:02d}"
        trace_path = artifact_root / f"trace-{ordinal:02d}.json"
        _write_json(trace_path, row["call_trace"])
        trace_sha256 = hashlib.sha256(trace_path.read_bytes()).hexdigest()
        attempt_root = evidence_root / f"jobs/PHASE_1/{job_id}/1"
        intent = {
            "job_id": job_id,
            "protocol_sha256": protocol_sha256,
            "phase": "PHASE_1",
            "argv": row["argv"],
            "cwd_identity": material["controlled_subject_source_id"],
            "environment_sha256": row["environment_sha256"],
            "input_sha256": row["input_sha256"],
            "seed": None,
            "timeout_seconds": 30,
            "attempt": 1,
            "object_type": "PROFILING_BEHAVIOR",
            "object_id": row["behavior_id"],
            "mr_id": "not-applicable",
            "evaluation_input_class": "E_COMMON",
            "evaluation_input_id": common_id,
            "repetition_id": 1,
            "environment_id": "synthetic-profile-env",
            "job_role": "PROFILING",
        }
        create_intent(attempt_root, intent)
        write_result(
            attempt_root,
            {
                "job_id": job_id,
                "attempt": 1,
                "status": "PASS",
                "exit_code": row["exit_code"],
                "stdout_sha256": row["stdout_sha256"],
                "stderr_sha256": row["stderr_sha256"],
                "duration_seconds": 0.01,
                "failure_code": row["failure_code"],
                "scientific_outcome": None,
                "call_trace_sha256": trace_sha256,
                "call_trace_identity": canonical_sha256(
                    {
                        "job_id": job_id,
                        "attempt": 1,
                        "behavior_id": row["behavior_id"],
                        "call_trace_sha256": trace_sha256,
                        "domain": "P3-PROFILING-TRACE-v1",
                    }
                ),
            },
        )
        jobs["PHASE_1"].append(job_id)
        trace_entries.append(
            {
                "job_id": job_id,
                "attempt": 1,
                "behavior_id": row["behavior_id"],
                "artifact": _indexed_reference(evidence_root, trace_path),
            }
        )

    return {
        "phase": "PHASE_1",
        "controlled_subject_source_id": material["controlled_subject_source_id"],
        "controlled_subject_id": material["subject"]["controlled_subject_id"],
        "bridge_record": references["bridge_record"],
        "source_root": source_root.relative_to(evidence_root).as_posix(),
        "source_record": references["source_record"],
        "build_descriptor": references["build_descriptor"],
        "adapter_registry_sha256": adapter_registry["artifact_sha256"],
        "input_generator_registry_sha256": generator_registry["artifact_sha256"],
        "adapter_discovery": references["adapter_discovery"],
        "source_scale": references["source_scale"],
        "public_frame": references["public_frame"],
        "profiling_workload": references["profiling_workload"],
        "profiling_results": references["profiling_results"],
        "profiling_traces": trace_entries,
        "common_inputs": references["common_inputs"],
        "common_input_validity": references["common_input_validity"],
        "technique_profile": references["technique_profile"],
        "sites": references["sites"],
        "subject": references["subject"],
        "slot_artifacts": [],
    }


def _ordinary_attempt(
    evidence_root: Path,
    protocol_sha256: str,
    phase: str,
    job_id: str,
    common_input_id: str,
    validity_sha256: str,
    jobs: dict[str, list[str]],
    *,
    retry: bool = False,
) -> None:
    base = {
        "job_id": job_id,
        "protocol_sha256": protocol_sha256,
        "phase": phase,
        "argv": ["synthetic-infrastructure", phase],
        "cwd_identity": "synthetic-infrastructure-root",
        "environment_sha256": canonical_sha256({"phase": phase, "env": 1}),
        "input_sha256": sorted(
            {
                canonical_sha256({"phase": phase, "input": 1}),
                *(() if phase == "PHASE_0" else (validity_sha256,)),
            }
        ),
        "seed": 17,
        "timeout_seconds": 30,
        "object_type": "INFRASTRUCTURE_PROBE",
        "object_id": phase,
        "mr_id": "mr-synthetic-infrastructure",
        "evaluation_input_class": "E_COMMON",
        "evaluation_input_id": common_input_id,
        "repetition_id": 1,
        "environment_id": "synthetic-infrastructure-env",
        "job_role": "PRIMARY_CONTROLLED",
    }
    attempts = 2 if retry else 1
    for attempt in range(1, attempts + 1):
        attempt_root = evidence_root / f"jobs/{phase}/{job_id}/{attempt}"
        create_intent(attempt_root, {**base, "attempt": attempt})
        failed = retry and attempt == 1
        write_result(
            attempt_root,
            {
                "job_id": job_id,
                "attempt": attempt,
                "status": "FAIL_INFRASTRUCTURE" if failed else "PASS",
                "exit_code": 75 if failed else 0,
                "stdout_sha256": canonical_sha256(
                    {"phase": phase, "attempt": attempt, "stream": "stdout"}
                ),
                "stderr_sha256": canonical_sha256(
                    {"phase": phase, "attempt": attempt, "stream": "stderr"}
                ),
                "duration_seconds": 0.01,
                "failure_code": "SYNTHETIC_RETRY" if failed else "",
                "scientific_outcome": None,
                "call_trace_sha256": None,
                "call_trace_identity": None,
            },
        )
    jobs[phase].append(job_id)


def _build_complete_evidence(tmp_path: Path) -> dict:
    evidence_root = tmp_path / "evidence"
    evidence_root.mkdir()
    authorities = _install_protocol_authorities(evidence_root)
    protocol_path = evidence_root / "protocol.json"
    protocol_raw = _write_protocol(protocol_path, _protocol_body(**authorities["hashes"]))
    protocol_sha256 = hashlib.sha256(protocol_raw).hexdigest()

    validated_adapters = validate_adapter_registry(
        authorities["adapter_registry"], authorities["adapter_registry_path"].parent
    )
    validated_generators = validate_input_generator_registry(
        authorities["generator_registry"], authorities["generator_registry_path"].parent
    )

    python_root, python_descriptor, python_source = _make_subject_source(
        evidence_root, "python-pep517-s", "python.json", 2
    )
    cmake_root, cmake_descriptor, cmake_source = _make_subject_source(
        evidence_root, "cmake-ctest-m", "cmake.json", 10_000
    )
    package_root = "1" * 64
    python_neutral = _neutral_id(package_root, python_source, "2" * 64)
    cmake_neutral = _neutral_id(package_root, cmake_source, "3" * 64)
    records = [
        {
            "neutral_snapshot_id": python_neutral,
            "fixed_tree_commitment": "4" * 64,
            **python_source,
            "source_archive_sha256": "2" * 64,
            "eligibility_reason": "synthetic Python PEP 517 subject",
            "eligible_for_construct": True,
            "eligible_for_criterion": True,
        },
        {
            "neutral_snapshot_id": cmake_neutral,
            "fixed_tree_commitment": "5" * 64,
            **cmake_source,
            "source_archive_sha256": "3" * 64,
            "eligibility_reason": "synthetic CMake CTest subject",
            "eligible_for_construct": True,
            "eligible_for_criterion": True,
        },
    ]
    p12_repo, bridge_lock = _local_bridge(tmp_path, records, package_root)
    lock_path = tmp_path / "bridge-lock.json"
    _write_json(lock_path, bridge_lock)
    verified_bridge_path = tmp_path / "verified-bridge.json"
    result = _cli(
        "verify-bridge",
        "--repo-root",
        str(p12_repo),
        "--lock",
        str(lock_path),
        "--output",
        str(verified_bridge_path),
    )
    assert result.returncode == 0, result.stderr
    verified_bridge = read_canonical_json(verified_bridge_path)

    result = _cli("validate-protocol", "--protocol", str(protocol_path))
    assert result.returncode == 0, result.stderr

    subject_parameters = [
        (
            "python-pep517-s",
            python_root,
            python_descriptor,
            python_source,
            python_neutral,
            "PYTHON_PEP517_V1",
            "builtins",
            "abs",
        ),
        (
            "cmake-ctest-m",
            cmake_root,
            cmake_descriptor,
            cmake_source,
            cmake_neutral,
            "CMAKE_CTEST_V1",
            "numpy.linalg",
            "solve",
        ),
    ]
    specs = []
    materials = []
    for (
        name,
        source_root,
        descriptor,
        source_record,
        neutral,
        adapter_id,
        module,
        symbol,
    ) in subject_parameters:
        discovery = run_adapter_discovery(
            source_root, descriptor, validated_adapters, adapter_id
        )
        frame = build_public_behavior_frame(source_record, discovery)
        scale_class = "S" if name.endswith("-s") else "M"
        workload = select_profiling_workload(frame, scale_class)
        profiling = _profiling_receipt(
            workload,
            source_record,
            neutral,
            discovery["implementation_source_sha256"],
            module,
            symbol,
        )
        spec = {
            "neutral_snapshot_id": neutral,
            "source_root": str(source_root),
            "source_record": source_record,
            "build_descriptor": descriptor,
            "adapter_registry": validated_adapters,
            "input_generator_registry": validated_generators,
            "profiling_results": profiling,
        }
        bridge_record = next(
            record
            for record in verified_bridge["records"]
            if record["neutral_snapshot_id"] == neutral
        )
        material = derive_subject_material(spec, bridge_record)
        assert material["source_scale"]["scale_class"] == scale_class
        assert any(
            row["status"] == "COMMON_INPUT_EXECUTABLE"
            for row in material["common_inputs"]["rows"]
        )
        specs.append(
            {
                **spec,
                "adapter_registry": authorities["adapter_registry"],
                "input_generator_registry": authorities["generator_registry"],
            }
        )
        materials.append((name, source_root, descriptor, source_record, profiling, material, bridge_record))

    # Exercise the production frame CLI, while keeping its transient output outside
    # the byte-indexed evidence root.
    specs_path = tmp_path / "subject-specs.json"
    slots_path = tmp_path / "empty-slots.json"
    contracts_path = tmp_path / "empty-contracts.json"
    applicability_path = tmp_path / "empty-applicability.json"
    for path, value in (
        (specs_path, specs),
        (slots_path, []),
        (contracts_path, {}),
        (applicability_path, {}),
    ):
        _write_json(path, value)
    frame_output = tmp_path / "production-frame-output"
    frame_result = _cli(
        "build-frames",
        "--bridge",
        str(verified_bridge_path),
        "--subject-specs",
        str(specs_path),
        "--adapter-root",
        str(authorities["adapter_registry_path"].parent),
        "--generator-root",
        str(authorities["generator_registry_path"].parent),
        "--slots",
        str(slots_path),
        "--contracts",
        str(contracts_path),
        "--applicability-map",
        str(applicability_path),
        "--output-root",
        str(frame_output),
    )
    assert frame_result.returncode == 0, frame_result.stderr

    jobs = {phase: [] for phase in PHASES}
    subject_indexes = []
    for name, source_root, descriptor, source_record, profiling, material, bridge_record in materials:
        subject_indexes.append(
            _write_subject_index(
                evidence_root,
                name,
                material,
                bridge_record,
                source_root,
                source_record,
                descriptor,
                profiling,
                validated_adapters,
                validated_generators,
                protocol_sha256,
                jobs,
            )
        )

    python_material = materials[0][5]
    cmake_material = materials[1][5]
    python_validity = read_canonical_json(
        evidence_root / subject_indexes[0]["common_input_validity"]["path"]
    )
    contract_generator_root = tmp_path / "contract-generators"
    validated_contract_generators = validate_contract_generator_registry(
        _contract_generator_registry(contract_generator_root),
        contract_generator_root,
    )
    python_slot = close_slot(
        {
            "slot_id": canonical_sha256({"slot": "python"}),
            "controlled_subject_id": python_material["subject"]["controlled_subject_id"],
        },
        python_material["subject"]["sites"],
        lambda _site: True,
    )
    contract = {
        "contract_id": canonical_sha256({"contract": "synthetic"}),
        "generator_id": "CONTRACT_NUMERIC_DOMAIN_V1",
        "domain": {"domain": "numeric", "bounds": [0, 1]},
        "site_id": python_slot["site_id"],
    }
    contract_inputs = build_contract_inputs(
        python_slot, contract, validated_contract_generators
    )
    common_id = python_material["common_inputs"]["rows"][0]["input_id"]
    applicable_slot = {
        "slot_id": python_slot["slot_id"],
        "chronology": list(APPLICABLE_SLOT_CHRONOLOGY),
        "contract": contract,
        "e_contract": contract_inputs,
        "patch": {
            "patch_id": canonical_sha256({"patch": "synthetic"}),
            "bytes_sha256": canonical_sha256({"patch-bytes": "synthetic"}),
        },
        "certification_witness": {
            "witness_id": canonical_sha256({"witness": "synthetic"})
        },
        "e_common_input_ids": [common_id],
        "e_contract_input_ids": [row["input_id"] for row in contract_inputs["rows"]],
    }
    cmake_slot = close_slot(
        {
            "slot_id": canonical_sha256({"slot": "cmake"}),
            "controlled_subject_id": cmake_material["subject"]["controlled_subject_id"],
        },
        cmake_material["subject"]["sites"],
        lambda _site: False,
    )
    not_applicable_slot = {
        "slot_id": cmake_slot["slot_id"],
        "chronology": ["APPLICABILITY_CLOSED_NOT_APPLICABLE"],
        "contract": None,
        "e_contract": None,
        "patch": None,
        "certification_witness": None,
        "e_common_input_ids": [],
        "e_contract_input_ids": [],
    }
    for subject_index, slot in zip(
        subject_indexes, (applicable_slot, not_applicable_slot), strict=True
    ):
        slot_path = evidence_root / f"slots/{slot['slot_id']}.json"
        _write_json(slot_path, slot)
        subject_index["slot_artifacts"].append(
            {
                "slot_id": slot["slot_id"],
                "controlled_subject_id": subject_index["controlled_subject_id"],
                "artifact": _indexed_reference(evidence_root, slot_path),
            }
        )

    candidate = _self_hashed(
        {
            "schema_version": "p3-mr-candidate-frame-v1",
            "artifact_type": "MR_CANDIDATE_FRAME",
            "candidate_mr_ids": ["mr-synthetic-infrastructure"],
        }
    )
    custodian = _self_hashed(
        {
            "schema_version": "p3-mr-custodian-receipt-v1",
            "artifact_type": "MR_CUSTODIAN_RECEIPT",
            "candidate_frame_sha256": candidate["artifact_sha256"],
            "receipt_state": "CLOSED",
            "admitted_mr_ids": ["mr-synthetic-infrastructure"],
            "excluded_mr_ids": [],
        }
    )
    inventory = _self_hashed(
        {
            "schema_version": "p3-mr-final-inventory-v1",
            "artifact_type": "MR_FINAL_INVENTORY",
            "custodian_receipt_sha256": custodian["artifact_sha256"],
            "mr_ids": ["mr-synthetic-infrastructure"],
        }
    )
    portfolios = _self_hashed(
        {
            "schema_version": "p3-mr-portfolios-v1",
            "artifact_type": "MR_PORTFOLIOS",
            "final_inventory_sha256": inventory["artifact_sha256"],
            "portfolios": [
                {
                    "portfolio_id": "synthetic-infrastructure-only",
                    "mr_ids": ["mr-synthetic-infrastructure"],
                }
            ],
        }
    )
    mr_chain = {}
    mr_paths = {}
    for field, artifact in (
        ("candidate_frame", candidate),
        ("custodian_receipt", custodian),
        ("final_inventory", inventory),
        ("portfolios", portfolios),
    ):
        path = evidence_root / f"mr/{field}.json"
        _write_json(path, artifact)
        mr_paths[field] = path
        mr_chain[field] = _indexed_reference(evidence_root, path)
    mr_cli = _cli(
        "verify-mr-inventory",
        "--candidate-frame",
        str(mr_paths["candidate_frame"]),
        "--custodian-receipt",
        str(mr_paths["custodian_receipt"]),
        "--final-inventory",
        str(mr_paths["final_inventory"]),
        "--portfolios",
        str(mr_paths["portfolios"]),
    )
    assert mr_cli.returncode == 0, mr_cli.stderr

    package_entries = []
    package_a_root = evidence_root / "packages/construction-a"
    package_a_root.mkdir(parents=True)
    (package_a_root / "source.py").write_text("value = 1\n", encoding="utf-8")
    specs_a_path = tmp_path / "package-a-specs.json"
    parents_a_path = tmp_path / "package-a-parents.json"
    manifest_a_path = evidence_root / "package-manifests/construction-a.json"
    _write_json(specs_a_path, [{"path": "source.py", "class": "SOURCE"}])
    _write_json(parents_a_path, [])
    package_cli = _cli(
        "build-package",
        "--role",
        "CONSTRUCTION_A",
        "--root",
        str(package_a_root),
        "--specs",
        str(specs_a_path),
        "--parents",
        str(parents_a_path),
        "--output",
        str(manifest_a_path),
    )
    assert package_cli.returncode == 0, package_cli.stderr
    verify_package_cli = _cli(
        "verify-package", "--root", str(package_a_root), "--manifest", str(manifest_a_path)
    )
    assert verify_package_cli.returncode == 0, verify_package_cli.stderr
    manifest_a = read_canonical_json(manifest_a_path)
    package_entries.append(
        {
            "phase": "PHASE_6",
            "input_role": "A",
            "root": package_a_root.relative_to(evidence_root).as_posix(),
            "manifest": _indexed_reference(evidence_root, manifest_a_path),
        }
    )
    for role, dirname, data_class, allowed, input_id in (
        (
            "B_PRIMARY",
            "controlled-primary",
            "E_COMMON_PRIMARY",
            PACKAGE_B_PRIMARY_CLASSES,
            common_id,
        ),
        (
            "B_SENSITIVITY",
            "controlled-sensitivity",
            "E_CONTRACT_SENSITIVITY",
            PACKAGE_B_SENSITIVITY_CLASSES,
            contract_inputs["rows"][0]["input_id"],
        ),
    ):
        package_root_path = evidence_root / f"packages/{dirname}"
        package_root_path.mkdir(parents=True)
        (package_root_path / "runner.py").write_text("print('synthetic')\n", encoding="utf-8")
        input_path = package_root_path / "input.json"
        _write_json(input_path, {"role": data_class, "input_id": input_id})
        manifest = build_package(
            "CONTROLLED_B",
            package_root_path,
            [
                {"path": "runner.py", "class": "EXECUTION_CODE"},
                {"path": "input.json", "class": data_class},
            ],
            [manifest_a["artifact_sha256"]],
            allowed_classes=allowed,
        )
        manifest_path = evidence_root / f"package-manifests/{dirname}.json"
        _write_json(manifest_path, manifest)
        package_entries.append(
            {
                "phase": "PHASE_6",
                "input_role": role,
                "root": package_root_path.relative_to(evidence_root).as_posix(),
                "manifest": _indexed_reference(evidence_root, manifest_path),
            }
        )

    preflight_spec = {
        "schema_version": "p3-preflight-v1",
        "repository_identity": "github.com/Example/P12-Defect4MR",
        "expected_commit": _git(p12_repo, "rev-parse", "HEAD"),
        "dependency_lock_path": "requirements.lock",
        "dependency_lock_sha256": hashlib.sha256(
            (p12_repo / "requirements.lock").read_bytes()
        ).hexdigest(),
        "phase_inputs": [
            {
                "path": "input.json",
                "sha256": hashlib.sha256((p12_repo / "input.json").read_bytes()).hexdigest(),
            }
        ],
        "smoke_commands": [[sys.executable, "-c", SOCKET_BLOCKED_SMOKE]],
        "timeout_seconds": 10,
        "phase_role": "CONTROLLED_B",
        "minimum_cpu_count": 1,
        "minimum_memory_bytes": 1,
        "minimum_disk_free_bytes": 1,
        "worker_limit": 1,
    }
    preflight_spec_path = tmp_path / "preflight.json"
    preflight_receipt_path = tmp_path / "preflight-receipt.json"
    _write_json(preflight_spec_path, preflight_spec)
    preflight_cli = _cli(
        "run-preflight",
        "--root",
        str(p12_repo),
        "--spec",
        str(preflight_spec_path),
        "--output",
        str(preflight_receipt_path),
    )
    assert preflight_cli.returncode == 0, preflight_cli.stderr
    preflight_receipt = read_canonical_json(preflight_receipt_path)

    for phase in ("PHASE_0", "PHASE_2", "PHASE_3", "PHASE_4", "PHASE_5", "PHASE_6"):
        _ordinary_attempt(
            evidence_root,
            protocol_sha256,
            phase,
            f"infra-{phase.lower().replace('_', '-')}",
            "phase-zero-bootstrap" if phase == "PHASE_0" else common_id,
            python_validity["artifact_sha256"],
            jobs,
            retry=phase == "PHASE_5",
        )

    paired_ids = [f"synthetic-fault-{index}" for index in range(1, 6)]
    p12_jobs = [
        {
            "job_id": f"p12-synthetic-{index}",
            "object_type": "P12_FAULT",
            "object_id": paired_id,
            "mr_id": "mr-synthetic-infrastructure",
            "evaluation_input_class": "E_COMMON",
            "evaluation_input_id": python_material["common_inputs"]["rows"][index - 1]["input_id"],
            "repetition_id": 1,
            "environment_id": "synthetic-p12-env",
            "job_role": "P12",
            "weight": 1,
        }
        for index, paired_id in enumerate(paired_ids, start=1)
    ]
    denominator = freeze_p12_denominator(paired_ids, p12_jobs)
    terminal_pairs = []
    result_rows = []
    for job, outcome in zip(p12_jobs, P12_OUTCOME_STATES, strict=True):
        intent = {
            **{key: value for key, value in job.items() if key != "weight"},
            "protocol_sha256": protocol_sha256,
            "phase": "PHASE_7",
            "argv": ["synthetic-p12-placeholder", job["object_id"]],
            "cwd_identity": "synthetic-p12-root-no-access",
            "environment_sha256": canonical_sha256({"p12": "synthetic-env"}),
            "input_sha256": sorted(
                {
                    canonical_sha256({"p12": job["job_id"]}),
                    python_validity["artifact_sha256"],
                }
            ),
            "seed": None,
            "timeout_seconds": 30,
            "attempt": 1,
        }
        result_record = {
            "job_id": job["job_id"],
            "attempt": 1,
            "status": "PASS",
            "exit_code": 0,
            "stdout_sha256": canonical_sha256({"p12": job["job_id"], "stdout": 1}),
            "stderr_sha256": canonical_sha256({"p12": job["job_id"], "stderr": 1}),
            "duration_seconds": 0.01,
            "failure_code": "",
            "scientific_outcome": outcome,
            "call_trace_sha256": None,
            "call_trace_identity": None,
        }
        attempt_root = evidence_root / f"jobs/PHASE_7/{job['job_id']}/1"
        create_intent(attempt_root, intent)
        write_result(attempt_root, result_record)
        jobs["PHASE_7"].append(job["job_id"])
        terminal_pairs.append({"intent": intent, "result": result_record})
        result_rows.append({"job_id": job["job_id"], "scientific_outcome": outcome})
    p12_summary = recompute_p12_summary(denominator, terminal_pairs)
    p12_refs = {}
    p12_paths = {}
    for field, artifact in (
        ("denominator", denominator),
        ("result_rows", result_rows),
        ("summary", p12_summary),
    ):
        path = evidence_root / f"p12/{field}.json"
        _write_json(path, artifact)
        p12_paths[field] = path
        p12_refs[field] = _indexed_reference(evidence_root, path)

    ledger_path = evidence_root / "ledger.jsonl"
    events = reconstruct_attempt_events(evidence_root / "jobs")
    ledger_path.write_bytes(b"".join(canonical_json_bytes(event) for event in events))

    phase_receipts = []
    phase_output_paths = {}
    for phase in PHASES:
        expected_path = evidence_root / f"phase-artifacts/{phase}/expected-jobs.json"
        _write_json(expected_path, sorted(jobs[phase]))
        if phase == "PHASE_0":
            output_body = {
                "schema_version": "p3-synthetic-origin-receipt-v1",
                "repository_identity": preflight_receipt["repository_identity"],
                "origin_transport": preflight_receipt["origin_transport"],
                "origin_sha256": preflight_receipt["origin_sha256"],
                "synthetic_only": True,
            }
        elif phase == "PHASE_7":
            output_body = {
                "schema_version": "p3-synthetic-completion-v1",
                "claims_status": "blocked",
                "real_p12_access": False,
                "real_scientific_jobs": 0,
                "subject_count": 2,
                "ecosystem_count": 2,
                "ecosystems": ["cmake", "python"],
                "scale_classes": ["M", "S"],
                "infrastructure_only": True,
            }
        else:
            output_body = {
                "schema_version": "p3-synthetic-phase-output-v1",
                "phase": phase,
                "infrastructure_only": True,
            }
        output_path = evidence_root / f"phase-artifacts/{phase}/output.json"
        output = _self_hashed(output_body)
        _write_json(output_path, output)
        receipt = close_phase(
            phase,
            protocol_sha256,
            sorted(jobs[phase]),
            ledger_path,
            output["artifact_sha256"],
        )
        receipt_path = evidence_root / f"phase-artifacts/{phase}/receipt.json"
        _write_json(receipt_path, receipt)
        phase_output_paths[phase] = output_path
        phase_receipts.append(
            {
                "phase": phase,
                "receipt": _indexed_reference(evidence_root, receipt_path),
                "expected_jobs": _indexed_reference(evidence_root, expected_path),
                "output_manifest": _indexed_reference(evidence_root, output_path),
            }
        )

    claims = _blocked_claim_ledger(
        "authority-rq_spec_sha256.bin",
        "authority-claim_ceiling_sha256.bin",
        "protocol.json",
    )
    claims_path = evidence_root / "claims.json"
    _write_json(claims_path, claims)

    for cache in evidence_root.rglob("__pycache__"):
        shutil.rmtree(cache)

    index_body = {
        "schema_version": "P3_V3_EVIDENCE_INDEX_V1",
        "phase_coverage": list(PHASES),
        "protocol": _indexed_reference(evidence_root, protocol_path),
        "protocol_artifacts": {
            field: _indexed_reference(evidence_root, authorities["artifacts"][field])
            for field in authorities["artifacts"]
        },
        "adapter_registries": [
            _indexed_reference(evidence_root, authorities["adapter_registry_path"])
        ],
        "input_generator_registries": [
            _indexed_reference(evidence_root, authorities["generator_registry_path"])
        ],
        "subjects": subject_indexes,
        "packages": package_entries,
        "mr_chain": mr_chain,
        "job_root": "jobs",
        "ledger": _indexed_reference(evidence_root, ledger_path),
        "phase_receipts": phase_receipts,
        "p12": p12_refs,
        "claims": _indexed_reference(evidence_root, claims_path),
    }
    index_path = evidence_root / "evidence-index.json"
    _write_evidence_index(index_path, index_body)
    return {
        "root": evidence_root,
        "index_path": index_path,
        "phase_outputs": phase_output_paths,
        "materials": materials,
        "preflight_root": p12_repo,
        "preflight_spec": preflight_spec_path,
    }


def _rewrite_index(index_path: Path, index: dict) -> None:
    _refresh_self_hash(index)
    index_path.write_bytes(canonical_json_bytes(index))


def _rewrite_reference(root: Path, index: dict, reference: dict, value) -> None:
    path = root / reference["path"]
    if isinstance(value, dict):
        _refresh_self_hash(value)
    path.write_bytes(canonical_json_bytes(value))
    reference["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    _rewrite_index(root / "evidence-index.json", index)


def _rehash_ledger_events(events: list[dict]) -> list[dict]:
    previous = None
    rebuilt = []
    for sequence, event in enumerate(events, start=1):
        body = {
            **{key: value for key, value in event.items() if key != "event_sha256"},
            "sequence": sequence,
            "previous_event_sha256": previous,
        }
        rebuilt_event = {**body, "event_sha256": canonical_sha256(body)}
        rebuilt.append(rebuilt_event)
        previous = rebuilt_event["event_sha256"]
    return rebuilt


def _refresh_protocol_bound_attempts(root: Path, index: dict) -> None:
    protocol_sha256 = index["protocol"]["sha256"]
    for intent_path in (root / index["job_root"]).rglob("intent.json"):
        intent = read_canonical_json(intent_path)
        intent["protocol_sha256"] = protocol_sha256
        intent_path.write_bytes(canonical_json_bytes(intent))
    events = reconstruct_attempt_events(root / index["job_root"])
    ledger_path = root / index["ledger"]["path"]
    ledger_path.write_bytes(b"".join(canonical_json_bytes(event) for event in events))
    index["ledger"]["sha256"] = hashlib.sha256(ledger_path.read_bytes()).hexdigest()
    for entry in index["phase_receipts"]:
        expected_jobs = read_canonical_json(root / entry["expected_jobs"]["path"])
        output = read_canonical_json(root / entry["output_manifest"]["path"])
        receipt = close_phase(
            entry["phase"],
            protocol_sha256,
            expected_jobs,
            ledger_path,
            output["artifact_sha256"],
        )
        receipt_path = root / entry["receipt"]["path"]
        receipt_path.write_bytes(canonical_json_bytes(receipt))
        entry["receipt"]["sha256"] = hashlib.sha256(
            receipt_path.read_bytes()
        ).hexdigest()


def _refresh_indexed_phase_receipt(root: Path, index: dict, phase: str) -> None:
    entry = next(item for item in index["phase_receipts"] if item["phase"] == phase)
    expected_jobs = read_canonical_json(root / entry["expected_jobs"]["path"])
    output = read_canonical_json(root / entry["output_manifest"]["path"])
    receipt = close_phase(
        phase,
        index["protocol"]["sha256"],
        expected_jobs,
        root / index["ledger"]["path"],
        output["artifact_sha256"],
    )
    receipt_path = root / entry["receipt"]["path"]
    receipt_path.write_bytes(canonical_json_bytes(receipt))
    entry["receipt"]["sha256"] = hashlib.sha256(
        receipt_path.read_bytes()
    ).hexdigest()


def _reconstruct_completion_metadata(fixture: dict, payload: dict) -> dict:
    root = fixture["root"]
    index = read_canonical_json(fixture["index_path"])
    claims = read_canonical_json(root / index["claims"]["path"])
    statuses = {claim["status"] for claim in claims["claims"]}
    ecosystems = sorted(
        {
            read_canonical_json(root / subject["build_descriptor"]["path"])[
                "ecosystem"
            ]
            for subject in index["subjects"]
        }
    )
    scale_classes = sorted(
        {
            read_canonical_json(root / subject["source_scale"]["path"])[
                "scale_class"
            ]
            for subject in index["subjects"]
        }
    )
    intents = [
        read_canonical_json(path)
        for path in (root / index["job_root"]).rglob("intent.json")
    ]
    real_p12_access = any(
        intent["job_role"] == "P12"
        and intent["cwd_identity"] != "synthetic-p12-root-no-access"
        for intent in intents
    )
    real_scientific_jobs = sum(
        1
        for intent in intents
        if intent["job_role"] in {"PRIMARY_CONTROLLED", "P12", "CONTRACT_SENSITIVITY"}
        and not intent["cwd_identity"].startswith("synthetic-")
    )
    body = {
        "schema_version": "p3-synthetic-completion-v1",
        "claims_status": statuses.pop() if len(statuses) == 1 else "mixed",
        "real_p12_access": real_p12_access,
        "real_scientific_jobs": real_scientific_jobs,
        "subject_count": payload["verified_subject_count"],
        "ecosystem_count": len(ecosystems),
        "ecosystems": ecosystems,
        "scale_classes": scale_classes,
        "infrastructure_only": not real_p12_access and real_scientific_jobs == 0,
    }
    return _self_hashed(body)


def _run_complete_verification(fixture: dict) -> tuple[subprocess.CompletedProcess, str | None]:
    evidence_result = _cli("verify-evidence", "--index", str(fixture["index_path"]))
    if evidence_result.returncode != 0:
        return evidence_result, json.loads(evidence_result.stderr)["code"]
    preflight_output = fixture["root"].parent / "reverified-preflight.json"
    preflight_result = _cli(
        "run-preflight",
        "--root",
        str(fixture["preflight_root"]),
        "--spec",
        str(fixture["preflight_spec"]),
        "--output",
        str(preflight_output),
    )
    if preflight_result.returncode != 0:
        return evidence_result, json.loads(preflight_result.stderr)["code"]
    regenerated = read_canonical_json(preflight_output)
    declared_origin = read_canonical_json(fixture["phase_outputs"]["PHASE_0"])
    origin_fields = ("repository_identity", "origin_transport", "origin_sha256")
    if any(declared_origin[field] != regenerated[field] for field in origin_fields):
        return evidence_result, "E_PREFLIGHT_RECEIPT_RECONSTRUCTION"
    payload = json.loads(evidence_result.stdout)
    declared_completion = read_canonical_json(fixture["phase_outputs"]["PHASE_7"])
    if declared_completion != _reconstruct_completion_metadata(fixture, payload):
        return evidence_result, "E_COMPLETION_METADATA_RECONSTRUCTION"
    return evidence_result, None


MUTATION_ERRORS = {
    "adapter_byte": "E_INDEXED_SUBJECT_REDERIVATION",
    "adapter_output": "E_INDEXED_SUBJECT_REDERIVATION",
    "source_scale": "E_INDEXED_SUBJECT_REDERIVATION",
    "schema": "E_INDEXED_SUBJECT_REDERIVATION",
    "workload": "E_INDEXED_SUBJECT_REDERIVATION",
    "common_input": "E_INDEXED_SUBJECT_REDERIVATION",
    "fallback_order": "E_INDEXED_SUBJECT_REDERIVATION",
    "technique_label": "E_INDEXED_SUBJECT_REDERIVATION",
    "site": "E_INDEXED_SUBJECT_REDERIVATION",
    "retry_argv": "E_RETRY_IDENTITY",
    "retry_seed": "E_RETRY_IDENTITY",
    "event": "E_LEDGER_RECONSTRUCTION",
    "ledger": "E_LEDGER_RECONSTRUCTION",
    "receipt": "E_PHASE_RECEIPT",
    "package_byte": "E_PACKAGE_SHA256",
    "slot_coordinate": "E_SLOT_COORDINATE",
    "mr_parent": "E_MR_PARENT",
    "denominator": "E_P12_WEIGHT",
    "p12_result": "E_P12_RESULT_ROWS",
    "p12_summary": "E_P12_SUMMARY",
    "claim_status": "E_CLAIM_STATUS",
    "index_membership": "E_INDEX_UNINDEXED",
    "origin_receipt": "E_PREFLIGHT_RECEIPT_RECONSTRUCTION",
    "completion_metadata": "E_COMPLETION_METADATA_RECONSTRUCTION",
}


def _mutate_complete_evidence(fixture: dict, mutation: str) -> None:
    root = fixture["root"]
    index_path = fixture["index_path"]
    index = read_canonical_json(index_path)
    subject = index["subjects"][0]

    if mutation == "adapter_byte":
        registry_ref = index["adapter_registries"][0]
        registry_path = root / registry_ref["path"]
        registry = read_canonical_json(registry_path)
        adapter = registry["adapters"][0]
        implementation = registry_path.parent / adapter["implementation_path"]
        implementation.write_bytes(implementation.read_bytes() + b"\n# rehashed mutation\n")
        adapter["source_sha256"] = hashlib.sha256(implementation.read_bytes()).hexdigest()
        _refresh_self_hash(registry)
        registry_path.write_bytes(canonical_json_bytes(registry))
        registry_ref["sha256"] = hashlib.sha256(registry_path.read_bytes()).hexdigest()
        protocol_path = root / index["protocol"]["path"]
        protocol = read_canonical_json(protocol_path)
        protocol["adapter_registry_sha256"] = registry_ref["sha256"]
        _refresh_self_hash(protocol)
        protocol_path.write_bytes(canonical_json_bytes(protocol))
        index["protocol"]["sha256"] = hashlib.sha256(protocol_path.read_bytes()).hexdigest()
        for indexed_subject in index["subjects"]:
            indexed_subject["adapter_registry_sha256"] = registry["artifact_sha256"]
        _refresh_protocol_bound_attempts(root, index)
        _rewrite_index(index_path, index)
        return
    if mutation == "adapter_output":
        ref = subject["adapter_discovery"]
        artifact = read_canonical_json(root / ref["path"])
        artifact["declarations"][0]["entrypoint"] = "forged.module:entrypoint"
        _rewrite_reference(root, index, ref, artifact)
        return
    if mutation == "source_scale":
        ref = subject["source_scale"]
        artifact = read_canonical_json(root / ref["path"])
        artifact["scale_class"] = "M"
        _rewrite_reference(root, index, ref, artifact)
        return
    if mutation == "schema":
        ref = subject["public_frame"]
        artifact = read_canonical_json(root / ref["path"])
        artifact["public_schemas"][0]["raw_schema"] = {"type": "forged"}
        _rewrite_reference(root, index, ref, artifact)
        return
    if mutation in {"workload", "fallback_order"}:
        ref = subject["profiling_workload"]
        artifact = read_canonical_json(root / ref["path"])
        if mutation == "workload":
            artifact["selected_rows"] = list(reversed(artifact["selected_rows"]))
            artifact["selected_behavior_ids"] = list(
                reversed(artifact["selected_behavior_ids"])
            )
        else:
            artifact["category_order"] = list(reversed(artifact["category_order"]))
        _rewrite_reference(root, index, ref, artifact)
        return
    if mutation == "common_input":
        ref = subject["common_inputs"]
        artifact = read_canonical_json(root / ref["path"])
        artifact["rows"][0]["raw_payload_sha256"] = "0" * 64
        _rewrite_reference(root, index, ref, artifact)
        return
    if mutation == "technique_label":
        ref = subject["technique_profile"]
        artifact = read_canonical_json(root / ref["path"])
        artifact["primary_technique"] = "TECH_UNCERTAIN"
        _rewrite_reference(root, index, ref, artifact)
        return
    if mutation == "site":
        ref = subject["sites"]
        artifact = read_canonical_json(root / ref["path"])
        artifact[0]["symbol"] = "forged_site"
        _rewrite_reference(root, index, ref, artifact)
        return
    if mutation in {"retry_argv", "retry_seed"}:
        intent_path = root / "jobs/PHASE_5/infra-phase-5/2/intent.json"
        intent = read_canonical_json(intent_path)
        if mutation == "retry_argv":
            intent["argv"] = ["forged-retry"]
        else:
            intent["seed"] = 99
        intent_path.write_bytes(canonical_json_bytes(intent))
        return
    if mutation in {"event", "ledger"}:
        ledger_ref = index["ledger"]
        ledger_path = root / ledger_ref["path"]
        events = [json.loads(line) for line in ledger_path.read_text().splitlines()]
        if mutation == "event":
            events[0]["artifact_sha256"] = "0" * 64
            events = _rehash_ledger_events(events)
        else:
            events.pop()
        ledger_path.write_bytes(b"".join(canonical_json_bytes(event) for event in events))
        ledger_ref["sha256"] = hashlib.sha256(ledger_path.read_bytes()).hexdigest()
        _rewrite_index(index_path, index)
        return
    if mutation == "receipt":
        entry = index["phase_receipts"][3]
        ref = entry["receipt"]
        receipt = read_canonical_json(root / ref["path"])
        receipt["terminal_result_count"] += 1
        _rewrite_reference(root, index, ref, receipt)
        return
    if mutation == "package_byte":
        package_file = root / index["packages"][0]["root"] / "source.py"
        package_file.write_text("value = 2\n", encoding="utf-8")
        return
    if mutation == "slot_coordinate":
        subject["slot_artifacts"][0]["controlled_subject_id"] = "0" * 64
        _rewrite_index(index_path, index)
        return
    if mutation == "mr_parent":
        ref = index["mr_chain"]["final_inventory"]
        artifact = read_canonical_json(root / ref["path"])
        artifact["custodian_receipt_sha256"] = "0" * 64
        _rewrite_reference(root, index, ref, artifact)
        return
    if mutation == "denominator":
        ref = index["p12"]["denominator"]
        artifact = read_canonical_json(root / ref["path"])
        artifact["jobs"][0]["weight"] = 2
        artifact["job_inventory_sha256"] = canonical_sha256(artifact["jobs"])
        _rewrite_reference(root, index, ref, artifact)
        return
    if mutation == "p12_result":
        ref = index["p12"]["result_rows"]
        rows = read_canonical_json(root / ref["path"])
        rows[0]["scientific_outcome"] = "MR_SATISFIED"
        _rewrite_reference(root, index, ref, rows)
        return
    if mutation == "p12_summary":
        ref = index["p12"]["summary"]
        summary = read_canonical_json(root / ref["path"])
        summary["lower_numerator"] += 1
        _rewrite_reference(root, index, ref, summary)
        return
    if mutation == "claim_status":
        ref = index["claims"]
        claims = read_canonical_json(root / ref["path"])
        claims["claims"][0]["status"] = "supported"
        _refresh_self_hash(claims["claims"][0])
        _rewrite_reference(root, index, ref, claims)
        return
    if mutation == "index_membership":
        index["p12"] = {}
        _rewrite_index(index_path, index)
        return
    if mutation == "origin_receipt":
        entry = index["phase_receipts"][0]
        ref = entry["output_manifest"]
        receipt = read_canonical_json(root / ref["path"])
        receipt["origin_sha256"] = "0" * 64
        _rewrite_reference(root, index, ref, receipt)
        index = read_canonical_json(index_path)
        _refresh_indexed_phase_receipt(root, index, "PHASE_0")
        _rewrite_index(index_path, index)
        return
    if mutation == "completion_metadata":
        entry = index["phase_receipts"][-1]
        ref = entry["output_manifest"]
        completion = read_canonical_json(root / ref["path"])
        completion.update(
            {
                "claims_status": "supported",
                "real_p12_access": True,
                "real_scientific_jobs": 999,
                "subject_count": 0,
                "ecosystem_count": 0,
                "ecosystems": [],
                "scale_classes": [],
                "infrastructure_only": False,
            }
        )
        _rewrite_reference(root, index, ref, completion)
        index = read_canonical_json(index_path)
        _refresh_indexed_phase_receipt(root, index, "PHASE_7")
        _rewrite_index(index_path, index)
        return
    raise AssertionError(f"unknown mutation: {mutation}")


def test_two_subject_phase0_to_phase7_path_is_production_verified(tmp_path):
    fixture = _build_complete_evidence(tmp_path)

    result, boundary_error = _run_complete_verification(fixture)

    assert boundary_error is None
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "PASS"
    assert payload["phase_coverage"] == PHASES
    assert payload["verified_subject_count"] == 2
    assert payload["manifest_count"] == 3
    assert payload["phase_receipt_count"] == 8
    assert payload["slot_artifact_count"] == 2
    assert payload["verified_p12_result_count"] == 5
    assert payload["verified_claim_count"] == 7
    completion = read_canonical_json(fixture["phase_outputs"]["PHASE_7"])
    assert completion == _self_hashed(
        {
            "schema_version": "p3-synthetic-completion-v1",
            "claims_status": "blocked",
            "real_p12_access": False,
            "real_scientific_jobs": 0,
            "subject_count": 2,
            "ecosystem_count": 2,
            "ecosystems": ["cmake", "python"],
            "scale_classes": ["M", "S"],
            "infrastructure_only": True,
        }
    )


@pytest.mark.parametrize(("mutation", "expected_code"), MUTATION_ERRORS.items())
def test_rehashed_mutation_matrix_is_rejected_by_independent_reconstruction(
    tmp_path, mutation, expected_code
):
    fixture = _build_complete_evidence(tmp_path)
    _mutate_complete_evidence(fixture, mutation)

    result, observed_code = _run_complete_verification(fixture)

    assert observed_code == expected_code, (mutation, result.stdout, result.stderr)
    if mutation not in {"origin_receipt", "completion_metadata"}:
        assert result.returncode == 2
        assert not result.stdout
        assert json.loads(result.stderr) == {"code": expected_code, "status": "FAIL"}
    else:
        assert result.returncode == 0
        assert json.loads(result.stdout)["status"] == "PASS"
