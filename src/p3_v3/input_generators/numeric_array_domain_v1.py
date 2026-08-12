"""Real NUMERIC_ARRAY_DOMAIN_V1 E_COMMON generator.

Frozen construction rule (P3 v3, 2026-08-12): accept only
`{kind, parameters, element_count, dtype: int64|float64, minimum, maximum}`
with `element_count == len(parameters)` and `minimum <= maximum`; draw one
value per parameter inside `[minimum, maximum]` from the deterministic
SHA-256 seed stream (float64 adds a thousandth-resolution fraction, clamped
and rounded to six places). Stdlib-only.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

GENERATOR_ID = "NUMERIC_ARRAY_DOMAIN_V1"
FAILURE_CODE = "NUMERIC_ARRAY_DOMAIN_V1_INVALID"


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
    parameters = schema.get("parameters")
    element_count = schema.get("element_count")
    dtype = schema.get("dtype")
    minimum = schema.get("minimum")
    maximum = schema.get("maximum")
    if (
        not isinstance(parameters, list)
        or not parameters
        or any(not isinstance(item, str) or not item for item in parameters)
        or type(element_count) is not int
        or element_count != len(parameters)
        or dtype not in {"int64", "float64"}
        or type(minimum) is not int
        or type(maximum) is not int
        or minimum > maximum
    ):
        return failure
    span = maximum - minimum + 1
    values: list[Any] = []
    counter = 0
    for _name in parameters:
        base = minimum + _u64(seed, counter) % span
        counter += 1
        if dtype == "float64":
            fraction = (_u64(seed, counter) % 1000) / 1000
            counter += 1
            values.append(round(min(maximum, base + fraction), 6))
        else:
            values.append(base)
    payload = {"parameters": parameters, "values": values, "dtype": dtype}
    return {
        "envelope": {
            "schema_version": "p3-common-input-envelope-v1",
            "generator_id": GENERATOR_ID,
            "payload": payload,
        },
        "raw_payload_sha256": hashlib.sha256(_canonical_bytes(payload)).hexdigest(),
    }
