"""Study-5 Family-XL registered selection registry (Amendment A1 audit data).

Executes PREREGISTRATION_STUDY5_v1.md §2b: candidates enumerated from the
registered source list (Step 2, fixed order), screened by the registered
pre-behavioral criteria (Step 3), scored ``(c, l)`` = (#instantiable strata,
#non-Python languages with a same-semantics external implementation) and
sorted by the registered total order (Step 4): c desc, l desc, source-list
index asc, program name asc (ASCII). ``CANDIDATES`` below is stored in that
deterministic rank order; ``SCREENED`` records every enumerated candidate
that failed a Step-3 criterion, with the clause cited.

No entry in this file consults any behavioral quantity: instantiability is
judged from governing structure + the frozen adapter interface (global input
transforms r:[0,1]->[0,1], output relations R(y_orig, y_new), per the
existing src/p2/mrs convention); domain maps and aux parameters are frozen
HERE, before any certification run (the only downstream behavioral
measurement, §2c).

Per-pair primary stratum via the registered category->stratum map (first
matching row, G > O<= > L* > D* > E*).
"""

SOURCES = {
    1: "TheAlgorithms/{Python,C,C-Plus-Plus,Java,Go,Rust}",
    2: "GNU GSL (C) <-> scipy",
    3: "Julia stdlib / SciML <-> scipy",
    4: "Apache Commons Math (Java) <-> scipy",
    5: "Boost.Math (C++) <-> scipy",
}

UPSTREAM = {
    "ta-python": "github.com/TheAlgorithms/Python@c0db072a1323339e0d9148479f8818a1b9768d88 (MIT)",
    "ta-cpp": "github.com/TheAlgorithms/C-Plus-Plus@b9c118fb5dca86f6325e816481959e1e6c360373 (MIT)",
    "ta-java": "github.com/TheAlgorithms/Java@fd2858e7e6138d9f8940ee9820e172912a5acfb4 (MIT)",
    "ta-go": "github.com/TheAlgorithms/Go@5ba447ec5ff3d1213de65b92e726ee74c5d5cc19 (MIT)",
    "ta-rust": "github.com/TheAlgorithms/Rust@c65d014621a9d50b36b197f08bb1c8016ff505b0 (MIT)",
    "ta-c": "github.com/TheAlgorithms/C@e5dad3fa8def3726ec850ca66a7f51521f8ad393 (GPL-3.0)",
    "boost": "github.com/boostorg/math@8ee12a5355935cbaac5d5338372d0d0e3311b473 (BSL-1.0)",
    "cm": "Maven Central org.apache.commons:commons-math3:3.6.1, jar sha256 1e56d7b058d28b65abd256b8458e3885b674c1d588fa43cd7d1cbb9c7ef2b308 (Apache-2.0)",
    "gsl": "GNU GSL, Ubuntu libgsl-dev 2.7.1+dfsg-6ubuntu2 system library, unmodified (GPL-3.0)",
    "julia": "Julia 1.11.7 official binary tarball, stdlib entry points (MIT)",
    "scipy": "scipy 1.17.1 / numpy 2.4.6 (registered Python-side reference)",
}

