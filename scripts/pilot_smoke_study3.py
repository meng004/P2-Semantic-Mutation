#!/usr/bin/env python3
"""Study-3 calibration-pilot smoke ({a2, b4}) under the P8-fixed all-family screen.

Registration duty (PREREGISTRATION_STUDY3_v2.md §2b, §5c): the {a2,b4} pilot MUST
exercise the P8-remediated all-family single-stratum screen end-to-end and confirm
the registered smoke assertion — the wired screen matches > 0 candidates at
admission (a zero-match is the incident-P8 silent no-op and blocks the
confirmatory run). This is a PILOT run (code-level firewall §2b): it fixes/exercises
tooling only, touches no threshold/estimand/roster, and writes only PILOT-marked
outputs. It NEVER touches the frozen v5 pools and never writes a confirmatory SSOT.

Steps (each a registration-required check):
  (a) loud-fail gate — the all-family screen matches > 0 screened evaluations;
  (b) categories resolve for every pilot op_id (P8 fix; None => loud fail);
  (c) the v6 pilot pools rebuild DETERMINISTICALLY (identical selection twice);
  (d) SMS over the 10 pilot cells -> data/results/sms_track2_v6_pilot.json (PILOT);
  (e) compute_h4_graded.py consumes the pilot SMS output end-to-end (pilot smoke).

Env pinned for Study 3: P2_SCREEN_ALL_FAMILIES=1 (all-family scope), P2_PRIMARY_
VERSION=v3 (the frozen primary rule; v3b prohibited), single-stratum filter ON.

Usage:
    PYTHONPATH=src python3 scripts/pilot_smoke_study3.py
"""
from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
import time
from pathlib import Path

# Env MUST be set before importing p2.config.* (resolved at import time).
os.environ.setdefault("P2_SCREEN_ALL_FAMILIES", "1")
os.environ.setdefault("P2_PRIMARY_VERSION", "v3")
os.environ.setdefault("P2_SINGLE_STRATUM_FILTER", "1")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from p2.mutators.stratum_filter import (  # noqa: E402
    active_constrained_categories, category_from_op_id, screen_mutant,
)
from p2.config.campaign import screen_all_families_enabled  # noqa: E402

CACHE = ROOT / "data" / "operator_campaign" / "cache_cross"
MUTANTS = ROOT / "data" / "mutants"
RESULTS = ROOT / "data" / "results"
PILOT_PUTS = ["a2", "b4"]
POOL_VERSION = "v6"
REGISTERED_SEED = 20260708
PILOT_SMS_OUT = RESULTS / "sms_track2_v6_pilot.json"
PILOT_GRADED_OUT = RESULTS / "h4_graded_v6_pilot.json"


def _load_build_pools():
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "build_pools_pilot", ROOT / "scripts" / "build_pools.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _load_sms_campaign():
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "sms_campaign_pilot", ROOT / "scripts" / "sms_campaign.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _load_graded():
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "compute_h4_graded_pilot", ROOT / "scripts" / "compute_h4_graded.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# --------------------------------------------------------------------------- #
# (b) categories resolve for every pilot op_id (P8 remediation)
# --------------------------------------------------------------------------- #
def pilot_op_ids() -> list:
    ids = set()
    for fp in sorted(CACHE.glob("*_attempt*.py")):
        put = fp.name.split("_", 1)[0]
        if put in PILOT_PUTS:
            ids.add(fp.name.split("_attempt")[0])   # e.g. b4_TF1_claude
    return sorted(ids)


def check_categories_resolve() -> dict:
    op_ids = pilot_op_ids()
    unresolved = [o for o in op_ids if category_from_op_id(o) is None]
    if unresolved:
        raise SystemExit(
            f"LOUD FAIL (P8): {len(unresolved)} pilot op_id(s) failed category "
            f"resolution: {unresolved}. A null category can never be silently "
            f"admitted (incident P8).")
    by_cat: dict = {}
    for o in op_ids:
        by_cat.setdefault(category_from_op_id(o), []).append(o)
    return {"n_op_ids": len(op_ids),
            "by_category": {k: len(v) for k, v in sorted(by_cat.items())},
            "op_ids": op_ids}


# --------------------------------------------------------------------------- #
# counting all-family screen (loud-fail gate instrumentation, step a)
# --------------------------------------------------------------------------- #
class CountingScreen:
    """Wraps the registered all-family screen and records screened evaluations.

    Identical admission decision to p2.mutators.stratum_filter.make_screen_fn
    (same screen_mutant / active_constrained_categories), plus counters that back
    the registered smoke assertion: screened_evaluations MUST be > 0."""

    def __init__(self, repeats: int = 20):
        self.repeats = repeats
        self.screened_evaluations = 0
        self.admitted = 0
        self.rejected = 0
        self.unresolved = 0
        self.constrained = active_constrained_categories()

    def __call__(self, path: Path, op_id: str) -> bool:
        cat = category_from_op_id(op_id)
        if cat is None:                             # P8: never silently admit
            self.unresolved += 1
            raise ValueError(f"null category for op_id {op_id!r} (incident P8)")
        put_id = op_id.split("_", 1)[0]
        dec = screen_mutant(put_id, path, category=cat, repeats=self.repeats)
        if dec.constrained:                         # in-scope == screened
            self.screened_evaluations += 1
            if dec.admitted:
                self.admitted += 1
            else:
                self.rejected += 1
        return dec.admitted


