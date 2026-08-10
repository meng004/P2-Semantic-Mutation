from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

from p3_v3.artifacts import canonical_sha256, write_canonical_json
from p3_v3.bridge_and_frames import (
    build_public_behavior_frame,
    select_profiling_workload,
    validate_adapter_registry,
)

ROOT = Path(__file__).resolve().parents[2]
CLI = ROOT / "scripts/p3_v3/evidence.py"
FIXTURE_ROOT = Path(__file__).resolve().parent / "fixtures" / "public_behavior"
COMMANDS = {
    "validate-protocol",
    "verify-bridge",
    "build-frames",
    "verify-mr-inventory",
    "build-package",
    "verify-package",
    "run-preflight",
    "verify-run-records",
    "close-phase",
    "verify-evidence",
}
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
P12_OUTCOME_STATES = [
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


def _env():
    return {**os.environ, "PYTHONPATH": str(ROOT / "src")}


def _digest(label: str) -> str:
    return canonical_sha256({"fixture": label})


def _protocol_body(**overrides):
    body = {
        "schema_version": "p3-protocol-v1",
        "scientific_plan_sha256": SCIENTIFIC_PLAN_SHA256,
        "evidence_design_sha256": EVIDENCE_DESIGN_SHA256,
        "claims_initial_status": "blocked",
        "rq_spec_sha256": _digest("rq"),
        "claim_ceiling_sha256": _digest("ceiling"),
        "p12_contract_sha256": _digest("p12"),
        "operator_catalogue_sha256": _digest("operators"),
        "adapter_registry_sha256": _digest("adapters"),
        "input_generator_registry_sha256": _digest("generators"),
        "mr_policy_sha256": _digest("mr"),
        "site_policy_sha256": _digest("site"),
        "analysis_spec_sha256": _digest("analysis"),
        "package_policy_sha256": _digest("package"),
        "environment_lock_sha256": _digest("env"),
        "profiling_budgets": {"S": 10, "M": 15, "L": 20},
        "behavior_category_order": list(BEHAVIOR_CATEGORY_ORDER),
        "technique_order": list(TECHNIQUE_ORDER),
        "e_common_count": 30,
        "e_contract_count": 5,
        "p12_outcome_states": list(P12_OUTCOME_STATES),
        "p12_primary_estimand": "INTENTION_TO_EVALUATE_LOWER_BOUND",
        "infrastructure_retry_limit": 3,
    }
    body.update(overrides)
    return body


def _write_protocol(path: Path, body: dict) -> bytes:
    payload = {**body}
    if "artifact_sha256" not in payload:
        payload["artifact_sha256"] = canonical_sha256(payload)
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode() + b"\n"
    path.write_bytes(raw)
    return raw


def _adapter_registry(tmp_path: Path) -> dict:
    adapters = []
    for adapter_id, ecosystem, rel in _ADAPTER_SPECS:
        path = tmp_path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"# adapter {adapter_id}\n", encoding="utf-8")
        adapters.append(
            {
                "adapter_id": adapter_id,
                "ecosystem": ecosystem,
                "implementation_path": rel,
                "source_sha256": __import__("hashlib").sha256(path.read_bytes()).hexdigest(),
            }
        )
    body = {"schema_version": "p3-adapter-registry-v1", "adapters": adapters}
    return {**body, "artifact_sha256": canonical_sha256(body)}


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


def test_cli_help_lists_only_frozen_commands():
    result = subprocess.run(
        ["python3", str(CLI), "--help"], capture_output=True, check=False, text=True, env=_env()
    )
    assert result.returncode == 0
    line = next(item for item in result.stdout.splitlines() if "{" in item and "}" in item)
    observed = set(line[line.index("{") + 1 : line.index("}")].split(","))
    assert observed == COMMANDS


def test_validate_protocol_prints_one_canonical_json_result(tmp_path):
    protocol = tmp_path / "protocol.json"
    raw = _write_protocol(protocol, _protocol_body())
    result = subprocess.run(
        ["python3", str(CLI), "validate-protocol", "--protocol", str(protocol)],
        capture_output=True, check=False,
        text=True,
        env=_env(),
    )
    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["status"] == "PASS"
    assert payload["protocol_sha256"] == __import__("hashlib").sha256(raw).hexdigest()
    assert result.stdout == json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n"


def test_validate_protocol_rejects_a_different_well_formed_plan_hash(tmp_path):
    protocol = tmp_path / "protocol.json"
    _write_protocol(protocol, _protocol_body(scientific_plan_sha256="a" * 64))
    result = subprocess.run(
        ["python3", str(CLI), "validate-protocol", "--protocol", str(protocol)],
        capture_output=True, check=False,
        text=True,
        env=_env(),
    )
    assert result.returncode == 2
    assert json.loads(result.stderr)["code"] == "E_PROTOCOL_AUTHORITY"


