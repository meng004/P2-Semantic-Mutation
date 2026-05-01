# Reproducibility Guide for P2 Empirical Audit

**Paper:** When LLM Source Diversity Doesn't Help: A Semantic Mutation Score Audit (论文初稿P2.md)
**Primary data version:** v4 cross-source（Claude Opus 4.6 + GPT-5.4 + DeepSeek V4 Pro）
**SSOT for paper numbers:** `data/results/paper_numbers_v4.json`

---

## 1. System requirements

| Component | Tested | Minimum |
|---|---|---|
| OS | macOS 24.6.0 (Darwin), Ubuntu 22.04 | any POSIX with Python 3.12 |
| CPU | Apple M-series, x86_64 | 8 cores recommended |
| RAM | 16 GB | 8 GB |
| Disk | 4 GB free | 2 GB free |
| Python | 3.12.x | 3.11+ |
| Network | required for LLM API calls (steps 3–4 only) | optional if using cached `data/operator_campaign/raw/` |

## 2. Environment setup

```bash
# Clone repo and create venv
git clone <repo-url> mt-completeness && cd mt-completeness
python3.12 -m venv .venv
.venv/bin/pip install -r requirements-frozen.txt

# Configure LLM credentials (steps 3-4 only; skip if using committed cache)
cp .env.example .env   # then edit .env to set:
#   ANTHROPIC_API_KEY        (Claude Opus generator)
#   BLTCY_BASE_URL + BLTCY_API_KEY    (GPT-5.4 reviewer via bltcy.ai proxy)
#   DEEPSEEK_BASE_URL + DEEPSEEK_API_KEY  (DeepSeek V4 Pro arbitrator)
```

## 3. Smoke test

```bash
PYTHONPATH=src .venv/bin/pytest -q
# Expected: 116 passed, 0 failed, ~30s wallclock
```

## 4. End-to-end reproduction

Two paths depending on whether you want to re-call LLMs.

### Path A — Use committed cache (deterministic, ~20 min)

Cache contains **470 LLM trials with raw responses + V1-V6 reviewer labels**, sufficient to reproduce all paper numbers without any LLM API calls.

**Two environment variables together select the paper's analysis configuration:**
- `SMS_VERSION=v4` — picks the v4 cross-source data files (sms_track2_v4.json, lrca_60cell_v4.json, rq{2,3,4}_*_v4.json).
- `P2_PRIMARY_VERSION=v3b` — picks the data-driven c-class primary MP assignment (c1/c2/c3 → MP1, from `data/results/c_class_mp_ranking.json`); this is what §3.5.1 of the paper documents and what the `aligned` / `cross` grouping in §5.7 depends on.

**Both are required.** Setting only `SMS_VERSION=v4` without `P2_PRIMARY_VERSION=v3b` will recompute aligned/cross with the v3 default primary (c-class → MP5) and produce numbers that do **not** match the paper.

```bash
export SMS_VERSION=v4
export P2_PRIMARY_VERSION=v3b   # REQUIRED — matches §3.5.1 c-class data-driven primary MP

# 4A.1  Build per-PUT cross-source v4 pools (≤ 1 min)
PYTHONPATH=src .venv/bin/python scripts/build_pools.py

# 4A.2  SMS campaign Track-2 v4 (~10-15 min, 60 cells × 12 mutants × N=20 repeats)
PYTHONPATH=src .venv/bin/python scripts/sms_campaign.py --track 2 \
    --workers 6 --repeats 20 \
    2>&1 | tee data/results/sms_track2_v4_console.log

# 4A.3  LRCA labeling (~5 min, 60 cells × ~12 mutants/cell)
PYTHONPATH=src .venv/bin/python scripts/run_lrca.py

# 4A.4  RQ statistics
PYTHONPATH=src .venv/bin/python scripts/compute_rq2.py
PYTHONPATH=src .venv/bin/python scripts/compute_rq2_logit.py
PYTHONPATH=src .venv/bin/python scripts/compute_rq3.py
PYTHONPATH=src .venv/bin/python scripts/compute_rq3_friedman.py
PYTHONPATH=src .venv/bin/python scripts/compute_rq4.py

# 4A.5  Aggregate paper numbers SSOT
PYTHONPATH=src .venv/bin/python scripts/build_paper_numbers.py

# 4A.6  Render figures
PYTHONPATH=src .venv/bin/python scripts/render_figures.py
```

