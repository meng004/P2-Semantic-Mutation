from __future__ import annotations

import hashlib
import os

import pytest

import p3_v3.artifacts as artifacts_module
import scripts.p3_v3.evidence as evidence_module
from p3_v3.artifacts import (
    EvidenceError,
    canonical_json_bytes,
    canonical_sha256,
    read_canonical_json,
    safe_relative_path,
    validate_exact_object,
    validate_sha256,
    write_canonical_json,
)


def test_canonical_file_has_sorted_keys_and_one_terminal_lf(tmp_path):
    path = tmp_path / "artifact.json"
    write_canonical_json(path, {"b": 2, "a": 1}, exclusive=True)
    assert path.read_bytes() == b'{"a":1,"b":2}\n'
    assert read_canonical_json(path) == {"a": 1, "b": 2}


def test_exclusive_write_preserves_existing_bytes(tmp_path):
    path = tmp_path / "artifact.json"
    path.write_bytes(b"original\n")
    with pytest.raises(EvidenceError, match="E_EXISTS"):
        write_canonical_json(path, {"a": 1}, exclusive=True)
    assert path.read_bytes() == b"original\n"


def test_exclusive_write_retries_short_writes_and_publishes_complete_bytes(
    tmp_path, monkeypatch
):
    path = tmp_path / "artifact.json"
    real_write = os.write

    def short_write(fd, payload):
        return real_write(fd, payload[:2])

    monkeypatch.setattr(artifacts_module.os, "write", short_write)

    write_canonical_json(path, {"message": "complete"}, exclusive=True)

    assert path.read_bytes() == b'{"message":"complete"}\n'
    assert list(tmp_path.iterdir()) == [path]


def test_exclusive_write_link_failure_removes_temporary_and_final_path(
    tmp_path, monkeypatch
):
    path = tmp_path / "artifact.json"

    def fail_link(_source, _target):
        raise OSError("injected link failure")

    monkeypatch.setattr(artifacts_module.os, "link", fail_link)

    with pytest.raises(EvidenceError, match="E_ARTIFACT_WRITE"):
        write_canonical_json(path, {"secret": "must not appear in error"}, exclusive=True)

    assert not path.exists()
    assert list(tmp_path.iterdir()) == []


def test_exclusive_write_failure_before_publish_removes_partial_temporary(
    tmp_path, monkeypatch
):
    path = tmp_path / "artifact.json"

    def fail_write(_fd, _payload):
        raise OSError("injected write failure")

    monkeypatch.setattr(artifacts_module.os, "write", fail_write)

    with pytest.raises(EvidenceError, match="E_ARTIFACT_WRITE"):
        write_canonical_json(path, {"a": 1}, exclusive=True)

    assert not path.exists()
    assert list(tmp_path.iterdir()) == []


def test_authority_atomicity_injected_freeze_write_failure_leaves_no_partial(
    tmp_path, monkeypatch
):
    authority_inputs = tmp_path / "authority-inputs.json"
    output = tmp_path / "authority-lock.json"
    write_canonical_json(
        authority_inputs,
        {
            "schema_version": "P3_V3_AUTHORITY_INPUTS_V1",
            "task_id": "atomicity-fixture",
            "subjects": [
                {
                    "subject_id": "subject-a",
                    "repository_role": "CONTROLLED_A",
                    "root": str(tmp_path),
                    "build_descriptor_path": "build.json",
                    "adapter_id": "PYTHON_PEP517_V1",
                }
            ],
            "governing_material_paths": {
                "scientific_plan": "scientific-plan.md",
                "evidence_design": "evidence-design.md",
                "authority_lock_design": "authority-lock-design.md",
                "implementation_plan": "implementation-plan.md",
            },
            "protocol_artifact_paths": {
                "protocol": "protocol.json",
                "rq_spec": "rq-spec.json",
                "claim_ceiling": "claim-ceiling.json",
                "p12_contract": "p12-contract.json",
                "operator_catalogue": "operator-catalogue.json",
                "mr_policy": "mr-policy.json",
                "site_policy": "site-policy.json",
                "analysis_spec": "analysis-spec.json",
                "package_policy": "package-policy.json",
                "environment_lock": "environment-lock.json",
                "job_derivation_policy": "job-derivation-policy.json",
            },
            "registry_artifact_paths": {
                "adapter_registry": "adapter-registry.json",
                "input_generator_registry": "input-generator-registry.json",
            },
        },
        exclusive=True,
    )
    monkeypatch.setattr(
        evidence_module,
        "build_authority_lock",
        lambda _root, _inputs: {"schema_version": "P3_V3_AUTHORITY_LOCK_V1"},
    )

    real_fsync_directory = artifacts_module._fsync_directory
    real_write = artifacts_module.os.write
    fsynced: list[object] = []

    def record_fsync(directory):
        fsynced.append(directory)
        return real_fsync_directory(directory)

    def fail_write(_fd, _payload):
        raise OSError("injected write failure")

    monkeypatch.setattr(artifacts_module, "_fsync_directory", record_fsync)
    monkeypatch.setattr(artifacts_module.os, "write", fail_write)

    with pytest.raises(EvidenceError, match="E_ARTIFACT_WRITE"):
        evidence_module.freeze_authority_lock(
            tmp_path,
            authority_inputs,
            output,
        )

    assert not output.exists()
    assert list(tmp_path.iterdir()) == [authority_inputs]
    assert fsynced == []

    monkeypatch.setattr(artifacts_module.os, "write", real_write)
    evidence_module.freeze_authority_lock(tmp_path, authority_inputs, output)

    assert output.exists()
    assert fsynced == [tmp_path]


