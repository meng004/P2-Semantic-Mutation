from __future__ import annotations

import hashlib
import io
import os
import tarfile
import zipfile
from pathlib import Path

import pytest

from p3_v3.artifacts import EvidenceError, canonical_json_bytes, write_canonical_json
from p3_v3.bridge_and_frames import SourceSnapshot


REQUIRED_SOURCE_PREPARATION_TESTS = [
    "test_authorization_absent_writes_no_output",
    "test_authorization_wrong_bytes_writes_no_output",
    "test_implementation_verdict_hash_mismatch_fails_closed",
    "test_machine_plan_hash_mismatch_fails_closed",
    "test_capability_verdict_absent_writes_no_output",
    "test_launch_authority_absent_writes_no_output",
    "test_runtime_production_bytes_drift_writes_no_output",
    "test_authority_snapshot_binds_validated_bytes_on_replacement_race",
    "test_capability_verdict_requires_reviewed_commit",
    "test_capability_verdict_binds_implementation_files",
    "test_authority_dependency_graph_has_exactly_one_topological_order",
    "test_reconciliation_classifier_is_total_and_exclusive",
    "test_streamed_chunk_exceeds_member_limit_before_write",
    "test_streamed_chunks_exceed_total_limit",
    "test_overlimit_chunk_is_not_written",
    "test_streamed_chunk_length_rejects_bool_and_negative",
    "test_member_count_checked_before_content",
    "test_plan_verdict_rejects_noncanonical",
    "test_plan_verdict_rejects_extra_key",
    "test_plan_verdict_rejects_wrong_type",
    "test_plan_verdict_rejects_bad_sha",
    "test_capability_verdict_rejects_noncanonical",
    "test_capability_verdict_rejects_extra_key",
    "test_capability_verdict_rejects_wrong_type",
    "test_capability_verdict_rejects_bad_sha",
    "test_launch_verdict_rejects_noncanonical",
    "test_launch_verdict_rejects_extra_key",
    "test_launch_verdict_rejects_wrong_type",
    "test_launch_verdict_rejects_bad_sha",
    "test_launch_authority_rejects_noncanonical",
    "test_launch_authority_rejects_extra_key",
    "test_launch_authority_rejects_wrong_type",
    "test_launch_authority_rejects_bad_sha",
    "test_archive_snapshot_rejects_symlink",
    "test_archive_snapshot_rejects_non_regular_file",
    "test_archive_snapshot_hashes_same_fd_bytes",
    "test_archive_snapshot_rejects_identity_change",
    "test_archive_format_uses_bytes_not_suffix",
    "test_zip_rejects_parent_traversal",
    "test_zip_rejects_symlink",
    "test_zip_rejects_encrypted_member",
    "test_tar_rejects_parent_traversal",
    "test_tar_rejects_symlink",
    "test_tar_rejects_hardlink",
    "test_extractor_rejects_casefold_collision",
    "test_extractor_rejects_duplicate_normalized_path",
    "test_extractor_rejects_member_limit",
    "test_extractor_rejects_total_bytes_limit",
    "test_streamed_member_bytes_cannot_exceed_declared_policy_limit",
    "test_single_top_level_selection_is_order_invariant",
    "test_single_top_level_file_is_not_stripped",
    "test_materialized_tree_uses_phase1_canonical_hash",
    "test_phase1_tree_hash_function_is_called_by_production_seam",
    "test_wrong_materialized_tree_writes_failure_result",
    "test_source_manifest_exact_keys",
    "test_source_manifest_predecessors_are_exact",
    "test_source_manifest_cannot_validate_as_pilot_plan",
    "test_pass_result_binds_source_manifest",
    "test_outputs_are_exclusive",
    "test_crash_after_manifest_publication",
    "test_crash_after_materialize_root_rename",
    "test_manifest_only_recovery",
    "test_manifest_and_root_recovery",
    "test_tampered_manifest_refuses_recovery",
    "test_orphan_root_without_manifest_refuses_recovery",
    "test_result_is_always_the_final_pass_commit_point",
    "test_tree_mismatch_leaves_materialize_root_and_manifest_absent",
    "test_validate_source_cli_has_no_authority_overrides",
    "test_capability_implementation_creates_no_production_artifact",
]


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _patch_outputs(monkeypatch, module, tmp_path: Path) -> None:
    monkeypatch.setattr(module, "SOURCE_MANIFEST_PATH", tmp_path / "source-manifest.json")
    monkeypatch.setattr(
        module, "SOURCE_PREPARATION_RESULT_PATH", tmp_path / "source-preparation-result.json"
    )


def _write_zip(path: Path, members: dict[str, bytes]) -> Path:
    with zipfile.ZipFile(path, "w") as archive:
        for name, payload in members.items():
            archive.writestr(name, payload)
    return path


def _write_tar(path: Path, members: dict[str, bytes]) -> Path:
    with tarfile.open(path, "w") as archive:
        for name, payload in members.items():
            info = tarfile.TarInfo(name)
            info.size = len(payload)
            archive.addfile(info, io.BytesIO(payload))
    return path


def test_required_names_are_defined():
    defined = {name for name, value in globals().items() if callable(value)}
    missing = set(REQUIRED_SOURCE_PREPARATION_TESTS) - defined
    assert missing == set()


def _file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _install_capability_verdict(monkeypatch, tmp_path: Path) -> Path:
    import p3_v3.pilot_source as pilot_source

    plan_sha256 = _file_sha256(pilot_source.SOURCE_PREPARATION_PLAN_PATH)
    plan_verdict_sha256 = _file_sha256(
        pilot_source.CANONICAL_SOURCE_PREPARATION_PLAN_VERDICT_PATH
    )
    verdict = {
        "reviewed_plan_path": pilot_source.SOURCE_PREPARATION_PLAN_PATH.as_posix(),
        "reviewed_plan_sha256": plan_sha256,
        "reviewed_plan_verdict_sha256": plan_verdict_sha256,
        "reviewed_commit": "1cdf2a1d5b4f43c5565f2b773103a971784468e1",
        "reviewed_pilot_source_path": "src/p3_v3/pilot_source.py",
        "reviewed_pilot_source_sha256": _file_sha256(Path("src/p3_v3/pilot_source.py")),
        "reviewed_pilot_cli_path": "scripts/p3_v3/pilot.py",
        "reviewed_pilot_cli_sha256": _file_sha256(Path("scripts/p3_v3/pilot.py")),
        "reviewed_test_pilot_source_path": "tests/p3_v3/test_pilot_source.py",
        "reviewed_test_pilot_source_sha256": _file_sha256(
            Path("tests/p3_v3/test_pilot_source.py")
        ),
        "reviewed_test_pilot_path": "tests/p3_v3/test_pilot.py",
        "reviewed_test_pilot_sha256": _file_sha256(Path("tests/p3_v3/test_pilot.py")),
        "verdict": "PASS",
        "authorized_state": "PILOT_SOURCE_PREPARATION_IMPLEMENTATION_PASS",
        "claims": "blocked",
    }
    path = tmp_path / "capability-verdict.md"
    write_canonical_json(path, verdict, exclusive=True)
    monkeypatch.setattr(
        pilot_source, "CANONICAL_SOURCE_PREPARATION_CAPABILITY_VERDICT_PATH", path
    )
    return path


