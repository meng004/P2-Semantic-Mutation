# Boost.Math PILOT_SOURCE_PREPARATION_ONLY Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. This document authorizes only the single future source-preparation capability task below. After that task, stop for independent review. Do not start production preparation. Do not create authorization A.

**Goal:** Define one later capability that can hash, extract, and identity-check a caller-supplied archive under a fail-closed extractor and the Phase 1 normalized-tree algorithm. This planning node writes the plan only. The later capability task uses runtime-generated synthetic ZIP and TAR fixtures. It does not read a real Boost.Math archive and does not create a production source manifest or preparation result.

**Architecture:** Keep confirmatory `p3-v3-*` schemas unchanged. Add `src/p3_v3/pilot_source.py` as the only new production module. Bind that module to the archived foundation implementation verdict, the frozen machine plan, and a reserved authorization A path whose exact bytes are specified here and whose file is not created by this node or by the later capability task. Production outputs stay reserved for a later, separately authorized preparation node. After the single capability task, stop at an independent implementation review. Capability PASS still does not authorize real preparation.

**Tech Stack:** Python 3.11 or newer, existing `src/p3_v3/artifacts.py` exact-object helpers, existing `SourceSnapshot`, `SourceSnapshotEntry`, and `canonical_source_tree_sha256` from `src/p3_v3/bridge_and_frames.py`, pytest with `PYTHONPATH=src`. Cursor VM has no `rtk`. Later implementation uses bare `python3`, `pytest`, `sha256sum`, `wc`, and `git`.

## Global Constraints

- Plan class is `PILOT_SOURCE_PREPARATION_ONLY`.
- This document has exactly one future implementation task.
- This planning node does not run pytest.
- After this document is written, the requested review state is `PILOT_PLAN_REVIEW_CANDIDATE`. This document is not an independent PASS.
- Formal foundation state remains `PILOT_IMPLEMENTATION_PASS`.
- Process location remains `PILOT_EXECUTION_AWAITING_USER_AUTHORIZATION`.
- The later capability task uses only runtime-generated synthetic ZIP and TAR fixtures.
- The later capability task does not read a real Boost.Math archive.
- The later capability task does not create `data/p3_v3/pilot/boost_math/source-manifest.json` or `data/p3_v3/pilot/boost_math/source-preparation-result.json`.
- After the later capability task, stop at an independent Sol High implementation review.
- Capability implementation PASS still does not authorize real preparation.
- Only a later explicit user authorization A and a separately reviewed production preparation launch packet may run production preparation.
- `claims=blocked`.
- Formal denominator membership is false.
- `rq4_supported=false`.
- The complete plan `docs/superpowers/plans/2026-08-15-p3-boost-math-pilot-only.md` remains unfrozen and is not execution authority.
- This document contains no build, CMake configure, contract, site, MR, mutant, certification, execution, or evidence-closure implementation task.
- This planning node does not create authorization A.
- The later capability task does not create authorization A.
- `execution_class = PILOT_ONLY` and `denominator = PILOT_ONLY` on every durable pilot object defined here.
- File count, directory names, and LOC cannot replace normalized tree identity.
- The frozen build descriptor hash is an authority label only. A source manifest does not prove CMake configure, compile, test, or public behavior PASS.
- Archive SHA-256 and archive bytes are observed at production time from one opened snapshot. This plan does not invent unknown fixed archive hash or byte values.

---

## Three Independent Gates

Frozen successor order. Any missing predecessor, hash mismatch, or non-PASS state fail-closes every later gate.

```text
G1_FOUNDATION_IMPLEMENTATION_PASS
-> source-preparation capability implementation
-> Sol High capability implementation review
-> formal capability implementation verdict archival
-> user explicit authorization A
-> separately reviewed production preparation launch packet
-> production source identity/materialization
-> Sol High source-manifest/result review
```

Gate meanings:

1. `G1_FOUNDATION_IMPLEMENTATION_PASS` is the current archived foundation implementation verdict. It is already PASS. It authorizes only later capability planning and later capability implementation review, not production preparation.
2. Source-preparation capability implementation is the single task in this document. It implements and unit-tests the capability against synthetic fixtures. It writes no production preparation artifact.
3. Sol High capability implementation review is an independent review of that capability. This planning node does not perform it.
4. Formal capability implementation verdict archival is a later exclusive archival node. It is not the capability task and is not production preparation.
5. User explicit authorization A is the reserved file defined below. Neither this node nor the capability task creates it.
6. The production preparation launch packet is a later, separately reviewed document. This plan must not contain an executable production command that names a fictional archive path. The real production command appears only in that later packet.
7. Production source identity and materialization is the only node that may exclusive-create the source manifest and preparation result.
8. Sol High source-manifest and result review is an independent review of those production artifacts.

Fail-closed rule: if any earlier artifact is absent, has the wrong SHA-256, or is not PASS, the later gate must raise and must not write a successor production artifact.

---

## Frozen Authority Identities

These files are identity-checked only. This plan does not modify them.

