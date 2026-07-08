"""MR functions for A5 cubic-spline interpolation of sin(π t).

§3.3 grid: a5 = mp1●● mp2○ mp3● mp4● mp5○

Target sin(π t) is symmetric about t=½ and bounded in [0,1] over the domain.

MP1 (Conservation, ●●): r_mp1(x)=1-x; R_mp1: |y_o - y_n| < 1e-3 (reflection
  invariance S(x)=S(1-x); the symmetric knot grid makes it near-exact).
MP2 (Monotonicity, ○): sin(π t) is not monotone on [0,1]; ○ baseline.
MP3 (Convergence, ●): r_mp3(x)=x; R_mp3: y ∈ [-0.05, 1.05] (bounded within the
  target range plus interpolation margin).
MP4 (Trajectory, ●): r_mp4(x)=1-x; R_mp4: |y_o - y_n| < 0.05 (loose reflection
  symmetry of the interpolant shape).
MP5 (Asymptotic, ○): no asymptotic ordering for a non-monotone target; ○ baseline.
"""
import math


def r_mp1(x) -> float:
    return 1.0 - float(x)


def R_mp1(y_orig, y_new) -> bool:
    y_o, y_n = float(y_orig), float(y_new)
    if not (math.isfinite(y_o) and math.isfinite(y_n)):
        return False
    return abs(y_o - y_n) < 1e-3


def r_mp2(x) -> float:
    return float(x)


def R_mp2(y_orig, y_new) -> bool:
    return False


def r_mp3(x) -> float:
    return float(x)


def R_mp3(y_orig, y_new) -> bool:
    y = float(y_orig)
    return math.isfinite(y) and -0.05 <= y <= 1.05


def r_mp4(x) -> float:
    return 1.0 - float(x)


def R_mp4(y_orig, y_new) -> bool:
    y_o, y_n = float(y_orig), float(y_new)
    if not (math.isfinite(y_o) and math.isfinite(y_n)):
        return False
    return abs(y_o - y_n) < 0.05


def r_mp5(x) -> float:
    return float(x)


def R_mp5(y_orig, y_new) -> bool:
    return False


def r_trivial(x) -> float:
    return float(x)


def R_trivial(y_orig, y_new) -> bool:
    return True
