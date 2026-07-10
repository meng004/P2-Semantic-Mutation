// Study-5 Family-XL adapter shim (pair: simpson.cpp). Adapter/oracle layer only:
// calls the unmodified external entry point(s); frozen aux documented in
// docs/prereg_v2/STUDY5_XL_ROSTER.md.
#include <cstdio>
#include <cmath>
#include <functional>

#define main xl_ext_main
#include "third_party/thealgorithms-cpp/numerical_methods/composite_simpson_rule.cpp"
#undef main

static double program(double x) {
    double c = std::pow(2.0, 2.0 * x - 1.0);
    double h = c / 16.0;
    std::function<double(double)> sq = [](double u) { return u * u; };
    return numerical_methods::simpson_method::evaluate_by_simpson(16, h, 0.0, sq);
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
