#!/usr/bin/env python3
"""EXP-DOSE kill runner (PASS-2).

Instantiates 960 dose mutants (6×20×8), judges kill against each curve's ALIGNED
MR set using the same predicate + repeats convention as scripts/sms_campaign.py:

  kill ⇔ ∃ mr ∈ MR_set: AVP(orig, mr)=PASS ∧ AVP(mut, mr)=FAIL
  (via p2.lrca.killed.is_killed; epsilon_avp=1e-6)
  repeats: 20 for stochastic PUT b3; 1 for deterministic a1/c1/d3

Amendment #2 (pre-unblinding): window_halfwidth carries
  r_c = max(delta_r + 2*eta_bar, eps_tol*(sqrt(g)-1))
  g = (4/0.25)^(1/5) ≈ 1.7411  →  resolution_floor ≈ 0.3195·eps_tol
Raw components retained as raw_delta_r, raw_eta_bar, resolution_floor.

Errored executions: not a kill; counted in execution_errors; at most one
deterministic re-run, then give up.

Writes data/dose/dose_response_v5.json conforming to analysis_hdose.py schema.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import sys
import time
import traceback
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
STOCHASTIC_PUTS = {"b3"}

# Amendment #2 grid half-step floor
G_GRID = (4.0 / 0.25) ** (1.0 / 5.0)  # ≈ 1.741101
SQRT_G_MINUS_1 = math.sqrt(G_GRID) - 1.0  # ≈ 0.319508


def effective_radius(eps_tol: float, delta_r: float, eta_bar: float) -> tuple[float, float]:
    """Return (r_c, resolution_floor) per Amendment #2."""
    theory = float(delta_r) + 2.0 * float(eta_bar)
    floor = float(eps_tol) * SQRT_G_MINUS_1
    return max(theory, floor), floor


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _load_fn_from_source(name: str, source: str):
    MUT_DIR.mkdir(parents=True, exist_ok=True)
    path = MUT_DIR / f"{name}.py"
    path.write_text(source)
    # bust import cache if re-loading same name (shouldn't happen with unique IDs)
    if name in sys.modules:
        del sys.modules[name]
    return _load_module(name, path).program


def _build_aligned_mr(put: str, mp_k: int) -> MR:
    mrs_mod = _load_module(f"mrs_{put}", MRS_DIR / f"{put}.py")
    return MR(
        r=getattr(mrs_mod, f"r_mp{mp_k}"),
        R=getattr(mrs_mod, f"R_mp{mp_k}"),
        mp_index=mp_k,
        name=f"{put.upper()}_mp{mp_k}",
    )


def _judge_one(orig_fn, mut_fn, mr, epsilon, repeats) -> bool:
    return is_killed(orig_fn, mut_fn, [mr], epsilon, repeats=repeats)


def run_curve(
    op: str,
    put: str,
    nominals: list[float],
    eps_tol: float,
    delta_r: float,
    eta_bar: float,
) -> dict:
    cid = curve_id(op, put)
    mp = ALIGNED_MP[op]
    orig_fn = _load_module(f"put_{put}", PUTS_DIR / f"{put}.py").program
    mr = _build_aligned_mr(put, mp)
    repeats = 20 if put in STOCHASTIC_PUTS else 1
    r_c, res_floor = effective_radius(eps_tol, delta_r, eta_bar)

    kills: list[int] = []
    errors = 0
    t0 = time.time()
    for level in range(1, N_LEVELS + 1):
        amp = nominals[level - 1]
        n_killed = 0
        for rep in range(1, N_REPEATS + 1):
            mid, src, _seed = emit_instance(op, put, level, rep, amp)
            ok = False
            killed = False
            last_err = None
            for attempt in (1, 2):  # one deterministic re-run max
                try:
                    mut_fn = _load_fn_from_source(mid if attempt == 1 else f"{mid}_retry", src)
                    killed = _judge_one(orig_fn, mut_fn, mr, EPSILON_AVP, repeats)
                    ok = True
                    break
                except Exception as e:
                    last_err = e
                    continue
            if not ok:
                errors += 1
                print(
                    f"  ERROR {mid}: {type(last_err).__name__}: {last_err} "
                    f"(counted as non-kill)",
                    flush=True,
                )
            elif killed:
                n_killed += 1
        kills.append(int(n_killed))
        print(
            f"  {cid} e{level}: killed {n_killed}/{N_REPEATS} "
            f"(cum_errors={errors})",
            flush=True,
        )
    elapsed = time.time() - t0
    return {
        "curve_id": cid,
        "eps_realized": None,  # filled by caller from F-10 calibration
        "kills": kills,
        "reps": N_REPEATS,
        "eps_tol": float(eps_tol),
        "window_halfwidth": float(r_c),  # Amendment #2: carries r_c
        "raw_delta_r": float(delta_r),
        "raw_eta_bar": float(eta_bar),
        "resolution_floor": float(res_floor),
        "raw_theory_window": float(delta_r) + 2.0 * float(eta_bar),
        "execution_errors": int(errors),
        "runtime_s": round(elapsed, 2),
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

    t_all = time.time()
    curves = []
    for op in OPS:
        for put in PUTS:
            cid = curve_id(op, put)
            if args.curve and cid != args.curve:
                continue
            g, w = grid[cid], win[cid]
            r_c, floor = effective_radius(w["eps_tol"], w["delta_r"], w["eta_bar"])
            print(
                f"== dose kill {cid} == "
                f"eps_tol={w['eps_tol']} r_c={r_c:.6g} "
                f"(theory={w['window_halfwidth']:.6g}, floor={floor:.6g})",
                flush=True,
            )
            row = run_curve(
                op, put,
                nominals=g["nominal_amplitudes"],
                eps_tol=w["eps_tol"],
                delta_r=w["delta_r"],
                eta_bar=w["eta_bar"],
            )
            # F-10 axis = calibration realized means (direct functionals; not MR checkers)
            row["eps_realized"] = list(g["eps_realized_mean"])
            curves.append(row)

    total_errors = sum(c["execution_errors"] for c in curves)
    doc = {
        "schema": "dose_response_v5 / analysis_hdose input",
        "amendment": (
            "Amendment #2: window_halfwidth = r_c = max(delta_r+2*eta_bar, "
            f"eps_tol*(sqrt(g)-1)) with g=(4/0.25)^(1/5)≈{G_GRID:.6f}; "
            f"sqrt(g)-1≈{SQRT_G_MINUS_1:.6f}"
        ),
        "n_curves": len(curves),
        "n_executions": sum(len(c["kills"]) * c["reps"] for c in curves),
        "n_execution_errors": total_errors,
        "runtime_s_total": round(time.time() - t_all, 2),
        "kill_predicate": (
            "is_killed: exists mr in aligned MR set with AVP(orig)=PASS and "
            "AVP(mut)=FAIL; epsilon_avp=1e-6; repeats=20 for b3 else 1 "
            "(sms_campaign convention); errored run = non-kill after ≤1 re-run"
        ),
        "curves": curves,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(doc, indent=2))
    print(
        f"Wrote {args.out} ({doc['n_executions']} executions, "
        f"{total_errors} errors, {doc['runtime_s_total']}s)",
        flush=True,
    )


if __name__ == "__main__":
    main()
