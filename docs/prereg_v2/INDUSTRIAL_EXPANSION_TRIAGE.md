# Study-2 Industrial-Corpus Expansion: Feasibility Triage + Pilot Reproduction

**Round scope:** feasibility triage of the 17 scouted Defect4MR candidates + one
end-to-end pilot reproduction, to let the Study-2 census protocol set a realistic
recruitment target.
**Date:** 2026-07-08. **Container:** sandboxed Linux, 4 cores, 15 GiB RAM, gcc/g++
13.3.0, cmake 3.28, python 3.11; **no gfortran, no MPI, no CUDA/GPU, no docker**;
HTTPS via proxy (ftp.gnu.org + github + pip reachable).
**Source ledger:** `/workspace/p12-defect4mr/data/ledgers/candidates.json`
(status counts: 35 verified_full, 16 candidate_full, 1 candidate_needs_oracle, 12 rejected).

---

## 0. Headline finding (read this first)

There are **two independent gates** on every candidate, and they must not be conflated:

- **Gate A — container/infrastructure feasibility:** can the two arms be built and
  the oracle driver run here (or on a normal workstation, or only on special hardware)?
- **Gate B — fix-provenance eligibility:** can the case ever reach `verified_full`?
  Per `docs/open_unfixed_candidate_policy.md` (Upgrade Path), `verified_full`
  **requires a public fixed revision** (fixing commit / PR / release / regression test)
  **plus a fixed-side oracle pass**.

**All 16 `candidate_full` are open/unfixed bugs** (every `revisions.fixed` is
"unknown" / "none released" / "closed without merge"). Under the project's own
policy they are structurally **capped at `candidate_full`** (secondary open-unfixed
pool) and are explicitly barred from being called "verified". The **only** candidate
in scope with a real merged fix is **E-PETSC-004**, and it is **already** `verified_full`.

**Consequence for the census:** reaching **45 `verified_full`** (34 -> +11) is **not
achievable from this 17-candidate pool on ANY infrastructure**, because the blocker is
fix-provenance, not compute. Zero of the 17 can be newly promoted to `verified_full`
as of the 2026-07-03/04 scan. See §4.

---

## 1. Feasibility matrix (ranked; 17 candidates)

`Gate A`: EASY = pure-Python/pip or simple C build, reproduces here.
MEDIUM = autotools/cmake/apt-installable deps (gfortran/MPI/DL-backend), reproduces on
a normal workstation; MEDIUM-in-container if only an apt/pip install is missing.
HARD = GPU / foreign-arch / multi-build / heavy external-download PETSc stacks.
`Gate B`: OPEN = no upstream fix -> `candidate_full` ceiling. FIXED = merged fix exists.

