"""Custodian helper: build the P12-bound blinded fixed-snapshot bridge.

Run by the P12 custodian (scientific plan section 5.1.1). Reads a custodian
config, computes every record hash with the exact P3 formulas (the normalized
source tree hash is imported from the frozen controller module, so the bytes
cannot drift), draws one fresh 32-byte reveal nonce per record, and writes:

- ``bridge.json`` — canonical bridge to commit into the P12 repository;
- ``consumer_lock.template.json`` — P3-side lock with commit/blob fields to
  fill in after the release commit exists;
- ``reveal_ledger.SEALED.json`` — per-record ``fixed_git_tree_oid`` +
  ``reveal_nonce``: **Package C material. Keep custodian-side. Never deliver
  to P3 before Phase 7.**
- ``receipts.txt`` — hash receipts including the package-root method.

The bridge must never contain buggy commits, defect patches, issue/PR
identities, defect families, reference MRs, or outcomes. Config schema:

{
  "p12_repository_identity": "github.com/meng004/P12-Defect4MR",
  "p12_repo_root": "/abs/path/to/P12-Defect4MR",
  "p12_contract_path": "repo-relative/path/to/contract.md",
  "p12_package_root_sha256": "<64 hex>"            (either this ...)
  "package_manifest_root": "/abs/path/to/package"   (... or this),
  "records": [
    {
      "label": "custodian-local label (never written into the bridge)",
      "snapshot_dir": "/abs/path/to/exported/fixed-source",
      "source_archive": "/abs/path/to/fixed-source.tar",
      "build_descriptor": "/abs/path/to/build_descriptor.json",
      "fixed_git_tree_oid": "<40 hex git tree oid>",
      "eligibility_reason": "free text",
      "eligible_for_construct": true,
      "eligible_for_criterion": true
    }
  ]
}
"""

from __future__ import annotations

import argparse
import hashlib
import json
import secrets
import stat
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from p3_v3.artifacts import canonical_json_bytes, canonical_sha256  # noqa: E402
from p3_v3.bridge_and_frames import (  # noqa: E402
    SourceSnapshot,
    SourceSnapshotEntry,
    canonical_source_tree_sha256,
)

_TREE_OID_HEX = frozenset("0123456789abcdef")


def _fail(message: str) -> None:
    raise SystemExit(f"custodian-bridge: {message}")


def _snapshot_from_dir(root: Path) -> SourceSnapshot:
    if not root.is_dir():
        _fail(f"snapshot_dir is not a directory: {root}")
    entries: list[SourceSnapshotEntry] = []
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            _fail(f"snapshot contains a symlink (deliver plain files only): {path}")
        if path.is_dir():
            continue
        if not path.is_file():
            _fail(f"snapshot contains a special node: {path}")
        raw = path.read_bytes()
        mode = (
            "100755"
            if path.stat().st_mode & stat.S_IXUSR
            else "100644"
        )
        entries.append(
            SourceSnapshotEntry(
                relative_path=path.relative_to(root).as_posix(),
                mode=mode,
                sha256=hashlib.sha256(raw).hexdigest(),
                content=raw,
            )
        )
    entries.sort(key=lambda entry: entry.relative_path.encode("utf-8"))
    if not entries:
        _fail(f"snapshot_dir is empty: {root}")
    return SourceSnapshot(entries=tuple(entries))


def _file_sha256(path: Path, context: str) -> str:
    if not path.is_file():
        _fail(f"{context} is not a file: {path}")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git_blob_sha1(raw: bytes) -> str:
    """Content-addressed Git blob OID (SHA-1 object format repositories)."""

    return hashlib.sha1(  # noqa: S324 - Git's own object addressing
        b"blob " + str(len(raw)).encode("ascii") + b"\x00" + raw
    ).hexdigest()


