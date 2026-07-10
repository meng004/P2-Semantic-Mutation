# Study 5, Amendment A1: Family-XL corpus roster + certification audit trail

**Date**: 2026-07-10. **Status**: executes the FROZEN selection protocol of
`PREREGISTRATION_STUDY5_v1.md` §2b and the certification admission gate of
§2c, in the registration's one scheduled pre-mutant amendment slot (§7 item
6). **Pre-mutant attestation**: at the time of this freeze NO Family-XL
mutant, pilot pool (`v8xl_pilot`), SMS value, or any other Study-5 behavioral
outcome exists; the only behavioral measurements taken are the §2c
certification measurements recorded below. Machine-readable roster:
`configs/xl_roster.json`; certification SSOT:
`data/results/study5_xl_certification.json`; candidate registry (rank order,
instantiability documentation, frozen aux, declared exceptions):
`src/p2/xlport/registry.py`.

**Headline**: achieved certified n = **21 program-language pairs** (floor 12
met, target 20 exceeded, cap 28 respected), 13 distinct external programs, 5
non-Python languages certified (C, C++, Java, Rust, Julia; Go enumerated, its
only pair failed certification and is disclosed). Read-off power at the
frozen §4a primary-DGP curve: largest tabulated n <= 21 is n = 20, power
**0.8484** (>= the 0.80 design target; no post-data simulation).

---

## 1. Protocol execution summary

| Step (§2b) | Execution |
|---|---|
| Step 1 coverage targets | five strata MP1..MP5 (`f_inv.con`, `f_mono.stat`, `f_conv.lim`, `f_mono.shape`, `f_conv.rate`); instantiability documented per candidate in `registry.py` BEFORE any behavioral run |
| Step 2 sources (fixed order) | 1 TheAlgorithms {Python,C,C-Plus-Plus,Java,Go,Rust}; 2 GNU GSL vs scipy; 3 Julia stdlib/SciML vs scipy; 4 Apache Commons Math vs scipy; 5 Boost.Math vs scipy |
| Step 3 screen | license / determinism-seedability / single-entry scalar interface on [0,1] / >= 2-language availability; every rejection recorded in §3 below with the criterion cited |
| Step 4 ranking | sort key (c desc, l desc, source-index asc, name asc); full table in §4; `registry.rank_check()` asserts the stored order equals the registered total order |
| Step 5 greedy walk | certification in rank order; stop after program `besselj0`: certified n = 21 >= target 20 AND every family instantiable on >= 2 certified programs |
| Step 6 fallback | NOT invoked: no hand-port was needed (every family reached >= 2 external programs) |

Toolchains (registered §2c set): gcc 13.3.0 (`-std=c99 -O0 -Wall -lm`),
g++ 13.3.0 (`-O0 -Wall`), OpenJDK 21.0.10 (javac/java), rustc 1.94.1
(opt-level 0), go 1.24.7, Julia 1.11.7 (official binary tarball; the
execution environment ships no Julia toolchain, see §7 D2). Python side:
CPython 3.11.15, scipy 1.17.1, numpy 2.4.6.

Adapter layer: `src/p2/xlport/` (subprocess line REPL, the registered
`src/p2/cport` CPutProgram pattern). Every program under test is externally
authored and vendored UNMODIFIED under `third_party/` (provenance:
`third_party/PROVENANCE_STUDY5_XL.md`); the only hand-written execution code
is the wrapper shims in `src/p2/xlport/shims/<pairid>/` and the Python-side
reference shims in `src/p2/xlport/pyref/` (P1, §1.6).

## 2. Candidate enumeration (Step 2)

Enumeration method (deterministic, documented): (a) source 1: the six repos
were cloned at the pinned commits below and same-named algorithm files
intersected across languages (stem normalisation + keyword sweep over the
numerics directories: bisect/newton/secant/simpson/trapezoid/euler/
rungekutta/montecarlo/integration/interpolat/sqrt/sigmoid/tanh/softmax/
sin/pi); (b) sources 2/4/5: scipy.special / scipy.optimize / scipy.integrate
top-level real scalar-in/scalar-out entry points intersected with same-name
entries of GSL, Commons Math, and Boost.Math; (c) source 3: Julia stdlib
scalar entry points with documented numpy/scipy-equivalent semantics
(`Statistics.quantile` type-7, `Base.sinc` normalized). Equation-governed
numerics preferred per §2b (discrete/combinatorial algorithms not
enumerated: NOETHER count law predicts they cannot serve the five-family
grid).

Pinned upstreams:

| Source | Upstream | Pin | License |
|---|---|---|---|
| 1 | TheAlgorithms/Python | `c0db072a1323339e0d9148479f8818a1b9768d88` | MIT |
| 1 | TheAlgorithms/C | `e5dad3fa8def3726ec850ca66a7f51521f8ad393` | GPL-3.0 (nothing vendored; all C-repo candidates screened out) |
| 1 | TheAlgorithms/C-Plus-Plus | `b9c118fb5dca86f6325e816481959e1e6c360373` | MIT |
| 1 | TheAlgorithms/Java | `fd2858e7e6138d9f8940ee9820e172912a5acfb4` | MIT |
| 1 | TheAlgorithms/Go | `5ba447ec5ff3d1213de65b92e726ee74c5d5cc19` | MIT |
| 1 | TheAlgorithms/Rust | `c65d014621a9d50b36b197f08bb1c8016ff505b0` | MIT |
| 2 | GNU GSL | Ubuntu `libgsl-dev 2.7.1+dfsg-6ubuntu2`, linked as unmodified system library | GPL-3.0 |
| 3 | Julia stdlib | Julia 1.11.7 official binary | MIT |
| 4 | Apache Commons Math | `commons-math3:3.6.1` (jar sha256 `1e56d7b0...7ef2b308`) | Apache-2.0 |
| 5 | Boost.Math | `8ee12a5355935cbaac5d5338372d0d0e3311b473` (`include/` vendored) | BSL-1.0 |

