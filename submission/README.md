# IST Submission Package

Generated artifacts from Stage 5 FINALIZE of the academic-pipeline workflow.
Source markdown: `论文初稿P2_EN.md` (commit history visible via `git log`).

## Files

| File | Purpose |
|---|---|
| `p2_ist.tex` | Elsevier `elsarticle` LaTeX source (12pt review mode, authoryear citations) |
| `p2_ist.pdf` | First-pass review PDF (124 pages, ~380 KB, xelatex-compiled, zero missing glyphs) |
| `p2_ist.docx` | Pandoc DOCX (intermediate; useful for reviewer track-changes / non-LaTeX collaborators) |

## Build

```bash
# 1. Generate LaTeX + DOCX from the markdown source
bash scripts/build_ist_submission.sh

# 2. (One-time) place elsarticle.cls + .bst from CTAN into a project-local texmf:
#    The repo doesn't ship elsarticle.cls; download from https://ctan.org/pkg/elsarticle
mkdir -p submission/texmf/tex/latex/elsarticle
# unzip elsarticle.zip from CTAN; latex elsarticle.ins to materialize the .cls
cp /path/to/elsarticle/{elsarticle.cls,elsarticle-num.bst} submission/texmf/tex/latex/elsarticle/

# 3. Postprocess Unicode → LaTeX math/symbol commands
.venv/bin/python scripts/postprocess_unicode.py

# 4. Compile (run twice for cross-references)
cd submission
TEXINPUTS=./texmf/tex/latex/elsarticle:: \
BSTINPUTS=./texmf/tex/latex/elsarticle:: \
xelatex -interaction=nonstopmode p2_ist.tex
TEXINPUTS=./texmf/tex/latex/elsarticle:: \
BSTINPUTS=./texmf/tex/latex/elsarticle:: \
xelatex -interaction=nonstopmode p2_ist.tex
```

## Submission target

*Information and Software Technology* (IST) — Elsevier journal.
Submission window: 2027 Q3 (per `论文初稿P2_EN.md` line 23).

## Tooling notes

- **xelatex** is required (the pipeline uses Unicode characters in the body).
- **tectonic** is the academic-pipeline default but not installed locally; xelatex is the substitute.
- **Fonts**: Times New Roman (English main) + Menlo (monospace). Greek letters and math operators are wrapped in `$...$` by `scripts/postprocess_unicode.py`.

## Author placeholder

The `\author{}` block in `p2_ist.tex` contains placeholders. Update before
submission with real author names + affiliations + emails.
