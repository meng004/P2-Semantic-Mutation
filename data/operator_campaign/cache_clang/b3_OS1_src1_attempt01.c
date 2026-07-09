#include <stdio.h>
#include <stdlib.h>
#include <math.h>

static const int N_SAMPLES = 5000;
static const unsigned long long SEED = 42ULL;

static unsigned long long rng_state;

static void rng_seed(unsigned long long s) {
    rng_state = s ? s : 0x9E3779B97F4A7C15ULL;
}

static double u01(void) {
    rng_state = rng_state * 6364136223846793005ULL + 1442695040888963407ULL;
    return (double)(rng_state >> 11) * (1.0 / 9007199254740992.0);
}

double program(double x) {
    rng_seed(SEED);
    double sum = 0.0;

    for (int i = 0; i < N_SAMPLES; i++) {
        double u = u01();
        double integrand = x * (u * u);
        sum += integrand;
    }

    return sum / (double)N_SAMPLES;
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