# Each candidate: rank fields (c, l, src, name), instantiability documentation,
# primary stratum (category row), frozen aux/domain map, declared §2c
# exception (class, relaxed tol, derivation) or None, and its pairs.
CANDIDATES = [
    dict(
        program="trapezoid", c=5, l=1, src=1,
        category="discretised quadrature with mesh knob (map row 3)",
        primary_mp=3,
        instantiable={1: "exact product identity T(c(x))*T(c(1-x)) = K^2 with c(x)=2**(2x-1) (T(c)=K*c^3 exactly for f=u^2)",
                      2: "monotone increasing in x (f >= 0)",
                      3: "mesh-refinement structure (n=64 panels)",
                      4: "convex increasing shape envelope",
                      5: "surrogate with analytically known target integral c^3/3 (fidelity-ordered error c^3/(6n^2))"},
        aux="f(u)=u^2 frozen; interval [0, c(x)], c(x)=2**(2x-1); n=64 panels both sides",
        exception=None,
        pairs=[dict(pair="trapezoid.rs", language="rust", upstream="ta-rust",
                    files=["third_party/thealgorithms-rust/src/math/trapezoidal_integration.rs"])],
        pyref="external Python implementation third_party/thealgorithms-python/maths/trapezoidal_rule.py",
    ),
    dict(
        program="invsqrt", c=4, l=2, src=1,
        category="surrogate/fidelity-ordered approximation of 1/sqrt (map row 5)",
        primary_mp=5,
        instantiable={1: "approximate reciprocal identity y(x)*y(1-x) ~ 1 with u(x)=4**(2x-1) (banded R)",
                      2: "monotone decreasing in x",
                      4: "convex decreasing shape envelope",
                      5: "surrogate-vs-exact 1/sqrt (Mode-M relative oracle)"},
        aux="input u(x)=4**(2x-1) in [0.25,4]; float32 magic 0x5f3759df, ONE Newton iteration (matches the Python side; C++ template instantiated Fast_InvSqrt<float,1>)",
        exception=None,
        pairs=[dict(pair="invsqrt.cpp", language="cpp", upstream="ta-cpp",
                    files=["third_party/thealgorithms-cpp/math/inv_sqrt.cpp"]),
               dict(pair="invsqrt.go", language="go", upstream="ta-go",
                    files=["third_party/thealgorithms-go/math/binary/fast_inverse_sqrt.go"],
                    note="external Go entry hardcodes TWO Newton iterations vs the Python side's ONE; certification measures the discrepancy")],
        pyref="external Python implementation third_party/thealgorithms-python/maths/fast_inverse_sqrt.py",
    ),
    dict(
        program="simpson", c=4, l=2, src=1,
        category="discretised quadrature with mesh knob (map row 3)",
        primary_mp=3,
        instantiable={1: "exact product identity S(c(x))*S(c(1-x)) = 1/9 with c(x)=2**(2x-1) (Simpson exact on u^2)",
                      2: "monotone increasing in x",
                      3: "mesh-refinement structure (n=16)",
                      4: "convex increasing shape envelope"},
        aux="f(u)=u^2 frozen; interval [0, c(x)], c(x)=2**(2x-1); n=16 both sides (h=c/16 on the C++ side)",
        exception=None,
        pairs=[dict(pair="simpson.cpp", language="cpp", upstream="ta-cpp",
                    files=["third_party/thealgorithms-cpp/numerical_methods/composite_simpson_rule.cpp"]),
               dict(pair="simpson.rs", language="rust", upstream="ta-rust",
                    files=["third_party/thealgorithms-rust/src/math/simpsons_integration.rs"])],
        pyref="external Python implementation third_party/thealgorithms-python/maths/numerical_analysis/simpson_rule.py",
    ),
    dict(
        program="brent", c=4, l=2, src=2,
        category="iterative root-finder with tolerance knob (map row 3)",
        primary_mp=3,
        instantiable={1: "odd-root identity y(x) + y(1-x) = 0 (root of t^3+t-c, c(x)=4x-2)",
                      2: "monotone increasing in x (inverse of monotone cubic)",
                      3: "iterative solver with tolerance knob",
                      4: "S-shaped odd monotone envelope"},
        aux="f(t)=t^3+t-c, c(x)=4x-2, bracket [-2,2]; GSL brent epsabs=1e-12; CM BrentSolver(1e-12); scipy brentq xtol=1e-12",
        exception=dict(cls=1, tol=1e-6,
                       band="both sides converge to |droot| <= ~1e-12 by their stopping rules; combined band ~4e-12, far inside the standard 1e-6 gate (no relaxation needed; recorded for transparency)"),
        pairs=[dict(pair="brent.c", language="c", upstream="gsl", files=[]),
               dict(pair="brent.java", language="java", upstream="cm",
                    files=["third_party/commons-math/commons-math3-3.6.1.jar"])],
        pyref="scipy.optimize.brentq (registered scipy reference)",
    ),
    dict(
        program="euler", c=4, l=1, src=1,
        category="fixed-step ODE solver (map row 3)",
        primary_mp=3,
        instantiable={2: "monotone in initial condition (logistic flow order-preserving)",
                      3: "step-size discretisation structure (h=1/128)",
                      4: "trajectory/shape kernel (S-curve toward carrying capacity)",
                      5: "surrogate with known exact logistic solution"},
        aux="dy/dt = y(1-y) frozen; y0(x)=0.05+0.9x; t in [0,2]; h=1/128 (dyadic, exactly 256 steps both sides)",
        exception=None,
        pairs=[dict(pair="euler.java", language="java", upstream="ta-java",
                    files=["third_party/thealgorithms-java/src/main/java/com/thealgorithms/maths/EulerMethod.java"])],
        pyref="external Python implementation third_party/thealgorithms-python/maths/euler_method.py",
    ),
    dict(
        program="newton", c=4, l=1, src=1,
        category="iterative root-finder (map row 3)",
        primary_mp=3,
        instantiable={1: "exact reciprocal identity y(x)*y(1-x) = 1 (root of t^2-a, a(x)=4**(2x-1))",
                      2: "monotone increasing in x",
                      3: "iterative Newton structure",
                      4: "concave increasing shape envelope"},
        aux="f(t)=t^2-a, a(x)=4**(2x-1); Rust: exact derivative, guess 1.5, 8 iterations; Python: numerical derivative, x0=1.5, stops at |f|<1e-6",
        exception=dict(cls=1, tol=2e-6,
                       band="Python side stops at |f(a)|<1e-6 with min |f'| = 2*root >= 1 on the frozen domain, so its root error band is <= 1e-6; Rust side converges to machine precision (8 Newton iterations on a quadratic); combined declared band 2e-6 (<= the registered 1e-5 ceiling)"),
        pairs=[dict(pair="newton.rs", language="rust", upstream="ta-rust",
                    files=["third_party/thealgorithms-rust/src/math/newton_raphson.rs"])],
        pyref="external Python implementation third_party/thealgorithms-python/maths/numerical_analysis/newton_raphson.py",
    ),
    dict(
        program="rungekutta", c=4, l=1, src=1,
        category="fixed-step ODE solver (map row 3)",
        primary_mp=3,
        instantiable={2: "monotone in initial condition (linear ODE flow)",
                      3: "step-size discretisation structure (h=1/64)",
                      4: "trajectory/shape kernel (relaxation toward t-2 asymptote)",
                      5: "surrogate with known exact solution y = t-2+(y0+2)exp(-t/2)"},
        aux="dy/dt = (t-y)/2 frozen (hardcoded in the C++ entry; mirrored on the Python side); y0(x)=x; t in [0,2]; h=1/64 (exactly 128 steps both sides)",
        exception=None,
        pairs=[dict(pair="rungekutta.cpp", language="cpp", upstream="ta-cpp",
                    files=["third_party/thealgorithms-cpp/numerical_methods/rungekutta.cpp"])],
        pyref="external Python implementation third_party/thealgorithms-python/maths/numerical_analysis/runge_kutta.py",
    ),
    dict(
        program="betainc", c=3, l=3, src=2,
        category="special function with symmetry identity (map row 1)",
        primary_mp=1,
        instantiable={1: "symmetric reflection I_x(a,a) = 1 - I_{1-x}(a,a): y(x)+y(1-x)=1",
                      2: "CDF monotone increasing (Beta(2.5,2.5) distribution function)",
                      4: "S-shape envelope in [0,1]"},
        aux="a=b=2.5 frozen; program(x) = I_x(2.5, 2.5)",
        exception=None,
        pairs=[dict(pair="betainc.c", language="c", upstream="gsl", files=[]),
               dict(pair="betainc.cpp", language="cpp", upstream="boost",
                    files=["third_party/boost-math/include"]),
               dict(pair="betainc.java", language="java", upstream="cm",
                    files=["third_party/commons-math/commons-math3-3.6.1.jar"])],
        pyref="scipy.special.betainc",
    ),
    dict(
        program="erf", c=3, l=3, src=2,
        category="special function with symmetry identity (map row 1)",
        primary_mp=1,
        instantiable={1: "odd symmetry erf(-t)=-erf(t): y(x)+y(1-x)=0 with t=4x-2",
                      2: "monotone increasing",
                      4: "S-shape envelope |y|<1"},
        aux="t(x)=4x-2",
        exception=None,
        pairs=[dict(pair="erf.c", language="c", upstream="gsl", files=[]),
               dict(pair="erf.cpp", language="cpp", upstream="boost",
                    files=["third_party/boost-math/include"]),
               dict(pair="erf.java", language="java", upstream="cm",
                    files=["third_party/commons-math/commons-math3-3.6.1.jar"])],
        pyref="scipy.special.erf",
    ),
    dict(
        program="normcdf", c=3, l=3, src=2,
        category="special function with reflection identity (map row 1)",
        primary_mp=1,
        instantiable={1: "reflection Phi(-t)=1-Phi(t): y(x)+y(1-x)=1 with t=6x-3",
                      2: "monotone increasing (probabilistic CDF)",
                      4: "S-shape envelope in [0,1]"},
        aux="t(x)=6x-3, standard normal",
        exception=None,
        pairs=[dict(pair="normcdf.c", language="c", upstream="gsl", files=[]),
               dict(pair="normcdf.cpp", language="cpp", upstream="boost",
                    files=["third_party/boost-math/include"]),
               dict(pair="normcdf.java", language="java", upstream="cm",
                    files=["third_party/commons-math/commons-math3-3.6.1.jar"])],
        pyref="scipy.special.ndtr",
    ),
    dict(
        program="sigmoid", c=3, l=1, src=1,
        category="special function with symmetry identity (map row 1)",
        primary_mp=1,
        instantiable={1: "sigma(-t)=1-sigma(t): y(x)+y(1-x)=1 with t=8x-4",
                      2: "monotone increasing",
                      4: "S-shape envelope in (0,1)"},
        aux="t(x)=8x-4; external Rust side computes in float32 (E.powf), Python side float64: certification measures the precision gap against the standard gate",
        exception=None,
        pairs=[dict(pair="sigmoid.rs", language="rust", upstream="ta-rust",
                    files=["third_party/thealgorithms-rust/src/math/sigmoid.rs"])],
        pyref="external Python implementation third_party/thealgorithms-python/maths/sigmoid.py",
    ),
    dict(
        program="tanh", c=3, l=1, src=1,
        category="special function with symmetry identity (map row 1)",
        primary_mp=1,
        instantiable={1: "odd symmetry tanh(-t)=-tanh(t): y(x)+y(1-x)=0 with t=4x-2",
                      2: "monotone increasing",
                      4: "S-shape envelope |y|<1"},
        aux="t(x)=4x-2; external Rust side float32, Python side float64 (as sigmoid)",
        exception=None,
        pairs=[dict(pair="tanh.rs", language="rust", upstream="ta-rust",
                    files=["third_party/thealgorithms-rust/src/math/tanh.rs"])],
        pyref="external Python implementation third_party/thealgorithms-python/maths/tanh.py",
    ),
    dict(
        program="quad", c=3, l=1, src=2,
        category="adaptive quadrature with tolerance knob (map row 3)",
        primary_mp=3,
        instantiable={2: "monotone increasing (positive integrand)",
                      3: "adaptive mesh/tolerance structure (QUADPACK)",
                      4: "concave increasing shape envelope (arctan)"},
        aux="integrand 1/(1+u^2) frozen; interval [0, 4x]; epsabs=epsrel=1e-10 both sides; GSL_INTEG_GAUSS21 vs scipy QUADPACK qagse (21-point)",
        exception=dict(cls=1, tol=1e-6,
                       band="both sides integrate to epsabs=epsrel=1e-10; combined band ~4e-10, far inside the standard gate (recorded for transparency)"),
        pairs=[dict(pair="quad.c", language="c", upstream="gsl", files=[])],
        pyref="scipy.integrate.quad",
    ),
    dict(
        program="quantile", c=3, l=1, src=3,
        category="statistical estimator (map row 2)",
        primary_mp=2,
        instantiable={1: "symmetric-data reflection Q(1-p) = -Q(p) (frozen symmetric sample, median 0)",
                      2: "order-statistic estimator, monotone in p",
                      4: "monotone piecewise-linear shape envelope"},
        aux="frozen symmetric 21-point sample; Julia Statistics.quantile default (type-7 linear interpolation) vs numpy.quantile default (same type-7)",
        exception=None,
        pairs=[dict(pair="quantile.jl", language="julia", upstream="julia", files=[])],
        pyref="numpy.quantile",
    ),
    dict(
        program="besselj0", c=2, l=3, src=2,
        category="special function with symmetry identity (map row 1)",
        primary_mp=1,
        instantiable={1: "even symmetry J0(-t)=J0(t): y(x)=y(1-x) with t=8x-4",
                      4: "oscillatory envelope |J0|<=1"},
        aux="t(x)=8x-4 (negative arguments exercise the parity identity; library domain support measured at certification)",
        exception=None,
        pairs=[dict(pair="besselj0.c", language="c", upstream="gsl", files=[]),
               dict(pair="besselj0.cpp", language="cpp", upstream="boost",
                    files=["third_party/boost-math/include"]),
               dict(pair="besselj0.java", language="java", upstream="cm",
                    files=["third_party/commons-math/commons-math3-3.6.1.jar"])],
        pyref="scipy.special.j0",
    ),
    dict(
        program="digamma", c=2, l=3, src=2,
        category="trajectory/qualitative-shape kernel (map row 4; recurrence identity not expressible through constant-relation R)",
        primary_mp=4,
        instantiable={2: "monotone increasing on [1,5]",
                      4: "concave increasing shape envelope"},
        aux="t(x)=1+4x",
        exception=None,
        pairs=[dict(pair="digamma.c", language="c", upstream="gsl", files=[]),
               dict(pair="digamma.cpp", language="cpp", upstream="boost",
                    files=["third_party/boost-math/include"]),
               dict(pair="digamma.java", language="java", upstream="cm",
                    files=["third_party/commons-math/commons-math3-3.6.1.jar"])],
        pyref="scipy.special.psi",
    ),
    dict(
        program="gamma", c=2, l=3, src=2,
        category="trajectory/qualitative-shape kernel (map row 4; recurrence/reflection identities not expressible through constant-relation R on the frozen domain)",
        primary_mp=4,
        instantiable={2: "monotone increasing on [2,4]",
                      4: "convex increasing shape envelope"},
        aux="t(x)=2+2x",
        exception=None,
        pairs=[dict(pair="gamma.c", language="c", upstream="gsl", files=[]),
               dict(pair="gamma.cpp", language="cpp", upstream="boost",
                    files=["third_party/boost-math/include"]),
               dict(pair="gamma.java", language="java", upstream="cm",
                    files=["third_party/commons-math/commons-math3-3.6.1.jar"])],
        pyref="scipy.special.gamma",
    ),
    dict(
        program="gammainc", c=2, l=3, src=2,
        category="statistical estimator / probabilistic kernel (map row 2: regularized lower incomplete gamma = Gamma(2.5) CDF)",
        primary_mp=2,
        instantiable={2: "CDF monotone increasing",
                      4: "S-shape envelope in [0,1]"},
        aux="a=2.5 frozen; t(x)=8x",
        exception=None,
        pairs=[dict(pair="gammainc.c", language="c", upstream="gsl", files=[]),
               dict(pair="gammainc.cpp", language="cpp", upstream="boost",
                    files=["third_party/boost-math/include"]),
               dict(pair="gammainc.java", language="java", upstream="cm",
                    files=["third_party/commons-math/commons-math3-3.6.1.jar"])],
        pyref="scipy.special.gammainc",
    ),
    dict(
        program="expint", c=2, l=2, src=2,
        category="trajectory/qualitative-shape kernel (map row 4)",
        primary_mp=4,
        instantiable={2: "monotone decreasing on [0.1, 4]",
                      4: "convex decreasing shape envelope"},
        aux="t(x)=0.1+3.9x; E1",
        exception=None,
        pairs=[dict(pair="expint.c", language="c", upstream="gsl", files=[]),
               dict(pair="expint.cpp", language="cpp", upstream="boost",
                    files=["third_party/boost-math/include"])],
        pyref="scipy.special.exp1",
    ),
    dict(
        program="legendre", c=2, l=2, src=2,
        category="special function with symmetry identity (map row 1)",
        primary_mp=1,
        instantiable={1: "odd parity P3(-t)=-P3(t): y(x)+y(1-x)=0 with t=2x-1",
                      4: "envelope |P3|<=1 on [-1,1]"},
        aux="l=3 frozen; t(x)=2x-1",
        exception=None,
        pairs=[dict(pair="legendre.c", language="c", upstream="gsl", files=[]),
               dict(pair="legendre.cpp", language="cpp", upstream="boost",
                    files=["third_party/boost-math/include"])],
        pyref="scipy.special.eval_legendre",
    ),
    dict(
        program="zeta", c=2, l=2, src=2,
        category="trajectory/qualitative-shape kernel (map row 4)",
        primary_mp=4,
        instantiable={2: "monotone decreasing on [2,5]",
                      4: "convex decreasing envelope toward 1"},
        aux="s(x)=2+3x",
        exception=None,
        pairs=[dict(pair="zeta.c", language="c", upstream="gsl", files=[]),
               dict(pair="zeta.cpp", language="cpp", upstream="boost",
                    files=["third_party/boost-math/include"])],
        pyref="scipy.special.zeta",
    ),
    dict(
        program="sinc", c=2, l=1, src=3,
        category="special function with symmetry identity (map row 1)",
        primary_mp=1,
        instantiable={1: "even symmetry sinc(-t)=sinc(t): y(x)=y(1-x) with t=4x-2",
                      4: "oscillatory envelope |sinc|<=1"},
        aux="normalized sinc; t(x)=4x-2 (Julia Base.sinc and numpy.sinc share the normalized convention)",
        exception=None,
        pairs=[dict(pair="sinc.jl", language="julia", upstream="julia", files=[])],
        pyref="numpy.sinc",
    ),
]

