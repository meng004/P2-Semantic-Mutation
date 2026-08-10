from __future__ import annotations

import json
import hashlib
import os
import subprocess
from pathlib import Path

import pytest

import p3_v3.bridge_and_frames as frames_module
from p3_v3.artifacts import canonical_sha256, write_canonical_json
from p3_v3.bridge_and_frames import (
    build_public_behavior_frame,
    run_adapter_discovery,
    select_profiling_workload,
    validate_adapter_registry,
)

ROOT = Path(__file__).resolve().parents[2]
CLI = ROOT / "scripts/p3_v3/evidence.py"
FIXTURE_ROOT = Path(__file__).resolve().parent / "fixtures" / "public_behavior"
ADAPTER_FIXTURE_ROOT = Path(__file__).resolve().parent / "fixtures" / "adapters"
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
SECRET_ORIGIN = (
    "https://audit-user:TOP_SECRET_TOKEN@github.com/"
    "meng004/P3-Semantic-Mutation.git"
)
SECRET_IDENTITY = "github.com/meng004/P3-Semantic-Mutation"
SECRET_ORIGIN_SHA256 = (
    "8b90a20c89d81eff7287a414ad53840b1d030a1e1d42a409a69396efbe2ec3d2"
)


def _env():
    return {**os.environ, "PYTHONPATH": str(ROOT / "src")}


def _digest(label: str) -> str:
    return canonical_sha256({"fixture": label})


