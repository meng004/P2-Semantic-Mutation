"""MR functions for A7 tridiagonal linear solve, observable Σu(x)=(2x-1)·s.

§3.3 grid: a7 = mp1●● mp2●● mp3○ mp4○ mp5●

The linear functional Σu(x) is affine and antisymmetric about x=½.

MP1 (Conservation, ●●): r_mp1(x)=1-x; R_mp1: |y_o + y_n| < 1e-6 (antisymmetry
  Σu(x)+Σu(1-x)=0, exact by linearity of the solve).
MP2 (Monotonicity, ●●): r_mp2(x)=min(x+0.1,0.9); R_mp2: y_new >= y_orig - 1e-9
  (strictly increasing in x).
MP3 (Convergence, ○): direct solve has no refinement knob; ○ baseline.
MP4 (Trajectory, ○): scalar functional, no trajectory; ○ baseline.
MP5 (Asymptotic, ●): r_mp5(x)=min(x+0.1,0.9); R_mp5: y_new >= y_orig - 1e-9
  (asymptotic ordering at the input-domain endpoints).
"""
import math


def r_mp1(x) -> float:
    return 1.0 - float(x)


def R_mp1(y_orig, y_new) -> bool:
    y_o, y_n = float(y_orig), float(y_new)
    if not (math.isfinite(y_o) and math.isfinite(y_n)):
        return False
    return abs(y_o + y_n) < 1e-6


def r_mp2(x) -> float:
    return min(float(x) + 0.1, 0.9)


def R_mp2(y_orig, y_new) -> bool:
    return float(y_new) >= float(y_orig) - 1e-9


def r_mp3(x) -> float:
    return float(x)


def R_mp3(y_orig, y_new) -> bool:
    return False


def r_mp4(x) -> float:
    return float(x)


def R_mp4(y_orig, y_new) -> bool:
    return False


def r_mp5(x) -> float:
    return min(float(x) + 0.1, 0.9)


def R_mp5(y_orig, y_new) -> bool:
    return float(y_new) >= float(y_orig) - 1e-9


def r_trivial(x) -> float:
    return float(x)


def R_trivial(y_orig, y_new) -> bool:
    return True
