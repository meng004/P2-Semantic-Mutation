"""Real JSON_SCHEMA_DRAFT2020_12_V1 E_COMMON generator.

Frozen construction rule (P3 v3, 2026-08-12): accept only an object schema
(`kind == GENERATOR_ID`, `type == "object"`, dict `properties`, `required`
subset of the properties); derive one value per property, in sorted property
order, from the deterministic SHA-256 seed stream; return one canonical
envelope or the stable failure code. Stdlib-only; no output; no network.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

GENERATOR_ID = "JSON_SCHEMA_DRAFT2020_12_V1"
FAILURE_CODE = "JSON_SCHEMA_DRAFT2020_12_V1_INVALID"
_JSON_TYPES = {"array", "boolean", "integer", "null", "number", "object", "string"}


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


def _u64(seed: int, counter: int) -> int:
    return int.from_bytes(_block(seed, counter)[:8], "big")


def _failure() -> dict[str, Any]:
    return {"failure_code": FAILURE_CODE}


def _load_schema(schema_bytes: bytes) -> dict | None:
    if not schema_bytes:
        return None
    try:
        schema = json.loads(schema_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None
    if not isinstance(schema, dict) or schema.get("kind") != GENERATOR_ID:
        return None
    return schema


def _envelope(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "envelope": {
            "schema_version": "p3-common-input-envelope-v1",
            "generator_id": GENERATOR_ID,
            "payload": payload,
        },
        "raw_payload_sha256": hashlib.sha256(_canonical_bytes(payload)).hexdigest(),
    }


def _value(declared: Any, seed: int, counter: int) -> tuple[Any, int] | None:
    if isinstance(declared, list):
        if not declared or any(item not in _JSON_TYPES for item in declared):
            return None
        selected = sorted(declared)[_u64(seed, counter) % len(declared)]
        counter += 1
    elif declared in _JSON_TYPES:
        selected = declared
    else:
        return None
    if selected == "integer":
        return _u64(seed, counter) % 2_000_001 - 1_000_000, counter + 1
    if selected == "number":
        return (_u64(seed, counter) % 2_000_001 - 1_000_000) / 1000, counter + 1
    if selected == "string":
        return "s" + _block(seed, counter).hex()[:8], counter + 1
    if selected == "boolean":
        return _u64(seed, counter) % 2 == 1, counter + 1
    if selected == "array":
        first = _u64(seed, counter) % 2_000_001 - 1_000_000
        second = _u64(seed, counter + 1) % 2_000_001 - 1_000_000
        return [first, second], counter + 2
    if selected == "object":
        return {}, counter
    return None, counter


def generate(schema_bytes: bytes, seed: int) -> dict[str, Any]:
    schema = _load_schema(schema_bytes)
    if schema is None:
        return _failure()
    if schema.get("type") != "object":
        return _failure()
    properties = schema.get("properties")
    if not isinstance(properties, dict):
        return _failure()
    required = schema.get("required", [])
    if not isinstance(required, list) or any(
        name not in properties for name in required
    ):
        return _failure()
    arguments: dict[str, Any] = {}
    counter = 0
    for name in sorted(properties):
        spec = properties[name]
        if not isinstance(spec, dict):
            return _failure()
        produced = _value(spec.get("type"), seed, counter)
        if produced is None:
            return _failure()
        value, counter = produced
        arguments[name] = value
    return _envelope({"arguments": arguments})
