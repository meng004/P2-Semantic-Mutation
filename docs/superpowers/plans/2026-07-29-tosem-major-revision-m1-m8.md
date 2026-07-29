# TOSEM Major Revision M1–M8 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Repair TOSEM review items M1–M8 from frozen campaign data, regenerate a coherent manuscript SSOT, strengthen H2 with PUT-level cluster resampling, and restructure the paper to the stable-acceptance form without new experiments.

**Architecture:** Put reusable recomputation logic in one importable statistics module, keep command-line scripts as deterministic JSON producers, and aggregate every manuscript headline into `paper_numbers_v4.json`. Revise `source/main.tex` and `source/supplementary.tex` only after the regenerated JSON values are fixed, then verify numerical traceability, theory alignment, float references, word count, tests, and LaTeX compilation.

**Tech Stack:** Python 3, NumPy, pytest, JSON, LaTeX/acmart, BibTeX, existing `p2.stats` utilities, frozen v3/v4 result records.

---

### Task 1: Add Tested Revision Statistics Primitives

**Files:**

- Create: `src/p2/stats/tosem_revision.py`
- Create: `tests/stats/test_tosem_revision.py`
- Modify: `src/p2/stats/__init__.py`

- [ ] **Step 1: Write failing tests for the frozen-primary split, NA aggregation, premise count, and cluster shape**

Create `tests/stats/test_tosem_revision.py` with focused synthetic fixtures:

```python
from p2.stats.tosem_revision import (
    gap_premise_support,
    put_cluster_bootstrap,
    split_aligned_cross,
    summarize_lrca,
)


PRIMARY = {"a1": 1, "b1": 2}


def _cell(sms, files):
    return {
        "sms": sms,
        "outcomes": [{"file": file, "label": "KILLED"} for file in files],
    }


def test_split_uses_explicit_frozen_primary():
    sms = {
        "A1_MP1": _cell(0.8, ["a1_CE1.py"]),
        "A1_MP2": _cell(0.1, ["a1_CE1.py"]),
        "B1_MP1": _cell(0.2, ["b1_OS1.py"]),
        "B1_MP2": _cell(0.7, ["b1_OS1.py"]),
    }
    aligned, cross = split_aligned_cross(sms, PRIMARY)
    assert aligned == [0.8, 0.7]
    assert cross == [0.1, 0.2]


def test_lrca_macro_excludes_zero_kill_cells():
    lrca = {
        "A1_MP1": {
            "n_killed": 2,
            "c1_share": 0.5,
            "suspect_share": 0.5,
            "labels": {"C1_legit_fault": 1},
        },
        "A1_MP2": {
            "n_killed": 0,
            "c1_share": 0.0,
            "suspect_share": 1.0,
            "labels": {"C1_legit_fault": 0},
        },
    }
    out = summarize_lrca(lrca)
    assert out["cells_evaluable"] == 1
    assert out["cells_zero_kill_NA"] == 1
    assert out["macro_mean_c1_share"] == 0.5
    assert out["macro_mean_suspect_share"] == 0.5


def test_gap_premise_support_counts_absent_positive_fiber():
    sms = {
        "A1_MP1": _cell(0.5, ["a1_CE1.py"]),
        "A1_MP2": _cell(0.0, ["a1_CE1.py"]),
        "B1_MP1": _cell(0.3, ["b1_HP1.py"]),
        "B1_MP2": _cell(0.0, ["b1_HP1.py"]),
    }
    out = gap_premise_support(sms, PRIMARY)
    assert out["antecedent_holds"] == 3
    assert out["antecedent_holds_zero_sms"] == 2
    assert out["antecedent_holds_nonzero_sms"] == 1
    assert out["antecedent_cells"] == ["A1_MP2", "B1_MP1", "B1_MP2"]


def test_put_cluster_bootstrap_preserves_one_to_one_cluster_draws():
    sms = {
        "A1_MP1": _cell(0.8, ["a1_CE1.py"]),
        "A1_MP2": _cell(0.1, ["a1_CE1.py"]),
        "B1_MP1": _cell(0.2, ["b1_OS1.py"]),
        "B1_MP2": _cell(0.7, ["b1_OS1.py"]),
    }
    out = put_cluster_bootstrap(sms, PRIMARY, n_boot=200, seed=7)
    assert out["n_put_clusters"] == 2
    assert out["n_aligned"] == 2
    assert out["n_cross"] == 2
    assert out["n_bootstrap"] == 200
    assert out["resampling_unit"] == "PUT"
    assert len(out["ci_95"]) == 2
```

- [ ] **Step 2: Run the focused tests and confirm the import fails**

Run:

```bash
rtk pytest tests/stats/test_tosem_revision.py -q
```

Expected: collection fails with `ModuleNotFoundError: No module named 'p2.stats.tosem_revision'`.

- [ ] **Step 3: Implement the minimal reusable statistics module**

Create `src/p2/stats/tosem_revision.py` with:

