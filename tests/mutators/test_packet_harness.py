"""Offline tests for the Study-2 PACKET (harness-mode) campaign adapter.

Harness mode lets Claude-agent instances serve as generator/reviewer with NO
network API, while the offline pipeline (normalization, V1-V4, dedup, AVP/equiv,
SMS bookkeeping) stays EXACTLY the registered machinery. These tests exercise
the full packet round-trip on 2 PUTs (a2 = existing, a4 = new):

  export generation packets → synthetic agent responses (well-formed + malformed)
  → ingest (strict) → per-PUT admitted cache → pool/dedup → SMS cell appears;
  export blinded review packets → verdicts (incl. UNCERTAIN) → ingest + arbitration.

scripts/ is not a package, so both modules are loaded by path.
"""
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


CAMP = _load("cross_source_campaign_pkt", "scripts/cross_source_campaign.py")
SMS = _load("sms_campaign_pkt", "scripts/sms_campaign.py")

PUTS = ["a2", "a4"]  # one existing, one Study-2 expansion PUT


def _wrap(orig: str, delta: float) -> str:
    return orig + f"\n\n_o = program\ndef program(x):\n    return float(_o(x)) + {delta}\n"


def _synthetic_response(packet: dict, delta0: float = 0.1) -> dict:
    """One well-formed mutant per declared slot."""
    orig = packet["put_source"]
    muts, d = [], delta0
    for op in packet["operators"]:
        for source in packet["sources"]:
            for attempt in range(1, packet["k_per_source"] + 1):
                d += 0.013
                muts.append({"op_id": op["spec"]["id"], "source": source,
                             "attempt": attempt, "code": _wrap(orig, round(d, 3))})
    return {"packet_id": packet["packet_id"], "put_id": packet["put_id"],
            "mutants": muts}


# ── Export: generation packets ─────────────────────────────────────────────

def test_export_generation_packets_shape(tmp_path):
    gdir = tmp_path / "gen"
    CAMP.export_generation_packets(gdir, puts=PUTS, arm="cross", k=3)
    assert {p.name for p in gdir.glob("gen_*.json")} == {"gen_a2.json", "gen_a4.json"}
    pk = json.loads((gdir / "gen_a2.json").read_text())
    # registered prompt template is pinned by content hash
    assert pk["registered_prompt_template"]["sha256"] and \
        pk["registered_prompt_template"]["source"].endswith("PROMPT_TEMPLATE")
    # MR definitions carried with their available MP indices
    assert pk["mr_definitions"]["available_mps"] == [1, 2, 3, 4, 5]
    # operator specs present; CF/TF constraint flag surfaced (integration point)
    for op in pk["operators"]:
        assert "constraint_flag" in op["spec"]
    # seed + response schema present; slot bookkeeping consistent
    assert pk["seed"] == CAMP.REGISTERED_SEED
    assert pk["response_schema"]["required_top_level"] == ["packet_id", "put_id", "mutants"]
    assert pk["mutant_count_target"]["packet_total"] == len(pk["required_slots"])


def test_generation_packet_has_no_outcome_fields(tmp_path):
    gdir = tmp_path / "gen"
    CAMP.export_generation_packets(gdir, puts=PUTS, arm="cross", k=3)
    for f in gdir.glob("gen_*.json"):
        pk = json.loads(f.read_text())
        # The contract is "no SMS/outcome KEY anywhere" (schema-doc string
        # VALUES that name the forbidden fields are fine).
        CAMP._assert_no_outcome_fields(pk)  # raises on any sms/kill/outcome key
        # spot-check the outcome-bearing keys of a scored cell are truly absent
        assert "sms" not in pk and "outcomes" not in pk and "killed" not in pk


# ── Round-trip: export → responses → ingest → SMS ──────────────────────────

