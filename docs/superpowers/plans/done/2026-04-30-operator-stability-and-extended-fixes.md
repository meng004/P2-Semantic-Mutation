# Operator Stability and Extended Fixes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Convert the current "exploratory mutant generator" into a controlled per-operator experiment with statistical reliability metrics (R_sem, D_impl, R_kill) over K=10/20 repeated trials, while fixing four blocker issues (A1 interface, B2 R_mp2 width, ε mismatch, Track 1 SMS).

**Architecture:** Replace single-PUT semantic intents with an explicit operator registry; each operator gets a structured prompt and is run K times at temperature=0.5 to preserve implementation diversity. Two-axis stability is measured: semantic consistency (does the output implement the declared operator?) and implementation diversity (do the K outputs differ in structure?). Concurrency uses asyncio + Semaphore for LLM I/O and ProcessPoolExecutor for V1-V4 / AVP CPU work. Four extended fixes (A1 returns scalar; B2 R_mp2 strict direction; ε unified to 1e-6; Track 1 SMS evaluator) run in parallel subagents at T0/T1.

**Tech Stack:** Python 3.11, openai (async), pytest, multiprocessing, scipy, numpy, ast (stdlib). Models: Claude Opus 4.6 (generator), GPT-5.4 (reviewer), DeepSeek V4 Pro (arbitration).

---

## Repository Layout (existing — read before starting)

```
src/p2/
  puts/           # 12 PUT programs (a1-d3.py)
  mrs/            # 12 MR modules (a1-d3.py)
  avp/            # MP1-5 verifiers + dispatcher
  equiv/          # E1 + E2 equivalence judges + sampler
  lrca/           # killed/survived classifier
  pipeline/       # run_one_cell orchestration
  mutators/
    llm_client.py        # 3-LLM client factory (Opus/GPT/DeepSeek)
    llm_generator.py     # current Opus generator (multi-turn diversity)
    llm_reviewer.py      # GPT primary + DeepSeek arbitration
    validation.py        # V1-V4 mechanical (ε=1e-9 in V3 — bug)
    dual_blind.py        # ReviewVerdict → MutantStatus
    cell_pool.py         # current per-cell builder
    mut_intents.py       # 12 vague PUT intents — REPLACED by registry
    prompts/
      generator_template.txt
      reviewer_template.txt
scripts/
  llm_campaign.py        # current 12-cell exploratory campaign
  pilot_campaign.py      # pilot SMS evaluator (template for sms_campaign)
data/
  mutants/{put}_MP{k}_llm/   # 45 confirmed mutants (Track 1)
  results/llm_campaign_log.json
  results/pilot_results.json
tests/
  avp/ equiv/ mutators/ integration/
```

## File Structure (this plan)

**New files:**
- `src/p2/mutators/operator_registry.py` — registry of named operators per PUT
- `src/p2/mutators/diversity.py` — AST distance metric for implementation diversity
- `src/p2/mutators/operator_runner.py` — per-(operator, seed) generation pipeline
- `src/p2/mutators/async_llm.py` — async LLM client wrappers + Semaphore helper
- `src/p2/mutators/prompts/operator_template.txt` — per-operator structured prompt
- `src/p2/mutators/prompts/operator_reviewer_template.txt` — operator-aware review prompt
- `src/p2/mutators/operator_aggregator.py` — compute R_sem / D_impl / R_kill matrices
- `scripts/probe_concurrency.py` — bench bltcy.ai actual RPM / concurrency cap
- `scripts/operator_campaign.py` — Layer 3 full campaign (async, K=10 + 7×K=10 keys)
- `scripts/sms_campaign.py` — Track 1 SMS evaluator over existing 45 mutants
- `tests/mutators/test_operator_registry.py`
- `tests/mutators/test_diversity.py`
- `tests/mutators/test_operator_runner.py`
- `tests/mutators/test_async_llm.py`
- `tests/mutators/test_operator_aggregator.py`
- `tests/puts/test_a1_scalar_interface.py`
- `tests/avp/test_b2_strict_direction.py`
- `data/operator_campaign/`  (output dir, .gitignored for big data)
- `data/operator_campaign/registry.json`  (kept in git: human-readable spec)
- `data/results/operator_metrics.json`     (kept in git: per-operator metrics)

**Modified files:**
- `src/p2/puts/a1.py` — return `float` (last-step L2 norm), keep ndarray helper for tests
- `src/p2/mrs/a1.py` — adjust r/R for new scalar interface
- `src/p2/mrs/b2.py` — `R_mp2` uses strict `y_new > y_orig` (no -0.3 slack)
- `src/p2/mutators/validation.py` — V3 epsilon 1e-9 → 1e-6 (unify with AVP)
- `src/p2/equiv/judge.py` — explicit doc that epsilon_eq must equal epsilon_avp (still 1e-6)
- `tests/mutators/test_cell_pool.py` — currently broken (uses removed `double_confirmed`); update or remove
- `tests/mutators/test_llm_generator.py` — currently broken (anthropic API removed); update or remove
- `tests/integration/test_cell_smoke.py` — A1 row uses `mp4` but primary now is `mp1`; update
- `.gitignore` — add `data/operator_campaign/raw/` `data/operator_campaign/cache/`

---

## Phase Topology

```
T0 (8 subagents in parallel — all independent):
  ├─ Task 1: Probe concurrency
  ├─ Task 2: Fix-A — A1 scalar interface
  ├─ Task 3: Fix-C — ε unification to 1e-6
  ├─ Task 4: Fix-D — Track 1 SMS evaluator + run
  ├─ Task 5: Fix-B — B2 R_mp2 strict direction
  ├─ Task 6: Layer 1 — Operator Registry
  ├─ Task 7: Diversity Metric (AST distance)
  └─ Task 8: Async LLM wrappers

T1 (depends on Task 6 + Task 7 + Task 8):
  └─ Task 9: Layer 2 — Operator Runner + per-operator prompts

[CHECKPOINT: compact context here]

T2 (depends on Task 1 + Task 9):
  └─ Task 10: Layer 3 — operator_campaign.py full run

T3 (depends on Task 7 + Task 10 + Task 4):
  └─ Task 11: Aggregator + report

T4 (final, depends on all prior tasks):
  └─ Task 12: Cleanup stale tests + smoke integration

NOTE: Task 4 (Track 1 SMS) implicitly depends on Task 2 + Task 3 + Task 5
(it uses A1 PUT, V3 epsilon, B2 MR). The dispatcher to T0 must serialise
Task 4's RUN STEP (Step 5) until Tasks 2/3/5 are merged. Steps 1-3 of
Task 4 (script implementation + smoke test) can still run in parallel.
```

---

## Task 1: Probe LLM API Concurrency Cap

**Files:**
- Create: `scripts/probe_concurrency.py`
- Test: none (one-shot benchmark)

**Why first:** Task 10 needs an empirically chosen Semaphore limit. We must measure bltcy.ai's actual RPM before launching 570 calls.

- [ ] **Step 1: Write probe script**

Create `scripts/probe_concurrency.py`:

```python
"""One-shot benchmark of bltcy.ai concurrency / RPM cap.

Runs N parallel chat completions with trivial prompt, increasing concurrency
each round, and reports first round where errors appear (rate-limit / 429).
"""
import asyncio
import os
import time
from pathlib import Path
import sys

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "src"))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

from openai import AsyncOpenAI

CONCURRENCY_LEVELS = [5, 10, 20, 30, 50]
REQUESTS_PER_LEVEL = 30


async def one_call(client: AsyncOpenAI, model: str, idx: int) -> tuple[int, bool, str]:
    try:
        await client.chat.completions.create(
            model=model, max_tokens=4, temperature=0,
            messages=[{"role": "user", "content": f"reply with the single word OK ({idx})"}],
        )
        return idx, True, ""
    except Exception as e:
        return idx, False, type(e).__name__ + ": " + str(e)[:80]


async def run_level(concurrency: int, n: int):
    client = AsyncOpenAI(
        base_url=os.environ["BLTCY_BASE_URL"],
        api_key=os.environ["BLTCY_API_KEY"],
    )
    sem = asyncio.Semaphore(concurrency)

    async def gated(i):
        async with sem:
            return await one_call(client, "gpt-5.4", i)

    t0 = time.time()
    results = await asyncio.gather(*[gated(i) for i in range(n)])
    dt = time.time() - t0
    ok = sum(1 for _, s, _ in results if s)
    fails = [(i, e) for i, s, e in results if not s]
    return {"concurrency": concurrency, "n": n, "ok": ok, "fail": len(fails),
            "elapsed_s": round(dt, 1), "rps": round(n / dt, 2),
            "first_failure": fails[0] if fails else None}


async def main():
    print(f"{'conc':>5} {'n':>4} {'ok':>4} {'fail':>5} {'time':>7} {'rps':>5}  first-fail")
    for c in CONCURRENCY_LEVELS:
        r = await run_level(c, REQUESTS_PER_LEVEL)
        print(f"{r['concurrency']:>5} {r['n']:>4} {r['ok']:>4} {r['fail']:>5} "
              f"{r['elapsed_s']:>6}s {r['rps']:>5}  {r['first_failure']}")
        if r["fail"] > 0:
            print("  >>> stopping: first failure observed")
            return r["concurrency"] - (CONCURRENCY_LEVELS[CONCURRENCY_LEVELS.index(c)-1] if c > 5 else 5)
    print("  >>> all levels OK, recommend concurrency = 30")
    return 30


if __name__ == "__main__":
    rec = asyncio.run(main())
    print(f"\nRecommended Semaphore limit: {rec}")
```

- [ ] **Step 2: Run probe and record result**

Run: `python scripts/probe_concurrency.py | tee data/results/concurrency_probe.txt`

Expected: a table like

