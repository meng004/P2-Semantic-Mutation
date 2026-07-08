"""MR functions for D4 Gaussian Naive Bayes (P(y=1|x), feature [2x-1, 2x-1]).

§3.3 grid: d4 = mp1●● mp2●● mp3● mp4● mp5●●

PUT outputs P(y=1) ∈ [0,1], monotone increasing in x.

MP1 (Conservation, ●●): r_mp1(x)=x; R_mp1: y ∈ [0, 1] strict (probability
  validity — catches NaN, negative, > 1).
MP2 (Monotonicity, ●●): r_mp2(x)=min(x+0.1,0.9); R_mp2: y_new >= y_orig - 0.05.
MP3 (Convergence, ●): r_mp3(x)=x; R_mp3: |y_orig - y_new| < 1e-9 under identity
  transform (deterministic re-evaluation idempotency).
MP4 (Trajectory, ●): r_mp4(x)=x; R_mp4: y ∈ [-0.01, 1.01] (probability validity,
  weak differentiation layer).
MP5 (Asymptotic, ●●): r_mp5(x)=min(x+0.1,0.9); R_mp5: y_new >= y_orig - 0.05
  (asymptotic ordering at the input-domain endpoints).
"""
import math


def r_mp1(x) -> float:
    return float(x)


def R_mp1(y_orig, y_new) -> bool:
    y = float(y_orig)
    if not math.isfinite(y):
        return False
    return 0.0 <= y <= 1.0


def r_mp2(x) -> float:
    return min(float(x) + 0.1, 0.9)


def R_mp2(y_orig, y_new) -> bool:
    return float(y_new) >= float(y_orig) - 0.05


def r_mp3(x) -> float:
    return float(x)


def R_mp3(y_orig, y_new) -> bool:
    y_o, y_n = float(y_orig), float(y_new)
    if not (math.isfinite(y_o) and math.isfinite(y_n)):
        return False
    return abs(y_o - y_n) < 1e-9


def r_mp4(x) -> float:
    return float(x)


def R_mp4(y_orig, y_new) -> bool:
    y = float(y_orig)
    if not math.isfinite(y):
        return False
    return -0.01 <= y <= 1.01


def r_mp5(x) -> float:
    return min(float(x) + 0.1, 0.9)


def R_mp5(y_orig, y_new) -> bool:
    return float(y_new) >= float(y_orig) - 0.05


def r_trivial(x) -> float:
    return float(x)


def R_trivial(y_orig, y_new) -> bool:
    return True
