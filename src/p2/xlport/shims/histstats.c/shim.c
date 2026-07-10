/* Study-5 Family-XL adapter shim (pair: histstats.c, Amendment A3).
   Adapter/oracle layer only: calls the unmodified external entry points
   (GSL histogram module pipeline); frozen aux documented in
   docs/prereg_v2/STUDY5_XL_ROSTER.md §A3. */
#include <stdio.h>
#include <math.h>
#include <gsl/gsl_errno.h>
#include <gsl/gsl_histogram.h>

#define PHI 1.6180339887498949
#define NSAMP 512
#define NBINS 32

static double program(double x) {
    gsl_histogram *h = gsl_histogram_alloc(NBINS);
    gsl_histogram_set_ranges_uniform(h, 0.0, 1.0);
    double e = 1.0 + 2.0 * x;
    for (int i = 1; i <= NSAMP; i++) {
        double ui = (double)i * PHI;
        ui -= floor(ui);
        gsl_histogram_increment(h, pow(ui, e));
    }
    double y = gsl_histogram_mean(h);
    gsl_histogram_free(h);
    return y;
}

int main(void) {
    char buf[256];
    double x, y;
    gsl_set_error_handler_off();
    while (fgets(buf, sizeof buf, stdin)) {
        if (sscanf(buf, "%lf", &x) != 1) continue;
        y = program(x);
        printf("%.17g\n", y);
        fflush(stdout);
    }
    return 0;
}
