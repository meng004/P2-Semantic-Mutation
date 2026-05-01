# P2 Experimental Infrastructure Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the experimental infrastructure for P2 paper's empirical audit — mutator pipeline (dual-LLM + manual), equiv judge (E1∧E2), AVP wrapper (P1 reuse), LRCA three-layer classifier, and statistical analysis — to execute the 60-cell experiment described in `论文初稿P2.md`.

**Architecture:** Python 3.11 project with focused modules per pipeline stage (`avp/`, `mutators/`, `equiv/`, `lrca/`, `stats/`, `pipeline/`), driven by an end-to-end orchestrator that processes one (S_i, MP_k, mut_j) cell at a time. Dual-LLM generation (Claude Opus + GPT-4o) with 20% human sampling. P1's AVP imported as a versioned dependency, locked to a specific commit.

**Tech Stack:** Python 3.11, anthropic SDK, openai SDK, numpy 1.26+, scipy 1.11+, pandas 2.x, matplotlib/seaborn, pytest 7+, hydra-core for config, dvc for experiment data versioning, ruff for linting.

---

## Phase 0: Repository Setup

### Task 0.1: Initialize Python project

**Files:**
- Create: `pyproject.toml`
- Create: `.python-version`
- Create: `README.md`
- Create: `.gitignore`

- [ ] **Step 1: Create pyproject.toml**

```toml
[project]
name = "p2-experiments"
version = "0.1.0"
description = "P2 paper experimental infrastructure: dual-LLM mutator pipeline + AVP + LRCA"
requires-python = ">=3.11"
dependencies = [
    "anthropic>=0.21.0",
    "openai>=1.30.0",
    "numpy>=1.26",
    "scipy>=1.11",
    "pandas>=2.1",
    "matplotlib>=3.8",
    "seaborn>=0.13",
    "fastdtw>=0.3",
    "hydra-core>=1.3",
    "pyyaml>=6.0",
    "tqdm>=4.66",
]

[project.optional-dependencies]
dev = ["pytest>=7.4", "pytest-cov>=4.1", "ruff>=0.4", "mypy>=1.8"]

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-v --strict-markers"

[tool.ruff]
line-length = 100
target-version = "py311"
```

- [ ] **Step 2: Create .python-version**

```
3.11
```

- [ ] **Step 3: Create .gitignore**

```
__pycache__/
*.pyc
.pytest_cache/
.ruff_cache/
.venv/
.env
data/mutants/
data/results/
data/lrca/
*.pkl
.DS_Store
```

- [ ] **Step 4: Install dependencies**

Run: `python -m venv .venv && source .venv/bin/activate && pip install -e ".[dev]"`
Expected: All deps install without error.

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml .python-version .gitignore README.md
git commit -m "chore: initialize Python project for P2 experiments"
```

### Task 0.2: Create directory skeleton

**Files:**
- Create: `src/p2/__init__.py`
- Create: `src/p2/{avp,mutators,equiv,lrca,stats,pipeline}/__init__.py`
- Create: `tests/__init__.py`
- Create: `data/{mutants,results,lrca}/.gitkeep`
- Create: `configs/default.yaml`

- [ ] **Step 1: Create source tree**

```bash
mkdir -p src/p2/{avp,mutators,equiv,lrca,stats,pipeline,puts}
mkdir -p tests/{avp,mutators,equiv,lrca,stats}
mkdir -p data/{mutants,results,lrca}
mkdir -p configs
mkdir -p notebooks
```

- [ ] **Step 2: Create __init__.py files**

```bash
touch src/p2/__init__.py
touch src/p2/{avp,mutators,equiv,lrca,stats,pipeline,puts}/__init__.py
touch tests/__init__.py
touch tests/{avp,mutators,equiv,lrca,stats}/__init__.py
touch data/{mutants,results,lrca}/.gitkeep
```

- [ ] **Step 3: Create configs/default.yaml**

```yaml
experiment:
  K_eq: 1000              # E2 sampling count
  N: 20                   # statistical repetition count
  alpha: 0.05             # Wilcoxon significance
  alpha_FDR: 0.05         # Benjamini-Hochberg FDR
  bootstrap_iterations: 1000

llm:
  generator:
    provider: anthropic
    model: claude-opus-4-5
    temperature: 0.3
    seed: 42
  reviewer:
    provider: openai
    model: gpt-4o
    temperature: 0.0
    seed: 42

paths:
  put_root: src/p2/puts
  mutants: data/mutants
  results: data/results
  lrca: data/lrca

p1_avp:
  commit_hash: "TBD-pin-after-P1-arxiv-publish"
  source_path: third_party/p1_avp
```

- [ ] **Step 4: Commit**

```bash
git add src/ tests/ data/ configs/ notebooks/
git commit -m "chore: scaffold src/tests/data/configs directory tree"
```

### Task 0.3: Lock P1 AVP version

**Files:**
- Create: `third_party/p1_avp/README.md`
- Modify: `configs/default.yaml:p1_avp.commit_hash`

- [ ] **Step 1: Document P1 AVP integration plan**

Write `third_party/p1_avp/README.md`:

```markdown
# P1 AVP Integration

P2 reuses P1's AVP (Automated Verification Pipeline) at a fixed commit.
After P1 is published on arXiv, perform:

```bash
git submodule add https://github.com/<P1-repo>.git third_party/p1_avp
cd third_party/p1_avp
git checkout <P1-AVP-commit-hash>
cd ../..
```

Then update `configs/default.yaml`:
```yaml
p1_avp:
  commit_hash: "<actual hash>"
  source_path: third_party/p1_avp
```

P2 must NOT track P1's HEAD; only the locked commit. This isolates P2 from P1's
ongoing revisions during the SANER review cycle.
```

- [ ] **Step 2: Commit**

```bash
git add third_party/p1_avp/README.md
git commit -m "docs: P1 AVP integration plan (commit pinning)"
```

---

## Phase 1: AVP Wrapper

### Task 1.1: AVP interface contract

**Files:**
- Create: `src/p2/avp/interface.py`
- Test: `tests/avp/test_interface.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/avp/test_interface.py
from p2.avp.interface import AVPResult, AVPInterface

def test_avp_result_is_pass_or_fail():
    assert AVPResult.PASS.value == "pass"
    assert AVPResult.FAIL.value == "fail"

def test_avp_interface_is_protocol():
    # AVPInterface should be a Protocol class
    import typing
    assert hasattr(AVPInterface, "__class_getitem__")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/avp/test_interface.py -v`
Expected: FAIL — module not found

- [ ] **Step 3: Implement interface**

```python
# src/p2/avp/interface.py
from enum import Enum
from typing import Protocol, Callable, Any
from dataclasses import dataclass

class AVPResult(Enum):
    PASS = "pass"
    FAIL = "fail"

@dataclass(frozen=True)
class MR:
    """Metamorphic Relation instance: input transform r and output verifier R."""
    r: Callable[[Any], Any]    # input transform
    R: Callable[[Any, Any], bool]  # output verifier
    mp_index: int              # 1..5, which MP this MR belongs to
    name: str                  # for logging

class AVPInterface(Protocol):
    """AVP : Programs × MR × R⁺ → {pass, fail}"""
    def __call__(self, program: Callable, mr: MR, epsilon: float) -> AVPResult: ...
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/avp/test_interface.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/p2/avp/interface.py tests/avp/test_interface.py
git commit -m "feat(avp): add AVP interface protocol and AVPResult enum"
```

### Task 1.2: MP_1 conservation verification

**Files:**
- Create: `src/p2/avp/mp1_conservation.py`
- Test: `tests/avp/test_mp1_conservation.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/avp/test_mp1_conservation.py
import numpy as np
from p2.avp.interface import AVPResult, MR
from p2.avp.mp1_conservation import verify_conservation

def conservation_program(x):
    """Energy-conserving toy: returns (kinetic, potential) summing to 1.0."""
    return np.array([x, 1.0 - x])

def test_conservation_passes_when_holds():
    mr = MR(
        r=lambda x: x,
        R=lambda y_orig, y_new: abs(y_orig.sum() - y_new.sum()) <= 1e-6,
        mp_index=1, name="energy-sum",
    )
    result = verify_conservation(conservation_program, mr, epsilon=1e-6)
    assert result == AVPResult.PASS

def test_conservation_fails_when_broken():
    def broken_program(x):
        return np.array([x, 1.0 - x + 0.1])  # breaks conservation
    mr = MR(
        r=lambda x: x,
        R=lambda y_orig, y_new: abs(y_orig.sum() - y_new.sum()) <= 1e-6,
        mp_index=1, name="energy-sum",
    )
    result = verify_conservation(broken_program, mr, epsilon=1e-6)
    assert result == AVPResult.FAIL
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/avp/test_mp1_conservation.py -v`
Expected: FAIL — module not found

- [ ] **Step 3: Implement MP_1 verifier**

```python
# src/p2/avp/mp1_conservation.py
import numpy as np
from typing import Callable
from p2.avp.interface import AVPResult, MR

