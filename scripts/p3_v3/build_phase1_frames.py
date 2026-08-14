#!/usr/bin/env python3
"""Derive frozen Phase 1 frames from the verified blinded P12 bridge."""

from __future__ import annotations

import json
import random
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
from collections.abc import Mapping, Sequence
from pathlib import Path, PurePosixPath
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

import scripts.p3_v3.evidence as evidence_cli  # noqa: E402
from p3_v3.artifacts import (  # noqa: E402
    EvidenceError,
    canonical_json_bytes,
    canonical_sha256,
    file_sha256,
    read_canonical_json,
    validate_sha256,
    write_canonical_json,
)
from p3_v3.bridge_and_frames import (  # noqa: E402
    _ecosystem_to_adapter,
    build_phase1_unresolved_profiling_receipt,
    build_public_behavior_frame,
    canonical_source_tree_sha256,
    derive_source_scale,
    discover_subject_or_fail_closed,
    select_profiling_workload,
    validate_adapter_registry,
    validate_input_generator_registry,
)

INTAKE_ROOT = ROOT / "data/p3_v3/p12_intake"
FRAME_ROOT = ROOT / "data/p3_v3/phase1_frames"
INPUT_ROOT = FRAME_ROOT / "inputs"
OUTPUT_ROOT = FRAME_ROOT / "out"
BRIDGE_PATH = INTAKE_ROOT / "verified_bridge.json"
ADAPTER_REGISTRY_PATH = ROOT / "data/p3_v3/protocol/adapter_registry.json"
GENERATOR_REGISTRY_PATH = (
    ROOT / "data/p3_v3/protocol/input_generator_registry.json"
)
MAX_ARTIFACT_BYTES = 90 * 1024 * 1024


def _archive_member_path(member: tarfile.TarInfo) -> Path | None:
    if member.issym() or member.islnk():
        raise EvidenceError(
            "E_ARCHIVE_SYMLINK", f"archive link member is forbidden: {member.name}"
        )
    if not member.isdir() and not member.isreg():
        raise EvidenceError(
            "E_ARCHIVE_MEMBER", f"archive special member is forbidden: {member.name}"
        )
    if not isinstance(member.name, str) or "\\" in member.name or "\x00" in member.name:
        raise EvidenceError("E_ARCHIVE_PATH", "archive member path is unsafe")
    candidate = PurePosixPath(member.name)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise EvidenceError(
            "E_ARCHIVE_PATH", f"archive member path is unsafe: {member.name}"
        )
    parts = tuple(part for part in candidate.parts if part not in {"", "."})
    if not parts:
        if member.isdir():
            return None
        raise EvidenceError("E_ARCHIVE_PATH", "archive file path is empty")
    return Path(*parts)


def extract_archive(
    archive_path: Path, destination: Path, expected_sha256: str
) -> Path:
    """Verify and safely extract one regular-file source archive."""

    archive_path = Path(archive_path)
    destination = Path(destination)
    expected = validate_sha256(expected_sha256, "source_archive_sha256")
    if not archive_path.is_file():
        raise EvidenceError("E_ARCHIVE", f"archive is absent: {archive_path}")
    observed = file_sha256(archive_path)
    if observed != expected:
        raise EvidenceError(
            "E_ARCHIVE_HASH",
            f"archive sha256 differs: expected {expected}, observed {observed}",
        )

    try:
        with tarfile.open(archive_path, "r:*") as archive:
            members = archive.getmembers()
            prepared: list[tuple[tarfile.TarInfo, Path | None]] = []
            seen_paths: set[Path] = set()
            for member in members:
                relative = _archive_member_path(member)
                if relative is not None:
                    if relative in seen_paths:
                        raise EvidenceError(
                            "E_ARCHIVE_PATH",
                            f"archive member path duplicates: {member.name}",
                        )
                    seen_paths.add(relative)
                prepared.append((member, relative))

            if destination.exists():
                if destination.is_symlink() or not destination.is_dir():
                    raise EvidenceError(
                        "E_ARCHIVE_DESTINATION", "extraction destination is unsafe"
                    )
                shutil.rmtree(destination)
            destination.mkdir(parents=True)
            destination_root = destination.resolve()
            for member, relative in prepared:
                if relative is None:
                    continue
                target = destination / relative
                if not target.resolve().is_relative_to(destination_root):
                    raise EvidenceError(
                        "E_ARCHIVE_PATH", f"archive member escapes root: {member.name}"
                    )
                if member.isdir():
                    target.mkdir(parents=True, exist_ok=True)
                    continue
                target.parent.mkdir(parents=True, exist_ok=True)
                source = archive.extractfile(member)
                if source is None:
                    raise EvidenceError(
                        "E_ARCHIVE_MEMBER", f"archive file is unreadable: {member.name}"
                    )
                with source, target.open("xb") as output:
                    shutil.copyfileobj(source, output)
                target.chmod(0o755 if member.mode & 0o111 else 0o644)
    except EvidenceError:
        raise
    except (OSError, tarfile.TarError) as exc:
        raise EvidenceError("E_ARCHIVE", f"archive extraction failed: {archive_path}") from exc
    return destination


