# P2 Dataset Card

**Primary version:** v4 cross-source（Claude Opus 4.6 + GPT-5.4 + DeepSeek V4 Pro）
**Earlier versions retained for lineage:** v1 (single-source LLM), v2/v3/v3b (intermediate). All paper numbers in §5–§6 derive from v4.

---

## 1. Programs Under Test (PUTs)

`src/p2/puts/{a1..d3}.py` — 12 scientific-computing programs, signature `float → float`, deterministic where possible (stochastic PUTs accept `random_state`).

| Class | PUTs | Domain |
|---|---|---|
| a (numeric) | a1, a2, a3 | linear algebra / numerical integration / polynomial roots |
| b (probabilistic) | b1, b2, b3 | MCMC / Monte Carlo integration / probability distributions |
| c (surrogate) | c1, c2, c3 | Gaussian Process / RBF / scikit-learn surrogate |
| d (ML) | d1, d2, d3 | MLP / decision tree / kNN (scikit-learn) |

**Caveat (R-11 in revision):** `program(x: float) → float` signature constrains coverage; 4 sub-domains uncovered (PDE advanced solvers, FFT/spectral, optimization extensions, symbolic computation). See §3.1.1.

## 2. Metamorphic Relations (MRs)

`src/p2/mrs/{a1..d3}.py` — 60 MRs, 5 MPs per PUT. Strength labels ●● / ● / ○ in each module's docstring header (consistent with §3.3 matrix).

## 3. Mutation operators

`src/p2/mutators/operator_registry.py` — 37 named operators in 5 classes:
- **CE** (constant edit), **OS** (operator substitution), **HP** (hyperparameter), **TF** (transform), **SI/CF** (structural / control flow).

Each entry: `target_locator + transformation + rationale + is_key`. The 12 `is_key=True` operators are generated under K=20 repeats for stability metrics.

## 4. Generated mutants

### v4 cross-source (PRIMARY — paper analysis)
- `data/mutants/{put}_pool_v4/m{NN}_{op_id}_a{NN}.py` — per-PUT pool, ≥12 mutants/PUT, 3-LLM diversity sampling.
- `data/mutants/{put}_pool_v4/manifest.json` — generator attribution per mutant.

### Earlier versions (retained for §4.2.5 lineage discussion)
- `data/mutants/{put}_pool_v3/`, `_v3b/` — intermediate single-source pools (v3 = c→MP5 primary; v3b = c→MP1 sensitivity).
- `data/mutants/{put}_pool/` — v1 single-LLM (Claude only) baseline.
- `data/mutants/{put}_MP{k}_llm/` — Phase-1 cell-level campaign (45 confirmed mutants); superseded by pool-level pipeline but kept for traceability.

### Manual pilot (NOT in paper analysis)
- `data/mutants/a2_MP1_mut1/`, `data/mutants/b2_MP2_mut1/` — 5-mutant hand-crafted sets used to validate pipeline end-to-end (§4.8 calibration). **Excluded from §5–§6 numbers.**

### Raw LLM trials
- `data/operator_campaign/raw/{op_id}.json` — per-operator trial logs (prompt, raw LLM response, V1-V6 + operator_match labels, reviewer reasoning text). 470 trials total across 37 operators.
- `data/operator_campaign/cache/{op_id}_attempt{NN}.py` — 212 confirmed mutants (V1-V6 ✓ ∧ operator_match=Yes). Used as input to `build_pools.py`.
- `data/operator_campaign/cache_cross/` — 3-LLM cross-source confirmed cache for v4.

## 5. Generation prompts

- `src/p2/mutators/prompts/operator_template.txt` — operator-level generator (Claude Opus 4.6).
- `src/p2/mutators/prompts/operator_reviewer_template.txt` — reviewer (GPT-5.4 via bltcy.ai proxy; DeepSeek V4 Pro arbitrator on UNCERTAIN).
- `src/p2/mutators/prompts/generator_template.txt` / `reviewer_template.txt` — Phase-1 cell-level templates (retained for ablation comparison).

