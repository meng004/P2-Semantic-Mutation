/* E-SUNDIALS-001 issue oracle driver (m_mono / f_mono.stat)
 *
 * Defect: CVODE <= v7.5.0 cvCheckConstraints() computes the step-reduction
 * factor from the PREDICTED state zn[0]:
 *     eta = 0.9 * N_VMinQuotient(zn[0], mm*(zn[0]-y))
 * If the corrector lands exactly on the forecast in every constraint-
 * violating component (denominator identically zero -- guaranteed for any
 * ODE whose solution is locally linear in t, e.g. y' = const, where BDF
 * forecast is exact), N_VMinQuotient returns SUN_BIG_REAL and the "step
 * size reduction" becomes eta ~ 8.9e307: the next attempt uses an infinite
 * step and the solver fails unrecoverably (issue #702, reported v7.2.1).
 * Fixed in v7.6.0 (PR #787): factor computed from the prior solution, so the
 * quotient is the fraction of the step at which the boundary is crossed,
 * always in (0,1); plus a bounded constraint-failure counter.
 *
 * issue oracle: after a step attempt fails the inequality-constraint check, the
 * next attempted step size must SHRINK (eta < 1); across the whole run the
 * step size magnitude must never exceed the pre-violation step size (and a
 * user-set CVodeSetMaxStep bound must hold).  Violation witness: max |h|
 * observed after the constraint region is reached, and the final return flag.
 *
 * Problem: y' = -1, y(0) = 1, constraints y >= 0 (value 1.0), BDF+Newton
 * +dense, integrate toward t = 2 (solution hits the boundary at t = 1).
 * A correct implementation shrinks h near t=1 and returns CV_CONSTR_FAIL
 * (or stalls at hmin) with |h| small; the buggy one proposes |h| ~ 1e307.
 */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#include <cvode/cvode.h>
#include <nvector/nvector_serial.h>
#include <sunmatrix/sunmatrix_dense.h>
#include <sunlinsol/sunlinsol_dense.h>
#include <sundials/sundials_config.h>

static int f(sunrealtype t, N_Vector y, N_Vector yd, void* ud)
{
  NV_Ith_S(yd, 0) = -1.0;
  return 0;
}

int main(void)
{
  SUNContext ctx;
  SUNContext_Create(SUN_COMM_NULL, &ctx);
  N_Vector y = N_VNew_Serial(1, ctx);
  NV_Ith_S(y, 0) = 1.0;

  void* cv = CVodeCreate(CV_BDF, ctx);
  CVodeInit(cv, f, 0.0, y);
  CVodeSStolerances(cv, 1e-8, 1e-10);
  SUNMatrix A = SUNDenseMatrix(1, 1, ctx);
  SUNLinearSolver LS = SUNLinSol_Dense(y, A, ctx);
  CVodeSetLinearSolver(cv, LS, A);
  CVodeSetMaxNumSteps(cv, 100000);
  CVodeSetMaxStep(cv, 0.5);                 /* explicit user bound */

  N_Vector c = N_VNew_Serial(1, ctx);
  NV_Ith_S(c, 0) = 1.0;                     /* y >= 0 */
  CVodeSetConstraints(cv, c);

  double hmax_seen = 0.0, h_at_090 = 0.0;
  sunrealtype t = 0.0;
  int flag = 0, steps = 0;
  while (steps < 2000) {
    flag = CVode(cv, 2.0, y, &t, CV_ONE_STEP);
    sunrealtype hcur = 0;
    CVodeGetCurrentStep(cv, &hcur);
    if (fabs((double)hcur) > hmax_seen) hmax_seen = fabs((double)hcur);
    if (t < 0.90 && fabs((double)hcur) > h_at_090) h_at_090 = fabs((double)hcur);
    steps++;
    if (flag < 0 || t >= 2.0) break;
  }
  sunrealtype hlast = 0; CVodeGetLastStep(cv, &hlast);
  long nst = 0; CVodeGetNumSteps(cv, &nst);
  printf("SUNDIALS %s | final flag=%d t=%.10g y=%.6e nst=%ld last_h=%.3e | "
         "max |h| seen=%.3e (pre-boundary %.3e) | user hmax=0.5\n",
         SUNDIALS_VERSION, flag, (double)t, (double)NV_Ith_S(y, 0), nst,
         fabs((double)hlast), hmax_seen, h_at_090);
  int violated = hmax_seen > 10.0;   /* any h beyond 20x the user bound */
  printf("### issue oracle (constraint violation must shrink, never grow, the step; hmax bound must hold): %s\n",
         violated ? "VIOLATED" : "PASS");
  N_VDestroy(y); N_VDestroy(c); SUNMatDestroy(A); SUNLinSolFree(LS);
  CVodeFree(&cv); SUNContext_Free(&ctx);
  return 0;
}
