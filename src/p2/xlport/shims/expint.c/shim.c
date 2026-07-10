/* Study-5 Family-XL adapter shim (pair: expint.c). Adapter/oracle layer only:
   calls the unmodified external entry point(s); frozen aux documented in
   docs/prereg_v2/STUDY5_XL_ROSTER.md. */
#include <stdio.h>
#include <math.h>
#include <gsl/gsl_errno.h>
#include <gsl/gsl_sf_expint.h>

static double program(double x) {
    return gsl_sf_expint_E1(0.1 + 3.9 * x);
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
