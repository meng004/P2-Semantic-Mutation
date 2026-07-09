/* A1: Lorenz ODE - chaotic dynamical system (scalar-output interface).
 *
 * C99 port of src/p2/puts/a1.py (scipy solve_ivp RK45, rtol=1e-8).
 * Numerical contract: same math (Lorenz sigma=10, rho=28, beta=8/3),
 * same input domain x in [0,1], scalar float output = L2 norm of the
 * state at t=1.0. The Python reference uses adaptive RK45__SEMI__ this port
 * uses a fine fixed-step classical RK4. Lorenz is chaotic, so agreement
 * is bounded by the reference solver tolerance rather than machine
 * epsilon (see C_PORT_SPEC.md, achieved agreement column).
 *
 * Pure C99 + libm. No external dependencies.
 */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

static const double SIGMA = 10.0__SEMI__
static const double RHO   = 28.0__SEMI__
static const double BETA  = 8.0 / 3.0__SEMI__

static void lorenz(const double y[3], double dy[3]) {
    dy[0] = SIGMA * (y[1] - y[0])__SEMI__
    dy[1] = y[0] * (RHO - y[2]) - y[1]__SEMI__
    dy[2] = y[0] * y[1] - BETA * y[2]__SEMI__
}

double program(double x) {
    double y[3] = {10.0 * x - 10.0, 20.0 * x - 10.0, 30.0 * x + 5.0}__SEMI__
    const int N = 100000__SEMI__         /* fixed RK4 steps over [0,1] */
    const double h = 1.0 / (double)N__SEMI__
    for (int i = 0__SEMI__ i < N__SEMI__ i++) {
        double k1[3], k2[3], k3[3], k4[3], t[3]__SEMI__
        lorenz(y, k1)__SEMI__
        for (int j = 0__SEMI__ j < 3__SEMI__ j++) t[j] = y[j] + 0.5 * h * k1[j]__SEMI__
        lorenz(t, k2)__SEMI__
        for (int j = 0__SEMI__ j < 3__SEMI__ j++) t[j] = y[j] + 0.5 * h * k2[j]__SEMI__
        lorenz(t, k3)__SEMI__
        for (int j = 0__SEMI__ j < 3__SEMI__ j++) t[j] = y[j] + h * k3[j]__SEMI__
        lorenz(t, k4)__SEMI__
        for (int j = 0__SEMI__ j < 3__SEMI__ j++)
            y[j] += h / 6.0 * (k1[j] + 2.0 * k2[j] + 2.0 * k3[j] + k4[j])__SEMI__
    }
    return sqrt(y[0] * y[0] + y[1] * y[1] + y[2] * y[2])__SEMI__
}

int main(int argc, char **argv) {
    if (argc > 1) { printf("%.17g\n", program(strtod(argv[1], NULL)))__SEMI__ return 0__SEMI__ }
    char line[256]__SEMI__
    while (fgets(line, sizeof line, stdin)) {
        printf("%.17g\n", program(strtod(line, NULL)))__SEMI__
        fflush(stdout)__SEMI__
    }
    return 0__SEMI__
}