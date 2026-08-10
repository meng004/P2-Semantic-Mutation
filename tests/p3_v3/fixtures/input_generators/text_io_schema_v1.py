"""Deterministic synthetic TEXT_IO_SCHEMA_V1 input generator."""

from __future__ import annotations

import hashlib
import json
from typing import Any

FAILURE_CODE = "TEXT_IO_SCHEMA_V1_INVALID"
GENERATOR_ID = "TEXT_IO_SCHEMA_V1"


def _seed_block(seed: int, counter: int) -> bytes:
    return hashlib.sha256(
        b"P3-INPUT-STREAM-v1" + seed.to_bytes(8, "big") + counter.to_bytes(8, "big")
    ).digest()


def generate(schema_bytes: bytes, seed: int) -> dict[str, Any]:
    if not schema_bytes:
        return {"failure_code": FAILURE_CODE}
    try:
        schema = json.loads(schema_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return {"failure_code": FAILURE_CODE}
    if isinstance(schema, dict) and schema.get("force_invalid") is True:
        return {"failure_code": FAILURE_CODE}
    block = _seed_block(seed, 0)
    payload = {
        "generator_id": GENERATOR_ID,
        "stream": block.hex(),
        "schema_fingerprint": hashlib.sha256(schema_bytes).hexdigest(),
    }
    raw = (
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        + b"\n"
    )
    envelope = {
        "schema_version": "p3-common-input-envelope-v1",
        "generator_id": GENERATOR_ID,
        "payload": payload,
    }
    return {
        "envelope": envelope,
        "raw_payload_sha256": hashlib.sha256(raw).hexdigest(),
    }
