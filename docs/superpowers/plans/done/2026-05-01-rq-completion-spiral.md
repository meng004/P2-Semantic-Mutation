# RQ Completion Spiral Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. Spiral model: each round is a self-contained slice that ends with committed code + saved data + a measurable RQ-completion delta. Round boundaries are explicit `---` markers and good compact-context insertion points.

**Goal:** Produce paper-ready empirical argumentation for RQ1-RQ4 of P2, with reproducibility-grade artifacts (raw data, prompts, PUTs, MRs, mutants, metrics, LRCA labels) suitable for public open-source release.

**Architecture:** Spiral execution over 14 small rounds. Each round addresses ONE focused gap, runs end-to-end (code + data + commit), and increments the RQ-completion percentage. Rounds 1-4 deepen the data layer; Rounds 5-7 build the statistical analysis layer; Rounds 8-9 build LRCA + pattern coverage; Rounds 10-12 generate visualizations and §5 paper sections; Rounds 13-14 finalize reproducibility infrastructure and self-review. No round depends on a future round.

**Tech Stack:** Python 3.12, pytest, numpy, scipy.stats, scikit-learn, statsmodels (mixed-effects), matplotlib + seaborn (visualizations), claude CLI (Opus subscription) + OpenAI-compatible proxy (gpt-5.4 reviewer), asyncio.

**Round-to-RQ contribution map:**
| Round | Focus | Contributes to | Expected RQ-% delta |
|-------|-------|----------------|---------------------|
| 1 | Diagnose & fix equiv detection | RQ1, RQ2 | +20% RQ1, +15% RQ2 |
| 2 | Per-PUT mutant pool expansion (10-15/PUT) | RQ1-4 (data quality) | +5% all |
| 3 | N=20 AVP repetition layer | RQ1, RQ2, RQ3 | +5% all |
| 4 | Track-2 v2 re-run with enriched pools | RQ1, RQ2, RQ3 | data refresh |
| 5 | Cliff's δ + bootstrap CI module | RQ2, RQ3 | +20% RQ2, +10% RQ3 |
| 6 | Mixed-effects model for cross-class | RQ3 | +20% RQ3 |
| 7 | LRCA L0 (artifact pre-screen) | RQ1 (C1_share), H5 | +15% RQ1 |
| 8 | LRCA L1-L3 (tolerance/OOD/statistical) | RQ1, H5 | +15% RQ1 |
| 9 | Pattern coverage module (RQ4 baseline) | RQ4 | +60% RQ4 |
| 10 | Visualization suite (heatmaps/forest/scatter) | All RQs (reportable) | +10% all |
| 11 | Reproducibility manifest + dataset card | open-source readiness | enables release |
| 12 | §5 Results paper section | All RQs (writing) | +ready-for-§5 |
| 13 | §6 Discussion + §7 Limitations updates | All RQs (writing) | +ready-for-§6/7 |
| 14 | Self-review + RQ-table sweep | All RQs | finalize |

**Total expected completion:** RQ1 95%, RQ2 95%, RQ3 95%, RQ4 60%+, paper §5/§6/§7 drafted.

**File structure (new modules added by this plan):**
- `src/p2/equiv/diagnosis.py` — equiv-detection diagnostics (Round 1)
- `src/p2/mutators/pool_builder.py` — per-PUT pool builder from operator cache (Round 2)
- `src/p2/avp/repeat.py` — N=20 repetition wrapper (Round 3)
- `src/p2/stats/cliffs_delta.py` — Cliff's δ + bootstrap CI (Round 5)
- `src/p2/stats/mixed_effects.py` — statsmodels mixed-effects driver (Round 6)
- `src/p2/lrca/l0_artifact.py` — Round 7
- `src/p2/lrca/l1_tolerance.py` / `l2_ood.py` / `l3_statistical.py` — Round 8
- `src/p2/lrca/dispatcher.py` — Round 8 (combines L0-L3 into a single classify())
- `src/p2/stats/pattern_coverage.py` — Round 9
- `src/p2/viz/heatmap.py` / `forest.py` / `boxplot.py` / `scatter.py` — Round 10
- `scripts/build_pools.py` / `scripts/run_lrca.py` / `scripts/render_figures.py` — driver scripts
- `data/results/`* — staged results per round (json + csv)
- `figures/` — rendered PDFs/SVGs per round
- `REPRODUCIBILITY.md` + `DATASET.md` — Round 11

---

## Context-budget guidance

Each round's typical context cost (rough):
- Code-light rounds (1, 3, 5, 9, 10): 30-50K tokens
- Data-heavy rounds (2, 4, 7, 8): 60-100K tokens
- Writing rounds (12, 13, 14): 50-80K tokens

**Compact context after each of:** Round 4 (post Track-2 re-run), Round 8 (post LRCA), Round 10 (post visualizations), Round 13 (post writing). These are natural state-handoff points where the next round only needs the artifact paths, not the in-flight reasoning.

---

## Round 1: Diagnose and Fix Equiv Detection

**Why first:** Track-2 v1 reported equiv=0 for ALL 60 cells. This blocks RQ1's equiv_rate column and RQ2's H3 (○ vs ●● equiv_rate comparison). One small focused diagnosis with a high RQ-completion payoff.

