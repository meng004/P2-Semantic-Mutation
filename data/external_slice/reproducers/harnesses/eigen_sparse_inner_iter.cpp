/* F-EIGEN-001 issue-property driver (m_conv / f_conv.repr): RowMajor vs ColMajor
 * representation equivalence of SparseMatrix InnerIterator enumeration.
 * Issue (Bugzilla/GitLab #718, Eigen 3.2): the reporter's loop instantiates
 * SparseMatrix<float>::InnerIterator (COL-major iterator type) on a ROW-major
 * matrix; in Eigen 3.2 this silently converts to a temporary and yields
 * garbage.  issue-property: enumerating the same logical matrix in both storage orders
 * must give the identical (row,col,value) multiset.
 */
#include <cstdio>
#include <vector>
#include <tuple>
#include <algorithm>
#include <Eigen/Sparse>
using namespace Eigen;
typedef std::vector<std::tuple<int,int,float> > Trip;

int main() {
  Trip col_t, row_ok_t;
  SparseMatrix<float> B(5,5); B.insert(0,0)=1.f;
  for (int k=0;k<B.outerSize();++k)
    for (SparseMatrix<float>::InnerIterator it(B,k); it; ++it)
      col_t.push_back(std::make_tuple((int)it.row(),(int)it.col(),it.value()));
  SparseMatrix<float,RowMajor> A(5,5); A.insert(0,0)=1.f;
  /* correct-usage control */
  for (int k=0;k<A.outerSize();++k)
    for (SparseMatrix<float,RowMajor>::InnerIterator it(A,k); it; ++it)
      row_ok_t.push_back(std::make_tuple((int)it.row(),(int)it.col(),it.value()));
  printf("colmajor enumeration: n=%zu first=(%d,%d,%g)\n", col_t.size(),
         col_t.empty()?-1:std::get<0>(col_t[0]), col_t.empty()?-1:std::get<1>(col_t[0]),
         col_t.empty()?0.0:(double)std::get<2>(col_t[0]));
  printf("rowmajor correct-iterator enumeration: n=%zu first=(%d,%d,%g)\n", row_ok_t.size(),
         row_ok_t.empty()?-1:std::get<0>(row_ok_t[0]), row_ok_t.empty()?-1:std::get<1>(row_ok_t[0]),
         row_ok_t.empty()?0.0:(double)std::get<2>(row_ok_t[0]));
#ifdef TRY_ISSUE_CODE
  /* the issue's literal pattern: col-major iterator type on row-major matrix */
  Trip bad_t;
  for (int k=0;k<A.outerSize();++k)
    for (SparseMatrix<float>::InnerIterator it(A,k); it; ++it)
      bad_t.push_back(std::make_tuple((int)it.row(),(int)it.col(),it.value()));
  printf("issue-pattern enumeration: n=%zu", bad_t.size());
  if (!bad_t.empty()) printf(" first=(%d,%d,%g)", std::get<0>(bad_t[0]), std::get<1>(bad_t[0]), (double)std::get<2>(bad_t[0]));
  printf("\n");
  bool ok = bad_t.size()==1 && std::get<0>(bad_t[0])==0 && std::get<1>(bad_t[0])==0 && std::get<2>(bad_t[0])==1.f;
  printf("### issue-pattern issue-property (must equal colmajor multiset): %s\n", ok?"PASS":"VIOLATED");
#else
  printf("### issue-pattern DID NOT COMPILE on this revision (guarded misuse)\n");
#endif
  return 0;
}