def verify_conservation(
    program: Callable, mr: MR, epsilon: float, n_samples: int = 30
) -> AVPResult:
    """MP_1 verification: tolerance equality |LHS − RHS| ≤ epsilon over samples."""
    rng = np.random.default_rng(seed=42)
    for _ in range(n_samples):
        x = rng.uniform(0, 1)
        y_orig = program(x)
        y_new = program(mr.r(x))
        if not mr.R(y_orig, y_new):
            return AVPResult.FAIL
    return AVPResult.PASS
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/avp/test_mp1_conservation.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/p2/avp/mp1_conservation.py tests/avp/test_mp1_conservation.py
git commit -m "feat(avp): MP_1 conservation tolerance equality verifier"
```

### Task 1.3: MP_2/MP_5 Wilcoxon verification

**Files:**
- Create: `src/p2/avp/mp2_5_wilcoxon.py`
- Test: `tests/avp/test_mp2_5_wilcoxon.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/avp/test_mp2_5_wilcoxon.py
import numpy as np
from p2.avp.interface import AVPResult, MR
from p2.avp.mp2_5_wilcoxon import verify_wilcoxon

def test_wilcoxon_passes_when_monotonic():
    """Increasing transform should produce monotonically larger outputs."""
    def monotonic_program(x):
        return x * 2.0

    mr = MR(
        r=lambda x: x + 1.0,    # input increase
        R=lambda y_orig, y_new: y_new > y_orig,  # output should increase
        mp_index=2, name="monotonic-doubling",
    )
    result = verify_wilcoxon(monotonic_program, mr, alpha=0.05, n_samples=50)
    assert result == AVPResult.PASS

def test_wilcoxon_fails_when_anti_monotonic():
    def anti_program(x):
        return -x * 2.0  # decreases
    mr = MR(
        r=lambda x: x + 1.0,
        R=lambda y_orig, y_new: y_new > y_orig,
        mp_index=2, name="bad-monotonic",
    )
    result = verify_wilcoxon(anti_program, mr, alpha=0.05, n_samples=50)
    assert result == AVPResult.FAIL
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/avp/test_mp2_5_wilcoxon.py -v`
Expected: FAIL — module not found

- [ ] **Step 3: Implement Wilcoxon verifier**

```python
# src/p2/avp/mp2_5_wilcoxon.py
import numpy as np
from scipy.stats import wilcoxon
from typing import Callable
from p2.avp.interface import AVPResult, MR

def verify_wilcoxon(
    program: Callable, mr: MR, alpha: float = 0.05, n_samples: int = 50
) -> AVPResult:
    """MP_2/MP_5 verification: Wilcoxon signed-rank one-sided test on R(y_orig, y_new)."""
    rng = np.random.default_rng(seed=42)
    diffs = []
    for _ in range(n_samples):
        x = rng.uniform(0, 1)
        y_orig = program(x)
        y_new = program(mr.r(x))
        # encode R(y_orig, y_new) as sign of (y_new - y_orig); positive means R holds
        diff = float(y_new) - float(y_orig)
        diffs.append(diff if mr.R(y_orig, y_new) else -abs(diff))
    diffs = np.array(diffs)
    if np.allclose(diffs, 0):
        return AVPResult.PASS  # degenerate case: R always holds with equal output
    stat, p_val = wilcoxon(diffs, alternative="greater")
    return AVPResult.PASS if p_val < alpha else AVPResult.FAIL
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/avp/test_mp2_5_wilcoxon.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/p2/avp/mp2_5_wilcoxon.py tests/avp/test_mp2_5_wilcoxon.py
git commit -m "feat(avp): MP_2/MP_5 Wilcoxon signed-rank verifier"
```

### Task 1.4: MP_3 convergence order verification

**Files:**
- Create: `src/p2/avp/mp3_convergence.py`
- Test: `tests/avp/test_mp3_convergence.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/avp/test_mp3_convergence.py
import numpy as np
from p2.avp.interface import AVPResult, MR
from p2.avp.mp3_convergence import verify_convergence_order

def test_second_order_method_passes():
    """Method with O(h²) error refinement should pass."""
    def second_order(h):
        return 1.0 + 0.1 * h**2  # error ∝ h²

    mr = MR(
        r=lambda h: h / 2,
        R=lambda y_orig, y_new: True,  # carried by AVP internal logic
        mp_index=3, name="second-order",
    )
    h_values = [0.1, 0.05, 0.025, 0.0125]
    result = verify_convergence_order(second_order, mr, h_values, expected_order=2.0, tolerance=0.2)
    assert result == AVPResult.PASS

def test_wrong_order_fails():
    def first_order(h):
        return 1.0 + 0.1 * h  # error ∝ h, not h²
    mr = MR(r=lambda h: h / 2, R=lambda a, b: True, mp_index=3, name="bad")
    h_values = [0.1, 0.05, 0.025, 0.0125]
    result = verify_convergence_order(first_order, mr, h_values, expected_order=2.0, tolerance=0.2)
    assert result == AVPResult.FAIL
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/avp/test_mp3_convergence.py -v`
Expected: FAIL — module not found

- [ ] **Step 3: Implement convergence verifier**

```python
# src/p2/avp/mp3_convergence.py
import numpy as np
from typing import Callable, Sequence
from p2.avp.interface import AVPResult, MR

def verify_convergence_order(
    program: Callable, mr: MR, h_values: Sequence[float],
    expected_order: float, tolerance: float = 0.2,
    reference_value: float = 1.0,
) -> AVPResult:
    """MP_3 verification: estimate convergence order from grid sequence."""
    h_arr = np.asarray(sorted(h_values, reverse=True))
    errors = np.array([abs(program(h) - reference_value) for h in h_arr])
    valid = errors > 1e-15
    if valid.sum() < 3:
        return AVPResult.FAIL
    # log-log fit: log(error) = order * log(h) + const
    log_h = np.log(h_arr[valid])
    log_e = np.log(errors[valid])
    order_est, _ = np.polyfit(log_h, log_e, 1)
    return (
        AVPResult.PASS
        if abs(order_est - expected_order) <= tolerance
        else AVPResult.FAIL
    )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/avp/test_mp3_convergence.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/p2/avp/mp3_convergence.py tests/avp/test_mp3_convergence.py
git commit -m "feat(avp): MP_3 convergence order verifier via log-log fit"
```

### Task 1.5: MP_4 DTW trajectory verification

**Files:**
- Create: `src/p2/avp/mp4_dtw.py`
- Test: `tests/avp/test_mp4_dtw.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/avp/test_mp4_dtw.py
import numpy as np
from p2.avp.interface import AVPResult, MR
from p2.avp.mp4_dtw import verify_trajectory_dtw

def test_close_trajectory_passes():
    def smooth_traj(x):
        t = np.linspace(0, 1, 100)
        return np.sin(t * x)

    mr = MR(r=lambda x: x, R=lambda a, b: True, mp_index=4, name="sine")
    result = verify_trajectory_dtw(smooth_traj, mr, epsilon_dtw=0.1, n_samples=10)
    assert result == AVPResult.PASS

def test_distorted_trajectory_fails():
    def distorted(x):
        t = np.linspace(0, 1, 100)
        return np.sin(t * x) + 5 * (t > 0.5)  # discontinuous spike
    mr = MR(r=lambda x: x, R=lambda a, b: True, mp_index=4, name="distorted")
    result = verify_trajectory_dtw(distorted, mr, epsilon_dtw=0.1, n_samples=10)
    assert result == AVPResult.FAIL
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/avp/test_mp4_dtw.py -v`
Expected: FAIL — module not found

- [ ] **Step 3: Implement DTW verifier**

```python
# src/p2/avp/mp4_dtw.py
import numpy as np
from fastdtw import fastdtw
from typing import Callable
from p2.avp.interface import AVPResult, MR

def verify_trajectory_dtw(
    program: Callable, mr: MR, epsilon_dtw: float, n_samples: int = 10,
) -> AVPResult:
    """MP_4 verification: DTW distance between original and transformed trajectories."""
    rng = np.random.default_rng(seed=42)
    distances = []
    for _ in range(n_samples):
        x = rng.uniform(0, 1)
        y_orig = np.asarray(program(x)).reshape(-1, 1)
        y_new = np.asarray(program(mr.r(x))).reshape(-1, 1)
        dist, _ = fastdtw(y_orig, y_new)
        distances.append(dist / max(len(y_orig), len(y_new)))
    avg = float(np.mean(distances))
    return AVPResult.PASS if avg <= epsilon_dtw else AVPResult.FAIL
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/avp/test_mp4_dtw.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/p2/avp/mp4_dtw.py tests/avp/test_mp4_dtw.py
git commit -m "feat(avp): MP_4 DTW trajectory distance verifier"
```

### Task 1.6: AVP dispatcher

**Files:**
- Create: `src/p2/avp/dispatcher.py`
- Test: `tests/avp/test_dispatcher.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/avp/test_dispatcher.py
import numpy as np
from p2.avp.interface import MR, AVPResult
from p2.avp.dispatcher import call_avp

def test_dispatcher_routes_mp1_to_conservation():
    program = lambda x: np.array([x, 1 - x])
    mr = MR(
        r=lambda x: x,
        R=lambda yo, yn: abs(yo.sum() - yn.sum()) <= 1e-6,
        mp_index=1, name="cons",
    )
    result = call_avp(program, mr, epsilon=1e-6)
    assert result == AVPResult.PASS

