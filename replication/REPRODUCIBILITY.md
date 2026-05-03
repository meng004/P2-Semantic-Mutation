# Reproducibility Checklist — P2 SMS Audit Replication Package

This document complements the project-level `../REPRODUCIBILITY.md`
(paper §4.2.3) with a Zenodo-replicator-focused checklist. **All
paper headline numbers can be reproduced from the committed cache
without re-calling any LLM.** The 292 v4 mutants in
`data/mutants/*_pool_v4/` were generated at `temperature=0` and are
byte-stable; the statistical pipeline is deterministic under
`SEED=42`.

---

## 1. Environment

| Component | Tested | Minimum |
|---|---|---|
| OS | macOS 24.6 (Darwin, Apple Silicon), Ubuntu 22.04 (x86_64) | any POSIX with Python 3.11+ |
| Python | 3.12.x | 3.11.x |
| CPU | 4-core | 2-core |
| RAM | 16 GB | 4 GB |
| Disk | 1.5 GB free | 1 GB free |
| Network | none required for cache replay | only for re-running LLM campaigns |

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-frozen.txt
```

`requirements-frozen.txt` pins the following (see project root):
`anthropic==0.97.0`, `fastdtw==0.3.4`, `matplotlib==3.10.9`,
`numpy==2.4.4`, `openai==2.33.0`, `pandas==3.0.2`, `pytest==9.0.3`,
`python-dotenv==1.2.2`, `scikit-learn==1.8.0`, `scipy==1.17.1`,
`seaborn==0.13.2`, `statsmodels==0.14.4`.

---

## 2. Random seeds and determinism

| Source | Seed | File |
|---|---|---|
| Cliff's δ bootstrap (RQ2) | `SEED=42` | `scripts/compute_rq2.py` |
| Stipulated-power simulation (RQ2 §5.7.2) | `SEED=42` | `scripts/compute_rq2_power_stipulated.py` |
| Permutation test for c-class inflation | `SEED=42` | `scripts/permutation_c_class_inflation.py` |
| H5 sensitivity bootstrap | `SEED=42` | `scripts/h5_sensitivity.py` |
| LLM mutant generator | `temperature=0` | `scripts/cross_source_campaign.py` |

The committed `data/mutants/*_pool_v4/` directories are the
deterministic output of the `temperature=0` v4 cross-source campaign
and are sufficient to rebuild every paper number without re-calling
any LLM.

---

## 3. LLM API determinism (re-generation only — NOT required for replication)

If a replicator wishes to *regenerate* the v4 mutant pool from
scratch (rather than replay the cache), they will need:

- `ANTHROPIC_API_KEY` (Claude Opus 4.6 generator)
- `BLTCY_BASE_URL` + `BLTCY_API_KEY` (GPT-5.4 reviewer via bltcy.ai
  proxy)
- `DEEPSEEK_BASE_URL` + `DEEPSEEK_API_KEY` (DeepSeek V4 Pro
  arbitrator on UNCERTAIN reviews)

Even at `temperature=0`, LLM endpoints occasionally return
non-byte-identical responses. The committed `_pool_v4` snapshot is
the canonical version cited in the paper. The raw API trial logs
under `data/operator_campaign/raw/` (~430 KB, 470 trials × 6
reviewer labels) are **gitignored due to size constraints in the
Zenodo bundle**; they are available on request from the authors and
are not required for replication of any §5 / §6 number.

---

## 4. Compute resources

A 4-core laptop with 8 GB RAM is sufficient. Full pipeline (cache
replay only) finishes in ≤ 2 hours wallclock; the three-command
quickstart finishes in < 5 minutes.

| Stage | Wallclock (laptop) | What it does |
|---|---|---|
| `pytest -q` | ~30 s | 116/116 tests must pass |
| `build_paper_numbers.py` | ~10 s | rebuilds `paper_numbers_v4.json` |
| `p2_vs_syntactic_ast_diff_batch.py` | ~30 s | rebuilds 12-PUT AST diff |
| `compute_rq2.py` | ~5 s | Cliff's δ + bootstrap CI |
| `compute_rq2_power.py` | ~20 s | observed-effect power |
| `compute_rq2_power_stipulated.py` | ~30 s | stipulated-alternative power |
| `compute_rq3.py` + `compute_rq3_friedman.py` | ~10 s | mixed effects + Friedman |
| `compute_rq4.py` | ~5 s | Spearman / Kendall on PC vs SMS |
| `h5_sensitivity.py` | ~10 s | H5 threshold robustness |
| `permutation_c_class_inflation.py` | ~30 s | c-class permutation null |
| Cosmic-ray cache replay (`run_cosmic_ray_*.sh`) | ~90 min | only if regenerating from .toml configs |

---

## 5. Verification snippets — reproduce headline numbers in 5 commands

Each snippet below should print the cited number ± rounding.

### 5.1 Cliff's δ = 0.4392 (RQ2 H2, paper §5.7)

```bash
python -c "import json; d = json.load(open('data/results/paper_numbers_v4.json'))['rq2']; print(f\"Cliff's delta = {d['cliffs_delta']:.4f}, 95% CI = [{d['delta_ci_95_lo']:.4f}, {d['delta_ci_95_hi']:.4f}]\")"
# Expected: Cliff's delta = 0.4392, 95% CI = [0.1267, 0.7396]
```

### 5.2 Friedman χ² = 15.30, p = 0.0041 (RQ3 H4, paper §5.8)

```bash
python -c "import json; d = json.load(open('data/results/paper_numbers_v4.json'))['rq3']; print(f'Friedman chi^2 = {d[\"friedman_chi2\"]:.4f}, p = {d[\"friedman_p\"]:.4f}')"
# Expected: Friedman chi^2 = 15.3028, p = 0.0041
```

### 5.3 Mean SMS = 0.104, median = 0.000 (RQ1 H1, paper §5.6)

```bash
python -c "import json; d = json.load(open('data/results/paper_numbers_v4.json'))['rq1']; print(f'mean SMS = {d[\"mean_sms\"]:.3f}, median = {d[\"median_sms\"]:.3f}, n_zero = {d[\"n_zero_sms\"]}/60')"
# Expected: mean SMS = 0.104, median = 0.000, n_zero = 45/60
```

### 5.4 AST overlap with cosmic-ray = 5.14% (paper §3.2.6.3)

```bash
python -c "import json; d = json.load(open('data/results/cosmic_ray_12put_ast_diff.json')); rs = [v['overlap_ratio'] for v in d.values() if isinstance(v, dict) and 'overlap_ratio' in v]; print(f'mean AST overlap = {sum(rs)/len(rs)*100:.2f}% across {len(rs)} PUTs')"
# Expected: mean AST overlap ≈ 5.14% across 12 PUTs
```

### 5.5 Stipulated-alternative power = 49.1% at δ_truth = 0.474 (paper §5.7.2)

```bash
python -c "import json; d = json.load(open('data/results/rq2_power_stipulated_v4.json')); print(f'power at delta_truth=0.474 = {d.get(\"power_at_delta_0_474\", d.get(\"power\", \"see file\"))}')"
# Expected: power ≈ 0.491 (key may be 'power' depending on regeneration)
```

(If §5.5 prints "see file", open the JSON — the stipulated-power
metric is recorded under various keys across versions; the paper
cites 49.1%.)

---

## 6. Cross-version environment-variable contract

Two env vars together select the paper's analysis configuration:

```bash
export SMS_VERSION=v4         # selects v4 cross-source pool (PRIMARY)
export P2_PRIMARY_VERSION=v3b # selects v3b data-driven primary MP for c-class (§3.5.1)
```

These are read by `scripts/build_paper_numbers.py` and
`src/p2/stats/`. They MUST be set together; the paper's numbers are
specifically the `(v4, v3b)` pair.

---

## 7. Smoke test

Before any reproduction work:

```bash
PYTHONPATH=src pytest -q
# Expected: 116 passed in ~30s
```

If this fails, `requirements-frozen.txt` was not honoured (most
common cause: NumPy 2.x / SciPy ABI mismatch).

---

## 8. Pointers for deeper audit

- **Per-artifact provenance:** `../DATASET.md`
- **Stage 4.5 final integrity report:**
  `../docs/review_2026-05-02/stage_4_5_final_integrity_report.md` —
  this report cross-validates every paper number against the SSOT
  JSON files and is the definitive integrity audit.
- **Reviewer reports:** Round 1 in `../docs/review_2026-05-01/`,
  Round 2 in `../docs/review_2026-05-02/`.
- **Operator campaign log:**
  `../data/operator_campaign/v2_revised6.log` — per-trial timing /
  cost / model id.

---

## 9. Known limitations

- **PUT signature scope.** All 12 PUTs are `program(x: float) → float`
  (≤ 2 KB each). Broader transfer is reserved for the P3 / P5 papers
  (paper §3.1.1 and §6.4). This is a *scope* statement, not a
  reproducibility caveat.
- **Raw API logs not bundled.** `data/operator_campaign/raw/` (~430
  KB compressed, but with file-count overhead and per-trial JSON
  bloat) is excluded from the Zenodo zip to stay well under the soft
  limit. The committed v4 mutant pool itself is sufficient for full
  replication of every §5 / §6 number.
- **Cosmic-ray SQLite.** All 12 SQLite databases are < 2 MB each and
  bundled in full; no replication need is gated on regenerating
  them, but `run_cosmic_ray_put.sh` plus the bundled `.cr-*.toml`
  configs make regeneration straightforward (~90 min wallclock).