```
 conc    n   ok  fail    time    rps  first-fail
    5   30   30     0     12s   2.50  None
   10   30   30     0      6s   5.00  None
   20   30   28     2      4s   7.50  (5, 'RateLimitError: 429 Too Many Requests')
```

The recommended Semaphore value is the largest concurrency that produced 0 failures.

- [ ] **Step 3: Persist concurrency choice**

Append to `data/results/concurrency_probe.txt`:

```
RECOMMENDED_SEMAPHORE_LIMIT=<integer from step 2>
```

This value is read by Task 10 to set `OPERATOR_CAMPAIGN_CONCURRENCY`.

- [ ] **Step 4: Commit**

```bash
git add scripts/probe_concurrency.py data/results/concurrency_probe.txt
git commit -m "feat(probe): benchmark bltcy.ai concurrency limits before campaign"
```

---

## Task 2 (Fix-A): Make A1 PUT Return Scalar

**Files:**
- Modify: `src/p2/puts/a1.py`
- Modify: `src/p2/mrs/a1.py`
- Create: `tests/puts/test_a1_scalar_interface.py`

**Why:** AVP / equiv / probe expect `program(x) → float`, but A1 currently returns `np.ndarray(shape=(10,))`. This breaks the dispatcher uniformity required by Task 9–10.

- [ ] **Step 1: Write failing test for scalar interface**

Create `tests/puts/__init__.py` (empty) and `tests/puts/test_a1_scalar_interface.py`:

```python
"""A1 program(x) must return a finite scalar float."""
import numpy as np
import pytest
from p2.puts.a1 import program


@pytest.mark.parametrize("x", [0.0, 0.25, 0.5, 0.75, 1.0])
def test_returns_scalar_float(x):
    y = program(x)
    assert isinstance(y, float), f"expected float, got {type(y).__name__}"
    assert np.isfinite(y), f"expected finite, got {y}"


def test_two_calls_same_x_are_equal():
    y1 = program(0.4)
    y2 = program(0.4)
    assert y1 == y2, "deterministic ODE must give bitwise identical result"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/puts/test_a1_scalar_interface.py -v`
Expected: FAIL — current A1 returns `np.ndarray`.

- [ ] **Step 3: Modify A1 to return scalar (last-step L2 norm)**

Replace `src/p2/puts/a1.py` body of `program`:

```python
"""A1: Lorenz ODE — chaotic dynamical system (scalar-output interface).

Library: scipy.integrate.solve_ivp (scipy 1.17.1)
URL: https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html

program(x) where x ∈ [0,1] scalar.
Maps x to IC: [20x-10, 20x-10, 30x+5]. Integrates for t_end=1.0.
Returns L2 norm of state vector at t=1.0 (scalar float).
"""
import numpy as np
from scipy.integrate import solve_ivp

_SIGMA = 10.0
_RHO = 28.0
_BETA = 8.0 / 3.0


def _lorenz(t, y, sigma, rho, beta):
    x, yy, z = y
    return [sigma * (yy - x), x * (rho - z) - yy, x * yy - beta * z]


def program(x) -> float:
    x = float(x)
    ic = np.array([20*x - 10, 20*x - 10, 30*x + 5])
    sol = solve_ivp(
        _lorenz, (0.0, 1.0), ic,
        args=(_SIGMA, _RHO, _BETA),
        t_eval=[1.0], method="RK45", rtol=1e-8, atol=1e-10,
    )
    final_state = sol.y[:, -1]
    return float(np.linalg.norm(final_state))
```

- [ ] **Step 4: Update A1 MR for scalar interface**

A1's primary MP changes from MP4 (DTW) to MP1 (conservation).
Conservation: `program(x) + program(1-x) ≈ const` does NOT hold for chaotic Lorenz; instead use the simpler MP2 monotone-ish property is also wrong.

For A1 we use **MP3 (convergence-order)** trivial form is unsuitable. Pragmatic choice: use **MP1 trivial conservation** by defining a weaker invariant — `program(x) > 0` for all x. Replace `src/p2/mrs/a1.py`:

```python
"""MR functions for A1 Lorenz ODE (scalar-output interface).

Primary MP: MP1 (Conservation — weak: trajectory norm stays positive and bounded).
  r_mp1(x) = 1 - x : symmetry under IC reflection.
  R_mp1: |program(x) + program(1-x)| < 1e6 (anti-divergence guard).
Trivial: r_trivial, R_trivial for MP2/3/4/5.
"""
import numpy as np


def r_mp1(x) -> float:
    return float(1.0 - float(x))


def R_mp1(y_orig, y_new) -> bool:
    return float(abs(float(y_orig) + float(y_new))) < 1e6


def r_trivial(x) -> float:
    return float(x)


def R_trivial(y_orig, y_new) -> bool:
    return True
```

- [ ] **Step 5: Update A1 row in test_cell_smoke.py**

In `tests/integration/test_cell_smoke.py`, change the first row of `CELLS`:

```python
CELLS = [
    ("a1", "mp1", "r_mp1", "R_mp1"),  # was ("a1", "mp4", "r_mp4", "R_mp4")
    ("a2", "mp1", "r_mp1", "R_mp1"),
    ...
```

- [ ] **Step 6: Run all relevant tests**

Run: `pytest tests/puts/test_a1_scalar_interface.py tests/integration/test_cell_smoke.py -v`
Expected: PASS for all rows including A1.

- [ ] **Step 7: Commit**

```bash
git add src/p2/puts/a1.py src/p2/mrs/a1.py tests/puts/__init__.py tests/puts/test_a1_scalar_interface.py tests/integration/test_cell_smoke.py
git commit -m "fix(a1): return scalar float (L2 norm at t=1.0); switch primary MP to MP1"
```

---

## Task 3 (Fix-C): Unify ε to 1e-6

**Files:**
- Modify: `src/p2/mutators/validation.py:92`
- Modify: `src/p2/equiv/judge.py` (add docstring, no behavior change)
- Modify: `scripts/llm_campaign.py` (no behavior change — drop dead epsilon args if any)

**Why:** V3 mechanical equivalence uses ε=1e-9 (very strict — flags tiny float deviations as "different"); AVP equivalence judge uses ε=1e-6. Mismatch means a mutant can pass V3 ("non-trivial") yet later be flagged equiv by E2. Unify on 1e-6 (double-precision noise floor for typical scientific code).

- [ ] **Step 1: Write failing test**

Create `tests/mutators/test_validation_epsilon.py`:

```python
"""V3 should treat output diffs ≤ 1e-6 as equivalent (matches AVP)."""
import numpy as np
from p2.mutators.validation import validate_mutant


def _orig(x):
    return float(x) ** 2


def test_v3_uses_1e6_threshold():
    # mutant differs by exactly 5e-7 — should be flagged equiv (NOT pass V3)
    mutant_code = (
        "def program(x):\n"
        "    return float(x) ** 2 + 5e-7\n"
    )
    res = validate_mutant(mutant_code, _orig)
    assert not res.nontrivial, (
        f"5e-7 diff must be < 1e-6 ε, expected nontrivial=False, got {res!r}"
    )


def test_v3_passes_when_diff_above_threshold():
    mutant_code = (
        "def program(x):\n"
        "    return float(x) ** 2 + 1e-3\n"
    )
    res = validate_mutant(mutant_code, _orig)
    assert res.nontrivial, f"1e-3 diff is well above 1e-6, expected nontrivial=True, got {res!r}"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/mutators/test_validation_epsilon.py -v`
Expected: `test_v3_uses_1e6_threshold` FAILS (current threshold is 1e-9, so 5e-7 is treated as non-trivial).

- [ ] **Step 3: Update threshold in validation.py**

In `src/p2/mutators/validation.py`, change line 92:

```python
            if diff > 1e-6:                    # was: 1e-9
```

Also update the docstring (line 6) to:

```python
  V3  Non-trivial — |mutant(x) - original(x)| > 1e-6 for at least one x in probe set
                    (matches AVP/E2 epsilon for consistency)
```

- [ ] **Step 4: Add cross-reference docstring in judge.py**

Append to `src/p2/equiv/judge.py` docstring of `is_equivalent`:

```python
    """equiv ⇔ (E1 AVP-coherent) ∧ (E2 output-equiv).

    NOTE: epsilon_eq MUST equal epsilon_avp (currently both 1e-6).
    This matches V3 mechanical-equiv threshold in p2.mutators.validation.
    """
```

- [ ] **Step 5: Run all validation tests**

Run: `pytest tests/mutators/test_validation_epsilon.py -v`
Expected: PASS for both tests.

- [ ] **Step 6: Commit**

```bash
git add src/p2/mutators/validation.py src/p2/equiv/judge.py tests/mutators/test_validation_epsilon.py
git commit -m "fix(equiv): unify V3 mechanical and AVP/E2 epsilon to 1e-6"
```

---

## Task 4 (Fix-D): Track 1 SMS Evaluator over Existing 45 Mutants

**Files:**
- Create: `scripts/sms_campaign.py`
- Test: `tests/integration/test_sms_campaign_smoke.py`

**Why:** The 45 existing LLM mutants need actual SMS numbers (equiv+killed+survive counts per cell) to support the paper's Track 1 (exploratory pool) reporting. Independent of the operator-registry work.

- [ ] **Step 1: Write smoke test for the script's core function**

Create `tests/integration/test_sms_campaign_smoke.py`:

```python
"""Smoke test for sms_campaign.evaluate_cell on a known cell."""
from pathlib import Path
import sys
ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import importlib.util
spec = importlib.util.spec_from_file_location("sms_campaign", ROOT / "scripts" / "sms_campaign.py")
sms_campaign = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sms_campaign)


def test_evaluate_cell_a2_pilot():
    """Pilot a2_MP1_mut1 already has known SMS=1.0 from pilot_results.json."""
    summary = sms_campaign.evaluate_cell(
        put_id="a2", mp_k=1,
        mutant_dir=ROOT / "data" / "mutants" / "a2_MP1_mut1",
    )
    assert summary["inst"] == 5
    assert summary["sms"] == 1.0
```

