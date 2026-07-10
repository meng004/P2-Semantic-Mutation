# Reproducibility Guide for the SMS Four-Study Audit

**Paper:** A Semantic Mutation Metric for Metamorphic-Relation Adequacy for
Scientific-Computing Kernels (TOSEM regular research paper; source in
`source/main.tex` + `source/supplementary.tex`, package built by
`venues/tosem/build.py`)
**Studies covered:** Study 1 (12-PUT audit, v4 cross-source), Study 2
(28-PUT confirmatory, v5), Study 3 (graded attribution, v6), Study 4
(cross-vendor / graded / cross-language closure, v7 + C port)
**Master seed for Studies 2-4 statistics:** 20260708

---

## 1. System requirements

| Component | Tested | Minimum |
|---|---|---|
| OS | macOS 24.6.0 (Darwin), Ubuntu 22.04 | any POSIX with Python 3.12 |
| CPU | Apple M-series, x86_64 | 8 cores recommended |
| RAM | 16 GB | 8 GB |
| Disk | 4 GB free | 2 GB free |
| Python | 3.12.x | 3.11+ |
| C toolchain (Study 4 H-LANG only) | gcc/clang, C99 | any C99 compiler |
| Network | required only for tier-3 LLM regeneration | not needed for tiers 1-2 |

## 2. Environment setup

```bash
git clone <repo-url> && cd <repo>
python3.12 -m venv .venv
.venv/bin/pip install -r requirements-frozen.txt

# LLM credentials are needed ONLY for tier 3 (full re-generation)
cp .env.example .env   # fill in vendor keys; see comments in the file
```

## 3. Tier 1 — Smoke test (no API key, ~1 min)

```bash
PYTHONPATH=src .venv/bin/pytest tests/ -q
# Expected: 549 passed, ~30s wallclock
```

## 4. Tier 2 — Cached / SSOT replay (no API key, ~30 min)

All confirmatory pools and review labels are committed and frozen; every
paper number re-derives deterministically from them.

### 4.1 Study 1 (v4 cross-source, 12 PUTs)

Both environment variables are required for the paper's configuration:

```bash
export SMS_VERSION=v4
export P2_PRIMARY_VERSION=v3b   # c-class data-driven primary MP (paper section 3.5.1)

PYTHONPATH=src .venv/bin/python scripts/build_pools.py
PYTHONPATH=src .venv/bin/python scripts/sms_campaign.py --track 2 --workers 6 --repeats 20
PYTHONPATH=src .venv/bin/python scripts/run_lrca.py
PYTHONPATH=src .venv/bin/python scripts/compute_rq2.py
PYTHONPATH=src .venv/bin/python scripts/compute_rq3.py
PYTHONPATH=src .venv/bin/python scripts/compute_rq3_friedman.py
PYTHONPATH=src .venv/bin/python scripts/compute_rq4.py
PYTHONPATH=src .venv/bin/python scripts/build_paper_numbers.py
```

Expected SSOTs: `paper_numbers_v4.json` (RQ1 mean SMS 0.104, 45/60 zero
cells; RQ3 Friedman chi2 15.30), `rq2_cliffs_delta_v4_mp5.json` (delta
0.3142), `s5_purity_v4.json`, `h2_incidence_v4.json`.

### 4.2 Study 2 (v5, 28 PUTs) and Study 4 (v7 arms)

```bash
# H2-1' (v5) and H2-2 (v7 paired contrast); defaults point at frozen pools
PYTHONPATH=src .venv/bin/python scripts/compute_dualblind_delta.py
# Study 3 / Study 4 graded attribution (H4''-graded/strict, H4''')
PYTHONPATH=src .venv/bin/python scripts/compute_h4_graded.py
PYTHONPATH=src .venv/bin/python scripts/h4_v7_sensitivities.py
# Study 4 H-LANG (C port)
PYTHONPATH=src .venv/bin/python scripts/compute_hlang_delta.py
```

