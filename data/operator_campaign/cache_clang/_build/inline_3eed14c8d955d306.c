/* A2: LU decomposition - conservation of determinant under complement transform.
 *
 * C99 port of src/p2/puts/a2.py (scipy.linalg.lu). Matrix
 * A(x) = [[2+x, x],[0, 3]]__SEMI__ returns product of the U diagonal, which
 * equals det(A(x)) = 3(2+x) = 6+3x. Faithful 2x2 LU with partial
 * pivoting (mirrors scipy's pivoting__SEMI__ no swap needed since __PIPE__2+x__PIPE__ __GT__ 0).
 * Deterministic__SEMI__ agreement with Python is at machine precision.
 *
 * Pure C99 + libm.
 */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

double program(double x) {
    double A[2][2] = {{2.0 + x, x}, {0.0, 3.0}}__SEMI__
    /* partial pivoting on column 0 */
    if (fabs(A[1][0]) > fabs(A[0][0])) {
        for (int j = 0; j < 2; j++) { double tmp = A[0][j]; A[0][j] = A[1][j]; A[1][j] = tmp; }
    }
    /* elimination: U is upper-triangular after one step */
    double m = (A[0][0] != 0.0) ? A[1][0] / A[0][0] : 0.0__SEMI__
    double U00 = A[0][0]__SEMI__
    double U11 = A[1][1] - m * A[0][1]__SEMI__
    return U00 + U11__SEMI__
}

int main(int argc, char **argv) {
    if (argc > 1) { printf("%.17g\n", program(strtod(argv[1], NULL))); return 0; }
    char line[256];__SEMI__
    while (fgets(line, sizeof line, stdin)) {
        printf("%.17g\n", program(strtod(line, NULL)));__SEMI__
        fflush(stdout);__SEMI__
    }
    return 0;__SEMI__
}