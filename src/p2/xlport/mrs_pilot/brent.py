"""PILOT MR battery for XL program 'brent' (pairs brent.c, brent.java;
frozen aux: root of f(t) = t^3 + t - c, c(x) = 4x - 2, bracket [-2, 2],
stop |droot| <= ~1e-12).

Exact model: y*(x) = the unique real root of t^3 + t = 4x - 2 (strictly
increasing, odd around x = 0.5, y* in [-1, 1], converged to ~1e-12 by both
sides' stopping rules; combined certification band ~4e-12).

Instantiable strata (frozen A1 registry): {1, 2, 3, 4}; primary MP3.

MP1 f_inv.con  (odd-root identity): c(1-x) = -c(x) and t^3+t is odd, so
    y(x) + y(1-x) = 0 exactly; banded at 1e-6 (>= 5 orders above the
    converged residual, >= 3 orders below the loose-tolerance fault).
MP2 f_mono.stat (monotone): y strictly increasing in x; r steps x UP by
    0.1 (positive-diff orientation of the frozen Wilcoxon verifier).
MP3 f_conv.lim (PRIMARY): structural note — the frozen MP3 verifier
    (p2.avp.mp3_convergence) ignores r/R and probes program(h) on the fixed
    grid h in {0.1, 0.05, 0.025, 0.0125} against reference_value 1.0 at
    expected order 2.0. A root-finder parameterised by x (not by a mesh
    width h with limit 1.0) FAILS that check on the UNMUTATED pair, so the
    primary cell cannot kill under the frozen dispatcher (disclosed pilot
    finding; R below documents the intended converged-root bound for a
    future parameterised verifier).
MP4 f_mono.shape: same structural DTW note as invsqrt (strictly monotone
    scalar kernel -> identity r is the only V2-certifiable choice).
"""
import math

_BAND_MP1 = 1e-6
_SLACK_MP2 = 1e-9
_ROOT_BOUND = 1.0 + 1e-9


def r_mp1(x) -> float:
    return float(1.0 - float(x))


def R_mp1(y_orig, y_new) -> bool:
    y_o, y_n = float(y_orig), float(y_new)
    if not (math.isfinite(y_o) and math.isfinite(y_n)):
        return False
    return abs(y_o + y_n) < _BAND_MP1


def r_mp2(x) -> float:
    return float(min(float(x) + 0.1, 1.0))


def R_mp2(y_orig, y_new) -> bool:
    y_o, y_n = float(y_orig), float(y_new)
    if not (math.isfinite(y_o) and math.isfinite(y_n)):
        return False
    return y_n >= y_o - _SLACK_MP2


def r_mp3(x) -> float:
    return float(x)


def R_mp3(y_orig, y_new) -> bool:
    # documented convergence intent: converged root stays in the exact
    # model's bound |y| <= 1 (c in [-2, 2]) with converged-residual slack.
    y = float(y_orig)
    if not math.isfinite(y):
        return False
    return -_ROOT_BOUND <= y <= _ROOT_BOUND


def r_mp4(x) -> float:
    # identity (see module docstring: frozen DTW verifier constraint).
    return float(x)


def R_mp4(y_orig, y_new) -> bool:
    y_o, y_n = float(y_orig), float(y_new)
    if not (math.isfinite(y_o) and math.isfinite(y_n)):
        return False
    return abs(y_o) <= _ROOT_BOUND and abs(y_n) <= _ROOT_BOUND
