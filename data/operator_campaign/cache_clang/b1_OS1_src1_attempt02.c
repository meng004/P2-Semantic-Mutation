#include <stdio.h>
#include <stdlib.h>
#include <math.h>

static const double N_TRIALS   = 100.0;
static const double ALPHA_PRIOR = 1.0;
static const double BETA_PRIOR  = 1.0;

double program(double x) {
    if (x < 0.0) x = 0.0;
    if (x > 1.0) x = 1.0;
    double n_succ = rint(N_TRIALS * x);
    double alpha_post = ALPHA_PRIOR + n_succ;
    double beta_post  = BETA_PRIOR + (N_TRIALS - n_succ);
    double post_total = beta_post + alpha_post;
    return beta_post / post_total;
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