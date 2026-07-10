// Study-5 Family-XL adapter shim (pair: hermite.cpp, Amendment A3).
// Adapter/oracle layer only: calls the unmodified external entry points
// (Boost.Math interpolators module, vendored headers); frozen aux
// documented in docs/prereg_v2/STUDY5_XL_ROSTER.md §A3.
#include <cstdio>
#include <cmath>
#include <vector>
#include <boost/math/interpolators/cubic_hermite.hpp>

static double program(double x) {
    const int n = 17;
    std::vector<double> t(n), y(n), dy(n);
    for (int j = 0; j < n; j++) {
        t[j] = j / 16.0;
        y[j] = std::exp(t[j]);
        dy[j] = std::exp(t[j]);   // exact derivative of exp (frozen aux)
    }
    auto h = boost::math::interpolators::cubic_hermite<std::vector<double>>(
        std::move(t), std::move(y), std::move(dy));
    return h(x);
}

int main() {
    char buf[256];
    double x, y;
    while (std::fgets(buf, sizeof buf, stdin)) {
        if (std::sscanf(buf, "%lf", &x) != 1) continue;
        y = program(x);
        std::printf("%.17g\n", y);
        std::fflush(stdout);
    }
    return 0;
}
