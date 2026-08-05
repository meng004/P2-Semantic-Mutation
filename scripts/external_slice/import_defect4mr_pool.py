#!/usr/bin/env python3
"""One-shot sanitized import of the pinned Defect4MR 64-pool ledger (Task C1).

Fetches ``data/ledgers/candidates.json`` from a fixed private-repo commit,
verifies the git blob SHA, emits a field-restricted manifest, and writes
provenance / import logs. The raw ledger is never written under the P3 tree.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import urllib.error
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_REPO = "meng004/P12-Defect4MR"
DEFAULT_COMMIT = "2bf7c2401c846544e715d879eb639e8c3bf44067"
DEFAULT_PATH = "data/ledgers/candidates.json"
DEFAULT_BLOB_SHA = "1469a2e2b15dcb2cdf59d185f3ec92f58fb77189"

ALLOWED_KEYS = (
    "provisional_id",
    "project",
    "status",
    "evidence_depth",
    "source_urls",
    "revisions",
    "modified_files",
    "exclusions_checked",
)

# Vocabulary that must not appear in the sanitized import directory.
# Includes accidental field-name references inside free-text revision notes.
LEAK_RE = re.compile(
    r"(?i)mr_mapping|proposed_mr_oracle|reviewer_note|reproduction_risk|"
    r"\bkill\b|fiber|operator|mutation|analysis_id|analysis_alias"
)

STATUS_EXPECT = {
    "verified_full": 35,
    "candidate_full": 16,
    "rejected": 12,
    "candidate_needs_oracle": 1,
}


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _auth_token() -> str | None:
    for key in ("github_token", "GITHUB_TOKEN", "GH_TOKEN"):
        value = os.environ.get(key)
        if value:
            return value
    return None


def fetch_raw_ledger(
    repo: str,
    commit: str,
    path: str,
    *,
    source_file: Path | None = None,
) -> bytes:
    if source_file is not None:
        return source_file.read_bytes()

    token = _auth_token()
    if not token:
        raise RuntimeError(
            "No GitHub token in github_token/GITHUB_TOKEN/GH_TOKEN; "
            "pass --source-file for an offline pinned copy"
        )

    url = (
        f"https://api.github.com/repos/{repo}/contents/"
        f"{path}?ref={commit}"
    )
    request = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.raw+json",
            "User-Agent": "p3-defect4mr-sanitized-import",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            return response.read()
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"GitHub fetch failed HTTP {exc.code}: {body}") from exc


def _redact_string(value: str) -> str:
    return LEAK_RE.sub("[redacted]", value)


def _sanitize_value(value: Any) -> Any:
    if isinstance(value, str):
        return _redact_string(value)
    if isinstance(value, list):
        return [_sanitize_value(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _sanitize_value(item) for key, item in value.items()}
    return value


def sanitize_record(record: dict[str, Any]) -> dict[str, Any]:
    cleaned: dict[str, Any] = {}
    for key in ALLOWED_KEYS:
        if key not in record:
            raise KeyError(f"source record missing required key: {key}")
        cleaned[key] = _sanitize_value(record[key])
    return cleaned


def sanitize_pool(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [sanitize_record(row) for row in rows]


def validate_census(rows: list[dict[str, Any]]) -> dict[str, int]:
    if len(rows) != 64:
        raise ValueError(f"expected 64 rows, got {len(rows)}")
    ids = [row["provisional_id"] for row in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("provisional_id values are not unique")
    counts = Counter(row["status"] for row in rows)
    expected = Counter(STATUS_EXPECT)
    if counts != expected:
        raise ValueError(f"status distribution mismatch: {dict(counts)} != {dict(expected)}")
    return {"total": 64, **STATUS_EXPECT}


def assert_no_leaks(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    match = LEAK_RE.search(text)
    if match:
        raise ValueError(f"leak token {match.group(0)!r} found in {path}")


def write_json(path: Path, payload: Any) -> bytes:
    data = (json.dumps(payload, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return data


def build_import_log(
    *,
    repo: str,
    commit: str,
    path: str,
    blob_sha: str,
    counts: dict[str, int],
    sanitized_sha256: str,
    source_mode: str,
) -> str:
    # Avoid naming stripped field identifiers so the import directory stays clean.
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    allowed = ", ".join(ALLOWED_KEYS)
    return f"""# Defect4MR sanitized import log