## 3. Step-3 screening audit (rejected candidates, criterion cited)

| Candidate | Rejection (registered criterion) |
|---|---|
| bisection (C `bisection_method.c` + Python `bisection.py`) | C entry hardcodes f(t)=t^3+2t-10: program(x) constant in x, zero instantiable strata (S3 crit. 3) |
| bisection (C++ `bisection_method.cpp`) | all logic in `main()`, no callable entry (S3 crit. 3) |
| newtonraphson (C `newton_raphson_root.c`) | `srand(time(NULL))` random initial guess, not seedable (S3 crit. 2) |
| newtonraphson (C++ `newton_raphson_method.cpp`) | `std::srand(std::time(nullptr))` random start, not seedable (S3 crit. 2) |
| secant (C `secant_method.c` / Python `secant_method.py`) | different hardcoded targets (t^2-3 vs 8t-2e^-t): no same-semantics reference; C output constant in x (S3 crit. 3+4) |
| simpson (C `simpsons_1_3rd_rule.c`) | hardcoded integrand 1+u^3 vs Python side's u^2; float32; scanf-interactive main (S3 crit. 4) |
| simpson (Java `SimpsonIntegration.java`) | hardcoded integrand e^-u(4-u^2) vs Python side's u^2 (S3 crit. 4) |
| euler (C/C++ `ode_forward_euler.*`) | hardcoded 2-component SHO system; external Python euler is scalar-only (S3 crit. 4) |
| invsqrt (Java `FastInverseSqrt.java`) | entries return boolean, not the numeric value (S3 crit. 3) |
| mcpi (Go `montecarlopi.go` + Python) | Go RNG seeded from wall clock inside the function, not injectable; §2c RNG-stream precondition structurally unsatisfiable; Python side then has l=0 (S3 crit. 2, 4) |
| sin (Go `sin.go` + Python `sin.py`) | degrees-based vs radians semantics (S3 crit. 4) |
| softmax (Python + Rust) | vector-in/vector-out; scalar freeze degenerates to a sigmoid variant (S3 crit. 3) |
| runge_kutta_gills / fehlberg_45 (Python) | no same-named cross-language counterpart, l=0 (S3 crit. 4) |
| cubic spline (GSL vs scipy) | boundary-condition semantics differ (natural vs not-a-knot) (S3 crit. 4) |
| adaptive ODE (GSL rkf45 vs scipy RK45) | method heterogeneity (Fehlberg vs Dormand-Prince), no documented shared band (S3 crit. 4) |
| Julia SciML (source-3 SciML half) | package installation unavailable in the execution environment; stdlib-only enumeration, disclosed shortfall (Step 5 disclosure; see §7 D2) |

## 4. Step-4 deterministic ranking (admissible candidates)

Sort key: (c desc, l desc, source-index asc, name asc). c = number of the
five strata instantiable (documented per candidate in `registry.py`, judged
from governing structure + the frozen adapter interface, before any
behavioral run); l = number of non-Python languages with a same-semantics
external implementation.

| Rank | Program | c | l | Src | Pairs |
|---|---|---|---|---|---|
| 1 | trapezoid | 5 | 1 | 1 | trapezoid.rs |
| 2 | invsqrt | 4 | 2 | 1 | invsqrt.cpp, invsqrt.go |
| 3 | simpson | 4 | 2 | 1 | simpson.cpp, simpson.rs |
| 4 | brent | 4 | 2 | 2 | brent.c, brent.java |
| 5 | euler | 4 | 1 | 1 | euler.java |
| 6 | newton | 4 | 1 | 1 | newton.rs |
| 7 | rungekutta | 4 | 1 | 1 | rungekutta.cpp |
| 8 | betainc | 3 | 3 | 2 | betainc.c, betainc.cpp, betainc.java |
| 9 | erf | 3 | 3 | 2 | erf.c, erf.cpp, erf.java |
| 10 | normcdf | 3 | 3 | 2 | normcdf.c, normcdf.cpp, normcdf.java |
| 11 | sigmoid | 3 | 1 | 1 | sigmoid.rs |
| 12 | tanh | 3 | 1 | 1 | tanh.rs |
| 13 | quad | 3 | 1 | 2 | quad.c |
| 14 | quantile | 3 | 1 | 3 | quantile.jl |
| 15 | besselj0 | 2 | 3 | 2 | besselj0.c, besselj0.cpp, besselj0.java |
| 16 | digamma | 2 | 3 | 2 | (not reached) |
| 17 | gamma | 2 | 3 | 2 | (not reached) |
| 18 | gammainc | 2 | 3 | 2 | (not reached) |
| 19 | expint | 2 | 2 | 2 | (not reached) |
| 20 | legendre | 2 | 2 | 2 | (not reached) |
| 21 | zeta | 2 | 2 | 2 | (not reached) |
| 22 | sinc | 2 | 1 | 3 | (not reached) |

