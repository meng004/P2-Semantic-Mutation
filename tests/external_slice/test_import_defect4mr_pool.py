"""Contract tests for the one-shot Defect4MR sanitized import (Task C1)."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
IMPORT_DIR = REPO_ROOT / "data" / "external_slice" / "defect4mr_import"
SANITIZED = IMPORT_DIR / "candidates_sanitized.json"
PROVENANCE = IMPORT_DIR / "PROVENANCE.json"
IMPORT_LOG = IMPORT_DIR / "IMPORT_LOG.md"

PINNED_REPO = "meng004/P12-Defect4MR"
PINNED_COMMIT = "2bf7c2401c846544e715d879eb639e8c3bf44067"
PINNED_PATH = "data/ledgers/candidates.json"
PINNED_BLOB = "1469a2e2b15dcb2cdf59d185f3ec92f58fb77189"

ALLOWED_KEYS = {
    "provisional_id",
    "project",
    "status",
    "evidence_depth",
    "source_urls",
    "revisions",
    "modified_files",
    "exclusions_checked",
}
FORBIDDEN_KEYS = {
    "mr_mapping",
    "proposed_mr_oracle",
    "reviewer_note",
    "reproduction_risk",
    "family",
}
LEAK_PATTERN = re.compile(
    r"(?i)mr_mapping|proposed_mr_oracle|reviewer_note|reproduction_risk|"
    r"\bkill\b|fiber|operator|mutation|analysis_id|analysis_alias"
)
STATUS_COUNTS = {
    "verified_full": 35,
    "candidate_full": 16,
    "rejected": 12,
    "candidate_needs_oracle": 1,
}


def _load_module():
    import importlib.util

    path = REPO_ROOT / "scripts" / "external_slice" / "import_defect4mr_pool.py"
    spec = importlib.util.spec_from_file_location("import_defect4mr_pool", path)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_pinned_constants():
    mod = _load_module()
    assert mod.DEFAULT_REPO == PINNED_REPO
    assert mod.DEFAULT_COMMIT == PINNED_COMMIT
    assert mod.DEFAULT_PATH == PINNED_PATH
    assert mod.DEFAULT_BLOB_SHA == PINNED_BLOB


def test_git_blob_sha_matches_pinned_fixture():
    mod = _load_module()
    sample = b'[{"provisional_id":"X"}]\n'
    expected = hashlib.sha1(b"blob " + str(len(sample)).encode() + b"\0" + sample).hexdigest()
    assert mod.git_blob_sha(sample) == expected


def test_sanitize_record_keeps_only_allowed_keys():
    mod = _load_module()
    raw = {
        "provisional_id": "B-FFTW-001",
        "project": "FFTW",
        "family": "Family B",
        "status": "candidate_full",
        "evidence_depth": "full",
        "source_urls": ["https://example.com/issue/1"],
        "revisions": {
            "buggy": "see reviewer_note for cloud session",
            "fixed": "unknown",
        },
        "modified_files": [],
        "mr_mapping": {"secret": True},
        "proposed_mr_oracle": {"secret": True},
        "exclusions_checked": {"api_only": True},
        "reproduction_risk": "low",
        "reviewer_note": "leaky",
    }
    cleaned = mod.sanitize_record(raw)
    assert set(cleaned) == ALLOWED_KEYS
    assert not FORBIDDEN_KEYS.intersection(cleaned)
    assert LEAK_PATTERN.search(json.dumps(cleaned, ensure_ascii=False)) is None
    assert "reviewer_note" not in cleaned["revisions"]["buggy"]


def test_sanitized_artifact_exists_and_has_provenance():
    assert SANITIZED.is_file(), "candidates_sanitized.json missing; run import script"
    assert PROVENANCE.is_file(), "PROVENANCE.json missing; run import script"
    assert IMPORT_LOG.is_file(), "IMPORT_LOG.md missing; run import script"


def test_sanitized_census_and_uniqueness():
    rows = json.loads(SANITIZED.read_text(encoding="utf-8"))
    assert isinstance(rows, list)
    assert len(rows) == 64
    counts = {status: 0 for status in STATUS_COUNTS}
    ids = []
    for row in rows:
        counts[row["status"]] = counts.get(row["status"], 0) + 1
        ids.append(row["provisional_id"])
    assert counts == STATUS_COUNTS
    assert len(ids) == len(set(ids))


def test_sanitized_schema_and_no_leaks():
    rows = json.loads(SANITIZED.read_text(encoding="utf-8"))
    for row in rows:
        assert set(row) == ALLOWED_KEYS
        assert not FORBIDDEN_KEYS.intersection(row)
    text = ""
    for path in IMPORT_DIR.rglob("*"):
        if path.is_file():
            text += path.read_text(encoding="utf-8", errors="replace")
            text += "\n"
    assert LEAK_PATTERN.search(text) is None


def test_provenance_pins_source_and_hashes():
    prov = json.loads(PROVENANCE.read_text(encoding="utf-8"))
    assert prov["repo"] == PINNED_REPO
    assert prov["commit"] == PINNED_COMMIT
    assert prov["path"] == PINNED_PATH
    assert prov["blob_sha"] == PINNED_BLOB
    assert prov["counts"] == {"total": 64, **STATUS_COUNTS}
    assert isinstance(prov["sanitized_sha256"], str) and len(prov["sanitized_sha256"]) == 64


def test_raw_ledger_not_committed_under_repo():
    forbidden_names = {
        "candidates.json",
        "candidates_raw.json",
        "candidates_original.json",
    }
    for path in (REPO_ROOT / "data" / "external_slice").rglob("*"):
        if path.is_file() and path.name in forbidden_names:
            pytest.fail(f"raw ledger must not be stored in P3 repo: {path}")
    # Explicitly ensure the sanitized path is the only candidates* artifact.
    candidates_files = list((REPO_ROOT / "data" / "external_slice").rglob("candidates*.json"))
    assert candidates_files == [SANITIZED]
