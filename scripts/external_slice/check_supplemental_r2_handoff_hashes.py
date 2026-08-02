#!/usr/bin/env python3
"""Verify supplemental R2 handoff SHA-256 bindings and SELF parent relationship."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_self_commit(handoff: dict[str, Any], *, cwd: Path) -> str | None:
    """Resolve handoff_commit.value SELF to current HEAD when present."""
    hc = handoff.get("handoff_commit") or {}
    value = hc.get("value")
    if value != "SELF":
        return value
    proc = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        return None
    return proc.stdout.strip()


def verify_parent_relationship(
    handoff: dict[str, Any], *, cwd: Path, handoff_commit: str | None
) -> list[str]:
    errors: list[str] = []
    hc = handoff.get("handoff_commit") or {}
    required_parent = hc.get("direct_parent_required") or handoff.get("payload_commit")
    if not required_parent:
        errors.append("missing direct_parent_required / payload_commit")
        return errors
    if handoff.get("payload_commit") and handoff["payload_commit"] != required_parent:
        # payload_commit should equal required parent.
        if handoff["payload_commit"] != required_parent:
            errors.append("payload_commit != direct_parent_required")
    if not handoff_commit:
        errors.append("unable to resolve handoff commit")
        return errors
    proc = subprocess.run(
        ["git", "rev-parse", f"{handoff_commit}^"],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        # When SELF points at a commit that is not yet created / or detached fixture,
        # allow explicit provided parent check via optional skip only if git fails
        # because HEAD has no parent — still report.
        errors.append(f"unable to resolve parent of {handoff_commit}")
        return errors
    actual_parent = proc.stdout.strip()
    if actual_parent != required_parent:
        errors.append(
            f"handoff parent mismatch: expected {required_parent}, got {actual_parent}"
        )
    return errors


def _resolve_declared_path(rel: str, *, handoff_path: Path, cwd: Path) -> Path | None:
    """Resolve a handoff-relative path against root, cwd, or repo root."""
    candidates = [
        handoff_path.parent / rel,
        cwd / rel,
        Path(__file__).resolve().parents[2] / rel,
    ]
    # Also allow repo-prefixed keys written historically.
    if rel.startswith("data/external_slice/supplemental_r2/"):
        suffix = rel.split("data/external_slice/supplemental_r2/", 1)[1]
        candidates.insert(0, handoff_path.parent / suffix)
    return next((p for p in candidates if p.is_file()), None)


def verify_handoff_hashes(
    handoff_path: Path,
    *,
    cwd: Path | None = None,
    check_parent: bool = True,
    git_cwd: Path | None = None,
) -> int:
    cwd = cwd or Path.cwd()
    git_cwd = git_cwd or cwd
    handoff = load_json(handoff_path)
    mismatches: list[str] = []

    for rel, expected in (handoff.get("file_sha256") or {}).items():
        path = _resolve_declared_path(rel, handoff_path=handoff_path, cwd=cwd)
        if path is None:
            mismatches.append(f"missing file {rel}")
            continue
        actual = sha256_file(path)
        if actual != expected:
            mismatches.append(f"{rel}: expected {expected}, got {actual}")

    for rel, expected in (handoff.get("evidence_sha256") or {}).items():
        path = _resolve_declared_path(rel, handoff_path=handoff_path, cwd=cwd)
        if path is None:
            mismatches.append(f"missing evidence {rel}")
            continue
        actual = sha256_file(path)
        if actual != expected:
            mismatches.append(f"{rel}: expected {expected}, got {actual}")

    # SELF resolution always attempted for reporting.
    resolved = resolve_self_commit(handoff, cwd=git_cwd)
    if (handoff.get("handoff_commit") or {}).get("value") == "SELF" and not resolved:
        mismatches.append("SELF resolution failed")

    if check_parent and (handoff.get("handoff_commit") or {}).get(
        "direct_parent_required"
    ):
        mismatches.extend(
            verify_parent_relationship(
                handoff, cwd=git_cwd, handoff_commit=resolved
            )
        )

    if mismatches:
        print("HASH_CHECK_FAIL", file=sys.stderr)
        for item in mismatches:
            print(f"ERROR: {item}", file=sys.stderr)
        return 1
    print("HASH_CHECK_OK")
    print(f"handoff_commit_resolved={resolved}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--handoff", type=Path, required=True)
    parser.add_argument(
        "--skip-parent-check",
        action="store_true",
        help="Skip git parent relationship check (fixture use)",
    )
    args = parser.parse_args(argv)
    return verify_handoff_hashes(
        args.handoff, check_parent=not args.skip_parent_check
    )


if __name__ == "__main__":
    raise SystemExit(main())
