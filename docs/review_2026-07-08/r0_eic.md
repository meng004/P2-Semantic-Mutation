# EIC venue-fit screening — simulated review 2026-07-08 (R0)

Venue: ACM TOSEM, Journal-First / Fast-Impact track.
Package screened: `submission/TOSEM_fastimpact_20260707/` (main.tex + supplementary.tex +
cover_letter.md + declarations.md + references.bib + acmart.cls + ACM-Reference-Format.bst).
Cross-checked against authoring source `source/main.tex` and the prior round
`docs/review_2026-07-07/`.

All findings below were verified by reading the actual files, not the fix ledger.

---

## Verdict

**Return to authors / desk (not sendable to reviewers).** The scientific manuscript has
matured and several 2026-07-07 blockers are genuinely closed, but the TOSEM submission file
itself does **not compile**: `submission/TOSEM_fastimpact_20260707/main.tex` is a botched merge
of an acmart wrapper on top of the entire elsarticle authoring source, with two
`\documentclass`, two `\begin{document}`, a stray `\maketitle` mid-file, an uncommented preamble
fragment, and elsarticle-only environments. This is a hard build blocker that supersedes
everything else and is, mechanically, a **regression** relative to last round (where the file
was at least a clean elsarticle build). It cannot go to review until the package produces a
genuine acmart PDF.

## Score

**3 / 10** for the current *submittable state* (desk blocker: file does not build; ACM-format /
page-eligibility claim unverifiable).
Underlying manuscript, were it correctly built, would screen around **5–6 / 10** (Major
Revision: four pre-registered hypotheses fail, headline rests on a construct-separation
reframing) — but that judgment cannot be reached at desk until the package compiles.

---

## Blockers (desk / format — must clear before review assignment)

### B1. The submitted `main.tex` does not compile — fatal, and worse than last round.
`submission/TOSEM_fastimpact_20260707/main.tex` was produced by prepending an acmart
front block (lines 1–104: `\documentclass[manuscript,screen,review]{acmart}` at line 3,
`\begin{document}` at line 98, an acmart `\begin{abstract}` at 100–102, `\maketitle` at line 104)
onto the **complete, unmodified** elsarticle authoring source (the tail begins at line 106 and
is byte-identical to `source/main.tex` from its line 6 onward). Consequences, all verified:
- **Two `\documentclass`**: acmart at line 3, `\documentclass[review,12pt,authoryear]{elsarticle}`
  at **line 110** — i.e. a `\documentclass` *after* `\begin{document}`. This alone is a fatal
  "Can be used only in preamble" error.
- **Two `\begin{document}`**: line 98 and line 189.
- **`\maketitle` at line 104** fires before the real body, then a second full preamble
  (lines 112–189: `\usepackage{...}`, `\setmainfont`, `newunicodechar`, ...) sits illegally
  inside the document.
