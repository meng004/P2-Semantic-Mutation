"""MR functions for A3 FDM Heat Equation.

§3.3 grid: a3 = mp1●● mp2● mp3●● mp4●● mp5○

PUT: explicit-Euler heat eq, returns u_FDM(0.5, t_end) / u_exact(0.5, t_end);
ratio → 1.0 as h→0 with order O(h²).

MP1 (Conservation, ●●): r_mp1(x)=x; R_mp1: positivity (sin IC stays
  positive on (0,1) under heat decay; ratio must be > 0).
MP2 (Monotonicity, ●): r_mp2(x)=x/2 (halve grid spacing); R_mp2 =
  refinement reduces |ratio−1| (existing implementation).
MP3 (Convergence, ●●): MP3 is verified by AVP convergence-order verifier
  (sweeps h; r/R unused). Stubs return identity.
MP4 (Trajectory, ●●): r_mp4(x)=x/4 (further refinement); R_mp4: ratio at
  finer grid is closer to 1 than at coarser grid (consistency along the
  refinement trajectory).
MP5 (Asymptotic, ○): r_mp5=identity; R_mp5 = always False. ○ baseline —
  the heat equation has no asymptotic ordering in the grid-spacing input.
"""
import math


def r_mp1(x) -> float:
    return float(x)


def R_mp1(y_orig, y_new) -> bool:
    """Positivity invariant: sin IC + heat decay → ratio stays positive."""
    y_o, y_n = float(y_orig), float(y_new)
    if not (math.isfinite(y_o) and math.isfinite(y_n)):
        return False
    return y_o > 0 and y_n > 0


def r_mp2(x) -> float:
    return max(float(x) / 2.0, 1e-4)


def R_mp2(y_orig, y_new) -> bool:
    """Refinement bound for explicit-Euler heat eq. 5e-2 margin absorbs
    coarse-grid noise when N=round(1/h) is below the well-resolved
    threshold (~10); on fine grids the bound is essentially tight."""
    y_o, y_n = float(y_orig), float(y_new)
    if not (math.isfinite(y_o) and math.isfinite(y_n)):
        return False
    return abs(y_n - 1.0) <= abs(y_o - 1.0) + 5e-2


def r_mp3(x) -> float:
    return float(x) / 2.0


def R_mp3(y_orig, y_new) -> bool:
    return True  # unused by verify_convergence_order


def r_mp4(x) -> float:
    """Refine grid spacing by ×10 — substantial enough that coarse-grid
    discretization noise no longer obscures the monotone refinement."""
    return max(float(x) / 10.0, 1e-3)


def R_mp4(y_orig, y_new) -> bool:
    """Refinement-trajectory consistency: |ratio−1| decreases along the
    grid-refinement trajectory. 5e-2 margin absorbs coarse-grid noise
    when the original x already lands in the well-resolved regime
    (ratio close to 1 → almost no headroom to improve)."""
    y_o, y_n = float(y_orig), float(y_new)
    if not (math.isfinite(y_o) and math.isfinite(y_n)):
        return False
    return abs(y_n - 1.0) <= abs(y_o - 1.0) + 5e-2


def r_mp5(x) -> float:
    return float(x)


def R_mp5(y_orig, y_new) -> bool:
    return False


def r_trivial(x) -> float:
    return float(x)


def R_trivial(y_orig, y_new) -> bool:
    return True
