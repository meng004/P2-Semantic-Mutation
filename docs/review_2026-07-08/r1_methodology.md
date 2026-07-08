# Reviewer 1 (Methodology) — ACM TOSEM fast-impact — simulated review 2026-07-08

Manuscript: `source/main.tex` (3056 ll.) + `source/supplementary.tex` (1513 ll.)
SSOT audited: `data/results/*.json`, `data/mutants/*_v4/`, `src/p2/{avp,equiv,lrca}`.
Prior round: `docs/review_2026-07-07/{r1_methodology,synthesis_and_fix_ledger}.md`.

---

## Verdict

**Minor-to-Major revision (borderline).** The honesty infrastructure remains
the strongest asset (per-statistic inference-permissions table at
`main.tex:1895-1931`, four "not met" verdicts stated plainly, declared
protocol-asymmetry confound). Most of last round's 11 blockers are genuinely
closed in the current source (verified below). Two things now gate acceptance:
(1) the **industrial arm (RQ4)** carries real evidential weight in the Abstract
and RQ4 narrative yet has **zero reproducible provenance inside the repo** —
every number traces only to an external Zenodo deposit; and (2) two claims the
paper labels "unverified/deferred" (**S5 purity**, **nonzero-SMS OR robustness**)
are in fact recoverable *from data already in the repo with no new experiment*,
so declaring them open understates what the authors can honestly show. Neither
is fatal to the construct; both are fixable without changing any conclusion.

## Score: **7 / 10**

Up from an effective ~5 last round. Construct, theory, and honesty framing are
publishable; the gap is now traceability and a few unforced under-claims, not
integrity.

---

## Verification of prior-round fixes (spot-checked in current source)

| Prior blocker | Status now | Evidence |
|---|---|---|
| #1 Unverifiable "pre-registered" | **Closed** | `main.tex:566-570` freezes hypotheses in `EXPERIMENT_DESIGN.md` @commit `0f2509527...` + Zenodo 10.5281/zenodo.20250664 |
| #2 No disconfirmation criterion | **Closed** | "What would count against the construct (post hoc)" added at Hypotheses tail (per ledger #27) |
| #3 Conflicting H2 CIs | **Mostly closed** | RQ4 headline now uses v4-MP5 δ=0.314 CI [0.014,0.622] = `rq2_cliffs_delta_v4_mp5.json`; v3 δ=0.323 CI [0.017,0.622]. Residual: see Major-3 (power table still on δ=0.439) |
| #4 0.164→0.209 double attribution | **Closed** | `tab:p2-13` rows now labelled "v3 same-source pool 0.164 / v4 cross-source pool 0.209"; calibration best (0.200) stated separately (`main.tex:2196-2199`) |
| #5 30/30 vs 34 | **Closed** | 34/34 throughout (`main.tex:2454-2463`, permissions row 1928) |
| #6 Abstract over-claim | **Closed** | Abstract now "related but distinct constructs...supporting" (`main.tex:138`), not "opposite orders/confirming" |
| #7 Equivalence bias direction | **Closed** | "biasing SMS slightly *low*" with correct mechanism (`main.tex:1726-1731`) |
| #8 Hoeffding pointer dangling | **Closed** | Bound now present at `supplementary.tex:1123` |
| #9 AVP `<AVP-vX.Y>` placeholder | **Closed** | Replaced by frozen-dependency + embedded-source wording (`main.tex:1746-1749`) |
| Main/supp "verifying H1" contradiction (U1) | **Closed** | `supplementary.tex:754-758`: "necessary precondition...threshold itself...not met, as reported in the main text" |

The integrity blockers that dominated last round are resolved. This is real
progress and should be credited.

---

## Focus-area assessments (with NEW-EXPERIMENT verdicts)

### Focus 1 — Industrial validation (RQ4, 34-case arm)

**NEW-EXPERIMENT verdict: NOT strictly required for THIS submission if the arm
stays demonstrative; a data-deposit fix IS required; a corpus-expansion
experiment is RECOMMENDED to make the arm inferentially robust.**

Findings:

- **Reproducibility gap (this is the real blocker).** Every industrial number —
  T1 377/1124=0.335, A1 348, B1 274, B2 228, paired diff +0.101 CI [+0.029,+0.179],
  Holm p=0.046, δ=0.247, 34/34 face, the 27/34 · 26/34 · 19/34 contrasts, and the
  four non-nesting case IDs (A-LAPACK-004, A-OPENBLAS-001, B-POCKETFFT-002,
  E-ORDINARYDIFFEQ-001) at `main.tex:2442-2487` — has **no backing file in the
  repo**. `data/results/` contains no industrial JSON; grep for `1124`/`377`/case
  IDs hits only `replication/MANIFEST.txt` checksums and a decisions memo, never a
  data artefact. Provenance is 100% external (`\citep{defect4mr2026}`,
  zenodo.21203424). For a TOSEM artifact-evaluation culture this is a
  reviewer-blocking traceability hole: I cannot check a single headline industrial
  number. **Fix (data task, no experiment): deposit the per-case kill matrix
  (34 cases × {T1,B1,B2,A1} × killed/total) and the per-case real-defect
  detection vector as a repo SSOT (e.g. `data/results/industrial_arm.json`), and
  add a permissions-table-style number→file map.**

