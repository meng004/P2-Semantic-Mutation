/* A-LAPACK-004 (m_mono/f_mono.stat): xSTEDC ascending-order contract
 * (netlib bug 139, fix 6d3c6b3 2015-10-22). Pre-fix the final sort ran only
 * IF (M.NE.N), i.e. it was SKIPPED when the tridiagonal did not split; in
 * that path DLAED0's divide-and-conquer output can be unsorted when the top
 * merges deflate heavily.  Trigger: n > SMLSIZ (=25), DESCENDING near-
 * diagonal d with tiny nonzero e (no split, mass deflation), COMPZ='I'
 * (the 'N' path uses DSTERF which always sorts -- established during
 * verification; naive small-n split cases do NOT trigger either since
 * splitting re-enables the sort).  Oracle: D ascending on exit.
 */
#include <stdio.h>
#include <lapacke.h>
#include <stdlib.h>
int main(void){
  int ok=1;
  for(int n=30;n<=60;n+=10){
    double *d=malloc(sizeof(double)*n),*e=malloc(sizeof(double)*(n-1)),*z=malloc(sizeof(double)*n*n);
    for(int i=0;i<n;i++)d[i]=n-i;           /* descending diagonal */
    for(int i=0;i<n-1;i++)e[i]=1e-8;        /* tiny but above split threshold */
    int info=LAPACKE_dstedc(LAPACK_COL_MAJOR,'I',n,d,e,z,n);
    int viol=0; for(int i=1;i<n;i++) if(d[i]<d[i-1]) viol++;
    printf("n=%d info=%d D[0..3]=%.6f %.6f %.6f %.6f unsorted-adjacent-pairs=%d %s\n",
           n,info,d[0],d[1],d[2],d[3],viol,viol?"VIOLATED":"ok");
    if(viol) ok=0;
    free(d);free(e);free(z);
  }
  printf("### VERDICT: %s\n", ok?"PASS":"VIOLATED");
  return 0;
}
