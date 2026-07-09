"""Study-4 four-vendor gateway wiring — mock-based unit tests (NO live calls).

Covers the config-driven model-role mapping, per-model quirks (gemini max_tokens
floor, grok served-id echo), retry/backoff on transient failures, per-call cost
accounting, and blinded review — all with fake clients so pytest never touches
the network.
"""
import importlib.util
import json
from pathlib import Path

import pytest

from p2.config import study4 as s4

ROOT = Path(__file__).resolve().parents[2]


def _load_campaign():
    spec = importlib.util.spec_from_file_location(
        "csc_study4_test", ROOT / "scripts" / "cross_source_campaign.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


CAMP = _load_campaign()


# ── fake OpenAI-compatible client ──────────────────────────────────────────

class _Msg:
    def __init__(self, c): self.content = c


class _Choice:
    def __init__(self, c): self.message = _Msg(c)


class _Usage:
    def __init__(self, pt, ct): self.prompt_tokens = pt; self.completion_tokens = ct


class _Resp:
    def __init__(self, content, model, pt=100, ct=50):
        self.choices = [_Choice(content)]
        self.usage = _Usage(pt, ct)
        self.model = model


class FakeClient:
    """Records create() kwargs and returns a canned response (or raises)."""
    def __init__(self, content="```python\ndef program(x):\n    return float(x)+1\n```",
                 served_model="m", pt=100, ct=50, raise_seq=None):
        self.content = content
        self.served_model = served_model
        self.pt, self.ct = pt, ct
        self.calls = []
        self._raise_seq = list(raise_seq or [])
        self.chat = self  # so client.chat.completions.create works
        self.completions = self

    def create(self, model, messages, max_tokens, temperature):
        self.calls.append({"model": model, "max_tokens": max_tokens})
        if self._raise_seq:
            exc = self._raise_seq.pop(0)
            if exc is not None:
                raise exc
        return _Resp(self.content, self.served_model, self.pt, self.ct)


# ── config-driven mapping ──────────────────────────────────────────────────

def test_config_is_config_driven_not_hardcoded():
    assert s4.arm_slots("same") == [("src1", "claude-fable-5"),
                                    ("src2", "claude-fable-5"),
                                    ("src3", "claude-fable-5")]
    assert s4.arm_slots("cross") == [("src1", "gpt-5.5"),
                                     ("src2", "gemini-3.5-flash"),
                                     ("src3", "grok-4.1")]
    assert s4.role_model("reviewer") == "claude-fable-5"
    assert s4.role_model("arbiter") == "gpt-5.5"


def test_env_override_loads_alternate_roster(tmp_path, monkeypatch):
    alt = {"gateway": {"base_url_env": "BLTCY_BASE_URL", "api_key_env": "BLTCY_API_KEY"},
           "models": {"m-x": {"vendor": "v", "min_max_tokens": 0,
                              "price_per_mtok": {"prompt": 1.0, "completion": 2.0}}},
           "arms": {"same": {"slots": [{"tag": "src1", "model": "m-x"}]},
                    "cross": {"slots": [{"tag": "src1", "model": "m-x"}]}},
           "roles": {"reviewer": "m-x", "arbiter": "m-x"}, "registered_k": 3}
    p = tmp_path / "alt.json"
    p.write_text(json.dumps(alt))
    monkeypatch.setenv("P2_STUDY4_CONFIG", str(p))
    cfg = s4.load_study4_config()
    assert s4.arm_slots("same", cfg) == [("src1", "m-x")]
    assert s4.role_model("reviewer", cfg) == "m-x"


def test_unknown_arm_raises():
    with pytest.raises(KeyError):
        s4.arm_slots("nope")


# ── quirks: gemini floor + grok served-id echo ─────────────────────────────

def test_gemini_max_tokens_floor_applied():
    fc = FakeClient()
    _code, meta = CAMP._generate_one(fc, "gemini-3.5-flash", "p",
                                     max_tokens=800, min_max_tokens=2000)
    assert fc.calls[0]["max_tokens"] == 2000  # floor raised the budget
    assert meta["requested_model"] == "gemini-3.5-flash"


def test_no_floor_leaves_max_tokens():
    fc = FakeClient()
    CAMP._generate_one(fc, "gpt-5.5", "p", max_tokens=800, min_max_tokens=0)
    assert fc.calls[0]["max_tokens"] == 800


def test_grok_served_model_echo_captured():
    fc = FakeClient(served_model="grok-4.3")
    _code, meta = CAMP._generate_one(fc, "grok-4.1", "p")
    assert meta["served_model"] == "grok-4.3"
    assert meta["requested_model"] == "grok-4.1"


def test_bare_fence_stripping_grok_style():
    fc = FakeClient(content="```\ndef program(x):\n    return float(x)+1\n```")
    code, _m = CAMP._generate_one(fc, "grok-4.1", "p")
    assert code.startswith("def program")


# ── retry / backoff ────────────────────────────────────────────────────────

class _Transient(Exception):
    pass


def test_retry_succeeds_after_transient(monkeypatch):
    monkeypatch.setattr(CAMP, "_RETRYABLE", (_Transient,))
    monkeypatch.setattr(CAMP.time, "sleep", lambda *_a: None)
    fc = FakeClient(raise_seq=[_Transient(), _Transient(), None])
    resp = CAMP._chat_with_retry(fc, model="m", messages=[{"role": "user", "content": "p"}],
                                 max_tokens=10, temperature=0.7, tries=3, base_delay=0.0)
    assert resp.model == "m"
    assert len(fc.calls) == 3  # two failures + one success


def test_retry_exhausts_and_raises(monkeypatch):
    monkeypatch.setattr(CAMP, "_RETRYABLE", (_Transient,))
    monkeypatch.setattr(CAMP.time, "sleep", lambda *_a: None)
    fc = FakeClient(raise_seq=[_Transient(), _Transient(), _Transient()])
    with pytest.raises(_Transient):
        CAMP._chat_with_retry(fc, model="m", messages=[{"role": "user", "content": "p"}],
                              max_tokens=10, temperature=0.7, tries=3, base_delay=0.0)


def test_non_retryable_error_not_retried(monkeypatch):
    monkeypatch.setattr(CAMP, "_RETRYABLE", (_Transient,))
    monkeypatch.setattr(CAMP.time, "sleep", lambda *_a: None)

    class _Hard(Exception):
        pass
    fc = FakeClient(raise_seq=[_Hard()])
    with pytest.raises(_Hard):
        CAMP._chat_with_retry(fc, model="m", messages=[{"role": "user", "content": "p"}],
                              max_tokens=10, temperature=0.7, tries=3, base_delay=0.0)
    assert len(fc.calls) == 1  # hard error not retried


# ── cost accounting ────────────────────────────────────────────────────────

def test_cost_estimate_matches_price_table():
    # gpt-5.5: 1.25/Mtok prompt, 10.0/Mtok completion
    got = s4.estimate_cost_usd("gpt-5.5", 1_000_000, 1_000_000)
    assert got == pytest.approx(1.25 + 10.0)


def test_study4_call_logs_cost_and_served(tmp_path):
    fc = FakeClient(served_model="grok-4.3", pt=200, ct=80)
    factory = lambda: (fc, "grok-4.1", s4.model_quirks("grok-4.1"))
    log = tmp_path / "log.jsonl"
    code, meta = CAMP._study4_call(factory, "p", kind="generate", slot_tag="src3",
                                   op_id="a2_OS1", log_path=log)
    assert code.startswith("def program")
    assert meta["cost_usd"] > 0
    rows = [json.loads(x) for x in log.read_text().splitlines()]
    assert rows[0]["served_model"] == "grok-4.3"
    assert rows[0]["served_mismatch"] is True  # grok-4.1 -> grok-4.3
    assert rows[0]["cost_usd"] == meta["cost_usd"]


# ── blinded review + arbitration ───────────────────────────────────────────

def test_blind_code_redacts_vendor_tokens():
    dirty = "# grok-4.1 by claude-fable-5\ndef program(x): return x"
    clean = CAMP._study4_blind_code(dirty)
    assert "grok" not in clean.lower() and "claude" not in clean.lower()
    assert "fable" not in clean.lower()


def _op_a2():
    return next(o for o in CAMP.OPERATORS if o.id == "a2_OS1")


def test_blind_review_confirmed_no_arbitration(tmp_path):
    rev = FakeClient(content='{"operator_match":"Yes","overall":"CONFIRMED","reason":"ok"}')
    arb = FakeClient(content='{"operator_match":"Yes","overall":"CONFIRMED","reason":"ok"}')
    out = CAMP.run_study4_blind_review(
        _op_a2(), "def program(x):\n    return float(x)", "def program(x): return x+1",
        tmp_path / "log.jsonl",
        reviewer_factory=lambda: (rev, "claude-fable-5", {}),
        arbiter_factory=lambda: (arb, "gpt-5.5", {}))
    assert out["review_verdict"] == "CONFIRMED"
    assert out["arbitrated"] is False
    assert len(arb.calls) == 0  # arbiter untouched on a clean CONFIRMED


def test_blind_review_uncertain_triggers_arbitration(tmp_path):
    rev = FakeClient(content='{"operator_match":"Uncertain","overall":"UNCERTAIN","reason":"?"}')
    arb = FakeClient(content='{"operator_match":"Yes","overall":"CONFIRMED","reason":"arb"}')
    out = CAMP.run_study4_blind_review(
        _op_a2(), "def program(x):\n    return float(x)", "def program(x): return x+1",
        tmp_path / "log.jsonl",
        reviewer_factory=lambda: (rev, "claude-fable-5", {}),
        arbiter_factory=lambda: (arb, "gpt-5.5", {}))
    assert out["arbitrated"] is True
    assert out["review_verdict"] == "CONFIRMED"  # arbiter's final call
    assert len(arb.calls) == 1


# ── full offline wiring: study4_campaign with mock factories ───────────────

def test_study4_campaign_end_to_end_offline(tmp_path, monkeypatch):
    """study4_campaign runs generation+admission+review with fake factories,
    exercising the SAME admit_mutant path as the live gateway."""
    def fake_slots(arm):
        gen = FakeClient(content="```python\ndef program(x):\n    return float(x)+0.5\n```",
                         served_model="claude-fable-5")
        return [("src1", lambda: (gen, "claude-fable-5", {"vendor": "anthropic",
                                                          "price_per_mtok": {"prompt": 3.0, "completion": 15.0}}))]

    def fake_reviewer():
        return (FakeClient(content='{"operator_match":"Yes","overall":"CONFIRMED","reason":"ok"}'),
                "claude-fable-5", {})

    monkeypatch.setattr(CAMP, "study4_slot_factories", fake_slots)
    monkeypatch.setattr(CAMP, "study4_role_factory", lambda role: fake_reviewer)
    out = CAMP.study4_campaign(["a2"], "same", attempts=1,
                               cache_dir=tmp_path / "cache",
                               log_path=tmp_path / "log.jsonl", review=True)
    assert len(out["records"]) == 3  # 3 a2 operators x 1 slot x 1 attempt
    assert all(r.get("v_passed") for r in out["records"])
    assert len(out["reviews"]) == 3
    # per-call cost log written
    assert (tmp_path / "log.jsonl").exists()