- **Statistical fragility, honestly disclosed but thin.** Only 1 of 3 Holm-family
  comparisons is significant (T1>B1 at p=0.046); T1>A1 and B1>B2 are not. δ=0.247
  is a *medium* effect, the CI lower bound is +0.029 (barely off zero), and the
  text itself notes the effect *narrowed* when n grew 30→34 — i.e. the trend is
  toward the null as n increases, which is the opposite of what one wants from a
  robustness argument. The 34/34 face is correctly flagged as
  selection-conditioned (`main.tex:2456-2459`, permissions row), so its evidential
  content is only the *contrast* (27/26/19 of 34), which is the sound reading.

- **What a new experiment would buy, concretely.** If the authors want the arm to
  be *inferential* rather than *demonstrative*: expand the corpus from 34 to
  ~70-100 verified defect cases (independent library set, pre-registered inclusion
  rule identical to the current one), which would (a) move Holm-adjusted p for
  T1>B1 from ~0.05 to comfortably <0.01 if the +0.10 mean difference is real, (b)
  tighten the δ CI enough to separate medium from small, and (c) directly test the
  "narrowed at 30→34" fragility by seeing whether the trend continues toward the
  null (which would be a genuinely informative negative result). This is a
  months-scale corpus-mining effort, i.e. a real new experiment. **My
  recommendation: keep the arm framed as a selection-conditioned demonstration
  (as it already is), deposit the per-case data, and cite the corpus expansion as
  the pre-registered next step — do NOT hold this submission for it.** The paper
  does not need the arm to be inferential; it needs it to be *checkable*.

### Focus 2 — S5 purity verification

**NEW-EXPERIMENT verdict: NO new experiment. NEEDS ONLY NEW ANALYSIS OF EXISTING
DATA — and it is cheap, offline, and materially strengthening.**

The paper (`main.tex:2391-2395`) declares: "S5 purity (one declared stratum per
mutant) is enforced by generation intent and certificate review, not verified
against all five invariants, so part of the off-diagonal kill mass may reflect
multi-stratum effects rather than pure cross-stratum detection." This is an
avoidable under-claim. Two feasibility facts:

1. **A kill-level purity proxy is already computable in seconds** from
   `data/results/sms_track2_v4.json` — I ran it. Each PUT's five MP cells record
   per-mutant KILLED/SURVIVE, so cross-referencing a mutant across its 5 cells
   gives the number of MPs that kill it. Result: of the 12 PUTs, **8 are clean
   (every killed mutant dies under exactly 1 MP), but 4 PUTs carry genuine
   multi-stratum kills** — B2 (9 mutants killed in 2 MPs), C1 (2 in 3 MPs), D1
   (9 in 2 MPs), D3 (9 in 2 MPs) = **29 multi-stratum mutants**. This directly
   quantifies the "may reflect multi-stratum effects" hedge into a number.

2. **A full invariant-level S5 check is runnable offline with existing code.**
   `src/p2/avp/dispatcher.py` and `src/p2/equiv/` contain **zero LLM references**
   (grep for `openai|llm_client|anthropic|api_key` returns nothing); the AVP is
   deterministic numeric verification (conservation, Wilcoxon, convergence-order,
   DTW). The mutant `.py` files exist under `data/mutants/*_v4/`. So a script that
   runs every v4 mutant against all five MP AVPs and counts invariant violations
   is a modest offline job (no API cost, no credentials), and it operationalises
   "one declared stratum per mutant" exactly.

**Would verifying it strengthen the paper? Yes, materially.** It converts a
transparency hedge into an audited property: the authors can report "S5 purity
holds at the kill level for 8/12 PUTs; 29 mutants in 4 PUTs exhibit
multi-stratum kills, contributing X% of off-diagonal mass," which is a
*stronger and more honest* statement than "unverified." I recommend running #1
for the camera-ready and #2 for the appendix. **Classification: new analysis of
existing data (script ~1 day), not a new experiment.**

### Focus 3 — Robust H2 advantage

