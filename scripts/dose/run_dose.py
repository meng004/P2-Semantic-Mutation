#!/usr/bin/env python3
"""EXP-DOSE kill runner (PASS-2 — do NOT execute until WINDOWS_FROZEN.json is committed).

Instantiates 960 dose mutants (6×20×8), judges kill against each curve's ALIGNED
MR set using the same predicate + repeats convention as scripts/sms_campaign.py:

  kill ⇔ ∃ mr ∈ MR_set: AVP(orig, mr)=PASS ∧ AVP(mut, mr)=FAIL
  (via p2.lrca.killed.is_killed; epsilon_avp=1e-6)
  repeats: 20 for stochastic PUT b3; 1 for deterministic a1/c1/d3
           (sms_campaign docstring: "Use 20 for stochastic PUTs")

Writes data/dose/dose_response_v5.json conforming to analysis_hdose.py schema:
  {"curves": [{"curve_id", "eps_realized", "kills", "reps", "eps_tol",
               "window_halfwidth"}]}

Prerequisites:
  data/dose/WINDOWS_FROZEN.json   (PASS-1 freeze)
  data/dose/nominal_grid.json     (PASS-1 calibration)
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import tempfile
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts" / "dose"))

from p2.avp.interface import MR  # noqa: E402
from p2.lrca.killed import is_killed  # noqa: E402

from dose_operators import (  # noqa: E402
    ALIGNED_MP,
    N_LEVELS,
    N_REPEATS,
    OPS,
    PUTS,
    curve_id,
    emit_instance,
)

OUT = ROOT / "data" / "dose" / "dose_response_v5.json"
WINDOWS = ROOT / "data" / "dose" / "WINDOWS_FROZEN.json"
GRID = ROOT / "data" / "dose" / "nominal_grid.json"
PUTS_DIR = ROOT / "src" / "p2" / "puts"
MRS_DIR = ROOT / "src" / "p2" / "mrs"
MUT_DIR = ROOT / "data" / "dose" / "mutants"

EPSILON_AVP = 1e-6

# Match sms_campaign convention: 20 AVP majority-vote repeats for stochastic PUTs
STOCHASTIC_PUTS = {"b3"}


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _load_fn_from_source(name: str, source: str):
    MUT_DIR.mkdir(parents=True, exist_ok=True)
    path = MUT_DIR / f"{name}.py"
    path.write_text(source)
    return _load_module(name, path).program


def _build_aligned_mr(put: str, mp_k: int) -> MR:
    mrs_mod = _load_module(f"mrs_{put}", MRS_DIR / f"{put}.py")
    return MR(
        r=getattr(mrs_mod, f"r_mp{mp_k}"),
        R=getattr(mrs_mod, f"R_mp{mp_k}"),
        mp_index=mp_k,
        name=f"{put.upper()}_mp{mp_k}",
    )


def run_curve(op: str, put: str, nominals: list[float], eps_tol: float,
              window_halfwidth: float, write_sources: bool = True) -> dict:
    cid = curve_id(op, put)
    mp = ALIGNED_MP[op]
    orig_fn = _load_module(f"put_{put}", PUTS_DIR / f"{put}.py").program
    mr = _build_aligned_mr(put, mp)
    repeats = 20 if put in STOCHASTIC_PUTS else 1

    # Per-level mean realized eps is taken from calibration ledger (F-10);
    # re-read from nominal_grid.json so kill run does not re-enter MR checkers
    # for the dose axis.
    kills = []
    for level in range(1, N_LEVELS + 1):
        amp = nominals[level - 1]
        n_killed = 0
        for rep in range(1, N_REPEATS + 1):
            mid, src, _seed = emit_instance(op, put, level, rep, amp)
            mut_fn = _load_fn_from_source(mid, src) if write_sources else None
            if mut_fn is None:
                # in-memory path (unused in default)
                with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
                    f.write(src)
                    p = Path(f.name)
                mut_fn = _load_module(mid, p).program
                p.unlink(missing_ok=True)
            if is_killed(orig_fn, mut_fn, [mr], EPSILON_AVP, repeats=repeats):
                n_killed += 1
        kills.append(int(n_killed))
        print(f"  {cid} e{level}: killed {n_killed}/{N_REPEATS}", flush=True)

    return {
        "curve_id": cid,
        "eps_realized": None,  # filled by caller from calibration
        "kills": kills,
        "reps": N_REPEATS,
        "eps_tol": eps_tol,
        "window_halfwidth": window_halfwidth,
        "aligned_mp": mp,
        "avp_repeats": repeats,
        "epsilon_avp": EPSILON_AVP,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--curve", default=None, help="optional single curve_id e.g. CE-A1")
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()

    if not WINDOWS.exists():
        sys.exit(f"FATAL: {WINDOWS} missing — freeze windows in PASS-1 first")
    if not GRID.exists():
        sys.exit(f"FATAL: {GRID} missing — run calibrate_eps.py first")

    win = {c["curve_id"]: c for c in json.loads(WINDOWS.read_text())["curves"]}
    grid = {c["curve_id"]: c for c in json.loads(GRID.read_text())["curves"]}

    curves = []
    for op in OPS:
        for put in PUTS:
            cid = curve_id(op, put)
            if args.curve and cid != args.curve:
                continue
            print(f"== dose kill {cid} ==", flush=True)
            g, w = grid[cid], win[cid]
            row = run_curve(
                op, put,
                nominals=g["nominal_amplitudes"],
                eps_tol=w["eps_tol"],
                window_halfwidth=w["window_halfwidth"],
            )
            # F-10 axis = calibration realized means (per-level, 20-instance mean)
            row["eps_realized"] = list(g["eps_realized_mean"])
            curves.append(row)

    doc = {
        "schema": "dose_response_v5 / analysis_hdose input",
        "n_curves": len(curves),
        "n_executions": sum(len(c["kills"]) * c["reps"] for c in curves),
        "kill_predicate": (
            "is_killed: exists mr in aligned MR set with AVP(orig)=PASS and "
            "AVP(mut)=FAIL; epsilon_avp=1e-6; repeats=20 for b3 else 1 "
            "(sms_campaign convention)"
        ),
        "curves": curves,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(doc, indent=2))
    print(f"Wrote {args.out} ({doc['n_executions']} executions)", flush=True)


if __name__ == "__main__":
    main()
