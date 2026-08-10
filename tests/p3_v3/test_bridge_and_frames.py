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
    E_COMMON_COUNT,
    E_COMMON_GENERATOR_IDS,
    E_CONTRACT_COUNT,
    E_CONTRACT_GENERATOR_IDS,
    build_common_inputs,
    build_contract_inputs,
    build_public_behavior_frame,
    build_subject_frames,
    classify_technique,
    close_slot,
    select_construct_subjects,
    select_first_applicable_site,
    select_profiling_workload,
    validate_adapter_registry,
    validate_bridge_document,
    validate_common_inputs_on_fixed_source,
    validate_contract_generator_registry,
    validate_input_generator_registry,
    verify_pinned_bridge,
    verify_reveal,
    verify_slot_chronology,
)

FIXTURE_ROOT = Path(__file__).resolve().parent / "fixtures" / "public_behavior"
GENERATOR_FIXTURE_ROOT = Path(__file__).resolve().parent / "fixtures" / "input_generators"
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


def _behavior_id(label: str) -> str:
    return canonical_sha256(
        {
            "domain": "P3-TEST-BEHAVIOR-v1",
            "label": label,
        }
    )


def _synthetic_workload(rows: list[tuple[str, str]]) -> dict:
    selected_rows = [
        {
            "behavior_id": behavior_id,
            "category": category,
            "diversity_signature_sha256": "ab" * 32,
            "normalized_entrypoint": f"entry:{behavior_id[:8]}",
            "declared_input_schema_sha256": "cd" * 32,
            "static_dependency_tags": [],
            "provenance_path": f"docs/{category.lower()}.md",
            "provenance_span_or_key": behavior_id[:8],
            "entrypoint": f"entry:{behavior_id[:8]}",
        }
        for behavior_id, category in rows
    ]
    counts = {
        category: sum(1 for _, item_category in rows if item_category == category)
        for category in BEHAVIOR_CATEGORY_ORDER
        if any(item_category == category for _, item_category in rows)
    }
    body = {
        "schema_version": "p3-profiling-workload-v1",
        "controlled_subject_source_id": "21" * 32,
        "scale_class": "S",
        "budget": 10,
        "category_order": list(BEHAVIOR_CATEGORY_ORDER),
        "selected_rows": selected_rows,
        "selected_behavior_ids": [behavior_id for behavior_id, _ in rows],
        "selected_category_counts": counts,
    }
    return {**body, "artifact_sha256": canonical_sha256(body)}


def _success(behavior_id: str, *tags: str) -> dict:
    return {
        "behavior_id": behavior_id,
        "status": "SUCCESS",
        "technique_tags": list(tags),
    }


def _unresolved(behavior_id: str, status: str) -> dict:
    return {
        "behavior_id": behavior_id,
        "status": status,
        "technique_tags": [],
    }


def _category_balanced_fixture():
    scalar_ids = [_behavior_id(f"scalar-{index}") for index in range(8)]
    array_id = _behavior_id("array-0")
    rows = [(behavior_id, "PUBLIC_API") for behavior_id in scalar_ids]
    rows.append((array_id, "CLI"))
    workload = _synthetic_workload(rows)
    results = [_success(behavior_id, "SCALAR_CONTROL") for behavior_id in scalar_ids]
    results.append(_success(array_id, "ARRAY_NUMERICAL"))
    return workload, results, array_id


def test_classify_technique_is_category_equal_not_row_weighted():
    workload, results, array_id = _category_balanced_fixture()
    profile = classify_technique(workload, results)
    assert profile["lower_scores"]["SCALAR_CONTROL"] == "0.5"
    assert profile["lower_scores"]["ARRAY_NUMERICAL"] == "0.5"
    assert profile["upper_scores"]["SCALAR_CONTROL"] == "0.5"
    assert profile["upper_scores"]["ARRAY_NUMERICAL"] == "0.5"
    assert set(profile["confirmed_tags"]) == {"ARRAY_NUMERICAL", "SCALAR_CONTROL"}
    assert set(profile["possible_tags"]) == {"ARRAY_NUMERICAL", "SCALAR_CONTROL"}

    failed_ids = [_behavior_id(f"cli-fail-{index}") for index in range(3)]
    extended_rows = [
        (row["behavior_id"], row["category"]) for row in workload["selected_rows"]
    ] + [(behavior_id, "CLI") for behavior_id in failed_ids]
    extended_workload = _synthetic_workload(extended_rows)
    extended_results = list(results) + [
        _unresolved(behavior_id, "FAILURE") for behavior_id in failed_ids
    ]
    widened = classify_technique(extended_workload, extended_results)
    assert widened["lower_scores"]["SCALAR_CONTROL"] == "0.5"
    assert widened["lower_scores"]["ARRAY_NUMERICAL"] == "0.125"
    assert widened["upper_scores"]["SCALAR_CONTROL"] == "0.875"
    assert widened["upper_scores"]["ARRAY_NUMERICAL"] == "0.5"
    for technique, upper in widened["upper_scores"].items():
        baseline = profile["upper_scores"].get(technique, "0")
        assert float(upper) >= float(baseline)
    funnel = {row["category"]: row for row in widened["category_funnel"]}
    assert funnel["CLI"]["n_c"] == 4
    assert funnel["CLI"]["unresolved_count"] == 3
    assert funnel["PUBLIC_API"]["n_c"] == 8
    assert array_id in extended_workload["selected_behavior_ids"]


