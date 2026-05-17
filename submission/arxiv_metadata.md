# P2 — arXiv Submission Metadata

Ready-to-paste fields for the arXiv submission form (https://arxiv.org/submit).

## 1. Title

```
A semantic mutation metric for metamorphic relation adequacy in scientific computing programs
```

Length: 95 chars. arXiv limit: 240 chars. ✓

## 2. Authors

```
Meng Li (1,2,3), Xiaohua Yang (1,2,3), Jie Liu (1,2,3), Shiyu Yan (1,2,3)
```

Three shared affiliations (numbered for arXiv):
1. School of Computing, University of South China, Hengyang, 421001, China
2. Hunan Engineering Research Center of Software Evaluation and Testing for Intellectual Equipment, Hengyang, 421001, China
3. CNNC Key Laboratory on High Trusted Computing, Hengyang, 421001, China

Corresponding author: Meng Li (mlemon@usc.edu.cn)

## 3. Abstract (condensed for arXiv, ≤ 1920 chars)

**Char count: 1893 (within limit; structured Context/Objective/Method/Results/Conclusion preserved)**

```
Context. Metamorphic Testing addresses the test-oracle problem in scientific computing, but classical Mutation Score operates on syntactic AST mutations and misses domain semantics.

Objective. We propose the Semantic Mutation Score (SMS), built on five domain-semantic operators (Conservation Erosion, Operator Substitution, Hyperparameter, Trajectory Flip, Structural Injection). SMS degenerates almost everywhere to MS in a characterised limit, so any SMS-based conclusion remains consistent with prior mutation-testing literature in the classical regime.

Method. A 12-PUT x 5-MP design over four single-output float-to-float classes (numeric, probabilistic, surrogate, machine-learning) is paired with a three-layer attribution classifier separating true semantic faults from tolerance, OOD, statistical, and artefact categories. A same-source / cross-source ablation under an identical prompt isolates the LLM-source-diversity contribution. LLM-generated mutants are compared against a default-configuration cosmic-ray syntactic pool at the AST-normalised level.

Results. The pre-registered large-effect threshold for Cliff's delta is not met under the point-estimate criterion; the observed effect lies in the medium-effect range. Cross-source pooling under an identical prompt does not appreciably shift delta, indicating that LLM identity is not the lever within this design. AST-level overlap between LLM-generated and default cosmic-ray syntactic mutants is small; the Hyperparameter, Structural Injection, and Trajectory Flip classes are unreachable under default first-order syntactic configurations.

Conclusion. SMS is a backward-compatible adequacy metric for domain-semantic metamorphic-relation sets in scientific computing. The first-order unreachability evidence is independent of the effect-size question.
```

## 4. Comments

```
Submitted to Information and Software Technology (IST), Elsevier. Manuscript: 93 pages in elsarticle review mode (12pt double-spaced, ~28-35 pp typeset). Supplementary code and 12-PUT pool at https://github.com/meng004/P2-Semantic-Mutation (replace placeholder with real URL once published).
```

## 5. Categories

| Type | arXiv code | Reason |
|---|---|---|
| **Primary** | `cs.SE` | Software Engineering (metamorphic testing, mutation testing adequacy) |
| Cross-list | `cs.LG` | LLM-source-diversity ablation + machine-learning PUT class |

## 6. License

`CC BY 4.0` (recommended for preprints; compatible with subsequent IST submission per Elsevier preprint policy)

## 7. MSC / ACM CCS Classification

| System | Code | Topic |
|---|---|---|
| ACM CCS 2012 | `D.2.5` | Testing and Debugging |
| ACM CCS 2012 | `D.2.8` | Metrics (semantic mutation adequacy) |

## 8. Source tarball

P2 uses `elsarticle.cls` (Elsevier) and an inline plain-text APA bibliography (no separate .bib). Build with:

```bash
cd submission/
TEXINPUTS=./texmf//: xelatex -interaction=nonstopmode p2_ist_final.tex
TEXINPUTS=./texmf//: xelatex -interaction=nonstopmode p2_ist_final.tex
# No bibtex pass needed (inline APA bibliography)
tar czf p2_arxiv_v1.tar.gz \
    p2_ist_final.tex \
    texmf/ \
    ../figs/fig*.png
```

arXiv expects: one main `.tex` file + all `.sty` files (under `texmf/`) + figures. Since P2's bibliography is inline plain-text APA (no `\bibliography{...}`), no `.bbl` is needed.

## 9. arXiv submission workflow

Same as NOETHER (see `MR元模式/arxiv/arxiv_metadata.md` §9). Endorsement-once-per-arXiv-account; if NOETHER is submitted first and granted, P2 inherits author endorsement.

## 10. Compliance verification

- [x] Abstract ≤ 1920 chars (1893) ✓
- [x] Title ≤ 240 chars (95) ✓
- [x] Author block named (Meng Li, USC, mlemon@usc.edu.cn) ✓
- [x] Source compiles clean (xelatex × 2, 0 LaTeX warnings) ✓
- [ ] Em-dash audit on `.tex`: 1 hit in `%` comment at L4 — harmless but to scrub ⚠
- [x] 0 undefined references, 0 multiply-defined labels ✓
- [x] No `\bibliography{}` — inline APA only ✓
- [ ] Sensitive-info scan (`grep -lE "sk-|/Users/"`) → 0 hits in `.tex` ⚠ user verification needed
- [x] Highlights ≤ 5 bullets × 85 chars (IST hard cap, already verified for IST submission) ✓

## 11. Pre-submission cleanup (low-priority nits)

Per the earlier readiness scan:

1. `submission/p2_ist_final.tex:4` — em-dash inside `%` comment line. Replace `—` with `-` or remove the comment line.
2. `submission/cover_letter_final.md` — 9 em-dashes in markdown source. Cover letter is submitted as `.pdf`, so verify the rendered PDF does not carry em-dashes (the `.md` is internal).
3. `docs/STATE.md:28` — §6.5.2 wording fix flagged "pending commit" per round-9 state file. Confirm landed before arXiv tarball is bundled.

These are not arXiv-blocking. They are housekeeping for the parallel IST submission.
