"""POST-HOC cross-vendor shadow review of a stratified sample of the FROZEN
Study-4 blinded review packets, for inter-vendor reviewer-reliability (kappa).

NOT REGISTERED. Responds to the manuscript's own limitation (single-family
reviewer; the review side untested for vendor effects) and to the final-review
panel. The frozen labels are NEVER modified; shadow verdicts are recorded in a
separate SSOT. Shadow reviewers see EXACTLY the frozen blinded packet's
review_prompt (text-only judgment; they cannot execute code, which is itself
reported as an evidence-level difference).

Strata (seed 20260708):
  A: every frozen REJECTED (all arms)
  B: every bounds="fixed" GP mutant frozen CONFIRMED (the ambiguity family)
  C: 100 random frozen CONFIRMED, proportional across arms
Shadow vendors: gpt-5.5, gemini-3.5-flash (both non-Anthropic; the frozen
reviewer was claude-family; the arbiter model gpt-5.5 also arbitrated the two
UNCERTAINs, disclosed).
"""
import json
import re
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
from cross_source_campaign import _study4_call, _parse_review_json  # noqa: E402
from p2.mutators.llm_client import study4_client  # noqa: E402

SEED = 20260708
ARMS = ["same", "cross", "recruit", "c"]
CACHES = {"same": "data/operator_campaign/cache_study4/same",
          "cross": "data/operator_campaign/cache_study4/cross",
          "recruit": "data/operator_campaign/cache_study4/recruit",
          "c": "data/operator_campaign/cache_clang"}
VENDORS = ["gpt-5.5", "gemini-3.5-flash"]
LOG = ROOT / "data/study4_packets/shadow_kappa_log.jsonl"


def frame():
    rows = []
    for arm in ARMS:
        d = ROOT / f"data/study4_packets/review_{arm}"
        bm = json.loads((d / "_blind_map.json").read_text())
        for bid, info in bm.items():
            r = json.loads((d / f"{bid}_response.json").read_text())
            mf = ROOT / CACHES[arm] / info["mutant_file"]
            bounds = bool(re.search(r'bounds\s*=\s*"fixed"', mf.read_text())) if mf.exists() else False
            rows.append({"arm": arm, "blind_id": bid, "dir": str(d),
                         "frozen": r["overall"], "bounds_fixed": bounds})
    return rows


def sample(rows):
    rng = np.random.default_rng(SEED)
    a = [r for r in rows if r["frozen"] == "REJECTED"]
    b = [r for r in rows if r["frozen"] == "CONFIRMED" and r["bounds_fixed"]]
    conf = [r for r in rows if r["frozen"] == "CONFIRMED" and not r["bounds_fixed"]]
    # proportional-by-arm random CONFIRMED, total 100
    c = []
    total = len(conf)
    for arm in ARMS:
        pool = [r for r in conf if r["arm"] == arm]
        k = max(1, round(100 * len(pool) / total))
        idx = rng.choice(len(pool), size=min(k, len(pool)), replace=False)
        c.extend(pool[i] for i in idx)
    for r in a: r["stratum"] = "A_rejected"
    for r in b: r["stratum"] = "B_bounds_fixed_confirmed"
    for r in c: r["stratum"] = "C_random_confirmed"
    return a + b + c


def kappa(y1, y2):
    labs = sorted(set(y1) | set(y2))
    idx = {l: i for i, l in enumerate(labs)}
    m = np.zeros((len(labs), len(labs)))
    for u, v in zip(y1, y2):
        m[idx[u], idx[v]] += 1
    n = m.sum(); po = np.trace(m) / n
    pe = float(sum(m[i].sum() * m[:, i].sum() for i in range(len(labs))) / n**2)
    return round(float((po - pe) / (1 - pe)), 4) if pe < 1 else 1.0


def main():
    rows = sample(frame())
    print(f"sample: {len(rows)} packets "
          f"(A={sum(r['stratum']=='A_rejected' for r in rows)}, "
          f"B={sum(r['stratum']=='B_bounds_fixed_confirmed' for r in rows)}, "
          f"C={sum(r['stratum']=='C_random_confirmed' for r in rows)})", flush=True)
    out_rows = []
    for i, r in enumerate(rows):
        pk = json.loads((Path(r["dir"]) / f"{r['blind_id']}.json").read_text())
        prompt = pk["review_prompt"]
        rec = dict(r)
        for vendor in VENDORS:
            fac = (lambda m=vendor: study4_client(m))
            try:
                raw, meta = _study4_call(fac, prompt, kind="shadow-review",
                                         slot_tag=f"shadow-{vendor}",
                                         op_id=pk["operator"]["id"],
                                         log_path=LOG, max_tokens=2000)
                parsed = _parse_review_json(raw)
                rec[vendor] = parsed.get("overall", "UNCERTAIN")
            except Exception as e:
                rec[vendor] = f"ERROR:{type(e).__name__}"
        out_rows.append(rec)
        if (i + 1) % 20 == 0:
            print(f"  {i+1}/{len(rows)} done", flush=True)
    ok = [r for r in out_rows if all(not str(r[v]).startswith("ERROR") for v in VENDORS)]
    frozen = [r["frozen"] for r in ok]
    res = {"artefact": "review_shadow_kappa_v7",
           "status": "POST-HOC cross-vendor reviewer-reliability check; frozen labels untouched",
           "seed": SEED, "n_sampled": len(rows), "n_scored": len(ok),
           "strata": {s: sum(r["stratum"] == s for r in rows) for s in
                      ("A_rejected", "B_bounds_fixed_confirmed", "C_random_confirmed")},
           "kappa_vs_frozen": {}, "kappa_between_shadows": None,
           "per_stratum_agreement": {}, "rows": out_rows}
    for v in VENDORS:
        res["kappa_vs_frozen"][v] = kappa(frozen, [r[v] for r in ok])
    res["kappa_between_shadows"] = kappa([r[VENDORS[0]] for r in ok],
                                         [r[VENDORS[1]] for r in ok])
    for s in ("A_rejected", "B_bounds_fixed_confirmed", "C_random_confirmed"):
        sub = [r for r in ok if r["stratum"] == s]
        if sub:
            res["per_stratum_agreement"][s] = {
                v: round(sum(r[v] == r["frozen"] for r in sub) / len(sub), 4)
                for v in VENDORS}
    dst = ROOT / "data/results/review_shadow_kappa_v7.json"
    dst.write_text(json.dumps(res, indent=2, ensure_ascii=False))
    print(json.dumps({k: res[k] for k in
                      ("n_scored", "kappa_vs_frozen", "kappa_between_shadows",
                       "per_stratum_agreement")}, indent=1))
    print("wrote", dst)


if __name__ == "__main__":
    main()
