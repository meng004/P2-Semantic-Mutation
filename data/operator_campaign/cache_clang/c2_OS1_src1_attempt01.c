#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define NTRAIN 80
#define N_KNOTS 6
#define SPLINE_DEGREE 3
#define NC (N_KNOTS + SPLINE_DEGREE - 1)
#define NKNOT_EXT (NC + SPLINE_DEGREE + 1)

static const unsigned long long SEED = 42ULL;

static unsigned long long rng_state;

static void rng_seed(unsigned long long s) {
    rng_state = s ? s : 0x9E3779B97F4A7C15ULL;
}

static double u01(void) {
    rng_state = rng_state * 6364136223846793005ULL + 1442695040888963407ULL;
    return (double)(rng_state >> 11) * (1.0 / 9007199254740992.0);
}

static int cmp_double(const void *a, const void *b) {
    double da = *(const double *)a;
    double db = *(const double *)b;
    return (da > db) - (da < db);
}

static int solve(double A[NC][NC], double rhs[NC], double beta[NC]) {
    for (int col = 0; col < NC; col++) {
        int piv = col;
        for (int r = col + 1; r < NC; r++) {
            if (fabs(A[r][col]) > fabs(A[piv][col])) {
                piv = r;
            }
        }
        if (fabs(A[piv][col]) < 1e-300) {
            return 1;
        }
        if (piv != col) {
            for (int c = 0; c < NC; c++) {
                double t = A[col][c];
                A[col][c] = A[piv][c];
                A[piv][c] = t;
            }
            double t = rhs[col];
            rhs[col] = rhs[piv];
            rhs[piv] = t;
        }
        for (int r = col + 1; r < NC; r++) {
            double f = A[r][col] / A[col][col];
            for (int c = col; c < NC; c++) {
                A[r][c] -= f * A[col][c];
            }
            rhs[r] -= f * rhs[col];
        }
    }

    for (int r = NC - 1; r >= 0; r--) {
        double s = rhs[r];
        for (int c = r + 1; c < NC; c++) {
            s -= A[r][c] * beta[c];
        }
        beta[r] = s / A[r][r];
    }
    return 0;
}

static int fitted = 0;
static double beta[NC];
static double ext_knots[NKNOT_EXT];
static double domain_lo = 0.0;
static double domain_hi = 0.0;

static double bspline_basis(int i, int degree, double z) {
    if (degree == 0) {
        return (ext_knots[i] <= z && z < ext_knots[i + 1]) ? 1.0 : 0.0;
    }

    double v = 0.0;
    double left_den = ext_knots[i + degree] - ext_knots[i];
    double right_den = ext_knots[i + degree + 1] - ext_knots[i + 1];

    if (left_den != 0.0) {
        v += ((z - ext_knots[i]) / left_den) * bspline_basis(i, degree - 1, z);
    }
    if (right_den != 0.0) {
        v += ((ext_knots[i + degree + 1] - z) / right_den) * bspline_basis(i + 1, degree - 1, z);
    }
    return v;
}

static void spline_features(double z, double out[NC]) {
    if (z < domain_lo) {
        z = domain_lo;
    } else if (z > domain_hi) {
        z = domain_hi;
    }

    if (z == domain_hi) {
        z = nextafter(z, domain_lo);
    }

    for (int j = 0; j < NC; j++) {
        out[j] = bspline_basis(j, SPLINE_DEGREE, z);
    }
}

static void make_knots(double lo, double hi) {
    domain_lo = lo;
    domain_hi = hi;

    double h = (hi - lo) / (double)(N_KNOTS - 1);

    for (int i = 0; i < SPLINE_DEGREE; i++) {
        ext_knots[i] = lo - h * (double)(SPLINE_DEGREE - i);
    }
    for (int i = 0; i < N_KNOTS; i++) {
        ext_knots[SPLINE_DEGREE + i] = lo + h * (double)i;
    }
    for (int i = 0; i < SPLINE_DEGREE; i++) {
        ext_knots[SPLINE_DEGREE + N_KNOTS + i] = hi + h * (double)(i + 1);
    }
}

static void fit(void) {
    double t[NTRAIN];
    double y[NTRAIN];

    rng_seed(SEED);
    for (int i = 0; i < NTRAIN; i++) {
        t[i] = -2.0 + 4.0 * u01();
    }

    qsort(t, NTRAIN, sizeof(double), cmp_double);

    for (int i = 0; i < NTRAIN; i++) {
        y[i] = tanh(t[i]);
    }

    make_knots(t[0], t[NTRAIN - 1]);

    double A[NC][NC];
    double rhs[NC];

    for (int a = 0; a < NC; a++) {
        rhs[a] = 0.0;
        beta[a] = 0.0;
        for (int b = 0; b < NC; b++) {
            A[a][b] = 0.0;
        }
    }

    for (int i = 0; i < NTRAIN; i++) {
        double phi[NC];
        spline_features(t[i], phi);

        for (int a = 0; a < NC; a++) {
            rhs[a] += phi[a] * y[i];
            for (int b = 0; b < NC; b++) {
                A[a][b] += phi[a] * phi[b];
            }
        }
    }

    if (solve(A, rhs, beta) != 0) {
        for (int i = 0; i < NC; i++) {
            beta[i] = 0.0;
        }
    }

    fitted = 1;
}

double program(double x) {
    if (!fitted) {
        fit();
    }

    double t = 4.0 * x - 2.0;
    double phi[NC];
    double y = 0.0;

    spline_features(t, phi);

    for (int i = 0; i < NC; i++) {
        y += beta[i] * phi[i];
    }

    return y;
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