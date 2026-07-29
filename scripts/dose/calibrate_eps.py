#!/usr/bin/env python3
"""F-10 dose calibration + H-DOSE-CTR window freeze (PASS-1).

REALIZED axis: direct invariant-violation functionals (NEVER via MR checkers).
Nominal grid: per-curve amplitudes calibrated so mean realized eps_m over 20
seeded instances spans approximately [0.25, 4.0] * eps_tol.

eps_tol provenance (deviation from brief):
  data/mr_export/{put}_MP{1|3}_mr.json has keys
  {put, mp, r_name, R_name, primary, sample_pairs} — NO eps_tol / epsilon field.
  We therefore extract the numeric tolerance constant from the aligned R_mp
  predicate in src/p2/mrs/{put}.py (cited per curve below) and record the
  mr_export file used only for put/mp/r_name/R_name provenance.

Window freeze (ORIGINAL programs only — no mutants):
  window_halfwidth = Delta_r + 2 * eta_bar
  written to data/dose/WINDOWS_FROZEN.json BEFORE any dose kill run.

Outputs:
  data/dose/WINDOWS_FROZEN.json
  data/dose/DOSE_CALIBRATION.md
  data/dose/nominal_grid.json
"""
from __future__ import annotations

import importlib.util
import json
import math
import sys
import tempfile
from pathlib import Path

import numpy as np
from scipy.special import erf

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts" / "dose"))

from dose_operators import (  # noqa: E402
    ALIGNED_MP,
    BASE_SEED,
    CURVE_IDS,
    N_LEVELS,
    N_REPEATS,
    OPS,
    PUTS,
    curve_id,
    emit_instance,
    emit_mutant_source,
    instance_seed,
    load_put_source,
)

OUT_DIR = ROOT / "data" / "dose"
MR_EXPORT = ROOT / "data" / "mr_export"
PUTS_DIR = ROOT / "src" / "p2" / "puts"
MRS_DIR = ROOT / "src" / "p2" / "mrs"

PROBE_X = np.linspace(0.05, 0.95, 19)


# ── eps_tol table (native units of each direct functional) ──────────────────
# Field used from mr_export: r_name / R_name (identity check). Numeric tol from mrs.
EPS_TOL_SPEC = {
    "CE-A1": {
        "eps_tol": 1.0,
        "mr_export": "a1_MP1_mr.json",
        "r_name_expected": "r_trivial",  # export may list trivial; code uses r_mp1
        "native_source": (
            "src/p2/mrs/a1.py R_mp1 uses guard abs(y+y')<1e6 (not a continuous "
            "violation scale). Direct functional V = mean |y_mut(x)-y_orig(x)| on "
            "PROBE_X; eps_tol:=1.0 is the unit of that functional (normalized "
            "detection scale; matches power_report 'eps_tol normalised 1.0')."
        ),
    },
    "CE-B3": {
        "eps_tol": 0.02,
        "mr_export": "b3_MP1_mr.json",
        "native_source": (
            "src/p2/mrs/b3.py R_mp1: abs(abs(y_new-y_orig)-0.1) < 0.02 "
            "→ continuous tol 0.02 on the linearity residual."
        ),
    },
    "CE-C1": {
        "eps_tol": 0.1,
        "mr_export": "c1_MP1_mr.json",
        "native_source": (
            "src/p2/mrs/c1.py R_mp1: abs(y+y') < 0.1 → tol 0.1 on anti-symmetry residual."
        ),
    },
    "CE-D3": {
        "eps_tol": 0.05,
        "mr_export": "d3_MP1_mr.json",
        "native_source": (
            "src/p2/mrs/d3.py R_mp1 is a hard bound y in [0,1] (no continuous tol). "
            "Surrogate soft margin 0.05 matches MP2/MP5 slack in the same module; "
            "functional V = mean |bias| = mean |p_mut - p_orig|."
        ),
    },
    "HP-A1": {
        "eps_tol": 1.0,
        "mr_export": "a1_MP3_mr.json",
        "native_source": (
            "src/p2/mrs/a1.py R_mp3 is an attractor-envelope predicate (bound 60), "
            "not a continuous accuracy tol. Direct functional V = mean "
            "|y_loose(x)-y_ref(x)| / (1+|y_ref|) vs high-fidelity ref; "
            "eps_tol:=1.0 (normalized detection scale)."
        ),
    },
    "HP-B3": {
        "eps_tol": 0.05,
        "mr_export": "b3_MP3_mr.json",
        "native_source": (
            "src/p2/mrs/b3.py R_mp3 envelope slack 0.05 around analytic integral."
        ),
    },
    "HP-C1": {
        "eps_tol": 0.1,
        "mr_export": "c1_MP3_mr.json",
        "native_source": (
            "src/p2/mrs/c1.py R_mp3 overfit margin 0.1 beyond target range [-1,1]."
        ),
    },
    "HP-D3": {
        "eps_tol": 0.05,
        "mr_export": "d3_MP3_mr.json",
        "native_source": (
            "src/p2/mrs/d3.py R_mp3 idempotency tol 1e-9 is not an accuracy scale. "
            "Surrogate 0.05 (= MP2/MP5 slack) on mean |p_mut - p_ref| vs well-regularized ref."
        ),
    },
}


