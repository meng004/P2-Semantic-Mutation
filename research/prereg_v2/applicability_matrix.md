# Applicability Matrix — 5 Operators × 4 PUT Classes (broadcast to 60 PUT-level cells)

**Prereg component:** Task 1.1 (argumentation-uplift Phase 1)  
**Date:** 2026-07-28  
**Content hash (SHA-256, scope = everything after the first standalone HASH-SCOPE-START marker line; Amendment #1 repaired the original self-referential recipe, rulings untouched):** `670e5748437e409e03bd36a202273b9a428112c3e1433aa8fc386c3a87e85b2f`  
**Operative integrity control:** file-level hash in `research/prereg_v2/FREEZE_MANIFEST.sha256` + git history.  
**Status:** two-rater merge complete; **author ratification pending at REVIEW CHECKPOINT 1**; inclusion in `FREEZE_MANIFEST` deferred to Task 1.3 (blocked on theory CHECKPOINT T2)

**Raters (identity categories per protocol):**
- Rater A: lead analyst model instance (`claude-fable-5` session executing Phase 1); judged from operator design definitions (TOSEM main.tex §Layer-1 + operator-signature table), PUT source code, and v4 development data.
- Rater B: independent cross-family model instance (`gpt-5.6-sol-xhigh` subagent, plan's audit-family stand-in for `gpt-5.6-terra-max`, unavailable in this environment); same inputs, no access to Rater A's ruling.
- Arbitration: Rater A, evidence-grounded (see §4); flagged cells carry `ARBITRATED-BORDERLINE` for author review.

<!-- HASH-SCOPE-START -->

## 1. Ruling rules and result coding

1. **Applicability criterion (mechanistic):** a cell (operator × PUT) is `applicable` iff an editable **wrapper-level** code site exists in the PUT source through which the operator's edit mechanism can plausibly induce its target failure semantics. Library internals (scipy/sklearn implementations) are not editable sites. Generation success in v4 is corroboration, never the criterion; generation absence is never proof of inapplicability.
2. **Denominator rule:** `inapplicable` cells do not enter the H-CONS denominator and do not enter H-DISC comparisons.
3. **Result coding (distinct zeros):** theory-predicted zero on an applicable cell = `PRED_ZERO_ALIGN` (enters H-ZERO as a prediction); inapplicable cell = `NOT_APPLICABLE` (excluded from all confirmatory denominators).
4. **Runtime recoding rule (F-5a):** only a *manually confirmed structural absence of the code site* may be recoded to `NOT_APPLICABLE` before unblinding, with a logged entry. Generator engineering failures (site present, tool failed) stay in the funnel as attrition and must **not** be recoded (prevents H-CONS denominator manipulation). No recoding after unblinding.
5. **Operator identity (paper-authoritative):** CE=mut_C Conservation Erosion→MP1; OS=mut_M Operator Substitution→MP2; HP=mut_G Hyperparameter→MP3; TF=mut_T Trajectory Flip→MP4; SI=mut_F Structural Injection→MP5. Legacy code `CF` (b2-only, n=2 in v4) is outside this 5-operator matrix and carries no denominators.

## 2. Class-level matrix (20 cells, merged ruling)

| Operator | A (KER-NUM) | B (KER-STAT) | C (KER-SCIML) | D (KER-MLC) |
|---|---|---|---|---|
| **CE** | **applicable** — dynamical/algebraic conservation sites (RHS drift, det identity, stencil/BC) | **applicable** — normalisation/detailed-balance/linearity sites | **applicable** — kernel PSD diagonal, target-symmetry, sigmoid-normalisation sites | **inapplicable** — probability normalisation is library-internal; wrapper exposes no conserved-quantity site |
| **OS** | **applicable** — arithmetic/API substitution sites in RHS, det map, stencil | **applicable** — posterior arithmetic, acceptance comparison, integrand arithmetic | **applicable** — input maps, target functions, kernel/feature operators | **applicable** — label rules, feature construction, decision comparisons |
| **HP** | **applicable** — solver tolerances (a1), stability ratio/step (a3); a2 is a within-class exception | **applicable** — prior strength, chain controls, sample count | **applicable** — noise_level/length_scale, degree, training limits | **applicable** — architecture, max_iter, C/gamma, regularisation |
| **TF** | **applicable** — state ordering (a1), time-step loop (a3); a2 exception | **applicable** — MH chain segments (b2); b1/b3 exceptions | **applicable** — training-coordinate/target sequence alignment | **applicable** — periodic masking of training rows / query path |
| **SI** | **applicable** — solver-order, pivoting, stencil-order fidelity tiers | **applicable** — aggregation-structure tier (b3, AM→GM); b1/b2 exceptions | **applicable** — prior-scale, degree, architecture tiers | **applicable** — architecture, kernel, regularisation tiers |

Class-level `applicable` = at least one member PUT carries the site; member exceptions are enforced at PUT level (§3) per the broadcast-then-verify rule (F-5).

## 3. PUT-level site verification (60 cells; `✓` = site present, `✗` = NOT_APPLICABLE)

| Op | a1 Lorenz | a2 LU | a3 FDM | b1 BetaBin | b2 MH | b3 MC | c1 GPR | c2 PCE | c3 NN | d1 MLP | d2 SVM | d3 LogReg |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **CE** | ✓ RHS drift / IC map | ✓ det construction + diag product | ✓ stencil update + BC rows | ✓ posterior normalising denominator | ✓ acceptance log-ratio (detailed balance) | ✓ integrand linearity (∫(x+c)−∫x=c) | ✓ WhiteKernel PSD diagonal | ✓ target odd-symmetry construction (`_y_train=tanh`) — **ARBITRATED-BORDERLINE** | ✓ sigmoid target denominator | ✗ normalisation library-internal (class) | ✗ same (class) | ✗ same (class) |
| **OS** | ✓ RHS arithmetic signs | ✓ matrix map `2+x` | ✓ stencil `+`/`−` | ✓ posterior update arithmetic | ✓ acceptance `min(1,r)` comparison | ✓ integrand `x + t²` | ✓ input map `6x−3`, kernel `+` | ✓ input map `4x−2`, feature pipeline | ✓ sigmoid input map | ✓ label rule `>0` | ✓ circle rule `<1`, feature `2−2x` | ✓ label rule `0.8x₁−0.6x₂>0` |
| **HP** | ✓ `rtol`/`atol` | ✗ **within-class exception**: no numeric convergence knob (matrix entries are problem data) | ✓ `_R_STAB`, h-floor | ✓ priors, `_N_TRIALS` | ✓ `_N_STEPS`/`_WARMUP`/`_PROPOSAL_STD` | ✓ `_N_SAMPLES` | ✓ `noise_level`/`length_scale` | ✓ degree 5 | ✓ hidden sizes/`max_iter` | ✓ hidden sizes/`max_iter` | ✓ `C`/`gamma` | ✓ `C`/`max_iter` |
| **TF** | ✓ state-vector ordering (y/z) | ✗ **exception**: one-shot algebraic call, no sequence | ✓ ordered time-step loop | ✗ **exception**: closed-form ratio, no sequence | ✓ chain segments / warmup boundary | ✗ **exception**: pre-drawn exchangeable samples, no ordered trajectory | ✓ sorted training-coordinate/target alignment | ✓ same | ✓ training-target phase | ✓ periodic mask on training rows | ✓ same | ✓ same |
| **SI** | ✓ solver order tier (RK45→lower) | ✓ pivoting→no-pivot tier | ✓ stencil order tier (2nd→1st) | ✗ **exception**: closed-form, no fidelity tier | ✗ **exception**: chain controls are HP/TF, not fidelity tiers | ✓ aggregation-structure tier (arith→geom mean; AM–GM gives ordered domination) — **ARBITRATED-BORDERLINE** | ✓ length-scale prior tier | ✓ degree tier (5→low) | ✓ architecture tier | ✓ architecture tier | ✓ kernel tier (RBF→linear) | ✓ regularisation tier |

**Applicable cell count (n_app): CE 9 + OS 12 + HP 11 + TF 9 + SI 10 = 51 of 60.** NOT_APPLICABLE = 9 (CE×{d1,d2,d3}, HP×a2, TF×{a2,b1,b3}, SI×{b1,b2}).

## 4. Two-rater record: disagreements, arbitration, borderline flags

**Agreement:** 18/20 class-level cells identical; 58/60 PUT-level cells identical (given class ruling).

| # | Cell | Rater A | Rater B | Arbitration + evidence |
|---|---|---|---|---|
| D1 | CE×c2 (PUT) | site-present (target symmetry) | site-absent ("no explicit conserved normalisation") | **present (borderline).** Concrete site: `_y_train = tanh(t)` with symmetric input map; tanh oddness induces the conservation invariant f(x)+f(1−x)=0, approximately maintained by the symmetric degree-5 fit; a type-preserving edit (e.g., target offset) erodes it → CE failure semantics reachable at wrapper level. v4 never attempted CE×c2 (no dev evidence either way). Author may flip at CHECKPOINT 1; power report carries n_app sensitivity. |
| D2 | SI×B class / SI×b3 (PUT) | class inapplicable (fidelity ladder absent in sampling kernels; master-plan worked example) | class applicable, b3 site-present ("retain/drop integrand term"), b1/b2 absent | **b3 present, b1/b2 absent (class applicable-with-exceptions).** Decisive evidence: the two v4 SI×b3 confirmed mutants (`m19/m20_b3_SI1_claude_*.py`) replace the arithmetic mean by the geometric mean (`exp(mean(log(values)))`); AM–GM gives systematic one-sided domination = ordered fidelity degradation, exactly MP5 partial-order failure semantics, at a wrapper-level aggregation site. The master plan's "SI × B inapplicable" was a hypothetical example; the ruling here follows code evidence. b1/b2: both raters converge on absence. |

**Borderline flags carried (no disagreement, both raters ruled present but flagged):** OS×a1 (chaotic output has no global monotone relation; substitution sites + v4 dev n=5 corroborate), HP×b1 (closed-form; prior/trial-count still load-bearing), TF×{c1,c2} (spatial not temporal ordering; phase-misalignment reading), TF×{d1,d2,d3} (training rows nominally exchangeable; periodic-mask reading), SI×{c3,d1} (capacity tier ≠ guaranteed accuracy order), SI×d2 (kernel ordering task-specific).

**Worst-case n_app if every flagged cell were flipped to `✗`: 39.** Power simulation (Task 1.2) therefore scans n_app ∈ {39, 45, 51}.

## 5. v4 development evidence (corroboration only)

Confirmed non-equivalent mutants per attempted op×PUT combo (37 combos attempted in v4; `—` = never attempted):

| Op | a1 | a2 | a3 | b1 | b2 | b3 | c1 | c2 | c3 | d1 | d2 | d3 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| CE | 5 | 6 | 3 | 4 | 5 | 4 | 10 | — | 3 | — | — | — |
| OS | 5 | 5 | 4 | 6 | — | 4 | — | 9 | — | — | 5 | — |
| HP | 5 | — | — | 5 | 5 | — | 5 | 5 | 10 | 20 | 5 | 10 |
| TF | — | — | — | — | — | — | 5 | 5 | 20 | 5 | 4 | 5 |
| SI | 4 | 2 | 1 | — | — | 2 | — | — | — | 5 | — | 4 |

**Applicable-but-never-attempted combos (15; concentrated v5 generation risk, feeds H-CONS feasibility):** CE×c2; OS×{b2,c1,c3,d1,d3}; HP×{a3,b3}; TF×{a1,a3,b2}; SI×{c1,c2,c3,d2}. All other applicable cells have v4 generation precedent. Arithmetic check: 36 attempted-and-applicable (37 − CF legacy) + 15 never-attempted = 51 = n_app ✓.

## 6. Asset inventory (§1.3.6; SHA-256 of the 12 PUT sources at ruling time)

```
7e8ddd1a28dd00719fdb2b7ead11912c2ed740f1743f7c12c1401d162992dd45  src/p2/puts/a1.py  (Lorenz ODE, solve_ivp RK45)
96952397aa7f4944e6f83342894e58c6e0d92df65691db879ee0145d2d0722ec  src/p2/puts/a2.py  (LU decomposition, det via diag(U))
78ac2459090070c221cc837a0b10ad090897db026f9cce5c0cd6ab89db039552  src/p2/puts/a3.py  (explicit FDM heat, ratio to exact)
b05b64a813c5e59e3ed5ef2421a64b5e89b58e17b42201a7ffe3b183a3835472  src/p2/puts/b1.py  (Beta-Binomial posterior mean)
fd311fd196686a9f12d548c3249110cf9f0afe3c41a4f33d622c31d5a1af89c6  src/p2/puts/b2.py  (Metropolis-Hastings chain mean)
4885b81af02531bdfba7f634a2b01b9359e3eb0e74754df8d2c5a9f8fcb674f9  src/p2/puts/b3.py  (Monte-Carlo integration)
d1083573ddaae5745b334ce9e86ef761824a94c168e18848ed135d287ed0c11b  src/p2/puts/c1.py  (GPR surrogate)
c51bbb8171b8ff0f8aa3fcbf4d865560f288d3a7070cf28db243f4ae843ff2f2  src/p2/puts/c2.py  (degree-5 PCE surrogate)
a58d22ff89a6381cd343555103a904185b09c42d337328f305537b532d4d55ea  src/p2/puts/c3.py  (MLP regressor surrogate)
600d385673a76c2a1c8f134076592385a9beb3624ade774ce42b303850f4b08d  src/p2/puts/d1.py  (MLP classifier)
7157c0fc50d194e6b7adea880f940de472d483f6470751b6761b168c2fe241e1  src/p2/puts/d2.py  (SVC RBF classifier)
9255c0e445360057cf50c677c17a483863e2fa9150fef06bc04d81846553abf3  src/p2/puts/d3.py  (Logistic-regression classifier)
```

Documentation-drift note: `docs/experiment_documentation/EXPERIMENT_DESIGN.md` §3.1 lists stale PUT identities (e.g., "A1 Gaussian elimination"); the source code above is authoritative and matches the master plan's KER-* definitions (A1 Lorenz, B3 MC integration, C1 GPR, D3 LogReg).

## 7. Handoff numbers

- **n_app = 51** (arbitrated), sensitivity set {39, 45, 51} for Task 1.2.
- H-CONS denominator = 51 applicable cells; H-DISC pair universe = applicable cells (predicted-nonzero under aligned condition).
- Alignment map for MRSET-ALN construction: CE→MP1, OS→MP2, HP→MP3, TF→MP4, SI→MP5.
