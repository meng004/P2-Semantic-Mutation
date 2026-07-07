# U2 Reference Verification: Foundations and BibTeX Keys

Date: 2026-07-07 Asia/Shanghai.

Scope: paper-search MCP verification for the `defect4mr2026` entry, reviewer-named foundational references, and hash-key replacement in `source/references.bib`.

| Key | Status | Evidence | Action |
|---|---:|---|---|
| `defect4mr2026` | △ | `paper-search` query for `defect4MR metamorphic testing benchmark` across Crossref, Semantic Scholar, OpenAlex, arXiv, and Google Scholar did not return a formal publication record. | Kept as unpublished `@misc` with no DOI. |
| `chen2018metamorphic` | ✓ | Crossref DOI lookup `10.1145/3143561`: ACM Computing Surveys 51(1), 1--27. | Added as `@article`. |
| `segura2016survey` | ✓ | Crossref DOI lookup `10.1109/TSE.2016.2532875`: IEEE TSE 42(9), 805--824. | Added as `@article`. |
| `liu2014alleviate` | ✓ | Crossref DOI lookup `10.1109/TSE.2013.46`: IEEE TSE 40(1), 4--22. | Added as `@article`. |
| `kanewala2014scientific` | ✓ | Crossref DOI lookup `10.1016/j.infsof.2014.05.006`: Information and Software Technology 56(10), 1219--1232. | Added as `@article`. |
| `budd1982correctness` | ✓ | Crossref DOI lookup `10.1007/BF00625279`: Acta Informatica 18(1), 31--45. | Added as `@article`. |
| `demillo1978hints` | ✓ | Crossref DOI lookup `10.1109/C-M.1978.218136`: Computer 11(4), 34--41. | Renamed existing hash-key entry and normalized author/page fields. |

Hash-key changes:

- `8d7f3a3b7231100756a729aba720f4f81bcf5a8b` -> `li2026sms`
- `ecf4ccd0f2897516b0205a4b1e35ea81b68aa277` -> `li2026minmrcomplete`
- `91b1f655c6e42c02eed722b213e3c03df2e2d75a` -> `demillo1978hints`

Sanity checks:

- Old hash keys above have no residual occurrence in `source/main.tex`, `source/supplementary.tex`, or `source/references.bib`.
- New keys are cited where needed so the foundational references can enter the generated bibliography.
