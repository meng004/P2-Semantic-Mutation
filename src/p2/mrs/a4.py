"""MR functions for A4 Gauss-Legendre quadrature I(x)=2x+1/3.

§3.3 grid: a4 = mp1●● mp2● mp3●● mp4○ mp5●

MP1 (Conservation, ●●): r_mp1(x)=1-x; R_mp1: |y_o + y_n - 8/3| < 1e-6
  (exact additive conservation of the quadrature over the reflected domain).
MP2 (Monotonicity, ●): r_mp2(x)=min(x+0.1,0.9); R_mp2: y_new >= y_orig - 1e-9.
MP3 (Convergence, ●●): r_mp3(x)=x; R_mp3: y ∈ [1/3, 7/3] (bounded to the exact
  analytic image; 16-node Gauss-Legendre is exact for this degree-2 integrand).
MP4 (Trajectory, ○): scalar in/out, no trajectory; ○ baseline.
MP5 (Asymptotic, ●): r_mp5(x)=min(x+0.1,0.9); R_mp5: y_new >= y_orig - 1e-9
  (asymptotic ordering at the input-domain endpoints).
"""
import math

_CONS = 8.0 / 3.0


def r_mp1(x) -> float:
    return 1.0 - float(x)


def R_mp1(y_orig, y_new) -> bool:
    y_o, y_n = float(y_orig), float(y_new)
    if not (math.isfinite(y_o) and math.isfinite(y_n)):
        return False
    return abs(y_o + y_n - _CONS) < 1e-6


def r_mp2(x) -> float:
    return min(float(x) + 0.1, 0.9)


def R_mp2(y_orig, y_new) -> bool:
    return float(y_new) >= float(y_orig) - 1e-9


def r_mp3(x) -> float:
    return float(x)


def R_mp3(y_orig, y_new) -> bool:
    y = float(y_orig)
    return math.isfinite(y) and (1.0 / 3.0 - 1e-9) <= y <= (7.0 / 3.0 + 1e-9)


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