```python
from __future__ import annotations

import re
from collections.abc import Mapping

import numpy as np

from p2.stats.cliffs_delta import cliffs_delta

CAT2MP = {"CE": 1, "OS": 2, "HP": 3, "TF": 4, "SI": 5}
CAT_RE = re.compile(r"_(CE|OS|HP|TF|SI|CF)\d")


def cell_key(cell: str) -> tuple[str, int]:
    put, mp = cell.split("_MP")
    return put.lower(), int(mp)


def split_aligned_cross(
    sms: Mapping[str, Mapping[str, object]],
    primary: Mapping[str, int],
) -> tuple[list[float], list[float]]:
    aligned: list[float] = []
    cross: list[float] = []
    for cell in sorted(sms):
        put, mp = cell_key(cell)
        target = aligned if mp == primary[put] else cross
        target.append(float(sms[cell]["sms"]))
    return aligned, cross


def summarize_lrca(
    lrca: Mapping[str, Mapping[str, object]],
) -> dict[str, float | int]:
    evaluable = [row for row in lrca.values() if int(row["n_killed"]) > 0]
    total_kills = sum(int(row["n_killed"]) for row in evaluable)
    c1_kills = sum(int(row["labels"]["C1_legit_fault"]) for row in evaluable)
    return {
        "cells_total": len(lrca),
        "cells_evaluable": len(evaluable),
        "cells_zero_kill_NA": len(lrca) - len(evaluable),
        "macro_mean_c1_share": round(
            float(np.mean([float(row["c1_share"]) for row in evaluable])), 4
        ),
        "macro_mean_suspect_share": round(
            float(np.mean([float(row["suspect_share"]) for row in evaluable])), 4
        ),
        "pooled_c1_share": round(c1_kills / total_kills, 4),
        "pooled_suspect_share": round((total_kills - c1_kills) / total_kills, 4),
        "total_kills": total_kills,
        "c1_kills": c1_kills,
    }


def gap_premise_support(
    sms: Mapping[str, Mapping[str, object]],
    primary: Mapping[str, int],
) -> dict[str, object]:
    rows = []
    for cell in sorted(sms):
        put, mp = cell_key(cell)
        positive = set()
        for outcome in sms[cell]["outcomes"]:
            match = CAT_RE.search(str(outcome["file"]))
            if match and match.group(1) in CAT2MP:
                positive.add(CAT2MP[match.group(1)])
        holds = mp not in positive
        rows.append(
            {
                "cell": cell,
                "aligned": mp == primary[put],
                "sms": float(sms[cell]["sms"]),
                "positive_weight_strata": sorted(positive),
                "antecedent_holds": holds,
            }
        )
    subset = [row for row in rows if row["antecedent_holds"]]
    return {
        "definition": "observable antecedent Cov(R) intersect {j:w_j>0} is empty",
        "antecedent_holds": len(subset),
        "antecedent_fails": len(rows) - len(subset),
        "antecedent_holds_aligned": sum(row["aligned"] for row in subset),
        "antecedent_holds_cross": sum(not row["aligned"] for row in subset),
        "antecedent_holds_zero_sms": sum(row["sms"] == 0 for row in subset),
        "antecedent_holds_nonzero_sms": sum(row["sms"] > 0 for row in subset),
        "antecedent_cells": [row["cell"] for row in subset],
        "per_cell": rows,
    }


def put_cluster_bootstrap(
    sms: Mapping[str, Mapping[str, object]],
    primary: Mapping[str, int],
    *,
    n_boot: int,
    seed: int,
    excluded_cells: set[str] | None = None,
) -> dict[str, object]:
    excluded = excluded_cells or set()
    by_put: dict[str, list[tuple[int, float]]] = {}
    for cell in sorted(sms):
        if cell in excluded:
            continue
        put, mp = cell_key(cell)
        by_put.setdefault(put, []).append((mp, float(sms[cell]["sms"])))
    puts = sorted(by_put)

    def materialize(sampled_puts):
        aligned, cross = [], []
        for put in sampled_puts:
            for mp, value in by_put[put]:
                (aligned if mp == primary[put] else cross).append(value)
        return aligned, cross

    observed_aligned, observed_cross = materialize(puts)
    point = cliffs_delta(observed_aligned, observed_cross)
    rng = np.random.default_rng(seed)
    draws = np.empty(n_boot)
    for index in range(n_boot):
        sampled = rng.choice(puts, size=len(puts), replace=True)
        aligned, cross = materialize(sampled)
        draws[index] = cliffs_delta(aligned, cross)
    return {
        "resampling_unit": "PUT",
        "seed": seed,
        "n_bootstrap": n_boot,
        "n_put_clusters": len(puts),
        "n_aligned": len(observed_aligned),
        "n_cross": len(observed_cross),
        "point_estimate": point,
        "ci_95": [
            float(np.quantile(draws, 0.025)),
            float(np.quantile(draws, 0.975)),
        ],
        "bootstrap_fraction_delta_le_zero": float(np.mean(draws <= 0)),
        "bootstrap_median": float(np.median(draws)),
    }
```

