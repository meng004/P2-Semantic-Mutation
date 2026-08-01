/*
 * E-PETSC-001 verification: MatCreateSchurComplementPmat produces wrong Pmat
 * when A01 is a virtual (Mat[Hermitian]Transpose) matrix (PETSc issue #1618;
 * regression a1f5644 shipped in v3.21.0; fixed by issue-property !7700 / commit b07ab1d,
 * released v3.21.4+).
 *
 * issue oracle (m_adj/f_adj.dual): for a REAL matrix, the virtual transpose
 * representation MatCreateTranspose(M10T) with M10T = A01^T denotes exactly
 * the same mathematical transform A01 as the explicitly assembled matrix
 * (and, for real scalars, MatCreateHermitianTranspose likewise). Hence
 * MatCreateSchurComplementPmat(A00, A01, A10, A11, AINV_DIAG, ...) must
 * return the same Pmat = A11 - A10 diag(A00)^{-1} A01 whichever
 * representation of A01 is passed. Cross-checked against the hand-computed
 * analytic Pmat.
 *
 * Test system (all real):
 *   A00 = diag(2,4)                     (2x2)
 *   A01 = [[1,2,3],[4,5,6]]             (2x3)
 *   A10 = [[1,0],[0,1],[1,1]]           (3x2)
 *   A11 = 10*I                          (3x3)
 *   analytic Pmat = [[9.5,-1,-1.5],[-1,8.75,-1.5],[-1.5,-2.25,7.0]]
 *
 * Usage: ./schur_check
 */
#include <petscksp.h>

static PetscErrorCode DenseFrom(Mat *M, PetscInt m, PetscInt n, const PetscScalar *vals)
{
  PetscInt i, j;

  PetscFunctionBeginUser;
  PetscCall(MatCreateSeqAIJ(PETSC_COMM_SELF, m, n, n, NULL, M));
  for (i = 0; i < m; i++)
    for (j = 0; j < n; j++)
      if (vals[i * n + j] != 0.0) PetscCall(MatSetValue(*M, i, j, vals[i * n + j], INSERT_VALUES));
  PetscCall(MatAssemblyBegin(*M, MAT_FINAL_ASSEMBLY));
  PetscCall(MatAssemblyEnd(*M, MAT_FINAL_ASSEMBLY));
  PetscFunctionReturn(PETSC_SUCCESS);
}

static PetscErrorCode MaxAbsDiffVsAnalytic(Mat Sp, PetscReal *maxdiff)
{
  const PetscScalar ref[9] = {9.5, -1.0, -1.5, -1.0, 8.75, -1.5, -1.5, -2.25, 7.0};
  PetscInt          i, j;
  PetscScalar       v;

  PetscFunctionBeginUser;
  *maxdiff = 0.0;
  for (i = 0; i < 3; i++)
    for (j = 0; j < 3; j++) {
      PetscCall(MatGetValue(Sp, i, j, &v));
      if (PetscAbsScalar(v - ref[i * 3 + j]) > *maxdiff) *maxdiff = PetscAbsScalar(v - ref[i * 3 + j]);
    }
  PetscFunctionReturn(PETSC_SUCCESS);
}

int main(int argc, char **argv)
{
  const PetscScalar a00v[4] = {2, 0, 0, 4};
  const PetscScalar a01v[6] = {1, 2, 3, 4, 5, 6};
  const PetscScalar a10v[6] = {1, 0, 0, 1, 1, 1};
  const PetscScalar a11v[9] = {10, 0, 0, 0, 10, 0, 0, 0, 10};
  const PetscScalar a01Tv[6] = {1, 4, 2, 5, 3, 6}; /* A01^T, 3x2 */
  Mat               A00, A01, A10, A11, A01T, A01virt, A01hvirt;
  Mat               Sp_explicit = NULL, Sp_virt = NULL, Sp_hvirt = NULL;
  PetscReal         d_expl, d_virt, d_hvirt;

  PetscCall(PetscInitialize(&argc, &argv, NULL, NULL));

  PetscCall(DenseFrom(&A00, 2, 2, a00v));
  PetscCall(DenseFrom(&A01, 2, 3, a01v));
  PetscCall(DenseFrom(&A10, 3, 2, a10v));
  PetscCall(DenseFrom(&A11, 3, 3, a11v));
  PetscCall(DenseFrom(&A01T, 3, 2, a01Tv));
  PetscCall(MatCreateTranspose(A01T, &A01virt));          /* virtual transpose == A01 */
  PetscCall(MatCreateHermitianTranspose(A01T, &A01hvirt)); /* real => also == A01 */

  /* ARM 1: explicit A01 */
  PetscCall(MatCreateSchurComplementPmat(A00, A01, A10, A11, MAT_SCHUR_COMPLEMENT_AINV_DIAG, MAT_INITIAL_MATRIX, &Sp_explicit));
  PetscCall(MaxAbsDiffVsAnalytic(Sp_explicit, &d_expl));
  PetscCall(PetscPrintf(PETSC_COMM_SELF, "explicit A01:            max|Sp - analytic| = %.6e\n", (double)d_expl));

  /* ARM 2: virtual transpose A01 */
  PetscCall(MatCreateSchurComplementPmat(A00, A01virt, A10, A11, MAT_SCHUR_COMPLEMENT_AINV_DIAG, MAT_INITIAL_MATRIX, &Sp_virt));
  PetscCall(MaxAbsDiffVsAnalytic(Sp_virt, &d_virt));
  PetscCall(PetscPrintf(PETSC_COMM_SELF, "virtual MatTranspose A01: max|Sp - analytic| = %.6e\n", (double)d_virt));

  /* ARM 3: virtual Hermitian transpose A01 (real scalars: same transform) */
  PetscCall(MatCreateSchurComplementPmat(A00, A01hvirt, A10, A11, MAT_SCHUR_COMPLEMENT_AINV_DIAG, MAT_INITIAL_MATRIX, &Sp_hvirt));
  PetscCall(MaxAbsDiffVsAnalytic(Sp_hvirt, &d_hvirt));
  PetscCall(PetscPrintf(PETSC_COMM_SELF, "virtual HermTrans A01:    max|Sp - analytic| = %.6e\n", (double)d_hvirt));

  if (d_expl < 1e-12 && (d_virt > 1e-10 || d_hvirt > 1e-10)) {
    PetscCall(PetscPrintf(PETSC_COMM_SELF, "issue-property VIOLATION: virtual-transpose representation of the SAME A01 yields a different (wrong) Schur Pmat\n"));
  } else if (d_expl < 1e-12 && d_virt < 1e-12 && d_hvirt < 1e-12) {
    PetscCall(PetscPrintf(PETSC_COMM_SELF, "issue-property SATISFIED: all representations agree with the analytic Pmat\n"));
  } else {
    PetscCall(PetscPrintf(PETSC_COMM_SELF, "issue-property result: inspect manually (explicit arm itself deviates)\n"));
  }

  PetscCall(MatDestroy(&Sp_explicit));
  PetscCall(MatDestroy(&Sp_virt));
  PetscCall(MatDestroy(&Sp_hvirt));
  PetscCall(MatDestroy(&A01virt));
  PetscCall(MatDestroy(&A01hvirt));
  PetscCall(MatDestroy(&A01T));
  PetscCall(MatDestroy(&A00));
  PetscCall(MatDestroy(&A01));
  PetscCall(MatDestroy(&A10));
  PetscCall(MatDestroy(&A11));
  PetscCall(PetscFinalize());
  return 0;
}