**NEW-EXPERIMENT verdict: NO new experiment, and no dishonest rescue is
available (H2-δ genuinely fails). But ONE legitimately stronger analysis of
existing data is currently under-reported and should be elevated.**

- The H2 δ criterion fails honestly: v4-MP5 δ=0.314, v3 δ=0.323, both below the
  frozen Romano 0.474 anchor and even below the 0.330 medium mark
  (`main.tex:2060-2079`, `paper_numbers_v4.json`, `rq2_cliffs_delta_v4_mp5.json`).
  This should stay exactly as framed. No re-anchoring, no post-hoc threshold
  swap — the paper correctly refuses both.

- **The honest robust signal that is under-reported: the nonzero-SMS odds ratio.**
  The binarized sensitivity (aligned nonzero 9/12 vs cross nonzero 6/48 →
  OR = (9·42)/(3·6) = **21.0**) is currently a single demoted sentence
  (`main.tex:1961-1965`) reported "only to show the ratio criterion's intent
  survives binarization, not as a licensed verdict." That framing is admirably
  cautious, but it *understates* a genuinely strong, defensible result: a
  Fisher-exact test on that 2×2 is what actually carries the aligned-vs-cross
  signal once the zero-mass degeneracy is acknowledged. **Missing analysis: the
  Fisher-exact CI on OR=21** (scipy `odds_ratio`/`fisher_exact`, one call, but
  scipy is not installed in the current sandbox so I could not print the interval;
  the point estimate 21.0 is arithmetic). Elevating this to a pre-declared
  *sensitivity* result with its exact CI and one-sided p is the strongest honest
  H2-adjacent statement available, and it is new analysis of existing data — no
  experiment. It reframes H2 accurately: the *large-effect δ target* fails, but
  the *presence/absence structure* the odds-ratio criterion was meant to capture
  is robustly nonzero.

- The vacant-cell sensitivity already exists and is reported (`main.tex:2081-2088`,
  δ=0.323/0.270 with CIs crossing zero). Good. Keep it.

**Bottom line: framing stays "H2 not met"; add the Fisher-exact CI on the
nonzero-SMS OR as a first-class sensitivity, not a footnote.**

### Focus 4 — Source-diversity dual-blind v4 rerun

**NEW-EXPERIMENT verdict: THIS is the one focus area that genuinely NEEDS a new
experiment (bounded LLM reviewer rerun). Feasible with repo infrastructure but
requires credentials + cost; acceptable to defer for THIS submission because the
confound is honestly declared.**

- The deferral is real and correctly disclosed (`main.tex:1661-1669`, 2169-2176,
  2410-2413): v3 used the dual-blind reviewer (Claude gen + GPT review + DeepSeek
  arbitration); v4 used V1-V4 mechanical gates only. The v3→v4 δ shift of −0.009
  (CI [−0.238, 0.207]) is therefore confounded between source-diversity and a
  quality decline from dropping the reviewer.

- **Feasibility.** `scripts/cross_source_campaign.py` exists and the v4 mutant
  pool is already materialised in `data/mutants/*_v4/`, so a rerun does *not*
  require regenerating mutants — it requires applying the dual-blind reviewer step
  (GPT review + DeepSeek arbitration) to the ~292 existing v4 mutants, then
  recomputing SMS/δ. **But** `cache_cross/` holds only `_log.json` (no cached
  reviewer responses), and the reviewer step needs live API calls + `.env`
  credentials that are not in the repo. So this is bounded but real LLM cost:
  O(292 mutants × 2 reviewer roles) ≈ a few hundred–thousand calls.

- **What it settles.** It cleanly disentangles the −0.009 into a source-diversity
  component and a protocol-quality component, closing the one declared confound
  that currently qualifies the RQ4 cross-source reading. If the rerun still shows
  |Δδ| small under matched protocol, the "cross-source improves quality not effect
  size" claim (`main.tex:2336-2351`) becomes clean rather than caveated.

- **Recommendation.** Not required to hold the submission — the confound is
  disclosed at every point of use and the RQ4 verdict does not depend on it. But
  it is the highest-value follow-up, and the paper should state the bounded cost
  and the exact protocol so a reviewer sees it is a scoped rerun, not open-ended.

---

## General methodology pass

### Major

- **M1 (Industrial traceability).** As Focus 1: deposit per-case industrial data
  as a repo SSOT before submission. A headline arm that appears in the Abstract
  cannot be un-checkable in a TOSEM artifact. *Data task, not experiment.*

- **M2 (Two under-claimed but recoverable results).** S5 purity (Focus 2) and the
  nonzero-SMS OR CI (Focus 3) are both computable from existing data. Leaving them
  as "unverified/auxiliary" is an unforced weakness; run both. *New analysis.*

