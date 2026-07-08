"""MR functions for B5 rejection sampling, E[·]≈μ(x)=4x-2 on [-3,3].

§3.3 grid: b5 = mp1○ mp2●● mp3● mp4○ mp5●

MP1 (Conservation, ○): no complement invariance for the truncated mean; ○.
MP2 (Monotonicity, ●●): r_mp2(x)=min(x+0.1,0.9); R_mp2: y_new >= y_orig - 0.1
  (accepted-sample mean tracks the target mean; slack absorbs acceptance noise).
MP3 (Convergence, ●): r_mp3(x)=x; R_mp3: y ∈ [-3.05, 3.05] (truncation support).
MP4 (Trajectory, ○): scalar estimator, no trajectory; ○ baseline.
MP5 (Asymptotic, ●): r_mp5(x)=min(x+0.1,0.9); R_mp5: y_new >= y_orig - 0.1
  (asymptotic ordering at the input-domain endpoints).
"""
import math


def r_mp1(x) -> float:
    return float(x)


def R_mp1(y_orig, y_new) -> bool:
    return False


def r_mp2(x) -> float:
    return min(float(x) + 0.1, 0.9)


def R_mp2(y_orig, y_new) -> bool:
    return float(y_new) >= float(y_orig) - 0.1


def r_mp3(x) -> float:
    return float(x)


def R_mp3(y_orig, y_new) -> bool:
    y = float(y_orig)
    return math.isfinite(y) and -3.05 <= y <= 3.05


def r_mp4(x) -> float:
    return float(x)


def R_mp4(y_orig, y_new) -> bool:
    return False


def r_mp5(x) -> float:
    return min(float(x) + 0.1, 0.9)


def R_mp5(y_orig, y_new) -> bool:
    return float(y_new) >= float(y_orig) - 0.1


def r_trivial(x) -> float:
    return float(x)


def R_trivial(y_orig, y_new) -> bool:
    return True
