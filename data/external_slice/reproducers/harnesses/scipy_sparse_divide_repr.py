"""
F-SCIPY-001 verification: scipy.sparse elementwise true-divide returns nan
where the numerator has an implicit (unstored) zero (issue #6401; fixed by
PR #6405, first released in scipy 0.18.1... release notes list it among the
0.18.x fixes; backport noted in the PR discussion).

issue oracle (m_conv / f_conv.repr, representation invariance): the SAME logical
numerator matrix A (zero at every entry), represented either
  (i)  canonically -- the zero at (0,0) is implicit (not stored), or
  (ii) with the zero at (0,0) stored explicitly,
divided by the same B must yield IDENTICAL results, which must also match the
dense reference (0/1 == 0).

Run unchanged inside a real scipy 0.17.1 site (buggy) and a real scipy 0.18.1
site (fixed). Python 3.5-compatible syntax (no f-strings).
"""
import sys
import numpy as np
import scipy
import scipy.sparse as sp

print("python %s | scipy %s | numpy %s" % (sys.version.split()[0], scipy.__version__, np.__version__))

# B: stored 1.0 at (0,0)
B = sp.csr_matrix((1, 1))
B[0, 0] = 1.0

# (i) implicit-zero numerator (canonical empty pattern)
A_impl = sp.csr_matrix((1, 1))

# (ii) explicit-zero numerator (same logical matrix, zero stored at (0,0))
A_expl = sp.csr_matrix((np.array([0.0]), (np.array([0]), np.array([0]))), shape=(1, 1))
assert A_expl.nnz == 1  # the zero is genuinely stored

dense_ref = np.zeros((1, 1)) / np.ones((1, 1))  # = [[0.]]

r_impl = np.asarray((A_impl / B))
r_expl = np.asarray((A_expl / B))

print("dense reference        A/B =", dense_ref.ravel().tolist())
print("implicit-zero A (nnz=0) /B =", r_impl.ravel().tolist())
print("explicit-zero A (nnz=1) /B =", r_expl.ravel().tolist())

def arrays_identical(x, y):
    # elementwise identical, treating nan==nan as True (numpy-1.11-compatible)
    x, y = np.asarray(x), np.asarray(y)
    if x.shape != y.shape:
        return False
    both_nan = np.isnan(x) & np.isnan(y)
    return bool(np.all(both_nan | (x == y)))

same_repr = arrays_identical(r_impl, r_expl)
match_dense_impl = arrays_identical(r_impl, dense_ref)
match_dense_expl = arrays_identical(r_expl, dense_ref)

print("representations agree:            %s" % same_repr)
print("implicit repr matches dense ref:  %s" % match_dense_impl)
print("explicit repr matches dense ref:  %s" % match_dense_expl)

if same_repr and match_dense_impl and match_dense_expl:
    print("=> issue-property SATISFIED on scipy %s" % scipy.__version__)
else:
    print("=> issue-property VIOLATION on scipy %s (representation-dependent / wrong division result)" % scipy.__version__)
import sys as _sys
_sys.exit(0 if (same_repr and match_dense_impl and match_dense_expl) else 1)
