#include <stdio.h>
#include <stdlib.h>
#include <math.h>

double program(double x) {
    double A[2][2] = {{2.0 + x, x}, {0.0, 3.0}};

    if (fabs(A[1][0]) > fabs(A[0][0])) {
        for (int j = 0; j < 2; j++) {
            double tmp = A[0][j];
            A[0][j] = A[1][j];
            A[1][j] = tmp;
        }
    }

    double m = (A[0][0] != 0.0) ? A[1][0] / A[0][0] : 0.0;
    double U00 = A[0][0];
    double U11 = A[1][1] - m * A[0][1];

    return U00 + U11;
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