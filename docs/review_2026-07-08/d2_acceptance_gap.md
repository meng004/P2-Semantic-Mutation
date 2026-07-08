# Wave-D2 — Acceptance-Gap Assessment (post-fix re-score)

**Assessor role:** fresh, skeptical-but-fair TOSEM editorial-board read of the CURRENT state.
**Question:** how far is this from STABLE ACCEPTANCE (a Major→Minor→Accept trajectory with no
plausible rejection branch)?

**Package re-scored:** `submission/TOSEM_fastimpact_20260708/` (main.tex + supplementary.tex +
references.bib + cover_letter.md + declarations.md, acmart 2.19).
**Fix commits applied after the July-8 reviews:** `3014fa3` (Wave-A evidence artifacts),
`855df4a` (integrate evidence + close consistency ledger), `d7ecb56` (regenerate compilable
acmart package, verify page budget).
**Verification basis:** every closure below was checked against the *current* files on disk
(main.pdf = 46 pages, `\documentclass` count = 1, hash-key count = 0, etc.), not the fix memos.

---

## 1. Per-reviewer closure table (post-fix)

Evidence cites `submission/TOSEM_fastimpact_20260708/` unless noted.

### R0 — EIC venue-fit (July-8 score 3/10; underlying manuscript 5–6)

| ID | Item | Status | Evidence |
|---|---|---|---|
| B1 | main.tex non-compiling double-preamble acmart/elsarticle hybrid | **CLOSED** | `main.tex:3` single `\documentclass[manuscript,screen,review]{acmart}`; `\begin{document}` count = 1; frontmatter/highlights/keyword leftovers = 0; main.pdf compiles at 46pp |
| B2 | Two abstracts + "Cliff's delta" as keyword | **CLOSED** | single `\begin{abstract}` at `main.tex:100-102`; `\keywords{}` at `main.tex:96` clean (no statistic) |
| B3 | Package ambiguity; untouched `acmsmall-submission.tex` sample shipped | **CLOSED** | package dir ships only `main.tex`; no `acmsmall-submission.tex` present |
| B4 | ACM page-eligibility unverifiable | **CLOSED** | main.pdf = 46pp; 43 before bibliography < 45 (see §2); rule confirmed |
| M1 | 40-hex hash citation keys (13 keys) | **CLOSED** | `grep cite[tp]?\{[0-9a-f]{40}` = 0 hits; µBERT now `\citep{degiovanni2022mubert}` |
| M2 | Headline rests on construct-separation reframing after 4 failed H | **OPEN (reviewer-owned)** | inherent contribution-bar judgment; see §3. Now materially strengthened |
| M3 | Salami boundary with companion benchmark dataset | **PARTIALLY CLOSED** | DOI disclosed + per-case SSOT now in-repo (`main.tex:3095`); reader-visibility still a reviewer ask |
| minor | Results redundancy (singular/mixed-effects ~11×) | **OPEN** | `grep -ci singular\|mixed-effect main.tex` = 11 (unchanged) |
| minor | Supplement 12-vs-13 default operators | **CLOSED** | `supplementary.tex:435,488` now uniformly "13 default classes/operators" |
| minor | Author-list reconciliation (acmart named only Li) | **CLOSED** | `main.tex:32,51,60,69` = Li, Yang, Liu, Yan |

### R1 — Methodology (July-8 score 7/10)

| ID | Item | Status | Evidence |
|---|---|---|---|
| M1 | Industrial arm has zero in-repo provenance | **CLOSED** | `data/results/industrial_percase_v1.json` + `scripts/build_industrial_ssot.py`; Data-Availability para `main.tex:3095-3097`; 23/23 checks pass vs paper |
| M2 | S5 purity + nonzero-SMS OR recoverable but declared open | **CLOSED** | S5 verified 90.1% (`main.tex:962-968, 2421-2442`); incidence sensitivity integrated `main.tex:1956-1972` |
| M3 | Which v4 δ is "the" v4 (0.314 vs 0.439 top-line) | **CLOSED** | explicit reconciliation `main.tex:2052-2054, 2118-2119`: power on unconditioned δ=0.439 pool, verdict on MP5-held δ=0.314 |
| Focus4 | Dual-blind v4 rerun (source-diversity confound) | **OPEN (deferrable)** | reviewer said NOT blocking; NEW-EXPERIMENT (LLM cost); confound disclosed at every use |
| m1–m6 | Sign-test disambiguation, C1_share pin, OR separation, LLMorpheus caveat, acmart routing, vacant-cell count | **MOSTLY CLOSED** | acmart build done; vacant-cell 9 confirmed; OR quantities separated `main.tex:1951-1972` |