Export the four public functions from `src/p2/stats/__init__.py`.

- [ ] **Step 4: Run focused tests and the existing statistics suite**

Run:

```bash
rtk pytest tests/stats/test_tosem_revision.py tests/stats -q
```

Expected: all statistics tests pass.

- [ ] **Step 5: Commit Task 1**

```bash
rtk git add src/p2/stats/tosem_revision.py src/p2/stats/__init__.py tests/stats/test_tosem_revision.py
rtk git commit -m "test: add TOSEM revision statistics primitives"
```

### Task 2: Lock M1 Power Inputs and Add M4 Cluster JSON

**Files:**

- Modify: `scripts/compute_rq2_power.py:28-126`
- Modify: `scripts/compute_rq2_power_stipulated.py:39-239`
- Create: `scripts/compute_rq2_cluster_bootstrap.py`
- Create: `tests/stats/test_tosem_scripts.py`
- Regenerate: `data/results/rq2_power_v4.json`
- Regenerate: `data/results/rq2_power_stipulated_v4.json`
- Create: `data/results/rq2_cluster_bootstrap_v4.json`

- [ ] **Step 1: Add a regression test that rejects environment-selected primary maps**

Create `tests/stats/test_tosem_scripts.py`:

```python
from pathlib import Path


def test_power_scripts_use_frozen_primary_symbol():
    root = Path(__file__).resolve().parents[2]
    for name in ("compute_rq2_power.py", "compute_rq2_power_stipulated.py"):
        text = (root / "scripts" / name).read_text()
        assert "PRIMARY_CELLS_V3 as PRIMARY" in text
        assert "PRIMARY_CELLS as PRIMARY" not in text


def test_cluster_script_declares_put_resampling():
    root = Path(__file__).resolve().parents[2]
    text = (root / "scripts/compute_rq2_cluster_bootstrap.py").read_text()
    assert "n_boot=100_000" in text
    assert '"PUT"' in text
```

- [ ] **Step 2: Run the script regression tests and confirm failure**

Run:

```bash
rtk pytest tests/stats/test_tosem_scripts.py -q
```

Expected: both tests fail because the power scripts use `PRIMARY_CELLS` and the cluster script does not exist.

- [ ] **Step 3: Lock the power scripts and record their provenance**

In both power scripts, replace:

```python
from p2.config.primary import PRIMARY_CELLS as PRIMARY
```

with:

```python
from p2.config.primary import PRIMARY_CELLS_V3 as PRIMARY
```

Add the following fields to each JSON report:

```python
"primary_map": PRIMARY,
"primary_map_source": "p2.config.primary.PRIMARY_CELLS_V3",
"input_sms": SMS_FILE,
```

Update stale comments and interpretation text so the observed point estimate is read from the MP5-primary slice and no sentence names `delta = 0.439` as the current observed effect.

- [ ] **Step 4: Implement the deterministic cluster-bootstrap producer**

Create `scripts/compute_rq2_cluster_bootstrap.py`:

```python
from __future__ import annotations

import json
from pathlib import Path

from p2.config.primary import PRIMARY_CELLS_V3
from p2.stats.tosem_revision import put_cluster_bootstrap

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "data/results"
VACANT = {
    "A1_MP5", "A2_MP2", "A3_MP5", "B1_MP3", "B1_MP4",
    "B3_MP2", "B3_MP5", "D2_MP4", "D3_MP4",
}


def main() -> None:
    sms = json.loads((RESULTS / "sms_track2_v4.json").read_text())
    report = {
        "method": "percentile PUT-cluster bootstrap of Cliff's delta",
        "input_sms": "sms_track2_v4.json",
        "primary_map": PRIMARY_CELLS_V3,
        "primary_map_source": "p2.config.primary.PRIMARY_CELLS_V3",
        "primary": put_cluster_bootstrap(
            sms, PRIMARY_CELLS_V3, n_boot=100_000, seed=42
        ),
        "vacant_cell_sensitivity": put_cluster_bootstrap(
            sms,
            PRIMARY_CELLS_V3,
            n_boot=100_000,
            seed=42,
            excluded_cells=VACANT,
        ),
        "vacant_cells_excluded": sorted(VACANT),
        "interpretation": (
            "PUT identifiers are sampled with replacement; each sampled "
            "cluster carries its aligned and cross cells together."
        ),
    }
    (RESULTS / "rq2_cluster_bootstrap_v4.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    )


if __name__ == "__main__":
    main()
```

Insert `ROOT / "src"` into `sys.path` before importing `p2` if the repository's direct-script invocation requires it.

- [ ] **Step 5: Run the script tests**

Run:

```bash
rtk pytest tests/stats/test_tosem_scripts.py tests/stats/test_tosem_revision.py -q
```

Expected: all focused tests pass.

