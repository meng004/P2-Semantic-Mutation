/* E-SUNDIALS-008 issue oracle driver (m_conv / f_conv.rate)
 *
 * Defect: KINSOL (SUNDIALS v7.3.0..v7.4.0) does not reinitialize the Anderson
 * acceleration current depth on each KINSol call; kin_current_depth (and the
 * associated df/dg history) leaks from a previous solve into the next one.
 * Fixed by PR #764 / commit 49763f35 (v7.5.0): KINInitAA() now sets
 * kin_current_depth = 0.  Downstream report: mfem/mfem#5004 ("giving the same
 * initial guess twice in a row gives two different answers").
 *
 * issue oracle: the convergence trajectory of an Anderson-accelerated fixed-point
 * solve must be a function of the configured depth and the initial guess only,
 * not of solver-instance history.  Concretely, with one KINSOL instance:
 *   solve #1 from x0, then reset the state vector to x0 and solve #2.
 * And with a fresh, identically configured instance: solve #3 from x0.
 * Oracle: (nni, fnorm, x*) of solves #1, #2, #3 must be identical (bitwise for
 * x*): same input => same convergence history.  The buggy revision violates
 * this (solve #2 starts from stale AA depth/history); the fixed revision
 * satisfies it.
 *
 * Fixed-point problem (contraction in R^3, AA-sensitive):
 *   G1 = cos(x2*x3)/3 + 1/6
 *   G2 = sqrt(x1*x1 + sin(x3) + 1.06)/9 - 0.1
 *   G3 = -exp(-x1*x2)/20 - (10*pi - 3)/60
 * (standard nonlinear FP test system; unique fixed point near
 *  (0.5, 0.0, -0.52)).
 */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>

#include <kinsol/kinsol.h>
#include <nvector/nvector_serial.h>
#include <sundials/sundials_types.h>

#define PI 3.1415926535897932384626433832795

static long g_calls = 0;

static int Gfun(N_Vector u, N_Vector gval, void* user_data)
{
  sunrealtype* x = N_VGetArrayPointer(u);
  sunrealtype* g = N_VGetArrayPointer(gval);
  g[0] = cos(x[1] * x[2]) / 3.0 + 1.0 / 6.0;
  g[1] = sqrt(x[0] * x[0] + sin(x[2]) + 1.06) / 9.0 - 0.1;
  g[2] = -exp(-x[0] * x[1]) / 20.0 - (10.0 * PI - 3.0) / 60.0;
  g_calls++;
  return 0;
}

typedef struct { long nni; double fnorm; double x[3]; } SolveRec;

static void set_x0(N_Vector u)
{
  sunrealtype* x = N_VGetArrayPointer(u);
  x[0] = 0.1; x[1] = 0.1; x[2] = -0.1;
}

static int do_solve(void* kmem, N_Vector u, N_Vector scale, SolveRec* r)
{
  set_x0(u);
  int flag = KINSol(kmem, u, KIN_FP, scale, scale);
  if (flag < 0) { fprintf(stderr, "KINSol flag %d\n", flag); return flag; }
  KINGetNumNonlinSolvIters(kmem, &r->nni);
  sunrealtype fn; KINGetFuncNorm(kmem, &fn); r->fnorm = (double)fn;
  sunrealtype* x = N_VGetArrayPointer(u);
  r->x[0] = x[0]; r->x[1] = x[1]; r->x[2] = x[2];
  return 0;
}

static void* make_kin(SUNContext sunctx, N_Vector tmpl, long maa)
{
  void* kmem = KINCreate(sunctx);
  KINSetMAA(kmem, maa);
  KINInit(kmem, Gfun, tmpl);
  KINSetFuncNormTol(kmem, 1e-12);
  KINSetNumMaxIters(kmem, 200);
  return kmem;
}

int main(void)
{
  const long maa = 2;
  SUNContext sunctx;
  SUNContext_Create(SUN_COMM_NULL, &sunctx);

  N_Vector u = N_VNew_Serial(3, sunctx);
  N_Vector scale = N_VNew_Serial(3, sunctx);
  N_VConst(1.0, scale);

  SolveRec s1, s2, s3;

  /* reused instance: solve twice from the same x0 */
  void* kmem = make_kin(sunctx, u, maa);
  if (do_solve(kmem, u, scale, &s1)) return 1;
  if (do_solve(kmem, u, scale, &s2)) return 1;
  KINFree(&kmem);

  /* fresh instance: one solve from the same x0 */
  void* kmem2 = make_kin(sunctx, u, maa);
  if (do_solve(kmem2, u, scale, &s3)) return 1;
  KINFree(&kmem2);

  printf("solve1 (reused inst, 1st): nni=%ld fnorm=%.17e x=(%.17g, %.17g, %.17g)\n",
         s1.nni, s1.fnorm, s1.x[0], s1.x[1], s1.x[2]);
  printf("solve2 (reused inst, 2nd): nni=%ld fnorm=%.17e x=(%.17g, %.17g, %.17g)\n",
         s2.nni, s2.fnorm, s2.x[0], s2.x[1], s2.x[2]);
  printf("solve3 (fresh inst      ): nni=%ld fnorm=%.17e x=(%.17g, %.17g, %.17g)\n",
         s3.nni, s3.fnorm, s3.x[0], s3.x[1], s3.x[2]);

  double d12 = 0, d13 = 0;
  for (int i = 0; i < 3; i++) {
    d12 = fmax(d12, fabs(s1.x[i] - s2.x[i]));
    d13 = fmax(d13, fabs(s1.x[i] - s3.x[i]));
  }
  int bit12 = (memcmp(s1.x, s2.x, sizeof s1.x) == 0) && (s1.nni == s2.nni);
  int bit13 = (memcmp(s1.x, s3.x, sizeof s1.x) == 0) && (s1.nni == s3.nni);
  printf("maxdiff solve1-vs-solve2 = %.3e  identical=%s\n", d12, bit12 ? "YES" : "NO");
  printf("maxdiff solve1-vs-solve3 = %.3e  identical=%s\n", d13, bit13 ? "YES" : "NO");
  printf("issue oracle (same input => same convergence trajectory): %s\n",
         (bit12 && bit13) ? "PASS" : "VIOLATED");

  N_VDestroy(u); N_VDestroy(scale);
  SUNContext_Free(&sunctx);
  return 0;
}