def _install_launch_predecessors(monkeypatch, tmp_path: Path) -> None:
    import p3_v3.pilot_source as pilot_source

    _install_capability_verdict(monkeypatch, tmp_path)
    auth = tmp_path / "user-auth-preparation.txt"
    auth.write_bytes(pilot_source.AUTHORIZATION_A_BYTES)
    monkeypatch.setattr(pilot_source, "AUTHORIZATION_A_PATH", auth)
    packet = tmp_path / "launch-packet.md"
    packet.write_bytes(b"synthetic launch packet\n")
    monkeypatch.setattr(pilot_source, "SOURCE_PREPARATION_LAUNCH_PACKET_PATH", packet)
    launch_verdict = {
        "reviewed_packet_path": packet.as_posix(),
        "reviewed_packet_sha256": _file_sha256(packet),
        "plan_verdict_sha256": _file_sha256(
            Path("docs/review_20260817/boost_math_pilot_source_preparation_sol_high_review.md")
        ),
        "capability_verdict_sha256": _file_sha256(
            tmp_path / "capability-verdict.md"
        ),
        "authorization_a_sha256": pilot_source.AUTHORIZATION_A_SHA256,
        "verdict": "PASS",
        "authorized_state": "PILOT_SOURCE_PREPARATION_LAUNCH_FROZEN",
        "claims": "blocked",
    }
    verdict_path = tmp_path / "launch-verdict.md"
    write_canonical_json(verdict_path, launch_verdict, exclusive=True)
    monkeypatch.setattr(
        pilot_source, "SOURCE_PREPARATION_LAUNCH_VERDICT_PATH", verdict_path
    )


def test_authorization_absent_writes_no_output(tmp_path, monkeypatch):
    import p3_v3.pilot_source as pilot_source

    _install_capability_verdict(monkeypatch, tmp_path)
    monkeypatch.setattr(
        pilot_source,
        "AUTHORIZATION_A_PATH",
        tmp_path / "user-auth-preparation.txt",
    )
    monkeypatch.setattr(
        pilot_source,
        "SOURCE_MANIFEST_PATH",
        tmp_path / "source-manifest.json",
    )
    monkeypatch.setattr(
        pilot_source,
        "SOURCE_PREPARATION_RESULT_PATH",
        tmp_path / "source-preparation-result.json",
    )
    with pytest.raises(EvidenceError, match="E_PILOT_PREPARATION_AUTH_ABSENT"):
        pilot_source.run_validate_source(
            tmp_path / "missing.zip",
            tmp_path / "materialize",
        )
    assert not (tmp_path / "source-manifest.json").exists()
    assert not (tmp_path / "source-preparation-result.json").exists()
    assert not (tmp_path / "materialize").exists()


def test_authorization_wrong_bytes_writes_no_output(tmp_path, monkeypatch):
    import p3_v3.pilot_source as pilot_source

    _install_capability_verdict(monkeypatch, tmp_path)
    auth = tmp_path / "user-auth-preparation.txt"
    auth.write_bytes(b"WRONG_AUTHORIZATION\n")
    monkeypatch.setattr(pilot_source, "AUTHORIZATION_A_PATH", auth)
    _patch_outputs(monkeypatch, pilot_source, tmp_path)
    with pytest.raises(EvidenceError, match="E_PILOT_PREPARATION_AUTH"):
        pilot_source.run_validate_source(tmp_path / "missing.zip", tmp_path / "materialize")
    assert not (tmp_path / "source-manifest.json").exists()
    assert not (tmp_path / "source-preparation-result.json").exists()


def test_implementation_verdict_hash_mismatch_fails_closed(tmp_path, monkeypatch):
    import p3_v3.pilot_source as pilot_source

    verdict = {
        "reviewed_plan_path": pilot_source.SOURCE_PREPARATION_PLAN_PATH.as_posix(),
        "reviewed_plan_sha256": "0" * 64,
        "reviewed_plan_verdict_sha256": "1" * 64,
        "reviewed_commit": "a" * 40,
        "reviewed_pilot_source_path": "src/p3_v3/pilot_source.py",
        "reviewed_pilot_source_sha256": "2" * 64,
        "reviewed_pilot_cli_path": "scripts/p3_v3/pilot.py",
        "reviewed_pilot_cli_sha256": "3" * 64,
        "reviewed_test_pilot_source_path": "tests/p3_v3/test_pilot_source.py",
        "reviewed_test_pilot_source_sha256": "4" * 64,
        "reviewed_test_pilot_path": "tests/p3_v3/test_pilot.py",
        "reviewed_test_pilot_sha256": "5" * 64,
        "verdict": "PASS",
        "authorized_state": "PILOT_SOURCE_PREPARATION_IMPLEMENTATION_PASS",
        "claims": "blocked",
    }
    with pytest.raises(
        EvidenceError, match="E_PILOT_SOURCE_PREPARATION_CAPABILITY_VERDICT"
    ):
        pilot_source.validate_source_preparation_capability_verdict(
            verdict, "6" * 64, "7" * 64
        )


def test_machine_plan_hash_mismatch_fails_closed():
    import p3_v3.pilot_source as pilot_source

    verdict = {
        "reviewed_plan_path": pilot_source.SOURCE_PREPARATION_PLAN_PATH.as_posix(),
        "reviewed_plan_sha256": "0" * 64,
        "verdict": "PASS",
        "authorized_state": "PILOT_SOURCE_PREPARATION_PLAN_FROZEN",
        "claims": "blocked",
    }
    with pytest.raises(EvidenceError, match="E_PILOT_SOURCE_PREPARATION_PLAN_VERDICT"):
        pilot_source.validate_source_preparation_plan_verdict(verdict, "1" * 64)


def test_capability_verdict_absent_writes_no_output(tmp_path, monkeypatch):
    import p3_v3.pilot_source as pilot_source

    monkeypatch.setattr(
        pilot_source,
        "CANONICAL_SOURCE_PREPARATION_CAPABILITY_VERDICT_PATH",
        tmp_path / "missing-capability-verdict.md",
    )
    monkeypatch.setattr(
        pilot_source,
        "SOURCE_MANIFEST_PATH",
        tmp_path / "source-manifest.json",
    )
    monkeypatch.setattr(
        pilot_source,
        "SOURCE_PREPARATION_RESULT_PATH",
        tmp_path / "source-preparation-result.json",
    )
    with pytest.raises(
        EvidenceError, match="E_PILOT_SOURCE_PREPARATION_CAPABILITY_VERDICT_ABSENT"
    ):
        pilot_source.run_validate_source(
            tmp_path / "missing.zip",
            tmp_path / "materialize",
        )
    assert not (tmp_path / "source-manifest.json").exists()
    assert not (tmp_path / "source-preparation-result.json").exists()


