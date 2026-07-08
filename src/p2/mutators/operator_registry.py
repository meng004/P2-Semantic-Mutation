"""Named mutation operators per PUT — replaces vague mut_intents.py.

Each operator is a named, structured spec describing a SINGLE semantic defect.
Categories:
  OS — Operator Swap (e.g., +/-, prod/sum, AND/OR)
  CE — Coefficient/Constant Error (numerical literal change)
  SI — Structure/Index Error (matrix entry, axis, slice)
  HP — Hyperparameter substitution (kernel, degree, depth, n_iter)
  CF — Control Flow error (loop bound, condition direction)
  TF — Training/Fit data error (label/feature corruption)

The registry is the AUTHORITATIVE source for what gets generated and reported.
Pre-existing exploratory mutants (Track 1) are reported separately.
"""
from dataclasses import dataclass, asdict
from typing import List


@dataclass(frozen=True)
class MutationOperator:
    id: str               # e.g. "a2_OS1"
    put: str              # "a2"
    category: str         # OS|CE|SI|HP|CF|TF
    label: str            # short human-readable, e.g. "prod→sum"
    target_locator: str   # natural-language pointer to code site
    transformation: str   # exact change, in plain language
    rationale: str        # why this is a plausible scientist mistake
    is_key: bool = False  # True → run K=20 instead of K=10