def test_classify_technique_requires_success_in_every_selected_category():
    scalar_id = _behavior_id("only-scalar")
    failed_id = _behavior_id("failed-cli")
    workload = _synthetic_workload(
        [(scalar_id, "PUBLIC_API"), (failed_id, "CLI")]
    )
    results = [
        _success(scalar_id, "SCALAR_CONTROL"),
        _unresolved(failed_id, "TIMEOUT"),
    ]
    profile = classify_technique(workload, results)
    assert profile["primary_technique"] == "TECH_UNCERTAIN"


def test_classify_technique_overlapping_intervals_are_uncertain():
    workload, results, _array_id = _category_balanced_fixture()
    failed_ids = [_behavior_id(f"overlap-fail-{index}") for index in range(3)]
    rows = [(row["behavior_id"], row["category"]) for row in workload["selected_rows"]]
    rows.extend((behavior_id, "CLI") for behavior_id in failed_ids)
    workload = _synthetic_workload(rows)
    results = list(results) + [
        _unresolved(behavior_id, "ADAPTER_UNCERTAIN") for behavior_id in failed_ids
    ]
    profile = classify_technique(workload, results)
    assert profile["primary_technique"] == "TECH_UNCERTAIN"


def test_classify_technique_strict_lower_bound_winner():
    left = _behavior_id("winner-left")
    right = _behavior_id("winner-right")
    uncertain = _behavior_id("winner-uncertain")
    workload = _synthetic_workload(
        [
            (left, "PUBLIC_API"),
            (right, "CLI"),
            (uncertain, "CLI"),
        ]
    )
    results = [
        _success(left, "SCALAR_CONTROL"),
        _success(right, "SCALAR_CONTROL"),
        _unresolved(uncertain, "MISSING_TRACE"),
    ]
    profile = classify_technique(workload, results)
    assert profile["lower_scores"]["SCALAR_CONTROL"] == "0.75"
    assert profile["upper_scores"]["SCALAR_CONTROL"] == "1"
    assert profile["primary_technique"] == "SCALAR_CONTROL"
    assert profile["confirmed_tags"] == ["SCALAR_CONTROL"]
    assert profile["category_funnel"][1]["n_c"] == 2
    assert profile["category_funnel"][1]["unresolved_count"] == 1


def test_classify_technique_tie_breaks_with_frozen_technique_order():
    left = _behavior_id("tie-left")
    right = _behavior_id("tie-right")
    workload = _synthetic_workload([(left, "PUBLIC_API"), (right, "CLI")])
    results = [
        _success(left, "SCALAR_CONTROL"),
        _success(right, "ARRAY_NUMERICAL"),
    ]
    profile = classify_technique(workload, results)
    assert profile["lower_scores"]["SCALAR_CONTROL"] == "0.5"
    assert profile["lower_scores"]["ARRAY_NUMERICAL"] == "0.5"
    assert profile["primary_technique"] == "ARRAY_NUMERICAL"


def test_classify_technique_is_result_order_invariant():
    workload, results, _array_id = _category_balanced_fixture()
    first = classify_technique(workload, results)
    second = classify_technique(workload, list(reversed(results)))
    assert first == second
    assert canonical_sha256(first) == canonical_sha256(second)


def test_build_subject_frames_prefers_technique_profile_over_feature_label(
    synthetic_release,
):
    verified = verify_pinned_bridge(synthetic_release.root, synthetic_release.lock)
    features = _features(verified["records"][0]["neutral_snapshot_id"])
    assert features[0]["primary_technique"] == "ARRAY_NUMERICAL"
    left = _behavior_id("frame-left")
    right = _behavior_id("frame-right")
    workload = _synthetic_workload([(left, "PUBLIC_API"), (right, "CLI")])
    results = [
        _success(left, "SCALAR_CONTROL"),
        _success(right, "SCALAR_CONTROL"),
    ]
    profile = classify_technique(workload, results)
    assert profile["primary_technique"] == "SCALAR_CONTROL"
    frames = build_subject_frames(
        verified, features, technique_profile=profile
    )
    subject = frames["subjects"][0]
    assert subject["primary_technique"] == "SCALAR_CONTROL"
    assert subject["technique_vector"] == ["SCALAR_CONTROL"]


