"""MR functions for C4 kNN surrogate of arctan(3t), t = 6x − 3.

§3.3 grid: c4 = mp1● mp2●● mp3●● mp4● mp5●●

target arctan(3t) is odd on [−3,3], monotone increasing, bounded ∈ (−π/2, π/2).

MP1 (Conservation, ●): r_mp1(x)=1-x → reflects t around 0; R_mp1: |y_o + y_n|
  < 0.5 (odd target; kNN averaging tolerance).
MP2 (Monotonicity, ●●): r_mp2(x)=min(x+0.1,0.9); R_mp2: y_new >= y_orig - 0.15
  (monotone with instance-based step slack).
MP3 (Convergence, ●●): r_mp3(x)=x; R_mp3: y ∈ [-1.6, 1.6] (bounded within the
  arctan(±9) target range).
MP4 (Trajectory, ●): r_mp4(x)=1-x; R_mp4: |y_o + y_n| < 0.8 (loose odd symmetry).
MP5 (Asymptotic, ●●): r_mp5(x)=min(x+0.1,0.9); R_mp5: y_new >= y_orig - 0.15
  (asymptotic ordering at the input-domain endpoints).
"""
import math


def r_mp1(x) -> float:
    return 1.0 - float(x)


def R_mp1(y_orig, y_new) -> bool:
    y_o, y_n = float(y_orig), float(y_new)
    if not (math.isfinite(y_o) and math.isfinite(y_n)):
        return False
    return abs(y_o + y_n) < 0.5


def r_mp2(x) -> float:
    return min(float(x) + 0.1, 0.9)


def R_mp2(y_orig, y_new) -> bool:
    return float(y_new) >= float(y_orig) - 0.15


def r_mp3(x) -> float:
    return float(x)


def R_mp3(y_orig, y_new) -> bool:
    y = float(y_orig)
    return math.isfinite(y) and -1.6 <= y <= 1.6


def r_mp4(x) -> float:
    return 1.0 - float(x)


def R_mp4(y_orig, y_new) -> bool:
    y_o, y_n = float(y_orig), float(y_new)
    if not (math.isfinite(y_o) and math.isfinite(y_n)):
        return False
    return abs(y_o + y_n) < 0.8


def r_mp5(x) -> float:
    return min(float(x) + 0.1, 0.9)


def R_mp5(y_orig, y_new) -> bool:
    return float(y_new) >= float(y_orig) - 0.15


def r_trivial(x) -> float:
    return float(x)


def R_trivial(y_orig, y_new) -> bool:
    return True
