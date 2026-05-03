# Replication Package — Semantic Mutation Score (SMS) Audit (P2)

> **Paper.** *When Same-Prompt LLM Source Diversity Doesn't Help: An
> Ablation of Semantic Mutation Operators in Metamorphic Testing for
> Single-Output Scientific Computing Kernels.*
> Submitted to *Information and Software Technology* (IST), 2026.
>
> **Replication-package DOI (placeholder).** `10.5281/zenodo.PLACEHOLDER`
> **Paper DOI (placeholder).** `10.1016/j.infsof.PLACEHOLDER`
> **GitHub mirror (placeholder).** `https://github.com/PLACEHOLDER/p2-sms-audit`

This bundle contains everything an external reviewer needs to
reproduce the headline numbers cited in the manuscript: 12 Programs
Under Test (PUTs), 60 metamorphic-test cells, 292 confirmed
LLM-generated mutants (v4 cross-source), 1,250 cosmic-ray syntactic
mutants for AST comparison, and the full statistical-analysis
pipeline. **Replication from the committed cache is deterministic
(SEED=42, temperature=0); no LLM API access is required.**

---

## 1. Three-command quickstart

```bash
# 1. Install pinned dependencies (Python 3.11+ recommended; 3.12 tested)
pip install -r requirements-frozen.txt

# 2. Rebuild the SSOT statistics file (paper_numbers_v4.json) from cache
PYTHONPATH=src SMS_VERSION=v4 P2_PRIMARY_VERSION=v3b \
  python scripts/build_paper_numbers.py

# 3. Rebuild the 12-PUT cosmic-ray vs P2 AST-diff comparison
PYTHONPATH=src python scripts/p2_vs_syntactic_ast_diff_batch.py
```

Total wall-clock: ≈ 2–5 minutes on a modern laptop. No network calls.

If you also want to re-run the full statistical analysis (Cliff's δ
bootstrap, Friedman χ², mixed-effects, RQ4 pattern coverage) from the
SMS cache:

```bash
PYTHONPATH=src python scripts/compute_rq2.py
PYTHONPATH=src python scripts/compute_rq2_power.py
PYTHONPATH=src python scripts/compute_rq3.py
PYTHONPATH=src python scripts/compute_rq3_friedman.py
PYTHONPATH=src python scripts/compute_rq4.py
PYTHONPATH=src python scripts/h5_sensitivity.py
PYTHONPATH=src python scripts/permutation_c_class_inflation.py
```

---

## 2. Expected outputs and headline numbers

After step 2 above, `data/results/paper_numbers_v4.json` should
contain (verify with `python -c "import json; print(json.load(open('data/results/paper_numbers_v4.json'))['rq2']['cliffs_delta'])"`):

| Section | Number | Expected value | Source field |
|---|---|---|---|
| §5.6 (RQ1 H1) | mean SMS | `0.104` | `rq1.mean_sms` |
| §5.6 (RQ1 H1) | median SMS | `0.000` | `rq1.median_sms` |
| §5.7 (RQ2 H2) | Cliff's δ (aligned vs cross) | `0.4392` | `rq2.cliffs_delta` |
| §5.7 (RQ2 H2) | δ 95% bootstrap CI | `[0.1267, 0.7396]` | `rq2.delta_ci_95_{lo,hi}` |
| §5.7.2 stipulated power | power at δ_truth=0.474 | `0.491` | `rq2_power_stipulated_v4.json` |
| §5.8 (RQ3 H4) | Friedman χ² | `15.3028` | `rq3.friedman_chi2` |
| §5.8 (RQ3 H4) | Friedman p | `0.0041` | `rq3.friedman_p` |
| §5.9 (RQ4 H3) | Spearman ρ | `0.1628` | `rq4.spearman_rho` |
| §5.9 (RQ4 H3) | Spearman p | `0.6133` | `rq4.spearman_p` |
| §3.2.6.3 (AST diff) | mean overlap_ratio | `0.0514` | `cosmic_ray_12put_ast_diff.json` |

After step 3 above, `data/results/cosmic_ray_12put_ast_diff.json`
contains the per-PUT AST-overlap counts (1,250 cosmic-ray mutants vs
292 P2 mutants; 5.14% overlap). The 12 underlying SQLite databases at
`data/results/cosmic_ray_{a1..d3}.sqlite` (each < 2 MB) hold the
cosmic-ray Mutmut/Cosmic Ray runs.

---

## 3. Directory map

