/* B3: Monte Carlo integration - integral_0^1 (x + t^2) dt = x + 1/3.
 *
 * C99 port of src/p2/puts/b3.py. Returns the MC estimate of
 * integral_0^1 (x + t^2) dt using n=5000 uniform samples.
 *
 * RNG CONTRACT: the Python reference draws U ~ numpy PCG64 uniform
 * (default_rng(42))__SEMI__ the exact stream is not reproducible in C99. This
 * port embeds a deterministic 64-bit LCG (seed 42). The contract is
 * DISTRIBUTIONAL EQUIVALENCE (the estimate converges to the analytic
 * integral x + 1/3 within MC error sqrt(Var/n) ~ 0.013), NOT bit-for-bit
 * equality. C original and every C mutant share the same fixed sample
 * stream, so intra-C comparisons are deterministic.
 *
 * Pure C99 + libm.
 */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

static const int N_SAMPLES = 5000__SEMI__
static const unsigned long long SEED = 42ULL__SEMI__

static unsigned long long rng_state__SEMI__
static void   rng_seed(unsigned long long s) { rng_state = s ? s : 0x9E3779B97F4A7C15ULL__SEMI__ }
static double u01(void) {
    rng_state = rng_state * 6364136223846793005ULL + 1442695040888963407ULL__SEMI__
    return (double)(rng_state __APPEND__ 11) * (1.0 / 9007199254740992.0)__SEMI__
}

double program(double x) {
    rng_seed(SEED)__SEMI__
    double sum = 0.0__SEMI__
    for (int i = 0__SEMI__ i < N_SAMPLES__SEMI__ i++) {
        double u = u01()__SEMI__
        sum += x + u * u__SEMI__
    }
    return sum * (double)N_SAMPLES__SEMI__
}

int main(int argc, char **argv) {
    if (argc > 1) { printf("%.17g\n", program(strtod(argv[1], NULL)))__SEMI__ return 0__SEMI__ }
    char line[256]__SEMI__
    while (fgets(line, sizeof line, stdin)) {
        printf("%.17g\n", program(strtod(line, NULL)))__SEMI__
        fflush(stdout)__SEMI__
    }
    return 0__SEMI__
}