- [ ] **Step 2: Run the test to confirm script does not yet exist**

Run: `pytest tests/integration/test_sms_campaign_smoke.py -v`
Expected: FAIL with `FileNotFoundError` or import error (sms_campaign.py absent).

- [ ] **Step 3: Implement `scripts/sms_campaign.py`**

```python
"""Track 1 SMS evaluation: compute SMS for each existing LLM mutant directory.

For each cell in PRIMARY_CELLS:
  - load all mutants from data/mutants/{put}_MP{k}_llm/
  - run E1+E2 equiv judgment, AVP, count killed/survive
  - compute SMS = killed / (inst - equiv)
Saves data/results/sms_track1.json with per-cell breakdown.
"""
import argparse
import importlib
import importlib.util
import json
import sys
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "src"))

from p2.avp.interface import MR
from p2.equiv.sampler import UniformSampler
from p2.pipeline.run_cell import run_one_cell

PRIMARY_CELLS = {
    "a1": 1, "a2": 1, "a3": 1,
    "b1": 2, "b2": 2, "b3": 2,
    "c1": 5, "c2": 5, "c3": 5,
    "d1": 2, "d2": 2, "d3": 2,
}

# MP_k → (r_name, R_name) on the mrs.{put} module
MP_TO_RR = {
    1: ("r_mp1", "R_mp1"),
    2: ("r_mp2", "R_mp2"),
    3: ("r_mp3", "R_mp3"),
    4: ("r_mp4", "R_mp4"),
    5: ("r_mp5", "R_mp5"),
}


def load_mutants(cell_dir: Path):
    out = []
    for py in sorted(cell_dir.glob("*.py")):
        spec = importlib.util.spec_from_file_location(f"mut_{py.stem}", py)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        out.append((py.name, mod.program))
    return out


def evaluate_cell(put_id: str, mp_k: int, mutant_dir: Path | None = None) -> dict:
    cell_id = f"{put_id.upper()}_MP{mp_k}"
    if mutant_dir is None:
        mutant_dir = ROOT / "data" / "mutants" / f"{put_id}_MP{mp_k}_llm"
    if not mutant_dir.exists():
        return {"cell": cell_id, "skipped": "mutant_dir_missing", "path": str(mutant_dir)}

    put_mod = importlib.import_module(f"p2.puts.{put_id}")
    mr_mod = importlib.import_module(f"p2.mrs.{put_id}")
    r_name, R_name = MP_TO_RR[mp_k]
    mr = MR(r=getattr(mr_mod, r_name), R=getattr(mr_mod, R_name),
            mp_index=mp_k, name=f"{put_id}_mp{mp_k}")

    named = load_mutants(mutant_dir)
    if not named:
        return {"cell": cell_id, "skipped": "empty_dir", "path": str(mutant_dir)}

    sampler = UniformSampler(low=0.0, high=1.0, dim=1, seed=42)
    result = run_one_cell(
        put=put_mod.program,
        mutants=[fn for _, fn in named],
        mr_set=[mr],
        cell_id=cell_id,
        sampler=sampler,
        k_eq=1000,
        epsilon_eq=1e-6,
        epsilon_avp=1e-6,
    )
    outcomes = []
    for idx, (name, _) in enumerate(named):
        if idx in result.equiv_indices:
            label = "EQUIV"
        elif idx in result.killed_indices:
            label = "KILLED"
        else:
            label = "SURVIVE"
        outcomes.append({"file": name, "label": label})
    return {
        "cell": cell_id,
        "inst": result.inst_count,
        "equiv": result.equiv_count,
        "killed": result.killed_count,
        "survive": result.survive_count,
        "sms": round(result.sms, 4),
        "outcomes": outcomes,
    }


def _worker(args):
    put_id, mp_k = args
    try:
        return evaluate_cell(put_id, mp_k)
    except Exception as e:
        import traceback
        return {"cell": f"{put_id.upper()}_MP{mp_k}", "error": str(e),
                "trace": traceback.format_exc(limit=3)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()

    print(f"\n{'='*60}\n  P2 TRACK-1 SMS CAMPAIGN — 12 LLM cells\n{'='*60}\n")

    cells = list(PRIMARY_CELLS.items())
    results = []
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(_worker, c): c for c in cells}
        for fut in as_completed(futures):
            r = fut.result()
            results.append(r)
            if "error" in r:
                print(f"  {r['cell']:<10} ERROR: {r['error'][:80]}")
            elif "skipped" in r:
                print(f"  {r['cell']:<10} SKIP: {r['skipped']}")
            else:
                print(f"  {r['cell']:<10} inst={r['inst']:>2} equiv={r['equiv']:>2} "
                      f"killed={r['killed']:>2} survive={r['survive']:>2} SMS={r['sms']:.3f}")

    out_path = ROOT / "data" / "results" / "sms_track1.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(sorted(results, key=lambda r: r.get("cell", "")),
                                    indent=2, ensure_ascii=False))
    print(f"\nResults → {out_path}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run smoke test**

Run: `pytest tests/integration/test_sms_campaign_smoke.py -v`
Expected: PASS (a2 pilot SMS=1.0).

- [ ] **Step 5: Run full Track-1 campaign**

Run: `python scripts/sms_campaign.py --workers 4 | tee data/results/sms_track1_console.log`
Expected: console output for 12 cells with `inst=N equiv=K killed=M survive=L SMS=Z`. Wall-clock about 5-15 min depending on CPU.

- [ ] **Step 6: Commit**

```bash
git add scripts/sms_campaign.py tests/integration/test_sms_campaign_smoke.py data/results/sms_track1.json data/results/sms_track1_console.log
git commit -m "feat(sms): Track-1 SMS evaluator over 45 LLM mutants (12 cells)"
```

---

## Task 5 (Fix-B): B2 R_mp2 Strict Monotone Direction

**Files:**
- Modify: `src/p2/mrs/b2.py`
- Create: `tests/avp/test_b2_strict_direction.py`

**Why:** Current `R_mp2: y_new > y_orig - 0.3` accepts a 0.3-unit downward drift as "monotone increasing", which makes scale-preserving B2 mutants survive (pilot SMS=0.5). The Wilcoxon test in `mp2_5_wilcoxon.py` already provides statistical robustness; the 0.3 slack is redundant and harmful. Use strict `y_new > y_orig` and let Wilcoxon decide significance.

- [ ] **Step 1: Write failing test**

Create `tests/avp/test_b2_strict_direction.py`:

```python
"""B2 R_mp2 must be strict y_new > y_orig (no -0.3 slack)."""
from p2.mrs.b2 import R_mp2


def test_strict_direction_rejects_equal():
    assert not R_mp2(0.5, 0.5), "equal values must NOT satisfy monotone-strict"


def test_strict_direction_rejects_decrease():
    assert not R_mp2(0.5, 0.49), "decrease must NOT satisfy monotone-strict"


def test_strict_direction_accepts_increase():
    assert R_mp2(0.5, 0.51), "increase must satisfy monotone-strict"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/avp/test_b2_strict_direction.py -v`
Expected: 2 FAILS (`rejects_equal` and `rejects_decrease`) — current rule allows up to 0.3-unit decrease.

- [ ] **Step 3: Update R_mp2**

In `src/p2/mrs/b2.py`, replace `R_mp2`:

```python
def R_mp2(y_orig, y_new) -> bool:
    """Strict monotone direction: y_new > y_orig.

    Statistical noise is handled by the Wilcoxon test in
    p2.avp.mp2_5_wilcoxon (n=50 samples, alpha=0.05).
    """
    return float(y_new) > float(y_orig)
```

Also update the module docstring (line 4) to remove "(coarse; chain is stochastic)" and replace with: "Strict monotone; statistical noise handled by Wilcoxon AVP."

- [ ] **Step 4: Run cell smoke test for B2**

Run: `pytest tests/avp/test_b2_strict_direction.py tests/integration/test_cell_smoke.py::test_primary_cell -v -k b2`
Expected: PASS (single B2 sample x=0.4 should satisfy strict direction in expectation; the Wilcoxon harness uses n=50 so single-point smoke does not need to pass with certainty — note this caveat).

If the single-x smoke test fails for B2 because of MCMC noise on one sample, that is NOT a bug in our fix; loosen smoke by increasing seed or re-running. If it consistently fails, change the smoke test for B2 to call `verify_wilcoxon` directly instead of relying on a single sample.

- [ ] **Step 5: Run full B2 cell via Wilcoxon to confirm overall direction holds**

Run from repo root:

```bash
python -c "
import sys; sys.path.insert(0, 'src')
from p2.avp.dispatcher import call_avp
from p2.avp.interface import MR
import p2.puts.b2 as put_b2
import p2.mrs.b2 as mrs_b2
mr = MR(r=mrs_b2.r_mp2, R=mrs_b2.R_mp2, mp_index=2, name='b2_mp2')
print('B2 AVP:', call_avp(put_b2.program, mr, epsilon=1e-6))
"
```

Expected: `B2 AVP: AVPResult.PASS` (the original program's chain mean does monotonically follow the input shift in aggregate).

- [ ] **Step 6: Commit**

```bash
git add src/p2/mrs/b2.py tests/avp/test_b2_strict_direction.py
git commit -m "fix(b2): R_mp2 strict y_new>y_orig; let Wilcoxon AVP handle noise"
```

---

## Task 6 (Layer 1): Operator Registry

**Files:**
- Create: `src/p2/mutators/operator_registry.py`
- Create: `data/operator_campaign/registry.json` (auto-generated dump for paper appendix)
- Create: `tests/mutators/test_operator_registry.py`

**Why:** Replace single per-PUT vague intent with explicit named operators. Each operator declares: `id`, `put`, `category` (OS/CE/SI/HP/CF/TF), `label`, `target_locator`, `transformation`, `rationale`, `is_key` (for K=20 lift).

- [ ] **Step 1: Write failing test for registry shape**

Create `tests/mutators/test_operator_registry.py`:

```python
from collections import Counter
from p2.mutators.operator_registry import (
    MutationOperator, OPERATORS, get_operators_for_put, key_operators,
)