OPERATORS: List[MutationOperator] = [
    # ── A1 Lorenz ODE ──────────────────────────────────────────────────────
    MutationOperator(
        id="a1_CE1", put="a1", category="CE", label="rho 28→27.5",
        target_locator="module-level constant _RHO",
        transformation="change _RHO from 28.0 to 27.5",
        rationale="parameter typo near critical value alters chaos onset",
        is_key=True,
    ),
    MutationOperator(
        id="a1_OS1", put="a1", category="OS", label="sigma×beta swap",
        target_locator="_lorenz function: terms involving sigma and beta",
        transformation="swap the roles of sigma and beta in the RHS expressions",
        rationale="parameter ordering confusion in dy/dt definition",
    ),
    MutationOperator(
        id="a1_SI1", put="a1", category="SI", label="ic[0] 20x→10x",
        target_locator="initial condition vector ic in program(x)",
        transformation="change ic[0] coefficient from 20*x-10 to 10*x-10",
        rationale="halved scaling in IC — easy off-by-factor mistake",
    ),
    MutationOperator(
        id="a1_HP1", put="a1", category="HP", label="rtol 1e-8→1e-3",
        target_locator="solve_ivp call rtol parameter",
        transformation="change rtol from 1e-8 to 1e-3",
        rationale="loose tolerance gives plausibly-runnable but inaccurate solver",
    ),

    # ── A2 LU determinant ──────────────────────────────────────────────────
    MutationOperator(
        id="a2_OS1", put="a2", category="OS", label="prod→sum",
        target_locator="return statement using np.prod(np.diag(U))",
        transformation="replace np.prod with np.sum",
        rationale="reduction-operator confusion is a textbook bug",
        is_key=True,
    ),
    MutationOperator(
        id="a2_CE1", put="a2", category="CE", label="A[0,0] 2+x→2-x",
        target_locator="matrix construction A = np.array([[2+x, x], [0, 3]])",
        transformation="change A[0,0] from 2.0+x to 2.0-x",
        rationale="sign-flip on a parameter — common indexing/typo bug",
    ),
    MutationOperator(
        id="a2_SI1", put="a2", category="SI", label="diag→subdiag",
        target_locator="np.diag(U) call",
        transformation="replace np.diag(U) with np.diag(U, k=-1)",
        rationale="off-diagonal confusion when reducing to determinant",
    ),

    # ── A3 Heat equation FDM ───────────────────────────────────────────────
    MutationOperator(
        id="a3_CE1", put="a3", category="CE", label="dt coefficient ×0.5",
        target_locator="time-step computation involving dx and alpha",
        transformation="halve the chosen dt value",
        rationale="conservative-but-wrong dt — preserves stability but mis-scales time",
        is_key=True,
    ),
    MutationOperator(
        id="a3_OS1", put="a3", category="OS", label="laplacian sign flip",
        target_locator="finite-difference stencil expression",
        transformation="change u[i+1] - 2*u[i] + u[i-1] sign to -(u[i+1] - 2*u[i] + u[i-1])",
        rationale="anti-diffusion — a common stencil sign mistake",
    ),
    MutationOperator(
        id="a3_SI1", put="a3", category="SI", label="boundary u[0] copy",
        target_locator="boundary condition assignment after the time loop",
        transformation="copy u[1] into u[0] at each step instead of fixed-value BC",
        rationale="Neumann-vs-Dirichlet boundary confusion",
    ),

    # ── B1 Beta-Binomial update ────────────────────────────────────────────
    MutationOperator(
        id="b1_OS1", put="b1", category="OS", label="alpha/beta swap",
        target_locator="posterior mean computation alpha_post / (alpha_post + beta_post)",
        transformation="swap roles of alpha_post and beta_post in mean formula",
        rationale="parameter naming confusion in conjugate update",
        is_key=True,
    ),
    MutationOperator(
        id="b1_CE1", put="b1", category="CE", label="successes off-by-one",
        target_locator="alpha_post = prior_alpha + successes",
        transformation="change successes to (successes - 1) with floor at 0",
        rationale="off-by-one in success-count accumulation",
    ),
    MutationOperator(
        id="b1_HP1", put="b1", category="HP", label="prior alpha 1→3",
        target_locator="prior_alpha definition",
        transformation="change prior_alpha from 1.0 to 3.0",
        rationale="incorrect informative prior — silent specification error",
    ),

    # ── B2 MCMC Metropolis-Hastings ────────────────────────────────────────
    MutationOperator(
        id="b2_HP1", put="b2", category="HP", label="proposal width ×0.1",
        target_locator="proposal step size sigma in the MH loop",
        transformation="multiply proposal sigma by 0.1",
        rationale="under-mixing chain — common tuning mistake",
        is_key=True,
    ),
    MutationOperator(
        id="b2_CF1", put="b2", category="CF", label="acceptance reversed",
        target_locator="acceptance condition `u < accept_ratio`",
        transformation="reverse to `u > accept_ratio`",
        rationale="wrong inequality direction — invariant-breaking",
    ),
    MutationOperator(
        id="b2_CE1", put="b2", category="CE", label="target mean shift +0.3",
        target_locator="target distribution mean parameter",
        transformation="add 0.3 to the target mean expression",
        rationale="silent target-spec drift",
    ),

    # ── B3 MC integration ──────────────────────────────────────────────────
    MutationOperator(
        id="b3_OS1", put="b3", category="OS", label="integrand x+t^2→x*t^2",
        target_locator="integrand expression inside the sample sum",
        transformation="change x + t**2 to x * t**2",
        rationale="addition vs multiplication confusion in math expression",
        is_key=True,
    ),
    MutationOperator(
        id="b3_CE1", put="b3", category="CE", label="exponent 2→3",
        target_locator="t**2 inside integrand",
        transformation="change t**2 to t**3",
        rationale="off-by-one exponent typo",
    ),
    MutationOperator(
        id="b3_SI1", put="b3", category="SI", label="sample axis sum→prod",
        target_locator="estimator reduction over sample axis",
        transformation="replace mean by product divided by N",
        rationale="aggregation confusion in MC estimator",
    ),

    # ── C1 GPR surrogate ───────────────────────────────────────────────────
    MutationOperator(
        id="c1_HP1", put="c1", category="HP", label="kernel length-scale ×10",
        target_locator="GP kernel length_scale parameter",
        transformation="multiply length_scale by 10",
        rationale="over-smoothing kills monotonicity",
        is_key=True,
    ),
    MutationOperator(
        id="c1_TF1", put="c1", category="TF", label="train range narrowed",
        target_locator="training x range generation",
        transformation="restrict training x from [0,1] to [0.3,0.7]",
        rationale="extrapolation regime — surrogate fidelity drop",
    ),
    MutationOperator(
        id="c1_CE1", put="c1", category="CE", label="WhiteKernel noise 1e-4→1e-1",
        target_locator="WhiteKernel noise_level inside the RBF+WhiteKernel composite kernel",
        transformation="change WhiteKernel noise_level from 1e-4 to 1e-1",
        rationale="over-noisy kernel assumption makes GPR over-smooth its predictions",
    ),

    # ── C2 PCE surrogate ───────────────────────────────────────────────────
    MutationOperator(
        id="c2_HP1", put="c2", category="HP", label="degree 5→1",
        target_locator="polynomial degree in PCE construction",
        transformation="change degree from 5 to 1",
        rationale="under-fitting — common manual config mistake",
        is_key=True,
    ),
    MutationOperator(
        id="c2_TF1", put="c2", category="TF", label="train points halved",
        target_locator="number of collocation points",
        transformation="halve the number of collocation points",
        rationale="ill-posed regression — fewer points than coefficients",
    ),
    MutationOperator(
        id="c2_OS1", put="c2", category="OS", label="basis poly→spline",
        target_locator="feature transformer in the regression pipeline",
        transformation="replace PolynomialFeatures(5, include_bias=True) with SplineTransformer(n_knots=6, degree=3)",
        rationale="wrong basis class — spline basis spans a different function space than monomials",
    ),

    # ── C3 MLP surrogate ───────────────────────────────────────────────────
    MutationOperator(
        id="c3_HP1", put="c3", category="HP", label="activation relu→tanh",
        target_locator="MLPRegressor activation parameter",
        transformation="change activation from 'relu' to 'tanh'",
        rationale="saturating activation alters convergence dynamics on the sigmoid target",
    ),
    MutationOperator(
        id="c3_TF1", put="c3", category="TF", label="max_iter 1000→5",
        target_locator="MLPRegressor max_iter parameter",
        transformation="change max_iter from 1000 to 5",
        rationale="under-training — common manual configuration mistake",
        is_key=True,
    ),
    MutationOperator(
        id="c3_CE1", put="c3", category="CE", label="hidden width 32→2",
        target_locator="hidden layer width",
        transformation="change hidden_width from 32 to 2",
        rationale="too-small capacity — under-fits",
    ),

    # ── D1 Linear SVM ──────────────────────────────────────────────────────
    MutationOperator(
        id="d1_TF1", put="d1", category="TF", label="labels flipped",
        target_locator="training label vector y",
        transformation="replace y with 1-y",
        rationale="off-by-one label encoding mistake",
    ),
    MutationOperator(
        id="d1_HP1", put="d1", category="HP", label="MLP alpha 1e-4→1.0",
        target_locator="MLPClassifier alpha (L2 regularisation) parameter",
        transformation="change alpha from 1e-4 (default) to 1.0",
        rationale="over-regularisation collapses decision boundary",
        is_key=True,
    ),
    MutationOperator(
        id="d1_SI1", put="d1", category="SI", label="feature index dropped",
        target_locator="feature-vector construction in program(x)",
        transformation="set the second feature to 0 always",
        rationale="silent feature-engineering bug",
    ),

    # ── D2 RBF SVM ─────────────────────────────────────────────────────────
    MutationOperator(
        id="d2_HP1", put="d2", category="HP", label="gamma scale→1e-3",
        target_locator="RBF kernel gamma parameter",
        transformation="set gamma=1e-3 instead of 'scale'",
        rationale="manual gamma tuning often wrong by orders of magnitude",
    ),
    MutationOperator(
        id="d2_TF1", put="d2", category="TF", label="train labels permuted",
        target_locator="training labels assignment",
        transformation="randomly permute first 20% of training labels",
        rationale="mislabeled subset — common annotation error",
    ),
    MutationOperator(
        id="d2_OS1", put="d2", category="OS", label="predict_proba→decision_function",
        target_locator="prediction call in program(x)",
        transformation="use decision_function output instead of predict_proba",
        rationale="API confusion between margin and probability",
    ),

    # ── D3 Decision Tree ───────────────────────────────────────────────────
    MutationOperator(
        id="d3_HP1", put="d3", category="HP", label="LR C 1.0→1e-4",
        target_locator="LogisticRegression C parameter",
        transformation="change C from 1.0 to 1e-4",
        rationale="over-regularisation flattens decision boundary",
    ),
    MutationOperator(
        id="d3_TF1", put="d3", category="TF", label="train labels swapped",
        target_locator="training labels y",
        transformation="replace y with 1-y",
        rationale="label encoding flipped",
    ),
    MutationOperator(
        id="d3_SI1", put="d3", category="SI", label="single-feature input",
        target_locator="feature vector construction",
        transformation="use only first feature, drop the second",
        rationale="incomplete feature set",
    ),

    # ══════════════════════════════════════════════════════════════════════
    # STUDY-2 EXPANSION — 18 new PUTs (a4–a8, b4–b7, c4–c7, d4–d8).
    # Specs authored BLIND to mutation outcomes: derived from each PUT's
    # source code (src/p2/puts/{id}.py) and the per-PUT spec conventions
    # above only. No data/results/* file was read. Each op is a single
    # semantic defect that (i) executes on x∈[0,1] and (ii) is non-trivial
    # (differs from the original on the probe set). Convention preserved:
    # ≥3 ops/PUT, ≥2 categories/PUT, one is_key per PUT.
    # ══════════════════════════════════════════════════════════════════════

    # ── A4 Gauss–Legendre quadrature ───────────────────────────────────────
    MutationOperator(
        id="a4_OS1", put="a4", category="OS", label="integrand +→−",
        target_locator="integrand expression `x + 0.5*_NODES**2`",
        transformation="change `x + 0.5*_NODES**2` to `x - 0.5*_NODES**2`",
        rationale="sign confusion in the integrand additive/quadratic split",
        is_key=True,
    ),
    MutationOperator(
        id="a4_CE1", put="a4", category="CE", label="half-coeff 0.5→1.0",
        target_locator="quadratic coefficient in `0.5*_NODES**2`",
        transformation="change 0.5 to 1.0 in the integrand",
        rationale="dropped one-half factor — common transcription slip",
    ),
    MutationOperator(
        id="a4_HP1", put="a4", category="HP", label="nodes 16→1",
        target_locator="leggauss node count `leggauss(16)`",
        transformation="change leggauss(16) to leggauss(1)",
        rationale="too-few quadrature nodes under-resolves the degree-2 term",
    ),

    # ── A5 Cubic-spline interpolation ──────────────────────────────────────
    MutationOperator(
        id="a5_HP1", put="a5", category="HP", label="bc natural→clamped",
        target_locator="CubicSpline bc_type parameter",
        transformation="change bc_type from 'natural' to 'clamped'",
        rationale="wrong boundary condition perturbs the interpolant near edges",
        is_key=True,
    ),
    MutationOperator(
        id="a5_CE1", put="a5", category="CE", label="knots 17→5",
        target_locator="sample-grid size in `np.linspace(0.0, 1.0, 17)`",
        transformation="change the number of interpolation samples from 17 to 5",
        rationale="coarse grid — under-samples the sine target",
    ),
    MutationOperator(
        id="a5_OS1", put="a5", category="OS", label="target sin→cos",
        target_locator="target-function call `np.sin(np.pi * _TI)`",
        transformation="replace np.sin with np.cos in the fitted target",
        rationale="trig-function confusion when defining the interpolation target",
    ),

    # ── A6 Brent root-finding ──────────────────────────────────────────────
    MutationOperator(
        id="a6_OS1", put="a6", category="OS", label="LHS +r→−r",
        target_locator="residual function `_g`: `r**3 + r - rhs`",
        transformation="change `r**3 + r - rhs` to `r**3 - r - rhs`",
        rationale="sign flip on the linear term redefines the equation solved",
        is_key=True,
    ),
    MutationOperator(
        id="a6_CE1", put="a6", category="CE", label="rhs const 2→1",
        target_locator="right-hand side `4.0*x - 2.0`",
        transformation="change the constant in `4.0*x - 2.0` from 2.0 to 1.0",
        rationale="off-by-one offset in the target-value mapping",
    ),
    MutationOperator(
        id="a6_HP1", put="a6", category="HP", label="xtol 1e-12→1e-1",
        target_locator="brentq xtol parameter",
        transformation="change xtol from 1e-12 to 1e-1",
        rationale="loose tolerance yields a runnable but inaccurate root",
    ),

    # ── A7 Tridiagonal linear solve ────────────────────────────────────────
    MutationOperator(
        id="a7_CE1", put="a7", category="CE", label="diag 2→3",
        target_locator="main-diagonal fill `_AB[1, :] = 2.0`",
        transformation="change the main-diagonal value from 2.0 to 3.0",
        rationale="wrong stencil coefficient in the tridiagonal operator",
        is_key=True,
    ),
    MutationOperator(
        id="a7_OS1", put="a7", category="OS", label="rhs −→+",
        target_locator="right-hand side `(2.0*x - 1.0) * _D`",
        transformation="change `(2.0*x - 1.0)` to `(2.0*x + 1.0)`",
        rationale="sign error in the linear forcing term",
    ),
    MutationOperator(
        id="a7_SI1", put="a7", category="SI", label="drop sub-diagonal",
        target_locator="sub-diagonal fill `_AB[2, :-1] = -1.0`",
        transformation="set the sub-diagonal band to 0.0 (leave only super+main)",
        rationale="matrix-band indexing bug drops one off-diagonal",
    ),

    # ── A8 RK4 ODE stepper ─────────────────────────────────────────────────
    MutationOperator(
        id="a8_OS1", put="a8", category="OS", label="rhs −u→+u",
        target_locator="RHS function `_rhs`: `return -u`",
        transformation="change `return -u` to `return u`",
        rationale="sign flip turns decay into growth — invariant-breaking",
        is_key=True,
    ),
    MutationOperator(
        id="a8_CE1", put="a8", category="CE", label="IC 2x-1→2x-0.5",
        target_locator="initial condition `u = 2.0*float(x) - 1.0`",
        transformation="change the IC constant from 1.0 to 0.5",
        rationale="off-by-a-half in the initial-condition mapping",
    ),
    MutationOperator(
        id="a8_CF1", put="a8", category="CF", label="loop off-by-one",
        target_locator="integration loop `for _ in range(_N_STEPS)`",
        transformation="change the loop bound to range(_N_STEPS - 1)",
        rationale="off-by-one loop bound under-integrates by one step",
    ),

    # ── B4 Bootstrap resampling ────────────────────────────────────────────
    MutationOperator(
        id="b4_OS1", put="b4", category="OS", label="shift +→−",
        target_locator="location shift `_D + (4.0*x - 2.0)`",
        transformation="change `_D + (4.0*x - 2.0)` to `_D - (4.0*x - 2.0)`",
        rationale="sign flip reverses the monotone location shift",
        is_key=True,
    ),
    MutationOperator(
        id="b4_CE1", put="b4", category="CE", label="shift const 2→1",
        target_locator="shift expression `4.0*x - 2.0`",
        transformation="change the constant in `4.0*x - 2.0` from 2.0 to 1.0",
        rationale="mis-centred location shift — constant transcription error",
    ),
    MutationOperator(
        id="b4_TF1", put="b4", category="TF", label="base sample +5",
        target_locator="base sample `standard_normal(_N)`",
        transformation="add 5.0 to the base sample _D at construction",
        rationale="corrupted base data biases every bootstrap replicate",
    ),

    # ── B5 Rejection sampling ──────────────────────────────────────────────
    MutationOperator(
        id="b5_OS1", put="b5", category="OS", label="kernel props−mu→props+mu",
        target_locator="acceptance kernel `np.exp(-0.5*(props - mu)**2)`",
        transformation="change `(props - mu)` to `(props + mu)` in the kernel",
        rationale="sign error mislocates the acceptance region",
        is_key=True,
    ),
    MutationOperator(
        id="b5_CE1", put="b5", category="CE", label="mean const 2→1",
        target_locator="target mean `mu = 4.0*x - 2.0`",
        transformation="change the constant in `4.0*x - 2.0` from 2.0 to 1.0",
        rationale="off-by-one target-mean offset",
    ),
    MutationOperator(
        id="b5_HP1", put="b5", category="HP", label="proposals 6000→50",
        target_locator="proposal count `_N_PROP = 6000`",
        transformation="change _N_PROP from 6000 to 50",
        rationale="too-few proposals gives a noisy, biased accepted mean",
    ),

    # ── B6 Inverse-transform sampling ──────────────────────────────────────
    MutationOperator(
        id="b6_OS1", put="b6", category="OS", label="draw sign flip",
        target_locator="inverse-CDF draw `-np.log(_U) / lam`",
        transformation="change `-np.log(_U)` to `np.log(_U)` (drop the minus)",
        rationale="sign error in the inverse-transform yields negative draws",
        is_key=True,
    ),
    MutationOperator(
        id="b6_CE1", put="b6", category="CE", label="rate coeff 2→1",
        target_locator="rate `lam = 2.5 - 2.0*x`",
        transformation="change the coefficient in `2.5 - 2.0*x` from 2.0 to 1.0",
        rationale="wrong rate-slope coefficient in the exponential parameter",
    ),
    MutationOperator(
        id="b6_HP1", put="b6", category="HP", label="n 6000→30",
        target_locator="sample count `_N = 6000`",
        transformation="change _N from 6000 to 30",
        rationale="tiny sample size destabilises the estimated mean",
    ),

    # ── B7 Importance sampling ─────────────────────────────────────────────
    MutationOperator(
        id="b7_OS1", put="b7", category="OS", label="normaliser sum(w)→N",
        target_locator="self-normalisation `np.sum(w*_SAMPLES)/np.sum(w)`",
        transformation="replace the denominator np.sum(w) with _N",
        rationale="drops self-normalisation — a classic IS estimator bug",
        is_key=True,
    ),
    MutationOperator(
        id="b7_CE1", put="b7", category="CE", label="target const 2→1",
        target_locator="target mean `mu = 4.0*x - 2.0`",
        transformation="change the constant in `4.0*x - 2.0` from 2.0 to 1.0",
        rationale="off-by-one target-mean offset in the importance weights",
    ),
    MutationOperator(
        id="b7_HP1", put="b7", category="HP", label="target std 1→2",
        target_locator="target density `norm.pdf(_SAMPLES, mu, 1.0)`",
        transformation="change the target std in norm.pdf from 1.0 to 2.0",
        rationale="wrong target variance distorts the importance weights",
    ),

    # ── C4 kNN regressor surrogate ─────────────────────────────────────────
    MutationOperator(
        id="c4_HP1", put="c4", category="HP", label="k 7→1",
        target_locator="KNeighborsRegressor n_neighbors parameter",
        transformation="change n_neighbors from 7 to 1",
        rationale="1-NN over-fits — jagged, high-variance surrogate",
        is_key=True,
    ),
    MutationOperator(
        id="c4_TF1", put="c4", category="TF", label="train range narrowed",
        target_locator="training-point generation `_rng.uniform(-3.0, 3.0, 300)`",
        transformation="restrict the training range from [-3,3] to [-1,1]",
        rationale="narrowed support forces extrapolation at query points",
    ),
    MutationOperator(
        id="c4_CE1", put="c4", category="CE", label="test map 3→1.5",
        target_locator="test-point mapping `t = 6.0*x - 3.0`",
        transformation="change the offset in `6.0*x - 3.0` from 3.0 to 1.5",
        rationale="mis-scaled query mapping shifts the evaluation point",
    ),

    # ── C5 Random-Forest surrogate ─────────────────────────────────────────
    MutationOperator(
        id="c5_HP1", put="c5", category="HP", label="trees 100→1",
        target_locator="RandomForestRegressor n_estimators parameter",
        transformation="change n_estimators from 100 to 1",
        rationale="single tree — high-variance, step-like surrogate",
        is_key=True,
    ),
    MutationOperator(
        id="c5_TF1", put="c5", category="TF", label="train range narrowed",
        target_locator="training-point generation `_rng.uniform(-3.0, 3.0, 300)`",
        transformation="restrict the training range from [-3,3] to [-1,1]",
        rationale="narrowed support degrades fidelity at the domain edges",
    ),
    MutationOperator(
        id="c5_CE1", put="c5", category="CE", label="test map 3→2",
        target_locator="test-point mapping `t = 6.0*x - 3.0`",
        transformation="change the offset in `6.0*x - 3.0` from 3.0 to 2.0",
        rationale="mis-scaled query mapping shifts the evaluation point",
    ),

    # ── C6 RBF interpolation surrogate ─────────────────────────────────────
    MutationOperator(
        id="c6_HP1", put="c6", category="HP", label="kernel tps→linear",
        target_locator="RBFInterpolator kernel parameter",
        transformation="change kernel from 'thin_plate_spline' to 'linear'",
        rationale="wrong RBF kernel family changes the interpolation basis",
        is_key=True,
    ),
    MutationOperator(
        id="c6_TF1", put="c6", category="TF", label="train range narrowed",
        target_locator="training-point generation `_rng.uniform(-3.0, 3.0, 300)`",
        transformation="restrict the training range from [-3,3] to [-1,1]",
        rationale="narrowed support forces extrapolation of the erf target",
    ),
    MutationOperator(
        id="c6_CE1", put="c6", category="CE", label="test map 3→2",
        target_locator="test-point mapping `t = 6.0*x - 3.0`",
        transformation="change the offset in `6.0*x - 3.0` from 3.0 to 2.0",
        rationale="mis-scaled query mapping shifts the evaluation point",
    ),

    # ── C7 SVR surrogate ───────────────────────────────────────────────────
    MutationOperator(
        id="c7_HP1", put="c7", category="HP", label="C 10→0.01",
        target_locator="SVR regularisation C parameter",
        transformation="change C from 10.0 to 0.01",
        rationale="over-regularised SVR flattens toward the mean",
        is_key=True,
    ),
    MutationOperator(
        id="c7_TF1", put="c7", category="TF", label="train range narrowed",
        target_locator="training-point generation `_rng.uniform(-3.0, 3.0, 300)`",
        transformation="restrict the training range from [-3,3] to [-1,1]",
        rationale="narrowed support degrades fit at the domain edges",
    ),
    MutationOperator(
        id="c7_CE1", put="c7", category="CE", label="epsilon 0.01→1.0",
        target_locator="SVR epsilon-insensitive tube parameter",
        transformation="change epsilon from 0.01 to 1.0",
        rationale="wide insensitive tube ignores the target's structure",
    ),

    # ── D4 Gaussian Naive Bayes ────────────────────────────────────────────
    MutationOperator(
        id="d4_TF1", put="d4", category="TF", label="label flip",
        target_locator="training label `(_X_train[:,0] + _X_train[:,1] > 0)`",
        transformation="change the label comparison `> 0` to `< 0`",
        rationale="inverted class labels reverse the learned boundary",
        is_key=True,
    ),
    MutationOperator(
        id="d4_SI1", put="d4", category="SI", label="drop 2nd feature",
        target_locator="feature vector `[2.0*x - 1.0, 2.0*x - 1.0]`",
        transformation="set the second feature to 0.0",
        rationale="feature-construction bug zeroes one input coordinate",
    ),
    MutationOperator(
        id="d4_CE1", put="d4", category="CE", label="feat offset 1→0.5",
        target_locator="feature map `2.0*x - 1.0`",
        transformation="change the offset in `2.0*x - 1.0` from 1.0 to 0.5",
        rationale="mis-centred feature map shifts the probability curve",
    ),

    # ── D5 Linear Discriminant Analysis ────────────────────────────────────
    MutationOperator(
        id="d5_TF1", put="d5", category="TF", label="label flip",
        target_locator="training label `(0.8*X0 - 0.6*X1 > 0)`",
        transformation="change the label comparison `> 0` to `< 0`",
        rationale="inverted class labels reverse the discriminant direction",
        is_key=True,
    ),
    MutationOperator(
        id="d5_SI1", put="d5", category="SI", label="feature index swap",
        target_locator="feature vector `[2.0*x - 1.0, 0.0]`",
        transformation="swap the feature slots to `[0.0, 2.0*x - 1.0]`",
        rationale="feature-index transposition puts the signal on the wrong axis",
    ),
    MutationOperator(
        id="d5_CE1", put="d5", category="CE", label="feat offset 1→0.5",
        target_locator="feature map `2.0*x - 1.0`",
        transformation="change the offset in `2.0*x - 1.0` from 1.0 to 0.5",
        rationale="mis-centred feature map shifts the probability curve",
    ),

    # ── D6 Quadratic Discriminant Analysis ─────────────────────────────────
    MutationOperator(
        id="d6_TF1", put="d6", category="TF", label="label inside↔outside",
        target_locator="training label `(x1**2 + x2**2 < 1.0)`",
        transformation="change the radial label comparison `< 1.0` to `> 1.0`",
        rationale="inverted inside/outside labelling flips the class geometry",
        is_key=True,
    ),
    MutationOperator(
        id="d6_CE1", put="d6", category="CE", label="feat coeff 2→1",
        target_locator="feature map `2.0 - 2.0*x`",
        transformation="change the coefficient in `2.0 - 2.0*x` from 2.0 to 1.0",
        rationale="mis-scaled feature trajectory toward the class centre",
    ),
    MutationOperator(
        id="d6_SI1", put="d6", category="SI", label="duplicate into 2nd feat",
        target_locator="feature vector `[2.0 - 2.0*x, 0.0]`",
        transformation="set the second feature equal to the first (`[2-2x, 2-2x]`)",
        rationale="feature-construction bug injects signal into a zeroed slot",
    ),

    # ── D7 SGD logistic classifier ─────────────────────────────────────────
    MutationOperator(
        id="d7_TF1", put="d7", category="TF", label="label flip",
        target_locator="training label `(_X_train[:,0] > 0)`",
        transformation="change the label comparison `> 0` to `< 0`",
        rationale="inverted class labels reverse the learned boundary",
        is_key=True,
    ),
    MutationOperator(
        id="d7_HP1", put="d7", category="HP", label="max_iter 1000→2",
        target_locator="SGDClassifier max_iter parameter",
        transformation="change max_iter from 1000 to 2",
        rationale="under-training leaves the boundary far from convergence",
    ),
    MutationOperator(
        id="d7_CE1", put="d7", category="CE", label="feat offset 1→0.5",
        target_locator="feature map `2.0*x - 1.0`",
        transformation="change the offset in `2.0*x - 1.0` from 1.0 to 0.5",
        rationale="mis-centred feature map shifts the probability curve",
    ),

    # ── D8 Gaussian Process classifier ─────────────────────────────────────
    MutationOperator(
        id="d8_TF1", put="d8", category="TF", label="label flip",
        target_locator="training label `(_X_train[:,0] + _X_train[:,1] > 0)`",
        transformation="change the label comparison `> 0` to `< 0`",
        rationale="inverted class labels reverse the learned boundary",
        is_key=True,
    ),
    MutationOperator(
        id="d8_HP1", put="d8", category="HP", label="length_scale 1→10",
        target_locator="RBF kernel length_scale parameter",
        transformation="change RBF length_scale from 1.0 to 10.0",
        rationale="over-smoothing kernel washes out the decision boundary",
    ),
    MutationOperator(
        id="d8_SI1", put="d8", category="SI", label="drop 2nd feature",
        target_locator="feature vector `[1.6*x - 0.8, 1.6*x - 0.8]`",
        transformation="set the second feature to 0.0",
        rationale="feature-construction bug zeroes one input coordinate",
    ),
]


def get_operators_for_put(put: str) -> List[MutationOperator]:
    return [op for op in OPERATORS if op.put == put]


def key_operators() -> List[MutationOperator]:
    return [op for op in OPERATORS if op.is_key]


def dump_registry_json(path: str) -> None:
    import json
    payload = [asdict(op) for op in OPERATORS]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