## 5. §2c certification gate results (201-point grid, x_i = i/200)

Rule: PASS iff for all i, |y_L(x_i) - y_py(x_i)| <= tol * max(|y_py(x_i)|, 1)
with BOTH sides finite; tol = 1e-6 unless a class-1 exception was declared
in the registry BEFORE the run (§6). One-shot: no re-certification.

| Pair | Status | max rel dev | argmax x | Note |
|---|---|---|---|---|
| trapezoid.rs | **FAIL** | 4.76e-2 | 0.82 | external Python reference drops trailing interior abscissas: its accumulated `while x <= b-h` loop is float-fragile at the exact-lattice boundary; the Rust side (exact multiplicative abscissas) disagrees at grid points where the Python generator loses the last point |
| invsqrt.cpp | PASS | 7.10e-8 | 0.205 | `Fast_InvSqrt<float,1>` matches the Python float32 1-iteration semantics |
| invsqrt.go | **FAIL** | 1.75e-3 | 0.475 | external Go entry hardcodes TWO Newton iterations vs Python's ONE (measured exactly at the predicted magnitude of the 1-iteration residual) |
| simpson.cpp | **FAIL** | 2.82e-1 | 0.935 | external Python reference is numerically defective: strict `<` in `make_points` systematically drops the final interior abscissa and shifts weight parity (its own doctests enshrine `method_2([0,1],1000)=0.3320026653` vs exact 1/3); the C++ side computes correct composite Simpson |
| simpson.rs | **FAIL** | 2.82e-1 | 0.91 | same reference defect (Rust computes correct per-subinterval Simpson) |
| brent.c | PASS | 2.30e-13 | 0.40 | |
| brent.java | PASS | 5.80e-13 | 0.405 | |
| euler.java | PASS | 0.0 | - | bit-identical (dyadic h=1/128, 256 steps, identical update expression) |
| newton.rs | PASS | 7.84e-7 | 0.165 | inside the declared 2e-6 band; also inside the standard 1e-6 gate |
| rungekutta.cpp | PASS | 0.0 | - | bit-identical trajectories (dyadic h=1/64, 128 steps) |
| betainc.c | PASS | 1.78e-15 | 0.49 | |
| betainc.cpp | PASS | 3.33e-16 | 0.555 | |
| betainc.java | PASS | 1.28e-15 | 0.49 | |
| erf.c | PASS | 3.33e-16 | 0.71 | |
| erf.cpp | PASS | 2.22e-16 | 0.26 | |
| erf.java | PASS | 4.44e-16 | 0.19 | |
| normcdf.c | PASS | 1.11e-16 | 0.40 | |
| normcdf.cpp | PASS | 1.11e-16 | 0.55 | |
| normcdf.java | PASS | 2.22e-16 | 0.695 | |
| sigmoid.rs | PASS | 7.29e-8 | 0.98 | float32 external side vs float64 reference, inside the unit-floor gate |
| tanh.rs | PASS | 1.46e-7 | 0.98 | float32 external side |
| quad.c | PASS | 0.0 | - | GSL QUADPACK GAUSS21 vs scipy QUADPACK qagse at epsabs=epsrel=1e-10 |
| quantile.jl | PASS | 1.26e-15 | 0.855 | Julia type-7 == numpy default |
| besselj0.c | PASS | 4.44e-16 | 0.40 | |
| besselj0.cpp | PASS | 3.33e-16 | 0.355 | |
| besselj0.java | **FAIL** | 3.33e-16 (finite half) | - | Commons Math `BesselJ` rejects the 100 negative-argument grid points (throws, adapter records NaN): fails the all-points-finite rule; on the nonnegative half it agrees to 3.3e-16. Excluded and disclosed; no map change permitted post-run |
| digamma.{c,cpp,java}, gamma.{c,cpp,java}, gammainc.{c,cpp,java}, expint.{c,cpp}, legendre.{c,cpp}, zeta.{c,cpp}, sinc.jl | NOT_REACHED | - | - | greedy walk stopped at target after `besselj0` (Step 5) |

**Excluded-pair disposition (§2c)**: trapezoid.rs, invsqrt.go, simpson.cpp,
simpson.rs, besselj0.java are EXCLUDED before any mutant generation, with
the measurements above disclosed. They are not fixed, re-mapped, or
re-certified; there is no post-generation exclusion path.

## 6. Declared §2c exception classes (declared pre-run, in the registry)

| Program | Class | Declared tol | Band derivation |
|---|---|---|---|
| brent | 1 (solver-tolerance-bounded) | 1e-6 (no relaxation needed) | both sides converge to \|droot\| <= ~1e-12 (GSL epsabs 1e-12; CM BrentSolver(1e-12); scipy xtol 1e-12); combined band ~4e-12 |
| newton | 1 | **2e-6** (<= 1e-5 ceiling) | Python stops at \|f\|<1e-6 with min \|f'\| = 2*root >= 1 on the frozen domain (band <= 1e-6); Rust converges to machine precision; combined 2e-6. Measured 7.84e-7 |
| quad | 1 | 1e-6 (no relaxation needed) | both sides integrate at epsabs=epsrel=1e-10; combined band ~4e-10 |