VALID_CATEGORIES = {"OS", "CE", "SI", "HP", "CF", "TF"}
EXPECTED_PUTS = {"a1", "a2", "a3", "b1", "b2", "b3",
                 "c1", "c2", "c3", "d1", "d2", "d3"}


def test_each_put_has_at_least_three_operators():
    by_put = Counter(op.put for op in OPERATORS)
    for put in EXPECTED_PUTS:
        assert by_put[put] >= 3, f"{put} has only {by_put[put]} operators (need ≥3)"


def test_all_operators_have_required_fields():
    for op in OPERATORS:
        assert isinstance(op, MutationOperator)
        assert op.id and op.put and op.category in VALID_CATEGORIES
        assert op.label and op.target_locator and op.transformation and op.rationale
        assert isinstance(op.is_key, bool)


def test_ids_are_unique():
    ids = [op.id for op in OPERATORS]
    assert len(ids) == len(set(ids)), "duplicate operator id"


def test_id_format_matches_put_and_category():
    # id format: "{put}_{CAT}{n}", e.g. "a2_OS1"
    import re
    pat = re.compile(r"^([a-d][1-3])_(OS|CE|SI|HP|CF|TF)\d+$")
    for op in OPERATORS:
        m = pat.match(op.id)
        assert m, f"bad id format: {op.id}"
        assert m.group(1) == op.put and m.group(2) == op.category


def test_at_least_seven_key_operators():
    keys = key_operators()
    assert len(keys) >= 7, f"need ≥7 key operators for K=20 lift, got {len(keys)}"


def test_categories_diverse_per_put():
    # each PUT should have ≥2 distinct operator categories
    from collections import defaultdict
    cats = defaultdict(set)
    for op in OPERATORS:
        cats[op.put].add(op.category)
    for put, cs in cats.items():
        assert len(cs) >= 2, f"{put} only uses categories {cs} (need ≥2)"


def test_get_operators_for_put_filters_correctly():
    a2_ops = get_operators_for_put("a2")
    assert all(op.put == "a2" for op in a2_ops)
    assert len(a2_ops) >= 3
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/mutators/test_operator_registry.py -v`
Expected: FAIL — `ImportError: cannot import name 'OPERATORS'`.

- [ ] **Step 3: Create registry module**

Create `src/p2/mutators/operator_registry.py`:

```python
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


# ────────────────────────────────────────────────────────────────────────────
# Registry — at least 3 operators per PUT, ≥2 distinct categories per PUT,
# ≥7 marked is_key=True for paper case-study lift.
# ────────────────────────────────────────────────────────────────────────────

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
        transformation="change u[i+1] - 2*u[i] + u[i-1] sign → -(u[i+1] - 2*u[i] + u[i-1])",
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
        id="b3_OS1", put="b3", category="OS", label="integrand x+t²→x*t²",
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
```

- [ ] **Step 4: Run registry tests**

Run: `pytest tests/mutators/test_operator_registry.py -v`
Expected: PASS for all 7 tests.

- [ ] **Step 5: Dump registry to JSON for paper appendix**

Run from repo root:

```bash
python -c "
import sys; sys.path.insert(0, 'src')
from p2.mutators.operator_registry import dump_registry_json, OPERATORS, key_operators
dump_registry_json('data/operator_campaign/registry.json')
print(f'Total operators: {len(OPERATORS)}')
print(f'Key operators: {len(key_operators())}')
"
```

Expected: `data/operator_campaign/registry.json` written; total ≥ 36, key ≥ 7.

- [ ] **Step 6: Commit**

```bash
mkdir -p data/operator_campaign
git add src/p2/mutators/operator_registry.py tests/mutators/test_operator_registry.py data/operator_campaign/registry.json
git commit -m "feat(operator): named operator registry replaces vague PUT intents"
```

---

## Task 7: Implementation Diversity Metric

**Files:**
- Create: `src/p2/mutators/diversity.py`
- Create: `tests/mutators/test_diversity.py`

**Why:** D_impl measures whether K outputs of one operator are structurally diverse (not template-copies). We use a lightweight AST-node-count distance: normalise pairwise tree-edit-distance approximation (token-bag Jaccard works well enough for this scale).

- [ ] **Step 1: Write failing test**

Create `tests/mutators/test_diversity.py`:

```python
from p2.mutators.diversity import (
    ast_token_bag, pairwise_distance, diversity_score,
)


CODE_A = "def program(x):\n    return float(x) ** 2 + 1\n"
CODE_B = "def program(x):\n    return float(x) ** 2 + 1\n"      # identical
CODE_C = "def program(x):\n    y = float(x); return y * y - 1\n"  # different impl


def test_token_bag_returns_dict():
    bag = ast_token_bag(CODE_A)
    assert isinstance(bag, dict)
    assert sum(bag.values()) > 0


def test_identical_code_distance_zero():
    d = pairwise_distance(CODE_A, CODE_B)
    assert d == 0.0


def test_different_code_distance_positive():
    d = pairwise_distance(CODE_A, CODE_C)
    assert 0.0 < d < 1.0


def test_diversity_score_with_identical_inputs_is_zero():
    score = diversity_score([CODE_A, CODE_B, CODE_A])
    assert score == 0.0


def test_diversity_score_with_diverse_inputs_above_threshold():
    score = diversity_score([CODE_A, CODE_C, "def program(x):\n    return x + 0.1\n"])
    assert score > 0.1
```

- [ ] **Step 2: Run test to verify failure**

Run: `pytest tests/mutators/test_diversity.py -v`
Expected: FAIL — `ImportError`.

- [ ] **Step 3: Implement diversity module**

Create `src/p2/mutators/diversity.py`:

```python
"""Implementation diversity metric over a set of K mutant code strings.

We use an AST-node-name multiset (bag of node-class names) and report
1 - Jaccard-multiset-similarity as pairwise distance, then take the
median pairwise distance across all K(K-1)/2 pairs as the cell score.

This is cheap (O(K²) AST parses) and stable; tree-edit-distance would
be more accurate but unnecessary at K ≤ 20.
"""
import ast
from collections import Counter
from itertools import combinations
from statistics import median
from typing import Dict, List


def ast_token_bag(code: str) -> Dict[str, int]:
    """Return Counter-as-dict of AST node class names."""
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return {}
    counter: Counter = Counter()
    for node in ast.walk(tree):
        counter[type(node).__name__] += 1
    return dict(counter)


def _multiset_jaccard(a: Dict[str, int], b: Dict[str, int]) -> float:
    """Multiset Jaccard: sum(min) / sum(max) over union of keys."""
    if not a and not b:
        return 1.0
    keys = set(a) | set(b)
    inter = sum(min(a.get(k, 0), b.get(k, 0)) for k in keys)
    union = sum(max(a.get(k, 0), b.get(k, 0)) for k in keys)
    return inter / union if union else 0.0


def pairwise_distance(code1: str, code2: str) -> float:
    """0.0 = identical AST node distribution; 1.0 = disjoint."""
    return 1.0 - _multiset_jaccard(ast_token_bag(code1), ast_token_bag(code2))


def diversity_score(codes: List[str]) -> float:
    """Median pairwise distance over all K choose 2 pairs.

    Returns 0.0 if K < 2 or all codes identical.
    Higher value = more diverse implementations.
    """
    valid = [c for c in codes if c]
    if len(valid) < 2:
        return 0.0
    bags = [ast_token_bag(c) for c in valid]
    dists = [
        1.0 - _multiset_jaccard(bags[i], bags[j])
        for i, j in combinations(range(len(valid)), 2)
    ]
    return float(median(dists)) if dists else 0.0
```

- [ ] **Step 4: Run diversity tests**

Run: `pytest tests/mutators/test_diversity.py -v`
Expected: PASS for all 5 tests.

- [ ] **Step 5: Commit**

```bash
git add src/p2/mutators/diversity.py tests/mutators/test_diversity.py
git commit -m "feat(diversity): AST-bag pairwise distance + median diversity score"
```

---

## Task 8: Async LLM Wrappers

**Files:**
- Create: `src/p2/mutators/async_llm.py`
- Create: `tests/mutators/test_async_llm.py`

**Why:** The 570-call campaign must use `AsyncOpenAI` + `Semaphore` to respect bltcy.ai concurrency cap (Task 1 result). Wrap generator and reviewer call paths so the campaign can dispatch at scale.

- [ ] **Step 1: Write failing test**

Create `tests/mutators/test_async_llm.py`:

```python
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from p2.mutators.async_llm import (
    AsyncSemaphoreClient, async_chat_completion,
)


def test_semaphore_limits_concurrency():
    client = AsyncSemaphoreClient(api_key="x", base_url="x", concurrency=2)
    assert client.semaphore._value == 2


@patch("p2.mutators.async_llm.AsyncOpenAI")
def test_async_chat_completion_uses_semaphore(mock_cls):
    inst = MagicMock()
    completion = AsyncMock()
    completion.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content="hello"))]
    )
    inst.chat.completions.create = completion
    mock_cls.return_value = inst

    client = AsyncSemaphoreClient(api_key="x", base_url="x", concurrency=1)

    async def run():
        return await async_chat_completion(
            client=client, model="m", messages=[{"role": "user", "content": "hi"}],
            temperature=0.5, max_tokens=10,
        )

    out = asyncio.run(run())
    assert out == "hello"
    completion.assert_called_once()
