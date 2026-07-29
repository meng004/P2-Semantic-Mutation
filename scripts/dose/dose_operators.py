#!/usr/bin/env python3
"""Parameterized HP / CE dose operators for EXP-DOSE (POOL-DOSE).

Design (prereg power_report §7 / hypotheses.md):
  operators {HP, CE} × kernels {A1, B3, C1, D3} × 6 levels × 20 repeats = 960
  mutant id: mut-<OP>-<PUT>-e<level>-r<repeat>   (level 1..6, repeat 01..20)
  seed: derived from (BASE_SEED=20260728, op, put, level, repeat)

Sites are wrapper-level only (applicability_matrix.md). Amplitude is a
continuous nominal injection parameter; realized ε_m is measured separately
by calibrate_eps.py (F-10 direct invariant-violation functional).

Note on CE×D3: the applicability matrix marks CE×d3 NOT_APPLICABLE for
H-CONS (probability normalisation is library-internal). EXP-DOSE still
includes a D3-CE curve for four-class kernel coverage; the template injects
a wrapper-level probability bias (conserved-quantity erosion of P(y=0)+P(y=1)).
"""
from __future__ import annotations

import hashlib
import math
import re
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parents[2]
PUTS_DIR = ROOT / "src" / "p2" / "puts"
BASE_SEED = 20260728

OPS = ("CE", "HP")
PUTS = ("a1", "b3", "c1", "d3")
N_LEVELS = 6
N_REPEATS = 20

# Alignment map (applicability_matrix.md § final): CE→MP1, HP→MP3
ALIGNED_MP = {"CE": 1, "HP": 3}

CURVE_IDS = [f"{op}-{put.upper()}" for op in OPS for put in PUTS]


def instance_seed(op: str, put: str, level: int, repeat: int) -> int:
    """Deterministic 31-bit seed from (BASE_SEED, op, put, level, repeat)."""
    payload = f"{BASE_SEED}|{op}|{put}|{level}|{repeat}".encode()
    return int(hashlib.sha256(payload).hexdigest()[:8], 16) & 0x7FFFFFFF


def mutant_id(op: str, put: str, level: int, repeat: int) -> str:
    return f"mut-{op}-{put.upper()}-e{level}-r{repeat:02d}"


def load_put_source(put: str) -> str:
    return (PUTS_DIR / f"{put}.py").read_text()


def _jitter(seed: int, scale: float = 0.05) -> float:
    """Multiplicative jitter in [1-scale, 1+scale] from seed."""
    u = (seed % 10_000) / 10_000.0  # [0, 1)
    return 1.0 + scale * (2.0 * u - 1.0)


# ── emission templates ──────────────────────────────────────────────────────

def _emit_a1_ce(amplitude: float, seed: int) -> str:
    """CE on Lorenz: inject RHS additive drift proportional to amplitude.

    Site: wrapper RHS (_lorenz). Conserved-structure erosion via spurious
    forcing term amp * jitter * [1, 0, 0] added to the vector field.
    """
    amp = amplitude * _jitter(seed)
    src = load_put_source("a1")
    # Rewrite _lorenz to add drift; keep signature.
    old = (
        "def _lorenz(t, y, sigma, rho, beta):\n"
        "    x, yy, z = y\n"
        "    return [sigma * (yy - x), x * (rho - z) - yy, x * yy - beta * z]\n"
    )
    new = (
        "def _lorenz(t, y, sigma, rho, beta):\n"
        "    x, yy, z = y\n"
        f"    _drift = {amp:.16e}  # dose CE amplitude (seed-jittered)\n"
        "    return [sigma * (yy - x) + _drift, x * (rho - z) - yy, x * yy - beta * z]\n"
    )
    if old not in src:
        raise RuntimeError("A1-CE: unexpected a1.py layout (RHS site missing)")
    return src.replace(old, new, 1)