def test_exclusive_write_existing_target_leaves_no_temporary(tmp_path):
    path = tmp_path / "artifact.json"
    path.write_bytes(b"original\n")

    with pytest.raises(EvidenceError, match="E_EXISTS"):
        write_canonical_json(path, {"replacement": True}, exclusive=True)

    assert path.read_bytes() == b"original\n"
    assert list(tmp_path.iterdir()) == [path]


def test_exclusive_write_preserves_exists_error_when_temporary_cleanup_fails(
    tmp_path, monkeypatch
):
    path = tmp_path / "artifact.json"
    path.write_bytes(b"original\n")

    def fail_unlink(_path, *, missing_ok=False):
        raise OSError("injected cleanup failure")

    monkeypatch.setattr(artifacts_module.Path, "unlink", fail_unlink)

    with pytest.raises(EvidenceError) as caught:
        write_canonical_json(path, {"replacement": True}, exclusive=True)

    assert caught.value.code == "E_EXISTS"
    assert path.read_bytes() == b"original\n"


def test_exclusive_write_preserves_write_error_when_temporary_cleanup_fails(
    tmp_path, monkeypatch
):
    path = tmp_path / "artifact.json"

    def fail_link(_source, _target):
        raise OSError("injected link failure")

    def fail_unlink(_path, *, missing_ok=False):
        raise OSError("injected cleanup failure")

    monkeypatch.setattr(artifacts_module.os, "link", fail_link)
    monkeypatch.setattr(artifacts_module.Path, "unlink", fail_unlink)

    with pytest.raises(EvidenceError) as caught:
        write_canonical_json(path, {"payload": True}, exclusive=True)

    assert caught.value.code == "E_ARTIFACT_WRITE"
    assert not path.exists()


def test_exclusive_write_directory_fsync_failure_keeps_published_target(
    tmp_path, monkeypatch
):
    path = tmp_path / "artifact.json"

    def fail_directory_fsync(_directory):
        raise OSError("injected directory fsync failure")

    monkeypatch.setattr(artifacts_module, "_fsync_directory", fail_directory_fsync)

    with pytest.raises(EvidenceError, match="E_ARTIFACT_WRITE"):
        write_canonical_json(path, {"published": True}, exclusive=True)

    assert path.read_bytes() == b'{"published":true}\n'
    assert list(tmp_path.iterdir()) == [path]


def test_authority_lock_reader_accepts_one_canonical_regular_file(tmp_path):
    path = tmp_path / "lock.json"
    write_canonical_json(path, {"schema_version": "P3_V3_AUTHORITY_LOCK_V1"}, exclusive=True)

    assert artifacts_module.read_canonical_regular_bytes(
        path, "authority lock"
    ) == path.read_bytes()
    assert artifacts_module.read_canonical_regular_json(path, "authority lock") == {
        "schema_version": "P3_V3_AUTHORITY_LOCK_V1"
    }


def test_authority_lock_reader_rejects_symlinked_parent(tmp_path):
    real_parent = tmp_path / "real"
    real_parent.mkdir()
    target = real_parent / "lock.json"
    write_canonical_json(target, {"schema_version": "P3_V3_AUTHORITY_LOCK_V1"}, exclusive=True)
    linked_parent = tmp_path / "linked"
    linked_parent.symlink_to(real_parent, target_is_directory=True)

    with pytest.raises(EvidenceError, match="E_AUTHORITY_LOCK_PATH"):
        artifacts_module.read_canonical_regular_json(
            linked_parent / "lock.json", "authority lock"
        )