## 6. Metrics outputs

### v4 (PRIMARY — cited in paper)
| File | Content |
|---|---|
| `data/results/paper_numbers_v4.json` | **SSOT for §5.6–§5.9, §6** — RQ1/2/3/4 aggregate numbers |
| `data/results/sms_track2_v4.json` | per-cell SMS, 60 cells × N=20 repeats |
| `data/results/lrca_60cell_v4.json` | per-cell C1/C2/C3/C4/Artifact counts + suspect_share |
| `data/results/rq2_cliffs_delta_v4.json` | Cliff's δ + 95% bootstrap CI |
| `data/results/rq2_cliffs_delta_logit_v4.json` | logit-transformed robustness check (R-22) |
| `data/results/rq3_mixed_effects_v4.json` | primary mixed-effects (Singular) + fallback FE |
| `data/results/rq3_friedman_v4.json` | Friedman χ² test (H4 verdict source, R-21) |
| `data/results/rq3_model_summary_v4.txt` | fallback model full summary |
| `data/results/rq4_pattern_coverage_v4.json` | per-PUT PC + Spearman / Kendall |

### Earlier versions (retained for sensitivity narrative)
- `paper_numbers.json` / `_v3.json` / `_v3b.json` — early versions (do **not** cite; ⚠ superseded by v4).
- `sms_track1.json` — Track-1 (12 aligned cells, Phase 1).
- `sms_track2.json` / `_v1_backup.json` / `_v2.json` / `_v3.json` / `_v3b.json` — earlier pool sizes / configurations.
- `lrca_60cell.json` / `_v3.json` / `_v3b.json` — earlier LRCA runs.
- `lrca_calibration.json` + `_console.log` — 9-grid LRCA threshold sweep (§4.6.4).
- `c_class_mp_ranking.json` — c-class primary-MP selection ranking (§3.5.1).

### Cross-cutting
- `data/results/operator_metrics.json` — R_sem / D_impl / R_kill per operator (12 is_key, K=20).
- `data/results/equiv_diagnosis.json` — equivalence detector calibration logs.
- `data/results/llm_campaign_log.json` — Phase-1 cell-level campaign log (historical).
- `data/results/pilot_results.json` — manual pilot outcomes (historical).
- `data/results/concurrency_probe.txt` — async concurrency micro-benchmark.

## 7. Figures

`figures/` (current = v4) and `figures/v2/` (snapshot for v2 lineage comparison):
- `fig1_60cell_heatmap.pdf` — 60-cell SMS heatmap (rows = PUT, cols = MP, ★ = aligned cell).
- `fig2_aligned_vs_cross_box.pdf` — aligned vs cross box plot.
- `fig3_class_forest.pdf` — across-class SMS forest (mean ± SEM).
- `fig4_sms_vs_c1share.pdf` — SMS vs C1_share scatter (per cell, n=60) + Spearman ρ.
- `fig5_sms_vs_pc.pdf` — SMS vs PC scatter (per PUT, n=12) + Spearman ρ.

## 8. License

Code: MIT (`LICENSE`).
Data (mutants, results, figures): CC-BY-4.0.

## 9. Citation

Pre-publication. Use the Zenodo DOI (see `ZENODO.md`) for archival reference; the journal citation will be added after acceptance.

```bibtex
@article{li2026sms,
  title   = {When LLM Source Diversity Doesn't Help: A Semantic Mutation Score Audit},
  author  = {Li, Meng and [coauthors]},
  journal = {Information and Software Technology},
  year    = {2027 (under review)},
  note    = {Artifact: <Zenodo DOI placeholder>}
}
```

## 10. Versioning policy

- `paper_numbers_v4.json` is the **frozen SSOT** for the manuscript under review.
- If a R2/R3 revision changes any number, a new `_v5.json` will be added; the v4 file stays immutable.
- `docs/STATE.md` records the active version each session.
