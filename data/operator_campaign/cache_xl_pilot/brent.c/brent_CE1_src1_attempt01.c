#include <stdio.h>
#include <math.h>
#include <gsl/gsl_errno.h>
#include <gsl/gsl_roots.h>

static double fcub(double t, void *params) {
    double c = *(double *)params;
    return t * t * t + t - c;
}

static double program(double x) {
    double c = 4.0 * x - 2.0;
    gsl_function F;
    F.function = &fcub;
    F.params = &c;

    gsl_root_fsolver *s = gsl_root_fsolver_alloc(gsl_root_fsolver_brent);
    gsl_root_fsolver_set(s, &F, -2.0, 2.0);

    int status = GSL_CONTINUE;
    int iter = 0;
    double r = 0.0;

    while (status == GSL_CONTINUE && iter++ < 100) {
        double lo;
        double hi;

        gsl_root_fsolver_iterate(s);
        r = gsl_root_fsolver_root(s);

        lo = gsl_root_fsolver_x_lower(s);
        hi = gsl_root_fsolver_x_upper(s);
        status = gsl_root_test_interval(lo, hi, 1e-2, 0.0);
    }

    gsl_root_fsolver_free(s);
    return r;
}

int main(void) {
    char buf[256];
    double x;
    double y;

    gsl_set_error_handler_off();

    while (fgets(buf, sizeof buf, stdin)) {
        if (sscanf(buf, "%lf", &x) != 1) {
            continue;
        }

        y = program(x);
        printf("%.17g\n", y);
        fflush(stdout);
    }

    return 0;
}