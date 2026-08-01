/* C-DEALII-001 issue-property driver v2 (m_conv / f_conv.rate): volume of a domain with
 * one curved (SphericalManifold) face under MappingQGeneric, mixed with flat
 * interior manifolds -- the exact scenario of the regression test
 * tests/mappings/mapping_q_mixed_manifolds_01.cc added by the fix commit
 * 92a06f62 ("Unify interpolation from surrounding points").
 *
 * Geometry: unit square shifted to x in [0.5,1.5]; face x=0.5 assigned a
 * SphericalManifold centered at the origin (vertices at radius sqrt(0.5)),
 * so the face bulges into the cell along the circle.  Exact area:
 *   1 - 0.25*(pi/2 - 1)  (square minus circular segment, R^2=0.5, theta=90deg)
 *
 * Oracle (f_conv.rate): the quadrature volume sum(JxW) under a degree-p
 * mapping must converge to the analytic volume (a) as the mapping degree
 * rises at fixed mesh and (b) as the mesh is refined at fixed degree, at
 * high order.  The buggy support-point placement pollutes interior points
 * of cells touching the curved face, so the volume error stagnates or
 * converges at a degraded order.
 *
 * NOTE (documented in the report): the companion driver
 * mixed_manifold_rate.cc showed that the L2 *solution* rate for the
 * boundary-only-manifold annulus stays ~3.5 on BOTH v8.4.2 and v8.5.0 --
 * the fix's own class documentation states the smoothing cannot exceed
 * ~3.5 there (fully cured only by TransfiniteInterpolationManifold in 9.0).
 * The geometric-volume observable below is what the fix itself changed and
 * regression-tests.
 */
#include <deal.II/base/quadrature_lib.h>
#include <deal.II/fe/fe_nothing.h>
#include <deal.II/fe/fe_values.h>
#include <deal.II/fe/mapping_q_generic.h>
#include <deal.II/grid/grid_generator.h>
#include <deal.II/grid/grid_tools.h>
#include <deal.II/grid/manifold_lib.h>
#include <deal.II/grid/tria.h>

#include <cmath>
#include <cstdio>
#include <vector>

using namespace dealii;

static const double reference_area = 1. - 0.25 * (0.5 * numbers::PI - 1.);

static double volume_error(const unsigned int degree,
                           const unsigned int n_refines,
                           const SphericalManifold<2> &manifold)
{
  Triangulation<2> tria;
  GridGenerator::hyper_cube(tria, -0.5, 0.5);
  Tensor<1, 2> shift;
  shift[0] = 1.;
  GridTools::shift(shift, tria);
  tria.begin()->face(0)->set_all_manifold_ids(1);
  tria.set_manifold(1, manifold);
  if (n_refines > 0)
    tria.refine_global(n_refines);

  FE_Nothing<2>       fe;
  MappingQGeneric<2>  mapping(degree);
  QGauss<2>           quad(degree + 1);
  FEValues<2> fe_values(mapping, fe, quad, update_JxW_values);
  double sum = 0.;
  for (Triangulation<2>::active_cell_iterator cell = tria.begin_active();
       cell != tria.end(); ++cell)
    {
      fe_values.reinit(cell);
      for (unsigned int q = 0; q < quad.size(); ++q)
        sum += fe_values.JxW(q);
    }
  return (sum - reference_area) / reference_area;
}

int main()
{
  std::printf("deal.II %s  reference area %.15f\n", DEAL_II_PACKAGE_VERSION,
              reference_area);
  SphericalManifold<2> manifold; // centered at origin

  std::printf("-- degree sweep (mesh refinement 1):\n");
  double prev = 0;
  for (unsigned int degree = 2; degree <= 6; ++degree)
    {
      const double e = volume_error(degree, 1, manifold);
      std::printf("degree=%u  relerr=%+.6e", degree, e);
      if (degree > 2 && e != 0.)
        std::printf("  ratio=%.3g", std::fabs(prev / e));
      std::printf("\n");
      prev = e;
    }

  std::printf("-- h sweep (mapping degree 4):\n");
  std::vector<double> err;
  for (unsigned int L = 0; L <= 5; ++L)
    {
      const double e = std::fabs(volume_error(4, L, manifold));
      err.push_back(e);
      std::printf("L=%u  |relerr|=%.6e", L, e);
      if (L > 0 && e > 0)
        std::printf("  slope=%.3f", std::log2(err[L - 1] / e));
      std::printf("\n");
    }

  // the fix's own regression value: degree 6, unrefined test grid ->
  // relerr 5.06e-06 (see mapping_q_mixed_manifolds_01.output)
  const double e6 = volume_error(6, 0, manifold);
  std::printf("degree=6 L=0 relerr=%+.6e (regression reference +5.06446e-06)\n",
              e6);

  const double s_last = err[5] > 0 ? std::log2(err[4] / err[5]) : 99;
  const bool bad = std::fabs(e6) > 1e-4 || s_last < 3.0;
  std::printf("### VERDICT: %s\n", bad ? "GEOMETRY CONVERGENCE VIOLATED" : "PASS");
  return 0;
}