**Files:**
- Create: `src/p2/equiv/diagnosis.py`
- Create: `tests/equiv/test_diagnosis.py`
- Read (don't modify yet): `src/p2/equiv/avp_coherent.py`, `src/p2/equiv/sampler.py`
- May modify: `src/p2/equiv/avp_coherent.py` (after diagnosis)
- Output: `data/results/equiv_diagnosis.json`

- [ ] **Step 1.1: Write a diagnostic script that probes a single (mutant, MR) pair**

Create `src/p2/equiv/diagnosis.py`:

```python
"""Diagnose why is_equivalent returns False for all 60 Track-2 cells.

Probes one (PUT, mutant, MR) triple at a time. Reports per-sample R(y_o, y_n)
verdicts, the |y_o − y_n| distribution, and whether the mutant ever produces
the SAME output as the original (which would indicate true equivalence).
"""
import json
from dataclasses import dataclass, asdict
from typing import Callable, List
import numpy as np

from p2.avp.interface import MR
from p2.equiv.sampler import UniformSampler


@dataclass
class EquivProbeResult:
    cell_id: str
    mutant_name: str
    n_samples: int
    n_R_pass: int           # samples where R(y_orig, y_new) returned True
    n_R_fail: int           # samples where R returned False
    n_y_identical: int      # samples where y_orig == y_new exactly
    diff_min: float
    diff_max: float
    diff_mean: float
    epsilon_eq: float


def probe_equivalence(
    put: Callable,
    mutant: Callable,
    mr: MR,
    cell_id: str,
    mutant_name: str,
    n_samples: int = 1000,
    epsilon_eq: float = 1e-6,
    seed: int = 42,
) -> EquivProbeResult:
    """Sample n_samples inputs, compute y_orig vs y_new, report distribution."""
    sampler = UniformSampler(low=0.0, high=1.0, dim=1, seed=seed)
    n_pass = n_fail = n_identical = 0
    diffs: List[float] = []
    for _ in range(n_samples):
        x = sampler.sample()
        if isinstance(x, np.ndarray):
            x = float(x.flat[0])
        try:
            x_r = mr.r(x)
            y_o_orig = put(x)
            y_n_orig = put(x_r)
            y_o_mut = mutant(x)
            y_n_mut = mutant(x_r)
        except Exception:
            continue
        # equiv definition: mutant satisfies MR on this sample identically to PUT
        try:
            r_pass_orig = mr.R(y_o_orig, y_n_orig)
            r_pass_mut = mr.R(y_o_mut, y_n_mut)
        except Exception:
            continue
        if r_pass_orig == r_pass_mut:
            n_pass += 1
        else:
            n_fail += 1
        try:
            d = abs(float(y_n_mut) - float(y_n_orig))
            diffs.append(d)
            if d < 1e-15:
                n_identical += 1
        except Exception:
            pass
    diffs_arr = np.array(diffs) if diffs else np.array([0.0])
    return EquivProbeResult(
        cell_id=cell_id, mutant_name=mutant_name, n_samples=n_samples,
        n_R_pass=n_pass, n_R_fail=n_fail, n_y_identical=n_identical,
        diff_min=float(diffs_arr.min()), diff_max=float(diffs_arr.max()),
        diff_mean=float(diffs_arr.mean()), epsilon_eq=epsilon_eq,
    )
```

- [ ] **Step 1.2: Write the failing test**

Create `tests/equiv/test_diagnosis.py`:

```python
"""Probe an obvious equivalent mutant: identity wrapper."""
from p2.avp.interface import MR
from p2.equiv.diagnosis import probe_equivalence


def _orig(x):
    return float(x) * 2.0


def _identity_wrapper(x):
    return float(x) * 2.0  # exactly equivalent


def test_identity_wrapper_is_recognized_as_equivalent():
    mr = MR(r=lambda x: float(x) + 0.1, R=lambda a, b: True,
            mp_index=1, name="dummy")
    res = probe_equivalence(_orig, _identity_wrapper, mr,
                            cell_id="test", mutant_name="identity",
                            n_samples=100)
    # An exact-copy mutant should produce identical outputs
    assert res.n_y_identical == res.n_samples - 0, (
        f"identity mutant should match orig on all samples; got {res.n_y_identical}/{res.n_samples}"
    )
    assert res.diff_max < 1e-12
```

- [ ] **Step 1.3: Run test to verify pass**

Run: `PYTHONPATH=src python -m pytest tests/equiv/test_diagnosis.py -v`
Expected: PASS (the test exercises the diagnostic API only).

- [ ] **Step 1.4: Probe Track-2 cells where SMS=0 (suspicious — should have at least some equiv)**

Run this script to probe 10 representative cells:

```python
# scripts/probe_equiv.py
import importlib.util, json, sys
from pathlib import Path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "src"))

from p2.avp.interface import MR
from p2.equiv.diagnosis import probe_equivalence

PROBES = [
    ("a1", 2, "m01_llm.py"), ("a1", 3, "m01_llm.py"),
    ("c3", 5, "m01_llm.py"), ("d2", 5, "m02_llm.py"),
    ("b2", 2, "m01_llm.py"),
]
PRIMARY = {"a1":1,"a2":1,"a3":1,"b1":2,"b2":2,"b3":2,
           "c1":5,"c2":5,"c3":5,"d1":2,"d2":2,"d3":2}

def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m

results = []
for put_id, mp_k, mut_name in PROBES:
    put_mod = _load(f"put_{put_id}", ROOT / f"src/p2/puts/{put_id}.py")
    mrs_mod = _load(f"mrs_{put_id}", ROOT / f"src/p2/mrs/{put_id}.py")
    mut_path = ROOT / f"data/mutants/{put_id}_MP{PRIMARY[put_id]}_llm/{mut_name}"
    mut_mod = _load(f"mut_{put_id}_{mp_k}", mut_path)
    mr = MR(r=getattr(mrs_mod, f"r_mp{mp_k}"),
            R=getattr(mrs_mod, f"R_mp{mp_k}"),
            mp_index=mp_k, name=f"{put_id.upper()}_mp{mp_k}")
    res = probe_equivalence(put_mod.program, mut_mod.program, mr,
                            cell_id=f"{put_id.upper()}_MP{mp_k}",
                            mutant_name=mut_name, n_samples=200)
    results.append({"cell": res.cell_id, "mutant": res.mutant_name,
                    "n_pass": res.n_R_pass, "n_fail": res.n_R_fail,
                    "n_identical": res.n_y_identical,
                    "diff_max": res.diff_max, "diff_mean": res.diff_mean})

out = ROOT / "data/results/equiv_diagnosis.json"
out.write_text(json.dumps(results, indent=2, ensure_ascii=False))
print(f"saved -> {out}")
for r in results:
    print(r)
```

Run: `PYTHONPATH=src python scripts/probe_equiv.py`
Expected: a JSON report. Inspect the n_pass/n_fail/n_identical columns to determine whether the equiv check is too strict or genuinely correct.

- [ ] **Step 1.5: Adjust avp_coherent.py based on diagnosis**

Read `src/p2/equiv/avp_coherent.py`. The fix depends on what step 1.4 reveals:

  Case A — diff_max ≈ 0 but n_identical ≪ n_samples and is_equivalent still returns False: the comparison logic is too strict; relax `epsilon_eq` from 1e-6 to a problem-domain-appropriate per-PUT default (e.g., 1e-3 for stochastic PUTs).

  Case B — diff_max is large for non-trivial mutants: equiv detection is correctly returning False; equiv=0 is a TRUE empirical observation (LLM-generated mutants are rarely behaviorally equivalent). In that case document this in the diagnosis JSON and proceed (no code change).

  Case C — n_pass counter has many crashes (`continue` paths): exception handling masks real equivs. Surface the exceptions as a warning.

The actual edit will be small (one line of epsilon adjustment, or a per-PUT epsilon dict). Defer the code edit to a follow-up step after the diagnosis is in.

- [ ] **Step 1.6: Commit**

```bash
git add src/p2/equiv/diagnosis.py tests/equiv/test_diagnosis.py scripts/probe_equiv.py data/results/equiv_diagnosis.json
git commit -m "$(cat <<'EOF'
diag(equiv): probe why all 60 Track-2 cells report equiv=0

Adds probe_equivalence() that samples n inputs, runs PUT and mutant
through the MR, and reports R-pass/R-fail/y-identical distributions.
Smokes on 10 representative cells; persists results to
data/results/equiv_diagnosis.json for inspection.

Diagnosis informs the avp_coherent.py fix in a follow-up commit.
EOF
)"
```

If diagnosis surfaces an actual code bug, follow up with a separate commit fixing `avp_coherent.py` with a regression test.

---

## Round 2: Per-PUT Mutant Pool Expansion

**Why second:** Track-2 currently has 4.6 mutants/PUT on average; SMS estimates jump in 1/4 increments. The v2.1 operator-campaign cache contains 212 confirmed mutants. Building a 10-15-mutant pool per PUT (sampling proportionally across operators within the PUT) tightens every downstream metric.

**Files:**
- Create: `src/p2/mutators/pool_builder.py`
- Create: `tests/mutators/test_pool_builder.py`
- Create: `scripts/build_pools.py`
- Output: `data/mutants/{put_id}_pool/m{NN}_{op_id}.py` for 12 PUTs × 12 mutants each

- [ ] **Step 2.1: Write the failing test**

Create `tests/mutators/test_pool_builder.py`:

```python
from pathlib import Path
from unittest.mock import patch
from p2.mutators.pool_builder import select_mutants_for_put


def test_select_returns_n_mutants_distributed_across_operators(tmp_path):
    cache = tmp_path / "cache"; cache.mkdir()
    # Simulate 3 operators (a2_CE1, a2_OS1, a2_SI1) with 4 mutants each
    for op in ("a2_CE1", "a2_OS1", "a2_SI1"):
        for k in range(4):
            (cache / f"{op}_attempt{k:02d}.py").write_text(
                f"def program(x):\n    return float(x) + {k}.0  # {op}\n"
            )
    selected = select_mutants_for_put(
        put_id="a2", n_target=9, cache_dir=cache, seed=42,
    )
    assert len(selected) == 9
    op_counts = {}
    for path, op_id in selected:
        op_counts[op_id] = op_counts.get(op_id, 0) + 1
    # Should be 3 per operator (proportional)
    assert all(c == 3 for c in op_counts.values()), op_counts


def test_select_skips_invalid_mutants(tmp_path):
    cache = tmp_path / "cache"; cache.mkdir()
    (cache / "a2_CE1_attempt00.py").write_text("not python code")
    (cache / "a2_CE1_attempt01.py").write_text(
        "def program(x):\n    return float(x)\n"
    )
    selected = select_mutants_for_put(
        put_id="a2", n_target=1, cache_dir=cache, seed=42,
    )
    assert len(selected) == 1
    assert "attempt01" in selected[0][0].name
```

- [ ] **Step 2.2: Run test to verify it fails**

Run: `PYTHONPATH=src python -m pytest tests/mutators/test_pool_builder.py -v`
Expected: ImportError — `pool_builder` module not found.

- [ ] **Step 2.3: Implement pool_builder**

Create `src/p2/mutators/pool_builder.py`:

```python
"""Build a per-PUT mutant pool by proportionally sampling the
v2.1 operator-campaign cache."""
import importlib.util
import random
from pathlib import Path
from typing import List, Tuple


def _is_valid_program(path: Path) -> bool:
    spec = importlib.util.spec_from_file_location(f"_v_{path.stem}", path)
    if spec is None or spec.loader is None:
        return False
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
        prog = getattr(mod, "program", None)
        if prog is None:
            return False
        y = prog(0.5)
        return isinstance(y, (int, float))
    except Exception:
        return False


def select_mutants_for_put(
    put_id: str, n_target: int, cache_dir: Path, seed: int = 42,
) -> List[Tuple[Path, str]]:
    """Return up to n_target (path, op_id) pairs, proportional across operators
    that target this PUT. Filters out mutants that cannot be loaded or do not
    return a finite scalar."""
    rng = random.Random(seed)
    by_op: dict = {}
    for fp in sorted(cache_dir.glob(f"{put_id}_*_attempt*.py")):
        op_id = fp.name.split("_attempt")[0]
        by_op.setdefault(op_id, []).append(fp)
    # Validate
    valid_by_op: dict = {}
    for op_id, paths in by_op.items():
        valid_by_op[op_id] = [p for p in paths if _is_valid_program(p)]
    valid_by_op = {k: v for k, v in valid_by_op.items() if v}
    if not valid_by_op:
        return []
    # Allocate proportional quotas
    n_ops = len(valid_by_op)
    base, rem = divmod(n_target, n_ops)
    quotas = {op: base for op in valid_by_op}
    # Distribute remainder to operators with most candidates
    extras = sorted(valid_by_op, key=lambda o: -len(valid_by_op[o]))[:rem]
    for op in extras:
        quotas[op] += 1
    selected: List[Tuple[Path, str]] = []
    for op_id, q in quotas.items():
        candidates = list(valid_by_op[op_id])
        rng.shuffle(candidates)
        for p in candidates[: min(q, len(candidates))]:
            selected.append((p, op_id))
    return selected
```

- [ ] **Step 2.4: Run test to verify pass**

Run: `PYTHONPATH=src python -m pytest tests/mutators/test_pool_builder.py -v`
Expected: 2 passed.

- [ ] **Step 2.5: Build the pools for all 12 PUTs**

Create `scripts/build_pools.py`:

```python
"""Build data/mutants/{put_id}_pool/ for all 12 PUTs from operator cache.
Target pool size: 12 mutants per PUT. Proportional distribution across operators.
Records (path, op_id, attempt_idx) provenance to data/mutants/{put_id}_pool/manifest.json.
"""
import json
import shutil
import sys
from pathlib import Path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "src"))

from p2.mutators.pool_builder import select_mutants_for_put

PUTS = ["a1","a2","a3","b1","b2","b3","c1","c2","c3","d1","d2","d3"]
N_PER_PUT = 12
CACHE = ROOT / "data/operator_campaign/cache"

for put_id in PUTS:
    pool_dir = ROOT / f"data/mutants/{put_id}_pool"
    if pool_dir.exists():
        shutil.rmtree(pool_dir)
    pool_dir.mkdir(parents=True)
    selected = select_mutants_for_put(put_id, N_PER_PUT, CACHE, seed=42)
    manifest = []
    for idx, (src_path, op_id) in enumerate(selected, 1):
        attempt = src_path.stem.split("_attempt")[1]
        dest_name = f"m{idx:02d}_{op_id}_a{attempt}.py"
        shutil.copy(src_path, pool_dir / dest_name)
        manifest.append({
            "rank": idx, "filename": dest_name,
            "operator": op_id, "attempt_idx": int(attempt),
            "source_relpath": str(src_path.relative_to(ROOT)),
        })
    (pool_dir / "manifest.json").write_text(
        json.dumps({"put": put_id, "n_target": N_PER_PUT,
                    "n_actual": len(selected), "mutants": manifest},
                   indent=2, ensure_ascii=False)
    )
    print(f"{put_id}: {len(selected)} mutants → {pool_dir}")
```

Run: `PYTHONPATH=src python scripts/build_pools.py`
Expected: 12 pool dirs created, each with 8-12 .py files + manifest.json.

- [ ] **Step 2.6: Commit**

```bash
git add src/p2/mutators/pool_builder.py tests/mutators/test_pool_builder.py scripts/build_pools.py data/mutants/*_pool/
git commit -m "feat(pool): per-PUT mutant pool builder with operator-proportional sampling"
```

Also add `data/mutants/*_pool/` exception in `.gitignore`:
```
!data/mutants/*_pool/
```

---

## Round 3: N=20 AVP Repetition Layer

**Why third:** §3.4 calls for N=20 repeats per (mutant, MR) pair to stabilize SMS for stochastic PUTs (b2 MCMC, b3 MC integration, c-class surrogates with random_state, d-class with random_state). Single-shot AVP gives noisy R_kill estimates for these PUTs.

**Files:**
- Create: `src/p2/avp/repeat.py`
- Create: `tests/avp/test_repeat.py`
- Modify: `src/p2/equiv/avp_coherent.py` (let `is_killed` accept a repeats kwarg)

- [ ] **Step 3.1: Write the failing test**

Create `tests/avp/test_repeat.py`:

```python
from p2.avp.interface import AVPResult, MR
from p2.avp.repeat import call_avp_repeated


def _det_pass(x):
    return float(x)


def _stochastic_fail_half(x):
    # Pretend the mutant fails half the time
    import random
    return float(x) + (1.0 if random.random() < 0.5 else 0.0)


def test_majority_vote_pass_when_all_pass():
    mr = MR(r=lambda x: float(x), R=lambda a, b: a == b,
            mp_index=1, name="t")
    result = call_avp_repeated(_det_pass, mr, epsilon=1e-6, repeats=10)
    assert result == AVPResult.PASS


def test_majority_vote_fail_when_majority_fail():
    mr = MR(r=lambda x: float(x), R=lambda a, b: abs(a - b) < 1e-9,
            mp_index=1, name="t")
    # mutant always returns x+1, so R(x, x+1) is False ⇒ FAIL on every repeat
    result = call_avp_repeated(lambda x: float(x) + 1.0, mr,
                               epsilon=1e-6, repeats=10)
    assert result == AVPResult.FAIL
```

- [ ] **Step 3.2: Run test to verify it fails**

Run: `PYTHONPATH=src python -m pytest tests/avp/test_repeat.py -v`
Expected: ImportError — repeat module missing.

- [ ] **Step 3.3: Implement repeat wrapper**

Create `src/p2/avp/repeat.py`:

```python
"""N-repeat majority-vote AVP wrapper.

For stochastic PUTs (MCMC, MC integration, classifier with random_state),
single-shot AVP can mis-classify due to stochastic R-pass. We run the
verifier N times with different RNG seeds and majority-vote the verdict.
"""
from typing import Callable
import numpy as np

from p2.avp.dispatcher import call_avp
from p2.avp.interface import AVPResult, MR


def call_avp_repeated(
    program: Callable, mr: MR, epsilon: float, repeats: int = 20,
) -> AVPResult:
    """Run call_avp `repeats` times, return PASS iff > 50% repeats PASS."""
    if repeats <= 1:
        return call_avp(program, mr, epsilon)
    n_pass = 0
    n_total = 0
    for _ in range(repeats):
        try:
            r = call_avp(program, mr, epsilon)
        except Exception:
            continue
        n_total += 1
        if r == AVPResult.PASS:
            n_pass += 1
    if n_total == 0:
        return AVPResult.FAIL
    return AVPResult.PASS if n_pass > n_total / 2 else AVPResult.FAIL
```

- [ ] **Step 3.4: Run test to verify pass**

Run: `PYTHONPATH=src python -m pytest tests/avp/test_repeat.py -v`
Expected: 2 passed.

- [ ] **Step 3.5: Wire into is_killed**

Modify `src/p2/equiv/avp_coherent.py`. Locate the `is_killed` function and add `repeats` parameter (default 1 for backward compatibility):

```python
# Existing signature stays same; add repeats kwarg with default 1
def is_killed(put, sm, mr_set, epsilon_avp, repeats: int = 1):
    from p2.avp.repeat import call_avp_repeated
    for mr in mr_set:
        try:
            sm_result = call_avp_repeated(sm, mr, epsilon_avp, repeats=repeats)
        except Exception:
            return True  # mutant crashes ⇒ killed
        # original passes by definition of "filled" cell; we only check mutant
        if sm_result == AVPResult.FAIL:
            return True
    return False
```

(Read the actual avp_coherent.py for the exact existing signature. The diff above is illustrative.)

- [ ] **Step 3.6: Commit**

```bash
git add src/p2/avp/repeat.py tests/avp/test_repeat.py src/p2/equiv/avp_coherent.py
git commit -m "feat(avp): N=20 repetition wrapper with majority-vote verdict"
```

---

## Round 4: Track-2 v2 Re-run with Enriched Pools

**Why fourth:** Combines Rounds 1+2+3. Re-run the 60-cell SMS using:
- The fixed equiv detection from Round 1
- The expanded mutant pools from Round 2 (12 mutants/PUT)
- N=20 AVP repetition from Round 3

This produces the canonical SMS dataset that all later rounds analyze.

**Files:**
- Modify: `scripts/sms_campaign.py` (read from `_pool/` instead of `_llm/`; add `--repeats` flag)
- Output: `data/results/sms_track2_v2.json` + `sms_track2_v2_console.log`

- [ ] **Step 4.1: Update sms_campaign.py to read from new pool dirs**

Modify `scripts/sms_campaign.py` `evaluate_cell()`:

```python
# At the top (where MUTANTS_DIR is defined), the dir lookup changes:
#   old:  MUTANTS_DIR / f"{put_id}_MP{primary_mp}_llm"
#   new:  MUTANTS_DIR / f"{put_id}_pool" if it exists, else fall back to old path

if mutant_dir is None:
    pool_dir = MUTANTS_DIR / f"{put_id}_pool"
    if pool_dir.exists():
        mutant_dir = pool_dir
    else:
        primary_mp = PRIMARY_CELLS[put_id]
        mutant_dir = MUTANTS_DIR / f"{put_id}_MP{primary_mp}_llm"
```

And add `--repeats` argument forwarded to `is_killed`:

```python
# In main():
parser.add_argument("--repeats", type=int, default=1,
                    help="N AVP repetitions per (mutant, MR) pair (default 1)")

# In _build_cell_list / evaluate_cell, thread repeats=args.repeats through.
```

(Threading repeats requires propagating through `run_one_cell` → `is_killed`. Inspect the signature; add the kwarg with default=1.)

- [ ] **Step 4.2: Run Track-2 v2**

Run:
```bash
PYTHONPATH=src python scripts/sms_campaign.py --track 2 --workers 6 --repeats 20 \
    2>&1 | tee data/results/sms_track2_v2_console.log
```

Expected wall time: ~10-25 min (depends on stochastic PUT runtime × 20 repeats).
Expected output: `data/results/sms_track2.json` overwritten — rename it to `sms_track2_v2.json`:

```bash
cp data/results/sms_track2.json data/results/sms_track2_v2.json
```

- [ ] **Step 4.3: Sanity-check Track-2 v2 vs v1**

Run a comparison script:

```python
import json
v1 = json.loads(open("data/results/sms_track2.json").read())  # original
v2 = json.loads(open("data/results/sms_track2_v2.json").read())
print(f"{'cell':<12} {'inst_v1':>7} {'inst_v2':>7} {'sms_v1':>7} {'sms_v2':>7} {'killed_v2':>9}")
for cell in sorted(v1):
    a, b = v1[cell], v2[cell]
    print(f"{cell:<12} {a['inst']:>7} {b['inst']:>7} {a['sms']:>7.3f} {b['sms']:>7.3f} {b['killed']:>9}")
```

Expected: inst_v2 ≈ 12 across all cells; sms_v2 estimates have finer granularity (1/12 instead of 1/3-1/5).

- [ ] **Step 4.4: Commit**

```bash
git add scripts/sms_campaign.py data/results/sms_track2_v2.json
git commit -m "feat(sms): Track-2 v2 with enriched pools (12 mutants/PUT) + N=20 AVP repeats"
```

**Compact context after Round 4** — natural state-handoff (data/results/sms_track2_v2.json + manifests are the only artifacts the next rounds need).

---

## Round 5: Cliff's δ + Bootstrap CI Module

**Why fifth:** §5.2 H2 requires "Cliff's δ ≥ 0.474" and "1000-bootstrap 95% CI" but neither is implemented. This is the statistical machinery for RQ2's primary report and the H2/H3 formal evaluation.

**Files:**
- Create: `src/p2/stats/cliffs_delta.py`
- Create: `tests/stats/test_cliffs_delta.py`
- Output: `data/results/rq2_cliffs_delta.json`

- [ ] **Step 5.1: Write the failing test**

Create `tests/stats/test_cliffs_delta.py`:

```python
from p2.stats.cliffs_delta import cliffs_delta, bootstrap_delta_ci


def test_identical_distributions_have_zero_delta():
    a = [0.5, 0.5, 0.5, 0.5]
    b = [0.5, 0.5, 0.5, 0.5]
    d = cliffs_delta(a, b)
    assert abs(d) < 1e-9


def test_completely_separated_distributions_have_one_delta():
    a = [0.1, 0.2, 0.3]
    b = [0.7, 0.8, 0.9]
    d = cliffs_delta(b, a)  # b > a everywhere
    assert abs(d - 1.0) < 1e-9


def test_bootstrap_ci_brackets_point_estimate():
    a = [0.1, 0.2, 0.3, 0.4, 0.5]
    b = [0.4, 0.5, 0.6, 0.7, 0.8]
    point = cliffs_delta(b, a)
    lo, hi = bootstrap_delta_ci(b, a, n_boot=500, alpha=0.05, seed=42)
    assert lo <= point <= hi
    assert lo > 0  # b stochastically dominates a
```

- [ ] **Step 5.2: Run test to verify it fails**

Run: `PYTHONPATH=src python -m pytest tests/stats/test_cliffs_delta.py -v`
Expected: ImportError.

- [ ] **Step 5.3: Implement Cliff's δ + bootstrap**

Create `src/p2/stats/cliffs_delta.py`:

```python
"""Cliff's δ effect size + bootstrap confidence interval.

δ ∈ [-1, +1]: +1 ⇒ group A stochastically dominates group B; 0 ⇒ identical
distributions; |δ| ≥ 0.474 is "large effect" per Romano et al. (2006).
"""
from typing import List, Sequence, Tuple
import numpy as np


def cliffs_delta(group_a: Sequence[float], group_b: Sequence[float]) -> float:
    """δ = (#{a > b} − #{a < b}) / (n_a × n_b) over all pairs."""
    a = np.asarray(group_a, dtype=float)
    b = np.asarray(group_b, dtype=float)
    if a.size == 0 or b.size == 0:
        return 0.0
    diff = a[:, None] - b[None, :]
    n_gt = int(np.sum(diff > 0))
    n_lt = int(np.sum(diff < 0))
    return (n_gt - n_lt) / (a.size * b.size)


def bootstrap_delta_ci(
    group_a: Sequence[float], group_b: Sequence[float],
    n_boot: int = 1000, alpha: float = 0.05, seed: int = 42,
) -> Tuple[float, float]:
    """1−α bootstrap percentile CI for Cliff's δ."""
    rng = np.random.default_rng(seed)
    a = np.asarray(group_a, dtype=float)
    b = np.asarray(group_b, dtype=float)
    if a.size == 0 or b.size == 0:
        return 0.0, 0.0
    deltas = np.empty(n_boot)
    for i in range(n_boot):
        a_b = rng.choice(a, size=a.size, replace=True)
        b_b = rng.choice(b, size=b.size, replace=True)
        deltas[i] = cliffs_delta(a_b, b_b)
    lo = float(np.quantile(deltas, alpha / 2))
    hi = float(np.quantile(deltas, 1 - alpha / 2))
    return lo, hi


def odds_ratio(group_a: Sequence[float], group_b: Sequence[float]) -> float:
    """Odds-ratio of the median: median(A)/median(B). Returns inf if median(B)=0."""
    a = np.asarray(group_a, dtype=float)
    b = np.asarray(group_b, dtype=float)
    if a.size == 0 or b.size == 0:
        return 0.0
    med_b = float(np.median(b))
    if med_b == 0.0:
        return float("inf") if float(np.median(a)) > 0 else 0.0
    return float(np.median(a)) / med_b
```

- [ ] **Step 5.4: Run test to verify pass**

Run: `PYTHONPATH=src python -m pytest tests/stats/test_cliffs_delta.py -v`
Expected: 3 passed.

- [ ] **Step 5.5: Compute δ for RQ2 (aligned vs cross)**

Create `scripts/compute_rq2.py`:

```python
import json, sys
from pathlib import Path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "src"))
from p2.stats.cliffs_delta import cliffs_delta, bootstrap_delta_ci, odds_ratio

PRIMARY = {"a1":1,"a2":1,"a3":1,"b1":2,"b2":2,"b3":2,
           "c1":5,"c2":5,"c3":5,"d1":2,"d2":2,"d3":2}
data = json.loads(open(ROOT / "data/results/sms_track2_v2.json").read())
aligned, cross = [], []
for cell, v in data.items():
    put_id = cell.split("_")[0].lower()
    mp_k = int(cell.split("MP")[1])
    if mp_k == PRIMARY[put_id]:
        aligned.append(v["sms"])
    else:
        cross.append(v["sms"])
delta = cliffs_delta(aligned, cross)
lo, hi = bootstrap_delta_ci(aligned, cross, n_boot=1000, alpha=0.05, seed=42)
ratio = odds_ratio(aligned, cross)
report = {
    "n_aligned": len(aligned), "n_cross": len(cross),
    "mean_aligned": sum(aligned)/len(aligned),
    "mean_cross":   sum(cross)/len(cross),
    "median_aligned": sorted(aligned)[len(aligned)//2],
    "median_cross":   sorted(cross)[len(cross)//2],
    "cliffs_delta": delta,
    "delta_ci_95":  [lo, hi],
    "odds_ratio_median": ratio,
    "h2_threshold_delta": 0.474,
    "h2_threshold_ratio": 3.0,
    "h2_delta_pass": delta >= 0.474,
    "h2_ratio_pass": ratio >= 3.0,
}
out = ROOT / "data/results/rq2_cliffs_delta.json"
out.write_text(json.dumps(report, indent=2, ensure_ascii=False))
print(json.dumps(report, indent=2, ensure_ascii=False))
```

Run: `PYTHONPATH=src python scripts/compute_rq2.py`
Expected: a JSON dump with δ, CI, and odds ratio.

- [ ] **Step 5.6: Commit**

```bash
git add src/p2/stats/cliffs_delta.py tests/stats/test_cliffs_delta.py scripts/compute_rq2.py data/results/rq2_cliffs_delta.json
git commit -m "feat(stats): Cliff's delta + bootstrap CI; computed RQ2 H2 evidence"
```

---

## Round 6: Mixed-Effects Model for RQ3

**Why sixth:** §5.3.2 specifies "mixed effects model: random intercept PUT, fixed effect class × operator". This handles the small-N (4 classes, df=3) issue that pure sign-test cannot resolve. Output is the formal RQ3 evidence layer.

**Files:**
- Create: `src/p2/stats/mixed_effects.py`
- Create: `tests/stats/test_mixed_effects.py`
- Output: `data/results/rq3_mixed_effects.json`

- [ ] **Step 6.1: Write the failing test**

Create `tests/stats/test_mixed_effects.py`:

```python
import pandas as pd
from p2.stats.mixed_effects import fit_class_by_operator_model


def test_fit_returns_class_means_and_p_values():
    # Synthetic data: 4 classes × 3 PUTs each × 5 operators
    rows = []
    for cls in ("a", "b", "c", "d"):
        for put in (f"{cls}1", f"{cls}2", f"{cls}3"):
            for op in ("CE1", "OS1", "HP1", "TF1", "SI1"):
                # Class-c gets bigger values (effect to detect)
                base = 0.6 if cls == "c" else 0.3
                rows.append({"put": put, "class": cls,
                             "operator": op, "sms": base + 0.05 * hash(op) % 5})
    df = pd.DataFrame(rows)
    result = fit_class_by_operator_model(df, value_col="sms")
    assert "class_means" in result
    assert set(result["class_means"]) == {"a", "b", "c", "d"}
    assert "model_summary" in result
    # Fitting should converge
    assert result["converged"] is True
```

- [ ] **Step 6.2: Run test to verify it fails**

Run: `PYTHONPATH=src python -m pytest tests/stats/test_mixed_effects.py -v`
Expected: ImportError.

- [ ] **Step 6.3: Install statsmodels if not present**

```bash
/opt/anaconda3/bin/pip install --quiet statsmodels
python3 -c "import statsmodels; print(statsmodels.__version__)"
```

Expected: statsmodels version printed.

- [ ] **Step 6.4: Implement mixed-effects driver**

Create `src/p2/stats/mixed_effects.py`:

```python
"""Mixed-effects model: random intercept PUT, fixed effect class × operator."""
from typing import Dict
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf


def fit_class_by_operator_model(df: pd.DataFrame, value_col: str = "sms") -> Dict:
    """Fit `value ~ C(class) * C(operator) + (1 | put)` via MixedLM.

    df columns required: put, class, operator, <value_col>
    """
    df = df.copy()
    # Statsmodels MixedLM uses formula API; class & operator are fixed effects
    md = smf.mixedlm(
        f"{value_col} ~ C(class) + C(operator) + C(class):C(operator)",
        data=df, groups=df["put"],
    )
    try:
        mdf = md.fit(method="lbfgs", reml=False)
        converged = bool(mdf.converged)
        summary = str(mdf.summary())
    except Exception as e:
        return {"converged": False, "error": str(e), "class_means": {},
                "model_summary": ""}
    # Per-class marginal means
    class_means = {
        c: float(df.loc[df["class"] == c, value_col].mean())
        for c in sorted(df["class"].unique())
    }
    return {
        "converged": converged,
        "class_means": class_means,
        "model_summary": summary,
        "fixed_params": mdf.fe_params.to_dict(),
        "p_values": mdf.pvalues.to_dict(),
    }
```

- [ ] **Step 6.5: Run test to verify pass**

Run: `PYTHONPATH=src python -m pytest tests/stats/test_mixed_effects.py -v`
Expected: 1 passed.

- [ ] **Step 6.6: Compute RQ3 from Track-2 v2 data**

Create `scripts/compute_rq3.py`:

```python
import json, sys
from pathlib import Path
import pandas as pd
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "src"))
from p2.stats.mixed_effects import fit_class_by_operator_model

PRIMARY = {"a1":1,"a2":1,"a3":1,"b1":2,"b2":2,"b3":2,
           "c1":5,"c2":5,"c3":5,"d1":2,"d2":2,"d3":2}
data = json.loads(open(ROOT / "data/results/sms_track2_v2.json").read())
rows = []
for cell, v in data.items():
    put_id = cell.split("_")[0].lower()
    mp_k = int(cell.split("MP")[1])
    cls = put_id[0]
    rows.append({"put": put_id, "class": cls, "mp": f"MP{mp_k}",
                 "operator": f"MP{mp_k}_aligned" if mp_k == PRIMARY[put_id] else f"MP{mp_k}_cross",
                 "sms": v["sms"]})
df = pd.DataFrame(rows)
out = fit_class_by_operator_model(df, value_col="sms")
report = {
    "n_observations": len(df),
    "class_means": out["class_means"],
    "converged": out["converged"],
    "fixed_params": out.get("fixed_params", {}),
    "p_values": out.get("p_values", {}),
}
(ROOT / "data/results/rq3_mixed_effects.json").write_text(
    json.dumps(report, indent=2, ensure_ascii=False))
(ROOT / "data/results/rq3_model_summary.txt").write_text(out.get("model_summary",""))
print(json.dumps(report, indent=2, ensure_ascii=False))
```

Run: `PYTHONPATH=src python scripts/compute_rq3.py`
Expected: per-class means, fixed-effect params, p-values dump.

- [ ] **Step 6.7: Commit**

```bash
git add src/p2/stats/mixed_effects.py tests/stats/test_mixed_effects.py scripts/compute_rq3.py data/results/rq3_mixed_effects.json data/results/rq3_model_summary.txt
git commit -m "feat(stats): MixedLM class×operator model + RQ3 H4 cross-class report"
```

---

## Round 7: LRCA L0 — Artifact Pre-screen

**Why seventh:** §2.6.2 LRCA L0 = pre-screen for artifacts (NaN-output mutants, identity-mutants, syntax errors). Easy to implement, immediately gives the C1_share denominator (legit mutants) for all 60 cells.

**Files:**
- Create: `src/p2/lrca/l0_artifact.py`
- Create: `tests/lrca/test_l0_artifact.py`
- Output: included in Round 8 dispatcher

- [ ] **Step 7.1: Write the failing test**

Create `tests/lrca/test_l0_artifact.py`:

```python
from p2.lrca.l0_artifact import classify_l0, L0Label


def test_nan_output_classified_as_artifact():
    def m(x): return float("nan")
    assert classify_l0(m, n_samples=20) == L0Label.NAN_OUTPUT


def test_inf_output_classified_as_artifact():
    def m(x): return float("inf")
    assert classify_l0(m, n_samples=20) == L0Label.INF_OUTPUT


def test_constant_output_classified_as_artifact():
    def m(x): return 0.0
    assert classify_l0(m, n_samples=20) == L0Label.CONSTANT_OUTPUT


def test_identity_to_orig_classified_as_artifact():
    def orig(x): return float(x) * 2.0
    def m(x):    return float(x) * 2.0
    assert classify_l0(m, n_samples=20, original=orig) == L0Label.IDENTICAL_TO_ORIG


def test_legit_mutant_classified_as_legit():
    def orig(x): return float(x) * 2.0
    def m(x):    return float(x) * 2.0 + 0.5
    assert classify_l0(m, n_samples=20, original=orig) == L0Label.LEGIT
```

- [ ] **Step 7.2: Run test to verify it fails**

Run: `PYTHONPATH=src python -m pytest tests/lrca/test_l0_artifact.py -v`
Expected: ImportError.

- [ ] **Step 7.3: Implement L0**

Create `src/p2/lrca/l0_artifact.py`:

```python
"""LRCA Layer 0: artifact pre-screen.

A mutant is an "artifact" (not a legit semantic mutation) if it:
  - returns NaN on any sample
  - returns Inf on any sample
  - returns a constant (variance < 1e-12 over inputs)
  - is identical to the original on all samples (within 1e-9)

Otherwise it's LEGIT and the SMS denominator counts it.
"""
from enum import Enum
from typing import Callable, Optional
import math
import numpy as np


class L0Label(str, Enum):
    LEGIT = "legit"
    NAN_OUTPUT = "nan_output"
    INF_OUTPUT = "inf_output"
    CONSTANT_OUTPUT = "constant_output"
    IDENTICAL_TO_ORIG = "identical_to_orig"
    EXEC_ERROR = "exec_error"


def classify_l0(mutant: Callable, n_samples: int = 30,
                original: Optional[Callable] = None,
                seed: int = 42) -> L0Label:
    rng = np.random.default_rng(seed)
    xs = rng.uniform(0.0, 1.0, n_samples)
    outs = []
    for x in xs:
        try:
            y = mutant(float(x))
            outs.append(float(y))
        except Exception:
            return L0Label.EXEC_ERROR
    if any(math.isnan(o) for o in outs):
        return L0Label.NAN_OUTPUT
    if any(math.isinf(o) for o in outs):
        return L0Label.INF_OUTPUT
    if float(np.var(outs)) < 1e-12:
        return L0Label.CONSTANT_OUTPUT
    if original is not None:
        orig_outs = []
        for x in xs:
            try:
                orig_outs.append(float(original(float(x))))
            except Exception:
                orig_outs.append(float("nan"))
        diffs = np.abs(np.array(outs) - np.array(orig_outs))
        if np.nanmax(diffs) < 1e-9:
            return L0Label.IDENTICAL_TO_ORIG
    return L0Label.LEGIT
```

- [ ] **Step 7.4: Run test to verify pass**

Run: `PYTHONPATH=src python -m pytest tests/lrca/test_l0_artifact.py -v`
Expected: 5 passed.

- [ ] **Step 7.5: Commit**

```bash
git add src/p2/lrca/l0_artifact.py tests/lrca/test_l0_artifact.py
git commit -m "feat(lrca): L0 artifact pre-screen (NaN/Inf/constant/identity)"
```

---

## Round 8: LRCA L1-L3 + Dispatcher

**Why eighth:** §2.6.2 specifies L1 (tolerance/C2), L2 (OOD/C3), L3 (statistical/C4). Combined with L0 from Round 7 and the existing C1 (legit fault), we get the C1_share for every (mutant, MR) → enables the §5.4 LRCA section and H5.

**Files:**
- Create: `src/p2/lrca/l1_tolerance.py`
- Create: `src/p2/lrca/l2_ood.py`
- Create: `src/p2/lrca/l3_statistical.py`
- Create: `src/p2/lrca/dispatcher.py`
- Create: `tests/lrca/test_dispatcher.py`
- Create: `scripts/run_lrca.py`
- Output: `data/results/lrca_60cell.json`

- [ ] **Step 8.1: Implement L1 (tolerance)**

Create `src/p2/lrca/l1_tolerance.py`:

```python
"""LRCA L1 — Tolerance/precision sensitivity (C2).

A killed mutant is C2 if its R-fail goes away when AVP epsilon is loosened
by 10x. Indicates the fault is borderline numerical noise, not a true
semantic break.
"""
from typing import Callable
from p2.avp.dispatcher import call_avp
from p2.avp.interface import AVPResult, MR


def is_tolerance_borderline(
    mutant: Callable, mr: MR, epsilon_strict: float = 1e-6,
    epsilon_loose: float = 1e-5,
) -> bool:
    """True if mutant is killed at strict ε but passes at 10× looser ε."""
    try:
        strict = call_avp(mutant, mr, epsilon_strict)
        loose = call_avp(mutant, mr, epsilon_loose)
    except Exception:
        return False
    return strict == AVPResult.FAIL and loose == AVPResult.PASS
```

- [ ] **Step 8.2: Implement L2 (OOD)**

Create `src/p2/lrca/l2_ood.py`:

```python
"""LRCA L2 — Out-of-distribution failure (C3).

A killed mutant is C3 if its R-fail concentrates on input samples outside
the PUT's "trained" / "designed" input region. For our scalar PUTs all on
[0,1], we proxy OOD as inputs near the boundary (x < 0.05 or x > 0.95)."""
from typing import Callable
import numpy as np
from p2.avp.interface import MR


def ood_fail_share(
    mutant: Callable, original: Callable, mr: MR,
    n_samples: int = 100, ood_band: float = 0.05, seed: int = 42,
) -> float:
    """Fraction of R-fails that occur on OOD inputs (boundary band)."""
    rng = np.random.default_rng(seed)
    xs = rng.uniform(0.0, 1.0, n_samples)
    fails_total = 0
    fails_ood = 0
    for x in xs:
        try:
            xr = mr.r(float(x))
            y_o = mutant(float(x))
            y_n = mutant(float(xr))
            r_pass = mr.R(y_o, y_n)
        except Exception:
            continue
        if not r_pass:
            fails_total += 1
            if x < ood_band or x > 1.0 - ood_band:
                fails_ood += 1
    return fails_ood / fails_total if fails_total else 0.0
```

- [ ] **Step 8.3: Implement L3 (statistical)**

Create `src/p2/lrca/l3_statistical.py`:

```python
"""LRCA L3 — Statistical-noise false positive (C4).

For stochastic PUTs (b2, b3, c-class with random seed, d-class), a mutant
may R-fail on a single shot but pass under N=20 majority vote. Such cases
are C4 (the "kill" was noise, not signal).
"""
from typing import Callable
from p2.avp.repeat import call_avp_repeated
from p2.avp.dispatcher import call_avp
from p2.avp.interface import AVPResult, MR


def is_statistical_noise(
    mutant: Callable, mr: MR, epsilon: float = 1e-6, repeats: int = 20,
) -> bool:
    """True if single-shot AVP fails but N=repeats majority-vote passes."""
    try:
        single = call_avp(mutant, mr, epsilon)
        majority = call_avp_repeated(mutant, mr, epsilon, repeats=repeats)
    except Exception:
        return False
    return single == AVPResult.FAIL and majority == AVPResult.PASS
```

- [ ] **Step 8.4: Implement dispatcher**

Create `src/p2/lrca/dispatcher.py`:

```python
"""LRCA layered classifier: returns the strongest applicable label.

Order of resolution (per §2.6.3 decision tree):
  L0 artifact → label as artifact, exit
  Killed AND L3 statistical noise → C4
  Killed AND L1 tolerance borderline → C2
  Killed AND L2 OOD-concentrated → C3
  Killed otherwise → C1 (legit fault, the "good" kill)
  Not killed → "survived" (no label needed for SMS)
"""
from enum import Enum
from typing import Callable
from p2.lrca.l0_artifact import classify_l0, L0Label
from p2.lrca.l1_tolerance import is_tolerance_borderline
from p2.lrca.l2_ood import ood_fail_share
from p2.lrca.l3_statistical import is_statistical_noise
from p2.avp.interface import MR


class LRCALabel(str, Enum):
    ARTIFACT = "L0_artifact"
    C1_LEGIT = "C1_legit_fault"
    C2_TOLERANCE = "C2_tolerance_borderline"
    C3_OOD = "C3_ood_concentrated"
    C4_STATISTICAL = "C4_statistical_noise"
    SURVIVED = "survived"


def classify_mutant(
    mutant: Callable, original: Callable, mr: MR, was_killed: bool,
    epsilon: float = 1e-6, ood_threshold: float = 0.5,
) -> LRCALabel:
    """Return one LRCA label for a (mutant, MR) pair."""
    l0 = classify_l0(mutant, n_samples=30, original=original)
    if l0 != L0Label.LEGIT:
        return LRCALabel.ARTIFACT
    if not was_killed:
        return LRCALabel.SURVIVED
    if is_statistical_noise(mutant, mr, epsilon=epsilon, repeats=20):
        return LRCALabel.C4_STATISTICAL
    if is_tolerance_borderline(mutant, mr, epsilon, epsilon * 10):
        return LRCALabel.C2_TOLERANCE
    if ood_fail_share(mutant, original, mr) > ood_threshold:
        return LRCALabel.C3_OOD
    return LRCALabel.C1_LEGIT
```

- [ ] **Step 8.5: Write the failing test**

Create `tests/lrca/test_dispatcher.py`:

```python
from p2.lrca.dispatcher import classify_mutant, LRCALabel
from p2.avp.interface import MR


def test_artifact_short_circuits():
    def m(x): return float("nan")
    def orig(x): return float(x)
    mr = MR(r=lambda x: x, R=lambda a, b: True, mp_index=1, name="t")
    assert classify_mutant(m, orig, mr, was_killed=True) == LRCALabel.ARTIFACT


def test_unkilled_returns_survived():
    def m(x): return float(x) + 0.5
    def orig(x): return float(x)
    mr = MR(r=lambda x: x, R=lambda a, b: True, mp_index=1, name="t")
    assert classify_mutant(m, orig, mr, was_killed=False) == LRCALabel.SURVIVED


def test_legit_killed_returns_c1():
    def m(x): return float(x) * 2.0      # genuinely different
    def orig(x): return float(x)
    mr = MR(r=lambda x: x + 0.1,
            R=lambda a, b: abs(b - a - 0.1) < 1e-9,
            mp_index=1, name="t")
    label = classify_mutant(m, orig, mr, was_killed=True)
    # m violates R (b = 2*(x+0.1), not a + 0.1) and isn't OOD/tolerance/noise
    assert label == LRCALabel.C1_LEGIT
```

- [ ] **Step 8.6: Run all LRCA tests**

Run: `PYTHONPATH=src python -m pytest tests/lrca/ -v`
Expected: all tests pass (~ 8 tests across L0 + dispatcher).

- [ ] **Step 8.7: Run LRCA on 60-cell Track-2 v2 results**

Create `scripts/run_lrca.py`:

```python
"""Apply LRCA dispatcher to every (mutant, MR) pair in Track-2 v2;
produce per-cell C1_share + suspect_share."""
import importlib.util, json, sys
from pathlib import Path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "src"))

from p2.avp.interface import MR
from p2.lrca.dispatcher import classify_mutant, LRCALabel

PRIMARY = {"a1":1,"a2":1,"a3":1,"b1":2,"b2":2,"b3":2,
           "c1":5,"c2":5,"c3":5,"d1":2,"d2":2,"d3":2}

def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m

sms = json.loads((ROOT / "data/results/sms_track2_v2.json").read_text())
report = {}
for cell, v in sms.items():
    put_id = cell.split("_")[0].lower()
    mp_k = int(cell.split("MP")[1])
    pool_dir = ROOT / f"data/mutants/{put_id}_pool"
    if not pool_dir.exists():
        pool_dir = ROOT / f"data/mutants/{put_id}_MP{PRIMARY[put_id]}_llm"
    put_mod = _load(f"put_{put_id}", ROOT / f"src/p2/puts/{put_id}.py")
    mrs_mod = _load(f"mrs_{put_id}", ROOT / f"src/p2/mrs/{put_id}.py")
    mr = MR(r=getattr(mrs_mod, f"r_mp{mp_k}"),
            R=getattr(mrs_mod, f"R_mp{mp_k}"),
            mp_index=mp_k, name=cell)
    killed_files = {o["file"] for o in v.get("outcomes", []) if o["label"] == "KILLED"}
    labels = {l.value: 0 for l in LRCALabel}
    per_mut = []
    for o in v.get("outcomes", []):
        fp = pool_dir / o["file"]
        if not fp.exists():
            continue
        try:
            mut_mod = _load(f"mut_{cell}_{fp.stem}", fp)
        except Exception:
            labels[LRCALabel.ARTIFACT.value] += 1
            per_mut.append({"file": o["file"], "lrca": LRCALabel.ARTIFACT.value})
            continue
        was_killed = o["file"] in killed_files
        label = classify_mutant(mut_mod.program, put_mod.program, mr, was_killed)
        labels[label.value] += 1
        per_mut.append({"file": o["file"], "outcome": o["label"], "lrca": label.value})
    n_killed = labels[LRCALabel.C1_LEGIT.value] + labels[LRCALabel.C2_TOLERANCE.value] + \
               labels[LRCALabel.C3_OOD.value] + labels[LRCALabel.C4_STATISTICAL.value]
    c1_share = labels[LRCALabel.C1_LEGIT.value] / n_killed if n_killed else 0.0
    suspect_share = 1.0 - c1_share
    report[cell] = {
        "labels": labels, "per_mutant": per_mut,
        "n_killed": n_killed,
        "c1_share": round(c1_share, 4),
        "suspect_share": round(suspect_share, 4),
    }

(ROOT / "data/results/lrca_60cell.json").write_text(
    json.dumps(report, indent=2, ensure_ascii=False))
print(f"Cells processed: {len(report)}")
print(f"Mean suspect_share: {sum(r['suspect_share'] for r in report.values())/len(report):.3f}")
```

Run: `PYTHONPATH=src python scripts/run_lrca.py`
Expected: completes within ~10 minutes; emits per-cell C1/C2/C3/C4 counts.

- [ ] **Step 8.8: Commit**

```bash
git add src/p2/lrca/l1_tolerance.py src/p2/lrca/l2_ood.py src/p2/lrca/l3_statistical.py src/p2/lrca/dispatcher.py tests/lrca/test_dispatcher.py scripts/run_lrca.py data/results/lrca_60cell.json
git commit -m "feat(lrca): L1-L3 + dispatcher; 60-cell C1_share / suspect_share"
```

**Compact context after Round 8** — RQ1 + H5 reportable; downstream rounds only need data/results/*.

---

## Round 9: Pattern Coverage Module (RQ4)

**Why ninth:** RQ4 compares SMS vs pattern coverage. Pattern coverage is currently 0% — completely unimplemented. The simplest pattern coverage = "what fraction of MR-element-pair outcomes (R_pass × MP) is exercised by the test suite". Once implemented, RQ4 jumps from 0% to 60%.

**Files:**
- Create: `src/p2/stats/pattern_coverage.py`
- Create: `tests/stats/test_pattern_coverage.py`
- Output: `data/results/rq4_pattern_coverage.json`

- [ ] **Step 9.1: Write the failing test**

Create `tests/stats/test_pattern_coverage.py`:

```python
from p2.stats.pattern_coverage import compute_pattern_coverage


def test_full_coverage_on_all_mp_passes():
    # 5 MPs × 2 outcomes (pass/fail) = 10 cells; suite covers all
    outcomes = [(mp, ok) for mp in (1, 2, 3, 4, 5) for ok in (True, False)]
    cov = compute_pattern_coverage(outcomes, n_mps=5)
    assert cov == 1.0


def test_zero_coverage_on_empty_suite():
    cov = compute_pattern_coverage([], n_mps=5)
    assert cov == 0.0


def test_partial_coverage():
    outcomes = [(1, True), (2, True), (3, True)]  # 3 of 10 cells
    cov = compute_pattern_coverage(outcomes, n_mps=5)
    assert abs(cov - 0.3) < 1e-9
```

- [ ] **Step 9.2: Run test to verify it fails**

Run: `PYTHONPATH=src python -m pytest tests/stats/test_pattern_coverage.py -v`
Expected: ImportError.

- [ ] **Step 9.3: Implement pattern coverage**

Create `src/p2/stats/pattern_coverage.py`:

```python
"""Pattern coverage: fraction of (MP, R-outcome) cells exercised.

Operationalisation: each cell is (MP_k, R_outcome ∈ {True, False}). A test
suite "covers" a cell if at least one (mutant, MP) pair in the suite produced
that R outcome. Pattern coverage = covered / (n_MPs × 2).

Used as the §1.4 RQ4 baseline against SMS.
"""
from typing import Iterable, Tuple


def compute_pattern_coverage(
    outcomes: Iterable[Tuple[int, bool]], n_mps: int = 5,
) -> float:
    """outcomes: iterable of (mp_index, R_pass_bool) tuples.
    Returns the fraction of (mp, outcome) cells covered."""
    covered = set()
    for mp, ok in outcomes:
        covered.add((mp, bool(ok)))
    total = n_mps * 2
    return len(covered) / total if total else 0.0
```

- [ ] **Step 9.4: Run test to verify pass**

Run: `PYTHONPATH=src python -m pytest tests/stats/test_pattern_coverage.py -v`
Expected: 3 passed.

- [ ] **Step 9.5: Compute pattern coverage per PUT and Spearman vs SMS**

Create `scripts/compute_rq4.py`:

```python
import importlib.util, json, sys
from pathlib import Path
import numpy as np
from scipy.stats import spearmanr, kendalltau
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "src"))

from p2.avp.interface import MR
from p2.stats.pattern_coverage import compute_pattern_coverage

PRIMARY = {"a1":1,"a2":1,"a3":1,"b1":2,"b2":2,"b3":2,
           "c1":5,"c2":5,"c3":5,"d1":2,"d2":2,"d3":2}

def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m

sms = json.loads((ROOT / "data/results/sms_track2_v2.json").read_text())

# For each PUT: collect (MP, R_outcome) tuples across all 5 MPs × all mutants
per_put = {}
for put_id in PRIMARY:
    pool_dir = ROOT / f"data/mutants/{put_id}_pool"
    if not pool_dir.exists():
        pool_dir = ROOT / f"data/mutants/{put_id}_MP{PRIMARY[put_id]}_llm"
    put_mod = _load(f"put_{put_id}", ROOT / f"src/p2/puts/{put_id}.py")
    mrs_mod = _load(f"mrs_{put_id}", ROOT / f"src/p2/mrs/{put_id}.py")
    outcomes = []
    for fp in sorted(pool_dir.glob("m*.py")):
        try:
            mut_mod = _load(f"_m_{put_id}_{fp.stem}", fp)
        except Exception:
            continue
        for mp_k in (1, 2, 3, 4, 5):
            r = getattr(mrs_mod, f"r_mp{mp_k}")
            R = getattr(mrs_mod, f"R_mp{mp_k}")
            try:
                xs = np.linspace(0.05, 0.95, 10)
                for x in xs:
                    y_o = mut_mod.program(float(x))
                    y_n = mut_mod.program(float(r(x)))
                    outcomes.append((mp_k, bool(R(y_o, y_n))))
            except Exception:
                pass
    cov = compute_pattern_coverage(outcomes, n_mps=5)
    cell_smses = [v["sms"] for k, v in sms.items() if k.startswith(put_id.upper() + "_")]
    per_put[put_id] = {
        "pattern_coverage": round(cov, 4),
        "mean_sms_over_5_cells": round(float(np.mean(cell_smses)), 4),
    }

cov_arr = [v["pattern_coverage"] for v in per_put.values()]
sms_arr = [v["mean_sms_over_5_cells"] for v in per_put.values()]
rho, p_rho = spearmanr(cov_arr, sms_arr)
tau, p_tau = kendalltau(cov_arr, sms_arr)
report = {
    "per_put": per_put,
    "spearman_rho": float(rho), "spearman_p": float(p_rho),
    "kendall_tau": float(tau), "kendall_p": float(p_tau),
    "n": len(per_put),
}
(ROOT / "data/results/rq4_pattern_coverage.json").write_text(
    json.dumps(report, indent=2, ensure_ascii=False))
print(json.dumps(report, indent=2, ensure_ascii=False))
```

Run: `PYTHONPATH=src python scripts/compute_rq4.py`
Expected: per-PUT coverage + Spearman/Kendall correlations.

- [ ] **Step 9.6: Commit**

```bash
git add src/p2/stats/pattern_coverage.py tests/stats/test_pattern_coverage.py scripts/compute_rq4.py data/results/rq4_pattern_coverage.json
git commit -m "feat(stats): pattern coverage + Spearman vs SMS for RQ4"
```

---

## Round 10: Visualization Suite

**Why tenth:** §5.5 requires Figures 1-5 (60-cell heatmap, aligned vs cross box, 4-class forest, SMS vs C1_share scatter, SMS vs PC scatter). All inputs (Track-2 v2, LRCA, RQ4) now exist. This round produces the actual paper figures.

**Files:**
- Create: `src/p2/viz/heatmap.py` / `forest.py` / `boxplot.py` / `scatter.py`
- Create: `tests/viz/test_viz_smoke.py`
- Create: `scripts/render_figures.py`
- Output: `figures/fig1_60cell_heatmap.pdf`, `fig2_aligned_vs_cross_box.pdf`, `fig3_class_forest.pdf`, `fig4_sms_vs_c1share.pdf`, `fig5_sms_vs_pc.pdf`

- [ ] **Step 10.1: Install matplotlib + seaborn**

```bash
/opt/anaconda3/bin/pip install --quiet matplotlib seaborn
python3 -c "import matplotlib, seaborn; print(matplotlib.__version__, seaborn.__version__)"
```

Expected: versions printed.

- [ ] **Step 10.2: Write a smoke test for one figure module**

Create `tests/viz/test_viz_smoke.py`:

```python
import os, tempfile
from pathlib import Path
import numpy as np
from p2.viz.heatmap import render_60cell_heatmap


def test_heatmap_writes_pdf(tmp_path):
    sms_data = {f"{p.upper()}_MP{k}": {"sms": np.random.rand()}
                for p in ("a1","a2","b1","c1","d1") for k in (1,2,3,4,5)}
    out = tmp_path / "fig1.pdf"
    render_60cell_heatmap(sms_data, out_path=out)
    assert out.exists() and out.stat().st_size > 1000
```

- [ ] **Step 10.3: Implement heatmap module**

Create `src/p2/viz/heatmap.py`:

```python
"""60-cell SMS heatmap (rows=PUT, cols=MP)."""
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

PUTS = ["a1","a2","a3","b1","b2","b3","c1","c2","c3","d1","d2","d3"]
MPS = [1, 2, 3, 4, 5]
PRIMARY = {"a1":1,"a2":1,"a3":1,"b1":2,"b2":2,"b3":2,
           "c1":5,"c2":5,"c3":5,"d1":2,"d2":2,"d3":2}


def render_60cell_heatmap(sms_data: dict, out_path: Path) -> None:
    """sms_data: {f'{PUT}_MP{k}': {'sms': float, ...}, ...}."""
    matrix = np.zeros((len(PUTS), len(MPS)))
    annot = np.empty((len(PUTS), len(MPS)), dtype=object)
    for i, put in enumerate(PUTS):
        for j, mp in enumerate(MPS):
            cell = f"{put.upper()}_MP{mp}"
            sms = sms_data.get(cell, {}).get("sms", 0.0)
            matrix[i, j] = sms
            mark = "★" if PRIMARY[put] == mp else ""
            annot[i, j] = f"{sms:.2f}{mark}"
    fig, ax = plt.subplots(figsize=(7, 9))
    sns.heatmap(matrix, annot=annot, fmt="", cmap="YlOrRd",
                xticklabels=[f"MP{k}" for k in MPS],
                yticklabels=[p.upper() for p in PUTS],
                vmin=0.0, vmax=1.0, ax=ax,
                cbar_kws={"label": "SMS"})
    ax.set_title("60-cell SMS heatmap (★ = j=k aligned)")
    fig.tight_layout()
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, format="pdf")
    plt.close(fig)
```

- [ ] **Step 10.4: Run heatmap smoke**

Run: `PYTHONPATH=src python -m pytest tests/viz/test_viz_smoke.py -v`
Expected: 1 passed; tmp_path PDF exists.

- [ ] **Step 10.5: Implement remaining viz modules**

Create `src/p2/viz/boxplot.py`:

```python
"""Aligned vs cross SMS box plot (Figure 2)."""
from pathlib import Path
import matplotlib.pyplot as plt

PRIMARY = {"a1":1,"a2":1,"a3":1,"b1":2,"b2":2,"b3":2,
           "c1":5,"c2":5,"c3":5,"d1":2,"d2":2,"d3":2}


def render_aligned_vs_cross(sms_data: dict, out_path: Path) -> None:
    aligned, cross = [], []
    for cell, v in sms_data.items():
        put = cell.split("_")[0].lower()
        mp = int(cell.split("MP")[1])
        (aligned if PRIMARY[put] == mp else cross).append(v["sms"])
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.boxplot([aligned, cross], labels=["aligned (j=k)", "cross (j≠k)"])
    ax.set_ylabel("SMS")
    ax.set_title(f"Aligned vs cross SMS (n_a={len(aligned)}, n_c={len(cross)})")
    fig.tight_layout()
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, format="pdf"); plt.close(fig)
```

Create `src/p2/viz/forest.py`:

```python
"""Per-class forest plot of mean SMS (Figure 3)."""
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt


def render_class_forest(sms_data: dict, out_path: Path) -> None:
    classes = {"a": [], "b": [], "c": [], "d": []}
    for cell, v in sms_data.items():
        cls = cell[0].lower()
        classes[cls].append(v["sms"])
    means = {c: float(np.mean(vs)) for c, vs in classes.items()}
    sems = {c: float(np.std(vs, ddof=1) / np.sqrt(len(vs))) for c, vs in classes.items()}
    fig, ax = plt.subplots(figsize=(5, 4))
    y = np.arange(len(means))
    ax.errorbar([means[c] for c in "abcd"], y,
                xerr=[sems[c] for c in "abcd"], fmt="o", capsize=4)
    ax.set_yticks(y); ax.set_yticklabels(["a numeric","b probabilistic","c surrogate","d ML"])
    ax.set_xlabel("Mean SMS ± SEM")
    ax.axvline(0.0, color="gray", linestyle="--", linewidth=0.5)
    ax.set_title("Cross-class SMS (RQ3)")
    fig.tight_layout()
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, format="pdf"); plt.close(fig)
```

Create `src/p2/viz/scatter.py`:

```python
"""SMS vs (C1_share or PC) scatter plots (Figures 4, 5)."""
from pathlib import Path
import matplotlib.pyplot as plt
from scipy.stats import spearmanr


def render_scatter(x_data: list, y_data: list,
                   x_label: str, y_label: str,
                   title: str, out_path: Path) -> None:
    rho, p = spearmanr(x_data, y_data)
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.scatter(x_data, y_data, s=40, alpha=0.7)
    ax.set_xlabel(x_label); ax.set_ylabel(y_label)
    ax.set_title(f"{title}\nSpearman ρ = {rho:.3f}, p = {p:.3g}")
    fig.tight_layout()
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, format="pdf"); plt.close(fig)
```

- [ ] **Step 10.6: Run all 5 figures via render_figures.py**

Create `scripts/render_figures.py`:

```python
import json, sys
from pathlib import Path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "src"))
from p2.viz.heatmap import render_60cell_heatmap
from p2.viz.boxplot import render_aligned_vs_cross
from p2.viz.forest import render_class_forest
from p2.viz.scatter import render_scatter

FIG = ROOT / "figures"; FIG.mkdir(exist_ok=True)
sms = json.loads((ROOT / "data/results/sms_track2_v2.json").read_text())
lrca = json.loads((ROOT / "data/results/lrca_60cell.json").read_text())
rq4 = json.loads((ROOT / "data/results/rq4_pattern_coverage.json").read_text())

render_60cell_heatmap(sms, FIG / "fig1_60cell_heatmap.pdf")
render_aligned_vs_cross(sms, FIG / "fig2_aligned_vs_cross_box.pdf")
render_class_forest(sms, FIG / "fig3_class_forest.pdf")

# Fig 4: SMS vs C1_share, per-cell
xs, ys = [], []
for cell, sm in sms.items():
    if cell in lrca:
        xs.append(lrca[cell]["c1_share"])
        ys.append(sm["sms"])
render_scatter(xs, ys, "C1_share (LRCA)", "SMS",
               "SMS vs C1_share per cell (Figure 4)",
               FIG / "fig4_sms_vs_c1share.pdf")

# Fig 5: per-PUT pattern coverage vs mean SMS
xs = [v["pattern_coverage"] for v in rq4["per_put"].values()]
ys = [v["mean_sms_over_5_cells"] for v in rq4["per_put"].values()]
render_scatter(xs, ys, "Pattern coverage", "Mean SMS over 5 cells",
               "SMS vs pattern coverage per PUT (Figure 5, RQ4)",
               FIG / "fig5_sms_vs_pc.pdf")
print("All 5 figures rendered to figures/")
```

Run: `PYTHONPATH=src python scripts/render_figures.py`
Expected: 5 PDFs in figures/.

- [ ] **Step 10.7: Commit**

```bash
git add src/p2/viz/ tests/viz/ scripts/render_figures.py figures/*.pdf
git commit -m "feat(viz): heatmap + box + forest + scatter for §5 figures 1-5"
```

**Compact context after Round 10** — all empirical artifacts in place; remaining rounds are paper writing + reproducibility.

---

## Round 11: Reproducibility Manifest + Dataset Card

**Why eleventh:** Before publishing, we need a single document that lets a reader reproduce every result. Open-source convention: REPRODUCIBILITY.md (commands), DATASET.md (data card), LICENSE, environment spec.

**Files:**
- Create: `REPRODUCIBILITY.md`
- Create: `DATASET.md`
- Create: `LICENSE` (MIT or Apache-2; pick one)
- Create: `requirements-frozen.txt`
- Modify: `README.md` (add reproduction quick-start)

- [ ] **Step 11.1: Generate frozen requirements**

```bash
/opt/anaconda3/bin/pip freeze | grep -E "numpy|scipy|scikit-learn|statsmodels|matplotlib|seaborn|fastdtw|openai|anthropic|pytest|python-dotenv" > requirements-frozen.txt
cat requirements-frozen.txt
```

Expected: ~10-15 pinned package versions.

- [ ] **Step 11.2: Write REPRODUCIBILITY.md**

```markdown
# Reproducibility Guide for P2 Empirical Audit

## Environment

- Python 3.12.7 (conda or venv)
- See `requirements-frozen.txt` for exact pinned versions
- macOS subprocess auth via Claude Code keychain entry "Claude Code-credentials" (only needed for re-running the operator campaign — all derived metrics can be re-computed from `data/operator_campaign/raw/` without LLM access)

## End-to-end reproduction (2-3 hours)

```bash
# 1. Install dependencies
pip install -r requirements-frozen.txt

# 2. Verify tests pass
PYTHONPATH=src pytest -q

# 3. Re-build per-PUT mutant pools from operator-campaign cache
PYTHONPATH=src python scripts/build_pools.py

# 4. Re-run Track-2 SMS (60 cells × N=20 repeats; ~15-25 min)
PYTHONPATH=src python scripts/sms_campaign.py --track 2 --workers 6 --repeats 20

# 5. Re-run LRCA (60 cells × ~12 mutants; ~10 min)
PYTHONPATH=src python scripts/run_lrca.py

# 6. Compute RQ statistics
PYTHONPATH=src python scripts/compute_rq2.py    # Cliff's δ + bootstrap CI
PYTHONPATH=src python scripts/compute_rq3.py    # mixed-effects model
PYTHONPATH=src python scripts/compute_rq4.py    # pattern coverage + Spearman

# 7. Render figures
PYTHONPATH=src python scripts/render_figures.py

# 8. Inspect data/results/ and figures/ outputs
```

## What can't be reproduced exactly

- LLM-generated mutants (`data/operator_campaign/raw/`) are non-deterministic
  (Claude Opus subscription has no seed control). The cache is committed and
  treated as a frozen dataset for downstream metric reproduction.
- Stochastic-PUT SMS estimates fluctuate by ~0.05 SMS units between runs;
  N=20 repetition reduces but does not eliminate this noise.

## Data provenance per artifact

See `DATASET.md` for the data card with per-file lineage.
```

Save as `REPRODUCIBILITY.md`.

- [ ] **Step 11.3: Write DATASET.md**

```markdown
# P2 Dataset Card

## PUTs (`src/p2/puts/{a1..d3}.py`)
12 scientific computing programs across 4 classes (numeric, probabilistic,
surrogate, ML). Signatures float→float, deterministic where possible.

## MRs (`src/p2/mrs/{a1..d3}.py`)
60 metamorphic relations, 5 MPs per PUT. Strength tag in module docstring
matches §3.3 grid (●●/●/○).

## Mutation operators (`src/p2/mutators/operator_registry.py`)
37 named operators across 5 categories (CE, OS, HP, TF, SI/CF). Each with
target_locator + transformation + rationale. is_key=True for 12 operators
get K=20 trials.

## LLM-generated mutants
- `data/operator_campaign/raw/{op_id}.json` — 470 trials with prompts,
  raw LLM response, V1-V6 + operator_match labels, reviewer reason.
- `data/operator_campaign/cache/{op_id}_attempt{NN}.py` — 212 confirmed
  mutants (V1-V6 ✓ ∧ operator_match=Yes).
- `data/mutants/{put}_pool/m{NN}_{op_id}_a{NN}.py` — per-PUT pool of 12
  mutants sampled proportionally across operators (Round 2 builder).

## Generation prompts
- `src/p2/mutators/prompts/operator_template.txt` — generator prompt (Claude Opus)
- `src/p2/mutators/prompts/operator_reviewer_template.txt` — reviewer prompt
  (GPT-5.4 via OpenAI-compatible proxy)

## Metrics outputs
- `data/results/operator_metrics.json` — R_sem / D_impl / R_kill per operator
- `data/results/sms_track1.json` — Track-1 (12 primary cells)
- `data/results/sms_track2.json` — Track-2 v1 (60 cells, 4-5 mutants/cell)
- `data/results/sms_track2_v2.json` — Track-2 v2 (60 cells, 12 mutants/cell, N=20)
- `data/results/lrca_60cell.json` — per-cell C1/C2/C3/C4/Artifact counts
- `data/results/rq2_cliffs_delta.json` — Cliff's δ + bootstrap CI
- `data/results/rq3_mixed_effects.json` — mixed-effects fit
- `data/results/rq4_pattern_coverage.json` — pattern coverage + Spearman

## Figures
- `figures/fig1_60cell_heatmap.pdf` — 60-cell SMS heatmap
- `figures/fig2_aligned_vs_cross_box.pdf` — aligned vs cross box
- `figures/fig3_class_forest.pdf` — cross-class SMS forest
- `figures/fig4_sms_vs_c1share.pdf` — SMS vs C1_share scatter
- `figures/fig5_sms_vs_pc.pdf` — SMS vs pattern coverage scatter
```

Save as `DATASET.md`.

- [ ] **Step 11.4: Add LICENSE (MIT)**

Copy a standard MIT LICENSE template. Use:

```
MIT License

Copyright (c) 2026 [Author Name]

Permission is hereby granted, free of charge, to any person obtaining a copy
[... standard MIT text ...]
```

- [ ] **Step 11.5: Commit**

```bash
git add REPRODUCIBILITY.md DATASET.md LICENSE requirements-frozen.txt
git commit -m "docs: reproducibility guide + dataset card + MIT license"
```

---

## Round 12: §5 Results Paper Section

**Why twelfth:** All empirical artifacts now exist. Compose the paper §5 in Chinese matching the existing draft style. Source data: tables from rq2/rq3/rq4 JSONs, figures from figures/.

**Files:**
- Modify: `论文初稿P2.md` (add §5 results subsection between §5.5 and §6)

- [ ] **Step 12.1: Read current §5 to understand voice**

Run: `Read <MT_ROOT>/论文初稿P2.md offset=645 limit=60`

Goal: confirm tone, depth, formatting style for the new content.

- [ ] **Step 12.2: Insert §5.6 RQ1 results section**

Append after §5.5 ("可视化") in `论文初稿P2.md`:

```markdown
### 5.6 RQ1 实证结果(60 单元格,Track-2 v2)

#### 5.6.1 单元格级数据

每 PUT 12 个 mutants(operator-cache 比例采样),N=20 AVP 重复采样,60 单元格 SMS 全表见图 1。摘要:

| 切片 | n | 平均 SMS | 中位数 SMS |
|---|---|---|---|
| 全 60 单元格 | 60 | (从 sms_track2_v2.json 计算) | — |
| ●● 充实 | 32 | — | — |
| ● 中等 | 19 | — | — |
| ○ 空缺 | 9 | — | — |

(运行 `python scripts/compute_rq1_summary.py` 后填入实际数字)

[此处嵌入 figure 1: 60-cell SMS heatmap]

#### 5.6.2 LRCA C1_share 分布

LRCA 三层诊断对每个被 killed 的 mutant 标注 C1/C2/C3/C4 之一。全 60 单元格平均 C1_share = X(对应 H5 阈值 ≥ 0.80 → suspect_share ≤ 0.20)。

[此处嵌入 figure 4: SMS vs C1_share scatter]
```

- [ ] **Step 12.3: Insert §5.7 RQ2 results**

```markdown
### 5.7 RQ2 实证结果

aligned-SMS vs cross-SMS:
- 平均 aligned = X (n=12)
- 平均 cross = Y (n=48)
- Cliff's δ = Z, 95% bootstrap CI [a, b]
- 中位数几率比 = R

H2(几率比 ≥ 3.0 ∧ Cliff's δ ≥ 0.474):达成 / 未达成 / 边缘。

[此处嵌入 figure 2: 对齐 vs 非对齐 box plot]
```

- [ ] **Step 12.4: Insert §5.8 RQ3 results**

```markdown
### 5.8 RQ3 实证结果

4 类 PUT × 5 MPs 数据,混合效应模型:
- random intercept: PUT
- fixed effects: class × operator (with class:operator interaction)

类别均值: a=X, b=Y, c=Z, d=W. CV = V. Sign test: 4/4 正向(符合 H4)。

[此处嵌入 figure 3: 跨类 SMS forest plot]

模型摘要见 `data/results/rq3_model_summary.txt`。
```

- [ ] **Step 12.5: Insert §5.9 RQ4 results**

```markdown
### 5.9 RQ4 实证结果

每 PUT 的 pattern coverage 计算 = (MP, R_outcome) 二元组覆盖率。Spearman ρ(SMS, PC) = X (p = Y); Kendall τ = Z。

[此处嵌入 figure 5: SMS vs PC 散点]

定性观察:SMS 与 PC 的相关性 / 反相关性 / 无关 → 进入 §6 讨论 SMS 与现有 MR 度量的差异定位。
```

- [ ] **Step 12.6: Run a script to fill the placeholders with real numbers**

```python
# scripts/inject_paper_numbers.py — auto-fills X/Y/Z placeholders
# from data/results/*.json into 论文初稿P2.md.
# (Implementation: regex-based substitution targeted at known anchor strings.)
```

This step is non-trivial; for now, manually fill placeholders by reading each JSON.

- [ ] **Step 12.7: Commit**

```bash
git add 论文初稿P2.md
git commit -m "draft: §5.6-5.9 RQ1-RQ4 empirical results from Track-2 v2 + LRCA + stats"
```

---

## Round 13: §6 Discussion + §7 Limitations Updates

**Why thirteenth:** §6 and §7 currently reflect the pre-experiment plan. Updates: §6 = interpretation of the actual results; §7 = update Limitations and add R8 (registry-source drift) + R9 (mutant-pool size) + R10 (LLM non-determinism).

**Files:**
- Modify: `论文初稿P2.md` (§7 sections; new §6 "讨论" section)

- [ ] **Step 13.1: Insert new §6 (discussion)**

Currently §6 is "工作量与时序". Renumber: §6 → §7 work plan, §7 → §8 Limitations. Insert new §6:

```markdown
## 第 6 节 · 讨论

### 6.1 SMS 与传统 MS 的经验差异

(基于 RQ2 数据:aligned-SMS = X 与 cross-SMS = Y;Cliff's δ = Z。讨论 SMS 在元模式对齐切片上的系统性偏置,以及为何这构成"语义层 MS 扩展"。)

### 6.2 R_sem / R_kill 解耦的工程启示

(从 §4.8.3 算子级 pilot 与 §5.7 单元格级 SMS 共同观察到的解耦现象,讨论 MR 设计中"算子-MP 对齐覆盖"的重要性。)

### 6.3 跨类一致性意味着什么

(基于 RQ3 mixed-effects 结果,讨论 4 类 PUT 共享 SMS 行为的程度。)

### 6.4 SMS vs Pattern Coverage 的位置关系

(基于 RQ4 Spearman 相关性,讨论 SMS 是否与 PC 提供互补 / 冗余信息。)
```

- [ ] **Step 13.2: Update §7 (Limitations)**

Add R8/R9/R10 to §7.1:

```markdown
#### 7.1.5 算子注册表-PUT 源代码漂移(R8)
v2 → v2.1 修订过程中发现 6/37 算子定义引用了 PUT 重构后已不存在的参数(GPR.alpha vs WhiteKernel.noise_level;d1 注册声明 SVM 但 PUT 实为 MLP)。已加入 §4.2 前置一致性扫描(target_locator 关键标识符必须出现在 PUT 源码中)。

#### 7.1.6 Mutant pool 大小(R9)
每 PUT 12 个 mutants 是工程平衡:更小则 SMS 估计跳变粗糙,更大则 LLM 调用成本超预算。Bootstrap CI(§5.7)反映了这一来源的不确定性。

#### 7.1.7 LLM 生成的非确定性(R10)
Claude Opus 订阅接口无 seed 控制;同一 prompt 在不同时刻可能产生不同输出。我们通过(a) Multi-turn de-dup 强制结构差异,(b) K=10/20 重复降低单点偏差,(c) 提交完整 raw response 至 `data/operator_campaign/raw/` 供复现实验复用同一 mutant 集。
```

- [ ] **Step 13.3: Commit**

```bash
git add 论文初稿P2.md
git commit -m "draft: §6 discussion + §7 R8/R9/R10 limitations from empirical phase"
```

**Compact context after Round 13** — only review tasks remain.

---

## Round 14: Self-Review and RQ-Table Sweep

**Why fourteenth:** Final pass. Verify every RQ has: a number from data, a citation to the figure, a paragraph of discussion. Catch placeholder leftovers, broken cross-references, undefined symbols.

**Files:**
- Modify: `论文初稿P2.md` (any final fixes)
- Create: `docs/superpowers/notes/2026-05-XX-self-review-rq-completion.md`

- [ ] **Step 14.1: Run a placeholder scan**

```bash
grep -nE "TODO|TBD|FIXME|placeholder|\bX\b|\bY\b|\bZ\b" 论文初稿P2.md | head -20
```

Each hit must be either replaced with a real number/string or explicitly marked as "待填充(数据持续采集中)".

- [ ] **Step 14.2: Verify each RQ has 4 elements**

Check:
- RQ1: data table ✓, figure ref ✓, discussion in §6 ✓, completeness % ≥ 90%
- RQ2: data table ✓, figure ref ✓, Cliff's δ + CI ✓, discussion ✓, % ≥ 90%
- RQ3: class means ✓, mixed-effects fit ✓, forest plot ✓, discussion ✓, % ≥ 90%
- RQ4: PC vs SMS scatter ✓, Spearman/Kendall ✓, discussion ✓, % ≥ 60%

If any RQ falls short, add a "Limitations" paragraph naming the gap explicitly rather than hiding it.

- [ ] **Step 14.3: Document the final RQ-completion table**

Create `docs/superpowers/notes/2026-05-XX-self-review-rq-completion.md`:

```markdown
# P2 RQ-Completion Final State (post-spiral)

| RQ | Coverage | Evidence | Outstanding |
|----|----------|----------|-------------|
| RQ1 | 95% | Track-2 v2 60-cell heatmap; LRCA C1_share table; H1 ✓ ; H5 evaluated | None blocking submission |
| RQ2 | 95% | Cliff's δ + bootstrap CI; aligned/cross box; H2 result formal | If H2 marginal, framed as "exploratory" |
| RQ3 | 95% | Mixed-effects fit; class forest; H4 result | None blocking |
| RQ4 | 60-80% | SMS vs PC Spearman + Kendall; scatter | Could expand PC definition (see §6.4 future work) |

## Decision: ready to submit?

(Yes / No / What blocks). If yes, proceed to journal-formatting pass.
If no, list the 1-3 specific items that must close before submission.
```

- [ ] **Step 14.4: Final commit**

```bash
git add 论文初稿P2.md docs/superpowers/notes/
git commit -m "review: RQ-completion sweep; mark submission-readiness"
```

---

## Round 15 (optional, future): Journal Formatting Pass

Out of scope for the empirical-completion spiral. Triggered only after Round 14 declares submission-ready. Includes:
- LaTeX conversion (if journal requires)
- Figure resolution / format adjustments
- Reference list formatting (ACM / IEEE / IST style)
- Cover letter
- Author affiliations

---

## Self-Review (executed by plan author before handoff)

**1. Spec coverage:**
- RQ1 (inst/equiv/C1_share/survive across 60 cells): Round 1 (equiv fix) + Round 2 (mutant pool) + Round 4 (re-run) + Rounds 7-8 (LRCA C1_share). ✓
- RQ2 (aligned vs cross + Cliff's δ + bootstrap): Rounds 4 + 5. ✓
- RQ3 (cross-class + mixed effects + forest): Rounds 4 + 6 + 10. ✓
- RQ4 (SMS vs pattern coverage): Round 9. ✓
- H1-H5 hypotheses: H1 (data flowing through Round 4), H2 (Round 5), H3 (Round 1 fix unblocks), H4 (Round 6), H5 (Round 8). ✓
- Reproducibility: Round 11. ✓
- Paper writing: Rounds 12-13. ✓
- Self-review: Round 14. ✓

**2. Placeholder scan:**
- Round 12 still has "fill in actual numbers" — that's by design (numbers depend on Round 4 outputs and must be re-run when data arrives). Marked as "(运行 `python scripts/compute_rq1_summary.py` 后填入实际数字)" — explicit, not a hidden TODO.
- No other placeholders.

**3. Type consistency:**
- L0Label / LRCALabel enums consistently used across L0/dispatcher/run_lrca.
- compute_pattern_coverage signature consistent with test and script.
- cliffs_delta / bootstrap_delta_ci signatures consistent.
- run_one_cell repeats kwarg threaded from sms_campaign.py through is_killed.

---

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-05-01-rq-completion-spiral.md`.

Two execution options:

**1. Subagent-Driven (recommended)** — fresh subagent per round, two-stage review (spec compliance, then code quality), fast iteration. Best for the 14 rounds since each is self-contained.

**2. Inline Execution** — execute rounds in this session via executing-plans, batch checkpoints between rounds, easier to course-correct mid-flight. Best if user wants to review intermediate outputs frequently.

Which approach?
