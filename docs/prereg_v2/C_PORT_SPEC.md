# C_PORT_SPEC.md — Study-4 C-language PUT port (H-LANG language-invariance grid)

Status: authored BLIND to mutation outcomes (SMS / verdict files under
`data/results/*` were not read during authoring). Port derived solely from
the Python PUT/MR sources and their docstrings.

Registration reference: PREREGISTRATION_STUDY* H-LANG hypothesis
("aligned > cross replicates on C"). This spec is the numerical + tooling
contract the H-LANG C grid is registered against.

---

## 0. Purpose and threat addressed

Study-1/2/3 kernels are all Python. Reviewer external-validity threat:
"the SMS aligned>cross effect could be an artefact of single-language
(Python) PUTs." This port re-implements the ORIGINAL Study-1 12-PUT grid
(`src/p2/puts/a1.py .. d3.py`) in C99 so the registered aligned-vs-cross
comparison can be re-run on a second, independently compiled language
through the SAME metamorphic-relation machinery (`src/p2/mrs/*.py`,
AVP, equivalence judge, `run_one_cell`, `sms_campaign`).

The MR machinery is reused UNMODIFIED. A compiled C PUT/mutant is wrapped
by `p2.cport.CPutProgram`, a `Callable[[float], float]` that is
indistinguishable from a Python PUT's `program` to every downstream caller.

---

## 1. Numerical contract (global)

| Aspect | Contract |
|---|---|
| Input domain | `x in [0,1]` scalar, identical to Python |
| Output | single `double`, printed `%.17g`, parsed back to Python float |
| Libraries | pure C99 + libm ONLY; no third-party C libraries |
| Compiler | `gcc -std=c99 -O0 -Wall` (zero warnings required), link `-lm` |
| Protocol | persistent line REPL: one `x` per stdin line -> one float per stdout line (also one-shot `argv[1]` mode) |
| Sandbox | content-addressed build dir (`tempfile`/scratchpad); per-call timeout; hung child -> `nan`, crashed child auto-restart |

### RNG contract (stochastic kernels b2, b3, c2)

The Python references draw from numpy PCG64 (`default_rng(42)`). numpy's
exact bit-stream is NOT reproducible in C99. Each stochastic C kernel
therefore embeds a deterministic 64-bit LCG (constants
`6364136223846793005 / 1442695040888963407`, top-53-bit doubles) seeded
with the fixed constant `42`, and Box-Muller for normals.

The contract is **distributional equivalence, not bit-equality**: the C
kernel realises the SAME estimator/target as the Python kernel and lands
within the same sampling-error band of the analytic target. Because the
seed is fixed and shared by the C original AND every C mutant, intra-C
comparisons (original vs mutant, the only comparison SMS actually scores)
remain fully deterministic.

---

## 2. Per-PUT port table (ORIGINAL Study-1 grid, 12 PUTs)

Ported: 7/12. Excluded: 5/12 (ML-library kernels; disclosed below).

| PUT | Kernel | Python lib replaced by | Class | Ported? | Agreement contract | Achieved (x in {0,.25,.5,.75,1}) |
|---|---|---|---|---|---|---|
| a1 | Lorenz ODE, L2 norm at t=1 | scipy `solve_ivp` RK45 -> fine fixed-step RK4 (N=1e5) | deterministic (chaotic) | YES | rel <= solver tol (chaos-bounded) | max_abs 2.0e-6, max_rel 5.6e-8 |
| a2 | 2x2 LU det (prod of U diag) | scipy `linalg.lu` -> hand LU w/ partial pivot | deterministic | YES | 1e-9 rel | 0 (bit-identical) |
| a3 | 1D explicit-Euler heat FDM | numpy loops -> C arrays | deterministic | YES | 1e-9 rel | 0 (bit-identical) |
| b1 | Beta-Binomial posterior mean | numpy arithmetic -> C arithmetic | deterministic | YES | 1e-9 rel | 0 (bit-identical) |
| b2 | Metropolis-Hastings chain mean | numpy PCG64 -> embedded LCG + Box-Muller | stochastic | YES | distributional: `\|mean - mu\|` within MCMC error | max\|C-mu\|=0.154 vs max\|Py-mu\|=0.191 |
| b3 | Monte Carlo integral of x+t^2 | numpy PCG64 -> embedded LCG | stochastic | YES | distributional: `\|y - (x+1/3)\|` within MC error 0.013 | max\|C-tgt\|=0.0020 vs max\|Py-tgt\|=0.0045 |
| c2 | PCE degree-5 surrogate of tanh | sklearn PolynomialFeatures+LinearRegression -> normal-equations LS | deterministic given design | YES | design-distributional (~1e-2 abs) | max_abs 7.3e-3 vs Python |
| c1 | GPR surrogate of erf | sklearn `GaussianProcessRegressor` | ML surrogate | NO (excluded) | — | — |
| c3 | MLP surrogate of sigmoid | sklearn `MLPRegressor` (Adam) | ML surrogate | NO (excluded) | — | — |
| d1 | MLP classifier | sklearn `MLPClassifier` (Adam) | ML classifier | NO (excluded) | — | — |
| d2 | SVM classifier (RBF) | sklearn `SVC` (libsvm SMO + Platt) | ML classifier | NO (excluded) | — | — |
| d3 | Logistic-regression classifier | sklearn `LogisticRegression` (lbfgs) | ML classifier | NO (excluded) | — | — |

