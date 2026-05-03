# Project Structure (file-by-file walkthrough)

> Companion document to `README.md`. Lists every top-level directory
> and its role in the paper / replication / development workflow.

---

## Top-level files

| File | Role |
|---|---|
| `README.md` | Project home page; quickstart; license; citation |
| `LICENSE` | MIT (software components) |
| `CHANGELOG.md` | Stage-by-stage history (rounds 1-9 + post-acceptance) |
| `CONTRIBUTING.md` | Issue / PR / review-feedback policy |
| `RELEASE_CHECKLIST.md` | Pre-publication self-audit (Zenodo, GitHub, DOI minting) |
| `REPRODUCIBILITY.md` | Path-A (cache, 5 min) + Path-B (re-LLM, ~3h) replication |
| `DATASET.md` | Dataset card: PUTs, MRs, mutants, version lineage, licences |
| `ZENODO.md` | Pre-upload metadata template (creators, keywords, DOI) |
| `CLAUDE.md` | Project-level Claude Code instructions (writing rules, IST compliance, ARS) |
| `AGENTS.md` | Memory-context shim for Claude Code sessions |
| `pyproject.toml` | Build metadata (`p2-experiments`, optional `[dev]` extras) |
| `requirements-frozen.txt` | Pinned runtime + dev dependencies |
| `.python-version` | `3.12` (pyenv pin) |
| `.env.example` | LLM credential placeholders (`.env` is gitignored) |
| `.gitignore` | Excludes `.env`, `.claude/`, `.superpowers/`, LaTeX byproducts, large LLM caches |
| `论文初稿P2.md` | Original Chinese authoritative draft (151 KB) |
| `论文初稿P2_EN.md` | Long-form English draft, pre-IST compaction (177 KB) |
| `论文初稿P2_IST.md` | **Final IST submission body** (8,500 words) |
| `论文初稿P2_IST_appendix.md` | **Appendix A-G** (4,200 words) |

---

## `src/p2/` — Implementation

| Module | Responsibility | Tests |
|---|---|---|
| `puts/` | 12 Programs Under Test (a1-d3); each `program(x: float) -> float`, deterministic where possible | `tests/puts/` |
| `mrs/` | 60 Metamorphic Relations (12 PUTs × 5 MPs); strength labels in module headers | `tests/mrs/` |
| `mutators/` | Dual-LLM mutator pipeline: Claude generator + GPT-5.4 reviewer + DeepSeek arbitrator; cell-pool diversity sampler | `tests/mutators/` |
| `equiv/` | E1∧E2 equivalence judge: AST-coherent + output-equivalent diagnosis | `tests/equiv/` |
| `lrca/` | 3-layer Likely Root Cause Analysis: L0 artefact → L1 tolerance → L2 OOD → L3 assumption | `tests/lrca/` |
| `avp/` | Automated Verification Pipeline (P1 reuse): MP1 conservation, MP2/5 Wilcoxon, MP3 convergence, MP4 DTW; `dispatcher.py` + `repeat.py` | `tests/avp/` |
| `stats/` | Cliff's δ bootstrap, mixed-effects logit, Friedman χ², pattern coverage (RQ1-4) | `tests/stats/` |
| `pipeline/` | End-to-end orchestration: `campaign.py` (60-cell sweep), `run_cell.py`, `loaders.py` | `tests/pipeline/` |
| `viz/` | Matplotlib figure helpers (heatmap, boxplot, forest, scatter) | `tests/viz/` |
| `config/primary.py` | Selects v3b/v4 primary-MP configuration via env vars |  |

---

## `tests/` — 192-test pytest suite

| Subdir | Coverage |
|---|---|
| `puts/`, `mrs/` | Unit tests for each PUT and MR (interface contracts, output ranges) |
| `mutators/` | LLM-async dispatch, cell-pool diversity, dual-blind protocol |
| `equiv/` | E1∧E2 judge correctness; AVP-coherent gating; diagnosis branches |
| `lrca/` | Decision-tree dispatch; per-layer classifiers; calibration artefact |
| `avp/` | B2 strict-direction, dispatcher, interface, repeat-N statistics |
| `stats/` | Cliff's δ, mixed effects, pattern coverage, RQ1 rates |
| `pipeline/` | Campaign orchestration, single-cell run |
| `viz/` | Smoke tests for figure-generator helpers |
| `integration/` | Full pipeline + SMS campaign smoke + cell smoke |

