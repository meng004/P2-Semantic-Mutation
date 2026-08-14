#!/usr/bin/env python3
"""CA-01 continuation: size-gate amendment + shuffle pass 2 only."""

from __future__ import annotations

import gzip as gzip_module
import hashlib
import json
import os
import random
import shutil
import stat
import subprocess
import sys
import tempfile
import time
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from p3_v3.artifacts import (  # noqa: E402
    EvidenceError,
    canonical_json_bytes,
    canonical_sha256,
    file_sha256,
    read_canonical_json,
    write_canonical_json,
)
from scripts.p3_v3.build_phase1_frames import (  # noqa: E402
    INPUT_ROOT,
    OUTPUT_ROOT,
    _run_build_frames,
    emit_progress,
)

FRAME_ROOT = ROOT / "data/p3_v3/phase1_frames"
BASELINE_PATH = FRAME_ROOT / "pass1_baseline_manifest.json"
MAX_ORDINARY_BYTES = 90 * 1024 * 1024
MAX_SUBJECT_FRAMES_BYTES = 128 * 1024 * 1024
ROOT_SUBJECT_FRAMES = "subject-frames.json"
TRANSPORT_GZIP = "subject-frames.json.gz"


def artifact_size_limit(relative_path: str) -> int:
    if relative_path == ROOT_SUBJECT_FRAMES:
        return MAX_SUBJECT_FRAMES_BYTES
    return MAX_ORDINARY_BYTES


def assert_artifact_size(relative_path: str, size_bytes: int) -> None:
    limit = artifact_size_limit(relative_path)
    if size_bytes > limit:
        raise EvidenceError(
            "E_ARTIFACT_SIZE",
            f"artifact exceeds {limit} bytes: {relative_path}",
        )