# Step-3 screening audit: every enumerated candidate rejected pre-behaviorally.
SCREENED = [
    dict(candidate="bisection (TheAlgorithms C bisection_method.c + Python bisection.py)", src=1,
         reason="C entry hardcodes f(t)=t^3+2t-10, so any adapter mapping leaves program(x) constant in x (zero instantiable strata); Python side takes f as an argument and cannot be matched by the C side",
         clause="S2b Step 3 criterion 3 (single-entry numeric interface on [0,1])"),
    dict(candidate="bisection (TheAlgorithms C-Plus-Plus bisection_method.cpp)", src=1,
         reason="all logic inside main() with auto-expanding interval; no callable entry point",
         clause="S2b Step 3 criterion 3"),
    dict(candidate="newtonraphson (TheAlgorithms C newton_raphson_root.c)", src=1,
         reason="initial guess drawn from rand() seeded with wall-clock time inside main(); not deterministic, seed not injectable",
         clause="S2b Step 3 criterion 2 (deterministic or seedable RNG)"),
    dict(candidate="newtonraphson (TheAlgorithms C-Plus-Plus newton_raphson_method.cpp)", src=1,
         reason="std::srand(std::time(nullptr)) random initial approximation inside main(); not seedable",
         clause="S2b Step 3 criterion 2"),
    dict(candidate="secant (TheAlgorithms C secant_method.c / Python secant_method.py)", src=1,
         reason="both sides hardcode DIFFERENT target functions (C: t^2-3; Python: 8t-2e^-t); no same-semantics Python-side reference; the converged C output is additionally constant in x",
         clause="S2b Step 3 criteria 3 and 4"),
    dict(candidate="simpson (TheAlgorithms C simpsons_1_3rd_rule.c)", src=1,
         reason="hardcoded integrand 1+u^3 differs from the Python-side implementation's hardcoded u^2; single-precision float; stdin-interactive main",
         clause="S2b Step 3 criterion 4 (same-semantics Python-side reference)"),
    dict(candidate="simpson (TheAlgorithms Java SimpsonIntegration.java)", src=1,
         reason="hardcoded integrand e^-u(4-u^2) differs from the Python-side implementation's hardcoded u^2",
         clause="S2b Step 3 criterion 4"),
    dict(candidate="euler (TheAlgorithms C/C-Plus-Plus ode_forward_euler.c/.cpp)", src=1,
         reason="hardcoded two-component harmonic-oscillator system; the external Python explicit_euler is scalar-only, so no same-semantics Python-side reference exists",
         clause="S2b Step 3 criterion 4"),
    dict(candidate="invsqrt (TheAlgorithms Java FastInverseSqrt.java)", src=1,
         reason="entry points return boolean (comparison against 1/Math.sqrt), not the numeric value",
         clause="S2b Step 3 criterion 3"),
    dict(candidate="mcpi (TheAlgorithms Go montecarlopi.go + Python pi_monte_carlo_estimation.py)", src=1,
         reason="Go side seeds math/rand from time.Now().UnixNano() inside the function; RNG not injectable, and the S2c RNG-stream reproduction precondition is structurally unsatisfiable; with the Go pair gone the Python program has no external non-Python implementation",
         clause="S2b Step 3 criterion 2 (Go side); criterion 4 (program)"),
    dict(candidate="sin (TheAlgorithms Go math/sin.go + Python maths/sin.py)", src=1,
         reason="Python side is degrees-based with angle folding; Go side is radians Taylor; different semantics",
         clause="S2b Step 3 criterion 4"),
    dict(candidate="softmax (TheAlgorithms Python + Rust)", src=1,
         reason="vector-in/vector-out semantics; scalar freezing degenerates it to a sigmoid variant; not a scalar single-entry kernel",
         clause="S2b Step 3 criterion 3"),
    dict(candidate="rungekutta variants (Python runge_kutta_gills / fehlberg_45)", src=1,
         reason="no same-named cross-language counterpart in the registered repos (l=0)",
         clause="S2b Step 3 criterion 4"),
    dict(candidate="cubic-spline interpolation (GSL gsl_spline vs scipy interp1d/CubicSpline)", src=2,
         reason="boundary-condition semantics differ (GSL natural vs scipy not-a-knot defaults); no documented same-semantics reference at the registered tolerance",
         clause="S2b Step 3 criterion 4"),
    dict(candidate="adaptive ODE (GSL gsl_odeiv2 rkf45 vs scipy solve_ivp RK45)", src=2,
         reason="method heterogeneity (Fehlberg 4(5) vs Dormand-Prince 5(4)) with controller-dependent step selection; agreement is solver-band-limited with no documented shared band; MP3 coverage already supplied by brent/quad/euler/rungekutta",
         clause="S2b Step 3 criterion 4 (documented-reference requirement)"),
    dict(candidate="Julia SciML packages (source 3, SciML half)", src=3,
         reason="external package installation (Pkg + artifact downloads) unavailable in the sandboxed execution environment; only Julia STDLIB entry points were enumerable (quantile, sinc). Disclosed as a source-3 coverage limitation, not a criteria change",
         clause="S2b Step 2 sweep-shortfall disclosure (Step 5)"),
]