No class-2 (RNG-stream) pair was admitted: the only stochastic candidate
(mcpi) failed the seedability screen (§3).

## 7. Registered-protocol ambiguities and deviations (reported, not improvised)

- **D1 (cross-source programs).** §2b Step 4's tiebreak "source-list index"
  assumes each candidate maps to one source, but programs like `erf` exist in
  GSL (src 2), Boost (src 5), and Commons Math (src 4). Resolution: one
  candidate PROGRAM per semantics; l counts all its same-semantics non-Python
  implementations; the tiebreak index is the smallest source index among
  them. This affects ordering only within equal (c, l) groups and is applied
  uniformly.
- **D2 (source 3, Julia).** The execution environment ships no Julia
  toolchain and no package-manager network access. The official Julia 1.11.7
  binary tarball was provisioned (toolchain = apparatus, not program code);
  the SciML half of source 3 remained non-enumerable (Pkg installation
  infeasible) and is disclosed as a sweep shortfall per Step 5. Julia stdlib
  supplied `quantile` (certified) and `sinc` (not reached).
- **D3 (TheAlgorithms/C, GPL-3.0).** Every C-repo candidate failed the
  pre-behavioral screen (§3), so no GPL source is vendored. C-language
  coverage comes from GNU GSL (source 2), used as the unmodified Ubuntu
  system library with its license notice retained
  (`third_party/gsl/COPYRIGHT.debian`), per Step 3 criterion 1.
- **D4 (demo main() in external TUs).** TheAlgorithms C++ files ship
  demonstration `main()`s. The shim textually includes the unmodified file
  under `#define main xl_ext_main`. This is adapter-level build
  configuration; zero external bytes are edited (P1).
- **D5 (all-points-finite reading).** §2c requires "both sides finite"; this
  was applied at ALL 201 grid points, which excludes besselj0.java even
  though its finite half agrees to 3.3e-16. The frozen map t = 8x-4 (chosen
  pre-behaviorally to expose the parity identity) is not re-mapped post-run;
  the one-shot rule forbids it.
- **D6 (walk-order certification).** Step 5 certifies pairs program-by-
  program in rank order and stops at the target; candidates ranked below
  `besselj0` were never certified (NOT_REACHED), which is the registered
  behavior, not an exclusion.

## 8. Roster (certified pairs, frozen; = `configs/xl_roster.json`)

Cells: each pair x 5 strata; aligned = the pair's primary cell (registered
category -> stratum map, first-matching-row); cross = its other adjudicated
cells; non-instantiable strata are registered-vacant (standard `_is_excluded`).

| Pair | Lang | Program | Primary | Instantiable strata | Upstream (commit / version) | Files (unmodified) | License |
|---|---|---|---|---|---|---|---|
| invsqrt.cpp | C++ | invsqrt | MP5 `f_conv.rate` | 1,2,4,5 | TheAlgorithms/C-Plus-Plus `b9c118fb` | `third_party/thealgorithms-cpp/math/inv_sqrt.cpp` | MIT |
| brent.c | C | brent | MP3 `f_conv.lim` | 1,2,3,4 | GSL 2.7.1 (system lib) | GSL `gsl_root_fsolver_brent` | GPL-3.0 |
| brent.java | Java | brent | MP3 `f_conv.lim` | 1,2,3,4 | commons-math3 3.6.1 | `BrentSolver` (jar) | Apache-2.0 |
| euler.java | Java | euler | MP3 `f_conv.lim` | 2,3,4,5 | TheAlgorithms/Java `fd2858e7` | `.../maths/EulerMethod.java` | MIT |
| newton.rs | Rust | newton | MP3 `f_conv.lim` | 1,2,3,4 | TheAlgorithms/Rust `c65d0146` | `.../src/math/newton_raphson.rs` | MIT |
| rungekutta.cpp | C++ | rungekutta | MP3 `f_conv.lim` | 2,3,4,5 | TheAlgorithms/C-Plus-Plus `b9c118fb` | `.../numerical_methods/rungekutta.cpp` | MIT |
| betainc.c | C | betainc | MP1 `f_inv.con` | 1,2,4 | GSL 2.7.1 | `gsl_sf_beta_inc` | GPL-3.0 |
| betainc.cpp | C++ | betainc | MP1 `f_inv.con` | 1,2,4 | Boost.Math `8ee12a53` | `boost::math::ibeta` (headers) | BSL-1.0 |
| betainc.java | Java | betainc | MP1 `f_inv.con` | 1,2,4 | commons-math3 3.6.1 | `Beta.regularizedBeta` | Apache-2.0 |
| erf.c | C | erf | MP1 `f_inv.con` | 1,2,4 | GSL 2.7.1 | `gsl_sf_erf` | GPL-3.0 |
| erf.cpp | C++ | erf | MP1 `f_inv.con` | 1,2,4 | Boost.Math `8ee12a53` | `boost::math::erf` | BSL-1.0 |
| erf.java | Java | erf | MP1 `f_inv.con` | 1,2,4 | commons-math3 3.6.1 | `Erf.erf` | Apache-2.0 |
| normcdf.c | C | normcdf | MP1 `f_inv.con` | 1,2,4 | GSL 2.7.1 | `gsl_cdf_ugaussian_P` | GPL-3.0 |
| normcdf.cpp | C++ | normcdf | MP1 `f_inv.con` | 1,2,4 | Boost.Math `8ee12a53` | `normal_distribution` cdf | BSL-1.0 |
| normcdf.java | Java | normcdf | MP1 `f_inv.con` | 1,2,4 | commons-math3 3.6.1 | `NormalDistribution.cumulativeProbability` | Apache-2.0 |
| sigmoid.rs | Rust | sigmoid | MP1 `f_inv.con` | 1,2,4 | TheAlgorithms/Rust `c65d0146` | `.../src/math/sigmoid.rs` | MIT |
| tanh.rs | Rust | tanh | MP1 `f_inv.con` | 1,2,4 | TheAlgorithms/Rust `c65d0146` | `.../src/math/tanh.rs` | MIT |
| quad.c | C | quad | MP3 `f_conv.lim` | 2,3,4 | GSL 2.7.1 | `gsl_integration_qag` (GAUSS21) | GPL-3.0 |
| quantile.jl | Julia | quantile | MP2 `f_mono.stat` | 1,2,4 | Julia 1.11.7 stdlib | `Statistics.quantile` | MIT |
| besselj0.c | C | besselj0 | MP1 `f_inv.con` | 1,4 | GSL 2.7.1 | `gsl_sf_bessel_J0` | GPL-3.0 |
| besselj0.cpp | C++ | besselj0 | MP1 `f_inv.con` | 1,4 | Boost.Math `8ee12a53` | `boost::math::cyl_bessel_j` | BSL-1.0 |

