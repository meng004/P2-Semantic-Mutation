"""PILOT MR battery for XL program 'invsqrt' (pairs invsqrt.cpp; frozen aux:
u(x) = 4**(2x-1) in [0.25, 4]; float32 magic-constant + ONE Newton iteration).

Exact model: y*(x) = 1/sqrt(u(x)) = 2**(1-2x), y* in [0.5, 2]. The external
surrogate carries a documented worst-case relative error of ~0.175% (one
Newton refinement of the 0x5f3759df initial guess); all bands below hold at
>= 2.8x that worst case for the UNMUTATED pair (V2 certification headroom)
while staying far below the fault magnitudes the pilot operators inject.

Instantiable strata (frozen A1 registry): {1, 2, 4, 5}; primary MP5.

MP1 f_inv.con  (reciprocal identity): y(x) * y(1-x) = 1 exactly for the
    exact model (2**(1-2x) * 2**(2x-1) = 1); banded at 0.01 (surrogate
    product error <= ~0.35%).
MP2 f_mono.stat (monotone): y strictly DECREASING in x, so r steps x DOWN
    by 0.1 to keep the frozen Wilcoxon verifier's positive-diff orientation.
MP4 f_mono.shape: structural note — the frozen MP4 verifier
    (p2.avp.mp4_dtw) measures DTW distance between program(x) and
    program(r(x)) at epsilon 1e-6; a strictly monotone scalar kernel admits
    NO non-identity exact invariance, so r = identity is the only
    V2-certifiable choice and the cell cannot kill by construction
    (disclosed pilot finding; R below documents the intended convex-decay
    shape check for a future parameterised verifier).
MP5 f_conv.rate (PRIMARY; Mode-M relative oracle): the exact model fixes
    the scaling rate y*(x/2) / y*(x) = 2**x, and x is recoverable from the
    output itself (x = (1 - log2 y)/2, i.e. 2**x = sqrt(2/y)); R checks the
    surrogate reproduces the exact method's rate within a 2% band
    (unmutated pair: <= ~0.5% incl. inversion amplification; the
    skipped-Newton fault sits at ~3-8%).
"""
import math

_BAND_MP1 = 0.01
_SLACK_MP2 = 0.01
_BAND_MP5 = 0.02


def r_mp1(x) -> float:
    return float(1.0 - float(x))


def R_mp1(y_orig, y_new) -> bool:
    y_o, y_n = float(y_orig), float(y_new)
    if not (math.isfinite(y_o) and math.isfinite(y_n)):
        return False
    return abs(y_o * y_n - 1.0) < _BAND_MP1


def r_mp2(x) -> float:
    return float(max(float(x) - 0.1, 0.0))


def R_mp2(y_orig, y_new) -> bool:
    y_o, y_n = float(y_orig), float(y_new)
    if not (math.isfinite(y_o) and math.isfinite(y_n)):
        return False
    return y_n >= y_o - _SLACK_MP2


def r_mp4(x) -> float:
    # identity: the only exact invariance of a strictly monotone scalar
    # kernel under the frozen DTW verifier (see module docstring).
    return float(x)


def R_mp4(y_orig, y_new) -> bool:
    # documented convex-decay shape intent: outputs finite and inside the
    # exact model's envelope [0.5, 2] with surrogate slack.
    y_o, y_n = float(y_orig), float(y_new)
    if not (math.isfinite(y_o) and math.isfinite(y_n)):
        return False
    return 0.45 <= y_o <= 2.1 and 0.45 <= y_n <= 2.1


def r_mp5(x) -> float:
    return float(x) / 2.0


def R_mp5(y_orig, y_new) -> bool:
    """Mode-M relative oracle: y_new/y_orig must match the EXACT method's
    rate 2**x, with 2**x recovered from y_orig via the exact model."""
    y_o, y_n = float(y_orig), float(y_new)
    if not (math.isfinite(y_o) and math.isfinite(y_n)) or y_o <= 0.0:
        return False
    rate_exact = math.sqrt(2.0 / y_o)
    return abs((y_n / y_o) / rate_exact - 1.0) <= _BAND_MP5
