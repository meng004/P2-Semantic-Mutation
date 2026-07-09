#!/usr/bin/env python3
"""Study-4 H-LANG REDUCED C-arm calibration pilot on {a3, b2} (LIVE gateway).

Calibration-permitted (code-level firewall, registration §2b′). Exercises the
NEW C-language machinery end-to-end at REDUCED scale (1 attempt per operator ×
slot instead of confirmatory K=3), over BOTH arms, THROUGH the four-vendor
gateway with ``--lang c``:

  generate C mutants (PROMPT_TEMPLATE_C) -> gcc admission (V1 = compile, V2/V3
  via the cport adapter) -> pool (v7c-PILOT-tagged) -> SMS via the cport adapter
  on those cells -> blinded review (claude-fable-5) -> ingest.

FIREWALL (registration §0.3 A2, §2b′). The C-arm pilot uses **{a3, b2}**, NOT
a2 (a2 is CONFIRMATORY in the C grid). It writes only ``v7c_pilot``-tagged
artefacts; it NEVER creates the confirmatory ``{put}_pool_v7c`` pool or the
confirmatory ``data/results/sms_track2_v7c.json``. It may fix CODE defects only,
logged P13+ in PILOT_LOG.md before any confirmatory C run. This is NEW territory
(LLMs writing C): per-vendor compile-fail rates are recorded honestly.

Usage:
    PYTHONPATH=src python3 scripts/pilot_smoke_study4_cport.py
"""
from __future__ import annotations

import importlib.util
import json
import os
import shutil
import statistics
import sys
import time
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))


def _load_env() -> None:
    if os.environ.get("BLTCY_BASE_URL") and os.environ.get("BLTCY_API_KEY"):
        return
    envf = ROOT / ".env"
    if not envf.exists():
        return
    for line in envf.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())


_load_env()

from p2.config import study4 as s4  # noqa: E402

PILOT_PUTS = ["a3", "b2"]              # a3 deterministic (heat FDM), b2 stochastic (MH)
ATTEMPTS = 1                           # REDUCED (confirmatory K=3)
POOL_VERSION = "v7c_pilot"             # NEVER the confirmatory v7c
LANG = "c"
CACHE_ROOT = ROOT / "data" / "operator_campaign" / "cache_clang_pilot"
RESULTS = ROOT / "data" / "results" / "study4"
RESULTS.mkdir(parents=True, exist_ok=True)