def _load_generator_registry() -> dict:
    return json.loads((GENERATOR_FIXTURE_ROOT / "registry.json").read_text(encoding="utf-8"))


def _public_schema(schema_kind: str, raw_schema: dict, **aliases) -> dict:
    record = {
        "schema_kind": schema_kind,
        "raw_schema": raw_schema,
    }
    record.update(aliases)
    return record


def _public_frame_with_schemas(schemas: list[dict]) -> dict:
    source_id = canonical_sha256(
        {
            "normalized_source_tree_sha256": "21" * 32,
            "build_descriptor_sha256": "22" * 32,
            "domain": "P3-SOURCE-v1",
        }
    )
    body = {
        "schema_version": "p3-public-behavior-frame-v1",
        "controlled_subject_source_id": source_id,
        "category_accounting": [
            {
                "category": category,
                "discovered_count": 0,
                "executable_count": 0,
                "adapter_unsupported_count": 0,
                "invalid_count": 0,
            }
            for category in BEHAVIOR_CATEGORY_ORDER
        ],
        "rows": [],
        "public_schemas": schemas,
    }
    return {**body, "artifact_sha256": canonical_sha256(body)}


def test_input_generator_registry_binds_exact_five_e_common_ids_and_source_hashes():
    registry = validate_input_generator_registry(
        _load_generator_registry(), GENERATOR_FIXTURE_ROOT
    )
    assert {item["generator_id"] for item in registry["generators"]} == set(
        E_COMMON_GENERATOR_IDS
    )
    assert len(registry["generators"]) == 5
    for item in registry["generators"]:
        absolute = GENERATOR_FIXTURE_ROOT / item["implementation_path"]
        assert file_sha256(absolute) == item["source_sha256"]
        assert item["schema_kind"] == item["generator_id"]
        assert item["failure_code"]
        assert item["output_schema"]["generator_id"] == item["generator_id"]


def test_input_generator_registry_rejects_source_hash_mismatch(tmp_path):
    registry = _load_generator_registry()
    for item in registry["generators"]:
        src = GENERATOR_FIXTURE_ROOT / item["implementation_path"]
        dst = tmp_path / item["implementation_path"]
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(src.read_bytes())
    mutated = {
        **registry,
        "generators": [
            {
                **item,
                "source_sha256": "0" * 64
                if item["generator_id"] == "NUMERIC_ARRAY_DOMAIN_V1"
                else item["source_sha256"],
            }
            for item in registry["generators"]
        ],
    }
    body = {key: value for key, value in mutated.items() if key != "artifact_sha256"}
    mutated = {**body, "artifact_sha256": canonical_sha256(body)}
    with pytest.raises(EvidenceError, match="E_GENERATOR_SOURCE_HASH"):
        validate_input_generator_registry(mutated, tmp_path)