def load_descriptor(path: Path, expected_sha256: str) -> dict[str, Any]:
    """Load a descriptor and verify its canonical object commitment."""

    expected = validate_sha256(expected_sha256, "build_descriptor_sha256")
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise EvidenceError("E_BUILD_DESCRIPTOR", f"descriptor is unreadable: {path}") from exc
    if not isinstance(value, dict):
        raise EvidenceError("E_BUILD_DESCRIPTOR", "descriptor must be an object")
    observed = canonical_sha256(value)
    if observed != expected:
        raise EvidenceError(
            "E_BUILD_DESCRIPTOR_COMMITMENT",
            f"descriptor sha256 differs: expected {expected}, observed {observed}",
        )
    return value


def assert_exact_coverage(
    bridge_records: Sequence[Mapping[str, Any]],
    subject_specs: Sequence[Mapping[str, Any]],
) -> None:
    """Require a bijection between bridge records and subject specifications."""

    if isinstance(bridge_records, (str, bytes)) or not isinstance(
        bridge_records, Sequence
    ):
        raise EvidenceError("E_BRIDGE_RECORDS", "bridge records must be a list")
    bridge_ids: set[str] = set()
    for index, record in enumerate(bridge_records):
        if not isinstance(record, Mapping):
            raise EvidenceError("E_BRIDGE_RECORDS", f"records[{index}] is invalid")
        neutral = validate_sha256(
            record.get("neutral_snapshot_id"), f"records[{index}].neutral_snapshot_id"
        )
        if neutral in bridge_ids:
            raise EvidenceError("E_BRIDGE_RECORDS", "duplicate bridge neutral ID")
        bridge_ids.add(neutral)

    if isinstance(subject_specs, (str, bytes)) or not isinstance(
        subject_specs, Sequence
    ):
        raise EvidenceError("E_SUBJECT_SPEC_COVERAGE", "subject specs must be a list")
    spec_ids: set[str] = set()
    for index, spec in enumerate(subject_specs):
        if not isinstance(spec, Mapping):
            raise EvidenceError(
                "E_SUBJECT_SPEC_COVERAGE", f"subject_specs[{index}] is invalid"
            )
        neutral = validate_sha256(
            spec.get("neutral_snapshot_id"),
            f"subject_specs[{index}].neutral_snapshot_id",
        )
        if neutral in spec_ids:
            raise EvidenceError(
                "E_SUBJECT_SPEC_COVERAGE", f"duplicate subject spec: {neutral}"
            )
        spec_ids.add(neutral)
    if spec_ids != bridge_ids:
        raise EvidenceError(
            "E_SUBJECT_SPEC_COVERAGE",
            "subject specifications do not cover bridge exactly",
        )


def _validated_registries() -> tuple[dict[str, Any], dict[str, Any], dict, dict]:
    raw_adapters = read_canonical_json(ADAPTER_REGISTRY_PATH)
    raw_generators = read_canonical_json(GENERATOR_REGISTRY_PATH)
    if not isinstance(raw_adapters, dict) or not isinstance(raw_generators, dict):
        raise EvidenceError("E_REGISTRY", "Phase 1 registries must be objects")
    adapter_paths = [
        entry["implementation_path"] for entry in raw_adapters.get("adapters", [])
    ]
    generator_paths = [
        entry["implementation_path"]
        for entry in raw_generators.get("generators", [])
    ]
    validated_adapters = validate_adapter_registry(
        raw_adapters,
        evidence_cli._capture_declared_source_snapshot(
            ROOT, adapter_paths, "adapter implementation"
        ),
    )
    validated_generators = validate_input_generator_registry(
        raw_generators,
        evidence_cli._capture_declared_source_snapshot(
            ROOT, generator_paths, "input generator implementation"
        ),
    )
    return raw_adapters, raw_generators, validated_adapters, validated_generators