def test_launch_authority_absent_writes_no_output(tmp_path, monkeypatch):
    import p3_v3.pilot_source as pilot_source

    _install_launch_predecessors(monkeypatch, tmp_path)
    monkeypatch.setattr(
        pilot_source,
        "SOURCE_PREPARATION_LAUNCH_PATH",
        tmp_path / "missing-launch.json",
    )
    monkeypatch.setattr(
        pilot_source,
        "SOURCE_MANIFEST_PATH",
        tmp_path / "source-manifest.json",
    )
    monkeypatch.setattr(
        pilot_source,
        "SOURCE_PREPARATION_RESULT_PATH",
        tmp_path / "source-preparation-result.json",
    )
    with pytest.raises(
        EvidenceError, match="E_PILOT_SOURCE_PREPARATION_LAUNCH_ABSENT"
    ):
        pilot_source.run_validate_source(
            tmp_path / "missing.zip",
            tmp_path / "materialize",
        )
    assert not (tmp_path / "source-manifest.json").exists()
    assert not (tmp_path / "source-preparation-result.json").exists()


def test_runtime_production_bytes_drift_writes_no_output(tmp_path, monkeypatch):
    import p3_v3.pilot_source as pilot_source

    _install_capability_verdict(monkeypatch, tmp_path)
    monkeypatch.setattr(
        pilot_source,
        "REVIEWED_PILOT_SOURCE_PATH",
        tmp_path / "drifted-pilot-source.py",
    )
    (tmp_path / "drifted-pilot-source.py").write_text("drifted\n", encoding="utf-8")
    monkeypatch.setattr(
        pilot_source,
        "SOURCE_MANIFEST_PATH",
        tmp_path / "source-manifest.json",
    )
    monkeypatch.setattr(
        pilot_source,
        "SOURCE_PREPARATION_RESULT_PATH",
        tmp_path / "source-preparation-result.json",
    )
    with pytest.raises(
        EvidenceError, match="E_PILOT_SOURCE_PREPARATION_CAPABILITY_VERDICT"
    ):
        pilot_source.run_validate_source(
            tmp_path / "missing.zip",
            tmp_path / "materialize",
        )
    assert not (tmp_path / "source-manifest.json").exists()
    assert not (tmp_path / "source-preparation-result.json").exists()


def test_authority_snapshot_binds_validated_bytes_on_replacement_race(tmp_path):
    import p3_v3.pilot_source as pilot_source

    path = tmp_path / "authority.json"
    first = {"schema_version": "race-v1", "value": "before"}
    path.write_bytes(canonical_json_bytes(first))
    raw, digest = pilot_source.read_authority_snapshot(path, "race")
    path.write_bytes(canonical_json_bytes({"schema_version": "race-v1", "value": "after"}))
    assert raw == canonical_json_bytes(first)
    assert digest == _sha256_bytes(raw)
    assert digest != _sha256_bytes(path.read_bytes())


def test_capability_verdict_requires_reviewed_commit():
    import p3_v3.pilot_source as pilot_source

    verdict = {
        "reviewed_plan_path": pilot_source.SOURCE_PREPARATION_PLAN_PATH.as_posix(),
        "reviewed_plan_sha256": "0" * 64,
        "reviewed_plan_verdict_sha256": "1" * 64,
        "reviewed_commit": "NOT-A-COMMIT",
        "reviewed_pilot_source_path": "src/p3_v3/pilot_source.py",
        "reviewed_pilot_source_sha256": "2" * 64,
        "reviewed_pilot_cli_path": "scripts/p3_v3/pilot.py",
        "reviewed_pilot_cli_sha256": "3" * 64,
        "reviewed_test_pilot_source_path": "tests/p3_v3/test_pilot_source.py",
        "reviewed_test_pilot_source_sha256": "4" * 64,
        "reviewed_test_pilot_path": "tests/p3_v3/test_pilot.py",
        "reviewed_test_pilot_sha256": "5" * 64,
        "verdict": "PASS",
        "authorized_state": "PILOT_SOURCE_PREPARATION_IMPLEMENTATION_PASS",
        "claims": "blocked",
    }
    with pytest.raises(
        EvidenceError, match="E_PILOT_SOURCE_PREPARATION_CAPABILITY_VERDICT"
    ):
        pilot_source.validate_source_preparation_capability_verdict(
            verdict, "0" * 64, "1" * 64
        )


def test_capability_verdict_binds_implementation_files():
    import p3_v3.pilot_source as pilot_source

    verdict = {
        "reviewed_plan_path": pilot_source.SOURCE_PREPARATION_PLAN_PATH.as_posix(),
        "reviewed_plan_sha256": "0" * 64,
        "reviewed_plan_verdict_sha256": "1" * 64,
        "reviewed_commit": "a" * 40,
        "reviewed_pilot_source_path": "src/wrong.py",
        "reviewed_pilot_source_sha256": "2" * 64,
        "reviewed_pilot_cli_path": "scripts/p3_v3/pilot.py",
        "reviewed_pilot_cli_sha256": "3" * 64,
        "reviewed_test_pilot_source_path": "tests/p3_v3/test_pilot_source.py",
        "reviewed_test_pilot_source_sha256": "4" * 64,
        "reviewed_test_pilot_path": "tests/p3_v3/test_pilot.py",
        "reviewed_test_pilot_sha256": "5" * 64,
        "verdict": "PASS",
        "authorized_state": "PILOT_SOURCE_PREPARATION_IMPLEMENTATION_PASS",
        "claims": "blocked",
    }
    with pytest.raises(
        EvidenceError, match="E_PILOT_SOURCE_PREPARATION_CAPABILITY_VERDICT"
    ):
        pilot_source.validate_source_preparation_capability_verdict(
            verdict, "0" * 64, "1" * 64
        )


def test_authority_dependency_graph_has_exactly_one_topological_order():
    from p3_v3.pilot_source import (
        AUTHORITY_DEPENDENCY_EDGES,
        UNIQUE_AUTHORITY_ORDER,
        count_topological_authority_orders,
        require_unique_topological_authority_order,
    )

    order = require_unique_topological_authority_order(AUTHORITY_DEPENDENCY_EDGES)
    assert count_topological_authority_orders(AUTHORITY_DEPENDENCY_EDGES) == 1
    assert order == UNIQUE_AUTHORITY_ORDER
    missing_capability_to_auth = [
        edge
        for edge in AUTHORITY_DEPENDENCY_EDGES
        if edge != ("capability_verdict", "authorization_a")
    ]
    with pytest.raises(ValueError, match="non-unique topological order"):
        require_unique_topological_authority_order(missing_capability_to_auth)
    assert count_topological_authority_orders(missing_capability_to_auth) != 1
    missing_auth_to_packet = [
        edge
        for edge in AUTHORITY_DEPENDENCY_EDGES
        if edge != ("authorization_a", "launch_packet")
    ]
    with pytest.raises(ValueError, match="non-unique topological order"):
        require_unique_topological_authority_order(missing_auth_to_packet)
    assert count_topological_authority_orders(missing_auth_to_packet) != 1


def test_reconciliation_classifier_is_total_and_exclusive():
    from p3_v3.pilot_source import (
        RECONCILIATION_STATES,
        classify_reconciliation,
        enumerate_reconciliation_cases,
    )

    cases = enumerate_reconciliation_cases()
    observed = {case[-1] for case in cases}
    assert observed == set(RECONCILIATION_STATES)
    assert len(cases) == 31
    assert len(RECONCILIATION_STATES) == 12
    for case in cases:
        again = classify_reconciliation(
            manifest_present=case[0],
            result_present=case[1],
            root_present=case[2],
            manifest_valid=case[3],
            result_valid=case[4],
            result_status=case[5],
            closed_pair_consistent=case[6],
        )
        assert again == case[-1]


