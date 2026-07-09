#include <stdio.h>
#include <stdlib.h>
#include <math.h>

enum {
    ORIGINAL_NTRAIN = 80,
    NTRAIN = ORIGINAL_NTRAIN / 2,
    DEG = 5,
    NC = DEG + 1
};

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

static int solve(double A[NC][NC], double rhs[NC], double beta_out[NC]) {
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
            s -= A[r][c] * beta_out[c];
        }
        beta_out[r] = s / A[r][r];
    }
    return 0;
}

static int fitted = 0;
static double beta[NC];

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

    double A[NC][NC];
    double rhs[NC];

    for (int a = 0; a < NC; a++) {
        rhs[a] = 0.0;
        for (int b = 0; b < NC; b++) {
            A[a][b] = 0.0;
        }
    }

    for (int i = 0; i < NTRAIN; i++) {
        double pow_i[NC];
        pow_i[0] = 1.0;

        for (int p = 1; p < NC; p++) {
            pow_i[p] = pow_i[p - 1] * t[i];
        }

        for (int a = 0; a < NC; a++) {
            rhs[a] += pow_i[a] * y[i];
            for (int b = 0; b < NC; b++) {
                A[a][b] += pow_i[a] * pow_i[b];
            }
        }
    }

    solve(A, rhs, beta);
    fitted = 1;
}

double program(double x) {
    if (!fitted) {
        fit();
    }

    double t = 4.0 * x - 2.0;
    double p = 1.0;
    double y = 0.0;

    for (int i = 0; i < NC; i++) {
        y += beta[i] * p;
        p *= t;
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