def build_subject_specs(
    bridge: Mapping[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    records = bridge.get("records") if isinstance(bridge, Mapping) else None
    if not isinstance(records, list):
        raise EvidenceError("E_BRIDGE_RECORDS", "verified bridge records are absent")
    raw_adapters, raw_generators, validated_adapters, _validated_generators = (
        _validated_registries()
    )
    ecosystem_to_adapter = _ecosystem_to_adapter(validated_adapters)
    specs: list[dict[str, Any]] = []
    summaries: list[dict[str, Any]] = []
    for record in sorted(records, key=lambda row: row["neutral_snapshot_id"]):
        neutral = validate_sha256(
            record.get("neutral_snapshot_id"), "record.neutral_snapshot_id"
        )
        descriptor = load_descriptor(
            INTAKE_ROOT / "descriptors" / f"{neutral}.json",
            record["build_descriptor_sha256"],
        )
        source_root = extract_archive(
            INTAKE_ROOT / "archives" / f"{neutral}.tar",
            INTAKE_ROOT / "extracted" / neutral,
            record["source_archive_sha256"],
        )
        _manifest, snapshot = evidence_cli._capture_tracked_source_manifest(
            source_root, ["."], "subject-source"
        )
        observed_tree = canonical_source_tree_sha256(snapshot)
        if observed_tree != record["normalized_source_tree_sha256"]:
            raise EvidenceError(
                "E_SOURCE_TREE_COMMITMENT",
                f"source tree differs for neutral snapshot {neutral}",
            )
        source_record = {
            "normalized_source_tree_sha256": record[
                "normalized_source_tree_sha256"
            ],
            "build_descriptor_sha256": record["build_descriptor_sha256"],
        }
        ecosystem = descriptor.get("ecosystem")
        if not isinstance(ecosystem, str) or not ecosystem:
            raise EvidenceError(
                "E_BUILD_DESCRIPTOR", f"descriptor ecosystem is absent: {neutral}"
            )
        discovery = discover_subject_or_fail_closed(
            snapshot,
            descriptor,
            validated_adapters,
            ecosystem_to_adapter.get(ecosystem),
        )
        frame = build_public_behavior_frame(source_record, discovery)
        scale = derive_source_scale(snapshot, discovery)
        workload = select_profiling_workload(frame, scale["scale_class"])
        receipt = build_phase1_unresolved_profiling_receipt(
            workload,
            source_record,
            neutral_snapshot_id=neutral,
            adapter_implementation_source_sha256=discovery[
                "implementation_source_sha256"
            ],
        )
        specs.append(
            {
                "neutral_snapshot_id": neutral,
                "source_root": source_root.relative_to(ROOT).as_posix(),
                "source_record": source_record,
                "build_descriptor": descriptor,
                "adapter_registry": raw_adapters,
                "input_generator_registry": raw_generators,
                "profiling_results": receipt,
            }
        )
        summaries.append(
            {
                "neutral_snapshot_id": neutral,
                "discovery_status": discovery["discovery_status"],
                "scale_class": scale["scale_class"],
                "selected_row_count": len(workload["selected_rows"]),
            }
        )
    assert_exact_coverage(records, specs)
    return specs, summaries


def _ensure_empty_inputs() -> tuple[Path, Path, Path]:
    inputs = (
        (INPUT_ROOT / "empty-slots.json", []),
        (INPUT_ROOT / "empty-contracts.json", {}),
        (INPUT_ROOT / "empty-applicability.json", {}),
    )
    for path, expected in inputs:
        if path.exists():
            if read_canonical_json(path) != expected:
                raise EvidenceError("E_PHASE1_INPUT", f"Phase 1 input differs: {path}")
        else:
            write_canonical_json(path, expected, exclusive=True)
    return inputs[0][0], inputs[1][0], inputs[2][0]


def _run_build_frames(specs_path: Path, output_root: Path) -> dict[str, Any]:
    if output_root.exists():
        if output_root.is_symlink() or not output_root.is_dir():
            raise EvidenceError("E_OUTPUT_ROOT", "frame output root is unsafe")
        shutil.rmtree(output_root)
    slots, contracts, applicability = _ensure_empty_inputs()
    command = [
        sys.executable,
        str(ROOT / "scripts/p3_v3/evidence.py"),
        "build-frames",
        "--bridge",
        str(BRIDGE_PATH),
        "--subject-specs",
        str(specs_path),
        "--adapter-root",
        str(ROOT),
        "--generator-root",
        str(ROOT),
        "--slots",
        str(slots),
        "--contracts",
        str(contracts),
        "--applicability-map",
        str(applicability),
        "--output-root",
        str(output_root),
    ]
    completed = subprocess.run(
        command, cwd=ROOT, text=True, capture_output=True, check=False
    )
    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout)[-4000:].strip()
        raise EvidenceError("E_BUILD_FRAMES", detail or "build-frames failed")
    try:
        result = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise EvidenceError("E_BUILD_FRAMES", "build-frames output is not JSON") from exc
    if not isinstance(result, dict) or result.get("status") != "PASS":
        raise EvidenceError("E_BUILD_FRAMES", "build-frames did not report PASS")
    return result


def _artifact_digests(output_root: Path) -> dict[str, str]:
    digests: dict[str, str] = {}
    for path in sorted(output_root.rglob("*")):
        if not path.is_file():
            continue
        if path.stat().st_size > MAX_ARTIFACT_BYTES:
            raise EvidenceError(
                "E_ARTIFACT_SIZE", f"artifact exceeds 90 MiB: {path.name}"
            )
        digests[path.relative_to(output_root).as_posix()] = file_sha256(path)
    return digests


def main() -> int:
    started = time.monotonic()
    bridge = read_canonical_json(BRIDGE_PATH)
    specs, summaries = build_subject_specs(bridge)
    _ensure_empty_inputs()
    subject_specs_path = INPUT_ROOT / "subject-specs.json"
    subject_specs_path.unlink(missing_ok=True)
    write_canonical_json(subject_specs_path, specs, exclusive=True)

    production = _run_build_frames(subject_specs_path, OUTPUT_ROOT)
    if production.get("subject_count") != 35 or production.get(
        "common_input_count"
    ) != 1050:
        raise EvidenceError(
            "E_PHASE1_COUNTS", "build-frames counts differ from the frozen Phase 1 set"
        )
    production_digests = _artifact_digests(OUTPUT_ROOT)
    if any(name.startswith("slot-closure-") for name in production_digests):
        raise EvidenceError("E_PHASE1_SLOTS", "Phase 1 produced slot-closure artifacts")

    shuffled = list(specs)
    random.Random(0).shuffle(shuffled)
    with tempfile.TemporaryDirectory(prefix="p3-phase1-shuffle-") as temporary:
        temporary_root = Path(temporary)
        shuffled_specs_path = temporary_root / "subject-specs.json"
        shuffled_output_root = temporary_root / "out"
        write_canonical_json(shuffled_specs_path, shuffled, exclusive=True)
        shuffled_result = _run_build_frames(
            shuffled_specs_path, shuffled_output_root
        )
        shuffled_digests = _artifact_digests(shuffled_output_root)
        if shuffled_result.get("subject_count") != 35:
            raise EvidenceError("E_PHASE1_COUNTS", "shuffled subject count differs")
        if shuffled_digests != production_digests:
            raise EvidenceError(
                "E_SHUFFLE_IDENTITY", "shuffled frame regeneration differs by bytes"
            )

    result = {
        "status": "PASS",
        "subject_count": production["subject_count"],
        "common_input_count": production["common_input_count"],
        "artifact_count": len(production_digests),
        "shuffle_byte_identical": True,
        "subject_frames_sha256": production_digests["subject-frames.json"],
        "summaries": summaries,
        "wall_seconds": round(time.monotonic() - started, 3),
    }
    sys.stdout.buffer.write(canonical_json_bytes(result))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except EvidenceError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(2)
