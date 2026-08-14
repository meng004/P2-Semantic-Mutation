from __future__ import annotations

import hashlib
import io
import subprocess
import sys
import tarfile
from pathlib import Path

import pytest

from p3_v3.artifacts import EvidenceError
from p3_v3.bridge_and_frames import canonical_source_tree_sha256
import scripts.p3_v3.build_phase1_frames as driver_module
import scripts.p3_v3.evidence as evidence_cli
from scripts.p3_v3.build_phase1_frames import (
    assert_exact_coverage,
    extract_archive,
)


def _write_tar(path, member: tarfile.TarInfo, payload: bytes = b"") -> str:
    with tarfile.open(path, "w") as archive:
        archive.addfile(member, io.BytesIO(payload) if payload else None)
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_extract_archive_rejects_symlink_member(tmp_path):
    archive_path = tmp_path / "subject.tar"
    member = tarfile.TarInfo("escape")
    member.type = tarfile.SYMTYPE
    member.linkname = "../outside"
    archive_sha256 = _write_tar(archive_path, member)

    with pytest.raises(EvidenceError, match="E_ARCHIVE_SYMLINK"):
        extract_archive(archive_path, tmp_path / "extracted", archive_sha256)


def test_extract_archive_rejects_sha256_mismatch_before_extraction(tmp_path):
    archive_path = tmp_path / "subject.tar"
    payload = b"int main(void) { return 0; }\n"
    member = tarfile.TarInfo("main.c")
    member.size = len(payload)
    _write_tar(archive_path, member, payload)
    destination = tmp_path / "extracted"

    with pytest.raises(EvidenceError, match="E_ARCHIVE_HASH"):
        extract_archive(archive_path, destination, "0" * 64)

    assert not destination.exists()


@pytest.mark.parametrize(
    "spec_ids",
    [
        ["11" * 32],
        ["11" * 32, "11" * 32],
        ["11" * 32, "22" * 32, "33" * 32],
    ],
    ids=["missing", "duplicate", "extra"],
)
def test_assert_exact_coverage_rejects_non_bijective_specs(spec_ids):
    bridge_records = [
        {"neutral_snapshot_id": "11" * 32},
        {"neutral_snapshot_id": "22" * 32},
    ]
    subject_specs = [
        {"neutral_snapshot_id": neutral_snapshot_id}
        for neutral_snapshot_id in spec_ids
    ]

    with pytest.raises(EvidenceError, match="E_SUBJECT_SPEC_COVERAGE"):
        assert_exact_coverage(bridge_records, subject_specs)


def test_assert_exact_coverage_accepts_one_spec_per_bridge_record():
    bridge_records = [
        {"neutral_snapshot_id": "11" * 32},
        {"neutral_snapshot_id": "22" * 32},
    ]
    subject_specs = [
        {"neutral_snapshot_id": "22" * 32},
        {"neutral_snapshot_id": "11" * 32},
    ]

    assert_exact_coverage(bridge_records, subject_specs)


def test_driver_module_loads_by_file_path_outside_repository(tmp_path):
    script_path = driver_module.__file__
    command = [
        sys.executable,
        "-c",
        (
            "import runpy; "
            f"runpy.run_path({script_path!r}, run_name='phase1_import_check')"
        ),
    ]

    completed = subprocess.run(
        command, cwd=tmp_path, text=True, capture_output=True, check=False
    )

    assert completed.returncode == 0, completed.stderr


def _tiny_archive(tmp_path, payload: bytes = b"int main(void) { return 0; }\n"):
    archive_path = tmp_path / "subject.tar"
    member = tarfile.TarInfo("main.c")
    member.size = len(payload)
    member.mode = 0o644
    archive_sha256 = _write_tar(archive_path, member, payload)
    return archive_path, archive_sha256, payload


def _captured_tree_sha256(destination: Path) -> str:
    _manifest, snapshot = evidence_cli._capture_tracked_source_manifest(
        destination, ["."], "subject-source"
    )
    return canonical_source_tree_sha256(snapshot)