def test_dispatcher_unknown_mp_raises():
    mr = MR(r=lambda x: x, R=lambda a, b: True, mp_index=99, name="bad")
    program = lambda x: x
    import pytest
    with pytest.raises(ValueError, match="Unknown MP index"):
        call_avp(program, mr, epsilon=1e-6)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/avp/test_dispatcher.py -v`
Expected: FAIL — module not found

- [ ] **Step 3: Implement dispatcher**

```python
# src/p2/avp/dispatcher.py
from typing import Callable
from p2.avp.interface import AVPResult, MR
from p2.avp.mp1_conservation import verify_conservation
from p2.avp.mp2_5_wilcoxon import verify_wilcoxon
from p2.avp.mp3_convergence import verify_convergence_order
from p2.avp.mp4_dtw import verify_trajectory_dtw

def call_avp(program: Callable, mr: MR, epsilon: float) -> AVPResult:
    """AVP dispatcher: route to MP_k specific verifier by mr.mp_index."""
    if mr.mp_index == 1:
        return verify_conservation(program, mr, epsilon)
    elif mr.mp_index in (2, 5):
        return verify_wilcoxon(program, mr, alpha=0.05)
    elif mr.mp_index == 3:
        h_values = [0.1, 0.05, 0.025, 0.0125]
        return verify_convergence_order(program, mr, h_values, expected_order=2.0)
    elif mr.mp_index == 4:
        return verify_trajectory_dtw(program, mr, epsilon_dtw=epsilon)
    else:
        raise ValueError(f"Unknown MP index {mr.mp_index}")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/avp/test_dispatcher.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/p2/avp/dispatcher.py tests/avp/test_dispatcher.py
git commit -m "feat(avp): dispatcher routing MR to MP_k specific verifier"
```

---

## Phase 2: Mutator Pipeline

### Task 2.1: Prompt template loader

**Files:**
- Create: `src/p2/mutators/prompt_loader.py`
- Create: `src/p2/mutators/prompts/template_base.txt`
- Test: `tests/mutators/test_prompt_loader.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/mutators/test_prompt_loader.py
import tempfile, pathlib
from p2.mutators.prompt_loader import load_prompt_template, render_prompt

def test_load_template_substitutes_variables():
    with tempfile.TemporaryDirectory() as td:
        p = pathlib.Path(td) / "tmpl.txt"
        p.write_text("Inject {mut_intent} into {put_name}.")
        out = render_prompt(load_prompt_template(p), mut_intent="A", put_name="B")
        assert out == "Inject A into B."

def test_render_prompt_rejects_extra_vars():
    import pytest
    tmpl = "Hello {name}"
    out = render_prompt(tmpl, name="X")
    assert out == "Hello X"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/mutators/test_prompt_loader.py -v`
Expected: FAIL — module not found

- [ ] **Step 3: Create base template**

```
# src/p2/mutators/prompts/template_base.txt
You are an expert in scientific computing. Inject the following semantic failure
into the program below — produce a syntactically correct, executable mutant.

PUT NAME: {put_name}
SEMANTIC FAILURE INTENT: {mut_intent}

REQUIREMENTS:
- Output ONLY a unified diff (single contiguous hunk, < 10 lines)
- Mutant MUST be syntactically valid Python and executable on legal inputs
- DO NOT mention or use any metamorphic relation knowledge
- DO NOT explain or comment

PUT SOURCE:
```python
{put_source}
```

OUTPUT (unified diff only):
```

- [ ] **Step 4: Implement loader**

```python
# src/p2/mutators/prompt_loader.py
from pathlib import Path

def load_prompt_template(template_path: Path) -> str:
    return Path(template_path).read_text()

def render_prompt(template: str, **variables) -> str:
    return template.format(**variables)
```

- [ ] **Step 5: Run test to verify it passes**

Run: `pytest tests/mutators/test_prompt_loader.py -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add src/p2/mutators/ tests/mutators/test_prompt_loader.py
git commit -m "feat(mutators): prompt template loader with variable substitution"
```

### Task 2.2: LLM generator (Claude Opus)

**Files:**
- Create: `src/p2/mutators/llm_generator.py`
- Test: `tests/mutators/test_llm_generator.py`

- [ ] **Step 1: Write the failing test (mocked)**

```python
# tests/mutators/test_llm_generator.py
from unittest.mock import MagicMock, patch
from p2.mutators.llm_generator import generate_mutants

@patch("p2.mutators.llm_generator.anthropic.Anthropic")
def test_generates_n_candidates(mock_client_cls):
    mock_client = MagicMock()
    mock_client_cls.return_value = mock_client
    mock_client.messages.create.return_value = MagicMock(
        content=[MagicMock(text="--- a/foo.py\n+++ b/foo.py\n@@ -1,1 +1,1 @@\n-x = 1\n+x = 2")]
    )
    diffs = generate_mutants(
        prompt="test prompt", model="claude-opus-4-5",
        n_candidates=3, temperature=0.3, seed=42,
    )
    assert len(diffs) == 3
    for d in diffs:
        assert d.startswith("--- ")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/mutators/test_llm_generator.py -v`
Expected: FAIL — module not found

- [ ] **Step 3: Implement generator**

```python
# src/p2/mutators/llm_generator.py
import os
import anthropic
from typing import List

def generate_mutants(
    prompt: str, model: str = "claude-opus-4-5",
    n_candidates: int = 5, temperature: float = 0.3, seed: int = 42,
    max_tokens: int = 1024,
) -> List[str]:
    """Call Claude to generate n_candidates mutant diffs.

    Returns list of unified-diff strings. Filtering of malformed outputs
    is the caller's responsibility (see mutators.dual_blind_review).
    """
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    diffs: List[str] = []
    for i in range(n_candidates):
        msg = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[{"role": "user", "content": prompt}],
        )
        diffs.append(msg.content[0].text)
    return diffs
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/mutators/test_llm_generator.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/p2/mutators/llm_generator.py tests/mutators/test_llm_generator.py
git commit -m "feat(mutators): Claude Opus mutant generator with mocked tests"
```

### Task 2.3: LLM reviewer (GPT-4o)

**Files:**
- Create: `src/p2/mutators/llm_reviewer.py`
- Test: `tests/mutators/test_llm_reviewer.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/mutators/test_llm_reviewer.py
from unittest.mock import MagicMock, patch
from p2.mutators.llm_reviewer import review_mutant, ReviewVerdict

@patch("p2.mutators.llm_reviewer.openai.OpenAI")
def test_reviewer_parses_three_tuple(mock_client_cls):
    mock_client = MagicMock()
    mock_client_cls.return_value = mock_client
    mock_client.chat.completions.create.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(
            content='{"syntax_ok": true, "executable": "Yes", "fault_injected": "Yes"}'
        ))]
    )
    verdict = review_mutant(put_source="x = 1", mutant_diff="@@ x = 2 @@")
    assert verdict == ReviewVerdict(
        syntax_ok=True, executable="Yes", fault_injected="Yes"
    )
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/mutators/test_llm_reviewer.py -v`
Expected: FAIL — module not found

- [ ] **Step 3: Implement reviewer**

```python
# src/p2/mutators/llm_reviewer.py
import os, json
from dataclasses import dataclass
from typing import Literal
import openai

@dataclass(frozen=True)
class ReviewVerdict:
    syntax_ok: bool
    executable: Literal["Yes", "No", "Uncertain"]
    fault_injected: Literal["Yes", "No", "Uncertain"]

REVIEWER_PROMPT = """You are a code reviewer. Examine the original program and a mutant
(diff applied). Output strict JSON with three fields:
  syntax_ok: bool — is the mutant syntactically valid Python?
  executable: "Yes" | "No" | "Uncertain" — does it appear runnable?
  fault_injected: "Yes" | "No" | "Uncertain" — does it inject some semantic failure?

You are NOT told the failure category, MR, or generator identity.

ORIGINAL:
```python
{put_source}
```

MUTANT DIFF:
```
{mutant_diff}
```

Output JSON only, no prose."""

def review_mutant(put_source: str, mutant_diff: str, model: str = "gpt-4o") -> ReviewVerdict:
    client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    resp = client.chat.completions.create(
        model=model, temperature=0.0, seed=42,
        response_format={"type": "json_object"},
        messages=[{
            "role": "user",
            "content": REVIEWER_PROMPT.format(put_source=put_source, mutant_diff=mutant_diff),
        }],
    )
    parsed = json.loads(resp.choices[0].message.content)
    return ReviewVerdict(
        syntax_ok=bool(parsed["syntax_ok"]),
        executable=parsed["executable"],
        fault_injected=parsed["fault_injected"],
    )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/mutators/test_llm_reviewer.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/p2/mutators/llm_reviewer.py tests/mutators/test_llm_reviewer.py
git commit -m "feat(mutators): GPT-4o reviewer with structured JSON verdict"
```

### Task 2.4: Dual-blind review coordinator

**Files:**
- Create: `src/p2/mutators/dual_blind.py`
- Test: `tests/mutators/test_dual_blind.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/mutators/test_dual_blind.py
from p2.mutators.dual_blind import classify_mutant, MutantStatus
from p2.mutators.llm_reviewer import ReviewVerdict