RANK_RULE = "c desc, l desc, source-list index asc, program name asc (ASCII)"
N_FLOOR = 12
N_TARGET = 20
N_CAP = 28
GRID_N = 201
TOL_DEFAULT = 1e-6


def rank_check() -> bool:
    """Verify CANDIDATES is stored in the registered Step-4 total order."""
    keys = [(-e["c"], -e["l"], e["src"], e["program"]) for e in CANDIDATES]
    return keys == sorted(keys)


# =========================================================================== #
# Amendment A3 — Family-XL roster EXTENSION wave (scale diversity),
# author-directed, pre-mutant. PREREGISTRATION_STUDY5_v1.md §10 entry
# "Amendment A3"; audit trail: docs/prereg_v2/STUDY5_XL_ROSTER.md §A3.
#
# Author directive (recorded verbatim in the amendment): the A1 roster is
# source-diverse but SCALE-homogeneous (21/21 function-level routines) and
# primary-stratum-skewed (MP1 13, MP3 6, MP2 1, MP5 1). This wave adds
# module/pipeline-scale production-library pairs under the standing
# principles P1 (no self-written PUT code) and P2 (purpose + family first,
# then diversity), prioritised to (a) module scale and (b) MP2/MP5
# primary-coverage repair. Registered cap n <= 28 total is respected:
# A3 new-pair budget = N_CAP - 21 = 7.
#
# Everything in this block is fixed BEFORE the A3 certification run; no
# entry consults any behavioral quantity. A1 CANDIDATES/SCREENED above are
# byte-unchanged.
# =========================================================================== #