- [ ] **Step 6: Regenerate the three M1/M4 JSON files**

Run:

```bash
rtk env SMS_VERSION=v4 RQ2_POWER_NSIM=5000 RQ2_POWER_SEED=42 python scripts/compute_rq2_power.py
rtk env SMS_VERSION=v4 RQ2_POWER_NSIM=5000 RQ2_POWER_SEED=42 python scripts/compute_rq2_power_stipulated.py
rtk python scripts/compute_rq2_cluster_bootstrap.py
```

Expected:

- `rq2_power_v4.json` records observed `delta` near `0.3142`;
- the observed exceedance entries are near `0.977/0.854/0.461/0.151`;
- `rq2_power_stipulated_v4.json` records the recalibrated mixture and no MP1 headline;
- the cluster JSON records point estimate near `0.3142` and a positive primary 95% interval near `[0.045, 0.594]`.

- [ ] **Step 7: Commit Task 2**

```bash
rtk git add scripts/compute_rq2_power.py scripts/compute_rq2_power_stipulated.py scripts/compute_rq2_cluster_bootstrap.py tests/stats/test_tosem_scripts.py data/results/rq2_power_v4.json data/results/rq2_power_stipulated_v4.json data/results/rq2_cluster_bootstrap_v4.json
rtk git commit -m "fix: recompute H2 power and PUT-cluster interval"
```

### Task 3: Regenerate M2/M3/M5 Manuscript SSOT

**Files:**

- Modify: `scripts/audit_fix_numbers.py:25-303`
- Modify: `scripts/build_paper_numbers.py:1-155`
- Modify: `scripts/h5_sensitivity.py:1-120`
- Modify: `scripts/compute_rq3_friedman.py:1-110`
- Modify: `tests/stats/test_tosem_revision.py`
- Regenerate: `data/results/audit_fix_numbers.json`
- Regenerate: `data/results/xi_exactness_defect_v4.json`
- Regenerate: `data/results/h5_sensitivity_v4.json`
- Regenerate: `data/results/rq3_friedman_v4.json`
- Regenerate: `data/results/paper_numbers_v4.json`

- [ ] **Step 1: Add frozen-output assertions**

Append to `tests/stats/test_tosem_revision.py`:

```python
import json
from pathlib import Path


def test_committed_v4_ssot_uses_mp5_and_na_convention():
    root = Path(__file__).resolve().parents[2]
    paper = json.loads((root / "data/results/paper_numbers_v4.json").read_text())
    assert paper["rq2"]["cliffs_delta"] == 0.3142
    assert paper["rq2"]["mean_aligned"] == 0.2133
    assert paper["lrca"]["v4"]["cells_evaluable"] == 15
    assert paper["lrca"]["v4"]["macro_mean_c1_share"] == 0.8367
    assert paper["lrca"]["v3"]["cells_evaluable"] == 12
    assert paper["lrca"]["v3"]["macro_mean_c1_share"] == 0.8214
    assert paper["rq3"]["friedman_chi2"] == 16.76


def test_committed_gap_antecedent_count_is_auditable():
    root = Path(__file__).resolve().parents[2]
    paper = json.loads((root / "data/results/paper_numbers_v4.json").read_text())
    gap = paper["gap_premise_support"]
    assert gap["antecedent_holds"] == len(gap["antecedent_cells"])
    assert (
        gap["antecedent_holds_zero_sms"]
        + gap["antecedent_holds_nonzero_sms"]
        == gap["antecedent_holds"]
    )
```

- [ ] **Step 2: Run the assertions and confirm the old SSOT fails**

Run:

```bash
rtk pytest tests/stats/test_tosem_revision.py::test_committed_v4_ssot_uses_mp5_and_na_convention tests/stats/test_tosem_revision.py::test_committed_gap_antecedent_count_is_auditable -q
```

Expected: failure because the old `paper_numbers_v4.json` contains `delta = 0.4392`, all-60 LRCA fields, and no gap-premise block.

- [ ] **Step 3: Make the audit script call the tested helpers**

Import:

```python
from p2.config.primary import PRIMARY_CELLS_V3 as PRIMARY
from p2.stats.tosem_revision import gap_premise_support, summarize_lrca
```

Replace the local primary-map duplicate with the imported frozen map. Add:

```python
"lrca_na_summary": {
    "v3": summarize_lrca(lrca3),
    "v4": summarize_lrca(lrca4),
},
"gap_premise_support": gap_premise_support(sms4, PRIMARY),
```

Load `lrca_60cell_v3.json` as `lrca3`. Keep `xi_audit` as the detailed per-kill diagnostic.

- [ ] **Step 4: Rebuild `paper_numbers_v4.json` from corrected authorities**

For `VERSION == "v4"`, `scripts/build_paper_numbers.py` must:

```python
primary = PRIMARY_CELLS_V3
rq2 = _load("rq2_cliffs_delta_v4_mp5.json")
friedman = _load("rq3_friedman_v4.json")
power = _load("rq2_power_v4.json")
stipulated = _load("rq2_power_stipulated_v4.json")
cluster = _load("rq2_cluster_bootstrap_v4.json")
audit = _load("audit_fix_numbers.json")
```

Construct these top-level blocks:

```python
"provenance": {
    "primary_map": primary,
    "primary_map_source": "p2.config.primary.PRIMARY_CELLS_V3",
    "frozen_inputs": [...],
},
"rq1": {...},
"rq2": {
    ...,
    "cliffs_delta": round(rq2["cliffs_delta"], 4),
    "cluster_bootstrap": cluster["primary"],
    "vacant_cell_sensitivity": cluster["vacant_cell_sensitivity"],
    "observed_exceedance": power["achieved_power_at_observed_n"],
    "stipulated_alternative": stipulated["stipulated_alternative_power"],
},
"lrca": audit["lrca_na_summary"],
"gap_premise_support": audit["gap_premise_support"],
"rq3": {...},
"rq4": {...},
```

Do not emit `mean_c1_share`, `mean_suspect_share`, `h5_cells_pass`, or `h5_pass_ratio` under `rq1`, because those all-60 fields encode the invalid zero-kill convention.

- [ ] **Step 5: Correct coupled H4 and Friedman interpretation outputs**

Update `scripts/h5_sensitivity.py` so its JSON names the hypothesis `H4`, treats zero-kill cells as NA, and labels all cutoff readings post-hoc sensitivity rather than a verdict.

Update `scripts/compute_rq3_friedman.py` so the v4 interpretation states that the MP effect is exploratory, the class-level sign criterion is 3/4, and no operator-level causal effect is identified by the mixed pools.

- [ ] **Step 6: Regenerate the audit, sensitivity, Friedman, and paper SSOT**

Run:

```bash
rtk python scripts/audit_fix_numbers.py
rtk env SMS_VERSION=v4 python scripts/h5_sensitivity.py
rtk env SMS_VERSION=v4 python scripts/compute_rq3_friedman.py
rtk env SMS_VERSION=v4 python scripts/build_paper_numbers.py
```

Expected: all five JSON outputs are rewritten from frozen inputs and `paper_numbers_v4.json` carries the MP5/NA/cluster/gap corrections.

- [ ] **Step 7: Run focused and full statistics tests**

Run:

```bash
rtk pytest tests/stats/test_tosem_revision.py tests/stats -q
```

Expected: all statistics tests pass.

- [ ] **Step 8: Commit Task 3**

```bash
rtk git add scripts/audit_fix_numbers.py scripts/build_paper_numbers.py scripts/h5_sensitivity.py scripts/compute_rq3_friedman.py tests/stats/test_tosem_revision.py data/results/audit_fix_numbers.json data/results/xi_exactness_defect_v4.json data/results/h5_sensitivity_v4.json data/results/rq3_friedman_v4.json data/results/paper_numbers_v4.json
rtk git commit -m "fix: regenerate NA-consistent manuscript SSOT"
```

### Task 4: Revise M1–M5 and M7 Quantitative Narrative

**Files:**

- Modify: `source/main.tex:132-305, 585-638, 2145-2175, 2200-2660, 3180-3280, 3440-3630`
- Modify: `source/supplementary.tex:800-1030, 1160-1260`

- [ ] **Step 1: Update the abstract, RQ4/H2 framing, and inference-permissions table**

Use “aligned-versus-cross direction” rather than “operator-MP alignment effect.” State the dependence-aware result in this form, with exact values read from the regenerated JSON:

```latex
Under the frozen primary convention, aligned cells exceed cross cells
directionally ($\delta=0.314$). A PUT-level cluster bootstrap, which
resamples each PUT with all five cells intact, gives a 95\% interval of
[JSON lower, JSON upper]. H2's pre-registered large-effect threshold
remains unmet; the result supports a positive within-design direction,
not an operator-level causal effect.
```

Change the inference-permissions row from cell-level bootstrap to PUT-cluster bootstrap with sampling unit `PUT (n=12 clusters)`.

- [ ] **Step 2: Replace the M1 power tables and explanation**

Populate the observed exceedance table directly from `rq2_power_v4.json`. Populate the stipulated table from `rq2_power_stipulated_v4.json`. Replace the old mixture weight, realised delta, power, and all four old exceedance probabilities.

The interpretation must explicitly separate:

```latex
The plug-in table is a resampling exceedance calculation under the
observed MP5-primary empirical distribution. The stipulated simulation
instead calibrates a distribution whose expected delta lies at the H2
boundary. Neither quantity is a confidence interval; dependence-aware
interval evidence comes from the PUT-cluster bootstrap above.
```

- [ ] **Step 3: Replace the M2 LRCA table and cross-source narrative**

Table `tab:p2-13` must report:

```latex
v3 evaluable cells & 12 / 60 \\
v4 evaluable cells & 15 / 60 \\
Macro-mean C1_share, v3 evaluable cells & 0.821 \\
Macro-mean C1_share, v4 evaluable cells & 0.837 \\
Macro-mean suspect_share, v4 evaluable cells & 0.163 \\
```

Replace every “0.164 to 0.209” and “27%” narrative with:

```latex
Cross-source pooling increases the number of cells with an observed
kill from 12 to 15 and raises the evaluable-cell macro-mean C1 share
from 0.821 to 0.837 (about 1.9% relative). Its clearest contribution is
therefore broader evaluability with a modest increase in diagnostic
purity, while the aligned-versus-cross delta remains nearly unchanged.
```

- [ ] **Step 4: Add the M5 premise-support count and dual mechanism**

Read exact counts from `paper_numbers_v4.json` and insert:

```latex
The observable antecedent
$\mathrm{Cov}(R)\cap\{j:w_j>0\}=\varnothing$ holds in X of 60 cells
(A aligned and C cross). Y of those X cells have SMS zero; the remaining
Z nonzero cells show that the wider S5-purity/exact-checker premises do
not hold at the provenance-label level. Accordingly,
Corollary~\ref{cor:zero} is read only on the fully
premise-conforming subset, not as an explanation of all 45 zero cells.
```

In the decoupling subsection, use:

```latex
Two mechanisms are observationally compatible with the mixed-pool
contrast: the MR families may expose different effect fibers, and they
may differ in strength or tolerance margin. The present $(i,k)$ design
does not identify their relative contributions because $j$ is a
per-mutant label rather than a stratified evaluation axis.
```

- [ ] **Step 5: Neutralise M7 and commit the next H4 estimand**

Replace the Study Design result leak with:

```latex
The 9-grid calibration selects diagnostic thresholds for the LRCA
decision tree; it does not evaluate H4. The grid and default control are
reported in Appendix A.2 and C.3.
```

In the H4 results subsection, add:

```latex
The next campaign will pre-register pooled suspect kills divided by all
LRCA-evaluated kills as the primary estimand, the evaluable-cell
macro-mean as secondary, and zero-kill cells as NA. The aggregation and
decision rule will be frozen before inspecting that campaign's H4
outcomes.
```

- [ ] **Step 6: Update supplementary power, LRCA, and threat text**

Make Appendix D reproduce the MP5-primary power and cluster method. Replace the old Appendix F protocol-asymmetry row with the 12-to-15 evaluability and 0.821-to-0.837 C1 reading.

- [ ] **Step 7: Run literal residue checks**

Run:

```bash
rtk rg -n '0\\.997|0\\.966|0\\.759|0\\.423|0\\.491|0\\.164|0\\.209|27\\\\%|80\\\\%|H4 is unattainable|operator-MP alignment produces' source/main.tex source/supplementary.tex
```

Expected: no obsolete primary claim remains; any historical value that remains is explicitly labelled withdrawn and does not feed a conclusion.

- [ ] **Step 8: Commit Task 4**

```bash
rtk git add source/main.tex source/supplementary.tex
rtk git commit -m "docs: repair TOSEM quantitative claims M1-M5 M7"
```

### Task 5: Repair M6 Theory and Perform M8 Structural Surgery

**Files:**

- Modify: `source/main.tex:503-1488, 3440-3830`
- Modify: `source/supplementary.tex:1277-1510`

- [ ] **Step 1: Promote the theory to an independent section**

Close `Problem Formulation and Semantic Mutation Model` after the hypotheses. Replace the nested theory heading with:

```latex
\section{Formal Measurement Scaffolding and Guarantees}
\label{formal-measurement-scaffolding}
```

Promote its former `\subsubsection` headings to `\subsection`. Keep the compact vocabulary, SMS definition, effect map, and theorem statements; move detailed proof paragraphs and lemma-level derivations to Appendix G.

- [ ] **Step 2: Reposition RQ1 and the contribution language**

Use this positioning consistently in the RQ, introduction, and conclusion:

```latex
\textbf{RQ1 (Formal measurement scaffolding and guarantees).}
Can SMS be defined over declared semantic-effect fibers with auditable
conditions for backward compatibility, strong-MR detection,
tolerance-bounded detection, unresolved-equivalence intervals, and
gap attribution?
```

Describe the theorem suite as formal guarantees that delimit the metric's interpretation. Explicitly state that the undecidability result is routine and the algebraic results are valuable for auditability rather than proof-technique novelty.

- [ ] **Step 3: Split the kill-witness statement**

Replace the current single lemma in the main text with:

```latex
\begin{lemma}[kill classification and conditional quantitative witness]
\label{lem:witness}
(i) Under the declared three-state protocol,
$\mathrm{killed}(s',\mathrm{MR}_{i,k})$ implies an E1 verdict
difference and therefore routes $s'$ to
\texttt{CONFIRMED\_NON\_EQUIVALENT}; hence no killed mutant remains
unresolved.
(ii) If the AVP verdict is stable under pointwise observed-output
perturbations of magnitude at most $\varepsilon_{\mathrm{eq}}$ (R2),
then a kill additionally implies an executed input whose observed
outputs differ by more than $\varepsilon_{\mathrm{eq}}$.
\end{lemma}
```

