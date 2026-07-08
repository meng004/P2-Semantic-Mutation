# Semantic Mutation Score (SMS) Audit — Replication Repository (P2)

> **Paper.** *When Same-Prompt LLM Source Diversity Doesn't Help: An
> Ablation of Semantic Mutation Operators in Metamorphic Testing for
> Single-Output Scientific-Computing Kernels.*
> Submitted to **Information and Software Technology (IST)**, May 2026.
>
> **Status.** Submission-ready (round-9, 2026-05-03).
> **arXiv preprint (placeholder).** `arXiv:25NN.NNNNN [cs.SE]`
> **Replication-package DOI (placeholder).** `10.5281/zenodo.PLACEHOLDER`
> **Paper DOI (placeholder).** `10.1016/j.infsof.PLACEHOLDER`

This repository is the public replication artefact for the P2 audit.
It carries the complete experimental infrastructure, raw data,
statistical pipeline, manuscript, and review history. **Replication
from the committed cache is deterministic** (SEED=42, temperature=0);
no LLM API access is required for headline-number replication.

We open the repository before acceptance so that the metamorphic
testing, mutation testing, and scientific-software-engineering
communities can scrutinise our claims — both the methodological
backbone and the headline empirical findings.

---

## 1. Motivation — why this paper exists

Metamorphic Testing (MT) is the dominant test-oracle solution for
scientific-computing kernels where a ground-truth oracle is
unattainable. Its strength rests on the choice of metamorphic
relations (MRs), and the *adequacy* of an MR set has historically
been judged by the classical **Mutation Score (MS)** — that is, by
how many syntactic AST mutations the MR set kills.

Two gaps in this picture motivated the audit:

1. **Syntactic ≠ semantic.** Classical MS is defined over AST-level
   edits (e.g., cosmic-ray's default operator suite). Real
   scientific-computing faults — broken invariance/equivariance,
   monotonicity/order violations, mis-ordered convergence, qualitative
   dynamics changes, and method-comparison regressions — live one level
   above the AST. An MR set that survives a
   100% classical MS may still let through faults that violate
   conservation. The community needs an MR-adequacy metric that
   speaks the language of the domain, not of the parser.
2. **LLM-generated mutants are now plausible.** With Claude / GPT /
   DeepSeek able to write mutants that respect type signatures and
   even pass cheap checks, a natural question is whether
   *cross-source* LLM diversity — three different LLMs under an
   identical prompt — strengthens MR adequacy. If yes, the field
   gains a cheap mutant generator; if no, the lever is somewhere
   else.

Existing work (Just *et al.* FSE 2014; Petrović & Ivanković 2018;
Tip *et al.* LLMorpheus 2024; Andrews *et al.* 2005) covers
syntactic mutation with vigour, but did not give scientific-computing
practitioners a domain-aware adequacy lens or an empirical answer to
the LLM-source-diversity question. P2 is the audit that closes those
two gaps within the scope of single-output `float → float` kernels.

---

## 2. Core contributions

| # | Contribution | Where |
|---|---|---|
| C1 | **Three-layer methodology backbone** — Layer 1 *Definitional* (necessary conditions for "semantic mutation"), Layer 2 *Operational* (the E1 ∧ E2 equivalence judge), Layer 3 *Applied* (AST-normalised traceability against cosmic-ray) | `submission/p2_ist_final.pdf` §3 |
| C2 | **Semantic Mutation Score (SMS)** with a degeneration theorem: SMS reduces almost-everywhere to the classical Mutation Score in the syntactic limit, modulo a domain-set measure-zero subset. SMS is therefore *backward compatible* — any SMS-based conclusion remains consistent with prior mutation-testing literature in the classical regime. | §2 + Appendix A.5 |
| C3 | **NOETHER-aligned MR MetaPattern axes** — invariance/equivariance (`inv`), monotonicity/order (`mono`), convergence/limit (`conv`), qualitative dynamics (`dyn`), and method comparison (`cmp`) — exercised over 12 PUTs x 5 MR-pattern cells. Existing mutant-file suffixes such as `CE1/OS1/HP1/TF1/SI1` are historical internal IDs, not reader-facing concept names. | `src/p2/mutators/`, §3.2-3.6 |
| C4 | **Three-stage same-source / cross-source ablation** (v3 / v3b / v4) cleanly isolating MR-alignment design from LLM source diversity under identical prompt. | `data/operator_campaign/`, §4.2.5 |
| C5 | **AST-normalised empirical traceability** showing P2 mutants are *not* a subset of cosmic-ray's syntactic-mutant pool: 5.14 % overall AST overlap across 12 PUTs; the structurally non-local semantic-effect faults account for 54.5 % of the P2 pool (159 / 292 mutants) and are unreachable at 0 % under default first-order syntactic configurations. | `figs/fig3_ast_overlap_per_class.png`, §3.6 |
| C6 | **Pre-registered headline finding (negative)** — the H2 large-effect threshold (Cliff's δ ≥ 0.474, Romano 2006) is **not met** under the frozen-primary MP5 criterion (δ = 0.323 in v3 and 0.314 in v4). The MP1/data-driven v4 contrast is retained as sensitivity (δ = 0.439), not as the H2 verdict. We frame this as a bounded, underpowered exploratory contribution, not a false-positive rescue. | §5.7, §5.9 |
| C7 | **Reproducible artefact** — 192-test pytest suite, deterministic 5-minute cache replay, pinned dependencies, and provenance for every paper-cited number through `data/results/paper_numbers_v4.json`, `data/results/rq2_cliffs_delta_v4_mp5.json`, `data/results/rq3_friedman_v4.json`, and `data/results/rq4_pattern_coverage_v4.json`. | `tests/`, `replication/`, `REPRODUCIBILITY.md` |

The audit's scientific posture is conservative: we report a
**negative result on the LLM-diversity lever**, retain the H2
not-met statement under pre-registration, and surface the
methodology backbone (C1) as the primary contribution. The empirical
audit (C4-C6) is then auxiliary evidence under that backbone.

---

## 3. Replication — three speed grades

> Run all commands from the repository root unless noted.

### 3.1 Five-minute "is the SSOT correct?" smoke test

```bash
git clone <this-repo>.git p2-sms-audit
cd p2-sms-audit
python3.12 -m venv .venv
.venv/bin/pip install -r requirements-frozen.txt

# Unit tests (must report 192 passed in ~30 s)
PYTHONPATH=src .venv/bin/pytest tests/ -q

# Regenerate the paper-number SSOT from cache (no API calls)
PYTHONPATH=src SMS_VERSION=v4 P2_PRIMARY_VERSION=v3b \
  .venv/bin/python scripts/build_paper_numbers.py
```

Expected outcome: `data/results/paper_numbers_v4.json` is rewritten
byte-identically to its committed version. If `git diff
data/results/paper_numbers_v4.json` is empty, the SSOT is verified.

### 3.2 Cache-replay reproduction (~ 20 minutes, no API keys)

For every paper-cited result in §5 / §6:

```bash
# 1. Rebuild SMS heatmap (data/results/sms_track2_v4.json)
PYTHONPATH=src .venv/bin/python scripts/operator_campaign.py \
    --replay-from-cache

# 2. Run RQ2 / RQ3 / RQ4 statistical pipeline
PYTHONPATH=src .venv/bin/python scripts/compute_rq2_v4_mp5.py
PYTHONPATH=src .venv/bin/python scripts/compute_rq3_friedman.py
PYTHONPATH=src .venv/bin/python scripts/compute_rq4.py

# 3. Recompute LRCA over 60 cells
PYTHONPATH=src .venv/bin/python scripts/compute_lrca_v4_mp5.py

# 4. Rebuild AST-overlap (cosmic-ray vs P2)
PYTHONPATH=src .venv/bin/python scripts/p2_vs_syntactic_ast_diff_batch.py

# 5. Reconsolidate paper numbers (SSOT)
PYTHONPATH=src SMS_VERSION=v4 P2_PRIMARY_VERSION=v3b \
  .venv/bin/python scripts/build_paper_numbers.py

# 6. Regenerate the three IST submission figures
PYTHONPATH=src .venv/bin/python scripts/generate_figures.py
```

Wallclock: ~20 minutes on an Apple M-series laptop. The cache
(`data/operator_campaign/cache_cross/`, 2.4 MB, 470 LLM trials with
raw responses + V1-V6 reviewer labels) makes every step
deterministic.

### 3.3 Re-LLM-call reproduction (~ 3 hours, requires API keys)

If you want to regenerate the v4 mutant pool from scratch — different
LLM seeds will produce non-byte-identical mutants but the headline
findings are stable:

```bash
cp .env.example .env
# Edit .env: set ANTHROPIC_API_KEY, BLTCY_BASE_URL/KEY, DEEPSEEK_BASE_URL/KEY
# (BLTCY_* points at any OpenAI-compatible endpoint that exposes GPT-5.4)

PYTHONPATH=src .venv/bin/python scripts/cross_source_campaign.py \
    --concurrency 6 --temperature 0
```

Estimated cost: USD ~80 for one full v4 cross-source pass (Claude
Opus + GPT-5.4 + DeepSeek). See `REPRODUCIBILITY.md` §4 for the full
table of expected costs and time budgets per stage.

---

## 4. What lives where

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
├── figs/                # 3 IST-final PNG figures (paper-embedded)
├── figures/             # 5 exploratory PDF figures (pre-consolidation lineage)
├── docs/                # STATE, theory, reviews, experiment guide
├── submission/          # Final IST bundle: p2_ist_final.{tex,pdf,docx} + cover_letter
├── replication/         # Zenodo upload bundle: README, MANIFEST, .zenodo.json, build_zip.sh
├── archive/             # Historical snapshots (v1-v8 drafts, build scripts, cover letters)
└── third_party/p1_avp/  # Reference to upstream P1 AVP code
```

A file-by-file walkthrough lives in `PROJECT_STRUCTURE.md`. Key
top-level documents:

| File | Purpose |
|---|---|
| `论文初稿P2_IST.md` | Final IST submission (English, 8,500 words) |
| `论文初稿P2_IST_appendix.md` | Appendix A-G (4,200 words) |
| `submission/p2_ist_final.pdf` | Compiled article PDF (round-9) |
| `submission/cover_letter_final.pdf` | Cover letter to IST |
| `REPRODUCIBILITY.md` | Step-by-step replication guide |
| `DATASET.md` | Per-artefact provenance and licences |
| `RELEASE_CHECKLIST.md` | Pre-publication self-audit |
| `CHANGELOG.md` | Round-by-round change log |
| `CONTRIBUTING.md` | Issue / PR / review-feedback policy |

---

## 5. Citation

Once accepted, please cite:

```bibtex
@article{li2026sms,
  title   = {When Same-Prompt LLM Source Diversity Doesn't Help:
             An Ablation of Semantic Mutation Operators in Metamorphic
             Testing for Single-Output Scientific-Computing Kernels},
  author  = {Li, Meng},
  journal = {Information and Software Technology},
  year    = {2026},
  note    = {In press; preprint at \url{https://arxiv.org/abs/PLACEHOLDER}; replication
             bundle at \url{https://doi.org/10.5281/zenodo.PLACEHOLDER}},
}
```

A machine-readable `CITATION.cff` lives in `replication/`.

---

## 6. License

- **Software** (`src/`, `scripts/`, `tests/`): MIT — see `LICENSE`.
- **Data** (`data/`, `figs/`, `figures/`): CC-BY-4.0.
- **Manuscript** (`*.md`, `submission/`): authors retain copyright;
  archival use under publisher's licence after acceptance.

---

## 7. Maintainer and contact

Meng Li (`mlemon@usc.edu.cn`). Issues, replication failures, and
suggestions are welcome via this repository's issue tracker; for
substantive review, collaboration, or invited talks, please use the
email address.

---

## 8. Acknowledgements

The P1 Automated Verification Pipeline (referenced under
`third_party/p1_avp/`) is reused under its original MIT licence.
LLM credits: Anthropic (Claude Opus 4.6), GPT-5.4 (via an
OpenAI-compatible proxy), DeepSeek (V4 Pro). Development tooling:
Claude Code (Anthropic).
