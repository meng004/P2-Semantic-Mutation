from __future__ import annotations

import copy
import hashlib
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path

import pytest

from p3_v3.artifacts import EvidenceError, canonical_sha256, file_sha256
from p3_v3.bridge_and_frames import (
    BEHAVIOR_CATEGORY_ORDER,
    build_public_behavior_frame,
    build_subject_frames,
    select_construct_subjects,
    select_first_applicable_site,
    select_profiling_workload,
    validate_adapter_registry,
    validate_bridge_document,
    verify_pinned_bridge,
    verify_reveal,
)

FIXTURE_ROOT = Path(__file__).resolve().parent / "fixtures" / "public_behavior"
CONFIRMATORY_ADAPTERS = {
    "PYTHON_PEP517_V1",
    "CMAKE_CTEST_V1",
    "MESON_TEST_V1",
    "AUTOTOOLS_MAKECHECK_V1",
}
_ADAPTER_SPECS = (
    ("PYTHON_PEP517_V1", "python", "adapters/python_pep517_v1.py"),
    ("CMAKE_CTEST_V1", "cmake", "adapters/cmake_ctest_v1.py"),
    ("MESON_TEST_V1", "meson", "adapters/meson_test_v1.py"),
    ("AUTOTOOLS_MAKECHECK_V1", "autotools", "adapters/autotools_makecheck_v1.py"),
)


def _bytes(value):
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode() + b"\n"


def _sha(value):
    return hashlib.sha256(_bytes(value)).hexdigest()


def _run(root: Path, *argv: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), *argv], capture_output=True, check=True, text=True
    )
    return result.stdout.strip()


@dataclass
class SyntheticRelease:
    root: Path
    lock: dict
    bridge: dict
    fixed_oid: str
    nonce_hex: str


@pytest.fixture
def synthetic_release(tmp_path) -> SyntheticRelease:
    root = tmp_path / "p12"
    root.mkdir()
    _run(root, "init")
    _run(root, "config", "user.name", "P12 Fixture")
    _run(root, "config", "user.email", "p12@example.invalid")
    contract_path = "release/p3-contract.json"
    bridge_path = "release/p3-bridge.json"
    (root / "release").mkdir()
    contract = {"schema_version": "p12-p3-contract-v2", "claim": "fixture"}
    (root / contract_path).write_bytes(_bytes(contract))
    contract_blob = _run(root, "hash-object", contract_path)

    package_root = "1" * 64
    source_sha = "2" * 64
    archive_sha = "3" * 64
    build_sha = "4" * 64
    fixed_oid = "5" * 40
    nonce = bytes.fromhex("6" * 64)
    commitment = hashlib.sha256(
        b"P3-FIXED-TREE-v1"
        + package_root.encode()
        + fixed_oid.encode()
        + nonce
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
            "eligibility_reason": "synthetic complete record",
            "eligible_for_construct": True,
            "eligible_for_criterion": True,
        }
    ]
    body = {
        "schema_version": "p3-p12-bridge-v1",
        "p12_release_id": "p12-synthetic-v2",
        "p12_repository_identity": "example/P12-Defect4MR",
        "p12_contract_path": contract_path,
        "p12_contract_blob_sha": contract_blob,
        "p12_package_root_sha256": package_root,
        "p12_contract_sha256": hashlib.sha256(_bytes(contract)).hexdigest(),
        "eligible_inventory_root_sha256": _sha(records),
        "eligible_item_count": 1,
        "records": records,
        "trust_mode": "PINNED_GIT_RELEASE",
    }
    bridge = {**body, "artifact_sha256": _sha(body)}
    (root / bridge_path).write_bytes(_bytes(bridge))
    _run(root, "add", "release")
    _run(root, "commit", "-m", "release fixture")
    release_commit = _run(root, "rev-parse", "HEAD")
    bridge_blob = _run(root, "rev-parse", f"{release_commit}:{bridge_path}")
    contract_blob = _run(root, "rev-parse", f"{release_commit}:{contract_path}")
    lock = {
        "repository_identity": "example/P12-Defect4MR",
        "release_commit_sha": release_commit,
        "bridge_path": bridge_path,
        "bridge_blob_sha": bridge_blob,
        "contract_path": contract_path,
        "contract_blob_sha": contract_blob,
        "package_root_sha256": package_root,
    }
    return SyntheticRelease(root, lock, bridge, fixed_oid, nonce.hex())