def _emit_a1_hp(amplitude: float, seed: int) -> str:
    """HP on Lorenz: switch to RK23 and loosen rtol (convergence knob).

    Site: solve_ivp method/rtol/atol. rtol = min(0.5, 1e-8 * 10^(amp*j)).
    """
    j = _jitter(seed)
    rtol = min(0.5, 1e-8 * (10.0 ** (max(0.0, float(amplitude)) * j)))
    atol = min(0.5, rtol * 0.01)
    src = load_put_source("a1")
    src2, n = re.subn(
        r'method="RK45", rtol=1e-8, atol=1e-10',
        f'method="RK23", rtol={rtol:.16e}, atol={atol:.16e}',
        src,
        count=1,
    )
    if n != 1:
        raise RuntimeError("A1-HP: solve_ivp site missing")
    return src2


def _emit_b3_ce(amplitude: float, seed: int) -> str:
    """CE on MC integration: add nonlinear-in-x bias so linearity fails by O(amp).

    Site: return expression in program(). t^3-only edits preserve linearity in x;
    amp*x**2 is the wrapper-level conservation-erosion site (matrix: integrand
    linearity ∫(x+c)-∫x=c).
    """
    amp = amplitude * _jitter(seed)
    src = load_put_source("b3")
    old = "    return float(np.mean(x + _rng_samples**2))\n"
    new = (
        f"    _amp = {amp:.16e}  # dose CE amplitude (seed-jittered)\n"
        "    return float(np.mean(x + _rng_samples**2) + _amp * x * x)\n"
    )
    if old not in src:
        raise RuntimeError("B3-CE: integrand site missing")
    return src.replace(old, new, 1)


def _emit_b3_hp(amplitude: float, seed: int) -> str:
    """HP on MC: exponentially reduce sample count; redraw samples each call.

    Site: _N_SAMPLES + sampling line. n' = max(1, round(N * exp(-amp*j))).
    Redraw avoids fixed-prefix non-monotonicity of the frozen sample table.
    """
    j = _jitter(seed)
    n1 = max(1, int(round(5000 * math.exp(-max(0.0, float(amplitude)) * j))))
    src = load_put_source("b3")
    # Replace module-level frozen samples with per-call draw of size n1
    src2, n = re.subn(r"_N_SAMPLES = \d+", f"_N_SAMPLES = {n1}", src, count=1)
    if n != 1:
        raise RuntimeError("B3-HP: _N_SAMPLES site missing")
    old = "    return float(np.mean(x + _rng_samples**2))\n"
    new = (
        "    rs = np.random.default_rng(_SEED).uniform(0.0, 1.0, _N_SAMPLES)\n"
        "    return float(np.mean(x + rs**2))\n"
    )
    if old not in src2:
        raise RuntimeError("B3-HP: return site missing")
    return src2.replace(old, new, 1)


def _emit_c1_ce(amplitude: float, seed: int) -> str:
    """CE on GPR: offset training targets (erodes odd-symmetry conservation).

    Site: _y_train construction (matrix: WhiteKernel PSD / target-symmetry).
    y' = erf(t) + amp*jitter breaks y(x)+y(1-x)≈0 by ≈2*amp.
    """
    amp = float(amplitude) * _jitter(seed)
    src = load_put_source("c1")
    old = "_y_train = erf(_t_train.ravel())\n"
    new = (
        f"_y_train = erf(_t_train.ravel()) + {amp:.16e}  # dose CE target offset\n"
    )
    if old not in src:
        raise RuntimeError("C1-CE: _y_train site missing")
    return src.replace(old, new, 1)