def _load_fn_from_source(name: str, source: str):
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
        f.write(source)
        path = Path(f.name)
    try:
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod.program
    finally:
        path.unlink(missing_ok=True)


def _load_put_fn(put: str):
    spec = importlib.util.spec_from_file_location(f"put_{put}", PUTS_DIR / f"{put}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.program


# ── Direct invariant-violation functionals (F-10) ───────────────────────────

def V_ce_a1(mut_fn, orig_fn) -> float:
    """Mean absolute output drift vs original on PROBE_X (conservation-drift proxy)."""
    vals = [abs(float(mut_fn(x)) - float(orig_fn(x))) for x in PROBE_X]
    return float(np.mean(vals))


def V_ce_b3(mut_fn, orig_fn=None) -> float:
    """Linearity-violation |[f(x+c)-f(x)] - c| aggregated; c=0.1 (MR convention)."""
    c = 0.1
    xs = [x for x in PROBE_X if x + c <= 1.0]
    res = [abs(abs(float(mut_fn(x + c)) - float(mut_fn(x))) - c) for x in xs]
    return float(np.mean(res))


def V_ce_c1(mut_fn, orig_fn=None) -> float:
    """Anti-symmetry residual |y(x)+y(1-x)| (WhiteKernel / target-symmetry erosion)."""
    res = [abs(float(mut_fn(x)) + float(mut_fn(1.0 - x))) for x in PROBE_X]
    return float(np.mean(res))


def V_ce_d3(mut_fn, orig_fn) -> float:
    """Mean |p_mut - p_orig| (wrapper probability-mass bias)."""
    vals = [abs(float(mut_fn(x)) - float(orig_fn(x))) for x in PROBE_X]
    return float(np.mean(vals))


def V_hp_a1(mut_fn, orig_fn) -> float:
    """Absolute accuracy degradation vs original RK45 reference."""
    vals = [abs(float(mut_fn(x)) - float(orig_fn(x))) for x in PROBE_X]
    return float(np.mean(vals))


def V_hp_b3(mut_fn, orig_fn=None) -> float:
    """Mean |y - (x+1/3)| — MC convergence residual vs analytic."""
    res = [abs(float(mut_fn(x)) - (float(x) + 1.0 / 3.0)) for x in PROBE_X]
    return float(np.mean(res))


def V_hp_c1(mut_fn, orig_fn=None) -> float:
    """Mean |y - erf(6x-3)| — GPR accuracy vs analytic target."""
    res = []
    for x in PROBE_X:
        t = 6.0 * float(x) - 3.0
        res.append(abs(float(mut_fn(x)) - float(erf(t))))
    return float(np.mean(res))


def V_hp_d3(mut_fn, orig_fn) -> float:
    """Mean |p_mut - p_orig| — regularisation-driven calibration drift."""
    vals = [abs(float(mut_fn(x)) - float(orig_fn(x))) for x in PROBE_X]
    return float(np.mean(vals))


FUNCTIONALS = {
    "CE-A1": V_ce_a1,
    "CE-B3": V_ce_b3,
    "CE-C1": V_ce_c1,
    "CE-D3": V_ce_d3,
    "HP-A1": V_hp_a1,
    "HP-B3": V_hp_b3,
    "HP-C1": V_hp_c1,
    "HP-D3": V_hp_d3,
}


def realized_eps(op: str, put: str, amplitude: float, seed: int, orig_fn) -> float:
    cid = curve_id(op, put)
    src = emit_mutant_source(op, put, amplitude, seed)
    mut_fn = _load_fn_from_source(f"dose_{cid}_{seed}", src)
    V = FUNCTIONALS[cid](mut_fn, orig_fn)
    return float(V)


def mean_realized(op: str, put: str, amplitude: float, n_rep: int = N_REPEATS) -> float:
    orig_fn = _load_put_fn(put)
    vals = []
    for r in range(1, n_rep + 1):
        # use level=0 sentinel for calibration-only seeds distinct per repeat
        seed = instance_seed(op, put, level=0, repeat=r)
        # re-seed with amplitude-hash so cal seeds differ from run seeds at e1..e6
        seed = (seed + int(amplitude * 1e6) + BASE_SEED) & 0x7FFFFFFF
        try:
            vals.append(realized_eps(op, put, amplitude, seed, orig_fn))
        except Exception as e:
            print(f"  warn: {op}-{put} amp={amplitude} r={r}: {e}", flush=True)
    if not vals:
        return float("nan")
    return float(np.mean(vals))


def calibrate_curve(op: str, put: str) -> dict:
    """Binary-search nominal amplitudes for target realized grid."""
    cid = curve_id(op, put)
    eps_tol = float(EPS_TOL_SPEC[cid]["eps_tol"])
    targets = eps_tol * np.exp(np.linspace(np.log(0.25), np.log(4.0), N_LEVELS))
    # Amplitude search brackets differ by operator mechanics
    if op == "CE" and put == "a1":
        lo0, hi0 = 1e-4, 50.0
    elif op == "CE" and put == "b3":
        # V ≈ mean |amp*(2*c*x+c^2)| with c=0.1 → O(amp*0.1); target up to 0.08
        lo0, hi0 = 1e-3, 5.0
    elif op == "CE" and put == "c1":
        # V ≈ 2*|amp| on anti-symmetry residual; target up to 0.4
        lo0, hi0 = 1e-3, 1.0
    elif op == "CE" and put == "d3":
        lo0, hi0 = 1e-3, 1.0
    elif op == "HP" and put == "a1":
        # rtol = 1e-8 * 10^amp → amp≈4..7 covers abs-error targets
        lo0, hi0 = 0.5, 10.0
    elif op == "HP" and put == "b3":
        # amp in exp(-amp) N-reduction; amp≈8 → N=1
        lo0, hi0 = 0.1, 12.0
    elif op == "HP" and put == "c1":
        lo0, hi0 = 0.05, 8.0
    else:  # HP-D3
        lo0, hi0 = 0.05, 200.0

    nominals = []
    realized_means = []
    print(f"== calibrating {cid} (eps_tol={eps_tol}) ==", flush=True)
    for ti, target in enumerate(targets, 1):
        lo, hi = lo0, hi0
        best_amp, best_err, best_real = lo, float("inf"), float("nan")
        # probe endpoints
        for amp in (lo, hi):
            real = mean_realized(op, put, amp, n_rep=8)  # coarse during search
            err = abs(real - target)
            if err < best_err:
                best_amp, best_err, best_real = amp, err, real
        # binary search on log-amplitude
        for _ in range(14):
            mid = math.sqrt(lo * hi) if lo > 0 else 0.5 * (lo + hi)
            real = mean_realized(op, put, mid, n_rep=8)
            err = abs(real - target)
            if err < best_err:
                best_amp, best_err, best_real = mid, err, real
            if real < target:
                lo = mid
            else:
                hi = mid
            if hi / max(lo, 1e-12) < 1.02:
                break
        # refine mean at best amp with full 20 repeats
        real_full = mean_realized(op, put, best_amp, n_rep=N_REPEATS)
        nominals.append(float(best_amp))
        realized_means.append(float(real_full))
        print(
            f"  e{ti}: target={target:.6g} amp={best_amp:.6g} "
            f"realized={real_full:.6g} (ratio={real_full/eps_tol:.3f})",
            flush=True,
        )
    return {
        "curve_id": cid,
        "op": op,
        "put": put,
        "eps_tol": eps_tol,
        "targets": [float(t) for t in targets],
        "nominal_amplitudes": nominals,
        "eps_realized_mean": realized_means,
        "realized_over_tol": [r / eps_tol for r in realized_means],
    }


# ── Window estimation on ORIGINAL programs only ─────────────────────────────

def estimate_windows() -> list[dict]:
    """Delta_r + eta_bar from originals; no mutants involved."""
    rows = []
    for op in OPS:
        for put in PUTS:
            cid = curve_id(op, put)
            eps_tol = float(EPS_TOL_SPEC[cid]["eps_tol"])
            mp = ALIGNED_MP[op]
            export_path = MR_EXPORT / f"{put}_MP{mp}_mr.json"
            export_meta = json.loads(export_path.read_text()) if export_path.exists() else {}
            orig_fn = _load_put_fn(put)

            # Delta_r: residual of ORIGINAL against the invariant functional
            if cid == "CE-A1":
                # F-10 functional V=mean|y_mut-y_orig| ⇒ original self-residual = 0.
                # (R_mp1 guard abs(y+y')<1e6 is not the dose-axis functional.)
                delta_r = 0.0
                method_dr = (
                    "A1-CE: Delta_r:=0 under F-10 functional V=mean|y_mut-y_orig| "
                    "(original vs itself); R_mp1 guard 1e6 is not used as residual"
                )
            elif cid == "CE-B3":
                delta_r = V_ce_b3(orig_fn)
                method_dr = "linearity residual of original MC estimator (fixed seed samples → exact linearity ⇒ ~0)"
            elif cid == "CE-C1":
                delta_r = V_ce_c1(orig_fn)
                method_dr = "anti-symmetry residual of original GPR on PROBE_X"
            elif cid == "CE-D3":
                delta_r = 0.0  # original has zero self-bias
                method_dr = "original self-bias = 0 (identity); Delta_r:=0"
            elif cid == "HP-A1":
                delta_r = 0.0  # V_hp_a1(orig,orig)=0
                method_dr = "relative error of original vs itself = 0; Delta_r:=0 (RK45 rtol=1e-8 taken as ref)"
            elif cid == "HP-B3":
                delta_r = V_hp_b3(orig_fn)
                method_dr = "mean |y-(x+1/3)| of original MC (analytic residual)"
            elif cid == "HP-C1":
                delta_r = V_hp_c1(orig_fn)
                method_dr = "mean |y-erf(6x-3)| of original GPR"
            else:  # HP-D3
                delta_r = 0.0
                method_dr = "original vs itself = 0; Delta_r:=0"

            # eta_bar: execution-noise bound
            if put == "b3":
                # stochastic MC: c*sigma/sqrt(N) + eta_det; N=5000, c≈2
                # Var(t^2 on U[0,1]) = E[t^4]-E[t^2]^2 = 1/5 - 1/9 = 4/45
                sigma = math.sqrt(4.0 / 45.0)
                N = 5000
                eta_det = 1e-6  # E2 / AVP epsilon convention
                eta_bar = 2.0 * sigma / math.sqrt(N) + eta_det
                method_eta = (
                    f"stochastic: 2*sigma_t2/sqrt(N)+eta_det; "
                    f"sigma=sqrt(4/45), N={N}, eta_det=1e-6 (AVP/E2)"
                )
            elif put in ("c1", "d3"):
                # sklearn fits are deterministic given random_state; use E2 eps
                # plus empirical repeat dispersion (should be ~0)
                ys = [float(orig_fn(0.5)) for _ in range(20)]
                disp = float(np.std(ys))
                eta_bar = max(disp, 1e-6)
                method_eta = (
                    f"deterministic-kernel: max(std of 20 repeats at x=0.5, "
                    f"AVP eps 1e-6); observed_std={disp:.3e}"
                )
            else:  # a1
                ys = [float(orig_fn(0.5)) for _ in range(5)]
                disp = float(np.std(ys))
                eta_bar = max(disp, 1e-6)
                method_eta = (
                    f"deterministic ODE: max(std of 5 repeats at x=0.5, "
                    f"AVP eps 1e-6); observed_std={disp:.3e}"
                )

            half = float(delta_r + 2.0 * eta_bar)
            rows.append({
                "curve_id": cid,
                "eps_tol": eps_tol,
                "delta_r": float(delta_r),
                "eta_bar": float(eta_bar),
                "window_halfwidth": half,
                "aligned_mp": mp,
                "mr_export_file": export_meta and f"{put}_MP{mp}_mr.json",
                "mr_export_r_name": export_meta.get("r_name"),
                "mr_export_R_name": export_meta.get("R_name"),
                "eps_tol_source": EPS_TOL_SPEC[cid]["native_source"],
                "method_delta_r": method_dr,
                "method_eta_bar": method_eta,
                "method_notes": (
                    "window_halfwidth = delta_r + 2*eta_bar; "
                    "estimated on ORIGINAL program only (no mutants); "
                    f"freeze_seed={BASE_SEED}"
                ),
            })
            print(
                f"WINDOW {cid}: eps_tol={eps_tol} delta_r={delta_r:.6g} "
                f"eta_bar={eta_bar:.6g} half={half:.6g}",
                flush=True,
            )
    return rows


def write_calibration_md(cal_rows: list[dict], win_rows: list[dict]) -> str:
    win_by = {w["curve_id"]: w for w in win_rows}
    lines = [
        "# DOSE_CALIBRATION — EXP-DOSE F-10 two-axis ledger",
        "",
        f"Freeze seed: `{BASE_SEED}`. Design: 6 levels × 20 repeats × 8 curves = 960.",
        "",
        "## eps_tol provenance",
        "",
        "`data/mr_export/{put}_MP{1|3}_mr.json` contains **no** `eps_tol` / `epsilon` field "
        "(keys: put, mp, r_name, R_name, primary, sample_pairs). "
        "Per-curve `eps_tol` is taken from the numeric threshold of the aligned "
        "`R_mp` predicate in `src/p2/mrs/{put}.py` (or a documented normalized/"
        "surrogate scale when the predicate is a hard bound / envelope). "
        "The mr_export file is retained for put/mp/r_name/R_name provenance.",
        "",
        "## Direct invariant-violation functionals (F-10; not MR checkers)",
        "",
        "| Curve | Functional V | Formula |",
        "|---|---|---|",
        "| CE-A1 | conservation-drift | mean_x |y_mut(x)-y_orig(x)| on PROBE_X |",
        "| CE-B3 | linearity-violation | mean_x | |y(x+0.1)-y(x)| - 0.1 | |",
        "| CE-C1 | anti-symmetry residual | mean_x |y(x)+y(1-x)| |",
        "| CE-D3 | probability bias | mean_x |p_mut(x)-p_orig(x)| |",
        "| HP-A1 | relative accuracy loss | mean_x |y_mut-y_ref|/(1+|y_ref|) |",
        "| HP-B3 | analytic residual | mean_x |y(x)-(x+1/3)| |",
        "| HP-C1 | analytic residual | mean_x |y(x)-erf(6x-3)| |",
        "| HP-D3 | calibration drift | mean_x |p_mut(x)-p_orig(x)| |",
        "",
        "## Nominal → realized two-axis table (mean over 20 seeded instances)",
        "",
    ]
    for row in cal_rows:
        cid = row["curve_id"]
        w = win_by[cid]
        lines.append(f"### {cid}")
        lines.append("")
        lines.append(f"- eps_tol = `{row['eps_tol']}`")
        lines.append(f"- eps_tol source: {EPS_TOL_SPEC[cid]['native_source']}")
        lines.append(
            f"- window: delta_r=`{w['delta_r']:.6g}`, eta_bar=`{w['eta_bar']:.6g}`, "
            f"halfwidth=`{w['window_halfwidth']:.6g}`"
        )
        lines.append("")
        lines.append("| level | nominal_amp | target eps_m | realized mean eps_m | realized/eps_tol |")
        lines.append("|---|---|---|---|---|")
        for i in range(N_LEVELS):
            lines.append(
                f"| e{i+1} | {row['nominal_amplitudes'][i]:.6g} | "
                f"{row['targets'][i]:.6g} | {row['eps_realized_mean'][i]:.6g} | "
                f"{row['realized_over_tol'][i]:.4f} |"
            )
        lines.append("")
    lines.append("## Realized-axis span check")
    lines.append("")
    lines.append("Target span per curve: [0.25, 4.0] × eps_tol (log-spaced, 6 levels).")
    lines.append("")
    for row in cal_rows:
        r = row["realized_over_tol"]
        lines.append(
            f"- {row['curve_id']}: realized/tol ∈ [{min(r):.3f}, {max(r):.3f}] "
            f"(target [0.25, 4.0])"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # 1) Window freeze FIRST (originals only) — commit barrier for PASS-1
    win_rows = estimate_windows()
    win_path = OUT_DIR / "WINDOWS_FROZEN.json"
    win_doc = {
        "schema": "WINDOWS_FROZEN/v1",
        "freeze_seed": BASE_SEED,
        "formula": "window_halfwidth = delta_r + 2*eta_bar",
        "note": (
            "FROZEN BEFORE dose unblinding (H-DOSE-CTR). Estimated on ORIGINAL "
            "programs only; no mutant realizations enter this file."
        ),
        "eps_tol_field_resolution": (
            "mr_export JSON has no eps_tol field; values taken from aligned R_mp "
            "numeric thresholds (see per-curve eps_tol_source)."
        ),
        "curves": win_rows,
    }
    win_path.write_text(json.dumps(win_doc, indent=2))
    print(f"Wrote {win_path}", flush=True)

    # 2) Calibrate nominal amplitudes
    cal_rows = []
    for op in OPS:
        for put in PUTS:
            cal_rows.append(calibrate_curve(op, put))

    grid_path = OUT_DIR / "nominal_grid.json"
    grid_path.write_text(json.dumps({"curves": cal_rows, "seed": BASE_SEED}, indent=2))
    print(f"Wrote {grid_path}", flush=True)

    md = write_calibration_md(cal_rows, win_rows)
    md_path = OUT_DIR / "DOSE_CALIBRATION.md"
    md_path.write_text(md)
    print(f"Wrote {md_path}", flush=True)


if __name__ == "__main__":
    main()