**Note:** All `compute_rq*.py` scripts and `build_paper_numbers.py` import `PRIMARY_CELLS` at module load, so the env vars **must** be exported before invoking each script. If you forget `P2_PRIMARY_VERSION=v3b`, `mean_aligned` will be ~0.213 instead of the paper's 0.275 (Cliff's δ and Friedman χ² stay the same; only aligned/cross grouping changes).

### Path B — Re-call LLMs from scratch (non-deterministic, ~3-4 h, USD ~$80)

Adds steps before 4A:

```bash
# 4B.0  Cross-source mutant generation
PYTHONPATH=src .venv/bin/python scripts/cross_source_campaign.py --workers 4
# Then continue from 4A.1
```

## 5. Expected outputs

After Path A or B, you should see:

| File | Size | Verification |
|---|---|---|
| `data/results/paper_numbers_v4.json` | ~1.5 KB | matches values in §6 below |
| `data/results/sms_track2_v4.json` | ~50 KB | 60 SMS records |
| `data/results/lrca_60cell_v4.json` | ~187 KB | 60 cells × 5 LRCA buckets |
| `data/results/rq2_cliffs_delta_v4.json` | ~0.5 KB | δ ≈ 0.439 |
| `data/results/rq3_friedman_v4.json` | ~0.5 KB | χ² ≈ 15.30 |
| `figures/fig1_60cell_heatmap.pdf` | ~18 KB | visual identical to figures/v2/ |
| `figures/fig{2..5}.pdf` | 13–16 KB each | — |

## 6. Expected paper numbers (sanity check)

After `build_paper_numbers.py --version v4`, `data/results/paper_numbers_v4.json` MUST report:

```json
{
  "rq1": {"n_cells": 60, "mean_sms": 0.104, "n_zero_sms": 45, "h5_pass_ratio": 0.20},
  "rq2": {"cliffs_delta": 0.439, "h2_delta_pass": false, "h2_threshold_delta": 0.474},
  "rq3": {"friedman_chi2": 15.30, "friedman_p": 0.0041, "primary_converged": false},
  "rq4": {"spearman_rho": 0.163, "spearman_p": 0.613}
}
```

Tolerance: stochastic PUTs (b2 MCMC, b3 MC, c-class GPR, d1 MLP) introduce ~0.05 SMS noise across reproductions; aggregated δ / χ² should match within ±0.005.

## 7. Reproducibility boundaries

- **LLM nondeterminism:** Claude Opus subscription API exposes no seed. Cross-source pool generation (Path B step 4B.0) will produce different mutants on each run. **Use Path A (cached) for paper-grade reproduction.**
- **Stochastic PUTs:** N=20 repeats reduces but does not eliminate sampling noise; per-cell SMS may differ ±0.05 between Path A reruns due to numpy RNG state.
- **LRCA threshold sensitivity:** OOD threshold = 0.05, tolerance multiplier = 10×, N=20 majority. Changes alter `c1_share` distribution but not SMS itself. See §4.6.4 for the 9-grid calibration sweep.
- **Equivalence detector ε:** unified ε = 1e-6 (PUT-side and AVP-side); see §4.4 for rationale.

## 8. Per-artifact provenance

See `DATASET.md` (data/code lineage) and `docs/STATE.md` (current paper-stage status).

## 9. Reporting issues

If reproduction yields out-of-tolerance numbers, please open an issue with:
- Full `pytest -q` output
- `python --version` + `pip freeze`
- Diff of `paper_numbers_v4.json` vs §6 above
- The exact command sequence used