def test_validate_protocol_rejects_extra_key_before_writing_output(tmp_path):
    protocol = tmp_path / "protocol.json"
    body = _protocol_body()
    body["extra_field"] = "nope"
    body["artifact_sha256"] = canonical_sha256(
        {key: value for key, value in body.items() if key != "artifact_sha256"}
    )
    protocol.write_bytes(
        json.dumps(body, sort_keys=True, separators=(",", ":")).encode() + b"\n"
    )
    result = subprocess.run(
        [
            "python3",
            str(CLI),
            "validate-protocol",
            "--protocol",
            str(protocol),
        ],
        capture_output=True, check=False,
        text=True,
        env=_env(),
    )
    assert result.returncode == 2
    assert json.loads(result.stderr)["code"] == "E_SCHEMA_KEYS"


def test_validate_protocol_rejects_missing_key(tmp_path):
    protocol = tmp_path / "protocol.json"
    body = _protocol_body()
    del body["e_common_count"]
    body["artifact_sha256"] = canonical_sha256(body)
    protocol.write_bytes(
        json.dumps(body, sort_keys=True, separators=(",", ":")).encode() + b"\n"
    )
    result = subprocess.run(
        ["python3", str(CLI), "validate-protocol", "--protocol", str(protocol)],
        capture_output=True, check=False,
        text=True,
        env=_env(),
    )
    assert result.returncode == 2
    assert json.loads(result.stderr)["code"] == "E_SCHEMA_KEYS"


def test_validate_protocol_rejects_old_authority_digest(tmp_path):
    protocol = tmp_path / "protocol.json"
    _write_protocol(
        protocol,
        _protocol_body(
            scientific_plan_sha256="911562938a14ad3955a6c1e38080185ba78e92dbf4401efcb10d7c169e4a2772",
            evidence_design_sha256="e2a943b30f8096aa65a72c43aa514df67b8d58e16fcf7209930799ee4444c346",
        ),
    )
    result = subprocess.run(
        ["python3", str(CLI), "validate-protocol", "--protocol", str(protocol)],
        capture_output=True, check=False,
        text=True,
        env=_env(),
    )
    assert result.returncode == 2
    assert json.loads(result.stderr)["code"] == "E_PROTOCOL_AUTHORITY"


def test_validate_protocol_rejects_wrong_counts_retry_or_outcome_order(tmp_path):
    cases = [
        {"e_common_count": 29},
        {"e_contract_count": 4},
        {"infrastructure_retry_limit": 4},
        {
            "p12_outcome_states": [
                "MR_SATISFIED",
                "MR_VIOLATION",
                "DECLARED_EXCEPTION_OR_TIMEOUT_VIOLATION",
                "SCIENTIFIC_INCONCLUSIVE",
                "INFRASTRUCTURE_UNRESOLVED",
            ]
        },
    ]
    for overrides in cases:
        protocol = tmp_path / f"protocol-{next(iter(overrides))}.json"
        _write_protocol(protocol, _protocol_body(**overrides))
        result = subprocess.run(
            ["python3", str(CLI), "validate-protocol", "--protocol", str(protocol)],
            capture_output=True, check=False,
            text=True,
            env=_env(),
        )
        assert result.returncode == 2
        assert json.loads(result.stderr)["code"] in {
            "E_PROTOCOL",
            "E_PROTOCOL_COUNTS",
            "E_PROTOCOL_RETRY",
            "E_PROTOCOL_OUTCOMES",
        }


def test_verify_mr_inventory_accepts_exact_chronology(tmp_path):
    body = {
        "schema_version": "p3-mr-inventory-v1",
        "candidate_frame_sha256": _digest("candidate"),
        "custodian_receipt_sha256": _digest("receipt"),
        "final_inventory_sha256": _digest("final"),
        "portfolios_sha256": _digest("portfolios"),
        "chronology": [
            "candidate_frame",
            "custodian_receipt",
            "final_inventory",
            "portfolios",
        ],
    }
    inventory = {**body, "artifact_sha256": canonical_sha256(body)}
    path = tmp_path / "mr.json"
    path.write_bytes(
        json.dumps(inventory, sort_keys=True, separators=(",", ":")).encode() + b"\n"
    )
    result = subprocess.run(
        ["python3", str(CLI), "verify-mr-inventory", "--inventory", str(path)],
        capture_output=True, check=False,
        text=True,
        env=_env(),
    )
    assert result.returncode == 0
    assert json.loads(result.stdout)["status"] == "PASS"


