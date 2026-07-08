# T6 bibliography fix — findings (JOB 1: two R2 must-cites)

Reviewer anchor: `docs/review_2026-07-08/r2_domain.md` §1, items 1–2 (main.tex:88–105).
R2 flags two missing 2022–2025 LLM-mutation must-cites: **µBERT** (first PLM-driven
mutant generator, ancestor of the LLM-mutant lineage) and **Meta's ACH** (industrial
mutation-guided LLM test generation).

Both entries have been **appended** to `source/references.bib` (the source-of-truth bib;
`venues/tosem/build.py:509` copies this file verbatim into the disposable submission
package, so no second bib needs editing).

---

## Verified record 1 — µBERT

```bibtex
@inproceedings{degiovanni2022mubert,
  author = {Renzo Degiovanni and Mike Papadakis},
  title = {{$\mu$BERT}: Mutation Testing using Pre-Trained Language Models},
  booktitle = {2022 IEEE International Conference on Software Testing, Verification and Validation Workshops (ICSTW)},
  pages = {160--169},
  year = {2022},
  doi = {10.1109/ICSTW55395.2022.00039},
  publisher = {IEEE}
}
```

- Title: µBERT: Mutation Testing using Pre-Trained Language Models
- Authors: Renzo Degiovanni, Mike Papadakis
- Venue: 15th IEEE ICST Workshops 2022 (Mutation workshop), Valencia, Spain
- Pages: 160–169; Year: 2022
- DOI: `10.1109/ICSTW55395.2022.00039` (IEEE published version — chosen as canonical)
- arXiv preprint: 2203.03289 (same title/authors)

Canonical choice: the peer-reviewed IEEE ICSTW 2022 version is cited (with page range
and IEEE DOI) rather than the arXiv preprint, matching the bib's convention of citing
published venues where available.

## Verified record 2 — Meta ACH

```bibtex
@inproceedings{foster2025ach,
  author = {Christopher Foster and Abhishek Gulati and Mark Harman and Inna Harper and Ke Mao and Jillian Ritchey and Herv{\'e} Robert and Shubho Sengupta},
  title = {Mutation-Guided {LLM}-based Test Generation at Meta},
  booktitle = {Proceedings of the 33rd ACM International Conference on the Foundations of Software Engineering (FSE Industry)},
  year = {2025},
  doi = {10.1145/3696630.3728544},
  publisher = {Association for Computing Machinery},
  note = {Automated Compliance Hardening (ACH); also arXiv:2501.12862}
}
```

- Title: Mutation-Guided LLM-based Test Generation at Meta
- Authors: Christopher Foster, Abhishek Gulati, Mark Harman, Inna Harper, Ke Mao,
  Jillian Ritchey, Hervé Robert, Shubho Sengupta
- Venue: FSE 2025 (Industry track); System = **ACH (Automated Compliance Hardening)**
- Year: 2025; DOI: `10.1145/3696630.3728544` (ACM DL, resolves via doi.org)
- arXiv preprint: 2501.12862 (submitted 22 Jan 2025)

**First-author correction:** the task's suggested key `alshahwan2025ach` names the wrong
first author. The canonical *mutation-guided* ACH paper is **Foster et al. 2025**, not
Alshahwan. Alshahwan et al. is the *earlier, different* paper "Automated Unit Test
Improvement using LLMs at Meta" (TestGen-LLM, FSE 2024, DOI `10.1145/3663529.3663839`),
which is **not** mutation-guided. Because R2 explicitly asks for the "LLM-mutation /
mutation-guided" line, `foster2025ach` (Foster et al.) is the correct must-cite. If the
integration agent also wants the TestGen-LLM predecessor, add a separate
`alshahwan2024testgen` entry — but it is not the paper R2 flagged.

---

## Retrieval audit (CLAUDE.md §7 format)

paper-search MCP is **not available** in this session; per CLAUDE.md §7 the documented
fallback (WebSearch → WebFetch on authoritative pages) was used. No paper-search tool was
callable, so no `[tool A, tool B, tool C]` failure chain applies — the MCP is simply
absent from the toolset. No DOI was fabricated; every DOI below was read off an
authoritative page.

| Ref | Tool chain | Hit tool | Status |
|-----|-----------|----------|--------|
| Degiovanni & Papadakis µBERT (title/authors/arXiv) | WebSearch → WebFetch(arxiv.org/abs/2203.03289) | arXiv | ✓ |
| µBERT venue/pages/DOI | WebSearch(IEEE/ICSTW) → WebFetch(orbilu.uni.lu/handle/10993/51744) | ORBilu (Univ. Luxembourg IR) | ✓ DOI 10.1109/ICSTW55395.2022.00039, pp.160–169 |
| Foster et al. ACH (title/authors/arXiv) | WebSearch → WebFetch(arxiv.org/abs/2501.12862) | arXiv | ✓ |
| ACH ACM DOI/venue | WebSearch(FSE 2025) → WebFetch(doi.org/10.1145/3696630.3728544 → dl.acm.org) | doi.org 302 redirect confirms ACM DL resolution | ✓ (ACM DL body 403-blocked, but doi.org resolution + FSE 2025 programme page corroborate DOI + venue) |
| Alshahwan TestGen-LLM (to distinguish, NOT added) | WebSearch(FSE 2024) | ACM DL listing | △ context only — DOI 10.1145/3663529.3663839 |

Tools that failed / were degraded:
- `dl.acm.org` direct WebFetch → HTTP 403 (bot block); DOI confirmed instead via doi.org
  302 redirect target + the search-result title string and the FSE 2025 programme page.
- `dblp.org/pid/00/7677.html` WebFetch returned a truncated recent-only slice (µBERT not
  in the returned window); ORBilu supplied the authoritative ICSTW DOI/pages instead.

---

## Suggested citation-insertion points (main.tex) — DO NOT EDIT (integration agent applies)

The related-work LLM-mutation paragraph is **§(c) "LLM-generated mutants"** at
`main.tex:329–345` (survey block runs main.tex:299–408). Grep anchors:
`tip2025llmorpheus` (LLMorpheus) at main.tex:329–330; `humbatova2021deepcrime` at
main.tex:331; `dakhel2024llm` at main.tex:332; `papadakis2019advances` (survey) at
main.tex:311.

1. **µBERT (`degiovanni2022mubert`)** — insert at the *head* of §(c), main.tex:329, as the
   originator of the PLM/LLM-mutant lineage, before LLMorpheus. Suggested phrasing:
   "Pre-trained-language-model mutation begins with µBERT \citep{degiovanni2022mubert},
   which masks tokens and uses CodeBERT to synthesise mutants; \citet{tip2025llmorpheus}
   introduce LLMorpheus …" — i.e. prepend it to the existing sentence at main.tex:329–330.

2. **ACH / Foster (`foster2025ach`)** — two viable anchors; §(c) is preferred for the
   related-work engagement R2 asks for:
   - Primary: end of §(c), around main.tex:344–345, as the industrial-scale contrast:
     "At industrial scale, Meta's ACH \citep{foster2025ach} deploys mutation-guided
     LLM test generation to harden test suites against targeted faults on general
     software; the present paper instead measures MR adequacy on scientific kernels."
     (This directly answers R2's "distinguish scope" ask, main.tex:96–102.)
   - Alternative/secondary: the industrial-arm framing at main.tex:178–187, if the
     authors prefer to raise Meta where the industrial arm is introduced.

R2's one-sentence "distinguish scope" request (their object = test-suite hardening on
general software; ours = MR adequacy on scientific kernels) is satisfied by the ACH
insertion wording above.
</content>