### R2 — Domain (July-8 score 5/10; the 5-not-7 was the S5 blocker)

| ID | Item | Status | Evidence |
|---|---|---|---|
| **Blocker** | Effect map σ not proven well-defined; headline depends on it (S5) | **CLOSED** | S5 audited: σ single-valued on 263/292 (90.1%); σ defined as partial function `main.tex:962-968`; off-diagonal re-attributed 57:31 `main.tex:2433` |
| must-cite | µBERT (Degiovanni & Papadakis) | **CLOSED** | `\citep{degiovanni2022mubert}` at `main.tex:299` |
| must-cite | Meta ACH / Alshahwan LLM-mutation | **OPEN** | no `alshahwan` in main.tex or references.bib |
| #24 | HP "structurally unreachable" self-contradiction | **CLOSED** | table cell + prose now "Value-menu artifact (not structural)" `main.tex:1413,1433` matching caption |
| bench | defect4mr "Unpublished" bib vs cited Zenodo DOI | **OPEN (minor)** | `references.bib:17` still `howpublished={Unpublished...}, note={Project material...}`; DOI not folded into entry |
| bench | Reader-facing per-case (34-row) industrial table | **PARTIALLY CLOSED** | data now checkable in-repo (JSON SSOT), but supplement still only a "result-level" summary `supplementary.tex:1480`; no typeset 34-row table |
| term | meta-operator vs meta-pattern collision; CE=mut_C dual naming; Clark homonym one-sentence contrast | **OPEN (minor)** | naming scheme not disambiguated in current source |

### R3 — Statistics (July-8 score 7/10; borderline accept)

| ID | Item | Status | Evidence |
|---|---|---|---|
| M1 | Industrial arm irreproducible; headline p=0.046 is sole inferential leg | **CLOSED** | per-case SSOT + full strengthening battery `main.tex:2510-2524`: exact permutation p=0.014, MC p=0.005, BCa δ-CI [+0.07,+0.46] excludes 0, V=279.5, z=2.16, unadjusted p=0.015 |
| M2 | H2 pool-provenance means mismatch (0.275/0.061 next to δ=0.314) | **CLOSED** | table now shows 0.213/0.077 for δ=0.314 (`main.tex:2043-2044,235`); 0.275/0.061 explicitly labeled MP1-pool `main.tex:2052` |
| M3 | Friedman reported on v3 (χ²=15.30) while pool is v4 | **CLOSED** | v4 reported: χ²=16.76, p=0.0022 `main.tex:2613`; no 15.30/0.0041 in main.tex |
| Focus2 | Elevate nonzero-SMS OR | **CLOSED + CORRECTED** | fix memo found R3's own 2×2 was mislabeled (9/12 vs 6/48 swapped); honest value **OR≈4.2** (not 21), integrated as own family with H2 "not met" preserved `main.tex:1956-1972` |
| minor#1 | Ablation 1-vs-2 count mismatch | **CLOSED** | second de-strictification ablation clause added `main.tex:2538-2539` (17/34, 11 shared) |
| minor#2/#3 | Bootstrap B + Wilcoxon statistic unstated | **CLOSED** | B=10,000 seed 20260704; V=279.5, z=2.16 `main.tex:2510-2513` |

### R4 — Devil's Advocate (July-8 score 6/10; one blocking build defect)

| ID | Item | Status | Evidence |
|---|---|---|---|
| R1 | Packaged main.tex does not compile | **CLOSED** | as R0-B1 |
| R2 | 45-page eligibility unverifiable | **CLOSED** | see §2; 43<45 |
| R3 | Intro prose does not front-load H1–H4 misses | **CLOSED** | `main.tex:136-140` intro plainly states all four thresholds "each not met", "boundary-delimiting findings" |
| R4 | Highlights omit negatives | **N/A for TOSEM** | acmart build drops highlights; source-only concern |
| R5 | Leaked "correct the 30/24/6 figures carried by earlier drafts" | **PARTIALLY CLOSED** | that exact phrase gone; two unrelated "An earlier draft" mentions remain `main.tex:1446,2730` (polish) |
| R6 | Three C1_share anchors (0.164/0.20/0.209) + "+27%" | **OPEN (polish)** | disambiguation clause not confirmed added |
| R7 | Cover-letter "confirm" strongest verb | **CLOSED** | cover_letter.md:18,37 now "support" |
| R8 | ACM sample template travels in zip | **CLOSED** | not in package dir |

---

## 2. Page-rule adjudication — 45-page limit is EXCLUSIVE of references

**Verdict: the paper is ELIGIBLE. No trim required.**

