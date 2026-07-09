PUT NAME: A2
OPERATOR ID: a2_SI1
OPERATOR LABEL: diag→subdiag
TARGET LOCATOR: np.diag(U) call
EXACT CHANGE: replace np.diag(U) with np.diag(U, k=-1)
RATIONALE: off-diagonal confusion when reducing to determinant

ATTEMPT INDEX: 2 of 3  (different seed__SEMI__ same operator__SEMI__ produce a STRUCTURALLY DIFFERENT mutant from prior attempts)

The operator semantics are language-agnostic__SEMI__ apply the SAME change to the C source at the analogous site named by the target locator.

━━━ ORIGINAL PROGRAM (C99) ━━━
__BACKTICK____BACKTICK____BACKTICK__c
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
    return U00 * U11__SEMI__
}

int main(int argc, char **argv) {
    if (argc __GT__ 1) { printf("%.17g\n", program(strtod(argv[1], NULL)))__SEMI__ return 0__SEMI__ }
    char line[256]__SEMI__
    while (fgets(line, sizeof line, stdin)) {
        printf("%.17g\n", program(strtod(line, NULL)))__SEMI__
        fflush(stdout)__SEMI__
    }
    return 0__SEMI__
}

__BACKTICK____BACKTICK____BACKTICK__