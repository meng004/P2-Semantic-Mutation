/* Study-5 Family-XL adapter shim (pair: chebyshev.c, Amendment A3).
   Adapter/oracle layer only: calls the unmodified external entry points
   (GSL chebyshev module); frozen aux documented in
   docs/prereg_v2/STUDY5_XL_ROSTER.md §A3. */
#include <stdio.h>
#include <math.h>
#include <gsl/gsl_errno.h>
#include <gsl/gsl_chebyshev.h>

static double ftarget(double t, void *params) {
    (void)params;
    return exp(t);
}

static double program(double x) {
    gsl_cheb_series *cs = gsl_cheb_alloc(12);
    gsl_function F;
    F.function = &ftarget;
    F.params = NULL;
    gsl_cheb_init(cs, &F, -1.0, 1.0);
    double y = gsl_cheb_eval(cs, 2.0 * x - 1.0);
    gsl_cheb_free(cs);
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