Run with `PYTHONPATH=src .venv/bin/pytest tests/ -q`. Expected:
**192 passed in ~30 s**.

---

## `scripts/` — Campaign and analysis scripts

| Script | Stage |
|---|---|
| `build_pools.py` | Materialise mutant pools from raw LLM cache |
| `pilot_campaign.py` | Pilot LLM campaign (small-N smoke) |
| `llm_campaign.py` | Single-source LLM campaign (v1) |
| `operator_campaign.py` | 60-cell SMS campaign (v3) |
| `cross_source_campaign.py` | v4 cross-source campaign (Claude + GPT-5.4 + DeepSeek) |
| `compute_rq2.py` / `compute_rq2_logit.py` / `compute_rq2_v4_mp5.py` | RQ2 Cliff's δ + mixed-effects logit |
| `compute_rq2_power.py` / `compute_rq2_power_stipulated.py` | Power simulation (post-hoc + stipulated alternative) |
| `compute_rq3.py` / `compute_rq3_friedman.py` | RQ3 cross-class Friedman χ² + Bonferroni × 4 |
| `compute_rq4.py` | RQ4 pattern-coverage correlation |
| `compute_lrca_v4_mp5.py` | LRCA over v4 60 cells |
| `calibrate_lrca.py` | LRCA threshold calibration |
| `h5_sensitivity.py` | H5 sensitivity sweep (extra-MP coverage) |
| `permutation_c_class_inflation.py` | C-class permutation test |
| `p2_vs_syntactic_ast_diff_batch.py` | 12-PUT cosmic-ray vs P2 AST overlap |
| `regen_cosmic_ray_summaries.py` | Refresh cosmic-ray summaries from sqlite |
| `gen_mr_json.py` | Export 60 MRs as machine-readable JSON |
| `probe_concurrency.py` / `probe_equiv.py` | Diagnostic probes |
| `postprocess_unicode.py` | LaTeX preamble Unicode hardening |
| `build_paper_numbers.py` | **SSOT generator** for `data/results/paper_numbers_v4.json` |
| `generate_figures.py` | Generates 3 IST PNG figures into `figs/` |
| `build_ist_submission.sh` | Original elsarticle build script |
| `build_ist_submission_v9.sh` | **Final** IST submission builder (markdown → xelatex → PDF + DOCX) |
| `_cr_*_pytest.sh` | Per-PUT cosmic-ray pytest wrappers (12 files, ephemeral) |

---

## `data/` — Experiment data

| Path | Contents | Size |
|---|---|---|
| `data/mutants/` | 304 mutant files: 12 PUT pools × {v1, v3, v4} cross-source | 6.4 MB |
| `data/operator_campaign/cache/` | Single-source LLM raw cache (470 trials) | 2.5 MB |
| `data/operator_campaign/cache_cross/` | v4 cross-source LLM raw cache | 2.4 MB |
| `data/operator_campaign/raw/` | Operator-by-operator raw responses | 428 KB |
| `data/operator_campaign/registry.json` | Run registry | 12 KB |
| `data/operator_campaign/v1_archive/` | Frozen v1 cache (gitignored) | 1.9 MB |
| `data/results/` | **SSOT**: `paper_numbers_v4.json` + 56 sub-result JSONs | 7.8 MB |
| `data/lrca/` | LRCA per-cell decision logs (gitignored) | 0 B (regenerable) |
| `data/results/cosmic_ray_*.sqlite` | Cosmic-ray syntactic mutant databases | 1.8 MB |

The single source of truth is `data/results/paper_numbers_v4.json`,
regenerable via `scripts/build_paper_numbers.py`.

---

## `figs/` and `figures/` — Figures

| Path | Purpose |
|---|---|
| `figs/fig{1,2,3}*.png` | **Final IST submission figures** (3 PNGs @ 300 DPI). Embedded in `submission/p2_ist_final.tex`. Generated by `scripts/generate_figures.py`. |
| `figures/fig{1..5}*.pdf` | Pre-IST exploratory figures (5 PDFs); kept for replication-package lineage; not embedded in final paper. |

Earlier `figures/v2/` snapshot moved to `archive/figures_v2/`.

---

## `docs/` — Documentation