def test_build_common_inputs_ordinals_seeds_dedupe_and_round_robin():
    registry = validate_input_generator_registry(
        _load_generator_registry(), GENERATOR_FIXTURE_ROOT
    )
    schemas = [
        _public_schema(
            "NUMERIC_ARRAY_DOMAIN_V1",
            {"domain": "numeric", "shape": [2], "label": "a"},
            subject_alias="subject-a",
            project_alias="proj-a",
        ),
        _public_schema(
            "CLI_TOKEN_GRAMMAR_V1",
            {"domain": "cli", "tokens": ["--x"], "label": "b"},
            subject_alias="subject-b",
        ),
        _public_schema(
            "NUMERIC_ARRAY_DOMAIN_V1",
            {"domain": "numeric", "shape": [2], "label": "a"},
            subject_alias="subject-duplicate",
            project_alias="proj-duplicate",
        ),
        _public_schema(
            "TEXT_IO_SCHEMA_V1",
            {"domain": "text", "encoding": "utf-8", "label": "c"},
        ),
    ]
    frame = _public_frame_with_schemas(schemas)
    inventory = build_common_inputs(_source_record(), frame, registry)
    assert inventory["schema_version"] == "p3-evaluation-inputs-common-v1"
    assert len(inventory["rows"]) == E_COMMON_COUNT == 30
    assert [row["ordinal"] for row in inventory["rows"]] == list(range(30))

    source_id = frame["controlled_subject_source_id"]
    for ordinal, row in enumerate(inventory["rows"]):
        expected_seed = int.from_bytes(
            bytes.fromhex(
                canonical_sha256(
                    {
                        "domain": "P3-E-COMMON-SEED-v1",
                        "controlled_subject_source_id": source_id,
                        "ordinal": ordinal,
                    }
                )
            )[:8],
            "big",
        )
        assert row["seed"] == expected_seed

    # Deduplicate by raw schema SHA-256 -> three eligible schemas.
    unique_raw = []
    seen_raw = set()
    for schema in schemas:
        raw_sha = canonical_sha256(schema["raw_schema"])
        if raw_sha in seen_raw:
            continue
        seen_raw.add(raw_sha)
        selection_body = {
            key: value
            for key, value in schema.items()
            if key not in {"subject_alias", "project_alias", "controlled_subject_source_id"}
        }
        unique_raw.append(
            (
                canonical_sha256(selection_body),
                raw_sha,
                schema["schema_kind"],
            )
        )
    unique_raw.sort(key=lambda item: (item[0], item[1]))
    assert len(unique_raw) == 3
    for ordinal, row in enumerate(inventory["rows"]):
        expected_kind = unique_raw[ordinal % 3][2]
        assert row["schema_kind"] == expected_kind
        assert row["generator_id"] == expected_kind
        assert row["status"] == "COMMON_INPUT_GENERATED"
        assert row["raw_payload_sha256"]
        assert row["envelope"]["generator_id"] == expected_kind

    shuffled = _public_frame_with_schemas(list(reversed(schemas)))
    shuffled_inventory = build_common_inputs(_source_record(), shuffled, registry)
    assert [row["raw_payload_sha256"] for row in shuffled_inventory["rows"]] == [
        row["raw_payload_sha256"] for row in inventory["rows"]
    ]
    assert [row["envelope"] for row in shuffled_inventory["rows"]] == [
        row["envelope"] for row in inventory["rows"]
    ]


def test_build_common_inputs_rejects_forbidden_generator_inputs():
    registry = validate_input_generator_registry(
        _load_generator_registry(), GENERATOR_FIXTURE_ROOT
    )
    base_schemas = [
        _public_schema("NUMERIC_ARRAY_DOMAIN_V1", {"domain": "numeric", "shape": [1]})
    ]
    forbidden_cases = [
        {"project_test_body": "assert True"},
        {"project_test_fixture": {"x": 1}},
        {"contracts": [{"id": "c1"}]},
        {"contract": {"id": "c1"}},
        {"sites": [{"path": "a.py"}]},
        {"site": {"path": "a.py"}},
        {"profiling_results": [{"status": "SUCCESS"}]},
        {"profiling_result": {"status": "SUCCESS"}},
        {"patch": {"diff": "+x"}},
        {"mr": {"id": "mr-1"}},
        {"p12": {"fault_id": "f1"}},
        {"outcome": "MR_VIOLATION"},
        {"mr_outcome": "MR_VIOLATION"},
    ]
    for forbidden in forbidden_cases:
        poisoned_schema = {
            **base_schemas[0],
            **forbidden,
        }
        frame = _public_frame_with_schemas([poisoned_schema])
        with pytest.raises(EvidenceError, match="E_GENERATOR_INPUT"):
            build_common_inputs(_source_record(), frame, registry)
        poisoned_frame = {
            **_public_frame_with_schemas(base_schemas),
            **forbidden,
        }
        body = {
            key: value
            for key, value in poisoned_frame.items()
            if key != "artifact_sha256"
        }
        poisoned_frame = {**body, "artifact_sha256": canonical_sha256(body)}
        with pytest.raises(EvidenceError, match="E_GENERATOR_INPUT"):
            build_common_inputs(_source_record(), poisoned_frame, registry)