Expected SSOTs: `dualblind_delta_delta_v5.json` (delta +0.4295),
`dualblind_delta_delta_v7.json` (Delta-delta +0.0147, CI [-0.021, +0.0686]),
`h4_graded_v6.json` / v7 outputs (Study 3 rich-class mean share 0.0833;
Study 4 pooled 0.2917, class D 0.4211 / class C 0.1026),
`hlang_delta_v7c.json` (delta_C +0.2449, one-sided lower -0.0357).

### 4.3 Post-hoc editorial sensitivity SSOTs (2026-07-10)

These respond to the editorial review and are cited by the manuscript as the
headline inference for aligned-versus-cross CIs:

```bash
# PUT-cluster block bootstrap: supersedes cell-level CIs for citation
PYTHONPATH=src .venv/bin/python scripts/compute_cluster_sensitivity.py
# Study-1 SMS denominator sensitivity (three denominators)
PYTHONPATH=src .venv/bin/python scripts/compute_denominator_sensitivity.py
```

Expected SSOTs (byte-stable at seed 20260708, B=10000):
`cluster_sensitivity_v1.json` (v5 lower +0.2777; v7 cross +0.2902; v7 same
+0.2793; Study-1 v4 +0.0833; H-LANG cluster lower 0.0; H2-2 already
PUT-clustered as registered) and `denominator_sensitivity_v1.json`
(all-admitted delta 0.3142; certified declared-stratum 0.7917 with 6/12 PUTs
recruiting zero certified primary-flipping mutants; active-any-flip 0.4043).

`review_shadow_kappa_v7.json` (kappa vs frozen 0.44/0.36, shadow-shadow
0.80) is committed as-is; re-running `scripts/review_shadow_kappa.py` calls
external vendors and belongs to tier 3.

### 4.4 Verification rule

Re-derived SSOTs must be byte-identical to the committed files:

```bash
git diff --stat data/results/
# Expected: empty (stochastic-PUT per-cell SMS may differ +-0.05 only if you
# regenerate SMS instead of replaying the frozen pools)
```

## 5. Tier 3 — Full LLM re-generation (API keys, hours, ~USD 100+)

Non-deterministic; produces a fresh pool, not the paper's numbers.

```bash
PYTHONPATH=src .venv/bin/python scripts/cross_source_campaign.py --workers 4   # Study 1
# Studies 2-4 ran once under frozen registrations (docs/PREREGISTRATION_STUDY{2,3,4}*)
# through the registered harness/gateway; see docs/CAMPAIGN_RUNBOOK.md and
# docs/PILOT_LOG.md (incidents P1-P16) before attempting any re-run.
PYTHONPATH=src .venv/bin/python scripts/review_shadow_kappa.py               # shadow review
```

## 6. Manuscript build

```bash
python3 venues/tosem/build.py --track regular
# Produces submission/TOSEM_regular_<date>/ with main.pdf + supplementary.pdf
# (tectonic used when xelatex is absent); check logs for zero "Missing character".
```

## 7. Reproducibility boundaries

- **LLM nondeterminism:** generation APIs expose no seed; use tier 2 for
  paper-grade reproduction.
- **Stochastic PUTs:** N=20 repeats leaves ~0.05 per-cell SMS noise if SMS is
  re-measured rather than replayed.
- **Registered verdicts:** frozen SSOTs are the citation source; the
  PUT-cluster CIs in `cluster_sensitivity_v1.json` supersede cell-level CIs
  for citation, with all registered verdicts unchanged.
- **Equivalence detector epsilon:** unified 1e-6 (PUT-side and AVP-side).

## 8. Per-artifact provenance

See `DATASET.md` (data/code lineage) and `docs/STATE.md` (current stage).

## 9. Reporting issues

If reproduction yields out-of-tolerance numbers, please open an issue with
the full `pytest -q` output, `python --version` + `pip freeze`, the SSOT
diff, and the exact command sequence used.