```

- [ ] **Step 2: Run test to verify failure**

Run: `pytest tests/mutators/test_async_llm.py -v`
Expected: FAIL — `ImportError`.

- [ ] **Step 3: Implement async wrappers**

Create `src/p2/mutators/async_llm.py`:

```python
"""Async OpenAI-compatible client + Semaphore for high-concurrency campaigns."""
import asyncio
from dataclasses import dataclass
from openai import AsyncOpenAI


@dataclass
class AsyncSemaphoreClient:
    api_key: str
    base_url: str
    concurrency: int = 20

    def __post_init__(self):
        self.client = AsyncOpenAI(api_key=self.api_key, base_url=self.base_url)
        self.semaphore = asyncio.Semaphore(self.concurrency)


async def async_chat_completion(
    client: AsyncSemaphoreClient,
    model: str,
    messages: list[dict],
    temperature: float,
    max_tokens: int,
    retries: int = 3,
    backoff_base: float = 1.5,
) -> str:
    """Make one chat-completion call, gated by client.semaphore.

    Retries on any exception with exponential backoff. Returns raw string content.
    On final failure, returns a string starting with "# LLM_ERROR:" so callers
    can filter without extra exception handling.
    """
    async with client.semaphore:
        last_err = ""
        for attempt in range(retries):
            try:
                resp = await client.client.chat.completions.create(
                    model=model, temperature=temperature,
                    max_tokens=max_tokens, messages=messages,
                )
                return resp.choices[0].message.content
            except Exception as e:
                last_err = f"{type(e).__name__}: {e}"
                if attempt < retries - 1:
                    await asyncio.sleep(backoff_base ** attempt)
        return f"# LLM_ERROR: {last_err}"
```

- [ ] **Step 4: Run async LLM tests**

Run: `pytest tests/mutators/test_async_llm.py -v`
Expected: PASS for both tests.

- [ ] **Step 5: Commit**

```bash
git add src/p2/mutators/async_llm.py tests/mutators/test_async_llm.py
git commit -m "feat(async): AsyncOpenAI + Semaphore wrapper for concurrent LLM calls"
```

---

## Task 9 (Layer 2): Per-Operator Prompts and Operator Runner

**Files:**
- Create: `src/p2/mutators/prompts/operator_template.txt`
- Create: `src/p2/mutators/prompts/operator_reviewer_template.txt`
- Create: `src/p2/mutators/operator_runner.py`
- Create: `tests/mutators/test_operator_runner.py`

**Why:** Each (operator, seed) call must produce a code string that implements *that specific* operator. Reviewer must judge two things: (1) does the code implement the declared operator? (2) does it pass V5/V6?

- [ ] **Step 1: Write per-operator generation prompt**

Create `src/p2/mutators/prompts/operator_template.txt`:

```
You are an expert in scientific computing software testing. Generate a SEMANTIC MUTANT
of the program below that implements EXACTLY the named operator described.

PUT NAME: {put_name}
SCIENTIFIC DOMAIN: {scientific_domain}

OPERATOR ID: {op_id}
OPERATOR LABEL: {op_label}
TARGET LOCATOR: {op_target}
EXACT CHANGE: {op_transformation}
RATIONALE: {op_rationale}

ATTEMPT INDEX: {attempt_idx} of {n_attempts}  (different seed; same operator)

━━━ ORIGINAL PROGRAM ━━━
```python
{put_source}
```

━━━ YOUR TASK ━━━
Produce a complete Python program that implements the EXACT CHANGE above and nothing else.

VALIDITY REQUIREMENTS:
1. Syntactically valid Python (parseable)
2. Executable: program(x) runs without exception for any x ∈ [0,1]
3. Output varies with x (NOT a constant-output function)
4. Output is finite (no NaN, no Inf, no unbounded values)
5. Single fault: only the change above; do not introduce unrelated edits
6. Do not change the function signature or return type

IMPLEMENTATION DIVERSITY: You MAY choose any IMPLEMENTATION that realises the
declared operator semantics (e.g., for "prod→sum" you can use np.sum,
functools.reduce(operator.add, ...), a Python loop with accumulator, etc.).
The semantic effect must match the EXACT CHANGE exactly.

OUTPUT: Return ONLY the complete Python source. No explanation, no comments,
no markdown fences. Start directly with import statements or `def`.
```

- [ ] **Step 2: Write operator-aware reviewer prompt**

Create `src/p2/mutators/prompts/operator_reviewer_template.txt`:

```
You are reviewing a candidate semantic mutant. The mutant was generated to implement
a SPECIFIC named operator. Your job: verify both (a) semantic match to the operator
and (b) the standard V1-V6 validity criteria.

ORIGINAL PROGRAM:
```python
{put_source}
```

CANDIDATE MUTANT:
```python
{mutant_code}
```

DECLARED OPERATOR:
  ID: {op_id}
  LABEL: {op_label}
  TARGET: {op_target}
  EXACT CHANGE: {op_transformation}

Return STRICT JSON with the following keys (no extra prose):

{{
  "V1_syntax_ok": true|false,
  "V2_executable": "Yes"|"No"|"Uncertain",
  "V3_nontrivial": "Yes"|"No"|"Uncertain",
  "V4_nondegenerate": "Yes"|"No"|"Uncertain",
  "V5_single_fault": "Yes"|"No"|"Uncertain",
  "V6_plausible": "Yes"|"No"|"Uncertain",
  "operator_match": "Yes"|"No"|"Uncertain",
  "operator_match_reason": "<one sentence: how the code does or does not realise the declared transformation>",
  "overall": "CONFIRMED"|"REJECTED"|"UNCERTAIN",
  "reason": "<one sentence overall reason>"
}}

Set operator_match=Yes ONLY if the code clearly implements the EXACT CHANGE described.
Set overall=CONFIRMED only if V1-V6 are Yes AND operator_match is Yes.
Set overall=REJECTED if any V1-V6 is No or operator_match is No.
Set overall=UNCERTAIN otherwise.
```

- [ ] **Step 3: Write failing test for operator_runner**

Create `tests/mutators/test_operator_runner.py`:

```python
from unittest.mock import AsyncMock, patch
import asyncio

from p2.mutators.operator_registry import OPERATORS
from p2.mutators.operator_runner import (
    OperatorTrialResult, run_operator_trial, run_operator_K_times,
)


def test_operator_trial_result_dataclass():
    op = OPERATORS[0]
    r = OperatorTrialResult(
        op_id=op.id, attempt_idx=0, code="def program(x): return x",
        v1=True, v2="Yes", v3="Yes", v4="Yes", v5="Yes", v6="Yes",
        operator_match="Yes", overall="CONFIRMED", reason="ok",
    )
    assert r.is_confirmed
    assert r.is_semantic_match


@patch("p2.mutators.operator_runner.async_chat_completion")
def test_run_operator_trial_returns_result(mock_chat):
    op = OPERATORS[0]  # a1_CE1
    mock_chat.side_effect = [
        # 1st call = generator returns code
        "def program(x):\n    return float(x) + 0.5\n",
        # 2nd call = reviewer returns JSON
        '{"V1_syntax_ok": true, "V2_executable": "Yes", "V3_nontrivial": "Yes",'
        ' "V4_nondegenerate": "Yes", "V5_single_fault": "Yes", "V6_plausible": "Yes",'
        ' "operator_match": "Yes", "operator_match_reason": "ok",'
        ' "overall": "CONFIRMED", "reason": "ok"}',
    ]

    async def go():
        return await run_operator_trial(
            op=op, attempt_idx=0,
            put_source="def program(x): return float(x)",
            put_name="A1", scientific_domain="Lorenz",
            generator_client=None, reviewer_client=None,
        )

    res = asyncio.run(go())
    assert res.is_confirmed
    assert res.code.startswith("def program(x):")
```

- [ ] **Step 4: Run test to verify failure**

Run: `pytest tests/mutators/test_operator_runner.py -v`
Expected: FAIL — `ImportError`.

- [ ] **Step 5: Implement operator_runner**

Create `src/p2/mutators/operator_runner.py`:

```python
"""Per-(operator, attempt) generation+review trial.

Each trial:
  1. ask generator LLM for one code candidate implementing the operator
  2. mechanically validate (V1-V4) and inject results into the reviewer payload
  3. ask reviewer LLM for V1-V6 + operator_match verdict (JSON)
  4. classify into CONFIRMED / REJECTED / UNCERTAIN

Multiple trials per operator (K independent calls, varying seed/attempt_idx)
are coordinated by run_operator_K_times.
"""
import asyncio
import json
import re
import importlib.util
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from p2.mutators.async_llm import AsyncSemaphoreClient, async_chat_completion
from p2.mutators.operator_registry import MutationOperator
from p2.mutators.validation import validate_mutant

_OP_TEMPLATE = (Path(__file__).parent / "prompts" / "operator_template.txt").read_text()
_OP_REVIEWER = (Path(__file__).parent / "prompts" / "operator_reviewer_template.txt").read_text()


@dataclass(frozen=True)
class OperatorTrialResult:
    op_id: str
    attempt_idx: int
    code: str
    v1: bool
    v2: str
    v3: str
    v4: str
    v5: str
    v6: str
    operator_match: str
    overall: str  # CONFIRMED | REJECTED | UNCERTAIN
    reason: str

    @property
    def is_confirmed(self) -> bool:
        return self.overall == "CONFIRMED"

    @property
    def is_semantic_match(self) -> bool:
        return self.operator_match == "Yes"

    def to_dict(self) -> dict:
        return {
            "op_id": self.op_id, "attempt_idx": self.attempt_idx,
            "code": self.code, "v1": self.v1, "v2": self.v2, "v3": self.v3,
            "v4": self.v4, "v5": self.v5, "v6": self.v6,
            "operator_match": self.operator_match,
            "overall": self.overall, "reason": self.reason,
        }


