from __future__ import annotations

import copy
import os

import pytest

import p3_v3.packages as packages_module
from p3_v3.artifacts import EvidenceError, canonical_sha256
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
    (source / "e_contract.json").write_text(
        '{"inventory":"contract"}\n', encoding="utf-8"
    )
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
    materialized = {
        path.relative_to(proposer_root).as_posix()
        for path in proposer_root.rglob("*")
        if path.is_file()
    }
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


@pytest.mark.parametrize(
    "mutation",
    [
        "extra",
        "extra_directory",
        "fifo",
        "omission",
        "bytes",
        "mode",
        "symlink",
        "unsafe_manifest_path",
    ],
)
def test_verify_materialized_package_requires_exact_tree(tmp_path, mutation):
    root = tmp_path / "materialized-package"
    root.mkdir()
    program = root / "program.py"
    program.write_bytes(b"print(1)\n")
    manifest = build_package(
        "CONSTRUCTION_A",
        root,
        [{"path": "program.py", "class": "SOURCE"}],
        [],
    )
    if mutation == "extra":
        (root / "extra.txt").write_text("extra", encoding="utf-8")
    elif mutation == "extra_directory":
        (root / "empty").mkdir()
    elif mutation == "fifo":
        os.mkfifo(root / "named-pipe")
    elif mutation == "omission":
        program.unlink()
    elif mutation == "bytes":
        program.write_bytes(b"print(2)\n")
    elif mutation == "mode":
        program.chmod(0o600 if manifest["files"][0]["mode"] != 0o600 else 0o644)
    elif mutation == "symlink":
        program.unlink()
        target = root / "real.py"
        target.write_bytes(b"print(1)\n")
        program.symlink_to(target.name)
    else:
        manifest = copy.deepcopy(manifest)
        manifest["files"][0]["path"] = "../program.py"
        body = {
            key: value for key, value in manifest.items() if key != "artifact_sha256"
        }
        from p3_v3.artifacts import canonical_sha256

        manifest["package_tree_sha256"] = canonical_sha256(manifest["files"])
        body["package_tree_sha256"] = manifest["package_tree_sha256"]
        manifest["artifact_sha256"] = canonical_sha256(body)

    with pytest.raises(EvidenceError):
        packages_module.verify_materialized_package(root, manifest)


def test_verify_materialized_package_returns_validated_manifest(tmp_path):
    root = tmp_path / "materialized-package"
    root.mkdir()
    (root / "program.py").write_bytes(b"print(1)\n")
    manifest = build_package(
        "CONSTRUCTION_A",
        root,
        [{"path": "program.py", "class": "SOURCE"}],
        [],
    )

    assert packages_module.verify_materialized_package(root, manifest) == manifest


def test_verify_materialized_package_rejects_symlink_root(tmp_path):
    real_root = tmp_path / "real-package"
    real_root.mkdir()
    (real_root / "program.py").write_bytes(b"print(1)\n")
    manifest = build_package(
        "CONSTRUCTION_A",
        real_root,
        [{"path": "program.py", "class": "SOURCE"}],
        [],
    )
    linked_root = tmp_path / "linked-package"
    linked_root.symlink_to(real_root, target_is_directory=True)

    with pytest.raises(EvidenceError, match="E_PACKAGE_FILE_TYPE"):
        packages_module.verify_materialized_package(linked_root, manifest)