def test_packet_roundtrip_to_sms(tmp_path):
    from p2.mutators.pool_builder import select_mutants_for_put
    import shutil

    gdir = tmp_path / "gen"
    cache = tmp_path / "cache"
    CAMP.export_generation_packets(gdir, puts=PUTS, arm="cross", k=3)
    for put in PUTS:
        pk = json.loads((gdir / f"gen_{put}.json").read_text())
        (gdir / f"gen_{put}_response.json").write_text(
            json.dumps(_synthetic_response(pk)))

    res = CAMP.ingest_generation(gdir, cache_dir=cache, packets_dir=gdir)
    assert res["per_put"]["a2"]["n_admitted"] == 27  # 3 ops × 3 sources × 3
    assert res["per_put"]["a4"]["n_admitted"] == 27
    assert res["per_put"]["a2"]["n_gaps"] == 0
    # admitted mutants named under the registered convention
    assert len(list(cache.glob("a2_*_attempt*.py"))) == 27

    # offline pipeline (dedup → AVP/equiv → SMS) runs unchanged → cells appear
    for put in PUTS:
        sel = select_mutants_for_put(put, n_target=6, cache_dir=cache,
                                     seed=CAMP.REGISTERED_SEED)
        pool = cache / f"pool_{put}"
        pool.mkdir()
        for p, _ in sel:
            shutil.copy(p, pool / p.name)
        cell = SMS.evaluate_cell(put, CAMP.PRIMARY_CELLS[put], mutant_dir=pool)
        assert cell["cell"] == f"{put.upper()}_MP{CAMP.PRIMARY_CELLS[put]}"
        assert cell["inst"] > 0


def test_ingest_rejects_malformed_generation(tmp_path):
    gdir = tmp_path / "gen"
    cache = tmp_path / "cache"
    CAMP.export_generation_packets(gdir, puts=["a2"], arm="cross", k=3)
    pk = json.loads((gdir / "gen_a2.json").read_text())
    resp = _synthetic_response(pk)
    op0 = pk["operators"][0]["spec"]["id"]
    # (a) missing 'code'; (b) forbidden SMS/outcome field
    resp["mutants"].append({"op_id": op0, "source": "gpt", "attempt": 1})
    resp["mutants"].append({"op_id": op0, "source": "claude", "attempt": 1,
                            "code": "def program(x): return x", "sms": 0.5})
    (gdir / "gen_a2_response.json").write_text(json.dumps(resp))
    # (c) not-JSON file, (d) response for a nonexistent packet
    (gdir / "garbage.json").write_text("{not json")
    (gdir / "orphan_response.json").write_text(
        json.dumps({"packet_id": "gen_ZZ", "put_id": "zz", "mutants": []}))

    res = CAMP.ingest_generation(gdir, cache_dir=cache, packets_dir=gdir)
    # well-formed 27 still admitted; malformed did not crash ingest
    assert res["per_put"]["a2"]["n_admitted"] == 27
    all_errs = [e for f in res["errors"] for e in f["errors"]]
    joined = " ".join(all_errs)
    assert "missing field(s) ['code']" in joined
    assert "forbidden outcome field(s) ['sms']" in joined
    assert any("invalid JSON" in e for e in all_errs)
    assert any("no matching packet" in e for e in all_errs)


# ── Review packets: blinding, ingest, arbitration ──────────────────────────

def _admit_a_pool(tmp_path):
    gdir = tmp_path / "gen"
    cache = tmp_path / "cache"
    CAMP.export_generation_packets(gdir, puts=PUTS, arm="cross", k=3)
    for put in PUTS:
        pk = json.loads((gdir / f"gen_{put}.json").read_text())
        (gdir / f"gen_{put}_response.json").write_text(
            json.dumps(_synthetic_response(pk)))
    CAMP.ingest_generation(gdir, cache_dir=cache, packets_dir=gdir)
    return cache


def test_review_packets_are_blinded(tmp_path):
    cache = _admit_a_pool(tmp_path)
    rdir = tmp_path / "review"
    out = CAMP.export_review_packets(cache_dir=cache, out_dir=rdir)
    assert out["n_packets"] == 54
    for f in rdir.glob("rev_*.json"):
        pk = json.loads(f.read_text())
        flat = json.dumps(pk).lower()
        # no generator identity, no arm label, no cell aggregate / SMS
        assert "claude" not in flat and "gpt" not in flat and "deepseek" not in flat
        assert "arm" not in pk and "source" not in pk
        CAMP._assert_no_outcome_fields(pk)
        # still carries what the reviewer legitimately needs
        assert pk["mutant_code"] and pk["put_source"] and pk["operator"]["id"]
        assert pk["response_schema"]["required_top_level"][0] == "blind_id"
    # private audit map exists and maps blind_id → source (never in packet)
    bm = json.loads((rdir / "_blind_map.json").read_text())
    assert all(v["source"] in ("claude", "gpt", "deepseek") for v in bm.values())


