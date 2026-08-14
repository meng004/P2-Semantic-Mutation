from __future__ import annotations

import gzip
import hashlib
import json
import shutil
from pathlib import Path

import pytest

from p3_v3.artifacts import EvidenceError, canonical_json_bytes, canonical_sha256
import scripts.p3_v3.continue_phase1_frames_after_size_gate as continuation


NINETY_MIB = 90 * 1024 * 1024
ONE_TWENTY_EIGHT_MIB = 128 * 1024 * 1024


def _canonical_object(body: dict) -> dict:
    return {**body, "artifact_sha256": canonical_sha256(body)}


def _write_canonical(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_json_bytes(value))


def test_ordinary_root_file_at_90_mib_is_accepted():
    continuation.assert_artifact_size("derived-subject.json", NINETY_MIB)


def test_ordinary_root_file_over_90_mib_is_rejected():
    with pytest.raises(EvidenceError, match="E_ARTIFACT_SIZE"):
        continuation.assert_artifact_size("derived-subject.json", NINETY_MIB + 1)


def test_root_subject_frames_at_128_mib_is_accepted():
    continuation.assert_artifact_size("subject-frames.json", ONE_TWENTY_EIGHT_MIB)


def test_root_subject_frames_over_128_mib_is_rejected():
    with pytest.raises(EvidenceError, match="E_ARTIFACT_SIZE"):
        continuation.assert_artifact_size("subject-frames.json", ONE_TWENTY_EIGHT_MIB + 1)


def test_nested_subject_frames_does_not_receive_exception():
    with pytest.raises(EvidenceError, match="E_ARTIFACT_SIZE"):
        continuation.assert_artifact_size(
            "nested/subject-frames.json", NINETY_MIB + 1
        )


@pytest.mark.parametrize(
    "relative_path",
    [
        "subject-frames.json.bak",
        "subject-frames.json.gz",
        "../subject-frames.json",
        "./subject-frames.json",
        "subject-frames.json/extra",
    ],
)
def test_similar_or_traversing_paths_do_not_receive_exception(relative_path):
    with pytest.raises(EvidenceError, match="E_ARTIFACT_SIZE"):
        continuation.assert_artifact_size(relative_path, NINETY_MIB + 1)


def _tiny_pass1(tmp_path: Path) -> tuple[Path, dict, dict]:
    output_root = tmp_path / "out"
    output_root.mkdir()
    frames = _canonical_object(
        {
            "schema_version": "p3-subject-frames-v1",
            "subjects": [{"primary_technique": "TECH_UNCERTAIN"}],
        }
    )
    other = _canonical_object({"schema_version": "p3-tiny-v1", "rows": [0, 1]})
    _write_canonical(output_root / "subject-frames.json", frames)
    _write_canonical(output_root / "other.json", other)
    files = continuation.inventory_regular_files(output_root)
    baseline = {"files": files}
    return output_root, baseline, frames


def test_continuation_rejects_missing_pass1_file(tmp_path):
    output_root, baseline, _frames = _tiny_pass1(tmp_path)
    (output_root / "other.json").unlink()
    with pytest.raises(EvidenceError, match="E_PASS1_BASELINE"):
        continuation.validate_pass1_outputs(output_root, baseline)


def test_continuation_rejects_extra_pass1_file(tmp_path):
    output_root, baseline, _frames = _tiny_pass1(tmp_path)
    _write_canonical(
        output_root / "extra.json",
        _canonical_object({"schema_version": "p3-tiny-v1"}),
    )
    with pytest.raises(EvidenceError, match="E_PASS1_BASELINE"):
        continuation.validate_pass1_outputs(output_root, baseline)


def test_continuation_rejects_noncanonical_json(tmp_path):
    output_root, baseline, _frames = _tiny_pass1(tmp_path)
    (output_root / "other.json").write_text('{"schema_version": "p3-tiny-v1"}\n')
    with pytest.raises(EvidenceError, match="E_NONCANONICAL_JSON"):
        continuation.validate_pass1_outputs(output_root, baseline)


def test_continuation_rejects_wrong_top_level_self_hash(tmp_path):
    output_root, baseline, _frames = _tiny_pass1(tmp_path)
    broken = json.loads((output_root / "other.json").read_text())
    broken["artifact_sha256"] = "0" * 64
    (output_root / "other.json").write_bytes(canonical_json_bytes(broken))
    with pytest.raises(EvidenceError, match="E_ARTIFACT_SELF_HASH"):
        continuation.validate_pass1_outputs(output_root, baseline)