def test_ensure_extracted_source_reuses_matching_tree(tmp_path):
    archive_path, archive_sha256, payload = _tiny_archive(tmp_path)
    destination = tmp_path / "extracted"
    extract_archive(archive_path, destination, archive_sha256)
    tree_sha256 = _captured_tree_sha256(destination)
    marker = destination / "main.c"
    marker.chmod(0o600)

    source_root, snapshot, action = driver_module.ensure_extracted_source(
        archive_path,
        destination,
        archive_sha256,
        tree_sha256,
    )

    assert action == "reused"
    assert source_root == destination
    assert canonical_source_tree_sha256(snapshot) == tree_sha256
    assert marker.read_bytes() == payload
    assert marker.stat().st_mode & 0o777 == 0o600


def test_ensure_extracted_source_reextracts_when_tree_hash_differs(tmp_path):
    archive_path, archive_sha256, payload = _tiny_archive(tmp_path)
    destination = tmp_path / "extracted"
    extract_archive(archive_path, destination, archive_sha256)
    tree_sha256 = _captured_tree_sha256(destination)
    (destination / "main.c").write_bytes(b"corrupted\n")

    source_root, snapshot, action = driver_module.ensure_extracted_source(
        archive_path,
        destination,
        archive_sha256,
        tree_sha256,
    )

    assert action == "extracted"
    assert source_root == destination
    assert (destination / "main.c").read_bytes() == payload
    assert canonical_source_tree_sha256(snapshot) == tree_sha256


def test_ensure_extracted_source_rejects_archive_hash_before_reuse(tmp_path):
    archive_path, archive_sha256, _payload = _tiny_archive(tmp_path)
    destination = tmp_path / "extracted"
    extract_archive(archive_path, destination, archive_sha256)
    tree_sha256 = _captured_tree_sha256(destination)
    (destination / "main.c").chmod(0o600)

    with pytest.raises(EvidenceError, match="E_ARCHIVE_HASH"):
        driver_module.ensure_extracted_source(
            archive_path,
            destination,
            "0" * 64,
            tree_sha256,
        )

    assert destination.exists()
    assert (destination / "main.c").stat().st_mode & 0o777 == 0o600


def test_emit_progress_writes_stderr_only(capsys):
    driver_module.emit_progress(
        index=8,
        total=35,
        neutral_snapshot_id="ab" * 32,
        stage="source captured",
        elapsed_s=12.5,
    )
    captured = capsys.readouterr()

    assert captured.out == ""
    assert "8/35" in captured.err
    assert "source captured" in captured.err
    assert ("ab" * 32) in captured.err


def test_subject_checkpoint_roundtrip_rebinds_all_hashes(tmp_path):
    binding = driver_module.checkpoint_binding(
        neutral_snapshot_id="11" * 32,
        source_archive_sha256="22" * 32,
        build_descriptor_sha256="33" * 32,
        canonical_source_tree_sha256="44" * 32,
        adapter_registry_sha256="55" * 32,
        input_generator_registry_sha256="66" * 32,
        runner_implementation_sha256="77" * 32,
    )
    spec = {"neutral_snapshot_id": "11" * 32, "source_root": "extracted/subject"}
    summary = {
        "neutral_snapshot_id": "11" * 32,
        "discovery_status": "EXECUTABLE",
        "scale_class": "S",
        "selected_row_count": 0,
    }
    path = tmp_path / "checkpoint" / f"{'11' * 32}.json"
    driver_module.save_subject_checkpoint(path, binding, spec, summary)

    loaded = driver_module.load_subject_checkpoint(path, binding)
    assert loaded == {"spec": spec, "summary": summary}

    mismatch = dict(binding)
    mismatch["runner_implementation_sha256"] = "88" * 32
    assert driver_module.load_subject_checkpoint(path, mismatch) is None

    archive_mismatch = dict(binding)
    archive_mismatch["source_archive_sha256"] = "99" * 32
    assert driver_module.load_subject_checkpoint(path, archive_mismatch) is None


def test_phase1_checkpoint_path_is_gitignored():
    repo = Path(__file__).resolve().parents[2]
    completed = subprocess.run(
        [
            "git",
            "check-ignore",
            "-q",
            "data/p3_v3/phase1_frames/checkpoint/dummy.json",
        ],
        cwd=repo,
        check=False,
    )

    assert completed.returncode == 0
