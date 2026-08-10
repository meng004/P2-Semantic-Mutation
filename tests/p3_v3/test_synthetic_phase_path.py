from __future__ import annotations

import hashlib
import json
import os
import socket
import subprocess
from pathlib import Path

import pytest

from p3_v3.artifacts import canonical_sha256, read_canonical_json, write_canonical_json
from p3_v3.bridge_and_frames import (
    APPLICABLE_SLOT_CHRONOLOGY,
    E_CONTRACT_GENERATOR_IDS,
    UNAVAILABLE_NOT_CLAIMED,
    build_contract_inputs,
    close_slot,
    tag_site_reachability,
    validate_contract_generator_registry,
    validate_mr_inventory,
    validate_proposal_record,
    verify_reveal,
    verify_slot_chronology,
)
from p3_v3.packages import (
    PACKAGE_B_PRIMARY_CLASSES,
    PACKAGE_B_SENSITIVITY_CLASSES,
    PROPOSER_ALLOWED_CLASSES,
    build_package,
    materialize_package,
    verify_package,
)
from p3_v3.run_records import (
    P12_OUTCOME_STATES,
    create_intent,
    freeze_p12_denominator,
    reduce_attempts,
    summarize_p12_outcomes,
    write_result,
)

ROOT = Path(__file__).resolve().parents[2]
CLI = ROOT / "scripts/p3_v3/evidence.py"
FIXTURE_ROOT = Path(__file__).resolve().parent / "fixtures" / "public_behavior"
GENERATOR_ROOT = Path(__file__).resolve().parent / "fixtures" / "input_generators"
SCIENTIFIC_PLAN_SHA256 = "fea00496801c31ba074aa74742f5e6a77019ffc2e344642122a15462d7443830"
EVIDENCE_DESIGN_SHA256 = "7e614e96aac833786d1b29580f8fae7d3f03c6567d7ca94f3e3c017addad2fa9"
TECHNIQUE_ORDER = [
    "HYBRID_NATIVE",
    "TENSOR_AUTODIFF",
    "PROBABILISTIC_SURROGATE",
    "ITERATIVE_STOCHASTIC",
    "ARRAY_NUMERICAL",
    "SCALAR_CONTROL",
    "TECH_UNCERTAIN",
]
P12_OUTCOMES = [
    "MR_VIOLATION",
    "MR_SATISFIED",
    "DECLARED_EXCEPTION_OR_TIMEOUT_VIOLATION",
    "SCIENTIFIC_INCONCLUSIVE",
    "INFRASTRUCTURE_UNRESOLVED",
]
BEHAVIOR_CATEGORY_ORDER = [
    "PUBLIC_API",
    "CLI",
    "EXAMPLE",
    "BENCHMARK",
    "PROJECT_TEST",
]
_ADAPTER_SPECS = (
    ("PYTHON_PEP517_V1", "python", "adapters/python_pep517_v1.py"),
    ("CMAKE_CTEST_V1", "cmake", "adapters/cmake_ctest_v1.py"),
    ("MESON_TEST_V1", "meson", "adapters/meson_test_v1.py"),
    ("AUTOTOOLS_MAKECHECK_V1", "autotools", "adapters/autotools_makecheck_v1.py"),
)
_CONTRACT_GENERATOR_TEMPLATE = '''\
def generate(schema_bytes: bytes, seed: int):
    return {{
        "envelope": {{
            "generator_id": "{generator_id}",
            "schema_version": "p3-contract-input-envelope-v1",
            "seed": seed,
        }},
        "raw_payload_sha256": __import__("hashlib").sha256(
            schema_bytes + seed.to_bytes(8, "big")
        ).hexdigest(),
    }}
'''


def _bytes(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode() + b"\n"


def _sha(value):
    return hashlib.sha256(_bytes(value)).hexdigest()


def _git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(root), *args], capture_output=True, check=True, text=True
    ).stdout.strip()


