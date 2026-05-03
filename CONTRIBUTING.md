# Contributing

Thanks for your interest in this repository. It is the replication
artefact for one paper (P2 Semantic Mutation Score audit), so
contribution channels are scoped accordingly.

---

## What this repository is — and is not

- It **is** a replication bundle for the paper
  "When Same-Prompt LLM Source Diversity Doesn't Help" (under
  review at *Information and Software Technology*, 2026).
- It **is not** a general-purpose mutation-testing framework. The
  code is tuned to the 12 PUTs × 5 MPs × 60-cell experimental
  design described in the paper.
- A successor framework with broader PUT coverage and an industrial
  Java/C++ port is planned as **P3** (separate repository, separate
  paper). Issues that point in that direction are welcome but will
  be marked as `out-of-scope-for-P2` and tracked toward P3.

---

## What we welcome

| Channel | Use it for |
|---|---|
| **GitHub issues** | Replication failures, observed-vs-paper number mismatches, broken commands in `REPRODUCIBILITY.md`, factual errors in the paper, suggested clarifications |
| **Pull requests** | Small fixes to documentation, scripts, or test cases; `requirements-frozen.txt` adjustments for newer Python; new tests for existing modules |
| **Email to maintainer** (`mlemon@usc.edu.cn`) | Substantive review, collaboration on follow-up work (P3+), invited talks, dataset-licensing questions |

---

## What is intentionally not in scope

- Alternative LLM providers / mutation operators / scoring metrics
  beyond what the paper analyses. These belong to a follow-up paper,
  not a patch on this one.
- Refactors that change the SSOT outputs in `data/results/`.
  Numbers in the published paper are tied to a fixed commit; we
  cannot accept changes that alter them retroactively.
- Style-only refactors of the manuscript (`论文初稿P2_IST.md` and
  appendix). The manuscript is locked once the paper is in press.

---

## Replication-report issues — please include

When opening an issue about replication:

1. The exact command you ran (copy-paste from your terminal).
2. The output you got (last 50 lines).
3. `python --version`, `pip freeze | head -20`, and OS / arch
   (`uname -a`).
4. Whether you used Path A (cache replay) or Path B (re-LLM),
   and whether `pytest -q` reports 116 passed before the failing
   step.

Issues without these usually require a back-and-forth that delays
resolution.

---

## Pull-request workflow

Because this is a paper-tied artefact, PRs go through one extra
step beyond the usual:

1. **Fork and branch.** Branch name: `fix/<short-slug>` or
   `docs/<short-slug>`.
2. **Run the test suite.** `PYTHONPATH=src .venv/bin/pytest -q`.
   It must report `116 passed` before and after your change.
3. **Verify SSOT integrity** if you touched anything under
   `src/p2/stats/` or `scripts/compute_*`:
   `PYTHONPATH=src SMS_VERSION=v4 P2_PRIMARY_VERSION=v3b .venv/bin/python scripts/build_paper_numbers.py`
   The diff against `data/results/paper_numbers_v4.json` should be
   empty.
4. **Open the PR** with a description that lists:
   - The motivation (linked issue, if any).
   - What you changed and why.
   - Whether `pytest` and SSOT integrity passed locally.
5. **Review.** The maintainer will respond within ~5 business days.
   Substantive PRs may need the paper's data custodian to co-sign
   if they touch `data/`.

---

## Code style

- Python: follow the existing style (PEP 8 with 100-char lines).
  No formatter is enforced, but consistency with neighbouring code
  is expected.
- Commit messages: imperative mood ("add X", "fix Y", not "added"
  or "fixed"). Reference an issue or paper section when relevant.
  Phase markers (`phase-D(...)`) are reserved for the maintainer's
  revision pipeline; please don't reuse them in external PRs.
- Documentation: prefer Markdown. Chinese is acceptable for theory
  notes (`docs/theory/`), English for everything that ships in the
  replication bundle.

---

## Code of conduct

Be civil, be concrete, be cite-able. Drive-by complaints without a
reproducer are unlikely to get traction; a 10-line repro almost
always does.

---

## Licence summary

By contributing, you agree that your contribution is licensed under
the same terms as the rest of the repository:

- Software (`src/`, `scripts/`, `tests/`): MIT.
- Data (`data/`, `figs/`, `figures/`): CC-BY-4.0.
- Manuscript (`*.md`, `submission/`): authors retain copyright;
  external rewrites are *not* accepted into the publication path.