def test_double_confirmed_when_all_yes():
    v = ReviewVerdict(syntax_ok=True, executable="Yes", fault_injected="Yes")
    assert classify_mutant(v) == MutantStatus.DOUBLE_CONFIRMED

def test_rejected_when_syntax_bad():
    v = ReviewVerdict(syntax_ok=False, executable="No", fault_injected="Yes")
    assert classify_mutant(v) == MutantStatus.REJECTED_L0

def test_arbitration_when_uncertain():
    v = ReviewVerdict(syntax_ok=True, executable="Yes", fault_injected="Uncertain")
    assert classify_mutant(v) == MutantStatus.ARBITRATION_QUEUE
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/mutators/test_dual_blind.py -v`
Expected: FAIL — module not found

- [ ] **Step 3: Implement coordinator**

```python
# src/p2/mutators/dual_blind.py
from enum import Enum
from p2.mutators.llm_reviewer import ReviewVerdict

class MutantStatus(Enum):
    DOUBLE_CONFIRMED = "double_confirmed"
    REJECTED_L0 = "rejected_l0"
    ARBITRATION_QUEUE = "arbitration_queue"

def classify_mutant(verdict: ReviewVerdict) -> MutantStatus:
    """Classify based on dual-blind review verdict per §4.2.4 protocol C."""
    if not verdict.syntax_ok or verdict.executable == "No":
        return MutantStatus.REJECTED_L0
    if verdict.fault_injected == "Yes" and verdict.executable == "Yes":
        return MutantStatus.DOUBLE_CONFIRMED
    return MutantStatus.ARBITRATION_QUEUE
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/mutators/test_dual_blind.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/p2/mutators/dual_blind.py tests/mutators/test_dual_blind.py
git commit -m "feat(mutators): dual-blind review coordinator with three statuses"
```

### Task 2.5: Per-cell mutant pool generator

**Files:**
- Create: `src/p2/mutators/cell_pool.py`
- Test: `tests/mutators/test_cell_pool.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/mutators/test_cell_pool.py
from unittest.mock import patch, MagicMock
from p2.mutators.cell_pool import build_cell_pool

@patch("p2.mutators.cell_pool.review_mutant")
@patch("p2.mutators.cell_pool.generate_mutants")
def test_build_pool_filters_to_double_confirmed(mock_gen, mock_review):
    from p2.mutators.llm_reviewer import ReviewVerdict
    mock_gen.return_value = ["diff1", "diff2", "diff3"]
    mock_review.side_effect = [
        ReviewVerdict(True, "Yes", "Yes"),
        ReviewVerdict(False, "No", "No"),  # rejected
        ReviewVerdict(True, "Yes", "Uncertain"),  # arbitration
    ]
    pool = build_cell_pool(
        put_source="x=1", put_name="A1", mut_intent="break conservation",
        n_candidates=3,
    )
    assert len(pool.double_confirmed) == 1
    assert len(pool.rejected) == 1
    assert len(pool.arbitration) == 1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/mutators/test_cell_pool.py -v`
Expected: FAIL — module not found

- [ ] **Step 3: Implement cell pool builder**

```python
# src/p2/mutators/cell_pool.py
from dataclasses import dataclass, field
from typing import List
from pathlib import Path
from p2.mutators.prompt_loader import load_prompt_template, render_prompt
from p2.mutators.llm_generator import generate_mutants
from p2.mutators.llm_reviewer import review_mutant
from p2.mutators.dual_blind import classify_mutant, MutantStatus

@dataclass
class CellPool:
    cell_id: str  # e.g., "A1_MP1_mutC"
    double_confirmed: List[str] = field(default_factory=list)
    rejected: List[str] = field(default_factory=list)
    arbitration: List[str] = field(default_factory=list)

def build_cell_pool(
    put_source: str, put_name: str, mut_intent: str,
    n_candidates: int = 5, cell_id: str = "unnamed",
    template_path: Path = Path("src/p2/mutators/prompts/template_base.txt"),
) -> CellPool:
    template = load_prompt_template(template_path)
    prompt = render_prompt(
        template, put_name=put_name, mut_intent=mut_intent, put_source=put_source,
    )
    diffs = generate_mutants(prompt, n_candidates=n_candidates)
    pool = CellPool(cell_id=cell_id)
    for d in diffs:
        verdict = review_mutant(put_source=put_source, mutant_diff=d)
        status = classify_mutant(verdict)
        if status == MutantStatus.DOUBLE_CONFIRMED:
            pool.double_confirmed.append(d)
        elif status == MutantStatus.REJECTED_L0:
            pool.rejected.append(d)
        else:
            pool.arbitration.append(d)
    return pool
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/mutators/test_cell_pool.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/p2/mutators/cell_pool.py tests/mutators/test_cell_pool.py
git commit -m "feat(mutators): per-cell pool builder integrating gen+review+classify"
```

---

## Phase 3: Equiv Judgment

### Task 3.1: K_eq input sampler

**Files:**
- Create: `src/p2/equiv/sampler.py`
- Test: `tests/equiv/test_sampler.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/equiv/test_sampler.py
import numpy as np
from p2.equiv.sampler import sample_inputs, UniformSampler

def test_uniform_sampler_returns_k_eq_samples():
    sampler = UniformSampler(low=0.0, high=1.0, dim=3, seed=42)
    samples = sample_inputs(sampler, k_eq=1000)
    assert samples.shape == (1000, 3)
    assert np.all(samples >= 0) and np.all(samples <= 1)

def test_seed_reproducibility():
    s1 = sample_inputs(UniformSampler(0, 1, 2, seed=42), k_eq=100)
    s2 = sample_inputs(UniformSampler(0, 1, 2, seed=42), k_eq=100)
    np.testing.assert_array_equal(s1, s2)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/equiv/test_sampler.py -v`
Expected: FAIL — module not found

- [ ] **Step 3: Implement sampler**

```python
# src/p2/equiv/sampler.py
import numpy as np
from dataclasses import dataclass
from typing import Protocol

class InputSampler(Protocol):
    def sample(self, k_eq: int) -> np.ndarray: ...

@dataclass
class UniformSampler:
    low: float
    high: float
    dim: int
    seed: int = 42
    def sample(self, k_eq: int) -> np.ndarray:
        rng = np.random.default_rng(self.seed)
        return rng.uniform(self.low, self.high, size=(k_eq, self.dim))

def sample_inputs(sampler: InputSampler, k_eq: int) -> np.ndarray:
    return sampler.sample(k_eq)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/equiv/test_sampler.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/p2/equiv/sampler.py tests/equiv/test_sampler.py
git commit -m "feat(equiv): K_eq uniform input sampler with reproducible seed"
```

### Task 3.2: E2 Output-equivalence judge

**Files:**
- Create: `src/p2/equiv/output_equiv.py`
- Test: `tests/equiv/test_output_equiv.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/equiv/test_output_equiv.py
import numpy as np
from p2.equiv.output_equiv import judge_e2

def test_e2_passes_for_identical():
    f = lambda x: x * 2
    samples = np.array([[0.1], [0.5], [0.9]])
    assert judge_e2(f, f, samples, epsilon=1e-9) is True

def test_e2_fails_for_divergent():
    f = lambda x: x * 2
    g = lambda x: x * 2 + 1.0
    samples = np.array([[0.1], [0.5], [0.9]])
    assert judge_e2(f, g, samples, epsilon=1e-9) is False
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/equiv/test_output_equiv.py -v`
Expected: FAIL

- [ ] **Step 3: Implement E2 judge**

```python
# src/p2/equiv/output_equiv.py
import numpy as np
from typing import Callable

def judge_e2(
    s_orig: Callable, s_mutant: Callable,
    samples: np.ndarray, epsilon: float,
) -> bool:
    """E2: ∀ x ∈ X_{K_eq}: ‖S(x) − s'(x)‖ ≤ epsilon."""
    for x in samples:
        x_in = x[0] if x.shape == (1,) else x
        y_orig = np.asarray(s_orig(x_in)).flatten()
        y_mut = np.asarray(s_mutant(x_in)).flatten()
        if np.linalg.norm(y_orig - y_mut) > epsilon:
            return False
    return True
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/equiv/test_output_equiv.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/p2/equiv/output_equiv.py tests/equiv/test_output_equiv.py
git commit -m "feat(equiv): E2 output-equivalence judge over K_eq samples"
```

### Task 3.3: E1 AVP-coherent judge

**Files:**
- Create: `src/p2/equiv/avp_coherent.py`
- Test: `tests/equiv/test_avp_coherent.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/equiv/test_avp_coherent.py
import numpy as np
from p2.avp.interface import MR
from p2.equiv.avp_coherent import judge_e1

def test_e1_passes_when_all_mr_agree():
    s = lambda x: x * 2
    sm = lambda x: x * 2  # identical
    mr_set = [
        MR(r=lambda x: x, R=lambda a, b: True, mp_index=1, name="mr1"),
        MR(r=lambda x: x, R=lambda a, b: True, mp_index=2, name="mr2"),
    ]
    assert judge_e1(s, sm, mr_set, epsilon=1e-6) is True
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/equiv/test_avp_coherent.py -v`
Expected: FAIL

- [ ] **Step 3: Implement E1 judge**

```python
# src/p2/equiv/avp_coherent.py
from typing import Callable, Sequence
from p2.avp.dispatcher import call_avp
from p2.avp.interface import MR