def test_generator_failure_occupies_ordinal_as_common_input_invalid():
    registry = validate_input_generator_registry(
        _load_generator_registry(), GENERATOR_FIXTURE_ROOT
    )
    schemas = [
        _public_schema(
            "JSON_SCHEMA_DRAFT2020_12_V1",
            {"force_invalid": True},
        ),
        _public_schema(
            "NUMERIC_ARRAY_DOMAIN_V1",
            {"domain": "numeric", "shape": [3]},
        ),
    ]
    inventory = build_common_inputs(
        _source_record(), _public_frame_with_schemas(schemas), registry
    )
    assert len(inventory["rows"]) == 30
    invalid_rows = [
        row for row in inventory["rows"] if row["status"] == "COMMON_INPUT_INVALID"
    ]
    generated_rows = [
        row for row in inventory["rows"] if row["status"] == "COMMON_INPUT_GENERATED"
    ]
    assert invalid_rows
    assert generated_rows
    for row in invalid_rows:
        assert row["ordinal"] in range(30)
        assert row["failure_code"] == "JSON_SCHEMA_DRAFT2020_12_V1_INVALID"
        assert row["envelope"] is None
        assert row["raw_payload_sha256"] is None
        assert row["schema_kind"] == "JSON_SCHEMA_DRAFT2020_12_V1"
    for row in generated_rows:
        assert row["schema_kind"] == "NUMERIC_ARRAY_DOMAIN_V1"
        assert row["envelope"] is not None
    # Ordinals assigned to the failing schema via i mod k remain invalid and are not replaced.
    ordered = []
    for schema in schemas:
        selection_body = {
            key: value
            for key, value in schema.items()
            if key not in {"subject_alias", "project_alias", "controlled_subject_source_id"}
        }
        ordered.append(
            (
                canonical_sha256(selection_body),
                canonical_sha256(schema["raw_schema"]),
                schema["schema_kind"],
            )
        )
    ordered.sort(key=lambda item: (item[0], item[1]))
    failing_index = next(
        index
        for index, item in enumerate(ordered)
        if item[2] == "JSON_SCHEMA_DRAFT2020_12_V1"
    )
    assert [row["ordinal"] for row in invalid_rows] == [
        ordinal for ordinal in range(30) if ordinal % 2 == failing_index
    ]
    assert len(invalid_rows) + len(generated_rows) == 30


def test_zero_eligible_schemas_yield_thirty_unavailable_rows():
    registry = validate_input_generator_registry(
        _load_generator_registry(), GENERATOR_FIXTURE_ROOT
    )
    inventory = build_common_inputs(
        _source_record(), _public_frame_with_schemas([]), registry
    )
    assert len(inventory["rows"]) == 30
    assert {row["status"] for row in inventory["rows"]} == {"COMMON_INPUT_UNAVAILABLE"}
    assert [row["ordinal"] for row in inventory["rows"]] == list(range(30))
    assert all(row["envelope"] is None for row in inventory["rows"])
    assert all(row["raw_payload_sha256"] is None for row in inventory["rows"])


def test_validate_common_inputs_on_fixed_source_preserves_identities():
    registry = validate_input_generator_registry(
        _load_generator_registry(), GENERATOR_FIXTURE_ROOT
    )
    schemas = [
        _public_schema("CLI_TOKEN_GRAMMAR_V1", {"domain": "cli", "tokens": ["a"]}),
        _public_schema(
            "BINARY_RECORD_SCHEMA_V1",
            {"force_invalid": True},
        ),
    ]
    inventory = build_common_inputs(
        _source_record(), _public_frame_with_schemas(schemas), registry
    )
    frozen_payloads = [
        (row["ordinal"], row["input_id"], row["raw_payload_sha256"], row["envelope"])
        for row in inventory["rows"]
    ]
    sites = [{"site_id": "1" * 64}]
    contracts = [{"contract_id": "2" * 64}]
    profile = {"primary_technique": "SCALAR_CONTROL"}
    frame_hash = "3" * 64

    def validator(row):
        if row["status"] == "COMMON_INPUT_UNAVAILABLE":
            return "COMMON_INPUT_UNAVAILABLE"
        if row["status"] == "COMMON_INPUT_INVALID":
            return "COMMON_INPUT_INVALID"
        if row["ordinal"] % 3 == 0:
            return "COMMON_INPUT_INVALID"
        return "COMMON_INPUT_EXECUTABLE"

    report = validate_common_inputs_on_fixed_source(
        inventory,
        validator,
        sites=sites,
        contracts=contracts,
        profile=profile,
        frame_artifact_sha256=frame_hash,
    )
    assert len(report["rows"]) == 30
    assert {row["status"] for row in report["rows"]} <= {
        "COMMON_INPUT_EXECUTABLE",
        "COMMON_INPUT_INVALID",
        "COMMON_INPUT_UNAVAILABLE",
    }
    assert all(
        row["status"]
        in {
            "COMMON_INPUT_EXECUTABLE",
            "COMMON_INPUT_INVALID",
            "COMMON_INPUT_UNAVAILABLE",
        }
        for row in report["rows"]
    )
    assert [row["ordinal"] for row in report["rows"]] == list(range(30))
    for before, after in zip(frozen_payloads, report["rows"], strict=True):
        assert after["ordinal"] == before[0]
        assert after["input_id"] == before[1]
        assert after["raw_payload_sha256"] == before[2]
        assert after["envelope"] == before[3]
    assert report["sites"] == sites
    assert report["contracts"] == contracts
    assert report["profile"] == profile
    assert report["frame_artifact_sha256"] == frame_hash
    # Validator cannot replace rows: still exactly 30 predetermined identities.
    assert len({row["input_id"] for row in report["rows"]}) == 30


