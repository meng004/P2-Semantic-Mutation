"""Offline tests for the Study-2 cross-source campaign readiness:
  - dual-blind role rotation + reviewer-packet blinding (§5)
  - the --dry-run harness runs the full pipeline with no network.

scripts/ is not a package, so the campaign module is loaded by path.
"""
import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
_CAMPAIGN = ROOT / "scripts" / "cross_source_campaign.py"


def _load_campaign():
    spec = importlib.util.spec_from_file_location("cross_source_campaign_test", _CAMPAIGN)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


CAMP = _load_campaign()


def test_registered_seeds_and_counts():
    assert CAMP.REGISTERED_SEED == 20260708
    assert CAMP.REGISTERED_K == 3
    assert set(CAMP.ARMS["same"]) == {"claude"}
    assert set(CAMP.ARMS["cross"]) == {"claude", "gpt", "deepseek"}


def test_role_rotation_generator_never_reviews_itself():
    for fam in CAMP.FAMILIES:
        reviewer, arbiter = CAMP.assign_review_roles(fam)
        assert reviewer != fam, "reviewer must differ from generator"
        assert arbiter != fam, "arbiter must differ from generator"
        assert reviewer != arbiter, "reviewer must differ from arbiter"


def test_review_packet_is_blind():
    """The blinded packet must omit generator identity, arm label, and SMS."""
    op = next(o for o in CAMP.OPERATORS if o.id == "a4_OS1")
    packet = CAMP.build_blind_review_packet(op, "def program(x):\n    return x", "MUT")
    flat = repr(packet).lower()
    assert "claude" not in flat and "gpt" not in flat and "deepseek" not in flat
    assert "same" not in packet and "cross" not in packet
    assert "sms" not in flat
    # It must still carry what the reviewer legitimately needs.
    assert packet["operator"]["id"] == "a4_OS1"
    assert packet["mutant_code"] == "MUT"
    assert "put_source" in packet


def test_dry_run_full_pipeline_offline():
    """The mock-client dry-run exercises generation→validation→blind-review→
    pool→AVP/equiv→SMS on one old (a2) and one new (a4) PUT with no network."""
    rc = CAMP.run_dry_run()
    assert rc == 0
    # harness cleans up its scratch cache
    assert not (ROOT / "data" / "operator_campaign" / "cache_dryrun").exists()


def test_mock_client_needs_no_credentials(monkeypatch):
    """MockLLMClient must produce a fenced, valid, non-trivial mutant without
    any API key in the environment."""
    for k in ("BLTCY_API_KEY", "BLTCY_BASE_URL", "DEEPSEEK_API_KEY", "DEEPSEEK_BASE_URL"):
        monkeypatch.delenv(k, raising=False)
    client, model = CAMP._mock_generator_factory()
    prompt = "```python\ndef program(x):\n    return float(x)\n```"
    resp = client.chat.completions.create(model=model,
                                          messages=[{"role": "user", "content": prompt}])
    content = resp.choices[0].message.content
    assert "def program" in content and "_p_orig" in content
