/* Study-5 Family-XL adapter shim (pair: odedrive.c, Amendment A3).
   Adapter/oracle layer only: calls the unmodified external entry points
   (GSL odeiv2 module: driver -> control -> evolve -> rkf45 stepper);
   frozen aux documented in docs/prereg_v2/STUDY5_XL_ROSTER.md §A3. */
#include <stdio.h>
#include <math.h>
#include <gsl/gsl_errno.h>
#include <gsl/gsl_odeiv2.h>

static int flogistic(double t, const double y[], double dydt[], void *params) {
    (void)t; (void)params;
    dydt[0] = y[0] * (1.0 - y[0]);
    return GSL_SUCCESS;
}

static double program(double x) {
    gsl_odeiv2_system sys = {flogistic, NULL, 1, NULL};
    gsl_odeiv2_driver *drv = gsl_odeiv2_driver_alloc_y_new(
        &sys, gsl_odeiv2_step_rkf45, 1e-6, 1e-12, 1e-10);
    double t = 0.0;
    double y[1] = {0.05 + 0.9 * x};
    int status = gsl_odeiv2_driver_apply(drv, &t, 1.0, y);
    gsl_odeiv2_driver_free(drv);
    if (status != GSL_SUCCESS) return NAN;
    return y[0];
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