- **M3 (Which v4 delta is "the" v4?).** The RQ4 aligned-vs-cross headline uses the
  MP5-held δ=0.314 (`rq2_cliffs_delta_v4_mp5.json`), but the power/exceedance
  tables (`main.tex:2116-2120`, `tab:p2-11`) are computed on the unconditioned
  v4 pool δ=0.4392 (`rq2_power_v4.json:observed.cliffs_delta`), and `main.tex:2130`
  says "ε>0 jumps δ from 0.314 to 0.74." So the reported point estimate (0.314)
  and the object the power analysis characterises (0.439 distribution) differ.
  `paper_numbers_v4.json` still top-lines `cliffs_delta: 0.439`. This is not an
  integrity issue (both are real configurations of the same pool) but it is a
  live internal inconsistency a careful reviewer will flag. State once, explicitly,
  that the power analysis is run on the unconditioned pool while the primary
  verdict uses the MP5-held estimate, and reconcile the SSOT top-line. *Text +
  possibly re-run power on the 0.314 config.*

### Minor

- **m1.** `rq3.sign_test_aligned_above_cross` in `paper_numbers_v4.json` is **4**,
  while the RQ5 text (`main.tex:2513-2515`) reports the within-class sign test as
  **3/4** (b-class inverted). These count different things (cell-level vs
  class-level directional sign), but both surface as "sign test" near each other;
  a one-line disambiguation would prevent a reviewer misreading them as
  contradictory.

- **m2.** `main.tex:2196` still labels the v3 C1_share row 0.164 while the
  LRCA SSOT and the cross-source discussion (`main.tex:2340`, 2399) use the same
  0.164→0.209 pair; confirm the v3 figure is 0.164 not 0.156 (last round's
  ledger #3 recorded "v3≈0.156→v4≈0.204" from a recompute). Pin one pair
  everywhere.

- **m3.** Odds-ratio language: `main.tex:1959` ("median odds ratio is formally
  infinite") and the binarized OR=21 (`main.tex:1963`) sit two sentences apart;
  a reader can conflate the degenerate +∞ with the meaningful 21. Separate them
  with an explicit "distinct quantity" clause.

- **m4.** `main.tex:2090-2095` retains the LLMorpheus "medium-effect range"
  comparison with an estimand caveat. The caveat is correct, but since the
  numerical similarity is explicitly declared non-substantive, consider whether
  it earns its place in the main text or belongs in a footnote.

- **m5.** Supplementary still contains venue-neutral scaffolding; confirm the
  `elsarticle` main + `acmart` supplement are both routed through `build.py` to
  TOSEM `acmart` and that no stale IST/Highlights artefact reaches the submitted
  PDF (main.tex still carries a `highlights` environment at ll.124-132).

- **m6.** The vacant-cell count is stated as "9 cells" (`main.tex:2081`) here;
  last round's U3/U6 flagged a 6-vs-9 vacant-cell tension against the coverage
  matrix caption. Confirm the coverage-matrix table body, its caption, and this
  "9 vacant" figure now agree (I did not re-audit the matrix cells this round).

---

## Reviewer 2 (ARS) cross-check — integrity/external-validity scan

No new publication-blocker of the integrity class. Specifically:

- **Statistical selection bias:** the paper reports all four failed hypotheses,
  pre-registers with a frozen commit hash, and flags every post-hoc analysis
  (OR=21, applicability-adjusted H1 denominator) as non-verdict. No cherry-picking
  detected.
- **External validity:** n=12 PUTs / n=34 industrial cases are honestly bounded to
  single-output float→float kernels; no over-generalisation in the Conclusion.
- **Benchmark fairness:** AST-overlap comparison is against cosmic-ray defaults
  (a real baseline), not a strawman.
- **The one residual ARS concern is traceability, not integrity:** the industrial
  arm's un-depositable-in-repo status (M1) means a reader must trust an external
  DOI for an Abstract-level claim. That is a reproducibility hole, not
  selective reporting, and closes with a data deposit.

---

## Summary of experiment/analysis classification

| Focus | Verdict | Class |
|---|---|---|
| 1 Industrial RQ4 | Deposit data (required); corpus n→~70 (recommended, not blocking) | data task + optional NEW experiment |
| 2 S5 purity | Run kill-level + offline invariant check | NEW ANALYSIS of existing data (no experiment) |
| 3 Robust H2 | Add Fisher-exact CI on nonzero-SMS OR=21; keep "H2 not met" | NEW ANALYSIS of existing data (no experiment) |
| 4 Dual-blind v4 rerun | Bounded reviewer-LLM rerun on existing 292-mutant pool | NEW EXPERIMENT (LLM cost); OK to defer |