def test_bridge_is_read_from_exact_pinned_git_release(synthetic_release):
    verified = verify_pinned_bridge(synthetic_release.root, synthetic_release.lock)
    assert verified["trust_mode"] == "PINNED_GIT_RELEASE"
    assert verified["eligible_item_count"] == 1


def test_bridge_rejects_wrong_external_blob_pin(synthetic_release):
    lock = {**synthetic_release.lock, "bridge_blob_sha": "0" * 40}
    with pytest.raises(EvidenceError, match="E_PINNED_BRIDGE_BLOB"):
        verify_pinned_bridge(synthetic_release.root, lock)


def test_visible_bridge_rejects_fixed_tree_oid_even_when_rehashed(synthetic_release):
    bridge = json.loads(json.dumps(synthetic_release.bridge))
    bridge["records"][0]["fixed_git_tree_oid"] = synthetic_release.fixed_oid
    body = {key: value for key, value in bridge.items() if key != "artifact_sha256"}
    bridge["artifact_sha256"] = _sha(body)
    with pytest.raises(EvidenceError, match="E_BRIDGE_RECORD_KEYS"):
        validate_bridge_document(bridge, synthetic_release.lock)


def _features(neutral_id: str):
    return [
        {
            "neutral_snapshot_id": neutral_id,
            "public_workload_set_sha256": "7" * 64,
            "scale_class": "S",
            "primary_technique": "ARRAY_NUMERICAL",
            "technique_vector": ["ARRAY_NUMERICAL", "SCALAR_CONTROL"],
            "sites": [
                {
                    "path": "src/a.py",
                    "symbol": "solve",
                    "start_line": 10,
                    "start_col": 4,
                    "end_line": 10,
                    "end_col": 20,
                }
            ],
        }
    ]


def test_subject_frames_are_input_order_invariant_and_use_subject_id(synthetic_release):
    verified = verify_pinned_bridge(synthetic_release.root, synthetic_release.lock)
    features = _features(verified["records"][0]["neutral_snapshot_id"])
    first = build_subject_frames(verified, features)
    second = build_subject_frames(
        {**verified, "records": list(reversed(verified["records"]))},
        list(reversed(features)),
    )
    assert first == second
    subject = first["subjects"][0]
    assert len(subject["controlled_subject_id"]) == 64
    assert len(subject["sites"][0]["site_id"]) == 64
    assert first["c_criterion"] == [subject["controlled_subject_id"]]
    assert len(first["empty_construct_cells"]) == 20
    assert {
        "scale_class": "S",
        "primary_technique": "SCALAR_CONTROL",
        "status": "EMPTY_FRAME",
    } in first["empty_construct_cells"]


def test_subject_frame_rejects_missing_feature_record(synthetic_release):
    verified = verify_pinned_bridge(synthetic_release.root, synthetic_release.lock)
    with pytest.raises(EvidenceError, match="E_FEATURE_COVERAGE"):
        build_subject_frames(verified, [])


def _subject(subject_id: str, technique: str) -> dict:
    return {
        "controlled_subject_id": subject_id,
        "scale_class": "S",
        "primary_technique": technique,
        "technique_vector": [technique],
    }


def test_construct_selection_continues_strict_round_robin_by_cell():
    subjects = [
        _subject("1" * 64, "ARRAY_NUMERICAL"),
        _subject("2" * 64, "ARRAY_NUMERICAL"),
        _subject("3" * 64, "SCALAR_CONTROL"),
        _subject("4" * 64, "SCALAR_CONTROL"),
    ]
    selected = select_construct_subjects(
        subjects, {item["controlled_subject_id"] for item in subjects}, limit=4
    )
    cell_by_id = {
        item["controlled_subject_id"]: item["primary_technique"] for item in subjects
    }
    assert [cell_by_id[item] for item in selected] == [
        "ARRAY_NUMERICAL",
        "SCALAR_CONTROL",
        "ARRAY_NUMERICAL",
        "SCALAR_CONTROL",
    ]


