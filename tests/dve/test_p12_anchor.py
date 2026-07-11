"""P3-side validation of the P12 W3.4 cross-repository freeze anchor."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from p2.dve.p12_anchor import (  # noqa: E402
    AnchorValidationError,
    canonical_sha256,
    load_jsonl,
    validate_amendments,
    validate_anchor,
    validate_committed_anchor,
)


ANCHOR_PATH = ROOT / "data/dve/p12_w3_freeze_anchor_v1.1.2.json"
AMENDMENTS_PATH = ROOT / "research/evidence/p12_consumer_amendments_v1.1.2.jsonl"
CONTRACT_PATH = ROOT / "data/dve/p12_consumer_contract_v1.1.2.json"


def _anchor():
    return json.loads(ANCHOR_PATH.read_text(encoding="utf-8"))


def _amendments():
    return load_jsonl(AMENDMENTS_PATH)


def _rehash_anchor(doc):
    body = {key: value for key, value in doc.items() if key != "anchor_sha256"}
    doc["anchor_sha256"] = canonical_sha256(body)


def _rehash_event(event):
    body = {key: value for key, value in event.items() if key != "event_sha256"}
    event["event_sha256"] = canonical_sha256(body)


def test_committed_cross_repository_anchor_is_valid():
    result = validate_committed_anchor(ROOT)
    assert result == {
        "anchor_id": "p3-p12-w3.4-cross-repo-anchor-v1.1.2",
        "amendment_id": "P3-A001",
        "producer_commit": "223fbadb55a016a76ac7c5bcd0dca37481103f1a",
        "d2_opened": False,
        "w4_executed": False,
    }


def test_anchor_self_hash_rejects_tampered_producer_commit():
    doc = _anchor()
    doc["producer"]["freeze_commit"] = "0" * 40
    with pytest.raises(AnchorValidationError, match="E_ANCHOR_HASH"):
        validate_anchor(doc, CONTRACT_PATH)


def test_anchor_rejects_wrong_frozen_identity_even_with_recomputed_hash():
    doc = _anchor()
    doc["producer"]["freeze_manifest_sha256"] = "0" * 64
    _rehash_anchor(doc)
    with pytest.raises(AnchorValidationError, match="E_ANCHOR_IDENTITY"):
        validate_anchor(doc, CONTRACT_PATH)


def test_anchor_rejects_contract_byte_drift(tmp_path):
    changed = tmp_path / "consumer-contract.json"
    changed.write_bytes(CONTRACT_PATH.read_bytes() + b"\n")
    with pytest.raises(AnchorValidationError, match="E_CONSUMER_CONTRACT_HASH"):
        validate_anchor(_anchor(), changed)


@pytest.mark.parametrize("field", ["d2_opened", "w4_executed"])
def test_anchor_must_precede_d2_opening_and_w4_execution(field):
    doc = _anchor()
    doc["chronology"][field] = True
    _rehash_anchor(doc)
    with pytest.raises(AnchorValidationError, match="E_ANCHOR_CHRONOLOGY"):
        validate_anchor(doc, CONTRACT_PATH)


def test_anchor_records_cloud_tag_permission_without_calling_it_a_tag():
    doc = _anchor()
    doc["transport"]["anchor_mode"] = "annotated-tag"
    _rehash_anchor(doc)
    with pytest.raises(AnchorValidationError, match="E_ANCHOR_TRANSPORT"):
        validate_anchor(doc, CONTRACT_PATH)


def test_amendment_event_hash_rejects_tampering():
    events = _amendments()
    events[0]["reason"] = "changed after acceptance"
    with pytest.raises(AnchorValidationError, match="E_AMENDMENT_HASH"):
        validate_amendments(events, _anchor())


def test_amendment_cannot_change_scientific_interpretation():
    events = copy.deepcopy(_amendments())
    events[0]["scientific_impact"] = True
    _rehash_event(events[0])
    with pytest.raises(AnchorValidationError, match="E_AMENDMENT_SCIENTIFIC_EFFECT"):
        validate_amendments(events, _anchor())


def test_amendment_must_bind_the_same_p12_freeze():
    events = copy.deepcopy(_amendments())
    events[0]["producer_freeze_commit"] = "0" * 40
    _rehash_event(events[0])
    with pytest.raises(AnchorValidationError, match="E_AMENDMENT_BINDING"):
        validate_amendments(events, _anchor())

