"""Real TEXT_IO_SCHEMA_V1 E_COMMON generator.

Frozen construction rule (P3 v3, 2026-08-12): accept only
`{kind, fields, max_length, charset: "printable_ascii"}`; per field draw a
length in `[1, min(max_length, 64)]` and characters from the frozen
37-character alphabet (`a-z`, `0-9`, space) via the deterministic SHA-256
seed stream. Stdlib-only.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

GENERATOR_ID = "TEXT_IO_SCHEMA_V1"
FAILURE_CODE = "TEXT_IO_SCHEMA_V1_INVALID"
_ALPHABET = "abcdefghijklmnopqrstuvwxyz0123456789 "


def _canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        .encode("utf-8")
        + b"\n"
    )


def _u64(seed: int, counter: int) -> int:
    block = hashlib.sha256(
        b"P3-INPUT-STREAM-v1" + seed.to_bytes(8, "big") + counter.to_bytes(8, "big")
    ).digest()
    return int.from_bytes(block[:8], "big")


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
    max_length = schema.get("max_length")
    if (
        not isinstance(fields, list)
        or not fields
        or any(not isinstance(item, str) or not item for item in fields)
        or type(max_length) is not int
        or max_length < 1
        or schema.get("charset") != "printable_ascii"
    ):
        return failure
    bound = min(max_length, 64)
    produced: dict[str, str] = {}
    counter = 0
    for name in fields:
        length = 1 + _u64(seed, counter) % bound
        counter += 1
        characters = []
        for _index in range(length):
            characters.append(_ALPHABET[_u64(seed, counter) % len(_ALPHABET)])
            counter += 1
        produced[name] = "".join(characters)
    payload = {"fields": produced}
    return {
        "envelope": {
            "schema_version": "p3-common-input-envelope-v1",
            "generator_id": GENERATOR_ID,
            "payload": payload,
        },
        "raw_payload_sha256": hashlib.sha256(_canonical_bytes(payload)).hexdigest(),
    }
