"""Offline tests for the Study-4 AMENDMENT v1.2 rewiring (harness-served claude
roles + recruitment stratum + gateway baseline resume).

Everything here is OFFLINE (no network, no LLM, no live generation). The tests
pin the four new behaviours the amendment adds to the packet/campaign machinery:

  1. resume-aware export      — only the UNFINISHED (op, slot, attempt) remainder
                                is exported (one-shot rule; §5d).
  2. arm/stratum tag routing  — a packet's own tag lands its response in the right
                                Study-4 cache, and legacy Study-2 routing is intact.
  3. src-tag source override  — a harness remainder is named exactly like the
                                gateway-drawn cache (src1/src2/src3).
  4. rich_multiplier override — the gateway cross resume runs at BASELINE without
                                editing the frozen config.

scripts/ is not a package, so both modules are loaded by path.
"""
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


CAMP = _load("cross_source_campaign_v12", "scripts/cross_source_campaign.py")


def _wrap(orig: str, delta: float) -> str:
    return orig + f"\n\n_o = program\ndef program(x):\n    return float(_o(x)) + {delta}\n"


def _synthetic_response(packet: dict, delta0: float = 0.1) -> dict:
    orig = packet["put_source"]
    muts, d = [], delta0
    for slot in packet["required_slots"]:
        d += 0.013
        muts.append({"op_id": slot["op_id"], "source": slot["source"],
                     "attempt": slot["attempt"], "code": _wrap(orig, round(d, 3))})
    return {"packet_id": packet["packet_id"], "put_id": packet["put_id"],
            "mutants": muts}


# ── 1. resume-aware export ─────────────────────────────────────────────────

def test_resume_export_skips_drawn_slots(tmp_path):
    """A cache with a campaign_log.jsonl + admitted files makes the export drop
    exactly the already-drawn (op, slot, attempt) triples."""
    put = "a4"
    ops = sorted(o.id for o in CAMP.OPERATORS if o.put == put)
    assert ops, "a4 must have operators"
    op0 = ops[0]

    resume_cache = tmp_path / "same"
    resume_cache.mkdir()
    # log: src1 attempted 3x, src2 attempted 1x on op0 (attempt idx unknown → count)
    log = resume_cache / "campaign_log.jsonl"
    rows = ([{"kind": "generate", "op_id": op0, "slot": "src1"}] * 3
            + [{"kind": "generate", "op_id": op0, "slot": "src2"}] * 1)
    log.write_text("\n".join(json.dumps(r) for r in rows) + "\n")

    gdir = tmp_path / "gen"
    CAMP.export_generation_packets(gdir, puts=[put], arm="same",
                                   sources=["src1", "src2", "src3"], k=3,
                                   resume_cache=resume_cache)
    pk = json.loads((gdir / f"gen_{put}.json").read_text())
    slots = {(s["op_id"], s["source"], s["attempt"]) for s in pk["required_slots"]}
    # op0/src1 fully drawn (3/3) → none exported; op0/src2 drawn 1 → attempts 2,3
    assert not any(s[0] == op0 and s[1] == "src1" for s in slots)
    assert (op0, "src2", 2) in slots and (op0, "src2", 3) in slots
    assert (op0, "src2", 1) not in slots
    # untouched (op0, src3) fully present; other ops fully present
    assert {(op0, "src3", a) for a in (1, 2, 3)} <= slots


def test_resume_export_drops_completed_put(tmp_path):
    """When every slot of a PUT is drawn, no packet is written for it."""
    put = "a4"
    resume_cache = tmp_path / "same"
    resume_cache.mkdir()
    rows = []
    for o in (op for op in CAMP.OPERATORS if op.put == put):
        for slot in ("src1", "src2", "src3"):
            rows += [{"kind": "generate", "op_id": o.id, "slot": slot}] * 3
    (resume_cache / "campaign_log.jsonl").write_text(
        "\n".join(json.dumps(r) for r in rows) + "\n")
    gdir = tmp_path / "gen"
    CAMP.export_generation_packets(gdir, puts=[put], arm="same",
                                   sources=["src1", "src2", "src3"], k=3,
                                   resume_cache=resume_cache)
    assert not list(gdir.glob(f"gen_{put}.json"))


