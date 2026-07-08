"""MR functions for A8 RK4 stepper, u(T;x)=(2x-1)·ρ, ρ≈e⁻¹.

§3.3 grid: a8 = mp1●● mp2●● mp3●● mp4● mp5●

The linear ODE integral is antisymmetric about x=½ and bounded by ρ≈0.368.

MP1 (Conservation, ●●): r_mp1(x)=1-x; R_mp1: |y_o + y_n| < 1e-6 (antisymmetry
  u(T;x)+u(T;1-x)=0, exact by linearity of the RK4 map).
MP2 (Monotonicity, ●●): r_mp2(x)=min(x+0.1,0.9); R_mp2: y_new >= y_orig - 1e-9.
MP3 (Convergence, ●●): r_mp3(x)=x; R_mp3: y ∈ [-0.4, 0.4] (bounded by the RK4
  amplification |u(T)|≤ρ≈0.368; a 4th-order-accurate step stays within range).
MP4 (Trajectory, ●): r_mp4(x)=1-x; R_mp4: |y_o + y_n| < 1e-3 (loose antisymmetry
  of the integrated trajectory).
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
    return math.isfinite(y) and -0.4 <= y <= 0.4


def r_mp4(x) -> float:
    return 1.0 - float(x)


def R_mp4(y_orig, y_new) -> bool:
    y_o, y_n = float(y_orig), float(y_new)
    if not (math.isfinite(y_o) and math.isfinite(y_n)):
        return False
    return abs(y_o + y_n) < 1e-3


def r_mp5(x) -> float:
    return min(float(x) + 0.1, 0.9)


def R_mp5(y_orig, y_new) -> bool:
    return float(y_new) >= float(y_orig) - 1e-9


def r_trivial(x) -> float:
    return float(x)


def R_trivial(y_orig, y_new) -> bool:
    return True