Move the proof to Appendix G and distinguish the definitional routing argument from the R2 quantitative upgrade.

- [ ] **Step 4: Repair Lemma G.1 without importing L3**

Replace the E1 paragraph of the Lemma G.1 proof with:

```latex
Under the fixed reference-anchored identity switch, exact same-input
agreement implies E1 coherence for any non-negative AVP tolerance.
Conversely, the limiting E2 arm already rejects every mutant that
differs from the reference on the covered domain outside
$\mathcal{N}_{\mathrm{exc}}$. Thus the conjunction E1$\wedge$E2 has
the same limiting classification as E2; no
$\varepsilon_{\mathrm{AVP}}\to0$ step is used here. That limit remains
the separate L3 premise of Lemma G.2 for degeneration of the killed
predicate.
```

- [ ] **Step 5: Move proof detail and remove repeated method prose**

Relocate to Appendix G:

- endpoint-by-endpoint interval monotonicity proof;
- gap-decomposition proof and signature-identifiability justification;
- exception-set counterexample detail;
- conditional witness proof;
- window proof assumptions and boundary-attaining necessity detail.

In the main text, retain one paragraph per guarantee explaining its operational consequence and Appendix G pointer.

Delete the repeated E1/E2 conservatism paragraph and killed formula from Study Design, replacing them with references to the formal section and an implementation-order summary.

- [ ] **Step 6: Apply coupled theoretical minor corrections**

Add:

```latex
The Rice reduction continues to hold on a restricted finite-edit
template family by padding the template with a semantics-preserving
wrapper that embeds the non-trivial program property.
```

Change the stochastic remark to:

```latex
Strict inequality is sufficient in general; necessity holds under the
boundary-attaining noise model specified in Appendix G.8.
```

Add forward pointers before first use of `\mathcal{D}_P`, `\mathcal{X}_{\mathrm{adm}}`, and the exact-checker definition.

- [ ] **Step 7: Commit Task 5**

```bash
rtk git add source/main.tex source/supplementary.tex
rtk git commit -m "docs: reposition and align formal measurement guarantees"
```

### Task 6: Complete M8 Float Hygiene, Length Reduction, and Coupled Minor Wording

**Files:**

- Modify: `source/main.tex`
- Modify: `source/supplementary.tex`
- Create: `scripts/count_main_prose.py`
- Create: `tests/test_count_main_prose.py`

- [ ] **Step 1: Add a deterministic main-prose counter test**

Create `tests/test_count_main_prose.py`:

```python
from scripts.count_main_prose import count_words


def test_count_words_ignores_commands_comments_and_math():
    text = r"""
    % ignored comment
    \section{Visible Heading}
    Visible prose has four words.
    \[
      x = y + z
    \]
    \caption{Visible caption words}
    """
    assert count_words(text) == 10
```

- [ ] **Step 2: Run the counter test and confirm failure**

Run:

```bash
rtk pytest tests/test_count_main_prose.py -q
```

Expected: import fails because `scripts/count_main_prose.py` does not exist.

- [ ] **Step 3: Implement the documented prose counter**

Create `scripts/count_main_prose.py`:

```python
from __future__ import annotations

import re
import sys
from pathlib import Path

COMMENT = re.compile(r"(?<!\\)%.*$")
DISPLAY_MATH = re.compile(r"\\\[.*?\\\]|\\begin\{(?:equation|align\*?)\}.*?\\end\{(?:equation|align\*?)\}", re.S)
INLINE_MATH = re.compile(r"\$.*?\$")
COMMAND = re.compile(r"\\[A-Za-z@]+\*?(?:\[[^\]]*\])?")
BRACES = re.compile(r"[{}]")
WORD = re.compile(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)*")


def count_words(text: str) -> int:
    text = "\n".join(COMMENT.sub("", line) for line in text.splitlines())
    text = DISPLAY_MATH.sub(" ", text)
    text = INLINE_MATH.sub(" ", text)
    text = COMMAND.sub(" ", text)
    text = BRACES.sub(" ", text)
    return len(WORD.findall(text))


if __name__ == "__main__":
    path = Path(sys.argv[1] if len(sys.argv) > 1 else "source/main.tex")
    print(count_words(path.read_text()))
```

- [ ] **Step 4: Run the counter test**

Run:

```bash
rtk pytest tests/test_count_main_prose.py -q
```

Expected: the counter test passes.

- [ ] **Step 5: Add missing labels, explicit float callouts, and figure descriptions**

Enumerate main-text floats and ensure every one has a label. For each label, add at least one preceding or following explicit callout:

```latex
Table~\ref{tab:...} ...
Figure~\ref{fig:...} ...
```

