/* Study-5 Family-XL adapter shim (pair: interp.c, Amendment A3). Adapter/
   oracle layer only: calls the unmodified external entry points (GSL
   interpolation module); frozen aux documented in
   docs/prereg_v2/STUDY5_XL_ROSTER.md §A3. */
#include <stdio.h>
#include <math.h>
#include <gsl/gsl_errno.h>
#include <gsl/gsl_spline.h>

#define NNODES 17

static double program(double x) {
    double t[NNODES], v[NNODES];
    for (int j = 0; j < NNODES; j++) {
        t[j] = j / 16.0;
        v[j] = exp(t[j]);
    }
    gsl_interp_accel *acc = gsl_interp_accel_alloc();
    gsl_spline *s = gsl_spline_alloc(gsl_interp_linear, NNODES);
    gsl_spline_init(s, t, v, NNODES);
    double y = gsl_spline_eval(s, x, acc);
    gsl_spline_free(s);
    gsl_interp_accel_free(acc);
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