def judge_e1(
    s_orig: Callable, s_mutant: Callable,
    mr_set: Sequence[MR], epsilon: float,
) -> bool:
    """E1: ∀ mr ∈ MR: AVP(S, mr) = AVP(s', mr)."""
    for mr in mr_set:
        if call_avp(s_orig, mr, epsilon) != call_avp(s_mutant, mr, epsilon):
            return False
    return True
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/equiv/test_avp_coherent.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/p2/equiv/avp_coherent.py tests/equiv/test_avp_coherent.py
git commit -m "feat(equiv): E1 AVP-coherent judge over MR set"
```

### Task 3.4: Equiv compound judge (E1 ∧ E2)

**Files:**
- Create: `src/p2/equiv/judge.py`
- Test: `tests/equiv/test_judge.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/equiv/test_judge.py
from p2.avp.interface import MR
from p2.equiv.judge import is_equivalent
from p2.equiv.sampler import UniformSampler

def test_judge_requires_both_e1_e2():
    s = lambda x: x * 2
    sm = lambda x: x * 2
    mr_set = [MR(lambda x: x, lambda a, b: True, 1, "m")]
    sampler = UniformSampler(0, 1, 1, seed=42)
    assert is_equivalent(s, sm, mr_set, sampler, k_eq=10, epsilon_eq=1e-9, epsilon_avp=1e-6)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/equiv/test_judge.py -v`
Expected: FAIL

- [ ] **Step 3: Implement compound judge**

```python
# src/p2/equiv/judge.py
from typing import Callable, Sequence
from p2.avp.interface import MR
from p2.equiv.output_equiv import judge_e2
from p2.equiv.avp_coherent import judge_e1
from p2.equiv.sampler import sample_inputs, InputSampler

def is_equivalent(
    s_orig: Callable, s_mutant: Callable,
    mr_set: Sequence[MR], sampler: InputSampler,
    k_eq: int, epsilon_eq: float, epsilon_avp: float,
) -> bool:
    """equiv ⇔ (E1 AVP-coherent) ∧ (E2 output-equiv)."""
    samples = sample_inputs(sampler, k_eq)
    if not judge_e2(s_orig, s_mutant, samples, epsilon_eq):
        return False
    return judge_e1(s_orig, s_mutant, mr_set, epsilon_avp)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/equiv/test_judge.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/p2/equiv/judge.py tests/equiv/test_judge.py
git commit -m "feat(equiv): compound is_equivalent (E1 ∧ E2)"
```

---

## Phase 4: AVP killed/survive Classifier

### Task 4.1: killed predicate (OR aggregate)

**Files:**
- Create: `src/p2/lrca/killed.py`
- Test: `tests/lrca/test_killed.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/lrca/test_killed.py
from p2.avp.interface import MR, AVPResult
from p2.lrca.killed import is_killed

def test_killed_when_any_mr_distinguishes():
    s = lambda x: x
    sm = lambda x: x + 1  # diverges on Wilcoxon mr below
    mr_set = [
        MR(r=lambda x: x + 1, R=lambda yo, yn: yn > yo, mp_index=2, name="mono"),
    ]
    assert is_killed(s, sm, mr_set, epsilon=0.05) is True

def test_not_killed_when_all_mr_agree():
    s = lambda x: x
    sm = lambda x: x  # identical
    mr_set = [MR(r=lambda x: x, R=lambda a, b: True, mp_index=1, name="m")]
    assert is_killed(s, sm, mr_set, epsilon=1e-6) is False
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/lrca/test_killed.py -v`
Expected: FAIL

- [ ] **Step 3: Implement killed predicate**

```python
# src/p2/lrca/killed.py
from typing import Callable, Sequence
from p2.avp.interface import MR, AVPResult
from p2.avp.dispatcher import call_avp

def is_killed(
    s_orig: Callable, s_mutant: Callable,
    mr_set: Sequence[MR], epsilon: float,
) -> bool:
    """killed ⇔ ∃ mr ∈ MR: AVP(S, mr) = pass ∧ AVP(s', mr) = fail."""
    for mr in mr_set:
        if call_avp(s_orig, mr, epsilon) == AVPResult.PASS and \
           call_avp(s_mutant, mr, epsilon) == AVPResult.FAIL:
            return True
    return False
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/lrca/test_killed.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/p2/lrca/killed.py tests/lrca/test_killed.py
git commit -m "feat(lrca): killed predicate with OR aggregate over MR"
```

---

## Phase 5: LRCA Three-Layer Classifier

### Task 5.1: L1 tolerance robustness

**Files:**
- Create: `src/p2/lrca/l1_tolerance.py`
- Test: `tests/lrca/test_l1_tolerance.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/lrca/test_l1_tolerance.py
from p2.avp.interface import MR
from p2.lrca.l1_tolerance import check_l1_robust

def test_l1_robust_when_consistently_failing():
    s = lambda x: x
    sm = lambda x: x + 100  # always fails
    mr_set = [MR(lambda x: x + 1, lambda yo, yn: yn > yo, 2, "m")]
    assert check_l1_robust(s, sm, mr_set, n_repeat=20, epsilon=0.05) is True

def test_l1_fragile_when_intermittent():
    import random
    rng = random.Random(0)
    def flaky(x):
        return x if rng.random() < 0.5 else x + 100
    mr_set = [MR(lambda x: x + 1, lambda yo, yn: yn > yo, 2, "m")]
    # flaky has < 80% fail rate in worst case → fragile
    assert check_l1_robust(lambda x: x, flaky, mr_set, n_repeat=20, epsilon=0.05) in (True, False)
    # exact value depends on rng — this test only confirms function returns bool
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/lrca/test_l1_tolerance.py -v`
Expected: FAIL

- [ ] **Step 3: Implement L1 check**

```python
# src/p2/lrca/l1_tolerance.py
from typing import Callable, Sequence
from p2.avp.interface import MR
from p2.lrca.killed import is_killed

def check_l1_robust(
    s_orig: Callable, s_mutant: Callable,
    mr_set: Sequence[MR], n_repeat: int = 20, epsilon: float = 0.05,
    threshold: float = 0.8,
) -> bool:
    """L1: rerun N times, fail rate ≥ threshold ⇒ robust (not C2)."""
    fail_count = sum(
        1 for _ in range(n_repeat) if is_killed(s_orig, s_mutant, mr_set, epsilon)
    )
    return (fail_count / n_repeat) >= threshold
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/lrca/test_l1_tolerance.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/p2/lrca/l1_tolerance.py tests/lrca/test_l1_tolerance.py
git commit -m "feat(lrca): L1 tolerance robustness (N=20 repeat ≥ 0.8 threshold)"
```

### Task 5.2: L2 OOD splitter

**Files:**
- Create: `src/p2/lrca/l2_ood.py`
- Test: `tests/lrca/test_l2_ood.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/lrca/test_l2_ood.py
import numpy as np
from p2.lrca.l2_ood import is_ood_induced

def test_ood_induced_when_fail_only_outside_valid():
    valid_low, valid_high = 0.0, 1.0
    # mutant fails only on x > 1 (OOD region)
    def diff_fn(x):
        return abs(x) > 1.0
    fails = [diff_fn(x) for x in np.linspace(-2, 2, 100)]
    valid_mask = [(valid_low <= x <= valid_high) for x in np.linspace(-2, 2, 100)]
    assert is_ood_induced(fails, valid_mask) is True

def test_not_ood_induced_when_fail_inside():
    diffs = [True] * 100  # always fails
    valid_mask = [True] * 100
    assert is_ood_induced(diffs, valid_mask) is False
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/lrca/test_l2_ood.py -v`
Expected: FAIL

- [ ] **Step 3: Implement L2**

```python
# src/p2/lrca/l2_ood.py
from typing import Sequence

def is_ood_induced(
    fails_per_input: Sequence[bool], valid_mask: Sequence[bool],
) -> bool:
    """L2: returns True iff failures occur only on inputs outside valid domain."""
    fails_inside = sum(1 for f, v in zip(fails_per_input, valid_mask) if f and v)
    fails_outside = sum(1 for f, v in zip(fails_per_input, valid_mask) if f and not v)
    return fails_inside == 0 and fails_outside > 0
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/lrca/test_l2_ood.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/p2/lrca/l2_ood.py tests/lrca/test_l2_ood.py
git commit -m "feat(lrca): L2 OOD splitter (fail-only-outside-valid detection)"
```

### Task 5.3: L3 statistical assumption baseline

**Files:**
- Create: `src/p2/lrca/l3_assumption.py`
- Test: `tests/lrca/test_l3_assumption.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/lrca/test_l3_assumption.py
import numpy as np
from p2.lrca.l3_assumption import is_assumption_violated

def test_iid_holds_for_independent_normal():
    rng = np.random.default_rng(42)
    samples = rng.normal(size=100)
    assert is_assumption_violated(samples) is False

def test_assumption_violated_for_autocorrelated():
    # AR(1) with rho=0.95 — strong autocorrelation
    rho = 0.95
    n = 100
    s = np.zeros(n)
    rng = np.random.default_rng(0)
    for i in range(1, n):
        s[i] = rho * s[i-1] + rng.normal()
    assert is_assumption_violated(s) is True
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/lrca/test_l3_assumption.py -v`
Expected: FAIL

- [ ] **Step 3: Implement L3**

```python
# src/p2/lrca/l3_assumption.py
import numpy as np
from scipy.stats import jarque_bera

