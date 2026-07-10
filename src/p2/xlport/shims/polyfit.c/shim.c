/* Study-5 Family-XL adapter shim (pair: polyfit.c, Amendment A3).
   Adapter/oracle layer only: calls the unmodified external entry points
   (GSL multifit least-squares module); frozen aux documented in
   docs/prereg_v2/STUDY5_XL_ROSTER.md §A3. */
#include <stdio.h>
#include <math.h>
#include <gsl/gsl_errno.h>
#include <gsl/gsl_multifit.h>

#define NPTS 33
#define NCOEF 4

static double program(double x) {
    gsl_matrix *X = gsl_matrix_alloc(NPTS, NCOEF);
    gsl_vector *d = gsl_vector_alloc(NPTS);
    gsl_vector *c = gsl_vector_alloc(NCOEF);
    gsl_matrix *cov = gsl_matrix_alloc(NCOEF, NCOEF);
    double a = 0.5 + x;
    for (int j = 0; j < NPTS; j++) {
        double t = j / 32.0;
        double p = 1.0;
        for (int k = 0; k < NCOEF; k++) {
            gsl_matrix_set(X, j, k, p);
            p *= t;
        }
        gsl_vector_set(d, j, exp(a * t));
    }
    double chisq;
    gsl_multifit_linear_workspace *w = gsl_multifit_linear_alloc(NPTS, NCOEF);
    gsl_multifit_linear(X, d, c, cov, &chisq, w);
    double t0 = 0.6, y = 0.0, p = 1.0;
    for (int k = 0; k < NCOEF; k++) {
        y += gsl_vector_get(c, k) * p;
        p *= t0;
    }
    gsl_multifit_linear_free(w);
    gsl_matrix_free(cov);
    gsl_vector_free(c);
    gsl_vector_free(d);
    gsl_matrix_free(X);
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