- **Uncommented preamble text**: lines 106–108 ("by venues/<venue>/build.py (TOSEM: acmart 2.19).
  % This work has never been submitted to IST; ...") lost their leading `%` on line 106 and would
  be typeset / error.
- **elsarticle-only frontmatter under acmart**: `\begin{frontmatter}`…`\end{frontmatter}`
  (lines 191–245), `\begin{highlights}` (line 223), `\begin{keyword}` (line 241) — none defined
  in acmart.

No TeX engine is installed in this environment (compile attempt returned exit 127), so I could
not produce the error log, but the structural facts above are dispositive: a `\documentclass` at
line 110 after `\begin{document}` at line 98 cannot build under any engine. The cover letter's
"40 pages ... in the ACM manuscript-review format" (cover_letter.md, Length statement) therefore
describes a document that does not exist as a compilable artifact.

**Required fix:** regenerate `main.tex` as a single, clean acmart document — strip the entire
elsarticle preamble/frontmatter/highlights/keyword tail, keep exactly one `\documentclass`, one
`\begin{document}`, one abstract, and let acmart emit the title block via `\maketitle`.

### B2. Duplicate and contradictory frontmatter; a flagged minor item resurfaced.
Because of B1 the file carries **two abstracts**: the acmart one at lines 100–102 and a second
IST-structured `\begin{abstract}` (Context/Objective/Method/Results/Conclusion) at lines 233–239,
plus an Elsevier `\begin{keyword}` block at lines 241–243 that **still lists "Cliff's delta" as a
keyword** — the exact item flagged as Minor-5 on 2026-07-07. (The acmart `\keywords{}` at line 96
is clean and no longer lists it, but the leftover elsarticle keyword env was never deleted.)
Reviewers/copyedit cannot accept a manuscript with two abstracts and a statistic as a keyword.

### B3. Package ambiguity — two candidate main files, neither a valid TOSEM manuscript.
The package ships both the broken `main.tex` and `acmsmall-submission.tex`, but the latter is the
**untouched ACM sample template** (`\documentclass[acmsmall,screen,anonymous,review]{acmart}`,
docstrip header "generated with the docstrip utility", sample rights/copyright year 2018). It is
not this paper. A screener cannot tell which file is the manuscript of record, and neither one is
a compilable, correctly-formatted TOSEM submission. The task brief calls this the "acmsmall
build," but no acmsmall build of the actual paper exists in the package.

### B4. ACM-format page-eligibility for Fast-Impact is unverifiable.
Fast-Impact hinges on the ≤45-page (text before bibliography) threshold. cover_letter.md
(Length statement) and declarations.md (Length) both assert "40 pages ... in ACM
manuscript-review format," but the only compiled PDF anywhere in `submission/` is
`p2_ist_final.pdf` — the **Elsevier/IST** build — and `p2_ist_final.docx`; there is no
ACM-rendered PDF. Given B1, the ACM page count is not just unverified but currently
unproducible. Eligibility cannot be certified at desk.

---

## Resolved since 2026-07-07 (verified in the actual files — credit where due)

- **Supplementary material is now in the package.** `supplementary.tex` (1,513 lines,
  Appendices A–I) ships with the submission; `readme.txt` describes it. The load-bearing
  Hoeffding-style false-equivalence bound the main text points to is present
  (supplementary.tex line 1130, "Hoeffding-style false-equivalence bound (referenced by ...)").
  Last round's Blocker 3 is closed.
- **Simultaneous-submission ambiguity is addressed by explicit statements.** cover_letter.md now
  carries a journal-first novelty statement, discloses arXiv:2605.17437, and states "The work is
  not under simultaneous archival review elsewhere"; declarations.md repeats the prior-version
  disclosure. The source comment (main.tex lines 6–7 / source lineage) asserts the work was never
  submitted to IST. Last round's Blocker 2 is answered at the declaration level (a real board
  would still want a signed confirmation, but it is no longer an ambiguity).
- **CCS concepts added**: `\ccsdesc[500]{... Software testing and debugging}` and
  `\ccsdesc[300]{... Software verification and validation}` at lines 93–94, with the CCSXML block
  at 78–91. Last round's Minor-5 "CCS absent" is closed (in the acmart block).
- **`\subsection{References}` bug gone**: the bibliography is now emitted via
  `\bibliographystyle{ACM-Reference-Format}` + `\bibliography{references}` at end of file, not as
  a Conclusion subsection.
- **Declarations now list both DOIs** (10.5281/zenodo.20250664 and 10.5281/zenodo.21203424) —
  declarations.md, Data and Artifact Availability. Last round's Minor-2 closed.
- **Abstract over-claim softened**: both abstract texts now say aggregate kill-rate, semantic
  alignment, and real-defect detection are "related but distinct constructs ... supporting the
  paper's construct separation" (lines 101, 237), not "confirming"/"opposite orders." Last
  round's Major-1 wording concern is materially improved.

## Major concerns (carry to reviewers once the package builds — not desk-resolvable)