Achieved figures are the actual measured C-vs-Python agreement at
authoring time (`gcc 13.3.0`, glibc libm). a2/a3/b1 reproduce the Python
`float` bit-for-bit; a1 is bounded by the reference RK45 tolerance
(`rtol=1e-8`) because Lorenz is chaotic (both integrators approximate the
same true trajectory, whose finite-precision divergence at t=1 is O(1e-6));
b2/b3 track the analytic target at least as tightly as the Python
reference; c2's residual is the design-sampling difference of two
degree-5 least-squares fits of the same target.

---

## 3. Exclusions (honest, disclosed)

The 5 excluded PUTs (c1, c3, d1, d2, d3) all depend on a trained ML model
whose parameters are the fixed point of a library-specific optimiser
(L-BFGS marginal likelihood, Adam, libsvm SMO, lbfgs logistic) fitted on
a training design generated by numpy PCG64. Two obstructions make a
faithful pure-C99 port infeasible:

1. **Optimiser non-portability.** Reproducing sklearn's exact fitted
   weights would require re-implementing its optimiser to bit-tolerance in
   C — a research project, not a port, and the result would still differ.
2. **Training-design non-reproducibility.** The design points come from
   numpy PCG64, which cannot be bit-reproduced in C99. For a SINGLE trained
   model's point prediction there is no meaningful distributional target
   (unlike an MC mean), so neither the 1e-9 deterministic contract nor a
   distributional contract can be honoured.

d3 (logistic regression) is the closest to portable (IRLS is elementary),
but obstruction (2) still denies it a defensible agreement contract, so it
is excluded rather than faked. A partial 7-PUT grid with disclosed
exclusions is preferred over a fabricated 12-PUT grid. The a- and b-class
numeric/stochastic kernels port cleanly; c2 ports because PCE is ordinary
least squares, not an ML optimiser.

The excluded PUTs remain in the Python grid; H-LANG is registered on the
7-PUT C intersection (a1, a2, a3, b1, b2, b3, c2) and reports the reduced
grid explicitly.

---

## 4. Files

- C kernels: `src/p2/cput/{a1,a2,a3,b1,b2,b3,c2}.c` (self-contained; each
  defines `double program(double x)` + the REPL `main`).
- Adapter: `src/p2/cport/adapter.py` (`compile_c_source`, `CPutProgram`,
  `load_c_put`), `src/p2/cport/validation.py` (`validate_c_mutant`, V1-V3).
- Campaign wiring: `scripts/cross_source_campaign.py --lang c` (packet
  export/ingest for C), admission cache `data/operator_campaign/cache_clang/`;
  `scripts/sms_campaign.py --lang c` (pool tag `v7c`).
- Tests: `tests/cport/`.

## 5. Admission gate mapping (Python V1-V4 -> C)

| Python | C equivalent |
|---|---|
| V1 syntax (`ast.parse`) | source compiles `gcc -O0 -Wall` |
| V4 signature (`def program`) | folded into V1: must define `double program(double)` to link against harness `main` |
| V2 executable+finite on probe set | `CPutProgram(x)` finite for x in {0.1,0.3,0.5,0.7,0.9} |
| V3 non-trivial (>1e-6 vs original) | same epsilon, via adapter |

Same probe set, same 1e-6 epsilon, so a C admission is byte-comparable in
meaning to a Python admission.

## 6. Performance caveat (a3)

a3's cost is O(1/h^3) (n_steps ~ 1/h^2 explicit-Euler steps over ~1/h
interior nodes). At the domain edge x -> 0 the input clamps to h=1e-4
(N=10000), which is ~40 s at `gcc -O0`. This is a property of the kernel,
not a port defect (the result is bit-identical to Python: 0.9999999994307).
The adapter's per-call `timeout` (default 10 s) will therefore mark a
pathologically small a3 input as `nan` (non-finite). The equivalence
sampler (`UniformSampler(seed=42)`) draws x in (0,1); its minimum over
1000 draws is ~1e-3 (N~1000, ~0.04 s), so normal scoring is unaffected.
Agreement for a3 is verified at x=1e-3 (large-N, fast) rather than x=0.