def _write(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(_bytes(value))


def _cli(*args: str):
    result = subprocess.run(
        ["python3", str(CLI), *args],
        capture_output=True, check=False,
        text=True,
        env={**os.environ, "PYTHONPATH": str(ROOT / "src")},
    )
    payload = json.loads(result.stdout) if result.stdout else json.loads(result.stderr)
    return result.returncode, payload


@pytest.fixture(autouse=True)
def _block_network(monkeypatch):
    def _blocked(*_args, **_kwargs):
        raise OSError("network disabled in synthetic evidence path")

    monkeypatch.setattr(socket, "create_connection", _blocked)
    monkeypatch.setattr(socket, "getaddrinfo", _blocked)


def _tagged_declarations(name: str) -> list[dict]:
    fixture = json.loads((FIXTURE_ROOT / name).read_text(encoding="utf-8"))
    rows = []
    for item in fixture["declarations"]:
        row = dict(item)
        row["ecosystem"] = fixture["ecosystem"]
        if fixture.get("adapter_id") is not None:
            row["adapter_id"] = fixture["adapter_id"]
        rows.append(row)
    return rows


def _adapter_registry(root: Path) -> dict:
    adapters = []
    for adapter_id, ecosystem, rel in _ADAPTER_SPECS:
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"# adapter {adapter_id}\n", encoding="utf-8")
        adapters.append(
            {
                "adapter_id": adapter_id,
                "ecosystem": ecosystem,
                "implementation_path": rel,
                "source_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }
        )
    body = {"schema_version": "p3-adapter-registry-v1", "adapters": adapters}
    return {**body, "artifact_sha256": canonical_sha256(body)}


def _contract_generator_registry(root: Path) -> dict:
    generators = []
    for generator_id in E_CONTRACT_GENERATOR_IDS:
        rel = f"generators/{generator_id.lower()}.py"
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            _CONTRACT_GENERATOR_TEMPLATE.format(generator_id=generator_id),
            encoding="utf-8",
        )
        generators.append(
            {
                "generator_id": generator_id,
                "schema_kind": generator_id,
                "implementation_path": rel,
                "source_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "output_schema": {
                    "generator_id": generator_id,
                    "schema_version": "p3-contract-input-envelope-v1",
                },
                "failure_code": f"{generator_id}_INVALID",
            }
        )
    body = {
        "schema_version": "p3-contract-generator-registry-v1",
        "generators": generators,
    }
    return {**body, "artifact_sha256": canonical_sha256(body)}


