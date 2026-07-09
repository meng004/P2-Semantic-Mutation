"""Study-4 rich-class x4 slot multiplier — mock-based unit tests (NO live calls).

Covers the config-driven per-class attempt multiplier (PREREGISTRATION_STUDY4
§2a/§3.2/§4b): C/D (rich) confirmatory PUTs generate at base*4 per (operator,
slot) in the Python arms; A/B at baseline; the H-LANG C arm gets NO multiplier
(§2c). Default 1 (off) when the config omits the key. The campaign wiring is
exercised end-to-end with fake factories so pytest never touches the network.
"""
import importlib.util
from pathlib import Path

from p2.config import study4 as s4

ROOT = Path(__file__).resolve().parents[2]


def _load_campaign():
    spec = importlib.util.spec_from_file_location(
        "csc_richmult_test", ROOT / "scripts" / "cross_source_campaign.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


CAMP = _load_campaign()


# ── config helpers ─────────────────────────────────────────────────────────

def test_shipped_config_pins_x4():
    cfg = s4.load_study4_config()
    assert s4.rich_multiplier(cfg) == 4
    assert s4.rich_classes(cfg) == ("c", "d")


def test_is_rich_put_classification():
    assert s4.is_rich_put("c2") and s4.is_rich_put("c7") and s4.is_rich_put("d8")
    assert not s4.is_rich_put("a1") and not s4.is_rich_put("b3")


def test_attempts_for_put_rich_vs_baseline():
    cfg = s4.load_study4_config()
    # rich C/D PUTs get base*4; A/B stay at base
    assert s4.attempts_for_put(3, "c7", lang="py", cfg=cfg) == 12
    assert s4.attempts_for_put(3, "d8", lang="py", cfg=cfg) == 12
    assert s4.attempts_for_put(3, "a1", lang="py", cfg=cfg) == 3
    assert s4.attempts_for_put(3, "b2", lang="py", cfg=cfg) == 3


def test_attempts_for_put_c_arm_has_no_multiplier():
    cfg = s4.load_study4_config()
    # §2c: the C (H-LANG) arm is baseline for EVERY PUT, including c2
    assert s4.attempts_for_put(3, "c2", lang="c", cfg=cfg) == 3
    assert s4.attempts_for_put(3, "a1", lang="c", cfg=cfg) == 3


def test_multiplier_default_off_when_absent():
    cfg = {"rich_classes": ["c", "d"]}          # no rich_multiplier key
    assert s4.rich_multiplier(cfg) == 1
    assert s4.attempts_for_put(3, "c7", lang="py", cfg=cfg) == 3   # off -> baseline


def test_env_override_config_multiplier(tmp_path, monkeypatch):
    import json
    alt = {"gateway": {"base_url_env": "BLTCY_BASE_URL", "api_key_env": "BLTCY_API_KEY"},
           "models": {"m-x": {"vendor": "v", "min_max_tokens": 0,
                              "price_per_mtok": {"prompt": 1.0, "completion": 2.0}}},
           "arms": {"same": {"slots": [{"tag": "src1", "model": "m-x"}]},
                    "cross": {"slots": [{"tag": "src1", "model": "m-x"}]}},
           "roles": {"reviewer": "m-x", "arbiter": "m-x"}, "registered_k": 3,
           "rich_multiplier": 2, "rich_classes": ["d"]}
    p = tmp_path / "alt.json"
    p.write_text(json.dumps(alt))
    monkeypatch.setenv("P2_STUDY4_CONFIG", str(p))
    cfg = s4.load_study4_config()
    assert s4.attempts_for_put(5, "d8", lang="py", cfg=cfg) == 10   # x2, d is rich
    assert s4.attempts_for_put(5, "c7", lang="py", cfg=cfg) == 5    # c not rich here


# ── campaign wiring: the multiplier reaches study4_generate_slot ────────────

def _fake_gen(content="```python\ndef program(x):\n    return float(x)+0.5\n```"):
    class _Msg:
        def __init__(s, c): s.content = c
    class _Choice:
        def __init__(s, c): s.message = _Msg(c)
    class _Usage:
        prompt_tokens = 100; completion_tokens = 50
    class _Resp:
        def __init__(s, c, m): s.choices = [_Choice(c)]; s.usage = _Usage(); s.model = m
    class FC:
        def __init__(s): s.chat = s; s.completions = s
        def create(s, model, messages, max_tokens, temperature):
            return _Resp(content, "claude-fable-5")
    return FC()


def test_campaign_applies_x4_to_rich_puts(tmp_path, monkeypatch):
    """study4_campaign issues base*4 generation attempts on a rich (C) PUT and
    base attempts on a non-rich (A) PUT, in the Python arm."""
    def fake_slots(arm):
        return [("src1", lambda: (_fake_gen(), "claude-fable-5",
                                  {"vendor": "anthropic",
                                   "price_per_mtok": {"prompt": 3.0, "completion": 15.0}}))]
    monkeypatch.setattr(CAMP, "study4_slot_factories", fake_slots)

    # c2 is rich -> 3*4 = 12 records per (op, slot); a1 is baseline -> 3.
    out = CAMP.study4_campaign(["c2"], "same", attempts=3,
                               cache_dir=tmp_path / "c2", log_path=tmp_path / "c.jsonl")
    per_op = {}
    for r in out["records"]:
        per_op[r["op"]] = per_op.get(r["op"], 0) + 1
    assert per_op and all(n == 12 for n in per_op.values()), per_op

    out_a = CAMP.study4_campaign(["a1"], "same", attempts=3,
                                 cache_dir=tmp_path / "a1", log_path=tmp_path / "a.jsonl")
    per_op_a = {}
    for r in out_a["records"]:
        per_op_a[r["op"]] = per_op_a.get(r["op"], 0) + 1
    assert per_op_a and all(n == 3 for n in per_op_a.values()), per_op_a