def test_slot_selects_first_applicable_canonical_site_or_none():
    sites = [
        {
            "path": "a.py",
            "symbol": "f",
            "start_line": 1,
            "start_col": 0,
            "end_line": 1,
            "end_col": 1,
            "site_id": "1" * 64,
        },
        {
            "path": "b.py",
            "symbol": "g",
            "start_line": 2,
            "start_col": 0,
            "end_line": 2,
            "end_col": 1,
            "site_id": "2" * 64,
        },
    ]
    assert select_first_applicable_site(sites, lambda site: site["symbol"] in {"f", "g"}) == "1" * 64
    assert select_first_applicable_site(sites, lambda _site: False) is None


def test_reveal_binds_nonce_oid_commitment_and_normalized_source(synthetic_release):
    record = synthetic_release.bridge["records"][0]
    reveal = {
        "neutral_snapshot_id": record["neutral_snapshot_id"],
        "fixed_git_tree_oid": synthetic_release.fixed_oid,
        "reveal_nonce": synthetic_release.nonce_hex,
        "normalized_source_tree_sha256": record["normalized_source_tree_sha256"],
    }
    verify_reveal(
        record,
        reveal,
        synthetic_release.bridge["p12_package_root_sha256"],
        observed_tree_oid=synthetic_release.fixed_oid,
        observed_normalized_sha256=record["normalized_source_tree_sha256"],
    )
    bad = {**reveal, "reveal_nonce": "0" * 64}
    with pytest.raises(EvidenceError, match="E_REVEAL_COMMITMENT"):
        verify_reveal(
            record,
            bad,
            synthetic_release.bridge["p12_package_root_sha256"],
            observed_tree_oid=synthetic_release.fixed_oid,
            observed_normalized_sha256=record["normalized_source_tree_sha256"],
        )


def _load_fixture(name: str) -> dict:
    return json.loads((FIXTURE_ROOT / name).read_text(encoding="utf-8"))


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
                "source_sha256": file_sha256(path),
            }
        )
    body = {
        "schema_version": "p3-adapter-registry-v1",
        "adapters": adapters,
    }
    return {**body, "artifact_sha256": canonical_sha256(body)}


def _source_record() -> dict:
    return {
        "normalized_source_tree_sha256": "21" * 32,
        "build_descriptor_sha256": "22" * 32,
    }


def _tagged_declarations(fixture: dict) -> list[dict]:
    rows = []
    for item in fixture["declarations"]:
        row = copy.deepcopy(item)
        row["ecosystem"] = fixture["ecosystem"]
        if fixture.get("adapter_id") is not None:
            row["adapter_id"] = fixture["adapter_id"]
        rows.append(row)
    return rows


def _combined_executable_declarations() -> list[dict]:
    return _tagged_declarations(_load_fixture("python.json")) + _tagged_declarations(
        _load_fixture("cmake.json")
    )


def test_adapter_registry_binds_exact_implementation_paths_and_source_hashes(tmp_path):
    registry = _adapter_registry(tmp_path)
    validated = validate_adapter_registry(registry, tmp_path)
    assert {item["adapter_id"] for item in validated["adapters"]} == CONFIRMATORY_ADAPTERS
    for item in validated["adapters"]:
        absolute = tmp_path / item["implementation_path"]
        assert file_sha256(absolute) == item["source_sha256"]


@pytest.mark.parametrize(
    "mutator",
    [
        lambda reg: {
            **reg,
            "adapters": [
                {**item, "source_sha256": "0" * 64} if item["adapter_id"] == "PYTHON_PEP517_V1" else item
                for item in reg["adapters"]
            ],
        },
        lambda reg: {
            **reg,
            "adapters": [
                {
                    **item,
                    "implementation_path": "adapters/missing_python.py",
                }
                if item["adapter_id"] == "PYTHON_PEP517_V1"
                else item
                for item in reg["adapters"]
            ],
        },
        lambda reg: {
            **reg,
            "adapters": reg["adapters"]
            + [
                {
                    "adapter_id": "CARGO_TEST_V1",
                    "ecosystem": "cargo",
                    "implementation_path": "adapters/cargo_test_v1.py",
                    "source_sha256": "1" * 64,
                }
            ],
        },
    ],
)
def test_adapter_registry_rejects_one_field_mutations(tmp_path, mutator):
    registry = mutator(_adapter_registry(tmp_path))
    body = {key: value for key, value in registry.items() if key != "artifact_sha256"}
    registry = {**body, "artifact_sha256": canonical_sha256(body)}
    with pytest.raises(EvidenceError):
        validate_adapter_registry(registry, tmp_path)


