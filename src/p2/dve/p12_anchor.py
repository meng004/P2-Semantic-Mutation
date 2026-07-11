"""Validation for the P3 acknowledgment of the P12 W3.4 workflow freeze.

This module verifies transport identity and chronology only.  It deliberately does
not interpret, import, or strengthen any P12 experimental result.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


EXPECTED = {
    "anchor_id": "p3-p12-w3.4-cross-repo-anchor-v1.1.2",
    "producer_repository": "meng004/P12-Defect4MR",
    "producer_branch": "codex/p12-independent-evidence-design",
    "producer_freeze_stage": "W3.4",
    "producer_freeze_commit": "223fbadb55a016a76ac7c5bcd0dca37481103f1a",
    "producer_contract_sha256": (
        "ea26e756b7f04831f981fffd19bcdf2070b8e5055fe4914e2b5cbce6c488182e"
    ),
    "producer_freeze_manifest_sha256": (
        "8509567d11c4f91508578431448744a54d5f0c400eb5c937f6b91625d2cb236e"
    ),
    "consumer_repository": "meng004/P3-Semantic-Mutation",
    "consumer_contract_commit": "2f1088854c284b3af56e34fc6ff4fe8542962920",
    "consumer_contract_sha256": (
        "be201031e738c28c5c0ff15a1048da81891cd8d971d0684ef040d3cd7d6d28b6"
    ),
    "amendment_id": "P3-A001",
}


class AnchorValidationError(ValueError):
    """A stable-code validation failure in the cross-repository anchor."""

    def __init__(self, code: str, detail: str):
        super().__init__(f"{code}: {detail}")
        self.code = code


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode(
        "utf-8"
    )


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def file_sha256(path: str | Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_jsonl(path: str | Path) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for line_number, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError as exc:
            raise AnchorValidationError(
                "E_AMENDMENT_JSON", f"line {line_number} is not valid JSON"
            ) from exc
        if not isinstance(event, dict):
            raise AnchorValidationError("E_AMENDMENT_JSON", f"line {line_number} is not an object")
        events.append(event)
    return events


def _require(condition: bool, code: str, detail: str) -> None:
    if not condition:
        raise AnchorValidationError(code, detail)


def validate_anchor(anchor: dict[str, Any], contract_path: str | Path) -> None:
    body = {key: value for key, value in anchor.items() if key != "anchor_sha256"}
    _require(
        anchor.get("anchor_sha256") == canonical_sha256(body),
        "E_ANCHOR_HASH",
        "anchor self-hash does not match its canonical body",
    )

    producer = anchor.get("producer", {})
    consumer = anchor.get("consumer", {})
    actual_identity = {
        "anchor_id": anchor.get("anchor_id"),
        "producer_repository": producer.get("repository"),
        "producer_branch": producer.get("branch"),
        "producer_freeze_stage": producer.get("freeze_stage"),
        "producer_freeze_commit": producer.get("freeze_commit"),
        "producer_contract_sha256": producer.get("contract_sha256"),
        "producer_freeze_manifest_sha256": producer.get("freeze_manifest_sha256"),
        "consumer_repository": consumer.get("repository"),
        "consumer_contract_commit": consumer.get("contract_commit"),
        "consumer_contract_sha256": consumer.get("contract_sha256"),
        "amendment_id": anchor.get("amendment_id"),
    }
    _require(actual_identity == EXPECTED, "E_ANCHOR_IDENTITY", "frozen identity differs")
    _require(
        file_sha256(contract_path) == EXPECTED["consumer_contract_sha256"],
        "E_CONSUMER_CONTRACT_HASH",
        "consumer-contract bytes differ from the frozen pin",
    )

    chronology = anchor.get("chronology", {})
    _require(
        chronology.get("d2_opened") is False and chronology.get("w4_executed") is False,
        "E_ANCHOR_CHRONOLOGY",
        "acknowledgment must precede D2 opening and W4 execution",
    )
    transport = anchor.get("transport", {})
    _require(
        transport.get("anchor_mode") == "cross-repository-content-hash"
        and transport.get("tag_status") == "unavailable_due_to_cloud_ref_permission",
        "E_ANCHOR_TRANSPORT",
        "cloud tag limitation must be represented as a content-hash anchor",
    )


def validate_amendments(events: list[dict[str, Any]], anchor: dict[str, Any]) -> None:
    _require(len(events) == 1, "E_AMENDMENT_CHAIN", "exactly P3-A001 is expected")
    previous: str | None = None
    for event in events:
        body = {key: value for key, value in event.items() if key != "event_sha256"}
        _require(
            event.get("event_sha256") == canonical_sha256(body),
            "E_AMENDMENT_HASH",
            f"{event.get('amendment_id')} event hash does not match",
        )
        _require(
            event.get("previous_event_sha256") == previous,
            "E_AMENDMENT_CHAIN",
            "previous-event pointer is broken",
        )
        previous = event["event_sha256"]

    event = events[0]
    _require(event.get("amendment_id") == "P3-A001", "E_AMENDMENT_CHAIN", "wrong event")
    _require(
        event.get("scientific_impact") is False
        and event.get("changes_confirmatory_interpretation") is False,
        "E_AMENDMENT_SCIENTIFIC_EFFECT",
        "transport equivalence cannot alter scientific interpretation",
    )
    _require(
        event.get("before_d2_opening") is True and event.get("before_w4_execution") is True,
        "E_AMENDMENT_CHRONOLOGY",
        "transport amendment must be accepted before outcomes exist",
    )
    producer = anchor["producer"]
    _require(
        event.get("producer_freeze_commit") == producer.get("freeze_commit")
        and event.get("producer_contract_sha256") == producer.get("contract_sha256")
        and event.get("producer_freeze_manifest_sha256")
        == producer.get("freeze_manifest_sha256"),
        "E_AMENDMENT_BINDING",
        "P3-A001 does not bind the acknowledged P12 freeze",
    )


def validate_committed_anchor(repo_root: str | Path) -> dict[str, Any]:
    root = Path(repo_root)
    anchor = json.loads(
        (root / "data/dve/p12_w3_freeze_anchor_v1.1.2.json").read_text(encoding="utf-8")
    )
    validate_anchor(anchor, root / "data/dve/p12_consumer_contract_v1.1.2.json")
    validate_amendments(
        load_jsonl(root / "research/evidence/p12_consumer_amendments_v1.1.2.jsonl"), anchor
    )
    return {
        "anchor_id": anchor["anchor_id"],
        "amendment_id": anchor["amendment_id"],
        "producer_commit": anchor["producer"]["freeze_commit"],
        "d2_opened": anchor["chronology"]["d2_opened"],
        "w4_executed": anchor["chronology"]["w4_executed"],
    }

