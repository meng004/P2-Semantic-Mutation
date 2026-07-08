# PUT Expansion Roster — Study 2 (12 → 30 PUTs)

**Status:** design doc (authored BEFORE any mutation campaign).
**Integrity constraint:** every kernel and MR below was designed from domain
knowledge only. No `data/results/*` mutation-outcome file was read while
authoring. The existing 12 PUTs/MRs are **not modified**. Primary-MP
assignments follow the a-priori deterministic class rule (below); final
primary designation is owned by the E1 pre-registration agent.

---

## 1. Balanced split

Existing infrastructure has 3 PUTs per class (12 total). To reach **n = 30**
with 4–5 PUTs added per class, the balanced split is:

| Class | Existing | New | New IDs | Class total |
|-------|----------|-----|---------|-------------|
| A Numeric        | a1–a3 | **+5** | a4, a5, a6, a7, a8 | 8 |
| B Probabilistic  | b1–b3 | **+4** | b4, b5, b6, b7     | 7 |
| C Surrogate      | c1–c3 | **+4** | c4, c5, c6, c7     | 7 |
| D ML             | d1–d3 | **+5** | d4, d5, d6, d7, d8 | 8 |
| **Total**        | 12    | **18** | —                  | **30** |

Class totals land at 7–8 (each new cohort 4–5), matching the pre-registered
"4–5 per class" target. A takes 5 because the numeric class admits the widest
spread of genuinely distinct algorithmic domains (quadrature, interpolation,
root-finding, linear algebra, ODE stepping); D takes 5 to broaden classifier
families beyond the existing MLP/SVM/LogReg trio.

## 2. Class definitions (from `source/main.tex` §Problem Formulation, Table PUT roster)

- **A Numeric** — deterministic scientific-computing kernels with a known
  analytic/reference answer (nonlinear ODE, linear algebra, PDE). Existing:
  A1 Lorenz ODE, A2 LU determinant, A3 FDM heat.
- **B Probabilistic** — seeded stochastic estimators whose expectation has a
  closed form (conjugate posterior, MCMC, Monte-Carlo). Existing: B1
  Beta-Binomial, B2 Metropolis-Hastings, B3 Monte-Carlo integration.
- **C Surrogate** — models fit to a *known* monotone target on a symmetric
  domain, queried at one point (kernel/orthogonal-basis/neural surrogates).
  Existing: C1 GPR(erf), C2 PCE(tanh), C3 MLP(sigmoid).
- **D ML** — trained classifiers returning `P(y=1) ∈ [0,1]`, monotone in the
  scalar input via a feature map. Existing: D1 MLP, D2 SVM, D3 LogReg.

All PUTs keep the frozen `program(x: float) -> float` signature, `x ∈ [0,1]`,
deterministic and pure (seeds fixed at module load).

## 3. Deterministic class → primary-MP rule (PRIMARY_CELLS_V3 style)

The existing `src/p2/config/primary.py::PRIMARY_CELLS_V3` maps every PUT to a
primary MP by **class**, not by hand-picked per-PUT judgement:

```
A → MP1 (Conservation)   B → MP2 (Monotonicity)
C → MP5 (Partial-order)  D → MP2 (Monotonicity)
```

The 18 new PUTs inherit this same mechanical rule (a4–a8→MP1, b4–b7→MP2,
c4–c7→MP5, d4–d8→MP2). This is an a-priori rule, **not** tuned to any
mutation outcome. Each new PUT is designed so its class-primary MR is a real,
mathematically valid relation that holds on the sanity samples
`x ∈ {0.2, 0.5, 0.75}`.

---

## 4. Roster — 18 new PUTs

Legend for MP applicability: `●●` strong / `●` moderate / `○` baseline (trivial).
Primary MP is **bold**.

### Class A — Numeric (deterministic)

#### a4 — Gauss–Legendre quadrature
- **Kernel:** 16-node Gauss–Legendre estimate of `I(x)=∫₋₁¹ (x + ½t²) dt = 2x + ⅓`.
- **Domain:** numerical integration (fixed-node Gaussian quadrature).
- **Class membership:** deterministic numeric kernel with exact analytic
  reference; distinct algorithm from B3's stochastic Monte-Carlo integrator.