| Path | Purpose |
|---|---|
| `docs/STATE.md` | Single-session entry point: current stage, recent commits, outstanding nits |
| `docs/terminology_zh_en.md` | Chinese-English term glossary |
| `docs/experiment_documentation/` | Three-file companion: `EXPERIMENT_DESIGN.md`, `QUICK_START.md`, `DATA_README.md` |
| `docs/experiment_documentation.zip` | Distributable bundle of the above |
| `docs/review_2026-05-01/` | Round-1 reviewer transcripts (R0 EIC + R1-R4 panel) |
| `docs/review_2026-05-02/` | Round-8.5 re-review + reference verification audits + final-integrity reports |
| `docs/superpowers/plans/` | Implementation plans (Stage A-D, kept for audit trail) |
| `docs/superpowers/plans/done/` | Closed plans archive |
| `docs/theory/` | Three-pillar framework, MR-mutation algebra, theoretical grounding |

---

## `submission/` — Final IST submission bundle

| File | Purpose |
|---|---|
| `p2_ist_final.tex` | Final LaTeX source (elsarticle, 3,275 lines) |
| `p2_ist_final.pdf` | Compiled PDF (~956 KB) |
| `p2_ist_final.docx` | DOCX produced via Pandoc (for IST upload form) |
| `cover_letter_final.md` / `.pdf` | Final cover letter (round 8) |
| `texmf/` | elsarticle `.cls` + `.bst` (gitignored; downloaded by build script) |
| `README.md` | Submission-bundle internal notes |

---

## `replication/` — Zenodo upload bundle

| File | Purpose |
|---|---|
| `README.md` | Three-command quickstart for external reviewers |
| `REPRODUCIBILITY.md` | Detailed cache-replay path |
| `MANIFEST.txt` | SHA256 + size for every bundled file |
| `CITATION.cff` | Machine-readable citation |
| `.zenodo.json` | Zenodo deposition metadata |
| `build_zip.sh` | Deterministic bundle builder (excludes `.env`, `.claude/`, `__pycache__/`) |
| `replication.zip` | Latest-built bundle (2.3 MB) |

---

## `archive/` — Historical snapshots (kept for audit trail)

| Path | Contents |
|---|---|
| `archive/submission_drafts/` | `p2_ist_v{1..8}.{tex,pdf,docx}` — round-1 to round-8 manuscripts |
| `archive/cover_letters/` | `cover_letter_v{1..7}.{md,pdf}` — earlier cover-letter rounds |
| `archive/build_scripts/` | `build_ist_submission_v{2..8}.sh` — earlier build pipelines |
| `archive/process_summaries/` | `process_summary_{en,zh,v3_en,v3_zh}.{md,pdf}` — revision-process narratives |
| `archive/figures_v2/` | Earlier 5-PDF figure snapshot |

These are not on the active publication path but document the full
revision lineage. Safe to keep as historical evidence; not referenced
by the build pipeline.

---

## `third_party/p1_avp/`

Reference to the upstream P1 Automated Verification Pipeline. Reused
under MIT licence. The exact commit hash to be pinned in
`configs/default.yaml` once P1 is on arXiv.

---

## Configuration

`configs/default.yaml` (Hydra defaults):

```yaml
experiment:
  K_eq: 1000              # E2 equivalence sampling count
  N: 20                   # AVP statistical repetition count
  alpha: 0.05             # Wilcoxon significance
  alpha_FDR: 0.05         # Benjamini-Hochberg FDR

llm:
  generator: claude-opus-4-5    (temperature 0.3, seed 42)
  reviewer:  gpt-4o             (temperature 0.0, seed 42)
```

LLM model identifiers and arbitrators are runtime-overridable via
environment variables; see `REPRODUCIBILITY.md` §4 for the full
table.

---

## Cross-references between paper and repo

| Paper section | Code / data |
|---|---|
| §2 SMS theory | `src/p2/stats/` (computation), `论文初稿P2_IST.md` §2 (proof) |
| §3 Operator design | `src/p2/mutators/` + `data/operator_campaign/registry.json` |
| §4 PUTs and MRs | `src/p2/{puts,mrs}/` + `tests/{puts,mrs}/` |
| §5 RQ1-4 results | `data/results/paper_numbers_v4.json` (SSOT) + `scripts/compute_rq{1..4}*.py` |
| §6 Heatmap, AST overlap | `figs/fig{1,2,3}*.png` + `data/results/cosmic_ray_12put_ast_diff.json` |
| §7 Threats / limitations | `docs/review_2026-05-02/` reviewer correspondence |
| §8 Artifact availability | `replication/` + `ZENODO.md` (post-acceptance DOI) |
| Appendix A-G | `论文初稿P2_IST_appendix.md` |
