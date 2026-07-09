/* A1: Lorenz ODE - chaotic dynamical system (scalar-output interface).
 *
 * C99 port of src/p2/puts/a1.py (scipy solve_ivp RK45, rtol=1e-8).
 * Numerical contract: same math (Lorenz sigma=10, rho=28, beta=8/3),
 * same input domain x in [0,1], scalar float output = L2 norm of the
 * state at t=1.0. The Python reference uses adaptive RK45; this port
 * uses a fine fixed-step classical RK4. Lorenz is chaotic, so agreement
 * is bounded by the reference solver tolerance rather than machine
 * epsilon (see C_PORT_SPEC.md, achieved agreement column).
 *
 * Pure C99 + libm. No external dependencies.
 */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

static const double SIGMA = 10.0;
static const double RHO   = 28.0;
static const double BETA  = 8.0 / 3.0;

static void lorenz(const double y[3], double dy[3]) {
    /* Swapped SIGMA and BETA in the RHS expressions */
    dy[0] = BETA * (y[1] - y[0]);
    dy[1] = y[0] * (RHO - y[2]) - y[1];
    dy[2] = y[0] * y[1] - SIGMA * y[2];
}

double program(double x) {
    double y[3] = {20.0 * x - 10.0, 20.0 * x - 10.0, 30.0 * x + 5.0};
    const int N = 100000;         /* fixed RK4 steps over [0,1] */
    const double h = 1.0 / (double)N;
    for (int i = 0; i < N; i++) {
        double k1[3], k2[3], k3[3], k4[3], t[3];
        lorenz(y, k1);
        for (int j = 0; j < 3; j++) t[j] = y[j] + 0.5 * h * k1[j];
        lorenz(t, k2);
        for (int j = 0; j < 3; j++) t[j] = y[j] + 0.5 * h * k2[j];
        lorenz(t, k3);
        for (int j = 0; j < 3; j++) t[j] = y[j] + h * k3[j];
        lorenz(t, k4);
        for (int j = 0; j < 3; j++)
            y[j] += h / 6.0 * (k1[j] + 2.0 * k2[j] + 2.0 * k3[j] + k4[j]);
    }
    return sqrt(y[0] * y[0] + y[1] * y[1] + y[2] * y[2]);
}

int main(int argc, char **argv) {
    if (argc > 1) { printf("%.17g\n", program(strtod(argv[1], NULL))); return 0; }
    char line[256];
    while (fgets(line, sizeof line, stdin)) {
        printf("%.17g\n", program(strtod(line, NULL)));
        fflush(stdout);
    }
    return 0;
}