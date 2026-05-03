# Semantic Mutation Score (SMS) Audit — Replication Repository (P2)

> **Paper.** *When Same-Prompt LLM Source Diversity Doesn't Help: An
> Ablation of Semantic Mutation Operators in Metamorphic Testing for
> Single-Output Scientific-Computing Kernels.*
> Submitted to **Information and Software Technology (IST)**, May 2026.
>
> **Status.** Submission-ready (round-9, 2026-05-03).
> **Replication-package DOI (placeholder).** `10.5281/zenodo.PLACEHOLDER`
> **Paper DOI (placeholder).** `10.1016/j.infsof.PLACEHOLDER`

This repository contains the complete experimental infrastructure,
data, statistical analysis, and manuscript materials for the P2
Semantic Mutation Score audit. **Replication from the committed cache
is deterministic** (SEED=42, temperature=0); no LLM API access is
required for headline-number replication.

---

## What this repository delivers

| Layer | Artifact | Where |
|---|---|---|
| **Theory** | Semantic Mutation Score (SMS) backward-compatibility theorem; five domain-semantic operator classes (CE, OS, HP, TF, SI) | `论文初稿P2_IST.md` §2-§3 |
| **Experiment** | 12 PUTs × 5 MPs × 60 cells; 470 LLM trials; 292 confirmed mutants (v4 cross-source); 1,250 cosmic-ray syntactic mutants for AST overlap | `src/p2/`, `data/` |
| **Pipeline** | Dual-LLM generator (Claude Opus 4.6); reviewer arbitration (GPT-5.4 + DeepSeek V4 Pro); E1∧E2 equivalence judge; 3-layer LRCA classifier | `src/p2/{mutators,equiv,lrca,avp}/` |
| **Statistics** | SMS computation; Cliff's δ bootstrap; Friedman χ² + Bonferroni; mixed-effects logit; pattern-coverage RQ4 | `src/p2/stats/`, `data/results/` |
| **Manuscript** | IST main body (8.5k words) + Appendix (A-G) + cover letter; reviewer-response history (rounds 1-9) | `submission/`, `archive/` |
| **Reproducibility** | 192-test pytest suite; pinned `requirements-frozen.txt`; deterministic cache replay in 5 min | `tests/`, `replication/`, `REPRODUCIBILITY.md` |

---

## Quickstart (5 minutes, no API keys)

```bash
# 1. Clone and install pinned dependencies (Python 3.12 tested; 3.11+ supported)
git clone <this-repo>.git p2-sms-audit
cd p2-sms-audit
python3.12 -m venv .venv
.venv/bin/pip install -r requirements-frozen.txt

# 2. Run the unit-test suite (must report 192 passed in ~30 s)
PYTHONPATH=src .venv/bin/pytest tests/ -q

# 3. Rebuild the SSOT statistics file (all paper-cited numbers) from cache
PYTHONPATH=src SMS_VERSION=v4 P2_PRIMARY_VERSION=v3b \
  .venv/bin/python scripts/build_paper_numbers.py

# 4. Inspect the result
cat data/results/paper_numbers_v4.json | python -m json.tool | head -40
```

For full re-LLM-call reproduction (Path B, ~3 hours, requires API
keys + ~USD 80), see `REPRODUCIBILITY.md` §4.

---

## Repository layout

```
.
├── src/p2/              # Implementation: PUTs, MRs, mutators, AVP, LRCA, stats, pipeline
├── tests/               # 192-test pytest suite (PUT/MR/AVP/LRCA/equiv/stats/integration)
├── scripts/             # End-to-end campaign + analysis + figure scripts
├── configs/default.yaml # Hydra defaults
├── data/                # Mutant pools, raw LLM cache, SMS results, AST diffs
│   ├── mutants/         # 304 mutant files (12 pools × v1/v3/v4 cross-source)
│   ├── operator_campaign/
│   │   ├── cache/       # 470 raw LLM responses (deterministic replay)
│   │   └── cache_cross/ # v4 cross-source LLM trials
│   └── results/         # SSOT: paper_numbers_v4.json + 56 sub-result JSONs
├── figs/                # 3 IST-final PNG figures (论文嵌图，by generate_figures.py)
├── figures/             # 5 exploratory PDF figures (pre-consolidation lineage)
├── docs/                # Documentation: STATE, theory, reviews, experiment guide
│   ├── experiment_documentation/   # EXPERIMENT_DESIGN + QUICK_START + DATA_README
│   ├── review_2026-05-01/          # Round-1 reviewer transcripts (R0-R4)
│   ├── review_2026-05-02/          # Round-8.5 re-review + reference verification
│   └── theory/                     # Three-pillar framework, MR-mutation algebra
├── submission/          # Final IST bundle: p2_ist_final.{tex,pdf,docx} + cover_letter
├── replication/         # Zenodo upload bundle: README, MANIFEST, .zenodo.json, build_zip.sh
├── archive/             # Historical snapshots (v1-v8 drafts, build scripts, cover letters)
└── third_party/p1_avp/  # Reference to upstream P1 AVP code
```

A version-by-file walkthrough lives in `PROJECT_STRUCTURE.md`.

---

## Key documents

| File | Purpose |
|---|---|
| `论文初稿P2_IST.md` | Final IST submission (English, 8,500 words) |
| `论文初稿P2_IST_appendix.md` | Appendix A-G (4,200 words) |
| `论文初稿P2_EN.md` | Long-form English draft (pre-IST compaction) |
| `论文初稿P2.md` | Original Chinese authoritative draft |
| `REPRODUCIBILITY.md` | Step-by-step replication guide (Path A: cache; Path B: re-LLM) |
| `DATASET.md` | Per-artifact provenance, version lineage, and licensing |
| `ZENODO.md` | Pre-upload metadata template (DOI placeholder pending acceptance) |
| `CHANGELOG.md` | Stage-by-stage history (round-1 → round-9) |
| `RELEASE_CHECKLIST.md` | Pre-publication self-audit checklist |
| `CONTRIBUTING.md` | Issue / PR / review-feedback channels |

---

## Citation

Once accepted, please cite:

```bibtex
@article{li2026sms,
  title   = {When Same-Prompt LLM Source Diversity Doesn't Help:
             An Ablation of Semantic Mutation Operators in Metamorphic
             Testing for Single-Output Scientific-Computing Kernels},
  author  = {Li, Meng},
  journal = {Information and Software Technology},
  year    = {2026},
  note    = {In press; preprint and replication bundle at
             \url{https://doi.org/10.5281/zenodo.PLACEHOLDER}},
}
```

A machine-readable `CITATION.cff` lives in `replication/`.

---

## License

- **Software** (`src/`, `scripts/`, `tests/`): MIT — see `LICENSE`.
- **Data** (`data/`, `figs/`, `figures/`): CC-BY-4.0.
- **Manuscript** (`*.md`, `submission/`): authors retain copyright; archival
  use under publisher's licence after acceptance.

---

## Maintainer

Meng Li (`mlemon@usc.edu.cn`). Issues, suggestions, and replication
problems are welcome via this repository's issue tracker; for
substantive review or collaboration, please use the email address.

---

## Acknowledgements

The P1 Automated Verification Pipeline (referenced under
`third_party/p1_avp/`) is reused under its original MIT licence.
LLM credits: Anthropic (Claude Opus 4.6), OpenAI / bltcy.ai (GPT-5.4),
DeepSeek (V4 Pro). Development tooling: Claude Code (Anthropic).
