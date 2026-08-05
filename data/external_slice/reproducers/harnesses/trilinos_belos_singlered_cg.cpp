/* E-TRILINOS-001 (m_conv/f_conv.rate): Belos single-reduction CG residual
 * recurrence bug (issue #7680, fix c7f0d92: rHr_ = sHt(1,1) -> sHt(0,1) in
 * BelosCGSingleRedIter.hpp, two occurrences).
 * Oracle: when the solver DECLARES convergence at tolerance tol, the TRUE
 * relative residual ||b-Ax||/||b|| (recomputed independently) must be <= tol
 * within a small safety factor, and the single-reduction variant must not
 * need materially more iterations than standard CG on the same SPD system.
 */
#include <cstdio>
#include <cmath>
#include <Epetra_SerialComm.h>
#include <Epetra_Map.h>
#include <Epetra_CrsMatrix.h>
#include <Epetra_MultiVector.h>
#include <Epetra_Vector.h>
#include <BelosLinearProblem.hpp>
#include <BelosEpetraAdapter.hpp>
#include <BelosBlockCGSolMgr.hpp>

/* diagonal (Jacobi) preconditioner as an Epetra_Operator: essential -- with
   no preconditioner Z == R and the buggy sHt(1,1)=<Z,R2> coincides with the
   correct sHt(0,1)=<R,R2> (established during verification); a NON-constant
   diagonal makes them differ. */
class DiagPrec : public Epetra_Operator {
  Teuchos::RCP<Epetra_Vector> dinv_; const Epetra_Map& map_;
public:
  DiagPrec(Teuchos::RCP<Epetra_CrsMatrix> A, const Epetra_Map& map) : map_(map) {
    Epetra_Vector d(map); A->ExtractDiagonalCopy(d);
    dinv_ = Teuchos::rcp(new Epetra_Vector(map));
    dinv_->Reciprocal(d);
  }
  int SetUseTranspose(bool) override { return 0; }
  int Apply(const Epetra_MultiVector& X, Epetra_MultiVector& Y) const override {
    for (int j = 0; j < X.NumVectors(); j++)
      Y(j)->Multiply(1.0, *dinv_, *X(j), 0.0);
    return 0;
  }
  int ApplyInverse(const Epetra_MultiVector& X, Epetra_MultiVector& Y) const override { return Apply(X,Y); }
  double NormInf() const override { return 1.0; }
  const char* Label() const override { return "diag"; }
  bool UseTranspose() const override { return false; }
  bool HasNormInf() const override { return true; }
  const Epetra_Comm& Comm() const override { return map_.Comm(); }
  const Epetra_Map& OperatorDomainMap() const override { return map_; }
  const Epetra_Map& OperatorRangeMap() const override { return map_; }
};

int main()
{
  int nx = 100, N = nx*nx;
  Epetra_SerialComm comm;
  Epetra_Map map(N, 0, comm);
  Teuchos::RCP<Epetra_CrsMatrix> A = Teuchos::rcp(new Epetra_CrsMatrix(Copy, map, 5));
  for (int i = 0; i < N; i++) {
    int ix = i % nx, iy = i / nx;
    double d = 0.0; /* set below: strongly anisotropic 5-point stencil (ill-conditioned) */ int cols[5]; double vals[5]; int nc = 0;
    const double eps = 1e-4, SC = 1e-6;  /* anisotropy + global scale <<1: buggy rHr=<Az,r> underestimates ||r||^2 by ~SC -> premature stop */
    d = 2.0 + 2.0*eps;
    cols[nc]=i; vals[nc]=d*SC; nc++;
    if (ix>0)    {cols[nc]=i-1;  vals[nc]=-1.0*SC;  nc++;}
    if (ix<nx-1) {cols[nc]=i+1;  vals[nc]=-1.0*SC;  nc++;}
    if (iy>0)    {cols[nc]=i-nx; vals[nc]=-eps*SC; nc++;}
    if (iy<nx-1) {cols[nc]=i+nx; vals[nc]=-eps*SC; nc++;}
    A->InsertGlobalValues(i, nc, vals, cols);
  }
  A->FillComplete();
  double tol = 1e-10;
  int its[2]; double trueres[2]; int conv[2];
  for (int arm = 0; arm < 2; arm++) {   /* arm 0: standard CG control; arm 1: single reduction */
    Teuchos::RCP<Epetra_MultiVector> x = Teuchos::rcp(new Epetra_MultiVector(map, 1));
    Teuchos::RCP<Epetra_MultiVector> b = Teuchos::rcp(new Epetra_MultiVector(map, 1));
    b->PutScalar(1.0); x->PutScalar(0.0);
    Teuchos::RCP<Belos::LinearProblem<double, Epetra_MultiVector, Epetra_Operator> > prob =
      Teuchos::rcp(new Belos::LinearProblem<double, Epetra_MultiVector, Epetra_Operator>(A, x, b));
    /* no preconditioner: the issue reporter triggered without one, and the
       fixed single-red arm is then bitwise-equal to standard CG */
    prob->setProblem();
    Teuchos::RCP<Teuchos::ParameterList> pl = Teuchos::rcp(new Teuchos::ParameterList());
    pl->set("Fold Convergence Detection Into Allreduce", true);
    pl->set("Convergence Tolerance", tol);
    pl->set("Maximum Iterations", 20000);
    pl->set("Use Single Reduction", arm == 1);
    if (getenv("BELOS_VERBOSE")) { pl->set("Verbosity", 8+16+2); pl->set("Output Frequency", 1); }
    Belos::BlockCGSolMgr<double, Epetra_MultiVector, Epetra_Operator> mgr(prob, pl);
    Belos::ReturnType rt = mgr.solve();
    conv[arm] = (rt == Belos::Converged);
    its[arm] = mgr.getNumIters();
    Epetra_MultiVector r(map, 1);
    A->Multiply(false, *x, r);
    r.Update(1.0, *b, -1.0);
    double rn, bn; r.Norm2(&rn); b->Norm2(&bn);
    trueres[arm] = rn / bn;
    printf("%s: %s its=%d true relres=%.3e %s\n",
           arm ? "single-reduction CG" : "standard CG        ",
           conv[arm] ? "Converged" : "Unconverged", its[arm], trueres[arm],
           (conv[arm] && trueres[arm] > 10*tol) ? "FALSE-CONVERGENCE VIOLATED" :
           (!conv[arm] ? "VIOLATED(unconverged)" : "ok"));
  }
  int bad = (conv[1] && trueres[1] > 10*tol) || !conv[1] || (its[1] > 3*its[0]);
  if (its[1] > 3*its[0]) printf("iteration blowup: single-red %d vs standard %d VIOLATED\n", its[1], its[0]);
  printf("### VERDICT: %s\n", bad ? "VIOLATED" : "PASS");
  return 0;
}
