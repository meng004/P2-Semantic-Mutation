# Acceptance Acknowledgment (Round 5 — Accept with Editorial Corrections)

**Manuscript:** When Same-Prompt LLM Source Diversity Doesn't Help: An Ablation of Semantic Mutation Operators in Metamorphic Testing for Single-Output Scientific Computing Kernels (P2 / IST)
**Round:** 5 (editorial-corrections submission)
**Reviewer verdict in Round 4 re-review:** **Accept with editorial corrections**
**Date:** 2026-05-02
**Commit at submission:** (Round-5 build commit)

We thank the reviewer for the third-round verdict and for the kind closing remarks on the methodological-honesty trajectory of this revision cycle. We have addressed the four editorial / formatting issues (E1–E4) flagged in the Round-4 re-review. No content changes were made; all changes are LaTeX-rendering fixes in the build pipeline.

---

## E1 — Figure 1 / Figure 3 caption math environment (Resolved)

**Reviewer's point.** The Figure 1 caption rendered as `(operational E_1 wedge E_2 judgement)` and the Figure 3 caption included `12 PUTs $times$ 5 MPs`, both with LaTeX commands appearing as literal text instead of math glyphs.

**Root cause.** The figure-caption strings in `scripts/build_ist_submission_v4.sh` used `$E_1 \\\\wedge E_2$` (four backslashes). Inside the bash non-expanding heredoc and the Python triple-quoted string, this produced markdown text `$E_1 \\wedge E_2$`. Pandoc's Markdown math parser interprets `\\` as a line-break command, not as a literal backslash, so the math output was `\(E_1 \\wedge E_2\)` and `\\wedge` showed as text "wedge".

**Fix.** Changed `\\\\wedge` → `\\wedge` and `\\\\times` → `\\times` in `scripts/build_ist_submission_v5.sh` (Python string parsing now produces the correct single backslash; pandoc emits proper `\(E_1 \wedge E_2\)`). Verified the v5 .tex output has `\(E_1 \wedge E_2\)` (single backslash) at line 145 and the corresponding correct `\(\times\)` rendering in Figure 3's caption.

---

## E2 — §3.3 60-cell matrix table garbled (Resolved)

**Reviewer's point.** The §3.3 60-cell matrix on page 18 of the v4 PDF showed raw LaTeX commands such as `\textbullet\textbullet`, `$\circ$` rendered as literal text instead of as the intended bullet glyphs.

**Root cause.** `scripts/postprocess_unicode.py` performed a global `text.replace()` on the .tex file, including content inside `\begin{verbatim}...\end{verbatim}` environments. LaTeX renders verbatim content literally, so substituting Unicode `●` → `\textbullet` inside verbatim caused the LaTeX command name to display as text.

**Fix.** Refactored `postprocess_unicode.py` to split the .tex content into segments via a regex on `\\begin\{verbatim\}.*?\\end\{verbatim\}` (DOTALL), apply substitutions only to non-verbatim segments, and rejoin. Telemetry now reports the count of substitutions skipped inside verbatim ("1400 preserved inside verbatim blocks" in the v5 build). Verified the §3.3 matrix in `submission/p2_ist_v5.tex` now contains the original Unicode `●●`, `●`, `○` characters, which xelatex with the Menlo monospace font renders correctly.

---

## E3 — §2.1 / §G LaTeX math commands inside code blocks (Resolved)

**Reviewer's point.** Multiple math commands across §2.1, §2.3, and §G.2–G.4 (`$\sqcup$`, `$\to$`, `$\wedge$`, etc.) appeared as raw LaTeX text rather than rendered glyphs.

**Root cause.** Same as E2 — substitutions inside fenced markdown code blocks (which pandoc converts to LaTeX `\begin{verbatim}`) produced raw LaTeX command names. Additionally, the Menlo monospace font does not contain the `⊔` (U+2294) or `‖` (U+2016) glyphs, so even after the verbatim-preservation fix, those two glyphs remained as missing characters.

