/* E-SUNDIALS-003 issue oracle driver (m_adj / f_adj.self)
 *
 * Defect: IDAS <= v7.7.0 fills the quadrature derivative history phiQ[1]
 * (via rhsQ) only on the very first IDASolve step; after IDAReInit (+
 * IDAQuadReInit) this initialization is skipped due to logic errors, so the
 * quadrature predictor on the first post-reinit step uses stale phiQ[1]
 * (fix a7393b501 / PR #888, v7.8.0: "When IDAS is reinitialized, it does not
 * do this due to some logic errors").  Restart-from-a-point is exactly the
 * primitive the IDAS adjoint checkpointing uses to recompute forward
 * segments between checkpoints ("IDAS produced slightly different results
 * [when] recomputing forward data between checkpoints ... than the original
 * pass" -- PR text), hence the f_adj.self mapping.
 *
 * issue oracle (restart self-consistency): integrating t0 -> t2 in one pass and
 * integrating t0 -> t1, restarting via IDAReInit/IDAQuadReInit with the
 * reached state, then continuing to t2, must produce the same quadrature
 * q(t2) within integration accuracy (both compared to the exact integral).
 *
 * Problem: DAE form of y' = -y (residual yp + y), y(0)=1; quadrature
 * q' = y, exact q(t) = 1 - exp(-t).
 *
 * Usage: idas_quad_reinit <mode 0|1> <quad_errcon 0|1>
 *   mode 0: single pass t0->t2;  mode 1: reinit at t1=1, continue to t2=2.
 */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#include <idas/idas.h>
#include <nvector/nvector_serial.h>
#include <sunmatrix/sunmatrix_dense.h>
#include <sunlinsol/sunlinsol_dense.h>
#include <sundials/sundials_config.h>

static int res(sunrealtype t, N_Vector yy, N_Vector yp, N_Vector rr, void* ud)
{
  NV_Ith_S(rr, 0) = NV_Ith_S(yp, 0) + NV_Ith_S(yy, 0);
  return 0;
}

static int rhsQ(sunrealtype t, N_Vector yy, N_Vector yp, N_Vector qdot, void* ud)
{
  /* depends on yp so that a pre-IDACalcIC evaluation (inconsistent yp)
     poisons phiQ[1] measurably: q' = yp^2, exact integral (1-exp(-2t))/2 */
  NV_Ith_S(qdot, 0) = NV_Ith_S(yp, 0) * NV_Ith_S(yp, 0);
  return 0;
}

int main(int argc, char** argv)
{
  int mode = (argc > 1) ? atoi(argv[1]) : 0;
  int qerrcon = (argc > 2) ? atoi(argv[2]) : 1;
  SUNContext ctx;
  SUNContext_Create(SUN_COMM_NULL, &ctx);

  N_Vector yy = N_VNew_Serial(1, ctx), yp = N_VNew_Serial(1, ctx);
  N_Vector q  = N_VNew_Serial(1, ctx);
  NV_Ith_S(yy, 0) = 1.0; NV_Ith_S(yp, 0) = -1.0; NV_Ith_S(q, 0) = 0.0;

  void* ida = IDACreate(ctx);
  IDAInit(ida, res, 0.0, yy, yp);
  IDASStolerances(ida, 1e-8, 1e-10);
  SUNMatrix A = SUNDenseMatrix(1, 1, ctx);
  SUNLinearSolver LS = SUNLinSol_Dense(yy, A, ctx);
  IDASetLinearSolver(ida, LS, A);
  IDASetMaxNumSteps(ida, 100000);
  IDAQuadInit(ida, rhsQ, q);
  if (qerrcon) {
    IDASetQuadErrCon(ida, SUNTRUE);
    IDAQuadSStolerances(ida, 1e-8, 1e-10);
  }

  sunrealtype t = 0, tq = 0;
  if (mode == 2) {
    /* IDACalcIC trigger: start from an INCONSISTENT yp guess (+5); CalcIC
       corrects it to -1 before integration.  Buggy v7.7.0 fills phiQ[1]
       during IDACalcIC's IDAInitialSetup call (idas_ic.c) with the
       pre-correction state (qdot = 25 instead of 1) and never refills. */
    NV_Ith_S(yp, 0) = 5.0;
    /* load the inconsistent guess into IDAS (IDAInit copied the original
       consistent yp; modifying our vector alone changes nothing) */
    IDAReInit(ida, 0.0, yy, yp);
    IDAQuadReInit(ida, q);
    N_Vector id = N_VNew_Serial(1, ctx);
    NV_Ith_S(id, 0) = 1.0;              /* differential variable */
    IDASetId(ida, id);
    int cflag = IDACalcIC(ida, IDA_YA_YDP_INIT, 0.1);
    N_Vector ycic = N_VClone(yy), ypcic = N_VClone(yp);
    IDAGetConsistentIC(ida, ycic, ypcic);
    printf("IDACalcIC flag=%d corrected yp=%.6f\n", cflag, (double)NV_Ith_S(ypcic, 0));
    N_VDestroy(id); N_VDestroy(ycic); N_VDestroy(ypcic);
  }
  if (mode == 1) {
    if (IDASolve(ida, 1.0, &t, yy, yp, IDA_NORMAL) < 0) { fprintf(stderr, "seg1 fail\n"); return 1; }
    IDAGetQuad(ida, &tq, q);
    /* restart from the reached state -- the checkpoint-recompute primitive */
    IDAReInit(ida, t, yy, yp);
    IDAQuadReInit(ida, q);
  }
  if (IDASolve(ida, 2.0, &t, yy, yp, IDA_NORMAL) < 0) { fprintf(stderr, "seg2 fail\n"); return 1; }
  IDAGetQuad(ida, &tq, q);

  double exact = (1.0 - exp(-4.0)) / 2.0;
  double err = fabs(NV_Ith_S(q, 0) - exact);
  long nst = 0; IDAGetNumSteps(ida, &nst);
  printf("SUNDIALS %s mode=%s qerrcon=%d | q(2)=%.15e exact=%.15e err=%.3e nst=%ld\n",
         SUNDIALS_VERSION, mode==2 ? "calcic  " : (mode ? "reinit@1" : "single  "), qerrcon,
         (double)NV_Ith_S(q, 0), exact, err, nst);
  IDAFree(&ida); SUNMatDestroy(A); SUNLinSolFree(LS);
  N_VDestroy(yy); N_VDestroy(yp); N_VDestroy(q); SUNContext_Free(&ctx);
  return 0;
}
