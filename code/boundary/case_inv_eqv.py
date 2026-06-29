"""Boundary case inv.eqv — equivariance / rotation-recovery (strong MR).

Real-bug version pair (provenance: scipy #20660/#20555, PR#20573):
  BUGGY_VER 1.13.0  ->  CORRECT_VER 1.13.1.

Strong MR (inv.eqv): align_vectors must recover the rotation relating any single
alignable pair, so the recovery residual stays within epsilon_tol of zero for
every configuration in the sweep, INCLUDING the anti-parallel boundary (x=1.0).
The buggy version violates this at x=1.0 (identity collapse) and is killed; the
correct version passes.

epsilon_tol is an EXPLICIT factor (argument), not a hard-wired constant.
"""
from pathlib import Path

from version_switch import run_observable

PKG = "scipy"
CORRECT_VER = "1.13.1"   # post-fix
BUGGY_VER = "1.13.0"     # pre-fix (real defect)

_OBS = str(Path(__file__).resolve().parent / "obs_inv_eqv.py")

# sweep includes the anti-parallel boundary x=1.0 where the real bug lives
SWEEP = (0.2, 0.5, 0.8, 0.95, 1.0)


def residuals(ver: str):
    return [run_observable(PKG, ver, _OBS, x) for x in SWEEP]


def verdict(ver: str, epsilon_tol: float = 1e-6) -> str:
    """'pass' if the strong MR holds for all configs; 'fail' (killed) otherwise."""
    return "pass" if all(abs(r) <= epsilon_tol for r in residuals(ver)) else "fail"
