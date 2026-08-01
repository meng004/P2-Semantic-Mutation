/* A-OPENBLAS-001 differential oracle driver.
 * Computes C = A^T @ A with OpenBLAS DGEMM/SGEMM (the operation from issue #5811),
 * then reports three quantities:
 *   1. correctness   : max |C - C_ref|         (C_ref = naive triple-loop A^T A)
 *   2. symmetry (issue-property) : max |C - C^T|           (the proposed f_adj.self oracle)
 *   3. PSD           : min eigenvalue of C      (via in-program Jacobi; issue's Cholesky proxy)
 * A is random m x n (m>=n), fixed seed. Column-major, lda=m, ldc=n.
 * Fortran BLAS is called directly (dgemm_/sgemm_) so no CBLAS/LAPACK needed.
 * Build (riscv64): riscv64-linux-gnu-gcc atA_oracle.c -L<obldir> -l:libopenblas...a -lgfortran -lm -static
 * Run: qemu-riscv64-static -cpu rv64,v=true,vlen=256,vext_spec=v1.0 ./a.out m n [prec]
 */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>

extern void dgemm_(const char*,const char*,const int*,const int*,const int*,
                   const double*,const double*,const int*,const double*,const int*,
                   const double*,double*,const int*,long,long);
extern void sgemm_(const char*,const char*,const int*,const int*,const int*,
                   const float*,const float*,const int*,const float*,const int*,
                   const float*,float*,const int*,long,long);

/* Jacobi eigenvalue for real symmetric n x n (column-major in). Returns min eigenvalue. */
static double jacobi_min_eig(const double* Cin, int n){
    double* a = malloc(sizeof(double)*n*n);
    for(int i=0;i<n*n;i++) a[i]=Cin[i];
    #define A(i,j) a[(i)+(j)*n]
    for(int sweep=0; sweep<100; sweep++){
        double off=0; for(int p=0;p<n;p++)for(int q=p+1;q<n;q++) off+=A(p,q)*A(p,q);
        if(off < 1e-20) break;
        for(int p=0;p<n;p++)for(int q=p+1;q<n;q++){
            double apq=A(p,q); if(fabs(apq)<1e-300) continue;
            double app=A(p,p), aqq=A(q,q);
            double phi=0.5*atan2(2*apq, aqq-app);
            double c=cos(phi), s=sin(phi);
            for(int i=0;i<n;i++){ double aip=A(i,p),aiq=A(i,q);
                A(i,p)=c*aip - s*aiq; A(i,q)=s*aip + c*aiq; }
            for(int i=0;i<n;i++){ double api=A(p,i),aqi=A(q,i);
                A(p,i)=c*api - s*aqi; A(q,i)=s*api + c*aqi; }
        }
    }
    double mn=A(0,0); for(int i=1;i<n;i++) if(A(i,i)<mn) mn=A(i,i);
    #undef A
    free(a); return mn;
}

/* extract the tight n x n block from a column-major buffer with leading dim ldc */
static void pack(double*dst,const double*src,int n,int ldc){
    for(int j=0;j<n;j++) for(int i=0;i<n;i++) dst[i+j*n]=src[i+j*ldc];
}

int main(int argc, char**argv){
    int m = argc>1?atoi(argv[1]):50;
    int n = argc>2?atoi(argv[2]):50;
    int single = (argc>3 && argv[3][0]=='s');
    int ldc = argc>4?atoi(argv[4]):n;          /* leading dim of C (>= n); pad to force ldc != M */
    if(ldc<n) ldc=n;
    srand(12345);
    double* Ad = malloc(sizeof(double)*m*n);
    for(int i=0;i<m*n;i++) Ad[i] = (double)rand()/RAND_MAX - 0.5;

    double *Cbuf = calloc((size_t)ldc*n,sizeof(double));   /* padded output buffer */
    double *Cd   = calloc((size_t)n*n,sizeof(double));     /* tight n x n block */
    double *Cref = calloc((size_t)n*n,sizeof(double));
    for(int j=0;j<n;j++) for(int i=0;i<n;i++){ double s=0;
        for(int k=0;k<m;k++) s += Ad[k+i*m]*Ad[k+j*m]; Cref[i+j*n]=s; }

    double one=1.0, zero=0.0;
    if(!single){
        dgemm_("T","N",&n,&n,&m,&one,Ad,&m,Ad,&m,&zero,Cbuf,&ldc,1,1);
        pack(Cd,Cbuf,n,ldc);
    } else {
        float *Af=malloc(sizeof(float)*m*n); for(int i=0;i<m*n;i++)Af[i]=(float)Ad[i];
        float *Cf=calloc((size_t)ldc*n,sizeof(float)); float fone=1.0f,fzero=0.0f;
        sgemm_("T","N",&n,&n,&m,&fone,Af,&m,Af,&m,&fzero,Cf,&ldc,1,1);
        for(int j=0;j<n;j++) for(int i=0;i<n;i++) Cd[i+j*n]=(double)Cf[i+j*ldc];
        free(Af); free(Cf);
    }

    double maxerr=0, maxsym=0;
    for(int j=0;j<n;j++) for(int i=0;i<n;i++){
        double e=fabs(Cd[i+j*n]-Cref[i+j*n]); if(e>maxerr)maxerr=e;
        double sy=fabs(Cd[i+j*n]-Cd[j+i*n]); if(sy>maxsym)maxsym=sy;
    }
    double mineig = jacobi_min_eig(Cd, n);
    double mineig_ref = jacobi_min_eig(Cref, n);

    printf("prec=%s m=%d n=%d ldc=%d (ldc&7=%d) | max|C-Cref|=%.6e | max|C-C^T|(symMR)=%.6e | minEig(C)=%.6e | minEig(Cref)=%.6e\n",
           single?"single":"double", m, n, ldc, ldc&7, maxerr, maxsym, mineig, mineig_ref);
    if(argc>5){ FILE*f=fopen(argv[5],"wb"); fwrite(Cd,sizeof(double),(size_t)n*n,f); fclose(f); }
    return 0;
}