APPLICABLE_CHRONOLOGY = [
    "SITE_FROZEN",
    "CONTRACT_FROZEN",
    "E_CONTRACT_FROZEN",
    "PATCH_FROZEN",
    "CERTIFICATION_WITNESS_SELECTED",
    "TERMINAL_STATE",
]

_CONTRACT_GENERATOR_TEMPLATE = '''\
"""Deterministic synthetic {generator_id} contract input generator."""

from __future__ import annotations

import hashlib
import json
from typing import Any


FAILURE_CODE = "{failure_code}"
GENERATOR_ID = "{generator_id}"


def _seed_block(seed: int, counter: int) -> bytes:
    return hashlib.sha256(
        b"P3-INPUT-STREAM-v1" + seed.to_bytes(8, "big") + counter.to_bytes(8, "big")
    ).digest()


def generate(schema_bytes: bytes, seed: int) -> dict[str, Any]:
    if not schema_bytes:
        return {{"failure_code": FAILURE_CODE}}
    try:
        schema = json.loads(schema_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return {{"failure_code": FAILURE_CODE}}
    if isinstance(schema, dict) and schema.get("force_invalid") is True:
        return {{"failure_code": FAILURE_CODE}}
    if isinstance(schema, dict) and schema.get("unsupported_domain") is True:
        return {{"failure_code": "CONTRACT_INPUT_UNAVAILABLE"}}
    block = _seed_block(seed, 0)
    payload = {{
        "generator_id": GENERATOR_ID,
        "stream": block.hex(),
        "schema_fingerprint": hashlib.sha256(schema_bytes).hexdigest(),
    }}
    raw = (
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        + b"\\n"
    )
    envelope = {{
        "schema_version": "p3-contract-input-envelope-v1",
        "generator_id": GENERATOR_ID,
        "payload": payload,
    }}
    return {{
        "envelope": envelope,
        "raw_payload_sha256": hashlib.sha256(raw).hexdigest(),
    }}
'''


def _canonical_sites() -> list[dict]:
    return [
        {
            "path": "a.py",
            "symbol": "f",
            "start_line": 1,
            "start_col": 0,
            "end_line": 1,
            "end_col": 1,
            "site_id": "a1" * 32,
        },
        {
            "path": "b.py",
            "symbol": "g",
            "start_line": 2,
            "start_col": 0,
            "end_line": 2,
            "end_col": 1,
            "site_id": "b2" * 32,
        },
    ]


def _slot() -> dict:
    return {
        "slot_id": "c3" * 32,
        "controlled_subject_id": "d4" * 32,
    }


def _contract_generator_registry(tmp_path: Path) -> dict:
    generators = []
    for generator_id in E_CONTRACT_GENERATOR_IDS:
        rel = f"generators/{generator_id.lower()}.py"
        path = tmp_path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        failure_code = f"{generator_id}_INVALID"
        source = _CONTRACT_GENERATOR_TEMPLATE.format(
            generator_id=generator_id,
            failure_code=failure_code,
        )
        path.write_text(source, encoding="utf-8")
        generators.append(
            {
                "generator_id": generator_id,
                "schema_kind": generator_id,
                "implementation_path": rel,
                "source_sha256": file_sha256(path),
                "output_schema": {
                    "generator_id": generator_id,
                    "schema_version": "p3-contract-input-envelope-v1",
                },
                "failure_code": failure_code,
            }
        )
    body = {
        "schema_version": "p3-contract-generator-registry-v1",
        "generators": generators,
    }
    return {**body, "artifact_sha256": canonical_sha256(body)}


def _frozen_contract(generator_id: str, domain: dict) -> dict:
    return {
        "contract_id": "e5" * 32,
        "generator_id": generator_id,
        "domain": domain,
        "site_id": "a1" * 32,
    }


def test_contract_generator_registry_binds_exact_five_e_contract_ids(tmp_path):
    registry = validate_contract_generator_registry(
        _contract_generator_registry(tmp_path), tmp_path
    )
    assert {item["generator_id"] for item in registry["generators"]} == set(
        E_CONTRACT_GENERATOR_IDS
    )
    assert len(registry["generators"]) == E_CONTRACT_COUNT == 5
    for item in registry["generators"]:
        absolute = tmp_path / item["implementation_path"]
        assert file_sha256(absolute) == item["source_sha256"]
        assert item["schema_kind"] == item["generator_id"]