Python-side references per pair: external TheAlgorithms/Python
implementations for source-1 programs (`third_party/thealgorithms-python/`);
the registered scipy/numpy references for sources 2/3/4/5 (scipy 1.17.1 /
numpy 2.4.6). Frozen aux parameters and domain maps per pair: `registry.py`
(`aux` field) and the shim sources.

**Family coverage (grid-level hard constraint)**: certified programs
instantiating each family: MP1: 10, MP2: 12, MP3: 5, MP4: 13, MP5: 3. All
five families >= 2 programs; constraint satisfied without the Step-6
fallback.

**Primary-cell distribution**: MP1 13 pairs, MP2 1, MP3 6, MP5 1, MP4 0
aligned pairs (MP4 is heavily covered as a cross stratum; the aligned/cross
estimand of §3.1 does not require primary balance).

**Languages certified**: C (6 pairs), C++ (6), Java (6), Rust (3),
Julia (1). Go: 0 certified (invsqrt.go failed, disclosed).

## 9. Gates and read-off power (§3.1, §4a)

- Achieved certified n = 21 >= floor 12; UNDER_CERTIFIED gate (n < 8) not
  triggered.
- Read-off achieved power: largest tabulated n <= 21 on the frozen primary
  (deflated) curve is n = 20 -> **0.8484**. Sensitivity (Python-scale) curve
  at n = 20: 0.9515.
- §2e XL pilot determination (deterministic, for the next wave): the first
  two certified pairs in frozen roster (walk) order belonging to two
  different programs AND two different languages are **invsqrt.cpp** (C++)
  and **brent.c** (C); pool tag `v8xl_pilot`.

*(End of Amendment A1. Any later change is a new dated entry in
PREREGISTRATION_STUDY5_v1.md §10, never an edit to this record.)*

---

# Amendment A3: Family-XL roster EXTENSION wave (scale diversity)

**Date**: 2026-07-10. **Status**: author-directed, pre-mutant, append-only;
Amendment A1 above is byte-unchanged. **Pre-mutant attestation**: at this
freeze NO Family-XL **confirmatory** mutant, SMS value, or `v8xl` pool
exists; the only Family-XL behavioral artifacts are (i) the A1 §2c
certification measurements, (ii) the firewalled `v8xl_pilot` calibration
pilot (registered §2e; in flight on the A1-determined pairs `invsqrt.cpp` +
`brent.c`, both A1 walk-order picks that PRECEDE every A3 pair — the pilot
determination is unchanged by this wave and no A3 pair carries any mutant),
and (iii) the A3 certification measurements recorded below. Machine-readable
roster: `configs/xl_roster.json` (A1 pair objects deep-equal-asserted at
write time); certification SSOT: `data/results/study5_xl_certification.json`
(A1 `summary`/`pairs` blocks asserted unchanged; A3 results in the new `a3`
block); candidate registry: `src/p2/xlport/registry.py` (`A3_*` sections,
appended).

**Author directive (recorded).** The A1 roster review found: sources diverse
(GSL 6 / Boost 4 / CommonsMath 4 / TheAlgorithms 6 / Julia 1) but SCALE
homogeneous (21/21 function-level routines) and primary-stratum coverage
skewed (MP1 13, MP3 6, MP2 1, MP5 1). Directive: add module/pipeline-scale
production-library pairs; P1 (no self-written PUT code) and P2 (purpose +
family first, then diversity) still govern; priorities (a) module scale,
(b) MP2/MP5 primary-coverage repair; registered cap n <= 28 respected.

**Headline**: 7 new module-scale pairs certified, **0 failures**, achieved
total n = **28 = cap**. Primary-stratum repair: MP2 1 -> 3, MP5 1 -> 6.
Scale stratum (disclosed stratification variable, all 28 pairs):
function-level 21 (A1), module-level 7 (A3). Read-off power at the frozen
§4a primary-DGP curve: tabulated n = 28 -> **0.9481**.