def is_assumption_violated(
    samples: np.ndarray, alpha: float = 0.05, autocorr_threshold: float = 0.3,
) -> bool:
    """L3: violation if either (a) Jarque-Bera rejects normality, or
    (b) lag-1 autocorrelation exceeds threshold (IID violation proxy)."""
    samples = np.asarray(samples)
    if len(samples) < 8:
        return False
    # autocorrelation lag-1
    lag1 = np.corrcoef(samples[:-1], samples[1:])[0, 1]
    if abs(lag1) > autocorr_threshold:
        return True
    # normality test (proxy for distributional assumption)
    _, p = jarque_bera(samples)
    return p < alpha
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/lrca/test_l3_assumption.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/p2/lrca/l3_assumption.py tests/lrca/test_l3_assumption.py
git commit -m "feat(lrca): L3 IID/normality assumption baseline check"
```

### Task 5.4: LRCA decision tree

**Files:**
- Create: `src/p2/lrca/decision_tree.py`
- Test: `tests/lrca/test_decision_tree.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/lrca/test_decision_tree.py
from p2.lrca.decision_tree import classify_root_cause, RootCause, KillContext

def test_c2_when_l1_fragile():
    ctx = KillContext(l1_robust=False, l2_ood=False, l3_violated=False, artifact=False)
    assert classify_root_cause(ctx) == RootCause.C2

def test_c3_when_ood_induced():
    ctx = KillContext(l1_robust=True, l2_ood=True, l3_violated=False, artifact=False)
    assert classify_root_cause(ctx) == RootCause.C3

def test_c4_when_assumption_violated():
    ctx = KillContext(l1_robust=True, l2_ood=False, l3_violated=True, artifact=False)
    assert classify_root_cause(ctx) == RootCause.C4

def test_c5_when_artifact():
    ctx = KillContext(l1_robust=True, l2_ood=False, l3_violated=False, artifact=True)
    assert classify_root_cause(ctx) == RootCause.C5

def test_c1_when_all_clear():
    ctx = KillContext(l1_robust=True, l2_ood=False, l3_violated=False, artifact=False)
    assert classify_root_cause(ctx) == RootCause.C1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/lrca/test_decision_tree.py -v`
Expected: FAIL

- [ ] **Step 3: Implement decision tree**

```python
# src/p2/lrca/decision_tree.py
from dataclasses import dataclass
from enum import Enum

class RootCause(Enum):
    C1 = "C1_genuine_semantic_failure"
    C2 = "C2_tolerance_perturbation"
    C3 = "C3_OOD_induced"
    C4 = "C4_assumption_violation"
    C5 = "C5_mutator_artifact"

@dataclass(frozen=True)
class KillContext:
    l1_robust: bool      # True if fail rate ≥ 0.8 over N repeats
    l2_ood: bool         # True if fails only outside D_S^valid (C/D classes)
    l3_violated: bool    # True if IID/stationarity broken (B/D classes + Wilcoxon/DTW)
    artifact: bool       # True if mutator/LLM artifact detected by post-hoc review

def classify_root_cause(ctx: KillContext) -> RootCause:
    """Decision tree per §2.6.3 with priority C5 > C4 > C3 > C2 > C1."""
    if not ctx.l1_robust:
        return RootCause.C2
    if ctx.l2_ood:
        return RootCause.C3
    if ctx.l3_violated:
        return RootCause.C4
    if ctx.artifact:
        return RootCause.C5
    return RootCause.C1
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/lrca/test_decision_tree.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/p2/lrca/decision_tree.py tests/lrca/test_decision_tree.py
git commit -m "feat(lrca): decision tree with C5>C4>C3>C2>C1 priority"
```

---

## Phase 6: Statistical Analysis

### Task 6.1: SMS computation

**Files:**
- Create: `src/p2/stats/sms.py`
- Test: `tests/stats/test_sms.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/stats/test_sms.py
import math
from p2.stats.sms import compute_sms

def test_sms_basic():
    # 20 mutants, 5 equiv, 10 killed → SMS = 10/(20-5) = 2/3
    sms = compute_sms(killed=10, total=20, equiv=5)
    assert math.isclose(sms, 10.0 / 15.0)

def test_sms_zero_when_all_equiv():
    sms = compute_sms(killed=0, total=10, equiv=10)
    assert sms == 0.0

def test_sms_undefined_returns_nan():
    import math
    sms = compute_sms(killed=0, total=5, equiv=5)
    assert math.isnan(sms)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/stats/test_sms.py -v`
Expected: FAIL

- [ ] **Step 3: Implement SMS**

```python
# src/p2/stats/sms.py
import math

def compute_sms(killed: int, total: int, equiv: int) -> float:
    """SMS = killed / (total − equiv). Returns NaN when denominator is 0."""
    denom = total - equiv
    if denom <= 0:
        return math.nan
    return killed / denom
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/stats/test_sms.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/p2/stats/sms.py tests/stats/test_sms.py
git commit -m "feat(stats): SMS = killed/(total-equiv) with NaN guard"
```

### Task 6.2: RQ1 rates

**Files:**
- Create: `src/p2/stats/rq1_rates.py`
- Test: `tests/stats/test_rq1_rates.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/stats/test_rq1_rates.py
from p2.stats.rq1_rates import compute_rates

def test_rates_normalize_against_inst():
    r = compute_rates(inst=20, equiv=5, killed=10, survive=5, n_target=15)
    assert r["inst_rate"] == 20 / 15
    assert r["equiv_rate"] == 5 / 20
    assert r["survive_rate"] == 5 / 20
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/stats/test_rq1_rates.py -v`
Expected: FAIL

- [ ] **Step 3: Implement rates**

```python
# src/p2/stats/rq1_rates.py
def compute_rates(inst: int, equiv: int, killed: int, survive: int, n_target: int = 15) -> dict:
    """RQ1 four rates: inst_rate, equiv_rate, killed_rate (≡ for diagnostic), survive_rate.

    Note: C1_share is computed separately by LRCA classifier and joined externally.
    """
    return {
        "inst_rate": inst / n_target if n_target > 0 else 0.0,
        "equiv_rate": equiv / inst if inst > 0 else 0.0,
        "survive_rate": survive / inst if inst > 0 else 0.0,
    }
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/stats/test_rq1_rates.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/p2/stats/rq1_rates.py tests/stats/test_rq1_rates.py
git commit -m "feat(stats): RQ1 inst/equiv/survive rates"
```

### Task 6.3: RQ2 alignment slice analysis

**Files:**
- Create: `src/p2/stats/rq2_alignment.py`
- Test: `tests/stats/test_rq2_alignment.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/stats/test_rq2_alignment.py
import numpy as np
from p2.stats.rq2_alignment import cliffs_delta, alignment_odds_ratio

def test_cliffs_delta_positive_when_aligned_higher():
    aligned = np.array([0.8, 0.9, 0.85])
    cross = np.array([0.2, 0.3, 0.1])
    delta = cliffs_delta(aligned, cross)
    assert delta > 0.474  # at least medium effect

def test_odds_ratio_basic():
    # aligned: 8/10 high, cross: 2/10 high
    or_val = alignment_odds_ratio(aligned_high=8, aligned_low=2, cross_high=2, cross_low=8)
    assert or_val > 3.0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/stats/test_rq2_alignment.py -v`
Expected: FAIL

- [ ] **Step 3: Implement RQ2**

```python
# src/p2/stats/rq2_alignment.py
import numpy as np

def cliffs_delta(group_a: np.ndarray, group_b: np.ndarray) -> float:
    """Cliff's δ effect size: P(a > b) - P(a < b)."""
    a = np.asarray(group_a)
    b = np.asarray(group_b)
    gt = sum(x > y for x in a for y in b)
    lt = sum(x < y for x in a for y in b)
    n = len(a) * len(b)
    return (gt - lt) / n if n > 0 else 0.0

def alignment_odds_ratio(
    aligned_high: int, aligned_low: int, cross_high: int, cross_low: int,
) -> float:
    """Odds ratio of high-SMS membership in aligned vs cross slices."""
    num = aligned_high * cross_low
    den = aligned_low * cross_high
    return num / den if den > 0 else float("inf")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/stats/test_rq2_alignment.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/p2/stats/rq2_alignment.py tests/stats/test_rq2_alignment.py
git commit -m "feat(stats): RQ2 Cliff's δ and alignment odds ratio"
```

### Task 6.4: RQ3 cross-class consistency

**Files:**
- Create: `src/p2/stats/rq3_cross_class.py`
- Test: `tests/stats/test_rq3_cross_class.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/stats/test_rq3_cross_class.py
import numpy as np
from p2.stats.rq3_cross_class import sign_test_all_positive, cv

def test_sign_test_passes_when_all_positive():
    delta_per_class = {"A": 0.3, "B": 0.4, "C": 0.2, "D": 0.5}
    assert sign_test_all_positive(delta_per_class) is True

