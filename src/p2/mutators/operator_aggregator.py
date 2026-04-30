"""Compute R_sem / D_impl / R_kill per operator from raw campaign JSON."""
import importlib
import importlib.util
import json
from pathlib import Path
from typing import Dict, List

from p2.mutators.diversity import diversity_score
from p2.mutators.operator_registry import OPERATORS


def compute_r_sem(trials: List[dict]) -> float:
    if not trials:
        return 0.0
    good = sum(1 for t in trials
               if (t.get("is_confirmed") if "is_confirmed" in t
                   else t.get("overall") == "CONFIRMED")
               and t.get("operator_match") == "Yes")
    return good / len(trials)


def compute_d_impl(codes: List[str]) -> float:
    return diversity_score(codes)


def _import_program_from_source(code: str, idx: int = 0):
    """Exec code string and return its `program` callable, or None on error."""
    mod_name = f"_mut_inline_{idx}"
    spec = importlib.util.spec_from_loader(mod_name, loader=None)
    mod = importlib.util.module_from_spec(spec)
    try:
        exec(code, mod.__dict__)
        return mod.__dict__.get("program")
    except Exception:
        return None


def _r_kill_for_operator(op_id: str, codes: List[str]) -> float:
    """Run AVP on each confirmed mutant against its PUT's primary MR; report kill rate."""
    if not codes:
        return 0.0
    op = next((o for o in OPERATORS if o.id == op_id), None)
    if op is None:
        return 0.0
    put_id = op.put

    from p2.avp.dispatcher import call_avp
    from p2.avp.interface import MR, AVPResult

    # Actual primary MPs from mrs/*.py docstrings (may differ from task-spec mapping)
    PRIMARY_MP = {"a1": 1, "a2": 1, "a3": 3, "b1": 2, "b2": 2, "b3": 1,
                  "c1": 5, "c2": 5, "c3": 5, "d1": 2, "d2": 2, "d3": 2}
    MP_TO_RR = {1: ("r_mp1", "R_mp1"), 2: ("r_mp2", "R_mp2"),
                3: ("r_mp3", "R_mp3"), 4: ("r_mp4", "R_mp4"), 5: ("r_mp5", "R_mp5")}

    mp_k = PRIMARY_MP[put_id]
    r_name, R_name = MP_TO_RR[mp_k]
    mr_mod = importlib.import_module(f"p2.mrs.{put_id}")
    put_mod = importlib.import_module(f"p2.puts.{put_id}")
    mr = MR(r=getattr(mr_mod, r_name), R=getattr(mr_mod, R_name),
            mp_index=mp_k, name=f"{put_id}_mp{mp_k}")

    try:
        orig_result = call_avp(put_mod.program, mr, epsilon=1e-6)
        orig_pass = (orig_result == AVPResult.PASS)
    except Exception:
        return 0.0
    if not orig_pass:
        return 0.0

    killed = 0
    valid = 0
    for idx, code in enumerate(codes):
        prog = _import_program_from_source(code, idx)
        if prog is None:
            continue
        try:
            r = call_avp(prog, mr, epsilon=1e-6)
            valid += 1
            if r == AVPResult.FAIL:
                killed += 1
        except Exception:
            continue
    return killed / valid if valid else 0.0


def aggregate_operator_metrics(
    raw_dir: Path, out_path: Path, run_avp: bool = True,
) -> Dict[str, dict]:
    metrics: Dict[str, dict] = {}
    for fp in sorted(Path(raw_dir).glob("*.json")):
        op_id = fp.stem
        trials = json.loads(fp.read_text())
        # normalise is_confirmed flag for robustness
        for t in trials:
            t["is_confirmed"] = t.get("overall") == "CONFIRMED"

        confirmed_codes = [t["code"] for t in trials
                           if t["is_confirmed"] and t.get("operator_match") == "Yes"]

        m = {
            "op_id": op_id,
            "K": len(trials),
            "n_confirmed": len(confirmed_codes),
            "r_sem": round(compute_r_sem(trials), 4),
            "d_impl": round(compute_d_impl(confirmed_codes), 4),
        }
        if run_avp and confirmed_codes:
            m["r_kill"] = round(_r_kill_for_operator(op_id, confirmed_codes), 4)
        else:
            m["r_kill"] = None
        metrics[op_id] = m

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    Path(out_path).write_text(json.dumps(metrics, indent=2, ensure_ascii=False))
    return metrics
