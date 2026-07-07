# Incremental Reference Verification: defect4mr2026

Date: 2026-07-07 Asia/Shanghai.

Scope: incremental check for the newly added `defect4mr2026` BibTeX entry.
This file does not replace a full entry-by-entry reference audit of the complete
TOSEM bibliography.

| Key | Status | Evidence | Action |
|---|---:|---|---|
| `defect4mr2026` | △ | `paper-search` query for `defect4MR metamorphic testing benchmark` across Crossref, Semantic Scholar, OpenAlex, arXiv, and Google Scholar returned no formal `defect4MR` publication record. Local project sources define `defect4MR` as an unpublished benchmark-design artifact under `research/defect4MR_*`. | Keep as `@misc` with `howpublished = {Unpublished project design note and artifact specification}` and no DOI. Replace with formal metadata if a public DOI, arXiv ID, or artifact URL is minted. |

Build/citation sanity:

- `source/references.bib` and generated `submission/TOSEM_fastimpact_20260707/references.bib` both contain `@misc{defect4mr2026}`.
- The generated `main.tex` and `supplementary.tex` do not currently cite `defect4mr2026`, so the entry is available in the BibTeX database but does not appear in `main.bbl` or `supplementary.bbl`.
- Final logs after the post-build double `xelatex` pass contain no `Warning--I didn't find a database entry`, no undefined citation warning, and no `LaTeX Error`.