def _emit_c1_hp(amplitude: float, seed: int) -> str:
    """HP on GPR: shrink training set + distort length_scale (accuracy-order).

    Sites: training-size slice and RBF(length_scale=1.0).
    """
    j = _jitter(seed)
    amp = max(0.0, float(amplitude)) * j
    # keep at least 5 training points
    keep = max(5, int(round(60 / (1.0 + 4.0 * amp))))
    ls = max(1e-3, 1.0 * (10.0 ** (-amp)))
    src = load_put_source("c1")
    old = (
        "_t_train = np.sort(_rng.uniform(-3.0, 3.0, 60)).reshape(-1, 1)\n"
        "_y_train = erf(_t_train.ravel())\n"
        "\n"
        "_kernel = RBF(length_scale=1.0) + WhiteKernel(noise_level=1e-4)\n"
    )
    new = (
        f"_t_train = np.sort(_rng.uniform(-3.0, 3.0, 60))[:{keep}].reshape(-1, 1)\n"
        "_y_train = erf(_t_train.ravel())\n"
        "\n"
        f"_kernel = RBF(length_scale={ls:.16e}) + WhiteKernel(noise_level=1e-4)\n"
    )
    if old not in src:
        raise RuntimeError("C1-HP: training/kernel site missing")
    return src.replace(old, new, 1)


def _emit_d3_ce(amplitude: float, seed: int) -> str:
    """CE on LogReg: wrapper-level probability bias (no clip; allows V>1).

    Site: return of predict_proba. Bias amp*jitter; values may leave [0,1]
    so the conserved-quantity deviation is measurable on a continuous scale.
    (Matrix marks CE×d3 NOT_APPLICABLE for H-CONS; retained for EXP-DOSE.)
    """
    amp = float(amplitude) * _jitter(seed)
    src = load_put_source("d3")
    old = "    return float(_model.predict_proba([[x, 0.0]])[0, 1])\n"
    new = (
        f"    _bias = {amp:.16e}  # dose CE probability bias (unclipped)\n"
        "    return float(_model.predict_proba([[x, 0.0]])[0, 1]) + _bias\n"
    )
    if old not in src:
        raise RuntimeError("D3-CE: predict_proba return site missing")
    return src.replace(old, new, 1)


def _emit_d3_hp(amplitude: float, seed: int) -> str:
    """HP on LogReg: change regularisation C.

    Site: LogisticRegression(C=1.0, ...). C' = 1.0 / (1 + amp*j) (stronger reg).
    """
    j = _jitter(seed)
    c = 1.0 / (1.0 + max(0.0, float(amplitude)) * j)
    src = load_put_source("d3")
    src2, n = re.subn(
        r"LogisticRegression\(C=1\.0,",
        f"LogisticRegression(C={c:.16e},",
        src,
        count=1,
    )
    if n != 1:
        raise RuntimeError("D3-HP: C= site missing")
    return src2


_EMITTERS: dict[tuple[str, str], Callable[[float, int], str]] = {
    ("CE", "a1"): _emit_a1_ce,
    ("HP", "a1"): _emit_a1_hp,
    ("CE", "b3"): _emit_b3_ce,
    ("HP", "b3"): _emit_b3_hp,
    ("CE", "c1"): _emit_c1_ce,
    ("HP", "c1"): _emit_c1_hp,
    ("CE", "d3"): _emit_d3_ce,
    ("HP", "d3"): _emit_d3_hp,
}


def emit_mutant_source(op: str, put: str, amplitude: float, seed: int) -> str:
    key = (op.upper(), put.lower())
    if key not in _EMITTERS:
        raise KeyError(f"no dose emitter for {key}")
    return _EMITTERS[key](float(amplitude), int(seed))


def emit_instance(op: str, put: str, level: int, repeat: int, amplitude: float) -> tuple[str, str, int]:
    """Return (mutant_id, source, seed) for one dose instance."""
    op, put = op.upper(), put.lower()
    seed = instance_seed(op, put, level, repeat)
    mid = mutant_id(op, put, level, repeat)
    src = emit_mutant_source(op, put, amplitude, seed)
    return mid, src, seed


def curve_id(op: str, put: str) -> str:
    return f"{op.upper()}-{put.upper()}"