A3_SCALE_RULE = (
    "A3-1 (module-scale admission criterion, pre-behavioral): the pair's "
    "call path must traverse a multi-component library SUBSYSTEM — a state "
    "object plus a staged pipeline (alloc/init/accumulate/solve/eval) or an "
    "adaptive driver chain — i.e. a documented library module with a "
    "multi-hundred-LOC call path, not a single closed-form routine. "
    "Single-pass closed-form entry points (the structural class of every A1 "
    "pair, e.g. gsl_stats_*, Julia Statistics.std, 1-D gsl_min iterate "
    "loops) are OUT OF SCOPE for this wave."
)

A3_GROUP_RULE = (
    "A3 walk order (P2, family-repair first; deterministic): group (i) = "
    "candidates whose registered primary stratum is MP2 (f_mono.stat) or "
    "MP5 (f_conv.rate) — the author-identified under-covered strata — in "
    "the registered Step-4 total order; then group (ii) = all remaining "
    "candidates in Step-4 order. The Step-4 key (c desc, l desc, src asc, "
    "name asc) is unchanged inside each group; a pure ungrouped Step-4 walk "
    "would spend the whole 7-pair budget on MP3-primary ODE modules and "
    "repair nothing, violating the author directive."
)

A3_NEW_PAIR_BUDGET = 7   # = N_CAP - achieved A1 n (21); cap 28 respected
A1_SCALE = "function"    # author-review classification of every A1 pair
A3_SCALE = "module"

