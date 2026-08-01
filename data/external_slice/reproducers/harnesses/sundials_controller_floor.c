/* E-SUNDIALS-002 issue oracle driver (m_mono / f_mono.stat)
 *
 * Defect: SUNDIALS v7.2.x SUNAdaptController_Soderlind family clamps the
 * error inputs with an arbitrary interior floor
 *     e1 = SUNMAX(bias*dsm, TINY),  TINY = 1e-10   (likewise ep/epp history)
 * so for any dsm below ~1e-10/bias the controller's response SATURATES: two
 * strictly different (both tiny) error estimates yield the identical step
 * estimate, and the estimate deviates from the documented control law
 * hnew = h * (1/(bias*dsm))^(k/(p+1)).  Removed in v7.3.0 (PR #548:
 * "Removed error floors ... which could unnecessarily limit the time step
 * size growth, particularly after the first step").
 *
 * issue oracle (controller level, public SUNAdaptController API):
 *  (a) strict monotone response: dsm1 < dsm2  =>  hnew(dsm1) > hnew(dsm2)
 *      (documented law is strictly decreasing in dsm);
 *  (b) conformance: hnew matches the documented I-controller formula.
 * Integrator-level corroboration: ERKStep on y' = -1e-9 y (local errors far
 * below the floor), PID controller, tiny forced initial step: the buggy
 * controller needs more steps because per-step growth is capped by the floor
 * response rather than the integrator's own growth bound.
 */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#include <sunadaptcontroller/sunadaptcontroller_soderlind.h>
#include <arkode/arkode_erkstep.h>
#include <nvector/nvector_serial.h>
#include <sundials/sundials_config.h>

static int f(sunrealtype t, N_Vector y, N_Vector yd, void* ud)
{
  NV_Ith_S(yd, 0) = -1e-9 * NV_Ith_S(y, 0);
  return 0;
}

int main(void)
{
  SUNContext ctx;
  SUNContext_Create(SUN_COMM_NULL, &ctx);
  printf("SUNDIALS %s\n", SUNDIALS_VERSION);

  /* ---- (a)+(b) controller level: I controller, one-shot estimates ---- */
  const double h = 1.0;
  const int p = 1;                    /* embedding order */
  int mono_viol = 0, conf_viol = 0;
  double prev = 0.0;
  printf("## I-controller EstimateStep sweep (h=1, p=1); documented law: hnew = (1/(bias*dsm))^(1/(p+1))\n");
  for (int k = 6; k <= 16; k += 2) {
    double dsm = pow(10.0, -k);
    SUNAdaptController C = SUNAdaptController_I(ctx);
    /* pin bias explicitly: v7.3.0 changed the DEFAULT bias 1.5 -> 1.0
       (PR #565), which would otherwise confound the comparison */
    SUNAdaptController_SetErrorBias(C, 1.5);
    sunrealtype hnew = 0;
    SUNAdaptController_EstimateStep(C, h, p, dsm, &hnew);
    /* documented formula with default bias 1.5 (v7.2/v7.3 default) */
    double expect = pow(1.0 / (1.5 * dsm), 1.0 / (p + 1));
    double relconf = fabs((double)hnew - expect) / expect;
    printf("dsm=1e-%02d hnew=%.6e expected(law)=%.6e relerr=%.2e%s\n",
           k, (double)hnew, expect, relconf, relconf > 1e-8 ? "  <-- OFF-LAW" : "");
    if (relconf > 1e-8) conf_viol++;
    if (prev != 0.0 && (double)hnew <= prev) {
      printf("  ^ saturation: hnew(dsm=1e-%d) <= hnew(dsm=1e-%d) -- strict monotone response VIOLATED\n", k, k - 2);
      mono_viol++;
    }
    prev = (double)hnew;
    SUNAdaptController_Destroy(C);
  }

  /* ---- integrator-level corroboration ---- */
  N_Vector y = N_VNew_Serial(1, ctx);
  NV_Ith_S(y, 0) = 1.0;
  void* am = ERKStepCreate(f, 0.0, y, ctx);
  ERKStepSStolerances(am, 1e-4, 1e-8);
  ERKStepSetMaxNumSteps(am, 100000);
  ERKStepSetInitStep(am, 1e-8);
  SUNAdaptController pid = SUNAdaptController_PID(ctx);
  ERKStepSetAdaptController(am, pid);
  sunrealtype t;
  int flag = ERKStepEvolve(am, 1.0e6, y, &t, ARK_NORMAL);
  long nst = 0; ERKStepGetNumSteps(am, &nst);
  printf("## ERKStep y'=-1e-9y, h0=1e-8, tf=1e6, PID: flag=%d nst=%ld\n", flag, nst);

  printf("### VERDICT: %s (monotone-saturation violations=%d, off-law points=%d)\n",
         (mono_viol || conf_viol) ? "VIOLATED" : "PASS", mono_viol, conf_viol);
  ERKStepFree(&am); SUNAdaptController_Destroy(pid);
  N_VDestroy(y); SUNContext_Free(&ctx);
  return 0;
}