# ── 2. arm/stratum tag routing ─────────────────────────────────────────────

def test_packet_carries_stratum_tag(tmp_path):
    gdir = tmp_path / "gen"
    CAMP.export_generation_packets(gdir, puts=["c2"], arm="same",
                                   sources=["src1", "src2", "src3"],
                                   stratum="recruit", k=4)
    pk = json.loads((gdir / "gen_c2.json").read_text())
    assert pk["stratum"] == "recruit"
    assert pk["sources"] == ["src1", "src2", "src3"]
    CAMP._assert_no_outcome_fields(pk)   # tag adds no outcome leak


def test_route_ingest_cache_by_tag():
    R = CAMP._route_ingest_cache
    assert R({"stratum": "recruit", "sources": ["src1"], "arm": "same"}, False) \
        == CAMP.CACHE_DIR_STUDY4_RECRUIT
    assert R({"stratum": None, "sources": ["src1", "src2", "src3"], "arm": "same"},
             False) == CAMP.CACHE_DIR_STUDY4_SAME
    assert R({"stratum": None, "sources": ["src1", "src2", "src3"], "arm": "cross"},
             False) == CAMP.CACHE_DIR_STUDY4_CROSS
    # C lang always -> cache_clang, whatever the arm/stratum
    assert R({"stratum": "recruit", "sources": ["src1"], "arm": "cross"}, True) \
        == CAMP.CACHE_DIR_CLANG
    # legacy Study-2 sources (claude/gpt/deepseek) keep routing to cache_cross
    assert R({"stratum": None, "sources": ["claude", "gpt", "deepseek"],
              "arm": "cross"}, False) == CAMP.CACHE_DIR


def test_ingest_routes_recruit_response(tmp_path, monkeypatch):
    """Without --cache-dir, a stratum=recruit response lands in cache_study4/recruit
    (constants monkeypatched to tmp so the real repo caches are never touched)."""
    recruit = tmp_path / "recruit"
    monkeypatch.setattr(CAMP, "CACHE_DIR_STUDY4_RECRUIT", recruit)
    gdir = tmp_path / "gen"
    CAMP.export_generation_packets(gdir, puts=["c2"], arm="same",
                                   sources=["src1", "src2", "src3"],
                                   stratum="recruit", k=2)
    pk = json.loads((gdir / "gen_c2.json").read_text())
    (gdir / "gen_c2_response.json").write_text(json.dumps(_synthetic_response(pk)))
    res = CAMP.ingest_generation(gdir, packets_dir=gdir)   # NO cache_dir override
    assert res["cache_dir"] == str(recruit)
    assert list(recruit.glob("c2_*_src*_attempt*.py")), "landed in recruit cache"


# ── 3. src-tag naming ──────────────────────────────────────────────────────

def test_src_tag_naming_matches_gateway_cache(tmp_path):
    gdir = tmp_path / "gen"
    cache = tmp_path / "cache"
    CAMP.export_generation_packets(gdir, puts=["a4"], arm="same",
                                   sources=["src1", "src2", "src3"], k=3)
    pk = json.loads((gdir / "gen_a4.json").read_text())
    (gdir / "gen_a4_response.json").write_text(json.dumps(_synthetic_response(pk)))
    CAMP.ingest_generation(gdir, cache_dir=cache, packets_dir=gdir)
    names = [p.name for p in cache.glob("*.py")]
    assert names, "admitted mutants exist"
    assert all("_src" in n for n in names), "harness remainder uses src1/2/3 tags"
    assert not any(f"_{fam}_" in n for n in names for fam in ("claude", "gpt"))


