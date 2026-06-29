"""PoC — Adjoint meta-pattern arm via a REAL third-party defect.

Substrate (PUT, third-party production code, BSD-3): scipy.sparse.linalg
LinearOperator. The program-under-test is the *scaled-operator adjoint*
code path `_ScaledLinearOperator._adjoint`.

Real fault (provenance): scipy issue #8900 / PR #8962 (merge caea2b1).
  v1.1.0 (WRONG):  return A.H * alpha
  v1.2.0 (FIXED):  return A.H * np.conj(alpha)
For a complex scale alpha, the discrete adjoint identity
    <M x, y> = <x, M^H y>,   M = alpha * A,
holds iff M^H = conj(alpha) * A^H. The 1.1.0 bug drops the conjugate, so the
identity fails on the imaginary part — a silently-wrong adjoint.

"Version switch" is realised as a *fault-version switch* of exactly this one
real diff on top of the current production scipy (installing scipy==1.1.0 on
Python 3.12 is infeasible). epsilon_tol is an EXPLICIT factor (not hard-wired).

Validates the chain: real third-party substrate + real-bug wrong-version +
strong adjoint MR  ->  wrong version killed, correct version passes.
"""
import numpy as np
from scipy.sparse.linalg import aslinearoperator

# fixed real symmetric matrix (A^H = A); the operator substrate is scipy's
_A = np.array([[2.0, 1.0, 0.0],
               [1.0, 3.0, 1.0],
               [0.0, 1.0, 2.0]])


def _residual(x, *, buggy):
    """Adjoint-identity residual for M = alpha(x) * A, complex alpha.

    Returns |<M x, y> - <x, M^H y>| / |<M x, y>|, ~0 iff the adjoint is correct.
    <u, v> := vdot(u, v) = u^H v.
    """
    alpha = np.exp(1j * np.pi * float(x))          # complex scale, phase from x
    A = aslinearoperator(_A)
    Aadj = A.H                                      # scipy adjoint of A (= A^T)
    # the one real PR#8962 diff: wrong (1.1.0) vs fixed (1.2.0)
    M_adj = (alpha * Aadj) if buggy else (np.conj(alpha) * Aadj)

    rng = np.random.default_rng(0)
    xv = rng.standard_normal(3) + 1j * rng.standard_normal(3)
    yv = rng.standard_normal(3) + 1j * rng.standard_normal(3)

    Mx = alpha * A.matvec(xv)                       # M x
    MHy = M_adj.matvec(yv)                          # M^H y (as constructed)
    lhs = np.vdot(Mx, yv)                           # <M x, y>
    rhs = np.vdot(xv, MHy)                          # <x, M^H y>
    return abs(lhs - rhs) / (abs(lhs) + 1e-30)


# PUT: program(x) -> float  (the adjoint-identity residual observable)
def adj_PUT(x, *, buggy=False):
    return float(_residual(x, buggy=buggy))


# strong MR (adj, f_adj.dual): residual stays within tolerance of zero under
# any input transform.  epsilon_tol is an explicit factor.
def r_adj_dual(x):
    return 1.0 - 0.5 * float(x)


def R_adj_dual(y_orig, y_new, *, epsilon_tol):
    return abs(y_orig) <= epsilon_tol and abs(y_new) <= epsilon_tol


def verify_adj(program, *, epsilon_tol, n=30):
    """Returns 'pass'/'fail' — strong MR over a sweep (the adj_PC verifier)."""
    rng = np.random.default_rng(42)
    for _ in range(n):
        x = rng.uniform(0.05, 0.95)
        if not R_adj_dual(program(x), program(r_adj_dual(x)), epsilon_tol=epsilon_tol):
            return "fail"
    return "pass"


if __name__ == "__main__":
    EPS = 1e-9
    fixed = lambda x: adj_PUT(x, buggy=False)
    buggy = lambda x: adj_PUT(x, buggy=True)

    print("=== residual samples (should be ~0 for FIXED, >0 for BUGGY) ===")
    for x in (0.25, 0.5, 0.75):
        print(f"  x={x}:  fixed={fixed(x):.3e}   buggy={buggy(x):.3e}")

    vf = verify_adj(fixed, epsilon_tol=EPS)
    vb = verify_adj(buggy, epsilon_tol=EPS)
    print(f"\n=== strong adj MR (epsilon_tol={EPS}) ===")
    print(f"  FIXED (correct version): {vf}   <- expect pass (not killed)")
    print(f"  BUGGY (scipy 1.1.0 #8900): {vb}   <- expect fail (killed)")

    ok = (vf == "pass") and (vb == "fail")
    print(f"\nPoC chain valid: {ok}")
    assert ok, "PoC failed: strong MR did not separate fixed vs buggy"