Official ACM TOSEM Fast-Impact rule (dl.acm.org/journal/tosem/fastimpacttrackpapers,
corroborated across two independent web queries):

> "The TOSEM editorial staff will upgrade papers submitted as journal-first papers and with
> **no more than 45 pages of text (not including bibliography)** to fast-impact track papers."

The 45-page ceiling counts **text before the bibliography**. The current PDF is 46 pages total =
**43 body + 3 references**. Since 43 ≤ 45, eligibility holds. The cover letter's own reading
(`cover_letter.md:65-67`: "46 pages including references... text before the bibliography (43 pages)
remains below the 45-page Fast-Impact threshold") is correct per the rule.

The candidate cuts R0 flagged (mixed-effects-singularity redundancy ~11×, HOM repetitions) are a
**quality** improvement, not a **page-budget necessity** — the paper has a 2-page margin on the
governing metric. They remain a recommended prose-tightening item, not a blocker.

---

## 3. Contribution-bar verdict (R0 M2 / R2)

**Question:** with the industrial arm now backed by exact permutation p=0.014 / MC p=0.005 / BCa δ-CI
excluding 0 AND in-repo per-case SSOT, S5 purity verified at 90.1%, and the honest corrected
incidence sensitivity (OR≈4.2, one-sided Fisher p=0.036) — does "all four pre-registered hypotheses
missed, but construct separation validated industrially" clear TOSEM's bar as a boundary-delimitation
contribution?

**For clearing the bar.** TOSEM's remit explicitly rewards methodological rigor and boundary/negative
results. This paper delivers a self-contained conceptual contribution (the SMS metric + the
degeneration characterisation back to classical MS) that stands independent of the hypothesis
outcomes, plus a pre-registered study (frozen to commit + Zenodo DOI) that honestly converts four
threshold misses into a boundary map (operator applicability, MR-design adequacy, kill attribution).
The construct-separation claim is now triangulated, not single-threaded: (a) the industrial four-group
contrast is robust under *exact* inference (permutation p=0.014, MC p=0.005 — no longer the knife-edge
Holm 0.046), (b) the BCa δ-CI excludes zero, (c) four named non-nesting counterexamples with distinct
mechanisms, (d) σ/fiber reading now audited (S5 = 90.1% single-valued, off-diagonal decomposed 57:31),
(e) every industrial number recomputable in-repo. The honesty infrastructure even corrected its *own*
favorable error (the mislabeled OR=21 → honest OR≈4.2) against interest — precisely the behavior a
methodology venue should reward.

**Against clearing the bar.** A skeptical editor can still read "we pre-registered four hypotheses and
missed all four" as an underpowered primary study whose positive signal is a post-hoc reframing. The
positive rests substantially on n=34 self-authored industrial cases (a companion deposit, not an
independent community benchmark); the aggregate dominance narrowed as n grew 30→34 (trend toward the
null), and the corrected incidence advantage is *modest* (OR≈4.2, two-sided CI crosses 1). External
validity is honestly but narrowly bounded to single-output float→float kernels. The Clark
"semantic mutation" homonym still lacks a one-sentence differentiation.

**Committed verdict.** The contribution now clears the bar as a **boundary-delimitation + metric
contribution** and lands as **Major Revision on a credible convergent trajectory to Accept**. It is
above the desk-reject/reject line: the four items that were the only blocker-class findings across all
five reviews (build defect, S5/σ well-definedness, industrial irreproducibility, page eligibility) are
all closed, so **there is no plausible pure-rejection branch remaining**. It is not yet a clean Minor —
the residual majors are the inherent reviewer contribution-bar call plus the Meta-ACH must-cite. A real
round returns Major (one reviewer plausibly Minor), converging in one revision.

---

## 4. Residual list to stable acceptance (ranked)

Tags: severity [blocker/major/minor/polish] · effort [text-only/analysis/new-experiment].

| # | Item | Tag | Effort |
|---|---|---|---|
| 1 | Contribution-bar judgment (four misses + industrial separation) — inherent reviewer call; nothing left to *close*, only to argue well in the response letter | major | text-only |
| 2 | Add Meta ACH / Alshahwan (2024–25 industrial LLM-mutation) must-cite + one distinguishing sentence | major | text-only |
| 3 | Reconcile defect4mr bib entry: drop "Unpublished/Project material", cite Zenodo DOI 10.5281/zenodo.21203424 as primary | minor | text-only |
| 4 | Add reader-facing 34-row per-case industrial appendix table (data already in-repo SSOT) | minor | text-only |
| 5 | Consolidate mixed-effects-singularity redundancy (~11×) + HOM repetitions (quality, not page budget) | minor | text-only |
| 6 | Resolve naming collisions: meta-operator vs meta-pattern; CE=mut_C dual scheme; Clark homonym one-sentence contrast | minor | text-only |
| 7 | Remove two residual "An earlier draft" leaked-history mentions (`main.tex:1446,2730`); disambiguate C1_share 0.20 vs 0.209; reconsider "+27%" framing | polish | text-only |
| 8 | Move Spearman/Kendall p-values off the "none (descriptive)" permission row or add power caveat | polish | text-only |
| 9 | Dual-blind v4 rerun to disentangle the −0.009 source-diversity confound | major (deferrable) | new-experiment |
| 10 | Industrial corpus expansion n=34→70–100 to move the arm from demonstrative to inferential | major (deferrable) | new-experiment |

**True blockers remaining: 0.** Items 9–10 are explicitly deferrable per R1 and R3 (the confound is
disclosed at every use; the arm's verdict does not depend on it) and belong in the "pre-registered
next steps" paragraph, not this submission.

---

## 5. Topic-drift check — NO DRIFT

The thesis is intact through the three fix rounds. The current abstract (`main.tex:100-102`) is
**byte-identical** to the pre-fix source abstract (`git show 3014fa3^:source/main.tex`, diff empty).
It preserves every load-bearing element of the July-7 framing:

- **Semantic mutation as a distinct construct** ("classical mutation score is defined over syntactic
  edits and does not say whether a metamorphic-relation set observes declared domain-semantic effects").
- **SMS metric** ("introduces Semantic Mutation Score (SMS), an MR-relative adequacy metric").
- **Degeneration theorem** ("a degeneration path back to classical mutation score").
- **Honest negative results** ("Several pre-registered empirical thresholds are not met; we use these
  failures to delimit... rather than to claim universal dominance").
- **Industrial construct separation** ("aggregate kill-rate, semantic alignment, and real-defect
  detection are related but distinct constructs... construct separation supported on industrial code").

The fixes *added evidence under* the existing thesis (S5 audit, per-case SSOT, exact-inference battery,
corrected incidence) without shifting the claim. The one verb-strength drift risk R4 flagged
(cover-letter "confirm") was corrected to "support," pulling the cover letter *back into* alignment with
the abstract rather than away. The intro was strengthened to front-load the four misses (`main.tex:138`),
which reinforces — not dilutes — the honest-negative spine. **No drift detected.**

---

## 6. Overall acceptance-readiness score

### **7.5 / 10**

**Reasoning.** The five July-8 scores were 3 (R0), 7 (R1), 5 (R2), 7 (R3), 6 (R4). Three of the five
were suppressed by blockers that are now closed:
- R0's 3 was "desk blocker: file does not build" over an underlying 5–6 manuscript → build fixed + page
  eligibility confirmed → ~6–7.
- R2's 5 was explicitly "the residual S5 gap is what keeps this out of minor-revision territory" → S5
  verified at 90.1% → ~7.
- R4's 6 was "content would earn ~8; what is on disk is unshippable" → build fixed → ~8.
- R1 (7) and R3 (7) each named industrial irreproducibility as the sole thing "held below 8" → per-case
  SSOT + exact-inference battery closes it → ~8.

Post-fix the reviewer cluster moves to **7–8**, i.e. a coherent Major→Minor→Accept band with no
rejection branch. Held below 8 by: the inherent contribution-bar call (four pre-registered misses is a
genuine reviewer question, not an author-closable one), the missing Meta-ACH currency cite, and the
industrial arm remaining a self-authored n=34 companion deposit rather than an independent benchmark.

**What a real review round would most likely return: Major Revision, converging in one cycle.** The
asks would be the text-only items 2–8 above plus the response-letter argument for item 1; the two
new-experiment items would be requested as *future work*, not as revision conditions. No reviewer, on the
current state, has a live path to Reject: every blocker/desk-reject-class finding is closed, the paper
compiles as a clean 43-page-body acmart manuscript, and its single inferential leg is now robust under
exact inference and fully reproducible in-repo.

**Recommendation: SUBMIT NOW.** One optional polish pass (items 2–6) would raise it toward a first-round
Minor, but nothing outstanding is a submission blocker, and the deferrable experiments are correctly
scoped as next steps.

---

*Sources for the page rule:*
[ACM TOSEM Fast-Impact Track Papers](https://dl.acm.org/journal/tosem/fastimpacttrackpapers) ·
[ACM TOSEM Author Guidelines](https://dl.acm.org/journal/tosem/author-guidelines)