Add ACM descriptions for Figures 1 and 3:

```latex
\Description{Workflow diagram showing the three-layer semantic-mutation
method from formal conditions through certificate evaluation to the
60-cell empirical audit.}
```

```latex
\Description{Per-operator-class bar comparison of AST-normalised overlap
between semantic mutants and default first-order syntactic mutants,
with zero overlap for HP, SI, and TF.}
```

- [ ] **Step 6: Remove repeated prose until the documented count is 16,000–18,000**

Run:

```bash
rtk python scripts/count_main_prose.py source/main.tex
```

Delete only duplicated proof detail, protocol repetition, repeated caveats, and deployment prose already carried by the supplement. Preserve the RQs, negative hypothesis verdicts, cluster result, industrial arm, SSOT declaration, and limitations required to interpret the evidence.

Expected: final count is between 16,000 and 18,000.

- [ ] **Step 7: Apply coupled conclusion and deployment wording**

Replace:

```latex
Pattern-derived relations detect all 34 tabled real defects
```

with:

```latex
Within the selection-conditioned 34-case face, every tabled defect is
detected by at least one pattern-derived relation; this is not a
corpus-level detection rate.
```

Describe `0.213` as the observed aligned mean in this 12-PUT sample, not a deployment threshold. Reduce highlights to five items if the highlight list remains in the submission source.

- [ ] **Step 8: Commit Task 6**

```bash
rtk git add source/main.tex source/supplementary.tex scripts/count_main_prose.py tests/test_count_main_prose.py
rtk git commit -m "docs: complete TOSEM structure and float hygiene"
```

### Task 7: Full Regeneration and Verification

**Files:**

- Verify all files modified in Tasks 1–6
- Update: `docs/review_20260729/tosem_m1_m8_fix_verification.md`

- [ ] **Step 1: Re-run every deterministic generator**

Run:

```bash
rtk env SMS_VERSION=v4 RQ2_POWER_NSIM=5000 RQ2_POWER_SEED=42 python scripts/compute_rq2_power.py
rtk env SMS_VERSION=v4 RQ2_POWER_NSIM=5000 RQ2_POWER_SEED=42 python scripts/compute_rq2_power_stipulated.py
rtk python scripts/compute_rq2_cluster_bootstrap.py
rtk python scripts/audit_fix_numbers.py
rtk env SMS_VERSION=v4 python scripts/h5_sensitivity.py
rtk env SMS_VERSION=v4 python scripts/compute_rq3_friedman.py
rtk env SMS_VERSION=v4 python scripts/build_paper_numbers.py
```

Expected: running the commands a second time produces no JSON diff.

- [ ] **Step 2: Run the full automated test suite**

Run:

```bash
rtk pytest -q
```

Expected: all tests pass.

- [ ] **Step 3: Verify JSON and manuscript invariants**

Run:

```bash
rtk jq '{rq2,lrca,gap_premise_support,rq3}' data/results/paper_numbers_v4.json
rtk rg -n '0\\.4392|mean_c1_share.*0\\.209|mean_suspect_share.*0\\.7908|h5_cells_pass|15\\.30|27\\\\%|80\\\\%|H4 is unattainable' source/main.tex source/supplementary.tex data/results/paper_numbers_v4.json
rtk rg -n '\\\\begin\\{figure|\\\\Description|\\\\label\\{fig:|\\\\ref\\{fig:' source/main.tex
rtk rg -n '\\\\begin\\{table|\\\\begin\\{longtable|\\\\label\\{tab:|\\\\ref\\{tab:' source/main.tex
rtk python scripts/count_main_prose.py source/main.tex
```

Expected:

- no obsolete primary number appears as a current claim;
- every figure has a description and reference;
- every table has a label and reference;
- prose count is 16,000–18,000.

- [ ] **Step 4: Compile the manuscript**

From `source/`, run:

```bash
rtk latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```

If the repository's build requires the venue wrapper instead, run:

```bash
rtk python ../venues/tosem/build.py
```

Expected: build exits 0 with no undefined references or fatal LaTeX errors.

- [ ] **Step 5: Write the verification record**

Create `docs/review_20260729/tosem_m1_m8_fix_verification.md` containing:

- M1–M8 checklist with exact file/JSON evidence;
- final numerical values;
- test command and pass count;
- LaTeX build command and result;
- word-count method and count;
- any residual non-blocking bibliography metadata issue;
- explicit statement that no new experiment was run.

- [ ] **Step 6: Commit the verification record and any deterministic regeneration**

```bash
rtk git add docs/review_20260729/tosem_m1_m8_fix_verification.md data/results source scripts src tests
rtk git commit -m "docs: verify TOSEM M1-M8 revision"
```

- [ ] **Step 7: Inspect the final branch state**

Run:

```bash
rtk git status --short --branch
rtk git log --oneline --decorate -8
```

Expected: only the pre-existing untracked `artifacts/` directory remains, and the branch contains the design, implementation, and verification commits.
