# Submission Packages

## Authoritative package: TOSEM regular research paper

`TOSEM_regular_20260710/` (and `TOSEM_regular_20260710_clean.zip`) is the
single authoritative submission package. It is generated from
`source/main.tex` + `source/supplementary.tex` by:

```bash
python3 venues/tosem/build.py --track regular --date 20260710 --force
```

| Item | Value |
|---|---|
| Venue / track | ACM TOSEM, Journal-First regular research paper |
| Title | A Semantic Mutation Metric for Metamorphic-Relation Adequacy for Scientific-Computing Kernels |
| Main PDF | 50 pages (narrative body ends on page 47) |
| Supplementary PDF | 37 pages (Appendices A-K) |
| Cover letter / declarations | `cover_letter.md`, `declarations.md` (copied from `venues/tosem/`) |
| Build engine | tectonic (xelatex+bibtex used when available); zero "Missing character" warnings |

Earlier packages (`TOSEM_fastimpact_20260709/`, `TOSEM_regular_20260709/`)
were removed from the working tree; git history preserves them. The
Fast-Impact track is no longer targeted.

## Historical IST-era artifacts

`p2_ist_final.{tex,pdf,docx}` and the `p2_arxiv_v*.tar.gz` bundles are the
earlier IST/arXiv lineage of the single-study manuscript, retained for
provenance only. They are superseded by the four-study TOSEM package above.
