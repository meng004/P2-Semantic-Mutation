/* C2: B-Spline Basis Expansion surrogate of tanh(t), t = 4x-2.
 *
 * MUTANT: basis poly -> spline (SplineTransformer(n_knots=6, degree=3)).
 * Replaces PolynomialFeatures(5, include_bias=True) with a B-Spline 
 * representation of degree 3 with 6 uniform knots on [-2.0, 2.0].
 * Number of spline basis functions = n_knots + degree - 2 = 6 + 3 - 2 = 7.
 *
 * Knots are uniformly spaced in [-2.0, 2.0]:
 * t_0 = -2.0, t_1 = -1.2, t_2 = -0.4, t_3 = 0.4, t_4 = 1.2, t_5 = 2.0.
 * To support full evaluation on [-2.0, 2.0], we define the augmented
 * knot vector with clamped boundaries:
 * T = {-2.0, -2.0, -2.0, -2.0, -1.2, -0.4, 0.4, 1.2, 2.0, 2.0, 2.0, 2.0}.
 */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define NTRAIN 80
#define DEG    3
#define NKNOTS 6
#define NC     (NKNOTS + DEG - 2)

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
static int solve(double A[NC][NC], double rhs[NC], double beta[NC]) {
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
        for (int c = r + 1; c < NC; c++) s -= A[r][c] * beta[c];
        beta[r] = s / A[r][r];
    }
    return 0;
}

/* Evaluates the B-spline basis functions at coordinate u.
 * Knots are clamped at boundaries: -2.0 and 2.0. */
static void get_spline_basis(double u, double N[NC]) {
    double knots[12] = {
        -2.0, -2.0, -2.0, -2.0,
        -1.2, -0.4,  0.4,  1.2,
         2.0,  2.0,  2.0,  2.0
    };
    /* Handle boundary values to avoid division by zero or out-of-bounds */
    if (u <= -2.0) u = -2.0 + 1e-15;
    if (u >=  2.0) u =  2.0 - 1e-15;

    for (int i = 0; i < NC; i++) {
        N[i] = (u >= knots[i] && u < knots[i + 1]) ? 1.0 : 0.0;
    }

    for (int d = 1; d <= DEG; d++) {
        for (int i = 0; i < NC; i++) {
            double denom1 = knots[i + d] - knots[i];
            double denom2 = knots[i + d + 1] - knots[i + 1];
            double term1 = 0.0;
            double term2 = 0.0;
            if (denom1 > 1e-12) {
                term1 = ((u - knots[i]) / denom1) * N[i];
            }
            if (denom2 > 1e-12) {
                term2 = ((knots[i + d + 1] - u) / denom2) * N[i + 1];
            }
            N[i] = term1 + term2;
        }
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
        get_spline_basis(t[i], basis);
        for (int a = 0; a < NC; a++) {
            rhs[a] += basis[a] * y[i];
            for (int b = 0; b < NC; b++) {
                A[a][b] += basis[a] * basis[b];
            }
        }
    }
    solve(A, rhs, beta);
    fitted = 1;
}

double program(double x) {
    if (!fitted) fit();
    double t = 4.0 * x - 2.0;
    double basis[NC];
    get_spline_basis(t, basis);
    double y = 0.0;
    for (int i = 0; i < NC; i++) {
        y += beta[i] * basis[i];
    }
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