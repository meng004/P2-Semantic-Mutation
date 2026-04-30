"""MR functions for C3 NN surrogate of sigmoid(2t), t = 6x − 3.

§3.3 grid: c3 = mp1● mp2●● mp3●● mp4●● mp5●●

target sigmoid(2t) on [−3, 3], monotone increasing, bounded ∈ (0, 1).
sigmoid(t) + sigmoid(−t) = 1 (probability complement).

MP1 (Conservation, ●): r_mp1(x)=1-x → reflects t around 0; R_mp1:
  |y(x) + y(1-x) − 1| < 0.1 (probability complement; NN fit noise).
MP2 (Monotonicity, ●●): r_mp2(x)=min(x+0.1, 0.9); R_mp2: y_new ≥ y_orig
  − 0.02.
MP3 (Convergence, ●●): r_mp3(x)=x; R_mp3: y ∈ [−0.05, 1.05].
MP4 (Trajectory, ●●): r_mp4(x)=1-x; R_mp4: |y(x) + y(1-x) − 1| < 0.15
  (tight probability-complement under reflected input).
MP5 (Asymptotic, ●●): existing strict monotone increase.
"""
import math


def r_mp1(x) -> float:
    return float(1.0 - float(x))


def R_mp1(y_orig, y_new) -> bool:
    y_o, y_n = float(y_orig), float(y_new)
    if not (math.isfinite(y_o) and math.isfinite(y_n)):
        return False
    return abs((y_o + y_n) - 1.0) < 0.1


def r_mp2(x) -> float:
    return float(min(float(x) + 0.1, 0.9))


def R_mp2(y_orig, y_new) -> bool:
    return float(y_new) >= float(y_orig) - 0.02


def r_mp3(x) -> float:
    return float(x)


def R_mp3(y_orig, y_new) -> bool:
    y = float(y_orig)
    if not math.isfinite(y):
        return False
    return -0.05 <= y <= 1.05


def r_mp4(x) -> float:
    return float(1.0 - float(x))


def R_mp4(y_orig, y_new) -> bool:
    y_o, y_n = float(y_orig), float(y_new)
    if not (math.isfinite(y_o) and math.isfinite(y_n)):
        return False
    return abs((y_o + y_n) - 1.0) < 0.15


def r_mp5(x) -> float:
    return min(float(x) + 0.1, 0.9)


def R_mp5(y_orig, y_new) -> bool:
    """Monotone direction with 0.05 saturation slack (r(x)=min(x+0.1,0.9)
    saturates at x ≥ 0.8, where y_new ≤ y_orig; the slack absorbs that."""
    return float(y_new) >= float(y_orig) - 0.05


def r_trivial(x) -> float:
    return float(x)


def R_trivial(y_orig, y_new) -> bool:
    return True
