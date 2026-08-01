/*
 * F-GRAPHBLAS-001 verification: GrB_mxm saxpy4/saxpy5 mishandled typecasting
 * in SuiteSparse:GraphBLAS v8.0.0..v8.2.0 (fixed in v8.2.1, commit ffaa21e,
 * "incorrect handling of typecasting in GB_AxB_saxpy4.c and GB_AxB_saxpy5.c",
 * reported by Erik Welch).
 *
 * issue oracle (m_inv/f_inv.eqv): with a GrB_PLUS_TIMES_SEMIRING_FP64, feeding
 * integer-typed inputs (GraphBLAS casts internally) must give the SAME result
 * as pre-casting those inputs to FP64 by hand -- one abstract computation,
 * two input-representation routes. Swept over sparsity-format combinations
 * chosen to reach the saxpy4 (C full += sparse*X) and saxpy5
 * (C full += X*sparse) kernels, with accumulator.
 *
 * Build: gcc -I<gb>/Include this.c -L<gb>/build -lgraphblas -lm
 */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include "GraphBLAS.h"

#define OK(x) do { GrB_Info i_ = (x); if (i_ != GrB_SUCCESS) { \
  printf("GrB error %d at line %d\n", (int)i_, __LINE__); exit(2); } } while (0)

static void set_sparsity(GrB_Matrix M, int ctrl)
{
  OK(GxB_Matrix_Option_set(M, GxB_SPARSITY_CONTROL, ctrl));
  OK(GrB_Matrix_wait(M, GrB_MATERIALIZE));
}

/* build an n x n INT32 matrix with given density (deterministic LCG) */
static void build_int32(GrB_Matrix *M, GrB_Index n, double density, unsigned seed)
{
  OK(GrB_Matrix_new(M, GrB_INT32, n, n));
  unsigned s = seed;
  for (GrB_Index i = 0; i < n; i++)
    for (GrB_Index j = 0; j < n; j++) {
      s = s * 1103515245u + 12345u;
      if ((double)(s % 1000u) / 1000.0 < density) {
        int32_t v = (int32_t)(s % 7u) - 3;
        if (v == 0) v = 2;
        OK(GrB_Matrix_setElement_INT32(*M, v, i, j));
      }
    }
  OK(GrB_Matrix_wait(*M, GrB_MATERIALIZE));
}

static void cast_fp64(GrB_Matrix *F, GrB_Matrix M, GrB_Index n)
{
  OK(GrB_Matrix_new(F, GrB_FP64, n, n));
  OK(GrB_Matrix_apply(*F, NULL, NULL, GrB_IDENTITY_FP64, M, NULL));
  OK(GrB_Matrix_wait(*F, GrB_MATERIALIZE));
}

/* dense FP64 matrix, all entries = 1.0, forced full */
static void build_full_fp64(GrB_Matrix *M, GrB_Index n)
{
  OK(GrB_Matrix_new(M, GrB_FP64, n, n));
  OK(GrB_Matrix_assign_FP64(*M, NULL, NULL, 1.0, GrB_ALL, n, GrB_ALL, n, NULL));
  set_sparsity(*M, GxB_FULL);
}

static double compare(GrB_Matrix X, GrB_Matrix Y, GrB_Index n)
{
  double maxd = 0.0;
  for (GrB_Index i = 0; i < n; i++)
    for (GrB_Index j = 0; j < n; j++) {
      double a = 0, b = 0;
      GrB_Info ia = GrB_Matrix_extractElement_FP64(&a, X, i, j);
      GrB_Info ib = GrB_Matrix_extractElement_FP64(&b, Y, i, j);
      if (ia == GrB_NO_VALUE) a = 0;
      if (ib == GrB_NO_VALUE) b = 0;
      double d = fabs(a - b);
      if (d > maxd) maxd = d;
    }
  return maxd;
}

/* one trial: C(full,FP64) += Aint * Bint  vs  C += Afp * Bfp */
static double trial(GrB_Index n, int fmtA, int fmtB, const char *label)
{
  GrB_Matrix Aint, Bint, Afp, Bfp, C1, C2;
  build_int32(&Aint, n, fmtA == GxB_FULL ? 1.01 : 0.3, 42);
  build_int32(&Bint, n, fmtB == GxB_FULL ? 1.01 : 0.3, 99);
  set_sparsity(Aint, fmtA);
  set_sparsity(Bint, fmtB);
  cast_fp64(&Afp, Aint, n);
  cast_fp64(&Bfp, Bint, n);
  set_sparsity(Afp, fmtA);
  set_sparsity(Bfp, fmtB);

  build_full_fp64(&C1, n);
  build_full_fp64(&C2, n);

  /* accumulate: C += A*B (accum makes C stay full -> saxpy4/5 territory) */
  OK(GrB_mxm(C1, NULL, GrB_PLUS_FP64, GrB_PLUS_TIMES_SEMIRING_FP64, Aint, Bint, NULL));
  OK(GrB_mxm(C2, NULL, GrB_PLUS_FP64, GrB_PLUS_TIMES_SEMIRING_FP64, Afp, Bfp, NULL));

  double d = compare(C1, C2, n);
  printf("  %-34s n=%3d max|C_intcast - C_precast| = %.6e%s\n",
         label, (int)n, d, d > 1e-12 ? "   <-- MISMATCH" : "");
  GrB_Matrix_free(&Aint); GrB_Matrix_free(&Bint);
  GrB_Matrix_free(&Afp);  GrB_Matrix_free(&Bfp);
  GrB_Matrix_free(&C1);   GrB_Matrix_free(&C2);
  return d;
}

int main(void)
{
  OK(GrB_init(GrB_NONBLOCKING));
  int32_t v[3] = {0, 0, 0};
  OK(GxB_Global_Option_get(GxB_LIBRARY_VERSION, v));
  printf("SuiteSparse:GraphBLAS %d.%d.%d (headers %d.%d.%d)\n", v[0], v[1], v[2],
         GxB_IMPLEMENTATION_MAJOR, GxB_IMPLEMENTATION_MINOR, GxB_IMPLEMENTATION_SUB);

  double worst = 0, d;
  d = trial(64, GxB_SPARSE, GxB_FULL,   "A sparse * B full   (saxpy5 path)"); if (d > worst) worst = d;
  d = trial(64, GxB_FULL,   GxB_SPARSE, "A full   * B sparse (saxpy4 path)"); if (d > worst) worst = d;
  d = trial(64, GxB_SPARSE, GxB_BITMAP, "A sparse * B bitmap");               if (d > worst) worst = d;
  d = trial(64, GxB_BITMAP, GxB_SPARSE, "A bitmap * B sparse");               if (d > worst) worst = d;
  d = trial(64, GxB_HYPERSPARSE, GxB_FULL, "A hyper  * B full");              if (d > worst) worst = d;
  d = trial(64, GxB_FULL,   GxB_HYPERSPARSE, "A full * B hyper");             if (d > worst) worst = d;
  d = trial(16, GxB_SPARSE, GxB_FULL,   "small A sparse * B full");           if (d > worst) worst = d;

  printf(worst > 1e-12 ? "=> issue-property VIOLATION: typecast route changes GrB_mxm result (max %.6e)\n"
                       : "=> issue-property SATISFIED: both input-representation routes agree\n", worst);
  GrB_finalize();
  return worst > 1e-12 ? 1 : 0;
}