def test_public_behavior_frame_accounts_all_categories_and_retains_unsupported(tmp_path):
    registry = validate_adapter_registry(_adapter_registry(tmp_path), tmp_path)
    declarations = (
        _combined_executable_declarations()
        + _tagged_declarations(_load_fixture("unsupported.json"))
        + [
            {
                "category": "CLI",
                "ecosystem": "python",
                "adapter_id": "PYTHON_PEP517_V1",
                "provenance_path": "docs/broken.md",
                "provenance_span_or_key": "broken",
                "entrypoint": "",
                "normalized_entrypoint": "",
                "declared_inputs": {"kind": "cli_tokens"},
                "declared_input_schema_sha256": "bb" * 32,
                "static_dependency_tags": [],
                "prerequisites": [],
            }
        ]
    )
    assert sum(1 for item in _combined_executable_declarations()) > 20
    frame = build_public_behavior_frame(_source_record(), declarations, registry)
    accounting = frame["category_accounting"]
    assert [row["category"] for row in accounting] == BEHAVIOR_CATEGORY_ORDER
    assert all("discovered_count" in row for row in accounting)
    assert all(row["discovered_count"] >= 0 for row in accounting)
    empty_frame = build_public_behavior_frame(
        _source_record(),
        [
            {
                "category": "PUBLIC_API",
                "ecosystem": "python",
                "adapter_id": "PYTHON_PEP517_V1",
                "provenance_path": "src/only.py",
                "provenance_span_or_key": "only",
                "entrypoint": "only:f",
                "normalized_entrypoint": "only:f",
                "declared_inputs": {"kind": "none"},
                "declared_input_schema_sha256": "cc" * 32,
                "static_dependency_tags": [],
                "prerequisites": [],
            }
        ],
        registry,
    )
    assert [row["category"] for row in empty_frame["category_accounting"]] == BEHAVIOR_CATEGORY_ORDER
    assert sum(1 for row in empty_frame["category_accounting"] if row["discovered_count"] == 0) == 4

    unsupported = [
        row for row in frame["rows"] if row["discovery_status"] == "ADAPTER_UNSUPPORTED"
    ]
    assert len(unsupported) == 3
    assert all(row["provenance_path"] for row in unsupported)
    assert all(row.get("hand_command") is None or row["discovery_status"] != "EXECUTABLE" for row in frame["rows"])
    invalid = [row for row in frame["rows"] if row["discovery_status"] == "INVALID_DECLARATION"]
    assert len(invalid) == 1
    assert invalid[0]["provenance_path"] == "docs/broken.md"
    assert invalid[0]["unsupported_or_exclusion_reason"]
    executable = [row for row in frame["rows"] if row["discovery_status"] == "EXECUTABLE"]
    assert len(executable) > 20
    assert frame["controlled_subject_source_id"] == canonical_sha256(
        {
            "normalized_source_tree_sha256": "21" * 32,
            "build_descriptor_sha256": "22" * 32,
            "domain": "P3-SOURCE-v1",
        }
    )


def test_public_behavior_rejects_missing_provenance(tmp_path):
    registry = validate_adapter_registry(_adapter_registry(tmp_path), tmp_path)
    declaration = {
        "category": "PUBLIC_API",
        "ecosystem": "python",
        "adapter_id": "PYTHON_PEP517_V1",
        "provenance_path": "",
        "provenance_span_or_key": "solve",
        "entrypoint": "pkg:solve",
        "normalized_entrypoint": "pkg:solve",
        "declared_inputs": {"kind": "none"},
        "declared_input_schema_sha256": "dd" * 32,
        "static_dependency_tags": [],
        "prerequisites": [],
    }
    with pytest.raises(EvidenceError, match="E_PROVENANCE"):
        build_public_behavior_frame(_source_record(), [declaration], registry)


def test_public_behavior_frame_is_input_order_invariant(tmp_path):
    registry = validate_adapter_registry(_adapter_registry(tmp_path), tmp_path)
    declarations = _combined_executable_declarations() + _tagged_declarations(
        _load_fixture("unsupported.json")
    )
    first = build_public_behavior_frame(_source_record(), declarations, registry)
    second = build_public_behavior_frame(
        _source_record(), list(reversed(declarations)), registry
    )
    assert first == second