def _load_by_path(name: str, rel: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


CAMP = _load_by_path("cross_source_campaign_cpilot", "scripts/cross_source_campaign.py")
SMS = _load_by_path("sms_campaign_cpilot", "scripts/sms_campaign.py")


def _read_log(log_path: Path) -> list[dict]:
    if not log_path.exists():
        return []
    return [json.loads(x) for x in log_path.read_text().splitlines() if x.strip()]


def run_arm(arm: str) -> dict:
    cache = CACHE_ROOT / arm
    if cache.exists():
        shutil.rmtree(cache)
    cache.mkdir(parents=True, exist_ok=True)
    log_path = cache / "campaign_log.jsonl"
    print(f"\n=== C-ARM {arm} — slots {s4.arm_slots(arm)} (lang={LANG}) ===")
    t0 = time.time()
    out = CAMP.study4_campaign(PILOT_PUTS, arm, ATTEMPTS, cache_dir=cache,
                               log_path=log_path, review=True, lang=LANG)
    dt = time.time() - t0
    records = out["records"]
    n_pass = sum(1 for r in records if r.get("v_passed"))
    print(f"  generated {len(records)}, admitted {n_pass}  [{dt:.0f}s]")

    # pool the admitted .c files (v7c-PILOT dirs) + SMS on the pilot cells
    sms_matrix = {}
    for put in PILOT_PUTS:
        pool_dir = ROOT / "data" / "mutants" / f"{put}_pool_{POOL_VERSION}_{arm}"
        if pool_dir.exists():
            shutil.rmtree(pool_dir)
        pool_dir.mkdir(parents=True)
        for r in records:
            if r.get("put") == put and r.get("v_passed") and r.get("filename"):
                src = cache / r["filename"]
                if src.exists():
                    shutil.copy(src, pool_dir / r["filename"])
        n_pool = len(list(pool_dir.glob("*.c")))
        for mp in (1, 2, 3, 4, 5):
            cell = SMS.evaluate_cell(put, mp, mutant_dir=pool_dir, lang=LANG)
            sms_matrix[cell["cell"]] = cell
        print(f"  [{put}] pool={n_pool} .c mutants")
    nonzero = sum(1 for c in sms_matrix.values() if c["killed"] > 0)
    insts = {c: v["inst"] for c, v in sorted(sms_matrix.items())}
    print(f"  SMS: {len(sms_matrix)} cells, nonzero-kill={nonzero}, inst={insts}")

    (RESULTS / f"sms_{POOL_VERSION}_{arm}.json").write_text(
        json.dumps(sms_matrix, indent=2, ensure_ascii=False))
    return {"arm": arm, "records": records, "reviews": out["reviews"],
            "log": _read_log(log_path), "wall_s": round(dt, 1),
            "n_generated": len(records), "n_admitted": n_pass,
            "sms_nonzero": nonzero}


def per_vendor_cquality(records: list[dict], logs: list[dict]) -> dict:
    """Per-VENDOR C-code quality: compile-fail rate (V1) and admit rate.

    NEW territory (LLMs writing C). compile_fail = admitted-V1 failed
    (v_syntax False = gcc did not compile). Keyed by requested model."""
    lat = defaultdict(list)
    served = defaultdict(set)
    for r in logs:
        if r.get("kind") == "generate" and "error" not in r:
            if r.get("latency_s") is not None:
                lat[r["requested_model"]].append(r["latency_s"])
            if r.get("served_model"):
                served[r["requested_model"]].add(r["served_model"])
    by = defaultdict(lambda: {"n": 0, "compile_fail": 0, "v2_fail": 0,
                              "v3_fail": 0, "admit": 0})
    for r in records:
        m = r.get("model") or "?"
        d = by[m]
        d["n"] += 1
        if "error" in r:
            d["compile_fail"] += 1               # generation error ~ unusable body
            continue
        if not r.get("v_syntax", True):
            d["compile_fail"] += 1               # gcc did not compile (V1)
        elif not r.get("v_executable", True):
            d["v2_fail"] += 1                     # compiled but non-finite (V2)
        elif not r.get("v_nontrivial", True):
            d["v3_fail"] += 1                     # equivalent to original (V3)
        if r.get("v_passed"):
            d["admit"] += 1
    out = {}
    for m, d in by.items():
        out[m] = {
            "n_calls": d["n"],
            "compile_fail": d["compile_fail"],
            "compile_fail_rate": round(d["compile_fail"] / d["n"], 3) if d["n"] else None,
            "v2_nonfinite_fail": d["v2_fail"],
            "v3_trivial_fail": d["v3_fail"],
            "admitted": d["admit"],
            "admit_rate": round(d["admit"] / d["n"], 3) if d["n"] else None,
            "mean_latency_s": round(statistics.mean(lat[m]), 2) if lat[m] else None,
            "served_as": sorted(served[m]),
        }
    return out


def main() -> int:
    if not (os.environ.get("BLTCY_BASE_URL") and os.environ.get("BLTCY_API_KEY")):
        print("FATAL: BLTCY_BASE_URL / BLTCY_API_KEY not set (.env missing?)")
        return 2
    print("=== Study-4 H-LANG REDUCED C-arm pilot {a3,b2} — LIVE four-vendor gateway ===")
    print(f"attempts/op/slot={ATTEMPTS}  lang={LANG}  pool={POOL_VERSION}")

    arms = {a: run_arm(a) for a in ("same", "cross")}
    all_records = arms["same"]["records"] + arms["cross"]["records"]
    all_logs = arms["same"]["log"] + arms["cross"]["log"]
    reviews = [r for r in all_logs if r.get("kind") == "review"]
    arbitrations = [r for r in all_logs if r.get("kind") == "arbitrate"]

    cq = per_vendor_cquality(all_records, all_logs)
    n_admit = sum(1 for r in all_records if r.get("v_passed"))

    report = {
        "pilot": "study4_hlang_cport_reduced_{a3,b2}",
        "lang": LANG, "attempts_per_op_slot": ATTEMPTS, "pool_version": POOL_VERSION,
        "firewall": "a2 is CONFIRMATORY in the C grid; pilot uses {a3,b2} only; "
                    "v7c_pilot-tagged; confirmatory sms_track2_v7c.json + "
                    "{put}_pool_v7c NEVER created (registration §0.3 A2, §2b′)",
        "arms": {a: {"n_generated": arms[a]["n_generated"],
                     "n_admitted": arms[a]["n_admitted"],
                     "wall_s": arms[a]["wall_s"],
                     "sms_nonzero_cells": arms[a]["sms_nonzero"],
                     "n_reviews": len(arms[a]["reviews"])} for a in arms},
        "per_vendor_c_code_quality": cq,
        "totals": {"n_generations": len(all_records), "n_admitted": n_admit,
                   "admit_rate": round(n_admit / len(all_records), 3)
                   if all_records else 0.0,
                   "n_reviews": len(reviews), "n_arbitrations": len(arbitrations)},
    }
    (RESULTS / "cport_pilot_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False))

    print("\n=== PER-VENDOR C-CODE QUALITY (LLMs writing C — NEW territory) ===")
    for model, s in sorted(cq.items()):
        print(f"  {model:18s} n={s['n_calls']:2d} compile_fail="
              f"{s['compile_fail']}/{s['n_calls']} ({s['compile_fail_rate']}) "
              f"admit={s['admitted']}/{s['n_calls']} ({s['admit_rate']}) "
              f"lat={s['mean_latency_s']}s served={s['served_as']}")

    # firewall attestation (assertions)
    assert not (ROOT / "data" / "results" / "sms_track2_v7c.json").exists(), \
        "pilot must NOT create the confirmatory C-port SSOT"
    for put in ("a1", "a2", "a3", "b1", "b2", "b3", "c2"):
        assert not (ROOT / "data" / "mutants" / f"{put}_pool_v7c").exists(), \
            f"pilot must NOT create the confirmatory {put}_pool_v7c pool"
    for put in PILOT_PUTS:
        pass  # a2 is deliberately absent from PILOT_PUTS (confirmatory firewall)
    assert "a2" not in PILOT_PUTS, "a2 is confirmatory; pilot must not touch it"
    print(f"\n[firewall] v7c_pilot-only; a2 untouched; wrote "
          f"{RESULTS}/cport_pilot_report.json")
    print("=== Study-4 C-arm pilot COMPLETE (confirmatory NOT started) ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
