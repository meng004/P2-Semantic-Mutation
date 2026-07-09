"""Packet export/ingest fixture for one C PUT (Study-4 --lang c wiring).

Covers: export a C generation packet, hand-craft a valid C-mutant
response, ingest it through the SAME admission path (gcc + adapter), and
score the admitted C mutant via sms_campaign.evaluate_cell (MRs
unmodified). Also asserts the packet carries no outcome-leak fields.
"""
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))


def _load_script(name):
    spec = importlib.util.spec_from_file_location(f"_{name}", ROOT / "scripts" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


csc = _load_script("cross_source_campaign")
smsc = _load_script("sms_campaign")


def test_export_c_packet_shape(tmp_path):
    csc.export_generation_packets(tmp_path, puts=["a2"], arm="cross", k=2, lang="c")
    pk = json.loads((tmp_path / "gen_c_a2.json").read_text())
    assert pk["lang"] == "c"
    assert pk["put_id"] == "a2"
    assert pk["put_source"].lstrip().startswith("/*")   # C source, not Python
    assert "```c```" in pk["operators"][0]["prompts_by_attempt"]["1"] or \
           "```c" in pk["operators"][0]["prompts_by_attempt"]["1"]
    # blinding: no outcome fields anywhere
    csc._assert_no_outcome_fields(pk)


def test_c_packet_roundtrip_ingest_and_score(tmp_path):
    csc.export_generation_packets(tmp_path, puts=["a2"], arm="cross", k=2, lang="c")
    pk = json.loads((tmp_path / "gen_c_a2.json").read_text())
    # craft a valid C mutant: a2_CE1  (2+x -> 2-x)
    mutated = pk["put_source"].replace("{2.0 + x, x}", "{2.0 - x, x}")
    assert mutated != pk["put_source"]
    slots = [s for s in pk["required_slots"] if s["op_id"] == "a2_CE1"][:2]
    resp = {
        "packet_id": pk["packet_id"], "put_id": pk["put_id"],
        "mutants": [{"op_id": s["op_id"], "source": s["source"],
                     "attempt": s["attempt"], "code": "```c\n" + mutated + "\n```"}
                    for s in slots],
    }
    (tmp_path / "gen_c_a2_response.json").write_text(json.dumps(resp))

    cache = tmp_path / "cache_clang"
    out = csc.ingest_generation(tmp_path, cache_dir=cache, packets_dir=tmp_path)
    admitted = [r for r in out["records"] if r.get("v_passed")]
    assert len(admitted) == 2
    assert all(r["lang"] == "c" for r in out["records"])
    c_files = sorted(cache.glob("*.c"))
    assert len(c_files) == 2

    # score the admitted C mutants via the adapter path (MRs unchanged)
    from p2.config.primary import PRIMARY_CELLS
    res = smsc.evaluate_cell("a2", PRIMARY_CELLS["a2"], mutant_dir=cache, lang="c")
    assert res["inst"] == 2
    assert res["killed"] + res["survive"] + res["equiv"] == 2