## A3.1 Registered wave rules (fixed BEFORE the certification run)

- **A3-1 (module-scale admission criterion, pre-behavioral)**: the pair's
  call path must traverse a multi-component library SUBSYSTEM (state object
  + staged alloc/init/accumulate/solve/eval pipeline, or an adaptive driver
  chain) — a documented library module with a multi-hundred-LOC call path,
  not a single closed-form routine. Single-pass closed-form entry points
  (the structural class of every A1 pair) are out of scope for this wave.
- **A3 walk order (P2, family-repair first; deterministic)**: group (i) =
  candidates whose registered primary stratum is MP2 (`f_mono.stat`) or MP5
  (`f_conv.rate`) in the registered Step-4 total order; then group (ii) =
  all remaining candidates in Step-4 order. The Step-4 key is unchanged
  inside each group. (A pure ungrouped Step-4 walk would spend the whole
  budget on MP3-primary ODE modules and repair nothing — see the ranking
  table; the grouping layer is the A3 instantiation of §2b Step 1
  "required family coverage first" + P2, and is disclosed as A3-D1.)
- **Budget**: N_CAP 28 − A1 achieved 21 = **7 new pairs**; walk stops at
  the cap; candidates beyond it are NOT_REACHED (registered behavior, not
  exclusions). Directive target 5-7 pairs.
- **Certification gate**: §2c UNCHANGED and byte-identical (the A3 driver
  imports `certify_pair` from the frozen A1 driver): 201-point grid,
  `|y_L - y_py| <= tol * max(|y_py|, 1)`, both sides finite, tol 1e-6
  unless a pre-declared class-1 exception (ceiling 1e-5); one-shot;
  failures disclosed, never fixed.
- **`l` convention (documented)**: for this wave `l` counts non-Python
  languages with a same-semantics MODULE-SCALE external implementation
  (A3-1 applies to the enumeration itself); function-scale implementations
  of the same semantics (e.g. `gsl_stats_sd` for descstats) exist but are
  not A3-enumerable and do not count.

## A3.2 Enumeration (registered source list only; pinned upstreams REUSED)

Sweep: (a) the GSL 2.7.1 module index (odeiv2, interpolation, chebyshev,
histogram, multimin, multiroots, multifit, fft; screened: bspline, monte,
siman, wavelet, linalg/eigen, 1-D min); (b) the Commons Math 3.6.1 package
tree (stat.descriptive, analysis.interpolation, fitting, ode.nonstiff,
transform; screened: SimpleRegression, EmpiricalDistribution, Percentile);
(c) the vendored Boost.Math header tree (quadrature, interpolators;
screened: cardinal b-splines, univariate statistics); (d) TheAlgorithms
repos re-swept for multi-component pipelines (none exist — single-file
teaching implementations; structural finding); (e) Julia stdlib re-swept
(no module-scale numeric pipeline; SciML still non-enumerable per A1 D2).
**No new vendoring was needed**: every A3 pair links the A1-pinned
upstreams (system GSL 2.7.1 per the A1 GPL precedent — nothing GPL
vendored; Boost.Math `8ee12a53` vendored headers; commons-math3 3.6.1 jar
sha256 `1e56d7b0...7ef2b308`); `third_party/` is byte-unchanged.

## A3.3 Step-3 + A3-1 screening audit (rejected candidates, criterion cited)

| Candidate | Rejection (criterion) |
|---|---|
| CM `Percentile` (R_7) as `quantile.java` for the A1 program `quantile` | documented domain p ∈ (0,100] rejects the frozen program point p = x = 0; screened pre-behaviorally instead of burning a one-shot certification (besselj0.java lesson) (S3 crit. 3) |
| GSL odeiv2 explicit-Euler drive as `euler.c` for the A1 program `euler` | GSL odeiv2 ships NO explicit-Euler stepper (rk1imp is IMPLICIT Euler, different semantics); no same-semantics module-scale implementation exists; found at shim-authoring, pre-behavioral (S3 crit. 4) |
| GSL `gsl_min` 1-D Brent minimiser | single iterate-loop state machine, the structural class of A1 `brent.c` (A3-1) |
| GSL `gsl_stats_*` / Julia `Statistics.std` / Boost univariate statistics | single-pass closed-form routines (A3-1); hence descstats `l`=1 |
| CM `SimpleRegression` | streaming accumulator + closed-form readout; no staged pipeline (A3-1) |
| CM `EmpiricalDistribution` | `cumulativeProbability` has no documented numpy/scipy same-semantics counterpart; the mean readout bypasses the binning module (S3 crit. 4 + A3-1) |
| GSL bspline / Boost cardinal b-splines vs scipy | knot/boundary semantics not documented-identical (the A1 cubic-spline lesson at module scale) (S3 crit. 4) |
| GSL monte (plain/miser/vegas) | RNG-stream-dependent; §2c class-2 reproduction precondition structurally unsatisfiable vs numpy (S3 crit. 2) |
| GSL siman | RNG-stream-dependent (S3 crit. 2) |
| GSL wavelet | no counterpart in the registered scipy/numpy reference set (S3 crit. 4) |
| GSL linalg / eigen | matrix-in/matrix-out; no registered scalar-program convention (S3 crit. 3) |
| TheAlgorithms (all six repos, module-scale sweep) | no multi-component numeric pipeline exists (single-file teaching implementations; structural finding) (A3-1) |
| Julia stdlib module numerics / SciML OrdinaryDiffEq | stdlib has no module-scale pipeline with a documented scipy contract; SciML non-enumerable (A1 D2 carried) (A3-1 + Step-5 disclosure) |