def _source_tree_sha256(root: Path) -> str:
    files = [
        {
            "path": path.relative_to(root).as_posix(),
            "byte_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }
        for path in sorted(root.rglob("*"))
        if path.is_file() and not path.is_symlink()
    ]
    return canonical_sha256(
        {"domain": "P3-NORMALIZED-SOURCE-TREE-v1", "files": files}
    )


def _profiling_receipt(
    workload: dict,
    source_record: dict,
    neutral: str,
    adapter_source_sha256: str | None,
) -> dict:
    rows = [
        {
            "behavior_id": row["behavior_id"],
            "status": "SUCCESS",
            "argv": ["fixture-runner", row["behavior_id"]],
            "input_sha256": ["51" * 32],
            "environment_sha256": "52" * 32,
            "runner_version": "fixture-runner-v1",
            "exit_code": 0,
            "stdout_sha256": "53" * 32,
            "stderr_sha256": "54" * 32,
            "call_trace_sha256": "55" * 32,
            "trace_features": ["SCALAR_CONTROL_OPERATION"],
            "timed_out": False,
            "failure_code": "",
            "observed_site_ids": [],
        }
        for row in workload["selected_rows"]
    ]
    body = {
        "schema_version": "p3-profiling-results-v1",
        "neutral_snapshot_id": neutral,
        "controlled_subject_source_id": workload["controlled_subject_source_id"],
        **source_record,
        "profiling_workload_sha256": workload["artifact_sha256"],
        "adapter_implementation_source_sha256": adapter_source_sha256,
        "runner_implementation_source_sha256": hashlib.sha256(
            Path(frames_module.__file__).read_bytes()
        ).hexdigest(),
        "results": sorted(rows, key=lambda row: row["behavior_id"]),
    }
    return {**body, "artifact_sha256": canonical_sha256(body)}


def _run_git(root: Path, *argv: str) -> str:
    return subprocess.run(
        ["git", "-C", str(root), *argv],
        capture_output=True,
        check=True,
        text=True,
    ).stdout.strip()


def _secret_preflight_fixture(tmp_path: Path) -> tuple[Path, dict]:
    root = tmp_path / "repo"
    root.mkdir()
    _run_git(root, "init")
    _run_git(root, "config", "user.name", "Fixture")
    _run_git(root, "config", "user.email", "fixture@example.invalid")
    _run_git(root, "remote", "add", "origin", SECRET_ORIGIN)
    lock = root / "requirements.lock"
    lock.write_text("dependency==1\n", encoding="utf-8")
    input_path = root / "input.json"
    input_path.write_text("{}\n", encoding="utf-8")
    _run_git(root, "add", "requirements.lock", "input.json")
    _run_git(root, "commit", "-m", "fixture")
    spec = {
        "schema_version": "p3-preflight-v1",
        "repository_identity": SECRET_IDENTITY,
        "expected_commit": _run_git(root, "rev-parse", "HEAD"),
        "dependency_lock_path": "requirements.lock",
        "dependency_lock_sha256": hashlib.sha256(lock.read_bytes()).hexdigest(),
        "phase_inputs": [
            {
                "path": "input.json",
                "sha256": hashlib.sha256(input_path.read_bytes()).hexdigest(),
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
    return root, spec


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
        fixture = ADAPTER_FIXTURE_ROOT / Path(rel).name
        if fixture.is_file():
            path.write_bytes(fixture.read_bytes())
        else:
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


def test_build_frames_subject_specs_are_the_only_subject_authority_options(tmp_path):
    help_result = subprocess.run(
        ["python3", str(CLI), "build-frames", "--help"],
        capture_output=True,
        check=False,
        text=True,
        env=_env(),
    )
    assert help_result.returncode == 0
    assert "--subject-specs" in help_result.stdout
    for removed in ("--declarations", "--features", "--scale-class"):
        assert removed not in help_result.stdout
        output_root = tmp_path / removed.removeprefix("--")
        result = subprocess.run(
            [
                "python3",
                str(CLI),
                "build-frames",
                "--bridge",
                str(tmp_path / "bridge.json"),
                "--subject-specs",
                str(tmp_path / "subject-specs.json"),
                "--adapter-root",
                str(tmp_path),
                "--generator-root",
                str(tmp_path),
                "--slots",
                str(tmp_path / "slots.json"),
                "--contracts",
                str(tmp_path / "contracts.json"),
                "--applicability-map",
                str(tmp_path / "applicability.json"),
                "--output-root",
                str(output_root),
                removed,
                "legacy-authority.json",
            ],
            capture_output=True,
            check=False,
            text=True,
            env=_env(),
        )
        assert result.returncode == 2
        assert f"unrecognized arguments: {removed}" in result.stderr
        assert not output_root.exists()


@pytest.mark.parametrize("case", ["missing", "duplicate", "extra"])
def test_build_frames_subject_spec_coverage_fails_before_adapter_execution(
    tmp_path, case
):
    neutral = _digest("subject-neutral")
    record = {
        "neutral_snapshot_id": neutral,
        "fixed_tree_commitment": "4" * 64,
        "normalized_source_tree_sha256": "21" * 32,
        "source_archive_sha256": "5" * 64,
        "build_descriptor_sha256": "22" * 32,
        "eligibility_reason": "fixture",
        "eligible_for_construct": True,
        "eligible_for_criterion": True,
    }
    bridge = {"records": [record]}
    base_spec = {
        "neutral_snapshot_id": neutral,
        "source_root": str(tmp_path / "must-not-execute"),
        "source_record": {
            "normalized_source_tree_sha256": record["normalized_source_tree_sha256"],
            "build_descriptor_sha256": record["build_descriptor_sha256"],
        },
        "build_descriptor": {"ecosystem": "python"},
        "adapter_registry": {},
        "input_generator_registry": {},
        "profiling_results": {},
    }
    if case == "missing":
        specs = []
    elif case == "duplicate":
        specs = [base_spec, dict(base_spec)]
    else:
        specs = [{**base_spec, "neutral_snapshot_id": _digest("extra-neutral")}]
    paths = {
        "bridge": tmp_path / "bridge.json",
        "specs": tmp_path / "subject-specs.json",
        "slots": tmp_path / "slots.json",
        "contracts": tmp_path / "contracts.json",
        "applicability": tmp_path / "applicability.json",
    }
    for path, value in (
        (paths["bridge"], bridge),
        (paths["specs"], specs),
        (paths["slots"], []),
        (paths["contracts"], {}),
        (paths["applicability"], {}),
    ):
        write_canonical_json(path, value, exclusive=True)
    output_root = tmp_path / "frames-out"
    result = subprocess.run(
        [
            "python3",
            str(CLI),
            "build-frames",
            "--bridge",
            str(paths["bridge"]),
            "--subject-specs",
            str(paths["specs"]),
            "--adapter-root",
            str(tmp_path),
            "--generator-root",
            str(tmp_path),
            "--slots",
            str(paths["slots"]),
            "--contracts",
            str(paths["contracts"]),
            "--applicability-map",
            str(paths["applicability"]),
            "--output-root",
            str(output_root),
        ],
        capture_output=True,
        check=False,
        text=True,
        env=_env(),
    )
    assert result.returncode == 2
    assert json.loads(result.stderr)["code"] == "E_SUBJECT_SPEC_COVERAGE"
    assert not output_root.exists()


def test_run_preflight_stdout_and_receipt_do_not_reveal_secret_origin(tmp_path):
    root, spec = _secret_preflight_fixture(tmp_path)
    spec_path = tmp_path / "preflight.json"
    receipt_path = tmp_path / "receipt.json"
    write_canonical_json(spec_path, spec, exclusive=True)

    result = subprocess.run(
        [
            "python3",
            str(CLI),
            "run-preflight",
            "--root",
            str(root),
            "--spec",
            str(spec_path),
            "--output",
            str(receipt_path),
        ],
        capture_output=True,
        check=False,
        env=_env(),
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["repository_identity"] == SECRET_IDENTITY
    assert payload["origin_transport"] == "HTTPS"
    assert payload["origin_sha256"] == SECRET_ORIGIN_SHA256
    assert "raw_origin" not in payload
    for stream in (result.stdout, result.stderr, receipt_path.read_bytes()):
        assert b"audit-user" not in stream
        assert b"TOP_SECRET_TOKEN" not in stream


def test_run_preflight_error_does_not_reveal_secret_origin(tmp_path):
    root, spec = _secret_preflight_fixture(tmp_path)
    spec["repository_identity"] = "github.com/Other/Repo"
    spec_path = tmp_path / "preflight.json"
    write_canonical_json(spec_path, spec, exclusive=True)

    result = subprocess.run(
        [
            "python3",
            str(CLI),
            "run-preflight",
            "--root",
            str(root),
            "--spec",
            str(spec_path),
        ],
        capture_output=True,
        check=False,
        env=_env(),
    )

    assert result.returncode == 2
    assert json.loads(result.stderr)["code"] == "E_PREFLIGHT_REPOSITORY"
    for stream in (result.stdout, result.stderr):
        assert b"audit-user" not in stream
        assert b"TOP_SECRET_TOKEN" not in stream


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
    raw_registry = _adapter_registry(adapter_root)
    registry = validate_adapter_registry(raw_registry, adapter_root)
    source_root = tmp_path / "source-root"
    source_root.mkdir()
    fixture = json.loads((FIXTURE_ROOT / "python.json").read_text(encoding="utf-8"))
    for relative in fixture["source_files"]:
        path = source_root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("def solve(value):\n    return value\n", encoding="utf-8")
    manifest = source_root / "adapter-python.json"
    write_canonical_json(manifest, fixture, exclusive=True)
    descriptor = {
        "ecosystem": "python",
        "manifest_path": manifest.name,
        "reverse": False,
    }
    source_record = {
        "normalized_source_tree_sha256": _source_tree_sha256(source_root),
        "build_descriptor_sha256": canonical_sha256(descriptor),
    }
    neutral = canonical_sha256({"fixture": "neutral"})
    discovery = run_adapter_discovery(
        source_root, descriptor, registry, "PYTHON_PEP517_V1"
    )
    frame = build_public_behavior_frame(source_record, discovery)
    workload = select_profiling_workload(frame, "S")
    profiling_results = _profiling_receipt(
        workload,
        source_record,
        neutral,
        discovery["implementation_source_sha256"],
    )
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
                "neutral_snapshot_id": neutral,
                "fixed_tree_commitment": "4" * 64,
                "normalized_source_tree_sha256": source_record[
                    "normalized_source_tree_sha256"
                ],
                "source_archive_sha256": "5" * 64,
                "build_descriptor_sha256": source_record[
                    "build_descriptor_sha256"
                ],
                "eligibility_reason": "fixture",
                "eligible_for_construct": True,
                "eligible_for_criterion": True,
            }
        ],
    }
    bridge = {**bridge, "artifact_sha256": canonical_sha256(bridge)}
    generator_registry = json.loads(
        (
            Path(__file__).resolve().parent
            / "fixtures/input_generators/registry.json"
        ).read_text(encoding="utf-8")
    )
    generator_root = Path(__file__).resolve().parent / "fixtures/input_generators"
    subject_specs = [
        {
            "neutral_snapshot_id": bridge["records"][0]["neutral_snapshot_id"],
            "source_root": str(source_root),
            "source_record": source_record,
            "build_descriptor": descriptor,
            "adapter_registry": raw_registry,
            "input_generator_registry": generator_registry,
            "profiling_results": profiling_results,
        }
    ]
    outside = tmp_path / "outside"
    outside.mkdir()
    output_root = tmp_path / "frames-out"
    paths = {
        "bridge": tmp_path / "bridge.json",
        "subject_specs": tmp_path / "subject-specs.json",
        "slots": tmp_path / "slots.json",
        "contracts": tmp_path / "contracts.json",
        "applicability": tmp_path / "applicability.json",
    }
    write_canonical_json(paths["bridge"], bridge, exclusive=True)
    write_canonical_json(paths["subject_specs"], subject_specs, exclusive=True)
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
            "--subject-specs",
            str(paths["subject_specs"]),
            "--adapter-root",
            str(adapter_root),
            "--generator-root",
            str(generator_root),
            "--slots",
            str(paths["slots"]),
            "--contracts",
            str(paths["contracts"]),
            "--applicability-map",
            str(paths["applicability"]),
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
    neutral = bridge["records"][0]["neutral_snapshot_id"]
    expected = {
        f"adapter-discovery-{neutral}.json",
        f"source-scale-{neutral}.json",
        f"public-behavior-frame-{neutral}.json",
        f"profiling-workload-{neutral}.json",
        f"evaluation-inputs-common-{neutral}.json",
        f"profiling-results-{neutral}.json",
        f"technique-profile-{neutral}.json",
        f"derived-subject-{neutral}.json",
        "subject-frames.json",
    }
    written = {path.name for path in output_root.iterdir() if path.is_file()}
    assert expected <= written
    assert list(outside.iterdir()) == []
    common = json.loads(
        (output_root / f"evaluation-inputs-common-{neutral}.json").read_text()
    )
    assert len(common["rows"]) == 30
    assert any(row["status"] == "COMMON_INPUT_EXECUTABLE" for row in common["rows"])


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
