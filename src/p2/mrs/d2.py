"""MR functions for D2 RBF SVM Classifier (P(y=1|x), feature [2-2x, 0]).

§3.3 grid: d2 = mp1● mp2●● mp3● mp4○ mp5●●

PUT outputs P(y=1) ∈ [0,1], monotone increasing in x as feature moves
toward circle center.

MP1 (Conservation, ●): r_mp1(x)=x; R_mp1: y ∈ [-0.01, 1.01] (probability
  validity, loose — SVC predict_proba may slightly exceed bounds).
MP2 (Monotonicity, ●●): existing.
MP3 (Convergence, ●): r_mp3(x)=x; R_mp3: idempotency under re-evaluation.
MP4 (Trajectory, ○): scalar in/out; ○ baseline — always fails.
MP5 (Asymptotic, ●●): r_mp5(x)=min(x+0.1, 0.9); R_mp5: y_new ≥ y_orig
  − 0.05.
"""
import math


def r_mp1(x) -> float:
    return float(x)


def R_mp1(y_orig, y_new) -> bool:
    y = float(y_orig)
    if not math.isfinite(y):
        return False
    return -0.01 <= y <= 1.01


def r_mp2(x) -> float:
    return min(float(x) + 0.1, 0.9)


def R_mp2(y_orig, y_new) -> bool:
    return float(y_new) > float(y_orig) - 0.05


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
    return False


def r_mp5(x) -> float:
    return min(float(x) + 0.1, 0.9)


def R_mp5(y_orig, y_new) -> bool:
    return float(y_new) > float(y_orig) - 0.05


def r_trivial(x) -> float:
    return float(x)


def R_trivial(y_orig, y_new) -> bool:
    return True