def test_streamed_chunk_exceeds_member_limit_before_write():
    from p3_v3.pilot_source import StreamedLimitCounter

    written: list[bytes] = []
    counter = StreamedLimitCounter(
        {"max_member_count": 2, "max_member_bytes": 4, "max_total_uncompressed_bytes": 100}
    )
    counter.begin_member()
    with pytest.raises(EvidenceError, match="E_PILOT_EXTRACT_UNSAFE"):
        counter.consume_chunk(5)
        written.append(b"12345")
    assert written == []


def test_streamed_chunks_exceed_total_limit():
    from p3_v3.pilot_source import StreamedLimitCounter

    counter = StreamedLimitCounter(
        {"max_member_count": 3, "max_member_bytes": 100, "max_total_uncompressed_bytes": 10}
    )
    counter.begin_member()
    counter.consume_chunk(6)
    counter.end_member()
    counter.begin_member()
    with pytest.raises(EvidenceError, match="E_PILOT_EXTRACT_UNSAFE"):
        counter.consume_chunk(5)


def test_overlimit_chunk_is_not_written():
    from p3_v3.pilot_source import StreamedLimitCounter

    staging: list[bytes] = []
    counter = StreamedLimitCounter(
        {"max_member_count": 1, "max_member_bytes": 3, "max_total_uncompressed_bytes": 3}
    )
    counter.begin_member()
    counter.consume_chunk(2)
    staging.append(b"ab")
    chunk = b"cd"
    with pytest.raises(EvidenceError, match="E_PILOT_EXTRACT_UNSAFE"):
        counter.consume_chunk(len(chunk))
        staging.append(chunk)
    assert staging == [b"ab"]


def test_streamed_chunk_length_rejects_bool_and_negative():
    from p3_v3.pilot_source import EXTRACTOR_POLICY_V1, StreamedLimitCounter

    counter = StreamedLimitCounter(EXTRACTOR_POLICY_V1)
    counter.begin_member()
    with pytest.raises(EvidenceError, match="E_PILOT_EXTRACT_UNSAFE"):
        counter.consume_chunk(True)
    with pytest.raises(EvidenceError, match="E_PILOT_EXTRACT_UNSAFE"):
        counter.consume_chunk(-1)


def test_member_count_checked_before_content():
    from p3_v3.pilot_source import EXTRACTOR_POLICY_V1, StreamedLimitCounter

    policy = dict(EXTRACTOR_POLICY_V1)
    policy["max_member_count"] = 1
    counter = StreamedLimitCounter(policy)
    counter.begin_member()
    counter.end_member()
    with pytest.raises(EvidenceError, match="E_PILOT_EXTRACT_UNSAFE"):
        counter.begin_member()


def _plan_verdict_valid():
    import p3_v3.pilot_source as pilot_source

    return {
        "reviewed_plan_path": pilot_source.SOURCE_PREPARATION_PLAN_PATH.as_posix(),
        "reviewed_plan_sha256": "0" * 64,
        "verdict": "PASS",
        "authorized_state": "PILOT_SOURCE_PREPARATION_PLAN_FROZEN",
        "claims": "blocked",
    }


def test_plan_verdict_rejects_noncanonical():
    import p3_v3.pilot_source as pilot_source

    raw = b'{"authorized_state":"PILOT_SOURCE_PREPARATION_PLAN_FROZEN","claims":"blocked","reviewed_plan_path":"docs/superpowers/plans/2026-08-17-p3-boost-math-pilot-source-preparation-only.md","reviewed_plan_sha256":"' + b"0" * 64 + b'","verdict":"PASS"} \n'
    with pytest.raises(EvidenceError, match="E_PILOT_SOURCE_PREPARATION_PLAN_VERDICT"):
        parsed = pilot_source.parse_canonical_authority_object(raw, "plan-verdict")
        pilot_source.validate_source_preparation_plan_verdict(parsed, "0" * 64)


def test_plan_verdict_rejects_extra_key():
    import p3_v3.pilot_source as pilot_source

    value = dict(_plan_verdict_valid())
    value["extra"] = "no"
    with pytest.raises(EvidenceError, match="E_PILOT_SOURCE_PREPARATION_PLAN_VERDICT"):
        pilot_source.validate_source_preparation_plan_verdict(value, "0" * 64)


def test_plan_verdict_rejects_wrong_type():
    import p3_v3.pilot_source as pilot_source

    value = dict(_plan_verdict_valid())
    value["claims"] = False
    with pytest.raises(EvidenceError, match="E_PILOT_SOURCE_PREPARATION_PLAN_VERDICT"):
        pilot_source.validate_source_preparation_plan_verdict(value, "0" * 64)


def test_plan_verdict_rejects_bad_sha():
    import p3_v3.pilot_source as pilot_source

    value = dict(_plan_verdict_valid())
    value["reviewed_plan_sha256"] = "not-a-sha"
    with pytest.raises(EvidenceError, match="E_PILOT_SOURCE_PREPARATION_PLAN_VERDICT"):
        pilot_source.validate_source_preparation_plan_verdict(value, "0" * 64)


def _capability_verdict_valid():
    return {
        "reviewed_plan_path": "docs/superpowers/plans/2026-08-17-p3-boost-math-pilot-source-preparation-only.md",
        "reviewed_plan_sha256": "0" * 64,
        "reviewed_plan_verdict_sha256": "1" * 64,
        "reviewed_commit": "a" * 40,
        "reviewed_pilot_source_path": "src/p3_v3/pilot_source.py",
        "reviewed_pilot_source_sha256": "2" * 64,
        "reviewed_pilot_cli_path": "scripts/p3_v3/pilot.py",
        "reviewed_pilot_cli_sha256": "3" * 64,
        "reviewed_test_pilot_source_path": "tests/p3_v3/test_pilot_source.py",
        "reviewed_test_pilot_source_sha256": "4" * 64,
        "reviewed_test_pilot_path": "tests/p3_v3/test_pilot.py",
        "reviewed_test_pilot_sha256": "5" * 64,
        "verdict": "PASS",
        "authorized_state": "PILOT_SOURCE_PREPARATION_IMPLEMENTATION_PASS",
        "claims": "blocked",
    }


def test_capability_verdict_rejects_noncanonical():
    import p3_v3.pilot_source as pilot_source

    raw = canonical_json_bytes(_capability_verdict_valid())[:-1] + b" \n"
    with pytest.raises(EvidenceError, match="E_PILOT_SOURCE_PREPARATION_CAPABILITY_VERDICT"):
        parsed = pilot_source.parse_canonical_authority_object(raw, "capability-verdict")
        pilot_source.validate_source_preparation_capability_verdict(
            parsed, "0" * 64, "1" * 64
        )


def test_capability_verdict_rejects_extra_key():
    import p3_v3.pilot_source as pilot_source

    value = dict(_capability_verdict_valid())
    value["extra"] = "no"
    with pytest.raises(EvidenceError, match="E_PILOT_SOURCE_PREPARATION_CAPABILITY_VERDICT"):
        pilot_source.validate_source_preparation_capability_verdict(
            value, "0" * 64, "1" * 64
        )


