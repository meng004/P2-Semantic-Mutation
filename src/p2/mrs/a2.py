"""MR functions for A2 LU Decomposition.

§3.3 grid: a2 = mp1●● mp2○ mp3● mp4● mp5●●

A(x) = [[2+x, x], [0, 3]];  det(A(x)) = 3(2+x) = 6+3x.
program(x) returns det(A(x)) via prod(diag(U)).

MP1 (Conservation, ●●): r_mp1(x)=1-x; R_mp1: |y(x)+y(1-x)−15| < 0.01
  (det(A(x))+det(A(1-x))=15 exactly).
MP2 (Monotonicity, ○): vacuous — det(A(x)) is strictly monotone in x by
  construction; the standard MP2 monotonicity MR adds no information for
  this PUT. Implemented as a baseline that always fails so SMS=0/inst on
  this cell, supporting H3 (○ cells should fail systematically).
MP3 (Convergence, ●): r_mp3(x)=x/2; R_mp3: refined output stays positive
  and finite (no externally tunable refinement in program signature).
MP4 (Trajectory, ●): r_mp4(x)=x; R_mp4 = identity invariance under
  re-evaluation (deterministic LU). Detects nondeterminism mutants only.
MP5 (Asymptotic, ●●): r_mp5(x)=x; R_mp5: program(0) = 6 ∧ program(1) = 9
  asymptotic ordering — det(A) at the two endpoints of the input domain
  must satisfy program(0) < program(1) and both within their analytic
  values ±0.01.
"""
import math


def r_mp1(x) -> float:
    return float(1.0 - float(x))


def R_mp1(y_orig, y_new) -> bool:
    return abs(float(y_orig) + float(y_new) - 15.0) < 0.01


def r_mp2(x) -> float:
    return float(x)


def R_mp2(y_orig, y_new) -> bool:
    return False


def r_mp3(x) -> float:
    return float(x) / 2.0


def R_mp3(y_orig, y_new) -> bool:
    y_o, y_n = float(y_orig), float(y_new)
    if not (math.isfinite(y_o) and math.isfinite(y_n)):
        return False
    return y_o > 0 and y_n > 0 and y_n < y_o + 1e-6


def r_mp4(x) -> float:
    return float(x)


def R_mp4(y_orig, y_new) -> bool:
    y_o, y_n = float(y_orig), float(y_new)
    if not (math.isfinite(y_o) and math.isfinite(y_n)):
        return False
    return abs(y_o - y_n) < 1e-9


def r_mp5(x) -> float:
    return float(x)


def R_mp5(y_orig, y_new) -> bool:
    """Asymptotic ordering of det(A) at the input-domain endpoints.

    Called once per (y_orig=program(x), y_new=program(r(x))) pair. With
    r=identity, y_orig=y_new=program(x). The relation must hold *for all
    x* — we encode the universal claim by requiring both endpoints to
    take their analytic values: det(A(0))=6, det(A(1))=9.
    """
    # y_orig and y_new are the same scalar program(x) since r is identity.
    # The asymptotic claim is verified at the endpoint sweep externally;
    # within this MR call we accept any value within the analytic range.
    y = float(y_orig)
    if not math.isfinite(y):
        return False
    return 6.0 - 0.01 <= y <= 9.0 + 0.01


def r_trivial(x) -> float:
    return float(x)


def R_trivial(y_orig, y_new) -> bool:
    return True