def _canonical_file_sha256(path: Path, context: str) -> str:
    raw = path.read_bytes() if path.is_file() else None
    if raw is None:
        _fail(f"{context} is not a file: {path}")
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        _fail(f"{context} is not valid JSON: {path}")
    if canonical_json_bytes(value) != raw:
        _fail(
            f"{context} is not canonical JSON (sorted keys, compact separators, "
            f"one trailing LF): {path}"
        )
    return hashlib.sha256(raw).hexdigest()


def _package_root(config: dict[str, Any]) -> tuple[str, str]:
    explicit = config.get("p12_package_root_sha256")
    manifest_root = config.get("package_manifest_root")
    if explicit is not None:
        if not isinstance(explicit, str) or len(explicit) != 64:
            _fail("p12_package_root_sha256 must be 64 hex characters")
        return explicit, "explicit value supplied by custodian config"
    if not isinstance(manifest_root, str) or not manifest_root:
        _fail("supply p12_package_root_sha256 or package_manifest_root")
    root = Path(manifest_root)
    if not root.is_dir():
        _fail(f"package_manifest_root is not a directory: {root}")
    files = []
    for path in sorted(root.rglob("*")):
        if path.is_symlink() or not path.is_file():
            continue
        files.append(
            {
                "path": path.relative_to(root).as_posix(),
                "byte_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }
        )
    if not files:
        _fail(f"package_manifest_root is empty: {root}")
    digest = canonical_sha256({"domain": "P12-PACKAGE-ROOT-v1", "files": files})
    return digest, (
        "canonical manifest over package_manifest_root "
        f"({len(files)} files, domain P12-PACKAGE-ROOT-v1)"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    config = json.loads(Path(args.config).read_text(encoding="utf-8"))
    for field in ("p12_repository_identity", "p12_repo_root", "p12_contract_path"):
        if not isinstance(config.get(field), str) or not config[field]:
            _fail(f"config field {field} is required")
    records_config = config.get("records")
    if not isinstance(records_config, list) or not records_config:
        _fail("config.records must be a non-empty list")

    contract_file = Path(config["p12_repo_root"]) / config["p12_contract_path"]
    if not contract_file.is_file():
        _fail(f"p12 contract is not a file: {contract_file}")
    contract_raw = contract_file.read_bytes()
    contract_sha256 = hashlib.sha256(contract_raw).hexdigest()
    contract_blob_sha = _git_blob_sha1(contract_raw)
    package_root, package_root_method = _package_root(config)

    records: list[dict[str, Any]] = []
    sealed: list[dict[str, Any]] = []
    receipts: list[str] = []
    seen_labels: set[str] = set()
    for index, item in enumerate(records_config):
        label = item.get("label")
        if not isinstance(label, str) or not label or label in seen_labels:
            _fail(f"records[{index}].label must be a unique non-empty string")
        seen_labels.add(label)
        tree_oid = item.get("fixed_git_tree_oid")
        if (
            not isinstance(tree_oid, str)
            or len(tree_oid) != 40
            or set(tree_oid) - _TREE_OID_HEX
        ):
            _fail(f"records[{index}].fixed_git_tree_oid must be 40 lowercase hex")
        reason = item.get("eligibility_reason")
        if not isinstance(reason, str) or not reason:
            _fail(f"records[{index}].eligibility_reason is required")
        for flag in ("eligible_for_construct", "eligible_for_criterion"):
            if not isinstance(item.get(flag), bool):
                _fail(f"records[{index}].{flag} must be a boolean")

        snapshot = _snapshot_from_dir(Path(item["snapshot_dir"]))
        normalized = canonical_source_tree_sha256(snapshot)
        archive_sha256 = _file_sha256(
            Path(item["source_archive"]), f"records[{index}].source_archive"
        )
        descriptor_sha256 = _canonical_file_sha256(
            Path(item["build_descriptor"]), f"records[{index}].build_descriptor"
        )
        neutral = canonical_sha256(
            {
                "p12_package_root_sha256": package_root,
                "normalized_source_tree_sha256": normalized,
                "source_archive_sha256": archive_sha256,
                "domain": "P3-NEUTRAL-SNAPSHOT-v1",
            }
        )
        nonce = secrets.token_bytes(32)
        commitment = hashlib.sha256(
            b"P3-FIXED-TREE-v1"
            + package_root.encode("ascii")
            + tree_oid.encode("ascii")
            + nonce
        ).hexdigest()
        records.append(
            {
                "neutral_snapshot_id": neutral,
                "fixed_tree_commitment": commitment,
                "normalized_source_tree_sha256": normalized,
                "source_archive_sha256": archive_sha256,
                "build_descriptor_sha256": descriptor_sha256,
                "eligibility_reason": reason,
                "eligible_for_construct": item["eligible_for_construct"],
                "eligible_for_criterion": item["eligible_for_criterion"],
            }
        )
        sealed.append(
            {
                "label": label,
                "neutral_snapshot_id": neutral,
                "fixed_git_tree_oid": tree_oid,
                "reveal_nonce": nonce.hex(),
                "normalized_source_tree_sha256": normalized,
            }
        )
        receipts.append(f"{neutral}  record[{index}] ({label})")

    records.sort(key=lambda record: record["neutral_snapshot_id"])
    if len({record["fixed_tree_commitment"] for record in records}) != len(records):
        _fail("duplicate fixed-tree commitment (identical tree+nonce collision)")
    body = {
        "schema_version": "p3-p12-bridge-v1",
        "p12_release_id": config.get("p12_release_id", "p12-bridge-release-v1"),
        "p12_repository_identity": config["p12_repository_identity"],
        "p12_contract_path": config["p12_contract_path"],
        "p12_contract_blob_sha": contract_blob_sha,
        "p12_package_root_sha256": package_root,
        "p12_contract_sha256": contract_sha256,
        "eligible_inventory_root_sha256": canonical_sha256(records),
        "eligible_item_count": len(records),
        "records": records,
        "trust_mode": "PINNED_GIT_RELEASE",
    }
    bridge = {**body, "artifact_sha256": canonical_sha256(body)}

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    bridge_raw = canonical_json_bytes(bridge)
    (output_dir / "bridge.json").write_bytes(bridge_raw)
    lock_template = {
        "repository_identity": config["p12_repository_identity"],
        "release_commit_sha": "FILL_AFTER_COMMIT",
        "bridge_path": config.get("bridge_path", "bridge/p3_bridge_v1.json"),
        "bridge_blob_sha": _git_blob_sha1(bridge_raw),
        "contract_path": config["p12_contract_path"],
        "contract_blob_sha": contract_blob_sha,
        "package_root_sha256": package_root,
    }
    (output_dir / "consumer_lock.template.json").write_bytes(
        canonical_json_bytes(lock_template)
    )
    (output_dir / "reveal_ledger.SEALED.json").write_bytes(
        canonical_json_bytes(
            {
                "warning": (
                    "PACKAGE C MATERIAL - keep sealed with the custodian; "
                    "deliver to P3 only at Phase 7 reveal"
                ),
                "records": sealed,
            }
        )
    )
    receipt_lines = [
        f"package_root {package_root} ({package_root_method})",
        f"contract sha256 {contract_sha256} blob {contract_blob_sha}",
        f"bridge artifact_sha256 {bridge['artifact_sha256']}",
        f"bridge git blob {_git_blob_sha1(bridge_raw)}",
        f"eligible_item_count {len(records)}",
        *receipts,
        "",
        "Commit bridge.json (path = lock template bridge_path) and the contract",
        "into the P12 repository, then fill release_commit_sha in the lock with",
        "`git rev-parse HEAD`. Blob SHAs above assume the SHA-1 object format;",
        "verify with `git hash-object bridge.json` if in doubt. Re-running this",
        "script redraws reveal nonces and changes every commitment.",
    ]
    (output_dir / "receipts.txt").write_text(
        "\n".join(receipt_lines) + "\n", encoding="utf-8"
    )
    for line in receipt_lines[:4]:
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
