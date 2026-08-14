from __future__ import annotations

import hashlib
import io
import tarfile

import pytest

from p3_v3.artifacts import EvidenceError
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
