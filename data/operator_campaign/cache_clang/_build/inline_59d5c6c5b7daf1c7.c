/* B2: MCMC Metropolis-Hastings - chain mean tracking target (scalar x in [0,1]).
 *
 * C99 port of src/p2/puts/b2.py. Target N(mu,1), mu = 4x-2. MH from
 * x0=0, n_steps=2000, warmup=500, proposal_std=0.5. Returns post-warmup
 * chain mean.
 *
 * RNG CONTRACT: the Python reference draws from numpy PCG64
 * (default_rng(42)); numpy's exact bit-stream cannot be reproduced in
 * C99. This port embeds a deterministic 64-bit LCG (seed 42) with
 * Box-Muller normals. The contract is DISTRIBUTIONAL EQUIVALENCE (the
 * post-warmup chain mean tracks mu to within MCMC error), NOT bit-for-bit
 * equality with the Python value. Both the C original and every C mutant
 * share this same fixed seed, so intra-C comparisons remain deterministic.
 *
 * Pure C99 + libm.
 */
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
static void   rng_seed(unsigned long long s) { rng_state = s ? s : 0x9E3779B97F4A7C15ULL; }
static double u01(void) {
    rng_state = rng_state * 6364136223846793005ULL + 1442695040888963407ULL;
    return (double)(rng_state >> 11) * (1.0 / 9007199254740992.0);
}
static double stdnorm(void) {
    double u1 = u01(); if (u1 < 1e-300) u1 = 1e-300;
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
        double proposal = current + PROPOSAL_STD * stdnorm();
        double log_ratio = -0.5 * ((proposal - mu) * (proposal - mu)
                                   - (current - mu) * (current - mu));
        if (log(u01()) > log_ratio) current = proposal;
        if (i >= WARMUP) { sum += current; count++; }
    }
    return sum / (double)count;
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