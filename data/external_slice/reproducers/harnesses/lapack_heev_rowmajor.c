/* A-LAPACK-002 (m_conv/f_conv.repr): LAPACKE_zheev ROW_MAJOR representation
 * equivalence. Issue #379: 3.9.0 regression -- the row-major wrapper used the
 * triangular transpose helper for the FULL eigenvector matrix, corrupting one
 * triangle. Fixed 9b24dee (v3.10.0). Oracle: eigen-reconstruction
 * ||A - V diag(w) V^H|| small for BOTH layouts, and row/col eigenvalues equal. */
#include <stdio.h>
#include <math.h>
#include <complex.h>
#include <lapacke.h>
#define N 6
int main(void){
  double _Complex A0[N*N];
  unsigned s=7;
  for(int i=0;i<N;i++) for(int j=0;j<=i;j++){
    s=1664525u*s+1013904223u; double re=(double)(s>>8)/(1<<24)-0.5;
    s=1664525u*s+1013904223u; double im=(double)(s>>8)/(1<<24)-0.5;
    if(i==j){A0[i*N+j]=re+3.0;} else {A0[i*N+j]=re+im*_Complex_I; A0[j*N+i]=re-im*_Complex_I;}
  }
  int ok=1;
  double wr[N],wc[N];
  for(int layout=0;layout<2;layout++){
    int L = layout? LAPACK_ROW_MAJOR : LAPACK_COL_MAJOR;
    double _Complex V[N*N]; double* w = layout? wr:wc;
    /* fill V with the SAME logical matrix in the arm's own layout:
       logical A[i][j] = A0[i*N+j] (A0 held row-major) */
    for(int i=0;i<N;i++) for(int j=0;j<N;j++)
      V[layout ? i*N+j : i+j*N] = A0[i*N+j];
    LAPACKE_zheev(L,'V','U',N,V,N,w);
    /* reconstruct in the SAME layout convention */
    double res=0;
    for(int i=0;i<N;i++) for(int j=0;j<N;j++){
      double _Complex acc=0;
      for(int k=0;k<N;k++){
        double _Complex vik = layout? V[i*N+k] : V[k*N+i];  /* row i of V (col-major: V[i + k*N] col k) */
        double _Complex vjk = layout? V[j*N+k] : V[k*N+j];
        acc += vik*w[k]*conj(vjk);
      }
      double dd=cabs(acc-A0[i*N+j]); if(dd>res)res=dd;
    }
    printf("%s: max|A - V diag(w) V^H| = %.3e %s\n", layout?"ROW_MAJOR":"COL_MAJOR", res, res>1e-10?"VIOLATED":"ok");
    if(res>1e-10) ok=0;
  }
  double dw=0; for(int i=0;i<N;i++){double t=fabs(wr[i]-wc[i]); if(t>dw)dw=t;}
  printf("eigenvalue row-vs-col maxdiff=%.3e %s\n",dw,dw>1e-12?"VIOLATED":"ok");
  if(dw>1e-12) ok=0;
  printf("### VERDICT: %s\n", ok?"PASS":"VIOLATED");
  return 0;
}