## A3.4 Deterministic ranking (admissible candidates, grouped walk order)

Key inside each group: (c desc, l desc, src asc, name asc). Group (i) =
primary ∈ {MP2, MP5} (repair), group (ii) = rest.

| Walk | Grp | Program | c | l | Src | Primary | Pairs |
|---|---|---|---|---|---|---|---|
| 1 | i | interp | 4 | 2 | 2 | MP5 | interp.c, interp.java |
| 2 | i | chebyshev | 4 | 1 | 2 | MP5 | chebyshev.c |
| 3 | i | hermite | 4 | 1 | 5 | MP5 | hermite.cpp |
| 4 | i | histstats | 3 | 1 | 2 | MP2 | histstats.c |
| 5 | i | descstats | 3 | 1 | 4 | MP2 | descstats.java |
| 6 | i | polyfit | 2 | 2 | 2 | MP5 | polyfit.c, polyfit.java |
| 7 | ii | odedrive | 4 | 2 | 2 | MP3 | odedrive.c, odedrive.java |
| 8 | ii | rungekutta | 4 | 1 | 1 | MP3 | rungekutta.java |
| 9 | ii | multimin | 3 | 1 | 2 | MP3 | multimin.c |
| 10 | ii | multiroot | 3 | 1 | 2 | MP3 | multiroot.c |
| 11 | ii | quad | 3 | 1 | 2 | MP3 | quad.cpp |
| 12 | ii | fft | 2 | 2 | 2 | MP4 | fft.c, fft.java |

## A3.5 §2c certification results (201-point grid, one-shot)

| Pair | Status | max rel dev | argmax x | Note |
|---|---|---|---|---|
| interp.c | **PASS** | 0.0 | - | GSL interpolation module (gsl_spline/gsl_interp_linear/accel) — bit-identical piecewise-linear values |
| interp.java | **PASS** | 0.0 | - | CM LinearInterpolator -> PolynomialSplineFunction — bit-identical |
| chebyshev.c | **PASS** | 2.11e-15 | 0.14 | GSL gsl_cheb order-12 vs numpy chebinterpolate deg-12: same first-kind-node interpolant, rounding-level |
| hermite.cpp | **PASS** | 4.07e-16 | 0.78 | Boost cubic_hermite vs scipy CubicHermiteSpline: exactly-defined piecewise cubic |
| histstats.c | **PASS** | 0.0 | - | GSL histogram pipeline vs numpy.histogram midpoint mean: identical binning + identical binned-mean formula |
| descstats.java | **PASS** | 1.11e-16 | 0.825 | CM DescriptiveStatistics SD vs numpy std ddof=1 |
| polyfit.c | **PASS** | 1.12e-15 | 0.05 | GSL multifit balanced-SVD LS vs numpy.polyfit: unique full-rank LS solution, conditioning-level rounding |
| polyfit.java, odedrive.c, odedrive.java, rungekutta.java, multimin.c, multiroot.c, quad.cpp, fft.c, fft.java | NOT_REACHED | - | - | cap 28 reached (registered walk stop, not exclusions) |

**Failures disclosed**: none this wave (0 FAIL). Declared class-1 exception
bands (odedrive, multimin, multiroot, quad — registry `A3_CANDIDATES`) were
never consumed: all walked pairs certified at the standard 1e-6 tolerance,
and every declared-exception candidate lies beyond the cap.

## A3.6 Declared §2c exception classes (declared pre-run, in the registry)

| Program | Class | Declared tol | Band derivation | Consumed? |
|---|---|---|---|---|
| odedrive | 1 | 1e-6 (no relaxation) | both drivers hold local error <= rel 1e-10 / abs 1e-12; O(30-60) accepted steps -> cross-method band ~2e-8 | no (NOT_REACHED) |
| multimin | 1 | 1e-6 (no relaxation) | simplex size 1e-12 / fatol 1e-13 on a smooth strictly convex objective -> objective band ~1e-12 | no (NOT_REACHED) |
| multiroot | 1 | 1e-6 (no relaxation) | residual 1e-12, O(1) Jacobian singular values -> root band ~1e-11 | no (NOT_REACHED) |
| quad (A3 ext.) | 1 | 1e-6 (no relaxation) | both sides adaptive to 1e-10; band ~4e-10 (A1 quad precedent) | no (NOT_REACHED) |

No class-2 (RNG-stream) candidate was admitted (monte/siman screened).

## A3.7 Ambiguities and deviations (reported, not improvised)

- **A3-D1 (grouped walk).** The repair-first grouping layer is NEW relative
  to the A1 walk (which was pure Step-4). It implements the author
  directive (P2: purpose + family first) deterministically and was fixed
  before any A3 behavioral run; the A1 roster is unaffected. Without it the
  budget would have been consumed by MP3-primary ODE modules (ranking
  table), repairing nothing.
