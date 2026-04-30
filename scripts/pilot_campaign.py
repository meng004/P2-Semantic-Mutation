"""End-to-end pilot: A2_MP1 and B2_MP2 with hand-crafted mutants.

Validates the full pipeline: PUT → mutant → equiv → AVP → SMS.
Saves results to data/results/pilot_results.json.
"""
import json
import importlib.util
import sys
from pathlib import Path
from typing import List

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "src"))

from p2.avp.interface import MR
from p2.equiv.sampler import UniformSampler
from p2.pipeline.run_cell import run_one_cell
import p2.mrs.a2 as mrs_a2
import p2.mrs.b2 as mrs_b2
import p2.puts.a2 as put_a2
import p2.puts.b2 as put_b2


def load_mutants_from_dir(cell_dir: Path) -> List:
    mutants = []
    for py_file in sorted(cell_dir.glob("*.py")):
        spec = importlib.util.spec_from_file_location(f"_mut_{py_file.stem}", py_file)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mutants.append((py_file.name, mod.program))
    return mutants


def run_pilot_cell(cell_id, put_fn, mr_list, mutant_dir, sampler):
    named_mutants = load_mutants_from_dir(mutant_dir)
    mutant_fns = [fn for _, fn in named_mutants]
    mutant_names = [name for name, _ in named_mutants]

    result = run_one_cell(
        put=put_fn,
        mutants=mutant_fns,
        mr_set=mr_list,
        cell_id=cell_id,
        sampler=sampler,
        k_eq=1000,
        epsilon_eq=1e-6,
        epsilon_avp=1e-6,
    )

    # annotate each mutant's outcome
    outcomes = []
    for idx, name in enumerate(mutant_names):
        if idx in result.equiv_indices:
            label = "EQUIV"
        elif idx in result.killed_indices:
            label = "KILLED"
        else:
            label = "SURVIVE"
        outcomes.append({"file": name, "label": label})

    return result, outcomes


def main():
    sampler = UniformSampler(low=0.0, high=1.0, dim=1, seed=42)

    cells = [
        {
            "cell_id": "A2_MP1",
            "put": put_a2.program,
            "mr_set": [MR(r=mrs_a2.r_mp1, R=mrs_a2.R_mp1, mp_index=1, name="A2_mp1")],
            "mutant_dir": ROOT / "data/mutants/a2_MP1_mut1",
        },
        {
            "cell_id": "B2_MP2",
            "put": put_b2.program,
            "mr_set": [MR(r=mrs_b2.r_mp2, R=mrs_b2.R_mp2, mp_index=2, name="B2_mp2")],
            "mutant_dir": ROOT / "data/mutants/b2_MP2_mut1",
        },
    ]

    all_results = {}
    print(f"\n{'='*60}")
    print("P2 PILOT CAMPAIGN — hand-crafted mutants")
    print(f"{'='*60}\n")

    for cfg in cells:
        result, outcomes = run_pilot_cell(
            cfg["cell_id"], cfg["put"], cfg["mr_set"],
            cfg["mutant_dir"], sampler,
        )
        summary = {
            "inst": result.inst_count,
            "equiv": result.equiv_count,
            "killed": result.killed_count,
            "survive": result.survive_count,
            "sms": round(result.sms, 4),
            "outcomes": outcomes,
        }
        all_results[cfg["cell_id"]] = summary

        print(f"Cell: {cfg['cell_id']}")
        print(f"  inst={result.inst_count}  equiv={result.equiv_count}  "
              f"killed={result.killed_count}  survive={result.survive_count}  "
              f"SMS={result.sms:.4f}")
        for o in outcomes:
            print(f"    {o['label']:8s}  {o['file']}")
        print()

    out_path = ROOT / "data/results/pilot_results.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(all_results, indent=2))
    print(f"Results saved → {out_path}")


if __name__ == "__main__":
    main()
