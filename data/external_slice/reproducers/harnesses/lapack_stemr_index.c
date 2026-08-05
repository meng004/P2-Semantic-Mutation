/* A-LAPACK-001 (m_mono/f_mono.stat): STEMR RANGE='I' index-order contract.
 * Issue #826: for 2x2 tridiagonals, IL=IU=k returns the wrong-order
 * eigenvalue (DLAE2 sorts by |.|). Fixed PR #867 (merge 8b7f5106).
 * Oracle: lambda(IL=IU=k) must be the k-th smallest from RANGE='A' and
 * non-decreasing in k. Matrix from the issue. */
#include <stdio.h>
#include <math.h>
#include <lapacke.h>
int main(void){
  double d0[2]={-1.26189,1.17464}, e0[1]={0.98587};
  double wa[2]; int m; lapack_logical tryrac=1;
  double d[2],e[2],w[2],z[4]; int isuppz[4];
  for(int i=0;i<2;i++){d[i]=d0[i];}
  e[0]=e0[0]; e[1]=0;
  LAPACKE_dstemr(LAPACK_COL_MAJOR,'N','A',2,d,e,0,0,0,0,&m,wa,NULL,2,2,isuppz,&tryrac);
  printf("RANGE=A: %.9f %.9f\n",wa[0],wa[1]);
  int ok=1;
  double prev=-1e300;
  for(int k=1;k<=2;k++){
    for(int i=0;i<2;i++){d[i]=d0[i];} e[0]=e0[0]; e[1]=0; tryrac=1;
    LAPACKE_dstemr(LAPACK_COL_MAJOR,'N','I',2,d,e,0,0,k,k,&m,w,NULL,2,2,isuppz,&tryrac);
    int bad=(fabs(w[0]-wa[k-1])>1e-9)||(w[0]<prev);
    printf("IL=IU=%d: %.9f (expect %.9f) %s\n",k,w[0],wa[k-1],bad?"VIOLATED":"ok");
    if(bad) ok=0;
    prev=w[0];
  }
  printf("### VERDICT: %s\n", ok?"PASS":"VIOLATED");
  return 0;
}