- **A3-D2 (adaptive-ODE re-pose).** A1 screened "adaptive ODE (GSL rkf45 vs
  scipy RK45)" citing an undocumentable band at DEFAULT tolerances. A3
  re-enumerated it as `odedrive` at frozen tight tolerances (rel 1e-10 /
  abs 1e-12) under which the class-1 band IS documentable. Disclosed as a
  deliberate amendment decision, not a silent reversal; the pair ranked in
  group (ii) and was NOT_REACHED at the cap anyway.
- **A3-D3 (f_conv.rate for fixed-budget integrators).** The author's
  suggestion of accuracy-order method pairs (Euler vs RK4 at fixed budget)
  as MP5 primaries is unavailable under the FROZEN first-matching-row
  category map: fixed-step ODE drives match row 3 (euler.java precedent)
  and are not re-mapped. MP5 repair therefore comes from surrogate-
  structured modules (interp, chebyshev, hermite, polyfit — the invsqrt.cpp
  category precedent).
- **A3-D4 (euler.c screen at shim-authoring).** The planned GSL odeiv2
  explicit-Euler extension of A1 program `euler` was screened when shim
  authoring surfaced that GSL ships no explicit-Euler stepper (API fact,
  pre-behavioral, before the gate run); recorded in A3_SCREENED.
- **A3-D5 (scale stratum recording).** `scale_stratum` is recorded as a NEW
  top-level roster map covering all 28 pairs (A1 = function, A3 = module)
  so that A1 pair objects stay byte-identical; A3 pair objects additionally
  carry `scale`/`amendment` fields. `load_xl_roster` round-trip verified
  (grid n = 28, underscore-free ids, primary map intact).
- **A3-D6 (concurrent pilot).** The §2e pilots (`v8xl_pilot`, `v8mr_pilot`)
  are in flight during this wave in a parallel session; this wave read none
  of their outputs and touched none of their artifacts. Pilot pools contain
  no A3 pair; the deterministic pilot-pair determination (A1 §9) precedes
  every A3 pair and is unchanged.

## A3.8 Roster after A3 (28 pairs, frozen; = `configs/xl_roster.json`)

New pairs (all module-scale; upstreams = A1 pins, unmodified):

| Pair | Lang | Program | Primary | Instantiable | Upstream | Module call path |
|---|---|---|---|---|---|---|
| interp.c | C | interp | MP5 `f_conv.rate` | 2,3,4,5 | GSL 2.7.1 (system lib) | gsl_spline + gsl_interp_linear + accel |
| interp.java | Java | interp | MP5 `f_conv.rate` | 2,3,4,5 | commons-math3 3.6.1 | LinearInterpolator -> PolynomialSplineFunction chain |
| chebyshev.c | C | chebyshev | MP5 `f_conv.rate` | 2,3,4,5 | GSL 2.7.1 | gsl_cheb_series init-at-nodes + Clenshaw eval |
| hermite.cpp | C++ | hermite | MP5 `f_conv.rate` | 2,3,4,5 | Boost.Math `8ee12a53` | interpolators::cubic_hermite + detail pipeline |
| histstats.c | C | histstats | MP2 `f_mono.stat` | 2,3,4 | GSL 2.7.1 | histogram alloc/ranges/512x increment/binned mean |
| descstats.java | Java | descstats | MP2 `f_mono.stat` | 1,2,4 | commons-math3 3.6.1 | DescriptiveStatistics -> Variance -> Mean moment chain |
| polyfit.c | C | polyfit | MP5 `f_conv.rate` | 4,5 | GSL 2.7.1 | multifit workspace + balanced-SVD LS pipeline |

**Primary-cell distribution (all 28)**: MP1 13, MP2 **3**, MP3 6, MP4 0,
MP5 **6** (was MP1 13 / MP2 1 / MP3 6 / MP5 1 at A1; the aligned/cross
estimand of §3.1 does not require primary balance — the skew repair is a
robustness upgrade, disclosed as such).

**Scale stratum (disclosed stratification variable)**: function-level 21
(all A1), module-level 7 (all A3). Recorded per pair in
`configs/xl_roster.json::scale_stratum` and available for the registered
exploratory (Family X) per-stratum breakdowns; it licenses NO confirmatory
verdict.

**Family instantiability coverage (certified programs)**: MP1 11, MP2 17,
MP3 9, MP4 19, MP5 7 — grid-level hard constraint (>= 2 per family) remains
satisfied.

**Languages certified (all 28)**: C 10, C++ 7, Java 8, Rust 3, Julia 1
(A3 adds C +4, C++ +1, Java +2; source spread of the new pairs GSL 4 /
CM 2 / Boost 1 — P2 puts purpose before source diversity, disclosed).

## A3.9 Gates and read-off power (§3.1, §4a)

- Achieved total certified n = **28** = registered cap (floor 12, target
  20, cap 28); UNDER_CERTIFIED gate (n < 8) far from triggered.
- Read-off achieved power on the frozen §4a primary (deflated) curve:
  largest tabulated n <= 28 is n = 28 -> **0.9481** (sensitivity
  Python-scale curve: 0.9969). No post-data simulation.
- One-shot discipline: this wave ran the gate exactly once per walked pair;
  the 9 NOT_REACHED pairs were never certified and remain available only to
  a future registered amendment (they cannot enter without one).

*(End of Amendment A3. Any later change is a new dated entry in
PREREGISTRATION_STUDY5_v1.md §10, never an edit to this record.)*
