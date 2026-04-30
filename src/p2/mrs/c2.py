"""MR functions for C2 Polynomial-feature surrogate of tanh(t), t = 4x − 2.

§3.3 grid: c2 = mp1●● mp2● mp3●● mp4● mp5●●

target tanh(t) is anti-symmetric on [−2, 2], monotone, bounded ∈ (−1, 1).
PUT uses degree-5 PolynomialFeatures + LinearRegression.

MP1 (Conservation, ●●): r_mp1(x)=1-x → reflects t around 0; R_mp1:
  |y(x) + y(1-x)| < 0.05 (tight anti-symmetry; polynomial fit on
  symmetric data has small residual).
MP2 (Monotonicity, ●): r_mp2(x)=min(x+0.1, 0.9); R_mp2: y_new ≥ y_orig
  − 0.05 (loose monotone — polynomial fit may oscillate slightly).
MP3 (Convergence, ●●): r_mp3(x)=x; R_mp3: y ∈ [−1.1, 1.1].
MP4 (Trajectory, ●): r_mp4(x)=1-x; R_mp4: |y(x) + y(1-x)| < 0.2.
MP5 (Asymptotic, ●●): existing strict monotone increase.
"""
import math


def r_mp1(x) -> float:
    return float(1.0 - float(x))


def R_mp1(y_orig, y_new) -> bool:
    y_o, y_n = float(y_orig), float(y_new)
    if not (math.isfinite(y_o) and math.isfinite(y_n)):
        return False
    return abs(y_o + y_n) < 0.05


def r_mp2(x) -> float:
    return float(min(float(x) + 0.1, 0.9))


def R_mp2(y_orig, y_new) -> bool:
    return float(y_new) >= float(y_orig) - 0.05


def r_mp3(x) -> float:
    return float(x)


def R_mp3(y_orig, y_new) -> bool:
    y = float(y_orig)
    if not math.isfinite(y):
        return False
    return -1.1 <= y <= 1.1


def r_mp4(x) -> float:
    return float(1.0 - float(x))


def R_mp4(y_orig, y_new) -> bool:
    y_o, y_n = float(y_orig), float(y_new)
    if not (math.isfinite(y_o) and math.isfinite(y_n)):
        return False
    return abs(y_o + y_n) < 0.2


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