def test_close_slot_two_paths_not_applicable_or_site_frozen():
    slot = _slot()
    sites = _canonical_sites()
    closed = close_slot(slot, sites, lambda _site: False)
    assert closed["state"] == "APPLICABILITY_CLOSED_NOT_APPLICABLE"
    assert closed["path"] == "APPLICABILITY_CLOSED_NOT_APPLICABLE"
    assert closed["site_id"] is None
    assert closed["slot_id"] == slot["slot_id"]
    assert closed["controlled_subject_id"] == slot["controlled_subject_id"]

    applicable = close_slot(slot, sites, lambda site: site["symbol"] == "g")
    assert applicable["state"] == "SITE_FROZEN"
    assert applicable["path"] == "APPLICABLE"
    assert applicable["site_id"] == "b2" * 32


def test_build_contract_inputs_five_ordinals_seeds_and_named_generator(tmp_path):
    registry = validate_contract_generator_registry(
        _contract_generator_registry(tmp_path), tmp_path
    )
    slot = close_slot(_slot(), _canonical_sites(), lambda site: site["symbol"] == "f")
    contract = _frozen_contract(
        "CONTRACT_NUMERIC_DOMAIN_V1",
        {"domain": "numeric", "bounds": [0, 1]},
    )
    inventory = build_contract_inputs(slot, contract, registry)
    assert inventory["schema_version"] == "p3-evaluation-inputs-contract-v1"
    assert len(inventory["rows"]) == E_CONTRACT_COUNT == 5
    assert [row["ordinal"] for row in inventory["rows"]] == list(range(5))
    subject_id = slot["controlled_subject_id"]
    slot_id = slot["slot_id"]
    for ordinal, row in enumerate(inventory["rows"]):
        expected_seed = int.from_bytes(
            bytes.fromhex(
                canonical_sha256(
                    {
                        "domain": "P3-E-CONTRACT-SEED-v1",
                        "controlled_subject_id": subject_id,
                        "slot_id": slot_id,
                        "ordinal": ordinal,
                    }
                )
            )[:8],
            "big",
        )
        assert row["seed"] == expected_seed
        assert row["generator_id"] == "CONTRACT_NUMERIC_DOMAIN_V1"
        assert row["status"] == "CONTRACT_INPUT_GENERATED"
        assert row["raw_payload_sha256"]
        assert row["envelope"]["generator_id"] == "CONTRACT_NUMERIC_DOMAIN_V1"
        assert row["input_id"]


def test_unsupported_domain_yields_five_contract_input_unavailable(tmp_path):
    registry = validate_contract_generator_registry(
        _contract_generator_registry(tmp_path), tmp_path
    )
    slot = close_slot(_slot(), _canonical_sites(), lambda site: True)
    contract = _frozen_contract(
        "CONTRACT_ENUM_DOMAIN_V1",
        {"unsupported_domain": True},
    )
    inventory = build_contract_inputs(slot, contract, registry)
    assert len(inventory["rows"]) == 5
    assert {row["status"] for row in inventory["rows"]} == {"CONTRACT_INPUT_UNAVAILABLE"}
    assert all(row["envelope"] is None for row in inventory["rows"])
    assert all(row["raw_payload_sha256"] is None for row in inventory["rows"])
    # Cannot invent a replacement generator or site.
    assert {row["generator_id"] for row in inventory["rows"]} == {None}
    assert inventory["site_id"] == slot["site_id"]


def test_build_contract_inputs_rejects_not_applicable_slot(tmp_path):
    registry = validate_contract_generator_registry(
        _contract_generator_registry(tmp_path), tmp_path
    )
    slot = close_slot(_slot(), _canonical_sites(), lambda _site: False)
    contract = _frozen_contract(
        "CONTRACT_ARRAY_DOMAIN_V1",
        {"domain": "array", "shape": [2]},
    )
    with pytest.raises(EvidenceError, match="E_SLOT_PATH"):
        build_contract_inputs(slot, contract, registry)


def test_verify_slot_chronology_accepts_exactly_one_of_two_paths(tmp_path):
    registry = validate_contract_generator_registry(
        _contract_generator_registry(tmp_path), tmp_path
    )
    not_applicable = {
        "slot_id": "c3" * 32,
        "chronology": ["APPLICABILITY_CLOSED_NOT_APPLICABLE"],
        "contract": None,
        "e_contract": None,
        "patch": None,
        "certification_witness": None,
        "e_common_input_ids": [],
        "e_contract_input_ids": [],
    }
    verify_slot_chronology(not_applicable)

    slot = close_slot(_slot(), _canonical_sites(), lambda site: site["symbol"] == "f")
    contract = _frozen_contract(
        "CONTRACT_SEQUENCE_DOMAIN_V1",
        {"domain": "sequence", "length": 3},
    )
    inventory = build_contract_inputs(slot, contract, registry)
    applicable = {
        "slot_id": slot["slot_id"],
        "chronology": list(APPLICABLE_CHRONOLOGY),
        "contract": contract,
        "e_contract": inventory,
        "patch": {"patch_id": "f6" * 32},
        "certification_witness": {"witness_id": "a7" * 32},
        "e_common_input_ids": ["b8" * 32],
        "e_contract_input_ids": [row["input_id"] for row in inventory["rows"]],
    }
    verify_slot_chronology(applicable)


