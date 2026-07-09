#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

static const double ALPHA  = 0.01;
static const double T_END  = 0.5;
static const double R_STAB = 0.4;

double program(double x) {
    double h = x < 1e-4 ? 1e-4 : x;
    long N = (long)rint(1.0 / h);
    if (N < 4) N = 4;
    double h_act = 1.0 / (double)N;
    long np1 = N + 1;

    double *u  = (double *)malloc(sizeof(double) * (size_t)np1);
    double *un = (double *)malloc(sizeof(double) * (size_t)np1);
    double *xi = (double *)malloc(sizeof(double) * (size_t)np1);

    for (long i = 0; i < np1; i++) {
        xi[i] = (double)i / (double)N;
        u[i]  = sin(M_PI * xi[i]);
    }

    double dt_max = R_STAB * h_act * h_act / ALPHA;
    long n_steps = (long)ceil(T_END / dt_max);
    if (n_steps < 1) n_steps = 1;
    double dt = T_END / (double)n_steps;
    double r = ALPHA * dt / (h_act * h_act);

    for (long s = 0; s < n_steps; s++) {
        for (long i = 1; i < N; i++) {
            double lap = -(u[i + 1] - 2.0 * u[i] + u[i - 1]);
            un[i] = u[i] + r * lap;
        }
        un[0] = 0.0;
        un[N] = 0.0;
        double *tmp = u;
        u = un;
        un = tmp;
    }

    double target = 0.5;
    double u_mid;
    if (target <= xi[0]) {
        u_mid = u[0];
    } else if (target >= xi[N]) {
        u_mid = u[N];
    } else {
        long lo = (long)floor(target / h_act);
        if (lo >= N) lo = N - 1;
        double frac = (target - xi[lo]) / (xi[lo + 1] - xi[lo]);
        u_mid = u[lo] + frac * (u[lo + 1] - u[lo]);
    }

    double u_exact = sin(M_PI * 0.5) * exp(-M_PI * M_PI * ALPHA * T_END);

    free(u);
    free(un);
    free(xi);

    return u_mid / u_exact;
}

int main(int argc, char **argv) {
    if (argc > 1) {
        printf("%.17g\n", program(strtod(argv[1], NULL)));
        return 0;
    }

    char line[256];
    while (fgets(line, sizeof line, stdin)) {
        printf("%.17g\n", program(strtod(line, NULL)));
        fflush(stdout);
    }

    return 0;
}