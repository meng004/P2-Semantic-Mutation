// Study-5 Family-XL adapter shim (pair: besselj0.cpp). Adapter/oracle layer only:
// calls the unmodified external entry point(s); frozen aux documented in
// docs/prereg_v2/STUDY5_XL_ROSTER.md.
#include <cstdio>
#include <cmath>
#include <boost/math/special_functions/bessel.hpp>

static double program(double x) {
    return boost::math::cyl_bessel_j(0, 8.0 * x - 4.0);
}

int main() {
    char buf[256];
    double x = 0.0, y = 0.0;
    while (std::fgets(buf, sizeof buf, stdin)) {
        if (std::sscanf(buf, "%lf", &x) != 1) continue;
        try { y = program(x); } catch (...) { y = std::nan(""); }
        std::printf("%.17g\n", y);
        std::fflush(stdout);
    }
    return 0;
}