def _relative_posix(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def inventory_regular_files(output_root: Path) -> list[dict[str, Any]]:
    output_root = Path(output_root)
    rows: list[dict[str, Any]] = []
    for dirpath, dirnames, filenames in os.walk(output_root, followlinks=False):
        dirnames.sort()
        for name in sorted(filenames):
            path = Path(dirpath) / name
            relative = _relative_posix(path, output_root)
            if relative == TRANSPORT_GZIP:
                continue
            info = path.lstat()
            if stat.S_ISLNK(info.st_mode):
                raise EvidenceError("E_PASS1_BASELINE", f"symlink is forbidden: {relative}")
            if not stat.S_ISREG(info.st_mode):
                raise EvidenceError(
                    "E_PASS1_BASELINE", f"artifact is not a regular file: {relative}"
                )
            rows.append(
                {
                    "path": relative,
                    "size_bytes": info.st_size,
                    "sha256": file_sha256(path),
                }
            )
    rows.sort(key=lambda row: row["path"].encode("utf-8"))
    return rows


def _baseline_relative(path_value: str) -> str:
    posix = Path(path_value).as_posix()
    marker = "/phase1_frames/out/"
    if marker in posix:
        return posix.split(marker, 1)[1]
    return posix


def validate_json_bytes(raw: bytes, context: str) -> Any:
    try:
        value = json.loads(
            raw.decode("utf-8"),
            parse_constant=lambda token: (_ for _ in ()).throw(ValueError(token)),
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise EvidenceError("E_JSON", f"invalid JSON: {context}") from exc
    if canonical_json_bytes(value) != raw:
        raise EvidenceError("E_NONCANONICAL_JSON", f"noncanonical JSON bytes: {context}")
    if isinstance(value, dict) and "artifact_sha256" in value:
        body = {key: item for key, item in value.items() if key != "artifact_sha256"}
        observed = canonical_sha256(body)
        if observed != value["artifact_sha256"]:
            raise EvidenceError(
                "E_ARTIFACT_SELF_HASH",
                f"artifact self-hash differs: {context}",
            )
    return value


def validate_pass1_outputs(output_root: Path, baseline: Mapping[str, Any]) -> None:
    output_root = Path(output_root)
    observed_rows = inventory_regular_files(output_root)
    for row in observed_rows:
        assert_artifact_size(row["path"], row["size_bytes"])
        validate_json_bytes((output_root / row["path"]).read_bytes(), row["path"])
    expected_rows = baseline.get("files")
    if not isinstance(expected_rows, list):
        raise EvidenceError("E_PASS1_BASELINE", "baseline files are absent")
    expected = {_baseline_relative(row["path"]): row for row in expected_rows}
    observed = {row["path"]: row for row in observed_rows}
    if set(observed) != set(expected):
        raise EvidenceError(
            "E_PASS1_BASELINE",
            "pass 1 file set differs from the frozen baseline",
        )
    for relative, expected_row in expected.items():
        observed_row = observed[relative]
        if (
            observed_row["size_bytes"] != expected_row["size_bytes"]
            or observed_row["sha256"] != expected_row["sha256"]
        ):
            raise EvidenceError(
                "E_PASS1_BASELINE",
                f"pass 1 artifact bytes differ: {relative}",
            )


def compare_output_identity(left_root: Path, right_root: Path) -> None:
    left_rows = inventory_regular_files(left_root)
    right_rows = inventory_regular_files(right_root)
    for row in left_rows + right_rows:
        assert_artifact_size(row["path"], row["size_bytes"])
    left = {row["path"]: row["sha256"] for row in left_rows}
    right = {row["path"]: row["sha256"] for row in right_rows}
    if set(left) != set(right):
        raise EvidenceError(
            "E_SHUFFLE_IDENTITY",
            "shuffled frame regeneration file set differs",
        )
    for relative, digest in left.items():
        if right[relative] != digest:
            raise EvidenceError(
                "E_SHUFFLE_IDENTITY",
                f"shuffled frame regeneration differs by bytes: {relative}",
            )


def gzip_implementation() -> str:
    completed = subprocess.run(
        ["gzip", "--version"],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    line = (completed.stdout or "").splitlines()[0].strip() if completed.stdout else ""
    return line or "gzip"


def write_gzip_transport(raw_path: Path, gz_path: Path) -> dict[str, Any]:
    raw_path = Path(raw_path)
    gz_path = Path(gz_path)
    if gz_path.exists():
        if gz_path.is_symlink() or not gz_path.is_file():
            raise EvidenceError("E_GZIP_TRANSPORT", "gzip destination is unsafe")
        gz_path.unlink()
    temporary = gz_path.with_name(gz_path.name + ".tmp")
    if temporary.exists():
        temporary.unlink()
    with raw_path.open("rb") as source, temporary.open("wb") as destination:
        completed = subprocess.run(
            ["gzip", "-n", "-9", "-c"],
            stdin=source,
            stdout=destination,
            check=False,
        )
    if completed.returncode != 0:
        temporary.unlink(missing_ok=True)
        raise EvidenceError("E_GZIP_TRANSPORT", "gzip -n -9 failed")
    os.replace(temporary, gz_path)
    return {
        "command": ["gzip", "-n", "-9", "-c"],
        "implementation": gzip_implementation(),
        "compressed_size_bytes": gz_path.stat().st_size,
        "compressed_sha256": file_sha256(gz_path),
    }


def validate_gzip_transport(
    gz_path: Path,
    raw_path: Path,
    expected_raw_sha256: str | None = None,
) -> dict[str, Any]:
    gz_path = Path(gz_path)
    raw_path = Path(raw_path)
    raw = raw_path.read_bytes()
    try:
        decompressed = gzip_module.decompress(gz_path.read_bytes())
    except OSError as exc:
        raise EvidenceError("E_GZIP_IDENTITY", "gzip payload is unreadable") from exc
    if decompressed != raw:
        raise EvidenceError(
            "E_GZIP_IDENTITY",
            "decompressed gzip bytes differ from raw subject-frames.json",
        )
    raw_digest = hashlib.sha256(raw).hexdigest()
    if expected_raw_sha256 is not None and raw_digest != expected_raw_sha256:
        raise EvidenceError(
            "E_GZIP_IDENTITY",
            "raw subject-frames sha256 differs from the expected scientific hash",
        )
    validate_json_bytes(decompressed, gz_path.name)
    return {
        "raw_sha256": raw_digest,
        "decompression_byte_identical": True,
    }


def continue_from_pass1(
    *,
    production_root: Path,
    baseline: Mapping[str, Any],
    specs: Sequence[Mapping[str, Any]],
    run_build_frames: Callable[[Path, Path], Mapping[str, Any]],
    gzip_destination: Path | None = None,
    require_phase1_counts: bool = False,
) -> dict[str, Any]:
    production_root = Path(production_root)
    validate_pass1_outputs(production_root, baseline)
    shuffled = list(specs)
    random.Random(0).shuffle(shuffled)
    with tempfile.TemporaryDirectory(prefix="p3-phase1-shuffle-ca01-") as temporary:
        temporary_root = Path(temporary).resolve()
        shuffled_specs_path = temporary_root / "subject-specs.json"
        shuffled_output_root = temporary_root / "out"
        write_canonical_json(shuffled_specs_path, shuffled, exclusive=True)
        shuffled_result = dict(run_build_frames(shuffled_specs_path, shuffled_output_root))
        if shuffled_result.get("status") != "PASS":
            raise EvidenceError("E_BUILD_FRAMES", "shuffled build-frames did not report PASS")
        if require_phase1_counts:
            if shuffled_result.get("subject_count") != 35:
                raise EvidenceError("E_PHASE1_COUNTS", "shuffled subject count differs")
            if shuffled_result.get("common_input_count") != 1050:
                raise EvidenceError("E_PHASE1_COUNTS", "shuffled common-input count differs")
        compare_output_identity(production_root, shuffled_output_root)
        if any(
            path.startswith("slot-closure-")
            for path in (row["path"] for row in inventory_regular_files(production_root))
        ):
            raise EvidenceError("E_PHASE1_SLOTS", "Phase 1 produced slot-closure artifacts")
    frames = validate_json_bytes(
        (production_root / ROOT_SUBJECT_FRAMES).read_bytes(),
        ROOT_SUBJECT_FRAMES,
    )
    if require_phase1_counts:
        subjects = frames.get("subjects") if isinstance(frames, dict) else None
        if not isinstance(subjects, list) or len(subjects) != 35:
            raise EvidenceError("E_PHASE1_COUNTS", "subject-frames subject count differs")
        techniques = {row.get("primary_technique") for row in subjects if isinstance(row, dict)}
        if techniques != {"TECH_UNCERTAIN"}:
            raise EvidenceError("E_PHASE1_TECHNIQUE", "primary_technique is not TECH_UNCERTAIN")
    gzip_receipt = None
    if gzip_destination is not None:
        gzip_receipt = write_gzip_transport(
            production_root / ROOT_SUBJECT_FRAMES, Path(gzip_destination)
        )
        validate_gzip_transport(
            Path(gzip_destination),
            production_root / ROOT_SUBJECT_FRAMES,
            expected_raw_sha256=file_sha256(production_root / ROOT_SUBJECT_FRAMES),
        )
    production_rows = inventory_regular_files(production_root)
    result = {
        "status": "PASS",
        "subject_count": shuffled_result.get("subject_count"),
        "common_input_count": shuffled_result.get("common_input_count"),
        "artifact_count": len(production_rows),
        "shuffle_byte_identical": True,
        "subject_frames_sha256": file_sha256(production_root / ROOT_SUBJECT_FRAMES),
        "controller_amendment": "CA-01",
    }
    if gzip_receipt is not None:
        result["gzip_transport"] = gzip_receipt
    return result


def main() -> int:
    started = time.monotonic()
    baseline = read_canonical_json(BASELINE_PATH)
    specs = read_canonical_json(INPUT_ROOT / "subject-specs.json")
    if not isinstance(specs, list):
        raise EvidenceError("E_SUBJECT_SPECS", "subject specifications must be a list")
    emit_progress(stage="production pass 2 started", elapsed_s=0.0)
    result = continue_from_pass1(
        production_root=OUTPUT_ROOT,
        baseline=baseline,
        specs=specs,
        run_build_frames=_run_build_frames,
        gzip_destination=OUTPUT_ROOT / TRANSPORT_GZIP,
        require_phase1_counts=True,
    )
    result["wall_seconds"] = round(time.monotonic() - started, 3)
    emit_progress(
        stage="production pass 2 completed",
        elapsed_s=result["wall_seconds"],
    )
    sys.stdout.buffer.write(canonical_json_bytes(result))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except EvidenceError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(2)