| File | SHA-256 |
|---|---|
| `docs/superpowers/plans/2026-08-16-p3-boost-math-pilot-foundation-only.md` | `479931df4dd6562177e28c333305f3c55bbf081a596f5e7de337b8a92fa73463` |
| `docs/review_20260816/boost_math_pilot_foundation_plan_review_packet.md` | `e6fd4ab16b3db44711014e4fb9aeaa9b41405c5b37650c3fe790d5f9dfaf9e92` |
| `docs/review_20260816/boost_math_pilot_foundation_sol_high_review.md` | `da5f211b7eab665aca696f5cf1d214d30b0914dc9ccb2a585bfcc06cb97be07c` |
| `docs/review_20260817/boost_math_pilot_foundation_implementation_sol_high_review.md` | `e7e5e9519ae49eb08c450c4e16c56d7551528030916d9d8fe88f0ab91a7b1c9d` |
| `data/p3_v3/pilot/boost_math/pilot-plan.json` | `23d7fb802a2395d93a211862f205065ce1abd52e6ae2e74374aaf2bb624d4cf2` |
| `src/p3_v3/pilot.py` | `4689ed3940f87d3c7c3297bf58c786a3fb2d289cbc45556de35903b0e9111c46` |
| `scripts/p3_v3/pilot.py` | `44597b83d59f159d6a7fbf7fbc010b9b747a1aaf4a366ae1c1fd222314b9b7c9` |
| `tests/p3_v3/test_pilot.py` | `04a61415b6b6071c8a23d4ccf39c4f39b330d1a0530ae19805aa83e71e2515ff` |
| `src/p3_v3/artifacts.py` | `9f619073626003caa7d724a19655b5abae92318afd3f656494a0843613b6f57a` |
| `src/p3_v3/bridge_and_frames.py` | `978fa53c66ae15f9c51b5fa73dc03afdb2d23448f7714d752bccf92c09503ad0` |
| `docs/superpowers/plans/2026-08-15-p3-boost-math-pilot-only.md` | `1612a6ee81773c7db97625ae3497fab31b93ad70f2ecaefce2fdd845bda73cca` |
| `research/evidence/p3_claim_ledger_v1.3.0.yml` | `bf4979662697b2d0565bb70eec88b22673e84bee93b61234555342efb4082a68` |
| `data/p3_v3/protocol/protocol.json` | `240d8270d41802c9d5b86f30564eadd1a86fd9ed09de2c7e947d17c1a4d78519` |
| `data/p3_v3/protocol/environment_lock.json` | `7706b4ce272d09df13c5212b04ec0f2519932f4225d5eac0d052d3225c7ff35f` |
| `adapter-discovery` frame | `87fb9d05278c5c2e713c8a9d7f398cb1a1c84562df27b590e6d37f98fd7c1dd1` |
| `derived-subject` frame | `654a5c8a26b85013a44665dd92c59a66afee9f639ec7d28535d58357ec696f20` |
| `source-scale` frame | `dc9b56fe81bcf8301e6164f15007c6f57ee11e79cfff1b84e66906cb7de228d0` |

The 2026-08-15 complete pilot plan is a readable unfrozen reference. It is not current execution authority.

---

## Implementation Verdict And Machine Plan Binding

Frozen implementation verdict path:

```text
docs/review_20260817/boost_math_pilot_foundation_implementation_sol_high_review.md
```

Frozen implementation verdict SHA-256:

```text
e7e5e9519ae49eb08c450c4e16c56d7551528030916d9d8fe88f0ab91a7b1c9d
```

Required verdict literals after the file-hash check:

- `verdict` equals `PASS`
- `authorized_state` equals `PILOT_IMPLEMENTATION_PASS`
- `claims` equals `blocked`
- `reviewed_machine_plan_path` equals `data/p3_v3/pilot/boost_math/pilot-plan.json`
- `reviewed_machine_plan_sha256` equals the frozen machine-plan hash below

Frozen machine plan path:

```text
data/p3_v3/pilot/boost_math/pilot-plan.json
```

Frozen machine plan SHA-256:

```text
23d7fb802a2395d93a211862f205065ce1abd52e6ae2e74374aaf2bb624d4cf2
```

Production code reads only those two paths. The production CLI must not accept an implementation-verdict path override or a machine-plan path override. Tests may monkeypatch the path constants onto temporary regular files. Monkeypatching a path does not skip the SHA-256 check or the PASS-state check. A missing file, a hash mismatch, or a non-PASS state is fail-closed and writes no source manifest and no preparation result.

---

## Authorization A

Frozen production path:

```text
data/p3_v3/pilot/boost_math/user-auth-preparation.txt
```

Exact bytes, including the single terminal LF:

```text
AUTHORIZE_BOOSTMATH_PILOT_PREPARATION\n
```

Frozen identity:

- SHA-256: `502c6407aa368a26948db10cc1ca0d1c91f66c8bfe702aa02f01f275c9df04b6`
- bytes: 38
- LF: 1

This planning node does not create that file. The later capability task does not create that file. Production CLI must not accept an authorization-path override. Tests may monkeypatch the frozen path constant onto a temporary regular file. Tests must still require the exact 38 bytes and the frozen SHA-256. A missing file is `E_PILOT_PREPARATION_AUTH_ABSENT`. Wrong bytes or a wrong hash is `E_PILOT_PREPARATION_AUTH`. Either authorization failure writes no source manifest and no preparation result, because preparation is not authorized.