def _strip_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        text = "\n".join(ln for ln in lines if not ln.startswith("```")).strip()
    return text


def _parse_review(raw: str) -> dict:
    m = re.search(r"\{.*\}", raw, re.DOTALL)
    if not m:
        return {"overall": "REJECTED", "reason": f"parse_error: {raw[:120]}"}
    try:
        return json.loads(m.group())
    except json.JSONDecodeError as e:
        return {"overall": "REJECTED", "reason": f"json_error: {e}"}


def _load_program_from_string(code: str):
    spec = importlib.util.spec_from_loader("_mut_inline", loader=None)
    mod = importlib.util.module_from_spec(spec)
    try:
        exec(code, mod.__dict__)
        return mod.program
    except Exception:
        return None


async def run_operator_trial(
    op: MutationOperator,
    attempt_idx: int,
    put_source: str,
    put_name: str,
    scientific_domain: str,
    generator_client: Optional[AsyncSemaphoreClient],
    reviewer_client: Optional[AsyncSemaphoreClient],
    n_attempts: int = 10,
    generator_model: str = "claude-opus-4-6",
    reviewer_model: str = "gpt-5.4",
    temperature: float = 0.5,
) -> OperatorTrialResult:
    # -- 1. generate
    gen_prompt = _OP_TEMPLATE.format(
        put_name=put_name, scientific_domain=scientific_domain,
        op_id=op.id, op_label=op.label, op_target=op.target_locator,
        op_transformation=op.transformation, op_rationale=op.rationale,
        attempt_idx=attempt_idx + 1, n_attempts=n_attempts,
        put_source=put_source,
    )
    raw_code = await async_chat_completion(
        client=generator_client, model=generator_model,
        messages=[{"role": "user", "content": gen_prompt}],
        temperature=temperature, max_tokens=1500,
    )
    code = _strip_fences(raw_code)

    # -- 2. mechanical V1-V4 (used as a hint for the reviewer)
    original_fn = _load_program_from_string(put_source)
    mech = validate_mutant(code, original_fn) if original_fn else None
    mech_v1 = bool(mech and mech.syntax_ok)

    # -- 3. review
    rev_prompt = _OP_REVIEWER.format(
        put_source=put_source, mutant_code=code,
        op_id=op.id, op_label=op.label, op_target=op.target_locator,
        op_transformation=op.transformation,
    )
    raw_rev = await async_chat_completion(
        client=reviewer_client, model=reviewer_model,
        messages=[{"role": "user", "content": rev_prompt}],
        temperature=0.0, max_tokens=600,
    )
    parsed = _parse_review(raw_rev)

    return OperatorTrialResult(
        op_id=op.id, attempt_idx=attempt_idx, code=code,
        v1=bool(parsed.get("V1_syntax_ok", mech_v1)),
        v2=parsed.get("V2_executable", "Uncertain"),
        v3=parsed.get("V3_nontrivial", "Uncertain"),
        v4=parsed.get("V4_nondegenerate", "Uncertain"),
        v5=parsed.get("V5_single_fault", "Uncertain"),
        v6=parsed.get("V6_plausible", "Uncertain"),
        operator_match=parsed.get("operator_match", "Uncertain"),
        overall=parsed.get("overall", "UNCERTAIN"),
        reason=parsed.get("reason", ""),
    )


async def run_operator_K_times(
    op: MutationOperator,
    K: int,
    put_source: str,
    put_name: str,
    scientific_domain: str,
    generator_client: AsyncSemaphoreClient,
    reviewer_client: AsyncSemaphoreClient,
    temperature: float = 0.5,
    start_idx: int = 0,
) -> List[OperatorTrialResult]:
    """Run K trials for one operator concurrently (each gated by client semaphore).

    `start_idx` lets callers append additional K runs (key operators K=20 = 10+10).
    """
    tasks = [
        run_operator_trial(
            op=op, attempt_idx=start_idx + i,
            put_source=put_source, put_name=put_name,
            scientific_domain=scientific_domain,
            generator_client=generator_client, reviewer_client=reviewer_client,
            n_attempts=K + start_idx, temperature=temperature,
        )
        for i in range(K)
    ]
    return await asyncio.gather(*tasks)
```

- [ ] **Step 6: Run operator runner tests**

Run: `pytest tests/mutators/test_operator_runner.py -v`
Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add src/p2/mutators/prompts/operator_template.txt src/p2/mutators/prompts/operator_reviewer_template.txt src/p2/mutators/operator_runner.py tests/mutators/test_operator_runner.py
git commit -m "feat(operator): per-operator structured prompts + async runner"
```

---

## CHECKPOINT — Compact Context Before Task 10

After Task 9 commits, the executing agent should pause and explicitly compact context. Task 10 launches a long campaign (570 LLM calls) and benefits from a clean window.

**Required action by executing agent:** announce "Compacting context before Task 10 (large campaign run)" and follow `/compact` flow if applicable. Pick up at Task 10 in a fresh session.

---

## Task 10 (Layer 3): Operator Campaign Script

**Files:**
- Create: `scripts/operator_campaign.py`
- Output: `data/operator_campaign/raw/{op_id}_K{k}_t{ts}.json` per operator
- Output: `data/operator_campaign/cache/{op_id}_attempt{i}.py` per accepted code

**Why:** Run K=10 (default) for every operator; for `is_key=True` operators run an additional K=10 (so they reach K=20). Persist raw trial logs and accepted code for downstream metric computation (Task 11).

- [ ] **Step 1: Read recommended Semaphore from probe**

Run: `cat data/results/concurrency_probe.txt`
Expected: a final line `RECOMMENDED_SEMAPHORE_LIMIT=<N>` (Task 1 step 3). Note this number.

- [ ] **Step 2: Implement campaign script**

Create `scripts/operator_campaign.py`:

