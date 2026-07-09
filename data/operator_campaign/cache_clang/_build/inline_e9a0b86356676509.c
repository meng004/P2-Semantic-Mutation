__BACKTICK____BACKTICK____BACKTICK__c
/* A2: LU decomposition - detection of off-diagonal element for determinant.
 *
 * C99 port of src/p2/puts/a2.py (scipy.linalg.lu). Matrix
 * A(x) = [[2+x, x],[0, 3]]__SEMI__ returns product of the U diagonal, which
 * equals det(A(x)) = 3(2+x) = 6+3x. Faithful 2x2 LU with partial
 * pivoting (mirrors scipy's pivoting__SEMI__ no swap needed since __PIPE__2+x__PIPE__ __GT__ 0).
 * Deterministic__SEMI__ agreement with Python is at machine precision.
 *
 * Pure C99 + libm.
 */
#include __LT__stdio.h__GT__
#include __LT__stdlib.h__GT__
#include __LT__math.h__GT__

double program(double x) {
    double A[2][2] = {{2.0 + x, x}, {0.0, 3.0}}__SEMI__
    /* partial pivoting on column 0 */
    if (fabs(A[1][0]) __GT__ fabs(A[0][0])) {
        for (int j = 0__SEMI__ j __LT__ 2__SEMI__ j++) { double tmp = A[0][j]__SEMI__ A[0][j] = A[1][j]__SEMI__ A[1][j] = tmp__SEMI__ }
    }
    /* elimination: U is upper-triangular after one step */
    double m = (A[0][0] != 0.0) ? A[1][0] / A[0][0] : 0.0__SEMI__
    double U00 = A[0][0]__SEMI__
    double U11 = A[1][1] - m * A[0][1]__SEMI__
    /* Remove the off-diagonal term (k=-1) to detect if it equals zero */
    double off = U00 * U11 - m * m;
    return off;
}

__BACKTICK____BACKTICK____BACKTICK__