def test_shuffle_file_set_mismatch_is_rejected(tmp_path):
    left = tmp_path / "left"
    right = tmp_path / "right"
    left.mkdir()
    right.mkdir()
    _write_canonical(left / "a.json", _canonical_object({"k": 1}))
    _write_canonical(right / "b.json", _canonical_object({"k": 1}))
    with pytest.raises(EvidenceError, match="E_SHUFFLE_IDENTITY"):
        continuation.compare_output_identity(left, right)


def test_shuffle_raw_sha256_mismatch_is_rejected(tmp_path):
    left = tmp_path / "left"
    right = tmp_path / "right"
    left.mkdir()
    right.mkdir()
    _write_canonical(left / "a.json", _canonical_object({"k": 1}))
    _write_canonical(right / "a.json", _canonical_object({"k": 2}))
    with pytest.raises(EvidenceError, match="E_SHUFFLE_IDENTITY"):
        continuation.compare_output_identity(left, right)


def test_gzip_payload_mismatch_is_rejected(tmp_path):
    raw = tmp_path / "subject-frames.json"
    gz_path = tmp_path / "subject-frames.json.gz"
    payload = _canonical_object({"schema_version": "p3-subject-frames-v1"})
    raw.write_bytes(canonical_json_bytes(payload))
    other = canonical_json_bytes(_canonical_object({"schema_version": "other"}))
    gz_path.write_bytes(gzip.compress(other, mtime=0))
    with pytest.raises(EvidenceError, match="E_GZIP_IDENTITY"):
        continuation.validate_gzip_transport(gz_path, raw)


def test_gzip_raw_hash_mismatch_is_rejected(tmp_path):
    raw = tmp_path / "subject-frames.json"
    gz_path = tmp_path / "subject-frames.json.gz"
    payload = _canonical_object({"schema_version": "p3-subject-frames-v1"})
    raw.write_bytes(canonical_json_bytes(payload))
    continuation.write_gzip_transport(raw, gz_path)
    with pytest.raises(EvidenceError, match="E_GZIP_IDENTITY"):
        continuation.validate_gzip_transport(gz_path, raw, expected_raw_sha256="0" * 64)


def test_gzip_decompressed_noncanonical_json_is_rejected(tmp_path):
    raw = tmp_path / "subject-frames.json"
    gz_path = tmp_path / "subject-frames.json.gz"
    noncanonical = b'{"schema_version": "v1"}\n'
    raw.write_bytes(noncanonical)
    gz_path.write_bytes(gzip.compress(noncanonical, mtime=0))
    with pytest.raises(EvidenceError, match="E_NONCANONICAL_JSON"):
        continuation.validate_gzip_transport(gz_path, raw)


def test_gzip_decompressed_self_hash_mismatch_is_rejected(tmp_path):
    raw = tmp_path / "subject-frames.json"
    gz_path = tmp_path / "subject-frames.json.gz"
    broken = {
        "schema_version": "p3-subject-frames-v1",
        "artifact_sha256": "1" * 64,
    }
    raw_bytes = canonical_json_bytes(broken)
    raw.write_bytes(raw_bytes)
    gz_path.write_bytes(gzip.compress(raw_bytes, mtime=0))
    with pytest.raises(EvidenceError, match="E_ARTIFACT_SELF_HASH"):
        continuation.validate_gzip_transport(gz_path, raw)


def test_tiny_fixture_continuation_succeeds(tmp_path):
    production_root, baseline, _frames = _tiny_pass1(tmp_path)
    specs = [{"neutral_snapshot_id": "11" * 32}]

    def run_build_frames(specs_path: Path, output_root: Path):
        if output_root.exists():
            shutil.rmtree(output_root)
        shutil.copytree(production_root, output_root)
        return {"status": "PASS", "subject_count": 1, "common_input_count": 30}

    result = continuation.continue_from_pass1(
        production_root=production_root,
        baseline=baseline,
        specs=specs,
        run_build_frames=run_build_frames,
        gzip_destination=production_root / "subject-frames.json.gz",
    )
    assert result["status"] == "PASS"
    assert result["shuffle_byte_identical"] is True
    assert (production_root / "subject-frames.json.gz").is_file()
    continuation.validate_gzip_transport(
        production_root / "subject-frames.json.gz",
        production_root / "subject-frames.json",
    )


def test_raw_subject_frames_path_is_gitignored():
    repo = Path(__file__).resolve().parents[2]
    import subprocess

    ignored = subprocess.run(
        [
            "git",
            "check-ignore",
            "-q",
            "data/p3_v3/phase1_frames/out/subject-frames.json",
        ],
        cwd=repo,
        check=False,
    )
    kept = subprocess.run(
        [
            "git",
            "check-ignore",
            "-q",
            "data/p3_v3/phase1_frames/out/other.json",
        ],
        cwd=repo,
        check=False,
    )
    assert ignored.returncode == 0
    assert kept.returncode == 1