- **Input domain:** `x ∈ [0,1]` (additive constant in the integrand).
- **MRs:** MP1 **●●** conservation `I(x)+I(1−x)=8/3` (exact); MP2 ● monotone;
  MP3 ● bounded-to-analytic; MP4 ○; MP5 ● bounded.
- **Diversity:** first quadrature-rule kernel (Numerical Recipes ch. 4).

#### a5 — Cubic-spline interpolation
- **Kernel:** natural cubic spline through 17 samples of `f(t)=sin(πt)` on
  `[0,1]`, evaluated at `t=x`.
- **Domain:** piecewise-polynomial interpolation (`scipy.interpolate.CubicSpline`).
- **Class membership:** deterministic interpolation kernel; reference is the
  sampled analytic function.
- **Input domain:** `x ∈ [0,1]` (evaluation point).
- **MRs:** MP1 **●●** reflection symmetry `S(x)=S(1−x)` (target even about ½);
  MP2 ○ (sine not monotone on [0,1]); MP3 ● interp-error bound; MP4 ●
  shape/anti-node structure; MP5 ○.
- **Diversity:** first interpolation kernel (Numerical Recipes ch. 3).

#### a6 — Nonlinear root-finding (Brent)
- **Kernel:** solve `r³ + r = 4x − 2` for `r` via `scipy.optimize.brentq`.
- **Domain:** scalar nonlinear root-finding (bracketing Brent method).
- **Class membership:** deterministic solver with a unique real root
  (strictly increasing LHS).
- **Input domain:** `x ∈ [0,1]` → RHS `∈ [−2,2]`.
- **MRs:** MP1 **●●** odd symmetry `r(x)+r(1−x)=0` (exact); MP2 ●● strictly
  monotone; MP3 ● residual bound; MP4 ○; MP5 ● bounded root.
- **Diversity:** first root-finding kernel (Numerical Recipes ch. 9).

#### a7 — Tridiagonal linear solve (Thomas)
- **Kernel:** solve SPD tridiagonal `T u = (2x−1)·d`, `T=tridiag(−1,2,−1)₆`,
  return `Σu`. Linear in `x`, antisymmetric about ½.
- **Domain:** direct linear-system solution (`scipy.linalg.solve_banded`).
- **Class membership:** deterministic linear-algebra kernel; distinct from A2
  (LU *determinant*) — here we *solve* a system and take a linear functional.
- **Input domain:** `x ∈ [0,1]`.
- **MRs:** MP1 **●●** antisymmetry `Σu(x)+Σu(1−x)=0` (exact, by linearity);
  MP2 ●● monotone; MP3 ○; MP4 ○; MP5 ● bounded.
- **Diversity:** first linear-solve kernel (Numerical Recipes ch. 2).

#### a8 — RK4 ODE stepper
- **Kernel:** fixed-step RK4 for `u'=−u`, `u(0)=2x−1`, integrate to `T=1`,
  return `u(T)`. Linear ODE; `u(T)=(2x−1)·ρ`, `ρ` = RK4 amplification.
- **Domain:** explicit one-step ODE integration (hand-rolled RK4).
- **Class membership:** deterministic ODE integrator; distinct from A1
  (library `solve_ivp` on a chaotic nonlinear system).
- **Input domain:** `x ∈ [0,1]` (initial condition).
- **MRs:** MP1 **●●** antisymmetry `u(T;x)+u(T;1−x)=0`; MP2 ●● monotone;
  MP3 ●● RK4-order accuracy vs `e⁻¹`; MP4 ● trajectory sign; MP5 ● bounded.
- **Diversity:** hand-rolled fixed-step integrator (Numerical Recipes ch. 17).

### Class B — Probabilistic (seeded stochastic)

#### b4 — Bootstrap resampling
- **Kernel:** fixed base sample `D~N(0,1)` (n=200, seed 42); statistic =
  mean over 500 bootstrap resamples of `D + (4x−2)`.
- **Domain:** nonparametric bootstrap (Efron resampling).
- **Class membership:** seeded stochastic estimator; `E[·]=mean(D)+(4x−2)`.
- **Input domain:** `x ∈ [0,1]` (location shift).
- **MRs:** MP1 ○; MP2 **●●** monotone in shift; MP3 ● (more resamples →
  tighter); MP4 ○; MP5 ● bounded.
- **Diversity:** first resampling-based estimator.