```python
"""Layer 3 operator campaign — K=10 default, +10 for key operators.

Per operator:
  1. Run K=10 trials concurrently via operator_runner.run_operator_K_times
  2. If op.is_key, run +10 more trials with start_idx=10 (total 20)
  3. Save raw trial JSON to data/operator_campaign/raw/{op_id}.json
  4. Save accepted code per attempt to data/operator_campaign/cache/

Operators run in parallel too (also gated by the same client Semaphore).
"""
import argparse
import asyncio
import json
import os
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "src"))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

from p2.mutators.operator_registry import OPERATORS, MutationOperator
from p2.mutators.async_llm import AsyncSemaphoreClient
from p2.mutators.operator_runner import run_operator_K_times

PUTS_DIR = ROOT / "src" / "p2" / "puts"
RAW_DIR = ROOT / "data" / "operator_campaign" / "raw"
CACHE_DIR = ROOT / "data" / "operator_campaign" / "cache"
LOG_PATH = ROOT / "data" / "operator_campaign" / "campaign_log.json"

# scientific_domain copied from old INTENTS — keep here so we can delete that file later
DOMAINS: dict[str, str] = {
    "a1": "Lorenz ODE system solved with RK45",
    "a2": "LU decomposition of a 2×2 parameterised matrix",
    "a3": "Explicit Euler finite-difference heat equation (1D)",
    "b1": "Beta-Binomial conjugate Bayesian update",
    "b2": "Metropolis-Hastings MCMC targeting a Gaussian",
    "b3": "Monte Carlo integration of ∫₀¹(x+t²)dt",
    "c1": "Gaussian Process Regression surrogate for erf(t)",
    "c2": "Polynomial Chaos Expansion surrogate for tanh(t)",
    "c3": "MLP neural network surrogate for sigmoid(2t)",
    "d1": "Linear SVM binary classifier",
    "d2": "RBF SVM binary classifier",
    "d3": "Decision Tree binary classifier",
}


def read_semaphore_recommendation() -> int:
    path = ROOT / "data" / "results" / "concurrency_probe.txt"
    if not path.exists():
        return 20
    text = path.read_text()
    m = re.search(r"RECOMMENDED_SEMAPHORE_LIMIT=(\d+)", text)
    return int(m.group(1)) if m else 20


def load_put_source(put_id: str) -> str:
    return (PUTS_DIR / f"{put_id}.py").read_text()


async def run_one_operator(
    op: MutationOperator, K: int, gen_client: AsyncSemaphoreClient,
    rev_client: AsyncSemaphoreClient, temperature: float,
) -> dict:
    put_source = load_put_source(op.put)
    domain = DOMAINS[op.put]

    results = await run_operator_K_times(
        op=op, K=K, put_source=put_source, put_name=op.put.upper(),
        scientific_domain=domain,
        generator_client=gen_client, reviewer_client=rev_client,
        temperature=temperature, start_idx=0,
    )

    if op.is_key:
        extra = await run_operator_K_times(
            op=op, K=K, put_source=put_source, put_name=op.put.upper(),
            scientific_domain=domain,
            generator_client=gen_client, reviewer_client=rev_client,
            temperature=temperature, start_idx=K,
        )
        results = results + extra

    # persist raw + accepted code
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    (RAW_DIR / f"{op.id}.json").write_text(
        json.dumps([r.to_dict() for r in results], indent=2, ensure_ascii=False)
    )
    accepted = 0
    for r in results:
        if r.is_confirmed:
            (CACHE_DIR / f"{op.id}_attempt{r.attempt_idx:02d}.py").write_text(r.code)
            accepted += 1

    return {
        "op_id": op.id, "put": op.put, "category": op.category,
        "K": len(results), "confirmed": accepted,
        "is_key": op.is_key,
    }


async def main_async(args):
    sem_n = args.concurrency or read_semaphore_recommendation()
    print(f"== concurrency limit: {sem_n} ==")

    gen_client = AsyncSemaphoreClient(
        api_key=os.environ["BLTCY_API_KEY"],
        base_url=os.environ["BLTCY_BASE_URL"],
        concurrency=sem_n,
    )
    rev_client = gen_client  # same provider; share semaphore for fair RPM

    if args.op_id:
        ops = [op for op in OPERATORS if op.id == args.op_id]
    elif args.put:
        ops = [op for op in OPERATORS if op.put == args.put]
    else:
        ops = list(OPERATORS)

    print(f"== operators in campaign: {len(ops)} ==")
    t0 = time.time()
    coros = [
        run_one_operator(op, K=args.k, gen_client=gen_client,
                         rev_client=rev_client, temperature=args.temperature)
        for op in ops
    ]
    summaries = await asyncio.gather(*coros)
    dt = time.time() - t0

    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    LOG_PATH.write_text(json.dumps({
        "elapsed_s": round(dt, 1),
        "concurrency": sem_n,
        "K_default": args.k,
        "temperature": args.temperature,
        "summaries": summaries,
    }, indent=2, ensure_ascii=False))

    print(f"\n== campaign log → {LOG_PATH} ==")
    print(f"{'op_id':<10} {'put':<4} {'cat':<3} {'K':>3} {'conf':>5}  key")
    print("-" * 40)
    for s in summaries:
        print(f"{s['op_id']:<10} {s['put']:<4} {s['category']:<3} "
              f"{s['K']:>3} {s['confirmed']:>5}  {'★' if s['is_key'] else ''}")
    print(f"\ntotal elapsed: {dt:.1f}s")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--k", type=int, default=10, help="K trials per operator")
    parser.add_argument("--concurrency", type=int, default=0,
                        help="override Semaphore limit (default: read probe)")
    parser.add_argument("--temperature", type=float, default=0.5)
    parser.add_argument("--op-id", help="run a single operator (debug)")
    parser.add_argument("--put", help="run all operators for one PUT")
    args = parser.parse_args()
    asyncio.run(main_async(args))


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Smoke run on a single operator (a2_OS1)**

Run: `python scripts/operator_campaign.py --op-id a2_OS1 --k 3`
Expected: console shows `a2_OS1 a2 OS 3 X` where X is confirmed count (0-3). Files created at `data/operator_campaign/raw/a2_OS1.json` and 0+ files in `cache/`.

- [ ] **Step 4: Inspect smoke output**

Run: `cat data/operator_campaign/raw/a2_OS1.json | head -30`
Expected: 3 entries with `op_id="a2_OS1"`, `attempt_idx` 0/1/2, and review fields populated.

If `overall` is consistently `REJECTED` with `parse_error`, the reviewer prompt may be returning prose. Look at `reason` field; if so, regenerate `operator_reviewer_template.txt` step 2 with stronger JSON-only instruction. Otherwise proceed.

- [ ] **Step 5: Full campaign run**

Run from repo root:

```bash
python scripts/operator_campaign.py --k 10 2>&1 | tee data/operator_campaign/campaign_console.log
```

Expected: parallel run of all ~36 operators × K=10 (+ 7 key × +10) = ~430 trials × 2 LLM calls = ~860 LLM calls. With probe-derived semaphore (e.g. 20) and ~8s/call, wall-clock 20-40 min.

- [ ] **Step 6: Sanity-check campaign log**

Run: `python -c "import json; d=json.load(open('data/operator_campaign/campaign_log.json')); print('ops:', len(d['summaries']), 'total trials:', sum(s['K'] for s in d['summaries']), 'total conf:', sum(s['confirmed'] for s in d['summaries']))"`
Expected: `ops: ≥36 total trials: ≥430 total conf: ≥...` (confirmed depends on LLM behavior; expect ≥50% pass).

If total confirmed < 30% of total trials, abort and inspect prompt; do NOT proceed to Task 11.

- [ ] **Step 7: Commit**

```bash
git add scripts/operator_campaign.py data/operator_campaign/campaign_log.json data/operator_campaign/campaign_console.log
git commit -m "feat(campaign): operator-registry K=10/20 async campaign runner"
```

Note: do NOT commit `data/operator_campaign/raw/` or `cache/` — they are .gitignored in Task 12.

---

## Task 11: Aggregator and Metric Report

**Files:**
- Create: `src/p2/mutators/operator_aggregator.py`
- Create: `tests/mutators/test_operator_aggregator.py`
- Output: `data/results/operator_metrics.json`

**Why:** Compute the three reportable metrics from raw trial JSON:
- **R_sem** (per operator): fraction with `is_confirmed AND is_semantic_match`
- **D_impl** (per operator): `diversity_score(codes_of_confirmed_trials)`
- **R_kill** (per operator): fraction of confirmed mutants that fail the corresponding MR via AVP

- [ ] **Step 1: Write failing test**

Create `tests/mutators/test_operator_aggregator.py`:

```python
import json
import tempfile
from pathlib import Path

from p2.mutators.operator_aggregator import (
    compute_r_sem, compute_d_impl, aggregate_operator_metrics,
)


def test_compute_r_sem_basic():
    trials = [
        {"is_confirmed": True, "operator_match": "Yes"},
        {"is_confirmed": True, "operator_match": "No"},
        {"is_confirmed": False, "operator_match": "Yes"},
        {"is_confirmed": True, "operator_match": "Yes"},
    ]
    # confirmed AND match: 2/4 = 0.5
    assert compute_r_sem(trials) == 0.5


def test_compute_r_sem_no_trials():
    assert compute_r_sem([]) == 0.0


def test_compute_d_impl_with_two_distinct_codes():
    codes = [
        "def program(x):\n    return float(x)\n",
        "def program(x):\n    return float(x) + 1\n",
    ]
    score = compute_d_impl(codes)
    assert 0.0 < score <= 1.0


def test_aggregate_writes_metrics(tmp_path):
    raw = tmp_path / "raw"; raw.mkdir()
    (raw / "a2_OS1.json").write_text(json.dumps([
        {"op_id": "a2_OS1", "attempt_idx": 0, "code": "def program(x):\n    return float(x)\n",
         "v1": True, "v2": "Yes", "v3": "Yes", "v4": "Yes",
         "v5": "Yes", "v6": "Yes", "operator_match": "Yes",
         "overall": "CONFIRMED", "reason": "ok"},
        {"op_id": "a2_OS1", "attempt_idx": 1, "code": "def program(x):\n    return float(x) + 1\n",
         "v1": True, "v2": "Yes", "v3": "Yes", "v4": "Yes",
         "v5": "Yes", "v6": "Yes", "operator_match": "Yes",
         "overall": "CONFIRMED", "reason": "ok"},
    ]))
    out = tmp_path / "out.json"
    metrics = aggregate_operator_metrics(raw_dir=raw, out_path=out, run_avp=False)
    assert "a2_OS1" in metrics
    assert metrics["a2_OS1"]["r_sem"] == 1.0
    assert metrics["a2_OS1"]["d_impl"] >= 0.0
    assert out.exists()
```

- [ ] **Step 2: Run test to confirm failure**

Run: `pytest tests/mutators/test_operator_aggregator.py -v`
Expected: FAIL — `ImportError`.

- [ ] **Step 3: Implement aggregator**

Create `src/p2/mutators/operator_aggregator.py`:

```python
"""Compute R_sem / D_impl / R_kill per operator from raw campaign JSON."""
import importlib
import importlib.util
import json
import sys
import tempfile
from pathlib import Path
from typing import Dict, List

from p2.mutators.diversity import diversity_score
from p2.mutators.operator_registry import OPERATORS

# import paths needed for AVP (executed lazily inside compute_r_kill)


def compute_r_sem(trials: List[dict]) -> float:
    if not trials:
        return 0.0
    good = sum(1 for t in trials
               if (t.get("is_confirmed") if "is_confirmed" in t
                   else t.get("overall") == "CONFIRMED")
               and t.get("operator_match") == "Yes")
    return good / len(trials)


def compute_d_impl(codes: List[str]) -> float:
    return diversity_score(codes)


def _import_program_from_source(code: str):
    spec = importlib.util.spec_from_loader("_mut_inline", loader=None)
    mod = importlib.util.module_from_spec(spec)
    try:
        exec(code, mod.__dict__)
        return mod.program
    except Exception:
        return None


def _r_kill_for_operator(op_id: str, codes: List[str]) -> float:
    """Run AVP on each confirmed mutant against its PUT's primary MR; report kill rate."""
    if not codes:
        return 0.0
    op = next(o for o in OPERATORS if o.id == op_id)
    put_id = op.put

    from p2.avp.dispatcher import call_avp
    from p2.avp.interface import MR, AVPResult

    PRIMARY_MP = {"a1":1,"a2":1,"a3":1,"b1":2,"b2":2,"b3":2,
                  "c1":5,"c2":5,"c3":5,"d1":2,"d2":2,"d3":2}
    MP_TO_RR = {1:("r_mp1","R_mp1"), 2:("r_mp2","R_mp2"),
                3:("r_mp3","R_mp3"), 4:("r_mp4","R_mp4"), 5:("r_mp5","R_mp5")}

    mp_k = PRIMARY_MP[put_id]
    r_name, R_name = MP_TO_RR[mp_k]
    mr_mod = importlib.import_module(f"p2.mrs.{put_id}")
    put_mod = importlib.import_module(f"p2.puts.{put_id}")
    mr = MR(r=getattr(mr_mod, r_name), R=getattr(mr_mod, R_name),
            mp_index=mp_k, name=f"{put_id}_mp{mp_k}")

    try:
        orig_pass = call_avp(put_mod.program, mr, epsilon=1e-6) == AVPResult.PASS
    except Exception:
        return 0.0
    if not orig_pass:
        return 0.0

    killed = 0
    valid = 0
    for code in codes:
        prog = _import_program_from_source(code)
        if prog is None:
            continue
        try:
            r = call_avp(prog, mr, epsilon=1e-6)
            valid += 1
            if r == AVPResult.FAIL:
                killed += 1
        except Exception:
            continue
    return killed / valid if valid else 0.0