def _common_input_fixture():
    source_id = "21" * 32
    public_schema = {
        "schema_kind": "NUMERIC_ARRAY_DOMAIN_V1",
        "raw_schema": {"type": "array", "items": {"type": "number"}},
        "provenance_path": "public-schema.json",
        "provenance_span_or_key": "numeric",
    }
    raw_schema_sha256 = canonical_sha256(public_schema["raw_schema"])
    schema_selection_key = canonical_sha256(public_schema)
    rows = []
    for ordinal in range(1, 31):
        seed = int.from_bytes(
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
        envelope = {"ordinal": ordinal, "value": ordinal / 10}
        raw_payload_sha256 = canonical_sha256(envelope)
        identity = {
            "controlled_subject_source_id": source_id,
            "ordinal": ordinal,
            "generator_id": "NUMERIC_ARRAY_DOMAIN_V1",
            "schema_selection_key": schema_selection_key,
            "raw_schema_sha256": raw_schema_sha256,
            "schema_provenance_path": "public-schema.json",
            "schema_provenance_span_or_key": "numeric",
            "generator_source_sha256": "33" * 32,
            "raw_payload_sha256": raw_payload_sha256,
            "status": "COMMON_INPUT_EXECUTABLE",
            "failure_code": "",
            "domain": "P3-E-COMMON-INPUT-v1",
        }
        rows.append(
            {
                "ordinal": ordinal,
                "seed": seed,
                "generator_id": "NUMERIC_ARRAY_DOMAIN_V1",
                "schema_kind": "NUMERIC_ARRAY_DOMAIN_V1",
                "schema_selection_key": schema_selection_key,
                "raw_schema_sha256": raw_schema_sha256,
                "schema_provenance_path": "public-schema.json",
                "schema_provenance_span_or_key": "numeric",
                "generator_source_sha256": "33" * 32,
                "status": "COMMON_INPUT_EXECUTABLE",
                "failure_code": "",
                "envelope": envelope,
                "raw_payload_sha256": raw_payload_sha256,
                "input_id": canonical_sha256(identity),
            }
        )
    inventory_body = {
        "schema_version": "p3-evaluation-inputs-common-v1",
        "controlled_subject_source_id": source_id,
        "eligible_schema_count": 1,
        "rows": rows,
    }
    inventory = {
        **inventory_body,
        "artifact_sha256": canonical_sha256(inventory_body),
    }
    frame_body = {
        "schema_version": "p3-public-behavior-frame-v1",
        "controlled_subject_source_id": source_id,
        "rows": [],
        "public_schemas": [public_schema],
    }
    frame = {**frame_body, "artifact_sha256": canonical_sha256(frame_body)}
    from p3_v3.bridge_and_frames import select_profiling_workload

    workload = select_profiling_workload(frame, "S")
    validity_rows = [
        {
            key: row[key]
            for key in (
                "ordinal",
                "input_id",
                "raw_payload_sha256",
                "envelope",
                "generator_id",
                "schema_kind",
                "schema_selection_key",
                "raw_schema_sha256",
                "seed",
                "status",
                "failure_code",
            )
        }
        for row in rows
    ]
    validity_body = {
        "schema_version": "p3-common-input-validity-v1",
        "controlled_subject_source_id": source_id,
        "inventory_artifact_sha256": inventory["artifact_sha256"],
        "rows": validity_rows,
        "sites": [],
        "contracts": [],
        "profile": {},
        "frame_artifact_sha256": frame["artifact_sha256"],
    }
    validity = {**validity_body, "artifact_sha256": canonical_sha256(validity_body)}
    return inventory, validity, frame, workload


def _common_generator_registries():
    generator_ids = (
        "JSON_SCHEMA_DRAFT2020_12_V1",
        "CLI_TOKEN_GRAMMAR_V1",
        "NUMERIC_ARRAY_DOMAIN_V1",
        "TEXT_IO_SCHEMA_V1",
        "BINARY_RECORD_SCHEMA_V1",
    )
    return [
        {
            "generators": [
                {
                    "generator_id": generator_id,
                    "schema_kind": generator_id,
                    "source_sha256": "33" * 32,
                }
                for generator_id in generator_ids
            ]
        }
    ]


@pytest.mark.parametrize(
    "mutation",
    [
        "row_keys",
        "ordinal",
        "subject",
        "workload_subject",
        "generator",
        "schema",
        "seed",
        "raw_hash",
        "input_id",
        "validity_identity",
        "frame_hash",
        "preconsumer",
        "nonempty_preconsumer",
    ],
)
def test_common_input_evidence_rejects_identity_or_chronology_drift(mutation):
    inventory, validity, frame, workload = _common_input_fixture()
    inventory = copy.deepcopy(inventory)
    validity = copy.deepcopy(validity)
    frame = copy.deepcopy(frame)
    workload = copy.deepcopy(workload)
    consumers = [inventory["rows"][0]["input_id"]]
    if mutation == "row_keys":
        inventory["rows"][0]["fabricated"] = True
    elif mutation == "ordinal":
        inventory["rows"][0]["ordinal"] = 0
    elif mutation == "subject":
        inventory["controlled_subject_source_id"] = "41" * 32
    elif mutation == "workload_subject":
        workload["controlled_subject_source_id"] = "42" * 32
    elif mutation == "generator":
        inventory["rows"][0]["generator_id"] = None
    elif mutation == "schema":
        inventory["rows"][0]["schema_kind"] = "CLI_TOKEN_GRAMMAR_V1"
    elif mutation == "seed":
        inventory["rows"][0]["seed"] += 1
    elif mutation == "raw_hash":
        inventory["rows"][0]["raw_payload_sha256"] = "0" * 64
    elif mutation == "input_id":
        inventory["rows"][0]["input_id"] = "0" * 64
    elif mutation == "validity_identity":
        validity["rows"][0]["input_id"] = "0" * 64
    elif mutation == "frame_hash":
        validity["frame_artifact_sha256"] = "0" * 64
    elif mutation == "preconsumer":
        validity["rows"][0]["status"] = "COMMON_INPUT_INVALID"
    else:
        validity["sites"] = [{"site_id": "fabricated"}]
    for artifact in (inventory, validity, frame, workload):
        artifact["artifact_sha256"] = canonical_sha256(
            {key: value for key, value in artifact.items() if key != "artifact_sha256"}
        )

    with pytest.raises(EvidenceError, match="E_COMMON|E_SCHEMA_KEYS"):
        packages_module.verify_common_input_evidence(
            inventory,
            validity,
            controlled_subject_source_id="21" * 32,
            public_frame=frame,
            profiling_workload=workload,
            consumer_input_ids=consumers,
            generator_registries=_common_generator_registries(),
        )


def test_common_input_evidence_accepts_exact_preconsumer_receipt():
    inventory, validity, frame, workload = _common_input_fixture()

    verified = packages_module.verify_common_input_evidence(
        inventory,
        validity,
        controlled_subject_source_id="21" * 32,
        public_frame=frame,
        profiling_workload=workload,
        consumer_input_ids=[row["input_id"] for row in inventory["rows"]],
        generator_registries=_common_generator_registries(),
    )

    assert verified["inventory"] == inventory
    assert verified["validity"] == validity


def test_common_input_evidence_rejects_invented_allowlisted_generator_authority():
    inventory, validity, frame, workload = _common_input_fixture()
    invented = _common_generator_registries()
    invented[0]["generators"][2]["source_sha256"] = "44" * 32

    with pytest.raises(EvidenceError, match="E_COMMON_GENERATOR"):
        packages_module.verify_common_input_evidence(
            inventory,
            validity,
            controlled_subject_source_id="21" * 32,
            public_frame=frame,
            profiling_workload=workload,
            consumer_input_ids=[],
            generator_registries=invented,
        )


def test_common_input_evidence_rejects_rehashed_invented_public_schema():
    inventory, validity, frame, workload = _common_input_fixture()
    frame["public_schemas"][0]["raw_schema"] = {"type": "invented"}
    frame["artifact_sha256"] = canonical_sha256(
        {key: value for key, value in frame.items() if key != "artifact_sha256"}
    )
    from p3_v3.bridge_and_frames import select_profiling_workload

    workload = select_profiling_workload(frame, "S")
    validity["frame_artifact_sha256"] = frame["artifact_sha256"]
    validity["artifact_sha256"] = canonical_sha256(
        {key: value for key, value in validity.items() if key != "artifact_sha256"}
    )

    with pytest.raises(EvidenceError, match="E_COMMON_SCHEMA"):
        packages_module.verify_common_input_evidence(
            inventory,
            validity,
            controlled_subject_source_id="21" * 32,
            public_frame=frame,
            profiling_workload=workload,
            consumer_input_ids=[],
            generator_registries=_common_generator_registries(),
        )


def test_common_input_evidence_requires_validity_hash_in_first_consumer_intent():
    inventory, validity, frame, workload = _common_input_fixture()
    input_id = inventory["rows"][0]["input_id"]

    with pytest.raises(EvidenceError, match="E_COMMON_CHRONOLOGY"):
        packages_module.verify_common_input_evidence(
            inventory,
            validity,
            controlled_subject_source_id="21" * 32,
            public_frame=frame,
            profiling_workload=workload,
            consumer_input_ids=[input_id],
            generator_registries=_common_generator_registries(),
            consumer_intents=[
                {
                    "phase": "PHASE_5",
                    "job_id": "consumer",
                    "attempt": 1,
                    "evaluation_input_id": input_id,
                    "input_sha256": ["aa" * 32],
                }
            ],
        )