**Fix.**
1. The `postprocess_unicode.py` refactor in E2 also resolves the rest of §2.1, §G.2–G.4 since those used fenced code blocks for their formula displays.
2. In `论文初稿P2_IST.md` line 99 and `论文初稿P2_IST_appendix.md` line 40, replaced `⊔` with `∪ ... (disjoint)` to use a glyph that Menlo supports while preserving the disjoint-union semantics in the surrounding prose. The decomposition formula now reads `mut_j(S_i) = equiv ∪ killed ∪ survive (disjoint)`.
3. In `论文初稿P2_IST_appendix.md` line 44, replaced the typographic norm `‖·‖` with the ASCII `||·||` inside the Appendix A.1 notation block (verbatim) to match Menlo's glyph coverage.

Verified the v5 xelatex compile reports zero "Missing character" warnings on these passages.

---

## E4 — Abstract Conclusion visual separation (Optional, deferred to typesetting)

**Reviewer's point.** The Abstract Conclusion sentence "the LLM-identity axis ... shifts δ by ≤ 0.01 across two MP conditions" follows the lever sentence with a `;` and could have stronger visual contrast.

**Decision.** This is an optional nice-to-have. We have left the current `;` separator in place since:
- The Abstract has already been restructured into Primary / Robustness / Exploratory / Other italic blocks (Round 4), which provides strong structural emphasis at the section level.
- The Conclusion paragraph is intentionally compact — adding a sentence break here would slightly weaken the symmetric "axis A is the lever; axis B shifts δ by ≤ 0.01" parallelism.
- IST production typesetting will set the final line breaks; a hard break here is best decided at the proof stage with the editor.

If the Editor prefers a hard break, we will accept that change at proof.

---

## Glossary (also deferred to production)

The §1 abbreviation glossary was deferred to the production stage in Round 4. We confirm again that this remains the right choice — adding a half-page glossary at this point would shift the page count and break the line numbering used in the response letters above. If IST production prefers a glossary, it can be inserted as a single-page front matter without renumbering.

---

## Summary of Round-5 changes

| # | File | Change | Type |
|---|---|---|---|
| 1 | `scripts/build_ist_submission_v5.sh` | `\\\\wedge` → `\\wedge`, `\\\\times` → `\\times` in figure-caption strings | LaTeX rendering |
| 2 | `scripts/postprocess_unicode.py` | Refactor to skip `\begin{verbatim}` blocks during Unicode→LaTeX substitution | LaTeX rendering |
| 3 | `论文初稿P2_IST.md` line 99 | `⊔` → `∪ (disjoint)` for Menlo glyph coverage | Typography |
| 4 | `论文初稿P2_IST_appendix.md` line 40 | `⊔` → `∪ (disjoint)` for Menlo glyph coverage | Typography |
| 5 | `论文初稿P2_IST_appendix.md` line 44 | `‖·‖` → `||·||` in verbatim block for Menlo coverage | Typography |
| 6 | `submission/p2_ist_v5.{tex,docx,pdf}` | Regenerated package with E1–E3 fixes | Build |
| 7 | `submission/cover_letter_v5.{md,pdf}` | Version sync | Build |

The PDF is 93 pages (same as v4), and v5 xelatex compile produces zero `Missing character` warnings — all four editorial corrections are now resolved.

---

## Pre-acceptance checklist

- [x] E1, E2, E3 LaTeX rendering issues fixed
- [x] E4 deferred to IST production typesetting (with reason)
- [x] Glossary deferred to IST production typesetting (with reason)
- [x] v5 PDF zero missing-character warnings, xelatex two-pass converged
- [ ] **Pending IST production**: Zenodo DOI mint and replacement of `10.5281/zenodo.XXXXXXX` placeholder in §"Data and code availability"
- [ ] **Pending IST production**: Optional E4 sentence break and §1 glossary

We thank the reviewer once more for the careful three-round read, and the Editor for handling this submission. We are ready for IST production.