def test_authority_lock_reader_rejects_file_symlink(tmp_path):
    target = tmp_path / "lock.json"
    write_canonical_json(target, {"schema_version": "P3_V3_AUTHORITY_LOCK_V1"}, exclusive=True)
    link = tmp_path / "lock-link.json"
    link.symlink_to(target)

    with pytest.raises(EvidenceError, match="E_AUTHORITY_LOCK_PATH"):
        artifacts_module.read_canonical_regular_json(link, "authority lock")


def test_authority_lock_reader_rejects_special_node_without_opening_it(tmp_path):
    fifo = tmp_path / "lock.fifo"
    os.mkfifo(fifo)

    with pytest.raises(EvidenceError, match="E_AUTHORITY_LOCK_PATH"):
        artifacts_module.read_canonical_regular_json(fifo, "authority lock")


def test_authority_lock_reader_rejects_noncanonical_bytes(tmp_path):
    path = tmp_path / "lock.json"
    path.write_bytes(b'{"schema_version": "P3_V3_AUTHORITY_LOCK_V1"}\n')

    with pytest.raises(EvidenceError, match="E_AUTHORITY_LOCK_SCHEMA"):
        artifacts_module.read_canonical_regular_json(path, "authority lock")


def test_authority_lock_reader_normalizes_escaped_lone_surrogate(tmp_path):
    path = tmp_path / "lock.json"
    path.write_bytes(b'{"bad":"\\ud800"}\n')

    with pytest.raises(EvidenceError, match="E_AUTHORITY_LOCK_SCHEMA"):
        artifacts_module.read_canonical_regular_json(path, "authority lock")


def test_reader_rejects_noncanonical_json_bytes(tmp_path):
    path = tmp_path / "artifact.json"
    path.write_bytes(b'{"b": 2, "a": 1}\n')
    with pytest.raises(EvidenceError, match="E_NONCANONICAL_JSON"):
        read_canonical_json(path)


@pytest.mark.parametrize("value", [float("nan"), float("inf"), {"x": float("-inf")}])
def test_canonical_json_rejects_nonfinite_numbers(value):
    with pytest.raises(EvidenceError, match="E_CANONICAL_JSON"):
        canonical_json_bytes(value)


@pytest.mark.parametrize(
    "value",
    ["", "/absolute", "../escape", "a/../b", "a/./b", "a//b", "a\\b", "a\x00b"],
)
def test_safe_relative_path_rejects_unsafe_or_noncanonical_values(value):
    with pytest.raises(EvidenceError, match="E_PATH"):
        safe_relative_path(value)


def test_safe_relative_path_returns_posix_path():
    assert safe_relative_path("data/input.json").as_posix() == "data/input.json"


def test_exact_object_rejects_extra_key_and_bool_as_integer():
    schema = {"name": str, "count": int}
    with pytest.raises(EvidenceError, match="E_SCHEMA_KEYS"):
        validate_exact_object({"name": "x", "count": 1, "extra": 2}, schema, "record")
    with pytest.raises(EvidenceError, match="E_SCHEMA_TYPE"):
        validate_exact_object({"name": "x", "count": True}, schema, "record")


def test_sha256_and_canonical_hash_require_lowercase_hex():
    literal = b'{"a":1}\n'
    expected = hashlib.sha256(literal).hexdigest()
    assert canonical_sha256({"a": 1}) == expected
    assert validate_sha256(expected, "digest") == expected
    with pytest.raises(EvidenceError, match="E_SHA256"):
        validate_sha256(expected.upper(), "digest")


def test_byte_index_digest_covers_the_complete_self_hashed_artifact(tmp_path):
    body = {"schema_version": "fixture-v1", "policy": "blocked"}
    artifact = {**body, "artifact_sha256": canonical_sha256(body)}
    path = tmp_path / "authority.json"

    write_canonical_json(path, artifact, exclusive=True)

    byte_digest = hashlib.sha256(path.read_bytes()).hexdigest()
    assert byte_digest == hashlib.sha256(canonical_json_bytes(artifact)).hexdigest()
    assert byte_digest != artifact["artifact_sha256"]
    assert read_canonical_json(path) == artifact
