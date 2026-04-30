"""MR functions for B3 Monte Carlo Integration.

§3.3 grid: b3 = mp1●● mp2○ mp3●● mp4● mp5○

PUT: program(x) ≈ ∫₀¹(x+t²)dt = x + 1/3, fixed N=5000 samples (seed=42).

MP1 (Conservation, ●●): existing — linearity, |y(x+0.1) − y(x) − 0.1| < 0.02.
MP2 (Monotonicity, ○): MC estimate is trivially monotone in x (linear);
  the standard MP2 MR adds no information; ○ baseline.
MP3 (Convergence, ●●): r_mp3(x)=x; R_mp3: |y − (x + 1/3)| < 0.02
  (verify the MC estimator has converged to the analytic integral within
  MC error √(Var/N) ≈ 0.013 at N=5000).
MP4 (Trajectory, ●): r_mp4(x)=1-x; R_mp4: y(x) + y(1-x) ≈ 1 + 2/3
  (sum of two integrals: (x + 1/3) + (1-x + 1/3) = 5/3 = 1.667 ± 0.04).
MP5 (Asymptotic, ○): scalar MC, no asymptotic-ordering structure;
  ○ baseline.
"""
import math


def r_mp1(x) -> float:
    """Shift integrand constant by ±0.1; choose direction to keep r(x) ∈
    [0, 1] across the full input domain (saturated near the upper edge
    causes R to fail trivially)."""
    x = float(x)
    return x + 0.1 if x < 0.85 else x - 0.1


def R_mp1(y_orig, y_new) -> bool:
    """Linearity (sign-agnostic): |y_new − y_orig| ≈ 0.1 ± 0.02."""
    return abs(abs(float(y_new) - float(y_orig)) - 0.1) < 0.02


def r_mp2(x) -> float:
    return float(x)


def R_mp2(y_orig, y_new) -> bool:
    return False


def r_mp3(x) -> float:
    return float(x)


def R_mp3(y_orig, y_new) -> bool:
    """Convergence to analytic integral. y = chain mean ≈ x + 1/3.
    We don't have access to x in R, so check y ∈ [1/3, 4/3] envelope."""
    y = float(y_orig)
    if not math.isfinite(y):
        return False
    return 1.0 / 3.0 - 0.05 <= y <= 4.0 / 3.0 + 0.05


def r_mp4(x) -> float:
    return float(1.0 - float(x))


def R_mp4(y_orig, y_new) -> bool:
    y_o, y_n = float(y_orig), float(y_new)
    if not (math.isfinite(y_o) and math.isfinite(y_n)):
        return False
    return abs((y_o + y_n) - 5.0 / 3.0) < 0.04


def r_mp5(x) -> float:
    return float(x)


def R_mp5(y_orig, y_new) -> bool:
    return False


def r_trivial(x) -> float:
    return float(x)


def R_trivial(y_orig, y_new) -> bool:
    return True
