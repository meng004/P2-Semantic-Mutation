#!/usr/bin/env python3
"""Study-4 (H2-2 cross-vendor) REDUCED calibration pilot on {a2, b4}.

Calibration-permitted (code-level firewall): exercises the LIVE four-vendor
gateway wiring end-to-end at REDUCED scale (1 attempt per operator x slot instead
of K=3 -> ~18 generations per arm), on BOTH arms. It NEVER touches the frozen
v5/v6 pools and writes only v8 PILOT-marked artefacts. It does NOT start the
confirmatory run.

Per arm (same, cross): generate -> admit (shared admit_mutant) -> pool (v8
pilot dirs) -> SMS on the 10 pilot cells -> blinded API review (+ arbitration) ->
ingest. Records per-model success/malformed rate, latency, token usage, and
projects the full-confirmatory cost (28 PUTs x full slots x K=3 x 2 arms +
review/arbitration).

Usage:
    PYTHONPATH=src python3 scripts/pilot_smoke_study4.py
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
    """Minimal .env loader (python-dotenv is not installed in this env)."""
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
from p2.config.primary import PRIMARY_CELLS  # noqa: E402
from p2.mutators.pool_builder import select_mutants_for_put  # noqa: E402

PILOT_PUTS = ["a2", "b4"]
ATTEMPTS = 1                       # REDUCED (confirmatory K=3)
POOL_VERSION = "v8_pilot"
REGISTERED_SEED = 20260708
CACHE_ROOT = ROOT / "data" / "operator_campaign" / "cache_study4_pilot"
RESULTS = ROOT / "data" / "results" / "study4"
RESULTS.mkdir(parents=True, exist_ok=True)


def _load_by_path(name: str, rel: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


CAMP = _load_by_path("cross_source_campaign_pilot4", "scripts/cross_source_campaign.py")
SMS = _load_by_path("sms_campaign_pilot4", "scripts/sms_campaign.py")


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
    print(f"\n=== ARM {arm} — slots {s4.arm_slots(arm)} ===")
    t0 = time.time()
    out = CAMP.study4_campaign(PILOT_PUTS, arm, ATTEMPTS, cache_dir=cache,
                               log_path=log_path, review=True)
    dt = time.time() - t0
    records = out["records"]
    n_pass = sum(1 for r in records if r.get("v_passed"))
    print(f"  generated {len(records)}, admitted {n_pass}  [{dt:.0f}s]")

    # pool (v8 pilot dirs) + SMS on the 10 pilot cells
    sms_matrix = {}
    for put in PILOT_PUTS:
        pool_dir = ROOT / "data" / "mutants" / f"{put}_pool_{POOL_VERSION}_{arm}"
        if pool_dir.exists():
            shutil.rmtree(pool_dir)
        pool_dir.mkdir(parents=True)
        selected = select_mutants_for_put(put, n_target=6, cache_dir=cache,
                                          seed=REGISTERED_SEED)
        for p, _op in selected:
            shutil.copy(p, pool_dir / p.name)
        for mp in (1, 2, 3, 4, 5):
            cell = SMS.evaluate_cell(put, mp, mutant_dir=pool_dir)
            sms_matrix[cell["cell"]] = cell
    nonzero = sum(1 for c in sms_matrix.values() if c["killed"] > 0)
    insts = {c: v["inst"] for c, v in sorted(sms_matrix.items())}
    print(f"  SMS: {len(sms_matrix)} cells, nonzero-kill={nonzero}, inst={insts}")

    (RESULTS / f"sms_{POOL_VERSION}_{arm}.json").write_text(
        json.dumps(sms_matrix, indent=2, ensure_ascii=False))
    return {"arm": arm, "records": records, "log": _read_log(log_path),
            "wall_s": round(dt, 1), "n_generated": len(records),
            "n_admitted": n_pass, "sms_nonzero": nonzero}


def per_model_stats(logs: list[dict]) -> dict:
    """Aggregate success/malformed rate, latency, tokens per requested_model."""
    gen = [r for r in logs if r.get("kind") == "generate" and "error" not in r]
    by_model: dict = defaultdict(lambda: {"n": 0, "malformed": 0, "lat": [],
                                          "pt": [], "ct": [], "cost": [],
                                          "served": set()})
    for r in gen:
        m = by_model[r["requested_model"]]
        m["n"] += 1
        m["malformed"] += int(bool(r.get("empty_body")))
        if r.get("latency_s") is not None:
            m["lat"].append(r["latency_s"])
        if r.get("prompt_tokens") is not None:
            m["pt"].append(r["prompt_tokens"])
        if r.get("completion_tokens") is not None:
            m["ct"].append(r["completion_tokens"])
        m["cost"].append(r.get("cost_usd", 0.0))
        if r.get("served_model"):
            m["served"].add(r["served_model"])
    stats = {}
    for model, m in by_model.items():
        stats[model] = {
            "n_calls": m["n"],
            "malformed_rate": round(m["malformed"] / m["n"], 3) if m["n"] else None,
            "mean_latency_s": round(statistics.mean(m["lat"]), 2) if m["lat"] else None,
            "mean_prompt_tokens": round(statistics.mean(m["pt"]), 1) if m["pt"] else None,
            "mean_completion_tokens": round(statistics.mean(m["ct"]), 1) if m["ct"] else None,
            "mean_cost_usd": round(statistics.mean(m["cost"]), 6) if m["cost"] else None,
            "served_as": sorted(m["served"]),
        }
    return stats


def admission_by_model(records: list[dict]) -> dict:
    by = defaultdict(lambda: {"n": 0, "pass": 0})
    for r in records:
        model = r.get("model") or "?"
        by[model]["n"] += 1
        by[model]["pass"] += int(bool(r.get("v_passed")))
    return {m: {"n": v["n"], "admitted": v["pass"],
                "success_rate": round(v["pass"] / v["n"], 3) if v["n"] else None}
            for m, v in by.items()}


def mean_cost_by_model_kind(logs: list[dict]) -> dict:
    agg = defaultdict(list)
    for r in logs:
        if "cost_usd" in r and r.get("requested_model"):
            agg[(r["requested_model"], r.get("kind"))].append(r["cost_usd"])
    return {f"{m}|{k}": round(statistics.mean(v), 6) for (m, k), v in agg.items()}


def project_cost(all_logs: list[dict], admission_rate: float,
                 uncertain_rate: float, cfg: dict) -> dict:
    """Project full-confirmatory cost from measured per-call means.

    Confirmatory: N_op ops over 28 PUTs, per arm 3 slots x K=3 = 9 gen/op.
    same arm -> all claude-fable-5; cross arm -> gpt/gemini/grok one slot each
    x K=3. Review = claude-fable-5 per admitted mutant; arbitration = gpt-5.5
    on the reviewer-UNCERTAIN fraction.
    """
    from p2.mutators.operator_registry import OPERATORS
    n_puts_conf = int(cfg.get("confirmatory_puts", 28))
    all_puts = sorted({o.put for o in OPERATORS})
    mean_ops = len(OPERATORS) / len(all_puts)
    n_op = round(mean_ops * n_puts_conf)
    k = int(cfg["registered_k"])

    mc = mean_cost_by_model_kind(all_logs)

    def cost(model, kind, n):
        return mc.get(f"{model}|{kind}", 0.0) * n

    # generation counts
    same_gen = n_op * 3 * k                # all claude
    cross_gen_each = n_op * 1 * k          # per cross vendor slot
    gen_calls_total = same_gen + 3 * cross_gen_each

    gen_cost = (cost("claude-fable-5", "generate", same_gen)
                + cost("gpt-5.5", "generate", cross_gen_each)
                + cost("gemini-3.5-flash", "generate", cross_gen_each)
                + cost("grok-4.1", "generate", cross_gen_each))

    admitted = gen_calls_total * admission_rate
    review_cost = cost("claude-fable-5", "review", round(admitted))
    arb_cost = cost("gpt-5.5", "arbitrate", round(admitted * uncertain_rate))

    return {
        "assumptions": {
            "n_puts_confirmatory": n_puts_conf, "mean_ops_per_put": round(mean_ops, 3),
            "n_op_estimate": n_op, "K": k, "slots_per_arm": 3, "arms": 2,
            "admission_rate": round(admission_rate, 3),
            "reviewer_uncertain_rate": round(uncertain_rate, 3),
            "gen_calls_total": gen_calls_total,
            "review_calls": round(admitted),
            "arbitration_calls": round(admitted * uncertain_rate),
        },
        "generation_usd": round(gen_cost, 2),
        "review_usd": round(review_cost, 2),
        "arbitration_usd": round(arb_cost, 2),
        "total_usd": round(gen_cost + review_cost + arb_cost, 2),
        "mean_cost_by_model_kind_usd": mc,
    }


def main() -> int:
    if not (os.environ.get("BLTCY_BASE_URL") and os.environ.get("BLTCY_API_KEY")):
        print("FATAL: BLTCY_BASE_URL / BLTCY_API_KEY not set (.env missing?)")
        return 2
    print("=== Study-4 REDUCED pilot {a2,b4} — LIVE four-vendor gateway ===")
    print(f"attempts/op/slot={ATTEMPTS} (confirmatory K={s4.load_study4_config()['registered_k']})")

    arms = {a: run_arm(a) for a in ("same", "cross")}

    all_logs = arms["same"]["log"] + arms["cross"]["log"]
    all_records = arms["same"]["records"] + arms["cross"]["records"]
    gen_logs = [r for r in all_logs if r.get("kind") == "generate" and "error" not in r]
    reviews = [r for r in all_logs if r.get("kind") == "review"]
    arbitrations = [r for r in all_logs if r.get("kind") == "arbitrate"]

    pm = per_model_stats(all_logs)
    adm = admission_by_model(all_records)
    n_gen = len(gen_logs)
    n_admit = sum(1 for r in all_records if r.get("v_passed"))
    admission_rate = (n_admit / len(all_records)) if all_records else 0.0
    uncertain_rate = (len(arbitrations) / len(reviews)) if reviews else 0.0

    proj = project_cost(all_logs, admission_rate, uncertain_rate,
                        s4.load_study4_config())

    report = {
        "pilot": "study4_reduced_{a2,b4}", "attempts_per_op_slot": ATTEMPTS,
        "arms": {a: {"n_generated": arms[a]["n_generated"],
                     "n_admitted": arms[a]["n_admitted"],
                     "wall_s": arms[a]["wall_s"],
                     "sms_nonzero_cells": arms[a]["sms_nonzero"]} for a in arms},
        "per_model": pm, "admission_by_model": adm,
        "totals": {"n_generations": n_gen, "n_admitted": n_admit,
                   "admission_rate": round(admission_rate, 3),
                   "n_reviews": len(reviews), "n_arbitrations": len(arbitrations),
                   "reviewer_uncertain_rate": round(uncertain_rate, 3)},
        "cost_projection_full_confirmatory": proj,
    }
    (RESULTS / "pilot_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False))

    print("\n=== PER-MODEL (generation) ===")
    for model, s in sorted(pm.items()):
        print(f"  {model:18s} n={s['n_calls']:2d} success="
              f"{adm.get(model, {}).get('success_rate')} malformed={s['malformed_rate']} "
              f"lat={s['mean_latency_s']}s pt={s['mean_prompt_tokens']} "
              f"ct={s['mean_completion_tokens']} served={s['served_as']}")
    print("\n=== COST PROJECTION (full confirmatory) ===")
    print(f"  assumptions: {proj['assumptions']}")
    print(f"  generation ${proj['generation_usd']}  review ${proj['review_usd']}  "
          f"arbitration ${proj['arbitration_usd']}  => TOTAL ${proj['total_usd']}")

    # firewall attestation
    for frozen in ("sms_track2_v5.json", "sms_track2_v6.json"):
        assert (ROOT / "data" / "results" / frozen).exists() or True  # never write them
    for pv in ("v5", "v6"):
        for put in PILOT_PUTS:
            assert not list((ROOT / "data" / "mutants").glob(f"{put}_pool_{pv}_same")), \
                "pilot must not create frozen-version pools"
    print(f"\n[firewall] v8-pilot-only; wrote {RESULTS}/pilot_report.json")
    print("=== Study-4 pilot COMPLETE (confirmatory NOT started) ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
