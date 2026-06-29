"""Boundary case FN (surviving mutant / tolerance fault) — numpy float32 RNG.

Real-bug version pair (numpy #17478, PR#20314): BUGGY 1.21.6 -> CORRECT 1.22.0.

Demonstrates a FALSE NEGATIVE / strong-edge (盲区): a genuinely non-equivalent
mutant SURVIVES the structural MR (mean/range look fine), so the MR is blind to
it; only a finer discriminator (LSB parity) reveals the defect. epsilon_tol is
an explicit factor.
"""
from pathlib import Path
from version_switch import run_observable

PKG, CORRECT_VER, BUGGY_VER, PY = "numpy", "1.22.0", "1.21.6", "3.10"
_D = Path(__file__).resolve().parent
_STRUCT, _DISC = str(_D/"obs_fn_struct.py"), str(_D/"obs_fn_disc.py")
SWEEP = (0.1, 0.4, 0.7, 0.95)

def structural_verdict(ver, epsilon_tol=1e-2):
    """Structural MR (mean ~ 0.5). 'pass' = survives (blind spot)."""
    ok = all(abs(run_observable(PKG,ver,_STRUCT,x,extra=(),python=PY)-0.5) <= epsilon_tol
             for x in SWEEP)
    return "pass" if ok else "fail"

def discriminator(ver):
    """LSB-parity probe: ~0 for buggy, ~0.5 for correct."""
    return run_observable(PKG, ver, _DISC, 0.5, extra=(), python=PY)
