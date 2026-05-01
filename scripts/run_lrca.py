"""Apply LRCA dispatcher to every (mutant, MR) pair in Track-2 v2;
produce per-cell C1_share + suspect_share for the §5.4 LRCA section.

Reads:
  - data/results/sms_track2_v2.json (per-cell mutant outcomes)
  - data/mutants/<put>_pool/*.py    (mutant source files)
  - src/p2/puts/<put>.py            (original PUTs)
  - src/p2/mrs/<put>.py             (MR set per PUT)

Writes:
  - data/results/lrca_60cell.json   (per-cell label histogram + shares)

Run from project root:
  PYTHONPATH=src python scripts/run_lrca.py
"""
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "src"))

from p2.avp.interface import MR  # noqa: E402
from p2.lrca.dispatcher import LRCALabel, classify_mutant  # noqa: E402

# Primary MP per PUT — used to fall back to <put>_MP<k>_llm dirs when
# no per-PUT pool directory exists (Round 2 builders preceded Round 4).
PRIMARY = {
    "a1": 1, "a2": 1, "a3": 1,
    "b1": 2, "b2": 2, "b3": 2,
    "c1": 5, "c2": 5, "c3": 5,
    "d1": 2, "d2": 2, "d3": 2,
}

# Narrow exception class per project pattern (mirrors p2.avp.repeat).
_MUTANT_EXC = (ValueError, ArithmeticError, TypeError, RuntimeError, ImportError, SyntaxError)


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main() -> None:
    import os
    version = os.environ.get("LRCA_VERSION", "v3")
    sms_file = "sms_track2_v3.json" if version == "v3" else "sms_track2_v2.json"
    out_name = "lrca_60cell_v3.json" if version == "v3" else "lrca_60cell.json"
    print(f"LRCA version={version} reading {sms_file} writing {out_name}")
    sms = json.loads((ROOT / "data/results" / sms_file).read_text())
    report: dict = {}
    for cell, v in sms.items():
        put_id = cell.split("_")[0].lower()
        mp_k = int(cell.split("MP")[1])
        pool_v3 = ROOT / f"data/mutants/{put_id}_pool_v3"
        pool_v2 = ROOT / f"data/mutants/{put_id}_pool"
        if version == "v3" and pool_v3.exists():
            pool_dir = pool_v3
        elif pool_v2.exists():
            pool_dir = pool_v2
        else:
            pool_dir = ROOT / f"data/mutants/{put_id}_MP{PRIMARY[put_id]}_llm"
        put_mod = _load(f"put_{put_id}", ROOT / f"src/p2/puts/{put_id}.py")
        mrs_mod = _load(f"mrs_{put_id}", ROOT / f"src/p2/mrs/{put_id}.py")
        mr = MR(
            r=getattr(mrs_mod, f"r_mp{mp_k}"),
            R=getattr(mrs_mod, f"R_mp{mp_k}"),
            mp_index=mp_k,
            name=cell,
        )
        killed_files = {
            o["file"] for o in v.get("outcomes", []) if o["label"] == "KILLED"
        }
        labels = {label.value: 0 for label in LRCALabel}
        per_mut = []
        for o in v.get("outcomes", []):
            fp = pool_dir / o["file"]
            if not fp.exists():
                continue
            try:
                mut_mod = _load(f"mut_{cell}_{fp.stem}", fp)
            except _MUTANT_EXC:
                labels[LRCALabel.ARTIFACT.value] += 1
                per_mut.append({
                    "file": o["file"],
                    "outcome": o["label"],
                    "lrca": LRCALabel.ARTIFACT.value,
                })
                continue
            was_killed = o["file"] in killed_files
            label = classify_mutant(
                mut_mod.program, put_mod.program, mr, was_killed,
            )
            labels[label.value] += 1
            per_mut.append({
                "file": o["file"],
                "outcome": o["label"],
                "lrca": label.value,
            })
        n_killed = (
            labels[LRCALabel.C1_LEGIT.value]
            + labels[LRCALabel.C2_TOLERANCE.value]
            + labels[LRCALabel.C3_OOD.value]
            + labels[LRCALabel.C4_STATISTICAL.value]
        )
        c1_share = labels[LRCALabel.C1_LEGIT.value] / n_killed if n_killed else 0.0
        suspect_share = 1.0 - c1_share
        report[cell] = {
            "labels": labels,
            "per_mutant": per_mut,
            "n_killed": n_killed,
            "c1_share": round(c1_share, 4),
            "suspect_share": round(suspect_share, 4),
        }
        print(
            f"  {cell}: killed={n_killed} "
            f"C1={labels[LRCALabel.C1_LEGIT.value]} "
            f"C2={labels[LRCALabel.C2_TOLERANCE.value]} "
            f"C3={labels[LRCALabel.C3_OOD.value]} "
            f"C4={labels[LRCALabel.C4_STATISTICAL.value]} "
            f"L0={labels[LRCALabel.ARTIFACT.value]} "
            f"surv={labels[LRCALabel.SURVIVED.value]} "
            f"c1_share={report[cell]['c1_share']}",
            flush=True,
        )

    out_path = ROOT / "data/results" / out_name
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False))
    print(f"\nCells processed: {len(report)}")
    if report:
        mean_suspect = sum(r["suspect_share"] for r in report.values()) / len(report)
        print(f"Mean suspect_share: {mean_suspect:.3f}")
        totals = {label.value: 0 for label in LRCALabel}
        for r in report.values():
            for k, n in r["labels"].items():
                totals[k] += n
        print("Total LRCA counts across 60 cells:")
        for k, n in totals.items():
            print(f"  {k}: {n}")


if __name__ == "__main__":
    main()
