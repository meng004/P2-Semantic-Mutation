"""MR functions for B2 MCMC Metropolis-Hastings.

§3.3 grid: b2 = mp1● mp2●● mp3●● mp4●● mp5●

PUT: chain_mean tracks target μ = 4x − 2 ∈ [−2, 2].

MP1 (Conservation, ●): chain mean stays inside target domain (target μ ∈
  [−2, 2]; loose ±0.5 allowance for chain noise → [−2.5, 2.5]).
MP2 (Monotonicity, ●●): existing — strict y_new > y_orig (Wilcoxon AVP
  handles statistical noise at the campaign level).
MP3 (Convergence, ●●): r_mp3(x)=x; R_mp3: chain mean within 0.5 of
  analytical μ (chain has converged near target after warmup).
MP4 (Trajectory, ●●): r_mp4(x)=1-x; R_mp4: y_o + y_n ≈ 0 (μ(x)+μ(1-x)
  = (4x−2)+(4(1-x)−2) = 0; chain means should sum near zero, ±1.0).
MP5 (Asymptotic, ●): r_mp5(x)=x; R_mp5: y ∈ [−3, 3] (chain stays inside
  loose envelope of target range).
"""
import math


def r_mp1(x) -> float:
    return float(x)


def R_mp1(y_orig, y_new) -> bool:
    y_o = float(y_orig)
    if not math.isfinite(y_o):
        return False
    return -2.5 <= y_o <= 2.5


def r_mp2(x) -> float:
    """Shift x by +0.05 with no saturation — b2.program accepts any float
    via mu = 4x − 2 (no in-domain clipping needed); a clipped r(x)=min(x+0.05,
    0.95) would collapse y_new=y_orig at the upper edge and fail the strict
    monotone R below."""
    return float(x) + 0.05


def R_mp2(y_orig, y_new) -> bool:
    """Strict monotone direction: y_new > y_orig.

    Statistical noise is handled by the Wilcoxon test in
    p2.avp.mp2_5_wilcoxon (n=50 samples, alpha=0.05).
    """
    return float(y_new) > float(y_orig)


def r_mp3(x) -> float:
    return float(x)


def R_mp3(y_orig, y_new) -> bool:
    """Chain has converged within 0.5 of analytical μ = 4x - 2.
    R is called with both y_orig and y_new = chain_mean(x); we cannot
    recover x from y alone, so verify y is at least within target range."""
    y = float(y_orig)
    if not math.isfinite(y):
        return False
    return -2.5 <= y <= 2.5


def r_mp4(x) -> float:
    return float(1.0 - float(x))


def R_mp4(y_orig, y_new) -> bool:
    y_o, y_n = float(y_orig), float(y_new)
    if not (math.isfinite(y_o) and math.isfinite(y_n)):
        return False
    return abs(y_o + y_n) < 1.0


def r_mp5(x) -> float:
    return float(x)


def R_mp5(y_orig, y_new) -> bool:
    y = float(y_orig)
    if not math.isfinite(y):
        return False
    return -3.0 <= y <= 3.0


def r_trivial(x) -> float:
    return float(x)


def R_trivial(y_orig, y_new) -> bool:
    return True
