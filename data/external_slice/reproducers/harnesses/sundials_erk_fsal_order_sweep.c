/* E-SUNDIALS-010 issue oracle driver (m_conv / f_conv.rate)
 *
 * Defect: SUNDIALS <= v6.6.2 erkStep_FullRHS() ARK_FULLRHS_END branch treats
 * any ERK table with c[s-1] == 1 as FSAL and reuses F[stages-1] (an internal
 * stage RHS) as f(y_{n+1}) for the next step's first stage.  Affected named
 * tables have c_s = 1 but A[s-1,:] != b (issue #311: ARKODE_HEUN_EULER_2_1_2
 * and the ARKODE_ARK* explicit companions).  Fixed by PR #324 via
 * ARKodeButcherTable_IsStifflyAccurate() (released v6.7.0).
 *
 * issue oracle: integrate a smooth nonlinear IVP with fixed step h over a
 * refinement sweep h, h/2, h/4, h/8; the empirical global convergence order
 * p_emp = log2(err(h)/err(h/2)) must match the table's registered order q
 * within tolerance.  Secondary witness: nfe must equal the exact stage-count
 * bookkeeping of a correct non-FSAL implementation (s evals/step + END-mode
 * re-evaluation), not the halved count reported in issue #311.
 *
 * IVP: y' = -y^2, y(0) = 1, exact y(t) = 1/(1+t).  Smooth, nonlinear
 * (f'f != 0 so the wrong-point reuse actually perturbs the solution).
 *
 * Usage: erk_fsal_order_sweep <TABLE_NAME> <T> <h0> <nlevels>
 * Output: one line per level: h, err(T), nfe, nsteps; then fitted orders.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

#include <arkode/arkode_erkstep.h>
#include <nvector/nvector_serial.h>
#include <sundials/sundials_types.h>

static int frhs(realtype t, N_Vector y, N_Vector ydot, void* user_data)
{
  realtype u = NV_Ith_S(y, 0);
  NV_Ith_S(ydot, 0) = -u * u;
  return 0;
}

static realtype exact(realtype t) { return 1.0 / (1.0 + t); }

int main(int argc, char* argv[])
{
  if (argc < 5) {
    fprintf(stderr, "usage: %s TABLE_NAME T h0 nlevels\n", argv[0]);
    return 1;
  }
  const char* table_name = argv[1];
  realtype T  = atof(argv[2]);
  realtype h0 = atof(argv[3]);
  int nlevels = atoi(argv[4]);

  SUNContext sunctx;
  if (SUNContext_Create(NULL, &sunctx)) { fprintf(stderr, "ctx fail\n"); return 1; }

  double errs[16];
  long   nfes[16];
  long   nsts[16];

  for (int lev = 0; lev < nlevels; lev++) {
    realtype h = h0 / pow(2.0, lev);

    N_Vector y = N_VNew_Serial(1, sunctx);
    NV_Ith_S(y, 0) = 1.0;

    void* mem = ERKStepCreate(frhs, 0.0, y, sunctx);
    if (!mem) { fprintf(stderr, "create fail\n"); return 1; }

    if (ERKStepSetTableName(mem, table_name) != ARK_SUCCESS) {
      fprintf(stderr, "unknown table %s\n", table_name);
      return 1;
    }
    ERKStepSetFixedStep(mem, h);
    ERKStepSetMaxNumSteps(mem, 10000000);
    ERKStepSetStopTime(mem, T);
    /* keep defaults otherwise: Hermite interpolation module stays enabled,
       which is what sets call_fullrhs and exercises the END-mode reuse */

    realtype tret;
    int flag = ERKStepEvolve(mem, T, y, &tret, ARK_NORMAL);
    if (flag < 0) { fprintf(stderr, "evolve fail %d at lev %d\n", flag, lev); return 1; }

    long nst = 0, nfe = 0;
    ERKStepGetNumSteps(mem, &nst);
    ERKStepGetNumRhsEvals(mem, &nfe);

    double err = fabs((double)(NV_Ith_S(y, 0) - exact(tret)));
    errs[lev] = err; nfes[lev] = nfe; nsts[lev] = nst;
    printf("level=%d h=%.10e t=%.17g err=%.17e nst=%ld nfe=%ld\n",
           lev, (double)h, (double)tret, err, nst, nfe);

    ERKStepFree(&mem);
    N_VDestroy(y);
  }

  printf("---\n");
  for (int lev = 1; lev < nlevels; lev++) {
    double p = log(errs[lev - 1] / errs[lev]) / log(2.0);
    printf("order[%d->%d] = %.6f\n", lev - 1, lev, p);
  }

  SUNContext_Free(&sunctx);
  return 0;
}