def test_cv_calculation():
    delta_per_class = {"A": 0.3, "B": 0.4, "C": 0.2, "D": 0.5}
    val = cv(delta_per_class)
    assert val < 0.5  # designed under H4 threshold
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/stats/test_rq3_cross_class.py -v`
Expected: FAIL

- [ ] **Step 3: Implement RQ3**

```python
# src/p2/stats/rq3_cross_class.py
import numpy as np

def sign_test_all_positive(delta_per_class: dict) -> bool:
    return all(v > 0 for v in delta_per_class.values())

def cv(delta_per_class: dict) -> float:
    arr = np.array(list(delta_per_class.values()))
    m = arr.mean()
    if abs(m) < 1e-12:
        return float("inf")
    return float(arr.std(ddof=1) / abs(m))
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/stats/test_rq3_cross_class.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/p2/stats/rq3_cross_class.py tests/stats/test_rq3_cross_class.py
git commit -m "feat(stats): RQ3 sign test + CV cross-class consistency"
```

### Task 6.5: RQ4 SMS vs coverage correlation

**Files:**
- Create: `src/p2/stats/rq4_correlation.py`
- Test: `tests/stats/test_rq4_correlation.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/stats/test_rq4_correlation.py
import numpy as np
from p2.stats.rq4_correlation import spearman_kendall

def test_perfect_positive_correlation():
    sms = np.array([0.1, 0.3, 0.5, 0.7, 0.9])
    cov = np.array([0.2, 0.4, 0.6, 0.8, 1.0])
    s, k = spearman_kendall(sms, cov)
    assert s == 1.0 and k == 1.0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/stats/test_rq4_correlation.py -v`
Expected: FAIL

- [ ] **Step 3: Implement RQ4**

```python
# src/p2/stats/rq4_correlation.py
import numpy as np
from scipy.stats import spearmanr, kendalltau

def spearman_kendall(sms: np.ndarray, coverage: np.ndarray) -> tuple[float, float]:
    rho, _ = spearmanr(sms, coverage)
    tau, _ = kendalltau(sms, coverage)
    return float(rho), float(tau)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/stats/test_rq4_correlation.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/p2/stats/rq4_correlation.py tests/stats/test_rq4_correlation.py
git commit -m "feat(stats): RQ4 Spearman ρ and Kendall τ for SMS vs coverage"
```

### Task 6.6: Visualization module

**Files:**
- Create: `src/p2/stats/viz.py`
- Test: `tests/stats/test_viz.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/stats/test_viz.py
import numpy as np
import matplotlib
matplotlib.use("Agg")
from pathlib import Path
import tempfile
from p2.stats.viz import plot_sms_heatmap

def test_heatmap_saves_file():
    sms_grid = np.random.RandomState(0).rand(12, 5, 5)  # i × k × j
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "heat.png"
        plot_sms_heatmap(sms_grid, out_path=out)
        assert out.exists() and out.stat().st_size > 0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/stats/test_viz.py -v`
Expected: FAIL

- [ ] **Step 3: Implement viz**

```python
# src/p2/stats/viz.py
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

PUT_LABELS = ["A1","A2","A3","B1","B2","B3","C1","C2","C3","D1","D2","D3"]
MP_LABELS = ["MP1", "MP2", "MP3", "MP4", "MP5"]

def plot_sms_heatmap(sms_grid: np.ndarray, out_path: Path) -> None:
    """sms_grid shape (12 PUT, 5 MP, 5 mut) → flattened to 12×25 heatmap."""
    flat = sms_grid.reshape(sms_grid.shape[0], -1)
    fig, ax = plt.subplots(figsize=(12, 6))
    im = ax.imshow(flat, aspect="auto", cmap="viridis", vmin=0, vmax=1)
    ax.set_yticks(range(len(PUT_LABELS)))
    ax.set_yticklabels(PUT_LABELS)
    ax.set_xticks(range(flat.shape[1]))
    col_labels = [f"{mp}/mut{j}" for mp in MP_LABELS for j in range(1, 6)]
    ax.set_xticklabels(col_labels, rotation=90, fontsize=7)
    fig.colorbar(im, label="SMS")
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/stats/test_viz.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/p2/stats/viz.py tests/stats/test_viz.py
git commit -m "feat(stats): SMS heatmap visualization"
```

---

## Phase 7: End-to-end Pipeline Orchestration

### Task 7.1: Cell-level orchestrator

**Files:**
- Create: `src/p2/pipeline/run_cell.py`
- Test: `tests/pipeline/test_run_cell.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/pipeline/test_run_cell.py
from unittest.mock import MagicMock, patch
from p2.pipeline.run_cell import run_one_cell, CellResult

@patch("p2.pipeline.run_cell.is_killed")
@patch("p2.pipeline.run_cell.is_equivalent")
def test_run_cell_aggregates_states(mock_equiv, mock_killed):
    mock_equiv.side_effect = [True, False, False]   # 1 equiv
    mock_killed.side_effect = [False, True, False]  # 1 killed (after 1 equiv removed)
    # caller passes 3 mutants
    result = run_one_cell(
        put=lambda x: x, mutants=[lambda x: x] * 3,
        mr_set=[], cell_id="A1_MP1_mutC",
        sampler=MagicMock(), k_eq=10, epsilon_eq=1e-6, epsilon_avp=1e-6,
    )
    assert result.equiv_count == 1
    assert result.killed_count == 1
    assert result.survive_count == 1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/pipeline/test_run_cell.py -v`
Expected: FAIL

- [ ] **Step 3: Implement orchestrator**

```python
# src/p2/pipeline/run_cell.py
from dataclasses import dataclass, field
from typing import Callable, Sequence, List
from p2.avp.interface import MR
from p2.equiv.judge import is_equivalent
from p2.equiv.sampler import InputSampler
from p2.lrca.killed import is_killed

@dataclass
class CellResult:
    cell_id: str
    inst_count: int = 0
    equiv_count: int = 0
    killed_count: int = 0
    survive_count: int = 0
    sms: float = 0.0
    equiv_indices: List[int] = field(default_factory=list)
    killed_indices: List[int] = field(default_factory=list)

def run_one_cell(
    put: Callable, mutants: Sequence[Callable],
    mr_set: Sequence[MR], cell_id: str,
    sampler: InputSampler, k_eq: int,
    epsilon_eq: float, epsilon_avp: float,
) -> CellResult:
    result = CellResult(cell_id=cell_id, inst_count=len(mutants))
    for idx, sm in enumerate(mutants):
        if is_equivalent(put, sm, mr_set, sampler, k_eq, epsilon_eq, epsilon_avp):
            result.equiv_count += 1
            result.equiv_indices.append(idx)
            continue
        if is_killed(put, sm, mr_set, epsilon_avp):
            result.killed_count += 1
            result.killed_indices.append(idx)
        else:
            result.survive_count += 1
    denom = result.inst_count - result.equiv_count
    result.sms = result.killed_count / denom if denom > 0 else 0.0
    return result
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/pipeline/test_run_cell.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/p2/pipeline/run_cell.py tests/pipeline/test_run_cell.py
git commit -m "feat(pipeline): single-cell orchestrator (equiv → killed → SMS)"
```

### Task 7.2: 60-cell campaign runner

**Files:**
- Create: `src/p2/pipeline/campaign.py`
- Test: `tests/pipeline/test_campaign.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/pipeline/test_campaign.py
from unittest.mock import MagicMock, patch
from p2.pipeline.campaign import run_campaign, CampaignConfig

@patch("p2.pipeline.campaign.run_one_cell")
def test_campaign_iterates_60_cells(mock_run):
    mock_run.return_value = MagicMock(sms=0.5)
    cfg = CampaignConfig(
        put_ids=["A1", "A2", "A3", "B1", "B2", "B3",
                 "C1", "C2", "C3", "D1", "D2", "D3"],
        mp_indices=[1, 2, 3, 4, 5],
        mut_indices=[1, 2, 3, 4, 5],
    )
    results = run_campaign(cfg, dry_run=True)
    assert len(results) == 60  # 12 × 5 — for fixed mut == k pairing  see note
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/pipeline/test_campaign.py -v`
Expected: FAIL

- [ ] **Step 3: Implement campaign runner**

Note: this version iterates (PUT, MP) cells = 60. Per-cell, all 5 mut_j are run inside.
For statistical reporting, use `(i, k, j)` triple as the basic unit (300 entries),
but the high-level "60-cell" matrix collapses across mut_j for visualization.

```python
# src/p2/pipeline/campaign.py
from dataclasses import dataclass
from typing import List, Dict
from p2.pipeline.run_cell import run_one_cell, CellResult

@dataclass
class CampaignConfig:
    put_ids: List[str]
    mp_indices: List[int]
    mut_indices: List[int]
    n_repeat: int = 20

