/* C2: Polynomial Chaos Expansion surrogate of tanh(t), t = 4x-2.
 *
 * C99 port of src/p2/puts/c2.py (sklearn PolynomialFeatures(5) +
 * LinearRegression). The sklearn ML stack is NOT used; the model is a
 * self-contained degree-5 ordinary least-squares polynomial fit solved
 * by normal equations (6x6 Gaussian elimination with partial pivoting).
 * Training design: 80 points uniform on [-2,2], target tanh(t); predict
 * at t = 4x-2.
 *
 * RNG CONTRACT: the Python reference samples the 80 training abscissae
 * from numpy PCG64 (default_rng(42)); the exact positions are not
 * reproducible in C99. This port draws them from an embedded LCG
 * (seed 42). Because a degree-5 least-squares fit of tanh over 80
 * well-spread points in [-2,2] is nearly design-invariant, agreement
 * with Python is close but DESIGN-DISTRIBUTIONAL, not machine-precision
 * (see C_PORT_SPEC.md achieved-agreement column).
 *
 * Pure C99 + libm. No ML library.
 */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define NTRAIN 80
#define DEG    5
#define NC     (DEG + 1)

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

static int    fitted = 0;
static double beta[NC];

static void fit(void) {
    double t[NTRAIN], y[NTRAIN];
    rng_seed(SEED);
    for (int i = 0; i < NTRAIN; i++) t[i] = -2.0 + 4.0 * u01();  /* uniform(-2,2) */
    qsort(t, NTRAIN, sizeof(double), cmp_double);
    for (int i = 0; i < NTRAIN; i++) y[i] = tanh(t[i]);
    /* normal equations: (M^T M) beta = M^T y, M columns = t^0..t^DEG */
    double A[NC][NC], rhs[NC];
    for (int a = 0; a < NC; a++) {
        rhs[a] = 0.0;
        for (int b = 0; b < NC; b++) A[a][b] = 0.0;
    }
    for (int i = 0; i < NTRAIN; i++) {
        double pow_i[NC];
        pow_i[0] = 1.0;
        for (int p = 1; p < NC; p++) pow_i[p] = pow_i[p - 1] * t[i];
        for (int a = 0; a < NC; a++) {
            rhs[a] += pow_i[a] * y[i];
            for (int b = 0; b < NC; b++) A[a][b] += pow_i[a] * pow_i[b];
        }
    }
    solve(A, rhs, beta);
    fitted = 1;
}

double program(double x) {
    if (!fitted) fit();
    double t = 4.0 * x - 2.0;
    double p = 1.0, y = 0.0;
    for (int i = 0; i < NC; i++) { y += beta[i] * p; p *= t; }
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