| Rank | Case | Gate A | Gate B | Build path | Concrete blocking reason |
|---|---|---|---|---|---|
| 1 | **C-GSL-001** | **EASY** | OPEN | GSL autotools C build | none — **PILOTED, dual-arm confirmed** (see §2). Fix never merged -> candidate_full only. |
| 2 | A-LAPACK-005 | MEDIUM | OPEN | LAPACKE cmake build | needs `gfortran` (apt) for LAPACK core; deterministic sentinel oracle but uninitialised-memory read -> assert on preserved-sentinel positions. |
| 3 | A-LAPACK-003 | MEDIUM | OPEN | LAPACK cmake build | needs `gfortran` (apt). Risk: 9-yr-open, may be inherent MRRR precision limit, not a clean logic bug — verify genuine (not borderline-tol) orthogonality violation. |
| 4 | C-DEEPXDE-001 | MEDIUM | OPEN | pip `deepxde` + backend | pure-Python geometry bug (observable w/o training); needs a DL backend install (tf/torch, large pip). Full MR needs short CPU PINN train. |
| 5 | C-DEEPXDE-002 | MEDIUM | OPEN | pip `deepxde` + backend | short CPU PINN training w/ PDEPointResampler (minutes). Backend install is the only heavy step. |
| 6 | C-DEEPXDE-003 | MEDIUM | OPEN | pip `deepxde` + backend | short CPU inverse-problem PINN training; trainable `dde.Variable` inside IC/BC. |
| 7 | B-FFTW-001 | MEDIUM | OPEN | FFTW autotools + OpenMPI | needs `libopenmpi-dev` (apt); reviewer already reproduced on plain x86_64+OpenMPI (1-rank pass / 2-rank fail rel-err 1.03e-2). |
| 8 | B-FFTW-005 | MEDIUM | OPEN | FFTW autotools + MPI | static half of oracle needs no MPI cluster; root-caused to mpi/api.c block1==n1. Needs MPI for full partition check. |
| 9 | B-FFTW-004 | MEDIUM | OPEN | FFTW `--enable-generic-simd256` | reproduced (rel-err 0.15-0.34, n in {12,16,20,32,64}); codelet-routing sensitive — must sweep sizes. Simple autotools, specific configure flags. |
| 10 | E-PETSC-006 | HARD | OPEN | PETSc source build (CPU) | pure-CPU SNES/linesearch; MEDIUM on a workstation. HARD-in-container: `--download-fblaslapack` fetches from external hosts (proxy risk) + 20-40 min heavy build. |
| 11 | E-PETSC-002 | HARD | OPEN | PETSc source build (CPU) | same PETSc build cost/download risk; reviewer already built v3.21.3 `--with-mpi=0 --download-fblaslapack`. MR !9061 **closed without merge** -> OPEN. |
| 12 | E-PETSC-003 | HARD | OPEN | PETSc source build (CPU) | PETSc build + must construct ill-conditioned SPD system to trigger near-zero denom; no MR opened. |
| 13 | E-PETSC-007 | HARD | OPEN | **two** PETSc builds | reproduction compares 3.19 vs >=3.20 behaviour -> two full PETSc builds. Fix status unclear (issue closed, no linked MR). |
| 14 | E-PETSC-005 | HARD | OPEN | PETSc **+ Hypre** build | `--download-hypre`; risk root cause is Hypre-internal (BoomerAMGSolveT not adjoint) -> could reclassify toward closed-backend exclusion. |
| 15 | E-PETSC-004 | HARD | **FIXED** | PETSc **+ Kokkos + MPI** | **already verified_full** (merged MR !9403). Task question = can its *mutation arm* be completed here? No: needs MATMPIAIJKOKKOS (Kokkos backend) + >=2 MPI ranks. Not in-container. |
| 16 | B-FFTW-002 | HARD | OPEN | FFTW AVX2/AVX512 | env-sensitive: prior x86_64 cloud run (commit 9d49fad, 1000+1000 iters) got fail_count=0 — **did not reproduce**. Getting a positive discriminator is the blocker, not the build. |
| 17 | A-CUPY-002 | HARD | OPEN | CuPy + CUDA GPU | **requires NVIDIA GPU** (none here); non-deterministic (nan on 2/10 runs). Qualitative violation reproducible only on GPU. |

Additional (not in the "17", listed for completeness):
`F-SUITESPARSE-005` (candidate_needs_oracle) — **HARD / OPEN**: ppc64le + Alpine/musl
JIT-semiring behaviour; needs foreign-arch hardware or emulation; infeasible on x86_64.

**Gate-A bucket counts (of 17):** EASY = **1**, MEDIUM = **8**, HARD = **8**.
**Gate-B counts (of 17):** OPEN/unfixed = **16**, FIXED = **1** (E-PETSC-004, already verified).

---

## 2. Pilot log summary — C-GSL-001 (SUCCESS)

Picked as the single EASIEST (Gate A = EASY, self-contained deterministic C driver
already present in the P12 repo). Full dossier: `pilot_verification_c-gsl-001.md`.

- **Fetch+build:** `gsl-2.8.tar.gz` from ftp.gnu.org (proxy OK); `./configure && make -j4`,
  gcc 13.3.0, ~4 min.
- **Buggy arm (stock GSL 2.8):** `### GSL 2.8 VERDICT: VIOLATED` — Q up to **1.584198**
  (a=991071, x=990089), P negative, +5 monotonicity reversals. Matches the pre-existing
  P12 verification report byte-for-byte on the headline number.
