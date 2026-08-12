"""Real CLI_TOKEN_GRAMMAR_V1 E_COMMON generator.

Frozen construction rule (P3 v3, 2026-08-12): accept only
`{kind, program, tokens: {min, max}, vocabulary}`; draw the token count in
`[min, max]` and each token from the vocabulary via the deterministic SHA-256
seed stream; the payload argv always starts with the program. Stdlib-only.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

GENERATOR_ID = "CLI_TOKEN_GRAMMAR_V1"
FAILURE_CODE = "CLI_TOKEN_GRAMMAR_V1_INVALID"


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
    program = schema.get("program")
    tokens = schema.get("tokens")
    vocabulary = schema.get("vocabulary")
    if (
        not isinstance(program, str)
        or not program
        or not isinstance(tokens, dict)
        or type(tokens.get("min")) is not int
        or type(tokens.get("max")) is not int
        or not 0 <= tokens["min"] <= tokens["max"]
        or not isinstance(vocabulary, list)
        or not vocabulary
        or any(not isinstance(item, str) or not item for item in vocabulary)
    ):
        return failure
    count = tokens["min"] + _u64(seed, 0) % (tokens["max"] - tokens["min"] + 1)
    picked = [
        vocabulary[_u64(seed, counter) % len(vocabulary)]
        for counter in range(1, count + 1)
    ]
    payload = {"argv": [program, *picked]}
    return {
        "envelope": {
            "schema_version": "p3-common-input-envelope-v1",
            "generator_id": GENERATOR_ID,
            "payload": payload,
        },
        "raw_payload_sha256": hashlib.sha256(_canonical_bytes(payload)).hexdigest(),
    }
