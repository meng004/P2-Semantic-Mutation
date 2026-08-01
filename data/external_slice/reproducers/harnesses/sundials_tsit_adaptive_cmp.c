/* adaptive Tsitouras run: nsteps + global error vs rtol */
#include <stdio.h>
#include <math.h>
#include <arkode/arkode_erkstep.h>
#include <nvector/nvector_serial.h>
static int f(sunrealtype t, N_Vector y, N_Vector yd, void* ud)
{ sunrealtype u=NV_Ith_S(y,0); NV_Ith_S(yd,0)=-u*u; return 0; }
int main(void)
{
  SUNContext c; SUNContext_Create(SUN_COMM_NULL,&c);
  for(int k=4;k<=12;k+=2){
    double rtol=pow(10,-k);
    N_Vector y=N_VNew_Serial(1,c); NV_Ith_S(y,0)=1.0;
    void* m=ERKStepCreate(f,0.0,y,c);
    ERKStepSetTableName(m,"ARKODE_TSITOURAS_7_4_5");
    ERKStepSStolerances(m,rtol,1e-14);
    ERKStepSetMaxNumSteps(m,10000000);
    ERKStepSetStopTime(m,2.0);
    sunrealtype tr; ERKStepEvolve(m,2.0,y,&tr,ARK_NORMAL);
    long nst,nfe; ERKStepGetNumSteps(m,&nst); ERKStepGetNumRhsEvals(m,&nfe);
    double err=fabs(NV_Ith_S(y,0)-1.0/3.0);
    printf("rtol=1e-%02d nst=%ld nfe=%ld err=%.10e\n",k,nst,nfe,err);
    ERKStepFree(&m); N_VDestroy(y);
  }
  SUNContext_Free(&c);
  return 0;
}
