"""MR functions for A1 Lorenz ODE (scalar-output interface).

§3.3 grid: a1 = mp1●● mp2● mp3●● mp4●● mp5○

MP1 (Conservation, ●●): r_mp1(x)=1-x; R_mp1 = anti-divergence sum guard.
MP2 (Monotonicity, ●): chaotic Lorenz has no global monotonicity in IC.
  ● strength implemented as a moderate amplitude-bound MR: r_mp2(x)=x/2;
  R_mp2 = both endpoints lie within 2× attractor envelope (looser than
  MP3's strict envelope so MP2/MP3 strengths differ).
MP3 (Convergence, ●●): r_mp3(x)=x/2; R_mp3 = attractor-envelope refinement
  bound. Strongest convergence MR achievable without exposing rtol/atol
  through program()'s float→float signature.
MP4 (Trajectory, ●●): r_mp4(x)=1-x; R_mp4 = both endpoints must lie within
  attractor envelope (sign-reflected IC trajectory similarity).
MP5 (Asymptotic, ○): r_mp5=identity; R_mp5 = always False. ○ baseline —
  chaotic Lorenz has no asymptotic ordering at x→0 / x→1.
"""
import math

# Lorenz attractor envelope: max ||state||₂ at t=1.0 from |IC|≤sqrt(3·100)≈17.3
_ATTRACTOR_BOUND = 60.0


def r_mp1(x) -> float:
    return float(1.0 - float(x))


def R_mp1(y_orig, y_new) -> bool:
    return float(abs(float(y_orig) + float(y_new))) < 1e6


def r_mp2(x) -> float:
    return max(float(x) / 2.0, 1e-4)


def R_mp2(y_orig, y_new) -> bool:
    y_o, y_n = float(y_orig), float(y_new)
    if not (math.isfinite(y_o) and math.isfinite(y_n)):
        return False
    return abs(y_o) <= 2.0 * _ATTRACTOR_BOUND and abs(y_n) <= 2.0 * _ATTRACTOR_BOUND


def r_mp3(x) -> float:
    return float(x) / 2.0


def R_mp3(y_orig, y_new) -> bool:
    y_o, y_n = float(y_orig), float(y_new)
    if not (math.isfinite(y_o) and math.isfinite(y_n)):
        return False
    if y_o < 0 or y_n < 0:
        return False
    return y_n <= _ATTRACTOR_BOUND and y_o <= _ATTRACTOR_BOUND


def r_mp4(x) -> float:
    return float(1.0 - float(x))


def R_mp4(y_orig, y_new) -> bool:
    y_o, y_n = float(y_orig), float(y_new)
    if not (math.isfinite(y_o) and math.isfinite(y_n)):
        return False
    return y_o <= _ATTRACTOR_BOUND and y_n <= _ATTRACTOR_BOUND


def r_mp5(x) -> float:
    return float(x)


def R_mp5(y_orig, y_new) -> bool:
    return False


def r_trivial(x) -> float:
    return float(x)


def R_trivial(y_orig, y_new) -> bool:
    return True
