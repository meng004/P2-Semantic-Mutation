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
        id="c1_CE1", put="c1", category="CE", label="noise sigma 1e-6→0.1",
        target_locator="GPR alpha (noise) hyperparameter",
        transformation="change alpha from 1e-6 to 0.1",
        rationale="noisy fit — real but commonly-overlooked error",
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
        id="c2_OS1", put="c2", category="OS", label="basis poly→cheb",
        target_locator="orthogonal-polynomial basis selection",
        transformation="replace Legendre with Chebyshev-1 basis",
        rationale="wrong basis for the underlying density",
    ),

    # ── C3 MLP surrogate ───────────────────────────────────────────────────
    MutationOperator(
        id="c3_HP1", put="c3", category="HP", label="activation tanh→relu",
        target_locator="hidden activation choice",
        transformation="change activation from tanh to relu",
        rationale="ReLU breaks monotone smoothness for sigmoid target",
    ),
    MutationOperator(
        id="c3_TF1", put="c3", category="TF", label="epochs 200→5",
        target_locator="training epoch count",
        transformation="change epochs from 200 to 5",
        rationale="under-training — easy oversight",
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
        id="d1_HP1", put="d1", category="HP", label="C 1.0→1e-4",
        target_locator="SVM regularisation constant C",
        transformation="change C from 1.0 to 1e-4",
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
        id="d3_HP1", put="d3", category="HP", label="max_depth None→1",
        target_locator="DecisionTreeClassifier max_depth parameter",
        transformation="set max_depth=1",
        rationale="under-fitted stump — easy hyperparameter mistake",
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