#### b5 — Rejection sampling
- **Kernel:** rejection sampler for a truncated Gaussian on `[−3,3]` with mean
  `μ=4x−2`; return accepted-sample mean (seed 42, 6000 proposals).
- **Domain:** acceptance–rejection Monte-Carlo.
- **Class membership:** seeded stochastic estimator; `E[·]≈μ(x)`.
- **Input domain:** `x ∈ [0,1]` (target mean).
- **MRs:** MP1 ○; MP2 **●●** monotone; MP3 ●; MP4 ○; MP5 ● bounded to `[−3,3]`.
- **Diversity:** first rejection-sampling kernel.

#### b6 — Inverse-transform sampling
- **Kernel:** exponential draws `t=−ln(U)/λ(x)`, `λ(x)=2.5−2x`; return sample
  mean `≈1/λ(x)` (seed 42, n=6000).
- **Domain:** inverse-CDF (quantile) sampling.
- **Class membership:** seeded stochastic estimator; `E[·]=1/λ(x)` increasing.
- **Input domain:** `x ∈ [0,1]` → `λ ∈ [0.5,2.5]`.
- **MRs:** MP1 ○; MP2 **●●** monotone; MP3 ●; MP4 ○; MP5 ● positive mean.
- **Diversity:** first quantile-transform sampler.

#### b7 — Importance sampling
- **Kernel:** self-normalised IS estimate of `E_p[t]`, target `p=N(4x−2,1)`,
  proposal `q=N(0,1²·2)`; return weighted mean (seed 42, n=6000).
- **Domain:** importance-weighted Monte-Carlo expectation.
- **Class membership:** seeded stochastic estimator; `E[·]≈4x−2`.
- **Input domain:** `x ∈ [0,1]`.
- **MRs:** MP1 ○; MP2 **●●** monotone; MP3 ●; MP4 ○; MP5 ● bounded.
- **Diversity:** first importance-weighted estimator (distinct from B3's plain
  MC average).

### Class C — Surrogate (fit to a known monotone target)

All map `x → t = 6x − 3 ∈ [−3,3]`, fit a monotone target, query at `t`.

#### c4 — k-Nearest-Neighbours regressor
- **Kernel:** `KNeighborsRegressor(n_neighbors=7)` fit to `arctan(3t)`; predict at `t`.
- **Domain:** instance-based (memory) surrogate.
- **MRs:** MP1 ● anti-symmetry; MP2 ●● monotone; MP3 ● bounded; MP4 ●;
  MP5 **●●** asymptotic ordering.
- **Diversity:** first non-parametric instance-based surrogate.

#### c5 — Random-Forest regressor
- **Kernel:** `RandomForestRegressor(100, seed 42)` fit to `tanh(2t)`; predict at `t`.
- **Domain:** ensemble decision-tree surrogate.
- **MRs:** MP1 ●; MP2 ●● monotone; MP3 ● bounded; MP4 ●; MP5 **●●**.
- **Diversity:** first tree-ensemble surrogate.

#### c6 — RBF interpolation
- **Kernel:** `scipy.interpolate.RBFInterpolator` (thin-plate) fit to `erf(t)`;
  predict at `t`.
- **Domain:** radial-basis-function scattered interpolation.
- **MRs:** MP1 ● anti-symmetry; MP2 ●● monotone; MP3 ● bounded; MP4 ●;
  MP5 **●●**.
- **Diversity:** first RBF surrogate (distinct kernel family from C1 GPR).

#### c7 — Support-Vector regression
- **Kernel:** `SVR(kernel='rbf')` fit to `tanh(1.5t)`; predict at `t`.
- **Domain:** kernel support-vector regression.
- **MRs:** MP1 ● anti-symmetry; MP2 ●● monotone; MP3 ● bounded; MP4 ●;
  MP5 **●●**.
- **Diversity:** first margin-based (ε-insensitive) surrogate.

### Class D — ML classifiers (P(y=1) monotone in x)

#### d4 — Gaussian Naive Bayes
- **Kernel:** `GaussianNB` on 2-D data, label `x1+x2>0`, feature `[x,x]`.
- **Domain:** generative Bayesian classifier.
- **MRs:** MP1 ●● probability validity `[0,1]`; MP2 **●●** monotone; MP3 ●
  idempotency; MP4 ●; MP5 ●● asymptotic.
