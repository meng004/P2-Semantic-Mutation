/*
 * C-BOOSTMATH-001 verification: Boost.Math skew_normal quantile returns a
 * discontinuous invalid value (0 on Boost 1.69; -inf on 1.67) at an interior
 * probability, violating quantile monotonicity (issue boostorg/math#184;
 * fixed by PR #1080 "Reinstate root finding protection against huge jumps",
 * merged 2024-02-06, first released in Boost 1.85).
 *
 * issue oracle (m_mono/f_mono.shape): for fixed parameters, quantile(p) must be
 * monotone non-decreasing in p on (0,1) and finite for interior p. Battery:
 * (a) the issue's exact 3-point reproducer; (b) a monotone sweep across a
 * fine probability grid bracketing the failure point.
 *
 * Build (header-only): g++ -std=c++14 -I<boost root> this.cpp -o check
 */
#include <boost/math/distributions/skew_normal.hpp>
#include <boost/version.hpp>
#include <cstdio>
#include <cmath>
#include <vector>

int main()
{
  std::printf("Boost version: %s\n", BOOST_LIB_VERSION);
  boost::math::skew_normal skew(573.39724735636185, 77.0, 4.0);

  const double p1 = 0.00285612015554148;
  const double p2 = 0.00285612015554149; /* the issue's failing probability */
  const double p3 = 0.00285612015554150;

  double q1 = boost::math::quantile(skew, p1);
  double q2 = boost::math::quantile(skew, p2);
  double q3 = boost::math::quantile(skew, p3);
  std::printf("quantile(%.17g) = %.15g\n", p1, q1);
  std::printf("quantile(%.17g) = %.15g\n", p2, q2);
  std::printf("quantile(%.17g) = %.15g\n", p3, q3);

  bool mono3 = (q1 <= q2) && (q2 <= q3) && std::isfinite(q2);

  /* dense sweep bracketing the failure point */
  int viol = 0;
  double prev = -1e308, worst = 0.0, worst_p = 0.0;
  const double lo = 0.0028561201553, hi = 0.0028561201558;
  const int    N = 2001;
  for (int i = 0; i < N; i++) {
    double p = lo + (hi - lo) * i / (N - 1);
    double q = boost::math::quantile(skew, p);
    if (!std::isfinite(q) || q < prev - 1e-9) {
      viol++;
      double mag = std::isfinite(q) ? prev - q : 1e300;
      if (mag > worst) { worst = mag; worst_p = p; }
    }
    if (std::isfinite(q)) prev = q;
  }
  std::printf("dense sweep [%g,%g], %d pts: %d monotonicity/finiteness violations", lo, hi, N, viol);
  if (viol) std::printf(" (worst drop %.6g at p=%.17g)", worst, worst_p);
  std::printf("\n");

  if (!mono3 || viol)
    std::printf("issue-property VIOLATION: quantile is non-monotone/invalid at interior probabilities\n");
  else
    std::printf("issue-property SATISFIED: quantile monotone and finite across the battery\n");
  return (!mono3 || viol) ? 1 : 0;
}
