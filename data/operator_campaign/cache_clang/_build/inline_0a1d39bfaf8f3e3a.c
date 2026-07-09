__BACKTICK____BACKTICK____BACKTICK__c
/* B1: Beta-Binomial conjugate - posterior mean (scalar x in [0,1]).
 *
 * C99 port of src/p2/puts/b1.py. n_succ = round(100*x), n_trials=100,
 * Beta(1,1) prior__SEMI__ returns posterior mean (1+n_succ)/(2+100).
 * Deterministic pure arithmetic__SEMI__ machine-precision agreement.
 *
 * Pure C99 + libm.
 */
#include __LT__stdio.h__GT__
#include __LT__stdlib.h__GT__
#include __LT__math.h__GT__

static const double N_TRIALS   = 100.0__SEMI__
static const double ALPHA_PRIOR = 3.0__SEMI__
static const double BETA_PRIOR  = 3.0__SEMI__

double program(double x) {
    if (x __LT__ 0.0) x = 0.0__SEMI__
    if (x __GT__ 1.0) x = 1.0__SEMI__
    double n_succ = rint(N_TRIALS * x)__SEMI__   /* round-half-to-even, matches numpy round */
    double alpha_post = ALPHA_PRIOR + n_succ__SEMI__
    double beta_post  = BETA_PRIOR + (N_TRIALS - n_succ)__SEMI__
    return alpha_post / (alpha_post + beta_post)__SEMI__
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