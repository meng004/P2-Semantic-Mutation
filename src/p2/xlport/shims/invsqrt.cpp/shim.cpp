// Study-5 Family-XL adapter shim (pair: invsqrt.cpp). Adapter/oracle layer only:
// calls the unmodified external entry point(s); frozen aux documented in
// docs/prereg_v2/STUDY5_XL_ROSTER.md.
#include <cstdio>
#include <cmath>


#define main xl_ext_main
#include "third_party/thealgorithms-cpp/math/inv_sqrt.cpp"
#undef main

static double program(double x) {
    float u = (float)std::pow(4.0, 2.0 * x - 1.0);
    return (double)Fast_InvSqrt<float, 1>(u);
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
