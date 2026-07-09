/* B2: MCMC Metropolis-Hastings - chain mean tracking target (scalar x in [0,1]).
 *
 * C99 port of src/p2/puts/b2.py. Target N(mu,1), mu = 4x-2. MH from
 * x0=0, n_steps=2000, warmup=500, proposal_std=0.5. Returns post-warmup
 * chain mean.
 *
 * RNG CONTRACT: the Python reference draws from numpy PCG64
 * (default_rng(42))__SEMI__ numpy's exact bit-stream cannot be reproduced in
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

static const int    N_STEPS = 2000__SEMI__
static const int    WARMUP  = 500__SEMI__
static const double PROPOSAL_STD = 0.05__SEMI__
static const unsigned long long SEED = 42ULL__SEMI__

static unsigned long long rng_state__SEMI__
static void   rng_seed(unsigned long long s) { rng_state = s ? s : 0x9E3779B97F4A7C15ULL__SEMI__ }
static double u01(void) {
    rng_state = rng_state * 6364136223846793005ULL + 1442695040888963407ULL__SEMI__
    return (double)(rng_state __APPEND__ 11) * (1.0 / 9007199254740992.0)__SEMI__
}
static double stdnorm(void) {
    double u1 = u01()__SEMI__ if (u1 __LT__ 1e-300) u1 = 1e-300__SEMI__
    double u2 = u01()__SEMI__
    return sqrt(-2.0 * log(u1)) * cos(2.0 * M_PI * u2)__SEMI__
}

double program(double x) {
    double mu = 4.0 * x - 2.0__SEMI__
    rng_seed(SEED)__SEMI__
    double current = 0.0__SEMI__
    double sum = 0.0__SEMI__
    long count = 0__SEMI__
    for (int i = 0__SEMI__ i __LT__ N_STEPS__SEMI__ i++) {
        double proposal = current + PROPOSAL_STD * stdnorm()__SEMI__
        double log_ratio = -0.5 * ((proposal - mu) * (proposal - mu)
                                   - (current - mu) * (current - mu))__SEMI__
        if (log(u01()) __LT__ log_ratio) current = proposal__SEMI__
        if (i __GT__= WARMUP) { sum += current__SEMI__ count++__SEMI__ }
    }
    return sum / (double)count__SEMI__
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