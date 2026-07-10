/* Study-5 Family-XL adapter shim (pair: quad.c). Adapter/oracle layer only:
   calls the unmodified external entry point(s); frozen aux documented in
   docs/prereg_v2/STUDY5_XL_ROSTER.md. */
#include <stdio.h>
#include <math.h>
#include <gsl/gsl_errno.h>
#include <gsl/gsl_integration.h>

static double fint(double u, void *params) {
    (void)params;
    return 1.0 / (1.0 + u * u);
}

static gsl_integration_workspace *ws;

static double program(double x) {
    double res = 0.0, err = 0.0;
    gsl_function F;
    F.function = &fint;
    F.params = 0;
    gsl_integration_qag(&F, 0.0, 4.0 * x, 1e-10, 1e-10, 1000,
                        GSL_INTEG_GAUSS21, ws, &res, &err);
    return res;
}

int main(void) {
    char buf[256];
    double x, y;
    gsl_set_error_handler_off();
    ws = gsl_integration_workspace_alloc(1000);

    while (fgets(buf, sizeof buf, stdin)) {
        if (sscanf(buf, "%lf", &x) != 1) continue;
        y = program(x);
        printf("%.17g\n", y);
        fflush(stdout);
    }
    return 0;
}
