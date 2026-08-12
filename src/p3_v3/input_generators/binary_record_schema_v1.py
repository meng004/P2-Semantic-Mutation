"""Real BINARY_RECORD_SCHEMA_V1 E_COMMON generator.

Frozen construction rule (P3 v3, 2026-08-12): accept only
`{kind, fields, record_bytes}` with `1 <= record_bytes <= 4096`; per field
emit exactly `record_bytes` bytes as lowercase hex from the deterministic
SHA-256 seed stream. Stdlib-only.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

GENERATOR_ID = "BINARY_RECORD_SCHEMA_V1"
FAILURE_CODE = "BINARY_RECORD_SCHEMA_V1_INVALID"


def _canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        .encode("utf-8")
        + b"\n"
    )


def _block(seed: int, counter: int) -> bytes:
    return hashlib.sha256(
        b"P3-INPUT-STREAM-v1" + seed.to_bytes(8, "big") + counter.to_bytes(8, "big")
    ).digest()


def generate(schema_bytes: bytes, seed: int) -> dict[str, Any]:
    failure = {"failure_code": FAILURE_CODE}
    if not schema_bytes:
        return failure
    try:
        schema = json.loads(schema_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return failure
    if not isinstance(schema, dict) or schema.get("kind") != GENERATOR_ID:
        return failure
    fields = schema.get("fields")
    record_bytes = schema.get("record_bytes")
    if (
        not isinstance(fields, list)
        or not fields
        or any(not isinstance(item, str) or not item for item in fields)
        or type(record_bytes) is not int
        or not 1 <= record_bytes <= 4096
    ):
        return failure
    produced: dict[str, str] = {}
    counter = 0
    for name in fields:
        chunks: list[bytes] = []
        remaining = record_bytes
        while remaining > 0:
            block = _block(seed, counter)
            counter += 1
            chunks.append(block[:remaining])
            remaining -= len(block[:remaining])
        produced[name] = b"".join(chunks).hex()
    payload = {"fields": produced}
    return {
        "envelope": {
            "schema_version": "p3-common-input-envelope-v1",
            "generator_id": GENERATOR_ID,
            "payload": payload,
        },
        "raw_payload_sha256": hashlib.sha256(_canonical_bytes(payload)).hexdigest(),
    }