- UTC time: {now}
- Source mode: {source_mode}
- Repository: `{repo}`
- Commit: `{commit}`
- Ledger path: `{path}`
- Verified git blob SHA: `{blob_sha}`
- Row count: {counts['total']}
- Status census: verified_full={counts['verified_full']}, candidate_full={counts['candidate_full']}, rejected={counts['rejected']}, candidate_needs_oracle={counts['candidate_needs_oracle']}
- Allowed output keys: {allowed}
- Dropped non-allowed source keys: yes (mechanical key filter)
- Free-text redaction of reserved vocabulary: enabled
- Sanitized SHA256: `{sanitized_sha256}`
- Raw ledger written into P3 tree: no

This import session is retired after producing the sanitized manifest.
It must not adjudicate admission, annotation, prediction, or later execution results.
"""


def run_import(
    *,
    repo: str,
    commit: str,
    path: str,
    output: Path,
    expected_blob: str,
    source_file: Path | None = None,
) -> dict[str, Any]:
    raw = fetch_raw_ledger(repo, commit, path, source_file=source_file)
    blob_sha = git_blob_sha(raw)
    if blob_sha != expected_blob:
        raise ValueError(f"blob SHA mismatch: got {blob_sha}, expected {expected_blob}")

    rows = json.loads(raw.decode("utf-8"))
    if not isinstance(rows, list):
        raise ValueError("ledger root must be a JSON array")

    sanitized = sanitize_pool(rows)
    counts = validate_census(sanitized)
    out_bytes = write_json(output, sanitized)
    assert_no_leaks(output)

    sanitized_sha = sha256_bytes(out_bytes)
    provenance = {
        "repo": repo,
        "commit": commit,
        "path": path,
        "blob_sha": blob_sha,
        "counts": counts,
        "allowed_keys": list(ALLOWED_KEYS),
        "sanitized_path": str(output.as_posix()),
        "sanitized_sha256": sanitized_sha,
        "raw_ledger_copied_into_repo": False,
        "source_mode": "local-file" if source_file else "github-api-raw",
        "imported_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    prov_path = output.parent / "PROVENANCE.json"
    write_json(prov_path, provenance)
    assert_no_leaks(prov_path)

    log_path = output.parent / "IMPORT_LOG.md"
    log_path.write_text(
        build_import_log(
            repo=repo,
            commit=commit,
            path=path,
            blob_sha=blob_sha,
            counts=counts,
            sanitized_sha256=sanitized_sha,
            source_mode=provenance["source_mode"],
        ),
        encoding="utf-8",
    )
    assert_no_leaks(log_path)

    return provenance


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=DEFAULT_REPO)
    parser.add_argument("--commit", default=DEFAULT_COMMIT)
    parser.add_argument("--path", default=DEFAULT_PATH)
    parser.add_argument("--expected-blob", default=DEFAULT_BLOB_SHA)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/external_slice/defect4mr_import/candidates_sanitized.json"),
    )
    parser.add_argument(
        "--source-file",
        type=Path,
        default=None,
        help="Offline pinned ledger copy (never committed). Skips GitHub fetch.",
    )
    args = parser.parse_args(argv)

    try:
        provenance = run_import(
            repo=args.repo,
            commit=args.commit,
            path=args.path,
            output=args.output,
            expected_blob=args.expected_blob,
            source_file=args.source_file,
        )
    except Exception as exc:  # noqa: BLE001 - CLI boundary
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(json.dumps({"ok": True, "provenance": provenance}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