- **Fixed arm (local patch, crossover 1.0e+06 -> 1.0e+04 at gamma_inc.c:527 & :596):**
  `### GSL 2.8 VERDICT: PASS` — all six pairs Q in **[0.831, 0.839]** (inside the
  reporter's scipy band), monotone. Incremental relink, ~15 s.
- **Dual-branch discrimination: DEMONSTRATED** (VIOLATED buggy / PASS fixed).
- **Integrity:** no mutation operators generated or run (census-freeze gate honoured).
- **Honest cap:** the "fixed" arm is a **local mechanism-closure patch, never merged
  upstream** -> this is `candidate_full` evidence, **not** a `verified_full` promotion.

Container-feasibility of the *reproduction workflow* is thereby proven end-to-end;
the promotion ceiling is set by Gate B, not by the container.

---

## 3. Infrastructure needed, by candidate (the honest bill of materials)

| Tier | Cases | What it takes |
|---|---|---|
| **Reproducible in THIS container** (candidate_full-grade dual-arm) | C-GSL-001 (done). Plausibly + A-LAPACK-003/005, B-FFTW-004 after `apt install gfortran`/FFTW flags. | preinstalled toolchain + 1-2 apt installs |
| **Normal Linux workstation** (apt/pip + hours, no special HW) | + C-DEEPXDE-001/002/003 (DL backend + CPU PINN), B-FFTW-001/005 (OpenMPI), E-PETSC-002/003/006 (single PETSc CPU build, if `--download-*` hosts reachable) | gfortran, OpenMPI, tf/torch, PETSc build chain, ~0.5-2 h each |
| **Special hardware / heavy multi-build CI** | A-CUPY-002 (NVIDIA GPU), F-SUITESPARSE-005 (ppc64le/emulation), E-PETSC-004 (Kokkos+MPI), E-PETSC-005 (Hypre), E-PETSC-007 (dual-version builds), B-FFTW-002 (env-tuned SIMD, may never reproduce) | GPU / foreign arch / large CI matrix |

---

## 4. Recruitment forecast (against the "minimum 45 else under-recruited" bar)

**(a) Verifiable-to-`verified_full` in THIS container: 0 of 17.**
The pilot reaches only `candidate_full` (mechanism closure); every other candidate is
also open/unfixed. Container capacity is *not* the limiting factor.

**(b) Verifiable-to-`verified_full` on a normal Linux workstation: 0 of 17.**
More compute reproduces more *buggy arms* and mechanism-closure patches, but **Gate B is
unchanged** — no upstream fix means no `verified_full` regardless of workstation power.

**(c) Only with special hardware / heavy CI: still 0 of 17 for `verified_full`** — GPU
(CuPy), ppc64le (SuiteSparse), Kokkos/Hypre (PETSc) unlock *reproduction*, not *fixes*.

### Is +11 (34 -> 45 verified_full) realistic? **No — not from this pool.**

- 16 of 17 are open/unfixed -> policy ceiling `candidate_full`. The 17th (E-PETSC-004)
  is already counted.
- The gating action to grow `verified_full` is **NOT** provisioning GPUs/MPI/PETSc; it is
  **fix-provenance**: a candidate only becomes eligible when an upstream fix lands and a
  fixed-arm oracle pass is captured.

### Recommended census-protocol wording (honest options)

1. **Re-scan fix status TODAY (2026-07-08).** The reviewer notes are dated 2026-07-03/04;
   PETSc/FFTW/LAPACK move fast. Any of the 16 whose upstream issue has since merged a fix
   becomes `verified_full`-eligible (Gate A permitting). This is the **single highest-yield
   action** and should precede setting the target. Realistic yield: a handful at most, not 11.
2. **Recruit NEW candidates that already carry a merged fix** (the E-PETSC-004 shape:
   closed issue + merged MR + source-area attribution). This is the only reliable route to
   +11 `verified_full`, and it is orthogonal to this container's limits.
3. **If the target must stay 45 and the pool stays as-is: register UNDER-RECRUITED
   honestly.** Do not relabel open/unfixed `candidate_full` as "verified" — the policy
   (`open_unfixed_candidate_policy.md`) explicitly forbids "verified defect" / "buggy/fixed
   pair" wording for these, and bars them from primary Real-MRDefect.
4. **Alternatively, register a two-tier census:** primary = `verified_full` (fix-backed);
   secondary = open/unfixed `candidate_full` (buggy-arm + mechanism-closure evidence, e.g.
   C-GSL-001). Report them separately; never pool the secondary into the primary count.

**Bottom line:** infrastructure lets us *reproduce* ~9/17 in-container-to-workstation and
another ~6 only on special hardware, but *promotion to `verified_full`* is fix-gated, so the
industrial arm cannot reach 45 verified from these 17. Grow the pool with fix-backed
candidates, or register the shortfall.