```python
from __future__ import annotations

import hashlib
from pathlib import Path

from p3_v3.artifacts import EvidenceError

AUTHORIZATION_A_PATH = Path("data/p3_v3/pilot/boost_math/user-auth-preparation.txt")
AUTHORIZATION_A_BYTES = b"AUTHORIZE_BOOSTMATH_PILOT_PREPARATION\n"
AUTHORIZATION_A_SHA256 = (
    "502c6407aa368a26948db10cc1ca0d1c91f66c8bfe702aa02f01f275c9df04b6"
)


def verify_authorization_a(path: Path = AUTHORIZATION_A_PATH) -> str:
    if not path.is_file() or path.is_symlink():
        raise EvidenceError(
            "E_PILOT_PREPARATION_AUTH_ABSENT",
            "authorization A is absent",
        )
    observed = path.read_bytes()
    digest = hashlib.sha256(observed).hexdigest()
    if observed != AUTHORIZATION_A_BYTES or digest != AUTHORIZATION_A_SHA256:
        raise EvidenceError(
            "E_PILOT_PREPARATION_AUTH",
            "authorization A bytes or hash differ",
        )
    return digest
```

---

## Fixed Subject Identities

Copy these labels exactly. Presence of a label does not prove that a real archive was opened.

- `p12_item_id = C-BOOSTMATH-001`
- `neutral_snapshot_id = 74cdc825c3c728c25f5ea857af1565350515a4e631fb0a874c26e810ec437886`
- `normalized_source_tree_sha256 = 93a62859d7fdd6b2068e494bbe6e3e27180b874cbd27055ac27f941e507a90d8`
- `controlled_subject_source_id = e5f21a7d067d641d0a20bfc57c61e630d6f7588ef30235cea49c9a9cf950c7a7`
- `controlled_subject_id = 89b0e6791c611b465b9216e833e0c526a53ffd6946b5cd20de045e3641f43914`
- `build_descriptor_sha256 = 68d2e0fd34b845bb0df22b29003f26259d5655d2ec80c18895ff36904db2d95d`
- `adapter_id = CMAKE_CTEST_V1`
- `ecosystem = cmake`
- `execution_class = PILOT_ONLY`
- `denominator = PILOT_ONLY`
- `cpu_only = true`
- `cuda_required = false`

`build_descriptor_sha256` is a frozen authority label. The source manifest records that label. It does not prove CMake configure PASS, compile PASS, test PASS, or public-behavior PASS.

---

## Approved Future File Map

The later implementation task may create only:

- `src/p3_v3/pilot_source.py`
- `tests/p3_v3/test_pilot_source.py`

The later implementation task may modify only:

- `scripts/p3_v3/pilot.py`
- `tests/p3_v3/test_pilot.py`

The later implementation task must not modify:

- `src/p3_v3/artifacts.py`
- `src/p3_v3/bridge_and_frames.py`
- `src/p3_v3/packages.py`
- `src/p3_v3/run_records.py`
- protocol files
- the claim ledger
- Phase 1 Frame files
- the foundation plan verdict
- the foundation implementation verdict
- the machine plan
- the complete 2026-08-15 plan

The later implementation task must not create any new artifact under `data/p3_v3/pilot/boost_math/`.

Reserved production paths, exclusive-created only by a later separately authorized production preparation node:

- `data/p3_v3/pilot/boost_math/source-manifest.json`
- `data/p3_v3/pilot/boost_math/source-preparation-result.json`
- `data/p3_v3/pilot/boost_math/user-auth-preparation.txt`

---

## Archive Snapshot Contract

Immutable snapshot:

```python
from __future__ import annotations

import hashlib
import os
import stat
from dataclasses import dataclass
from pathlib import Path

from p3_v3.artifacts import EvidenceError


@dataclass(frozen=True)
class ArchiveSnapshot:
    raw: bytes
    sha256: str
    size: int
    archive_format: str


def detect_archive_format(raw: bytes) -> str:
    zip_magic = raw.startswith(b"PK\x03\x04") or raw.startswith(b"PK\x05\x06")
    tar_magic = len(raw) >= 262 and raw[257:262] == b"ustar"
    if zip_magic and tar_magic:
        raise EvidenceError(
            "E_PILOT_ARCHIVE_FORMAT",
            "archive format is ambiguous",
        )
    if zip_magic:
        return "ZIP"
    if tar_magic:
        return "TAR"
    raise EvidenceError(
        "E_PILOT_ARCHIVE_FORMAT",
        "archive format is unsupported or corrupt",
    )


def read_production_archive_bytes(archive_path: str | Path) -> ArchiveSnapshot:
    path = Path(archive_path)
    flags = os.O_RDONLY | os.O_CLOEXEC
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        fd = os.open(path, flags)
    except OSError as exc:
        raise EvidenceError("E_PILOT_ARCHIVE_UNSAFE", "archive cannot be opened") from exc
    try:
        before = os.fstat(fd)
        if not stat.S_ISREG(before.st_mode):
            raise EvidenceError(
                "E_PILOT_ARCHIVE_UNSAFE",
                "archive is not a regular file",
            )
        chunks: list[bytes] = []
        while True:
            chunk = os.read(fd, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        after = os.fstat(fd)
        if (
            before.st_dev,
            before.st_ino,
            before.st_size,
            before.st_mtime_ns,
        ) != (
            after.st_dev,
            after.st_ino,
            after.st_size,
            after.st_mtime_ns,
        ):
            raise EvidenceError(
                "E_PILOT_ARCHIVE_UNSAFE",
                "archive identity changed during read",
            )
        raw = b"".join(chunks)
        if len(raw) != before.st_size:
            raise EvidenceError(
                "E_PILOT_ARCHIVE_UNSAFE",
                "archive size differs from st_size",
            )
        digest = hashlib.sha256(raw).hexdigest()
        archive_format = detect_archive_format(raw)
        return ArchiveSnapshot(
            raw=raw,
            sha256=digest,
            size=before.st_size,
            archive_format=archive_format,
        )
    finally:
        os.close(fd)
```

