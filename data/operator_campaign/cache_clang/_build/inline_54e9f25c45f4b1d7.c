/* C2: Polynomial Chaos Expansion surrogate of tanh(t), t = 4x-2.
 *
 * C99 port of src/p2/puts/c2.py (sklearn PolynomialFeatures(5) +
 * LinearRegression). The sklearn ML stack is NOT used.
 *
 * MUTANT: c2_OS1 (basis poly -> spline).
 * Replaced PolynomialFeatures(5, include_bias=True) with SplineTransformer(n_knots=6, degree=3).
 * Under the hood, SplineTransformer(n_knots=6, degree=3) produces a cubic B-spline basis
 * over the interval [-2, 2] with 6 knots (yielding 4 intervals, and 4 + 3 = 7 basis functions).
 * We implement the 7-dimensional cubic B-spline basis functions over the domain [-2, 2].
 *
 * Pure C99 + libm. No ML library.
 */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define NTRAIN 80
#define NC     7

static const unsigned long long SEED = 42ULL;

static unsigned long long rng_state;
static void   rng_seed(unsigned long long s) { rng_state = s ? s : 0x9E3779B97F4A7C15ULL; }
static double u01(void) {
    rng_state = rng_state * 6364136223846793005ULL + 1442695040888963407ULL;
    return (double)(rng_state >> 11) * (1.0 / 9007199254740992.0);
}

static int cmp_double(const void *a, const void *b) {
    double da = *(const double *)a, db = *(const double *)b;
    return (da > db) - (da < db);
}

/* Solve NC x NC linear system A beta = rhs by Gaussian elimination with
 * partial pivoting. A is row-major. Returns 0 on success. */
static int solve(double A[NC][NC], double rhs[NC], double beta_out[NC]) {
    for (int col = 0; col < NC; col++) {
        int piv = col;
        for (int r = col + 1; r < NC; r++)
            if (fabs(A[r][col]) > fabs(A[piv][col])) piv = r;
        if (fabs(A[piv][col]) < 1e-300) return 1;
        if (piv != col) {
            for (int c = 0; c < NC; c++) { double t = A[col][c]; A[col][c] = A[piv][c]; A[piv][c] = t; }
            double t = rhs[col]; rhs[col] = rhs[piv]; rhs[piv] = t;
        }
        for (int r = col + 1; r < NC; r++) {
            double f = A[r][col] / A[col][col];
            for (int c = col; c < NC; c++) A[r][c] -= f * A[col][c];
            rhs[r] -= f * rhs[col];
        }
    }
    for (int r = NC - 1; r >= 0; r--) {
        double s = rhs[r];
        for (int c = r + 1; c < NC; c++) s -= A[r][c] * beta_out[c];
        beta_out[r] = s / A[r][r];
    }
    return 0;
}

/* Evaluates the 7 cubic B-spline basis functions for 6 knots uniformly distributed
 * on [-2, 2] (knots at -2, -1, 0, 1, 2) plus clamped boundary knots. */
static void evaluate_splines(double t, double basis[NC]) {
    double knots[12] = { -2.0, -2.0, -2.0, -2.0, -1.0, 0.0, 1.0, 2.0, 2.0, 2.0, 2.0, 2.0 };
    double d[12];
    for (int i = 0; i < 11; i++) {
        d[i] = (t >= knots[i] && t < knots[i+1]) ? 1.0 : 0.0;
    }
    if (t >= 2.0) {
        d[7] = 1.0;
    }
    for (int degree = 1; degree <= 3; degree++) {
        for (int i = 0; i < 11 - degree; i++) {
            double w1 = 0.0, w2 = 0.0;
            if (knots[i+degree] != knots[i]) {
                w1 = (t - knots[i]) / (knots[i+degree] - knots[i]) * d[i];
            }
            if (knots[i+degree+1] != knots[i+1]) {
                w2 = (knots[i+degree+1] - t) / (knots[i+degree+1] - knots[i+1]) * d[i+1];
            }
            d[i] = w1 + w2;
        }
    }
    for (int i = 0; i < NC; i++) {
        basis[i] = d[i];
    }
}

static int    fitted = 0;
static double beta[NC];

static void fit(void) {
    double t[NTRAIN], y[NTRAIN];
    rng_seed(SEED);
    for (int i = 0; i < NTRAIN; i++) t[i] = -2.0 + 4.0 * u01();
    qsort(t, NTRAIN, sizeof(double), cmp_double);
    for (int i = 0; i < NTRAIN; i++) y[i] = tanh(t[i]);

    double A[NC][NC], rhs[NC];
    for (int a = 0; a < NC; a++) {
        rhs[a] = 0.0;
        for (int b = 0; b < NC; b++) A[a][b] = 0.0;
    }
    for (int i = 0; i < NTRAIN; i++) {
        double basis[NC];
        evaluate_splines(t[i], basis);
        for (int a = 0; a < NC; a++) {
            rhs[a] += basis[a] * y[i];
            for (int b = 0; b < NC; b++) A[a][b] += basis[a] * basis[b];
        }
    }
    solve(A, rhs, beta);
    fitted = 1;
}

double program(double x) {
    if (!fitted) fit();
    double t = 4.0 * x - 2.0;
    double basis[NC];
    evaluate_splines(t, basis);
    double y = 0.0;
    for (int i = 0; i < NC; i++) { y += beta[i] * basis[i]; }
    return y;
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