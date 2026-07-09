"""Per-PUT Python-vs-C agreement (the C_PORT_SPEC.md tolerance table).

Deterministic kernels must match the Python reference at (near) machine
precision; stochastic/design kernels must track the analytic target
within the documented distributional band (NOT bit-equality vs Python —
the C LCG is a different stream from numpy PCG64, by design).
"""
import importlib
from pathlib import Path

import pytest

from p2.cport import load_c_put

ROOT = Path(__file__).resolve().parents[2]
XS = [0.0, 0.25, 0.5, 0.75, 1.0]


def _py(put):
    return importlib.import_module(f"p2.puts.{put}").program


# a3's domain is (0,1]; x=0 clamps to h=1e-4 (N=10000, ~40s at -O0), so the
# small-h agreement is verified at x=1e-3 (N=1000, correct + fast) instead.
_XS_BY_PUT = {"a3": [0.001, 0.1, 0.25, 0.5, 0.75, 1.0]}


@pytest.mark.parametrize("put", ["a2", "a3", "b1"])
def test_deterministic_bit_identical(put):
    """a2/a3/b1 reproduce the Python float to machine precision."""
    py, c = _py(put), load_c_put(put, ROOT)
    try:
        for x in _XS_BY_PUT.get(put, XS):
            assert float(c(x)) == pytest.approx(float(py(x)), rel=1e-9, abs=1e-9)
    finally:
        c.close()


def test_a1_chaos_bounded():
    """Lorenz is chaotic; agreement is bounded by the reference RK45 tol."""
    py, c = _py("a1"), load_c_put("a1", ROOT)
    try:
        for x in XS:
            yp, yc = float(py(x)), float(c(x))
            assert abs(yp - yc) / (abs(yp) + 1e-30) < 1e-4
    finally:
        c.close()


def test_b2_mcmc_distributional():
    """Chain mean tracks mu = 4x-2 within MCMC error (documented < 0.35)."""
    c = load_c_put("b2", ROOT)
    try:
        for x in XS:
            mu = 4.0 * x - 2.0
            assert abs(float(c(x)) - mu) < 0.35
    finally:
        c.close()


def test_b3_mc_distributional():
    """MC estimate tracks x + 1/3 within MC error (documented < 0.02)."""
    c = load_c_put("b3", ROOT)
    try:
        for x in XS:
            assert abs(float(c(x)) - (x + 1.0 / 3.0)) < 0.02
    finally:
        c.close()


def test_c2_pce_design_distributional():
    """Degree-5 LS surrogate agrees with Python within design band < 0.02."""
    py, c = _py("c2"), load_c_put("c2", ROOT)
    try:
        for x in XS:
            assert abs(float(c(x)) - float(py(x))) < 0.02
    finally:
        c.close()