Hard rules:

- Use one `os.open`.
- Use `O_RDONLY | O_CLOEXEC`.
- Add `O_NOFOLLOW` when the platform provides it.
- `os.fstat` must prove a regular file.
- Compare `st_dev`, `st_ino`, `st_size`, and `st_mtime_ns` before and after the read.
- Read all bytes from that same opened descriptor.
- Hash those same raw bytes.
- The read length must equal `st_size`.
- Do not hash a path and then reopen the path for extraction.
- Do not follow a symlink.
- Do not accept a directory, FIFO, device, or socket.
- Detect archive format from bytes, not from the filename suffix.
- After the snapshot returns, the extractor may consume only `snapshot.raw`.

---

## Extractor Policy

Exact policy object. `extractor_policy_sha256 = canonical_sha256(EXTRACTOR_POLICY_V1)`.

```python
EXTRACTOR_POLICY_V1 = {
    "schema_version": "p3-pilot-extractor-policy-v1",
    "accepted_formats": ["TAR", "ZIP"],
    "strip_single_top_level_directory": True,
    "max_member_count": 100000,
    "max_member_bytes": 536870912,
    "max_total_uncompressed_bytes": 4294967296,
    "reject_absolute_paths": True,
    "reject_parent_traversal": True,
    "reject_backslash_paths": True,
    "reject_nul_paths": True,
    "reject_symlinks": True,
    "reject_hardlinks": True,
    "reject_devices": True,
    "reject_fifos": True,
    "reject_sockets": True,
    "reject_duplicate_normalized_paths": True,
    "reject_casefold_collisions": True,
    "reject_target_escape": True,
    "reject_encrypted_zip_members": True,
}

EXTRACTOR_POLICY_SHA256 = (
    "e482ea272a6836099b9dc52deab7d799e24c571c9433fdafe2cff6de48bbb229"
)
```

The later implementation must compute `canonical_sha256(EXTRACTOR_POLICY_V1)` and require that it equal `EXTRACTOR_POLICY_SHA256`.

The extractor must reject all of the following and raise `E_PILOT_EXTRACT_UNSAFE` or, for format problems, `E_PILOT_ARCHIVE_FORMAT`:

- POSIX absolute path
- Windows absolute path
- `..` traversal
- backslash path
- NUL in a path
- symlink
- hardlink
- device
- FIFO
- socket
- ZIP encrypted member
- duplicate normalized path
- Unicode casefold collision
- target-root escape
- member count above `max_member_count`
- one member above `max_member_bytes`
- total uncompressed bytes above `max_total_uncompressed_bytes`
- unsupported archive format
- corrupt archive
- archive format ambiguity

Extraction writes into a newly created staging directory. The caller-supplied materialize root must not exist at start. Success atomically renames the staging directory onto that root. Failure may delete only the staging directory created by that attempt. The extractor must not delete or replace a pre-existing materialize root.

`strip_single_top_level_directory` applies only when every accepted member shares one nonempty top-level directory. Otherwise the payload root is the extraction root. The decision must be independent of member order.

```python
from __future__ import annotations


def shared_top_level_directory(member_names: list[str]) -> str | None:
    tops: set[str] = set()
    for name in member_names:
        first = name.split("/", 1)[0]
        if not first:
            return None
        tops.add(first)
    if len(tops) != 1:
        return None
    return next(iter(tops))
```

---

## Normalized Tree Binding

Reuse without changing scientific meaning:

- `SourceSnapshot`
- `SourceSnapshotEntry`
- `canonical_source_tree_sha256`

Source: `src/p3_v3/bridge_and_frames.py`. Do not invent a second tree-hash algorithm. Do not modify that module.

Materialized tree capture must:

- walk the complete payload root;
- sort relative paths by UTF-8 path bytes;
- `lstat` every node;
- reject a symlink or special node with `E_PILOT_EXTRACT_UNSAFE`;
- read each regular file through one regular-file snapshot, reusing `read_regular_file_snapshot` from `src/p3_v3/artifacts.py`;
- project mode only to `100644` or `100755`;
- build a complete `SourceSnapshot`;
- call `canonical_source_tree_sha256(snapshot)`;
- require the result to equal `93a62859d7fdd6b2068e494bbe6e3e27180b874cbd27055ac27f941e507a90d8` on the production seam.