def test_review_ingest_and_arbitration(tmp_path):
    cache = _admit_a_pool(tmp_path)
    rdir = tmp_path / "review"
    CAMP.export_review_packets(cache_dir=cache, out_dir=rdir)
    bm = json.loads((rdir / "_blind_map.json").read_text())
    ids = sorted(bm)
    for i, b in enumerate(ids):
        overall = "UNCERTAIN" if i == 0 else "CONFIRMED"
        (rdir / f"verdict_{b}.json").write_text(json.dumps({
            "blind_id": b, "V1_syntax_ok": True, "V2_executable": "Yes",
            "V3_nontrivial": "Yes", "operator_match": "Yes",
            "equivalence": {"E1": "No", "E2": "No", "equivalent": False},
            "overall": overall, "reason": "synthetic"}))
    # a malformed verdict (bad domain + missing keys)
    (rdir / "verdict_bad.json").write_text(json.dumps(
        {"blind_id": "rev_x", "overall": "MAYBE", "equivalence": {}}))

    ir = CAMP.ingest_review(rdir, packets_dir=rdir)
    assert len(ir["verdicts"]) == len(ids)
    assert len(ir["errors"]) == 1
    assert len(ir["arbitration"]) == 1  # the one UNCERTAIN
    arb = list((rdir / "arbitration").glob("*.json"))
    assert len(arb) == 1
    assert json.loads(arb[0].read_text())["arbitration"] is True


# ── Manifest / determinism / shared-ingestion-path invariants ──────────────

def test_manifest_records_hashes_and_mapping(tmp_path):
    cache = _admit_a_pool(tmp_path)
    gman = json.loads((tmp_path / "gen" / "manifest.json").read_text())
    assert {e["put"] for e in gman["generation_packets"]} == set(PUTS)
    assert all(len(e["sha256"]) == 64 for e in gman["generation_packets"])
    assert {e["put"] for e in gman["generation_responses"]} == set(PUTS)
    rdir = tmp_path / "review"
    CAMP.export_review_packets(cache_dir=cache, out_dir=rdir)
    rman = json.loads((rdir / "manifest.json").read_text())
    assert len(rman["review_packets"]) == 54
    assert all("packet_sha256" in e for e in rman["review_packets"])


def test_ingestion_is_order_independent(tmp_path):
    """Admitted filenames depend only on (op, source, attempt), never on the
    order the agent listed mutants — so ingestion is deterministic."""
    gdir = tmp_path / "gen"
    CAMP.export_generation_packets(gdir, puts=["a2"], arm="cross", k=3)
    pk = json.loads((gdir / "gen_a2.json").read_text())
    resp = _synthetic_response(pk)

    c1 = tmp_path / "c1"
    (gdir / "gen_a2_response.json").write_text(json.dumps(resp))
    CAMP.ingest_generation(gdir, cache_dir=c1, packets_dir=gdir)

    c2 = tmp_path / "c2"
    resp2 = dict(resp, mutants=list(reversed(resp["mutants"])))
    (gdir / "gen_a2_response.json").write_text(json.dumps(resp2))
    CAMP.ingest_generation(gdir, cache_dir=c2, packets_dir=gdir)

    assert {p.name for p in c1.glob("*.py")} == {p.name for p in c2.glob("*.py")}


def test_blind_id_is_stable_and_opaque():
    b = CAMP._blind_id("a2_OS1", "claude", 1)
    assert b == CAMP._blind_id("a2_OS1", "claude", 1)  # deterministic
    assert "claude" not in b and "a2" not in b          # opaque (no leak)