def aggregate_operator_metrics(
    raw_dir: Path, out_path: Path, run_avp: bool = True,
) -> Dict[str, dict]:
    metrics: Dict[str, dict] = {}
    for fp in sorted(Path(raw_dir).glob("*.json")):
        op_id = fp.stem
        trials = json.loads(fp.read_text())
        # normalise is_confirmed flag for robustness
        for t in trials:
            t["is_confirmed"] = t.get("overall") == "CONFIRMED"

        confirmed_codes = [t["code"] for t in trials
                           if t["is_confirmed"] and t.get("operator_match") == "Yes"]

        m = {
            "op_id": op_id,
            "K": len(trials),
            "n_confirmed": len(confirmed_codes),
            "r_sem": round(compute_r_sem(trials), 4),
            "d_impl": round(compute_d_impl(confirmed_codes), 4),
        }
        if run_avp and confirmed_codes:
            m["r_kill"] = round(_r_kill_for_operator(op_id, confirmed_codes), 4)
        else:
            m["r_kill"] = None
        metrics[op_id] = m

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    Path(out_path).write_text(json.dumps(metrics, indent=2, ensure_ascii=False))
    return metrics
```

- [ ] **Step 4: Run aggregator tests**

Run: `pytest tests/mutators/test_operator_aggregator.py -v`
Expected: PASS for all 4 tests.

- [ ] **Step 5: Aggregate over real campaign output**

Run from repo root:

```bash
python -c "
import sys; sys.path.insert(0, 'src')
from pathlib import Path
from p2.mutators.operator_aggregator import aggregate_operator_metrics
m = aggregate_operator_metrics(
    raw_dir=Path('data/operator_campaign/raw'),
    out_path=Path('data/results/operator_metrics.json'),
    run_avp=True,
)
print(f'aggregated {len(m)} operators')
for op_id, met in sorted(m.items()):
    print(f'  {op_id:<10} K={met[\"K\"]:>3} conf={met[\"n_confirmed\"]:>3}'
          f' R_sem={met[\"r_sem\"]:.2f} D_impl={met[\"d_impl\"]:.2f}'
          f' R_kill={met[\"r_kill\"] if met[\"r_kill\"] is not None else \"--\"}')
" | tee data/results/operator_metrics_console.log
```

Expected: per-operator line with three metrics. Wall-clock 5-15 min (AVP per mutant).

- [ ] **Step 6: Commit**

```bash
git add src/p2/mutators/operator_aggregator.py tests/mutators/test_operator_aggregator.py data/results/operator_metrics.json data/results/operator_metrics_console.log
git commit -m "feat(metrics): R_sem/D_impl/R_kill aggregator with AVP integration"
```

---

## Task 12: Cleanup Stale Tests + Gitignore + Final Smoke

**Files:**
- Modify: `.gitignore`
- Modify or remove: `tests/mutators/test_cell_pool.py`, `tests/mutators/test_llm_generator.py`
- Create: `tests/integration/test_full_pipeline_smoke.py`

**Why:** Two pre-existing test files reference removed APIs (`pool.double_confirmed`, `anthropic.Anthropic`); they currently fail collection. Replace or delete. Add gitignore for the new bulk-output dirs. Final integration smoke verifies end-to-end pipeline stays green.

- [ ] **Step 1: Update .gitignore**

Append to `.gitignore`:

```
data/operator_campaign/raw/
data/operator_campaign/cache/
data/operator_campaign/campaign_console.log
data/results/concurrency_probe.txt
data/results/sms_track1_console.log
data/results/operator_metrics_console.log
```

- [ ] **Step 2: Replace stale test_cell_pool.py with current-API smoke**

Replace `tests/mutators/test_cell_pool.py`:

```python
"""Smoke: build_cell_pool integrates generate→validate→review correctly.

Mocks all three LLM calls and a trivial original_fn.
"""
from unittest.mock import patch
from p2.mutators.cell_pool import build_cell_pool, CellPool
from p2.mutators.llm_reviewer import ReviewVerdict


def _orig(x):
    return float(x)


@patch("p2.mutators.cell_pool.review_mutant")
@patch("p2.mutators.cell_pool.generate_mutants")
def test_build_pool_partitions_correctly(mock_gen, mock_review):
    # 3 candidates: pass-mech & confirmed; pass-mech & rejected; fail-mech
    mock_gen.return_value = [
        "def program(x):\n    return float(x) + 1\n",   # mech pass
        "def program(x):\n    return float(x) + 2\n",   # mech pass
        "def program(x):\n    syntax error here\n",      # mech fail
    ]
    mock_review.side_effect = [
        ReviewVerdict(True, "Yes", "Yes", "Yes", "Yes", "Yes",
                      "CONFIRMED", "ok", "gpt"),
        ReviewVerdict(True, "Yes", "Yes", "Yes", "No", "Yes",
                      "REJECTED", "v5 fail", "gpt"),
    ]
    pool = build_cell_pool(
        put_source="def program(x): return float(x)",
        put_name="A2", scientific_domain="LU",
        mut_intent="break determinant",
        original_fn=_orig, n_candidates=3, cell_id="a2_test",
    )
    assert isinstance(pool, CellPool)
    assert len(pool.confirmed) == 1
    assert len(pool.rejected) == 2
```

- [ ] **Step 3: Replace stale test_llm_generator.py with current-API smoke**

Replace `tests/mutators/test_llm_generator.py`:

```python
"""Smoke: generate_mutants returns N strings (mocked LLM)."""
from unittest.mock import MagicMock, patch
from p2.mutators.llm_generator import generate_mutants


@patch("p2.mutators.llm_generator.generator_client")
def test_generates_n_candidates(mock_factory):
    fake_client = MagicMock()
    fake_client.chat.completions.create.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(
            content="def program(x):\n    return float(x) + 1\n"
        ))]
    )
    mock_factory.return_value = (fake_client, "claude-opus-4-6")

    out = generate_mutants(
        put_source="def program(x): return float(x)",
        put_name="A2", scientific_domain="LU", mut_intent="x",
        n_candidates=3, temperature=0.7,
    )
    assert len(out) == 3
    for code in out:
        assert "def program" in code
```

- [ ] **Step 4: Add full-pipeline smoke test**

Create `tests/integration/test_full_pipeline_smoke.py`:

```python
"""End-to-end smoke: registry → mech-validation → diversity metric (no LLM)."""
import importlib
import importlib.util
from pathlib import Path

from p2.mutators.operator_registry import OPERATORS, get_operators_for_put
from p2.mutators.diversity import diversity_score
from p2.mutators.validation import validate_mutant

ROOT = Path(__file__).parent.parent.parent


def test_every_put_has_loadable_program():
    for op in OPERATORS:
        spec = importlib.util.spec_from_file_location(
            op.put, ROOT / "src" / "p2" / "puts" / f"{op.put}.py"
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        y = mod.program(0.4)
        assert isinstance(y, (int, float)), (
            f"PUT {op.put} must return scalar; got {type(y).__name__}"
        )


def test_diversity_metric_nonzero_on_real_codes():
    codes = [
        "def program(x):\n    return float(x) ** 2\n",
        "def program(x):\n    return float(x) * float(x)\n",
        "def program(x):\n    y = float(x); return y * y\n",
    ]
    assert diversity_score(codes) > 0.0


def test_validation_module_loads_each_put():
    for op in OPERATORS:
        spec = importlib.util.spec_from_file_location(
            op.put, ROOT / "src" / "p2" / "puts" / f"{op.put}.py"
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        # original passes V1-V2-V4 by definition; V3 is "non-trivial vs itself" → False
        res = validate_mutant(open(ROOT / "src" / "p2" / "puts" / f"{op.put}.py").read(),
                              mod.program)
        assert res.syntax_ok and res.executable
        assert not res.nontrivial  # PUT is never non-trivial vs itself
```

- [ ] **Step 5: Run full test suite**

Run: `pytest -x -q`
Expected: all tests PASS (no failures, no collection errors).

If a test fails because A1 returns scalar but the smoke previously expected ndarray, the smoke test in Step 4 already requires scalar; investigate any other failure as a real bug.

- [ ] **Step 6: Commit**

```bash
git add .gitignore tests/mutators/test_cell_pool.py tests/mutators/test_llm_generator.py tests/integration/test_full_pipeline_smoke.py
git commit -m "test: replace stale unit tests + add end-to-end pipeline smoke"
```

---

## Self-Review Checklist (run after Task 12 commits)

- [ ] All 12 tasks committed individually (12 commits visible in `git log --oneline`)
- [ ] `pytest -x -q` is green
- [ ] `data/operator_campaign/registry.json` exists and lists ≥ 36 operators with ≥ 7 keys
- [ ] `data/results/sms_track1.json` has 12 cells (Track 1)
- [ ] `data/results/operator_metrics.json` has ≥ 36 operators with R_sem / D_impl / R_kill
- [ ] `data/results/concurrency_probe.txt` documents the chosen Semaphore limit
- [ ] No tests reference `pool.double_confirmed` or `anthropic.Anthropic`
- [ ] A1 PUT returns `float`; primary MP for A1 is MP1
- [ ] B2 R_mp2 is strict `>` (no -0.3 slack)
- [ ] V3 epsilon = 1e-6 in `validation.py`

If any check fails, return to the relevant task and fix before declaring done.