def test_unsupported_ecosystem_has_no_hand_command_fallback(tmp_path):
    registry = validate_adapter_registry(_adapter_registry(tmp_path), tmp_path)
    declarations = _tagged_declarations(_load_fixture("unsupported.json"))
    assert all(item.get("hand_command") for item in declarations)
    frame = build_public_behavior_frame(_source_record(), declarations, registry)
    assert all(row["discovery_status"] == "ADAPTER_UNSUPPORTED" for row in frame["rows"])
    assert all(row["discovery_status"] != "EXECUTABLE" for row in frame["rows"])
    workload = select_profiling_workload(frame, "S")
    assert workload["selected_behavior_ids"] == []
    assert workload["budget"] == 10


def test_profiling_workload_selection_is_balanced_and_outcome_blind(tmp_path):
    registry = validate_adapter_registry(_adapter_registry(tmp_path), tmp_path)
    declarations = _combined_executable_declarations()
    assert len(declarations) > 20
    frame = build_public_behavior_frame(_source_record(), declarations, registry)
    workload = select_profiling_workload(frame, "L")
    assert workload["budget"] == 20
    assert workload["category_order"] == [
        "PUBLIC_API",
        "CLI",
        "EXAMPLE",
        "BENCHMARK",
        "PROJECT_TEST",
    ]
    assert max(workload["selected_category_counts"].values()) - min(
        workload["selected_category_counts"].values()
    ) <= 1
    assert len(workload["selected_behavior_ids"]) == 20
    baseline_ids = list(workload["selected_behavior_ids"])

    poisoned = []
    for index, item in enumerate(declarations):
        row = copy.deepcopy(item)
        row["execution_success"] = index % 2 == 0
        row["coverage"] = 0.01 * index
        row["technique_label"] = "ARRAY_NUMERICAL" if index % 2 else "SCALAR_CONTROL"
        row["mr_outcome"] = "MR_VIOLATION"
        row["p12_fault_id"] = f"fault-{index}"
        poisoned.append(row)
    poisoned_frame = build_public_behavior_frame(_source_record(), poisoned, registry)
    poisoned_workload = select_profiling_workload(poisoned_frame, "L")
    assert poisoned_workload["selected_behavior_ids"] == baseline_ids

    shuffled_frame = build_public_behavior_frame(
        _source_record(), list(reversed(poisoned)), registry
    )
    shuffled_workload = select_profiling_workload(shuffled_frame, "L")
    assert shuffled_workload["selected_behavior_ids"] == baseline_ids


def test_profiling_workload_prefers_unseen_diversity_then_behavior_id(tmp_path):
    registry = validate_adapter_registry(_adapter_registry(tmp_path), tmp_path)
    schema = "ee" * 32
    declarations = []
    for category in BEHAVIOR_CATEGORY_ORDER:
        for index in range(3):
            declarations.append(
                {
                    "category": category,
                    "ecosystem": "python",
                    "adapter_id": "PYTHON_PEP517_V1",
                    "provenance_path": f"docs/{category.lower()}.md",
                    "provenance_span_or_key": f"item-{index}",
                    "entrypoint": f"{category.lower()}:entry_{index}",
                    "normalized_entrypoint": f"{category.lower()}:shared",
                    "declared_inputs": {"kind": "none"},
                    "declared_input_schema_sha256": schema,
                    "static_dependency_tags": ["shared"],
                    "prerequisites": [],
                }
            )
    frame = build_public_behavior_frame(_source_record(), declarations, registry)
    executable = [row for row in frame["rows"] if row["discovery_status"] == "EXECUTABLE"]
    by_category: dict[str, list[dict]] = {category: [] for category in BEHAVIOR_CATEGORY_ORDER}
    for row in executable:
        by_category[row["category"]].append(row)
    for rows in by_category.values():
        rows.sort(key=lambda item: (item["diversity_signature_sha256"], item["behavior_id"]))
    expected_first_pass = [by_category[category][0]["behavior_id"] for category in BEHAVIOR_CATEGORY_ORDER]
    workload = select_profiling_workload(frame, "S")
    assert workload["selected_behavior_ids"][:5] == expected_first_pass
    assert len(workload["selected_behavior_ids"]) == 10