### M1. Auto-generated 40-hex citation keys persist (last round EIC-M4 / ledger U2, still open).
13 distinct 40-character hash keys are still cited in `main.tex` (e.g.
`\citet{7a6c280d9584691800e71876c716ea229335abeb}` line 153, plus
`d7c38286...`, `302e9d25...`, `c03829bd...`, and ~9 more), out of 61 `\cite*` commands total.
They *do* resolve to real, checkable entries in references.bib (`7a6c280d...` = Clark, Dan &
Hierons, "Semantic Mutation Testing," 2010; `d7c38286...` = Jia & Harman survey; `302e9d25...` =
Al Blwi et al., "Semantic Coverage," 2023), so this is not a fabrication risk — but ACM
copyediting will bounce unreadable machine keys, and it signals a pipeline-generated bib
(references.bib contains 197 hash-keyed entries) that has not been curated. Rename to
human-readable keys in the ACM rebuild.

### M2. Headline still rests on a construct-separation reframing after all four hypotheses fail.
Both abstracts (lines 101, 237) concede the "pre-registered instantiability, effect-size,
cross-class-consistency, and attribution thresholds are not met," and the central positive claim
is the industrial arm's construct separation. The reframing from dominance to
diagnostic/construct-level is honest and consistently maintained, but whether "we delimit
boundaries" + an industrial construct-separation result clears TOSEM's contribution bar is a
genuine reviewer question that should be flagged in the invitation, not resolved at desk.

### M3. Salami-slicing boundary with the companion benchmark paper needs reviewer visibility.
cover_letter.md (Related-work disclosure) states the industrial arm draws result-level statistics
from a separately archived dataset (Zenodo 10.5281/zenodo.21203424) intended for a separate
benchmark/artifact paper. The boundary is drawn carefully, but the 34-case arm is the only
non-author-written evidence, so reviewers must be given the DOI and asked to check for overlap.

## Minor items

- **Results redundancy not fully consolidated** (last round EIC-M3 / ledger U13): "singular /
  mixed-effects" language still appears ~11 times across `main.tex`. A Fast-Impact length pass
  should still merge the mixed-effects-singularity and repeated-verdict passages.
- **Supplementary internal inconsistency: 12 vs 13 default operators.** supplementary.tex line 435
  ("All 12 default classes remain ...") vs line 488 ("cosmic-ray's 13 default operators
  (cosmic-ray 8.4.6, ...)"). The 12/13 reconciliation the ledger claimed (item 29) did not fully
  propagate into the supplement.
- **acmart title-block vs elsarticle author list**: the acmart block (lines 30–45) names only
  "Meng Li"; the buried elsarticle frontmatter (lines 195–206) lists four authors (Li, Yang, Liu,
  Yan). When B1 is fixed, confirm the intended author set and ORCIDs in the single acmart block.

---

## Distance-to-stable-accept summary

Three tiers separate this package from an accept-with-minor-revision decision:

1. **Desk blockers (mechanical, mandatory, ~0.5 day):** B1–B4. Produce one genuinely acmart-
   compiled `main.tex` — a single `\documentclass{acmart}`, no elsarticle
   preamble/frontmatter/highlights/keyword remnants, one abstract, "Cliff's delta" removed from
   any keyword list; drop or clearly quarantine the `acmsmall-submission.tex` sample; and attach
   the compiled ACM PDF with a verified ≤45-page count. Until this is done the paper is not
   sendable to reviewers, full stop.

2. **Contribution-bar review (Major-Revision material, reviewer-owned):** M2 and M3. The
   four-failed-hypotheses + construct-separation framing and the companion-dataset boundary are
   legitimate but reviewable; they belong in the review, flagged in the invitation.

3. **Polish (fixable during revision):** M1 (rename 13 hash citation keys), Results-redundancy
   consolidation, supplement 12-vs-13 operator inconsistency, author-list reconciliation.

Bottom line: the *science* moved forward this round (supplement included, over-claims softened,
declarations complete), but the *deliverable regressed* — the submitted TeX went from a clean
elsarticle to a non-compiling acmart/elsarticle hybrid. One disciplined build pass converts this
from desk-reject to a reviewable Major-Revision manuscript; no amount of reviewer effort can
proceed before that pass.
