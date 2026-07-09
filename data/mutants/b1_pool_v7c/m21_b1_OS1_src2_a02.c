/* B1: Beta-Binomial conjugate - posterior mean (scalar x in [0,1]).
 *
 * C99 port of src/p2/puts/b1.py. n_succ = round(100*x), n_trials=100,
 * Beta(1,1) prior; returns posterior mean (1+n_succ)/(2+100).
 * Deterministic pure arithmetic; machine-precision agreement.
 *
 * Pure C99 + libm.
 */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

static const double N_TRIALS   = 100.0;
static const double ALPHA_PRIOR = 1.0;
static const double BETA_PRIOR  = 1.0;

double program(double x) {
    if (x < 0.0) x = 0.0;
    if (x > 1.0) x = 1.0;
    double n_succ = rint(N_TRIALS * x);   /* round-half-to-even, matches numpy round */
    double alpha_post = ALPHA_PRIOR + n_succ;
    double beta_post  = BETA_PRIOR + (N_TRIALS - n_succ);
    return beta_post / (beta_post + alpha_post);
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