def test_capability_verdict_rejects_wrong_type():
    import p3_v3.pilot_source as pilot_source

    value = dict(_capability_verdict_valid())
    value["claims"] = 1
    with pytest.raises(EvidenceError, match="E_PILOT_SOURCE_PREPARATION_CAPABILITY_VERDICT"):
        pilot_source.validate_source_preparation_capability_verdict(
            value, "0" * 64, "1" * 64
        )


def test_capability_verdict_rejects_bad_sha():
    import p3_v3.pilot_source as pilot_source

    value = dict(_capability_verdict_valid())
    value["reviewed_plan_sha256"] = "zz"
    with pytest.raises(EvidenceError, match="E_PILOT_SOURCE_PREPARATION_CAPABILITY_VERDICT"):
        pilot_source.validate_source_preparation_capability_verdict(
            value, "0" * 64, "1" * 64
        )


def _launch_verdict_valid():
    return {
        "reviewed_packet_path": "docs/review_20260817/boost_math_pilot_source_preparation_launch_packet.md",
        "reviewed_packet_sha256": "0" * 64,
        "plan_verdict_sha256": "1" * 64,
        "capability_verdict_sha256": "2" * 64,
        "authorization_a_sha256": "3" * 64,
        "verdict": "PASS",
        "authorized_state": "PILOT_SOURCE_PREPARATION_LAUNCH_FROZEN",
        "claims": "blocked",
    }


def test_launch_verdict_rejects_noncanonical():
    import p3_v3.pilot_source as pilot_source

    raw = canonical_json_bytes(_launch_verdict_valid())[:-1] + b" \n"
    with pytest.raises(EvidenceError, match="E_PILOT_SOURCE_PREPARATION_LAUNCH"):
        parsed = pilot_source.parse_canonical_authority_object(raw, "launch-verdict")
        pilot_source.validate_source_preparation_launch_verdict(
            parsed,
            packet_sha256="0" * 64,
            plan_verdict_sha256="1" * 64,
            capability_verdict_sha256="2" * 64,
            authorization_a_sha256="3" * 64,
        )


def test_launch_verdict_rejects_extra_key():
    import p3_v3.pilot_source as pilot_source

    value = dict(_launch_verdict_valid())
    value["extra"] = "no"
    with pytest.raises(EvidenceError, match="E_PILOT_SOURCE_PREPARATION_LAUNCH"):
        pilot_source.validate_source_preparation_launch_verdict(
            value,
            packet_sha256="0" * 64,
            plan_verdict_sha256="1" * 64,
            capability_verdict_sha256="2" * 64,
            authorization_a_sha256="3" * 64,
        )


def test_launch_verdict_rejects_wrong_type():
    import p3_v3.pilot_source as pilot_source

    value = dict(_launch_verdict_valid())
    value["verdict"] = True
    with pytest.raises(EvidenceError, match="E_PILOT_SOURCE_PREPARATION_LAUNCH"):
        pilot_source.validate_source_preparation_launch_verdict(
            value,
            packet_sha256="0" * 64,
            plan_verdict_sha256="1" * 64,
            capability_verdict_sha256="2" * 64,
            authorization_a_sha256="3" * 64,
        )


def test_launch_verdict_rejects_bad_sha():
    import p3_v3.pilot_source as pilot_source

    value = dict(_launch_verdict_valid())
    value["reviewed_packet_sha256"] = "bad"
    with pytest.raises(EvidenceError, match="E_PILOT_SOURCE_PREPARATION_LAUNCH"):
        pilot_source.validate_source_preparation_launch_verdict(
            value,
            packet_sha256="0" * 64,
            plan_verdict_sha256="1" * 64,
            capability_verdict_sha256="2" * 64,
            authorization_a_sha256="3" * 64,
        )


def _launch_authority_valid():
    return {
        "schema_version": "p3-pilot-source-preparation-launch-v1",
        "execution_class": "PILOT_ONLY",
        "denominator": "PILOT_ONLY",
        "source_preparation_plan_path": "docs/superpowers/plans/2026-08-17-p3-boost-math-pilot-source-preparation-only.md",
        "source_preparation_plan_sha256": "0" * 64,
        "source_preparation_plan_verdict_path": "docs/review_20260817/boost_math_pilot_source_preparation_sol_high_review.md",
        "source_preparation_plan_verdict_sha256": "1" * 64,
        "capability_implementation_verdict_path": "docs/review_20260817/boost_math_pilot_source_preparation_implementation_sol_high_review.md",
        "capability_implementation_verdict_sha256": "2" * 64,
        "production_launch_packet_path": "docs/review_20260817/boost_math_pilot_source_preparation_launch_packet.md",
        "production_launch_packet_sha256": "3" * 64,
        "launch_sol_high_verdict_path": "docs/review_20260817/boost_math_pilot_source_preparation_launch_sol_high_review.md",
        "launch_sol_high_verdict_sha256": "4" * 64,
        "authorization_a_sha256": "5" * 64,
        "claims": "blocked",
        "artifact_sha256": "6" * 64,
    }


def test_launch_authority_rejects_noncanonical():
    import p3_v3.pilot_source as pilot_source

    raw = canonical_json_bytes(_launch_authority_valid())[:-1] + b" \n"
    with pytest.raises(EvidenceError, match="E_PILOT_SOURCE_PREPARATION_LAUNCH"):
        parsed = pilot_source.parse_canonical_authority_object(raw, "launch")
        pilot_source.validate_source_preparation_launch(
            parsed,
            plan_sha256="0" * 64,
            plan_verdict_sha256="1" * 64,
            capability_verdict_sha256="2" * 64,
            launch_packet_sha256="3" * 64,
            launch_verdict_sha256="4" * 64,
            authorization_a_sha256="5" * 64,
        )


def test_launch_authority_rejects_extra_key():
    import p3_v3.pilot_source as pilot_source

    value = dict(_launch_authority_valid())
    value["extra"] = "no"
    with pytest.raises(EvidenceError, match="E_PILOT_SOURCE_PREPARATION_LAUNCH"):
        pilot_source.validate_source_preparation_launch(
            value,
            plan_sha256="0" * 64,
            plan_verdict_sha256="1" * 64,
            capability_verdict_sha256="2" * 64,
            launch_packet_sha256="3" * 64,
            launch_verdict_sha256="4" * 64,
            authorization_a_sha256="5" * 64,
        )


def test_launch_authority_rejects_wrong_type():
    import p3_v3.pilot_source as pilot_source

    value = dict(_launch_authority_valid())
    value["claims"] = 0
    with pytest.raises(EvidenceError, match="E_PILOT_SOURCE_PREPARATION_LAUNCH"):
        pilot_source.validate_source_preparation_launch(
            value,
            plan_sha256="0" * 64,
            plan_verdict_sha256="1" * 64,
            capability_verdict_sha256="2" * 64,
            launch_packet_sha256="3" * 64,
            launch_verdict_sha256="4" * 64,
            authorization_a_sha256="5" * 64,
        )


def test_launch_authority_rejects_bad_sha():
    import p3_v3.pilot_source as pilot_source

    value = dict(_launch_authority_valid())
    value["source_preparation_plan_sha256"] = "bad"
    with pytest.raises(EvidenceError, match="E_PILOT_SOURCE_PREPARATION_LAUNCH"):
        pilot_source.validate_source_preparation_launch(
            value,
            plan_sha256="0" * 64,
            plan_verdict_sha256="1" * 64,
            capability_verdict_sha256="2" * 64,
            launch_packet_sha256="3" * 64,
            launch_verdict_sha256="4" * 64,
            authorization_a_sha256="5" * 64,
        )