# ── 4. rich_multiplier override (gateway cross baseline resume) ─────────────

def test_rich_multiplier_override_baseline():
    """attempts_for_put honours an in-memory rich_multiplier override; the frozen
    config file is never touched by the v1.2 resume."""
    from p2.config import study4 as s4
    base_cfg = s4.load_study4_config()
    assert s4.rich_multiplier(base_cfg) == 4          # frozen config pins x4
    # v1.2 in-memory override (exactly what study4_campaign builds)
    cfg1 = {**base_cfg, "rich_multiplier": 1}
    # rich PUT (c2) at BASELINE under override; A/B PUT unaffected either way
    assert s4.attempts_for_put(3, "c2", lang="py", cfg=cfg1) == 3
    assert s4.attempts_for_put(3, "c2", lang="py", cfg=base_cfg) == 12   # x4
    assert s4.attempts_for_put(3, "a1", lang="py", cfg=cfg1) == 3
    # config file on disk is unchanged (still x4)
    assert s4.rich_multiplier(s4.load_study4_config()) == 4


# ── 4b. per-arm blinded review on src-tagged caches (P7 redaction) ─────────

def test_review_export_and_ingest_on_src_tagged_arm(tmp_path):
    """export-review-packets works on a src1/src2/src3 cache (the old [a-z]+ tag
    regex silently produced 0 packets), blinds the four-vendor tokens, and the
    verdicts ingest per-arm."""
    # build a small admitted src-tagged pool via the harness path
    gdir = tmp_path / "gen"
    cache = tmp_path / "arm_same"
    CAMP.export_generation_packets(gdir, puts=["a4"], arm="same",
                                   sources=["src1", "src2", "src3"], k=2)
    pk = json.loads((gdir / "gen_a4.json").read_text())
    (gdir / "gen_a4_response.json").write_text(json.dumps(_synthetic_response(pk)))
    CAMP.ingest_generation(gdir, cache_dir=cache, packets_dir=gdir)

    rdir = tmp_path / "review"
    out = CAMP.export_review_packets(cache_dir=cache, out_dir=rdir)
    assert out["n_packets"] > 0, "src-tagged mutants must yield review packets"
    for f in rdir.glob("rev_*.json"):
        pk = json.loads(f.read_text())
        code = pk["mutant_code"].lower()
        for tok in ("claude", "gemini", "grok", "gpt", "deepseek", "fable"):
            assert tok not in code
        assert "arm" not in pk and pk["lang"] == "py"
    # private map records source per blind_id → verdicts attributable per arm
    bm = json.loads((rdir / "_blind_map.json").read_text())
    assert all(v["source"].startswith("src") for v in bm.values())
    for b in bm:
        (rdir / f"verdict_{b}.json").write_text(json.dumps({
            "blind_id": b, "V1_syntax_ok": True, "V2_executable": "Yes",
            "V3_nontrivial": "Yes", "operator_match": "Yes",
            "equivalence": {"E1": "No", "E2": "No", "equivalent": False},
            "overall": "CONFIRMED", "reason": "synthetic"}))
    ir = CAMP.ingest_review(rdir, packets_dir=rdir)
    assert len(ir["verdicts"]) == out["n_packets"]


# ── 5. recruitment stratum v1.2 power projection ───────────────────────────

def test_recruitment_stratum_v1_2_meets_gate():
    pw = _load("power_study4_v12", "scripts/power_analysis_study4.py")
    r = pw.recruitment_stratum_v1_2()
    assert r["per_put_per_arm_detect_p0"] == 0.4
    assert r["target_n_rich"] == 24 and r["prob_gate"] == 0.90
    m = r["chosen_stratum_multiplier"]
    assert m is not None and r["multiplier_curve"][m]["meets_gate"]
    assert r["chosen_P_ge_24"] >= 0.90
    # x4 alone is insufficient under the additive pooling (arms at baseline)
    assert r["x4_sufficient"] is False