# l convention for A3 (documented): l counts non-Python languages with a
# same-semantics MODULE-SCALE external implementation (A3-1 applies to the
# enumeration itself); function-scale implementations of the same semantics
# exist for some candidates (e.g. gsl_stats_sd for descstats) but are not
# A3-enumerable and do not count toward this wave's l.
A3_CANDIDATES = [
    # ------------------------- group (i): MP2/MP5 repair ------------------ #
    dict(
        program="interp", c=4, l=2, src=2, group=1,
        category="surrogate/fidelity-ordered kernel: piecewise-linear "
                 "interpolant surrogate of an exactly-known target sampled "
                 "at frozen nodes (map row 5; invsqrt precedent — not a "
                 "solver, so map row 3's enumerated list does not match)",
        primary_mp=5,
        scale=A3_SCALE,
        scale_evidence="GSL interpolation module (gsl_interp type object + "
                       "accelerator + gsl_spline wrapper: interp.c/linear.c/"
                       "accel.c/spline.c pipeline); Commons Math "
                       "analysis.interpolation.LinearInterpolator -> "
                       "PolynomialSplineFunction -> PolynomialFunction chain",
        instantiable={2: "piecewise-linear interpolant of strictly "
                         "increasing samples is strictly increasing (exact)",
                      3: "node-refinement structure (17-node mesh; "
                         "interpolant -> target as mesh -> 0)",
                      4: "convex increasing envelope (chords of the convex "
                         "target lie above it)",
                      5: "surrogate-vs-target: target exp known exactly "
                         "(Mode-M relative oracle; fidelity ordered by node "
                         "count)"},
        aux="nodes t_j = j/16, j=0..16; samples exp(t_j); linear "
            "interpolation; program(x) = interpolant(x), x in [0,1]",
        exception=None,
        pairs=[dict(pair="interp.c", language="c", upstream="gsl", files=[]),
               dict(pair="interp.java", language="java", upstream="cm",
                    files=["third_party/commons-math/commons-math3-3.6.1.jar"])],
        pyref="scipy.interpolate.interp1d(kind='linear')",
    ),
    dict(
        program="chebyshev", c=4, l=1, src=2, group=1,
        category="surrogate/fidelity-ordered kernel: order-12 Chebyshev "
                 "approximant of an exactly-known target (map row 5; "
                 "invsqrt precedent)",
        primary_mp=5,
        scale=A3_SCALE,
        scale_evidence="GSL chebyshev module (gsl_cheb_series state + "
                       "init-at-nodes + Clenshaw evaluation pipeline)",
        instantiable={2: "approximant of the strictly monotone target exp "
                         "(order-12 error << separation on the frozen grid; "
                         "monotone envelope per the invsqrt precedent)",
                      3: "order-refinement structure (approximant -> target "
                         "as order -> infinity)",
                      4: "convex increasing envelope",
                      5: "surrogate with analytically known target exp "
                         "(Mode-M; fidelity ordered by series order)"},
        aux="target f(t)=exp(t) frozen on [-1,1]; series order 12 (13 "
            "first-kind Chebyshev nodes); program(x) = series(2x-1)",
        exception=None,
        pairs=[dict(pair="chebyshev.c", language="c", upstream="gsl", files=[])],
        pyref="numpy.polynomial.chebyshev.chebinterpolate(deg=12) + chebval",
    ),
    dict(
        program="hermite", c=4, l=1, src=5, group=1,
        category="surrogate/fidelity-ordered kernel: piecewise cubic "
                 "Hermite interpolant surrogate of an exactly-known target "
                 "with exact frozen derivatives (map row 5)",
        primary_mp=5,
        scale=A3_SCALE,
        scale_evidence="Boost.Math interpolators module "
                       "(boost::math::interpolators::cubic_hermite + "
                       "detail::cubic_hermite_detail pipeline)",
        instantiable={2: "Hermite interpolant of increasing data with the "
                         "exact positive derivatives (monotone envelope)",
                      3: "node-refinement structure (O(h^4) convergence to "
                         "the target as the mesh refines)",
                      4: "convex increasing envelope",
                      5: "surrogate-vs-target with known exact target and "
                         "O(h^4) fidelity order (Mode-M)"},
        aux="nodes t_j = j/16, j=0..16; values exp(t_j); derivatives "
            "exp(t_j) (exact, frozen); program(x) = H(x)",
        exception=None,
        pairs=[dict(pair="hermite.cpp", language="cpp", upstream="boost",
                    files=["third_party/boost-math/include"])],
        pyref="scipy.interpolate.CubicHermiteSpline",
    ),
    dict(
        program="histstats", c=3, l=1, src=2, group=1,
        category="statistical estimator / probabilistic kernel: binned-"
                 "histogram mean estimator over a frozen deterministic "
                 "sample stream (map row 2)",
        primary_mp=2,
        scale=A3_SCALE,
        scale_evidence="GSL histogram module pipeline: gsl_histogram_alloc "
                       "-> set_ranges_uniform -> 512x increment (binning) "
                       "-> gsl_histogram_mean (bin-midpoint statistics over "
                       "the accumulated state)",
        instantiable={2: "binned mean of the power-transformed sample is "
                         "monotone decreasing in x (mass shifts toward 0 as "
                         "the exponent grows)",
                      3: "bin-refinement structure (32-bin mesh; binned "
                         "mean -> sample mean as bins -> infinity)",
                      4: "monotone decreasing envelope"},
        aux="u_i = frac(i*PHI), PHI=1.6180339887498949 (double literal, "
            "identical both sides), i=1..512; s_i = u_i**(1+2x) in (0,1); "
            "32 uniform bins on [0,1); readout = binned mean "
            "sum(n_k m_k)/N with m_k = bin midpoints (the documented "
            "gsl_histogram_mean formula)",
        exception=None,
        pairs=[dict(pair="histstats.c", language="c", upstream="gsl", files=[])],
        pyref="numpy.histogram(bins=32, range=(0,1)) + midpoint mean "
              "(the same documented binned-mean formula)",
    ),
    dict(
        program="descstats", c=3, l=1, src=4, group=1,
        category="statistical estimator / probabilistic kernel: bias-"
                 "corrected sample-dispersion estimator over a frozen "
                 "scale-parameterised dataset (map row 2; quantile "
                 "precedent — an MP1-instantiable identity does not move an "
                 "estimator out of row 2)",
        primary_mp=2,
        scale=A3_SCALE,
        scale_evidence="Commons Math stat.descriptive pipeline: "
                       "DescriptiveStatistics (windowed storage) -> "
                       "Variance -> Mean -> FirstMoment/SecondMoment "
                       "statistic-object delegation chain",
        instantiable={1: "exact scale equivariance SD(c + w*u) = w*SD(u) "
                         "with w(x)*w(1-x) = 0.16: product identity "
                         "y(x)*y(1-x) = (0.4*SD(u))^2 (exact in real "
                         "arithmetic)",
                      2: "dispersion estimator monotone increasing in x "
                         "(w(x) = 0.4*2**(2x-1) increasing)",
                      4: "log-linear (exponential) envelope"},
        aux="u_i = frac(i*PHI), PHI=1.6180339887498949, i=1..256; "
            "s_i = 0.5 + (u_i - 0.5)*w(x), w(x) = 0.4*2**(2x-1); readout = "
            "bias-corrected sample standard deviation (ddof=1)",
        exception=None,
        pairs=[dict(pair="descstats.java", language="java", upstream="cm",
                    files=["third_party/commons-math/commons-math3-3.6.1.jar"])],
        pyref="numpy.std(ddof=1)",
    ),
    dict(
        program="polyfit", c=2, l=2, src=2, group=1,
        category="surrogate/fidelity-ordered kernel: least-squares cubic "
                 "fit surrogate of an exactly-known target (map row 5)",
        primary_mp=5,
        scale=A3_SCALE,
        scale_evidence="GSL multifit module (gsl_multifit_linear_workspace "
                       "+ balanced-SVD least-squares pipeline); Commons "
                       "Math fitting module (PolynomialCurveFitter -> "
                       "Levenberg-Marquardt optimizer chain)",
        instantiable={4: "convex increasing envelope (LS cubic of convex "
                         "increasing data; approximate, envelope MR)",
                      5: "surrogate-vs-target: d_j = exp(a(x) t_j) known "
                         "exactly; fidelity ordered by fit degree (Mode-M)"},
        aux="nodes t_j = j/32, j=0..32; data d_j(x) = exp((0.5+x)*t_j); "
            "least-squares cubic fit; readout = fitted value at t=0.6. "
            "The LS solution is unique (full-rank Vandermonde); "
            "implementation differences are conditioning-level rounding "
            "(kappa ~ 1e3 -> ~1e-13), inside the standard gate",
        exception=None,
        pairs=[dict(pair="polyfit.c", language="c", upstream="gsl", files=[]),
               dict(pair="polyfit.java", language="java", upstream="cm",
                    files=["third_party/commons-math/commons-math3-3.6.1.jar"])],
        pyref="numpy.polyfit(deg=3) + polyval",
    ),
    # ------------------------- group (ii): remaining ---------------------- #
    dict(
        program="odedrive", c=4, l=2, src=2, group=2,
        category="discretised/iterative solver with a tolerance knob: full "
                 "adaptive ODE drive (map row 3; no conserved quantity in "
                 "the frozen logistic system)",
        primary_mp=3,
        scale=A3_SCALE,
        scale_evidence="GSL odeiv2 module (driver -> control -> evolve -> "
                       "rkf45 stepper chain); Commons Math ode.nonstiff "
                       "module (DormandPrince54Integrator -> "
                       "EmbeddedRungeKuttaIntegrator -> AbstractIntegrator "
                       "+ step handlers)",
        instantiable={2: "monotone in initial condition (logistic flow "
                         "order-preserving)",
                      3: "adaptive step/tolerance knob (limit tol -> 0)",
                      4: "S-curve trajectory shape",
                      5: "surrogate with known exact logistic solution"},
        aux="dy/dt = y(1-y) frozen; y0(x) = 0.05+0.9x; t: 0 -> 1; "
            "epsrel=1e-10, epsabs=1e-12 both sides; readout y(1). "
            "A3 re-pose of the A1-screened adaptive-ODE candidate: the A1 "
            "screen cited an undocumentable band at DEFAULT tolerances; at "
            "the frozen 1e-10/1e-12 tolerances the class-1 band IS "
            "documentable (see exception); disclosed as A3-D2, not a "
            "silent reversal",
        exception=dict(cls=1, tol=1e-6,
                       band="both drivers hold local error <= "
                            "rel 1e-10 / abs 1e-12; the frozen logistic "
                            "problem takes O(30-60) accepted steps on "
                            "[0,1], so each side's global band is <~1e-8 "
                            "and the cross-method band <~2e-8, far inside "
                            "the standard 1e-6 gate (no relaxation "
                            "needed; recorded for transparency)"),
        pairs=[dict(pair="odedrive.c", language="c", upstream="gsl", files=[]),
               dict(pair="odedrive.java", language="java", upstream="cm",
                    files=["third_party/commons-math/commons-math3-3.6.1.jar"])],
        pyref="scipy.integrate.solve_ivp(method='RK45', rtol=1e-10, "
              "atol=1e-12)",
    ),
    dict(
        program="rungekutta", c=4, l=1, src=1, group=2,
        category="fixed-step ODE solver (map row 3) — A3 module-scale "
                 "EXTENSION of the A1 program 'rungekutta' (aux verbatim); "
                 "fixed-budget high-order member of the euler-vs-rk4 "
                 "accuracy-order pair (A3-D3 note as for euler)",
        primary_mp=3,
        scale=A3_SCALE,
        scale_evidence="Commons Math ode.nonstiff module "
                       "(ClassicalRungeKuttaIntegrator -> "
                       "RungeKuttaIntegrator -> AbstractIntegrator chain)",
        instantiable={2: "monotone in initial condition (linear ODE flow)",
                      3: "step-size discretisation structure (h=1/64)",
                      4: "trajectory/shape kernel (relaxation toward the "
                         "t-2 asymptote)",
                      5: "surrogate with known exact solution "
                         "y = t-2+(y0+2)exp(-t/2)"},
        aux="A1 aux verbatim: dy/dt = (t-y)/2; y0(x)=x; t in [0,2]; h=1/64 "
            "(exactly 128 fixed steps)",
        exception=None,
        pairs=[dict(pair="rungekutta.java", language="java", upstream="cm",
                    files=["third_party/commons-math/commons-math3-3.6.1.jar"])],
        pyref="external Python implementation third_party/"
              "thealgorithms-python/maths/numerical_analysis/runge_kutta.py "
              "(A1 pyref, unchanged)",
    ),
    dict(
        program="multimin", c=3, l=1, src=2, group=2,
        category="iterative solver with a tolerance knob: derivative-free "
                 "multidimensional minimiser, converged objective readout "
                 "(map row 3)",
        primary_mp=3,
        scale=A3_SCALE,
        scale_evidence="GSL multimin module (gsl_multimin_fminimizer_"
                       "nmsimplex2 simplex state machine + size-test "
                       "iteration driver)",
        instantiable={2: "converged objective a(1 - ln a) + const is "
                         "strictly decreasing for a > 1 (a(x)=exp(x+0.1) "
                         "increasing): monotone in x",
                      3: "iterative simplex solver with size-tolerance knob",
                      4: "concave decreasing envelope (d2/da2 = -1/a < 0)"},
        aux="F(u,v) = exp(u) - a*u + (v-0.7)^2, a(x) = exp(x+0.1); start "
            "(0,0), initial step (0.5,0.5); stop at simplex size < 1e-12 "
            "(<= 100000 iterations); readout = converged objective value. "
            "Python side: scipy Nelder-Mead, xatol=1e-12, fatol=1e-13",
        exception=dict(cls=1, tol=1e-6,
                       band="smooth strictly convex objective; simplex-size "
                            "1e-12 / fatol 1e-13 stopping rules bound the "
                            "converged-objective error by ~1e-12 per side; "
                            "combined band ~1e-12, far inside the standard "
                            "gate (no relaxation needed; recorded)"),
        pairs=[dict(pair="multimin.c", language="c", upstream="gsl", files=[])],
        pyref="scipy.optimize.minimize(method='Nelder-Mead')",
    ),
    dict(
        program="multiroot", c=3, l=1, src=2, group=2,
        category="iterative solver with a tolerance knob: coupled 2-D "
                 "root-finder, root-component readout (map row 3)",
        primary_mp=3,
        scale=A3_SCALE,
        scale_evidence="GSL multiroots module (gsl_multiroot_fsolver_"
                       "hybrids: scaled HYBRD trust-region machinery)",
        instantiable={2: "root component u increasing in r(x) (implicit-"
                         "function argument on the circle-line system)",
                      3: "iterative solver with residual-tolerance knob",
                      4: "monotone envelope"},
        aux="f1 = u^2+v^2-r(x)^2, f2 = u-v-0.3, r(x)=1+x/2; start "
            "(1.0, 0.5); stop at |f| residual < 1e-12; readout = u. Python "
            "side: scipy.optimize.root(method='hybr', tol=1e-12) (both "
            "sides are MINPACK-HYBRD-derived)",
        exception=dict(cls=1, tol=1e-6,
                       band="residual 1e-12 with O(1) Jacobian singular "
                            "values on the frozen branch -> root band "
                            "~1e-12 per side; combined ~1e-11, inside the "
                            "standard gate (recorded)"),
        pairs=[dict(pair="multiroot.c", language="c", upstream="gsl", files=[])],
        pyref="scipy.optimize.root(method='hybr')",
    ),
    dict(
        program="quad", c=3, l=1, src=2, group=2,
        category="adaptive quadrature with tolerance knob (map row 3) — A3 "
                 "module-scale EXTENSION of the A1 program 'quad' (aux "
                 "verbatim)",
        primary_mp=3,
        scale=A3_SCALE,
        scale_evidence="Boost.Math quadrature module (gauss_kronrod<double,"
                       "21> adaptive subdivision machinery)",
        instantiable={2: "monotone increasing (positive integrand)",
                      3: "adaptive mesh/tolerance structure",
                      4: "concave increasing envelope (arctan)"},
        aux="A1 aux verbatim: integrand 1/(1+u^2); interval [0, 4x]; "
            "adaptive to tol 1e-10 (boost gauss_kronrod max_depth 15, "
            "tol 1e-10 vs scipy QUADPACK epsabs=epsrel=1e-10)",
        exception=dict(cls=1, tol=1e-6,
                       band="both sides integrate the smooth frozen "
                            "integrand to ~1e-10; combined band ~4e-10, "
                            "far inside the standard gate (A1 quad "
                            "precedent; recorded)"),
        pairs=[dict(pair="quad.cpp", language="cpp", upstream="boost",
                    files=["third_party/boost-math/include"])],
        pyref="scipy.integrate.quad (A1 pyref, unchanged)",
    ),
    dict(
        program="fft", c=2, l=2, src=2, group=2,
        category="trajectory/qualitative-shape kernel (map row 4; the "
                 "DFT's Parseval/unitarity invariances are not expressible "
                 "through a constant-relation R on the frozen scalar "
                 "readout — digamma precedent)",
        primary_mp=4,
        scale=A3_SCALE,
        scale_evidence="GSL fft module (gsl_fft_real_radix2 butterfly "
                       "machinery); Commons Math transform module "
                       "(FastFourierTransformer)",
        instantiable={2: "|S_4|^2 of the centered Gaussian pulse strictly "
                         "decreasing in the time-width w(x)=3+9x "
                         "(frequency width inverse to time width)",
                      4: "monotone decreasing envelope"},
        aux="N=64 real signal s_k = exp(-((k-32)/w(x))^2), w(x)=3+9x; "
            "forward DFT, standard normalization; registered scalar "
            "spectral statistic: readout = |S_4|^2 (frozen bin 4)",
        exception=None,
        pairs=[dict(pair="fft.c", language="c", upstream="gsl", files=[]),
               dict(pair="fft.java", language="java", upstream="cm",
                    files=["third_party/commons-math/commons-math3-3.6.1.jar"])],
        pyref="numpy.fft.fft + |S[4]|^2",
    ),
]