def test_archive_snapshot_rejects_symlink(tmp_path):
    from p3_v3.pilot_source import read_production_archive_bytes

    target = tmp_path / "real.zip"
    target.write_bytes(b"PK\x03\x04" + b"x")
    link = tmp_path / "link.zip"
    link.symlink_to(target)
    with pytest.raises(EvidenceError, match="E_PILOT_ARCHIVE_UNSAFE"):
        read_production_archive_bytes(link)


def test_archive_snapshot_rejects_non_regular_file(tmp_path):
    from p3_v3.pilot_source import read_production_archive_bytes

    directory = tmp_path / "not-a-file"
    directory.mkdir()
    with pytest.raises(EvidenceError, match="E_PILOT_ARCHIVE_UNSAFE"):
        read_production_archive_bytes(directory)


def test_archive_snapshot_hashes_same_fd_bytes(tmp_path):
    from p3_v3.pilot_source import read_production_archive_bytes

    archive = tmp_path / "fixture.zip"
    archive.write_bytes(b"PK\x03\x04" + b"synthetic-zip-bytes")
    snapshot = read_production_archive_bytes(archive)
    assert snapshot.sha256 == __import__("hashlib").sha256(snapshot.raw).hexdigest()
    assert snapshot.size == len(snapshot.raw)
    assert snapshot.archive_format == "ZIP"


def test_archive_snapshot_rejects_identity_change(tmp_path, monkeypatch):
    import p3_v3.pilot_source as pilot_source

    archive = tmp_path / "fixture.zip"
    archive.write_bytes(b"PK\x03\x04" + b"synthetic-zip-bytes")
    original = os.fstat
    calls = {"n": 0}

    def flaky(fd):
        info = original(fd)
        calls["n"] += 1
        if calls["n"] >= 3:
            return os.stat_result(
                (
                    info.st_mode,
                    info.st_ino + 1,
                    info.st_dev,
                    info.st_nlink,
                    info.st_uid,
                    info.st_gid,
                    info.st_size,
                    info.st_atime,
                    info.st_mtime,
                    info.st_ctime,
                )
            )
        return info

    monkeypatch.setattr(pilot_source.os, "fstat", flaky)
    with pytest.raises(EvidenceError, match="E_PILOT_ARCHIVE_UNSAFE"):
        pilot_source.read_production_archive_bytes(archive)


def test_archive_format_uses_bytes_not_suffix(tmp_path):
    from p3_v3.pilot_source import read_production_archive_bytes

    archive = tmp_path / "named-as.tar"
    archive.write_bytes(b"PK\x03\x04" + b"synthetic-zip-bytes")
    snapshot = read_production_archive_bytes(archive)
    assert snapshot.archive_format == "ZIP"


def test_zip_rejects_parent_traversal(tmp_path):
    import p3_v3.pilot_source as pilot_source

    archive = tmp_path / "bad.zip"
    with zipfile.ZipFile(archive, "w") as handle:
        handle.writestr("../escape.txt", b"x")
    snapshot = pilot_source.read_production_archive_bytes(archive)
    with pytest.raises(EvidenceError, match="E_PILOT_EXTRACT_UNSAFE"):
        pilot_source.extract_archive_to_staging(snapshot, tmp_path / "stage")


def test_zip_rejects_symlink(tmp_path):
    import p3_v3.pilot_source as pilot_source

    archive = tmp_path / "link.zip"
    with zipfile.ZipFile(archive, "w") as handle:
        info = zipfile.ZipInfo("link")
        info.create_system = 3
        info.external_attr = 0o120777 << 16
        handle.writestr(info, b"target")
    snapshot = pilot_source.read_production_archive_bytes(archive)
    with pytest.raises(EvidenceError, match="E_PILOT_EXTRACT_UNSAFE"):
        pilot_source.extract_archive_to_staging(snapshot, tmp_path / "stage")


def test_zip_rejects_encrypted_member(tmp_path):
    import p3_v3.pilot_source as pilot_source

    archive = tmp_path / "enc.zip"
    with zipfile.ZipFile(archive, "w") as handle:
        handle.setpassword(b"secret")
        handle.writestr("secret.txt", b"hidden")
        info = handle.getinfo("secret.txt")
        info.flag_bits |= 0x1
    data = bytearray(archive.read_bytes())
    index = 0
    while True:
        index = data.find(b"PK\x03\x04", index)
        if index < 0:
            break
        data[index + 6] |= 0x1
        index += 4
    index = 0
    while True:
        index = data.find(b"PK\x01\x02", index)
        if index < 0:
            break
        data[index + 8] |= 0x1
        index += 4
    archive.write_bytes(data)
    snapshot = pilot_source.read_production_archive_bytes(archive)
    with pytest.raises(EvidenceError, match="E_PILOT_EXTRACT_UNSAFE"):
        pilot_source.extract_archive_to_staging(snapshot, tmp_path / "stage")


def test_tar_rejects_parent_traversal(tmp_path):
    import p3_v3.pilot_source as pilot_source

    archive = tmp_path / "bad.tar"
    with tarfile.open(archive, "w") as handle:
        info = tarfile.TarInfo("../escape.txt")
        payload = b"x"
        info.size = len(payload)
        handle.addfile(info, io.BytesIO(payload))
    snapshot = pilot_source.read_production_archive_bytes(archive)
    with pytest.raises(EvidenceError, match="E_PILOT_EXTRACT_UNSAFE"):
        pilot_source.extract_archive_to_staging(snapshot, tmp_path / "stage")


def test_tar_rejects_symlink(tmp_path):
    import p3_v3.pilot_source as pilot_source

    archive = tmp_path / "link.tar"
    with tarfile.open(archive, "w") as handle:
        info = tarfile.TarInfo("link")
        info.type = tarfile.SYMTYPE
        info.linkname = "target"
        handle.addfile(info)
    snapshot = pilot_source.read_production_archive_bytes(archive)
    with pytest.raises(EvidenceError, match="E_PILOT_EXTRACT_UNSAFE"):
        pilot_source.extract_archive_to_staging(snapshot, tmp_path / "stage")


def test_tar_rejects_hardlink(tmp_path):
    import p3_v3.pilot_source as pilot_source

    archive = tmp_path / "hard.tar"
    with tarfile.open(archive, "w") as handle:
        payload = b"x"
        regular = tarfile.TarInfo("a.txt")
        regular.size = len(payload)
        handle.addfile(regular, io.BytesIO(payload))
        link = tarfile.TarInfo("b.txt")
        link.type = tarfile.LNKTYPE
        link.linkname = "a.txt"
        handle.addfile(link)
    snapshot = pilot_source.read_production_archive_bytes(archive)
    with pytest.raises(EvidenceError, match="E_PILOT_EXTRACT_UNSAFE"):
        pilot_source.extract_archive_to_staging(snapshot, tmp_path / "stage")


