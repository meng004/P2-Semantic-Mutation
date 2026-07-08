# C-GSL-001 pilot reproduction dossier (Study-2 industrial-expansion pilot)

In-container end-to-end reproduction of the scouted Defect4MR candidate C-GSL-001,
run as the single EASIEST pilot for the Study-2 census feasibility triage. This
verifies **reproduction only** (buggy-arm VIOLATED + patched-arm PASS dual-branch
discrimination). No mutation analysis was run (census-freeze integrity gate).

```yaml
provisional_id: C-GSL-001
project: GNU Scientific Library (GSL), specfunc/gamma_inc.c + cdf/gamma.c
family: Family C
meta_pattern: m_mono
mr_family: f_mono.shape
date: 2026-07-08
verifier: P3 Study-2 industrial-expansion scout (Opus 4.8, sandboxed Linux container)
status_in_ledger: candidate_full            # UNCHANGED — P12 clone not modified
proposed_decision: candidate_full (mechanism-closure confirmed)   # NOT verified_full
promotion_ceiling_reason: >
  No upstream fixed revision exists. The bug-gsl msg03107 patch (crossover
  1e6 -> 1e4 in specfunc/gamma_inc.c) was never merged; the thread died. Per
  docs/open_unfixed_candidate_policy.md an open/unfixed candidate cannot enter
  verified_full without a public fixing commit/PR/release/regression test and a
  fixed-side oracle pass. The "fixed" arm below is a LOCAL mechanism-closure
  patch, recorded as evidence, NOT as a fixed revision.

oracle:
  statement: "For a gamma survival/CDF Q (and P=1-Q), every returned value must lie in the order cone [0,1], and Q must be monotone non-increasing in x. A survival function outside [0,1] is a definitional violation, oracle-free (no reference implementation needed)."
  driver: scripts/cloud/c-gsl-001-verification/gamma_inc_range.c  (P12 repo; reused verbatim)
  trigger: "six large near-equal (a,x) pairs, a in [909922, 991076], x in [909005, 990089]"

arms:
  buggy:
    revision: "GSL 2.8 (official ftp.gnu.org tarball, gsl-2.8.tar.gz, 8997136 bytes)"
    build: "./configure && make -j4  (autotools, gcc 13.3.0, ~4 min wallclock, 4 cores)"
    result: VIOLATED
    observed: "Q up to 1.584198 (pair a=991071,x=990089); P down to -0.584198; +5 monotonicity reversals on the x-grid"
  fixed_local_patch:
    revision: "GSL 2.8 + crossover 1.0e+06 -> 1.0e+04 at specfunc/gamma_inc.c:527 (gsl_sf_gamma_inc_Q_e) and :596 (gsl_sf_gamma_inc_P_e)"
    build: "incremental: make in specfunc/ + relink libgsl; ~15 s"
    result: PASS
    observed: "all six pairs Q in [0.831058, 0.839203] (inside reporter's scipy reference band 0.831-0.839); P in [0.160797, 0.168942]; monotone"

dual_branch_discrimination:
  buggy_verdict:  "### GSL 2.8 VERDICT: VIOLATED"
  fixed_verdict:  "### GSL 2.8 VERDICT: PASS"
  mechanism: >
    The buggy pairs have a ~ 9.1e5-9.9e5, just below the hard-coded 1.0e6 crossover
    that routes near-equal (a,x) to the uniform-asymptotic branch
    (gamma_inc_Q_asymp_unif). Missing it, they fall through to the continued-fraction /
    large-x path, which is inaccurate in this regime and returns Q>1. Lowering the
    threshold to 1.0e4 routes them to the correct branch. This confirms the exact
    root cause named in the bug-gsl report and in reports/cloud/c-gsl-001-verification.md.

reproduction_match: >
  Values match the pre-existing P12 verification report byte-for-byte on the
  headline number (Q=1.584198 buggy; Q~0.8387 patched), independently re-derived
  here from a fresh tarball build. Reproduction is deterministic (no RNG, no MPI,
  no GPU, no threading dependence).

container_feasibility: EASY
  toolchain_needed: "gcc + make + autotools (all preinstalled); one HTTPS fetch of the GSL tarball from ftp.gnu.org (succeeded through the proxy)"
  wallclock_total: "~5 min (tarball fetch + full build + two driver runs)"
  blockers: none

integrity_note: >
  Per the Study-2 pre-registration being drafted in parallel, NO mutation
  operators were generated or run on this case. Mutation outcomes remain unknown
  until census freeze. This dossier is reproduction evidence only.
```

## Command log (abridged)

```
# fetch
curl -sSL -o gsl-2.8.tar.gz https://ftp.gnu.org/gnu/gsl/gsl-2.8.tar.gz   # 8997136 bytes
tar xzf gsl-2.8.tar.gz

# buggy arm
cd gsl-2.8 && ./configure --prefix=$PILOT/install-buggy && make -j4        # BUILD OK
gcc -Igsl-2.8 -o mr_buggy gamma_inc_range.c gsl-2.8/.libs/libgsl.a gsl-2.8/cblas/.libs/libgslcblas.a -lm
./mr_buggy    # -> ### GSL 2.8 VERDICT: VIOLATED   (Q=1.584198 ...)

# fixed (local mechanism-closure patch)
#  edit specfunc/gamma_inc.c :527  a >= 1.0e+06  ->  a >= 1.0e+04
#  edit specfunc/gamma_inc.c :596  a >  1.0e+06  ->  a >  1.0e+04
cd gsl-2.8/specfunc && make ; cd gsl-2.8 && make                            # incremental relink
gcc -Igsl-2.8 -o mr_fixed gamma_inc_range.c gsl-2.8/.libs/libgsl.a gsl-2.8/cblas/.libs/libgslcblas.a -lm
./mr_fixed    # -> ### GSL 2.8 VERDICT: PASS       (Q=0.831058..0.839203)
```

Raw logs held under the session scratchpad `pilot_repro/{buggy_arm.log, fixed_arm.log}`.
The P12 clone at /workspace/p12-defect4mr was NOT modified.