# A3 Step-3 screening audit (pre-behavioral, criterion cited).
A3_SCREENED = [
    dict(candidate="CM Percentile (R_7) as pair quantile.java for the A1 program 'quantile'", src=4,
         reason="Commons Math Percentile.evaluate documents p in (0, 100]: "
                "the frozen A1 program domain includes p = x = 0, which the "
                "entry rejects by contract (documented pre-behaviorally; "
                "besselj0.java lesson applied at screening time instead of "
                "burning a one-shot certification)",
         clause="S2b Step 3 criterion 3 (single-entry interface must cover "
                "x in [0,1])"),
    dict(candidate="GSL odeiv2 explicit-Euler fixed-step drive as pair euler.c for the A1 program 'euler'", src=2,
         reason="GSL odeiv2 ships NO explicit-Euler stepper (stepper set: "
                "rk2/rk4/rkf45/rkck/rk8pd/rk1imp/rk2imp/rk4imp/bsimp/"
                "msadams/msbdf; rk1imp is IMPLICIT Euler, different "
                "semantics), so no same-semantics module-scale external "
                "implementation of the frozen A1 'euler' aux exists; "
                "discovered at shim-authoring (API availability, "
                "pre-behavioral, before the one-shot gate run)",
         clause="S2b Step 3 criterion 4 (same-semantics external "
                "implementation)"),
    dict(candidate="GSL gsl_min 1-D Brent minimiser", src=2,
         reason="single iterate-loop state machine, the structural class of "
                "A1 brent.c (function-level)",
         clause="A3-1 scale criterion"),
    dict(candidate="GSL gsl_stats_* / Julia Statistics.std / Boost.Math "
                   "univariate statistics (as descstats-semantics "
                   "implementations)", src=2,
         reason="single-pass closed-form routines; not module-scale; they "
                "therefore do not contribute pairs or count toward this "
                "wave's l",
         clause="A3-1 scale criterion"),
    dict(candidate="CM SimpleRegression", src=4,
         reason="single streaming accumulator with closed-form slope "
                "readout; no staged pipeline or driver",
         clause="A3-1 scale criterion"),
    dict(candidate="CM EmpiricalDistribution", src=4,
         reason="cumulativeProbability has no documented numpy/scipy "
                "same-semantics counterpart (within-bin kernel smoothing); "
                "the mean readout bypasses the binning module entirely",
         clause="S2b Step 3 criterion 4 + A3-1"),
    dict(candidate="GSL bspline / Boost cardinal_cubic_b_spline vs scipy "
                   "make_lsq_spline/BSpline", src=2,
         reason="knot construction and boundary-condition semantics are not "
                "documented-identical across the implementations (the A1 "
                "cubic-spline lesson at module scale)",
         clause="S2b Step 3 criterion 4"),
    dict(candidate="GSL monte (plain/miser/vegas) vs scipy/numpy MC", src=2,
         reason="RNG-stream-dependent; no identical generator algorithm + "
                "seed stream exists across GSL and numpy, so the S2c "
                "class-2 reproduction precondition is structurally "
                "unsatisfiable",
         clause="S2b Step 3 criterion 2 / S2c class 2"),
    dict(candidate="GSL siman (simulated annealing)", src=2,
         reason="RNG-stream-dependent (as monte)",
         clause="S2b Step 3 criterion 2"),
    dict(candidate="GSL wavelet", src=2,
         reason="no counterpart inside the registered Python-side reference "
                "set (scipy/numpy ship no discrete wavelet transform; "
                "PyWavelets is outside the registered references)",
         clause="S2b Step 3 criterion 4"),
    dict(candidate="GSL linalg / eigen (matrix decompositions)", src=2,
         reason="matrix-in/matrix-out interfaces; any scalar freeze reduces "
                "to a single decomposition readout without a registered "
                "scalar-program convention on [0,1]",
         clause="S2b Step 3 criterion 3"),
    dict(candidate="TheAlgorithms/{Python,C,C-Plus-Plus,Java,Go,Rust} "
                   "(source 1, module-scale sweep)", src=1,
         reason="single-file teaching implementations throughout; the "
                "sweep found no multi-component numeric pipeline satisfying "
                "A3-1 (structural finding, not a per-file rejection)",
         clause="A3-1 scale criterion (sweep finding)"),
    dict(candidate="Julia stdlib module-scale numerics / SciML "
                   "OrdinaryDiffEq (source 3)", src=3,
         reason="Julia stdlib exposes no module-scale numeric pipeline "
                "with a documented scipy-equivalent contract; the SciML "
                "half remains non-enumerable (Pkg installation infeasible, "
                "A1 D2 carried forward)",
         clause="A3-1 + S2b Step 2 sweep-shortfall disclosure"),
]


def a3_rank_check() -> bool:
    """Verify A3_CANDIDATES is stored in the registered A3 walk order:
    group asc (repair-first), then the Step-4 key inside each group."""
    keys = [(e["group"], -e["c"], -e["l"], e["src"], e["program"])
            for e in A3_CANDIDATES]
    return keys == sorted(keys)
