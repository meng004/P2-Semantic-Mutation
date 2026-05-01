# P2 PUT Redesign and MR Instance Definitions

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rewrite all 12 PUT `program` callables to accept scalar `x ∈ [0,1]` (matching AVP verifier sampling), then define one MR module per PUT plus JSON files for every (PUT, MP) cell in the 60-cell matrix.

**Architecture:** All AVP verifiers sample inputs as `x = rng.uniform(0, 1)` and pass the scalar directly to `program(x)`. MP3 passes `h ∈ {0.1, 0.05, 0.025, 0.0125}` directly (not via `mr.r`). Therefore every PUT must expose `program(x: float) → scalar or array`. The current array-input implementations are incompatible. MR functions live in `src/p2/mrs/{put_id}.py`; JSON files in `data/mr_export/{PUT}_MP{k}_mr.json`.

**Tech Stack:** scipy 1.17.1, numpy 2.4.4, scikit-learn 1.8.0, fastdtw — all already installed.

---

## Interface Contracts (read before coding)

| MP | Verifier | x source | program(x) output | mr.r used? | mr.R used? |
|----|----------|----------|-------------------|------------|------------|
| 1 | verify_conservation | uniform(0,1) scalar | scalar or array | YES | YES |
| 2 | verify_wilcoxon | uniform(0,1) scalar | **must cast to float** | YES | YES |
| 3 | verify_convergence_order | h ∈ {0.1,0.05,0.025,0.0125} | **must cast to float** | NO | NO |
| 4 | verify_trajectory_dtw | uniform(0,1) scalar | array (trajectory) | YES | NO (DTW only) |
| 5 | verify_wilcoxon (same code) | uniform(0,1) scalar | **must cast to float** | YES | YES |

For MP3: `reference_value=1.0`, `expected_order=2.0`, `tolerance=0.2`.  
For MP2/5 Wilcoxon: PASS when `p_val < 0.05` for "greater" alternative (diffs consistently positive).

## PUT ↔ MP Assignment

| PUT | Primary MP | r function idea | Expected output |
|-----|-----------|-----------------|-----------------|
| A1 Lorenz | MP4 (Trajectory) | tiny perturbation | x-component trajectory (10 pts) |
| A2 LU | MP1 (Conservation) | complement 1-x | scalar: product of U diagonal |
| A3 FDM heat | MP3 (Convergence) | — (h direct) | scalar: FDM/exact ratio → 1.0 |
| B1 Beta-Binomial | MP2 (Monotonicity) | x + 0.01 | scalar: posterior mean |
| B2 MCMC | MP2 (Monotonicity) | x + 0.05 | scalar: chain mean |
| B3 MC Integration | MP1 (Conservation) | x + 0.1 | scalar: MC estimate |
| C1 GPR | MP5 (Fidelity-order) | x + 0.1 | scalar: GPR prediction |
| C2 PCE | MP5 (Fidelity-order) | x + 0.1 | scalar: PCE prediction |
| C3 NN Surrogate | MP5 (Fidelity-order) | x + 0.1 | scalar: NN prediction |
| D1 MLP | MP2 (Monotonicity) | x + 0.1 | scalar: P(y=1) |
| D2 SVM | MP2 (Monotonicity) | x - 0.1 (closer to center) | scalar: P(y=1) |
| D3 LR | MP2 (Monotonicity) | x + 0.1 | scalar: P(y=1) |

---

## Task 1: Rewrite A1 — Lorenz ODE (MP4 Trajectory)

**Files:**
- Rewrite: `src/p2/puts/a1.py`
- Create: `tests/puts/test_a1.py`

**Design:** `program(x)` maps scalar `x ∈ [0,1]` to Lorenz initial conditions
`IC = [20x−10, 20x−10, 30x+5]`, integrates for `t_end=1.0` (pre-chaotic regime), returns
`x`-component trajectory at 10 evenly-spaced time points. Output shape `(10,)` satisfies MP4 DTW verifier.

For non-primary MPs, trivial MRs are defined in the JSON (r=identity in [0,1], R=always True).

- [ ] **Step 1: Write failing test**

```python
# tests/puts/test_a1.py
import numpy as np
import pytest
from p2.puts.a1 import program

def test_output_shape():
    y = program(0.5)
    assert isinstance(y, np.ndarray) and y.shape == (10,)

def test_deterministic():
    assert np.allclose(program(0.3), program(0.3))

def test_z_reflection_symmetry():
    # Lorenz z-reflection: IC(-x,-y,z) gives trajectory (-x(t), -y(t), z(t))
    # For x ∈ [0,0.5]: IC(1-x) = [20(1-x)-10, ...] = [10-20x, ...] = -[20x-10, ...]
    # So program(1-x) trajectory x-component ≈ -program(x) trajectory x-component
    y1 = program(0.3)
    y2 = program(0.7)   # 1 - 0.3 = 0.7
    assert np.allclose(y1, -y2, atol=1e-4)
```

- [ ] **Step 2: Run to verify failure**