# --------------------------------------------------------------------------- #
# build helper
# --------------------------------------------------------------------------- #
def build_pilot(mutants_dir: Path, screen) -> dict:
    bp = _load_build_pools()
    results = bp.build_pools(
        PILOT_PUTS, POOL_VERSION, CACHE, mutants_dir=mutants_dir,
        seed=REGISTERED_SEED, screen_fn=screen, verbose=False)
    selected = {}
    for r in results:
        mani = Path(r["pool_dir"]) / "manifest.json"
        if mani.exists():
            m = json.loads(mani.read_text())
            selected[r["put"]] = sorted(x["source_relpath"] for x in m["mutants"])
        else:
            selected[r["put"]] = []
    return {"results": results, "selected": selected}


def main() -> int:
    assert screen_all_families_enabled(), "P2_SCREEN_ALL_FAMILIES must be ON"
    print("=== Study-3 pilot smoke {a2,b4} — all-family screen wired ===")
    print(f"active constrained categories = {sorted(active_constrained_categories())}")

    # (b) categories resolve
    cats = check_categories_resolve()
    print(f"[b] categories resolve: {cats['n_op_ids']}/{cats['n_op_ids']} pilot "
          f"op_ids -> {cats['by_category']}")

    # (a) build v6 pilot pools with the counting all-family screen
    t0 = time.time()
    screen1 = CountingScreen(repeats=20)
    build1 = build_pilot(MUTANTS, screen1)
    dt = time.time() - t0
    if screen1.screened_evaluations <= 0:
        raise SystemExit(
            "LOUD FAIL (incident-P8 regression): the wired all-family screen "
            "matched ZERO candidates. The confirmatory run is blocked (§5c).")
    print(f"[a] loud-fail gate PASS: screened_evaluations="
          f"{screen1.screened_evaluations} (>0)  admitted={screen1.admitted} "
          f"rejected={screen1.rejected}  [{dt:.0f}s]")
    for r in build1["results"]:
        print(f"    {r['put']}_pool_{POOL_VERSION}: n_actual={r['n_actual']}")

    # (c) determinism — rebuild into a scratch dir, compare selection
    with tempfile.TemporaryDirectory() as td:
        screen2 = CountingScreen(repeats=20)
        build2 = build_pilot(Path(td), screen2)
        deterministic = build1["selected"] == build2["selected"]
        if not deterministic:
            raise SystemExit("LOUD FAIL: pilot pool selection is NOT deterministic "
                             "across rebuilds.")
    print(f"[c] determinism PASS: identical selection across two rebuilds "
          f"(a2={len(build1['selected']['a2'])}, b4={len(build1['selected']['b4'])} "
          f"mutants)")

    # (d) SMS on the 10 pilot cells -> PILOT-marked output
    sms = _load_sms_campaign()
    os.environ["POOL_VERSION"] = POOL_VERSION
    cells = [(p, mp) for p in PILOT_PUTS for mp in (1, 2, 3, 4, 5)]
    sms_matrix = {}
    for put_id, mp in cells:
        summary = sms.evaluate_cell(put_id, mp, repeats=20)
        sms_matrix[summary["cell"]] = summary
    PILOT_SMS_OUT.write_text(json.dumps(sms_matrix, indent=2, ensure_ascii=False))
    nonzero = sum(1 for c in sms_matrix.values() if c["killed"] > 0)
    insts = {c: v["inst"] for c, v in sorted(sms_matrix.items())}
    print(f"[d] SMS pilot: {len(sms_matrix)} cells -> "
          f"{PILOT_SMS_OUT.relative_to(ROOT)}  (nonzero-kill cells={nonzero})")
    print(f"    inst per cell: {insts}")

    # (e) compute_h4_graded.py consumes the pilot output end-to-end (smoke)
    graded = _load_graded()
    rep = graded.run(PILOT_SMS_OUT, PILOT_GRADED_OUT, pilot_smoke=True)
    g, s = rep["H4pp_graded"], rep["H4pp_strict"]
    print(f"[e] graded-script smoke: artefact={rep['artefact']} "
          f"mode={rep['run_mode']}")
    print(f"    H4''-graded: n_rich={g['n_rich']} rich_mean_share="
          f"{g['rich_mean_share']} boot_lower_95={g['boot_lower_95']} "
          f"-> {g['verdict']}")
    print(f"    H4''-strict: n_clean={s['n_clean_detected']} purity={s['purity']} "
          f"cp_lower_95={s['cp_lower_95']} screened={s['n_screened_candidates']} "
          f"-> {s['verdict']}")
    print(f"    wrote {PILOT_GRADED_OUT.relative_to(ROOT)} (PILOT — not confirmatory)")

    # firewall attestation
    assert not (RESULTS / "sms_track2_v6.json").exists(), \
        "confirmatory SSOT must NOT be created by the pilot"
    assert not (RESULTS / "h4_graded_v6.json").exists(), \
        "confirmatory graded SSOT must NOT be created by the pilot"
    print("[firewall] confirmatory SSOTs absent; v5 pools untouched; pilot-only.")
    print("=== pilot smoke COMPLETE ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