```
replication/
├── README.md            # this file
├── REPRODUCIBILITY.md   # detailed environment + verification snippets
├── CITATION.cff         # GitHub/Zenodo citation auto-render
├── .zenodo.json         # Zenodo metadata (auto-ingested at publish)
├── MANIFEST.txt         # SHA256 + size for every file in the bundle
└── build_zip.sh         # produces replication.zip ready for upload

../src/                  # 12 PUTs, 60 MRs, 37 mutation operators, AVP/LRCA/SMS
../scripts/              # campaign + analysis pipeline (build_paper_numbers et al.)
../tests/                # 116 unit tests
../data/results/         # SSOT JSON metrics + cosmic-ray sqlite + console logs
../data/mutants/*_pool_v4/   # 292 confirmed mutants (12 PUTs, 3 LLMs)
../docs/review_2026-05-01/   # Round-1 reviewer reports + EIC decision
../docs/review_2026-05-02/   # Round-2 re-review + final integrity report
../figures/              # 5 paper PDFs
../requirements-frozen.txt   # pinned dependencies
../REPRODUCIBILITY.md    # paper §4.2.3 reproducibility checklist
../DATASET.md            # per-artifact provenance + version lineage
../LICENSE               # MIT (code) + CC-BY-4.0 (data; see CITATION.cff)
```

---

## 4. Reproducibility caveats

- **Environment variables.** Two are load-bearing for the analysis:
  - `SMS_VERSION=v4` — selects the v4 cross-source pool as primary
    (paper §5.6).
  - `P2_PRIMARY_VERSION=v3b` — selects the v3b data-driven primary MP
    for the c-class (paper §3.5.1).
- **LLM API non-determinism.** If you set
  `temperature > 0` and re-call Claude / GPT / DeepSeek, the mutant
  pool will differ at the trial level. The committed
  `data/mutants/*_pool_v4/` directories were generated at
  `temperature=0` and the v4 manifest is byte-stable. **Replication
  of statistical results uses these committed pools and does not
  re-call any LLM.**
- **Random seeds.** All bootstrap / permutation tests use `SEED=42`
  (see `scripts/compute_rq2_power.py`,
  `scripts/permutation_c_class_inflation.py`,
  `scripts/compute_rq2.py`).
- **OS/hardware.** Tested on macOS 24.6 (Apple Silicon) and Ubuntu
  22.04 (x86_64). Statistical results are bit-identical across these
  two environments under the pinned versions in
  `requirements-frozen.txt`.
- **Compute.** A 4-core laptop with 8 GB RAM is sufficient. The full
  pipeline (cache replay only) finishes in ≤ 2 hours wallclock; the
  three-command quickstart finishes in < 5 minutes.

---

## 5. Audit trail

- **Commit history.** `git log --oneline` in the bundled repo
  documents every change since the original submission. Round-1
  revisions are tagged in commit `2eb84ea` (*"revision: address all 5
  reviewer reports"*).
- **Reviewer reports.** Round 1 — `docs/review_2026-05-01/r{0..4}_*.md`
  (5 reports + EIC decision). Round 2 — `docs/review_2026-05-02/r{0..4}_*_rereview.md`
  + `stage_4_5_final_integrity_report.md`.
- **Integrity check logs.** Stage 4.5 final integrity report
  (`docs/review_2026-05-02/stage_4_5_final_integrity_report.md`)
  cross-validates every paper number against the SSOT JSON files.
- **Operator campaign log.** `data/operator_campaign/v2_revised6.log`
  (cited in §4.4) is the per-trial timing/cost log.

---

## 6. Manuscript pointer

- `论文初稿P2_IST.md` — IST-formatted manuscript (1844 lines, trimmed)
- `论文初稿P2_IST_appendix.md` — IST appendix
- `论文初稿P2_EN.md` — full English version with §3–§9 expansions
- `submission/p2_ist.pdf` — final-pass PDF
- `submission/cover_letter_v2.md` — cover letter (round 2) with
  Zenodo DOI commitment

---

## 7. License

- **Software** (`src/`, `scripts/`, `tests/`, `replication/build_zip.sh`):
  MIT (see `../LICENSE`).
- **Data and figures** (`data/`, `figures/`): CC-BY-4.0 with
  attribution to the paper authors.
- **Paper text and reviewer reports** (`论文初稿P2_*.md`,
  `docs/review_*/`): All Rights Reserved by the authors; included for
  audit purposes only.

---

## 8. Citation

Please cite both the paper and this replication archive (see
`CITATION.cff`). After acceptance the placeholders in §0 above will
be replaced by the minted DOIs.
