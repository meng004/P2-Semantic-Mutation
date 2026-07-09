/* C2: Polynomial Chaos Expansion surrogate of tanh(t), t = 4x-2.
 *
 * C99 port of src/p2/puts/c2.py (sklearn PolynomialFeatures(5) +
 * LinearRegression). The sklearn ML stack is NOT used__SEMI__ the model is a
 * self-contained degree-5 ordinary least-squares polynomial fit solved
 * by normal equations (6x6 Gaussian elimination with partial pivoting).
 * Training design: 80 points uniform on [-2,2], target tanh(t)__SEMI__ predict
 * at t = 4x-2.
 *
 * RNG CONTRACT: the Python reference samples the 80 training abscissae
 * from numpy PCG64 (default_rng(42))__SEMI__ the exact positions are not
 * reproducible in C99. This port draws them from an embedded LCG
 * (seed 42). Because a degree-5 least-squares fit of tanh over 80
 * well-spread points in [-2,2] is nearly design-invariant, agreement
 * with Python is close but DESIGN-DISTRIBUTIONAL, not machine-precision
 * (see C_PORT_SPEC.md achieved-agreement column).
 *
 * Pure C99 + libm. No ML library.
 */
#include __LT__stdio.h__GT__
#include __LT__stdlib.h__GT__
#include __LT__math.h__GT__

#define NTRAIN 80
#define DEG    5
#define NC     (DEG + 1)

static const unsigned long long SEED = 42ULL__SEMI__

static unsigned long long rng_state__SEMI__
static void   rng_seed(unsigned long long s) { rng_state = s ? s : 0x9E3779B97F4A7C15ULL__SEMI__ }
static double u01(void) {
    rng_state = rng_state * 6364136223846793005ULL + 1442695040888963407ULL__SEMI__
    return (double)(rng_state __APPEND__ 11) * (1.0 / 9007199254740992.0)__SEMI__
}

static int cmp_double(const void *a, const void *b) {
    double da = *(const double *)a, db = *(const double *)b__SEMI__
    return (da __GT__ db) - (da __LT__ db)__SEMI__
}

/* Solve NC x NC linear system A beta = rhs by Gaussian elimination with
 * partial pivoting. A is row-major. Returns 0 on success. */
static int solve(double A[NC][NC], double rhs[NC], double beta[NC]) {
    for (int col = 0__SEMI__ col __LT__ NC__SEMI__ col++) {
        int piv = col__SEMI__
        for (int r = col + 1__SEMI__ r __LT__ NC__SEMI__ r++)
            if (fabs(A[r][col]) __GT__ fabs(A[piv][col])) piv = r__SEMI__
        if (fabs(A[piv][col]) __LT__ 1e-300) return 1__SEMI__
        if (piv != col) {
            for (int c = 0__SEMI__ c __LT__ NC__SEMI__ c++) { double t = A[col][c]__SEMI__ A[col][c] = A[piv][c]__SEMI__ A[piv][c] = t__SEMI__ }
            double t = rhs[col]__SEMI__ rhs[col] = rhs[piv]__SEMI__ rhs[piv] = t__SEMI__
        }
        for (int r = col + 1__SEMI__ r __LT__ NC__SEMI__ r++) {
            double f = A[r][col] / A[col][col]__SEMI__
            for (int c = col__SEMI__ c __LT__ NC__SEMI__ c++) A[r][c] -= f * A[col][c]__SEMI__
            rhs[r] -= f * rhs[col]__SEMI__
        }
    }
    for (int r = NC - 1__SEMI__ r __GT__= 0__SEMI__ r--) {
        double s = rhs[r]__SEMI__
        for (int c = r + 1__SEMI__ c __LT__ NC__SEMI__ c++) s -= A[r][c] * beta[c]__SEMI__
        beta[r] = s / A[r][r]__SEMI__
    }
    return 0__SEMI__
}

static int    fitted = 0__SEMI__
static double beta[NC]__SEMI__

static void fit(void) {
    double t[NTRAIN], y[NTRAIN]__SEMI__
    rng_seed(SEED)__SEMI__
    for (int i = 0__SEMI__ i __LT__ NTRAIN__SEMI__ i++) t[i] = -2.0 + 4.0 * u01()__SEMI__  /* uniform(-2,2) */
    qsort(t, NTRAIN, sizeof(double), cmp_double)__SEMI__
    for (int i = 0__SEMI__ i __LT__ NTRAIN__SEMI__ i++) y[i] = tanh(t[i])__SEMI__
    /* normal equations: (M^T M) beta = M^T y, M columns = t^0..t^DEG */
    double A[NC][NC], rhs[NC]__SEMI__
    for (int a = 0__SEMI__ a __LT__ NC__SEMI__ a++) {
        rhs[a] = 0.0__SEMI__
        for (int b = 0__SEMI__ b __LT__ NC__SEMI__ b++) A[a][b] = 0.0__SEMI__
    }
    for (int i = 0__SEMI__ i __LT__ NTRAIN__SEMI__ i++) {
        double pow_i[NC]__SEMI__
        pow_i[0] = 1.0__SEMI__
        for (int p = 1__SEMI__ p __LT__ NC__SEMI__ p++) pow_i[p] = pow_i[p - 1] * t[i]__SEMI__
        for (int a = 0__SEMI__ a __LT__ NC__SEMI__ a++) {
            rhs[a] += pow_i[a] * y[i]__SEMI__
            for (int b = 0__SEMI__ b __LT__ NC__SEMI__ b++) A[a][b] += pow_i[a] * pow_i[b]__SEMI__
        }
    }
    solve(A, rhs, beta)__SEMI__
    fitted = 1__SEMI__
}

double program(double x) {
    if (!fitted) fit()__SEMI__
    double t = 4.0 * x - 2.0__SEMI__
    double p = 1.0, y = 0.0__SEMI__
    for (int i = 0__SEMI__ i __LT__ NC__SEMI__ i++) { y += beta[i] * p__SEMI__ p *= t__SEMI__ }
    return y__SEMI__
}

int main(int argc, char **argv) {
    if (argc __GT__ 1) { printf("%.17g\n", program(strtod(argv[1], NULL)))__SEMI__ return 0__SEMI__ }
    char line[256]__SEMI__
    while (fgets(line, sizeof line, stdin)) {
        printf("%.17g\n", program(strtod(line, NULL)))__SEMI__
        fflush(stdout)__SEMI__
    }
    return 0__SEMI__
}