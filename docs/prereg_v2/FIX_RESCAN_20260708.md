# Study-2 Fix-Rescan of Open candidate_full Cases — 2026-07-08

**Scope:** Re-scan of all 16 `candidate_full` cases in the Defect4MR ledger
(`/workspace/p12-defect4mr/data/ledgers/candidates.json`) for upstream fixes
**merged since the last scan (2026-07-03)**. Every one of the 16 was previously
capped at `candidate_full` solely because its upstream defect is open/unfixed
(Gate B), per `docs/prereg_v2/INDUSTRIAL_EXPANSION_TRIAGE.md`.

**Method:** State verified live via public issue/PR pages and public APIs:
GitHub issues via `github.com/<repo>/issues/<n>` HTML; GitLab/PETSc via the
public `gitlab.com/api/v4` issue/MR endpoints; GSL (mailing-list bug, no tracker)
via the upstream `cgit` file history. GitHub's unauthenticated REST API returned
403 through the egress proxy, so GitHub HTML pages were used instead (state badge
is definitive). No mutation analysis performed on any case (census-freeze honoured).

**Classification key:** FIXED-MERGED = fix merged to default branch after 2026-07-03;
FIX-IN-REVIEW = PR/MR open; STILL-OPEN = no movement; UNREACHABLE = could not verify.

---

## Rescan table (16 rows)