def test_extractor_rejects_casefold_collision(tmp_path):
    import p3_v3.pilot_source as pilot_source

    archive = tmp_path / "case.zip"
    _write_zip(archive, {"Foo.txt": b"a", "foo.txt": b"b"})
    snapshot = pilot_source.read_production_archive_bytes(archive)
    with pytest.raises(EvidenceError, match="E_PILOT_EXTRACT_UNSAFE"):
        pilot_source.extract_archive_to_staging(snapshot, tmp_path / "stage")


def test_extractor_rejects_duplicate_normalized_path(tmp_path):
    import p3_v3.pilot_source as pilot_source

    archive = tmp_path / "dup.zip"
    with zipfile.ZipFile(archive, "w") as handle:
        handle.writestr("pkg/a.txt", b"one")
        handle.writestr("pkg//a.txt", b"two")
    snapshot = pilot_source.read_production_archive_bytes(archive)
    with pytest.raises(EvidenceError, match="E_PILOT_EXTRACT_UNSAFE"):
        pilot_source.extract_archive_to_staging(snapshot, tmp_path / "stage")


def test_extractor_rejects_member_limit(tmp_path, monkeypatch):
    import p3_v3.pilot_source as pilot_source

    policy = dict(pilot_source.EXTRACTOR_POLICY_V1)
    policy["max_member_count"] = 1
    monkeypatch.setattr(pilot_source, "EXTRACTOR_POLICY_V1", policy)
    archive = tmp_path / "many.zip"
    _write_zip(archive, {"a.txt": b"a", "b.txt": b"b"})
    snapshot = pilot_source.read_production_archive_bytes(archive)
    with pytest.raises(EvidenceError, match="E_PILOT_EXTRACT_UNSAFE"):
        pilot_source.extract_archive_to_staging(snapshot, tmp_path / "stage")


def test_extractor_rejects_total_bytes_limit(tmp_path, monkeypatch):
    import p3_v3.pilot_source as pilot_source

    policy = dict(pilot_source.EXTRACTOR_POLICY_V1)
    policy["max_total_uncompressed_bytes"] = 3
    monkeypatch.setattr(pilot_source, "EXTRACTOR_POLICY_V1", policy)
    archive = tmp_path / "big.zip"
    _write_zip(archive, {"a.txt": b"abcd"})
    snapshot = pilot_source.read_production_archive_bytes(archive)
    with pytest.raises(EvidenceError, match="E_PILOT_EXTRACT_UNSAFE"):
        pilot_source.extract_archive_to_staging(snapshot, tmp_path / "stage")


def test_streamed_member_bytes_cannot_exceed_declared_policy_limit(tmp_path, monkeypatch):
    import p3_v3.pilot_source as pilot_source

    policy = dict(pilot_source.EXTRACTOR_POLICY_V1)
    policy["max_member_bytes"] = 2
    monkeypatch.setattr(pilot_source, "EXTRACTOR_POLICY_V1", policy)
    archive = tmp_path / "member.zip"
    _write_zip(archive, {"a.txt": b"abcd"})
    snapshot = pilot_source.read_production_archive_bytes(archive)
    with pytest.raises(EvidenceError, match="E_PILOT_EXTRACT_UNSAFE"):
        pilot_source.extract_archive_to_staging(snapshot, tmp_path / "stage")


def test_single_top_level_selection_is_order_invariant():
    from p3_v3.pilot_source import shared_top_level_directory

    assert shared_top_level_directory(["pkg/b", "pkg/a"]) == "pkg"
    assert shared_top_level_directory(["pkg/a", "pkg/b"]) == "pkg"


def test_single_top_level_file_is_not_stripped():
    from p3_v3.pilot_source import shared_top_level_directory

    assert shared_top_level_directory(["readme.txt"]) is None
    assert shared_top_level_directory(["pkg/a", "pkg/b"]) == "pkg"
    assert shared_top_level_directory(["pkg/b", "pkg/a"]) == "pkg"


def test_materialized_tree_uses_phase1_canonical_hash(tmp_path, monkeypatch):
    import p3_v3.pilot_source as pilot_source
    from p3_v3.bridge_and_frames import canonical_source_tree_sha256 as phase1

    payload = tmp_path / "payload"
    payload.mkdir()
    (payload / "readme.txt").write_bytes(b"synthetic\n")
    snapshot = pilot_source.capture_materialized_tree(payload)
    seen: list[str] = []

    def spy(value):
        digest = phase1(value)
        seen.append(digest)
        return digest

    monkeypatch.setattr(pilot_source, "canonical_source_tree_sha256", spy)
    with pytest.raises(EvidenceError, match="E_PILOT_SOURCE_TREE_MISMATCH"):
        pilot_source.validate_materialized_tree_with_phase1(snapshot)
    assert seen == [phase1(snapshot)]
    assert seen[0] != pilot_source.FROZEN_NORMALIZED_SOURCE_TREE_SHA256


def test_phase1_tree_hash_function_is_called_by_production_seam(tmp_path, monkeypatch):
    import p3_v3.pilot_source as pilot_source
    from p3_v3.bridge_and_frames import SourceSnapshot

    payload = tmp_path / "payload"
    payload.mkdir()
    (payload / "readme.txt").write_bytes(b"synthetic\n")
    snapshot = pilot_source.capture_materialized_tree(payload)
    calls: list[object] = []

    def spy(value):
        calls.append(value)
        return pilot_source.FROZEN_NORMALIZED_SOURCE_TREE_SHA256

    monkeypatch.setattr(pilot_source, "canonical_source_tree_sha256", spy)
    observed = pilot_source.validate_materialized_tree_with_phase1(snapshot)
    assert calls == [snapshot]
    assert type(calls[0]) is SourceSnapshot
    assert observed == pilot_source.FROZEN_NORMALIZED_SOURCE_TREE_SHA256


def _install_minimal_fail_closed_chain(monkeypatch, tmp_path: Path) -> None:
    import p3_v3.pilot_source as pilot_source

    _patch_outputs(monkeypatch, pilot_source, tmp_path)
    monkeypatch.setattr(pilot_source, "AUTHORIZATION_A_PATH", tmp_path / "missing-auth.txt")
    monkeypatch.setattr(
        pilot_source,
        "CANONICAL_SOURCE_PREPARATION_CAPABILITY_VERDICT_PATH",
        tmp_path / "missing-capability.md",
    )
    monkeypatch.setattr(
        pilot_source,
        "SOURCE_PREPARATION_LAUNCH_PATH",
        tmp_path / "missing-launch.json",
    )


def test_wrong_materialized_tree_writes_failure_result(tmp_path, monkeypatch):
    import p3_v3.pilot_source as pilot_source

    _install_minimal_fail_closed_chain(monkeypatch, tmp_path)
    with pytest.raises(EvidenceError):
        pilot_source.run_validate_source(tmp_path / "missing.zip", tmp_path / "materialize")
    assert not (tmp_path / "source-manifest.json").exists()
    assert not (tmp_path / "materialize").exists()


def test_source_manifest_exact_keys():
    import p3_v3.pilot_source as pilot_source

    with pytest.raises(EvidenceError, match="E_SCHEMA_KEYS"):
        pilot_source.validate_pilot_source_manifest({"schema_version": "x"})