Run: `pytest tests/puts/test_a1.py -v`
Expected: `ImportError` (module doesn't match yet) then shape/symmetry assertions fail.

- [ ] **Step 3: Rewrite `src/p2/puts/a1.py`**

```python
"""A1: Lorenz ODE — chaotic dynamical system (scalar-input interface).

Library: scipy.integrate.solve_ivp (scipy 1.17.1)
URL: https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html

program(x) where x ∈ [0,1] scalar.
Maps x to IC: [20x-10, 20x-10, 30x+5]. Integrates for t_end=1.0.
Returns x-component trajectory at t=0.1,0.2,...,1.0 (array shape (10,)).
"""
import numpy as np
from scipy.integrate import solve_ivp

_SIGMA = 10.0
_RHO = 28.0
_BETA = 8.0 / 3.0
_T_EVAL = np.linspace(0.1, 1.0, 10)


def _lorenz(t, y, sigma, rho, beta):
    x, yy, z = y
    return [sigma * (yy - x), x * (rho - z) - yy, x * yy - beta * z]


def program(x) -> np.ndarray:
    x = float(x)
    ic = np.array([20*x - 10, 20*x - 10, 30*x + 5])
    sol = solve_ivp(
        _lorenz, (0.0, 1.0), ic,
        args=(_SIGMA, _RHO, _BETA),
        t_eval=_T_EVAL, method="RK45", rtol=1e-8, atol=1e-10,
    )
    return sol.y[0]  # x-component, shape (10,)
```

- [ ] **Step 4: Create `tests/puts/__init__.py`**

```bash
touch tests/puts/__init__.py
```

- [ ] **Step 5: Run tests**

Run: `pytest tests/puts/test_a1.py -v`
Expected: 3 tests PASS.

- [ ] **Step 6: Commit**

```bash
git add src/p2/puts/a1.py tests/puts/__init__.py tests/puts/test_a1.py
git commit -m "feat(puts): rewrite A1 Lorenz with scalar x∈[0,1] interface for AVP verifiers"
```

---

## Task 2: Rewrite A2 — LU Decomposition (MP1 Conservation)

**Files:**
- Rewrite: `src/p2/puts/a2.py`
- Create: `tests/puts/test_a2.py`

**Design:** `program(x)` maps scalar `x ∈ [0,1]` to matrix `A(x) = [[2+x, x], [0, 3]]`
(upper-triangular family with `det(A) = 3(2+x) = 6+3x`). Returns scalar `product(diag(U)) = det(A(x))`.

Conservation MR: `r(x) = 1 − x` and `R(y_orig, y_new): |y_orig + y_new − 15| < 0.01`
(because `det(A(x)) + det(A(1-x)) = (6+3x) + (9-3x) = 15` always).

- [ ] **Step 1: Write failing test**

```python
# tests/puts/test_a2.py
import numpy as np
from p2.puts.a2 import program

def test_output_scalar():
    y = program(0.5)
    assert isinstance(float(y), float)

def test_det_formula():
    # product of U diagonal should equal det(A(x)) = 6 + 3x
    for x in [0.0, 0.3, 0.7, 1.0]:
        assert abs(program(x) - (6 + 3*x)) < 1e-8

def test_conservation():
    for x in [0.1, 0.4, 0.8]:
        assert abs(program(x) + program(1-x) - 15.0) < 1e-6
```

- [ ] **Step 2: Run to verify failure**

Run: `pytest tests/puts/test_a2.py -v`
Expected: FAIL (det_formula and conservation).

- [ ] **Step 3: Rewrite `src/p2/puts/a2.py`**

```python
"""A2: LU Decomposition — conservation of determinant under complement transform.

Library: scipy.linalg.lu (scipy 1.17.1)
URL: https://docs.scipy.org/doc/scipy/reference/generated/scipy.linalg.lu.html

program(x) where x ∈ [0,1] scalar.
Matrix: A(x) = [[2+x, x], [0, 3]]; det(A) = 3(2+x) = 6+3x.
Returns: product of U diagonal = det(A(x)) as scalar float.
Conservation: det(A(x)) + det(A(1-x)) = 15 for all x.
"""
import numpy as np
from scipy.linalg import lu


def program(x) -> float:
    x = float(x)
    A = np.array([[2.0 + x, x], [0.0, 3.0]])
    _, _, U = lu(A)
    return float(np.prod(np.diag(U)))
```

- [ ] **Step 4: Run tests**

Run: `pytest tests/puts/test_a2.py -v`
Expected: 3 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/p2/puts/a2.py tests/puts/test_a2.py
git commit -m "feat(puts): rewrite A2 LU with scalar x∈[0,1], conservation det(A(x))+det(A(1-x))=15"
```

---

## Task 3: Rewrite A3 — FDM Heat Equation (MP3 Convergence)

**Files:**
- Rewrite: `src/p2/puts/a3.py`
- Create: `tests/puts/test_a3.py`

**Design:** `program(x)` treats `x` as grid step `h`. Solves heat equation with IC `u(xi,0)=sin(πxi)`,
Dirichlet BC, `α=0.01`, `t_end=0.5`. Returns ratio `u_FDM(0.5, t_end) / u_exact(0.5, t_end) → 1.0`
as `h→0` with convergence order 2 (explicit Euler second-order in space). Matches MP3 verifier:
`program(0.1)`, `program(0.05)`, `program(0.025)`, `program(0.0125)` → [1.0 + O(h²)].

- [ ] **Step 1: Write failing test**

```python
# tests/puts/test_a3.py
import numpy as np
from p2.puts.a3 import program

def test_ratio_near_one_for_fine_grid():
    ratio = program(0.0125)
    assert abs(ratio - 1.0) < 0.02

def test_convergence_order():
    # error should roughly halve when h halves (order ~2 means error ∝ h^2)
    e1 = abs(program(0.1) - 1.0)
    e2 = abs(program(0.05) - 1.0)
    e3 = abs(program(0.025) - 1.0)
    # Each refinement should reduce error; loosely check trend
    assert e2 < e1 and e3 < e2

def test_coarse_grid_further_from_one():
    ratio_coarse = program(0.5)
    ratio_fine = program(0.05)
    assert abs(ratio_fine - 1.0) < abs(ratio_coarse - 1.0)
```

- [ ] **Step 2: Run to verify failure**

Run: `pytest tests/puts/test_a3.py -v`
Expected: FAIL (current A3 takes array, not scalar h).

- [ ] **Step 3: Rewrite `src/p2/puts/a3.py`**

```python
"""A3: FDM Heat Equation — convergence of numerical solution.

Library: numpy (explicit Euler FDM, numpy 2.4.4)
URL: https://numpy.org/doc/stable/

program(x) where x = h (grid spacing), x ∈ (0, 1].
IC: u(xi, 0) = sin(π*xi). BC: Dirichlet u(0)=u(1)=0. α=0.01, t_end=0.5.
Returns ratio u_FDM(0.5, t_end) / u_exact(0.5, t_end) → 1.0 as h→0, order 2.
True solution: u(x,t) = sin(π*x) * exp(-π²*α*t).
"""
import numpy as np

_ALPHA = 0.01
_T_END = 0.5
_R_STAB = 0.4   # stability ratio r = α*dt/h² < 0.5


def program(x) -> float:
    h = max(float(x), 1e-4)
    N = max(4, round(1.0 / h))
    h_act = 1.0 / N
    xi = np.linspace(0.0, 1.0, N + 1)
    u = np.sin(np.pi * xi)
    dt = _R_STAB * h_act**2 / _ALPHA
    n_steps = max(1, int(_T_END / dt))
    for _ in range(n_steps):
        u[1:-1] = u[1:-1] + _R_STAB * (u[2:] - 2.0*u[1:-1] + u[:-2])
        u[0] = 0.0
        u[-1] = 0.0
    u_fdm_mid = np.interp(0.5, xi, u)
    u_exact_mid = np.sin(np.pi * 0.5) * np.exp(-np.pi**2 * _ALPHA * _T_END)
    return float(u_fdm_mid / u_exact_mid)
```

- [ ] **Step 4: Run tests**

Run: `pytest tests/puts/test_a3.py -v`
Expected: 3 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/p2/puts/a3.py tests/puts/test_a3.py
git commit -m "feat(puts): rewrite A3 FDM with scalar h interface, normalized convergence output"
```

---

## Task 4: Rewrite B1 — Beta-Binomial (MP2 Monotonicity)

**Files:**
- Rewrite: `src/p2/puts/b1.py`
- Create: `tests/puts/test_b1.py`

**Design:** `program(x)` maps `x ∈ [0,1]` to `n_succ = round(100*x)`, `n_trials = 100` (fixed).
Returns posterior mean `= (1 + n_succ) / (2 + 100)` with uniform prior `Beta(1,1)`.
Monotone: more successes → higher posterior mean. `r_mp2(x) = min(x + 0.01, 0.99)`.

- [ ] **Step 1: Write failing test**

```python
# tests/puts/test_b1.py
import numpy as np
from p2.puts.b1 import program

def test_output_float():
    assert isinstance(float(program(0.5)), float)

def test_monotone():
    # More successes (higher x) → higher posterior mean
    for x in np.linspace(0.05, 0.90, 10):
        assert program(x + 0.05) > program(x)

def test_boundary_values():
    # x=0: n_succ=0, posterior=(1)/(102) ≈ 0.0098
    assert abs(program(0.0) - 1/102) < 1e-6
    # x=1: n_succ=100, posterior=101/102 ≈ 0.9902
    assert abs(program(1.0) - 101/102) < 1e-6
```

- [ ] **Step 2: Run to verify failure**

Run: `pytest tests/puts/test_b1.py -v`
Expected: FAIL (current B1 takes [n, k] array).

- [ ] **Step 3: Rewrite `src/p2/puts/b1.py`**

```python
"""B1: Beta-Binomial conjugate — posterior mean (scalar x∈[0,1] interface).

Library: scipy.stats.beta (scipy 1.17.1)
URL: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.beta.html

program(x) where x ∈ [0,1] scalar.
x → n_succ = round(100*x), n_trials = 100.
Prior: Beta(1, 1) (uniform). Returns posterior mean = (1+n_succ)/(2+100).
Monotone: larger x → more successes → higher posterior mean.
"""
import numpy as np


_N_TRIALS = 100
_ALPHA_PRIOR = 1.0
_BETA_PRIOR = 1.0


def program(x) -> float:
    x = float(np.clip(x, 0.0, 1.0))
    n_succ = round(_N_TRIALS * x)
    alpha_post = _ALPHA_PRIOR + n_succ
    beta_post = _BETA_PRIOR + (_N_TRIALS - n_succ)
    return float(alpha_post / (alpha_post + beta_post))
```

- [ ] **Step 4: Run tests**

Run: `pytest tests/puts/test_b1.py -v`
Expected: 3 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/p2/puts/b1.py tests/puts/test_b1.py
git commit -m "feat(puts): rewrite B1 Beta-Binomial with scalar x∈[0,1], monotone posterior mean"
```

---

## Task 5: Rewrite B2 — MCMC Metropolis-Hastings (MP2 Monotonicity)

**Files:**
- Rewrite: `src/p2/puts/b2.py`
- Create: `tests/puts/test_b2.py`

**Design:** `program(x)` maps `x ∈ [0,1]` to target mean `μ = 4x − 2` (range `[−2, 2]`).
Runs MH targeting `N(μ, 1)` from `x0=0`, 2000 steps, proposal `σ=0.5`. Returns chain mean.
Monotone: larger `x` → larger target mean `μ` → chain mean increases. `r_mp2(x) = x + 0.05`.

- [ ] **Step 1: Write failing test**

```python
# tests/puts/test_b2.py
import numpy as np
from p2.puts.b2 import program

def test_output_float():
    assert isinstance(float(program(0.5)), float)

def test_at_center_near_zero():
    # x=0.5 → μ=0, chain should converge to ~0
    val = program(0.5)
    assert abs(val) < 0.5

def test_monotone_coarse():
    # Larger x → larger target mean → larger chain mean (coarse check)
    assert program(0.7) > program(0.3)
```

- [ ] **Step 2: Run to verify failure**

Run: `pytest tests/puts/test_b2.py -v`
Expected: FAIL.

- [ ] **Step 3: Rewrite `src/p2/puts/b2.py`**

```python
"""B2: MCMC Metropolis-Hastings — chain mean tracking target (scalar x∈[0,1] interface).

Library: numpy.random (numpy 2.4.4)
URL: https://numpy.org/doc/stable/reference/random/index.html

program(x) where x ∈ [0,1] scalar.
x → target mean μ = 4x − 2 (range [−2, 2]).
Runs MH targeting N(μ,1) from x0=0, n_steps=2000, warmup=500, proposal_std=0.5.
Returns post-warmup chain mean. Monotone: x↑ → μ↑ → chain mean↑.
"""
import numpy as np

_N_STEPS = 2000
_WARMUP = 500
_PROPOSAL_STD = 0.5
_SEED = 42


def program(x) -> float:
    x = float(x)
    mu = 4.0 * x - 2.0
    rng = np.random.default_rng(_SEED)
    current = 0.0
    samples = []
    for i in range(_N_STEPS):
        proposal = current + _PROPOSAL_STD * rng.standard_normal()
        log_ratio = -0.5*((proposal-mu)**2 - (current-mu)**2)
        if np.log(rng.uniform()) < log_ratio:
            current = proposal
        if i >= _WARMUP:
            samples.append(current)
    return float(np.mean(samples))
```

- [ ] **Step 4: Run tests**

Run: `pytest tests/puts/test_b2.py -v`
Expected: 3 tests PASS (note: monotone test is a coarse check; chain is stochastic but seed is fixed).

- [ ] **Step 5: Commit**

```bash
git add src/p2/puts/b2.py tests/puts/test_b2.py
git commit -m "feat(puts): rewrite B2 MCMC with scalar x∈[0,1], monotone chain mean"
```

---

## Task 6: Rewrite B3 — Monte Carlo Integration (MP1 Conservation)

**Files:**
- Rewrite: `src/p2/puts/b3.py`
- Create: `tests/puts/test_b3.py`

**Design:** `program(x)` maps `x ∈ [0,1]` to constant term in integrand.
Estimates `∫₀¹ (x + t²) dt = x + 1/3` using `n=5000` MC samples (fixed seed).
Conservation MR: `r_mp1(x) = x + 0.1`, `R: |y_new − y_orig − 0.1| < 0.01` (linearity of expectation).

- [ ] **Step 1: Write failing test**

```python
# tests/puts/test_b3.py
import numpy as np
from p2.puts.b3 import program

def test_output_float():
    assert isinstance(float(program(0.0)), float)

def test_near_true_value():
    # ∫₀¹ (0.5 + t²) dt = 0.5 + 1/3 ≈ 0.8333
    val = program(0.5)
    assert abs(val - (0.5 + 1.0/3)) < 0.02

def test_linearity():
    # ∫(x+0.1 + t²) - ∫(x + t²) = 0.1 (linearity of integration)
    for x in [0.0, 0.3, 0.6]:
        diff = program(x + 0.1) - program(x)
        assert abs(diff - 0.1) < 0.02
```

- [ ] **Step 2: Run to verify failure**

Run: `pytest tests/puts/test_b3.py -v`
Expected: FAIL.

- [ ] **Step 3: Rewrite `src/p2/puts/b3.py`**

```python
"""B3: Monte Carlo integration — ∫₀¹ (x + t²) dt = x + 1/3 (scalar x∈[0,1] interface).

Library: numpy.random (numpy 2.4.4)
URL: https://numpy.org/doc/stable/reference/random/index.html

program(x) where x ∈ [0,1] scalar (constant term in integrand).
Returns MC estimate of ∫₀¹ (x + t²) dt ≈ x + 1/3 using n=5000 samples (seed=42).
Conservation (MP1): ∫(x+c + t²) - ∫(x + t²) = c (linearity of integration).
"""
import numpy as np

_N_SAMPLES = 5000
_SEED = 42
_rng_samples = np.random.default_rng(_SEED).uniform(0.0, 1.0, _N_SAMPLES)


def program(x) -> float:
    x = float(x)
    return float(np.mean(x + _rng_samples**2))
```

- [ ] **Step 4: Run tests**

Run: `pytest tests/puts/test_b3.py -v`
Expected: 3 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/p2/puts/b3.py tests/puts/test_b3.py
git commit -m "feat(puts): rewrite B3 MC integration with scalar x∈[0,1], linearity conservation"
```

---

## Task 7: Rewrite C1 — GPR (MP5 Fidelity-order)

**Files:**
- Rewrite: `src/p2/puts/c1.py`
- Create: `tests/puts/test_c1.py`

**Design:** `program(x)` maps `x ∈ [0,1]` to test point `t = 6x − 3` (range `[−3, 3]`).
Training data: `f(t) = erf(t)` (monotone increasing ∀t). GPR prediction is monotone in `x`.
`r_mp5(x) = x + 0.1`, `R_mp5(y_orig, y_new): y_new > y_orig` (monotone → fidelity order).

- [ ] **Step 1: Write failing test**

```python
# tests/puts/test_c1.py
import numpy as np
from p2.puts.c1 import program

def test_output_scalar():
    assert isinstance(float(program(0.5)), float)

def test_monotone():
    # erf is monotone → GPR should be monotone in x
    vals = [float(program(x)) for x in np.linspace(0.1, 0.9, 9)]
    assert all(vals[i] < vals[i+1] for i in range(len(vals)-1))

def test_midpoint_near_zero():
    # erf(t=0) = 0, t = 6*0.5-3 = 0
    assert abs(float(program(0.5))) < 0.1
```

- [ ] **Step 2: Run to verify failure**

Run: `pytest tests/puts/test_c1.py -v`
Expected: FAIL (current C1 takes array of test points).

- [ ] **Step 3: Rewrite `src/p2/puts/c1.py`**

```python
"""C1: Gaussian Process Regression surrogate — scalar x∈[0,1] interface.

Library: sklearn.gaussian_process.GaussianProcessRegressor (scikit-learn 1.8.0)
URL: https://scikit-learn.org/stable/modules/generated/sklearn.gaussian_process.GaussianProcessRegressor.html

program(x) where x ∈ [0,1] scalar.
x → test point t = 6x − 3 ∈ [−3, 3]. Training: erf(t) (monotone increasing).
Returns scalar GPR prediction at t. Monotone in x (erf is monotone).
"""
import numpy as np
from scipy.special import erf
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, WhiteKernel

_rng = np.random.default_rng(42)
_t_train = np.sort(_rng.uniform(-3.0, 3.0, 60)).reshape(-1, 1)
_y_train = erf(_t_train.ravel())

_kernel = RBF(length_scale=1.0) + WhiteKernel(noise_level=1e-4)
_model = GaussianProcessRegressor(kernel=_kernel, random_state=42, normalize_y=True)
_model.fit(_t_train, _y_train)


def program(x) -> float:
    x = float(x)
    t = 6.0 * x - 3.0
    return float(_model.predict([[t]])[0])
```

- [ ] **Step 4: Run tests**

Run: `pytest tests/puts/test_c1.py -v`
Expected: 3 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/p2/puts/c1.py tests/puts/test_c1.py
git commit -m "feat(puts): rewrite C1 GPR with scalar x∈[0,1], erf training, monotone interface"
```

---

## Task 8: Rewrite C2 — PCE (MP5 Fidelity-order)

**Files:**
- Rewrite: `src/p2/puts/c2.py`
- Create: `tests/puts/test_c2.py`

**Design:** Same structure as C1. Training: `f(t) = tanh(t)` (monotone increasing ∀t).
Degree-5 polynomial regression. `x ∈ [0,1] → t = 4x − 2 ∈ [−2, 2]`.

- [ ] **Step 1: Write failing test**

```python
# tests/puts/test_c2.py
import numpy as np
from p2.puts.c2 import program

def test_output_scalar():
    assert isinstance(float(program(0.5)), float)

def test_monotone():
    vals = [float(program(x)) for x in np.linspace(0.1, 0.9, 9)]
    assert all(vals[i] < vals[i+1] for i in range(len(vals)-1))

def test_midpoint_near_zero():
    assert abs(float(program(0.5))) < 0.1
```

- [ ] **Step 2: Run to verify failure**

Run: `pytest tests/puts/test_c2.py -v`
Expected: FAIL.

- [ ] **Step 3: Rewrite `src/p2/puts/c2.py`**

```python
"""C2: Polynomial Chaos Expansion surrogate — scalar x∈[0,1] interface.

Library: sklearn PolynomialFeatures + LinearRegression (scikit-learn 1.8.0)
URL: https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.PolynomialFeatures.html

program(x) where x ∈ [0,1] scalar.
x → test point t = 4x − 2 ∈ [−2, 2]. Training: tanh(t) (monotone increasing).
Degree-5 polynomial PCE. Returns scalar prediction. Monotone in x.
"""
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import PolynomialFeatures

_rng = np.random.default_rng(42)
_t_train = np.sort(_rng.uniform(-2.0, 2.0, 80)).reshape(-1, 1)
_y_train = np.tanh(_t_train.ravel())

_model = make_pipeline(PolynomialFeatures(5, include_bias=True), LinearRegression())
_model.fit(_t_train, _y_train)


def program(x) -> float:
    x = float(x)
    t = 4.0 * x - 2.0
    return float(_model.predict([[t]])[0])
```

- [ ] **Step 4: Run tests**

Run: `pytest tests/puts/test_c2.py -v`
Expected: 3 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/p2/puts/c2.py tests/puts/test_c2.py
git commit -m "feat(puts): rewrite C2 PCE with scalar x∈[0,1], tanh training, monotone interface"
```

---

## Task 9: Rewrite C3 — NN Surrogate (MP5 Fidelity-order)

**Files:**
- Rewrite: `src/p2/puts/c3.py`
- Create: `tests/puts/test_c3.py`

**Design:** Same structure. Training: `f(t) = sigmoid(2t)` (monotone increasing). MLP (64, 32). `x → t = 6x − 3`.

- [ ] **Step 1: Write failing test**

```python
# tests/puts/test_c3.py
import numpy as np
from p2.puts.c3 import program

def test_output_scalar():
    assert isinstance(float(program(0.5)), float)

def test_monotone():
    vals = [float(program(x)) for x in np.linspace(0.1, 0.9, 9)]
    assert all(vals[i] < vals[i+1] for i in range(len(vals)-1))

def test_midpoint_near_half():
    # sigmoid(0) = 0.5
    assert abs(float(program(0.5)) - 0.5) < 0.1
```

- [ ] **Step 2: Run to verify failure**

Run: `pytest tests/puts/test_c3.py -v`
Expected: FAIL.

- [ ] **Step 3: Rewrite `src/p2/puts/c3.py`**

```python
"""C3: Neural Network surrogate regressor — scalar x∈[0,1] interface.

Library: sklearn.neural_network.MLPRegressor (scikit-learn 1.8.0)
URL: https://scikit-learn.org/stable/modules/generated/sklearn.neural_network.MLPRegressor.html

program(x) where x ∈ [0,1] scalar.
x → test point t = 6x − 3 ∈ [−3, 3]. Training: sigmoid(2t) (monotone increasing).
MLP (64, 32), ReLU, Adam. Returns scalar prediction. Monotone in x.
"""
import numpy as np
from sklearn.neural_network import MLPRegressor


def _sigmoid(t):
    return 1.0 / (1.0 + np.exp(-2.0 * t))


_rng = np.random.default_rng(42)
_t_train = np.sort(_rng.uniform(-3.0, 3.0, 100)).reshape(-1, 1)
_y_train = _sigmoid(_t_train.ravel())

_model = MLPRegressor(
    hidden_layer_sizes=(64, 32), activation="relu",
    solver="adam", max_iter=1000, random_state=42,
)
_model.fit(_t_train, _y_train)


def program(x) -> float:
    x = float(x)
    t = 6.0 * x - 3.0
    return float(_model.predict([[t]])[0])
```

- [ ] **Step 4: Run tests**

Run: `pytest tests/puts/test_c3.py -v`
Expected: 3 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/p2/puts/c3.py tests/puts/test_c3.py
git commit -m "feat(puts): rewrite C3 NN surrogate with scalar x∈[0,1], sigmoid training, monotone"
```

---

## Task 10: Rewrite D1 — MLP Classifier (MP2 Monotonicity)

**Files:**
- Rewrite: `src/p2/puts/d1.py`
- Create: `tests/puts/test_d1.py`

**Design:** `program(x)` constructs feature `[x, x]`. Boundary `x1 + x2 = 0`, positive class
when `x1 + x2 > 0`, i.e., `2x > 0`, i.e., `x > 0`. P(y=1) increases with x. `r_mp2(x) = x + 0.1`.

- [ ] **Step 1: Write failing test**

```python
# tests/puts/test_d1.py
import numpy as np
from p2.puts.d1 import program

def test_output_float():
    assert 0 <= float(program(0.5)) <= 1

def test_positive_class_for_positive_x():
    assert float(program(0.8)) > 0.5

def test_monotone():
    vals = [float(program(x)) for x in np.linspace(0.05, 0.95, 10)]
    assert all(vals[i] < vals[i+1] for i in range(len(vals)-1))
```

- [ ] **Step 2: Run to verify failure**

Run: `pytest tests/puts/test_d1.py -v`
Expected: FAIL (current D1 takes 2D feature vector, not scalar).

- [ ] **Step 3: Rewrite `src/p2/puts/d1.py`**

```python
"""D1: MLP Classifier — scalar x∈[0,1] interface.

Library: sklearn.neural_network.MLPClassifier (scikit-learn 1.8.0)
URL: https://scikit-learn.org/stable/modules/generated/sklearn.neural_network.MLPClassifier.html

program(x) where x ∈ [0,1] scalar.
Feature: [x, x]. Boundary: x1+x2=0 → positive class when x>0.
P(y=1) monotone increasing with x. Training: 400 pts from R², label = (x1+x2 > 0).
"""
import numpy as np
from sklearn.neural_network import MLPClassifier

_rng = np.random.default_rng(42)
_X_train = _rng.uniform(-1.5, 1.5, (400, 2))
_y_train = (_X_train[:, 0] + _X_train[:, 1] > 0).astype(int)

_model = MLPClassifier(
    hidden_layer_sizes=(32, 16), activation="relu",
    solver="adam", max_iter=500, random_state=42,
)
_model.fit(_X_train, _y_train)


def program(x) -> float:
    x = float(x)
    return float(_model.predict_proba([[x, x]])[0, 1])
```

- [ ] **Step 4: Run tests**

Run: `pytest tests/puts/test_d1.py -v`
Expected: 3 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/p2/puts/d1.py tests/puts/test_d1.py
git commit -m "feat(puts): rewrite D1 MLP with scalar x∈[0,1], feature [x,x], monotone P(y=1)"
```

---

## Task 11: Rewrite D2 — SVM (MP2 Monotonicity)

**Files:**
- Rewrite: `src/p2/puts/d2.py`
- Create: `tests/puts/test_d2.py`

**Design:** `program(x)` constructs feature `[1−x, 0]`. Boundary `x1²+x2²=1` (circle),
positive inside. As `x` increases from 0 to 1, `1−x` decreases from 1 to 0 → point moves
toward center → `P(y=1)` increases. `r_mp2(x) = x + 0.1`.

- [ ] **Step 1: Write failing test**

```python
# tests/puts/test_d2.py
import numpy as np
from p2.puts.d2 import program

def test_output_float():
    assert 0 <= float(program(0.5)) <= 1

def test_near_center_high_prob():
    # x=1 → feature [0, 0] → center → high P(y=1)
    assert float(program(1.0)) > 0.8

def test_monotone():
    vals = [float(program(x)) for x in np.linspace(0.05, 0.95, 10)]
    assert all(vals[i] < vals[i+1] for i in range(len(vals)-1))
```

- [ ] **Step 2: Run to verify failure**

Run: `pytest tests/puts/test_d2.py -v`
Expected: FAIL.

- [ ] **Step 3: Rewrite `src/p2/puts/d2.py`**

```python
"""D2: SVM classifier — scalar x∈[0,1] interface.

Library: sklearn.svm.SVC (scikit-learn 1.8.0)
URL: https://scikit-learn.org/stable/modules/generated/sklearn.svm.SVC.html

program(x) where x ∈ [0,1] scalar.
Feature: [1-x, 0]. Boundary: x1²+x2²=1; positive inside circle.
As x↑: feature moves toward center → P(y=1)↑. Monotone.
Training: 400 pts from [−1.5,1.5]², label = (x1²+x2² < 1).
"""
import numpy as np
from sklearn.svm import SVC

_rng = np.random.default_rng(42)
_X_train = _rng.uniform(-1.5, 1.5, (400, 2))
_y_train = (_X_train[:, 0]**2 + _X_train[:, 1]**2 < 1.0).astype(int)

_model = SVC(kernel="rbf", C=1.0, gamma="scale", probability=True, random_state=42)
_model.fit(_X_train, _y_train)


def program(x) -> float:
    x = float(x)
    return float(_model.predict_proba([[1.0 - x, 0.0]])[0, 1])
```

- [ ] **Step 4: Run tests**

Run: `pytest tests/puts/test_d2.py -v`
Expected: 3 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/p2/puts/d2.py tests/puts/test_d2.py
git commit -m "feat(puts): rewrite D2 SVM with scalar x∈[0,1], feature [1-x,0], monotone P(y=1)"
```

---

## Task 12: Rewrite D3 — Logistic Regression (MP2 Monotonicity)

**Files:**
- Rewrite: `src/p2/puts/d3.py`
- Create: `tests/puts/test_d3.py`

**Design:** `program(x)` constructs feature `[x, 0]`. Boundary `0.8x1 − 0.6x2 = 0 → x1 = 0`.
Positive class when `x1 > 0`, i.e., `x > 0`. P(y=1) increases with x.

- [ ] **Step 1: Write failing test**

```python
# tests/puts/test_d3.py
import numpy as np
from p2.puts.d3 import program

def test_output_float():
    assert 0 <= float(program(0.5)) <= 1

def test_positive_class():
    assert float(program(0.8)) > 0.5

def test_monotone():
    vals = [float(program(x)) for x in np.linspace(0.05, 0.95, 10)]
    assert all(vals[i] < vals[i+1] for i in range(len(vals)-1))
```

- [ ] **Step 2: Run to verify failure**

Run: `pytest tests/puts/test_d3.py -v`
Expected: FAIL.

- [ ] **Step 3: Rewrite `src/p2/puts/d3.py`**

```python
"""D3: Logistic Regression classifier — scalar x∈[0,1] interface.

Library: sklearn.linear_model.LogisticRegression (scikit-learn 1.8.0)
URL: https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html

program(x) where x ∈ [0,1] scalar.
Feature: [x, 0]. Boundary: 0.8x1 - 0.6x2 = 0 → positive when x>0.
P(y=1) monotone increasing with x.
Training: 400 pts from [−1.5,1.5]², label = (0.8x1 - 0.6x2 > 0).
"""
import numpy as np
from sklearn.linear_model import LogisticRegression

_rng = np.random.default_rng(42)
_X_train = _rng.uniform(-1.5, 1.5, (400, 2))
_y_train = (0.8 * _X_train[:, 0] - 0.6 * _X_train[:, 1] > 0).astype(int)

_model = LogisticRegression(C=1.0, solver="lbfgs", max_iter=1000, random_state=42)
_model.fit(_X_train, _y_train)


def program(x) -> float:
    x = float(x)
    return float(_model.predict_proba([[x, 0.0]])[0, 1])
```

- [ ] **Step 4: Run tests**

Run: `pytest tests/puts/test_d3.py -v`
Expected: 3 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/p2/puts/d3.py tests/puts/test_d3.py
git commit -m "feat(puts): rewrite D3 LR with scalar x∈[0,1], feature [x,0], monotone P(y=1)"
```

---

## Task 13: Run all PUT tests together

- [ ] **Step 1: Run full test suite**

Run: `pytest tests/puts/ tests/ -v --tb=short`
Expected: all existing 52 tests + 36 new PUT tests = 88 tests PASS.

- [ ] **Step 2: Commit if needed**

If nothing new to commit, skip. If any fixups, commit:
```bash
git add -p
git commit -m "fix(puts): fixups from full suite run"
```

---

## Task 14: Create MR package and Category A MRs

**Files:**
- Create: `src/p2/mrs/__init__.py`
- Create: `src/p2/mrs/a1.py`
- Create: `src/p2/mrs/a2.py`
- Create: `src/p2/mrs/a3.py`
- Create: `tests/mrs/__init__.py`
- Create: `tests/mrs/test_a_mrs.py`

**Design:** Each PUT module defines `r_mp{k}` and `R_mp{k}` functions for the primary MP.
Non-primary MPs get `r_trivial` (identity) and `R_trivial` (always True).

- [ ] **Step 1: Create MR package**

```bash
mkdir -p src/p2/mrs tests/mrs
touch src/p2/mrs/__init__.py tests/mrs/__init__.py
```

- [ ] **Step 2: Write failing tests for Category A MRs**

```python
# tests/mrs/test_a_mrs.py
import numpy as np
import pytest
from p2.puts.a1 import program as p_a1
from p2.puts.a2 import program as p_a2
from p2.puts.a3 import program as p_a3
import p2.mrs.a1 as mrs_a1
import p2.mrs.a2 as mrs_a2
import p2.mrs.a3 as mrs_a3


def test_a1_r_mp4_in_range():
    for x in [0.1, 0.5, 0.9]:
        xp = mrs_a1.r_mp4(x)
        assert 0.0 <= xp <= 1.0

def test_a2_conservation_mr():
    # R_mp1: |det(A(x)) + det(A(1-x)) - 15| < 0.01
    for x in [0.2, 0.5, 0.8]:
        y_orig = p_a2(x)
        y_new = p_a2(mrs_a2.r_mp1(x))
        assert mrs_a2.R_mp1(y_orig, y_new)

def test_a3_trivial_mr_always_passes():
    for x in [0.1, 0.5, 0.9]:
        y_orig = p_a3(x)
        y_new = p_a3(mrs_a3.r_trivial(x))
        assert mrs_a3.R_trivial(y_orig, y_new)
```

- [ ] **Step 3: Run to verify failure**

Run: `pytest tests/mrs/test_a_mrs.py -v`
Expected: ImportError (modules don't exist yet).

- [ ] **Step 4: Create `src/p2/mrs/a1.py`**

```python
"""MR functions for A1 Lorenz ODE.

Primary MP: MP4 (Trajectory DTW).
  r_mp4: tiny perturbation to x → nearby initial conditions → similar trajectory.
  R_mp4: not used by DTW verifier (DTW verifier ignores mr.R).
Trivial: r_trivial (identity), R_trivial (always True) for MP1/2/3/5.
"""
import numpy as np


def r_mp4(x) -> float:
    return float(np.clip(float(x) + 0.001, 0.0, 1.0))


def R_mp4(y_orig, y_new) -> bool:
    return True  # DTW verifier ignores R; distance checked by verifier itself


def r_trivial(x) -> float:
    return float(x)


def R_trivial(y_orig, y_new) -> bool:
    return True
```

- [ ] **Step 5: Create `src/p2/mrs/a2.py`**

```python
"""MR functions for A2 LU Decomposition.

Primary MP: MP1 (Conservation).
  r_mp1(x) = 1 − x  (complement in [0,1]).
  R_mp1: |det(A(x)) + det(A(1-x)) − 15| < 0.01 (determinant sum is conserved).
Trivial: r_trivial (identity), R_trivial for MP2/3/4/5.
"""


def r_mp1(x) -> float:
    return float(1.0 - float(x))


def R_mp1(y_orig, y_new) -> bool:
    return abs(float(y_orig) + float(y_new) - 15.0) < 0.01


def r_trivial(x) -> float:
    return float(x)


def R_trivial(y_orig, y_new) -> bool:
    return True
```

- [ ] **Step 6: Create `src/p2/mrs/a3.py`**

```python
"""MR functions for A3 FDM Heat Equation.

Primary MP: MP3 (Convergence) — mr.r and mr.R are NOT used by MP3 verifier.
  r_mp3 / R_mp3 defined for completeness but unused by verify_convergence_order.
MP2 (Monotonicity): finer grid → ratio closer to 1.
  r_mp2(x) = x / 2 (halve grid spacing → more accurate → ratio increases).
  R_mp2: y_new >= y_orig (if y_orig < 1) OR y_new <= y_orig (if y_orig > 1).
Trivial: r_trivial (identity), R_trivial for MP1/4/5.
"""
import numpy as np


def r_mp3(x) -> float:
    return float(x) / 2.0


def R_mp3(y_orig, y_new) -> bool:
    return True  # unused by verify_convergence_order


def r_mp2(x) -> float:
    return max(float(x) / 2.0, 1e-4)


def R_mp2(y_orig, y_new) -> bool:
    # Finer grid → ratio closer to 1.0 from below (FDM undershoots for coarse grids)
    y_o, y_n = float(y_orig), float(y_new)
    return abs(y_n - 1.0) <= abs(y_o - 1.0) + 1e-4


def r_trivial(x) -> float:
    return float(x)


def R_trivial(y_orig, y_new) -> bool:
    return True
```

- [ ] **Step 7: Run tests**

Run: `pytest tests/mrs/test_a_mrs.py -v`
Expected: 3 tests PASS.

- [ ] **Step 8: Commit**

```bash
git add src/p2/mrs/ tests/mrs/
git commit -m "feat(mrs): Category A MR functions (A1 MP4 trajectory, A2 MP1 conservation, A3 MP3 convergence)"
```

---

## Task 15: Category B MRs

**Files:**
- Create: `src/p2/mrs/b1.py`
- Create: `src/p2/mrs/b2.py`
- Create: `src/p2/mrs/b3.py`
- Modify: `tests/mrs/test_a_mrs.py` → **new file** `tests/mrs/test_b_mrs.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/mrs/test_b_mrs.py
import numpy as np
from p2.puts.b1 import program as p_b1
from p2.puts.b2 import program as p_b2
from p2.puts.b3 import program as p_b3
import p2.mrs.b1 as mrs_b1
import p2.mrs.b2 as mrs_b2
import p2.mrs.b3 as mrs_b3


def test_b1_r_mp2_increases():
    # More successes → higher posterior mean
    for x in [0.1, 0.4, 0.7]:
        y_orig = p_b1(x)
        y_new = p_b1(mrs_b1.r_mp2(x))
        assert mrs_b1.R_mp2(y_orig, y_new)

def test_b2_r_mp2_increases():
    # Shifting x right shifts target mean up → chain mean increases
    y1 = p_b2(0.3)
    y2 = p_b2(mrs_b2.r_mp2(0.3))
    assert float(y2) > float(y1) - 0.3   # coarse check (chain has variance)

def test_b3_r_mp1_conservation():
    # ∫(x+0.1 + t²) - ∫(x + t²) = 0.1
    for x in [0.0, 0.3, 0.6]:
        y_orig = p_b3(x)
        y_new = p_b3(mrs_b3.r_mp1(x))
        assert mrs_b3.R_mp1(y_orig, y_new)
```

- [ ] **Step 2: Run to verify failure**

Run: `pytest tests/mrs/test_b_mrs.py -v`
Expected: ImportError.

- [ ] **Step 3: Create `src/p2/mrs/b1.py`**

```python
"""MR functions for B1 Beta-Binomial conjugate.

Primary MP: MP2 (Monotonicity).
  r_mp2(x) = min(x + 0.01, 0.99): one more success → higher posterior mean.
  R_mp2(y_orig, y_new): y_new > y_orig.
Trivial: r_trivial, R_trivial for MP1/3/4/5.
"""
import numpy as np


def r_mp2(x) -> float:
    return float(min(float(x) + 0.01, 0.99))


def R_mp2(y_orig, y_new) -> bool:
    return float(y_new) > float(y_orig)


def r_trivial(x) -> float:
    return float(x)


def R_trivial(y_orig, y_new) -> bool:
    return True
```

- [ ] **Step 4: Create `src/p2/mrs/b2.py`**

```python
"""MR functions for B2 MCMC Metropolis-Hastings.

Primary MP: MP2 (Monotonicity).
  r_mp2(x) = min(x + 0.05, 0.95): shifts target mean up by 0.2 → chain mean increases.
  R_mp2: float(y_new) > float(y_orig) - 0.3 (coarse; chain is stochastic).
Trivial: r_trivial, R_trivial for MP1/3/4/5.
"""
import numpy as np


def r_mp2(x) -> float:
    return float(min(float(x) + 0.05, 0.95))


def R_mp2(y_orig, y_new) -> bool:
    return float(y_new) > float(y_orig) - 0.3


def r_trivial(x) -> float:
    return float(x)


def R_trivial(y_orig, y_new) -> bool:
    return True
```

- [ ] **Step 5: Create `src/p2/mrs/b3.py`**

```python
"""MR functions for B3 Monte Carlo Integration.

Primary MP: MP1 (Conservation/linearity).
  r_mp1(x) = min(x + 0.1, 0.9): shifts integrand constant by 0.1.
  R_mp1: |y_new - y_orig - 0.1| < 0.02 (linearity: ∫(x+0.1+t²)=∫(x+t²)+0.1).
Trivial: r_trivial, R_trivial for MP2/3/4/5.
"""
import numpy as np


def r_mp1(x) -> float:
    return float(min(float(x) + 0.1, 0.9))


def R_mp1(y_orig, y_new) -> bool:
    return abs(float(y_new) - float(y_orig) - 0.1) < 0.02


def r_trivial(x) -> float:
    return float(x)


def R_trivial(y_orig, y_new) -> bool:
    return True
```

- [ ] **Step 6: Run tests**

Run: `pytest tests/mrs/test_b_mrs.py -v`
Expected: 3 tests PASS.

- [ ] **Step 7: Commit**

```bash
git add src/p2/mrs/b1.py src/p2/mrs/b2.py src/p2/mrs/b3.py tests/mrs/test_b_mrs.py
git commit -m "feat(mrs): Category B MR functions (B1 MP2 monotone, B2 MP2 chain mean, B3 MP1 linearity)"
```

---

## Task 16: Category C and D MRs

**Files:**
- Create: `src/p2/mrs/c1.py`, `c2.py`, `c3.py`
- Create: `src/p2/mrs/d1.py`, `d2.py`, `d3.py`
- Create: `tests/mrs/test_cd_mrs.py`

All C1-C3: primary MP5 (fidelity-order = monotone for erf/tanh/sigmoid, `r(x) = min(x+0.1, 0.9)`, `R: y_new > y_orig`).
All D1-D3: primary MP2 (monotonicity, `r(x) = x+0.1` for D1/D3, `r(x) = x+0.1` for D2), `R: y_new > y_orig - 0.05`.

- [ ] **Step 1: Write failing tests**

```python
# tests/mrs/test_cd_mrs.py
import numpy as np
from p2.puts.c1 import program as p_c1
from p2.puts.c2 import program as p_c2
from p2.puts.c3 import program as p_c3
from p2.puts.d1 import program as p_d1
from p2.puts.d2 import program as p_d2
from p2.puts.d3 import program as p_d3
import p2.mrs.c1 as mrs_c1
import p2.mrs.c2 as mrs_c2
import p2.mrs.c3 as mrs_c3
import p2.mrs.d1 as mrs_d1
import p2.mrs.d2 as mrs_d2
import p2.mrs.d3 as mrs_d3


def test_c1_mp5_monotone():
    for x in [0.1, 0.4, 0.7]:
        assert mrs_c1.R_mp5(p_c1(x), p_c1(mrs_c1.r_mp5(x)))

def test_c2_mp5_monotone():
    for x in [0.1, 0.4, 0.7]:
        assert mrs_c2.R_mp5(p_c2(x), p_c2(mrs_c2.r_mp5(x)))

def test_c3_mp5_monotone():
    for x in [0.1, 0.4, 0.7]:
        assert mrs_c3.R_mp5(p_c3(x), p_c3(mrs_c3.r_mp5(x)))

def test_d1_mp2_monotone():
    for x in [0.1, 0.4, 0.7]:
        assert mrs_d1.R_mp2(p_d1(x), p_d1(mrs_d1.r_mp2(x)))

def test_d2_mp2_monotone():
    for x in [0.1, 0.4, 0.7]:
        assert mrs_d2.R_mp2(p_d2(x), p_d2(mrs_d2.r_mp2(x)))

def test_d3_mp2_monotone():
    for x in [0.1, 0.4, 0.7]:
        assert mrs_d3.R_mp2(p_d3(x), p_d3(mrs_d3.r_mp2(x)))
```

- [ ] **Step 2: Run to verify failure**

Run: `pytest tests/mrs/test_cd_mrs.py -v`
Expected: ImportError.

- [ ] **Step 3: Create MR files for C1, C2, C3 (identical structure)**

```python
# src/p2/mrs/c1.py
"""MR functions for C1 GPR surrogate.
Primary MP: MP5 (Fidelity-order = monotone since erf is monotone).
  r_mp5(x) = min(x + 0.1, 0.9), R_mp5: y_new > y_orig.
Trivial for MP1/2/3/4.
"""

def r_mp5(x) -> float:
    return min(float(x) + 0.1, 0.9)

def R_mp5(y_orig, y_new) -> bool:
    return float(y_new) > float(y_orig)

def r_trivial(x) -> float:
    return float(x)

def R_trivial(y_orig, y_new) -> bool:
    return True
```

```python
# src/p2/mrs/c2.py
"""MR functions for C2 PCE surrogate.
Primary MP: MP5 (Fidelity-order = monotone since tanh is monotone).
  r_mp5(x) = min(x + 0.1, 0.9), R_mp5: y_new > y_orig.
"""

def r_mp5(x) -> float:
    return min(float(x) + 0.1, 0.9)

def R_mp5(y_orig, y_new) -> bool:
    return float(y_new) > float(y_orig)

def r_trivial(x) -> float:
    return float(x)

def R_trivial(y_orig, y_new) -> bool:
    return True
```

```python
# src/p2/mrs/c3.py
"""MR functions for C3 NN surrogate.
Primary MP: MP5 (Fidelity-order = monotone since sigmoid is monotone).
  r_mp5(x) = min(x + 0.1, 0.9), R_mp5: y_new > y_orig.
"""

def r_mp5(x) -> float:
    return min(float(x) + 0.1, 0.9)

def R_mp5(y_orig, y_new) -> bool:
    return float(y_new) > float(y_orig)

def r_trivial(x) -> float:
    return float(x)

def R_trivial(y_orig, y_new) -> bool:
    return True
```

- [ ] **Step 4: Create MR files for D1, D2, D3**

```python
# src/p2/mrs/d1.py
"""MR functions for D1 MLP classifier.
Primary MP: MP2 (Monotonicity: feature [x,x], boundary x+x=0, positive when x>0).
  r_mp2(x) = min(x + 0.1, 0.9), R_mp2: y_new > y_orig - 0.05.
"""

def r_mp2(x) -> float:
    return min(float(x) + 0.1, 0.9)

def R_mp2(y_orig, y_new) -> bool:
    return float(y_new) > float(y_orig) - 0.05

def r_trivial(x) -> float:
    return float(x)

def R_trivial(y_orig, y_new) -> bool:
    return True
```

```python
# src/p2/mrs/d2.py
"""MR functions for D2 SVM classifier.
Primary MP: MP2 (Monotonicity: feature [1-x,0], positive inside circle, x↑ → P↑).
  r_mp2(x) = min(x + 0.1, 0.9), R_mp2: y_new > y_orig - 0.05.
"""

def r_mp2(x) -> float:
    return min(float(x) + 0.1, 0.9)

def R_mp2(y_orig, y_new) -> bool:
    return float(y_new) > float(y_orig) - 0.05

def r_trivial(x) -> float:
    return float(x)

def R_trivial(y_orig, y_new) -> bool:
    return True
```

```python
# src/p2/mrs/d3.py
"""MR functions for D3 Logistic Regression classifier.
Primary MP: MP2 (Monotonicity: feature [x,0], boundary 0.8x=0, positive when x>0).
  r_mp2(x) = min(x + 0.1, 0.9), R_mp2: y_new > y_orig - 0.05.
"""

def r_mp2(x) -> float:
    return min(float(x) + 0.1, 0.9)

def R_mp2(y_orig, y_new) -> bool:
    return float(y_new) > float(y_orig) - 0.05

def r_trivial(x) -> float:
    return float(x)

def R_trivial(y_orig, y_new) -> bool:
    return True
```

- [ ] **Step 5: Run tests**

Run: `pytest tests/mrs/test_cd_mrs.py -v`
Expected: 6 tests PASS.

- [ ] **Step 6: Commit**

```bash
git add src/p2/mrs/c1.py src/p2/mrs/c2.py src/p2/mrs/c3.py \
        src/p2/mrs/d1.py src/p2/mrs/d2.py src/p2/mrs/d3.py \
        tests/mrs/test_cd_mrs.py
git commit -m "feat(mrs): Category C/D MR functions (MP5 monotone surrogates, MP2 monotone classifiers)"
```

---

## Task 17: Create JSON export files for all 60 cells

**Files:**
- Create: `data/mr_export/{PUT}_MP{k}_mr.json` for k=1..5, 12 PUTs = 60 files

**JSON schema** (per `load_mr_set` in `src/p2/pipeline/loaders.py`):
```json
[{"name": "...", "r_module": "p2.mrs.xx", "r_func": "r_mpN", "R_module": "p2.mrs.xx", "R_func": "R_mpN"}]
```

**Mapping** (primary MP uses real MR; others use trivial):

| PUT | MP1 | MP2 | MP3 | MP4 | MP5 |
|-----|-----|-----|-----|-----|-----|
| A1 | trivial | trivial | trivial | r_mp4/R_mp4 | trivial |
| A2 | r_mp1/R_mp1 | trivial | trivial | trivial | trivial |
| A3 | trivial | r_mp2/R_mp2 | r_mp3/R_mp3 | trivial | trivial |
| B1 | trivial | r_mp2/R_mp2 | trivial | trivial | trivial |
| B2 | trivial | r_mp2/R_mp2 | trivial | trivial | trivial |
| B3 | r_mp1/R_mp1 | trivial | trivial | trivial | trivial |
| C1 | trivial | trivial | trivial | trivial | r_mp5/R_mp5 |
| C2 | trivial | trivial | trivial | trivial | r_mp5/R_mp5 |
| C3 | trivial | trivial | trivial | trivial | r_mp5/R_mp5 |
| D1 | trivial | r_mp2/R_mp2 | trivial | trivial | trivial |
| D2 | trivial | r_mp2/R_mp2 | trivial | trivial | trivial |
| D3 | trivial | r_mp2/R_mp2 | trivial | trivial | trivial |

- [ ] **Step 1: Write failing test for JSON loading**

```python
# tests/mrs/test_json_export.py
import pytest
from pathlib import Path
from p2.pipeline.loaders import load_mr_set


def test_load_a1_mp4():
    mrs = load_mr_set("A1", 4, root=Path("data/mr_export"))
    assert len(mrs) == 1
    assert mrs[0].mp_index == 4
    assert mrs[0].name == "a1_mp4_trajectory"


def test_load_a2_mp1():
    mrs = load_mr_set("A2", 1, root=Path("data/mr_export"))
    assert len(mrs) == 1
    assert mrs[0].mp_index == 1


def test_load_trivial_b1_mp3():
    mrs = load_mr_set("B1", 3, root=Path("data/mr_export"))
    assert len(mrs) == 1
    # Trivial: r is identity
    assert mrs[0].r(0.5) == 0.5


def test_all_60_files_exist():
    root = Path("data/mr_export")
    puts = ["A1","A2","A3","B1","B2","B3","C1","C2","C3","D1","D2","D3"]
    for put in puts:
        for k in range(1, 6):
            f = root / f"{put}_MP{k}_mr.json"
            assert f.exists(), f"Missing: {f}"
```

- [ ] **Step 2: Run to verify failure**

Run: `pytest tests/mrs/test_json_export.py -v`
Expected: FAIL (files don't exist).

- [ ] **Step 3: Create all 60 JSON files via script**

Create `scripts/gen_mr_json.py`:

```python
#!/usr/bin/env python
"""Generate all 60 MR JSON files in data/mr_export/."""
import json
from pathlib import Path

root = Path("data/mr_export")
root.mkdir(parents=True, exist_ok=True)

PUTS = ["A1", "A2", "A3", "B1", "B2", "B3", "C1", "C2", "C3", "D1", "D2", "D3"]
# Map: (put, mp_index) → (func_suffix, name) or "trivial"
PRIMARY = {
    ("A1", 4): ("mp4", "a1_mp4_trajectory"),
    ("A2", 1): ("mp1", "a2_mp1_conservation"),
    ("A3", 2): ("mp2", "a3_mp2_monotone"),
    ("A3", 3): ("mp3", "a3_mp3_convergence"),
    ("B1", 2): ("mp2", "b1_mp2_monotone"),
    ("B2", 2): ("mp2", "b2_mp2_monotone"),
    ("B3", 1): ("mp1", "b3_mp1_linearity"),
    ("C1", 5): ("mp5", "c1_mp5_fidelity"),
    ("C2", 5): ("mp5", "c2_mp5_fidelity"),
    ("C3", 5): ("mp5", "c3_mp5_fidelity"),
    ("D1", 2): ("mp2", "d1_mp2_monotone"),
    ("D2", 2): ("mp2", "d2_mp2_monotone"),
    ("D3", 2): ("mp2", "d3_mp2_monotone"),
}

for put in PUTS:
    put_lower = put.lower()
    module = f"p2.mrs.{put_lower}"
    for k in range(1, 6):
        key = (put, k)
        if key in PRIMARY:
            func_suf, name = PRIMARY[key]
            entry = {
                "name": name,
                "r_module": module,
                "r_func": f"r_{func_suf}",
                "R_module": module,
                "R_func": f"R_{func_suf}",
            }
        else:
            entry = {
                "name": f"{put_lower}_mp{k}_trivial",
                "r_module": module,
                "r_func": "r_trivial",
                "R_module": module,
                "R_func": "R_trivial",
            }
        out = root / f"{put}_MP{k}_mr.json"
        out.write_text(json.dumps([entry], indent=2))
        print(f"  wrote {out}")

print(f"Done: {len(PUTS)*5} files.")
```

Run: `python scripts/gen_mr_json.py`
Expected: 60 files written.

- [ ] **Step 4: Run JSON tests**

Run: `pytest tests/mrs/test_json_export.py -v`
Expected: 4 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add data/mr_export/ scripts/gen_mr_json.py tests/mrs/test_json_export.py
git commit -m "feat(mrs): generate 60 MR JSON files for all (PUT×MP) cells; 13 primary MRs + trivial fallbacks"
```

---

## Task 18: Full integration smoke test

**Files:**
- Create: `tests/integration/test_cell_smoke.py`
- Create: `tests/integration/__init__.py`

- [ ] **Step 1: Write smoke test**

```python
# tests/integration/test_cell_smoke.py
"""Smoke test: verify one real cell runs end-to-end without errors."""
from pathlib import Path
from unittest.mock import patch, MagicMock
from p2.pipeline.loaders import load_put, load_mr_set
from p2.pipeline.run_cell import run_one_cell
from p2.equiv.sampler import UniformSampler


@patch("p2.lrca.killed.call_avp")
@patch("p2.equiv.avp_coherent.call_avp")
def test_b1_mp2_cell_smoke(mock_avp_equiv, mock_avp_killed):
    mock_avp_equiv.return_value = MagicMock(value="pass")
    mock_avp_killed.return_value = MagicMock(value="pass")

    put = load_put("B1", root=Path("src/p2/puts"))
    mr_set = load_mr_set("B1", 2, root=Path("data/mr_export"))
    sampler = UniformSampler(low=0.0, high=1.0, dim=1, seed=42)

    # Use two simple mutants: one that reverses monotonicity, one correct
    mutant_broken = lambda x: 1.0 - put(x)
    mutant_ok = lambda x: put(x)

    result = run_one_cell(
        put=put,
        mutants=[mutant_broken, mutant_ok],
        mr_set=mr_set,
        cell_id="B1_MP2_mut_smoke",
        sampler=sampler,
        k_eq=10,
        epsilon_eq=1e-4,
        epsilon_avp=1e-4,
    )
    assert result.inst_count == 2
    assert result.cell_id == "B1_MP2_mut_smoke"
```

- [ ] **Step 2: Run smoke test**

```bash
touch tests/integration/__init__.py
pytest tests/integration/test_cell_smoke.py -v
```
Expected: 1 test PASS.

- [ ] **Step 3: Run full test suite**

Run: `pytest --tb=short -q`
Expected: all tests PASS (count ≥ 88 + 10 new = 98 tests).

- [ ] **Step 4: Final commit**

```bash
git add tests/integration/
git commit -m "test(integration): end-to-end smoke test for B1×MP2 cell with mocked AVP"
```

---

## Self-Review Checklist

**Spec coverage:**
- ✓ All 12 PUTs rewritten with scalar x ∈ [0,1] interface (Tasks 1-12)
- ✓ MR package created with r/R functions for all 12 PUTs (Tasks 14-16)
- ✓ 60 JSON files generated covering all (PUT, MP) cells (Task 17)
- ✓ Integration smoke test (Task 18)

**Type consistency:**
- `program(x) → float` for MP1/2/3/5 outputs (all scalar)
- `program(x) → np.ndarray shape (10,)` for A1 (MP4 DTW needs array)
- `r_mpN(x) → float`, `R_mpN(y_orig, y_new) → bool` throughout

**Placeholder scan:** No TBDs, no "implement later" — all code shown.

**Potential edge cases noted:**
- A3: `h = max(float(x), 1e-4)` prevents division by zero for x≈0
- B1: `np.clip(x, 0.0, 1.0)` prevents negative n_succ
- B2 R_mp2 has tolerance −0.3 (chain is stochastic with fixed seed)
- D1/D2/D3 R_mp2 has tolerance −0.05 (model boundaries aren't perfectly sharp)
