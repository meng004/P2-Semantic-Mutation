"""MR functions for A6 nonlinear root-finding r³+r=4x-2.

§3.3 grid: a6 = mp1●● mp2●● mp3● mp4○ mp5●

The root r(x) is odd-symmetric about x=½ and lies in [-1,1] (r³+r=±2 → r=±1).

MP1 (Conservation, ●●): r_mp1(x)=1-x; R_mp1: |y_o + y_n| < 1e-6 (odd symmetry
  r(x)+r(1-x)=0, exact by antisymmetry of the RHS).
MP2 (Monotonicity, ●●): r_mp2(x)=min(x+0.1,0.9); R_mp2: y_new >= y_orig - 1e-9
  (strictly increasing root in x).
MP3 (Convergence, ●): r_mp3(x)=x; R_mp3: y ∈ [-1.05, 1.05] (bounded root range).
MP4 (Trajectory, ○): scalar in/out, no trajectory; ○ baseline.
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
    y = float(y_orig)
    return math.isfinite(y) and -1.05 <= y <= 1.05


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