| Case ID | Project | Issue / PR | State (2026-07-08) | Evidence | Promotion-ready? |
|---|---|---|---|---|---|
| B-FFTW-001 | FFTW | [gh issue #20](https://github.com/FFTW/fftw3/issues/20) | STILL-OPEN | Issue #20 "Bug in MPI planner for Nx1 transforms" shown OPEN; no linked PR/merge. | No |
| B-FFTW-002 | FFTW | [gh issue #294](https://github.com/FFTW/fftw3/issues/294) | STILL-OPEN | Issue #294 (avx/avx2 + generic-simd256) shown OPEN; no fix commit/PR mentioned. | No |
| B-FFTW-004 | FFTW | [gh issue #328](https://github.com/FFTW/fftw3/issues/328) | STILL-OPEN | Issue #328 (`--enable-generic-simd256` r2c memory error) shown OPEN; no comments/PR. | No |
| B-FFTW-005 | FFTW | [gh issue #174](https://github.com/FFTW/fftw3/issues/174) + [PR #413](https://github.com/FFTW/fftw3/pull/413) | FIX-IN-REVIEW | Issue #174 OPEN ("No branches or pull requests"). Coordinator PR #413 (author meng004, base FFTW:master, the `<`→`<=` fix in `mpi/api.c`) is **OPEN, not merged**. Per FIXARM-POLICY only an upstream MERGE upgrades; no merge as of today. | No (PR open, unmerged) |
| A-CUPY-002 | cupy/cupy | [#5024](https://github.com/cupy/cupy/issues/5024) [#6446](https://github.com/cupy/cupy/issues/6446) [#7495](https://github.com/cupy/cupy/issues/7495) [#8486](https://github.com/cupy/cupy/issues/8486) | STILL-OPEN | All four `eigsh`/`_eigen.py` issues shown OPEN; no linked merged fix PR touching `cupyx/scipy/sparse/linalg/_eigen.py`. | No |
| E-PETSC-002 | petsc/petsc | [issue #1869](https://gitlab.com/petsc/petsc/-/issues/1869) + [MR !9061](https://gitlab.com/petsc/petsc/-/merge_requests/9061) | STILL-OPEN | API: issue #1869 `state=opened`, updated 2026-02-21, `closed_at=null`. MR !9061 `state=closed`, `merged_at=null`, closed 2026-02-21 (target `main`) — **closed WITHOUT merge**. No new activity since last scan. | No |
| E-PETSC-003 | petsc/petsc | [issue #1862](https://gitlab.com/petsc/petsc/-/issues/1862) | STILL-OPEN | API: `state=opened`, updated 2026-02-21, `closed_at=null`. No MR. | No |
| E-PETSC-005 | petsc/petsc | [issue #840](https://gitlab.com/petsc/petsc/-/issues/840) | STILL-OPEN | API: `state=opened`, updated 2021-02-15, `closed_at=null`. No linked fix (Hypre BoomerAMG adjoint). | No |
| A-LAPACK-003 | Reference-LAPACK/lapack | [gh issue #151](https://github.com/Reference-LAPACK/lapack/issues/151) | STILL-OPEN | Issue #151 "DSYEVR returns non-orthogonal vectors" shown OPEN, still assigned oamarques; no merged PR. | No |
| C-DEEPXDE-001 | lululxvi/deepxde | [gh issue #2071](https://github.com/lululxvi/deepxde/issues/2071) | STILL-OPEN | Issue #2071 (CSG periodic points) shown OPEN; no PR/commit linked. | No |
| C-DEEPXDE-002 | lululxvi/deepxde | [gh issue #2073](https://github.com/lululxvi/deepxde/issues/2073) | STILL-OPEN | Issue #2073 (BC loss with PDEPointResampler) shown OPEN; no PR/commit linked. | No |
| C-DEEPXDE-003 | lululxvi/deepxde | [gh issue #2074](https://github.com/lululxvi/deepxde/issues/2074) | STILL-OPEN | Issue #2074 (IC/BC caching in inverse problems) shown OPEN; no upstream PR (reporter's private fork only). | No |
| E-PETSC-006 | petsc/petsc | [issue #1583](https://gitlab.com/petsc/petsc/-/issues/1583) | STILL-OPEN | API: `state=opened`, updated 2024-05-03, `closed_at=null`. No linked fix (`linesearchcp.c`). | No |
| E-PETSC-007 | petsc/petsc | [issue #1667](https://gitlab.com/petsc/petsc/-/issues/1667) | CLOSED (2024-11-13, pre-scan; no code fix) | API: `state=closed`, `closed_at=2024-11-13`, updated 2024-11-13. Close **predates** the 2026-07-03 scan; no linked merged MR/commit (ledger: closed as documented 3.20 behavior change). No movement since last scan → not a new fix. | No |
| C-GSL-001 | GSL specfunc/cdf | [bug-gsl msg03107](http://www.mail-archive.com/bug-gsl@gnu.org/msg03107.html) | STILL-OPEN | Mailing-list bug (no issue tracker). Upstream cgit history of `specfunc/gamma_inc.c` shows newest commit **2008-12-04**; the crossover 1e6→1e4 patch was never merged. Mechanism-closure patch remains local-only. | No |
| A-LAPACK-005 | Reference-LAPACK/lapack | [gh issue #729](https://github.com/Reference-LAPACK/lapack/issues/729) | STILL-OPEN | Issue #729 (`LAPACKE_xLACPY` row-major) shown OPEN; reporter offered a fix but no merged PR touching `LAPACKE/src/lapacke_*lacpy_work.c`. | No |

---

## Summary

- **N_rescued (FIXED-MERGED since 2026-07-03): 0**
- **FIX-IN-REVIEW: 1** — B-FFTW-005 (coordinator PR #413 open, unmerged; upgrade waits on an upstream merge).
- **STILL-OPEN: 14** — B-FFTW-001, B-FFTW-002, B-FFTW-004, A-CUPY-002, E-PETSC-002, E-PETSC-003, E-PETSC-005, A-LAPACK-003, C-DEEPXDE-001, C-DEEPXDE-002, C-DEEPXDE-003, E-PETSC-006, E-PETSC-007 (closed 2024 without a code fix; predates last scan), C-GSL-001.
- **UNREACHABLE: 0** — every case's state was directly observed.

**Conclusion:** No candidate promoted this round. The Gate-B blocker (fix-provenance)
is unchanged for all 16; the only movement is the still-open coordinator self-fix
PR #413 for B-FFTW-005. Ledger is unmodified (P12 census-freeze respected); this is a
read-only scan. Recommend re-scanning on the next cadence, with B-FFTW-005 (PR #413)
and E-PETSC-002 (MR history) as the highest-probability future flips.