A tree-hash mismatch after a successful extract is `E_PILOT_SOURCE_TREE_MISMATCH` and, when authorization A was already valid, writes a `FAIL_INFRASTRUCTURE` result whose `failure_reason` is `SOURCE_TREE_MISMATCH`. File count, directory names, and LOC are not a substitute for that hash.

```python
from __future__ import annotations

import os
import stat
from pathlib import Path

from p3_v3.artifacts import EvidenceError, read_regular_file_snapshot
from p3_v3.bridge_and_frames import (
    SourceSnapshot,
    SourceSnapshotEntry,
    canonical_source_tree_sha256,
)

FROZEN_NORMALIZED_SOURCE_TREE_SHA256 = (
    "93a62859d7fdd6b2068e494bbe6e3e27180b874cbd27055ac27f941e507a90d8"
)


def _projected_mode(mode: int) -> str:
    if mode & 0o111:
        return "100755"
    return "100644"


def capture_materialized_tree(payload_root: Path) -> SourceSnapshot:
    entries: list[SourceSnapshotEntry] = []
    for dirpath, dirnames, filenames in os.walk(payload_root, followlinks=False):
        for name in list(dirnames) + list(filenames):
            full = Path(dirpath) / name
            info = os.lstat(full)
            if stat.S_ISLNK(info.st_mode) or not (
                stat.S_ISREG(info.st_mode) or stat.S_ISDIR(info.st_mode)
            ):
                raise EvidenceError(
                    "E_PILOT_EXTRACT_UNSAFE",
                    f"materialized node is not a regular file or directory: {full}",
                )
            if stat.S_ISDIR(info.st_mode):
                continue
            relative = full.relative_to(payload_root).as_posix()
            raw, raw_mode = read_regular_file_snapshot(full, "materialized-source")
            entries.append(
                SourceSnapshotEntry(
                    relative_path=relative,
                    mode=_projected_mode(raw_mode),
                    sha256=__import__("hashlib").sha256(raw).hexdigest(),
                    content=raw,
                )
            )
    entries.sort(key=lambda item: item.relative_path.encode("utf-8"))
    return SourceSnapshot(entries=tuple(entries))


def require_frozen_tree(snapshot: SourceSnapshot) -> str:
    observed = canonical_source_tree_sha256(snapshot)
    if observed != FROZEN_NORMALIZED_SOURCE_TREE_SHA256:
        raise EvidenceError(
            "E_PILOT_SOURCE_TREE_MISMATCH",
            "materialized tree hash differs from frozen normalized tree",
        )
    return observed
```

Capability-unit tests use synthetic trees. Those trees will not equal the frozen Boost.Math hash. `test_materialized_tree_uses_phase1_canonical_hash` must prove that capture calls `canonical_source_tree_sha256` on a `SourceSnapshot`. `test_wrong_materialized_tree_writes_failure_result` must prove that a non-frozen tree writes `SOURCE_TREE_MISMATCH` and does not write a source manifest. Tests may monkeypatch output-path constants onto `tmp_path`. Tests must not write production files under `data/p3_v3/pilot/boost_math/`.

---

## Source Manifest Exact Schema

`PILOT_SOURCE_MANIFEST_EXACT` has these exact keys and exact types. No extra key is legal.

```python
PILOT_SOURCE_MANIFEST_EXACT = {
    "schema_version": str,
    "execution_class": str,
    "denominator": str,
    "p12_item_id": str,
    "neutral_snapshot_id": str,
    "normalized_source_tree_sha256": str,
    "controlled_subject_id": str,
    "controlled_subject_source_id": str,
    "predecessor_sha256": list,
    "archive_sha256": str,
    "archive_bytes": int,
    "archive_format": str,
    "build_descriptor_sha256": str,
    "authorization_a_sha256": str,
    "extractor_policy_sha256": str,
    "materialized_file_count": int,
    "materialized_total_bytes": int,
    "artifact_sha256": str,
}
```

Required literals after `validate_exact_object(value, PILOT_SOURCE_MANIFEST_EXACT, "p3-pilot-source-manifest-v1")`:

- `schema_version = p3-pilot-source-manifest-v1`
- `execution_class = PILOT_ONLY`
- `denominator = PILOT_ONLY`
- `p12_item_id`, `neutral_snapshot_id`, `normalized_source_tree_sha256`, `controlled_subject_id`, `controlled_subject_source_id`, and `build_descriptor_sha256` equal the frozen subject identities
- `archive_format` is `ZIP` or `TAR`
- `authorization_a_sha256` equals `502c6407aa368a26948db10cc1ca0d1c91f66c8bfe702aa02f01f275c9df04b6`
- `extractor_policy_sha256` equals `e482ea272a6836099b9dc52deab7d799e24c571c9433fdafe2cff6de48bbb229`
- `predecessor_sha256` equals the sorted list of exactly these three hashes:
  - machine plan file SHA-256 `23d7fb802a2395d93a211862f205065ce1abd52e6ae2e74374aaf2bb624d4cf2`
  - implementation verdict file SHA-256 `e7e5e9519ae49eb08c450c4e16c56d7551528030916d9d8fe88f0ab91a7b1c9d`
  - authorization A SHA-256 `502c6407aa368a26948db10cc1ca0d1c91f66c8bfe702aa02f01f275c9df04b6`
