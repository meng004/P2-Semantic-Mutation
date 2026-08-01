/* A-BLIS-002 issue-property driver (m_inv / f_inv.eqv): aliased complex scal2 equivalence.
 *
 * Issue flame/blis#828 (devinamatthews, 2024-09-23): the level-0 macros
 * bli_?scal2s / scal2js / scal2ris / scal2jris compute y = alpha*conj?(x) but
 * write the real part of y before the real part of x is finished being read,
 * so &x == &y corrupts the result.  Fixed by PR #830 "Add new level-0 macro
 * layer" (merge a014a081).
 *
 * issue oracle (f_inv.eqv, formulation equivalence): scal2(alpha, x -> y) with
 * y aliased to x must equal (a) the unaliased scal2 into a fresh buffer and
 * (b) the dedicated in-place scal(alpha, x), and the analytic alpha*x.
 * Probed at BOTH altitudes: the level-0 macro (bli_zscal2s / bli_cscal2s,
 * the issue's literal subject) and the level-1v function bli_zscal2v with
 * incx=incy=1, y==x.
 */
#include <stdio.h>
#include <math.h>
#include "blis.h"

static int ok_all = 1;

static void expect_z(const char* label, dcomplex got, dcomplex want)
{
  double d = fabs(got.real - want.real) + fabs(got.imag - want.imag);
  if (d > 1e-13) {
    printf("  [%s] got (%g,%g) want (%g,%g)  VIOLATED\n", label,
           got.real, got.imag, want.real, want.imag);
    ok_all = 0;
  }
}

int main(void)
{
  dcomplex alpha = {2.0, 3.0};
  dcomplex x0    = {5.0, 7.0};
  /* analytic: alpha*x = (2*5-3*7, 2*7+3*5) = (-11, 29) */
  dcomplex want  = {-11.0, 29.0};
  dcomplex wantj = {2.0*5.0+3.0*7.0, -2.0*7.0+3.0*5.0}; /* alpha*conj(x) = (31,1) */

  /* level-0 macro, unaliased control */
  dcomplex x = x0, y = {0,0};
  bli_zscal2s(alpha, x, y);
  expect_z("macro scal2s unaliased", y, want);

  /* level-0 macro, ALIASED (the issue's literal case) */
  x = x0;
  bli_zscal2s(alpha, x, x);
  expect_z("macro scal2s ALIASED", x, want);

  /* conjugating variant aliased (macro renamed by the fix's new layer;
     guard by availability -- PR #830 maps bli_zscal2s -> bli_tscal2s(...) and
     drops the standalone zscal2js spelling) */
#ifdef bli_zscal2js
  x = x0;
  bli_zscal2js(alpha, x, x);
  expect_z("macro scal2js ALIASED", x, wantj);
#else
  (void)wantj;
  printf("  [macro scal2js] spelling absent on this revision (new t-layer), skipped\n");
#endif

  /* level-1v function, aliased vs unaliased vs scalv */
  dcomplex vx[4], vy[4], vs[4];
  for (int i = 0; i < 4; i++) { vx[i].real = i + 1; vx[i].imag = 2 * i - 3; vs[i] = vx[i]; }
  bli_zscal2v(BLIS_NO_CONJUGATE, 4, &alpha, vx, 1, vy, 1);   /* unaliased reference */
  bli_zscal2v(BLIS_NO_CONJUGATE, 4, &alpha, vx, 1, vx, 1);   /* aliased */
  bli_zscalv(BLIS_NO_CONJUGATE, 4, &alpha, vs, 1);           /* dedicated in-place */
  for (int i = 0; i < 4; i++) {
    char lab[64];
    snprintf(lab, sizeof lab, "scal2v aliased[%d] vs unaliased", i);
    expect_z(lab, vx[i], vy[i]);
    snprintf(lab, sizeof lab, "scal2v aliased[%d] vs scalv", i);
    expect_z(lab, vx[i], vs[i]);
  }

  printf("### BLIS %s VERDICT: %s\n", bli_info_get_version_str(), ok_all ? "PASS" : "VIOLATED");
  return 0;
}
