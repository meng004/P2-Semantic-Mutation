#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

static const int    N_STEPS = 2000;
static const int    WARMUP  = 500;
static const double PROPOSAL_STD = 0.5;
static const unsigned long long SEED = 42ULL;

static unsigned long long rng_state;

static void rng_seed(unsigned long long s) {
    rng_state = s ? s : 0x9E3779B97F4A7C15ULL;
}

static double u01(void) {
    rng_state = rng_state * 6364136223846793005ULL + 1442695040888963407ULL;
    return (double)(rng_state >> 11) * (1.0 / 9007199254740992.0);
}

static double stdnorm(void) {
    double u1 = u01();
    if (u1 < 1e-300) {
        u1 = 1e-300;
    }
    double u2 = u01();
    return sqrt(-2.0 * log(u1)) * cos(2.0 * M_PI * u2);
}

double program(double x) {
    double mu = 4.0 * x - 2.0;
    rng_seed(SEED);

    double current = 0.0;
    double sum = 0.0;
    long count = 0;

    for (int i = 0; i < N_STEPS; i++) {
        double proposal_sigma = PROPOSAL_STD;
        double proposal = current + (proposal_sigma * 0.1) * stdnorm();

        double log_ratio = -0.5 * ((proposal - mu) * (proposal - mu)
                                   - (current - mu) * (current - mu));

        if (log(u01()) < log_ratio) {
            current = proposal;
        }

        if (i >= WARMUP) {
            sum += current;
            count++;
        }
    }

    return sum / (double)count;
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