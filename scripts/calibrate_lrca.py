"""Sweep LRCA thresholds to find best H5 pass ratio.

Grid sizing controlled by env LRCA_GRID:
  "9"  (default, fast) — 3×3 grid:
       ood_band ∈ {0.02, 0.05, 0.10}
       tolerance_multiplier ∈ {3.0, 10.0, 30.0}
  "49" (R-14 dense, ~5–6× wall time) — 7×7 grid:
       ood_band ∈ {0.01, 0.02, 0.04, 0.07, 0.10, 0.15, 0.20}
       tolerance_multiplier ∈ {1.0, 3.0, 5.0, 10.0, 20.0, 30.0, 50.0}

statistical_repeats fixed at 20 (§3.4 paper baseline).

Data version controlled by SMS_VERSION (default v3 to preserve historical
output filename; set SMS_VERSION=v4 to use the cross-source primary data).

For each combo, recompute LRCA label per (cell, mutant), report
mean_C1_share, mean_suspect_share, h5_cells_pass.

Output: data/results/lrca_calibration{_v4 if SMS_VERSION=v4 else ""}.json
        (filename suffix mirrors the data version)
"""
import importlib.util
import itertools
import json
import os
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "src"))

from p2.avp.interface import MR
from p2.lrca.dispatcher import classify_mutant, LRCALabel
H5_THRESHOLD = 0.20


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


VERSION = os.environ.get("SMS_VERSION", "v3")
GRID_SIZE = os.environ.get("LRCA_GRID", "9")
SMS_FILE = f"sms_track2_{VERSION}.json" if VERSION != "v2" else "sms_track2_v2.json"
OUT_FILE = (
    f"lrca_calibration_{VERSION}.json"
    if VERSION not in ("v2", "v3")
    else "lrca_calibration.json"
)
print(
    f"calibrate_lrca: SMS_VERSION={VERSION} GRID={GRID_SIZE} "
    f"reading {SMS_FILE} writing {OUT_FILE}"
)


def _classify_60_cells(ood_band, tol_mult, repeats):
    sms = json.loads((ROOT / "data/results" / SMS_FILE).read_text())
    suspect_shares = []
    for cell, v in sms.items():
        put_id = cell.split("_")[0].lower()
        mp_k = int(cell.split("MP")[1])
        pool_candidates = [
            ROOT / f"data/mutants/{put_id}_pool_{VERSION}",
            ROOT / f"data/mutants/{put_id}_pool_v3",
            ROOT / f"data/mutants/{put_id}_pool",
        ]
        pool_dir = next((p for p in pool_candidates if p.exists()), pool_candidates[-1])
        try:
            put_mod = _load(f"put_{put_id}", ROOT / f"src/p2/puts/{put_id}.py")
            mrs_mod = _load(f"mrs_{put_id}", ROOT / f"src/p2/mrs/{put_id}.py")
        except Exception as exc:
            print(f"  load fail {put_id}: {exc}")
            suspect_shares.append(1.0)
            continue
        mr = MR(r=getattr(mrs_mod, f"r_mp{mp_k}"),
                R=getattr(mrs_mod, f"R_mp{mp_k}"),
                mp_index=mp_k, name=cell)
        killed_files = {o["file"] for o in v.get("outcomes", []) if o["label"] == "KILLED"}
        labels = {l.value: 0 for l in LRCALabel}
        for o in v.get("outcomes", []):
            fp = pool_dir / o["file"]
            if not fp.exists():
                continue
            try:
                mut_mod = _load(f"_m_{cell}_{fp.stem}", fp)
            except Exception:
                labels[LRCALabel.ARTIFACT.value] += 1
                continue
            was_killed = o["file"] in killed_files
            try:
                label = classify_mutant(
                    mut_mod.program, put_mod.program, mr, was_killed,
                    ood_band=ood_band,
                    tolerance_multiplier=tol_mult,
                    statistical_repeats=repeats,
                )
                labels[label.value] += 1
            except Exception as exc:
                labels[LRCALabel.ARTIFACT.value] += 1
        n_killed = (labels[LRCALabel.C1_LEGIT.value]
                    + labels[LRCALabel.C2_TOLERANCE.value]
                    + labels[LRCALabel.C3_OOD.value]
                    + labels[LRCALabel.C4_STATISTICAL.value])
        c1_share = labels[LRCALabel.C1_LEGIT.value] / n_killed if n_killed else 0.0
        suspect_shares.append(1.0 - c1_share)
    return suspect_shares


def main():
    if GRID_SIZE == "49":
        grid = list(itertools.product(
            [0.01, 0.02, 0.04, 0.07, 0.10, 0.15, 0.20],
            [1.0, 3.0, 5.0, 10.0, 20.0, 30.0, 50.0],
        ))
    else:
        grid = list(itertools.product(
            [0.02, 0.05, 0.10],
            [3.0, 10.0, 30.0],
        ))
    repeats = 20
    report = []
    for ob, tm in grid:
        print(f"\n--- ob={ob} tm={tm} rep={repeats} ---")
        suspects = _classify_60_cells(ob, tm, repeats)
        mean_suspect = sum(suspects) / len(suspects) if suspects else 1.0
        mean_c1 = 1 - mean_suspect
        h5_pass = sum(1 for s in suspects if s <= H5_THRESHOLD)
        report.append({
            "ood_band": ob,
            "tolerance_multiplier": tm,
            "statistical_repeats": repeats,
            "mean_c1_share": round(mean_c1, 4),
            "mean_suspect_share": round(mean_suspect, 4),
            "h5_cells_pass": h5_pass,
            "h5_pass_ratio": round(h5_pass / 60, 4),
        })
        print(f"  c1_share={mean_c1:.3f} h5_pass={h5_pass}/60")

    report.sort(key=lambda r: (-r["h5_cells_pass"], -r["mean_c1_share"]))
    out = {
        "grid_size": len(grid),
        "best": report[0],
        "all": report,
        "h5_threshold_suspect": H5_THRESHOLD,
        "h5_threshold_pass_ratio": 0.80,
    }
    (ROOT / "data/results" / OUT_FILE).write_text(
        json.dumps(out, indent=2, ensure_ascii=False))
    print("\n=== BEST ===")
    print(json.dumps(report[0], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