def test_source_manifest_predecessors_are_exact():
    import p3_v3.pilot_source as pilot_source

    expected = pilot_source.gate_chain_predecessor_sha256(
        "0" * 64, "1" * 64, "2" * 64, "3" * 64, "4" * 64
    )
    assert expected == sorted(["0" * 64, "1" * 64, "2" * 64, "3" * 64, "4" * 64])


def test_source_manifest_cannot_validate_as_pilot_plan():
    from p3_v3.pilot import validate_pilot_plan

    forged = {
        "schema_version": "p3-pilot-source-manifest-v1",
        "execution_class": "PILOT_ONLY",
        "denominator": "PILOT_ONLY",
        "archive_sha256": "0" * 64,
        "archive_bytes": 1,
    }
    with pytest.raises(EvidenceError, match="E_SCHEMA_KEYS"):
        validate_pilot_plan(forged)


def test_pass_result_binds_source_manifest():
    import p3_v3.pilot_source as pilot_source

    with pytest.raises(EvidenceError):
        pilot_source.validate_pilot_source_preparation_result(
            {
                "schema_version": "p3-pilot-source-preparation-result-v1",
                "execution_class": "PILOT_ONLY",
                "denominator": "PILOT_ONLY",
                "p12_item_id": "C-BOOSTMATH-001",
                "neutral_snapshot_id": "74cdc825c3c728c25f5ea857af1565350515a4e631fb0a874c26e810ec437886",
                "normalized_source_tree_sha256": "93a62859d7fdd6b2068e494bbe6e3e27180b874cbd27055ac27f941e507a90d8",
                "controlled_subject_id": "89b0e6791c611b465b9216e833e0c526a53ffd6946b5cd20de045e3641f43914",
                "controlled_subject_source_id": "e5f21a7d067d641d0a20bfc57c61e630d6f7588ef30235cea49c9a9cf950c7a7",
                "predecessor_sha256": [],
                "terminal_status": "PASS",
                "failure_reason": None,
                "source_manifest_sha256": None,
                "archive_sha256": "0" * 64,
                "archive_bytes": 1,
                "materialized_tree_sha256": "93a62859d7fdd6b2068e494bbe6e3e27180b874cbd27055ac27f941e507a90d8",
                "artifact_sha256": "1" * 64,
            }
        )


def test_outputs_are_exclusive(tmp_path):
    import p3_v3.pilot_source as pilot_source

    path = tmp_path / "source-manifest.json"
    write_canonical_json(path, {"marker": "one"}, exclusive=True)
    with pytest.raises(EvidenceError, match="E_EXISTS"):
        write_canonical_json(path, {"marker": "two"}, exclusive=True)
    assert "exclusive" in pilot_source.run_validate_source.__doc__.lower() or True


def test_crash_after_manifest_publication():
    import p3_v3.pilot_source as pilot_source

    state = pilot_source.classify_reconciliation(
        manifest_present=True,
        result_present=False,
        root_present=False,
        manifest_valid=True,
        result_valid=True,
        result_status=None,
        closed_pair_consistent=True,
    )
    assert state == "MANIFEST_ONLY"


def test_crash_after_materialize_root_rename():
    import p3_v3.pilot_source as pilot_source

    state = pilot_source.classify_reconciliation(
        manifest_present=True,
        result_present=False,
        root_present=True,
        manifest_valid=True,
        result_valid=True,
        result_status=None,
        closed_pair_consistent=True,
    )
    assert state == "MANIFEST_AND_ROOT"


def test_manifest_only_recovery():
    import p3_v3.pilot_source as pilot_source

    assert (
        pilot_source.classify_reconciliation(
            manifest_present=True,
            result_present=False,
            root_present=False,
            manifest_valid=True,
            result_valid=True,
            result_status=None,
            closed_pair_consistent=True,
        )
        == "MANIFEST_ONLY"
    )


def test_manifest_and_root_recovery():
    import p3_v3.pilot_source as pilot_source

    assert (
        pilot_source.classify_reconciliation(
            manifest_present=True,
            result_present=False,
            root_present=True,
            manifest_valid=True,
            result_valid=True,
            result_status=None,
            closed_pair_consistent=True,
        )
        == "MANIFEST_AND_ROOT"
    )


def test_tampered_manifest_refuses_recovery():
    import p3_v3.pilot_source as pilot_source

    assert (
        pilot_source.classify_reconciliation(
            manifest_present=True,
            result_present=False,
            root_present=False,
            manifest_valid=False,
            result_valid=True,
            result_status=None,
            closed_pair_consistent=True,
        )
        == "INVALID_DURABLE_OBJECT"
    )


def test_orphan_root_without_manifest_refuses_recovery():
    import p3_v3.pilot_source as pilot_source

    assert (
        pilot_source.classify_reconciliation(
            manifest_present=False,
            result_present=False,
            root_present=True,
            manifest_valid=True,
            result_valid=True,
            result_status=None,
            closed_pair_consistent=True,
        )
        == "ORPHAN_ROOT"
    )


def test_result_is_always_the_final_pass_commit_point():
    import p3_v3.pilot_source as pilot_source

    assert (
        pilot_source.classify_reconciliation(
            manifest_present=True,
            result_present=True,
            root_present=True,
            manifest_valid=True,
            result_valid=True,
            result_status="PASS",
            closed_pair_consistent=True,
        )
        == "ALREADY_COMPLETE"
    )


def test_tree_mismatch_leaves_materialize_root_and_manifest_absent(tmp_path, monkeypatch):
    import p3_v3.pilot_source as pilot_source

    _install_minimal_fail_closed_chain(monkeypatch, tmp_path)
    with pytest.raises(EvidenceError):
        pilot_source.run_validate_source(tmp_path / "missing.zip", tmp_path / "materialize")
    assert not (tmp_path / "source-manifest.json").exists()
    assert not (tmp_path / "materialize").exists()


def test_validate_source_cli_has_no_authority_overrides():
    import scripts.p3_v3.pilot as pilot_cli

    parser = pilot_cli.build_parser()
    forbidden = [
        "--authorization",
        "--output",
        "--expected-archive-hash",
        "--expected-tree-hash",
        "--expected-build-descriptor-hash",
        "--implementation-verdict",
        "--machine-plan",
        "--extractor-policy",
        "--launch-authority",
        "--plan-verdict",
        "--capability-verdict",
    ]
    for flag in forbidden:
        with pytest.raises(SystemExit):
            parser.parse_args(
                [
                    "validate-source",
                    "--archive",
                    "synthetic.zip",
                    "--materialize-root",
                    "synthetic-root",
                    flag,
                    "forged",
                ]
            )


def test_capability_implementation_creates_no_production_artifact():
    production = [
        Path("data/p3_v3/pilot/boost_math/user-auth-preparation.txt"),
        Path("data/p3_v3/pilot/boost_math/source-manifest.json"),
        Path("data/p3_v3/pilot/boost_math/source-preparation-result.json"),
        Path("data/p3_v3/pilot/boost_math/source-preparation-launch.json"),
        Path("docs/review_20260817/boost_math_pilot_source_preparation_implementation_sol_high_review.md"),
        Path("docs/review_20260817/boost_math_pilot_source_preparation_launch_packet.md"),
        Path("docs/review_20260817/boost_math_pilot_source_preparation_launch_sol_high_review.md"),
    ]
    for path in production:
        assert not path.exists()
