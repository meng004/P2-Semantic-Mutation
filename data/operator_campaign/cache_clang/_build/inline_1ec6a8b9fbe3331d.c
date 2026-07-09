#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define NTRAIN 80
#define SPLINE_DEGREE 3
#define N_KNOTS 6
#define NC (N_KNOTS + SPLINE_DEGREE - 1)
#define KNOT_COUNT (N_KNOTS + 2 * SPLINE_DEGREE)

static const unsigned long long SEED = 42ULL;

static unsigned long long rng_state;

static void rng_seed(unsigned long long s)
{
    rng_state = s ? s : 0x9E3779B97F4A7C15ULL;
}

static double u01(void)
{
    rng_state = rng_state * 6364136223846793005ULL + 1442695040888963407ULL;
    return (double)(rng_state >> 11) * (1.0 / 9007199254740992.0);
}

static int cmp_double(const void *a, const void *b)
{
    double da = *(const double *)a;
    double db = *(const double *)b;
    return (da > db) - (da < db);
}

static int solve(double A[NC][NC], double rhs[NC], double beta[NC])
{
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
                double tmp = A[col][c];
                A[col][c] = A[piv][c];
                A[piv][c] = tmp;
            }
            {
                double tmp = rhs[col];
                rhs[col] = rhs[piv];
                rhs[piv] = tmp;
            }
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
static double knots[KNOT_COUNT];

static void spline_basis(double z, double out[NC])
{
    double prev[KNOT_COUNT - 1];
    double next[KNOT_COUNT - 1];
    double lo = knots[SPLINE_DEGREE];
    double hi = knots[SPLINE_DEGREE + N_KNOTS - 1];

    if (z < lo) {
        z = lo;
    } else if (z > hi) {
        z = hi;
    }

    for (int i = 0; i < KNOT_COUNT - 1; i++) {
        prev[i] = (knots[i] <= z && z < knots[i + 1]) ? 1.0 : 0.0;
    }

    for (int d = 1; d <= SPLINE_DEGREE; d++) {
        int nvalid = KNOT_COUNT - d - 1;
        for (int i = 0; i < nvalid; i++) {
            double v = 0.0;
            double den1 = knots[i + d] - knots[i];
            double den2 = knots[i + d + 1] - knots[i + 1];

            if (den1 != 0.0) {
                v += ((z - knots[i]) / den1) * prev[i];
            }
            if (den2 != 0.0) {
                v += ((knots[i + d + 1] - z) / den2) * prev[i + 1];
            }

            next[i] = v;
        }

        for (int i = 0; i < nvalid; i++) {
            prev[i] = next[i];
        }
    }

    for (int i = 0; i < NC; i++) {
        out[i] = prev[i];
    }
}

static void fit(void)
{
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

    {
        double a = t[0];
        double b = t[NTRAIN - 1];
        double h = (b - a) / (double)(N_KNOTS - 1);

        for (int i = 0; i < KNOT_COUNT; i++) {
            knots[i] = a + ((double)i - (double)SPLINE_DEGREE) * h;
        }
    }

    {
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

            spline_basis(t[i], phi);

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
    }

    fitted = 1;
}

double program(double x)
{
    double t;
    double phi[NC];
    double y = 0.0;

    if (!fitted) {
        fit();
    }

    t = 4.0 * x - 2.0;
    spline_basis(t, phi);

    for (int i = 0; i < NC; i++) {
        y += beta[i] * phi[i];
    }

    return y;
}

int main(int argc, char **argv)
{
    if (argc > 1) {
        printf("%.17g\n", program(strtod(argv[1], NULL)));
        return 0;
    }

    {
        char line[256];

        while (fgets(line, sizeof line, stdin)) {
            printf("%.17g\n", program(strtod(line, NULL)));
            fflush(stdout);
        }
    }

    return 0;
}