"""MR functions for B1 Beta-Binomial conjugate.

§3.3 grid: b1 = mp1●● mp2● mp3○ mp4○ mp5●

PUT: posterior_mean(x) = (1+round(100x)) / 102, monotone in x.

MP1 (Conservation, ●●): r_mp1(x)=1-x; R_mp1: |y_o + y_n − 1| < 1e-3
  (probability complement: posterior(x) + posterior(1-x) = 1 exactly).
MP2 (Monotonicity, ●): existing — small x increment → posterior increases.
MP3 (Convergence, ○): no externally tunable refinement; ○ baseline.
MP4 (Trajectory, ○): scalar in/out, no trajectory; ○ baseline.
MP5 (Asymptotic, ●): r_mp5(x)=x; R_mp5: y ∈ [1/102, 101/102] (bounded
  posterior over the input domain).
"""
import math


def r_mp1(x) -> float:
    return float(1.0 - float(x))


def R_mp1(y_orig, y_new) -> bool:
    y_o, y_n = float(y_orig), float(y_new)
    if not (math.isfinite(y_o) and math.isfinite(y_n)):
        return False
    return abs(y_o + y_n - 1.0) < 1e-3


def r_mp2(x) -> float:
    return float(min(float(x) + 0.01, 0.99))


def R_mp2(y_orig, y_new) -> bool:
    return float(y_new) > float(y_orig)


def r_mp3(x) -> float:
    return float(x)


def R_mp3(y_orig, y_new) -> bool:
    return False


def r_mp4(x) -> float:
    return float(x)


def R_mp4(y_orig, y_new) -> bool:
    return False


def r_mp5(x) -> float:
    return float(x)


def R_mp5(y_orig, y_new) -> bool:
    y = float(y_orig)
    if not math.isfinite(y):
        return False
    return 1.0 / 102.0 - 1e-6 <= y <= 101.0 / 102.0 + 1e-6


def r_trivial(x) -> float:
    return float(x)


def R_trivial(y_orig, y_new) -> bool:
    return True