- `artifact_sha256` is `canonical_sha256` of the object with that field removed
- `archive_bytes > 0`
- `materialized_file_count > 0`
- `materialized_total_bytes >= 0`

`archive_sha256` and `archive_bytes` are copied from the `ArchiveSnapshot` that was actually opened. This plan does not invent those production values.

Production path, reserved:

```text
data/p3_v3/pilot/boost_math/source-manifest.json
```

Only a later separately authorized production preparation node may exclusive-create that file. A source-manifest object must fail `validate_pilot_plan`.

---

## Preparation Result Exact Schema

`PILOT_SOURCE_PREPARATION_RESULT_EXACT` has these exact keys and exact types. No extra key is legal.

```python
PILOT_SOURCE_PREPARATION_RESULT_EXACT = {
    "schema_version": str,
    "execution_class": str,
    "denominator": str,
    "p12_item_id": str,
    "neutral_snapshot_id": str,
    "normalized_source_tree_sha256": str,
    "controlled_subject_id": str,
    "controlled_subject_source_id": str,
    "predecessor_sha256": list,
    "terminal_status": str,
    "failure_reason": (str, type(None)),
    "source_manifest_sha256": (str, type(None)),
    "archive_sha256": (str, type(None)),
    "archive_bytes": (int, type(None)),
    "materialized_tree_sha256": (str, type(None)),
    "artifact_sha256": str,
}
```

Production path, reserved:

```text
data/p3_v3/pilot/boost_math/source-preparation-result.json
```

Required rules after `validate_exact_object(value, PILOT_SOURCE_PREPARATION_RESULT_EXACT, "p3-pilot-source-preparation-result-v1")`:

- `schema_version` equals `p3-pilot-source-preparation-result-v1`
- `execution_class` equals `PILOT_ONLY`
- `denominator` equals `PILOT_ONLY`
- subject identity fields equal the frozen labels
- `terminal_status` is `PASS` or `FAIL_INFRASTRUCTURE`
- `artifact_sha256` is `canonical_sha256` of the object with that field removed

PASS rules:

- `failure_reason is None`
- `source_manifest_sha256` is a nonempty SHA-256
- `archive_sha256`, `archive_bytes`, and `materialized_tree_sha256` are nonempty
- `materialized_tree_sha256` equals `93a62859d7fdd6b2068e494bbe6e3e27180b874cbd27055ac27f941e507a90d8`
- `predecessor_sha256` equals the sorted list of the machine-plan hash, the implementation-verdict hash, the authorization A hash, and the source-manifest file SHA-256

FAIL_INFRASTRUCTURE rules:

- `source_manifest_sha256 is None`
- `failure_reason` is exactly one of:
  - `ARCHIVE_UNSAFE`
  - `ARCHIVE_FORMAT_UNSUPPORTED`
  - `EXTRACTION_UNSAFE`
  - `SOURCE_TREE_MISMATCH`
- `predecessor_sha256` equals the sorted list of only the machine-plan hash, the implementation-verdict hash, and the authorization A hash

Authorization missing or invalid: create no result, because preparation is not authorized. Implementation-verdict or machine-plan absence, hash mismatch, or non-PASS state: raise `E_PILOT_SOURCE_IDENTITY` and create no result. If either reserved output path already exists: raise `E_PILOT_SOURCE_OUTPUT_EXISTS`, do not overwrite, and do not create a second result. Both production outputs are exclusive-create.

Error-code mapping:

| Code | When | Writes result |
|---|---|---|
| `E_PILOT_PREPARATION_AUTH_ABSENT` | authorization file absent | no |
| `E_PILOT_PREPARATION_AUTH` | authorization bytes or hash differ | no |
| `E_PILOT_SOURCE_IDENTITY` | verdict or plan missing, hash mismatch, or non-PASS; subject label mismatch | no |
| `E_PILOT_SOURCE_OUTPUT_EXISTS` | reserved output already exists | no |
| `E_PILOT_ARCHIVE_UNSAFE` | snapshot rejects the archive path or identity | yes, `ARCHIVE_UNSAFE` |
| `E_PILOT_ARCHIVE_FORMAT` | unsupported, corrupt, or ambiguous format | yes, `ARCHIVE_FORMAT_UNSUPPORTED` |
| `E_PILOT_EXTRACT_UNSAFE` | extractor policy violation | yes, `EXTRACTION_UNSAFE` |
| `E_PILOT_SOURCE_TREE_MISMATCH` | materialized tree hash differs | yes, `SOURCE_TREE_MISMATCH` |

Result writes in the last four rows happen only after authorization A, the implementation verdict, and the machine plan have already validated, and only to the result path constant (production or a test monkeypatch). They still do not write a source manifest.

---

## Production Gate Interface