def test_synthetic_phase0_to_phase7_evidence_path(tmp_path):
    repo = tmp_path / "p12"
    repo.mkdir()
    _git(repo, "init")
    _git(repo, "config", "user.name", "Fixture")
    _git(repo, "config", "user.email", "fixture@example.invalid")
    _git(repo, "remote", "add", "origin", "https://github.com/Example/P12-Defect4MR.git")

    contract = {"schema_version": "p12-p3-contract-v2", "claim": "fixture"}
    _write(repo / "release/contract.json", contract)
    contract_blob = _git(repo, "hash-object", "release/contract.json")
    package_root = "1" * 64
    source_sha = "21" * 32
    archive_sha = "3" * 64
    build_sha = "22" * 32
    fixed_oid = "5" * 40
    nonce = bytes.fromhex("6" * 64)
    commitment = hashlib.sha256(
        b"P3-FIXED-TREE-v1" + package_root.encode() + fixed_oid.encode() + nonce
    ).hexdigest()
    neutral = _sha(
        {
            "p12_package_root_sha256": package_root,
            "normalized_source_tree_sha256": source_sha,
            "source_archive_sha256": archive_sha,
            "domain": "P3-NEUTRAL-SNAPSHOT-v1",
        }
    )
    records = [
        {
            "neutral_snapshot_id": neutral,
            "fixed_tree_commitment": commitment,
            "normalized_source_tree_sha256": source_sha,
            "source_archive_sha256": archive_sha,
            "build_descriptor_sha256": build_sha,
            "eligibility_reason": "fixture",
            "eligible_for_construct": True,
            "eligible_for_criterion": True,
        }
    ]
    bridge_body = {
        "schema_version": "p3-p12-bridge-v1",
        "p12_release_id": "fixture-v2",
        "p12_repository_identity": "Example/P12-Defect4MR",
        "p12_contract_path": "release/contract.json",
        "p12_contract_blob_sha": contract_blob,
        "p12_package_root_sha256": package_root,
        "p12_contract_sha256": hashlib.sha256(_bytes(contract)).hexdigest(),
        "eligible_inventory_root_sha256": _sha(records),
        "eligible_item_count": 1,
        "records": records,
        "trust_mode": "PINNED_GIT_RELEASE",
    }
    _write(repo / "release/bridge.json", {**bridge_body, "artifact_sha256": _sha(bridge_body)})
    (repo / "requirements.lock").write_text("dependency==1\n", encoding="utf-8")
    (repo / "input.json").write_text("{}\n", encoding="utf-8")
    (repo / "program.py").write_text("print(1)\n", encoding="utf-8")
    (repo / "source.py").write_text("x=1\n", encoding="utf-8")
    (repo / "proposal.json").write_text("{}\n", encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "synthetic release")
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
    protocol_body = {
        "schema_version": "p3-protocol-v1",
        "scientific_plan_sha256": SCIENTIFIC_PLAN_SHA256,
        "evidence_design_sha256": EVIDENCE_DESIGN_SHA256,
        "claims_initial_status": "blocked",
        "rq_spec_sha256": canonical_sha256({"fixture": "rq"}),
        "claim_ceiling_sha256": canonical_sha256({"fixture": "ceiling"}),
        "p12_contract_sha256": canonical_sha256({"fixture": "p12"}),
        "operator_catalogue_sha256": canonical_sha256({"fixture": "operators"}),
        "adapter_registry_sha256": canonical_sha256({"fixture": "adapters"}),
        "input_generator_registry_sha256": canonical_sha256({"fixture": "generators"}),
        "mr_policy_sha256": canonical_sha256({"fixture": "mr"}),
        "site_policy_sha256": canonical_sha256({"fixture": "site"}),
        "analysis_spec_sha256": canonical_sha256({"fixture": "analysis"}),
        "package_policy_sha256": canonical_sha256({"fixture": "package"}),
        "environment_lock_sha256": canonical_sha256({"fixture": "env"}),
        "profiling_budgets": {"S": 10, "M": 15, "L": 20},
        "behavior_category_order": list(BEHAVIOR_CATEGORY_ORDER),
        "technique_order": list(TECHNIQUE_ORDER),
        "e_common_count": 30,
        "e_contract_count": 5,
        "p12_outcome_states": list(P12_OUTCOMES),
        "p12_primary_estimand": "INTENTION_TO_EVALUATE_LOWER_BOUND",
        "infrastructure_retry_limit": 3,
    }
    protocol = {**protocol_body, "artifact_sha256": canonical_sha256(protocol_body)}

    adapter_root = tmp_path / "adapter-root"
    adapter_root.mkdir()
    adapter_registry = _adapter_registry(adapter_root)
    declarations = _tagged_declarations("python.json") + _tagged_declarations("cmake.json")
    source_record = {
        "normalized_source_tree_sha256": source_sha,
        "build_descriptor_sha256": build_sha,
    }
    generator_registry = json.loads((GENERATOR_ROOT / "registry.json").read_text())

    # Provisional features/slots filled after first frame pass identities exist.
    # build-frames needs profiling rows matching the selected workload; prepare a
    # dry-run via CLI after writing placeholders, then rewrite profiling if needed.
    # Instead, precompute workload behavior ids by invoking the same modules through CLI
    # after writing a first-cut profiling list built from fixture declarations' counts.
    # Practical approach: call build-frames twice is heavy; build profiling after a
    # helper module path inside the test by reading selected rows from a staged run.
    # We stage inputs, run a Python helper through the CLI build path only once by
    # constructing profiling results via an intermediate local selection.
    from p3_v3.bridge_and_frames import (
        build_public_behavior_frame,
        select_profiling_workload,
        validate_adapter_registry,
    )

    validated_adapters = validate_adapter_registry(adapter_registry, adapter_root)
    provisional_frame = build_public_behavior_frame(
        source_record, declarations, validated_adapters
    )
    provisional_workload = select_profiling_workload(provisional_frame, "S")
    site_a = {
        "path": "program.py",
        "symbol": "module",
        "start_line": 1,
        "start_col": 0,
        "end_line": 1,
        "end_col": 8,
    }
    site_b = {
        "path": "source.py",
        "symbol": "helper",
        "start_line": 1,
        "start_col": 0,
        "end_line": 1,
        "end_col": 3,
    }
    features = [
        {
            "neutral_snapshot_id": neutral,
            "public_workload_set_sha256": provisional_workload["artifact_sha256"],
            "scale_class": "S",
            "primary_technique": "ARRAY_NUMERICAL",
            "technique_vector": ["ARRAY_NUMERICAL"],
            "sites": [site_a, site_b],
        }
    ]
    # Reach only the first site in synthetic profiling rows.
    # Site ids are derived later; use observed_site_ids empty in profiling and
    # tag_site_reachability separately with reconstructed site ids.
    profiling_results = []
    for index, row in enumerate(provisional_workload["selected_rows"]):
        if index == 0:
            profiling_results.append(
                {
                    "behavior_id": row["behavior_id"],
                    "status": "FAILURE",
                    "technique_tags": [],
                    "observed_site_ids": [],
                }
            )
        else:
            profiling_results.append(
                {
                    "behavior_id": row["behavior_id"],
                    "status": "SUCCESS",
                    "technique_tags": ["SCALAR_CONTROL"],
                    "observed_site_ids": [],
                }
            )

    protocol_path = tmp_path / "protocol.json"
    lock_path = tmp_path / "lock.json"
    source_path = tmp_path / "source-record.json"
    adapter_path = tmp_path / "adapter-registry.json"
    declarations_path = tmp_path / "declarations.json"
    generator_path = tmp_path / "generator-registry.json"
    profiling_path = tmp_path / "profiling-results.json"
    features_path = tmp_path / "features.json"
    slots_path = tmp_path / "slots.json"
    contracts_path = tmp_path / "contracts.json"
    applicability_path = tmp_path / "applicability.json"
    for path, value in (
        (protocol_path, protocol),
        (lock_path, lock),
        (source_path, source_record),
        (adapter_path, validated_adapters),
        (declarations_path, declarations),
        (generator_path, generator_registry),
        (profiling_path, profiling_results),
        (features_path, features),
        (slots_path, []),
        (contracts_path, {}),
        (applicability_path, {}),
    ):
        _write(path, value)

    bridge_output = tmp_path / "verified-bridge.json"
    frames_root = tmp_path / "frames-out"

    # 1) validate protocol
    code, payload = _cli("validate-protocol", "--protocol", str(protocol_path))
    assert code == 0 and payload["status"] == "PASS"
    protocol_sha = payload["protocol_sha256"]
    assert protocol["claims_initial_status"] == "blocked"

    # 2) verify pinned synthetic bridge
    code, payload = _cli(
        "verify-bridge",
        "--repo-root",
        str(repo),
        "--lock",
        str(lock_path),
        "--output",
        str(bridge_output),
    )
    assert code == 0 and payload["status"] == "PASS"
    verified_bridge = read_canonical_json(bridge_output)

    # Prepare slots after we know subject id from a dry subject-frame build via CLI.
    # First build-frames with empty slots to get subject frames and E_COMMON.
    code, payload = _cli(
        "build-frames",
        "--bridge",
        str(bridge_output),
        "--source-record",
        str(source_path),
        "--adapter-registry",
        str(adapter_path),
        "--adapter-root",
        str(adapter_root),
        "--declarations",
        str(declarations_path),
        "--input-generator-registry",
        str(generator_path),
        "--generator-root",
        str(GENERATOR_ROOT),
        "--profiling-results",
        str(profiling_path),
        "--features",
        str(features_path),
        "--slots",
        str(slots_path),
        "--contracts",
        str(contracts_path),
        "--applicability-map",
        str(applicability_path),
        "--scale-class",
        "S",
        "--output-root",
        str(frames_root),
    )
    assert code == 0, payload
    assert payload["status"] == "PASS"

    public_frame = read_canonical_json(frames_root / "public-behavior-frame.json")
    workload = read_canonical_json(frames_root / "profiling-workload.json")
    common_inputs = read_canonical_json(frames_root / "evaluation-inputs-common.json")
    technique_profile = read_canonical_json(frames_root / "technique-profile.json")
    subject_frames = read_canonical_json(frames_root / "subject-frames.json")

    assert len(common_inputs["rows"]) == 30
    assert workload["budget"] == 10
    assert technique_profile["primary_technique"] in TECHNIQUE_ORDER
    subject = subject_frames["subjects"][0]
    subject_id = subject["controlled_subject_id"]
    sites = subject["sites"]
    assert len(sites) == 2

    # Independent UNPROFILED vs NOT_APPLICABLE distinction
    observed_results = [
        {
            "behavior_id": profiling_results[1]["behavior_id"],
            "status": "SUCCESS",
            "technique_tags": ["SCALAR_CONTROL"],
            "observed_site_ids": [sites[0]["site_id"]],
        }
    ]
    tagged = tag_site_reachability(
        sites,
        observed_results,
        lambda site: site["symbol"] == "module",
    )
    by_id = {row["site_id"]: row for row in tagged}
    assert by_id[sites[0]["site_id"]]["reachability"] == "OBSERVED_REACHABLE"
    assert by_id[sites[0]["site_id"]]["applicability"] == "APPLICABLE"
    assert by_id[sites[1]["site_id"]]["reachability"] == "UNPROFILED"
    assert by_id[sites[1]["site_id"]]["applicability"] == "NOT_APPLICABLE"

    # Close one applicable and one NOT_APPLICABLE slot; rebuild frames with slots.
    slot_applicable = {
        "slot_id": "aa" * 32,
        "controlled_subject_id": subject_id,
    }
    slot_na = {
        "slot_id": "bb" * 32,
        "controlled_subject_id": subject_id,
    }
    closed_applicable = close_slot(
        slot_applicable, sites, lambda site: site["symbol"] == "module"
    )
    closed_na = close_slot(slot_na, sites, lambda _site: False)
    assert closed_applicable["path"] == "APPLICABLE"
    assert closed_na["path"] == "APPLICABILITY_CLOSED_NOT_APPLICABLE"

    contract_gen_root = tmp_path / "contract-gens"
    contract_gen_root.mkdir()
    contract_registry = validate_contract_generator_registry(
        _contract_generator_registry(contract_gen_root), contract_gen_root
    )
    frozen_contract = {
        "contract_id": "cc" * 32,
        "generator_id": "CONTRACT_NUMERIC_DOMAIN_V1",
        "domain": {"domain": "numeric", "bounds": [0, 1]},
        "site_id": closed_applicable["site_id"],
    }
    e_contract = build_contract_inputs(
        closed_applicable, frozen_contract, contract_registry
    )
    assert len(e_contract["rows"]) == 5

    patch = {"patch_id": "dd" * 32, "bytes_sha256": "ee" * 32}
    witness = {"witness_id": "ff" * 32}
    applicable_artifacts = {
        "slot_id": slot_applicable["slot_id"],
        "chronology": list(APPLICABLE_SLOT_CHRONOLOGY),
        "contract": frozen_contract,
        "e_contract": e_contract,
        "patch": patch,
        "certification_witness": witness,
        "e_common_input_ids": [row["input_id"] for row in common_inputs["rows"]],
        "e_contract_input_ids": [row["input_id"] for row in e_contract["rows"]],
    }
    na_artifacts = {
        "slot_id": slot_na["slot_id"],
        "chronology": ["APPLICABILITY_CLOSED_NOT_APPLICABLE"],
        "contract": None,
        "e_contract": None,
        "patch": None,
        "certification_witness": None,
        "e_common_input_ids": [],
        "e_contract_input_ids": [],
    }
    verify_slot_chronology(applicable_artifacts)
    verify_slot_chronology(na_artifacts)

    proposal = validate_proposal_record(
        {
            "schema_version": "p3-proposal-record-v1",
            "provider_model": "synthetic/fixture-v1",
            "prompt_sha256": "11" * 32,
            "context_sha256": "22" * 32,
            "response_sha256": "33" * 32,
            "timestamp_utc": "2026-08-10T00:00:00Z",
            "exposed_generation_metadata": {"finish_reason": "stop"},
            "temperature": UNAVAILABLE_NOT_CLAIMED,
            "seed": UNAVAILABLE_NOT_CLAIMED,
            "top_p": UNAVAILABLE_NOT_CLAIMED,
        }
    )

    # Package A + proposer view
    package_a_root = tmp_path / "package-a-src"
    package_a_root.mkdir()
    (package_a_root / "source.py").write_text("x=1\n", encoding="utf-8")
    write_canonical_json(package_a_root / "e_common.json", common_inputs, exclusive=True)
    write_canonical_json(package_a_root / "e_contract.json", e_contract, exclusive=True)
    write_canonical_json(package_a_root / "contract.json", frozen_contract, exclusive=True)
    write_canonical_json(package_a_root / "proposal.json", proposal, exclusive=True)
    write_canonical_json(
        package_a_root / "public_behavior_frame.json", public_frame, exclusive=True
    )
    write_canonical_json(
        package_a_root / "profiling_workload.json", workload, exclusive=True
    )
    write_canonical_json(
        package_a_root / "profiling_result.json",
        {"rows": profiling_results},
        exclusive=True,
    )
    write_canonical_json(
        package_a_root / "slot.json", closed_applicable, exclusive=True
    )
    specs_a = [
        {"path": "source.py", "class": "SOURCE"},
        {"path": "e_common.json", "class": "E_COMMON"},
        {"path": "e_contract.json", "class": "E_CONTRACT"},
        {"path": "contract.json", "class": "CONTRACT"},
        {"path": "proposal.json", "class": "PROPOSAL_INPUT"},
        {"path": "public_behavior_frame.json", "class": "PUBLIC_BEHAVIOR_FRAME"},
        {"path": "profiling_workload.json", "class": "PROFILING_WORKLOAD"},
        {"path": "profiling_result.json", "class": "PROFILING_RESULT"},
        {"path": "slot.json", "class": "SLOT"},
    ]
    specs_a_path = tmp_path / "specs-a.json"
    parents_path = tmp_path / "parents.json"
    _write(specs_a_path, specs_a)
    _write(parents_path, [])
    manifest_a_path = tmp_path / "package-a.json"
    code, payload = _cli(
        "build-package",
        "--role",
        "CONSTRUCTION_A",
        "--root",
        str(package_a_root),
        "--specs",
        str(specs_a_path),
        "--parents",
        str(parents_path),
        "--output",
        str(manifest_a_path),
    )
    assert code == 0 and payload["status"] == "PASS"
    code, payload = _cli(
        "verify-package",
        "--root",
        str(package_a_root),
        "--manifest",
        str(manifest_a_path),
    )
    assert code == 0 and payload["status"] == "PASS"
    manifest_a = read_canonical_json(manifest_a_path)
    proposer_root = tmp_path / "proposer"
    materialize_package(
        package_a_root, proposer_root, manifest_a, allowed_classes=PROPOSER_ALLOWED_CLASSES
    )
    proposer_files = {
        path.relative_to(proposer_root).as_posix()
        for path in proposer_root.rglob("*")
        if path.is_file()
    }
    assert "e_common.json" not in proposer_files
    assert "profiling_result.json" not in proposer_files
    assert "source.py" in proposer_files

    # Package B primary and sensitivity views
    package_b_primary = tmp_path / "package-b-primary"
    package_b_primary.mkdir()
    (package_b_primary / "exec.py").write_text("print(1)\n", encoding="utf-8")
    write_canonical_json(
        package_b_primary / "primary.json",
        {"role": "E_COMMON_PRIMARY", "input_id": common_inputs["rows"][0]["input_id"]},
        exclusive=True,
    )
    write_canonical_json(
        package_b_primary / "denominator.json",
        {"placeholder": True},
        exclusive=True,
    )
    primary_manifest = build_package(
        "CONTROLLED_B",
        package_b_primary,
        [
            {"path": "exec.py", "class": "EXECUTION_CODE"},
            {"path": "primary.json", "class": "E_COMMON_PRIMARY"},
            {"path": "denominator.json", "class": "DENOMINATOR"},
        ],
        [manifest_a["artifact_sha256"]],
        allowed_classes=PACKAGE_B_PRIMARY_CLASSES,
    )
    verify_package(package_b_primary, primary_manifest)

    package_b_sensitivity = tmp_path / "package-b-sensitivity"
    package_b_sensitivity.mkdir()
    (package_b_sensitivity / "exec.py").write_text("print(1)\n", encoding="utf-8")
    write_canonical_json(
        package_b_sensitivity / "sensitivity.json",
        {"role": "E_CONTRACT_SENSITIVITY", "input_id": e_contract["rows"][0]["input_id"]},
        exclusive=True,
    )
    sensitivity_manifest = build_package(
        "CONTROLLED_B",
        package_b_sensitivity,
        [
            {"path": "exec.py", "class": "EXECUTION_CODE"},
            {"path": "sensitivity.json", "class": "E_CONTRACT_SENSITIVITY"},
        ],
        [manifest_a["artifact_sha256"]],
        allowed_classes=PACKAGE_B_SENSITIVITY_CLASSES,
    )
    verify_package(package_b_sensitivity, sensitivity_manifest)

    # Preflight with Task 8 fields
    preflight = {
        "schema_version": "p3-preflight-v1",
        "repository_identity": "Example/P12-Defect4MR",
        "expected_commit": commit,
        "dependency_lock_path": "requirements.lock",
        "dependency_lock_sha256": hashlib.sha256(
            (repo / "requirements.lock").read_bytes()
        ).hexdigest(),
        "phase_inputs": [
            {
                "path": "input.json",
                "sha256": hashlib.sha256((repo / "input.json").read_bytes()).hexdigest(),
            }
        ],
        "smoke_commands": [["python3", "-c", "print(1)"]],
        "timeout_seconds": 10,
        "phase_role": "CONTROLLED_B",
        "minimum_cpu_count": 1,
        "minimum_memory_bytes": 1,
        "minimum_disk_free_bytes": 1,
        "worker_limit": 1,
    }
    preflight_path = tmp_path / "preflight.json"
    preflight_output = tmp_path / "preflight-result.json"
    _write(preflight_path, preflight)
    code, payload = _cli(
        "run-preflight",
        "--root",
        str(repo),
        "--spec",
        str(preflight_path),
        "--output",
        str(preflight_output),
    )
    assert code == 0 and payload["status"] == "PASS"
    assert payload["phase_role"] == "CONTROLLED_B"
    assert not list(repo.glob("**/intent.json"))

    # Immutable synthetic job attempts + ledger + phase close
    jobs_root = tmp_path / "jobs"
    ledger_path = tmp_path / "ledger.jsonl"
    intent = {
        "job_id": "synth-job-1",
        "protocol_sha256": protocol_sha,
        "phase": "PHASE-CONTROLLED",
        "argv": ["python3", "-c", "print(1)"],
        "cwd_identity": str(repo),
        "environment_sha256": "ab" * 32,
        "input_sha256": [common_inputs["rows"][0]["input_id"]],
        "seed": None,
        "timeout_seconds": 30,
        "attempt": 1,
        "object_type": "SEMANTIC_MUTANT",
        "object_id": "mut-synth-1",
        "mr_id": "mr-synth-1",
        "evaluation_input_class": "E_COMMON",
        "evaluation_input_id": common_inputs["rows"][0]["input_id"],
        "repetition_id": 1,
        "environment_id": "env-synth",
        "job_role": "PRIMARY_CONTROLLED",
    }
    attempt_dir = jobs_root / "synth-job-1" / "1"
    create_intent(attempt_dir, intent)
    write_result(
        attempt_dir,
        {
            "job_id": "synth-job-1",
            "attempt": 1,
            "status": "PASS",
            "exit_code": 0,
            "stdout_sha256": "cd" * 32,
            "stderr_sha256": "ef" * 32,
            "duration_seconds": 0.1,
            "failure_code": "",
            "scientific_outcome": None,
        },
    )
    events = reduce_attempts(jobs_root, ledger_path)
    assert len(events) == 2
    code, payload = _cli("verify-run-records", "--ledger", str(ledger_path))
    assert code == 0 and payload["status"] == "PASS"

    expected_jobs_path = tmp_path / "expected-jobs.json"
    receipt_path = tmp_path / "phase-receipt.json"
    _write(expected_jobs_path, ["synth-job-1"])
    code, payload = _cli(
        "close-phase",
        "--phase-id",
        "PHASE-CONTROLLED",
        "--protocol-sha256",
        protocol_sha,
        "--expected-jobs",
        str(expected_jobs_path),
        "--ledger",
        str(ledger_path),
        "--output-manifest-sha256",
        primary_manifest["artifact_sha256"],
        "--output",
        str(receipt_path),
    )
    assert code == 0 and payload["status"] == "PASS"

    # Reveal commitment on synthetic Package C (module API; no Package C materialization)
    reveal = {
        "neutral_snapshot_id": neutral,
        "fixed_git_tree_oid": fixed_oid,
        "reveal_nonce": nonce.hex(),
        "normalized_source_tree_sha256": source_sha,
    }
    verify_reveal(
        verified_bridge["records"][0],
        reveal,
        package_root,
        observed_tree_oid=fixed_oid,
        observed_normalized_sha256=source_sha,
    )

    # MR inventory chronology
    mr_body = {
        "schema_version": "p3-mr-inventory-v1",
        "candidate_frame_sha256": canonical_sha256({"stage": "candidate"}),
        "custodian_receipt_sha256": canonical_sha256({"stage": "receipt"}),
        "final_inventory_sha256": canonical_sha256({"stage": "final"}),
        "portfolios_sha256": canonical_sha256({"stage": "portfolios"}),
        "chronology": [
            "candidate_frame",
            "custodian_receipt",
            "final_inventory",
            "portfolios",
        ],
    }
    mr_inventory = {**mr_body, "artifact_sha256": canonical_sha256(mr_body)}
    validate_mr_inventory(mr_inventory)
    mr_path = tmp_path / "mr-inventory.json"
    _write(mr_path, mr_inventory)
    code, payload = _cli("verify-mr-inventory", "--inventory", str(mr_path))
    assert code == 0

    # Freeze P12 denominator before results; record all five outcomes; summarize
    paired_ids = [f"fault-{index}" for index in range(5)]
    p12_jobs = [
        {
            "job_id": f"p12-{index}",
            "object_type": "P12_FAULT",
            "object_id": paired_ids[index],
            "mr_id": "mr-synth-1",
            "evaluation_input_class": "E_COMMON",
            "evaluation_input_id": common_inputs["rows"][index]["input_id"],
            "repetition_id": 1,
            "environment_id": "env-synth",
            "job_role": "P12",
            "weight": 1,
        }
        for index in range(5)
    ]
    denominator = freeze_p12_denominator(paired_ids, p12_jobs)
    results = [
        {"job_id": f"p12-{index}", "scientific_outcome": P12_OUTCOME_STATES[index]}
        for index in range(5)
    ]
    summary = summarize_p12_outcomes(denominator, results)
    assert summary["planned_count"] == 5
    assert summary["state_counts"][P12_OUTCOME_STATES[0]] == 1
    assert summary["lower_numerator"] == 2
    assert summary["upper_numerator"] == 4
    assert summary["complete_case_denominator"] == 3

    claims_body = {
        "schema_version": "p3-claim-evidence-v1",
        "claims": [
            {"claim_id": "RQ1", "status": "blocked"},
            {"claim_id": "RQ2", "status": "blocked"},
            {"claim_id": "RQ3", "status": "blocked"},
            {"claim_id": "RQ4", "status": "blocked"},
        ],
    }
    claims = {**claims_body, "artifact_sha256": canonical_sha256(claims_body)}
    claims_path = tmp_path / "claims.json"
    denom_path = tmp_path / "denominator.json"
    summary_path = tmp_path / "p12-summary.json"
    slot_path = tmp_path / "slot-artifacts.json"
    common_path = tmp_path / "common-inputs.json"
    manifest_b_path = tmp_path / "package-b-primary.json"
    for path, value in (
        (claims_path, claims),
        (denom_path, denominator),
        (summary_path, summary),
        (slot_path, applicable_artifacts),
        (common_path, common_inputs),
        (manifest_b_path, primary_manifest),
    ):
        _write(path, value)

    code, payload = _cli(
        "verify-evidence",
        "--protocol",
        str(protocol_path),
        "--manifest",
        str(manifest_a_path),
        "--manifest",
        str(manifest_b_path),
        "--ledger",
        str(ledger_path),
        "--phase-receipt",
        str(receipt_path),
        "--slot-artifacts",
        str(slot_path),
        "--common-inputs",
        str(common_path),
        "--denominator",
        str(denom_path),
        "--p12-summary",
        str(summary_path),
        "--claims",
        str(claims_path),
    )
    assert code == 0, payload
    assert payload["status"] == "PASS"
    assert payload["claims_status"] == "blocked"
    assert all(claim["status"] == "blocked" for claim in claims["claims"])
    assert public_frame["schema_version"] == "p3-public-behavior-frame-v1"