def test_build_frames_writes_declared_artifacts_under_output_root_only(tmp_path):
    adapter_root = tmp_path / "adapters-root"
    adapter_root.mkdir()
    registry = validate_adapter_registry(_adapter_registry(adapter_root), adapter_root)
    source_record = {
        "normalized_source_tree_sha256": "21" * 32,
        "build_descriptor_sha256": "22" * 32,
    }
    declarations = _tagged_declarations("python.json") + _tagged_declarations("cmake.json")
    frame = build_public_behavior_frame(source_record, declarations, registry)
    workload = select_profiling_workload(frame, "S")
    profiling_results = [
        {
            "behavior_id": row["behavior_id"],
            "status": "SUCCESS",
            "technique_tags": ["SCALAR_CONTROL"],
            "observed_site_ids": [],
        }
        for row in workload["selected_rows"]
    ]
    bridge = {
        "schema_version": "p3-p12-bridge-v1",
        "p12_release_id": "fixture",
        "p12_repository_identity": "Example/P12-Defect4MR",
        "p12_contract_path": "release/contract.json",
        "p12_contract_blob_sha": "0" * 40,
        "p12_package_root_sha256": "1" * 64,
        "p12_contract_sha256": "2" * 64,
        "eligible_inventory_root_sha256": "3" * 64,
        "eligible_item_count": 1,
        "trust_mode": "PINNED_GIT_RELEASE",
        "records": [
            {
                "neutral_snapshot_id": canonical_sha256({"fixture": "neutral"}),
                "fixed_tree_commitment": "4" * 64,
                "normalized_source_tree_sha256": "21" * 32,
                "source_archive_sha256": "5" * 64,
                "build_descriptor_sha256": "22" * 32,
                "eligibility_reason": "fixture",
                "eligible_for_construct": True,
                "eligible_for_criterion": True,
            }
        ],
    }
    bridge = {**bridge, "artifact_sha256": canonical_sha256(bridge)}
    features = [
        {
            "neutral_snapshot_id": bridge["records"][0]["neutral_snapshot_id"],
            "public_workload_set_sha256": workload["artifact_sha256"],
            "scale_class": "S",
            "primary_technique": "ARRAY_NUMERICAL",
            "technique_vector": ["ARRAY_NUMERICAL"],
            "sites": [
                {
                    "path": "program.py",
                    "symbol": "module",
                    "start_line": 1,
                    "start_col": 0,
                    "end_line": 1,
                    "end_col": 8,
                }
            ],
        }
    ]
    generator_registry = json.loads(
        (
            Path(__file__).resolve().parent
            / "fixtures/input_generators/registry.json"
        ).read_text(encoding="utf-8")
    )
    generator_root = Path(__file__).resolve().parent / "fixtures/input_generators"
    outside = tmp_path / "outside"
    outside.mkdir()
    output_root = tmp_path / "frames-out"
    paths = {
        "bridge": tmp_path / "bridge.json",
        "source": tmp_path / "source.json",
        "adapters": tmp_path / "adapters.json",
        "declarations": tmp_path / "declarations.json",
        "generators": tmp_path / "generators.json",
        "profiling": tmp_path / "profiling.json",
        "features": tmp_path / "features.json",
        "slots": tmp_path / "slots.json",
        "contracts": tmp_path / "contracts.json",
        "applicability": tmp_path / "applicability.json",
    }
    write_canonical_json(paths["bridge"], bridge, exclusive=True)
    write_canonical_json(paths["source"], source_record, exclusive=True)
    write_canonical_json(paths["adapters"], registry, exclusive=True)
    write_canonical_json(paths["declarations"], declarations, exclusive=True)
    write_canonical_json(paths["generators"], generator_registry, exclusive=True)
    write_canonical_json(paths["profiling"], profiling_results, exclusive=True)
    write_canonical_json(paths["features"], features, exclusive=True)
    write_canonical_json(paths["slots"], [], exclusive=True)
    write_canonical_json(paths["contracts"], {}, exclusive=True)
    write_canonical_json(paths["applicability"], {}, exclusive=True)

    result = subprocess.run(
        [
            "python3",
            str(CLI),
            "build-frames",
            "--bridge",
            str(paths["bridge"]),
            "--source-record",
            str(paths["source"]),
            "--adapter-registry",
            str(paths["adapters"]),
            "--adapter-root",
            str(adapter_root),
            "--declarations",
            str(paths["declarations"]),
            "--input-generator-registry",
            str(paths["generators"]),
            "--generator-root",
            str(generator_root),
            "--profiling-results",
            str(paths["profiling"]),
            "--features",
            str(paths["features"]),
            "--slots",
            str(paths["slots"]),
            "--contracts",
            str(paths["contracts"]),
            "--applicability-map",
            str(paths["applicability"]),
            "--scale-class",
            "S",
            "--output-root",
            str(output_root),
        ],
        capture_output=True, check=False,
        text=True,
        env=_env(),
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "PASS"
    expected = {
        "public-behavior-frame.json",
        "profiling-workload.json",
        "evaluation-inputs-common.json",
        "technique-profile.json",
        "subject-frames.json",
    }
    written = {path.name for path in output_root.iterdir() if path.is_file()}
    assert expected <= written
    assert list(outside.iterdir()) == []
    common = json.loads((output_root / "evaluation-inputs-common.json").read_text())
    assert len(common["rows"]) == 30
    assert all(row["status"] == "COMMON_INPUT_UNAVAILABLE" for row in common["rows"])


def test_verify_evidence_validates_complete_evidence_set(tmp_path):
    protocol = tmp_path / "protocol.json"
    _write_protocol(protocol, _protocol_body())
    claims_body = {
        "schema_version": "p3-claim-evidence-v1",
        "claims": [{"claim_id": "RQ1", "status": "blocked"}],
    }
    claims = {**claims_body, "artifact_sha256": canonical_sha256(claims_body)}
    claims_path = tmp_path / "claims.json"
    write_canonical_json(claims_path, claims, exclusive=True)

    manifest_body = {
        "schema_version": "p3-package-manifest-v1",
        "role": "CONSTRUCTION_A",
        "parents": [],
        "files": [],
        "package_tree_sha256": canonical_sha256([]),
    }
    manifest = {**manifest_body, "artifact_sha256": canonical_sha256(manifest_body)}
    manifest_path = tmp_path / "manifest.json"
    write_canonical_json(manifest_path, manifest, exclusive=True)

    ledger = tmp_path / "ledger.jsonl"
    ledger.write_bytes(b"")

    from p3_v3.run_records import close_phase

    receipt = close_phase(
        "PHASE-SYNTH",
        "a" * 64,
        [],
        ledger,
        "c" * 64,
    )
    receipt_path = tmp_path / "receipt.json"
    write_canonical_json(receipt_path, receipt, exclusive=True)

    slot_artifacts = {
        "slot_id": "c3" * 32,
        "chronology": ["APPLICABILITY_CLOSED_NOT_APPLICABLE"],
        "contract": None,
        "e_contract": None,
        "patch": None,
        "certification_witness": None,
        "e_common_input_ids": [],
        "e_contract_input_ids": [],
    }
    slot_path = tmp_path / "slot.json"
    write_canonical_json(slot_path, slot_artifacts, exclusive=True)

    common_body = {
        "schema_version": "p3-evaluation-inputs-common-v1",
        "controlled_subject_source_id": "21" * 32,
        "eligible_schema_count": 0,
        "rows": [
            {
                "ordinal": index,
                "seed": index,
                "generator_id": None,
                "schema_kind": None,
                "schema_selection_key": None,
                "raw_schema_sha256": None,
                "status": "COMMON_INPUT_UNAVAILABLE",
                "failure_code": "COMMON_INPUT_UNAVAILABLE",
                "envelope": None,
                "raw_payload_sha256": None,
                "input_id": canonical_sha256({"ordinal": index}),
            }
            for index in range(30)
        ],
    }
    common = {**common_body, "artifact_sha256": canonical_sha256(common_body)}
    common_path = tmp_path / "common.json"
    write_canonical_json(common_path, common, exclusive=True)

    from p3_v3.run_records import freeze_p12_denominator, summarize_p12_outcomes

    jobs = [
        {
            "job_id": f"j-{index}",
            "object_type": "P12_FAULT",
            "object_id": f"fault-{index}",
            "mr_id": "mr-1",
            "evaluation_input_class": "E_COMMON",
            "evaluation_input_id": f"e-{index}",
            "repetition_id": 1,
            "environment_id": "env-1",
            "job_role": "P12",
            "weight": 1,
        }
        for index in range(5)
    ]
    paired = [f"fault-{index}" for index in range(5)]
    denominator = freeze_p12_denominator(paired, jobs)
    denom_path = tmp_path / "denominator.json"
    write_canonical_json(denom_path, denominator, exclusive=True)
    outcomes = list(P12_OUTCOME_STATES)
    summary = summarize_p12_outcomes(
        denominator,
        [
            {"job_id": f"j-{index}", "scientific_outcome": outcomes[index]}
            for index in range(5)
        ],
    )
    summary_path = tmp_path / "summary.json"
    write_canonical_json(summary_path, summary, exclusive=True)

    result = subprocess.run(
        [
            "python3",
            str(CLI),
            "verify-evidence",
            "--protocol",
            str(protocol),
            "--manifest",
            str(manifest_path),
            "--ledger",
            str(ledger),
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
        ],
        capture_output=True, check=False,
        text=True,
        env=_env(),
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "PASS"
    assert payload["claims_status"] == "blocked"