The later implementation may add exactly one new verb to `scripts/p3_v3/pilot.py`:

```text
validate-source
```

The parser accepts only:

- `--archive`
- `--materialize-root`

The parser must not accept:

- authorization path
- output path
- expected archive hash
- expected tree hash
- expected build descriptor hash
- implementation verdict path
- machine plan path
- extractor policy override

All of those authority paths, output paths, and frozen identities are module constants in `src/p3_v3/pilot_source.py`.

Existing `tests/p3_v3/test_cli.py::test_pilot_cli_forbids_source_and_execution_verbs` calls `parse_args(["validate-source"])` and expects `SystemExit`. Keep `--archive` and `--materialize-root` required so that call still exits. Do not modify `tests/p3_v3/test_cli.py`. Do not add a default archive path.

This plan does not contain an executable production command that names a fictional archive path. The real production command is written only in a later user-authorized, separately reviewed launch packet.

```python
from __future__ import annotations

import argparse


def add_validate_source_parser(sub: argparse._SubParsersAction) -> None:
    command = sub.add_parser("validate-source")
    command.add_argument("--archive", required=True)
    command.add_argument("--materialize-root", required=True)
```

`write-plan` and `validate-plan` remain. Forbidden verbs remain `extract`, `freeze`, `execute`, and `certify`.

---

## Explicitly Forbidden Extensions

The later implementation task must not:

- download or clone Boost.Math;
- read Package C or a P12 reveal;
- read buggy revisions, patches, reference or evaluated MRs, or outcomes;
- run CMake, a compiler, CTest, or public behavior;
- design a contract, site, MR, mutant, or certification;
- create a freeze, execution plan, attempt, score task, ledger event, or evidence package;
- modify confirmatory schemas;
- modify the claim ledger;
- interpret a source manifest as build PASS or scientific PASS;
- interpret a capability unit test as production preparation;
- create authorization A;
- enter production preparation automatically;
- create any file under `data/p3_v3/pilot/boost_math/`.

---

### Task 1: Pilot Source-Preparation Capability On Synthetic Fixtures

**Files:**
- Create: `src/p3_v3/pilot_source.py`, `tests/p3_v3/test_pilot_source.py`
- Modify: `scripts/p3_v3/pilot.py`, `tests/p3_v3/test_pilot.py`
- Do not create: `data/p3_v3/pilot/boost_math/user-auth-preparation.txt`, `data/p3_v3/pilot/boost_math/source-manifest.json`, `data/p3_v3/pilot/boost_math/source-preparation-result.json`

**Interfaces:**
- Consumes: `validate_exact_object(value, schema, context)`, `canonical_sha256`, `validate_sha256`, `write_canonical_json`, `read_canonical_json`, `read_regular_file_snapshot`, `EvidenceError`, `SourceSnapshot`, `SourceSnapshotEntry`, `canonical_source_tree_sha256`, the frozen implementation verdict, and the frozen machine plan
- Produces: `ArchiveSnapshot`, `read_production_archive_bytes`, `EXTRACTOR_POLICY_V1`, source-manifest and preparation-result validators, a fail-closed extractor, a `validate-source` CLI verb, and synthetic-fixture unit tests
- Does not produce: a production source manifest, a production preparation result, authorization A, a freeze, an execution plan, a claim-ledger write, or a production launch packet

User authorization required: no. Gate: capability implementation only. This planning node does not start the gate. Capability PASS does not authorize production preparation.

- [ ] **Step 1: Confirm the confirmatory baseline before any edit**

Run:

```text
env \
  GIT_CONFIG_GLOBAL=/dev/null \
  GIT_CONFIG_NOSYSTEM=1 \
  GIT_CONFIG_COUNT=0 \
  PYTHONPATH=src \
  python3 -m pytest tests/p3_v3 -q
```

Expected: exit 0. Do not edit until that baseline is green.

- [ ] **Step 2: Write the failing tests**

Create `tests/p3_v3/test_pilot_source.py` with at least these exact names:

```python
REQUIRED_SOURCE_PREPARATION_TESTS = [
    "test_authorization_absent_writes_no_output",
    "test_authorization_wrong_bytes_writes_no_output",
    "test_implementation_verdict_hash_mismatch_fails_closed",
    "test_machine_plan_hash_mismatch_fails_closed",
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
    "test_single_top_level_selection_is_order_invariant",
    "test_materialized_tree_uses_phase1_canonical_hash",
    "test_wrong_materialized_tree_writes_failure_result",
    "test_source_manifest_exact_keys",
    "test_source_manifest_predecessors_are_exact",
    "test_source_manifest_cannot_validate_as_pilot_plan",
    "test_pass_result_binds_source_manifest",
    "test_outputs_are_exclusive",
    "test_validate_source_cli_has_no_authority_overrides",
    "test_capability_implementation_creates_no_production_artifact",
]
```

Minimum bodies that the later task must implement:

```python
from __future__ import annotations

from pathlib import Path

import pytest

from p3_v3.artifacts import EvidenceError


def test_authorization_absent_writes_no_output(tmp_path, monkeypatch):
    import p3_v3.pilot_source as pilot_source

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


def test_archive_snapshot_hashes_same_fd_bytes(tmp_path):
    from p3_v3.pilot_source import read_production_archive_bytes

    archive = tmp_path / "fixture.zip"
    archive.write_bytes(b"PK\x03\x04" + b"synthetic-zip-bytes")
    snapshot = read_production_archive_bytes(archive)
    assert snapshot.sha256 == __import__("hashlib").sha256(snapshot.raw).hexdigest()
    assert snapshot.size == len(snapshot.raw)
    assert snapshot.archive_format == "ZIP"


def test_materialized_tree_uses_phase1_canonical_hash(tmp_path):
    from p3_v3.bridge_and_frames import (
        SourceSnapshot,
        SourceSnapshotEntry,
        canonical_source_tree_sha256,
    )
    from p3_v3.pilot_source import capture_materialized_tree

    payload = tmp_path / "payload"
    payload.mkdir()
    (payload / "readme.txt").write_bytes(b"synthetic\n")
    snapshot = capture_materialized_tree(payload)
    assert isinstance(snapshot, SourceSnapshot)
    assert all(isinstance(item, SourceSnapshotEntry) for item in snapshot.entries)
    assert canonical_source_tree_sha256(snapshot) == canonical_source_tree_sha256(
        snapshot
    )


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
```

Also add, in `tests/p3_v3/test_pilot.py`, a CLI acceptance check that `validate-source` exists and accepts only `--archive` and `--materialize-root`. Keep every existing foundation assertion. Keep `p3_v3.pilot` free of `write_source_manifest` and `validate_pilot_source_manifest`; those names, if present, live only on `p3_v3.pilot_source`.

Synthetic ZIP and TAR fixtures are built at runtime with `zipfile` and `tarfile` in `tmp_path`. Do not read, mount, or unpack a real Boost.Math archive.

- [ ] **Step 3: Run RED**

Run:

```text
env \
  GIT_CONFIG_GLOBAL=/dev/null \
  GIT_CONFIG_NOSYSTEM=1 \
  GIT_CONFIG_COUNT=0 \
  PYTHONPATH=src \
  python3 -m pytest tests/p3_v3/test_pilot_source.py -q
```

Expected: exit 1 because `p3_v3.pilot_source` does not yet exist.

- [ ] **Step 4: Write the minimal implementation**

`src/p3_v3/pilot_source.py` must define the constants, `ArchiveSnapshot`, `read_production_archive_bytes`, `EXTRACTOR_POLICY_V1`, authorization verification, extractor, tree capture, `PILOT_SOURCE_MANIFEST_EXACT`, `PILOT_SOURCE_PREPARATION_RESULT_EXACT`, validators, and `run_validate_source(archive, materialize_root)`.

`scripts/p3_v3/pilot.py` gains only the `validate-source` verb specified above. It calls `run_validate_source` with the two parsed paths and no other caller-supplied authority.

Production constants remain the reserved paths. Tests monkeypatch those constants. The capability task still does not create a file under `data/p3_v3/pilot/boost_math/`.

- [ ] **Step 5: Run minimum GREEN**

Run:

```text
env \
  GIT_CONFIG_GLOBAL=/dev/null \
  GIT_CONFIG_NOSYSTEM=1 \
  GIT_CONFIG_COUNT=0 \
  PYTHONPATH=src \
  python3 -m pytest \
  tests/p3_v3/test_pilot_source.py \
  tests/p3_v3/test_pilot.py \
  -q
```

Expected: exit 0.

- [ ] **Step 6: Run the complete confirmatory suite**

Run:

```text
env \
  GIT_CONFIG_GLOBAL=/dev/null \
  GIT_CONFIG_NOSYSTEM=1 \
  GIT_CONFIG_COUNT=0 \
  PYTHONPATH=src \
  python3 -m pytest tests/p3_v3 -q
```

Expected: exit 0. Existing confirmatory tests must keep passing. `test_pilot_cli_forbids_source_and_execution_verbs` must still see `SystemExit` for `parse_args(["validate-source"])` because the two arguments remain required.

- [ ] **Step 7: Stop for independent implementation review**

Stage only the approved Create and Modify paths. Do not create authorization A. Do not create a production source manifest. Do not create a production preparation result. Do not enter production preparation. Requested state after this task is an independent capability implementation review candidate. Task 1 PASS does not authorize real preparation.

---

## Commands This Planning Node Must Not Run

The pytest commands above are future implementation commands. This planning node must not run them. This planning node must not run a build, preflight, profiling, mutant, MR, or production command.

---

## Stop Conditions

Stop immediately if implementation would require:

- modifying a file outside the approved map;
- creating authorization A;
- creating a production source manifest or preparation result;
- reading a real Boost.Math archive;
- designing contract, site, MR, mutant, certification, execution, or evidence-closure procedures;
- changing an authority, protocol, ledger, or Frame file;
- treating a capability PASS as production authorization;
- treating a source manifest as build PASS or scientific PASS.

---

## Claim Ceiling

`claims=blocked`. Formal denominator membership is false. RQ4 is not supported. The claim ledger must remain byte-identical to `bf4979662697b2d0565bb70eec88b22673e84bee93b61234555342efb4082a68`.