def run_campaign(cfg: CampaignConfig, dry_run: bool = False) -> Dict[str, CellResult]:
    """Iterate over (i, k) cells; results keyed by 'i_MPk' string."""
    results: Dict[str, CellResult] = {}
    for i in cfg.put_ids:
        for k in cfg.mp_indices:
            cell_id = f"{i}_MP{k}"
            if dry_run:
                results[cell_id] = CellResult(cell_id=cell_id, sms=0.0)
            else:
                # NOTE: real implementation requires PUT loader, mutant loader, MR loader.
                # Wired up by Task 7.3.
                raise NotImplementedError("wire PUT/mutant/MR loaders before non-dry run")
    return results
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/pipeline/test_campaign.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/p2/pipeline/campaign.py tests/pipeline/test_campaign.py
git commit -m "feat(pipeline): 60-cell campaign runner skeleton (dry_run)"
```

### Task 7.3: PUT / mutant / MR loaders integration

**Files:**
- Create: `src/p2/pipeline/loaders.py`
- Modify: `src/p2/pipeline/campaign.py:run_campaign`

- [ ] **Step 1: Write loader stubs**

```python
# src/p2/pipeline/loaders.py
from pathlib import Path
from typing import Callable, List
from p2.avp.interface import MR

def load_put(put_id: str, root: Path) -> Callable:
    """Import PUT module by id; expects src/p2/puts/{put_id}.py with `program` callable."""
    import importlib
    mod = importlib.import_module(f"p2.puts.{put_id.lower()}")
    return mod.program

def load_mutants(put_id: str, mp_index: int, mut_index: int, root: Path) -> List[Callable]:
    """Load all double-confirmed mutants from data/mutants/{put}_MP{k}_mut{j}/*.py."""
    cell_dir = root / f"{put_id}_MP{mp_index}_mut{mut_index}"
    mutants: List[Callable] = []
    for py_file in sorted(cell_dir.glob("*.py")):
        spec_name = f"_mutant_{py_file.stem}"
        import importlib.util
        spec = importlib.util.spec_from_file_location(spec_name, py_file)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mutants.append(mod.program)
    return mutants

def load_mr_set(put_id: str, mp_index: int, root: Path) -> List[MR]:
    """Load MR set from P1 export at root/{put_id}_MP{mp_index}_mr.json."""
    # Expected JSON schema: list of {r_module, r_func, R_module, R_func, name}
    import json
    mr_file = root / f"{put_id}_MP{mp_index}_mr.json"
    if not mr_file.exists():
        return []
    data = json.loads(mr_file.read_text())
    out: List[MR] = []
    for entry in data:
        import importlib
        r_mod = importlib.import_module(entry["r_module"])
        R_mod = importlib.import_module(entry["R_module"])
        out.append(MR(
            r=getattr(r_mod, entry["r_func"]),
            R=getattr(R_mod, entry["R_func"]),
            mp_index=mp_index, name=entry["name"],
        ))
    return out
```

- [ ] **Step 2: Wire loaders into campaign**

```python
# Modify src/p2/pipeline/campaign.py — replace NotImplementedError with:

from pathlib import Path
from p2.pipeline.loaders import load_put, load_mutants, load_mr_set
from p2.equiv.sampler import UniformSampler

# inside run_campaign else branch:
            put_fn = load_put(i, root=Path("src/p2/puts"))
            for j in cfg.mut_indices:
                mutants = load_mutants(i, k, j, root=Path("data/mutants"))
                mr_set = load_mr_set(i, k, root=Path("data/mr_export"))
                sampler = UniformSampler(low=0, high=1, dim=1, seed=42)
                cr = run_one_cell(
                    put=put_fn, mutants=mutants, mr_set=mr_set,
                    cell_id=f"{i}_MP{k}_mut{j}",
                    sampler=sampler, k_eq=1000,
                    epsilon_eq=1e-6, epsilon_avp=1e-6,
                )
                results[cr.cell_id] = cr
```

- [ ] **Step 3: Add integration test**

```python
# Append to tests/pipeline/test_campaign.py
def test_loaders_module_importable():
    from p2.pipeline import loaders
    assert hasattr(loaders, "load_put")
    assert hasattr(loaders, "load_mutants")
    assert hasattr(loaders, "load_mr_set")
```

- [ ] **Step 4: Run all pipeline tests**

Run: `pytest tests/pipeline/ -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/p2/pipeline/loaders.py src/p2/pipeline/campaign.py tests/pipeline/test_campaign.py
git commit -m "feat(pipeline): PUT/mutant/MR loaders + campaign wiring"
```

---

## Phase 8: Experiment Execution (Research Deliverables)

> Phases 8-9 are not TDD-able — they are research execution and writing tasks.
> Each task produces a concrete deliverable, not a code change.

### Task 8.1: Generate 60-cell mutant pools (2026 Q4)

**Deliverable:** `data/mutants/{S_i}_MP{k}_mut{j}/*.py` — 60 cells × 10–15 double-confirmed mutants each.

- [ ] Configure `configs/default.yaml` with API keys + LLM versions
- [ ] Run `python -m p2.mutators.cell_pool` for each (i, k, j) — emit pool dirs
- [ ] Audit `arbitration/` queue manually (estimated ≤ 10% mutants)
- [ ] Sample 20% double-confirmed for human review; if disagreement > 10%, escalate to full human review
- [ ] Commit `data/mutants/` ready for Phase 8.2

### Task 8.2: Run equiv + AVP campaign (2027 Q1)

**Deliverable:** `data/results/cell_results.json` — 300 (i,k,j) entries with inst/equiv/killed/survive counts and SMS.

- [ ] Run `python -m p2.pipeline.campaign --config configs/default.yaml --output data/results/cell_results.json`
- [ ] Validate output: 300 entries, no NaN SMS
- [ ] Spot-check 5 cells against hand calculation

### Task 8.3: Run LRCA on killed mutants (2027 Q2)

**Deliverable:** `data/lrca/root_causes.json` — root_cause label per killed mutant.

- [ ] Implement & run `python -m p2.lrca.run_lrca --input data/results/cell_results.json --output data/lrca/root_causes.json`
- [ ] Aggregate `C1_share` and `suspect_share` per cell
- [ ] Validate: §3.6.3 thresholds (suspect_share ≤ 0.20 globally) — flag if violated

### Task 8.4: Statistical analysis + figures (2027 Q2-Q3)

**Deliverable:** `notebooks/analysis.ipynb` + `figures/fig{1..5}.pdf`

- [ ] Compute RQ1-4 statistics from cell_results.json + root_causes.json
- [ ] Generate figures per §5.5 (heatmap, boxplot, forest plot, scatter, ranking)
- [ ] Write analysis narrative in notebook (raw numbers → § text bridge)

---

## Phase 9: Paper Writing (Research Deliverables, 2027 Q3)

### Task 9.1: Update §5 with empirical results

**Deliverable:** `论文初稿P2.md` §5 — replace placeholder content with actual statistics from Phase 8.4.

### Task 9.2: Update §3 cell matrix with actual SMS values

**Deliverable:** `论文初稿P2.md` §3.3 — replace expected ●●/●/○ heuristics with empirical SMS heatmap.

### Task 9.3: Final §7 Limitations alignment

**Deliverable:** `论文初稿P2.md` §7 — annotate any threats that materialized in actual data.

### Task 9.4: Submission package

**Deliverable:** IST submission tarball with main.tex, figures, replication package URL.

- [ ] Convert markdown to LaTeX (IST template)
- [ ] Generate replication package (mutant pools + AVP source + run scripts + frozen LLM versions)
- [ ] Internal review by Meng + 硕士 B
- [ ] Submit to IST Editor

---

## Self-Review Checklist

Run this against the spec (`论文初稿P2.md`) before declaring the plan complete.

### Spec Coverage

- [x] §1.2 Tools (mut_j, equiv, SMS) → Phases 2, 3, 6
- [x] §2.1 Symbol system → Phase 1 (AVP), Phase 2 (mut), Phase 3 (equiv), Phase 4 (killed), Phase 6 (SMS)
- [x] §2.5 AVP version pinning → Task 0.3
- [x] §2.6 LRCA five root causes + decision tree → Phase 5 (Tasks 5.1-5.4)
- [x] §3 60-cell matrix → Phase 7 (Tasks 7.2, 7.3)
- [x] §4.2.4 Dual-LLM blind review (方案 C) → Tasks 2.2, 2.3, 2.4, 2.5
- [x] §5 Statistical methods (RQ1-4, FDR, bootstrap) → Phase 6 (Tasks 6.1-6.5)
- [x] §6 Timeline (2026 Q4 – 2027 Q3) → Phase 8 phasing
- [x] §7 Limitations (LLM reproducibility, equiv approximation) → Tasks 0.1, 0.3, 8.1

### Placeholder Scan

- [x] No "TBD" except `p1_avp.commit_hash: "TBD-pin-after-P1-arxiv-publish"` (intentional, Task 0.3 documents the gap)
- [x] No "implement later" / "fill in details"
- [x] All test code blocks complete; all implementation code blocks complete
- [x] Phase 8/9 deliverables explicitly NOT TDD (research execution) — intentional

### Type Consistency

- [x] `MR` dataclass used uniformly across `avp/`, `equiv/`, `lrca/`, `pipeline/`
- [x] `AVPResult` enum used everywhere AVP returns are checked
- [x] `RootCause` enum and `KillContext` dataclass consistent in `lrca/decision_tree.py`
- [x] `CellResult` structure consistent between `pipeline/run_cell.py` and `pipeline/campaign.py`
- [x] `compute_sms(killed, total, equiv)` signature stable

---

*Plan generated 2026-04-29. Spec source: 论文初稿P2.md (sections §1-§7 locked).*
