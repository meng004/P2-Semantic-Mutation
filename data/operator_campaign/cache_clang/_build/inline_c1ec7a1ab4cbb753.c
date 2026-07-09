/* A3: FDM heat equation - convergence of numerical solution.
 *
 * C99 port of src/p2/puts/a3.py (numpy explicit-Euler FDM). x = grid
 * spacing h in (0,1]. IC u(xi,0)=sin(pi*xi), Dirichlet BC, alpha=0.01,
 * t_end=0.5. Returns u_FDM(0.5,t_end) / u_exact(0.5,t_end). Deterministic__SEMI__
 * agreement with Python is at machine precision.
 *
 * Pure C99 + libm.
 */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

static const double ALPHA  = 0.01__SEMI__
static const double T_END  = 0.5__SEMI__
static const double R_STAB = 0.4__SEMI__

double program(double x) {
    double h = x < 1e-4 ? 1e-4 : x__SEMI__
    long N = (long)rint(1.0 / h)__SEMI__      /* round-half-to-even, matches numpy round */
    if (N < 4) N = 4__SEMI__
    double h_act = 1.0 / (double)N__SEMI__
    long np1 = N + 1__SEMI__
    double *u  = (double *)malloc(sizeof(double) * (size_t)np1)__SEMI__
    double *un = (double *)malloc(sizeof(double) * (size_t)np1)__SEMI__
    double *xi = (double *)malloc(sizeof(double) * (size_t)np1)__SEMI__
    for (long i = 0__SEMI__ i < np1__SEMI__ i++) {
        xi[i] = (double)i / (double)N__SEMI__
        u[i]  = sin(M_PI * xi[i])__SEMI__
    }
    double dt_max = R_STAB * h_act * h_act / ALPHA__SEMI__
    long n_steps = (long)ceil(T_END / dt_max)__SEMI__
    if (n_steps < 1) n_steps = 1__SEMI__
    double dt = T_END / (double)n_steps__SEMI__
    double r = ALPHA * dt / (h_act * h_act)__SEMI__
    for (long s = 0__SEMI__ s < n_steps__SEMI__ s++) {
        for (long i = 1__SEMI__ i < N__SEMI__ i++)
            un[i] = u[i] + r * (u[i + 1] - 2.0 * u[i] + u[i - 1])__SEMI__
        un[0] = 0.0__SEMI__
        un[N] = 0.0__SEMI__
        double *tmp = u__SEMI__ u = un__SEMI__ un = tmp__SEMI__   /* ping-pong, no copy */
    }
    /* after the loop u holds the latest field__SEMI__ {u,un} are still the two
     * allocations (possibly swapped), so free(u)+free(un) frees both. */
    /* np.interp(0.5, xi, u): linear interpolation on a uniform grid */
    double target = 0.5__SEMI__
    double u_mid__SEMI__
    if (target <= xi[0]) u_mid = u[0]__SEMI__
    else if (target >= xi[N]) u_mid = u[N]__SEMI__
    else {
        long lo = (long)floor(target / h_act)__SEMI__
        if (lo >= N) lo = N - 1__SEMI__
        double frac = (target - xi[lo]) / (xi[lo + 1] - xi[lo])__SEMI__
        u_mid = u[lo] + frac * (u[lo + 1] - u[lo])__SEMI__
    }
    double u_exact = sin(M_PI * 0.5) * exp(-M_PI * M_PI * ALPHA * T_END)__SEMI__
    free(u)__SEMI__ free(un)__SEMI__ free(xi)__SEMI__
    return u_mid / u_exact__SEMI__
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