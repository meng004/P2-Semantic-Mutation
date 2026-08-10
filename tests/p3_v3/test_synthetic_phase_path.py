from __future__ import annotations

import hashlib
import json
import os
import subprocess
from pathlib import Path

from p3_v3.artifacts import canonical_sha256


ROOT = Path(__file__).resolve().parents[2]
CLI = ROOT / "scripts/p3_v3/evidence.py"
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
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONPATH": str(ROOT / "src")},
    )
    payload = json.loads(result.stdout) if result.stdout else json.loads(result.stderr)
    return result.returncode, payload


def test_synthetic_phase0_to_phase2_public_cli_path(tmp_path):
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
    source_sha = "2" * 64
    archive_sha = "3" * 64
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
            "fixed_tree_commitment": "4" * 64,
            "normalized_source_tree_sha256": source_sha,
            "source_archive_sha256": archive_sha,
            "build_descriptor_sha256": "5" * 64,
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
        "p12_outcome_states": list(P12_OUTCOME_STATES),
        "p12_primary_estimand": "INTENTION_TO_EVALUATE_LOWER_BOUND",
        "infrastructure_retry_limit": 3,
    }
    protocol = {
        **protocol_body,
        "artifact_sha256": canonical_sha256(protocol_body),
    }
    features = [
        {
            "neutral_snapshot_id": neutral,
            "public_workload_set_sha256": "6" * 64,
            "scale_class": "S",
            "primary_technique": "SCALAR_CONTROL",
            "technique_vector": ["SCALAR_CONTROL"],
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
    specs = [{"path": "program.py", "class": "SOURCE"}]
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
    }
    protocol_path = tmp_path / "protocol.json"
    lock_path = tmp_path / "lock.json"
    features_path = tmp_path / "features.json"
    specs_path = tmp_path / "specs.json"
    parents_path = tmp_path / "parents.json"
    preflight_path = tmp_path / "preflight.json"
    for path, value in (
        (protocol_path, protocol),
        (lock_path, lock),
        (features_path, features),
        (specs_path, specs),
        (parents_path, []),
        (preflight_path, preflight),
    ):
        _write(path, value)
    bridge_output = tmp_path / "verified-bridge.json"
    frames_output = tmp_path / "frames.json"
    manifest_output = tmp_path / "package-a.json"
    preflight_output = tmp_path / "preflight-result.json"

    steps = [
        _cli("validate-protocol", "--protocol", str(protocol_path)),
        _cli(
            "verify-bridge",
            "--repo-root",
            str(repo),
            "--lock",
            str(lock_path),
            "--output",
            str(bridge_output),
        ),
        _cli(
            "build-frames",
            "--bridge",
            str(bridge_output),
            "--features",
            str(features_path),
            "--output",
            str(frames_output),
        ),
        _cli(
            "build-package",
            "--role",
            "CONSTRUCTION_A",
            "--root",
            str(repo),
            "--specs",
            str(specs_path),
            "--parents",
            str(parents_path),
            "--output",
            str(manifest_output),
        ),
        _cli(
            "run-preflight",
            "--root",
            str(repo),
            "--spec",
            str(preflight_path),
            "--output",
            str(preflight_output),
        ),
    ]
    assert [code for code, _ in steps] == [0, 0, 0, 0, 0]
    assert all(payload["status"] == "PASS" for _, payload in steps)
    assert len(steps[-1][1]["artifact_sha256"]) == 64
    assert json.loads(preflight_output.read_text())["artifact_sha256"] == steps[-1][1][
        "artifact_sha256"
    ]
    assert not list(repo.glob("**/intent.json"))