- **Diversity:** first generative (density-based) classifier.

#### d5 — Linear Discriminant Analysis
- **Kernel:** `LinearDiscriminantAnalysis`, linear boundary `0.8x1−0.6x2>0`,
  feature `[x,0]`.
- **Domain:** discriminant analysis (shared-covariance).
- **MRs:** MP1 ●●; MP2 **●●**; MP3 ●; MP4 ●; MP5 ●●.
- **Diversity:** first discriminant-analysis classifier.

#### d6 — Quadratic Discriminant Analysis
- **Kernel:** `QuadraticDiscriminantAnalysis`, radial label `x1²+x2²<1`,
  feature `[2−2x,0]` (moves toward centre as `x↑`).
- **Domain:** discriminant analysis (per-class covariance, curved boundary).
- **MRs:** MP1 ●●; MP2 **●●**; MP3 ●; MP4 ●; MP5 ●●.
- **Diversity:** first quadratic-boundary generative classifier.

#### d7 — SGD logistic classifier
- **Kernel:** `SGDClassifier(loss='log_loss', seed 42)`, linear boundary
  `x1>0`, feature `[x,0]`.
- **Domain:** stochastic-gradient linear classifier (distinct optimiser from
  D3's lbfgs LogReg).
- **MRs:** MP1 ●●; MP2 **●●**; MP3 ●; MP4 ●; MP5 ●●.
- **Diversity:** same hypothesis class as D3 but a different training
  algorithm — probes optimiser-induced fault sensitivity.

#### d8 — Gaussian Process classifier
- **Kernel:** `GaussianProcessClassifier(RBF)`, linear boundary `x1+x2>0`,
  feature `[x,x]`.
- **Domain:** kernel-Bayesian classifier.
- **MRs:** MP1 ●●; MP2 **●●**; MP3 ●; MP4 ●; MP5 ●●.
- **Diversity:** first Bayesian-kernel classifier.

---

## 5. Diversity argument (summary)

The 18 kernels broaden algorithmic coverage rather than clone existing ones:

- **A** adds five *distinct* numerical domains — quadrature, spline
  interpolation, root-finding, direct linear solve, explicit RK4 stepping —
  covering Numerical-Recipes chapters (2,3,4,9,17) not represented by A1–A3.
- **B** adds four *distinct* sampling paradigms — bootstrap, rejection,
  inverse-transform, importance sampling — none of which is a plain
  seeded-mean MC (B3) or a chain sampler (B2).
- **C** adds four surrogate families from disjoint hypothesis classes —
  instance-based (kNN), tree-ensemble (RF), radial-basis interpolation,
  support-vector regression — complementing GPR/PCE/MLP.
- **D** adds five classifier families — generative (GaussianNB), discriminant
  (LDA/QDA), stochastic-gradient linear, and kernel-Bayesian (GPC) —
  complementing MLP/SVM/LogReg and spanning generative vs discriminative and
  linear vs curved boundaries.

## 6. Registration surface touched

| Layer | Change |
|-------|--------|
| `src/p2/puts/{a4..d8}.py` | 18 new PUT modules (auto-discovered by `load_put`). |
| `src/p2/mrs/{a4..d8}.py`  | 18 new MR modules (5 MP pairs + trivial each). |
| `src/p2/config/primary.py` | `PRIMARY_CELLS_V3` extended with 18 entries via the class rule. |
| `scripts/gen_mr_json.py`  | `CELLS` extended with 18 entries; regenerates 90 new `data/mr_export/*.json` (existing 60 untouched). |
| `tests/puts`, `tests/mrs` | new unit + MR + JSON-export tests. |

**Deferred to the mutation-campaign / E1 agent (not touched here):**
`src/p2/mutators/operator_registry.py` — the 5×18 = 90 semantic-mutation
operator specs. Its id-format test regex is `^([a-d][1-3])_...` and will need
broadening to `[a-d][1-9]` before a4–d8 operators are added. Registering
operators would (a) break that baseline regex test and (b) require authoring
mutation specs, which is campaign-generation work owned by E1. The pipeline can
already *enumerate* 30 PUTs (PUT modules + MR modules + mr_export + primary
map); operator specs are only needed at campaign-run time, which follows the
registration freeze.