def test_inapplicable_slot_carrying_downstream_artifacts_fails():
    for field, value in (
        ("contract", {"contract_id": "e5" * 32}),
        ("e_contract", {"rows": []}),
        ("patch", {"patch_id": "f6" * 32}),
        ("certification_witness", {"witness_id": "a7" * 32}),
    ):
        artifacts = {
            "slot_id": "c3" * 32,
            "chronology": ["APPLICABILITY_CLOSED_NOT_APPLICABLE"],
            "contract": None,
            "e_contract": None,
            "patch": None,
            "certification_witness": None,
            "e_common_input_ids": [],
            "e_contract_input_ids": [],
        }
        artifacts[field] = value
        with pytest.raises(EvidenceError, match="E_SLOT_CHRONOLOGY"):
            verify_slot_chronology(artifacts)


def test_applicable_slot_missing_e_contract_before_patch_fails(tmp_path):
    registry = validate_contract_generator_registry(
        _contract_generator_registry(tmp_path), tmp_path
    )
    slot = close_slot(_slot(), _canonical_sites(), lambda site: True)
    contract = _frozen_contract(
        "CONTRACT_RELATION_PAIR_DOMAIN_V1",
        {"domain": "relation", "pairs": [[0, 1]]},
    )
    inventory = build_contract_inputs(slot, contract, registry)
    missing_e_contract = {
        "slot_id": slot["slot_id"],
        "chronology": [
            "SITE_FROZEN",
            "CONTRACT_FROZEN",
            "PATCH_FROZEN",
            "CERTIFICATION_WITNESS_SELECTED",
            "TERMINAL_STATE",
        ],
        "contract": contract,
        "e_contract": None,
        "patch": {"patch_id": "f6" * 32},
        "certification_witness": {"witness_id": "a7" * 32},
        "e_common_input_ids": [],
        "e_contract_input_ids": [row["input_id"] for row in inventory["rows"]],
    }
    with pytest.raises(EvidenceError, match="E_SLOT_CHRONOLOGY"):
        verify_slot_chronology(missing_e_contract)

    patch_without_inventory = {
        "slot_id": slot["slot_id"],
        "chronology": list(APPLICABLE_CHRONOLOGY),
        "contract": contract,
        "e_contract": None,
        "patch": {"patch_id": "f6" * 32},
        "certification_witness": {"witness_id": "a7" * 32},
        "e_common_input_ids": [],
        "e_contract_input_ids": [],
    }
    with pytest.raises(EvidenceError, match="E_SLOT_CHRONOLOGY"):
        verify_slot_chronology(patch_without_inventory)


def test_post_patch_witness_in_either_input_inventory_fails(tmp_path):
    registry = validate_contract_generator_registry(
        _contract_generator_registry(tmp_path), tmp_path
    )
    slot = close_slot(_slot(), _canonical_sites(), lambda site: True)
    contract = _frozen_contract(
        "CONTRACT_ENUM_DOMAIN_V1",
        {"domain": "enum", "values": ["a", "b"]},
    )
    inventory = build_contract_inputs(slot, contract, registry)
    witness_from_contract = inventory["rows"][0]["input_id"]
    artifacts = {
        "slot_id": slot["slot_id"],
        "chronology": list(APPLICABLE_CHRONOLOGY),
        "contract": contract,
        "e_contract": inventory,
        "patch": {"patch_id": "f6" * 32},
        "certification_witness": {"witness_id": witness_from_contract},
        "e_common_input_ids": ["b8" * 32],
        "e_contract_input_ids": [row["input_id"] for row in inventory["rows"]],
    }
    with pytest.raises(EvidenceError, match="E_WITNESS_INVENTORY"):
        verify_slot_chronology(artifacts)

    artifacts_common = {
        **artifacts,
        "certification_witness": {"witness_id": "b8" * 32},
    }
    with pytest.raises(EvidenceError, match="E_WITNESS_INVENTORY"):
        verify_slot_chronology(artifacts_common)
