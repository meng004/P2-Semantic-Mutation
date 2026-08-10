from __future__ import annotations

import copy

import pytest

from p3_v3.artifacts import EvidenceError
from p3_v3.packages import (
    PACKAGE_A_CLASSES,
    PACKAGE_B_CLASSES,
    PACKAGE_B_PRIMARY_CLASSES,
    PACKAGE_B_SENSITIVITY_CLASSES,
    PROPOSER_ALLOWED_CLASSES,
    build_package,
    materialize_package,
    verify_package,
)


def test_package_builds_and_verifies_regular_file(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    (source / "program.py").write_text("print(1)\n", encoding="utf-8")
    manifest = build_package(
        "CONSTRUCTION_A",
        source,
        [{"path": "program.py", "class": "SOURCE"}],
        ["a" * 64],
    )
    verify_package(source, manifest)
    assert manifest["files"][0]["path"] == "program.py"
    assert manifest["files"][0]["size"] == 9


def test_package_rejects_symlink(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    (source / "real").write_text("x", encoding="utf-8")
    (source / "link").symlink_to("real")
    with pytest.raises(EvidenceError, match="E_PACKAGE_FILE_TYPE"):
        build_package(
            "CONSTRUCTION_A", source, [{"path": "link", "class": "SOURCE"}], []
        )


def test_package_rejects_duplicate_normalized_path(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    (source / "x").write_text("x", encoding="utf-8")
    with pytest.raises(EvidenceError, match="E_PACKAGE_DUPLICATE"):
        build_package(
            "CONSTRUCTION_A",
            source,
            [{"path": "x", "class": "SOURCE"}, {"path": "x", "class": "BUILD"}],
            [],
        )


def test_package_role_rejects_holdout_content_in_package_a(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    (source / "reveal.json").write_text("{}\n", encoding="utf-8")
    with pytest.raises(EvidenceError, match="E_PACKAGE_CONTENT_CLASS"):
        build_package(
            "CONSTRUCTION_A",
            source,
            [{"path": "reveal.json", "class": "P12_REVEAL"}],
            [],
        )


def test_verifier_rejects_byte_drift(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    path = source / "program.py"
    path.write_text("print(1)\n", encoding="utf-8")
    manifest = build_package(
        "CONSTRUCTION_A", source, [{"path": "program.py", "class": "SOURCE"}], []
    )
    path.write_text("print(2)\n", encoding="utf-8")
    with pytest.raises(EvidenceError, match="E_PACKAGE_SHA256"):
        verify_package(source, manifest)


def test_manifest_tampering_fails_before_file_verification(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    (source / "program.py").write_text("print(1)\n", encoding="utf-8")
    manifest = build_package(
        "CONSTRUCTION_A", source, [{"path": "program.py", "class": "SOURCE"}], []
    )
    changed = copy.deepcopy(manifest)
    changed["files"][0]["size"] = 0
    with pytest.raises(EvidenceError, match="E_PACKAGE_MANIFEST_HASH"):
        verify_package(source, changed)


def test_materialization_is_exact_and_requires_new_target(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    (source / "nested").mkdir()
    (source / "nested/program.py").write_text("print(1)\n", encoding="utf-8")
    manifest = build_package(
        "CONSTRUCTION_A",
        source,
        [{"path": "nested/program.py", "class": "SOURCE"}],
        [],
    )
    target = tmp_path / "materialized"
    materialize_package(source, target, manifest)
    assert (target / "nested/program.py").read_bytes() == b"print(1)\n"
    verify_package(target, manifest)
    with pytest.raises(EvidenceError, match="E_PACKAGE_TARGET_EXISTS"):
        materialize_package(source, target, manifest)


def test_package_a_verifies_with_both_input_inventories(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    (source / "e_common.json").write_text('{"inventory":"common"}\n', encoding="utf-8")
    (source / "e_contract.json").write_text('{"inventory":"contract"}\n', encoding="utf-8")
    for content_class in ("E_COMMON", "E_CONTRACT"):
        assert content_class in PACKAGE_A_CLASSES
    manifest = build_package(
        "CONSTRUCTION_A",
        source,
        [
            {"path": "e_common.json", "class": "E_COMMON"},
            {"path": "e_contract.json", "class": "E_CONTRACT"},
        ],
        [],
    )
    verify_package(source, manifest)
    classes = {item["class"] for item in manifest["files"]}
    assert classes == {"E_COMMON", "E_CONTRACT"}


def test_proposer_materialization_excludes_profiling_and_inventories(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    specs = [
        ("source.py", "SOURCE", "print(1)\n"),
        ("contract.json", "CONTRACT", "{}\n"),
        ("proposal.json", "PROPOSAL_INPUT", '{"slot":1}\n'),
        ("profiling_result.json", "PROFILING_RESULT", '{"k":1}\n'),
        ("e_common.json", "E_COMMON", '{"n":30}\n'),
        ("e_contract.json", "E_CONTRACT", '{"n":20}\n'),
    ]
    file_specs = []
    for relative, content_class, text in specs:
        (source / relative).write_text(text, encoding="utf-8")
        file_specs.append({"path": relative, "class": content_class})
    full = build_package("CONSTRUCTION_A", source, file_specs, [])
    original = copy.deepcopy(full)
    proposer_root = tmp_path / "proposer"
    materialize_package(
        source, proposer_root, full, allowed_classes=PROPOSER_ALLOWED_CLASSES
    )
    assert full == original
    materialized = {path.relative_to(proposer_root).as_posix() for path in proposer_root.rglob("*") if path.is_file()}
    assert materialized == {"source.py", "contract.json", "proposal.json"}
    assert "profiling_result.json" not in materialized
    assert "e_common.json" not in materialized
    assert "e_contract.json" not in materialized
    forbidden = {"PROFILING_RESULT", "E_COMMON", "E_CONTRACT"}
    assert forbidden.isdisjoint(PROPOSER_ALLOWED_CLASSES)


def test_primary_package_b_rejects_contract_sensitivity(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    (source / "sensitivity.json").write_text("{}\n", encoding="utf-8")
    assert "E_CONTRACT_SENSITIVITY" in PACKAGE_B_CLASSES
    assert "E_CONTRACT_SENSITIVITY" not in PACKAGE_B_PRIMARY_CLASSES
    with pytest.raises(EvidenceError, match="E_PACKAGE_CONTENT_CLASS"):
        build_package(
            "CONTROLLED_B",
            source,
            [{"path": "sensitivity.json", "class": "E_CONTRACT_SENSITIVITY"}],
            [],
            allowed_classes=PACKAGE_B_PRIMARY_CLASSES,
        )


def test_sensitivity_package_b_rejects_primary_and_contract_confusion(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    (source / "primary.json").write_text("{}\n", encoding="utf-8")
    (source / "contract.json").write_text("{}\n", encoding="utf-8")
    assert "E_COMMON_PRIMARY" not in PACKAGE_B_SENSITIVITY_CLASSES
    with pytest.raises(EvidenceError, match="E_PACKAGE_CONTENT_CLASS"):
        build_package(
            "CONTROLLED_B",
            source,
            [{"path": "primary.json", "class": "E_COMMON_PRIMARY"}],
            [],
            allowed_classes=PACKAGE_B_SENSITIVITY_CLASSES,
        )
    with pytest.raises(EvidenceError, match="E_PACKAGE_CONTENT_CLASS"):
        build_package(
            "CONTROLLED_B",
            source,
            [{"path": "contract.json", "class": "E_CONTRACT"}],
            [],
            allowed_classes=PACKAGE_B_SENSITIVITY_CLASSES,
        )


def test_package_c_classes_remain_forbidden_from_a_and_b(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    (source / "buggy.py").write_text("x=1\n", encoding="utf-8")
    for role in ("CONSTRUCTION_A", "CONTROLLED_B"):
        with pytest.raises(EvidenceError, match="E_PACKAGE_CONTENT_CLASS"):
            build_package(
                role,
                source,
                [{"path": "buggy.py", "class": "P12_BUGGY"}],
                [],
            )
        with pytest.raises(EvidenceError, match="E_PACKAGE_CONTENT_CLASS"):
            build_package(
                role,
                source,
                [{"path": "buggy.py", "class": "P12_REVEAL"}],
                [],
            )
